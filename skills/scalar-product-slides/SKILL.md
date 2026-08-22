---
name: scalar-product-slides
description: >-
  Build Scalar Inc. decks end to end — company introduction, product
  introduction, feature catalog, use cases: confirm deck type, target product and
  audience, research the facts from the official site and developer docs, then
  generate and QA the deck.
  Use for: 製品紹介スライド, 機能紹介スライド, 会社紹介スライド, Scalar 紹介資料,
  ユースケーススライド.
  Not: customer-specific proposals driven by a customer's challenges
  (scalar-proposal-slides); decks about anything other than Scalar
  (google-slides / google-slides-template); PPTX authoring
  (document-skills:pptx).
---

*[日本語](SKILL.ja.md)*

# Scalar Product Introduction Slides

Use `references/scalar/workflow-contract.md` for shared sales-material rules
and `references/scalar/research-policy.md` for research. This skill owns only
product-deck-specific decisions and generation.

Working directory: the slide-forge root — `${CLAUDE_PLUGIN_ROOT}` when running
from an installed plugin, `/path/to/slide-forge` on a local clone
(literal `cd` paths below assume the local clone).

## Product-deck rules

- Use `google-slides-template` only for template-specific implementation details
  activated by this deck; shared auth, Drive, approval, and QA behavior comes
  from the two workflow contracts above.
- **Product facts come from the OKF bundle.** Capability, edition, version,
  release status, and pricing are looked up in the OKF bundle before any web
  research — `references/scalar/okf-bundle.md` says where it is and how to cite
  it (one version at a time, edition always stated, preview status labelled).
  Its `pricing/` figures are published list prices: citable as 定価
  (tax-excluded) and as reference-estimate material, never as a confirmed price.
- **Research facts before writing them.** Company info, versions, and case
  studies start from `references/scalar/research-2026-08.md`, but **re-research
  if more than 3 months have passed since the research date** (Phase 2 below).
  Never fill gaps with guesses. Omit items you cannot confirm (e.g. capital
  stock).

## Quick Reference

| Task | Use |
|------|-----|
| Conventions for settling premises interactively | `references/interactive-intake.md` (sections 0, 3, 4, 5) |
| Company intro + product overview + use-case deck | `scripts/scalar/build_scalar_intro.py` |
| Feature catalog deck (1 feature = 1 slide, with diagrams) | `scripts/scalar/build_scalar_features.py` |
| Product capability / edition / version / list price | `references/scalar/okf-bundle.md` → the OKF bundle |
| Researched facts and pitfalls | `references/scalar/research-2026-08.md` |
| Run | `cd /path/to/slide-forge && .venv/bin/python scripts/scalar/<script>.py [--folder <Drive URL>]` |

Both scripts accept two CLI flags: `--folder <Drive folder URL>` (optional;
when omitted the deck is created directly in My Drive) and `--dry-run`
(validate offline without calling the API).

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
  folder, cover date, and language (Japanese / English) together in a second
  round. The shared contract owns the QA question.
- **Do not ask about**: how diagrams are composed, coordinates, colors, or
  which diagram each feature gets. Those are fixed by `FEATURES_DB` /
  `FEATURES_DL` and the design conventions.

Once the type and target are settled, **present the slide outline (page count
and each slide's heading) and get approval before generating**. Pass this gate
before rewriting `build_plan()`.

## Phase 2: Research

Read `references/scalar/research-2026-08.md`; if it is fresh enough, use it as
is. If information needs refreshing, apply `research-policy.md`: check changes
first, use one researcher for a small update, and split into non-overlapping
scopes only when multiple areas genuinely need fresh evidence:

1. Company info and news: https://scalar-labs.com/ja/ (company / news), press
   release searches
2. Product technology: https://developers.scalar-labs.com/ → the actual docs
   live at https://scalardb.scalar-labs.com/docs/latest/ and
   https://scalardl.scalar-labs.com/docs/latest/
   (start from features / overview / design / releases, then follow individual
   feature pages)
3. Use cases and case studies: the case-study category of the news feed plus
   web search (there is no dedicated case-study page)

Give researchers only their source boundary and the compact return schema from
the policy—not this full skill. Cite source URLs, mark unknowns explicitly,
never guess, and update the dated research cache.
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
cd /path/to/slide-forge
.venv/bin/python scripts/scalar/build_scalar_features.py --dry-run   # audits only, no API
.venv/bin/python scripts/scalar/build_scalar_features.py [--folder <URL>]
```

1. Before committing, the scripts run `audit_bounds / audit_connectors /
   audit_overlaps / audit_text_fit` on every slide and print "audit:" lines ("検査:" with GSLIDES_LANG=ja).
   **If any audit fires, fix the spec and rebuild** (faster than patching).
   Delete the old deck from Drive before rebuilding
2. Apply the shared contract's selected QA and cleanup procedure.
3. **Rebuilding changes the URL.** Tell the user the new URL and be explicit
   about what happens to the old deck (deletion)
4. Use the shared contract's final-adjustment choices before handoff.

## File layout

| Path | Role |
|------|------|
| `scripts/scalar/build_scalar_intro.py` | Company intro deck builder (boilerplate + insertion approach; a worked 27-slide example) |
| `scripts/scalar/build_scalar_features.py` | Feature catalog deck builder (24 features with diagrams; a worked 31-slide example) |
| `templates/scalar-2026.json` | Scalar 2026 template (generated decks) |
| `templates/scalar-2026-boilerplate.json` | Scalar 2026 boilerplate template (official bundled slides) |
| `assets/scalar/{logos,product-logos,pictograms}` | Brand assets (company/product logos, pictograms) |
| `references/scalar/okf-bundle.md` | Where the OKF bundle is and how to cite product facts and prices from it |
| `references/scalar/research-2026-08.md` | Researched facts (company, products, case studies) and 6 slide-making pitfalls |

The scripts are "worked examples you can re-run as is"; when changing the
structure, editing these two scripts is the shortest path. The architecture
diagram examples `examples/scalardb-architecture.py` /
`examples/scalardl-architecture.py` (from google-slides-template) can be used
alongside them.
