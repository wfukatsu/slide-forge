# slide-forge

Agent-driven Google Slides deck generation for Codex and Claude Code: ten
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

## Repository layout

```
.agents/      Codex skill discovery links and the Codex-native forge skill
AGENTS.md     Codex project rules and host-tool compatibility mappings
skills/       shared SKILL.md definitions used by Codex and Claude Code
commands/     Claude Code slash command (/forge)
scripts/      shared engine — one importable package
  _auth.py        OAuth helper (Slides + Drive)
  build_deck.py   template-driven generator (TemplateDeck); --dry-run validation
  diagrams.py     Canvas drawing hub (aggregates the mixins below)
  charts.py illustrations.py patterns.py pages.py events.py   figure libraries
  icons.py cloud_icons.py images.py                 pictograms, vendor icons, AI images
  inspect_template.py assemble_spec.py layout_sample.py list_templates.py
  fetch_thumbnails.py cleanup_qa.py fetch_cloud_icons.py export_pptx.py
  build_sheet.py  line-item spreadsheets (xlsx + Google Spreadsheet)
  deckkit.py render_deck.py validate_layout.py      code-first path (offline checks)
  drawio_export.py drive_folder.py snapshot_version.py   draw.io export, Drive folders, version snapshots
  scalar/         Scalar deck builders
templates/    registered masters (scalar-2026*, aixdevops, corporate) + blank-16x9 + themes/ + presets/ (template-forge design presets)
assets/       scalar/ (brand: pictograms, logos, product-logos), cloud-icons/ (gitignored)
references/   engine, workflow, and host compatibility documentation
examples/     runnable spec catalogs and code-first example decks
config/       credentials.json + token.json (gitignored, 0600)
cache/ out/   transient render cache and QA output (gitignored)
```

## Install as a Claude Code plugin

The repo doubles as a plugin marketplace (`.claude-plugin/marketplace.json`,
one plugin bundling all ten skills):

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
`.agents/skills/` entries expose all ten generation/support skills plus the
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

### 5. Optional: AI image generation

For `scripts/images.py`, set `GEMINI_API_KEY` or save the key to
`config/gemini_api_key` (gitignored, like the OAuth files). The key must
belong to a **billed** project — the image model has zero free-tier quota.

### What each skill needs

| Skill | venv + OAuth | Cloud icons | draw.io CLI | Gemini key |
|---|---|---|---|---|
| `google-slides-template` | ✔ | when drawing cloud diagrams | — | optional |
| `google-slides` | ✔ | when drawing cloud diagrams | — | optional |
| `scalar-product-slides` | ✔ | when drawing cloud diagrams | — | — |
| `scalar-proposal-slides` | ✔ | — | to edit the bundled environment diagram | — |
| `drawio-diagrams` | ✔ (for deck insertion) | — | ✔ | — |
| `slide-qa` | ✔ | — | — | — |
| `pptx-export` | ✔ | — | — | — |
| `spreadsheets` | ✔ (OAuth only for Google Spreadsheet output) | — | — | — |
| `template-forge` | ✔ | — | — | — |

Secrets hygiene: `config/` (credentials, tokens, API keys), `out/`, `cache/`,
and `assets/cloud-icons/` are gitignored — nothing machine-local is ever
committed. Keep Drive sharing on your master decks restricted; their file IDs
appear in `templates/*.json`.

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

## License

MIT. Cloud vendor icons remain the property of their vendors and are fetched
locally under their respective terms (see `references/cloud-icons.md`).
