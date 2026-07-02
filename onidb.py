#!/usr/bin/env python3
"""ONI DB 読み取り専用CLI/ライブラリ。

2層構成:
  - query_*() : DBを引いてPythonのlist[dict]/dictを返す純粋な関数群。
                `import onidb` して直接呼び出せる(CLIに依存しない)。
  - cmd_*()   : argparseのNamespaceを受け取り、query_*()の結果を
                テーブル表示 or JSON表示するCLI側の薄いラッパー。
"""
import argparse
import json
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent / "oni.db"


def connect(db_path=None):
    path = Path(db_path) if db_path else DB_PATH
    if not path.exists():
        sys.exit(f"DBが見つかりません: {path}\n"
                  f"先に `sqlite3 oni.db < schema.sql && sqlite3 oni.db < seed.sql` を実行してください。")
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    return con


def _rows_to_dicts(rows):
    return [dict(r) for r in rows]


# ============================================================
# query_*: ライブラリとして使う純粋関数群(sqlite3.Rowではなくlist[dict]/dictを返す)
# ============================================================

def query_agents(name=None, con=None):
    own = con is None
    con = con or connect()
    try:
        if name:
            rows = con.execute("SELECT id, name FROM agents WHERE name LIKE ? ORDER BY name",
                                (f"%{name}%",)).fetchall()
        else:
            rows = con.execute("SELECT id, name FROM agents ORDER BY name").fetchall()
        return _rows_to_dicts(rows)
    finally:
        if own:
            con.close()


def query_resources(name=None, con=None):
    own = con is None
    con = con or connect()
    try:
        if name:
            rows = con.execute("SELECT id, name FROM resources WHERE name LIKE ? ORDER BY name",
                                (f"%{name}%",)).fetchall()
        else:
            rows = con.execute("SELECT id, name FROM resources ORDER BY name").fetchall()
        return _rows_to_dicts(rows)
    finally:
        if own:
            con.close()


def query_terms(name=None, con=None):
    own = con is None
    con = con or connect()
    try:
        if name:
            rows = con.execute("SELECT id, name, description FROM terms WHERE name LIKE ? ORDER BY name",
                                (f"%{name}%",)).fetchall()
        else:
            rows = con.execute("SELECT id, name, description FROM terms ORDER BY name").fetchall()
        return _rows_to_dicts(rows)
    finally:
        if own:
            con.close()


def query_agent_io(agent=None, resource=None, con=None):
    """指定Agentの入出力一覧、または指定資源を入出力するAgent一覧を返す。agent/resourceどちらか必須。"""
    if not agent and not resource:
        raise ValueError("agent または resource のいずれかを指定してください")
    own = con is None
    con = con or connect()
    try:
        if agent:
            rows = con.execute(
                "SELECT agent_name, recipe, resource_name, basis, rate_per_cycle FROM agent_io_detail "
                "WHERE agent_name LIKE ? ORDER BY agent_name, recipe, rate_per_cycle",
                (f"%{agent}%",)).fetchall()
        else:
            rows = con.execute(
                "SELECT agent_name, recipe, resource_name, basis, rate_per_cycle FROM agent_io_detail "
                "WHERE resource_name LIKE ? ORDER BY resource_name, rate_per_cycle",
                (f"%{resource}%",)).fetchall()
        return _rows_to_dicts(rows)
    finally:
        if own:
            con.close()


def query_setups(con=None):
    own = con is None
    con = con or connect()
    try:
        return _rows_to_dicts(con.execute("SELECT id, name FROM setups ORDER BY name").fetchall())
    finally:
        if own:
            con.close()


def query_balance(setup, con=None):
    """setup名またはidを受け取り、{"setup": {...}, "balance": [...]}を返す。見つからなければNone。"""
    own = con is None
    con = con or connect()
    try:
        setup_row = con.execute("SELECT id, name FROM setups WHERE name = ? OR id = ?",
                                 (setup, setup)).fetchone()
        if not setup_row:
            return None
        rows = con.execute(
            "SELECT resource_name, net_balance FROM setup_balance WHERE setup_id = ? "
            "ORDER BY net_balance DESC", (setup_row["id"],)).fetchall()
        return {"setup": dict(setup_row), "balance": _rows_to_dicts(rows)}
    finally:
        if own:
            con.close()


def query_gaps(con=None):
    """熱反応/加工系Agentの消費側に登録されていない資源を洗い出す。"""
    own = con is None
    con = con or connect()
    try:
        prefixes = ["融解(", "昇華(", "気化(", "凝縮(", "凝固(", "分解(",
                    "腐敗(", "焼成(", "焼成窯(", "粉砕機(", "期限切れ(", "コンポスト("]
        like_clause = " OR ".join(["a.name LIKE ?"] * len(prefixes))
        params = [f"{p}%" for p in prefixes]
        query = f"""
            SELECT r.name FROM resources r
            WHERE r.id NOT IN (
              SELECT ai.resource_id FROM agent_io ai
              JOIN agents a ON a.id = ai.agent_id
              WHERE ({like_clause})
                AND ai.rate_per_cycle < 0
            )
            ORDER BY r.name
        """
        return _rows_to_dicts(con.execute(query, params).fetchall())
    finally:
        if own:
            con.close()


DEFAULT_IGNORE_RESOURCES = ("電力", "天然ガス")

