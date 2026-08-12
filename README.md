# slide-forge

Agent-driven Google Slides deck generation for Codex and Claude Code: seventeen
generation/support skills plus one end-to-end workflow on a shared Python
engine. It covers corporate-template decks, from-scratch architecture
diagrams, template creation from a design spec, validation before generation,
optional thumbnail-based visual QA (on by default), PowerPoint (`.pptx`)
export, and line-item spreadsheets (Excel / Google Spreadsheet) for estimates
and BOMs.

```
intake → author (spec JSON or Python) → validate (offline, free) → generate → visual QA (opt-in, default on) → cleanup → PPTX export (opt-in)
                                            ↑____________fix_____________________|
```

## Skills

| Skill | What it does |
|---|---|
| `google-slides-template` | Generate a deck from a registered Google Slides master template: interactive intake, template analysis/registration (`template.json`), spec authoring with `--dry-run` validation, page-fragment authoring for large decks (parallel when permitted, sequential otherwise), generation. The main workflow. |
| `google-slides` | From-scratch decks without a corporate master. Spec path (`templates/blank-16x9.json` + the same engine) or code-first path (`deckkit.py` + offline layout validation for connector-heavy diagrams). |
| `template-forge` | Create and register a **new template (master)** from a design spec — brand colors, fonts, logo, footer (`scripts/build_template.py`). The Slides API cannot create masters, so a base (Google default or a registered template) is copied and its layouts restyled via batchUpdate; roles are assigned deterministically and the result lands in `templates/<id>.json`, ready for `google-slides-template`. Ships 3 design presets (`templates/presets/`). |
| `slide-template-creator` | Create and register reusable **single-slide content templates** with semantic input slots, examples, offline validation, and catalog previews. These live under `slide-templates/` and are independent of Google Slides masters. |
| `current-state-analysis` | Run **current-state analysis / problem-identification frameworks** (現状分析・課題の特定) on user-supplied material and render the results with the `analysis` pack: PEST, Five Forces, process pain-points, logic tree, KPI tree, why-why, fishbone, Pareto, As-Is/To-Be gap analysis and an impact-effort priority matrix (SWOT / 3C reuse the `marketing-analysis` pack). Facts go in the figures, interpretation in the insight, sources are mandatory, and each template's guardrails encode the method's misuse patterns. |
| `analysis-template-creator` | Create and maintain the **analysis-framework slide templates** themselves (the `slide-templates/analysis/` pack) and their drawing primitives (`fishbone`, `pareto` are the precedents): encodes the framework-specific design rules — one question per template, fact/interpretation slot split, required sources, misuse guardrails — and follows `slide-template-creator`'s schema/validation/registration rules for everything else. |
| `b2b-account-maps` | Build the two account maps a B2B software deal turns on: an **influence map** of the buying committee (影響力 × 賛否, champion highlighted) and a **discovery map** colouring each MEDDPICC item confirmed / partly known / still assumed, plus the committee table, approval path, pain chain, and the gaps with who to ask by when. Eight page templates ship as the `b2b-sales` pack under `slide-templates/`. Internal working artifacts, not customer-facing pages. |
| `scalar-account-plan` | Keep one **sales ledger per customer** (`accounts/<AE>/<customer>/account.json`) — facts labelled said / observed / assumed, the buying committee, MEDDPICC status, the pain chain, BANT risk, the current stage's exit criteria with the customer-side evidence for each, and the open actions — and render it as a nine-page **activity plan whose URL never changes** (`build_deck.py --into` replaces the pages of the existing deck). What the ledger cannot answer becomes the deliverable: `account_ledger.py gaps` checks the playbook's ten review questions and turns every unanswered one into an action with a person to ask, a deadline and a completion condition, carried over between runs and written as both a slide and Markdown for the CRM. Internal only. |
| `scalar-account-planning-session` | Build the annual **Account Planning Session** decks for an account the ledger already covers — a full Plan Document for the account team and a nine-page executive review deck — from one `aps.json` that adds the customer's published material to the ledger. Ties each proposal to a sentence of the customer's own mid-term management plan, gives every deal its own chapter, and works out **who to meet next** per legal entity from published officer lists and org charts, each name carrying the person we would go through. The builder holds only the layout; every string lives in `aps.json` under the ignored `accounts/` tree. Internal only. |
| `scalar-ae-materials` | Build **one visit's materials**, routed by deal phase (0–6) × audience × purpose, so the customer-facing one-pager, the internal visit plan, the WPS win plan and the Deal Desk / 稟議 packet are never the same file. Includes a pre-generation check that no judgement about a named individual, competitor weakness or unconfirmed figure reaches anything a customer will read, and files each artifact under `<root>/<AE name>/<customer name>/{00_活動計画, 01_顧客提示, 02_顧客提案, 90_社内}` in Drive. Eight page templates ship as the `scalar-ae` pack. Rules come from `references/scalar/sales-playbook.md`. |
| `scalar-product-slides` | Scalar Inc. company/product/feature deck workflow on the `scalar-2026` templates. |
| `scalar-proposal-slides` | Customer-specific Scalar solution proposals driven by the customer's challenges: hearing checklist, challenge→product mapping (`references/scalar/proposal-map.md`), and a problem-solving proposal structure with a rewritable worked example (`scripts/scalar/build_scalar_proposal.py`). |
| `drawio-diagrams` | Dense cloud architecture / data-flow / network diagrams authored as draw.io files, exported to PNG headlessly (`drawio` CLI), visually QA'd, and inserted into decks. The editable `.drawio` is archived in the deck's Drive folder. |
| `image-slots` | Fill the empty picture frames of an **existing** deck with AI-generated images (`scripts/fill_image_slots.py`): finds the frames the same three ways template registration does (PICTURE placeholders, empty image elements left in a layout, frames the deck reuses), draws each picture for that frame's shape, and places it filling the frame. Standalone on any deck URL — including decks slide-forge did not generate — and needs no registered template. For decks still driven by a spec, put `aiImage` in the spec instead and regenerate. |
| `slide-qa` | Thumbnail-based visual QA of a generated deck: fetch every page as PNG, inspect against a defect checklist, drive the fix-and-regenerate loop, then delete the local QA files (`scripts/cleanup_qa.py`). Invoked by the generation skills when the user opts in at intake (the default), or standalone on any deck URL. |
| `pptx-export` | Export a generated deck to PowerPoint (`.pptx`) as a delivery format (`scripts/export_pptx.py`): Drive API export with automatic fallback past the 10MB limit, saved locally and optionally archived in the deck's Drive folder. Chosen at intake (出力形式) when PPTX delivery is expected, or run standalone on any deck URL. From-scratch PPTX authoring stays with `document-skills:pptx`. |
| `spreadsheets` | Line-item spreadsheets — estimates, BOMs, cost breakdowns — as Excel and/or Google Spreadsheet from one JSON spec (`scripts/build_sheet.py`): typed columns, real formulas for amounts and subtotal/tax/total, `--dry-run` validation, and in-place updates that keep the Spreadsheet URL stable. Companion to a proposal deck's cost slide (same Drive folder), or standalone. Worked example: `examples/estimate-sample.json`. |

