---
title: "feat: Add marketing analysis slide recipes"
type: feat
status: superseded
date: 2026-08-10
superseded_by: docs/plans/2026-08-10-feat-slide-template-creator-skill-plan.md
---

# マーケティング分析スライド・レシピの追加計画

## 概要

市場分析、顧客分析、行動分析、施策効果測定、需要予測の結果を、再利用可能な1枚単位のスライドとして生成できるようにする。

このリポジトリでは `templates/*.json` がGoogle Slidesのマスター定義を意味するため、分析スライドを同じ場所へ追加しない。分析用テンプレートは `recipes/marketing-analysis/` の「slide recipe」とし、既存の `scripts/patterns.py`、`scripts/pages.py`、`scripts/charts.py` で構成する。不足する図だけ `scripts/marketing.py` に描画プリミティブとして追加する。

さらに `.agents/skills/marketing-analysis-slides/SKILL.md` を追加し、エージェントが分析目的、データの種類、主張に応じてレシピを選択・入力データへ適合・検証できるようにする。

## 問題と目的

現在のエンジンには、TAM/SAM/SOM、ポジショニング、ファネル、表、棒・折れ線グラフなどの部品はあるが、次の課題がある。

- マーケティング分析の手法名から適切な図表へ到達するルーティングがない。
- SWOT、3C、PESTLE、RFM、コホート、アトリビューション、MMMなどは専用表現がない。
- 既存部品で作れる分析でも、座標、入力スキーマ、アクションタイトル、出典の置き方を毎回組み直す必要がある。
- 戦略フレームワーク、記述分析、予測、因果推論の区別がスライド生成時に担保されていない。
- 一覧カタログがないため、ユーザーが生成可能な分析スライドを選びにくい。

成功状態は、ユーザーが「RFM分析を1枚にして」「施策別ROASと増分効果を比較して」のように依頼すると、エージェントが適切なレシピを選択し、根拠のない数値を補完せず、オフライン検証可能なデッキ仕様を生成できることである。

## スコープ

### 対象

- マーケティング分析用の再利用可能なslide recipe
- recipeを構成するために不足している描画プリミティブ
- recipeのメタデータ、入力契約、選択ルール
- エージェント用スキルと `AGENTS.md` / `forge` のルーティング
- サンプルデータ入りカタログデッキ
- オフライン検証と目視QAの手順
- 各分析の解釈上の注意、出典・注記ルール

### 対象外

- 新しいブランドマスターの作成
- 統計計算エンジン、MMM推定器、クラスタリング処理そのもの
- GA4、広告API、CRMからの自動データ取得
- ユーザー所有デッキへの自動挿入
- 分析結果の正しさをスライド描画コードだけで保証すること

## 設計方針

### 1. マスター、プリミティブ、レシピ、スキルを分離する

```text
ユーザーの依頼
  -> marketing-analysis-slides skill（選択・入力確認・解釈ガード）
    -> recipe manifest（目的と入力から1枚の型を選択）
      -> slide recipe JSON（ページ骨格、座標、プレースホルダ）
        -> Canvas primitives（既存部品 + marketing.py）
          -> build_deck.py --dry-run --strict
            -> Google Slides生成 -> slide-qa
```

- **Master**: `templates/*.json`。ブランド、レイアウト、プレースホルダを定義する。
- **Primitive**: `Canvas` の描画関数。単一の図表表現を担当する。
- **Recipe**: 1枚の論理構成、標準座標、入力項目、注記を定義する。
- **Skill**: どのrecipeを選び、どの情報をユーザーへ確認し、何を断定してはいけないかを定義する。

### 2. 既存部品の組み合わせを優先する

新しい手法名ごとに描画関数を増やさない。既存の `matrix`、`table`、`cards`、`funnel`、`nested_circles`、`posmap`、`linechart`、`waterfall`、`source_note` で表現できるものはrecipeだけを追加する。

専用プリミティブを追加する条件は次のとおり。

- 既存部品の組み合わせでは毎回20個以上の低水準shape指定が必要になる。
- マーケティング分析固有の軸・凡例・セル表現を検証する必要がある。
- 同じ表現を3つ以上のrecipeが共有する。
- 入力不整合を関数レベルで検出する価値がある。

### 3. 数値と主張をrecipeへ埋め込まない

