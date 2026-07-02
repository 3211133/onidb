# 日本語化MOD公式訳への用語統一 進捗メモ

## 目的
~/Claude/oni-db の resources / agents / terms にある日本語名を、
Steam Workshop「Japanese Language Pack」(ID 928606476, GitHub: nsk4762jp/OxygenNotIncluded-Japanese)
の公式訳語に統一する。現状は独自に逐次翻訳しており、表記ゆれ・重複が多数ある。

## 作業手順
1. https://raw.githubusercontent.com/nsk4762jp/OxygenNotIncluded-Japanese/master/strings.po を
   `/tmp/oni_ja.po` にダウンロード(curl)。再開時は再ダウンロードが必要(/tmpは揮発)。
2. awk/grepでカテゴリごとに `msgctxt "STRINGS.xxx.NAME"` → 次のmsgid(英語)/msgstr(日本語)を抽出。
   例:
   ```
   awk '/msgctxt "STRINGS.CREATURES.SPECIES.*\.NAME"$/{ctx=$0; getline; getline jp; print ctx" || "jp}' /tmp/oni_ja.po
   ```
3. 抽出した英語名でDBのresources/agents/termsの既存エントリと突き合わせ、
   `UPDATE` 文で公式訳に一括置換。重複が発生する場合は統合(agent_io/termsの行を移すかDELETE)。
4. 本ファイルに進捗を都度追記し、中断・再開できるようにする。

## カテゴリ別ステータス

### クリッター・植物 (STRINGS.CREATURES.SPECIES.*) — ✅完了 (DB反映済み、リビルド検証OK)
185件抽出済み(/tmp/critter_names.txtに保存、揮発するため再実行が必要な場合は上記awkコマンドを再実行)。

主な訂正例(現行DB名 → 公式訳):
- プフト → パフ (PUFT)
- プフトプリンス → パフ プリンス (PUFT.VARIANT_ALPHA)
- スクイーキープフト → やかまし パフ (PUFT.VARIANT_BLEACHSTONE)
- デンスプフト → こってり パフ (PUFT.VARIANT_OXYLITE)
- ガッシームー → ぷすぷす モー (MOO)
- ハスキームー → ハスキー モー (DIESELMOO) ※ほぼ一致
- ストーンハッチ → ごつごつ ハッチ (HATCH.VARIANT_HARD)
- スムースハッチ → つるつる ハッチ (HATCH.VARIANT_METAL)
- グロッシードレッコ → つやつや ドレッコ (DRECKO.VARIANT_PLASTIC)
- トロピカルパクー → 熱帯パクー (PACU.VARIANT_TROPICAL)
- ガルプフィッシュ → がぶ飲み フィッシュ (PACU.VARIANT_CLEANER)
- デレクタボール → うまうまネズミ (MOLE.VARIANT_DELICACY)
- ニット → ブヤ (MOSQUITO)
- シャタープロックス → ワレモノフロックス (GLASSDEER)
- リーガルバンモス → オウサマバンモス (ICEBELLY.VARIANT_GOLD)
- ロングヘアスリックスター → ふさふさ スリックスター (OILFLOATER.VARIANT_DECOR)
- モルテンスリックスター → とろとろ スリックスター (OILFLOATER.VARIANT_HIGHTEMP)
- スロゴ → スロッゴ (SNAIL)
- ギルドゴ → グリッゴ (SNAIL.VARIANT_IRON)
- シークワイン → シークイン (SEAHORSE)
- オアハル → オレハル (SEATURTLE)
- グローイカ → グロー イカ (SQUID、スペースあり)
- アビスバグ → アビス バグ (LIGHTBUG.VARIANT_BLACK)
- ラディアントバグ → 煌き バグ (LIGHTBUG.VARIANT_CRYSTAL)
- ブラムラム → ブラム ラム (ALGAE_STEGO、スペースあり)
- ラム → ラム (STEGO、一致)
- フロックス → フロックス (WOODDEER、一致)
- ドレッコ・パクー・ピップ・ぐりぐりネズミ・モーブ・シャインバグ・スリックスター・ビータ・ミミカ・
  スウィートル・グラブグラブ・レックス・ダートル・バンモス・ビーコン・ケルポール・ジョーボ・
  ポークシェル・サニシェル・オークシェル・ハッチ → 一致(変更不要)