## End-to-end workflow

The `forge` workflow runs the whole pipeline as one continuous flow: route to
the right generation skill → interactive intake (including visual-QA and
output-format choices) → outline approval → spec + offline validation →
generation → visual QA via `slide-qa` (when chosen) → QA-file cleanup → PPTX
export via `pptx-export` (when chosen) → final report.

- Codex: invoke the `forge` skill by name.
- Claude Code: use `/forge` or `/slide-forge:forge`.

### Account Executive workflow

Two more commands cover the sales side, where the deliverable is not a deck but
the AE's next action:

- `/account <顧客名>` — create or update a customer's activity plan. Reads the
  ledger, records what came out of the last meeting, checks the playbook's ten
  review questions, turns the unanswered ones into dated actions, and replaces
  the contents of the same activity-plan deck (the shared link keeps working).
- `/visit <顧客名>` — prepare one visit. Routes phase × audience to the right
  material type, keeps customer-facing and internal artifacts in separate
  files and folders, generates and files them, then writes the visit back to
  the ledger and refreshes the activity plan.

Both keep the source of truth in `accounts/<AE 名>/<顧客名>/account.json`
(git-ignored) and file the output under `<Drive ルート>/<AE 名>/<顧客名>/`.
The Drive root is asked once and remembered in `config/sales.json`. The phases,
gate IDs, five material types and ten checkpoints all live in
`references/scalar/sales-playbook.md`.

## Repository layout

