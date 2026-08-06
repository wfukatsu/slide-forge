---
name: google-slides-template
description: >-
  Duplicate an existing Google Slides template (master deck) and generate a
  presentation that follows its layouts. Confirms template, purpose, outline,
  and length interactively via AskUserQuestion, then covers template analysis
  and registration (template.json), deck generation, and visual QA from
  thumbnails. For designing from scratch without a template, use the
  google-slides skill; for Scalar company/product decks, use the
  scalar-product-slides skill (a dedicated workflow layered on top of this one).
  Triggers: "このテンプレートでスライドを作って", "マスタースライドから生成", "テンプレートを登録",
  "テンプレートを解析", "gslides-template", "create slides from this template",
  "use this master", or when given a Google Slides template URL.
---

# Template-Driven Google Slides Generation

## Important

- **Scope of this skill**: duplicate an existing Google Slides presentation as the **design source of truth** and flow text into its layouts.
- **Run every command from the slide-forge root as cwd.** The relative paths `scripts/…`, `templates/…`, and `.venv/bin/python` resolve from there. The root is `${CLAUDE_PLUGIN_ROOT}` when this skill runs from an installed plugin (the placeholder is substituted to the install path); on a local clone it is `/Users/wfukatsu/work/slide-forge`. Literal `cd` paths below assume the local clone — substitute the plugin root when installed.
- **Out of scope**:
  - Designing from scratch without a template → `google-slides` skill (composer, infographics, code-first `deckkit` decks)
  - Scalar company/product/feature decks → `scalar-product-slides` skill (a dedicated workflow layered on top of this one)
  - Customer-specific Scalar solution proposals (challenge-driven) → `scalar-proposal-slides` skill (same layering)
  - Authoring PPTX files from scratch → `document-skills:pptx`. Exporting a deck generated here to `.pptx` (delivery format) → `pptx-export` skill, chosen via the 出力形式 intake question
  - Changing the template's own design → **the Slides API does not support creating or editing masters/layouts.** Do it in the Google Slides UI.
- Python 3.10+ is required. `.venv` is a **symlink** to `~/.claude/venvs/gslides`, shared with the pre-consolidation skills. Changing dependencies affects everything that uses this venv.
- Credentials are discovered in this order: `$GSLIDES_CONFIG_DIR` → `config/` in the repo (canonical) → `~/.claude/skills/google-slides/config/` (legacy fallback). If OAuth was already set up for the old skills, it keeps working unchanged.
- **Drive folder rule**: every generated deck gets its own Drive folder with all related files under it. Create it with `.venv/bin/python scripts/drive_folder.py create "<Deck title>" [--parent <URL/ID>]`, pass the printed ID as `--folder` to `build_deck.py`, then `drive_folder.py upload <FOLDER_ID> deck.json …` for the spec, `.drawio` sources, and figure PNGs. Report the folder URL together with the deck URL.
- Dense cloud architecture / data-flow / network diagrams (nested containers, 10+ nodes) → author the figure with the `drawio-diagrams` skill (draw.io → PNG → insert as an `image` part).
- **When updating an existing deck the user already has** (same URL, in-place edits — as opposed to the normal flow of generating a fresh copy), run `.venv/bin/python scripts/snapshot_version.py <URL>` first to record the pre-edit revision and take a local PPTX backup, and report the revision ID to the user before editing. Rollback is via the Slides UI "File → Version history".
- **Visual QA is a separate skill (`slide-qa`), chosen at generation time.** A clean API response cannot tell you whether text overflows, whether an arrow crosses over another shape, or whether a connector attaches to the semantically correct shape — so QA defaults to **run** and is recommended as such. Settle the choice during intake (Phase 1, `references/interactive-intake.md`); when the user opts out, skip Phase 5, state clearly in the report that the deck is unverified, and offer `slide-qa` as a follow-up. When QA runs, it ends by deleting the local QA files (`scripts/cleanup_qa.py`).
- **If the premises are unspecified, settle them with `AskUserQuestion` before generating.** Template, purpose, outline, and length are the branch points that force a full rebuild when wrong. Phase 1 and `references/interactive-intake.md` give the procedure. Do not ask about items the user already specified or when they said "your call" — state the adopted premise in one line and proceed.

## Quick Reference

