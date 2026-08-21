*[English](nexus-reports.md)*
# nexus-architect のレポート → スライドテンプレート対応

`nexus-report-slides` スキル用。どの種類のレポートが何になるか、途中まで進んだ
パイプラインをどう表現するか、そしてパックがこの形になっている理由。

## 入力の実態

| 供給元 | 位置 | 形式 |
|---|---|---|
| フェーズ状態（architect / product） | `work/pipeline-progress.json` | 全フェーズの `status`・`outputs`・記録済み `summary`・時刻 |
| 解決済みの状態（任意） | `tools/nexus-status.sh <dir> --json --view=architect\|product` | 上と同じ内容に、`{project}` の解決・`outputs_written/declared`・陳腐化を加えたもの |
| architect のレポート | `reports/before/{project}/`、`01_analysis/`、`02_evaluation/`、`03_design/`、`04_stories/`、`review/` | YAML frontmatter（`title`・`phase`・`skill`・`generated_at`・`input_files`）付き Markdown、表、mermaid |
| レビュー結果 | `reports/review/individual/review-*.json` | `perspective`、`dimensions[] {name, weight, score}` |
| product のレポート | `reports/00_core/`、`01_ux/`、`02_spec/`、`03_domain/`、`04_quality/`、`05_adaptation/` | 同じ Markdown 形式 |
| UI モック | `reports/02_spec/ui-mocks/{STORY}-NN-{slug}.html`、`{STORY}-index.html` | 自己完結・クリック可能な HTML（1 画面 1 ファイル） |
| infra | `reports/08_infrastructure/`（`infra-design-*.md`、`env-matrix-*.md`、`adr/`、`reviews/`）または `docs/infra/` | Markdown。フェーズ登録なし |
| scalardb | 生成されたアプリコード、`schema.json`、`docker-compose.yml`、レビュー所見 | コード成果物。読み込まず棚卸しする |

infra と scalardb にはフェーズマニフェストが無いので、状態ではなく**どの成果物が
存在するか**で表現する。これは欠落ではなく仕様の違い。「進捗 0%」と見せないこと。

## 対応表

`collect.py` が各ファイルに `kind` を割り当てる。その kind が何になるかが以下。
1 つのテンプレートを複数の kind で使い回すのは意図的（ファイルごとに 1 枚ではなく、
パック全体で 14 枚）。

| レポート | kind | テンプレート |
|---|---|---|
| 各フェーズの章扉 | — | `phase-digest` |
| 実行全体 | — | `pipeline-coverage` |
| `technology-stack.md`、`codebase-structure.md`、`tech-stack-fitness.md` | investigation / domain | `stack-inventory` |
| `issues-and-debt.md`、`review-*.json` の指摘 | investigation / review-finding | `issue-register` |
| `mmi-overview.md`、`ddd-readiness.md`、レビュースコア | evaluation | `score-card` |
| `mmi-by-module.md`、`ddd-tactical-*.md` | evaluation | `score-breakdown` |
| `context-map.md`、`bounded-contexts-redesign.md`、`domain-map.md` | design / domain | `context-map` |
| `target-architecture.md`、`er-diagram-current.md`、`architecture.md`、`infra-design-*.md` | design / infra | `architecture-exhibit`（mermaid → PNG） |
| `api-style-decisions.md`、`adr/adr-NNN-*.md`、`select-scalardb-edition` の出力 | design / infra | `decision-record` |
| `transformation-plan.md`、`design-implementation` の出力、`change-log.md` | design / adaptation | `roadmap` |
| `personas.md`、`journey-maps.md`、`domain-story-*.md` | ux / domain-story | `persona-journey` |
| `ui-mocks/{STORY}-*.html` | ui-mock | `ui-mock-flow`（3 画面）、`ui-mock-detail`（1 画面） |
| `open-questions.md`、`assumptions.md`、未完了フェーズ | — | `open-questions` |
| `ubiquitous-language.md`、`nfr.md`、`sla.md`、`requirements-definition.md`、生成コードの一覧 | analysis / quality / requirements | `read-alone` を再利用: `dense-comparison-table`、`claim-evidence-table`、`exec-summary-readable` |

用語一覧や NFR の行のような素の表に専用テンプレートは要らない。`read-alone` の
再利用で、ファイルごとにページ型が増えるのを防いでいる。

## 途中のパイプラインの表現

- `pipeline-coverage` は全デッキの 2 ページ目。`counts` はフェーズ数であって
  レポート数ではない。`basis` には、未完了フェーズが扱うはずだった論点を書く。
- `skipped` と `pending` は別の事実。スキップは判断の結果（`legacy` 実行では
  `define-requirements` を飛ばす）、未着手は単にまだやっていない。
  「対象外」に丸めない。
- 完了フェーズなのに宣言した出力が無ければ `missing-output` の未回答になる。
  `{placeholder}` を含む宣言パス（`domain-story-{domain}.md`）は先に glob で
  照合する — 書かれているレポートを「欠落」と報告しないため。
- 未回答の行には、それを埋めるコマンド（`/architect:<phase>`、`/product:<phase>`）を
  必ず併記する。コマンドが分からないときは、担当者を推測せずそう書く。
- `stale`（上流フェーズがこの実行より後に変わった）も未回答として扱う。
  そこから作ったページは、古い状態を説明している可能性がある。

## 密度と詰め方

これらのレポートは情報量が多く、デッキは投影より読み物になることが多い。

- `deep` は `--density print`、`exec` は `presentation` で組む。
- パックの全テーブルが `textMargin` を設定している（print 0.02in / presentation
  0.04in、Slides 既定のセル内余白は 0.05in）。片側あたり全角約 1 文字分が戻る
  （`references/api-notes.ja.md` 14 節）。
- セルの上下パディングを動かす手段は API に無く、行はフォントの行高より低くならない。
  縦方向は `size` / `rowH` とページ分割で詰める。`rowH` を下限より下げても効かない
  （`charts.min_table_row_h`）。
- 各テンプレートの行数上限は `build_deck.py --dry-run --strict` を通る値に
  合わせてある。データが超えるときはページを分け、`source` にその旨を書く。
  黙って行を落とさない。

## 画像

- `mermaid_export.py` は構造図（`graph`・`flowchart`・`erDiagram`・
  `sequenceDiagram`・`classDiagram`）を描画し、**チャート系**（`xychart`・`pie`・
  `quadrantChart` ほか）は既定で対象外。チャートの元数値はレポートの表にあるので、
  `score-breakdown` / `issue-register` / `hbars` でネイティブに描き直すほうが
  デッキと揃い、あとから編集もできる。
- `html_shot.py` は headless Chrome で UI モックを指定サイズで撮る。Chrome は
  PNG を書いたあと終了しないため、ファイルが安定したのを見てこちらからプロセスを
  止めている。
- 貼る前に必ず PNG を Read で開く。スライドサイズで読めないことも、モックの
  スタイルが当たらなかったことも、ツールは教えてくれない。

## 背骨は生成、残りは執筆にしている理由

`build_nexus_deck.py` が書くのは、パイプライン自身の記録だけで決まるもの
（カバレッジ、記録済み要約からの章扉、未回答一覧、レポート付録）。それ以外は
レポートを**読まないと**決まらない — どの表が答えなのか、3 つ挙げるならどれか、
その図は何を示しているのか。Markdown を正規表現で刈り取れば「導出したように見えて
実はしていない」ページができるので、解釈が要るページは同じ `pages/` に書き足し、
`assemble_spec.py` がファイル名順に統合する。章扉の番号が 18 ずつ空いているのは
そのため。
