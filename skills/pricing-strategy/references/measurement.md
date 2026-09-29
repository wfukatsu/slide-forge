*[日本語](measurement.ja.md)*

# Measuring price sensitivity

Covers how to confirm, as numbers from research and experiments, price sensitivity (how much purchasing changes when price changes) and willingness to pay (the most a buyer considers acceptable to pay). Its role is to test the assumptions at each stage of the value cascade (value creation → value communication → price structure → pricing policy → price level → price competition), especially price structure and price level. Use it to choose methods and to plan measurement before and after launch.

## Key points

- Measurement supplements management judgment; it does not replace it. Understanding who buys, why, and how comes first.
- Being precise and being accurate are different things. A research result reported to the decimal point is still just a research result; report it as a range.
- Classify methods on a 2×2 of "measurement conditions (uncontrolled / experimentally controlled)" × "variable measured (actual purchases / preferences and intentions)" ([1] Exhibit 8-1). Actual purchases are more reliable but costly, and cannot be used for products not yet launched.
- Never ask directly "what is the most you would pay?" Answers are distorted by haggling, ingratiation, or snap answers given without thought, and it is not accepted as a valid method.
- Use buy-response surveys only to identify the acceptable price range and to see "changes" across times and conditions. Do not use them to forecast sales volume.
- In-depth interviews do not ask about value directly; they infer it from usage. They are the foundation of value-based selling in B2B.
- Trade-off (conjoint) analysis can decompose price into the value of each attribute and is the most useful for strategy. However, it artificially raises attention to price, so it tends to overstate price sensitivity.
- Historical sales data is cheap, but what it estimates is the price elasticity (percent change in unit sales ÷ percent change in price) of the next level of the channel (for a manufacturer, wholesaler and retailer purchases), and it suffers from aggregation, multicollinearity, and too little price variation.

## Decision criteria and when to use what

### Classification of methods ([1] Exhibit 8-1)

| | Uncontrolled (observe) | Experimentally controlled (manipulate variables) |
|---|---|---|
| Actual purchases | Historical sales data, panel data, store scanner / transaction data, win/loss records | In-store purchase experiments, online A/B price tests, laboratory purchase experiments |
| Preferences and intentions | Direct questioning (do not use), buy-response surveys, in-depth interviews | Simulated purchase experiments, trade-off (conjoint) analysis |

The closer to the top right (controlled actual purchases), the more accurate and costly; the closer to the bottom left (uncontrolled preferences and intentions), the cheaper but more biased.

### Strengths and limits of each method

| Method | Strengths | Limits and cautions |
|---|---|---|
| Historical sales data | Nearly free | Yields only the elasticity of the next level of the channel. Aggregation erases differences between stores and promotions. Cannot detect anything if price has not moved. If price always moves with advertising, multicollinearity (explanatory variables moving together so effects cannot be separated) makes them inseparable. Cannot extrapolate to prices outside the observed range |
| Panel data | Gives prices actually paid, competitor purchases, and segment analysis linked to household attributes | Participating households are not fully representative. The act of recording raises price awareness |
| Store scanner / transaction data | Cheap, daily, and per store | In B2B, few transactions. Competitor prices reported by customers are biased low |
| In-store purchase experiments, A/B tests | Highest-quality estimates | Physical stores are expensive. Price differences between customers damage trust. If competitors notice, results are contaminated |
| Laboratory purchase experiments | Low cost and hidden from competitors. Control allows inference from few purchases | In a simple environment, attention to price is exaggerated. Being observed brings out behavior meant to look smart |
| Buy-response surveys | Cheap and fast. Yield a purchase probability curve (the share of respondents intending to buy at each price) | Responses run high. Cultural differences by country. Cannot forecast actual sales |
| Attribute ratings | Easy | Answers are careless and biased positive, with a halo effect (the tendency to rate all attributes similarly) |
| In-depth interviews | Can infer value drivers (the sources of benefit for the buyer) and the size of value | Costly and small samples. The share of customers that fit needs a separate quantitative survey |
| Simulated purchase experiments | Can test the price of a concept before development. Framing it as a choice among several brands curbs haggling and ingratiation | No actual purchase takes place |
| Trade-off analysis | Gives utility by attribute, price sensitivity by segment, and share forecasts for combinations that do not yet exist | Tends to overstate the role of price. For housing or face-to-face negotiated B2B, useful only for direction |

### First choice by situation ([1] pp.201–202)

| Situation | First choice | Reason |
|---|---|---|
| Concept or prototype stage | Trade-off analysis, in-depth interviews, simulated purchases | Neither historical data nor purchase experiments are available |
| Developed, low-price, frequently purchased products | In-store experiments, sophisticated laboratory purchase experiments | Buyers normally pay little attention to price, so surveys distort sensitivity. Pair a few in-store experiments with simulated purchases to correct the bias |
| Developed, high-priced durables | Simple laboratory experiments, simulated purchase surveys | Buyers naturally pay attention to price, so even simple methods come out fairly accurate |
| Products some time after launch | Historical sales data, win/loss records | If price changes made together with advertising are kept separate from those made alone, the effects can be separated |
| Online sales | A/B price tests, online simulated stores | Gets data close to actual purchases at low cost and in a short time |
| The tier structure itself is the issue | Trade-off analysis | Reveals utility by attribute, so you can set tier boundaries |

## Procedure

