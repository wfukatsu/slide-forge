*[日本語](README.ja.md)*

# references/ — what is in here

Every file below also exists as `<name>.ja.md` in Japanese, except where noted.
Start from the group that matches what you are doing; you are not meant to read
this directory end to end.

## Start here

| File | What it is for |
|---|---|
| [commands.md](commands.md) | The three slash commands — `/forge`, `/account`, `/visit`. Start here if you want to *use* slide-forge rather than change it |
| [workflow-contract.md](workflow-contract.md) | The single shared contract for end-to-end deck generation. Read this before changing how any host runs the pipeline. The English text is normative |
| [interactive-intake.md](interactive-intake.md) | How to settle template, purpose, structure and length with the user before writing a spec |
| [validation.md](validation.md) | The two gates: offline coordinate checks, then thumbnail QA. What each one can and cannot catch |
| [parallel-generation.md](parallel-generation.md) | Splitting a large deck into per-page fragments, in parallel or sequentially |
| [codex-compatibility.md](codex-compatibility.md) | Where the Codex host differs, and its setup. The English text is normative |

## Writing a deck

| File | What it is for |
|---|---|
| [deck-outlines.md](deck-outlines.md) | What order to talk in — standard deck structures, before any diagram question |
| [composers/](composers/) | Page-by-page composition guidance per deck genre: [basic](composers/basic.md), [content](composers/content.md), [product](composers/product.md), [usecase](composers/usecase.md), [db-middleware](composers/db-middleware.md), [enterprise](composers/enterprise.md) |
| [slide-patterns.md](slide-patterns.md) | How to compose one page: skeleton × content, the `PageMixin` parts |
| [template-schema.md](template-schema.md) | The shape of `template.json` and of a deck spec |
| [settings.md](settings.md) | `config/settings.json` — image generation and where artifacts go |

## Catalogs — look, then choose

| File | What it is for |
|---|---|
| [slide-pattern-catalog.md](slide-pattern-catalog.md) | 52 page patterns, each with a rendered image. Generated |
| [slide-template-catalog.md](slide-template-catalog.md) | 108 one-page templates, each with a rendered image, its **Inputs** table, and guardrails. Generated |

## Drawing (the `scripts/` engine)

| File | What it is for |
|---|---|
| [diagrams.md](diagrams.md) | `Canvas` itself — drawing conventions and self-checks. The hub the mixins below attach to |
| [diagram-cookbook.md](diagram-cookbook.md) | Working recipes, in inches, copied from real decks |
| [layout-contract.md](layout-contract.md) | Coordinates and limits **measured from real output**, not estimated. Diagram decks break here first |
| [charts.md](charts.md) | Tables and charts (`charts.py`) |
| [patterns.md](patterns.md) | Business-framework figures (`patterns.py`) |
| [calendars.md](calendars.md) | Parts whose input is dates, not coordinates (`calendars.py`) |
| [events.md](events.md) | Seminar and conference announcement parts (`events.py`) |
| [images.md](images.md) | The 5 ways to illustrate something, and how to choose |
| [pictogram-catalog.md](pictogram-catalog.md) | The 32 generic pictograms and the metaphor diagrams (`illustrations.py`) |
| [icons.md](icons.md) | The 62 Scalar-branded pictograms (`icons.py`), and when to prefer them |
| [cloud-icons.md](cloud-icons.md) | The 1,757 AWS / Google Cloud / Azure icons |
| [code-blocks.md](code-blocks.md) | Syntax-highlighted code samples |
| [account-graphs.md](account-graphs.md) | Influence and discovery graphs |
| [drawio.md](drawio.md) | Dense diagrams as `.drawio`, exported headlessly to PNG |

## The Slides API itself

| File | What it is for |
|---|---|
| [api-notes.md](api-notes.md) | **Read this first.** Constraints and pitfalls confirmed by hand, most of them documented nowhere else |
| [google-slides-api.md](google-slides-api.md) | The raw request shapes, units and limits — where you go when api-notes does not answer it |

## Per-skill rules

| File | What it is for |
|---|---|
| [hearing-kit.md](hearing-kit.md) | The record `hearing-sheet` and `hearing-slides` share, including the customer filter that decides what a customer may see; neither skill redefines it |
| [nexus-reports.md](nexus-reports.md) | What each nexus-architect report becomes as slides |
| [account-planning-session.md](account-planning-session.md) | The procedure for an Account Planning Session deck |

## Scalar-specific (internal)

`scalar/` holds customer- and product-specific sales material, not engine
documentation: [sales-playbook](scalar/sales-playbook.md) (phases, gates,
material types), [proposal-map](scalar/proposal-map.md) (problem → product),
[stage-io-map](scalar/stage-io-map.md) (inputs and outputs per deal stage),
[nurture-map](scalar/nurture-map.md) (pre-deal segments and tracks),
[okf-bundle](scalar/okf-bundle.md) (where product facts and pricing come from),
[research-2026-08](scalar/research-2026-08.md), and
[research-policy](scalar/research-policy.md) *(English only)*.
`scalar/workflow-contract.md` is the Scalar-side contract and the home of the
customer-facing / internal rule for sales material *(English only)*.

## Not reference material

These are kept for history. They describe what was planned or measured at a
point in time, and they are **not** statements about how the system works now:

- [calendar-template-plan.md](calendar-template-plan.md) — the calendar pack's implementation plan
- [account-planning-template-plan.md](account-planning-template-plan.md) — the APS page templates' implementation plan
- [`docs/plans/`](../docs/plans/) and [`docs/brainstorms/`](../docs/brainstorms/) — the same kind of record for work that started as a brainstorm. `2026-08-15-feat-targeted-slide-update` is the plan behind `--update-slides`, and is marked completed
- `agent-token-cost-review.ja.md` — a one-off token-cost audit *(Japanese only)*

## Generated, not written

- `images/` — rendered PNGs for the two catalogs, committed so the catalogs read with figures on a bare clone
- `i18n/` — English sidecar strings for the two generated catalogs **in this directory**

There are two `i18n/` directories and they are not the same thing:

| Directory | Holds | Read by |
|---|---|---|
| `references/i18n/` | English text for the generated catalog **documents** | `build_pattern_catalog.py`, `build_template_catalog_doc.py` |
| `slide-templates/i18n/` | The words a **slide** prints for itself — table headers, axis ends, "Source:", weekday names | `slide_templates.resolve_label()`, via `{"$t": …}` in a template and `Canvas._label()` in drawing code |

Editing the first changes a document; editing the second changes what
appears on a generated slide.
