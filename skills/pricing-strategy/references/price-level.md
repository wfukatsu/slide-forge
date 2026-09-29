*[日本語](price-level.ja.md)*

# Price level

Covers how to decide "how much to charge" for each segment and each offer. This is the fifth stage of the value cascade (value creation → value communication → price structure → pricing policy → price level → price competition). Use it after the price structure is set ([price-structure.md](price-structure.md)), when deciding the initial price of a new product or a price increase or cut for an existing one.

## Key points

- Set the price level where value creation and value capture meet. Do not compromise between the finance and sales views; fuse them through one procedure.
- The procedure has six steps: price range → strategic choice → breakeven sales change → price elasticity → psychological factors → communicating the new price ([1] Exhibit 6-1).
- The ceiling is total economic value (price of the next-best competitive alternative + differentiation value). The floor is the price of the next-best competitive alternative (the best option a customer picks instead of you) for a positively differentiated product, or incremental cost (the cost added by that sale) for a negatively differentiated product.
- The rate of performance improvement and the premium you can charge are not the same. Derive the premium from differentiation value (the difference in value from the next-best competitive alternative, expressed as money).
- The strategies are skimming (high price, capturing price-insensitive buyers), penetration pricing (low price to win volume), and neutral pricing (keeping price from being the main driver of the purchase decision). Given capabilities and market position, the choice usually narrows to one.
- Instead of estimating a demand curve, calculate the minimum sales change needed to keep profit. That is largely determined by the contribution margin ratio (contribution margin as a share of price).
- Price sensitivity is a variable you can move by how you communicate value. Whether a price increase succeeds depends on how you communicate its fairness.

## Decision criteria and when to use what

### Price range