# recipe名にこれらのバフ名を含む反応は、質量コストゼロの上位互換レシピ
# (例: グラブグラブが居るだけで生産×1.5)なので、常時有効にするとソルバーが
# 無条件に選んでしまう(direct_grazing_resource_alias.mdの偽経路問題と同型)。
# 既定では読み込み時に除外し、--buff で明示指定されたときだけ含める。
# 詳細: docs/issues/plant_buff_and_milk_model.md
OPTIONAL_BUFF_RECIPES = ("グラブグラブ世話",)


def _recipe_buff_gated(recipe, buffs):
    """recipe名がオプションゲート対象のバフを含み、かつそのバフが有効化されていなければTrue。"""
    return any(gated in recipe and gated not in buffs for gated in OPTIONAL_BUFF_RECIPES)

# 質量を持たない擬似資源。Agentの質量保存判定(mass_creating_agents)の対象外にする。
# カロリー(kcal)・電力(W)は単位が質量ではなく、「〜成長量」は植物の成長進捗を表す内部量。
MASSLESS_RESOURCE_NAMES = ("カロリー", "電力")
MASSLESS_RESOURCE_SUFFIXES = ("成長量",)


def mass_creating_agents(con, ignore=(), tolerance=1e-6, buffs=()):
    """出力の質量合計が入力の質量合計を上回る(=実質的に質量を創り出す)Agent名の集合を返す。

    増殖閉路(発散)には、閉路のどこかに質量を創出する反応が最低1つ必要
    (全反応が質量保存なら、閉じた系での正味増加は数学的に不可能)。
    calories側は発散閉路(ray)から除外対象を選ぶ際、この集合を「物理的な元凶」として優先する。
    水洗トイレ(5kg→11.7kg)、多くのクリッター・植物、油井(600kg→2018kg)などが該当。

    カロリー・電力・成長量などの擬似資源は質量ゼロとして合計から除外する。
    さらにignoreで無制限扱いにした資源も質量ゼロとして数える: 例えば天然ガスを
    無視すると天然ガス発電機(天然ガス→汚染水+CO2)は「タダの資源から質量を生む」
    実質的な創出者になるため、kg保存的に見えてもここで検出される必要がある。"""
    massless = set()
    for row in con.execute("SELECT id, name FROM resources"):
        if (row["name"] in MASSLESS_RESOURCE_NAMES
                or row["name"].endswith(MASSLESS_RESOURCE_SUFFIXES)
                or row["name"] in ignore):
            massless.add(row["id"])
    creators = set()
    for r in load_reactions(con, buffs=buffs):
        net_mass = sum(rate for rid, rate in r["rates"].items() if rid not in massless)
        if net_mass > tolerance:
            creators.add(r["name"])
    return creators


