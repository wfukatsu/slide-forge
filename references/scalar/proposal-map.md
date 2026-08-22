*[日本語](proposal-map.ja.md)*

# Scalar Proposal Deck Design Reference — Problem-to-Product Mapping and Proposal Structure (researched 2026-08-05)

**Freshness warning**: Case studies, pricing, and edition composition go stale.
Apply the same **3-month rule** as `research-2026-08.md` (if more than 3 months
have passed since the research date, re-research before using this file). The proposal "structure"
(the composition and conventions in §2) does not go stale as quickly and does not need re-research.

## 1. Items to confirm before proposing (discovery)

A proposal cannot be written without customer-specific information. First check
whether the following are filled in; for anything not yet obtained, **either confirm it
with AskUserQuestion, or treat it in the deck as "to be confirmed today"**
(never fill it in with a guess). Sources: Y's system proposal guide +
BANT (§6).

**Collection forms**: [`templates/sales/hearing-sheet.ja.md`](../../templates/sales/hearing-sheet.ja.md)
(product-neutral — it collects the customer's facts) and
[`templates/sales/products/scalar.ja.md`](../../templates/sales/products/scalar.ja.md)
(the Scalar product-fit judgment). The mapping from the categories below to the
sheet's sections is in the sheet's §14.3. When a filled-in sheet exists, use it
as the Phase 1 input.

| Category | What to confirm | Where it's used in the deck |
|---|---|---|
| Problem / objective | What is the current problem. **Whose** problem is it, and how strong/large in monetary terms | Problem summary, expected outcomes |
| Current system | System configuration, DB product, integration method (batch/API/manual), **whether direct writes bypassing ScalarDB will remain** (directly relevant to the constraints in §4) | Current-state / proposed architecture diagram |
| Expected outcomes | Expected quantitative results, and whether the data to calculate them is available | Expected outcomes, PoC success criteria |
| Organization | Customer-side program structure, operating structure, expected capacity | Organization chart |
| Decision structure | Decision-making unit (DMU) members, approval process, who the approver is | Summary granularity, comparison axes |
| Budget | Whether a budget line exists, its scale, timing of budget approval (fiscal year) | Cost, schedule |
| Schedule | Desired implementation timing, and the deal steps from kickoff to decision | Gantt chart, next steps |
| Enterprise-specific | Security/compliance requirements, non-functional requirements (availability, performance), intent to run a PoC and its evaluation criteria | Risks, PoC proposal |

## 2. Items to include in the proposal (structure and conventions)

The structural foundation is `references/deck-outlines.md`'s "problem-solving proposal."
The standard structure, reinforced with B2B proposal best practices (Sairu, HubSpot, Y's, §6),
is `scripts/scalar/build_scalar_proposal.py` (worked example, 20 slides).

| # | Section | Slide in the worked example | Rationale |
|---|---|---|---|
| 0 | Cover | COVER | — |
| 1 | Executive summary | `exec_summary` (situation → problem → answer + discussion points) | Decision-makers only read the opening. Lead with the conclusion |
| 2 | Background and current state | `icon_flow` + `so_what` | Build agreement on problem recognition before the solution |
| 3 | Problem summary (3 points) | `cards` | Limit problems to 3 points |
| 4 | Problem structure | `iceberg` (surface issue / root cause) | Foundation for differentiating from symptomatic fixes |
| 5 | Target state and scope | `before_after` + explicit out-of-scope items | Manage expectations by stating what is not included |
| 6 | Solution (product proposal) | Integrated layer diagram (icon_row + bands + arrows) | A diagram over prose. Use drawio-diagrams for dense diagrams |
| 7 | Problem-to-solution mapping | `table` (problem → feature → resulting state) | Match the order and wording of the problem slide |
| 8 | Comparison of solutions | `table` (comparison with alternatives) | "Why it has to be this" is essential for internal approval |
| 9 | Expected outcomes | `before_after` (change in operations) + quantification policy | Talk about the change in operations, not features. Never state quantitative figures without grounds |
| 10 | Case studies | `cards` + `source_note` | Reinforce trust after sparking interest (don't lead with the company introduction) |
| 11 | Implementation approach | `journey` + PoC success criteria | Explicit small start and Go/No-Go |
| 12 | Schedule | `gantt` | Proof of feasibility |
| 13 | Organization | `orgchart` + role table (state the customer-side workload explicitly) | Show that it "won't take much effort" |
| 14 | Estimated cost | `table` + `source_note` | Place pricing **after** the solution and outcomes |
| 15 | Risks and countermeasures | `table` (concern → countermeasure) | Preempt the decision-maker's concerns |
| 16 | Next steps | `flow` + `so_what` | Make the next action explicit. Don't just send it and leave it |
| 17 | Closing | CLOSING | — |

Conventions (whole deck):

- **Write the problem in the customer's own words**. State explicitly that it comes from
  discovery, and add a line such as "if our understanding is off, we'd like to correct it today"
  (reaching agreement on the problem is itself the purpose of the meeting)
- **Only include quantitative outcome figures that can be backed by a calculation basis**.
  If none exists, state it qualitatively and frame it as
  "we'll measure it in the PoC and use it as material for internal approval"
- **Only use figures from published case studies** (ENS statutory reporting ~1/5, Tsuneishi
  Shipbuilding MVP roughly 3 months, 70% reduction in implementation effort, etc.). Keep the source in
  `source_note` and the speaker notes
- Put mid/long-term roadmap and detailed feature explanations in the Appendix (keep the main body lean)

## 3. Problem category → product mapping

When you hear the customer's problem, check it against this table first. If it doesn't fit,
or if it falls under §4, don't force it into a Scalar product fit (honesty is also part of proposal quality).

| Category | Example customer phrasing | Product / feature | Case study (published) |
|---|---|---|---|
| A. Siloed multiple DBs / distributed data integration | "Each department has its own separate app and DB," "we want to simplify a system that's become complex due to silos" | ScalarDB (virtually unifies heterogeneous DBs behind one API, no migration needed). SQL/GraphQL is Premium. Cross-cutting analytics is Analytics | Major broadcaster (content data management), LayerX Ai Workforce (Oct 2024) |
| B. Data consistency across microservices | "After splitting into services, we can't keep consistency across DBs" | ScalarDB distributed ACID (strict serializability), 2-phase commit interface | Tsuneishi Shipbuilding (consistency guarantee across split services) |
| C. Legacy/mainframe migration | "The monolith has become a black box and we haven't been able to modernize it in over a decade," "migrating COBOL assets is blocked by data-integration reliability" | ScalarDB's DB-agnostic interface + `--import` (importing existing tables). Copy Book→JSON conversion done jointly with NSW | Tsuneishi Shipbuilding (MVP in roughly 3 months, 70% reduction in implementation effort, MONOist), NSW modernization |
| D. Generative AI / RAG use of internal data | "We want to use scattered data for AI, but connection development and consistency are challenges" | ScalarDB RAG support, vector search (Premium, preview) | LayerX Ai Workforce, Tsuneishi Shipbuilding (data access foundation for AI agents) |
| E. Tamper detection / evidence preservation / audit trail | "We need to keep proving data hasn't been tampered with for 10+ years," "we need an audit trail for regulatory compliance" | ScalarDL (BFT detection, append-only ledger, Ledger+Auditor, tens of thousands of TPS) | Toyota PCE (IP evidence preservation, Azure), Toyota Financial Services proof of concept |
| F. Environmental value / traceability (GX) | "We want to record and track the environmental value of renewable energy in a third-party-verifiable form" | ScalarDL (preserving and linking generation/demand data) | J-POWER environmental value platform (from Jan 2025), corporate PPA proof of concept (Apr 2026) |
| G. Core systems that must withstand demand fluctuation | "We can't predict changes in user volume and want to scale flexibly up and down" | Scalar DLT (ScalarDB+ScalarDL, scales from a minimal configuration) | ENS shared new-power-retailer intake (Sarubobo Coin plan), ENS 30-minute electricity volume data (statutory reporting ~1/5) |
| H. Multi-cloud data management | "We want to manage data across clouds/regions" | ScalarDB (cloud-agnostic), remote replication (preview) | No published case study (be honest if asked for one) |

## 4. Cases to avoid proposing or to flag caution on (constraints from the docs)

Reflect these in the comparison table, risk countermeasures, and speaker notes. Hiding them
will surface during the PoC and cost trust.

ScalarDB:

- **A configuration where the app bypasses ScalarDB and writes to the DB directly is not allowed**
  (it breaks the isolation-level guarantee). If a migration-period design leaves direct writes
  from an existing system in place, flag it as an item requiring further discussion
- Being an abstraction layer, **DB-specific features (e.g., PL/SQL) and the full set of data types cannot be used**
- Core is designed for OLTP (many small reads/writes). **Analytical queries must go through ScalarDB Analytics**
- The underlying DB requires administrator-level privileges (MySQL: CREATE/DROP/ALTER etc., Oracle: ANY-class privileges)
- Environment requirements: JDK LTS (8/11/17/21), Cluster requires Kubernetes 1.32–1.35.
  Db2 for z/OS is unsupported, Spanner only supports the PostgreSQL dialect
- Authentication/authorization is Enterprise; encryption, ABAC, SQL/GraphQL, and vector search are Premium
  (don't write features that aren't in Community into a proposal premised on Community)

ScalarDL:

- It **detects** tampering; it does not **prevent** it (don't overstate this)
- The completeness of detection **depends on operating Ledger and Auditor as 2 independent administrative domains**
- Data operations performed outside the ledger are out of scope (the app must be migrated to go through contracts)
- Internally uses ScalarDB (its DB support and constraints follow ScalarDB's)

## 5. Pricing / editions (as of 2026-08-05)

**Source of record: the OKF bundle (`okf-bundle.md` → `okf/pricing/`).** Read it
before writing any figure — it carries the JPY list prices, the billing model,
the Pod-counting rules, and the edition/feature matrix, none of which are on
scalar-labs.com. The bundle repository is public, so those figures are citable;
label them as 定価 (tax-excluded) and treat them as reference-estimate material,
with the AE reviewing anything that goes to the customer as a quote. What the
bundle marks 非公開 — 3-year terms, prepaid credits, discount rates — stays out.
The table below keeps the **Marketplace** figures, which are the published
per-hour prices for the same products.

| Product | Billing | Notes |
|---|---|---|
| ScalarDB Community | Free (Apache 2.0) | No commercial features |
| ScalarDB Enterprise Standard | AWS $1.40/h, GCP $1.50/h, BYOL ¥100,000/month (excl. tax) | Clustering, authentication/authorization, non-transactional |
| ScalarDB Enterprise Premium | AWS $2.79/h, GCP $2.89/h, BYOL ¥200,000/month (excl. tax) | + SQL/GraphQL, encryption, ABAC/vector search/replication (preview) |
| ScalarDL Ledger / Auditor | $1.40/h each (AWS; Auditor must be purchased together with Ledger), BYOL by individual inquiry | — |

- The unit for hourly billing cannot be confirmed from the Marketplace page (`research-2026-08.md`
  records Pod=2vCPU/4GB. In the deck, keep it to something like "× number of Pods" and don't state a firm amount)
- ScalarDB Analytics is **not** priced per Pod: it is metered per SDBU-hour with a 6 SDBU minimum,
  ¥33.5 / SDBU-hour list (`okf/pricing/scalardb-analytics-pricing.md` — the minimum configuration
  works out to 4,464 SDBU-hours ≈ ¥149,544 / month). scalar-labs.com publishes nothing on this, so
  the bundle is the source. Whether Azure Marketplace offers consumption-based pricing is unknown
  (BYOL container listing and non-availability listing are both present)
- ScalarDL Auditor requires Ledger, in a **separate administrative domain** (separate account /
  cluster) — co-locating them in one cluster does not satisfy the Auditor premise. Quote both
  (`okf/pricing/scalardl-pricing.md`)
- 3-year list prices, prepaid credit prices, and discount rates are 非公開 even inside the bundle.
  Route them to the AE; never interpolate them from the monthly/annual figures
- Always place a `source_note` (AWS Marketplace published value + date) on the estimated cost slide

## 6. Standard initial-proposal environment configuration and BOM

The initial proposal must **always include a system architecture diagram and a configuration
breakdown (BOM)**. The standard is the following 3 environments, with **AWS as the default**
cloud (if specified otherwise, rebuild with the same role split on GCP / Azure. The
validated diagramming style is `references/drawio.md`).

| Environment | Role | Main configuration | Scalar product / quantity (default) |
|---|---|---|---|
| Development (local) | Development and unit-level verification self-contained on each developer's PC | Docker Compose (app + PostgreSQL container) | ScalarDB Core (Community) × number of developers — free |
| Test (aidd-infra-test) | Standing environment for integration testing and automated testing | EKS / NLB / RDS (Single-AZ) / ECR / CloudWatch / S3 | ScalarDB Cluster (Enterprise Standard) × 1 Pod |
| Staging (aidd-infra-staging) | Acceptance and performance verification in a production-equivalent configuration | EKS (2 AZ) / NLB / RDS (Multi-AZ) / Secrets Manager / CloudWatch / S3 | ScalarDB Cluster (Enterprise Standard) × 3 Pods |

- Monthly estimate formula: **$1.40/h (Standard, AWS) × number of Pods × 730h** →
  1 Pod ≈ $1,022/month, 3 Pods ≈ $3,066/month, default configuration total ≈ **$4,088/month**
  (Scalar license only; AWS infrastructure usage fees and the production environment are separate).
  When a proposal includes a feature that requires Premium (SQL/GraphQL, encryption, etc.),
  recalculate using $2.79/h (§5)
- For proposals that include ScalarDL, count Ledger + Auditor ($1.40/h each, Auditor must be
  purchased together) per environment
- Worked example architecture diagram: `examples/scalar-proposal-envs.drawio` (regenerate the
  PNG with `scripts/drawio_export.py`). When rewriting for customer requirements, follow the
  conventions of the `drawio-diagrams` skill
- **Separately from the deck, the post-generation report should also present the list of
  services and the Scalar product/quantity/monthly-cost list** (the builder prints this to
  stdout as `=== Bill of Materials (BOM) ===`)

## 7. Sources

Proposal structure: Sairu proposal template https://sairu.co.jp/method/3543/ /
Sairu internal approval documents https://sairu.co.jp/method/18438/ / Sairu sales material improvement
https://sairu.co.jp/method/5296/ / HubSpot https://blog.hubspot.jp/sales/proposal-formula /
Y's https://ysinc.co.jp/blog/system-proposal-guide/ / BANT
https://cyber-synapse.com/business-knowledge/sales_strategy/how-to-use-bant-for-sales-interview/

Product / constraints: https://scalardb.scalar-labs.com/docs/latest/overview/ /
…/design/ / …/requirements/ / https://scalardl.scalar-labs.com/docs/latest/overview/ /
…/requirements/ / https://www.scalar-labs.com/ja/scalardb / …/ja/scalardl / …/ja/pricing

Case studies: Tsuneishi Shipbuilding https://prtimes.jp/main/html/rd/p/000000071.000037795.html +
https://monoist.itmedia.co.jp/mn/articles/2606/25/news030.html (70% reduction in implementation effort) /
Toyota PCE https://prtimes.jp/main/html/rd/p/000000031.000037795.html /
J-POWER https://www.jpower.co.jp/news_release/2025/01/news250106.html +
https://www.jpower.co.jp/news/2026/04/news260417_1.html /
LayerX https://prtimes.jp/main/html/rd/p/000000376.000036528.html /
ENS https://prtimes.jp/main/html/rd/p/000000006.000037795.html /
NSW https://www.nsw.co.jp/topics/news_detail.html?eid=763
