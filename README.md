# slide-forge

Google Slides deck generation for Claude Code: five skills on one shared
Python engine, from corporate-template decks to from-scratch architecture
diagrams, with validation before generation and thumbnail-based visual QA
after it.

```
intake → author (spec JSON or Python) → validate (offline, free) → generate → visual QA
                                            ↑____________fix____________|
```

## Skills

| Skill | What it does |
|---|---|
| `google-slides-template` | Generate a deck from a registered Google Slides master template: interactive intake, template analysis/registration (`template.json`), spec authoring with `--dry-run` validation, parallel per-page authoring for large decks, generation, mandatory thumbnail QA. The main workflow. |
| `google-slides` | From-scratch decks without a corporate master. Spec path (`templates/blank-16x9.json` + the same engine) or code-first path (`deckkit.py` + offline layout validation for connector-heavy diagrams). |
| `scalar-product-slides` | Scalar Inc. company/product/feature deck workflow on the `scalar-2026` templates. |
| `scalar-proposal-slides` | Customer-specific Scalar solution proposals driven by the customer's challenges: hearing checklist, challenge→product mapping (`references/scalar/proposal-map.md`), and a problem-solving proposal structure with a rewritable worked example (`scripts/scalar/build_scalar_proposal.py`). |
| `drawio-diagrams` | Dense cloud architecture / data-flow / network diagrams authored as draw.io files, exported to PNG headlessly (`drawio` CLI), visually QA'd, and inserted into decks. The editable `.drawio` is archived in the deck's Drive folder. |

## Repository layout

```
skills/       SKILL.md per skill (symlinked into ~/.claude/skills/)
scripts/      shared engine — one importable package
  _auth.py        OAuth helper (Slides + Drive)
  build_deck.py   template-driven generator (TemplateDeck); --dry-run validation
  diagrams.py     Canvas drawing hub (aggregates the mixins below)
  charts.py illustrations.py patterns.py pages.py   figure libraries
  icons.py cloud_icons.py images.py                 pictograms, vendor icons, AI images
  inspect_template.py assemble_spec.py layout_sample.py list_templates.py
  fetch_thumbnails.py fetch_cloud_icons.py
  deckkit.py render_deck.py validate_layout.py      code-first path (offline checks)
  drawio_export.py drive_folder.py snapshot_version.py   draw.io export, Drive folders, version snapshots
  scalar/         Scalar deck builders
templates/    registered masters (scalar-2026*, aixdevops, corporate) + blank-16x9 + themes/
assets/       scalar/ (brand: pictograms, logos, product-logos), cloud-icons/ (gitignored)
references/   engine and workflow docs (validation.md, diagrams.md, charts.md, …)
examples/     runnable spec catalogs and code-first example decks
config/       credentials.json + token.json (gitignored, 0600)
cache/ out/   transient render cache and QA output (gitignored)
```

## Install as a Claude Code plugin

The repo doubles as a plugin marketplace (`.claude-plugin/marketplace.json`,
one plugin bundling all five skills):

```
/plugin marketplace add wfukatsu/slide-forge
/plugin install slide-forge@slide-forge
```

Skills become available as `slide-forge:<skill-name>`. After installing,
run the Setup below inside the plugin root (`${CLAUDE_PLUGIN_ROOT}`) — the
venv, OAuth credentials, and cloud icons are machine-local and not bundled.
Alternatively, clone the repo and symlink `skills/*` into `~/.claude/skills/`
(the layout used during development); pick one of the two, not both, or the
skills will be listed twice.

## Requirements

- **Python 3.10+** (macOS / Linux)
- A Google account that can create Google Slides / Drive files
- **draw.io desktop** — only for the `drawio-diagrams` skill:
  `brew install --cask drawio` (the export script also finds the app-bundle
  binary at `/Applications/draw.io.app`)
- A Gemini API key — only for optional AI image generation

## Setup

All commands run from the slide-forge root (the clone directory, or
`${CLAUDE_PLUGIN_ROOT}` for a plugin install).

### 1. Python environment

The repo expects `.venv` at its root; a symlink to a shared venv is fine
(the skills use `~/.claude/venvs/gslides` so plugin updates don't wipe it):

```bash
python3 -m venv ~/.claude/venvs/gslides
~/.claude/venvs/gslides/bin/pip install -r requirements.txt
ln -sfn ~/.claude/venvs/gslides .venv        # absolute target recommended
# or simply: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

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
.venv/bin/python scripts/fetch_thumbnails.py <URL> --out out/qa
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
mandatory thumbnail QA is for: see `references/validation.md`.

## License

MIT. Cloud vendor icons remain the property of their vendors and are fetched
locally under their respective terms (see `references/cloud-icons.md`).