| Task | Command |
|---------|---------|
| List registered templates (material for interactive choices) | `.venv/bin/python scripts/list_templates.py` / `--json` |
| Interactive intake procedure (AskUserQuestion) | `references/interactive-intake.md` |
| Analyze and register a template | `.venv/bin/python scripts/inspect_template.py <URL> --emit templates/<id>.json --name <id>` |
| Fetch layout thumbnails | `.venv/bin/python scripts/inspect_template.py <URL> --thumbnails out/layouts` |
| Validate a deck spec (no API calls) | `.venv/bin/python scripts/build_deck.py --template … --spec … --dry-run` |
| Generate a deck | `.venv/bin/python scripts/build_deck.py --template … --spec … --title "…"` |
| Visual QA of the output (optional, default: run) | `slide-qa` skill — `.venv/bin/python scripts/fetch_thumbnails.py <URL> --out out/qa [--pages 9-16]` |
| Delete local QA files after verification | `.venv/bin/python scripts/cleanup_qa.py` |
| Snapshot a version before editing an existing deck | `.venv/bin/python scripts/snapshot_version.py <URL> [--out out/backups]` |
| Create the deck's Drive folder / collect related files | `.venv/bin/python scripts/drive_folder.py create "<title>"` / `upload <FOLDER> <files…>` |
| Dense cloud/data-flow diagrams (draw.io → PNG) | `drawio-diagrams` skill + `references/drawio.md` |
| Assemble page fragments into one spec | `.venv/bin/python scripts/assemble_spec.py --out deck.json --title "…" out/<deck>/pages` |
| Fan-out generation of large decks (sub-agents) | `references/parallel-generation.md` |
| Validation gates (offline check + thumbnail QA) | `references/validation.md` |
| Generate an image with AI | `.venv/bin/python scripts/images.py --prompt "…" --style flat_vector --out out/x.png` |
| Search icons | `.venv/bin/python scripts/icons.py --list` / `--search 情報銀行` |
| Fetch cloud icons (**required once, first time**) | `.venv/bin/python scripts/fetch_cloud_icons.py` |
| Search cloud icons | `.venv/bin/python scripts/cloud_icons.py --search s3` / `--list --vendor aws` |
| Catalog of every component (8 families, 45 types, one deck; live spec examples) | `examples/design-catalog.json` |
| Drawing diagrams (`Canvas`) and drafting conventions | `references/diagrams.md` |
| Tables and charts | `references/charts.md` |
| Table/chart catalog (live spec example) | `examples/charts-demo.json` |
| Business framework figures | `references/patterns.md` |
| Framework figure catalog (live spec example) | `examples/patterns-demo.json` |
| Slide patterns (6 skeletons × 35 body patterns) | `references/slide-patterns.md` |
| Index of every pattern (59 slides, one pattern each) | `examples/slide-pattern-index.json` |
| Read-alone (handout) style catalog (30 slides) | `examples/read-alone-guide.json` |
| Code samples with highlighting | `references/code-blocks.md` |
| Code block catalog (live spec example) | `examples/code-blocks-demo.json` |
| Deck outline templates (problem-solving / new-business proposal / product intro / talk) | `references/deck-outlines.md` |
| Images and illustration figures | `references/images.md` |
| Icon library | `references/icons.md` |
| Cloud icons (AWS/GCP/Azure) | `references/cloud-icons.md` |
| Illustration catalog (live spec example) | `examples/illustration-gallery.json` |
| Icon catalog (live spec example) | `examples/icon-gallery.json` |
| Cloud architecture diagrams (live spec example) | `examples/cloud-architecture.json` |
| ScalarDB architecture (using `Canvas` directly) | `examples/scalardb-architecture.py` |
| ScalarDL architecture (mixing three icon families) | `examples/scalardl-architecture.py` |
| template.json schema | `references/template-schema.md` |
| API constraints and pitfalls | `references/api-notes.md` |
| Registered templates | `templates/*.json` |

---

## Phase 0: Prerequisites

1. Python and dependencies. The venv is shared; the real environment lives at `~/.claude/venvs/gslides`:

```bash
cd /Users/wfukatsu/work/slide-forge
.venv/bin/python -c "import googleapiclient; print('ok')"
```

If it is broken or missing, rebuild the shared venv and re-link. If
`~/.claude/venvs/gslides-requirements.txt` does not exist, seed it from the
repo's `requirements.txt` first:

```bash
[ -f ~/.claude/venvs/gslides-requirements.txt ] || \
  cp /Users/wfukatsu/work/slide-forge/requirements.txt ~/.claude/venvs/gslides-requirements.txt
python3 -m venv ~/.claude/venvs/gslides
~/.claude/venvs/gslides/bin/pip install -U -r ~/.claude/venvs/gslides-requirements.txt
rm -rf /Users/wfukatsu/work/slide-forge/.venv
ln -s ~/.claude/venvs/gslides /Users/wfukatsu/work/slide-forge/.venv
```

