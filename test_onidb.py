import sqlite3
import unittest

import onidb


def make_db(resources, reactions):
    """reactionsの各要素は (agent名, rates) または (agent名, recipe, rates)。"""
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.executescript("""
        CREATE TABLE agents (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE);
        CREATE TABLE resources (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE);
        CREATE TABLE agent_io (
            id INTEGER PRIMARY KEY,
            agent_id INTEGER NOT NULL,
            recipe TEXT NOT NULL DEFAULT '',
            resource_id INTEGER NOT NULL,
            rate_per_cycle REAL NOT NULL,
            basis TEXT NOT NULL
        );
    """)
    for resource_id, name in enumerate(resources, 1):
        con.execute("INSERT INTO resources(id, name) VALUES (?, ?)", (resource_id, name))
    name_to_id = {name: i for i, name in enumerate(resources, 1)}
    seen_agents = {}
    for entry in reactions:
        if len(entry) == 3:
            name, recipe, rates = entry
        else:
            name, rates = entry
            recipe = ""
        if name not in seen_agents:
            seen_agents[name] = len(seen_agents) + 1
            con.execute("INSERT INTO agents(id, name) VALUES (?, ?)", (seen_agents[name], name))
        for resource, rate in rates.items():
            con.execute(
                "INSERT INTO agent_io(agent_id, recipe, resource_id, rate_per_cycle, basis) "
                "VALUES (?, ?, ?, ?, 'active')",
                (seen_agents[name], recipe, name_to_id[resource], rate),
            )
    return con


def loop_supports(results):
    return [{r["agent"] for r in result["reactions"]} for result in results]


class LoopDetectionTests(unittest.TestCase):
    def test_simplex(self):
        value, solution = onidb.simplex_maximize([[1.0]], [1.0], [2.0])
        self.assertAlmostEqual(value, 2.0)
        self.assertAlmostEqual(solution[0], 1.0)

    def test_simplex_bland_rule_prevents_cycling(self):
        # Bealeの循環例。最急被約費用を選ぶDantzig則では同じ基底を
        # 巡回するが、Bland則なら有限回で最適値1へ到達する。
        value, solution = onidb.simplex_maximize(
            [
                [0.5, -5.5, -2.5, 9.0],
                [0.5, -1.5, -0.5, 1.0],
                [1.0, 0.0, 0.0, 0.0],
            ],
            [0.0, 0.0, 1.0],
            [10.0, -57.0, -9.0, -24.0],
            max_pivots=100,
        )
        self.assertAlmostEqual(value, 1.0)
        self.assertAlmostEqual(solution[0], 1.0)
        self.assertAlmostEqual(solution[2], 1.0)

    def test_missing_secondary_input_is_not_ignored(self):
        con = make_db(
            ["A", "B", "C"],
            [
                ("多入力反応", {"A": -1, "B": -1, "C": 10}),
                ("戻し反応", {"C": -1, "A": 1}),
            ],
        )
        self.assertEqual(onidb.query_loops(max_depth=4, con=con), [])

    def test_multi_input_closed_loop_is_detected(self):
        con = make_db(
            ["水", "電力", "原料", "燃料"],
            [
                ("採掘", {"水": -1, "電力": -1, "原料": 3}),
                ("精製", {"原料": -1, "燃料": 1}),
                ("発電", {"燃料": -1, "水": 0.5, "電力": 2}),
            ],
        )
        results = onidb.query_loops(max_depth=4, con=con)
        self.assertEqual(len(results), 1)
        self.assertEqual(loop_supports(results)[0], {"採掘", "精製", "発電"})
        self.assertGreater(results[0]["gain"], 1.0)

    def test_positive_byproduct_is_detected_when_cycle_start_is_balanced(self):
        con = make_db(
            ["A", "B", "C"],
            [
                ("生成", {"A": -1, "B": -1, "C": 3}),
                ("回収", {"C": -1, "A": 1, "B": 1}),
            ],
        )
        results = onidb.query_loops(max_depth=3, con=con)
        self.assertEqual(len(results), 1)
        self.assertIn(results[0]["target"], {"A", "B", "C"})
        self.assertAlmostEqual(results[0]["gain"], 3.0)

    def test_two_to_three_activity_ratio_can_create_a_pure_byproduct(self):
        con = make_db(
            ["A", "B", "副産物"],
            [
                ("反応1", {"A": -3, "B": 3}),
                ("反応2", {"B": -2, "A": 2, "副産物": 1}),
            ],
        )
        results = onidb.query_loops(max_depth=2, con=con)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["target"], "副産物")
        self.assertIsNone(results[0]["gain"])
        activities = {r["agent"]: r["activity"] for r in results[0]["reactions"]}
        self.assertAlmostEqual(activities["反応2"] / activities["反応1"], 1.5)

    def test_cycle_normalized_harvest_is_combined_with_agent_inputs(self):
        con = make_db(["餌", "収穫物"], [("植物", {"餌": -2, "収穫物": 1})])
        con.execute("UPDATE agent_io SET basis='harvest' WHERE rate_per_cycle > 0")
        reactions = onidb.load_reactions(con)
        self.assertEqual(len(reactions), 1)
        self.assertEqual(reactions[0]["basis"], "steady")
        self.assertEqual(set(reactions[0]["rates"].values()), {-2.0, 1.0})

    def test_real_database_detects_petroleum_and_sour_gas_routes(self):
        con = onidb.connect()
        supports = loop_supports(onidb.query_loops(max_depth=8, con=con))
        self.assertTrue(any({"油井", "熱分解(原油→石油)", "石油発電機(石油)"} <= support for support in supports))
        self.assertTrue(any({
            "油井",
            "熱分解(原油→石油)",
            "熱分解(石油→酸性ガス)",
            "気化(メタン(液体)→天然ガス)",
            "天然ガス発電機",
        } <= support for support in supports))


