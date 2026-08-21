---
name: nexus-report-slides
description: >-
  Turn a nexus-architect project's output reports and UI mocks into an
  explanation deck, including while the pipeline is still unfinished: read
  work/pipeline-progress.json first to establish what is actually known, build
  only from the reports that exist, embed the product UI mocks as screenshots
  and the structure diagrams as rendered mermaid, and carry every unanswered
  phase into an open-questions page instead of guessing. Covers all four
  plugins (architect, product, infra, scalardb) via the slide-templates/nexus
  pack.
  Triggers: "nexus-architect のレポートを説明資料にして", "分析結果をスライドに",
  "アーキテクチャ分析の報告資料", "UI モックを貼ったスライド", "途中まででいいので資料化",
  "nexus-report-slides", "turn the architect reports into slides",
  "report deck from the pipeline".
  Out of scope: producing the reports themselves (that is nexus-architect's
  own skills), authoring new slide templates (slide-template-creator), deck
  generation mechanics (google-slides-template), and visual QA (slide-qa).
---

*[English](SKILL.md)*

# nexus-architect レポートのスライド化

nexus-architect プロジェクトが**いまの時点で出しているもの**から説明デッキを組む。
プロジェクトは**読むだけ**で、こちらから書き込むことはない。

作業ディレクトリは slide-forge ルート、コマンドは `.venv/bin/python`。

## 境界

| 依頼 | 担当 |
|---|---|
| nexus-architect の分析結果をスライドで説明する | 本スキル |
| 分析そのものを実行・再実行する | nexus-architect 側の `/architect:*` `/product:*` |
| ページテンプレートの追加・変更 | `slide-template-creator`（パックの規約は `references/nexus-reports.ja.md`） |
| デッキ生成の仕組み、マスター選択 | `google-slides-template` |
| 生成したデッキの目視検証 | `slide-qa` |
| PowerPoint への書き出し | `pptx-export`（または `config/settings.json` の `output: local`） |

## パイプラインは途中であるのが普通

未着手のフェーズ、実行中のフェーズ、宣言した 4 つの出力のうち 2 つだけ書けた
フェーズ — これが通常の状態。ここから 3 つの規則が出る。省略不可。

1. **中身より先にカバレッジを確定する。** `collect.py` が
   `work/pipeline-progress.json`（nexus-architect のチェックアウトに届くなら
   `tools/nexus-status.sh --json` も）を読んで `coverage.json` を 1 つ作る。
   全デッキの 2 ページ目は `pipeline-coverage`（何フェーズ分に基づくか）。
2. **本文になるのは完了した仕事だけ。** 一部だけ出力されたフェーズは、
   実在するファイルからのみ組む。無いファイルからは組まない。
3. **未回答は未回答のまま載せる。** 未着手・実行中・失敗のフェーズと欠落した出力は
   すべて `open-questions` の行になり、それを埋めるコマンドを併記する。
   もっともらしい記述で穴を埋めない。

## 進め方

### 1. インテイク（1 ラウンド）

足りないものだけ聞く: プロジェクトのパス、読者プロファイル
（`exec` 12〜18 枚／`deep` 完了フェーズすべて）、対象プラグイン、QA の有無。
先に `config/settings.json` を読み、そこが答えている項目は聞かない
（`references/settings.ja.md`）。デッキの言語はプロジェクトの
`options.output_language` に従う。

### 2. 収集し、何よりも先にカバレッジを示す

```bash
.venv/bin/python scripts/nexus/collect.py --project <プロジェクトのディレクトリ>
```

「architect 25 フェーズ中 21、product は未着手、未回答 36 件」のように、
**アウトライン提案より前に** 1 行で伝える。この数字がデッキ全体の前提になる。

### 3. 背骨を組む

```bash
.venv/bin/python scripts/nexus/build_nexus_deck.py \
    --coverage out/nexus/<project>/coverage.json --profile deep
```

表紙、`pipeline-coverage`、完了フェーズごとの `phase-digest`（`exec` は領域ごと）、
`open-questions`、レポート付録を `out/nexus/<project>/pages/` に書き出す。
いずれも解釈を挟まず、パイプライン自身の記録から機械的に決まるページ。

### 4. 解釈が要るページを書き足す

背骨は digest の間に番号を空けてある。該当レポートを読み、
`references/nexus-reports.ja.md` の対応表でテンプレートを選び、スロット JSON を書いて
同じディレクトリへレンダリングする。

```bash
.venv/bin/python scripts/nexus/collect.py --project <dir> \
    --report reports/02_evaluation/mmi-overview.md      # 見出し・表・mermaid
.venv/bin/python scripts/render_slide_template.py --template score-card \
    --data out/nexus/<project>/data/score.json --density print \
    --out out/nexus/<project>/pages/165-mmi-score.json
```

全ページに `source`（レポートのパスと `generated_at`）を必ず入れる。
数値はレポートの表から取る。記憶からも、再計算からも作らない。

### 5. 画像

```bash
.venv/bin/python scripts/mermaid_export.py <report.md> --list      # 描画対象の確認
.venv/bin/python scripts/mermaid_export.py <report.md> --index 1 --out out/nexus/<p>/shots/x.png
.venv/bin/python scripts/html_shot.py <ui-mock>.html --out out/nexus/<p>/shots/s01.png
```

構造図（`graph`・`erDiagram`・`sequenceDiagram`）は画像化する。チャート系は
意図的に対象外 — レポートの表から `score-breakdown` / `issue-register` で描き直すほうが
デッキ全体と揃う。**貼る前に必ず PNG を Read で開く**。スタイルが当たらなかった
モックでも撮影自体は成功するし、横長の `graph LR` は描画できてもスライドでは読めない。

### 6. 統合・検証・生成

```bash
.venv/bin/python scripts/assemble_spec.py --out out/nexus/<p>/deck.json \
    --title "<タイトル>" out/nexus/<p>/pages/
.venv/bin/python scripts/build_deck.py --template templates/blank-16x9.json \
    --spec out/nexus/<p>/deck.json --dry-run --strict
```

監査の指摘をすべて潰してから生成する。生成後は（選ばれていれば）`slide-qa` に渡し、
デッキが確定したら `out/nexus/<project>/` を削除する。

パイプラインが進んだあとの再実行では、spec を作り直して
`build_deck.py --into <deck> --update-slides <ページ>` を使い URL を保つ。
カバレッジのページは毎回変わるので、毎回作り直すこと。

## 規則

- **プロジェクトに書き込まない。** レポートも状態ファイルも編集しない。
  `nexus-status.sh` は `--json` モードでしか呼ばない。
- **数値・担当者・日付を創作しない。** レポートに書いていないことは
  open-questions のページに載せる。
- **レポートの語彙をそのまま使う**（MMI の帯域、DDD 用語、関係種別）。
  平易な言い換えは出典との対応を切ってしまう。
- **要約は結論ではない。** `phase-digest` が運ぶのはフェーズ自身が記録した要約。
  それを超える主張をするなら、レポートを開いた状態で書く。
- 高密度になるのは想定内。行を黙って削るのではなく `print` 密度とパックの
  `textMargin` で詰める。削ったときは、そのページの `source` に明記する。
