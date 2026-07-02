# 卵・孵化幼体〆データ調査レポート

作成日: 2026-07-03 / 調査元: oxygennotincluded.wiki.gg(Egg / Egg Cracker / Raw Egg / Egg Shell / Meat / 各クリッター個別ページ)

本レポートは読み取り専用調査。seed.sql / schema.sql / onidb.py / oni.db は変更していない。
数値の質量換算は原則 **kcal ÷ 1600 kcal/kg = kg**(生卵・肉とも 1600 kcal/kg、下記で検証)を使用。
未確認 = wiki 該当ページに記載を確認できなかった値(捏造しない)。

主要ソースURL:
- Egg一覧: https://oxygennotincluded.wiki.gg/wiki/Egg
- 卵割り機: https://oxygennotincluded.wiki.gg/wiki/Egg_Cracker
- 卵の中身: https://oxygennotincluded.wiki.gg/wiki/Raw_Egg (1600 kcal/kg を明記)
- 卵の殻: https://oxygennotincluded.wiki.gg/wiki/Egg_Shell
- 肉: https://oxygennotincluded.wiki.gg/wiki/Meat (1600 kcal/kg、および「幼体は成体と同量をドロップ」の記載)

---

## 1. 卵1つあたりの質量(種別)

| 種(日本語/DB名) | 卵 | 卵質量 kg | DB登録 | ソース |
|---|---|---|---|---|
| ハッチ系(無印/セイジ/ごつごつ/つるつる) | Hatch Egg 各種 | 2 | あり(4種) | https://oxygennotincluded.wiki.gg/wiki/Egg |
| ドレッコ / つやつやドレッコ | Drecko / Glossy Drecko Egg | 2 | あり | 同上 |
| パフ系(無印/やかまし/こってり/プリンス) | Puft Egg 各種 | 0.5 | あり(4種) | 同上 |
| パクー / 熱帯パクー / がぶ飲みフィッシュ | Pacu / Tropical / Gulp Fish Egg | 0.75 | あり | 同上 |
| ピップ(+Cuddle Pip) | Pip Egg | 2 | あり(Cuddleは未登録) | 同上 |
| ポークシェル / オークシェル / サニシェル | 各 Roe | 2 | あり | 同上 |
| スリックスター系(無印/とろとろ/ふさふさ) | Slickster Egg 各種 | 2 | あり | 同上 |
| シャインバグ系(煌き/アビス含む全モーフ) | Shine Bug Egg 各種 | 0.2 | あり(3種) | 同上 |
| ぐりぐりネズミ(Shove Vole)/ うまうまネズミ(Delecta Vole) | Vole Egg | 2 | あり | 同上 |
| バンモス / オウサマバンモス | Bammoth Egg | 8 | あり | 同上 |
| フロックス / ワレモノフロックス | Flox Egg | 2 | あり | 同上 |
| パッキンアシカ(Spigot Seal) | Spigot Seal Egg | 2 | あり | 同上 |
| グラブグラブ / スウィートル(Divergent) | Grubgrub Wormling / Sweetle Egg | 2 | あり | 同上 |
| ナメクジ系(びりびり/スポンジ/スモッグ, Plug Slug) | Plug Slug Egg 各種 | 2 | あり | 同上 |
| ダートル(Dartle) | Dartle Egg | 2 | あり | 同上 |
| ジョーボ(Jawbo) | Jawbo Egg | 3 | あり | 同上 |
| レックス(Rhex) | Rhex Egg | 8 | あり | 同上 |
| ラム / ブラムラム(Lumb / Blum Lumb) | Lumb Egg | 8 | あり | 同上 |
| ビーコン(Beakon) | Beakon Egg | 0.75 | あり | 同上 |
| ブローター(Blowter) | Blowter Egg | 2 | あり | 同上 |
| オレハル(Orehull) | Orehull Egg | 3 | あり | 同上 |
| シークイン(Seaquine) | Seaquine Egg | 2 | あり | 同上 |
| スロッゴ / グリッゴ(Slogo / Gildgo) | Slogo / Gildgo Egg | 0.5 | あり | 同上 |
| ガッシーモー(Gassy Moo) | **卵なし**(Mooteor で増殖) | — | DBに「ぷすぷすモー」「ハスキーモー」あり(対応は下記注) | https://oxygennotincluded.wiki.gg/wiki/Gassy_Moo |
| ムークリ(Moo Kri?) | — | 未確認 | **DB未登録** | — |
| グロー・スクイッド(Glo Squid) | Glo Squid Egg | 2 | 未登録? (要確認) | https://oxygennotincluded.wiki.gg/wiki/Egg |
| ニット(Gnit) | Gnit Egg | 1(**割れない卵**) | 未登録 | 同上 |

