*[日本語](financial-analysis.ja.md)*

# Financial analysis for pricing decisions

How to put numbers on a price change using incremental cost and the breakeven sales change. In the value cascade (value creation → value communication → price structure → price policy → price level → price competition), this is the arithmetic behind price-level and price-competition decisions. Use it to evaluate price changes, new tiers, and matching a competitor, and to build input for `scripts/pricing/breakeven.py` (which computes the breakeven sales change and profit impact for each candidate price).

## Key points

- The question is not "is this price profitable?" but "how much must volume change for this price to beat the alternative price?" You do not need to know the demand curve; you only need to judge whether the required change is realistic.
- Use only costs that are both incremental (added by the decision) and avoidable (can be avoided depending on the decision). Exclude allocated overhead, sunk costs, and capacity that exists either way.
- Fixed costs that come with implementing the price change (a campaign, a new support setup, added capacity) count as incremental fixed costs. Semi-fixed costs are incremental depending on the volume range.
- The basic formula is: breakeven sales change (the percentage change in volume needed to keep total contribution after the price change) = −ΔP / (CM + ΔP). ΔP is the price change; CM is the contribution margin (price − unit incremental cost). It extends to variable-cost changes, incremental fixed costs, reactive price changes, and revenue terms.
- Price cuts and price increases are asymmetric. At a contribution margin ratio (CM ÷ price) of 45%, a 10% cut needs about 29% more sales, while a 10% increase can absorb about an 18% loss in sales.
- The comparison is against the baseline (sales if the price did not change), not today's volume.
- A new low-price tier causes cannibalization (sales of the higher-priced product being replaced by the lower-priced one). Show the net replacement ratio and the gross replacement ratio separately.
- Do not add non-incremental fixed costs or sunk costs to the price. The time to consider costs is before the investment, while it can still be avoided.

## Criteria and choices

### Deciding which costs are relevant

| Cost | Treatment | Reason |
|---|---|---|
| Variable costs (materials, payment fees, usage-based infrastructure) | Include | Change with volume |
| Fixed costs directly tied to the price change (announcing the new price, advertising the discount, dedicated support) | Include as incremental fixed cost | Would not occur without the decision |
| Semi-fixed costs (capacity or staff that must be added above a certain volume) | Include if the range is exceeded | Whether they are incremental depends on the volume range |
| Past development costs, rent during a lease term | Exclude | Sunk; the current decision does not change them |
| Allocated corporate overhead, R&D | Exclude | The total does not change with the price option |
| Cost of inventory | Include at replacement cost | The cost of a sale is the cost of restocking (NIFO: next-in, first-out) |
| Holding cost of resalable assets | Avoidable up to the salvage value | Avoidable by disposing of the asset |
| Contribution lost on higher-priced sales (opportunity cost) | Include | Keeps cannibalization and capacity competition in view |

## Steps

1. Set the baseline: the volume and contribution if the price did not change. In a growing market, use the post-growth forecast; for a launch, use the volume expected at the alternative price.
2. Identify the relevant costs and compute the unit contribution margin.

   ```
   CM  = 価格 − 単位あたり増分コスト
   %CM = CM ÷ 価格
   ```

3. Compute the breakeven sales change with the basic formula. ΔP is negative for a price cut. Express CM and ΔP in the same units (money, %, or decimal).

   ```
   損益分岐販売変化率 = −ΔP / (CM + ΔP)
   損益分岐販売変化量 = 損益分岐販売変化率 × ベースライン販売量
   利益の増減 = (実際の販売変化量 − 損益分岐販売変化量) × 新CM
   ```

   A price cut needs at least this much sales growth. A price increase pays off as long as the sales loss stays within this range.
4. Extend as needed.

   ```
   # 変動費も変わる場合（金額単位で計算する）
   ΔCM = ΔP − ΔC
   損益分岐販売変化率 = −ΔCM / (CM + ΔCM) = −ΔCM / 新CM

   # 増分固定費 IFC がある場合（固定費を回避できるなら IFC は負）
   損益分岐販売変化率 = −ΔP / (CM + ΔP) + IFC / (新CM × ベースライン販売量)
   損益分岐販売変化量 = ベースライン販売量 × (−ΔP / (CM + ΔP)) + IFC / 新CM

   # 反応的価格変更（競合への追随）
   反応的損益分岐販売変化率 = 価格変化率 / 貢献利益率      # = ΔP / CM
   値下げへの追随が得なのは: 追随しない場合の販売損失率 > −ΔP / CM
   競合の値上げに追随しないのが得なのは: 追随しない場合の販売増加率 > ΔP / CM
   （値下げへの追随は scripts/pricing/breakeven.py --reactive で算出。単位コストも変わる場合は (CM前 − CM後) / CM前）

   # 金額（売上高）ベースへの換算
   %BE(金額) = %BE(数量) + %ΔP × (1 + %BE(数量))
   ```