recipeには架空のサンプル値と、差し替え対象を明示する。実デッキ生成時はユーザー提供データまたは出典確認済みデータだけを使用する。数値スライドには `source_note` を必須とし、推計値、予測値、実測値を注記で区別する。

### 4. 記述、予測、因果を明示する

各recipe manifestに `inferenceLevel` を持たせる。

- `descriptive`: 何が起きたかを示す
- `diagnostic`: どこで・誰に起きたかを比較する
- `predictive`: 将来予測を示す
- `causal`: 実験または妥当な因果設計に基づく増分効果を示す
- `strategic`: 定性情報を構造化する

アトリビューションを増分効果として、相関を因果効果として記述しないよう、recipeとskillの両方に禁止事項を置く。

## 手法と実装方式の対応

### A. 既存プリミティブだけで作るrecipe

| 手法 | recipe ID | 主な既存部品 | 骨格 |
|---|---|---|---|
| TAM/SAM/SOM | `market-sizing` | `nested_circles`, `source_note` | E |
| 5フォース | `five-forces` | `hub`, `cards` | A |
| STP | `stp-flow` | `flow`, `cards` | D |
| ポジショニング | `positioning-map` | `posmap`, `so_what` | E |
| クラスター比較 | `segment-profile` | `table`, `vbars_grouped` | B |
| LTV | `ltv-economics` | `metric`, `waterfall`, `table` | B |
| コンジョイント | `conjoint-utilities` | `hbars`, `table` | B |
| ファネル | `conversion-funnel` | `funnel`, `metric` | B |
| カスタマージャーニー | `customer-journey` | `journey`, `table` | D |
| パス分析 | `behavior-path` | `flow`, `hbars` | B |
| KPIスコアカード | `channel-scorecard` | `metric`, `table` | A |
| 時系列予測 | `forecast-trend` | `linechart`, `source_note` | B |
| シナリオ分析 | `forecast-scenarios` | `linechart`, `table` | B |

### B. 新しい専用プリミティブを追加するrecipe

| 手法 | recipe ID | 新規 primitive | 理由 |
|---|---|---|---|
| PESTLE | `pestle-scan` | `factor_grid` | 6分類を一貫した密度で表示し、空分類を検出するため |
| 3C | `three-c-analysis` | `three_c` | Customer/Competitor/Companyの重なりと戦略示唆を固定するため |
| SWOT | `swot-analysis` | `swot` | 内外・正負の軸、4象限見出し、戦略接続を標準化するため |
| RFM | `rfm-segments` | `rfm_matrix` | Recency/FrequencyのセルとMonetaryの表現を一体で扱うため |
| コホート | `cohort-retention` | `heatmap` | 時系列セルの色尺度、欠損、母数表示が必要なため |
| アンケート | `survey-results` | `diverging_bars` | Likert尺度を中立点から左右へ描くため |
| A/Bテスト | `experiment-result` | `experiment_compare` | uplift、信頼区間、母数、期間、判定を固定配置するため |
| アトリビューション | `attribution-path` | `attribution_path` | 接点順序と配賦率を区別して描くため |
| MMM | `marketing-mix` | `contribution_bars`, `response_curve` | ベースライン、増分寄与、飽和曲線を表現するため |
| 売上要因分解 | `sales-driver-decomposition` | 既存 `waterfall` を拡張 | 正負、合計整合、実績差分を扱うため |

### C. 戦略フレームワークのrecipe構成

PESTLE、3C、SWOTを単独の記入欄として終わらせない。各recipeは最低限、次の3層を持つ。

1. 観測事実または根拠
2. 自社への影響・解釈
3. 優先アクションまたは次に検証する仮説

SWOTは必要に応じてTOWSへ接続できる拡張recipeを用意するが、MVPではSWOT本体を優先する。

## ファイル構成

```text
.agents/skills/marketing-analysis-slides/
  SKILL.md
  references/
    method-selection.md
    interpretation-guardrails.md

recipes/marketing-analysis/
  manifest.json
  strategic/
    pestle-scan.json
    three-c-analysis.json
    swot-analysis.json
    five-forces.json
    market-sizing.json
    stp-flow.json
    positioning-map.json
  customer/
    segment-profile.json
    rfm-segments.json
    cohort-retention.json
    survey-results.json
    ltv-economics.json
    conjoint-utilities.json
  behavior/
    conversion-funnel.json
    customer-journey.json
    behavior-path.json
  effectiveness/
    channel-scorecard.json
    experiment-result.json
    attribution-path.json
    marketing-mix.json
    sales-driver-decomposition.json
  forecast/
    forecast-trend.json
    forecast-scenarios.json

scripts/
  marketing.py
  validate_recipes.py
  build_recipe_catalog.py

examples/
  marketing-analysis-catalog.json

references/
  marketing-analysis-patterns.md
```