植物側の主な訂正(現行DB名 → 公式訳、CREATURES.SPECIES内に植物も混在):
- ミールウッド(BASICSINGLEHARVESTPLANT) 一致
- シンブルリード → シンブル リード(BASICFABRICMATERIALPLANT、スペースあり)
- ベリードマックルート → 埋もれたムックルート(BASICFORAGEPLANTPLANTED)
- ノッシュスプラウト → ノッシュの木(BEAN_PLANT)
- アルベオベラ → エアロベラ(BLUE_GRASS)
- バルブルーム 一致(BULBLOOM)
- バディバッド → バディのつぼみ(BULBPLANT)
- ミミカバッド → ミミカのつぼみ(BUTTERFLYPLANT)
- ジャンピングジョイヤ → ジャンピング ジョヤ(CACTUSPLANT、スペースあり)
- プルームスクワッシュプラント → ハネナンキン(CARROTPLANT)
- クランパム → クランパン(CLAM)
- ウィーズワート → ウィーズウォート(COLDBREATHER)
- スリートウィート → 雪ん小麦(COLDWHEAT)
- サターンクリッタートラップ → ケモノジゴク(CRITTERTRAPPLANT)
- ブリスバースト → ブリス バースト(CYLINDRICA、スペースあり)
- デュードリッパー → ツユシボリ(DEWDRIPPERPLANT)
- ガムパーム → ゴムヤシ(DEWPALM)
- メガフロンド → 巨大シダ(DINOFERN)
- スポアキッド → 胞子ラン(EVILFLOWER)
- ペッタポーフ → ペッタ プフ(FILAMENTPLANT、スペースあり)
- フシャカップス → ミズサボテン(FILTERPLANT)
- ルラプラント → ルラ(FLYTRAPPLANT)
- ヘキサレント 一致(FORESTFORAGEPLANTPLANTED)
- リングローズブッシュ → リングローズの茨(GARDENDECORPLANT)
- スウェットコーンストーク → スウェットコーンの茎(GARDENFOODPLANT)
- スナクタス → スナックサボテン(GARDENFORAGEPLANTPLANTED)
- ガスグラス → ぷかぷか草(GASGRASS)
- パイクアップルブッシュ → パイクップルの低木(HARDSKINBERRYPLANT)
- アイディラフラワー → ボッカ(ICEFLOWER)
- シーコーム → シーコンブ(KELPPLANT)
- マースリーフ → マース リーフ(LEAFYPLANT、スペースあり)
- ダスクキャップ 一致(MUSHROOMPLANT)
- マッスルスプラウト → ムールの芽(MUSSELSPROUT)
- オキシファーン 一致
- フルーコーラル → フルー サンゴ(OXYCORAL、スペースあり)
- スターナクル → ホシツボ(PLANKTONCORAL)
- ブリッスルブロッサム → ブリッスル ブロッサム(PRICKLEFLOWER、スペースあり)
- ダシャソルトバイン → ダーシャ シオカズラ(SALTPLANT)
- ソディケーン → ソディケーン(SALTYSTICKSPLANT、一致)
- タワーケルプ → タワーケルプ(SEATREE、一致)
- シャーベリープラント → シャーベリー(ICECAVESFORAGEPLANTPLANTED)
- ボンボンツリー 一致(SPACETREE)
- ピンチャペッパー → ピンチャ ペッパー(SPICE_VINE、スペースあり)
- ボグバケット → ドロバケツ(SWAMPHARVESTPLANT)
- バームリリー 一致(SWAMPLILY)
- トゥブリア → チューブリア(TUBEWORM)
- ピンポケット 一致(URCHINPLANT)
- オバグロノード → オヴァグロ(VINEMOTHER)
- フーシャカップ(WATERCUPS、新規=旧フシャカップスとは別物。要注意: FILTERPLANT=ミズサボテン と
  WATERCUPS=フーシャカップ は別エンティティ。現行DBの「フシャカップス」はFILTERPLANT=ミズサボテンに対応するか要再確認)