> Create the symlink with an **absolute path**. In environments where the
> directory itself is a symlink, relative links fail to resolve and break.

> To add a dependency, edit `~/.claude/venvs/gslides-requirements.txt`. The
> repo's `requirements.txt` is a record, not the actual install source.

2. Authentication: `credentials.json` must exist in one of the discovery
locations (`$GSLIDES_CONFIG_DIR` → `config/` in the repo → the legacy
`~/.claude/skills/google-slides/config/`). If none exists, have the user create
an OAuth 2.0 desktop client in Google Cloud Console and **enable both the
Slides API and the Drive API**. `token.json` is generated automatically on the
first run.

3. **Only when drawing cloud architecture diagrams**: the official AWS / Google
Cloud / Azure icons are **vendor assets that cannot be redistributed, so they
are not committed to the repo**. Fetch them once:

```bash
.venv/bin/python scripts/fetch_cloud_icons.py          # 1-2 min, ~8.6 MB
.venv/bin/python scripts/fetch_cloud_icons.py --verify # check they are present
```

Using `cloud_icon` before fetching stops with an error that points to this
step. Do not commit the fetched assets (`assets/cloud-icons/` is gitignored).
Details in `references/cloud-icons.md`.

4. **Access to the template**: duplication requires Drive view + copy
permission. A shared file with "Disable download, print, copy" cannot be
duplicated.

5. **Only if using AI image generation** (`ai_image` / cover images), a billed
`GEMINI_API_KEY` is required (optional) — as an env var or saved to
`config/gemini_api_key` (gitignored). The shape-drawn `illustrations` /
`patterns` need no key.

---

## Phase 1: Settle the Design Interactively

For a new deck with unspecified premises, **settle the decisions with
`AskUserQuestion` before generating anything**. Skipping this and producing 40
slides means a full rebuild when a premise turns out wrong.

When the user has **no usable template at all** and wants one designed to
their brand (colors/fonts/logo), hand off to the **`template-forge`** skill
first — it creates and registers a new master; then come back here to
generate the deck against the new id.

Decisions to settle (each one forces a rebuild when wrong):

| Decision | Default | Impact when wrong |
|---|---|---|
| Template | `scalar-2026` | Every layout and color changes |
| Purpose (Proposal / Presentation family) | Proposal | A deck with a mismatched register |
| Outline type | Problem-solving | The narrative order changes = every slide reordered |
| Length | ~20 slides | Information density per slide changes |

Key points of the procedure (details, question wording, and concrete options
are in **`references/interactive-intake.md`**):

1. **Build the options from live data.** Build the template choices from
   `scripts/list_templates.py` output. Hardcoded lists rot when templates are
   added or removed.
2. **Ask in batches.** Do not go one question per round trip. At most 3 round
   trips (4 premise questions → content → outline approval).
3. **Never skip the outline approval gate.** Before writing any JSON, present
   slide count, layouts, and each slide's headline in the conversation body and
   get approval. After approval, run straight through to QA.
4. **Never ask about**: coordinates, font sizes, component choice, colors.
   Those are this skill's responsibility. Also do not ask about items the user
   already specified or delegated ("your call") — but state the adopted
   premises explicitly.

```bash
.venv/bin/python scripts/list_templates.py        # human-readable
.venv/bin/python scripts/list_templates.py --json # material for building options
```

---

## Phase 2: Analyze and Register the Template

**If Phase 1 selected an already-registered template, skip this phase
entirely.** Analyze and register only when given a new (unregistered) URL.

```bash
.venv/bin/python scripts/inspect_template.py "<template URL>" \
    --emit templates/<id>.json --name <id> --thumbnails out/layouts
```

The emitted `template.json` contains the page size, color scheme, every
layout's `layoutId` / placeholder structure / element coordinates / default
text styles / decorations, and the IDs of the slides bundled with the template.

### Verifying roles (mandatory, human judgment)

`roles` is a **guess** derived from display names and placeholder structure; it
cannot be trusted as-is.

1. Open the PNGs produced by `--thumbnails` with the Read tool and check what
   each layout actually looks like
2. Resolve every "N candidates, needs confirmation" and "unassigned roles"
   entry in the report
3. Edit `roles` in `template.json` to finalize it, and record the verification
   date and reasoning in `__roles_note`

`.venv/bin/python scripts/layout_sample.py --template templates/<id>.json`
generates a catalog deck that flows sample strings into every layout. Use it to
visually verify role assignments.