def query_calorie_yield(resource, target="カロリー", ignore=DEFAULT_IGNORE_RESOURCES,
                         exclude_agents=None, buffs=(), con=None):
    """指定資源1kgから、加工チェーン全体(複数材料同時消費のレシピも含む)を通じて
    最大どれだけtarget(既定: カロリー)を生産できるかをLPで解く。

    仕組み:
      - 全AgentのAgent単位の反応(load_reactions、多入力・多出力を不可分に保持)を
        変数とし、その稼働比率(activity)>=0を求める線形計画問題として解く。
      - 起点資源(resource)は外部から無制限に調達できる原料とみなし、
        ネットワーク全体でのその資源の正味消費量をちょうど1kgに固定する(等式制約)。
      - target以外の資源は、ネットワーク内で「生産量 >= 消費量」を満たす必要がある
        (=他の材料を魔法のように生み出すことはできない。ガスレンジの複数食材等も
        ちゃんと別経路で用意しないと使えない)。
      - ignoreに指定した資源(既定: 電力、ガスレンジ等が使う天然ガス)だけは
        balance制約から除外し、無制限に使える前提にする(ユーザー指示による)。
      - targetは目的関数(最大化対象)なので、balance制約は課さない(消費されない前提)。
    load_reactions()は「消費・生産の両方があるAgentのみ」を反応化するため、
    無から資源を生む(alwaysで純生産するだけの)Agentは最初から候補に入らない。

    自己増殖ループ(発散)の扱い — exclude_agentsがNone(既定)のとき:
      LPが非有界になった場合のみ、単体法が示す発散方向(ray=その瞬間実際に成立している
      増殖閉路の構成反応)を取り出し、そのメンバーの中から質量を創出するAgent
      (mass_creating_agents: 水洗トイレ等の物理的な元凶)を優先して除外し、解き直す。
      有界になるまでこれを反復する。完全な閉路が存在しない限り無限増殖は起きないため、
      閉路に参加していないAgentは(質量創出型であっても)一切除外されない。
      静的な一括除外(ループ検出結果の全構成員除外/質量創出Agent全除外)は
      どちらも過剰検出だったため、この「発散した閉路だけを最小限切る」方式に置き換えた。
    exclude_agentsを明示的に渡した場合は自動除外を行わず、発散したら無限大として報告する。"""
    own = con is None
    con = con or connect()
    try:
        start = con.execute("SELECT id, name FROM resources WHERE name LIKE ? ORDER BY length(name) LIMIT 1",
                             (f"%{resource}%",)).fetchone()
        if not start:
            return None
        target_row = con.execute("SELECT id, name FROM resources WHERE name = ?", (target,)).fetchone()
        if not target_row:
            return None
        resource_id = start["id"]
        target_id = target_row["id"]

        ignore_ids = set()
        for name in ignore:
            row = con.execute("SELECT id FROM resources WHERE name = ?", (name,)).fetchone()
            if row:
                ignore_ids.add(row["id"])

        auto_break = exclude_agents is None
        exclude_set = set() if auto_break else set(exclude_agents)
        # 発散閉路から除外対象を選ぶときの優先候補(質量を創出する=物理的な元凶のAgent)。
        # 気化・凝縮・浄水機のような質量保存の変換器は、同じ閉路に居ても除外を後回しにする。
        creators = mass_creating_agents(con, ignore=ignore, buffs=buffs) if auto_break else set()

        # 発散(非有界)するたびに「実際に成立している増殖閉路(単体法のray)」を取り出し、
        # その閉路の構成メンバーだけから除外して解き直す反復。閉路を組んでいないAgentは
        # 質量創出型であっても一切除外されない(ユーザー指摘: 完全な閉路が存在しなければ
        # 無限増殖は起きないので、静的な一括除外は過剰検出になる)。
        while True:
            all_reactions = [r for r in load_reactions(con, buffs=buffs) if r["name"] not in exclude_set]
            if not all_reactions:
                return {"resource": start["name"], "target": target_row["name"],
                         "kcal_per_kg": 0.0, "reactions": [], "byproducts": [],
                         "excluded_agents": sorted(exclude_set)}

            # Rから実際に調達可能な資源だけを使う反応に絞り込む(前向き到達可能性のフィックスポイント)。
            # Rと無関係な場所にある増殖閉路をLPに持ち込まないための枝刈り。
            reachable = {resource_id} | ignore_ids
            reactions = []
            remaining = list(all_reactions)
            changed = True
            while changed:
                changed = False
                still_remaining = []
                for r in remaining:
                    inputs = [rid for rid, rate in r["rates"].items() if rate < 0]
                    if all(rid in reachable for rid in inputs):
                        reactions.append(r)
                        outputs = [rid for rid, rate in r["rates"].items() if rate > 0]
                        for rid in outputs:
                            if rid not in reachable:
                                reachable.add(rid)
                                changed = True
                    else:
                        still_remaining.append(r)
                remaining = still_remaining

            if target_id not in reachable:
                return {"resource": start["name"], "target": target_row["name"],
                         "kcal_per_kg": 0.0, "reactions": [], "byproducts": [],
                         "excluded_agents": sorted(exclude_set)}

            # 後ろ向き閉包: targetの生産に(材料供給として間接的にも)寄与し得る反応だけ残す。
            # 出力がどれも「target生産チェーンの必要物」でない反応は、資源を浪費するだけで
            # 最適解に含まれることはないため安全に落とせる。LPのサイズと縮退を減らす。
            useful = {target_id}
            kept = []
            pool = list(reactions)
            changed = True
            while changed:
                changed = False
                still = []
                for r in pool:
                    if any(rate > 0 and rid in useful for rid, rate in r["rates"].items()):
                        kept.append(r)
                        for rid, rate in r["rates"].items():
                            if rate < 0 and rid not in useful:
                                useful.add(rid)
                                changed = True
                    else:
                        still.append(r)
                pool = still
            reactions = kept

            touched = sorted({rid for r in reactions for rid in r["rates"]} - ignore_ids - {resource_id, target_id})

            n = len(reactions)
            # balance制約: 各資源について 正味生産(=生産-消費) >= 0 → -net <= 0
            # 誰も消費しない資源(純粋な副産物)の行は常に満たされるため生成しない。
            # RHSは0ではなく微小な正値にする(縮退対策の摂動。b=0の行が大量にあると
            # 単体法が目的関数を進めない縮退ピボットで空回りする。非有界の検出には影響しない)。
            consumed_rids = {rid for r in reactions for rid, rate in r["rates"].items() if rate < 0}
            constraints = []
            bounds = []
            for k, rid in enumerate(rid for rid in touched if rid in consumed_rids):
                constraints.append([-reactions[i]["rates"].get(rid, 0.0) / reactions[i]["scale"] for i in range(n)])
                bounds.append(1e-9 * (k + 1))
            # 起点資源の正味消費量をちょうど1kgに固定する等式制約(<=1 かつ >=1の2本で表現)
            constraints.append([reactions[i]["rates"].get(resource_id, 0.0) / reactions[i]["scale"] for i in range(n)])
            bounds.append(-1.0)
            constraints.append([-reactions[i]["rates"].get(resource_id, 0.0) / reactions[i]["scale"] for i in range(n)])
            bounds.append(1.0)

            objective = [reactions[i]["rates"].get(target_id, 0.0) / reactions[i]["scale"] for i in range(n)]

            # 起点資源を消費する反応が(閉包・除外の結果)1つも残っていなければ、
            # 「ちょうど1kg消費する」等式制約が満たせずLPは実行不可能。先に打ち切る。
            if not any(r["rates"].get(resource_id, 0.0) < 0 for r in reactions):
                return {"resource": start["name"], "target": target_row["name"],
                         "kcal_per_kg": 0.0, "reactions": [], "byproducts": [],
                         "excluded_agents": sorted(exclude_set)}

            try:
                optimum, scaled_activity = simplex_maximize(constraints, bounds, objective)
                break
            except UnboundedLP as e:
                ray_agents = {reactions[i]["name"] for i in e.ray}
                if not auto_break or not ray_agents:
                    return {"resource": start["name"], "target": target_row["name"],
                            "kcal_per_kg": float("inf"), "reactions": [], "byproducts": [],
                            "excluded_agents": sorted(exclude_set),
                            "note": "この起点資源が到達できる範囲に自己増殖ループが含まれるため、"
                                    "理論上は無限にカロリーを生産できます(`onidb.py loops`で該当ループを確認してください)。"}
                # 閉路メンバーのうち質量創出型を優先して除外。居なければ閉路全体を除外して前進を保証。
                to_exclude = (ray_agents & creators) or ray_agents
                exclude_set |= to_exclude

        resource_names = {r["id"]: r["name"] for r in con.execute("SELECT id, name FROM resources")}
        # RHS摂動(縮退対策)の副作用として微小な無意味稼働が大量に立つ。摂動は1e-9*行数
        # オーダーだが、scaleの大きい反応(食事系: カロリー1200等)では1e-4程度まで増幅される
        # ため、最大稼働量比1e-3未満を表示から落とす(結果のkcal値への影響は同オーダーで無視できる)。
        max_scaled = max(scaled_activity) if scaled_activity else 0.0
        cutoff = max_scaled * 1e-3
        used = [(i, scaled_activity[i] / reactions[i]["scale"]) for i in range(n)
                if scaled_activity[i] > cutoff]
        net = defaultdict_sum(reactions, used)

        used_reactions = [
            {"agent": reactions[i]["name"], "basis": reactions[i]["basis"], "activity": activity}
            for i, activity in sorted(used, key=lambda t: -t[1])
        ]
        byproducts = [
            {"resource": resource_names[rid], "value": value}
            for rid, value in sorted(net.items(), key=lambda t: -t[1])
            if value > 1e-6 and rid not in (resource_id, target_id) and rid not in ignore_ids
        ]

        return {
            "resource": start["name"],
            "target": target_row["name"],
            "kcal_per_kg": optimum,
            "reactions": used_reactions,
            "byproducts": byproducts,
            "excluded_agents": sorted(exclude_set),
        }
    finally:
        if own:
            con.close()