recipeの実ファイル数が多くなりすぎる場合でも、分野別の巨大JSONへまとめない。1 recipe 1 fileを維持し、manifestから発見できるようにする。

## Recipe manifestの契約

`recipes/marketing-analysis/manifest.json` は最低限、次の情報を持つ。

```json
{
  "id": "cohort-retention",
  "displayName": "コホート継続率",
  "category": "customer",
  "answers": ["獲得時期別に継続率は改善しているか"],
  "inferenceLevel": "diagnostic",
  "requiredInputs": ["cohortLabels", "periodLabels", "values", "sampleSizes", "source"],
  "optionalInputs": ["segment", "benchmark", "notes"],
  "recommendedSkeleton": "B",
  "recipe": "customer/cohort-retention.json",
  "guardrails": [
    "母数の小さいセルを同じ確度で解釈しない",
    "観測期間が異なる右下セルを単純比較しない"
  ],
  "tags": ["retention", "repeat", "cohort"]
}
```

`validate_recipes.py` でID重複、参照切れ、必須キー、未知の `figure.type`、プレースホルダ残存、フッター侵入を検査する。

## 実装フェーズ

### Phase 1: Recipe基盤とMVP 8手法

対象:

- SWOT
- 3C
- TAM/SAM/SOM
- ポジショニング
- RFM
- コホート
- コンバージョンファネル
- A/Bテスト

作業:

- [ ] `recipes/marketing-analysis/manifest.json` のスキーマを確定する。
- [ ] recipe中の置換変数の表記を決める。JSONを直接 `build_deck.py` に渡せる形を壊さず、サンプル値と `notes` で差し替え箇所を明示する方式を第一候補とする。
- [ ] `scripts/marketing.py` にMVPで必要な `three_c`、`swot`、`rfm_matrix`、`heatmap`、`experiment_compare` を実装する。
- [ ] `scripts/diagrams.py` の `Canvas` に `MarketingMixin` を追加する。
- [ ] `scripts/build_deck.py::FIGURES` に新しいtypeと必須位置引数を登録する。
- [ ] snake_case/camelCase変換、必須入力、配列長、0〜1範囲、負値などを検証する。
- [ ] 8つのrecipeを標準10×5.625インチ座標で作る。
- [ ] `scripts/validate_recipes.py` を追加し、全recipeを一括dry-runできるようにする。
- [ ] `references/template-schema.md` から新しいマーケティング図表のリファレンスへリンクする。

完了条件:

- 8 recipeが `--dry-run --strict` とfigure auditを通る。
- 既存 `examples/*.json` のdry-run結果を壊さない。
- 各recipeに質問、必要データ、出典、解釈上の注意がある。

### Phase 2: 顧客・行動分析の拡充

- [ ] PESTLE、5フォース、STPを追加する。
- [ ] アンケート、セグメント比較、LTV、コンジョイントを追加する。
- [ ] カスタマージャーニー、パス分析を追加する。
- [ ] `factor_grid` と `diverging_bars` を追加する。
- [ ] カテゴリ名、値、母数、期間の長さに対する可読性上限を各primitiveに実装する。
- [ ] 1枚で読めない入力には例外または「分割せよ」という警告を返す。

### Phase 3: 効果測定・予測の拡充

- [ ] KPIスコアカード、アトリビューション、MMM、売上要因分解を追加する。
- [ ] 時系列予測とシナリオ比較を追加する。
- [ ] `attribution_path`、`contribution_bars`、`response_curve` を追加する。
- [ ] 予測値には実績/予測境界と予測区間を表示できるよう `linechart` を拡張するか、互換性を保った `forecast_chart` を追加する。
- [ ] MMM recipeではベースラインと増分寄与を分離し、モデル適合度だけで因果妥当性を主張しない注記を必須にする。
- [ ] アトリビューションrecipeには「配賦であり増分効果ではない」注記を既定で含める。