5. Build a table of sales-change scenarios and list the profit change net of incremental fixed costs (a what-if table). `volume_scenarios_pct` in `scripts/pricing/breakeven.py` produces it.
6. To compare several price options, draw a breakeven sales curve ([1] Exhibit 9-5 / 9-6). The vertical axis is price; the horizontal axis is the volume needed at that price to earn the same profit. If actual volume is to the right of the curve, profit rises; to the left, it falls.
7. Ask about price elasticity (percentage change in volume ÷ percentage change in price) in reverse. Instead of "what is our elasticity?", compute "what is the minimum elasticity that justifies this decision (or, for an increase, the maximum we can tolerate)?", then judge whether the market is more or less elastic than that. Gather evidence with [measurement.md](measurement.md) (methods for measuring price sensitivity).
8. Judge the sales response. For a price cut, require evidence and a plan for reaching the needed sales growth; for an increase, require evidence that sales will hold and an explanation for customers. Check competitor reactions with [price-competition.md](price-competition.md) (responding to price competition).
9. After implementation, track whether the actual sales change exceeds breakeven.

### Worked example (price 10.00, unit incremental cost 5.50, CM 4.50 = 45%, baseline 4,000 units)

| Price change | New price | ΔP | Breakeven sales change | Required volume |
|---|---|---|---|---|
| +25% | 12.50 | +2.50 | −2.50 / 7.00 = −35.7% | 2,571 |
| +15% | 11.50 | +1.50 | −1.50 / 6.00 = −25.0% | 3,000 |
| +10% | 11.00 | +1.00 | −1.00 / 5.50 = −18.2% | 3,273 |
| +5% | 10.50 | +0.50 | −0.50 / 5.00 = −10.0% | 3,600 |
| −5% | 9.50 | −0.50 | 0.50 / 4.00 = +12.5% | 4,500 |
| −10% | 9.00 | −1.00 | 1.00 / 3.50 = +28.6% | 5,143 |
| −15% | 8.50 | −1.50 | 1.50 / 3.00 = +50.0% | 6,000 |
| −20% | 8.00 | −2.00 | 2.00 / 2.50 = +80.0% | 7,200 |

- With incremental fixed cost: at −15% with IFC 2,400, 50% + 2,400 / (3.00 × 4,000) = 70% (6,800 units).
- At −5% with a semi-fixed cost of 800 (per 1,000 units), 12.5% + 800 / (4.00 × 4,000) = 17.5% (700 more units). If sales rise 20% (800 units), (800 − 500) × 4.00 − 800 = +400.
- A 5% cut while lowering variable cost by 0.22: ΔCM = −0.50 + 0.22 = −0.28 → 0.28 / 4.22 = +6.6% (265 units).
- Revenue terms: the 12.5% for a 5% cut equals 0.125 + (−0.05)(1.125) = +6.9% revenue growth.
- Reactive: a competitor cuts 15% → −15% / 45% = −33.3%. Match only if not matching would lose more than 33.3%. `--price 10 --cost 5.5 --candidates 8.5 --reactive` gives the same 33.3%.
- Growing baseline (%CM 55%, 2,000 → 2,400 units even with no change): the 10% for a 5% cut is 240 units; computing from today's 2,000 units gives 200 and understates it.
- Avoided fixed cost (the case in [1] Appendix 9A: a price increase avoids building 9,000 of capacity; %CM 58.5%, 10% increase, baseline 45,000 units, new CM 2.635): −14.6% + (−9,000) / (2.635 × 45,000) = −22.2%.

### Cannibalization (adding a low-price tier)

When a cheaper Lite sits next to Full, customers who switch stop paying Full's contribution but do pay Lite's. The two ratios answer different questions, so always state which one you show.

| Ratio | Formula | Question it answers |
|---|---|---|
| Net replacement ratio | (CM_full − CM_lite) ÷ CM_lite | How many new Lite customers are needed to make up for one Full customer switching |
| Gross replacement ratio | CM_full ÷ CM_lite | How many Lite units equal the contribution of one Full unit |

Example: Full 120k, incremental cost 45k (CM 75k). Lite at 60k (CM 15k, same cost) gives net 4.0, gross 5.0. Lite at 75k (CM 30k) gives net 1.5, gross 2.5. The test for launching Lite:

```
new Lite volume × CM_lite  >  switching volume × (CM_full − CM_lite) + Lite incremental fixed cost
```

Cannibalization is mainly a price-structure problem, not a price-level one. Fence Lite with price fences (conditions that separate prices by buyer attributes or purchase terms): capacity or user caps, buyer-size conditions, no enterprise features, credit on upgrade. Strip out what only Full buyers need to lower the switching rate. For the design, see [price-structure.md](price-structure.md) (price structure and price fences).

### Derivation of the basic formula ([1] Appendix 9B)

Let P be price, Q volume, and C unit variable cost. A price cut loses ΔP × Q of contribution on existing sales Q (price effect, rectangle A) and gains (P + ΔP − C) × ΔQ on the added sales ΔQ (volume effect, rectangle B). Set profit before and after equal.

