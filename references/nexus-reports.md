*[日本語](nexus-reports.ja.md)*
# nexus-architect Reports → Slide Templates

For the `nexus-report-slides` skill. What each kind of report becomes, how a
half-finished pipeline is represented, and why the pack is built the way it is.

## The inputs

| Source | Where | Shape |
|---|---|---|
| Phase status (architect / product) | `work/pipeline-progress.json` | every phase with `status`, `outputs`, a recorded `summary`, timestamps |
| Resolved status (optional) | `tools/nexus-status.sh <dir> --json --view=architect\|product` | the same, with `{project}` placeholders resolved, `outputs_written/declared`, staleness |
| architect reports | `reports/before/{project}/`, `01_analysis/`, `02_evaluation/`, `03_design/`, `04_stories/`, `review/` | Markdown with YAML frontmatter (`title`, `phase`, `skill`, `generated_at`, `input_files`), tables, mermaid |
| Review findings | `reports/review/individual/review-*.json` | `perspective`, `dimensions[] {name, weight, score}` |
| product reports | `reports/00_core/`, `01_ux/`, `02_spec/`, `03_domain/`, `04_quality/`, `05_adaptation/` | same Markdown shape |
| UI mocks | `reports/02_spec/ui-mocks/{STORY}-NN-{slug}.html`, `{STORY}-index.html` | self-contained clickable HTML, one file per screen |
| infra | `reports/08_infrastructure/` (`infra-design-*.md`, `env-matrix-*.md`, `adr/`, `reviews/`) or `docs/infra/` | Markdown; no phase registry |
| scalardb | generated app code, `schema.json`, `docker-compose.yml`, review findings | code artifacts; inventoried, not read |

infra and scalardb have no phase manifest, so they are represented by **which
artifacts exist**, not by a status. That is a real difference, not a gap — do
not show them as "0 % complete".

## The mapping

`collect.py` classifies every file into a `kind`; this is what each kind
becomes. One template serves several report kinds on purpose — the pack has 14
pages, not one per file.

| Report | kind | Template |
|---|---|---|
| any phase, as a chapter opener | — | `phase-digest` |
| the run as a whole | — | `pipeline-coverage` |
| `technology-stack.md`, `codebase-structure.md`, `tech-stack-fitness.md` | investigation / domain | `stack-inventory` |
| `issues-and-debt.md`, `review-*.json` findings | investigation / review-finding | `issue-register` |
| `mmi-overview.md`, `ddd-readiness.md`, review scores | evaluation | `score-card` |
| `mmi-by-module.md`, `ddd-tactical-*.md` | evaluation | `score-breakdown` |
| `context-map.md`, `bounded-contexts-redesign.md`, `domain-map.md` | design / domain | `context-map` |
| `target-architecture.md`, `er-diagram-current.md`, `architecture.md`, `infra-design-*.md` | design / infra | `architecture-exhibit` (mermaid → PNG) |
| `api-style-decisions.md`, `adr/adr-NNN-*.md`, `select-scalardb-edition` output | design / infra | `decision-record` |
| `transformation-plan.md`, `design-implementation` output, `change-log.md` | design / adaptation | `roadmap` |
| `personas.md`, `journey-maps.md`, `domain-story-*.md` | ux / domain-story | `persona-journey` |
| `ui-mocks/{STORY}-*.html` | ui-mock | `ui-mock-flow` (3 screens), `ui-mock-detail` (1 screen) |
| `open-questions.md`, `assumptions.md`, unfinished phases | — | `open-questions` |
| `ubiquitous-language.md`, `nfr.md`, `sla.md`, `requirements-definition.md`, generated code inventory | analysis / quality / requirements | reuse `read-alone`: `dense-comparison-table`, `claim-evidence-table`, `exec-summary-readable` |

A plain table of terms or NFR rows does not need a bespoke template — reusing
the `read-alone` pack keeps the pack from growing a page per file.

## Representing an unfinished pipeline

- `pipeline-coverage` is page 2 of every deck. Its `counts` are phase counts,
  never report counts, and `basis` names what the unfinished phases would have
  covered.
- `skipped` and `pending` are different facts. A skipped phase was a decision
  (`legacy` runs skip `define-requirements`); a pending one is simply not done.
  Never merge them into "not covered".
- A completed phase whose declared outputs are missing is a `missing-output`
  gap. A declared path carrying a `{placeholder}` (`domain-story-{domain}.md`)
  is matched as a glob first — a written report must not be reported missing.
- Every gap row carries the command that closes it (`/architect:<phase>`,
  `/product:<phase>`). When there is no command, the row says so rather than
  guessing an owner.
- `stale` (an upstream phase changed after this one ran) is a gap too: the page
  built from it may be describing a superseded state.

## Density and packing

These reports are dense, and the deck is usually read rather than projected.

- Build with `--density print` for `deep`, `presentation` for `exec`.
- Every table in the pack sets `textMargin` — `0.02in` at print, `0.04in` at
  presentation — against the `0.05in` Slides bakes into a cell. That is roughly
  one extra full-width character per side per line (`references/api-notes.md`
  §14).
- Slides gives no lever on a cell's vertical padding, so a row never shrinks
  below its font's line height. Pack vertically with `size` / `rowH` and by
  splitting the page, not by lowering `rowH` past the floor
  (`charts.min_table_row_h`).
- The row caps in each template are calibrated so the page passes
  `build_deck.py --dry-run --strict`. When the data exceeds them, split across
  pages and say so in the `source` — never drop rows silently.

## Images

- `mermaid_export.py` renders structure diagrams (`graph`, `flowchart`,
  `erDiagram`, `sequenceDiagram`, `classDiagram`) and **skips chart kinds**
  (`xychart`, `pie`, `quadrantChart`, …) by default. Chart data lives in the
  report's tables; redrawing it natively (`score-breakdown`, `issue-register`,
  `hbars`) matches the rest of the deck and stays editable.
- `html_shot.py` captures a UI mock with headless Chrome at the window size you
  give it. Chrome writes the PNG and then does not exit, so the script waits for
  the file to settle and stops the process itself.
- Read every PNG before placing it. Neither tool can tell you that a diagram is
  unreadable at slide size or that a mock lost its styles.

## Why the spine is generated and the rest is authored

`build_nexus_deck.py` writes only what the pipeline's own records settle:
coverage, per-phase digests from recorded summaries, the gap list, the report
appendix. Everything else needs a report to be **read** — which table is the
answer, which three findings matter, what the diagram is showing. Regex over a
Markdown report would produce a page that looks derived and is not, so the
interpretive pages are authored into the same `pages/` directory and merged by
`assemble_spec.py` in filename order. Digest numbering leaves 18 slots between
phases for exactly that.