- メロマロ(WINECUPS)
- アーバーツリー → アーバー ツリー(WOOD_TREE、スペースあり)
- グラブフルーツプラント → ひょろひょろグラブフルーツの木(WORMPLANT) ※要注意、Spindly側の可能性
- グラブグラブ(動物)とは別に SUPERWORMPLANT もあり要整理

**重要な不一致候補(要再調査):**
- FILTERPLANT=ミズサボテン と URCHINPLANT/WATERCUPS 周りの植物対応が現行DBの命名(フシャカップス等)と
  ズレている可能性が高い。Aquatic Planet Pack系植物は再マッピングが必要。
- WORMPLANT(ひょろひょろグラブフルーツの木) と SUPERWORMPLANT(グラブフルーツの木) の対応が
  現行の「グラブフルーツプラント」「スピンドリーグラブフルーツプラント」とどちらがどちらか要確認。

### 資源 (STRINGS.ELEMENTS.*) — 一部完了

**✅解決済み: 「にがり」の資源分割。**
旧「にがり」を以下3資源に分割し、各Agentを個別検証して再割当て済み:
- 濃塩水(Brine) — デサリネーター(濃塩水)消費、グリーナー(モー乳)生産、グロー イカ消費(原文"brine/polluted brine"と曖昧なため暫定採用、要再検証)
- 濃塩氷(Brine Ice) — ツユシボリ消費、レックス生産
- 汚染濃塩水(Polluted Brine) — チューブリア消費(wiki.gg "Tublia"で明記確認済み)

リビルド検証OK。

**確定済みの単純リネーム(済):**
- ブラッケン → モー乳 (MILK、Gassy Moo/ぷすぷすモーの搾乳産物)
- ブラックワックス → モー脂肪 (MILKFAT、Gleanerの副産物)
- オボレーン → オボレン (FISHMILK、表記ゆれのみ)
- 精製炭素 → 精錬炭素 (REFINEDCARBON、表記ゆれ)

**確認済みで一致していたもの(変更不要):**
水・氷・蒸気・酸素・二酸化炭素・原油・石油・塩・塩水・砂・土・硫黄・汚染水・汚染酸素・緑藻(藻類は要確認)

**未確認のまま残っているもの:** カビア(Caviar公式訳は本poファイルから未発見、再検索要)、
にがり分割問題の再割当て、その他の元素・アイテム系(218+179件)の網羅的突合せ。

### 建物 (STRINGS.BUILDINGS.PREFABS.*) — 主要設備は完了、家具・センサー・配線等は未着手

抽出コマンド: `awk '/msgctxt "STRINGS.BUILDINGS.PREFABS.*\.NAME"$/{ctx=$0; getline; getline jp; print ctx" || "jp}' /tmp/oni_ja.po`
結果は `/tmp/building_names.txt` に保存(963件、揮発するため再開時は再実行要)。

**✅完了した主要設備(20件以上のリネーム適用済み、リビルド検証OK):**
- デサリネーター → 淡水化装置
- エタノール蒸留器 → エタノール蒸留機
- グラスフォージ → ガラス工房
- 金属精錬機 → 精錬装置
- 石油精製プラント → 製油装置
- ロッククラッシャー → 岩石粉砕機
- ラストデオキシダイザー → 錆脱酸素装置
- ウォーターシーブ → 浄水機
- スチームタービン → 蒸気タービン(公式訳には「[陳腐化]」表記あり、game内で旧式扱いの可能性)
- ピートバーナー → 泥炭バーナー
- デオドライザー → 脱臭機
- 藻類テラリウム → テラリウム
- カーボンスキマー → 炭素スキマー
- オキシライト精製所 → オキシライト精錬装置
- オキシライトスコンス → オキシライト燭台
- 酸素ディフューザー → 酸素散布装置(内部キーMINERALDEOXIDIZER)
- マイクロブマッシャー → 微生物粉砕機
- ディープフライヤー → フライヤー
- キルン → 焼成窯
- 天然ガス発電機・石油発電機は元々公式訳と一致(変更不要)

