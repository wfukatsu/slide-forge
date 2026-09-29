*[日本語](value-cascade.ja.md)*

# The value cascade and the principles of strategic pricing
This document covers the whole value cascade (value creation → value communication → price structure → price policy → price level → price competition) and the three principles that run through it. Other documents cover each tier in detail. Read this first when you get a pricing question, and decide which tier has the problem and which document to read next.

## Key points
- Product, promotion, and distribution "create" value; pricing "captures" that value as profit. The upper limit on what can be captured is set upstream.
- Organize strategic pricing as a six-tier value cascade: value creation → value communication → price structure → price policy → price level → price competition. The first three tiers are value management; the last three are price management.
- Cutting corners at any tier becomes a "gap" that leaks profit. Value shrinks tier by tier: potential value → realized value → perceived value → target price → willingness to pay (the most a customer is willing to pay) → actual price → sustainable profit.
- The three principles are value-based, proactive, and profit-driven.
- Do not use the three approaches of cost-plus, customer-driven, and share-driven pricing; they have structural flaws.
- In practice, asking for the breakeven sales change (the change in sales volume needed to keep total contribution margin unchanged after a price change) works better than estimating and optimizing a demand curve.
- Value-based pricing runs the process in the opposite direction from cost-plus. Think in the order customer → value → price → cost → product; the target price determines allowable cost and specifications ([1] Exhibit 1-3).
- Most complaints that "the price is too high" are problems of communication, structure, or policy, not price level.

## Decision criteria

### Questions and leaks by tier
| Tier | Question to answer | Typical leak when skipped | Read next |
|---|---|---|---|
| 1. Value creation | Does the offer include only benefits customers pay for? Is allowable cost set from the target price? | Features nobody values only raise cost | [economic-value.md](economic-value.md) |
| 2. Value communication | Do customers understand the value well enough to justify the price? | A feature list, so buyers look only at price | [value-communication.md](value-communication.md) |
| 3. Price structure | Do the price metric (the unit of charge), tiers, and price fences (conditions for applying segment-specific prices) reflect differences in value and cost-to-serve across segments? | A single price leaves money on the table with high-value customers and loses low-value ones | [price-structure.md](price-structure.md) |
| 4. Price policy | Are there consistent rules for discount requests and competitive threats? | Ad hoc exceptions teach customers that list price is a starting point for negotiation | [pricing-policy.md](pricing-policy.md) |
| 5. Price level | Within the acceptable range, do you choose skimming (high price to capture high-value customers), penetration pricing (low price to win volume), or neutral pricing (price is not the deciding factor)? | The price is set by cost-plus or by "what the customer says" | [price-level.md](price-level.md) |
| 6. Price competition | Is it still profitable after factoring in competitor reactions? | A price war that erodes everyone's profit | [price-competition.md](price-competition.md) |

### Diagnose the tier from symptoms
| Symptom | Suspected tier |
|---|---|
| Even customers who have adopted the product do not feel its value, or many features go unused | 1 Creation |
| Prospects say "it's expensive," but adopting customers are highly satisfied | 2 Communication (perceived value is below economic value) |
| Large and small customers pay the same price, and one group is unhappy | 3 Structure |
| Discount rates widen every quarter, and exception approvals have become routine | 4 Policy |
| Value and structure are sorted out, and only the number remains to be set | 5 Level |
| You are unsure whether to follow a competitor's price cut | 6 Competition (plus 3 and 4) |

### Three approaches to avoid
| Approach | Flaw | Replacement question |
|---|---|---|
| Cost-plus | Unit cost depends on volume, and volume depends on price, so the logic is circular. It yields prices too high in weak markets and too low in strong ones. Raising prices to recover fixed costs cuts volume, leading to a "death spiral" | Given an achievable price, how much cost can we afford? |
| Customer-driven | Matching what customers "say they will pay" teaches buyers to hide value. It abandons sales' job of moving willingness to pay closer to value | What is the value to this customer, and how do we communicate it to justify the price? |
| Share-driven | Price cuts are quickly copied, so any advantage is temporary and only the low margin is permanent | What level of share is most profitable? |