def defaultdict_sum(reactions, used):
    net = {}
    for i, activity in used:
        for rid, rate in reactions[i]["rates"].items():
            net[rid] = net.get(rid, 0.0) + rate * activity
    return net


def load_reactions(con, buffs=()):
    """Agentの理想定常運転を「(Agent, recipe)ごとの不可分な反応式」として読み込む。

    buffsに含まれないオプションゲート対象バフ(OPTIONAL_BUFF_RECIPES)を
    recipe名に含む行は読み込み時に除外する。

    active/always/eat/harvestはすべてcycle当たりに正規化済みなので、
    連続稼働・即時収穫・毛刈り条件維持の理想値として(Agent, recipe)単位で合算する。
    deathは死亡1回当たりで寿命換算されていないため除外する。
    入出力を個別の辺に分解しないため、多入力レシピでも必要資源を
    すべて同時に満たすことが強制される。
    recipe=''はそのAgentの唯一/既定の挙動。recipe付きの場合、表示名は「Agent名(recipe)」。"""
    from collections import defaultdict

    grouped = defaultdict(dict)
    rows = con.execute(
        "SELECT ai.agent_id, a.name AS agent_name, ai.recipe, ai.resource_id, "
        "ai.rate_per_cycle, ai.basis "
        "FROM agent_io ai JOIN agents a ON a.id = ai.agent_id"
    ).fetchall()
    for row in rows:
        if row["basis"] == "death":
            continue
        if _recipe_buff_gated(row["recipe"], buffs):
            continue
        key = (row["agent_id"], row["agent_name"], row["recipe"])
        grouped[key][row["resource_id"]] = (
            grouped[key].get(row["resource_id"], 0.0) + row["rate_per_cycle"]
        )

    reactions = []
    for (agent_id, name, recipe), rates in grouped.items():
        if not any(v < 0 for v in rates.values()):
            continue
        if not any(v > 0 for v in rates.values()):
            continue
        scale = max(abs(v) for v in rates.values())
        reactions.append({
            "agent_id": agent_id,
            "name": f"{name}({recipe})" if recipe else name,
            "recipe": recipe,
            "basis": "steady",
            "rates": rates,
            "scale": scale,
        })
    return reactions


class UnboundedLP(RuntimeError):
    """LPが非有界(目的関数を無限に増やせる)ときに送出される。

    ray属性に、非有界方向で稼働量が増加していく変数(=反応)のインデックス集合を持つ。
    これは「実際にその瞬間の基底で成立している自己増殖の組み合わせ」そのものなので、
    呼び出し側はこの中から除外対象を選んで解き直すことで、閉路を組んでいない
    無関係なAgentを巻き添えにせずに発散だけを潰せる。"""

    def __init__(self, ray):
        super().__init__("LPが非有界です")
        self.ray = ray


