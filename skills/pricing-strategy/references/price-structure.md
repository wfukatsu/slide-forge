*[日本語](price-structure.ja.md)*

# Price structure

This document covers how to design "who buys which bundle, in which unit, under which conditions" when value or cost-to-serve differs by segment. It is the third tier of the value cascade (value creation → value communication → price structure → price policy → price level → price competition); use it when turning estimated value and segments into the skeleton of a price list.

## Key points

- A single price is too low for high-value customers and too high for low-value ones. Price structure aligns prices with differences in value and cost-to-serve, and creates price differences without case-by-case negotiation. In a five-segment example, going from 1 → 2 → 5 price points raises contribution margin ((price − unit incremental cost) × volume) from $2,750 → $3,800 → $4,950 (thousand dollars), about 80% ([1] Exhibit 4-1).
- There are three mechanisms: offer configuration, price metric, and price fence. They are easiest to enforce in that order, and are usually combined.
- Customers on the high-price side try to pass as the low-price side. Gray-market resale, and flexible pricing that gives sales discretion to discount, order prices by negotiating power rather than value. So design the structure proactively.
- Bundling works when segments rank the importance of components in opposite order. Bundling a service with variable costs for free attracts high-cost customers, so unbundle strategically.
- The price metric sets "what the buyer gets per unit paid." Score candidates on five criteria; if no single metric satisfies them, use a multi-part structure of base fee plus usage.
- A price fence is an eligibility condition for applying different price levels to the same product and the same metric. Always test it for leaks.
- Segmentation is built in [economic-value.md](economic-value.md). Primary segments are customer groups that seek different benefits; secondary segments divide these by the value driver with the widest differences.

## Decision criteria

| Source of value difference | Mechanism | Enforcement difficulty |
|---|---|---|
| Different features or services needed | Offer configuration (bundles, tiers) | Low (customers self-select) |
| Different usage volume, intensity, or outcomes | Price metric | Medium (depends on measurability) |
| Same product and use, but different ability to pay or alternatives | Price fence | High (easy to cross) |

### Offer configuration types

| Type | When to use / key points |
|---|---|
| Tiers (good/better/best) | Needed features differ in steps. About three tiers. Build lower versions by removing value that only high-value customers care about |
| Mixed bundle | Rankings of importance are reversed. Show the sum of individual prices as the bundle's reference value (the price customers compare against) |
| Segment-specific add-ons | Instead of cutting price, bundle add-ons that only the segment that would not come without a low price appreciates |
| Selective uglification | Add conditions to the low-price version that impair value only for high-value customers (the Saturday-night-stay condition on discount fares) |
| Unbundling / options | Charge by usage for services whose cost varies by customer, or limit them to upper tiers. For customers used to getting them free, introduce the change as "refunded if not used" |

### Five criteria for price metrics (scoring template)

Score each candidate 0–2 (0 = not met, 1 = partly, 2 = fully) and write a one-line rationale.

| Candidate | ① Value difference | ② Cost-to-serve difference | ③ Measurement and enforcement | ④ Competitive comparison | ⑤ Value experience | Total | Rationale |
|---|---|---|---|---|---|---|---|
| e.g. number of users |  |  |  |  |  |  |  |
| e.g. base fee + transactions |  |  |  |  |  |  |  |

- ① Do customers who get more value pay more? (the antidepressant Prozac, priced "per day of treatment")
- ② Does revenue rise when cost-to-serve rises? (surcharges for residential delivery)
- ③ Can both sides count it without dispute? (published indexes and measured values over self-reports)
- ④ Does it avoid looking bad in unit-price comparisons? (call-center software is 72% more expensive "per minute" but 11% cheaper "per completed call"; [1] Exhibit 4-5)
- ⑤ Is it a unit in which the buyer feels value? (monthly DVD rental priced by the number of discs out at once)

Capacity-based metrics track cost but rarely track value. Performance-based pricing tracks value and shifts performance risk to the seller (the GE90 charged per flight hour), but needs agreement on measurement and customer data. If that is not feasible, look for a proxy that "roughly predicts" value and cost.

### Price fence types

| Type | Examples | Main ways it leaks |
|---|---|---|
| Buyer identification | Student, senior, and nonprofit discounts; coupons (self-identification) | Faked eligibility |
| Purchase location / channel | Regional pricing, channel pricing, freight absorption | Parallel imports, resale |
| Time of purchase | Off-peak discounts, priority pricing (launch new products high and lower in steps) | Deferred purchases |
| Purchase quantity | Volume discounts, two-part tariffs | Pooled purchasing, split orders |
| Product design | Feature-limited versions, selective uglification | The low-price version can serve high-value uses |

In [1], fences are the first four types, and product design is treated as offer configuration. It is included here to keep leak testing in one place.

