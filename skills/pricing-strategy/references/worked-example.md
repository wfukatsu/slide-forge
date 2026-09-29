*[日本語](worked-example.ja.md)*

# Worked example: revising the price structure of B2B software

This example applies the value-based pricing process to one real analysis. The steps run in order: estimate value, run breakeven analysis on the price level, compare price structures, then make recommendations and set policy. The product name is withheld, and amounts are converted to USD with the original ratios kept. Use it as a model for how to run the analysis, how to use the calculation tools, and how to write up conclusions. All figures are illustrative and include assumptions; do not reuse them directly in other cases.

The example uses three calculation tools, all Python scripts.

| Script | What it calculates |
|---|---|
| `scripts/pricing/eve_calc.py` | Economic value per segment (reference value + differentiation value) |
| `scripts/pricing/breakeven.py` | Breakeven sales change for each candidate price |
| `scripts/pricing/structure_compare.py` | Revenue, contribution margin, and price-to-value ratio by customer size for each price-structure option |

## Situation

- **Product X**: data-platform middleware that keeps data consistent across multiple databases. It is billed per Kubernetes node (container).
- **Editions**: free Community, Standard (1,000 USD per node per month), and Premium (2,000 USD; adds SQL compatibility and encryption).
- **Request**: "Is the price right? Should we cut it to drive adoption?"
- **Request type**: a review of existing prices. The analysis, however, found that the problem was in the price structure (the metric), not the price level. This is a typical case where the wording of the request and the layer holding the real issue differ. For how to decide which layer solves a pricing problem (value creation → value communication → price structure → pricing policy → price level → price competition), see [value-cascade.md](value-cascade.md).

## Step 1: Organize the inputs (flag items that need confirmation)

| Assumption | Value | Status |
|---|---|---|
| Next-best competitive alternative | Building and maintaining consistency control in house, 84,000 USD per year (12 person-months to build, amortized over 3 years, + 3 person-months/year of maintenance, at 12,000 USD per person-month) | Needs confirmation |
| Incremental cost | 150 USD per node per month (support effort) | Needs confirmation |
| Node-count distribution (per 100 systems) | 2 nodes: 30, 4 nodes: 30, 6 nodes: 20, 10 nodes: 15, 16 nodes: 5 | Needs confirmation |
| Lifecycle stage | Core product in growth; new features in introduction | Confirmed |

Set the distribution and costs first, even as assumptions, and mark the items with high sensitivity as you go. Running one full pass on assumptions and then showing what needs confirming gets a faster decision from the client than stopping with a list of questions.

## Step 2: Economic value by segment (`scripts/pricing/eve_calc.py`)

Economic value is the most a fully informed customer could pay. Estimate it with the following formula (EVE: Economic Value Estimation).

- **Reference value**: the cost to the customer of the next-best alternative (here, building it in house).
- **Differentiation value**: the value of the ways the product is better than the alternative, minus the value of the ways it is worse.
- **Economic value** = reference value + differentiation value.

For details, see [economic-value.md](economic-value.md).

Input (excerpt from `eve.json`):

```json
{"unit": "1 システムあたり年額", "currency": "USD",
 "segments": [
  {"name": "新規サービス開発（Standard）",
   "reference": {"alternative": "自前での整合性制御の実装と保守", "value": 84000},
   "drivers": [
     {"name": "整合性障害の削減", "short": "障害の削減", "type": "monetary", "sign": "+", "formula": "incidents × cost × reduction", "inputs": {"incidents": 4, "cost": 20000, "reduction": 0.5}},
     {"name": "DB 変更時の改修回避", "short": "改修の回避", "type": "monetary", "sign": "+", "formula": "months × rate", "inputs": {"months": 2, "rate": 12000}},
     {"name": "学習・導入工数", "short": "学習・導入", "type": "monetary", "sign": "-", "formula": "months × rate", "inputs": {"months": 2, "rate": 12000}},
     {"name": "運用の追加負担", "short": "運用の負担", "type": "monetary", "sign": "-", "formula": "months × rate", "inputs": {"months": 1, "rate": 12000}}]}]}
```

