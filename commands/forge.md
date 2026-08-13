---
description: >-
  Run Google Slides deck generation as a single flow: skill selection →
  intake → outline approval → spec creation → offline validation → generation
  → visual QA (optional, on by default) → delete validation files →
  additional deliverables (PPTX / cost breakdown spreadsheet, optional) → report
argument-hint: "[theme / template URL / material path / customer name, etc.]"
---

*[日本語](forge.ja.md)*

# /forge — Deck Generation Pipeline

Starting from `$ARGUMENTS`, run the slide-forge generation flow **through in
one continuous pass, without stopping**. The working directory is the
slide-forge root (`${CLAUDE_PLUGIN_ROOT}` for the plugin, `/path/to/slide-forge`
for a local clone).

## Step 1: Choose the generation skill (routing)

Pick one based on the arguments and context. Only ask once via
`AskUserQuestion` if it's unclear.

| Type of request | Skill to use |
|---|---|
| Deck introducing Scalar's company / products / features | `scalar-product-slides` |
| Scalar solution proposal starting from a customer problem | `scalar-proposal-slides` |
| Building a reusable, single-slide-unit template | `slide-template-creator` |
| B2B deal stakeholder map / discovery organization | `b2b-account-maps` |
| A template/master URL exists, build with a registered template (default) | `google-slides-template` |
| Build from scratch with no corporate master | `google-slides` |

From here, follow the chosen skill's SKILL.md. This command's role is to
carry the following sequence through without skipping steps or stopping.

## Step 2: Intake of assumptions (1-2 rounds)

Following `references/interactive-intake.md`, ask only about unspecified
assumptions, batched together. **Always include the "validation" question**
(whether to run visual QA after generation) — the default/recommended answer
is "yes". When PPTX delivery/distribution is expected (proposals, customer-
facing materials), include the "output format" question (whether to also
export PPTX) in the same set; when cost/configuration figures will appear,
also include the "breakdown material" question (whether to also produce a
cost breakdown as a spreadsheet). Don't ask about items the user has already
specified or has left to your discretion ("おまかせ") — instead, state the
adopted assumptions in one line.

The 用途 (Purpose) answer also fixes the **template density**: 提案書 / 社内共有
→ `print`, 登壇 → `presentation`. Pass it as `--density` to every
`render_slide_template.py` call for templates that declare `$density` variants
(e.g. the `read-alone` pack); when the master has no Proposal/Presentation
category, ask the reduced two-option form (投影用 / 印刷・配布用) instead of
skipping the question.

## Step 3: Outline approval gate (do not skip)

Present the slide count, layout, and each slide's action title in the body
text, and get approval. **After approval, proceed through to the Step 7
report without further confirmation.**

## Step 4: Spec creation and offline validation

Following the skill's steps, write the spec (JSON or deck module), and always
validate it before generating:

```bash
.venv/bin/python scripts/build_deck.py --template templates/<id>.json --spec deck.json --dry-run --strict
# For code-first: .venv/bin/python scripts/validate_layout.py deck.py
```

For more than 12 slides, use the fan-out approach in
`references/parallel-generation.md`.

## Step 5: Generation

Create the Drive folder first, then generate, and consolidate the spec and
diagram sources into the folder (the Drive folder rule). If generation fails,
delete the partial deck from Drive and rebuild.

## Step 6: Visual QA and cleanup (branches on the Step 2 choice)

- **"Run it" (default)**: follow the `slide-qa` skill's steps — fetch
  thumbnails → visually inspect against the checklist → if there are defects,
  fix the spec and regenerate (delete the old deck from Drive) → **always
  delete the validation files at the end**:

  ```bash
  .venv/bin/python scripts/cleanup_qa.py
  ```

- **"Skip it"**: skip QA and go to Step 6.5. In the report, note explicitly
  that **QA was not performed**, and that it can be validated later with the
  `slide-qa` skill.

## Step 6.5: Additional deliverables (branches on the Step 2 choice)

- **If "also export PPTX" was chosen**: run this with the `pptx-export` skill
  after the deck is finalized (after the QA/fix loop completes):

  ```bash
  .venv/bin/python scripts/export_pptx.py "<deck URL>" --folder "<Drive folder URL>"
  ```

  Even if regenerated due to QA fixes, always export the **final version**.

- **If "produce breakdown material" was chosen**: generate the cost breakdown
  with the `spreadsheets` skill (create spec → `--dry-run` →
  `build_sheet.py --gsheet --folder "<Drive folder URL>"`). Make the breakdown
  total match the cost figures on the slides, and confirm the computed
  results via CSV export.

## Step 7: Report

1. The deck URL and the Drive folder URL (for PPTX, the local path; for the
   breakdown spreadsheet, the Spreadsheet URL and xlsx path too)
2. QA results (which page range was inspected, what was fixed and what
   wasn't) or an explicit note that QA was not performed. Also note that the
   validation files have been deleted
3. Final check (`references/interactive-intake.md` §4): finalize / fix
   wording / change how a diagram is presented / adjust the slide count
