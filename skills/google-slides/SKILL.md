---
name: google-slides
description: >-
  Generate Google Slides presentations and infographics from scratch (no registered
  corporate master) with Python + the Google Slides API, using the shared slide-forge
  engine: spec-driven decks on a blank 16:9 template, or code-first decks with offline
  layout validation for diagram-heavy material.
  Triggers: "Google Slides を作って", "スライドを生成", "gslides", "インフォグラフィクスを作って",
  "create Google Slides", "generate slides", "create infographic", or when a Google Slides
  URL is included.
---

# Google Slides Generation (from scratch)

## Important

- **Scope**: building decks WITHOUT a registered corporate master. Two paths, both on the shared engine in this repo:
  - **Spec path** — `templates/blank-16x9.json` + `scripts/build_deck.py --spec deck.json` for typical text/figure decks
  - **Code-first path** — write the deck as a Python module (`deckkit.py`), validate coordinates offline, render with `scripts/render_deck.py`
- **Routing**:
  - User has a template/master URL, or wants text flowed into an existing corporate layout → `google-slides-template` skill
  - Scalar company/product/use-case decks → `scalar-product-slides` skill
  - Dense cloud architecture / data-flow / network diagrams (nested containers, 10+ nodes) → author them with the `drawio-diagrams` skill (draw.io → PNG → insert); simple concept figures stay on `diagrams.py`
  - Authoring PPTX files from scratch → `document-skills:pptx` (exporting a deck generated here to `.pptx` → `pptx-export` skill); Slidev → `slidev` skill
  - A bare "make slides" request uses this skill only when a Google Drive / Google Slides context is explicit
- **Working directory**: the slide-forge root — `${CLAUDE_PLUGIN_ROOT}` when running from an installed plugin, `/Users/wfukatsu/work/slide-forge` on a local clone. All commands below run from there (literal paths assume the local clone).
- **Auth** is centralized in `scripts/_auth.py`. It finds `credentials.json` / `token.json` in: `$GSLIDES_CONFIG_DIR` → `config/` at the repo root (canonical) → the old skill layout (transitional fallback). Never write per-script inline auth.
- **Visual QA is a separate skill (`slide-qa`), chosen at generation time** (Phase 5). Default: run — recommend it when asking (Phase 1); a clean API response cannot show overflow or misattached arrows. If the user opts out, skip Phase 5, state in the report that the deck is unverified, and offer `slide-qa` as a follow-up. When QA runs, it ends by deleting the local QA files (`scripts/cleanup_qa.py`).
- On QA failure, **delete the broken presentation and regenerate** from the fixed spec/module. Never patch a live deck with incremental API edits.
- The delete-and-regenerate rule applies only to decks generated in the current session. **When updating an existing deck the user already has** (inserting or fixing slides in place, keeping the same URL), first run `scripts/snapshot_version.py <URL>` to record the pre-edit revision (keepForever pin attempt + local PPTX backup), report the revision ID to the user, and only then edit. Rollback is via the Slides UI "File → Version history".

## Quick Reference

