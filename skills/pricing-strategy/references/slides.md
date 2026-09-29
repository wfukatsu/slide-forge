*[日本語](slides.ja.md)*

# Turning Analysis Results into Slides

How to turn the results of a pricing strategy analysis (economic value, breakeven, price structure comparison, competitive response, discount policy) into slides with the page templates of the `slide-templates/pricing` pack. It covers how the detailed report sections (templates A–F in `report-templates.md`) map to templates, how to feed data from the calculation scripts, and points to watch.

## 0. Confirm before building

Before starting on the slides, confirm the following four points **once, with AskUserQuestion** (skip any the user has already answered). The answers change the script options, the templates used, and the destination.

| Question (header) | Options (first is recommended) | What the answer changes |
|---|---|---|
| Include calculation-logic slides? (Calculation logic) | Group them in an appendix (recommended) / Place each right after its result / Do not include | Whether to add `--slides-logic`, page order |
| Use (Use) | Handout / reading (`print`) (recommended) / Presenting (`presentation`) | `--density`. For presenting, shorten the wording |
| Output (Output) | Generate through Google Slides (recommended) / Stop at slot data (JSON) | Whether to generate Google Slides or hand over the data and stop |
| Length (Length) | Detailed, 10–12 slides (recommended) / Brief, 5–6 slides | Number of result templates used |

If generating through Google Slides, say in the description of that output option that files will be created in the user's Google Drive.

## 1. Template mapping

Analysis results become slides using the page templates of the `slide-templates/pricing` pack. Each slide answers one question.

| Template | Question answered | Report section | Data source |
|---|---|---|---|
| `economic-value-waterfall` | What is the value, and where does the price sit within it? | A3, C3, B3 | `eve_calc.py --slides` (one slide per segment) |
| `breakeven-sales-change` | How much must volume move for a price change to pay? | A6, B4 | `breakeven.py --slides` |
| `price-structure-compare` | Which pricing structure tracks value across customer sizes? | C5 | `structure_compare.py --slides` |
| `competitor-response` | Should we match a competitor's price cut? | D3–D4 | `breakeven.py --reactive --slides` |
| `give-get-policy` | In exchange for what may we discount? | A8, E4 | Written by hand (no script) |
| `calculation-logic` | How is this number computed, and which inputs does it depend on? | Appendix | Each script's `--slides DIR --slides-logic` |

For the conclusion page, use the existing `exec-summary-readable` or `conclusion-rationale-implication`.

Calculation-logic slides written by `--slides-logic`:

| File | Contents |
|---|---|
| `calculation-logic-economic-value-N.json` | Segment N's reference value, the formula for each value driver (with input values substituted), and the total economic value |
| `calculation-logic-breakeven.json` | Current price, incremental unit cost, unit contribution margin, and the breakeven sales change calculation for each candidate price |
| `calculation-logic-reactive.json` | Calculation of the churn rate at which matching pays (only with `--reactive`) |
| `calculation-logic-structure.json` | Each option's base fee, tiers and discount definitions, incremental cost, customer distribution, and how value is set |

## 2. Steps

1. Run the calculation scripts with `--slides DIR` (plus `--slides-logic` to include calculation logic). DIR receives slot data (JSON) for each template.
2. Replace every value starting with `【要記入】` (`[TODO]` in English). The title is a one-sentence conclusion, the lead gives target, period and units, and the source gives sources and assumptions. Verdict and recommendation fields cannot be decided by the scripts. For calculation-logic slides, write the title as one sentence on "what determines this number".
3. Number the pages according to the confirmed placement. For an appendix, put them after the result pages; to place them directly after, give each the number following its result page (e.g. logic 045 for result 040).
4. Render at the repository root, assemble the deck, and validate. When generating through Google Slides, follow the steps of the `google-slides` skill (create Drive folder → generate → visual check).

