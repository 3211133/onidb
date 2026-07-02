-- Oxygen Not Included: 生産チェーン収支計算用データベース
-- Agent(建物/動物/植物を統一した「資源を入出力する主体」)モデル
PRAGMA foreign_keys = ON;

CREATE TABLE agents (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE resources (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

-- 収支計算の対象外(資源を入出力しない)だが用語として記録しておきたいもの。
-- 装飾専用植物、単発採取の資源ノード、データ未確定の生物・植物などが該当。
CREATE TABLE terms (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL UNIQUE,
    description TEXT
);

-- Agentごとの入出力レート(1個体/1台・1サイクル(600秒)あたり)
-- rate_per_cycle: 正=生産, 負=消費
-- basis: 発生条件 (always=常時, active=稼働時, harvest=刈り取り, eat=食事時, death=死亡時)
-- recipe: 同一Agent(建物/生物)が複数レシピを持つ場合の区別子。''はそのAgentの唯一/既定の挙動。
--         同じ(agent_id, recipe)を持つ行の集合が「不可分な1つの反応式」(全入力が同時に必要)を表す。
--         歴史的経緯: 以前は「精錬装置(銅鉱→銅)」のようにレシピを別Agent名として埋め込んでいた。
--         新規登録はrecipe列を使い、既存の名前埋め込みAgentは段階的に移行する。
CREATE TABLE agent_io (
    id             INTEGER PRIMARY KEY,
    agent_id       INTEGER NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    recipe         TEXT NOT NULL DEFAULT '',
    resource_id    INTEGER NOT NULL REFERENCES resources(id) ON DELETE CASCADE,
    rate_per_cycle REAL NOT NULL,
    basis          TEXT NOT NULL CHECK (basis IN ('always','active','harvest','eat','death')),
    UNIQUE(agent_id, recipe, resource_id, basis)
);

-- 構成(複数Agentを組み合わせたレイアウト案)
CREATE TABLE setups (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

-- 構成に含まれるAgentとその個体数/台数
-- recipe: そのAgentをどのレシピで稼働させるか(建物は同時に1レシピしか実行できないため、
--         「どのレシピで何台」を指定する)。''はレシピ区別のないAgent。
CREATE TABLE setup_agents (
    id        INTEGER PRIMARY KEY,
    setup_id  INTEGER NOT NULL REFERENCES setups(id) ON DELETE CASCADE,
    agent_id  INTEGER NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    recipe    TEXT NOT NULL DEFAULT '',
    quantity  INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
    UNIQUE(setup_id, agent_id, recipe)
);

-- 構成ごとの資源収支(生産-消費)を自動計算するビュー
CREATE VIEW setup_balance AS
SELECT
    s.id          AS setup_id,
    s.name        AS setup_name,
    r.id          AS resource_id,
    r.name        AS resource_name,
    SUM(aio.rate_per_cycle * sa.quantity) AS net_balance
FROM setup_agents sa
JOIN agent_io aio ON aio.agent_id = sa.agent_id AND aio.recipe = sa.recipe
JOIN resources r  ON r.id = aio.resource_id
JOIN setups s     ON s.id = sa.setup_id
GROUP BY s.id, r.id;

-- Agent単体の入出力一覧
CREATE VIEW agent_io_detail AS
SELECT
    a.name AS agent_name,
    aio.recipe AS recipe,
    r.name AS resource_name,
    aio.basis,
    aio.rate_per_cycle
FROM agent_io aio
JOIN agents a ON a.id = aio.agent_id
JOIN resources r ON r.id = aio.resource_id;