```
(P − C)Q = (P + ΔP − C)(Q + ΔQ)
PQ − CQ  = PQ + ΔP·Q − CQ + P·ΔQ + ΔP·ΔQ − C·ΔQ
0        = ΔP·Q + P·ΔQ + ΔP·ΔQ − C·ΔQ
ΔQ / Q   = −ΔP / (P + ΔP − C)
         = −ΔP / (CM + ΔP)        # CM = P − C; the denominator is the contribution after the change
```

Every remaining term contains a Δ, because only changes matter in evaluating a price change. If unit cost also changes, replacing C with C + ΔC gives −ΔCM / new CM. A price increase is explained by the same diagram, reading P + ΔP and Q + ΔQ as the initial state.

## Input schema for `scripts/pricing/breakeven.py`

```json
{
  "currency": "USD",
  "unit": "per seat per year",
  "baseline": {"price": 100, "unit_cost": 40, "volume": 1000},
  "volume_unit": "seats",
  "candidates": [
    {"price": 90, "expected": "+5–10%", "verdict": "No"},
    {"price": 110, "unit_cost": 42},
    {"price": 120, "incremental_fixed_cost": 20000}
  ],
  "volume_scenarios_pct": [-30, -15, 0, 15, 30]
}
```

Cannibalization mode (adding a cheaper tier next to an existing one):

```json
{
  "currency": "USD",
  "cannibalization": {
    "full": {"price": 120000, "unit_cost": 45000, "volume": 80},
    "lite_candidates": [{"price": 60000}, {"price": 75000, "unit_cost": 40000}],
    "downgrade_rates_pct": [5, 10, 20],
    "lite_fixed_cost": 0
  }
}
```

For each Lite price, it outputs the net and gross replacement ratios and the new Lite volume needed to break even at each switching rate. If a Lite candidate omits `unit_cost`, Full's unit cost is used.

`baseline.volume` is optional. If omitted, only percentages are output. `volume_scenarios_pct` defaults to `[-30, -15, 0, 15, 30]` and outputs profit-impact rows.

For a quick run use `--price 10 --cost 5.5 --candidates 9.5,10.5 --volume 4000`; for JSON input use `--input <file>`; for machine-readable output add `--json`.

For reactive mode, add `--reactive` or put `"reactive": true` at the top level of the JSON. For each candidate below the current price, it outputs in a separate table the sales-loss threshold above which matching pays off ((CM before − CM after) / CM before).

Optional fields used only when building slides (`--slides DIR`, `--slides-logic`): `volume_unit` (unit of volume, shown in the calculation logic as in "30 tenants"), per-candidate `expected` (expected volume change) and `verdict` (judgment), and `expected_loss` for competitive response (expected churn rate). Money amounts carry `currency`.

## Checklist

- [ ] The baseline is volume "if the price did not change"
- [ ] Allocated overhead and sunk costs are excluded from unit cost
- [ ] Incremental fixed costs of implementation and avoidable fixed costs are counted
- [ ] Inventory is valued at replacement cost, not acquisition cost
- [ ] CM and ΔP are in the same units
- [ ] The asymmetry between cuts and increases is shown in numbers
- [ ] Matching a competitor uses the reactive breakeven sales change formula
- [ ] If there is cannibalization, it says whether the net or gross replacement ratio is shown
- [ ] Evidence that the required sales change is achievable (measurement, competitor reactions) is attached

## Common mistakes and fixes

| Mistake | Fix |
|---|---|
| Rejecting prices below fully allocated average cost | Evaluate with incremental, avoidable costs. Some sales below average cost still add profit |
| Raising the price to recover development costs | Sunk costs are irrelevant to pricing. Adding them reduces sales and widens the loss |
| Crediting the price cut with growth that would have happened anyway | Compare against a baseline that includes growth |
| Looking only at the low-price tier's revenue | Subtract the lost Full contribution (opportunity cost) |
| Reporting a volume change as a revenue change | Convert with the revenue formula |
| Ignoring the steps in semi-fixed costs | Check where fixed costs step up in the scenario table |
| Not deciding because elasticity is unknown | Compute the required elasticity and judge whether the market is above or below it |
| Ignoring short-term losses for long-term strategic reasons | Quantify the short-term profit impact first, then layer on strategic considerations |

## Related documents

- [price-competition.md](price-competition.md): five questions for deciding whether to respond to a competitor's price cut
- [measurement.md](measurement.md): measurement methods to check whether the required sales change is reachable
- [price-structure.md](price-structure.md): price fences that limit cannibalization

## References

[1] Nagle, T. T., & Müller, G. (2018). *The Strategy and Tactics of Pricing: A Guide to Growing More Profitably* (6th ed.). Routledge.
- Chapter 9 "Financial Analysis: Analyzing Costs and Profits for Pricing", pp. 207–239.

In the text, "[1] p.N" refers to page N of [1].

Supplement not based on [1]: the numerical examples of the net and gross replacement ratios for cannibalization, the test for launching Lite, and how to use `scripts/pricing/breakeven.py`.
