---
name: current-state-analysis
description: >-
  Run current-state and problem-identification frameworks on the user's material
  and render the results as slides: PEST, Five Forces, process pain-points, logic
  tree, KPI tree, why-why, fishbone, Pareto, As-Is/To-Be gap, impact-effort
  priority matrix, plus SWOT / 3C.
  Use for: 現状分析, 課題を特定・構造化, 真因分析, As-Is/To-Be 整理,
  課題の優先順位付け, ヒアリングメモを分析スライドに.
  Not: authoring new templates (analysis-template-creator); deck generation
  mechanics (google-slides); visual QA (slide-qa).
---
*[日本語](SKILL.ja.md)*

# Current-State Analysis (Current-State Analysis & Problem Identification)

Applies an analysis framework to material the user brings in (hearing notes,
business documents, data) and renders the result as slides from the
`slide-templates/analysis` pack (plus, in some cases, the
`marketing-analysis` pack).

The working directory is the slide-forge root. The command is
`.venv/bin/python`.

## Boundaries

| Request | Route |
|---|---|
| Perform a current-state analysis / problem identification and turn it into slides | this skill |
| Create or change a template for an analysis framework | `analysis-template-creator` |
| A single market-analysis slide such as SWOT / 3C / positioning map | `google-slides-template` + the marketing-analysis pack |
| The mechanics of deck generation itself / master selection | `google-slides` / `google-slides-template` |
| Visual inspection of a generated deck | `slide-qa` |
| Deal- or account-specific problem organization (with an account ledger) | the `scalar-account-plan` family |

## Mapping methods to templates

Analysis deepens in the order "environment → business process → structuring
→ problem definition → prioritization." **Do not do all of it.** Choose only
the stages needed to answer the question at hand.

| Stage | Question answered | Method | Template |
|---|---|---|---|
| 1. Environment | What are the external factors? | PEST | `pest-analysis` |
| 1. Environment | Where does industry competitive pressure come from? | Five Forces | `five-forces` |
| 1. Environment | Strengths/weaknesses × opportunities/threats | SWOT | `swot-analysis` (marketing-analysis) |
| 1. Environment | Customer, competitor, company | 3C | `three-c-analysis` (marketing-analysis) |
| 2. Business process | Which process steps concentrate the problems? | Business flow + pain points | `process-painpoints` |
| 3. Structuring | What can the problem be broken down into? | Logic tree | `logic-tree` |
| 3. Structuring | Which metric is responsible for the shortfall? | KPI tree | `kpi-tree` |
| 3. Structuring | What is the root cause (single chain)? | Why-why analysis | `why-why` |
| 3. Structuring | Which family does the causal hypothesis belong to? | Fishbone diagram | `fishbone-diagram` |
| 3. Structuring | Which factor accounts for the majority? | Pareto analysis | `pareto-analysis` |
| 4. Problem definition | What is the gap between current and ideal state? | Gap analysis | `gap-analysis` |
| 5. Prioritization | Which should be tackled first? | Priority matrix | `priority-matrix` |

A standard combination (for business/IT transformation work):
`process-painpoints` → (`pareto-analysis` or `logic-tree`) → `why-why` →
`gap-analysis` → `priority-matrix`. For strategy-oriented work, go from
stage 1 (PEST / 5F / 3C / SWOT) straight to `gap-analysis`.

The input slots and constraints for each template are authoritatively
defined in `slide-templates/analysis/<id>/template.json`, and can be listed
with `.venv/bin/python scripts/list_slide_templates.py --tag analysis`. This
skill does not restate the slot definitions.

## Workflow

### 1. Intake

Confirm all of the following in one pass:

- the question to be answered (what is this analysis for — a decision, an
  approval, an improvement proposal…);
- the material (hearing notes, data, public documents) and its **source and
  freshness**;
- the depth of analysis (which stage, from environment to prioritization, is
  actually needed);
- the output form (a single slide / a whole analysis chapter / an addition
  to an existing deck).

**Do not take on** an analysis with no material. If something is missing,
first return a list of hearing items / research items needed to fill the
gap — that list is itself a deliverable.

### 2. Running the analysis

A framework is a thinking template, not a filler template:

- **Separate fact from interpretation.** The content of the diagram (process
  steps, counts, environmental factors, causes) must be facts drawn from the
  material only. Interpretation goes into `insight` (so_what) and `title`.
- When filling a gap not covered by the material with an inference, mark it
  explicitly as (hypothesis) and attach a verification method.
- Every figure must state its source, period, and base in the `source` slot.
  Do not include a figure that cannot be sourced this way.
- Each template's `guardrails` enumerate misuse patterns for the method
  (reading correlation as causation, stopping at "human carelessness," etc).
  **Read them during the analysis, and follow them.**

### 3. Authoring and validating the slot JSON

For each method, build an input JSON in the same shape as `example.json`,
and validate it one page at a time:

```bash
.venv/bin/python scripts/render_slide_template.py \
  --template <id> --data <data.json> --out out/<n>_<id>.json
```

For multiple pages, bundle them into a single deck spec with
`assemble_spec.py` and audit it offline:

```bash
.venv/bin/python scripts/assemble_spec.py out/*_*.json --out out/analysis-deck.json --title <title>
.venv/bin/python scripts/build_deck.py --template templates/<master>.json \
  --spec out/analysis-deck.json --dry-run --strict
```

Fix audit findings (overflow, overlap, wrapping) by **shortening the data
side**. If you find yourself wanting to change the template or a primitive,
go to `analysis-template-creator`.

### 4. Generation and QA

Follow `google-slides` / `google-slides-template` for the conventions on how
to run generation, where to save, and titling. After generation, do a visual
inspection with `slide-qa` and clean up the QA thumbnails afterward.

### 5. Report

- The methods used and the rationale for choosing them (which question each
  answers);
- Each slide's claim (title) and the source it is based on;
- Where material was insufficient and treated as (hypothesis), and how it
  would be verified;
- The deck URL and QA result (if generation was carried through).

## Safety and quality rules

- **Never fabricate analysis results.** Interview statements, counts, and
  effort figures must be real data only. For demo purposes, follow the
  example.json convention and mark the source explicitly as "sample."
- Do not mix descriptive, diagnostic, and causal claims. A Pareto chart
  supports "this is concentrated" — "this is the cause" is the job of
  why-why / verification.
- An analysis that can identify a customer or an individual (organizational
  structure, who said what about a pain point) is internal material. A
  version handed to the customer must be produced separately, following the
  exposure-check approach used in `scalar-ae-materials`.
- Keep generated artifacts and QA files under `out/` (do not commit them).