Standard role names: `COVER` / `SECTION` / `CONTENT` / `TITLE_ONLY` / `BLANK` /
`CLOSING`. If a template has purpose-specific families (proposal vs. talk),
adding custom roles like `CONTENT_PRESENTATION` is fine. Roles are just
aliases; a layout key can also be specified directly.

> **The same layout can have more than one appearance.** For example, in a
> layout with a full-page white rectangle that covers the master's footer, the
> copyright notice defined on the template side is not shown. If `decorations`
> contains a full-page-sized rectangle, suspect this.

---

## Phase 3: Write the Deck Spec

Write the slide structure as JSON.

```json
{
  "title": "Title of the generated presentation",
  "slides": [
    { "layout": "COVER", "title": "…", "subtitle": "…", "body": "2026年MM月DD日\n会社名", "notes": "speaker notes" },
    { "layout": "SECTION", "title": "Section name", "body": "supporting line" },
    { "layout": "CONTENT", "title": "Action title", "body": ["item 1", "item 2"] },
    { "layout": "CLOSING" }
  ]
}
```

- `layout`: a role name or a layout key
- `body`: a string (used as-is) or an array (joined with newlines)
- `bodies`: for 2/3-column layouts. Write `[["left line 1","left line 2"], ["right line 1"]]` and the arrays flow into BODY index 0, 1, 2… in order. Mutually exclusive with `body`
- `notes`: optional speaker notes
- **Specifying a placeholder the layout does not have is an error.** See `placeholders` in `template.json` to learn what each layout has. Entries with `#N` such as `["TITLE","BODY","BODY#1"]` indicate multiple columns.

### How to write titles

Write what can be **claimed**, not what is shown (the action-title principle).

- Bad: "Revenue trend"
- Good: "Revenue grew 20% YoY for three consecutive quarters"

### Estimating body text volume

Placeholder default fonts are often large, tuned for hand-written decks. Tune
Japanese body text with `bodyFontSize` / `bodyLineSpacing` / `bodySpaceAbove` /
`bodySpaceBelow` (per slide, or globally via `defaults`).

```json
{ "defaults": { "bodyFontSize": 13, "bodyLineSpacing": 115,
                "bodySpaceAbove": 0, "bodySpaceBelow": 3 }, "slides": [ ... ] }
```

Estimate fit with this formula. **The API returns no error when text
overflows**, and `--dry-run`'s `audit_text_fit` only inspects `figures`, so you
must compute body fit yourself.

```
paragraph height = wrapped lines × fontSize × 1.2 × (lineSpacing / 100)
                   + spaceAbove + spaceBelow      ← per-paragraph margins add up
capacity         = (body h[in]) × 72 ≥ sum of all paragraph heights
chars per line   = (body w[in] − 0.1×2) × 72 ÷ fontSize   ← count full-width as 1, half-width as 0.5
```

> **Always include paragraph spacing in the estimate.** Most templates' BODY
> placeholders carry `spaceAbove` / `spaceBefore` margins around paragraphs;
> ignoring them makes the real capacity roughly 60% of the estimate. Measured
> example (`aixdevops` CONTENT, body 9.0 × 4.244 in):
>
> | Settings | Paragraphs that fit |
> |---|---|
> | 13pt / 140% / default paragraph spacing (unspecified) | **10** |
> | 13pt / 115% / paragraph spacing 0 | **18** |
> | 12pt / 115% / 3pt below each paragraph | **16** |
>
> An empty line (`""`) also consumes the same height as one paragraph.
> Overflowing text collides with the footer and gets clipped.

### Always validate before generating

```bash
.venv/bin/python scripts/build_deck.py --template templates/<id>.json \
    --spec deck.json --dry-run
```

This checks layout resolution and placeholder consistency without any API
calls. Pass this before the real run. Add `--strict` to make a single figure
audit warning exit with an error (recommended as a CI-style pre-generation
gate). See `references/validation.md` for how this gate relates to thumbnail
QA.

### If the deck exceeds 12 slides, do not write the spec alone

**Once the outline and action titles are fixed, fan the pages out to
sub-agents.** The procedure that keeps the spec JSON out of the main agent's
context is **`references/parallel-generation.md`** (2-3 slides per agent,
self-verification, model choice by page difficulty, assembly via
`assemble_spec.py`).

```bash
mkdir -p out/<deck>/pages          # each agent writes exactly one 0120-*.json
.venv/bin/python scripts/assemble_spec.py \
    --out out/<deck>/deck.json --title "Deck title" out/<deck>/pages
```

**Four jobs must never be delegated: the outline, the titles, sourcing the
numbers, and the assembly.** Splitting them breaks cross-slide logic and source
consistency. Below 10 slides, the fan-out overhead costs more than it saves —
write the spec yourself.