| Task | Where |
|------|-------|
| Build from a JSON spec | `scripts/build_deck.py` + `templates/blank-16x9.json` |
| Write a deck as Python | `scripts/deckkit.py` (+ `examples/pattern-gallery/deck.py`, `examples/scalardb-scalardl/deck.py`) |
| Validate layout offline (no API) | `scripts/validate_layout.py` + `references/layout-contract.md` |
| Render a Python deck | `scripts/render_deck.py` |
| Visual QA (optional, default: run) | `slide-qa` skill (`scripts/fetch_thumbnails.py` + checklist + cleanup) |
| Delete local QA files after verification | `scripts/cleanup_qa.py` |
| Snapshot a version before editing an existing deck | `scripts/snapshot_version.py` |
| Diagrams (flows, architecture) | `scripts/diagrams.py` (Canvas) + `references/diagrams.md`, `references/diagram-cookbook.md` |
| Dense cloud/data-flow diagrams (draw.io → PNG) | `drawio-diagrams` skill + `scripts/drawio_export.py` + `references/drawio.md` |
| Drive folder per deck (create / collect files) | `scripts/drive_folder.py` |
| Charts and tables | `scripts/charts.py` + `references/charts.md` |
| Shape-drawn pictograms and metaphor figures | `scripts/illustrations.py` + `references/pictogram-catalog.md` |
| Business-framework figures (posmap, gantt, orgchart…) | `scripts/patterns.py` + `references/patterns.md` |
| Page scaffolding and analysis figures | `scripts/pages.py` + `references/slide-patterns.md` |
| Scalar brand pictograms | `scripts/icons.py` + `assets/scalar/pictograms` + `references/icons.md` |
| Cloud vendor icons (AWS/GCP/Azure) | `scripts/cloud_icons.py` + `assets/cloud-icons` + `references/cloud-icons.md` |
| Restore cloud icons (first use) | `scripts/fetch_cloud_icons.py` |
| AI-generated images (covers, section art) | `scripts/images.py` (needs `GEMINI_API_KEY`) + `references/images.md` |
| API pitfalls | `references/google-slides-api.md`, `references/api-notes.md` |
| Deck composition recipes | `references/composers/{basic,content,product,usecase,enterprise,db-middleware}.md` |

---

## Phase 0: Environment check

1. **venv** — `.venv` at the repo root is a symlink to the shared venv `~/.claude/venvs/gslides`. Verify:

   ```bash
   cd /Users/wfukatsu/work/slide-forge
   .venv/bin/python -c "import googleapiclient; print('ok')"
   ```

   If broken or missing, recreate the shared venv and relink:

   ```bash
   python3 -m venv ~/.claude/venvs/gslides
   ~/.claude/venvs/gslides/bin/pip install -U -r requirements.txt
   ln -sfn ~/.claude/venvs/gslides /Users/wfukatsu/work/slide-forge/.venv
   ```

2. **Credentials** — confirm `config/credentials.json` exists (OAuth 2.0 Desktop client; Slides API and Drive API enabled in the GCP project). `config/token.json` is created on first run via a browser auth flow. If `credentials.json` is missing, stop and ask the user to place it — do not generate or run anything until it is confirmed.

3. **Optional capabilities** (check only if the deck needs them):
   - Cloud icons: they are not bundled (vendor license terms forbid redistribution). Verify with `.venv/bin/python scripts/cloud_icons.py --list --vendor aws | head`; if missing, run `.venv/bin/python scripts/fetch_cloud_icons.py` once (~1–2 min).
   - AI images: `images.py` needs `GEMINI_API_KEY` (env var, or a `config/gemini_api_key` file — gitignored). If unset and the deck wants generated imagery, fall back to `illustrations.py` or ask the user.

---

## Phase 1: Choose a path

| | Spec path | Code-first path |
|---|---|---|
| Author | `deck.json` (JSON spec) | `deck.py` (Python module) |
| Best for | Typical decks: text pages, standard figures, charts, page patterns | Connector-heavy architecture diagrams, dense custom drawings, anything where endpoint/overlap precision matters |
| Validation | `build_deck.py --dry-run --strict` | `validate_layout.py` (offline geometry checks) |
| Generate | `build_deck.py` | `render_deck.py` |

Guidance: default to the **spec path**. Switch to **code-first** when the deck centers on architecture/flow diagrams with many connectors — the offline validator checks connector endpoints, overlaps, and overflow that a spec dry-run cannot see.

Also settle with the user (1–2 questions max): audience and purpose, approximate page count, output Drive folder (URL/ID, optional), copyright/footer text if any, and whether to run visual QA after generation (default and recommended: run; see Phase 5). For structuring help see `references/deck-outlines.md` and `references/composers/`.

---

## Phase 2: Author

### Spec path

Write `deck.json` against `templates/blank-16x9.json`. All figure capabilities are available from the spec: diagrams (`diagrams.py` Canvas), charts/tables (`charts.py`), shape-drawn pictograms and metaphor figures (`illustrations.py`), business-framework figures (`patterns.py`), page scaffolding and analysis figures (`pages.py`), Scalar pictograms (`icons.py`), cloud icons (`cloud_icons.py`), AI images (`images.py`). See `references/template-schema.md` for the spec format and each module's reference for its parts.