## Procedure
1. Summarize the question in one sentence and use the diagnosis table above to identify the most upstream suspect tier. Even for downstream symptoms (discounts, competitor price cuts), fix upstream first if the cause is upstream.
2. Check tiers 1 and 2. If the target segment, the next-best competitive alternative (what the customer would choose without you), and the top value drivers (factors that affect the customer's economics or satisfaction) are not articulated, start with [economic-value.md](economic-value.md).
3. Check tiers 3 and 4. See whether the price metric, offer configuration (what is sold in which tiers and combinations), price fences, and discount rules are documented.
4. Set the price level in tier 5. For each candidate price change, calculate the breakeven sales change and compare it with the expected demand response. Contribution margin (CM) is price − unit incremental cost (cost that grows with volume); the contribution margin ratio is that divided by price.
   ```
   Breakeven sales change = −ΔP / (CM + ΔP)
     ΔP: price change ratio (negative for a cut)  CM: contribution margin ratio before the change
   e.g. CM 20%, 10% price cut → 0.10/(0.20−0.10) = +100%
        CM 70%, 10% price cut → 0.10/(0.70−0.10) ≒ +17%
        CM 30%, 10% price increase → −0.10/(0.30+0.10) = −25% (profit does not fall unless volume drops more than 25%)
   ```
   Connecting the values for each price change gives the breakeven sales curve ([1] Exhibit 1-1). If actual demand is steeper than this curve (inelastic), a price increase pays; if it is flatter (elastic), a price cut pays. For detailed calculations, use [financial-analysis.md](financial-analysis.md) and scripts/pricing/breakeven.py, which computes the breakeven sales change.
5. In tier 6, predict competitor reactions and confirm the move is still profitable after they react ([price-competition.md](price-competition.md)).
6. Check the conclusion against the three principles: does the value difference become a price difference (value-based), do you anticipate reactions and requests (proactive), and is the metric profit rather than share (profit-driven)?
7. If there are organizational obstacles (who sets prices, whether the needed information exists, whether sales compensation depends only on revenue), refer them to [pricing-capability.md](pricing-capability.md).

## Checklist
- [ ] States which tier the problem is in and why (the symptoms)
- [ ] Checks the state of value (tier 1) and communication (tier 2) before discussing price level
- [ ] Bases the price on customer value, not stacked-up costs or "what the customer said they would pay"
- [ ] Reasons backward from the target price to allowable cost and specifications
- [ ] Attaches a breakeven sales change to each proposed price change
- [ ] Judges success by contribution margin, not share or volume
- [ ] Considers competitor reactions and what customers learn in negotiation
- [ ] Addresses organizational obstacles: decision rights, information, and incentives (if applicable)

## Common mistakes and fixes
| Mistake | Fix |
|---|---|
| Trying to solve everything at tier 5: "cut the price and it will sell" | Check upstream with the diagnosis table. If low perceived value is the cause, the answer is communication, not a price cut |
| Adding a markup to a unit cost that includes allocated fixed costs | Calculate contribution margin with incremental cost only, and do not use fixed costs as a basis for price |
| Treating customer satisfaction as the outcome | Satisfaction can be bought with underpricing. Measure value capture and contribution margin |
| Cutting prices to hit a share target | Check whether competitors can follow. If they follow, profit falls permanently |
| Spending time estimating elasticity precisely | It is enough to compute the breakeven sales change and judge whether the actual response is likely to exceed it |
| Leaving pricing decisions entirely to sales | Set policy and approval rules first, and give sales tools for selling value |

## Related documents
- [economic-value.md](economic-value.md): Tier 1. Estimating economic value and segmentation.
- [value-communication.md](value-communication.md): Tier 2. Value messages and price presentation.
- [price-structure.md](price-structure.md): Tier 3. Designing metrics and fences.
- [pricing-policy.md](pricing-policy.md): Tier 4. Discount policy and give–get.
- [price-level.md](price-level.md): Tier 5. Price ranges and choosing a strategy.
- [price-competition.md](price-competition.md): Tier 6. Predicting competitor reactions.
- [financial-analysis.md](financial-analysis.md): Detailed breakeven sales change calculations.
- [pricing-capability.md](pricing-capability.md): Organizational mechanisms for setting prices.

## References

[1] Nagle, T. T., & Müller, G. (2018). *The Strategy and Tactics of Pricing: A Guide to Growing More Profitably* (6th ed.). Routledge.
- Chapter 1 "Strategic Pricing: Coordinating the Drivers of Profitability", pp. 1–25.

In the text, "[1] p.N" refers to page N of [1].