| Differentiation | Ceiling | Floor |
|---|---|---|
| Positive | Total economic value = price of the next-best competitive alternative + differentiation value | Price of the next-best competitive alternative (going below it invites a price war) |
| Negative | Total economic value (below the competitor's price) | Incremental cost ([1] calls it variable cost) |

- Selling at the ceiling leaves no reason to switch. The gap to the ceiling is the purchase incentive.
- The feasible price range, narrowed by strategy, breakeven, elasticity, and psychological factors, is much narrower than the theoretical range.
- Draw the range per segment. If ranges overlap, use one offer + price fences; if not, use separate tiers ([price-structure.md](price-structure.md)).

### Choosing a strategy

| Strategy | Conditions for success | Failure pattern |
|---|---|---|
| Skimming | Enough price-insensitive buyers who value the differentiating attributes highly / you can invest in communicating why the price is high / patents, brand, or distribution block low-price substitutes, or a low price would not deter entry anyway / buyers who pass move to your lower-end product | Imitated, and the high price lures entrants |
| Sequential skimming | Low repurchase rate; buyers leave once they buy. Cut price in stages, starting from the least sensitive buyers | Frequent cuts make buyers wait. Space them out and cut when launching a lower-end model |
| Penetration pricing | Most of the market would switch for a low price / high contribution margin ratio (at 90%, a 10% price cut needs only a 12.5% volume increase) / a reason competitors will not follow (cost or resource advantage, a loss leader recovered through complements, too small to provoke a response) | Competitors follow and profit disappears. Customers are conditioned to wait for "deals" |
| Neutral pricing | Neither set of conditions holds / you compete on product, brand, or service | Mistaking it for matching the competitor's price (neutral can work at a premium too) |

Penetration pricing is the most casually chosen and the least well founded. Do not adopt it unless you can answer "why won't competitors follow?" "Start low and raise later" is hard, because the initial price becomes the benchmark of fairness.

### Factors that affect price sensitivity (sidebar in [1] p.147–148)

| Factor | Condition that lowers price sensitivity |
|---|---|
| Reference value | You can frame the comparison against a more expensive alternative (in a new category, the initial price is the reference point) |
| Switching cost | Monetary and non-monetary costs of switching are large |
| Difficult comparison | Comparing and trying are hard, and failing to get the expected benefit is a large loss |
| Importance of end benefit | A tiny share of the total cost of an important outcome, or a high cost of failure |
| Price–quality perception | Price serves as a proxy for quality |
| Size of expenditure | Small share of budget (a large share raises sensitivity) |
| Shared cost | Someone else (insurer, employer) pays part |
| Transaction value | There is transaction utility from feeling the price is below a "fair price" |
| Perceived fairness | The price or increase is justified by cost or value (sensitivity spikes outside that range) |

Do not use these as a substitute for value estimation. Use them to argue for a position within the range and to design how you communicate it.

### New vs. existing products

| Aspect | New product | Existing product |
|---|---|---|
| Starting point | Value estimate from prospect research. As a last resort, a 50:50 split of differentiation value | Current price |
| Reference price | The initial price becomes the reference point and is hard to raise later | Changes are judged on fairness |
| Elasticity information | Controlled experiments, purchase intention surveys, structured inference ([measurement.md](measurement.md)) | Past natural experiments; judge whether they still apply |
| Main risks | Not understanding the value (address with education), perceived risk (address with guarantees) | Demand is more elastic for increases than for cuts |

## Procedure

1. **Define the range.** For each segment, line up total economic value ([economic-value.md](economic-value.md); `scripts/pricing/eve_calc.py` computes it per segment from value drivers), the price of the next-best competitive alternative, and incremental cost.
2. **Choose a strategy.** Test each condition for success one at a time and record the rationale.
   ```
   value capture rate = (price − price of next-best competitive alternative) / differentiation value
   ```
3. **Calculate the breakeven sales change (the change in sales volume needed to keep total contribution margin after a price change).** `scripts/pricing/breakeven.py` computes it for each candidate price (details in [financial-analysis.md](financial-analysis.md)).
   ```
   breakeven sales change = −ΔP / (CM + ΔP)
     ΔP: price change; CM: contribution margin per unit before the change (same units; as a ratio, relative to price)
   e.g. CM 50%, +5% → −5/55 = −9.1% (can lose up to 9.1%)
        CM 50%, −5% → +5/45 = +11.1%
        CM 50%, −25% → +25/25 = +100%
   price elasticity E = %ΔQ / %ΔP (usually negative)
   ```
   If the price cut is at or above the contribution margin ratio, no amount of extra sales will restore profit.
4. **Estimate elasticity.** Judge whether the required sales change is likely. Use past natural experiments, questions to sales (would they accept a target increase equal to breakeven in exchange for discount authority?), and the methods in [measurement.md](measurement.md). If unsure, change price in small steps and check the response.
5. **Consider psychological factors.** Identify which price sensitivity factors are at work, and lower price sensitivity by setting the reference value, offering guarantees, or restating the unit. If perceived risk is the obstacle, tie price to value with money-back or performance guarantees.
6. **Check competitor response** (an addition to the six steps of [1]; see [price-competition.md](price-competition.md)).
7. **Choose the final price and communicate it** (next section).

### Communicating the new price

1. **Explain it to all customers at once, tied to cost.** Where possible, link it to a published index (index-linked pricing).
   ```
   price increase rate = input cost increase rate × that cost's share of price
   e.g. energy +24%, share 10% → 2.4%
   ```
2. **Give advance notice.** Notify several months ahead and leave room to buy ahead at the old price. Show the time since the last increase, a comparison with the industry index, and how the added profit will be used.
3. **Do not be opportunistic.** "Buy more and you're exempt from the increase" signals that the rationale was bogus and invites retaliation.
4. **Consider non-price levers.** Surcharges, changing package contents, a low-price brand as a fallback, steering to off-peak, reformulation.
5. **To correct a price that was too low,** explain that "from now on all prices will match value," and offer either a path to earn the low price through cost-reducing behavior (such as long-term contracts) or an unbundled version at the old price.

## Checklist

- [ ] The ceiling and floor for each segment are given as numbers
- [ ] Variable cost is not used as the floor for a positively differentiated product
- [ ] The strategy's conditions for success were tested, and for penetration pricing there is a "reason competitors won't follow"
- [ ] Each candidate price has a breakeven sales change, and its feasibility was assessed with evidence
- [ ] The price sensitivity factors at work, and actions to lower them, are identified
- [ ] Competitor response has been considered
- [ ] There is a plan for communicating the new price (rationale, notice timing, whether to index, alternative levers)

## Common mistakes and fixes

| Mistake | Fix |
|---|---|
| Deciding by compromising between cost-plus and matching competitors | Define ceiling and floor by value, and align through the six steps |
| "x% better, so an x% premium" | Estimate differentiation value in money |
| Choosing penetration pricing without grounds | Show why competitors won't follow and the volume increase required |
| Pricing right at the ceiling | Leave a purchase incentive. Address lack of understanding with education and perceived risk with guarantees |
| Launching a new product cheap and raising later | Launch at a value-based price, and give adoption incentives through time-limited credits or guarantees |

## Related documents

- [price-structure.md](price-structure.md): Offer configuration, price metrics, and price fences (the previous stage).
- [economic-value.md](economic-value.md): Estimating total economic value and differentiation value.
- [financial-analysis.md](financial-analysis.md): Details of incremental cost and breakeven analysis.
- [measurement.md](measurement.md): Research methods for measuring price sensitivity and elasticity.
- [price-competition.md](price-competition.md): Reading competitor response and price competition.

## References

[1] Nagle, T. T., & Müller, G. (2018). *The Strategy and Tactics of Pricing: A Guide to Growing More Profitably* (6th ed.). Routledge.
- Chapter 6 "Price Level: Setting Prices that Capture a Share of the Value Created", pp. 133–151.

In the text, "[1] p.N" refers to page N of [1].
