---
name: pricing-strategy
description: >-
  Value-based pricing (Nagle & Müller). Use for what to charge for a new
  product/tier, raising or cutting a price, price structure (metric, tiers,
  per-seat vs usage, fences), whether a discount pays, responding to a
  competitor's price cut, discount policy, or pricing organization. Runs
  bundled calculators (economic value, breakeven, structure comparison).
  Triggers: 値付け, 価格戦略, 値上げ, 値下げ, 値引き, 料金体系, 課金単位,
  競合の値下げ, プライシング, how much to charge, pricing model.
---
*[日本語](SKILL.ja.md)*

# Pricing Strategy (Value-Based Strategic Pricing)

Turns a pricing question into a recommendation backed by numbers. The method follows the value cascade of Nagle & Müller [1] (value creation → value communication → price structure → pricing policy → price level → price competition). Price level is the fifth of six layers, not the first thing to decide.

The working directory is the slide-forge root, and the command is `.venv/bin/python`. References live in this skill's `references/`. Read the English files (`x.md`); `x.ja.md` holds the same content in Japanese. Read only one of them. To save tokens:

- Read a reference only when you enter that step and need it for a decision. **In brief mode, do not read references as a rule.** Answer from this SKILL.md and the script output, and read the relevant file only when a point is genuinely unclear.
- Run the scripts without reading their source. Only when the input format is unclear, read the docstring at the top with `head -60`.
- Do not read all of `references/glossary.md` (60KB). Pull only the matching lines with `grep -i "<term>" skills/pricing-strategy/references/glossary.md`. For translations, `references/i18n.json` is enough.

## Output language

Write in the language the user specifies, or else the language of the request. Ask confirmation questions in the same language. Keep method terms consistent using `references/i18n.json` (English → Japanese). When writing in English, use its English side.

## 1. Request type

Classify by the layer the issue sits in, not by the words of the request. The answer to "should we cut the price?" may be a structural change. If unsure, use the "Diagnosing the layer from symptoms" table in `references/value-cascade.md`.

| Type | Typical request | Main references | Scripts |
|---|---|---|---|
| **A. New-product pricing** | Price for a new product, new plan, add-on, API | economic-value, price-structure, price-level, financial-analysis | eve_calc, breakeven |
| **B. Repricing an existing offer** | Price increase, price cut, is the price right | price-level, financial-analysis, pricing-policy | breakeven |
| **C. Price structure redesign** | Price metric, tiers, usage vs flat, large vs small customer price gap, cannibalization | price-structure, economic-value, financial-analysis | structure_compare, breakeven |
| **D. Competitive response** | Competitor's price cut, cheap new entrant, price war | price-competition, financial-analysis | breakeven `--reactive` |
| **E. Discounts and policy** | Discount requests, habitual discounting, negotiation rules, promotions | pricing-policy, value-communication | breakeven |
| **F. Capability assessment** | Who sets prices, approval process, sales compensation | pricing-capability | none |

When a request spans several types, lead with the most upstream layer. If the value has not been articulated, start from step 1 whatever the type.

## 2. Depth

- **Brief mode** (default): the user says "ざっくり" or "quick", or answering one question is enough (how much volume is needed at price X, does this discount pay, which of two options). Always run the scripts. Write in the "Brief-mode format" below, and add one line on the steps skipped and the conditions under which to go to detailed analysis.
- **Detailed mode**: a real launch or price-change decision, material for executives, multiple segments, or the user asks for a "proposal" or "report". Write every section of the matching template in `references/report-templates.md`.

If ambiguous, answer in brief mode and offer a detailed report in one line at the end.

## 3. Steps

**0. Gather only information that changes the answer.** Ask, in one batch, only for missing items that affect the recommendation. For items you can assume, mark them "to confirm" and complete a first pass. The information needed: the product and target segments (1–3), each segment's next-best competitive alternative and its cost, benefits over that alternative, incremental cost (never sunk cost), current price, volume and trend, lifecycle stage and competitive situation, objectives and constraints.

**1. Estimate value** (economic-value). For each segment, write the reference value and value drivers in JSON and run `eve_calc.py`. Total economic value is the price ceiling, not the recommended price. Use the differentiation share to judge whether the offer sells on value or gets compared on price. If only a total is known, put in an illustrative breakdown and mark it "illustrative, to confirm".

**2. Decide the structure** (price-structure). Decide offer configuration, price metric and price fences, and check for loopholes. Compare structure options with `structure_compare.py` against the distribution of customer sizes. If the price/value ratio by size is skewed, the metric is not tied to value. Express a revenue-neutral base fee as `"base_fee": "neutral"` and existing volume discounts as `"discounts": [{"min_size": 9, "pct": 35}]`. Compute cannibalization of a lower plan with the cannibalization mode of `breakeven.py`.

