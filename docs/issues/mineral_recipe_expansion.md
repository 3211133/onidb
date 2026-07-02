# 汎用資源「鉱物」の廃止と資源別レシピへの横展開 + 産卵の給餌recipe統合

作業日: 2026-07-03。方針は generic_refined_metal_placeholder.md の教訓
「ゲーム内に実在しない汎用カテゴリを資源として登録しない」に従い、
プレースホルダー資源『鉱物』の全参照を実在する資源別のrecipeへ展開して資源定義を削除した。
同時に(ユーザー指示による設計変更)独立recipe『産卵』『産卵(モー乳)』を廃止し、産卵を給餌recipeへ統合した。

## 1. 調査した生データと出典

### 1.1 ハッチ (Hatch) — wiki.gg "Hatch" のDietテーブル(wikitext原文を直接取得、DietExhaustive=yes)
出典: https://oxygennotincluded.wiki.gg/wiki/Hatch (?action=raw で取得)

基本ハッチの餌(各 140,000 g/cycle 消費 → Coal 70,000 g/cycle、50%変換):
- Crushed Rock(破砕岩)、Sandstone(砂岩)、Sedimentary Rock(堆積岩)、Shale(頁岩)、
  Clay(粘土)、Dirt(土)、Sand(砂) — 計7種。金属鉱石・硬岩は食べない。
- ほかに「食料 700kcal/cycle → 消費質量の50%を石炭」があるが、摂取量が数グラム単位で
  実用外(wiki本文の注記)のため未登録(従来どおり)。

### 1.2 ごつごつ ハッチ (Stone Hatch)
Dietテーブルはタグ表記(「Hard Rock 140kg→Coal 70kg」「Some Metal Ores 140kg→Coal 35kg」)のため、
具体種は各元素ページの記載で個別に裏取りした:
- 岩石(140kg/cycle → 石炭70kg/cycle、50%): 基本ハッチの7種
  (砂岩ページ「All Hatch types besides the Sage Hatch can eat Sandstone」、堆積岩ページ「Hatches and
  Stone Hatches can eat」)に加えて、
  - Igneous Rock(火成岩): https://oxygennotincluded.wiki.gg/wiki/Igneous_Rock 「Stone Hatches can eat」
  - Granite(花崗岩): https://oxygennotincluded.wiki.gg/wiki/Granite 「50% efficiency」
  - Obsidian(黒曜石): https://oxygennotincluded.wiki.gg/wiki/Obsidian 「50% efficiency」
  → 計10種。Mafic Rock(苦鉄質岩)ページにはハッチ摂食の記載なし → 除外。
- 金属鉱石(140kg/cycle → 石炭35kg/cycle、25%): 元素ページに「Stone Hatches can eat」の明記が
  あった7種のみ採用: 銅鉱石・金アマルガム・鉄鉱石・アルミニウム鉱石・コバルト鉱石・ニッケル鉱石・亜鉛鉱石
  (亜鉛鉱石ページは「25% efficiency」と倍率も明記)。
  鉄マンガン重石(Wolframite)・辰砂鉱石(Cinnabar)・方鉛鉱(Galena)・黄鉄鉱(Pyrite)の各ページには
  Stone Hatchの記載がないため未登録(要再検証。ゲーム内で食べられる可能性は残る)。

### 1.3 つるつる ハッチ (Smooth Hatch) — 金属鉱石 100kg/cycle → 対応精錬金属 75kg/cycle (75%)
出典: wiki.gg "Hatch"本文「They will eat a 100 kg of ore, "refining" it into 75 kg of Refined Metal」
+ 各元素ページ + パッチノート U56-674504「The Smooth Hatch diet has been updated to include
Cinnabar and Nickel Ore」。登録した9種:
- 銅鉱石→銅、金アマルガム→金、鉄鉱石→鉄、アルミニウム鉱石→アルミニウム、コバルト鉱石→コバルト、
  ニッケル鉱石→ニッケル、亜鉛鉱石→亜鉛(以上は元素ページで「75%」明記を確認)
- 辰砂鉱石→水銀(U56パッチノート由来。辰砂鉱石ページ自体は未更新でハッチ記載なし)
- 鉄マンガン重石→タングステン(wiki "Hatch" Diet要約より。元素ページに記載なし、確度は上記より一段低い)
方鉛鉱・黄鉄鉱はどの情報源にも記載がなく未登録。
これにより「銅で代表」の暫定登録(generic_refined_metal_placeholder.md)は解消。

### 1.4 プラグナメクジ系(スポンジナメクジ/スモッグナメクジ)の『鉱石』recipe
出典: https://oxygennotincluded.wiki.gg/wiki/Plug_Slug (Dietは「Most Metal Ore」表記) +
https://oxygennotincluded.wiki.gg/wiki/Cinnabar_Ore 「Plug Slugs consume 60kg/cycle …
Smog Slugs and Sponge Slugs consume 30kg/cycle」。
展開した鉱石9種(WebFetch要約のPlug Slug食リスト準拠): 銅鉱石・亜鉛鉱石・コバルト鉱石・
アルミニウム鉱石・金アマルガム・ニッケル鉱石・鉄鉱石・辰砂鉱石・方鉛鉱。
『精錬金属』recipe(銅で代表)は今回のスコープ外のため従来どおり(要再検証のまま)。

