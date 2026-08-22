---
name: current-state-analysis
description: >-
  Run current-state and problem-identification frameworks on the user's material
  and render the results as slides: PEST, Five Forces, process pain-points, logic
  tree, KPI tree, why-why, fishbone, Pareto, As-Is/To-Be gap, impact-effort
  priority matrix, plus SWOT / 3C.
  Use for: 現状分析, 課題を特定・構造化, 真因分析, As-Is/To-Be 整理,
  課題の優先順位付け, ヒアリングメモを分析スライドに.
  Not: authoring new templates (analysis-template-creator); deck generation
  mechanics (google-slides); visual QA (slide-qa).
---
*[English](SKILL.md)*

# Current-State Analysis（現状分析・課題の特定）

ユーザーが持ち込む材料（ヒアリングメモ・業務資料・データ）に分析フレーム
ワークを適用し、その結果を `slide-templates/analysis` パック（+ 一部
`marketing-analysis` パック）のスライドに落とす。

作業ディレクトリは slide-forge ルート。コマンドは `.venv/bin/python`。

## Boundaries

| 依頼 | 行き先 |
|---|---|
| 現状分析・課題特定を実行し、スライドにする | このスキル |
| 分析フレームワークのテンプレートを新設・変更する | `analysis-template-creator` |
| SWOT / 3C / ポジショニングマップ等の市場分析 1 枚だけ | `google-slides-template` + marketing-analysis パック |
| デッキ生成そのものの仕組み・マスター選択 | `google-slides` / `google-slides-template` |
| 生成したデッキの目視検査 | `slide-qa` |
| 商談・アカウント固有の課題整理（台帳あり） | `scalar-account-plan` 系 |

## 手法とテンプレートの対応

分析は「環境 → 業務 → 構造化 → 課題定義 → 優先順位」の順に深くなる。
**全部やらない。** 問いに答えるのに必要な段だけ選ぶ。

| 段 | 答える問い | 手法 | テンプレート |
|---|---|---|---|
| 1. 環境 | 外部要因は何か | PEST | `pest-analysis` |
| 1. 環境 | 業界の競争圧力はどこから | 5フォース | `five-forces` |
| 1. 環境 | 強み・弱み × 機会・脅威 | SWOT | `swot-analysis`（marketing-analysis） |
| 1. 環境 | 顧客・競合・自社 | 3C | `three-c-analysis`（marketing-analysis） |
| 2. 業務 | どの工程に問題が集中しているか | 業務フロー + ペイン | `process-painpoints` |
| 3. 構造化 | 問題は何に分解できるか | ロジックツリー | `logic-tree` |
| 3. 構造化 | 未達はどの指標のせいか | KPI ツリー | `kpi-tree` |
| 3. 構造化 | 真因は何か（単線） | なぜなぜ分析 | `why-why` |
| 3. 構造化 | 原因の仮説はどの系統か | 特性要因図 | `fishbone-diagram` |
| 3. 構造化 | どの要因が大半を占めるか | パレート分析 | `pareto-analysis` |
| 4. 課題定義 | 現状と理想の差は何か | ギャップ分析 | `gap-analysis` |
| 5. 優先順位 | どれから着手するか | 優先順位マトリクス | `priority-matrix` |

定番の組み合わせ（業務・IT 改革系）:
`process-painpoints` →（`pareto-analysis` か `logic-tree`）→ `why-why` →
`gap-analysis` → `priority-matrix`。戦略系は 1 段目（PEST / 5F / 3C / SWOT）
から `gap-analysis` へ。

各テンプレートの入力スロットと制約は
`slide-templates/analysis/<id>/template.json` が正で、
`.venv/bin/python scripts/list_slide_templates.py --tag analysis` で一覧できる。
このスキルでスロット定義を再掲しない。

## Workflow

### 1. Intake

一度にまとめて確認する:

- 答えるべき問い（何を決めるための分析か。決裁・稟議・改善企画…）;
- 材料（ヒアリングメモ・データ・公開資料）と、その**出典・鮮度**;
- 分析の深さ（環境〜優先順位のどの段まで要るか）;
- 出力形態（単スライド / 分析章まるごと / 既存デッキへの追加）。

材料が無い分析は**引き受けない**。不足があれば、埋めるためのヒアリング
項目・調査項目のリストを先に返す（それ自体が成果物になる）。

### 2. 分析の実行

フレームワークは思考の型であって、埋め草の型ではない:

- **事実と解釈を分ける。** 図の中身（工程・件数・環境要因・原因）は材料に
  ある事実だけ。解釈は `insight`（so_what）と `title` に置く。
- 材料に無いことを推測で埋めるときは（仮説）と明示し、検証方法を添える。
- 数値はすべて出典・期間・母数を `source` スロットに書く。書けない数値は
  載せない。
- 各テンプレートの `guardrails` は手法の誤用パターン（相関を因果と読む、
  「人の不注意」で止める等）を列挙している。**分析中に読み、従う。**

### 3. スロット JSON の作成と検証

手法ごとに `example.json` と同じ形の入力 JSON を作り、1 枚ずつ検証する:

```bash
.venv/bin/python scripts/render_slide_template.py \
  --template <id> --data <data.json> --out out/<n>_<id>.json
```

複数枚は `assemble_spec.py` で 1 つのデッキ仕様に束ね、オフラインで監査する:

```bash
.venv/bin/python scripts/assemble_spec.py out/*_*.json --out out/analysis-deck.json --title <題名>
.venv/bin/python scripts/build_deck.py --template templates/<master>.json \
  --spec out/analysis-deck.json --dry-run --strict
```

監査指摘（はみ出し・重なり・折り返し）は**データ側を短く**して直す。
テンプレートやプリミティブを変えたくなったら `analysis-template-creator` へ。

### 4. 生成と QA

生成の実行・保存先・タイトルの流儀は `google-slides` / `google-slides-template`
に従う。生成後は `slide-qa` で目視検査し、QA サムネイルを後始末する。

### 5. Report

- 使った手法と、その選定理由（どの問いに答えるためか）;
- 各スライドの主張（title）と、根拠の出典;
- 材料不足で（仮説）扱いにした箇所と、その検証方法;
- デッキ URL と QA 結果（生成まで実行した場合）。

## Safety and quality rules

- **分析結果を捏造しない。** インタビュー発言・件数・工数は実データのみ。
  デモ用は example.json の流儀に合わせ、source に「サンプル」と明記する。
- 記述（descriptive）・診断（diagnostic）・因果（causal）の主張を混ぜない。
  パレート図は「集中している」までで、「これが原因」は why-why / 検証の仕事。
- 顧客・個人が特定できる分析（体制・ペインの発言者等）は社内資料。顧客に
  渡す版は `scalar-ae-materials` の露出チェックの考え方に従って別に作る。
- 生成物・QA ファイルは `out/` 以下に置く（コミットしない）。
