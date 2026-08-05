---
name: scalar-product-slides
description: >-
  Builds Google Slides decks for Scalar Inc. — company introductions, product
  introductions, feature catalogs, and use-case decks — end to end: confirms the
  deck type, target product, and audience via AskUserQuestion, researches facts
  from the official site and developers docs, then generates and QAs the deck.
  A Scalar-specific workflow layered on top of the google-slides-template skill
  (scalar-2026 templates) in this repo.
  Triggers: "製品紹介スライドを作って", "機能紹介スライド", "会社紹介スライド",
  "Scalar 紹介資料", "ユースケーススライド", "scalar-product-slides",
  "ScalarDB/ScalarDL の紹介資料を作って".
  Out of scope: PPTX generation (document-skills:pptx), decks about anything
  other than Scalar (use google-slides / google-slides-template), and
  customer-specific solution proposals driven by a customer's challenges
  (use scalar-proposal-slides).
---

# Scalar Product Introduction Slides

Working directory: the slide-forge root — `${CLAUDE_PLUGIN_ROOT}` when running
from an installed plugin, `/Users/wfukatsu/work/slide-forge` on a local clone
(literal `cd` paths below assume the local clone).

## Important

- **Prerequisite skill**: `google-slides-template` (same repo) — auth, the shared
  venv, the `scalar-2026` / `scalar-2026-boilerplate` templates, and cloud icons.
  Follow that SKILL.md for setup, API constraints, and the drawing API. This
  skill owns only what is Scalar-specific: deck structures, build scripts, and
  research findings. Auth and the venv are shared at the repo root
  (`config/`, `.venv`).
- **Research facts before writing them.** Company info, versions, and case
  studies start from `references/scalar/research-2026-08.md`, but **re-research
  if more than 3 months have passed since the research date** (Phase 2 below).
  Never fill gaps with guesses. Omit items you cannot confirm (e.g. capital
  stock).
- **Visual QA is a separate skill (`slide-qa`), chosen at generation time**
  (Phase 1 asks; default and recommended: run). When it runs, follow that
  skill — fetch every page with `scripts/fetch_thumbnails.py`, inspect, then
  delete the local QA files with `scripts/cleanup_qa.py`. When skipped, say
  so in the report and offer `slide-qa` as a follow-up.
- **Drive folder rule** (shared with `google-slides-template`): create a Drive
  folder for the deck first (`scripts/drive_folder.py create "<title>"`), pass
  its ID as the output folder, and collect the spec / figure sources there
  with `drive_folder.py upload`. Report the folder URL with the deck URL.
- **When updating an existing deck the user already has** (same URL, in-place
  edits — not the normal copy-the-boilerplate flow), run
  `.venv/bin/python scripts/snapshot_version.py <URL>` first to record the
  pre-edit revision and take a local PPTX backup, and report the revision ID
  before editing (rule shared with `google-slides-template`).
- **If the premises are unspecified, settle them with `AskUserQuestion` before
  researching** (Phase 1). Follow the interaction conventions in
  `references/interactive-intake.md` (sections 0, 3, 4, 5). Only the question
  set itself is specific to this skill.

## Quick Reference

| Task | Use |
|------|-----|
| Conventions for settling premises interactively | `references/interactive-intake.md` (sections 0, 3, 4, 5) |
| Company intro + product overview + use-case deck | `scripts/scalar/build_scalar_intro.py` |
| Feature catalog deck (1 feature = 1 slide, with diagrams) | `scripts/scalar/build_scalar_features.py` |
| Researched facts and pitfalls | `references/scalar/research-2026-08.md` |
| Run | `cd /Users/wfukatsu/work/slide-forge && .venv/bin/python scripts/scalar/<script>.py [--folder <Drive URL>]` |

Both scripts accept a single CLI flag: `--folder <Drive folder URL>` (optional;
when omitted the deck is created directly in My Drive).

## Phase 1: Settle the deck type and premises interactively

Decide **before** researching. Picking the wrong deck type means redoing the
research (a company intro and a feature catalog need different facts). Follow
`references/interactive-intake.md` — sections 0 (when to ask), 3 (outline
approval gate), 4 (post-generation confirmation), and 5 (how not to ask).
**Ask everything in one batch; do not go back and forth one question at a time.**

Question set (specific to this skill; ask all 4 questions of Q1 in one round):

| # | header | Question | Options |
|---|---|---|---|
| 1 | Deck type | Which deck type? | Company intro + product overview (`build_scalar_intro.py`, reuses the official boilerplate slides) / Feature catalog (`build_scalar_features.py`, 1 feature = 1 slide) / Use-case focused (feature catalog narrowed by industry) |
| 2 | Target product | Which product? | ScalarDB / ScalarDL / both |
| 3 | Audience | Who will see it? | Customers (first meeting, sales) / Engineers (evaluation, PoC) / Executives (investment decision) / Partners (sales enablement) |
| 4 | Research | How fresh must the facts be? | Use `references/scalar/research-2026-08.md` as is / Re-research (run Phase 2) |

- **Never decide Q4 on your own.** If more than 3 months have passed since the
  research date, put "Re-research" first as the recommended option and state the
  reason (research date and months elapsed) in the `description`.
- These 4 questions fill one round. If unspecified, ask for the output Drive
  folder, the cover date, the language (Japanese / English), and whether to
  run visual QA after generation (default and recommended: run; skipping means
  the deck ships unverified) together in a second round (without `--folder`,
  the deck goes directly to My Drive).
- **Do not ask about**: how diagrams are composed, coordinates, colors, or
  which diagram each feature gets. Those are fixed by `FEATURES_DB` /
  `FEATURES_DL` and the design conventions.

