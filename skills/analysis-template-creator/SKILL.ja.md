---
name: analysis-template-creator
description: >-
  Author and maintain the slide templates in the slide-templates/analysis pack —
  PEST, Five Forces, logic tree, KPI tree, why-why, fishbone, Pareto, gap
  analysis, process pain-points, priority matrix — including the drawing
  primitive a new framework needs. Encodes each framework's own rules: the
  question it answers, the fact/interpretation split, required sources, misuse
  guardrails.
  Use for: 分析フレームのテンプレートを追加・修正, add an analysis-framework template.
  Not: generic page templates (slide-template-creator); running an analysis
  (current-state-analysis).
---
*[English](SKILL.md)*

# Analysis Template Creator（分析テンプレート作成）

現状分析・課題特定系フレームワークのスライドテンプレートを
`slide-templates/analysis/` パックに追加・変更する専門スキル。

**スキーマ・検証・登録・互換性の規約は
[`slide-template-creator`](../slide-template-creator/SKILL.md) が正。**
このスキルはその上に、分析フレームワーク固有の設計ルールを足すだけで、
共通規約を再定義しない。作業ディレクトリは slide-forge ルート、
コマンドは `.venv/bin/python`。

## Boundaries

| 依頼 | 行き先 |
|---|---|
| 分析フレームワークのテンプレート新設・変更 | このスキル |
| 分析以外の汎用ページテンプレート | `slide-template-creator` |
| 分析を実行してスライドを作る | `current-state-analysis` |
| ブランド・マスターの作成 | `template-forge` |
| 生成デッキの目視検査 | `slide-qa` |

## analysis パックの現状

| category | テンプレート | 主プリミティブ |
|---|---|---|
| macro | `pest-analysis` | `comparison`（4 列） |
| macro | `five-forces` | `cards` × 5（十字配置） |
| structure | `logic-tree` / `kpi-tree` | `mece_tree` |
| cause | `why-why` | `flow` |
| cause | `fishbone-diagram` | `fishbone`（patterns.py） |
| cause | `pareto-analysis` | `pareto`（charts.py） |
| process | `process-painpoints` | `flow` + `table` |
| gap | `gap-analysis` | `before_after` + `cards` |
| priority | `priority-matrix` | `posmap` |

SWOT / 3C / ポジショニングマップは `marketing-analysis` パックに既存。
**重複を作らない**（同じ問いに同じ視覚文法で答えるなら再利用・拡張）。
category は上記 6 種（macro / structure / cause / process / gap / priority）
から選び、増やすときは分析の段（環境→業務→構造化→課題定義→優先順位）に
対応させる。

## 分析テンプレート固有の設計ルール

`slide-template-creator` の共通規約に加えて、以下を必須とする:

1. **答える問いを 1 つに固定する。** `answers` に書く。問いが 2 つあるなら
   テンプレートも 2 つ（例: 原因の洗い出しは fishbone、真因の特定は why-why）。
2. **事実と解釈のスロットを分ける。** 図の中身（要因・工程・数値）は事実
   スロット、解釈は `insight`（`so_what` に描く）と `title`。insight スロットの
   maxLength は so_what の実容量（本文高 = h − 0.54in、約 46 字/行）から
   逆算して決める。1 行なら 44、2 行（h ≥ 1.1in）なら 88 が目安。
3. **数値が載る手法は `source` 必須**、期間・母数・定義の明記を guardrails で
   要求する。
4. **手法の誤用パターンを guardrails に落とす。** 教科書的定義から「やりがちな
   間違い」を最低 3 つ書く。例: パレート＝合計に意味のある量だけ／率を混ぜ
   ない、なぜなぜ＝「人の不注意」で止めない、5F＝自社の強み弱みを書かない、
   ギャップ分析＝未合意の願望を To-Be に置かない、優先順位＝座標は主観評価
   なので評価者・評価日を書く。
5. **inferenceLevel を正しく付ける。** 記述（pareto, process-painpoints）/
   診断（logic-tree, kpi-tree, fishbone）/ 因果（why-why）/ 戦略（PEST, 5F,
   gap, priority）。因果を名乗れるのは因果の連鎖を描く手法だけ。

## 新しい手法を追加する手順

1. **検索。** `list_slide_templates.py --tag <手法名>` と
   `rg '<手法名>' slide-templates references` で既存・類似を確認する。
2. **手法の分解。** 教科書的定義から (a) 答える問い、(b) 入力（事実）と
   出力（解釈）、(c) 誤用パターンを書き出す。ここが guardrails の材料になる。
3. **プリミティブ選定。**
   [primitive-selection.md](../slide-template-creator/references/primitive-selection.md)
   に従い既存部品を優先する。フレームワーク固有の形が必要なときだけ
   `patterns.py`（フレームワーク図）か `charts.py`（グラフ）に追加する —
   `fishbone` / `pareto` が前例で、i18n の `register()`、入力検証の
   `ValueError`、`build_deck.py::FIGURES` への登録、`references/patterns.md`
   / `references/charts.md` / `references/template-schema.md` の文書化まで
   がセット。
4. **作成と検証。** template.json + example.json を書き、
   `validate_slide_templates.py --id <id>` → `--pack analysis` →
   `build_slide_template_catalog.py --pack analysis` を通す。
   **監査指摘ゼロが合格線**（既存パックはすべてゼロ）。
5. **視覚 QA。** カタログデッキを生成して `slide-qa` を通し、境界サイズの
   入力（最長ラベル・最多項目）で崩れないことを確認、QA 成果物を後始末する。
6. **登録と報告。** manifest 登録、`current-state-analysis` の対応表への追記、
   互換性影響の報告（既存スロットの変更は
   [registration-and-compatibility.md](../slide-template-creator/references/registration-and-compatibility.md)
   に従う）。

## Safety and quality rules

- example.json は必ずサンプルと明記する（source スロットに書く）。実在の
  顧客名・実データを例に使わない。
- 実行時バリデーション（描画側の ValueError）とスロット制約は二重にする。
  スロット制約は「監査指摘が出ない範囲」に合わせて決め、描画側は「読めなく
  なる入力」を拒否する。
- 追加・変更のたびに `--pack analysis` 全体と、プリミティブを触った場合は
  他パックの回帰（marketing-analysis / b2b-sales / scalar-ae / planning）も
  検証する。