---

## Phase 4: Generate

```bash
.venv/bin/python scripts/build_deck.py \
    --template templates/<id>.json --spec deck.json \
    --title "Deck title" [--folder "<Drive folder URL or ID>"]
```

Processing steps:

1. Duplicate the template with `drive.files().copy()`
2. Delete the slides bundled with the template
3. Create each slide with `createSlide(layoutId)` + `placeholderIdMappings`, fill with `insertText`
4. Draw page numbers as text boxes (`--no-page-numbers` suppresses this)
5. Execute `batchUpdate` in chunks of 500 (transient 5xx / 429 retried with exponential backoff)
6. If there are speaker notes or image size corrections, re-fetch the presentation and apply them in a second `batchUpdate` (both need information that only exists after creation)
7. If images were temporarily uploaded, delete them from Drive and revoke public sharing

**Decorations, logos, and footers on the template side are inherited
automatically by the copy — never draw them yourself** (you would get double
rendering). `masterDecorations` in `template.json` is a record of "what is
already drawn", not a drawing instruction.

### Nine ways to show things visually — choose by purpose first

| What to show | Use | Characteristics |
|---|---|---|
| Structure, procedure, numeric relationships | `diagrams.Canvas` (`references/diagrams.md`) | Precise. Relationships between elements are guaranteed |
| Tables and charts (comparison, trend, composition) | `charts` (`table` / `vbars` / `vbars_stacked` / `linechart` / `pie` …) | Tables are native and editable afterwards. Zero-baseline, fixed series colors, and other conventions built in |
| Concepts, metaphors, actors | `illustrations` (`icon_flow` / `pyramid` / `iceberg` …) | Drawn with shapes. **No key, deterministic output**, theme colors |
| Business framework staples | `patterns` (`posmap` / `gantt` / `orgchart` / `lean_canvas` / `nested_circles` / `testimonial`) | The standard figures for proposals and ringi. No key, theme colors |
| Page skeletons and analysis figures | `pages` (`governing_message` / `lead_in` / `so_what` / `source_note` / `exhibit_frame` / `waterfall` / `rating_matrix` …) | How to compose a page; only density varies by purpose. No key, theme colors |
| Domain-vocabulary icons | `icons` (`asset_icon` / `asset_icon_flow` …) | 62 brand assets. Brand-compliant. **Requires network** |
| Cloud architecture diagrams | `cloud_icons` (`cloud_icon` / `cloud_zone` …) | 1,757 official AWS/GCP/Azure icons. **Never recolor or rotate**. Requires network |
| Mood, scenery, covers | `images` (`ai_image` / `image`) | AI-generated or local images |
| Code samples | `code_block` (java / graphql / json / bash) | Monospace + VS Code Dark+ style highlighting. **Square corners** |

All nine are methods on the same `Canvas`, so they can be mixed on one slide.
From a deck spec (JSON) they are available via `figures`. **For details — code
examples, component inventory, drafting and layout conventions, and using
`build_deck.py` as a library — read `references/diagrams.md`.** Per-family
usage: `references/charts.md` / `references/patterns.md` /
`references/slide-patterns.md` / `references/images.md` / `references/icons.md`
/ `references/cloud-icons.md` / `references/code-blocks.md`; live examples are
the demo specs in `examples/`.

### Diagram essentials (details and rationale in `references/diagrams.md`)

- **Always call all four audits before generating.** `audit_bounds()` (shapes outside the frame) / `audit_connectors()` (floating or buried arrows) / `audit_overlaps()` (hidden text, colliding labels) / `audit_text_fit()` (too much text for the box). All are defects detectable from coordinates alone; left unchecked, you only find them in the thumbnails.
- **Never draw connecting lines between shapes by coordinates.** Choose as follows.

| Purpose | Use |
|---|---|
| Shape A → B, should follow when moved | `d.connect(a, b)` |
| Shape A → B, must sit exactly on the edge | `d.link(a, b)` |
| Route bends, axes, leader lines | `d.line(..., free=True)` |

- **Never put text inside a rotated shape.** Draw the shape without `text` and overlay a `label()`.
- **When in doubt, use `illustrations`.** They work offline and always follow the template's colors. Only AI generation (`ai_image`) needs a billed `GEMINI_API_KEY`.
- `--dry-run` expands figures to coordinates and audits them without API calls (`--strict` errors out on a single warning).

---

## Phase 5: Visual QA (optional — `slide-qa` skill)

Run this phase **when the user chose to run QA at intake (the default)**. When
they opted out, skip it, say explicitly in the report that no visual
verification was done, and offer the `slide-qa` skill as a follow-up.