Once the type and target are settled, **present the slide outline (page count
and each slide's heading) and get approval before generating**. Pass this gate
before rewriting `build_plan()`.

## Phase 2: Research

Read `references/scalar/research-2026-08.md`; if it is fresh enough, use it as
is. If it is stale or new information is needed, dispatch research agents **in
parallel**:

1. Company info and news: https://scalar-labs.com/ja/ (company / news), press
   release searches
2. Product technology: https://developers.scalar-labs.com/ → the actual docs
   live at https://scalardb.scalar-labs.com/docs/latest/ and
   https://scalardl.scalar-labs.com/docs/latest/
   (start from features / overview / design / releases, then follow individual
   feature pages)
3. Use cases and case studies: the case-study category of the news feed plus
   web search (there is no dedicated case-study page)

Always instruct the agents: cite source URLs, mark unknowns explicitly as
unknown, no guessing. Update `references/scalar/` with the results and rewrite
the research date.
**Check the pitfall list (at the end of the references file) before turning
anything into slides, every time.**

## Phase 3: How to build each deck type

The type was settled in Phase 1. These are implementation notes for building it.

### A. Company intro deck (`scripts/scalar/build_scalar_intro.py`)

Copies `templates/scalar-2026-boilerplate.json` with `keep_existing=True` and
**keeps the official boilerplate slides** (company overview VISION, executive
team, product overview, customer logos, the Toyota / broadcaster case studies,
closing), inserting research-based generated slides among them. Executive photos
and customer logos cannot be reproduced, so always use this approach.

- Of the 12 bundled slides, delete the placeholder cover (position 1) and the
  sub-section heading (position 10)
- Replace the cover wording via `replaceAllText` ("<Presentation Title>" etc.)
- Insert generated slides with `add_slide(..., index=final position)`.
  **Declare the final page order in a single list (`build_plan()`) and insert
  in ascending order — that keeps the insertionIndex arithmetic trivial**
- Page numbers: SLIDE_NUMBER on the bundled slides tracks automatically.
  For generated slides, draw the final-position number with
  `draw_page_number()` (the single-slide variant). Do not use
  `add_page_numbers()` — it assumes consecutive numbering and does not mix
  well with the insertion approach

### B. Feature catalog deck (`scripts/scalar/build_scalar_features.py`)

A "1 feature = 1 slide" catalog generated from `templates/scalar-2026.json`.
All feature slides share one layout:

- Left (x 0.5–5.75): **diagram** (a per-feature `fig_*` function) plus a
  one-line caption at the bottom edge
- Right (x 6.0–9.5): **feature overview** card (≤ 200 chars as a guideline)
- Bottom: **use cases** row (bullets in 2 columns, each ≤ 28 chars as a
  guideline) plus a **key strengths** band (≤ 100 chars as a guideline)
- Top right: edition, introduced-in version, preview status
- Speaker notes: source URLs and limitations

Feature data lives in the `FEATURES_DB` / `FEATURES_DL` lists of dicts
(`title` / `figure` / `overview` / `usecases` / `value` / `edition` / `notes`).
Edit these to add, remove, or reword features. Each section opens with a 2×2
feature map.

### Design conventions (both approaches)

- **Rectangles that carry a straight accent bar must not have rounded corners**
  (`RECTANGLE`). Chips and bands without a bar may be rounded (same rule as the
  google-slides-template SKILL.md)
- Titles are action titles ("what can we claim"). The form
  "Feature name — one-line value" fits well
- Compose diagrams from the `illustrations` pictograms, `_pill` (rounded
  chips), `cloud_zone`, and `_anchored` arrows. Official cloud icons must not
  be modified

## Phase 4: Generate and QA

```bash
cd /Users/wfukatsu/work/slide-forge
.venv/bin/python scripts/scalar/build_scalar_features.py [--folder <URL>]
```

1. Before committing, the scripts run `audit_bounds / audit_connectors /
   audit_overlaps / audit_text_fit` on every slide and print "検査:" lines.
   **If any audit fires, fix the spec and rebuild** (faster than patching).
   Delete the old deck from Drive before rebuilding
2. **If the user chose visual QA (the default)**, run the `slide-qa` skill:
   fetch every page with `scripts/fetch_thumbnails.py`, inspect with Read
   (overflow, overlaps, wrong layout picked), and when done delete the local
   QA files with `scripts/cleanup_qa.py`. If QA was skipped, state so in the
   report and offer `slide-qa` as a follow-up
3. **Rebuilding changes the URL.** Tell the user the new URL and be explicit
   about what happens to the old deck (deletion)
4. Pass QA yourself before presenting results. If there is room to improve,
   offer via `AskUserQuestion`: "finalize / adjust wording / change a diagram /
   add or remove features" (`interactive-intake.md` section 4)

## File layout

| Path | Role |
|------|------|
| `scripts/scalar/build_scalar_intro.py` | Company intro deck builder (boilerplate + insertion approach; a worked 27-slide example) |
| `scripts/scalar/build_scalar_features.py` | Feature catalog deck builder (24 features with diagrams; a worked 31-slide example) |
| `templates/scalar-2026.json` | Scalar 2026 template (generated decks) |
| `templates/scalar-2026-boilerplate.json` | Scalar 2026 boilerplate template (official bundled slides) |
| `assets/scalar/{logos,product-logos,pictograms}` | Brand assets (company/product logos, pictograms) |
| `references/scalar/research-2026-08.md` | Researched facts (company, products, case studies) and 6 slide-making pitfalls |

The scripts are "worked examples you can re-run as is"; when changing the
structure, editing these two scripts is the shortest path. The architecture
diagram examples `examples/scalardb-architecture.py` /
`examples/scalardl-architecture.py` (from google-slides-template) can be used
alongside them.