### Phase 4: エージェント統合

- [ ] `.agents/skills/marketing-analysis-slides/SKILL.md` を追加する。
- [ ] スキルのインテイクは「分析目的」「利用可能データ」「対象期間・セグメント」「出典」「登壇用/配布用」を1回で確認する。
- [ ] `AGENTS.md` のSkill routingへマーケティング分析デッキを追加する。
- [ ] `.agents/skills/forge/SKILL.md` にルーティングを追加する。
- [ ] `google-slides` と `google-slides-template` の図表リファレンスにrecipe利用手順を追加する。
- [ ] recipe選択時に、ユーザーが指定した手法名より「答えたい問い」を優先するルールを書く。
- [ ] データ不足時は空欄をもっともらしい数字で埋めず、必要入力を返すルールを書く。

### Phase 5: カタログ、QA、ドキュメント

- [ ] `scripts/build_recipe_catalog.py` でmanifestからカタログ仕様を生成する。
- [ ] `examples/marketing-analysis-catalog.json` に全recipeの実物、用途、入力項目、注意点を掲載する。
- [ ] `references/marketing-analysis-patterns.md` に手法選択表、JSON例、Python例を記載する。
- [ ] カタログを `blank-16x9` と少なくとも1つの登録テンプレートで生成する。
- [ ] `slide-qa` で全ページを目視し、文字溢れ、色尺度、凡例、軸、出典、フッターを確認する。
- [ ] QA修正はprimitiveまたはrecipeへ戻し、生成済みデッキの手修正で済ませない。
- [ ] `scripts/cleanup_qa.py` でローカルQAファイルを削除する。

## テスト・検証計画

### 単体相当のオフライン検証

- 正常な最小入力で描画できる。
- 必須配列の長さ不一致で明確なエラーになる。
- 比率が0〜1または0〜100のどちらか曖昧な入力を黙って解釈しない。
- コホートの三角行列と欠損セルを正しく扱う。
- RFMのスコア範囲外を拒否する。
- A/Bテストで `n`, baseline, variant, upliftの整合を確認する。
- SWOTなどで空の象限がある場合、警告または明示的な「該当なし」を要求する。
- 文字数・カテゴリ数が上限を超えたら分割を促す。
- 数値recipeに `source` がない場合は検証を失敗させる。

### 回帰検証

- `examples/patterns-demo.json`
- `examples/charts-demo.json`
- `examples/slide-pattern-index.json`
- `examples/read-alone-guide.json`

上記を既存テンプレートでdry-runし、`Canvas` のMixin追加と `FIGURES` 登録が既存出力を壊していないことを確認する。

### 統合シナリオ

1. 「市場参入分析」からPESTLE、3C、TAM/SAM/SOM、ポジショニングを選び、4枚の仕様を作れる。
2. CSV由来のRFM集計値からRFMスライドを作り、架空データを残さない。
3. コホートデータの期間数が多すぎる場合、縮小せず分割案を出す。
4. A/Bテスト結果に統計的有意差がない場合、「効果なし」と断定せず、不確実性を表示する。
5. アトリビューションとMMMを同一デッキへ入れても、配賦と増分効果の用語が混同されない。

## 受け入れ基準

### 機能

- [ ] manifestから全recipeを列挙できる。
- [ ] エージェントが手法名または答えたい問いからrecipeを選択できる。
- [ ] MVP 8手法、最終的に上記23前後のrecipeを提供する。
- [ ] recipeはblank masterと登録済みmasterの双方で使用できる。
- [ ] 全数値recipeが出典欄を持つ。
- [ ] recipeはサンプル値と実データを明確に区別する。

### 品質

- [ ] 全recipeがオフラインstrict validationを通る。
- [ ] カタログ全ページを目視QA済みである。
- [ ] 本文12pt以上、タイトル20pt以上、主要テキストのコントラスト4.5:1以上を維持する。
- [ ] 10×5.625インチのフッター安全域へ侵入しない。
- [ ] 日本語と英語の代表入力で折り返しを確認する。

### エージェント動作

- [ ] データ不足時に値を推測・捏造しない。
- [ ] 相関、アトリビューション、予測を因果効果として表現しない。
- [ ] 戦略フレームワークでは事実、解釈、アクションを分ける。
- [ ] 生成前のdry-runと、選択された場合のslide-qaを省略しない。