### Volume discounts, two-part tariffs, and tie-ins

| Tool | When to use |
|---|---|
| Volume discount (cumulative over a period) | Retaining large customers |
| Order discount (per order quantity) | Reducing order-processing and delivery costs |
| Step discount (only on the amount above a threshold) | Winning demand for other uses while protecting the unit price on small volumes (block pricing for electricity) |
| Two-part tariff (fixed + usage) | Acquiring or visiting a new customer has a fixed cost, and the marginal cost of additional volume is low |
| Tie-in | Capital goods whose value varies with intensity of use. Price the equipment low and mark up dedicated consumables. Enforcing this by contract is legally difficult, so do it through technical design (for legal issues, see [ethics-legal.md](ethics-legal.md)) |

## Procedure

1. **Take the segments as input.** As a rule, separate primary segments with different offers, and secondary segments with metrics and fences.
2. **Lay out value and cost-to-serve, and estimate contribution margin for each number of price points.**
   ```
   CM with single price P       = Σ_{WTP_i ≥ P} N_i × (P − VC_i)
   CM with segment prices       = Σ_i N_i × (P_i − VC_i)   (P_i ≤ WTP_i)
     N_i: volume, WTP_i: willingness to pay, VC_i: unit variable cost
   ```
   Add price points as long as the gain exceeds the cost of complexity and enforcement.
3. **Choose the offer configuration.** For each segment, sort components into required, important, and unneeded, and choose from the types table.
   ```
   Bundling pays when: min over segments of total WTP > sum of the individual prices that capture all segments
   e.g. Segment A $18/$23, Segment B $6/$33 → individually at most $6+$23=$29; as a bundle, both buy at $39
   ```
4. **Score price metrics.** Score 3–5 candidates on the five criteria. If no single metric satisfies both ① and ②, use a multi-part structure.
5. **Compare across the customer size distribution.** Pass a JSON list of customer sizes and counts, plus the candidates, to `scripts/pricing/structure_compare.py` (for each candidate of base fee plus tiered usage rates, it computes payment by customer size, total revenue, and contribution margin); the schema is at the top of the script. Check for size bands that are extremely overpriced or underpriced, and sizes where payment crosses a competitor's. When building slides, add `short` per option (for column headings, up to 12 characters) and `recommended` (the name of the option to highlight). In the calculation logic, amounts get `currency` and counts get `unit_label` as their units.
6. **Design price fences.** For each secondary segment, choose eligibility conditions from the types table.
7. **Test for leaks.** For each fence, ask "Can a high-price customer buy through the low-price entrance?" (faking, resale, splitting or pooling, shifting timing, substituting the low-price version), and if so add verification effort or rules.
8. **Deliverable:** For each primary segment, a table of "offer/tier, metric, list price (provisional), fence, cost-to-serve notes." Settle the level in [price-level.md](price-level.md) and transaction terms in [pricing-policy.md](pricing-policy.md).

## Checklist

- [ ] Every price difference is explained by a difference in value or cost-to-serve
- [ ] Lower tiers are built by removing value only high-value customers care about, and downgrading from upper tiers has been considered
- [ ] Services whose cost varies by customer are not bundled for free (or there is a reason if they are)
- [ ] There is a five-criteria scoring table for candidate metrics
- [ ] Payments have been estimated across the customer size distribution
- [ ] Every fence has leak-test results
- [ ] Volume discounts apply to increments and are not retroactive to existing volume

## Common mistakes and fixes

| Mistake | Fix |
|---|---|
| Using the industry's customary metric as is | Score alternatives on the five criteria. Companies that changed the convention have gained margin |
| Adding paid services for free to differentiate | Switch to usage-based charging or limit them to upper tiers |
| Achieving segment prices through sales-discretion discounts | Differentiate proactively with offer configuration and fences |
| Promising performance-based pricing without a way to measure | Use a proxy, or a base fee plus a performance bonus |

## Related documents

- [economic-value.md](economic-value.md): Estimating total economic value and segmentation (input).
- [price-level.md](price-level.md): How to set the price level (how much) for each offer.
- [pricing-policy.md](pricing-policy.md): How to move prices per transaction: discounts, exceptions, and price increases.
- [ethics-legal.md](ethics-legal.md): Legal constraints such as on tie-ins.

## References

[1] Nagle, T. T., & Müller, G. (2018). *The Strategy and Tactics of Pricing: A Guide to Growing More Profitably* (6th ed.). Routledge.
- Chapter 4 "Price Structure: Tactics for Pricing Differently Across Customer Segments", pp. 76–105.

In the text, "[1] p.N" refers to page N of [1].

Note: the individual-price ceiling in the bundle example is $6+$23=$29 to match Exhibit 4-3 (the text on p.82 says $6+$25=$31, which conflicts with the exhibit; the conclusion is the same).