The Premium segment (legacy migration) adds "reduced migration effort from SQL compatibility, 6 person-months".

| Segment | Reference value | Positive differentiation value | Negative differentiation value | Total economic value | Differentiation share |
|---|---|---|---|---|---|
| New service development (Standard) | 84,000 | +64,000 | −36,000 | 112,000 | 25% |
| Legacy migration (Premium) | 84,000 | +136,000 | −36,000 | 184,000 | 54% |

**How to read it**: the higher the differentiation share (net differentiation value ÷ total economic value), the easier it is to sell on value. Standard has a low differentiation share and is exposed to price comparison with building in house. More than half of Premium's value is reduced migration effort, so it can be sold on value. The negative drivers (learning and operating burden) can be reduced with onboarding support, which raises value.

## Step 3: Breakeven on the price level (`scripts/pricing/breakeven.py`)

Contribution margin (CM) is price minus the incremental cost per unit (the cost newly incurred by that sale). The breakeven sales change is the change in sales volume needed to keep total contribution margin unchanged after a price change. It is calculated as `−ΔP ÷ (CM + ΔP)`, where ΔP is the price change. For details, see [financial-analysis.md](financial-analysis.md).

```json
{"currency": "USD", "unit": "1 ノードあたり月額（Standard）",
 "baseline": {"price": 1000, "unit_cost": 150, "volume": 100},
 "candidates": [{"price": 800}, {"price": 900}, {"price": 1100}, {"price": 1200}],
 "volume_scenarios_pct": [-20, -10, 0, 10, 20]}
```

| Candidate price | Change | CM per node | Breakeven sales change |
|---|---|---|---|
| 800 | −20% | 650 | +30.8% |
| 900 | −10% | 750 | +13.3% |
| 1,100 | +10% | 950 | −10.5% |
| 1,200 | +20% | 1,050 | −19.0% |

**How to read it**: because the contribution margin ratio is high at 85%, a 10% price cut reduces profit unless the node count grows by at least 13.3%. This rules out the "cut the price to drive adoption" option.

## Step 4: Compare price structures (`scripts/pricing/structure_compare.py`)

The EVE shows that customer value is set mostly per system and is not proportional to node count. Price, however, is proportional to node count. To check this mismatch, three structures were compared on the same distribution.

```json
{"currency": "USD", "period": "年額", "unit_label": "ノード", "unit_cost": 1800,
 "distribution": [{"size": 2, "count": 30}, {"size": 4, "count": 30}, {"size": 6, "count": 20}, {"size": 10, "count": 15}, {"size": 16, "count": 5}],
 "value": 112000, "baseline": "現行（ノード単価のみ）",
 "options": [
  {"name": "現行（ノード単価のみ）", "short": "現行", "tiers": [{"from": 1, "rate": 11400}]},
  {"name": "A: 二部料金", "base_fee": "neutral", "tiers": [{"from": 1, "rate": 6000}]},
  {"name": "B: 段階割引（9 ノード目以降 50% 引き）", "short": "B: 段階割引", "tiers": [{"from": 1, "rate": 11400}, {"from": 9, "rate": 5700}]}],
 "recovery_size": 10, "show_sizes": [2, 4, 10, 16]}
```

| Option | CM (vs. baseline) | 2 nodes | 4 nodes | 10 nodes | 16 nodes |
|---|---|---|---|---|---|
| Current (per-node price only) | ±0% | 22,800 (20% of value) | 45,600 (41%) | 114,000 (102%) | 182,400 (163%) |
| A: Two-part tariff (base fee of 28,620 calculated as revenue-neutral + 6,000 per node) | ±0% | 40,620 (36%) | 52,620 (47%) | 88,620 (79%) | 124,620 (111%) |
| B: Tiered discount | −7.8% | 22,800 (20%) | 45,600 (41%) | 102,600 (92%) | 136,800 (122%) |

