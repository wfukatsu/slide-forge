---
name: slide-template-creator
description: >-
  Create, register, update, and catalog reusable single-slide templates for
  slide-forge. Use when a user asks to add a slide pattern or page template
  such as SWOT, cohort retention, KPI dashboard, comparison, process, or
  analysis slides; turn an existing slide or screenshot into a reusable page
  template; define semantic input slots; or list and maintain registered slide
  templates. This creates content-level slide templates, not Google Slides
  masters. Route brand/master creation to template-forge, deck generation to
  google-slides or google-slides-template, and visual QA of finished decks to
  slide-qa.
---

# Slide Template Creator

Create one reusable page specification at a time. Keep Google Slides masters in
`templates/`; store content-level templates in `slide-templates/`.

Run all commands from the slide-forge repository root. Use `.venv/bin/python`.

## Boundaries

| Request | Route |
|---|---|
| Create or update a reusable one-slide content pattern | this skill |
| Analysis-framework templates (PEST, logic tree, Pareto, …) | `analysis-template-creator` |
| Create brand colors, fonts, logo, master, or layouts | `template-forge` |
| Generate a complete deck | `google-slides` / `google-slides-template` |
| Verify generated slides visually | `slide-qa` |

A slide template is a `template.json` plus `example.json`, registered in
`slide-templates/manifest.json`. It expands to one ordinary slide-forge slide
object and therefore composes with `scripts/assemble_spec.py`.

## Workflow

### 1. Intake

Ask only for missing information, in one round:

- the question or message the slide must communicate;
- representative input data and expected variations;
- presentation or read-alone density;
- portable across masters or restricted to one registered master;
- any source slide, screenshot, or visual reference.

If the user supplies an existing user-owned deck, snapshot it before any live
edit. Prefer inspecting it and rebuilding the template locally; do not use the
live deck as the template registry.

### 2. Search before adding

```bash
.venv/bin/python scripts/list_slide_templates.py
.venv/bin/python scripts/list_slide_templates.py --tag <term>
rg '<term>' slide-templates scripts references
```

Reuse or extend an existing template when it answers the same question with the
same visual grammar. Create a new ID only when the required slots or visual
structure are materially different.

Read [primitive-selection.md](references/primitive-selection.md) when choosing
the drawing parts. Read [design-rules.md](references/design-rules.md) for page
structure, density, sources, and master portability.

### 3. Approve the template outline

Before editing, present and obtain approval for:

- ID and display name;
- question answered and inference level;
- page skeleton and semantic slots;
- reused or new primitives;
- sample preview content;
- interpretation guardrails.

Do not skip this gate when the user has not already approved those decisions.

### 4. Author the template

Create:

```text
slide-templates/<pack>/<id>/template.json
slide-templates/<pack>/<id>/example.json
```

Register it in `slide-templates/manifest.json`. Follow the complete schema in
[template-schema.md](references/template-schema.md).

Prefer existing primitives in `scripts/patterns.py`, `pages.py`, `charts.py`,
and `illustrations.py`. Add a primitive only when the same low-level drawing is
repeated, domain input needs function-level validation, and the function can be
named and reused independently of one template.

Portable templates must use `BLANK` plus `governing_message`, semantic palette
tokens through Canvas primitives, and the 10 × 5.625 inch safe area. Do not
reference a master object ID or hard-code brand RGB values.

### 5. Validate offline

```bash
.venv/bin/python scripts/validate_slide_templates.py --id <id>
.venv/bin/python scripts/render_slide_template.py \
  --template <id> --data slide-templates/<pack>/<id>/example.json \
  --out out/<id>.json
```

The validator checks registry/schema/input consistency, renders the example,
then runs `build_deck.py --dry-run --strict`. Fix every audit finding.

For all templates in a pack:

```bash
.venv/bin/python scripts/validate_slide_templates.py --pack <pack>
.venv/bin/python scripts/build_slide_template_catalog.py \
  --pack <pack> --out out/<pack>-catalog.json
```

### 6. Visual QA

Generate a catalog deck only after offline validation. Run `slide-qa` on every
catalog page. Test both representative input and boundary-size input for new
slot shapes. Fix the template, example, or shared primitive—not the generated
deck—and regenerate. Clean QA thumbnails before reporting.

### 7. Report

Report:

- template ID, pack, and paths;
- question answered and slot names;
- whether it is portable or master-specific;
- offline validation result;
- catalog URL and visual-QA result when live generation was authorized;
- any new primitive or compatibility constraint.

## Safety and quality rules

- Never invent production data to fill a template. `example.json` must identify
  itself as sample data in its source or notes.
- Require a `source` slot for numeric claims.
- Keep descriptive, diagnostic, predictive, causal, and strategic claims
  distinct. Put method-specific caveats in `guardrails`.
- Reject undeclared input slots and unresolved slot references.
- Keep generated and QA files under ignored `out/` paths.
- Preserve backward compatibility for stable templates. See
  [registration-and-compatibility.md](references/registration-and-compatibility.md).