**未着手:** termsテーブルに大量にある家具(Furniture)・センサー/ロジックゲート(Automation)・
配管/配線インフラ(Plumbing/Ventilation/Power)・医療(Medicine)・ロケット部品(Rocketry)の
日本語名(現在は私の逐次翻訳のまま)。建物963件のうち上記以外は未照合。

### 食品アイテム (STRINGS.ITEMS.FOOD.*) — ✅完了
99件抽出済み(`/tmp/all_food_names.txt`)、約50件をDBに反映・リビルド検証OK。

**重要な訂正:**
- 以前「実在しない資源」として削除した「ライスローフ」は、実は英語名Liceloaf(内部キーBASICPLANTBAR)の
  正式な日本語訳そのものだった。今回 `Liceloaf` → `ライスローフ` で再統一(削除は結果的に問題なかったが、
  理由付け「架空の資源」は誤りだったので訂正)。
- カラマリ → ゲソ(SQUIDMEAT)、フィッシュフィレ → 魚の切り身(FISHMEAT)、
  生シェルフィッシュ → 生の剥き身(SHELLFISHMEAT) など、英語名のままだった食材を軒並み訳語化。
- 硬い肉(Tough Meat)の調理後形態「Tender Brisket」の公式訳は「柔らかバラ肉」(SMOKEDDINOSAURMEAT)と判明。
  ただし質量(kg)は依然未確認のためAgent化はしていない。

**✅ELEMENTS主要鉱物・素材系も完了:**
シェール→頁岩、バサルト→玄武岩、コキーナ→石灰岩、コラリウム→サンゴ、サーミウム→テルミウム、
樹脂→サップ、汚染マッド→汚泥、マッド→泥、精製油→バイオディーゼル。
リネーム時に「汚泥」「泥」が既存の未使用/重複定義と衝突したため、不要だった重複定義を削除して解消
(L14の汚泥は使われていないダミー定義だった、L23の泥はグラブグラブの生産物と整合一致)。
resources件数 192→190。リビルド検証OK。

**✅ 英語名の完全解消**
resources/agentsテーブル内に残っていた英語名(Atmo Suit, Vitamin Chews, Pinpoki, Nectar,
Squash Fries等、計17件)を全て公式日本語訳に置換。最終確認で
`SELECT name FROM resources WHERE name GLOB '*[A-Za-z]*'` および同agentsクエリが
0件になることを確認済み(リビルド検証OK、resources 189件)。

**未着手:** ELEMENTS(218件中、ガス/液体/固体の温度状態違いバリエーション(*GAS, MOLTEN*, SOLID*等)は
今回未照合、ただしDB内でそうした状態違いは現状ほぼ使っていないため実害は小さい見込み)。
建物963件のうちtermsに格納された家具・センサー・配線・医療・ロケット部品は依然未着手。
抽出コマンド:
```
awk '/msgctxt "STRINGS.ELEMENTS.*\.NAME"$/{ctx=$0; getline; getline jp; print ctx" || "jp}' /tmp/oni_ja.po
awk '/msgctxt "STRINGS.ITEMS.*\.NAME"$/{ctx=$0; getline; getline jp; print ctx" || "jp}' /tmp/oni_ja.po
```