注: DBの「ぷすぷすモー」「ハスキーモー」がどの英語名モー(Gassy Moo 等)に対応するかは wiki 側で日本語名を確認できず **未確認**。Gassy Moo は産卵しないため卵フローは不要。

---

## 2. 卵割り機(Egg Cracker)の出力(殻の有無と分割)

換算式: 卵の中身 kg = 表示kcal ÷ 1600 kcal/kg。合計検算 = 中身 + 殻 と卵質量の比較。

| 卵 | 卵質量 kg | 卵の中身 (kcal → kg) | 卵の殻 kg | 中身:殻 | 50/50? | ソース |
|---|---|---|---|---|---|---|
| ハッチ/ドレッコ/ピップ/スリックスター/ポークシェル系/Vole系/フロックス/Divergent/Plug Slug/アシカ/ダートル/ブローター/シークイン等の「標準2kg卵」 | 2 | 1600 → 1.0 | 1.0 | 1:1 | ○ | https://oxygennotincluded.wiki.gg/wiki/Egg_Cracker |
| パフ系 | 0.5 | 400 → 0.25 | 0.25 | 1:1 | ○ | 同上 |
| シャインバグ系 | 0.2 | 160 → 0.1 | 0.1 | 1:1 | ○ | 同上 |
| バンモス/ラム/レックス(8kg卵) | 8 | 6400 → 4.0 | 4.0 | 1:1 | ○ | 同上 |
| ジョーボ / オレハル(3kg卵) | 3 | 3200 → 2.0 | 1.0 | **2:1** | **×** | https://oxygennotincluded.wiki.gg/wiki/Egg_Cracker, https://oxygennotincluded.wiki.gg/wiki/Egg |
| パクー/熱帯パクー/がぶ飲み(0.75kg卵) | 0.75 | 1200 → 0.75 | **0(殻なし)** | 1:0 | **×** | 同上(Egg ページに "Produces no Egg Shell when cracked" 明記) |
| ビーコン(0.75kg卵) | 0.75 | 未確認(推定 1200 kcal) | **0(殻なし)** | 1:0 | × | https://oxygennotincluded.wiki.gg/wiki/Egg |
| スロッゴ/グリッゴ(0.5kg卵) | 0.5 | 未確認(推定 800 kcal) | **0(殻なし)** | 1:0 | × | 同上 |
| グロー・スクイッド | 2 | 未確認 | **0(殻なし)** | — | × | 同上 |
| ニット(Gnit) | 1 | **割れない(卵割り機不可)** | — | — | — | 同上 |

補足(Egg_Shell ページ): 「どの卵も孵化後/破壊時に殻を残す」とあるが、水棲系(魚卵)は卵割り機で殻を産出しない点が Egg ページで個別に明記されており、後者を優先。シャインバグ卵の殻は 100 g。Egg Cracker ページの WebFetch 要約に「Shine Bug 卵 → Resin 5kg」という記述が返ったが他ソースと整合せず **信頼性低・未確認** として不採用。

---

## 3. 卵の中身(Raw Egg)の質量と kcal