def simplex_maximize(a, b, c, eps=1e-10, max_pivots=20000):
    """max c*x, subject to a*x <= b and x >= 0.

    ループ問題では b >= 0 かつ0ベクトルが常に初期実行可能解なので、
    スラック変数から始める単体法で完全に解ける。外部依存は不要。
    非有界の場合はUnboundedLP(発散方向の変数集合ray付き)を送出する。"""
    m = len(a)
    n = len(c)
    basis = [n + i for i in range(m)]
    nonbasis = list(range(n)) + [-1]
    tab = [[0.0] * (n + 2) for _ in range(m + 2)]
    for i in range(m):
        tab[i][:n] = a[i]
        tab[i][n] = -1.0
        tab[i][n + 1] = b[i]
    for j in range(n):
        tab[m][j] = -c[j]
    tab[m + 1][n] = 1.0
    pivots = 0

    def pivot(row, col):
        nonlocal pivots
        pivots += 1
        if pivots > max_pivots:
            raise RuntimeError("ループ収支LPが反復上限に達しました")
        inverse = 1.0 / tab[row][col]
        for i in range(m + 2):
            if i == row:
                continue
            for j in range(n + 2):
                if j != col:
                    tab[i][j] -= tab[row][j] * tab[i][col] * inverse
        for j in range(n + 2):
            if j != col:
                tab[row][j] *= inverse
        for i in range(m + 2):
            if i != row:
                tab[i][col] *= -inverse
        tab[row][col] = inverse
        basis[row], nonbasis[col] = nonbasis[col], basis[row]

    def run_simplex(phase):
        objective_row = m + 1 if phase == 1 else m
        seen_bases = set()
        while True:
            state = tuple(basis)
            # 通常は高速なDantzig則を使い、同じ基底へ戻ったピボット
            # だけBland則にする。循環を抜けたら高速規則へ戻す。
            use_bland = state in seen_bases
            seen_bases.add(state)
            choices = [
                j for j in range(n + 1)
                if not (phase == 2 and nonbasis[j] == -1)
                and tab[objective_row][j] < -eps
            ]
            if not choices:
                return True
            if use_bland:
                col = min(choices, key=lambda j: nonbasis[j])
            else:
                col = min(choices, key=lambda j: (tab[objective_row][j], nonbasis[j]))
            rows = [i for i in range(m) if tab[i][col] > eps]
            if not rows:
                # 非有界: 入る変数nonbasis[col]をいくら増やしても制約に当たらない。
                # 発散方向で値が増える変数(入る変数 + 係数が負の基底変数)のうち、
                # 元の変数(スラックでないもの)を発散閉路の構成メンバーとして報告する。
                ray = {v for v in [nonbasis[col]] + [basis[i] for i in range(m) if tab[i][col] < -eps]
                       if 0 <= v < n}
                raise UnboundedLP(ray)
            ratios = {i: tab[i][n + 1] / tab[i][col] for i in rows}
            min_ratio = min(ratios.values())
            tolerance = eps * max(1.0, abs(min_ratio))
            tied = [i for i in rows if ratios[i] <= min_ratio + tolerance]
            # 比率判定が同率なら、基底変数番号が最小のものを出す。
            row = min(tied, key=lambda i: basis[i])
            pivot(row, col)

    row = min(range(m), key=lambda i: tab[i][n + 1])
    if tab[row][n + 1] < -eps:
        pivot(row, n)
        if not run_simplex(1) or tab[m + 1][n + 1] < -eps:
            raise RuntimeError("ループ収支LPに実行可能解がありません")
        if abs(tab[m + 1][n + 1]) > eps:
            raise RuntimeError("ループ収支LPの人工変数が残りました")
        if -1 in basis:
            artificial_row = basis.index(-1)
            col = min(range(n + 1), key=lambda j: (tab[artificial_row][j], nonbasis[j]))
            pivot(artificial_row, col)
    run_simplex(2)

    x = [0.0] * n
    for i in range(m):
        if basis[i] < n:
            x[basis[i]] = tab[i][n + 1]
    return tab[m][n + 1], x


def reaction_components(reactions):
    """反応の入力→出力から資源の強連結成分を求める。

    閉じた収支に必要な資源は必ず同じ強連結成分に属する。
    これによりLPを小さな候補群に分け、網羅性を落とさず高速化する。"""
    from collections import defaultdict

    graph = defaultdict(set)
    nodes = set()
    for reaction in reactions:
        inputs = [rid for rid, rate in reaction["rates"].items() if rate < 0]
        outputs = [rid for rid, rate in reaction["rates"].items() if rate > 0]
        nodes.update(inputs)
        nodes.update(outputs)
        for source in inputs:
            graph[source].update(outputs)

    index = 0
    indices = {}
    lowlink = {}
    stack = []
    on_stack = set()
    components = []

    def visit(node):
        nonlocal index
        indices[node] = index
        lowlink[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)
        for nxt in graph[node]:
            if nxt not in indices:
                visit(nxt)
                lowlink[node] = min(lowlink[node], lowlink[nxt])
            elif nxt in on_stack:
                lowlink[node] = min(lowlink[node], indices[nxt])
        if lowlink[node] == indices[node]:
            component = set()
            while True:
                current = stack.pop()
                on_stack.remove(current)
                component.add(current)
                if current == node:
                    break
            components.append(component)

    for node in nodes:
        if node not in indices:
            visit(node)
    return components


def _strip_ignored_resources(reactions, ignore_ids):
    """反応群からignore_idsに含まれる資源の入出力行を取り除く(=balance制約対象外にする)。
    その結果、消費または生産のどちらかが無くなった反応は反応として成立しなくなるため除外する。"""
    if not ignore_ids:
        return reactions
    result = []
    for r in reactions:
        rates = {rid: rate for rid, rate in r["rates"].items() if rid not in ignore_ids}
        if not any(v < 0 for v in rates.values()):
            continue
        if not any(v > 0 for v in rates.values()):
            continue
        scale = max(abs(v) for v in rates.values())
        result.append({**r, "rates": rates, "scale": scale})
    return result