The procedure — thumbnail fetch, inspection priorities, checklist, fix loop,
and cleanup — is owned by the **`slide-qa` skill**; follow it. In short:

```bash
.venv/bin/python scripts/fetch_thumbnails.py "<generated deck URL>" --out out/qa --size LARGE
# … inspect with Read, fix the spec and regenerate on any defect …
.venv/bin/python scripts/cleanup_qa.py   # always delete the local QA files when done
```

- If the deck exceeds 15 slides, split the QA across sub-agents with
  `--pages 9-16` (6-8 slides each, findings returned as text only —
  `references/parallel-generation.md`).
- On any defect, fix `deck.json` or the layout choice and **regenerate**;
  never patch the artifact. Delete superseded decks from Drive
  (`drive.files().delete(fileId=…)`) — the user holds exactly one URL.
- The full checklist and reporting rules are in `references/validation.md`.

**Pass QA yourself before presenting results.** Do not let the user find
defects that a visual pass would have caught. Then, if there is still room to
adjust, offer via `AskUserQuestion`: "finalize / adjust wording / change how a
figure is shown / adjust slide count" (`references/interactive-intake.md`,
section 4). When rebuilding, **delete the old artifact from Drive first**, then
regenerate.

---

## Error Handling

| Symptom | Cause and fix |
|------|-----------|
| `プレゼンテーション ID を抽出できません` | Unexpected URL shape. Pass the `<ID>` from `/presentation/d/<ID>/` directly |
| `credentials.json が見つかりません` | Phase 0 auth setup. Confirm both the Slides API and the Drive API are enabled |
| `RefreshError` / `invalid_grant` | Expired auth token. Delete `token.json` from the active config dir (`config/token.json`, or the legacy `~/.claude/skills/google-slides/config/token.json`) and re-run; the browser re-auth flow starts |
| 403 on copy | No copy permission on the template. Ask the owner for "Viewer (can copy)" |
| `Invalid requests[N].createSlide: layout not found` | `template.json` is stale; the template was probably edited. Re-analyze |
| Page numbers missing | The Slides API cannot instantiate SLIDE_NUMBER placeholders. Confirm `add_page_numbers()` is called |
| Footer doubled | You drew a footer the template already provides. Remove your own drawing |
| Text cut off mid-way | Placeholder height insufficient. Reduce the text, or switch to another layout that has `BODY` |

**Principle on failure**: delete a deck that failed mid-generation (the
template copy already exists in Drive), fix the spec, and **rebuild from
scratch**. Partial patches to a half-built artifact are not reproducible, and
with copy-based generation a re-run is faster anyway.

---

## File Layout

All paths are relative to the repository root `/Users/wfukatsu/work/slide-forge`.

