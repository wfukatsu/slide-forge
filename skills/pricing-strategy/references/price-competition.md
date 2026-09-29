*[日本語](price-competition.ja.md)*

# Responding to price competition

Covers how to respond to a competitor's price cut or a low-price entrant, and when you may start a price cut yourself. This is the last stage of the value cascade (value creation → value communication → price structure → pricing policy → price level → price competition), where you decide how to protect the price you set from competitor moves. Use it when such a situation arises, to decide through five questions whether to respond and, if you respond, to narrow the response to its least costly form.

## Key points

- Price competition is usually a negative-sum game (a game where competing raises total cost). The less a price cut grows total market demand and the more alike the players' cost structures, the more everyone gets hurt, winner included. The model is war and diplomacy, not sports (positive-sum).
- The structure is close to the prisoner's dilemma. Cutting price alone looks profitable, but when everyone cuts, everyone's profit falls. Create a situation where competitors can expect that "cutting price won't pay."
- Drop the market-share myth (the belief that profit follows once you win share). Share and profit correlate only because both result from sustainable competitive advantage; share bought with price cuts brings no profit.
- The sources of competitive advantage are low cost, product value (the power to command a premium), and unique customer access. The measure is not market share but gross margin per sale compared with competitors (relative gross margin).
- Decide whether to respond to a competitor's price cut by going through five questions in order ([1] Exhibit 7-1). Every path that leads to "respond" passes through the quantitative test "cost of response < loss prevented."
- Even when you respond, avoid a uniform cut for all customers. Narrow it to the targeted customers, the incremental volume at risk, or markets where the competitor stands to lose more, or counter with value other than price.
- Most price wars start from lack of information and misreading. Collect competitor prices and intentions systematically, and disclose your own intentions and capabilities selectively (signaling).
- Low prices yield profitable growth only when one of four conditions holds: an incremental cost advantage, a niche where competitors will not respond, cross-subsidy from complementary products, or market expansion.

## Decision criteria and when to use what

### Types of game

| Type | Effect of competing | Examples | Implication for price |
|---|---|---|---|
| Positive-sum | Competing increases total benefit | New products, service improvement, value communication, operational efficiency | Make it the basis of a sustainable strategy |
| Negative-sum | Competing increases total cost | Competing on price alone, price wars | Fight only when you have a winning structure and can calculate that benefits exceed costs |

### Sources of competitive advantage (Porter's three positionings)

| Source | What it is | How to use it in pricing |
|---|---|---|
| Needs-based | Optimize operations for a specific segment's needs | Achieve a premium or low cost in that segment |
| Access-based | Unique customer touchpoints derived from geography or customer size | Compete through channels that deliver more cheaply than competitors |
| Focus-based | Specialize in a narrow activity that adds value across industries | Charge for expertise that cannot be imitated |

Having neither a value advantage nor a cost advantage is called being "stuck in the middle." Seeking growth through price in that position is suicidal.

### Response options

| Response | When to choose it |
|---|---|
| Accommodate / ignore | The cost of response exceeds the loss prevented. The competitor can restore the price gap with another cut. No spillover to other markets |
| Defend (selective response) | The cost of response is below the loss prevented, and the competitor cannot rebuild the price gap |
| Strategic defense | Your position in other markets (regions, products) is threatened, and the value of that market justifies the cost of response |
| Attack (cut price yourself) | One of the four conditions below holds |

### Four conditions under which aggressive pricing pays ([1] pp.170–171)

| Condition | What to check |
|---|---|
| 1. Incremental cost advantage | Is your incremental cost (the cost added by that sale) sufficiently lower than competitors', so they cannot follow? Can you keep the price gap smaller than the cost gap? |
| 2. A niche that draws no response | Does your offer appeal to only a small part of the competitor's market, leaving it no reason to respond? |
| 3. Cross-subsidy from complementary products | Can profits on complementary products cover the losses, when competitors cannot do the same? |
| 4. Market expansion | Does the price cut expand the market enough that industry profit rises even if competitors follow? |

## Procedure

1. Define the threat. Identify the competitor, the size of the cut, the targeted segments, regions, and products, and when it starts.
2. Calculate the reactive breakeven sales change. This is the threshold: if the sales you would lose by not following exceed it, following pays. Contribution margin (CM) is price − incremental cost per unit, and the contribution margin ratio is that as a share of price. The derivation and a numeric example are under "Reactive price changes" in [financial-analysis.md](financial-analysis.md) (breakeven analysis of price changes).

   ```
   reactive breakeven sales change = price change rate / contribution margin ratio
   e.g. a 15% matching cut, contribution margin ratio 45% → −15% / 45% = −33.3%
   Following pays only if you expect to lose more than 33.3% of sales by not following
   ```

   The same formula gives the sales increase needed (+33.3% in the example above) when you do not follow a competitor's price increase.
   For following a price cut, pass `--price <current> --cost <incremental cost> --candidates <matching price> --reactive` to `scripts/pricing/breakeven.py` (which computes the breakeven sales change for each candidate price); for JSON input, use `"reactive": true`. For each candidate below the current price, it outputs this threshold in a table separate from the regular breakeven.