def query_loops(min_gain=1.0, max_depth=8, ignore=(), buffs=(), con=None):
    """全資源の正味収支が0以上となる反応の組をLPで探す。

    各資源を目的関数にして正味生産を最大化する。すべての消費資源
    (電力も含む)は同じ反応組の生産で補う必要があるため、多入力の
    一部だけを無視した偽ループは成立しない。戻り値はlist[dict]
    (reactions/positive/target/gain)。

    ignoreに資源名を渡すと、その資源はbalance制約から除外される
    (=無制限に使える前提でループを探す。calories側で電力を除外した
    状態でも自己完結してしまうループを洗い出すのに使う)。"""
    own = con is None
    con = con or connect()
    try:
        ignore_ids = set()
        for name in ignore:
            row = con.execute("SELECT id FROM resources WHERE name = ?", (name,)).fetchone()
            if row:
                ignore_ids.add(row["id"])
        reactions = _strip_ignored_resources(load_reactions(con, buffs=buffs), ignore_ids)
        resources = {r["id"]: r["name"] for r in con.execute("SELECT id, name FROM resources")}
        from collections import defaultdict

        edges = defaultdict(list)
        for i, reaction in enumerate(reactions):
            inputs = [rid for rid, rate in reaction["rates"].items() if rate < 0]
            outputs = [rid for rid, rate in reaction["rates"].items() if rate > 0]
            for source in inputs:
                for target in outputs:
                    edges[source].append((target, i))

        found = {}
        checked_supports = set()

        def evaluate(candidate_support, target_rid):
            candidate_support = tuple(sorted(candidate_support))
            if candidate_support in checked_supports:
                return
            checked_supports.add(candidate_support)
            touched = sorted(set().union(*(reactions[i]["rates"] for i in candidate_support)))
            matrix = [[
                reactions[reaction_i]["rates"].get(rid, 0.0) / reactions[reaction_i]["scale"]
                for reaction_i in candidate_support
            ] for rid in touched]
            constraints = [[-v for v in row] for row in matrix]
            constraints.append([1.0] * len(candidate_support))
            bounds = [0.0] * len(touched) + [1.0]

            candidates = [target_rid] + [
                rid for rid in touched
                if rid != target_rid
                and any(reactions[i]["rates"].get(rid, 0.0) < 0 for i in candidate_support)
                and any(reactions[i]["rates"].get(rid, 0.0) > 0 for i in candidate_support)
            ]
            target_i = touched.index(target_rid)
            optimum, scaled_activity = simplex_maximize(constraints, bounds, matrix[target_i])
            if optimum <= 1e-8:
                combined_objective = [
                    sum(matrix[row_i][j] for row_i in range(len(touched)))
                    for j in range(len(candidate_support))
                ]
                optimum, scaled_activity = simplex_maximize(constraints, bounds, combined_objective)
            best = None
            if optimum > 1e-8:
                local_support = tuple(i for i, value in enumerate(scaled_activity) if value > 1e-8)
                support = tuple(candidate_support[i] for i in local_support)
                activity = {
                    candidate_support[i]: scaled_activity[i] / reactions[candidate_support[i]]["scale"]
                    for i in local_support
                }
                net = {
                    rid: sum(reactions[i]["rates"].get(rid, 0.0) * activity[i] for i in support)
                    for rid in touched
                }
                if min(net.values()) < -1e-7:
                    return
                for candidate_rid in candidates:
                    consumed = -sum(
                        min(0.0, reactions[i]["rates"].get(candidate_rid, 0.0) * activity[i])
                        for i in support
                    )
                    produced = sum(
                        max(0.0, reactions[i]["rates"].get(candidate_rid, 0.0) * activity[i])
                        for i in support
                    )
                    if consumed <= 1e-10:
                        continue
                    gain = produced / consumed
                    if gain <= min_gain + 1e-8:
                        continue
                    positive = [
                        (resources[rid], value / consumed)
                        for rid, value in net.items() if value > 1e-8
                    ]
                    positive.sort()
                    best = {
                        "reactions": [(reactions[i], activity[i] / consumed) for i in support],
                        "positive": positive,
                        "target": resources[candidate_rid],
                        "gain": gain,
                    }
                    break
                if best is None:
                    # 循環資源自体は収支0で、循環外の副生成物だけが
                    # 増えるケースも閉ループである。倍率の分母が無いため
                    # 「純増」として報告する。
                    positive_rids = [rid for rid, value in net.items() if value > 1e-8]
                    if positive_rids:
                        byproduct_rid = max(positive_rids, key=lambda rid: net[rid])
                        positive = [(resources[rid], value) for rid, value in net.items() if value > 1e-8]
                        positive.sort()
                        best = {
                            "reactions": [(reactions[i], activity[i]) for i in support],
                            "positive": positive,
                            "target": resources[byproduct_rid],
                            "gain": None,
                        }
            if best is None:
                return
            key = tuple(sorted((r["agent_id"], r["recipe"]) for r, _ in best["reactions"]))
            previous = found.get(key)
            if previous is None or (
                best["gain"] is not None
                and (previous["gain"] is None or best["gain"] > previous["gain"])
            ):
                found[key] = best

        # まずLPを回さずにサイクル候補だけを集める。同じAgent集合に
        # 複数の資源サイクルがあっても1集合にまとめる。
        candidate_targets = defaultdict(set)
        for component in reaction_components(reactions):
            if len(component) < 2:
                continue
            for start in sorted(component):
                path_nodes = {start}

                def walk(node, path_reactions):
                    if len(path_reactions) >= max_depth:
                        return
                    for nxt, reaction_i in edges[node]:
                        if nxt not in component or reaction_i in path_reactions:
                            continue
                        if nxt == start:
                            if path_reactions:
                                support = tuple(sorted(path_reactions + (reaction_i,)))
                                candidate_targets[support].add(start)
                        elif nxt >= start and nxt not in path_nodes:
                            path_nodes.add(nxt)
                            walk(nxt, path_reactions + (reaction_i,))
                            path_nodes.remove(nxt)

                walk(start, ())

        # Agent数1から大きい順に検証する。成立した最小集合Aを含む
        # 上位集合は、Aと同じループを必ず含むためLP前に枝刈りする。
        identity_to_index = {
            (reaction["agent_id"], reaction["recipe"]): i
            for i, reaction in enumerate(reactions)
        }
        minimal_supports = []
        for support in sorted(candidate_targets, key=lambda item: (len(item), item)):
            support_set = set(support)
            if any(minimal < support_set for minimal in minimal_supports):
                continue
            evaluate(support, min(candidate_targets[support]))
            for key in found:
                found_support = {identity_to_index[identity] for identity in key}
                if found_support not in minimal_supports:
                    minimal_supports.append(found_support)

        results = list(found.values())
        # 同じ基本ループに変換工程を足しただけの包含系は、最小反応集合を残す。
        supports = [set((r["agent_id"], r["recipe"]) for r, _ in result["reactions"]) for result in results]
        minimal = []
        for i, result in enumerate(results):
            if any(other < supports[i] for j, other in enumerate(supports) if i != j):
                continue
            minimal.append(result)
        results = minimal
        results.sort(key=lambda r: (
            r["gain"] is None,
            -(r["gain"] or 0.0),
            len(r["reactions"]),
            r["target"],
        ))

        # CLI/JSON双方で使いやすいプレーンなdict形式に変換する
        plain = []
        for result in results:
            plain.append({
                "target": result["target"],
                "gain": result["gain"],
                "reactions": [
                    {"agent": r["name"], "basis": r["basis"], "activity": activity}
                    for r, activity in result["reactions"]
                ],
                "positive": [{"resource": name, "value": value} for name, value in result["positive"]],
            })
        return plain
    finally:
        if own:
            con.close()