## リスクと対策

| リスク | 影響 | 対策 |
|---|---|---|
| `template`という語の衝突 | マスター定義と分析ページを混同する | `recipe` と命名し別ディレクトリに置く |
| 専用関数の増殖 | 保守性低下、表現の重複 | 新規primitiveの採用条件を設け、既存部品を優先する |
| recipe JSONのコピペずれ | 修正が全ファイルへ反映されない | manifest検証とカタログ自動生成を用意する |
| サンプル値の混入 | 誤情報を納品する | 明示的なサンプルフラグと生成前チェックを設ける |
| 統計的な誤読 | 意思決定を誤らせる | inferenceLevelとmethod別guardrailを必須にする |
| 情報過多 | 文字を縮小した読めないページになる | 項目数上限と分割エラーをprimitiveに持たせる |
| master依存のレイアウト崩れ | テンプレートごとに見た目が変わる | 10×5.625標準座標、Palette利用、複数masterでのカタログQA |
| 既存Mixinへの影響 | 既存デッキ生成が壊れる | `MarketingMixin` を独立させ、回帰dry-runを行う |

## 代替案

### `scripts/patterns.py` へ全手法を直接追加する

短期的には簡単だが、一般的なビジネス図とマーケティング固有図の責務が混ざり、ファイルと `FIGURES` が肥大化するため採用しない。

### 各手法を完成済みGoogle Slidesマスターとして作る

マスターはブランドとレイアウトのためのもので、データや図表の内容を表現する場所ではない。またSlides APIは新しいlayoutを自由に作成できないため採用しない。

### すべてをJSONサンプルだけで提供する

TAMやファネルには十分だが、コホート、RFM、A/Bテストなどで検証可能な入力契約を持てず、低水準shape指定が重複するため一部のみ採用する。

### 先に統計計算機能まで実装する

スコープと検証コストが大きくなる。最初は「分析済みデータを正しく伝える」ことに限定し、計算機能は将来の別機能とする。

## 実装順と目安

1. Recipe契約・manifest・validator: 1〜2日
2. MVP primitives 5種と8 recipes: 3〜5日
3. 顧客・行動分析recipes: 3〜4日
4. 効果測定・予測recipes: 4〜6日
5. skill統合、カタログ、複数master QA: 2〜4日

合計は1名で約2〜3週間を想定する。最初のマイルストーンはMVP 8手法に絞り、カタログを確認してから残りの表現を確定する。

## 将来拡張

- CSV/Google Sheetsからrecipe入力へ変換するデータアダプター
- GA4、広告、CRMコネクター
- 統計計算済み結果のJSON Schema
- 業界別recipeパック（SaaS、EC、店舗、B2B）
- 日本語/英語ラベルのi18n
- recipeを組み合わせた「市場参入分析」「顧客維持分析」「広告効果測定」デッキcomposer

## 内部参照

- `scripts/patterns.py` — TAM/SAM/SOM、ポジショニングなど既存のビジネス図
- `scripts/pages.py` — アクションタイトル、示唆、出典、分析ページ骨格
- `scripts/charts.py` — 表、棒、折れ線、円グラフ
- `scripts/build_deck.py:858` — JSON figure typeのregistryと検証入口
- `scripts/diagrams.py:145` — Canvas mixin構成
- `references/slide-patterns.md` — 骨格6種、標準座標、出典ルール
- `references/patterns.md` — 既存ビジネスフレームワーク図
- `references/template-schema.md` — デッキ仕様とfigure schema
- `examples/slide-pattern-index.json` — 既存ページパターンの実物索引
- `.agents/skills/template-forge/SKILL.md` — masterとlayoutに関する制約
- `.agents/skills/google-slides/SKILL.md` — dry-run、生成、QAフロー

## 最初に確定すべき判断

実装開始時に、以下だけはMVP着手前に確認する。

1. 初期リリースをMVP 8手法に限定するか、全手法を一括で作るか。
2. recipeを「コピーして編集するJSON」とするか、置換変数を持つレンダラーまで初期実装するか。推奨は前者から始める。
3. カタログの既定言語を日本語のみとするか、日英を同時に用意するか。推奨は日本語を先行し、ラベルをi18n可能な構造にする。