class BuffFilterTests(unittest.TestCase):
    """オプションゲート対象バフ(グラブグラブ世話)recipeの読み込みフィルタ。"""

    def make_buff_db(self):
        return make_db(
            ["水", "ベリー", "肥料"],
            [
                ("植物", "", {"水": -20, "ベリー": 0.1667}),
                ("植物", "農家の手", {"水": -20, "肥料": -1, "ベリー": 0.3334}),
                ("植物", "グラブグラブ世話", {"水": -20, "ベリー": 0.25}),
                ("植物", "農家の手+グラブグラブ世話", {"水": -20, "肥料": -1, "ベリー": 0.4168}),
            ],
        )

    def test_grubgrub_recipes_are_excluded_by_default(self):
        names = {r["name"] for r in onidb.load_reactions(self.make_buff_db())}
        self.assertEqual(names, {"植物", "植物(農家の手)"})

    def test_grubgrub_recipes_are_included_when_buff_enabled(self):
        names = {r["name"] for r in onidb.load_reactions(self.make_buff_db(),
                                                          buffs=("グラブグラブ世話",))}
        self.assertEqual(names, {
            "植物", "植物(農家の手)",
            "植物(グラブグラブ世話)", "植物(農家の手+グラブグラブ世話)",
        })

    def test_agent_name_containing_buff_is_not_filtered(self):
        # フィルタ対象はrecipe名のみ。Agent名『グラブグラブ』は影響を受けない。
        con = make_db(["硫黄", "泥"], [("グラブグラブ", {"硫黄": -50, "泥": 5})])
        self.assertEqual([r["name"] for r in onidb.load_reactions(con)], ["グラブグラブ"])

    def test_real_database_gates_grubgrub_recipes(self):
        con = onidb.connect()
        default_names = {r["name"] for r in onidb.load_reactions(con)}
        self.assertFalse(any("グラブグラブ世話" in name for name in default_names))
        buffed_names = {r["name"] for r in onidb.load_reactions(con, buffs=("グラブグラブ世話",))}
        self.assertIn("ブリッスル ブロッサム(グラブグラブ世話)", buffed_names)
        self.assertIn("ブリッスル ブロッサム(農家の手+グラブグラブ世話)", buffed_names)
        # 農家の手(肥料コストあり)と給餌+モー乳変種は常時有効
        self.assertIn("ブリッスル ブロッサム(農家の手)", default_names)
        self.assertIn("ハッチ(堆積岩+モー乳)", default_names)
        # 独立recipe『産卵』『産卵(モー乳)』は給餌recipeへ統合済みで存在しない
        self.assertFalse(any("産卵" in name for name in default_names))


if __name__ == "__main__":
    unittest.main()