# ============================================================
# CLI表示ヘルパー
# ============================================================

def print_table(rows, headers):
    if not rows:
        print("(該当なし)")
        return
    widths = [max(len(str(h)), max((len(str(r[i])) for r in rows), default=0)) for i, h in enumerate(headers)]
    fmt = "  ".join(f"{{:<{w}}}" for w in widths)
    print(fmt.format(*headers))
    print(fmt.format(*("-" * w for w in widths)))
    for r in rows:
        print(fmt.format(*(str(v) for v in r)))


def emit(args, data, headers=None, row_fn=None):
    """--jsonならJSON、それ以外ならテーブル表示する共通出口。
    headers/row_fnを渡すとdictのlistをテーブル整形できる。"""
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return
    if headers is None:
        print(data)
        return
    rows = [row_fn(d) for d in data] if row_fn else [tuple(d.values()) for d in data]
    print_table(rows, headers)


# ============================================================
# cmd_*: argparse Namespace -> query_*() 呼び出し -> 表示
# ============================================================

def cmd_agents(args):
    data = query_agents(args.name)
    emit(args, data, headers=["id", "name"])


def cmd_resources(args):
    data = query_resources(args.name)
    emit(args, data, headers=["id", "name"])


def cmd_terms(args):
    data = query_terms(args.name)
    emit(args, data, headers=["id", "name", "description"])


def cmd_agent_io(args):
    if not args.agent and not args.resource:
        sys.exit("--agent または --resource のいずれかを指定してください")
    data = query_agent_io(agent=args.agent, resource=args.resource)
    emit(args, data, headers=["agent", "recipe", "resource", "basis", "rate_per_cycle"])


def cmd_setups(args):
    data = query_setups()
    emit(args, data, headers=["id", "name"])


def cmd_balance(args):
    result = query_balance(args.setup)
    if result is None:
        sys.exit(f"setup が見つかりません: {args.setup}")
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    print(f"[{result['setup']['name']}] 収支(サイクルあたり):")
    print_table([(b["resource_name"], b["net_balance"]) for b in result["balance"]],
                ["resource", "net_balance"])


def cmd_gaps(args):
    data = query_gaps()
    emit(args, data, headers=["resource (未登録の可能性あり)"], row_fn=lambda d: (d["name"],))