```bash
.venv/bin/python scripts/render_slide_template.py --template breakeven-sales-change \
  --data DIR/breakeven-sales-change.json --density print --out pages/090-breakeven.json
.venv/bin/python scripts/render_slide_template.py --template calculation-logic \
  --data DIR/calculation-logic-breakeven.json --density print --out pages/190-logic-breakeven.json
.venv/bin/python scripts/assemble_spec.py --out deck.json --title "Price change proposal" --density print pages/
.venv/bin/python scripts/build_deck.py --template templates/blank-16x9.json --spec deck.json --dry-run --strict
```

Notes:

- The exported data is sized to the character limits of the `print` density, meant for handouts. The presenting `--density presentation` has shorter limits, so shorten long wording.
- Long display names exceed the template limits. Give value drivers and structure options a `"short"` in the input JSON (up to 12 characters). Calculation-logic fields allow up to 72 characters. The scripts warn when a limit is exceeded.
- Numbers in calculation logic carry units. For amounts, use `currency` from the input JSON; for counts, `unit_label` (price structure) and `volume_unit` (breakeven). Write the units of value-driver inputs in `units` (e.g. `"units": {"docs": "件", "rate": "円/時", "prob": "（年間発生確率）"}`; a unit starting with a parenthesis is attached directly after the number). Inputs without `units` show the number only, so prompt the user to add them.
- Calculation-logic slides are written from the same input at the same time as the result slides. If you later regenerate only the results, regenerate the logic too.
- Each template's `guardrails` lists the ways that chart is misused. Read it before rendering.

## 3. Generation and visual check

Points that broke easily when actually building decks, and how to prevent them.

- **Read every automated check finding.** Do not cut the output of `build_deck.py --dry-run --strict` with `tail`. If there is even one "overlap", "overflow" or "wrap" finding, fix it, or render and confirm it is fine, before generating.
- **Keep titles to about 30 full-width characters, on one line.** A two-line title overlaps the lead.
- **Keep bar labels in incremental-breakdown charts to about 6 full-width characters (roughly 10–12 Latin characters).** With 6–7 bars, each bar is narrow; the render audit flags a label that wraps. Shorten with `short` in the input JSON.
- **Keep table cells to one line, and leave no cell empty.** A wrapped or empty cell makes that row taller and pushes it into the source line. Slides table rows cannot be shorter than about 0.34 inches, and the automated check can miss this, so check table pages as images.
- **State display rounding.** If result slides are rounded to 10,000 yen while calculation logic stays in yen, write the unit in the lead. For a price rounded for presentation (e.g. computed 670,000 yen → presented 700,000 yen), write both in the source line.
- **Check every page as an image.** Render with `scripts/fetch_thumbnails.py` and look at each slide. After a fix, recheck the changed page and the pages that use the same template.
- **Clean up old versions after rebuilding.** Move versions whose URL has not been shared to the trash, and keep in the Drive folder only one deck and the source data for rebuilding it (`deck.json`, input JSON, the script that assembles the content).
- **Put the content in an assembly script.** A single script that reads the `--slides` output, replaces `【要記入】`, renders each page and assembles the deck lets you rebuild every page the same way when inputs change.

## Related documents

- [report-templates.md](report-templates.md): templates for the detailed report (the "Report section" numbers in the table refer to sections of these templates).
- `scripts/pricing/slide_data.py`: output format of `--slides` and `--slides-logic`, and the placeholder definitions.

## References

[1] Nagle, T. T., & Müller, G. (2018). *The Strategy and Tactics of Pricing: A Guide to Growing More Profitably* (6th ed.). Routledge.
- Chapter 2 "Economic Value: The Guiding Force of Pricing Strategy", pp. 26–55.
- Chapter 4 "Price Structure: Tactics for Pricing Differently Across Customer Segments", pp. 76–105.
- Chapter 5 "Pricing Policy: Influencing Customer Expectations and Purchase Behaviors", pp. 106–132.
- Chapter 7 "Price Competition: Managing Conflict Thoughtfully", pp. 152–172.
- Chapter 9 "Financial Analysis: Analyzing Costs and Profits for Pricing", pp. 207–239.

The analyses the templates show follow the method of [1]. The template design and these steps were created for this skill and slide-forge and are not in [1].