| Path | Role |
|------|------|
| `scripts/_auth.py` | OAuth (discovery: `$GSLIDES_CONFIG_DIR` → `config/` → legacy), unit conversion, color conversion, URL → ID extraction |
| `scripts/inspect_template.py` | Template analysis → `template.json`, layout thumbnail fetch |
| `scripts/build_deck.py` | Template copy → deck generation (`TemplateDeck`). Also owns spec validation (`--dry-run` / `--strict`) |
| `scripts/fetch_thumbnails.py` | Thumbnail fetch for visual QA (used via the `slide-qa` skill). `--pages 9-16` restricts the range (for split QA); `--size SMALL/MEDIUM/LARGE` |
| `scripts/cleanup_qa.py` | Deletes local QA files when verification is done (`out/qa`, `out/qa-*`, `out/*/qa`; only touches `out/`). `--dry-run` previews |
| `scripts/assemble_spec.py` | Concatenates per-page JSON fragments in ascending order into one deck spec. The assembler for fan-out generation |
| `scripts/layout_sample.py` | Generates a layout sample deck, one slide per layout. For visually verifying role assignments |
| `scripts/list_templates.py` | Lists registered templates (roles, layout count, bundled slide count). Material for interactive template choices. Has `--json` |
| `scripts/fetch_cloud_icons.py` | One-time fetch of the official AWS/GCP/Azure icon sets into `assets/cloud-icons/` (gitignored). `--verify` checks presence |
| `scripts/diagrams.py` | Diagram primitives (`Canvas`): flows, cards, hbar charts, shape connectors (`connect` / `link`), rotation and transparency, code blocks (`code_block`, highlighted, square corners), `font` selection, self-audits (`audit_bounds` / `audit_connectors` / `audit_overlaps` / `audit_text_fit`) |
| `scripts/charts.py` | Tables and charts (`ChartMixin`): native tables, vbars, grouped vbars, `vbars_stacked`, line charts, pie/donut. Enforces zero baselines and fixed, CVD-verified series colors in the implementation |
| `scripts/illustrations.py` | Illustration figures (`IllustrationMixin`): 30 pictograms and 12 metaphor figures. Shape-only — no key, no network |
| `scripts/patterns.py` | Business framework figures (`PatternMixin`): posmap / gantt / orgchart / lean_canvas / nested_circles / testimonial. No key, no network |
| `scripts/pages.py` | Page components and analysis figures (`PageMixin`): governing_message / lead_in / so_what / source_note / exhibit_frame (skeletons) + mece_tree / waterfall / rating_matrix (analysis) + exec_summary / storyline / ghost (deck design) — 11 components. Blocks empty sources and mismatched totals in the implementation. No key, no network |
| `scripts/icons.py` | Icon library (`IconLibraryMixin`): renders SVGs from `assets/scalar/pictograms/` to PNG with recoloring and places them. Also a search/list CLI |
| `scripts/cloud_icons.py` | Cloud icons (`CloudIconMixin`): official AWS/GCP/Azure SVGs rendered **without recoloring**. Also a search CLI |
| `scripts/images.py` | Images (`ImageMixin`): AI generation (Gemini, cached) and insertion of local/URL/Drive images. Works standalone as a CLI |
| `scripts/colors.py` | Color utilities (`Palette` / `lighten` / `readable_on`), shared by diagrams / charts / illustrations / patterns / images |
| `scripts/deckkit.py`, `scripts/render_deck.py`, `scripts/validate_layout.py` | The code-first deck path of the `google-slides` skill (deck modules in Python, offline coordinate validation). Shared repo, different entry point — see `references/validation.md` |
| `config/` | Canonical location for `credentials.json` / `token.json` |
| `assets/scalar/pictograms/` | 62 Scalar brand icons (`icons.json` + `svg/` + backup `png/`) |
| `assets/scalar/logos/`, `assets/scalar/product-logos/` | Scalar / ScalarDB / ScalarDL logos (PNG and SVG) |
| `assets/cloud-icons/` | 1,757 official AWS / Google Cloud / Azure icons (`cloud-icons.json` + `<vendor>/<category>/*.svg`). Gitignored; restore with `scripts/fetch_cloud_icons.py` |
| `references/template-schema.md` | Schema of `template.json` and the deck spec JSON |
| `references/diagrams.md` | Drawing diagrams (`Canvas`): code examples for the families, line attachment, the 4 audits, color and layout conventions, library usage |
| `references/charts.md` | Tables and charts (`charts.py`): usage and design conventions |
| `references/patterns.md` | Business framework figures (`patterns.py`) |
| `references/slide-patterns.md` | Slide patterns (`pages.py`): the 6 skeletons with **standard coordinates**, rationale for the conventions, talk-vs-handout density, anti-patterns |
| `references/parallel-generation.md` | Fanning out large decks page-by-page to sub-agents: jobs that must not be split, model choice, QA splitting |
| `references/validation.md` | The two validation gates: offline coordinate checks (`--dry-run` / `validate_layout.py`) and thumbnail QA — what each catches, what only eyes catch, the fix loop, reporting rules |
| `references/code-blocks.md` | Code blocks (`code_block`): usage and height estimation |
| `references/interactive-intake.md` | Interactive intake: AskUserQuestion question sets, the outline approval gate, what never to ask |
| `references/deck-outlines.md` | Deck outline templates (problem-solving / 15-section new-business proposal / product intro / talk). The "outline" options in intake come from here |
| `references/images.md` | Images and illustrations: when to use which, full method list |
| `references/icons.md` | Icon library: lookup, colors, constraints, adding assets |
| `references/cloud-icons.md` | Cloud icons: lookup, drawing API, license terms, update procedure |
| `references/api-notes.md` | Google Slides API constraints and pitfalls found by measurement |
| `examples/design-catalog.json` | **Catalog of every component** (49 slides): 8 families, 44 of the 45 `FIGURES` types actually drawn. Only `aiImage` stays spec-only because it needs a billed `GEMINI_API_KEY` (with a key, switch the slide back to `aiImage` and regenerate). When unsure which visual to use, generate this first and look |
| `examples/read-alone-guide.json` | **Read-alone (handout) style catalog** (30 slides): all 11 `pages.py` components plus an anti-pattern collection, acted out on a fictional case ("order-processing cost reduction"). A deck for **learning density and style** |
| `examples/slide-pattern-index.json` | **Index of every slide pattern** (59 slides): 6 skeletons × 35 purpose-specific pages, one pattern per slide. A deck for **choosing pages by looking at them**. Generate and show it when the user should point at the pages to build with |
| `examples/illustration-gallery.json` | Deck spec using every pictogram, every metaphor figure, and image placement (live example) |
| `examples/icon-gallery.json` | Deck spec using every icon and the 5 `asset_icon_*` methods (live example) |
| `examples/cloud-architecture.json` | Deck spec for cloud architecture diagrams (zones, multi-cloud, data flows) (live example) |
| `examples/scalardb-architecture.py` | ScalarDB architecture: cloud icons + logos + connectors composed with `Canvas` |
| `examples/scalardl-architecture.py` | ScalarDL architecture (4 layers / Auditor topology / tamper-detection flow): mixing three icon families |
| `templates/*.json` | Registered templates |
| `templates/scalar-2026.json` | Scalar Slide Master 2026 (8 layouts, Proposal / Presentation families) |
| `templates/scalar-2026-boilerplate.json` | Scalar Slide Master 2026 + 12 boilerplate slides (company overview, CEO profile, product overview, customers, case studies, …). Layouts identical to `scalar-2026`; the only difference is the bundled slides. Use with `--keep-existing` to keep them. Registered 2026-08-01 |
| `templates/aixdevops.json` | AIxDevOps Theme (Scalar co-brand. 22 layouts, 2/3-column, Proposal / Presentation families, `CLOSING` with QR code. Re-analyzed 2026-08-01) |
| `templates/corporate.json` | Corporate Master (derived from aixdevops: navy scheme, brand elements removed) |
| `templates/themes/*.json` | Design-token themes for the `google-slides` composer path (`scalar.json`, `aixdevops.json`, `corporate.json`) |