1. Write down the decision to be made: price level, tier structure, or discount policy. Also set the precision needed. What is usually needed is not the demand curve itself but a judgment of whether sales are "likely to exceed" the breakeven sales change (the change in sales volume needed to keep total contribution margin after a price change; [financial-analysis.md](financial-analysis.md)).
2. Start with exploratory qualitative research. Pin down who buys, why, and how they decide. To estimate value, use the total economic value framework (the price of the next-best competitive alternative = reference value, plus differentiation value) ([economic-value.md](economic-value.md)).
3. Choose a method from the tables above based on product stage and price range. Do not choose only because it is cheap, fast, or convenient.
4. Build judgment into the measurement design.
   - Sample: Match the attribute mix of actual buyers (proportional sampling). Check that weekday daytime surveys do not miss working people.
   - External factors: Record seasons, special events, competitor stockouts, and the like, and remove them in analysis.
   - Separating variables: If price and promotion always move together, either assume one effect from experience or run them separately.
   - Model structure: Set the experiment period and lags from the purchase cycle and inventory behavior.
   - Product description: Wording changes associations ("abrasion resistant" vs. "tough"). Match the appeal used in actual selling.
5. Points for each method.
   - In-depth interviews: Semi-structured, 1–2 hours. Ask about how the work is done today, costs, and where it fails; do not ask about price. 10–12 interviews per major segment surface about 90% of the important needs. In B2B, use evocative anchoring and ask "which budget line would you cut to get this benefit?"
   - Buy-response surveys: Show each respondent one different price and ask "would you buy at this price?" Aggregate into a purchase probability curve and look for the price where intention drops sharply (the knee of the curve).
   - Trade-off analysis: Have respondents choose among combinations that systematically vary attribute levels and price, and estimate each attribute's utility and price sensitivity. Look by segment, not the overall average (a high price that fails overall can work in a specific segment).
   - A/B and in-store tests: Limit to one region, channel, or cohort, and set up a control group. Run longer than the purchase cycle.
   - Historical data: Control for non-price factors with multivariate regression. Use the estimates only within the observed price range.
6. Interpret the results. First ask "why did this result come out?" Read them on the assumption that purchase intentions run high and that conjoint price sensitivity also runs high.
7. Report as a range, and reach a conclusion together with judgment. Use estimates not to replace judgment but as material to revise it.

### Measurement plan template

| Assumption to test | Method | Timing | Decision affected |
|---|---|---|---|
| The largest value driver exists at the assumed size | In-depth interviews (10–12 per major segment) | Before launch | Reference value, differentiation value, messaging |
| Tier boundaries match buyers' priorities among features | Trade-off survey | Before launch | Offer configuration ([price-structure.md](price-structure.md)) |
| Purchase intention holds at the recommended price | Buy-response survey | Before launch | Price level ([price-level.md](price-level.md)) |
| The discount policy is being followed | Win/loss records, exception approval records | From launch | Policy review ([pricing-policy.md](pricing-policy.md)) |
| Competitor response | Market monitoring | First two quarters | Response to competition ([price-competition.md](price-competition.md)) |

Always record quoted price, discount, competitor, and outcome in win/loss records. In B2B they are the closest thing to actual purchase data; start them on launch day.

## Checklist

- [ ] Stated the decision the measurement answers (price level, structure, policy)
- [ ] Can explain where the method falls in the 2×2
- [ ] Not using the direct question "how much would you pay?"
- [ ] Not using buy-response survey results to forecast sales volume
- [ ] The sample matches the mix of actual buyers
- [ ] Took steps to separate linked variables such as price and promotion
- [ ] Not extrapolating estimates outside the observed price range
- [ ] Stated which channel level's elasticity the historical sales data represents
- [ ] Looked at results by segment
- [ ] Reported results as a range, with the direction of each method's inherent bias

## Common mistakes and fixes

| Mistake | Fix |
|---|---|
| Asking "what's the most you would pay?" | Switch to in-depth interviews that infer value from usage, or to buy-response surveys with a fixed price |
| Using the share of purchase intention directly as a sales forecast | Use it only to identify the acceptable price range and to compare changes |
| Adopting conjoint price sensitivity as is | It runs high because prices are compared side by side. Correct with actual purchase data where possible |
| Describing end-customer elasticity from manufacturer shipment data | Remove the effect of channel inventory and interpret it as next-level elasticity |
| Giving up on a high price after looking only at the overall average | Analyze by segment. A high price can work for a specific group |
| Taking a precise number to be accurate | Understand that it is precise because it excludes factors that cannot be measured, and supplement with judgment |
| Trying to measure the effect with a company-wide price change | Set up limited tests and a control group, and present the results as facts |
| Using competitor prices reported by customers as is | Correct them, since they are biased low |

## Related documents

- [financial-analysis.md](financial-analysis.md): The breakeven sales change that measurement judges whether sales will exceed
- [economic-value.md](economic-value.md): Estimating value with total economic value
- [price-structure.md](price-structure.md): Designing tiers and offer configuration
- [price-level.md](price-level.md): How to set the price level
- [pricing-policy.md](pricing-policy.md): Discount and exception policy
- [price-competition.md](price-competition.md): Responding to competitor price cuts

## References

[1] Nagle, T. T., & Müller, G. (2018). *The Strategy and Tactics of Pricing: A Guide to Growing More Profitably* (6th ed.). Routledge.
- Chapter 8 "Measurement of Price Sensitivity: Research Techniques to Supplement Judgment", pp. 173–206.

In the text, "[1] p.N" refers to page N of [1].

Supplement not based on [1]: the "Online sales" and "tier structure" rows of the first-choice-by-situation table, and the measurement plan template.