def cmd_calories(args):
    ignore = tuple(args.ignore) if args.ignore else DEFAULT_IGNORE_RESOURCES
    # --exclude 未指定なら自動検出(query_loops)に任せる(None)。指定時のみ手動リストを使う。
    exclude_agents = tuple(args.exclude) if args.exclude else None
    result = query_calorie_yield(args.resource, ignore=ignore, exclude_agents=exclude_agents,
                                  buffs=tuple(args.buff or ()))
    if result is None:
        sys.exit(f"資源またはカロリーが見つかりません: {args.resource}")
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    if not result["reactions"]:
        if result.get("note"):
            print(f"[{result['resource']}] {result['target']} 1kgあたり: 無限大")
            print(result["note"])
        else:
            print(f"[{result['resource']}] から {result['target']} を生産する経路が見つかりませんでした。")
        return
    print(f"[{result['resource']}] 1kgあたりの最大{result['target']}生産量: "
          f"{result['kcal_per_kg']:.2f} kcal/kg")
    print(f"(除外資源: {', '.join(ignore)})")
    print(f"(自己増殖ループとして自動除外したAgent: {', '.join(result['excluded_agents']) or 'なし'})\n")
    print("使用するAgentと稼働比率(1kgあたり):")
    for r in result["reactions"]:
        print(f"  {r['agent']}[{r['basis']}]  x{r['activity']:.6g}")
    if result["byproducts"]:
        print("\n副産物(正味増加):")
        for b in result["byproducts"]:
            print(f"  {b['resource']} +{b['value']:.6g}")


def cmd_loops(args):
    results = query_loops(min_gain=args.min_gain, max_depth=args.max_depth,
                           buffs=tuple(args.buff or ()))
    results = results[: args.limit]

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    if not results:
        print("閉じた収支で資源が正味増加するループは見つかりませんでした。")
        return

    print(f"閉じた収支で資源が正味増加するループ: {len(results)}件")
    print("※ Agentの全入出力を不可分な反応式とし、電力を含む全消費をループ内で補う条件\n")
    for index, result in enumerate(results, 1):
        agents = " + ".join(f"{r['agent']}[{r['basis']}]" for r in result["reactions"])
        positives = ", ".join(f"{p['resource']} +{p['value']:.6g}" for p in result["positive"])
        if result["gain"] is None:
            print(f"[{index}] {result['target']} 純増: {agents}")
        else:
            print(f"[{index}] {result['target']} {result['gain']:.4f}倍: {agents}")
        print(f"    正味増加(正規化値): {positives}")


def build_parser():
    # --json はサブコマンドの前でも後でも使えるように、共通の親パーサーとして各サブコマンドにも継承させる
    json_parent = argparse.ArgumentParser(add_help=False)
    json_parent.add_argument("--json", action="store_true", help="結果をJSONで出力する")

    # 質量コストゼロの上位互換バフrecipe(既定除外)を有効化する共通オプション
    buff_parent = argparse.ArgumentParser(add_help=False)
    buff_parent.add_argument("--buff", action="append",
                              help="有効化するバフ名(例: グラブグラブ世話)。複数指定可。"
                                   "未指定時はrecipe名に該当バフを含む反応を計算から除外する")

    p = argparse.ArgumentParser(prog="onidb", description="ONI DB 読み取り専用CLI")
    sub = p.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("agents", help="Agent検索", parents=[json_parent])
    sp.add_argument("name", nargs="?", help="部分一致で検索(省略時は全件)")
    sp.set_defaults(func=cmd_agents)

    sp = sub.add_parser("resources", help="資源検索", parents=[json_parent])
    sp.add_argument("name", nargs="?", help="部分一致で検索(省略時は全件)")
    sp.set_defaults(func=cmd_resources)

    sp = sub.add_parser("terms", help="用語検索", parents=[json_parent])
    sp.add_argument("name", nargs="?", help="部分一致で検索(省略時は全件)")
    sp.set_defaults(func=cmd_terms)

    sp = sub.add_parser("io", help="Agentの入出力一覧、または資源を扱うAgent一覧", parents=[json_parent])
    sp.add_argument("--agent", help="Agent名で絞り込み")
    sp.add_argument("--resource", help="資源名で絞り込み")
    sp.set_defaults(func=cmd_agent_io)

    sp = sub.add_parser("setups", help="setup一覧", parents=[json_parent])
    sp.set_defaults(func=cmd_setups)

    sp = sub.add_parser("balance", help="setupの資源収支を計算", parents=[json_parent])
    sp.add_argument("setup", help="setup名またはid")
    sp.set_defaults(func=cmd_balance)

    sp = sub.add_parser("gaps", help="熱反応/加工系Agentの消費側に未登録の資源を洗い出す", parents=[json_parent])
    sp.set_defaults(func=cmd_gaps)

    sp = sub.add_parser("calories", help="指定資源1kgから最大どれだけカロリーを生産できるかをLPで解く",
                         parents=[json_parent, buff_parent])
    sp.add_argument("resource", help="起点となる資源名(部分一致)")
    sp.add_argument("--ignore", action="append",
                     help="balance制約から除外する資源(無制限に使える前提にする)。複数指定可。既定: 電力, 天然ガス")
    sp.add_argument("--exclude", action="append",
                     help="計算から除外するAgent名(質量保存則を破る特殊仕様など)。複数指定可。"
                          "既定: 水洗トイレ, 壁掛けトイレ, 野営トイレ")
    sp.set_defaults(func=cmd_calories)

    sp = sub.add_parser("loops", help="多入力を含む閉じた収支の増加ループを検出する",
                         parents=[json_parent, buff_parent])
    sp.add_argument("--max-depth", type=int, default=8, help="探索する最大反応数(既定8)")
    sp.add_argument("--min-gain", type=float, default=1.0, help="この倍率を超えるサイクルのみ報告(既定1.0)")
    sp.add_argument("--limit", type=int, default=50, help="表示件数上限(既定50)")
    sp.set_defaults(func=cmd_loops)

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