```
.agents/      Codex skill discovery links and the Codex-native forge skill
AGENTS.md     Codex project rules and host-tool compatibility mappings
skills/       shared SKILL.md definitions used by Codex and Claude Code
commands/     Claude Code slash commands (/forge, /account, /visit)
accounts/     per-customer sales ledgers (git-ignored; never committed)
scripts/      shared engine — one importable package
  _auth.py        OAuth helper (Slides + Drive)
  build_deck.py   template-driven generator (TemplateDeck); --dry-run validation
  diagrams.py     Canvas drawing hub (aggregates the mixins below)
  charts.py illustrations.py patterns.py pages.py events.py   figure libraries
  icons.py cloud_icons.py images.py                 pictograms, vendor icons, AI images
  inspect_template.py assemble_spec.py layout_sample.py list_templates.py
  account_graph.py build_account_graph.py   influence / discovery graphs -> .drawio
  scalar/account_ledger.py       per-customer sales ledger: validate, gaps, slot data
  scalar/account_workspace.py    Drive tree <root>/<AE>/<customer>/… (idempotent)
  scalar/build_account_plan.py   ledger -> activity-plan deck (same URL on update)
  export_template_master.py import_template_master.py   bundled masters <-> Drive
  fetch_thumbnails.py cleanup_qa.py fetch_cloud_icons.py export_pptx.py
  build_sheet.py  line-item spreadsheets (xlsx + Google Spreadsheet)
  deckkit.py render_deck.py validate_layout.py      code-first path (offline checks)
  drawio_export.py drive_folder.py snapshot_version.py   draw.io export, Drive folders, version snapshots
  scalar/         Scalar deck builders
templates/    registered masters (scalar-2026*, aixdevops, corporate) + blank-16x9 + themes/ + presets/ (template-forge design presets)
  masters/        drop a master .pptx here and import it (gitignored; see its README)
slide-templates/ reusable single-slide content templates + registry
assets/       scalar/ (brand: pictograms, logos, product-logos), cloud-icons/ (gitignored)
references/   engine, workflow, and host compatibility documentation
  images/slide-patterns/  pattern catalog images (gitignored; generated in Setup)
examples/     runnable spec catalogs and code-first example decks
config/       credentials.json + token.json (gitignored, 0600)
cache/ out/   transient render cache and QA output (gitignored)
```

## Install as a Claude Code plugin

The repo doubles as a plugin marketplace (`.claude-plugin/marketplace.json`,
one plugin bundling all seventeen skills):

```
/plugin marketplace add wfukatsu/slide-forge
/plugin install slide-forge@slide-forge
```

Skills become available as `slide-forge:<skill-name>`, and the pipeline
command as `/slide-forge:forge`. After installing,
run the Setup below inside the plugin root (`${CLAUDE_PLUGIN_ROOT}`) — the
venv, OAuth credentials, and cloud icons are machine-local and not bundled.
Alternatively, clone the repo and symlink `skills/*` into `~/.claude/skills/`
(the layout used during development); pick one of the two, not both, or the
skills will be listed twice.

## Use with Codex

Codex uses the same skills and Python engine. In a repository clone, the
`.agents/skills/` entries expose all seventeen generation/support skills plus the
end-to-end `forge` skill. Start Codex from the repository root and invoke
`forge` by name; the Claude-specific `/slide-forge:forge` command and plugin
marketplace manifest are not required.

Project-wide Codex instructions live in `AGENTS.md`. Host-tool mappings,
sequential fallback for environments where agent delegation is unavailable,
and setup details are documented in
[`references/codex-compatibility.md`](references/codex-compatibility.md).

The `.agents/skills/*` symlinks point back to `skills/*`, so Codex and Claude
Code read the same skill definitions rather than maintaining two copies.

Verify discovery from the repository root by asking Codex to list or use the
`forge`, `google-slides`, and `slide-qa` skills. No Claude plugin installation
is needed for Codex.

## Requirements

- **Python 3.10+** (macOS / Linux)
- A Google account that can create Google Slides / Drive files
- **draw.io desktop** — only for the `drawio-diagrams` skill:
  `brew install --cask drawio` (the export script also finds the app-bundle
  binary at `/Applications/draw.io.app`)
- A Gemini API key — only for optional AI image generation

## Setup

All commands run from the slide-forge root: the clone directory for Codex or a
local Claude setup, and `${CLAUDE_PLUGIN_ROOT}` for a Claude plugin install.

**Some things are generated on your machine rather than committed** — the
vendor cloud icons and the slide masters. They are large (a master is 6–8MB),
machine-specific, or not ours to redistribute, so the repository ships the
means to produce them instead of the files. A clone is not fully usable until
you have run the steps below that you need.