3. Answer the five questions ([1] Exhibit 7-1) in order.
   1. Is there a response that costs less than the sales loss it prevents? Estimate the "preventable" loss realistically (exclude customers who would not come back even if you matched the price). If Yes, go to question 2; if No, go to question 4.
   2. If you respond, will the competitor cut again to rebuild the price gap? Competitors with small share and no weapon other than price, or with large sunk costs (spent and unrecoverable) that act as exit barriers, will. If No, respond; if Yes, go to question 3.
   3. Is the total cost of responding again and again smaller than the sales loss avoided? Compare the cost of the whole price war, not the first move. If Yes, respond; if No, go to question 4.
   4. Even if question 1 or 3 was No, would the competitor gaining share endanger your position in other markets (regions, products)? If No, accommodate / ignore; if Yes, go to question 5.
   5. Does the value of that at-risk market justify the cost of response? Quantify it, even roughly. If Yes, respond; if No, accommodate.
4. Once you decide to respond, choose the least costly form.
   - Offer a flanking offer (a low-price version with low-value elements stripped out) only to the targeted price-sensitive customers, in a form you can withdraw later.
   - Protect only the incremental volume at risk (for example, give a competitive discount only on volume above 80% of last year's purchases).
   - Fight back in markets where the competitor loses more than you (the competitor's home market, the competitor's core product).
   - Raise the competitor's cost of cutting (tell the competitor's existing customers that only new customers get the low price, advertise a lowest-price guarantee).
   - Raise value through your competitive advantage rather than price. Make it an offer that costs the competitor more than you to copy.
   - Use price fences (conditions that separate prices by buyer attributes or purchase conditions) to narrow the target. For design, see [price-structure.md](price-structure.md) (price structure and price fences) and [pricing-policy.md](pricing-policy.md) (operating discounts and exceptions).
5. If every response costs more than conceding the sales, concede share to protect margin, and put the cash into cost efficiency and value improvement.
6. Before approving a retaliatory cut for "strategic reasons," require the long-term benefits (future additional sales, complementary product sales, cost advantage) and risks (spillover of the cut to other customers and markets, a downward spiral) to be stated in writing.
7. Manage competitive information.
   - Collect: Have sales record competitor prices in call reports and aggregate them. Also use loyal customers, industry associations, analysts, distributors, and store checks. Collect intentions too (the aim of a merger, investment plans).
   - Verify: Discount purchasing agents' claims that "the competitor bid lower." No customer says "your price was too low" when you win, so sales easily come to believe your prices are too high.
   - Signal: Explain price increases publicly with reasons, and announce them well before the effective date. Show your intent to defend with lowest-price guarantees or right of first refusal clauses. If attacking on a cost advantage, first release information that convinces competitors the advantage is decisive.
   - Respond faster. Responding in one week instead of three cuts the benefit of an opportunistic price cut by two-thirds.
8. If you start a price cut yourself, state which of the four conditions above applies. If none applies, switch to non-price means.

## Checklist

- [ ] Calculated the reactive breakeven sales change (price change rate / contribution margin ratio) and compared it with the expected sales loss
- [ ] Excluded from the "preventable" loss the sales that would not come back even if you matched the price
- [ ] Assessed the competitor's ability to cut again (share, cost structure, exit barriers)
- [ ] Compared on the total cost of the price war (multiple responses)
- [ ] Quantified the risk of spillover to other markets and the value of those markets
- [ ] Narrowed the response to target customers, incremental volume, or markets rather than all customers uniformly
- [ ] Considered non-price countermeasures (added value, flanking offers with price fences)
- [ ] Checked that your price cut will be read as intended (not misread as a grab for share)
- [ ] For an aggressive price cut, stated which of the four conditions applies
- [ ] Price is not below variable cost (for the legal risk of predatory pricing, see [ethics-legal.md](ethics-legal.md))

## Common mistakes and fixes

| Mistake | Fix |
|---|---|
| Reflexively following every price cut | Decide only after running the reactive breakeven sales change and the five questions |
| Cutting price to hit a share target | Share is a result, not a goal. Measure advantage by relative gross margin |
| Answering a threat to some customers by cutting price on all sales | Narrow the scope with flanking offers, discounts on incremental volume, or regional limits |
| Assuming a large firm can drive out small competitors through attrition | Pricing below variable cost can violate antitrust law. Even if you drive them out, new entrants who bought the bankrupt assets cheaply come back |
| Approving a retaliatory cut for "strategic reasons" without numbers | Require long-term benefits and risks to be stated, and a rough estimate of the at-risk market's value |
| Taking competitor prices quoted by purchasing agents at face value | Monitor competitor prices systematically so you can spot exaggeration |
| Keeping information too secret, inviting competitor overinvestment or dumping | Explain the industry outlook and reasons for price increases publicly |
| Releasing information that later proves wrong | You lose credibility and later signals stop working. Release only fact-based information |

## Related documents

- [financial-analysis.md](financial-analysis.md): Formulas for the breakeven sales change and reactive price changes, and inputs to `scripts/pricing/breakeven.py`
- [price-structure.md](price-structure.md): Segment-specific prices through price fences and offer configuration
- [pricing-policy.md](pricing-policy.md): Policies for handling discount requests and exceptions
- [ethics-legal.md](ethics-legal.md): Legal constraints such as predatory pricing

## References

[1] Nagle, T. T., & Müller, G. (2018). *The Strategy and Tactics of Pricing: A Guide to Growing More Profitably* (6th ed.). Routledge.
- Chapter 7 "Price Competition: Managing Conflict Thoughtfully", pp. 152–172.

In the text, "[1] p.N" refers to page N of [1].

Supplement not based on [1]: the explanation using the prisoner's dilemma framework.