- Raw Egg のカロリー密度: **1600 kcal/kg**(https://oxygennotincluded.wiki.gg/wiki/Raw_Egg)
- 種別の中身 kcal(卵割り機表示、上表と同値): 標準2kg卵 1600 kcal (1kg) / パフ 400 kcal (0.25kg) / シャインバグ 160 kcal (0.1kg) / パクー 1200 kcal (0.75kg) / ジョーボ・オレハル 3200 kcal (2kg) / 8kg卵 6400 kcal (4kg)。
- kcal/kg は全卵種で一定 1600。**種によって変わるのは質量のみ**。

---

## 4. 孵化直後の幼体を〆たときの生産物

Meat ページに「幼体および大半のモーフは成体と同量をドロップする」と記載(https://oxygennotincluded.wiki.gg/wiki/Meat)。よって断りのない限り幼体=成体ドロップ。例外はポークシェル系幼体。換算: kg = kcal ÷ 1600(肉・切り身系)。

| 種 | 生産物 | 量(成体=幼体) | ソース |
|---|---|---|---|
| ハッチ系(全4種) | 肉 | 3200 kcal = 2 kg | https://oxygennotincluded.wiki.gg/wiki/Hatch, /wiki/Meat |
| ドレッコ / つやつや | 肉 | 2 kg | https://oxygennotincluded.wiki.gg/wiki/Meat |
| パフ系(全4種) | 肉 | 1600 kcal = 1 kg | https://oxygennotincluded.wiki.gg/wiki/Puft |
| ピップ / Cuddle Pip | 肉 | 1600 kcal = 1 kg | https://oxygennotincluded.wiki.gg/wiki/Pip |
| スリックスター系(全3種) | 肉 | 3200 kcal = 2 kg | https://oxygennotincluded.wiki.gg/wiki/Slickster |
| パクー/熱帯/がぶ飲み | **魚の切り身** | 1000 kcal = 0.625 kg | https://oxygennotincluded.wiki.gg/wiki/Pacu |
| シャインバグ系 | **なし**(0 kg) | 0 | https://oxygennotincluded.wiki.gg/wiki/Meat(Shine Bug は 0 kg と明記) |
| ポークシェル(成体) | **生シェルフィッシュ + モルト** | 1200 kcal = 0.75 kg + モルト 60 kg(モルト量は要再確認) | https://oxygennotincluded.wiki.gg/wiki/Pokeshell |
| ポークシェル(幼体) | **モルトのみ** | 5 kg(生シェルフィッシュなし=幼体〆の例外) | 同上 |
| サニシェル | 生シェルフィッシュ | 4000 kcal = 2.5 kg(モルトなし) | 同上 |
| オークシェル | モルト系(死亡時 500 kg 木質モルトとの記述、要再確認) | 未確認 | 同上 |
| ぐりぐりネズミ(Shove Vole) | 肉 | 16000 kcal = 10 kg | https://oxygennotincluded.wiki.gg/wiki/Shove_Vole |
| うまうまネズミ(Delecta Vole) | 肉 | 8000 kcal = 5 kg | 同上 |
| バンモス / オウサマ | 肉 | 22400 kcal = 14 kg | https://oxygennotincluded.wiki.gg/wiki/Bammoth, /wiki/Meat |
| フロックス / ワレモノ | 肉 | 1600 kcal = 1 kg | https://oxygennotincluded.wiki.gg/wiki/Flox |
| ガッシーモー | 肉 | 16000 kcal = 10 kg(ただし卵なし) | https://oxygennotincluded.wiki.gg/wiki/Gassy_Moo |
| スウィートル | 肉 | 1600 kcal = 1 kg | https://oxygennotincluded.wiki.gg/wiki/Divergent |
| グラブグラブ | 肉 | 4800 kcal = 3 kg | 同上 |
| ナメクジ系(Plug Slug) | 肉 | 2 kg | https://oxygennotincluded.wiki.gg/wiki/Meat |
| パッキンアシカ | **獣脂(Tallow)** | 50 kg | https://oxygennotincluded.wiki.gg/wiki/Spigot_Seal |
| ダートル | 肉 | 800 kcal = 0.5 kg | https://oxygennotincluded.wiki.gg/wiki/Dartle |
| ジョーボ | **ジョーボの切り身** | 12000 kcal(切り身のkcal/kg未確認のため kg 未確認) | https://oxygennotincluded.wiki.gg/wiki/Jawbo |
| レックス | **硬い肉(Tough Meat)** | 5 kg | https://oxygennotincluded.wiki.gg/wiki/Rhex |
| ラム / ブラムラム | 硬い肉 | 12 kg | https://oxygennotincluded.wiki.gg/wiki/Lumb |
| スロッゴ / グリッゴ | 肉 | 800 kcal = 0.5 kg | https://oxygennotincluded.wiki.gg/wiki/Slogo |
| ビーコン | 魚の切り身 | 1000 kcal = 0.625 kg | https://oxygennotincluded.wiki.gg/wiki/Beakon |
| ブローター / シークイン / オレハル | 未確認 | 未確認 | — |
| モーブ | なし(0 kg) | 0 | https://oxygennotincluded.wiki.gg/wiki/Meat |

---

## 5. 分析: 種間で一様なもの / 種別が必要なもの

### 5.1 一様(pooled のままで成立)
- **Raw Egg のカロリー密度 1600 kcal/kg**: 全卵種共通。中身の質量だけが変わる。
- **殻ありの陸上卵の 50/50 分割**: 0.2 / 0.5 / 2 / 8 kg 卵すべてで中身:殻 = 1:1 が成立。
- **肉 1600 kcal/kg**: 肉ドロップ種すべてで kcal↔kg が一致(検算済み)。

### 5.2 50/50 ルールを破る種
- **魚卵(パクー系・ビーコン・スロッゴ/グリッゴ・グロースクイッド)**: 殻ゼロ、卵質量 = ほぼ全量が中身。
- **ジョーボ / オレハル(3kg卵)**: 中身 2kg + 殻 1kg = **2:1**。
- **ニット(Gnit)**: そもそも割れない。

### 5.3 「標準2kg卵」を破る種
0.2kg(シャインバグ系)、0.5kg(パフ系、スロッゴ/グリッゴ)、0.75kg(パクー系、ビーコン)、1kg(ニット)、3kg(ジョーボ、オレハル)、8kg(バンモス系、ラム系、レックス)。

### 5.4 孵化→〆生産物と卵質量の相関
生産物は肉/切り身/硬い肉/生シェルフィッシュ/獣脂/なし と多様で、**卵質量とは相関しない**。例: 同じ2kg卵でも ドレッコ=肉2kg、ピップ=肉1kg、シャインバグ0.2kg卵=0kg、パッキンアシカ2kg卵=獣脂50kg、バンモス8kg卵=肉14kg(卵の1.75倍)。〆生産は完全に種固有パラメータ。

### 5.5 DBへの示唆
現状 DB は単一プール資源『卵』(2kg標準卵前提の卵割り機 2kg→中身1kg+殻1kg、seed.sql 4015行付近)であり、産卵側は種別レートで『卵』に合流している。

**プールのままで良いフロー**:
- 殻あり陸上卵 → 卵割り機 の質量分割(50/50)は卵質量に対して線形なので、『卵』を kg プールとして扱う限り 卵割り機の入出力比 (−2 / +1 / +1) は 2kg卵・0.5kg卵・8kg卵を混ぜても質量比として正しい。
- 卵の殻→岩石粉砕機、卵の中身→グリル/期限切れ の下流もプールで問題なし。

**種別資源が必要なフロー**:
1. **魚卵系(パクー/熱帯/がぶ飲み/ビーコン/スロッゴ/グリッゴ)**: 殻ゼロなので現行比率だと殻を過大計上。少なくとも『魚卵』プール(卵割り機: −X → 中身X、殻0)を分離すべき。
2. **ジョーボ/オレハル卵**: 2:1 分割の別エージェント行が必要。
3. **孵化→〆(繁殖余剰の食肉化)**: 生産物種と量が完全に種固有。プール『卵』からは種情報が失われるため、〆フローをモデル化するなら卵を種別資源にするか、〆をエージェント側(各クリッターの death 行、既に一部存在: ハッチ肉2kg等)で持ち続けて卵→幼体の変換を種別に紐付ける必要がある。
4. **ニット卵**: 卵割り機に入れられないため、プールに合流させると誤り。

最小変更案: 『卵』を『卵(殻あり50/50)』『魚卵(殻なし)』『卵(2:1系)』の3プール+ニット除外に分割すれば、卵割り機フローは3行で正確になり、〆フローのみ種別 death/harvest 行で扱う、という構成が質量保存的に整合する。

---

## 6. 未確認事項(今後の課題)
- ビーコン/スロッゴ/グリッゴ/グロースクイッド卵の中身 kcal(質量からの推定値のみ)
- ジョーボの切り身・硬い肉・獣脂・生シェルフィッシュの kcal/kg(切り身は 1600 kcal/kg なら 0.625kg で seed.sql の既存値と整合)
- ポークシェル成体モルト 60kg / オークシェル死亡 500kg の正確値
- ぷすぷすモー/ハスキーモーの英語名対応
- ムークリの存在・データ(DB未登録)
- Egg Cracker ページ由来「シャインバグ卵→レジン5kg」記述(他ソースと矛盾、不採用)