**未解決の数値齟齬(レートは指示どおり変更していない)**: 本DBは スモッグ -60/水素+3、スポンジ -30/水素+1.5
だが、wiki.ggでは 基本Plug Slugが60kg/cycle、SmogとSpongeは30kg/cycle。つまりDBのスモッグの数値は
wikiの「基本Plug Slug」の値に相当する可能性が高い(基本プラグナメクジのAgent自体が未登録)。要再検証。

### 1.5 精錬装置・岩石粉砕機
recipe名が実入力鉱石を既に明示していた(例: '方鉛鉱→鉛' で入力だけが『鉱物』-1500)ので、
入力資源をrecipe名の鉱石に差し替えた。レート変更なし。

## 2. 資源の追加・改名(公式日本語訳への統一、ja_localization_unification.md準拠)
strings.po(nsk4762jp/OxygenNotIncluded-Japanese)の STRINGS.ELEMENTS.*.NAME で確認した公式訳:
- 新規追加10種: 破砕岩(CRUSHEDROCK)、銅鉱石(CUPRITE)、亜鉛鉱石(ZINCORE)、辰砂鉱石(CINNABAR)、
  鉄マンガン重石(WOLFRAMITE)、アルミニウム鉱石(ALUMINUMORE)、コバルト鉱石(COBALTITE)、
  ニッケル鉱石(NICKELORE)、方鉛鉱(GALENA)、黄鉄鉱(FOOLSGOLD)
- 既存recipe名の表記を公式訳へ全置換: シンナバー鉱→辰砂鉱石、銅鉱→銅鉱石、亜鉛鉱→亜鉛鉱石、
  アルミニウム鉱→アルミニウム鉱石、コバルト鉱→コバルト鉱石、ニッケル鉱→ニッケル鉱石、
  ガレナ→方鉛鉱、ウォルフラマイト→鉄マンガン重石
- 『火成岩』の資源定義はファイル後方(マグマ凝固の節)にあったが、ハッチ等が先に参照するため
  冒頭のresources一括INSERTへ移動。
- 『鉱物』の資源定義は全参照の移行完了後に削除(未移行の残存参照なし)。

## 3. 置換したagent_io行の一覧
- ハッチ: 鉱物-140/石炭+70 → 岩石7種recipe(各 -140/石炭+70/卵+0.333) + '+モー乳'7種(モー乳-5、卵+0.708)
- ごつごつ ハッチ: 鉱物-140/石炭+70 → 岩石10種recipe(-140/+70) + 鉱石7種recipe(-140/+35)
- つるつる ハッチ: 鉱物-100/銅+75 → 鉱石9種recipe(各 -100/対応金属+75)
- スポンジナメクジ『鉱石』: 鉱物-30/水素+1.5 → 鉱石9種recipe(各 -30/+1.5)
- スモッグナメクジ『鉱石』: 鉱物-60/水素+3 → 鉱石9種recipe(各 -60/+3)
- 精錬装置 10recipe / 岩石粉砕機 10recipe: 入力『鉱物』-1500 → recipe名の実鉱石 -1500

## 4. 産卵の給餌recipe統合(ユーザー指示の設計変更)
産卵は「餌を食べている個体」が大前提のため、独立recipe『産卵』『産卵(モー乳)』を全10クリッター
(ハッチ・ドレッコ・パフ・パクー・ピップ・ポークシェル・スリックスター・ぐりぐりネズミ・バンモス・フロックス)
で廃止し、次の形に統合した(卵レート・導出は従来のGroomed値のまま):
- 各給餌recipe(単一食のクリッターは既定recipe'')の出力に 卵(harvest、Groomedレート)を追加
- 各給餌recipeに '<餌名>+モー乳' recipeを追加: 給餌IO(死亡時ドロップ除く) + モー乳-5(active) +
  卵×2.125(Groomed+モー乳=幸福度9=基礎の2125%)
これにより産卵反応がソルバーに給餌コスト込みで参加する(餌なしで卵が湧く偽経路の防止)。
詳細は docs/issues/plant_buff_and_milk_model.md の該当節を参照。

## 5. 検証結果
- スキーマ+seedからoni.dbを再構築: OK(外部キー・UNIQUE制約違反なし)
- test_onidb.py: 12件グリーン(『ハッチ(産卵(モー乳))』を参照していたアサーションを
  『ハッチ(堆積岩+モー乳)』+『産卵recipe不存在』の確認に更新)
- `onidb.py loops` / `loops --buff グラブグラブ世話`: 実行結果は本ファイル末尾の追記参照

## 6. loops実行結果の詳細(2026-07-03)
- 既定 / --buff グラブグラブ世話 とも変更前後で **50ループのまま増減なし**。
- 卵・モー乳を含むループは0件(産卵統合による新規増殖ループなし)。
- ループの顔ぶれの変化: 旧構成でセイジ ハッチのみだったハッチ系の参加に加え、
  ハッチ(砂)・ごつごつ ハッチ(砂) を含む水系ループが出現した。これは「焼成(土→砂)→ハッチが砂を
  食べて石炭化→石炭発電機」という**ゲーム内に実在する経路**が、砂の食餌を正しく登録したことで
  検出可能になったもの(レートは従来の140→70のままで、質量創出の偽ループではない)。
