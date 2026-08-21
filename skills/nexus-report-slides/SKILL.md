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

*[日本語](SKILL.ja.md)*

# nexus-architect Report Slides

Builds an explanation deck from what a nexus-architect project has produced so
far. The project is **read only** — this skill never writes into it.

Working directory is the slide-forge root; the command is `.venv/bin/python`.

## Boundaries

| Request | Route |
|---|---|
| Explain a nexus-architect project's results as slides | this skill |
| Produce or rerun the analysis itself | nexus-architect's own `/architect:*` `/product:*` skills |
| Add or change a page template | `slide-template-creator` (pack rules: `references/nexus-reports.md`) |
| Deck generation mechanics, master selection | `google-slides-template` |
| Check the generated deck visually | `slide-qa` |
| Export to PowerPoint | `pptx-export` (or `output: local` in `config/settings.json`) |

## The unfinished pipeline is the normal case

A pipeline is usually mid-flight: phases pending, one running, another that
wrote two of its four declared outputs. Three rules follow, and they are not
optional:

1. **Establish coverage before content.** `collect.py` reads
   `work/pipeline-progress.json` (and `tools/nexus-status.sh --json` when a
   nexus-architect checkout is reachable) and writes one `coverage.json`. Page 2
   of every deck is `pipeline-coverage`, stating how many phases the deck rests on.
2. **Only completed work becomes content.** A phase with some outputs written
   is built from the files that exist, never from the ones that do not.
3. **Gaps ship as gaps.** Every pending / running / failed phase and every
   missing output becomes a row on the `open-questions` page, with the command
   that closes it. Never fill a gap with a plausible-sounding claim.

## Workflow

### 1. Intake (one round)

Ask only what is missing: the project path, the audience profile
(`exec` ≈ 12–18 pages / `deep` = every completed phase), which plugins to
cover, and QA. Read `config/settings.json` first and skip what it answers
(`references/settings.md`). Deck language follows the project's
`options.output_language`.

### 2. Collect, and show the coverage before anything else

```bash
.venv/bin/python scripts/nexus/collect.py --project <project dir>
```

Report the numbers to the user in one line — "21 of 25 architect phases, product
not started, 36 open items" — **before** proposing an outline. That number is
the premise the whole deck rests on.

### 3. Build the spine

```bash
.venv/bin/python scripts/nexus/build_nexus_deck.py \
    --coverage out/nexus/<project>/coverage.json --profile deep
```

Writes cover, `pipeline-coverage`, one `phase-digest` per completed phase (per
area for `exec`), `open-questions`, and the report appendix into
`out/nexus/<project>/pages/`. These need no interpretation and are derived
entirely from the pipeline's own records.

### 4. Author the interpretive pages

The spine leaves numbered gaps between digests. Read the specific report, map it
to a template with the table in `references/nexus-reports.md`, write the slot
JSON, and render it into the same directory:

```bash
.venv/bin/python scripts/nexus/collect.py --project <dir> \
    --report reports/02_evaluation/mmi-overview.md      # headings, tables, mermaid
.venv/bin/python scripts/render_slide_template.py --template score-card \
    --data out/nexus/<project>/data/score.json --density print \
    --out out/nexus/<project>/pages/165-mmi-score.json
```

Every page carries a `source` with the report path and its `generated_at`.
Numbers come from the report's tables — never from memory, never re-derived.

### 5. Images

```bash
.venv/bin/python scripts/mermaid_export.py <report.md> --list      # what is renderable
.venv/bin/python scripts/mermaid_export.py <report.md> --index 1 --out out/nexus/<p>/shots/x.png
.venv/bin/python scripts/html_shot.py <ui-mock>.html --out out/nexus/<p>/shots/s01.png
```

Structure diagrams (`graph`, `erDiagram`, `sequenceDiagram`) become images;
chart kinds are skipped on purpose — redraw those from the report's table with
`score-breakdown` / `issue-register` so they match the rest of the deck.
**Open every PNG with the Read tool before placing it**: a mock whose styles
failed to load still screenshots successfully, and a wide `graph LR` renders
fine yet is unreadable at slide size.

### 6. Assemble, validate, generate

```bash
.venv/bin/python scripts/assemble_spec.py --out out/nexus/<p>/deck.json \
    --title "<title>" out/nexus/<p>/pages/
.venv/bin/python scripts/build_deck.py --template templates/blank-16x9.json \
    --spec out/nexus/<p>/deck.json --dry-run --strict
```

Fix every audit finding before generating. Then generate, run `slide-qa` when
chosen, and delete `out/nexus/<project>/` when the deck is final.

Re-running as the pipeline advances: rebuild the spec and use
`build_deck.py --into <deck> --update-slides <pages>` so the URL survives. The
coverage page changes on every rerun — regenerate it each time.

## Rules

- **Never write into the project.** No report is edited, no status file is
  touched, and `nexus-status.sh` is only ever called in its `--json` mode.
- **Never invent a number, an owner or a date.** If the report does not say it,
  it belongs on the open-questions page.
- **Keep the report's own vocabulary** (MMI bands, DDD terms, relationship
  types). Translating them into looser words breaks the tie back to the source.
- **A summary is not a conclusion.** `phase-digest` carries the phase's recorded
  summary; any claim beyond it needs the report open in front of you.
- Dense pages are expected — use `print` density and the pack's `textMargin`
  settings rather than dropping rows silently. When you do cut rows, say so in
  the page's `source`.