B does not reach breakeven unless it wins 4.7 additional 10-node customers (+31% over the current number).

**How to read it**: under the current structure, the price recovers only 20% of value from small customers and charges large customers more than the value they get. If discounting has become routine on large deals, the cause is the structure. Option A brings price closer to the value curve without changing contribution margin.

## Step 5: Writing the recommendation

The opening recommendation was limited to three points.

1. **Do not lower the price level.** Basis: the breakeven sales change (a 10% price cut needs a +13.3% volume increase).
2. **Revise the billing unit.** Move to a two-part tariff of a per-system base fee plus a per-node price (Option A, revenue-neutral). Basis: the price-to-value ratio (102% → 79% at 10 nodes).
3. **Limit discounts to give–get.** Every discount must be in exchange for something from the customer. Standardize the exchange terms on multi-year contracts, committed node counts, and public case studies ([pricing-policy.md](pricing-policy.md)).

It then stated the biggest risk (a 78% price increase for 2-node customers) and the countermeasure: apply the new structure to new contracts first, and move existing contracts over at renewal with a cap.

## Step 6: What the remaining sections covered

- **Price fences**: a price fence is a condition that keeps customers outside a segment from using that segment's price. Here, the contract defines "system" clearly. If the definition is vague, customers can avoid the base fee by splitting clusters ([price-structure.md](price-structure.md)).
- **Strategy**: penetration pricing for Community (low price to prioritize adoption), neutral pricing for Standard, and value-based positioning for Premium ([price-level.md](price-level.md)).
- **Lifecycle**: for new features in the introduction stage, build reference prices through contracts with early adopters. Decide first whether to bundle them or sell them as add-ons ([specialized-strategies.md](specialized-strategies.md)).
- **Measurement**: first, aggregate the node distribution and actual selling prices from contract data and recalculate Option A's coefficients. Then test it on a bounded set of new deals ([measurement.md](measurement.md)).
- **Legal**: record the basis for price differences between customers. Do not fix resale prices ([ethics-legal.md](ethics-legal.md)).

## Lessons from this example

- **The wording of a request and the layer of the real issue often differ.** The answer to "should we cut the price?" was a change in structure.
- **Lining up the price-to-value ratio by size exposes metric problems.** If price exceeds value at some sizes, that is where discount pressure comes from.
- **Design structural changes to be revenue-neutral, and handle the pain of transition separately.** If you can show the total does not change, the discussion can focus on whose price moves and how.
- **Run one full pass first, even on an assumed distribution.** Once you know which assumptions the conclusion depends on, you can ask for specific things to be confirmed.

## Related documents

- [value-cascade.md](value-cascade.md): how to identify which layer a pricing problem sits in.
- [economic-value.md](economic-value.md): economic value estimation (EVE) and segmentation.
- [financial-analysis.md](financial-analysis.md): calculating incremental cost, breakeven sales change, and cannibalization.
- [price-structure.md](price-structure.md): price metrics, offer configuration, and price fences.
- [price-level.md](price-level.md): price ranges and choosing among skimming, penetration, and neutral pricing.
- [pricing-policy.md](pricing-policy.md): discount policy and give–get.

## References

[1] Nagle, T. T., & Müller, G. (2018). *The Strategy and Tactics of Pricing: A Guide to Growing More Profitably* (6th ed.). Routledge.
- Chapter 2 "Economic Value: The Guiding Force of Pricing Strategy", pp. 26–55.
- Chapter 4 "Price Structure: Tactics for Pricing Differently Across Customer Segments", pp. 76–105.
- Chapter 6 "Price Level: Setting Prices that Capture a Share of the Value Created", pp. 133–151.
- Chapter 9 "Financial Analysis: Analyzing Costs and Profits for Pricing", pp. 207–239.

The analysis steps in this example follow the method in [1]. The product, figures, and conclusions are an illustration based on a real case and are not based on [1].