| Generated here | Why not committed | Step |
|---|---|---|
| `assets/cloud-icons/` | AWS / Google Cloud / Azure do not permit redistribution | [4](#4-cloud-vendor-icons-only-for-cloud-architecture-figures) |
| `templates/masters/*.pptx` | 6–8MB each; the master has to live in *your* Drive to be copied | [5](#5-slide-masters-for-the-copy-mode-templates) |

### 1. Python environment

The repo expects `.venv` at its root. A local environment is the simplest
cross-host setup:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

For Claude plugin installations that can be replaced during upgrades, keeping
the real environment outside the plugin root is useful. Create a shared venv
and point `.venv` at it with an absolute symlink. The historical
`~/.claude/venvs/gslides` location remains supported but is not required by
Codex or by the engine.

### 2. Google Cloud OAuth client (one-time)

The engine calls the Slides + Drive APIs as **you**, via an OAuth desktop
client (scopes: `auth/presentations`, `auth/drive`). In
[Google Cloud Console](https://console.cloud.google.com/):

1. Create (or pick) a project.
2. **APIs & Services → Library** — enable **Google Slides API** and
   **Google Drive API**.
3. **APIs & Services → OAuth consent screen** — configure the app
   (Internal for a Workspace org; External works too — add yourself as a
   test user while the app is in Testing).
4. **APIs & Services → Credentials → Create credentials → OAuth client ID →
   Desktop app** — download the JSON and save it as `config/credentials.json`
   (`chmod 600`). Override the directory with `$GSLIDES_CONFIG_DIR` if you
   keep credentials elsewhere.

### 3. First run / verify

```bash
.venv/bin/python scripts/list_templates.py
```

CLI messages are English by default; set `GSLIDES_LANG=ja` for Japanese
(`export GSLIDES_LANG=ja`, or per command). This affects only the scripts'
terminal output — never the generated deck or spreadsheet content.

The first call opens a browser consent screen and writes `config/token.json`
(refreshed automatically afterwards). If a template list prints, auth works.

### 4. Cloud vendor icons (only for cloud architecture figures)

AWS / Google Cloud / Azure icon sets are vendor assets and are **not
committed**; fetch them once:

```bash
.venv/bin/python scripts/fetch_cloud_icons.py
```

### 5. Slide masters (for the `copy`-mode templates)

`scalar-2026`, `scalar-2026-boilerplate`, `corporate` and `aixdevops` are
`generationMode: copy` templates: generating duplicates a real Google Slides
presentation. `templates/<id>.json` only *points* at one, so on a fresh clone
those templates cannot work until the master exists in your own Drive.

The masters themselves are **not committed** — 6–8MB each, and a master is only
useful once it lives in your own Drive. Pick whichever applies:

**a. Build your own.** The `template-forge` skill creates a new master from a
design spec — brand colours, fonts, logo, footer — and registers it, ready for
`google-slides-template`. Nothing else is needed; this is the path if you are
not working with an existing corporate deck.

```bash
.venv/bin/python scripts/build_template.py --help
```

**b. Register a master you already have in Drive.** Analyse it once and review
the guessed roles by hand:

```bash
.venv/bin/python scripts/inspect_template.py <URL> --emit templates/<id>.json --name <id>
```

**c. Import a `.pptx` of a master.** Save it as `templates/masters/<id>.pptx`,
then upload and re-register it in one step:

```bash
.venv/bin/python scripts/import_template_master.py --all
# or one at a time
.venv/bin/python scripts/import_template_master.py --id scalar-2026
```

Importing a `.pptx` makes Slides mint new object IDs for every layout, master
and decoration, so the script re-runs `inspect_template.py` over the imported
presentation and writes the result over `templates/<id>.json`. The
human-verified **role assignment is preserved** — only the identifiers move.
Expect `templates/*.json` to show as locally modified afterwards; that is your
machine's copy of the registration and is not meant to be committed back.

If you have edit access to a master already, write it out for a teammate with
`scripts/export_template_master.py --all`. Drive refuses to export a
Docs-editors file over 10MB (`exportSizeLimitExceeded`), so larger masters have
to be downloaded by hand from the Slides UI (File > Download > Microsoft
PowerPoint). Do **not** delete slides to get under the limit: Slides drops any
layout that no slide uses — `aixdevops` loses three registered layouts that way
— and the bundled slides listed in `existingSlideIds` are part of what those
templates offer. See [`templates/masters/README.md`](templates/masters/README.md).

`blank-16x9` is `generationMode: create` and needs no master, so the
`google-slides` spec path and every `--dry-run` validation work on a bare clone.

### 6. Slide pattern catalog images

[`references/slide-pattern-catalog.md`](references/slide-pattern-catalog.md)
shows all 43 page patterns as rendered images. Both the text and the images
(~2MB, under `references/images/slide-patterns/`) are committed, so a bare
clone reads with pictures. When a pattern is added or its rendering changes,
regenerate the catalog and commit the images with it:

```bash
.venv/bin/python scripts/build_deck.py \
    --template templates/scalar-2026.json --spec examples/slide-pattern-index.json
.venv/bin/python scripts/fetch_thumbnails.py <URL printed above> --out out/patterns --size MEDIUM
.venv/bin/python scripts/build_pattern_catalog.py --thumbs out/patterns
```

Regeneration needs a working `scalar-2026` master (step 5) and, for the three
cloud-architecture patterns, the vendor icons (step 4).

The slide-template catalog
([`references/slide-template-catalog.md`](references/slide-template-catalog.md),
images under `references/images/slide-templates/`, also committed) works the
same way: build each pack's catalog spec with
`scripts/build_slide_template_catalog.py`, generate the deck, fetch
thumbnails, and run `scripts/build_template_catalog_doc.py` — the regeneration
commands are at the top of that document.

### 7. Optional: AI image generation

For `scripts/images.py`, set `GEMINI_API_KEY` or save the key to
`config/gemini_api_key` (gitignored, like the OAuth files). The key must
belong to a **billed** project — the image model has zero free-tier quota.

### What each skill needs

| Skill | venv + OAuth | Slide master | Cloud icons | draw.io CLI | Gemini key |
|---|---|---|---|---|---|
| `google-slides-template` | ✔ | ✔ for the copy-mode templates | when drawing cloud diagrams | — | optional |
| `google-slides` | ✔ | — (blank-16x9 needs none) | when drawing cloud diagrams | — | optional |
| `scalar-product-slides` | ✔ | ✔ scalar-2026 | when drawing cloud diagrams | — | — |
| `scalar-proposal-slides` | ✔ | ✔ scalar-2026 | — | to edit the bundled environment diagram | — |
| `drawio-diagrams` | ✔ (for deck insertion) | — | — | ✔ | — |
| `slide-qa` | ✔ | — | — | — | — |
| `pptx-export` | ✔ | — | — | — | — |
| `spreadsheets` | ✔ (OAuth only for Google Spreadsheet output) | — | — | — | — |
| `template-forge` | ✔ | base master, if copying one | — | — | — |

Secrets hygiene: `config/` (credentials, tokens, API keys), `out/`, `cache/`,
and `assets/cloud-icons/` are gitignored — nothing machine-local is ever
committed. Keep Drive sharing on your master decks restricted; their file IDs appear in
`templates/*.json`. Masters are not committed either: `templates/masters/` is gitignored, so a
master .pptx you drop there stays local. Review what a master contains before
sharing one — `scalar-2026-boilerplate` carries company and customer-facing
slides.

## Quick start (template-driven)

```bash
.venv/bin/python scripts/list_templates.py                 # registered templates
.venv/bin/python scripts/build_deck.py \
    --template templates/scalar-2026.json --spec deck.json --dry-run --strict
.venv/bin/python scripts/build_deck.py \
    --template templates/scalar-2026.json --spec deck.json
.venv/bin/python scripts/fetch_thumbnails.py <URL> --out out/qa   # visual QA (slide-qa skill)
.venv/bin/python scripts/cleanup_qa.py                            # delete QA files when done
.venv/bin/python scripts/export_pptx.py <URL> --folder <FOLDER>   # optional PPTX delivery (pptx-export skill)
```

Register a new master: `scripts/inspect_template.py <URL> --emit templates/<id>.json --name <id>`,
then review the guessed roles by hand (see the google-slides-template skill).

## Quick start (code-first)

A deck is one Python module; a function is one slide. See
`examples/pattern-gallery/deck.py` and `references/diagram-cookbook.md`.

```bash
.venv/bin/python scripts/validate_layout.py mydeck.py   # offline checks, no API calls
.venv/bin/python scripts/render_deck.py     mydeck.py   # validates, then generates
```

`validate_layout.py` catches footer intrusion, off-slide geometry, title
wrapping, floating/buried connector endpoints, text hidden behind
later-drawn shapes, and text overflow — before any API call. What it cannot
judge (arrow routing, contrast, whether the figure communicates) is what the
thumbnail QA of the `slide-qa` skill is for: see `references/validation.md`.

## Slide pattern catalog

Which page shapes can this build? See
[`references/slide-pattern-catalog.md`](references/slide-pattern-catalog.md) —
43 patterns in 8 groups, each with a rendered image, when to use it, and the
`figures` type names to write in the spec. The layout rules behind them are in
[`references/slide-patterns.md`](references/slide-patterns.md).

| Group | Patterns | Picks |
|---|---|---|
| 骨格 6 種 | 6 | How the page itself is laid out |
| 構成ページ | 4 | Deck scaffolding — summary, agenda, storyline, ghost |
| 定量ページ | 7 | Arguing with numbers |
| 比較・評価ページ | 6 | Putting options side by side |
| 構造・論理ページ | 7 | Making a relationship visible |
| 計画・体制ページ | 5 | Time and people |
| 定性・技術ページ | 5 | Everything that isn't a number |
| 締め・付録ページ | 3 | The decision and what follows |

Beyond these page patterns, `slide-templates/` registers 37 ready-made
one-page templates in five packs (marketing-analysis, b2b-sales, scalar-ae,
planning, analysis). Each is catalogued with a rendered image, the question it
answers, and its guardrails in
[`references/slide-template-catalog.md`](references/slide-template-catalog.md).

## Examples

Every spec under `examples/` is authored against **`templates/scalar-2026.json`**
and validates cleanly against it. They are not portable to
`templates/blank-16x9.json` — that template has no TITLE placeholder and
declares no `CLOSING` role, so the same spec reports dozens of findings.
`corporate` and `aixdevops` accept some of them; `scalar-2026` accepts all.

```bash
.venv/bin/python scripts/build_deck.py \
    --template templates/scalar-2026.json --spec examples/<name>.json --dry-run --strict
```

| Example | Slides | Shows |
|---|---|---|
| `charts-demo.json` | 5 | Tables and graphs — the `charts.py` catalog |
| `patterns-demo.json` | 7 | Layout patterns from `patterns.py` |
| `illustration-gallery.json` | 13 | Concept figures from `illustrations.py` |
| `icon-gallery.json` | 10 | The pictogram library (`icons.py`) |
| `code-blocks-demo.json` | 2 | Syntax-highlighted code blocks |
| `event-announcement.json` | 4 | Seminar / conference announcement parts |
| `read-alone-guide.json` | 30 | Density patterns for print / read-alone decks |
| `design-catalog.json` | 49 | The full design-pattern catalog †|
| `slide-pattern-index.json` | 60 | One page per pattern — 1 slide = 1 pattern †|
| `cloud-architecture.json` | 6 | Cloud architecture figures †|
| `b2b-account-review.json` | 13 | A worked account review built from all eight `b2b-sales` templates — cover, exec summary, both maps in their two-axis/MEDDPICC and structural forms, and their supporting pages |
| `estimate-sample.json` | 2 sheets | Line-item estimate for the `spreadsheets` skill ‡|

† Draws `cloud_icon*` / `cloud_zone` figures, so it needs the vendor icons
first — they are excluded from the repository because AWS, Google Cloud and
Azure do not permit redistribution. Without them `--dry-run` reports
`Cloud icons have not been fetched yet`; run
`.venv/bin/python scripts/fetch_cloud_icons.py` once (see
[`assets/cloud-icons/README.md`](assets/cloud-icons/README.md)). Every other
example above validates on a bare clone.

‡ A spreadsheet, not a deck — run it through `build_sheet.py` instead:
`.venv/bin/python scripts/build_sheet.py --dry-run examples/estimate-sample.json`

Code-first decks are Python modules rather than specs, and generate against
`scalar-2026` directly:

| Example | Shows |
|---|---|
| `examples/scalardb-architecture.py` | ScalarDB architecture — cloud icons, pictograms, brand logos and connectors on one slide † |
| `examples/scalardl-architecture.py` | ScalarDL architecture, same mix † |
| `examples/pattern-gallery/deck.py` | The `deckkit.py` code-first path |

## License

MIT. Cloud vendor icons remain the property of their vendors and are fetched
locally under their respective terms (see `references/cloud-icons.md`).