### 建物不要の自然な物質変化(相変化・自然分解) — ✅大部分完了
水(融解/凝固/気化/凝縮)に加え、以下を追加・検証済み(リビルドOK、相変化Agent計73件):
- 錆⇔溶融した鉄⇔鉄(融点1534.85℃、wiki.gg "Rust"より。鉄が自然に錆びる仕組みは存在しないことも確認)
- 期限切れ食品(49品目個別)→腐った塊→汚染土(1:1、wiki.gg "Rot Pile"より)
- 汚染水: 気化は蒸気99%+土1%の分離反応(単純な1:1ではない、wiki.gg "Polluted Water"より)、凍結は1:1
- 金属全般(銅・金・アルミ・コバルト・鉛・ニッケル・タングステン・ニオブ・亜鉛・鋼鉄)の融解/凝固、1:1質量保存
- ガラス(ガラス⇔溶融ガラス)
- 気体/液体/固体3態を持つ物質(硫黄・塩・石油・原油・エタノール・二酸化炭素・酸素・塩素・水素・天然ガス)の相変化、計17ペア
- 水銀(液体⇔気体)、サップ(液体⇔固体)、ムチン(液体⇔凍結)、スクロース(固体⇔液体)

**副次的に発見・修正した命名誤り:**
- 「精錬金属」は元々Copper専用の仮資源だったが、Plug Slug/Smooth Hatchの「任意の金属」用途と混在していた
  → 銅専用部分のみ「銅」資源に分離、汎用部分は「精錬金属」のまま維持
- 液体硫黄→液化硫黄、液体酸素→酸素(液体)、液体塩素→塩素(液体)、塩素ガス→塩素(気体)、
  ムシン→ムチン(いずれも公式訳との表記ゆれを修正)

**未着手:** Helium, Phosphorus, Propane, Naphtha, Viscogel, Syngas, Supercoolantなど、
現状DBで未使用の物質の相変化(これらはどのAgentからも参照されていないため優先度低)。

**✅ 「揮発」(昇華・固体→気体の直接変化)も追加調査・対応済み:**
- オキシライト→酸素(質量の50%、wiki.gg "Oxylite"より)。オキシライトスコンス建物とは別に、
  建物なしの自然昇華として登録(従来の建物経由レートとは比率が異なる点に注意)
- 漂白石→塩素(気体)(1:1、速度は質量比例だが比率自体は質量保存則を適用)
- スライム・汚染土も自然昇華するが、放出速度が質量に非線形(平方根)依存し、
  デブリの分割数にも依存するため、固定kg/cycleレートとして登録不可と判断しterms化
  (Sublimatorカテゴリ全体を調査し網羅、wiki.gg "Category:Sublimators"より)

### DB反映 — ✅完了 (2026-07-01、現行MOD版で再照合)
- `STRINGS.*.NAME` の内部ID、英語原名、日本語訳が一意に対応するもののみ反映。
- agents 32件、terms 241件を現行訳へ更新。resourcesは今回の確定置換なし。
- 主な変更: ラバトリー→水洗トイレ、アウトハウス→野営トイレ、シンク→流し台、
  ウォッシュベイスン→洗面台、プラグスラグ→びりびりナメクジ、藻類蒸留器→蒸留機。
- `Flower Pot` は基本設備の `FLOWERVASE.NAME`=「植木鉢」、`Mini Fridge` は
  `MINIFRIDGE.NAME`=「小型冷蔵庫」を採用し、ファサードや小道具用の同英名エントリと区別。
- 未一致12件は産卵・相変化・気体ルート確認などのDB独自名、または対応先を
  一意に確定できない「クリッタールアー」であり、意図的に維持。
- `schema.sql + seed.sql` からの再構築、`integrity_check`、`foreign_key_check`、現行DBと再構築DBの
  dumpハッシュ一致を確認済み。

## 再開手順(レートリミット等で中断した場合)
1. このファイルの「カテゴリ別ステータス」で「未着手」となっている項目から再開する。
2. /tmp/oni_ja.po が無ければ再ダウンロード(冒頭のcurlコマンド参照)。
3. 完了したカテゴリは見出しを「✅完了」に書き換える。