### Code-first path

Write a deck module: 1 module = 1 deck, one function per slide, registered with `slide()` / `plain()` from `deckkit`. Coordinates are inches, origin top-left; `d` is a `diagrams.Canvas`. Start from the working examples:

- `examples/pattern-gallery/deck.py` — one slide per available part
- `examples/scalardb-scalardl/deck.py` — a real product/architecture deck

Contract rules (footer safe area, title height, connector attachment) are in `references/layout-contract.md`; drawing recipes in `references/diagram-cookbook.md`.

### Design principles (both paths)

- **Action titles**: every content slide title is a conclusion sentence, not a label
- **Connectors attach to shapes**, never drawn as free coordinates — the API does not validate line endpoints, so a detached arrow is invisible until QA
- Body >= 12pt, title >= 20pt; WCAG AA contrast (4.5:1); max ~6 bullets, 1 slide = 1 message; 60-30-10 color rule
- Do not guess cloud icon names — search with `scripts/cloud_icons.py --search <term>`; recoloring/rotating/flipping vendor icons is prohibited by their license terms
- Full principles and per-slide-type guidance: `references/google-slides-api.md`, `references/composers/`, `references/slide-patterns.md`

---

## Phase 3: Validate (before any API call)

Spec path:

```bash
.venv/bin/python scripts/build_deck.py --template templates/blank-16x9.json \
    --spec deck.json --dry-run --strict
```

Code-first path:

```bash
.venv/bin/python scripts/validate_layout.py path/to/deck.py \
    --template templates/blank-16x9.json
```

`validate_layout.py` is offline and free — it checks footer intrusion, off-slide geometry, title wrapping, connector endpoints (detached or buried), partial overlap of text-bearing shapes, and text overflow. Exit code 1 means fix and re-run. Never skip validation (`--skip-validate` exists on `render_deck.py` but do not use it).

---

## Phase 4: Generate

Spec path:

```bash
.venv/bin/python scripts/build_deck.py --template templates/blank-16x9.json \
    --spec deck.json --title "Deck title" [--folder <DRIVE_FOLDER_URL_OR_ID>]
```

Code-first path:

```bash
.venv/bin/python scripts/render_deck.py path/to/deck.py --title "Deck title" \
    [--folder <URL/ID>] [--only 1-5]
```

`--only` renders a page range for cheap prototyping. First run opens a browser for OAuth and writes `config/token.json`. The script prints the presentation URL — relay it to the user.

**Drive folder rule**: every generated deck gets its own Drive folder, and all related files live under it. Create the folder first, generate into it, then collect the sources:

```bash
.venv/bin/python scripts/drive_folder.py create "<Deck title>" [--parent <URL/ID>]
# pass the printed ID as --folder to build_deck.py / render_deck.py, then:
.venv/bin/python scripts/drive_folder.py upload <FOLDER_ID> deck.json figures/*.drawio out/diagrams/*.png
```

Upload whatever lets the user regenerate or edit later: the spec (`deck.json`) or deck module (`deck.py`), `.drawio` sources, and exported figure PNGs. QA thumbnails stay local. Report the folder URL together with the presentation URL.

For large decks, page-level fan-out to subagents is possible; see `references/parallel-generation.md` for what may and may not be split.

---

## Phase 5: Visual QA (optional — `slide-qa` skill)

Run when the user chose QA in Phase 1 (the default). When they opted out, skip
this phase, state in the report that no visual verification was done, and offer
the `slide-qa` skill as a follow-up.

The procedure is owned by the **`slide-qa` skill** — follow it. In short:

```bash
.venv/bin/python scripts/fetch_thumbnails.py <URL or ID> --out out/qa --size LARGE
# … inspect every PNG with Read …
.venv/bin/python scripts/cleanup_qa.py   # always delete the local QA files when done
```

Check: text clipped or overflowing its frame, elements overlapping decorations, detached connector arrows, unreadable contrast, awkward line wraps. These are invisible in API responses.

On any failure: fix the spec/module, re-run Phase 3 validation, **delete the broken presentation, and regenerate**. Repeat until the thumbnails are clean, clean up the QA files, then report the final URL.
