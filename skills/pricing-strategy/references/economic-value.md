*[日本語](economic-value.ja.md)*

# Economic value estimation (EVE) and value-based segmentation
This document covers how to estimate in money the economic value a product delivers to customers (EVE: Economic Value Estimation), and value-based segmentation, which divides the market by differences in value. It is the most upstream tier, "value creation," of the value cascade (value creation → value communication → price structure → price policy → price level → price competition); the downstream tiers take the value produced here as given. Read it when you need a monetary price ceiling, when choosing the next-best competitive alternative, when segmenting for pricing, or when preparing input for scripts/pricing/eve_calc.py (which computes total economic value and differentiation share per segment).

## Key points
- Price rests not on use value (the total utility from the product) but on economic value (exchange value), which is set by the alternatives.
- Total economic value is reference value plus positive differentiation value minus negative differentiation value. It is "the maximum a fully informed buyer would pay": a ceiling, not the price to charge ([1] p.29).
- Reference value starts from the price of the next-best competitive alternative (NBCA).
- Value can be monetary (cost savings or revenue gains) or psychological (peace of mind, prestige). Estimate the former with depth interviews and a formula per value driver (a factor that affects the customer's economics or satisfaction), called a value driver algorithm; estimate the latter with conjoint analysis.
- Perceived value (the value the buyer actually recognizes) is usually below economic value because of missing information. EVE's greatest use is telling apart whether a product fails to sell because it is "expensive for its value" or because "its value is not known" ([1] p.40).
- It is wrong to think "if performance is x% better, the price can be x% higher," or to set price from the average relationship between quality and price (a fair value line). Competition holds reference value below use value, but differentiation value can translate one-for-one into a price premium ([1] pp.45–47).
- Segment for pricing not by demographics but where "value to the customer" overlaps with "the seller's costs and constraints" (step 8).

## Decision criteria
| Category | Definition | Estimation method | Caution |
|---|---|---|---|
| Reference value | Price of the next-best competitive alternative, aligned on units and terms | Published prices, interviews with sales, competitor prices customers cite | Not comparable unless normalized for quantity and service level |
| Positive differentiation value | Customer-economic value of ways you are better than the alternative | Value driver algorithm | Measure either cost savings or added benefit, not both; avoid double counting |
| Negative differentiation value | Ways you are worse, switching costs, new-vendor risk | Same | Do not omit it. It justifies the minimum discount |
| Monetary value | Cost avoidance, revenue gain, risk reduction, time savings | Depth interviews (meetings that dig into the customer's operations) | The main driver in B2B |
| Psychological value | Peace of mind, status, comfort, convenience | Conjoint analysis (a survey that estimates willingness to pay (the most one would pay) per attribute from choice tasks), what the customer pays elsewhere for the same peace of mind | Do not drop it. Conjoint works poorly for innovative benefits that are hard to imagine |

### Pitfalls in choosing the next-best competitive alternative
| Pitfall | Description | Fix |
|---|---|---|
| Market myopia | Limiting competitors to the same industry | Ask, in the customer's words, "What would the customer do without us?" |
| Basket alternative | A combination of several products is the alternative | Use the combined price as the reference value |
| Doing nothing | Not recognizing the need is the biggest competitor | Set reference value to 0 and communicate everything as differentiation value |

### Reading differentiation share
Differentiation share = (Σ positive differentiation value − Σ negative differentiation value) / total economic value. A high share (as a guide, over 50%) means the product can sell on value and defend a premium. A low share means the product is compared on price, so structure and communication matter more than price level.

## Procedure
1. **Set segments and units.** Value varies by application, so estimate per segment. Align on a usage unit and period, such as per user per year, per transaction, or per site.
2. **Identify the next-best competitive alternative.** What would the customer do without you (competitor X, in-house or manual work, nothing)? Its total cost, converted to the same unit, is the reference value. If the alternative differs by segment, keep a reference value per segment.
3. **List value drivers.** List factors that change the customer's economics (cost avoidance, revenue gain, risk reduction, time savings) and negative factors (switching costs, missing features, training, new-vendor risk), and classify each as monetary or psychological. Gather them through depth interviews that dig into the customer's business model.
4. **Turn each driver into an algorithm.** Use inputs the customer knows.
   ```
   Value of time saved      = hours saved per month × loaded hourly rate × 12
   Value of fewer incidents = incidents per year × cost per incident × reduction rate
   Value of new orders      = share of target deals × share winnable × contribution margin per deal
   ```
   For now, enter typical values for the segment; later, sales replace them with the customer's own values. State where the typical values come from. Being roughly right beats being precisely wrong. Do not drop an important driver just because it is hard to quantify.
5. **Add it up.**
   ```
   Total economic value = reference value + Σ positive differentiation value − Σ negative differentiation value
   Differentiation share = (Σ positive − Σ negative) / total economic value
   ```
   There are three rules for adding up ([1] p.36). Value only the differences from the alternative (shared benefits are already in the reference value). Measure either cost savings or added benefit, not both. Do not assume value is proportional to performance (if doubling service life halves line stoppages, the value is far more than double).
6. **Build a value profile.** Drivers sorted by monetary size form the value profile. The top 2–3 become the sales message and get the most thorough validation. Placing value per segment alongside market size shows where to compete and at what price.
7. **Diagnose.** If the price is below economic value and the product still does not sell, it is a communication problem; educate the market instead of cutting the price (for how to communicate, see [value-communication.md](value-communication.md)). If economic value itself is below the price, you need a price cut or a redesign of the value.
8. **Run value-based segmentation (six steps)** ([1] pp.49–54).
   1. Build a preliminary map of the market from existing research and statistics.
   2. Identify discriminating value drivers: drivers that differ widely between segments and are consistent within a segment.
   3. Understand your own operational constraints and advantages. Use activity-based costing (a method that assigns the cost of each activity to customers) to find the cost-to-serve per customer, and compare it with competitors.
   4. Create primary and secondary segments. Primary segments are the strategic overlap of customer needs and your constraints; secondary segments divide these by the driver with the widest differences.
   5. Describe segments in operational terms that sales can use to classify a customer on sight.
   6. Design price metrics (units of charge) and price fences (conditions for applying segment-specific prices). See [price-structure.md](price-structure.md) for details.

### Input schema for scripts/pricing/eve_calc.py

```json
{
  "unit": "per site per year",
  "currency": "USD",
  "segments": [
    {
      "name": "Mid-size manufacturers",
      "reference": {"alternative": "Vendor X + in-house integration", "value": 30000},
      "drivers": [
        {"name": "Integration labor avoided", "short": "Labor avoided", "type": "monetary", "sign": "+",
         "formula": "hours × rate", "inputs": {"hours": 400, "rate": 90},
         "units": {"hours": "h", "rate": "USD/h"}},
        {"name": "Downtime avoided", "type": "monetary", "sign": "+",
         "formula": "incidents × cost × reduction", "inputs": {"incidents": 6, "cost": 12000, "reduction": 0.5}},
        {"name": "Vendor risk (new supplier)", "type": "psychological", "sign": "-", "value": 5000}
      ],
      "price": 24000
    }
  ]
}
```

Give each driver either `value` directly or `formula` and `inputs`. Formulas can use `×`, `*`, `+`, `-`, `/`, `÷`, parentheses, and input names. The script outputs totals, differentiation share, and the value profile per segment.

Optional fields used only when building slides (`--slides DIR`, `--slides-logic`):

| Field | Meaning |
|---|---|
| `short` | Short name used for bar labels in the chart. Six or seven bars sit side by side, so keep it to about 6 full-width characters (roughly 10–12 Latin characters) |
| `units` | Unit per input. Shown after the number on the calculation-logic slide (e.g. `{"docs": "件", "rate": "円/時"}`). A unit starting with a parenthesis is attached directly after the number (e.g. `"prob": "（年間発生確率）"`). Inputs without a unit show only the number, and readers cannot check the math |
| `price` | Recommended (or current) price for the segment. Used to compute "value left to the customer" (total economic value − price) |

## Checklist
- [ ] Estimates per segment, with units and periods aligned
- [ ] Identifies the next-best competitive alternative from the customer's viewpoint, including doing nothing and in-house work
- [ ] Normalizes reference value for quantity and service level
- [ ] Includes negative differentiation value (switching costs, risk, missing features)
- [ ] Each driver has a formula, inputs, and their sources
- [ ] Does not double count cost savings and added benefits
- [ ] Keeps psychological value and states how it is estimated
- [ ] Treats total economic value as a ceiling, not the price to charge
- [ ] Top drivers connect to the sales message and the validation plan
- [ ] Segments cover the cost and constraint side and are described in terms sales can use to classify customers

## Common mistakes and fixes
| Mistake | Fix |
|---|---|
| Averaging the willingness to pay customers state | Buyers understate value to negotiate and cannot value benefits they have not experienced. Estimate with algorithms |
| Setting price with a "fair value line" that regresses price on per-attribute quality scores | It undervalues highly differentiated products and yields an average product's price. Build up differentiation value separately |
| Treating the seller's cost savings as customer value | Measure value in terms of the customer's economics |
| Thinking "twice the performance, up to twice the price" | That holds only when buying more of the reference product yields the same benefit. Recalculate with the customer's value drivers |
| Segmenting only by demographics or company size | Re-segment on axes where purchase motivation and cost-to-serve differ |
| Discounting heavily when net differentiation is negative | Use EVE to find the minimum discount that makes customers consider switching, and remove the disadvantage by non-price means (e.g. shortening lead times with local inventory) |

## Related documents
- [value-cascade.md](value-cascade.md): The whole value cascade and diagnosing which tier has the problem.
- [value-communication.md](value-communication.md): How to communicate estimated economic value to customers.
- [price-structure.md](price-structure.md): Designing price metrics and price fences to fit segments.

## References

[1] Nagle, T. T., & Müller, G. (2018). *The Strategy and Tactics of Pricing: A Guide to Growing More Profitably* (6th ed.). Routledge.
- Chapter 2 "Economic Value: The Guiding Force of Pricing Strategy", pp. 26–55.

In the text, "[1] p.N" refers to page N of [1].

Supplement not based on [1]: differentiation share and the "over 50%" guide are metrics this skill introduces for reading the output of scripts/pricing/eve_calc.py.