## Deriving a Recolored Master from an Existing Template

The Slides API **cannot create masters/layouts, but it can modify existing
ones** (`references/api-notes.md`, section 1). If a good template already
exists, you can duplicate it and swap only the colors and brand elements to
produce a derived master. `templates/corporate.json` was made this way from
`aixdevops`.

> This procedure is now automated: the **`template-forge`** skill /
> `scripts/build_template.py` runs the whole derivation (or styles Google's
> default master from scratch) from a design spec, including registration.
> The manual steps below remain as the reference for what it does.

Procedure:

1. Duplicate the template with `drive.files().copy()` and delete all bundled slides
2. **Delete brand-specific elements with `deleteObject`** (wordmarks, product logos, screenshots of the source deck, …). Object IDs survive a Drive copy, so the IDs from the analysis can be used directly
3. **Overwrite every element that references theme colors with explicit RGB.** `colorScheme` cannot be changed via the API, so anything left as `theme:ACCENT5` resolves to the original palette
4. Analyze with `inspect_template.py` → verify `roles` → register
5. Verify visually with thumbnails

> **Always check `propertyState` before rewriting colors.** Templates
> sometimes contain a "transparent full-page rectangle that only carries a
> color" (`propertyState: NOT_RENDERED`); painting it makes it opaque and it
> covers the master's logo and footer. Details in `references/api-notes.md`,
> section 3b.

## Relationship with the `google-slides` Skill

Both skills now live in this one repository and share `scripts/`, `assets/`,
`config/`, and `templates/`. They are two entry points over the same engine:

| | This skill | `google-slides` |
|---|---|---|
| Approach | Template-driven: flow text into an existing master's layouts | From scratch: composer over a blank/16:9 template, infographics, architecture diagrams, plus the code-first `deckkit` path (deck modules in Python, rendered by `render_deck.py`) |
| Generation origin | Master copy (`scripts/build_deck.py`) | `presentations().create()` + BLANK drawing / `render_deck.py` |
| Source of design truth | `templates/<id>.json` (layout structure, coordinates, role assignments) | `templates/themes/*.json` design tokens (font hierarchy, table styles, chart colors) and `deckkit` layout constants |
| Offline validation | `build_deck.py --dry-run --strict` | `validate_layout.py` (see `references/validation.md`) |

`templates/scalar-2026.json` and `templates/themes/scalar.json` **point at the
same master (`1shiZp7…`)**. Both exist because they serve different roles, as
above. Copy-based generation is implemented **only in this skill's path**
(`build_deck.py`).

When the master itself is updated, keep both in sync:

1. Re-analyze: `.venv/bin/python scripts/inspect_template.py <URL> --emit templates/scalar-2026.json --name scalar-2026`
2. Re-verify and finalize `roles`
3. Cross-check and update `layouts.*.layoutId` and `master.sampleSlideIds` in `templates/themes/scalar.json`
