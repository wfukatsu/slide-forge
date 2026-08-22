---
name: analysis-template-creator
description: >-
  Author and maintain the slide templates in the slide-templates/analysis pack —
  PEST, Five Forces, logic tree, KPI tree, why-why, fishbone, Pareto, gap
  analysis, process pain-points, priority matrix — including the drawing
  primitive a new framework needs. Encodes each framework's own rules: the
  question it answers, the fact/interpretation split, required sources, misuse
  guardrails.
  Use for: 分析フレームのテンプレートを追加・修正, add an analysis-framework template.
  Not: generic page templates (slide-template-creator); running an analysis
  (current-state-analysis).
---
*[日本語](SKILL.ja.md)*

# Analysis Template Creator (Analysis Template Authoring)

A specialist skill for adding and changing slide templates for current-state
analysis and problem-identification frameworks in the
`slide-templates/analysis/` pack.

**The schema, validation, registration, and compatibility conventions are
owned by [`slide-template-creator`](../slide-template-creator/SKILL.md).**
This skill only adds analysis-framework-specific design rules on top of
those; it does not redefine the shared conventions. The working directory
is the slide-forge root, and the command is `.venv/bin/python`.

## Boundaries

| Request | Route |
|---|---|
| Create or change a template for an analysis framework | this skill |
| A generic (non-analysis) page template | `slide-template-creator` |
| Run an analysis and turn it into slides | `current-state-analysis` |
| Create a brand/master | `template-forge` |
| Visual inspection of a generated deck | `slide-qa` |

## Current state of the analysis pack

| category | template | primary primitive |
|---|---|---|
| macro | `pest-analysis` | `comparison` (4 columns) |
| macro | `five-forces` | `cards` × 5 (cross layout) |
| structure | `logic-tree` / `kpi-tree` | `mece_tree` |
| cause | `why-why` | `flow` |
| cause | `fishbone-diagram` | `fishbone` (patterns.py) |
| cause | `pareto-analysis` | `pareto` (charts.py) |
| process | `process-painpoints` | `flow` + `table` |
| gap | `gap-analysis` | `before_after` + `cards` |
| priority | `priority-matrix` | `posmap` |

SWOT / 3C / positioning map already exist in the `marketing-analysis` pack.
**Do not create duplicates** (if the same question is answered with the same
visual grammar, reuse or extend it). Choose `category` from the six above
(macro / structure / cause / process / gap / priority), and when adding a
new one, map it to the appropriate stage of analysis (environment → business
process → structuring → problem definition → prioritization).

## Design rules specific to analysis templates

In addition to `slide-template-creator`'s shared conventions, the following
are mandatory:

1. **Fix the question the template answers to exactly one.** Write it in
   `answers`. If there are two questions, there should be two templates
   (e.g. enumerating causes is fishbone, identifying the root cause is
   why-why).
2. **Separate fact slots from interpretation slots.** The content of the
   diagram (factors, process steps, figures) belongs in fact slots;
   interpretation goes in `insight` (rendered in `so_what`) and `title`. The
   `maxLength` of the insight slot should be derived backward from the
   actual capacity of `so_what` (body height = h − 0.54in, roughly 46
   characters/line). As a rule of thumb, 44 for one line, 88 for two lines
   (h ≥ 1.1in).
3. **Methods that carry numeric figures require `source`**, and guardrails
   must require the period, base, and definition to be stated explicitly.
4. **Encode misuse patterns for the method in guardrails.** From the
   textbook definition, write at least three "common mistakes." Examples:
   Pareto — only use quantities where the total is meaningful, do not mix
   in a rate; why-why — do not stop at "human carelessness"; Five Forces —
   do not write your own company's strengths/weaknesses; gap analysis — do
   not place unagreed wishes into To-Be; priority matrix — since the
   coordinates are a subjective assessment, record the assessor and
   assessment date.
5. **Assign `inferenceLevel` correctly.** Descriptive (pareto,
   process-painpoints) / diagnostic (logic-tree, kpi-tree, fishbone) /
   causal (why-why) / strategic (PEST, 5F, gap, priority). Only methods that
   draw a causal chain may claim causal.

## Procedure for adding a new method

1. **Search first.** Check for existing or similar templates with
   `list_slide_templates.py --tag <method name>` and
   `rg '<method name>' slide-templates references`.
2. **Decompose the method.** From the textbook definition, write out (a) the
   question it answers, (b) inputs (facts) and outputs (interpretation),
   and (c) misuse patterns. This becomes the material for guardrails.
3. **Select primitives.**
   Follow
   [primitive-selection.md](../slide-template-creator/references/primitive-selection.md)
   and prefer existing parts. Only add a framework-specific shape to
   `patterns.py` (framework diagrams) or `charts.py` (charts) when truly
   needed — `fishbone` / `pareto` are the precedents, and the full set
   includes registering with i18n's `register()`, input-validation
   `ValueError`s, registration in `build_deck.py::FIGURES`, and
   documentation in `references/patterns.md` / `references/charts.md` /
   `references/template-schema.md`.
4. **Create and validate.** Write template.json + example.json, and run
   `validate_slide_templates.py --id <id>` → `--pack analysis` →
   `build_slide_template_catalog.py --pack analysis`. **Zero audit findings
   is the passing bar** (every existing pack has zero).
5. **Visual QA.** Generate the catalog deck and run it through `slide-qa`,
   confirm it does not break with boundary-size inputs (longest label, most
   items), and clean up the QA artifacts afterward.
6. **Registration and reporting.** Register in the manifest, add an entry
   to `current-state-analysis`'s mapping table, and report the compatibility
   impact (changes to existing slots follow
   [registration-and-compatibility.md](../slide-template-creator/references/registration-and-compatibility.md)).

## Safety and quality rules

- example.json must always be clearly marked as a sample (write this in the
  source slot). Never use real customer names or real data as examples.
- Double up runtime validation (the `ValueError`s on the rendering side) and
  slot constraints. Slot constraints should be set to "whatever keeps audit
  findings at zero"; the rendering side should reject "input that would
  become unreadable."
- On every addition or change, verify the entire `--pack analysis`, and if a
  primitive was touched, also verify regressions in the other packs
  (marketing-analysis / b2b-sales / scalar-ae / planning).