**3. Decide level and strategy** (price-level). Set the ceiling (total economic value) and the floor (the alternative's price if differentiation is positive, incremental cost if negative), and choose skimming, penetration or neutral pricing according to the conditions. Do not adopt penetration pricing unless you can answer "why won't competitors follow?"

**4. Compare with breakeven** (financial-analysis). Run `breakeven.py` for each candidate price. The question is "how much must volume change for this price to beat the alternative price?" Breakeven sales change = −ΔP ÷ (CM + ΔP). The baseline is not today's volume but the trajectory without the change.

**5. Anticipate competitor reaction** (price-competition). This is the core for type D. Answer the decision questions one by one, and close with the breakeven of a reactive price change. Matching is justified only when the volume lost by not matching exceeds (CM before − CM after) ÷ CM before (`--reactive`). Estimate lost volume from existing customers who could actually leave. Exclude volume locked in by multi-year contracts, and do not treat the share of the new-business pipeline as the churn rate.

**6. Communication and policy** (value-communication, pricing-policy). Write the discount policy before the first negotiation (what is given in exchange for what, sales discretion, what is never discounted). For a price increase, plan the rationale, advance notice, and treatment of existing customers.

**7. Lifecycle, measurement, legal** (specialized-strategies, measurement, ethics-legal). Read these only in detailed mode. The legal part prompts a check and is not legal advice. It is US-law centered, so for Japan and the EU write that legal counsel should confirm. If organizational obstacles appear, read pricing-capability.

**8. Write.** Open with the conclusion (price or action, target, strategy, and the one number that justifies it). Put assumptions in a table, with confirmed / to confirm and sensitivity on each row. Include script tables as Markdown, and in detailed mode attach the input JSON as an appendix. Read `references/slides.md` only when slides are requested, and before starting, use AskUserQuestion once to confirm whether to include calculation-logic slides, the use, the output destination and the length (use the `slide-templates/pricing` pack).

### Brief-mode format

```
**推奨 / Recommendation** — price (or action), target, the justifying number (2–3 sentences)
**数字 / Numbers** — script tables cut down to the rows that matter for the decision
**構造 / Structure** — only when tiers, cannibalization, fences or competitive response are involved (3–5 items)
**前提 / Assumptions** — bullets; mark unconfirmed items
**次の一手 / Next step** — 1–2 items
```

Keep the body to about 400 words excluding tables (about 800 characters in Japanese).

## Reference files (`references/`)

| File | Contents |
|---|---|
| value-cascade | Overall picture, diagnosing which layer the problem is in |
| economic-value | Value estimation, segmentation, `eve_calc` input format |
| value-communication | Communicating value, framing |
| price-structure | Metrics, tiers, bundles, fences, two-part tariffs |
| pricing-policy | Discounts, negotiation, communicating increases, promotions, price waterfall |
| price-level | Price range, choosing a strategy, drivers of price sensitivity |
| price-competition | Competitor price cuts, price wars |
| measurement | Research methods for willingness to pay and price sensitivity |
| financial-analysis | Incremental cost, breakeven, cannibalization, `breakeven` input format |
| specialized-strategies | Lifecycle, innovation, exchange rates, recessions, transfer pricing |
| pricing-capability | Pricing organization, authority, process, compensation |
| ethics-legal | Ethics, antitrust, price discrimination, resale price |
| worked-example | A worked analysis (a case where a structural change was the answer) |
| glossary | 222 terms (look up with grep) |

Network effects and dynamic pricing are not topics of [1]. When covering them, state explicitly that it is general knowledge not based on [1].

## Scripts

The calculation scripts are in `scripts/pricing/` (relative to the slide-forge root). Put input JSON in an ignored path such as `out/pricing/`. Standard library only (Python 3.8+). All output Markdown; `--json` switches to JSON and `--lang en|ja` sets the language. Do calculations with the scripts, not by hand.

```bash
.venv/bin/python scripts/pricing/eve_calc.py --input eve.json --lang ja
.venv/bin/python scripts/pricing/breakeven.py --input prices.json --lang ja
.venv/bin/python scripts/pricing/breakeven.py --price 100 --cost 40 --candidates 90,110,120 --volume 1000
.venv/bin/python scripts/pricing/breakeven.py --price 12 --cost 2 --candidates 8 --reactive
.venv/bin/python scripts/pricing/structure_compare.py --input structures.json --lang ja
# each also writes slot data for slide-forge's pricing pack with --slides DIR (and calculation-logic slides with --slides-logic)
```

## Common mistakes

- **Cost-plus under another name**: cost sets only the floor. Go back to step 1.
- **Pricing to the willingness to pay of the customer in front of you**: early buyers cannot judge value. Price at the value satisfied users acknowledge, and invest in demonstrating value.
- **One price for everyone**: if value differs widely between segments, solve it with structure, not a compromise price.
- **Solving a structure or policy problem with the level**: if discounts concentrate at a particular size, first look at price/value by size with `structure_compare.py`.
- **Including sunk costs**: only incremental, avoidable costs go into breakeven.
- **Confusing precision with accuracy**: show ranges and sensitivity for guessed inputs.
- **Reflexively matching a competitor's price cut**: first check breakeven and how far the reaction spreads, and if you match, limit the scope.
- **Setting policy after the first negotiation**: the first deal becomes the reference point for all that follow.

## References

[1] Nagle, T. T., & Müller, G. (2018). *The Strategy and Tactics of Pricing: A Guide to Growing More Profitably* (6th ed.). Routledge.
- Chapters 1–12 (pp. 1–316). The chapters and pages each reference file covers are listed in the "References" section at the end of that file.
