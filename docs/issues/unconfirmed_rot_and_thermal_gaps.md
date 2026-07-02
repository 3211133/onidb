# 未確認の腐敗/熱反応 残課題

## 腐敗(Spoil)未確認の食品系資源
以下はWikiページが404、またはSpoil Time(腐敗までの日数)の記載が見つからず、腐敗Agent登録を保留した。
確度の低い推測での登録を避けるため、要再調査。

- モー乳 (Moo Milk) — ページ404
- ガス草由来「植物の殻」(Plant Husk) — 腐敗情報の記載なし。食品(Edible)タグかどうかも未確認
- トニックルート (Tonic Root) — 腐敗情報の記載なし。生食可能かどうかも未確認
- ネクター (Nectar) — 腐敗情報の記載なし
- ピンチャペッパー (Pincha Peppernuts) — 腐敗情報の記載なし
- ツユシボリのツユ (Dewdrip) — 日本語化MOD訳を確認済み。腐敗可否は未確認
- ミミレット — 該当英語名を未特定(要調査してから再検索)
- ミールウッド (Mealwood、放牧的に直接消費される葉/木部分。ミールライス側は期限切れ(ミールライス)で既に登録済み)
- リード繊維 — ユーザーの過去の指示により厳密化不要と明言済み([[project_oni_db_terms_table]]参照)
- 卵、藻類、雪ん小麦の種籾 — 個別未調査

登録済み(確実なSpoil Time記載あり): ノッシュ豆(8cyc)・ノリ(32cyc)・レタス(4cyc)・硬い肉(4cyc) → 腐った塊

## 熱反応(融解方向)未確認
- ムチン (Mucus) の「凝固(ムチン→凍結ムチン)」— wiki.gg "Slime Mold Mucus"ページが404。既存の融解(凍結ムチン→ムチン)の逆反応にあたるが未登録。要ページ名再調査。
- ナフサ(液体)の凝固点/凍結生成物 — 未調査
- 塩(Salt)のさらなる相変化 — 未調査(おそらく最終生成物で反応なしと推定されるが未確認)

## 経緯
ユーザーからの「加熱した結果何らかの変換自体はされるということですね」「加熱残はある？」「冷却方面で登録漏れはありますか」という一連の指摘を受け、SQLで機械的に「熱反応系Agentの消費側に未登録の資源」を洗い出す手法を確立した([[project_oni_db_terms_table]])。今後もこのSQLクエリで定期的に再チェックすることを推奨:

```sql
SELECT r.name FROM resources r
WHERE r.id NOT IN (
  SELECT ai.resource_id FROM agent_io ai
  JOIN agents a ON a.id = ai.agent_id
  WHERE (a.name LIKE '融解(%' OR a.name LIKE '昇華(%' OR a.name LIKE '気化(%'
      OR a.name LIKE '凝縮(%' OR a.name LIKE '凝固(%' OR a.name LIKE '分解(%'
      OR a.name LIKE '腐敗(%' OR a.name LIKE '焼成(%' OR a.name LIKE '焼成窯(%' OR a.name LIKE '%粉砕機(%'
      OR a.name LIKE '期限切れ(%' OR a.name LIKE 'コンポスト(%')
    AND ai.rate_per_cycle < 0
)
ORDER BY r.name;
```

また、「先頭のリンク付き生成物のみが実際の単一/主生成物で、後続の裸アイコン(リンクなし)は凡例ノイズ」という判別手法もこの過程で確立した(Granite/Sandstone/Coquina/Magma等で繰り返し確認)。WebFetchで多重生成物が返ってきた場合はこのパターンをまず疑い、raw HTML/リンクの有無で厳密に再確認すること。
