*[日本語](account-planning-session.ja.md)*

# Account Planning Session Deck Creation Procedure

A procedure for building the deck for an Account Planning Session (APS
below) in the order preparation → workshop → summarization → generation.

## 0. Source and Handling of This Document

- Source material: `FY17_AP_Template_Training_Public.pptx` (Oracle Key
  Account PMO, 2016-06-29, 106 pages).
- Taken from the source material: **the 2-way classification of
  deliverables, the 3-phase flow, the 22 page definitions, how to run the
  workshop, and each page's information sources and considerations**.
- Adapted for Scalar: product names, organization names, the review
  structure, and currency units. See the mapping table in §12.
- Related documents: `skills/scalar-account-planning-session/SKILL.md`
  (how to run the APS), `skills/scalar-account-plan/SKILL.md` (per-customer
  activity plan ledger), `references/scalar/sales-playbook.md` (stage and
  gate definitions), `references/account-planning-template-plan.md` (page
  template implementation plan).

The source material explicitly states that "you don't need to follow the
template format strictly — using it as a reference sample is fine too."
This procedure takes the same stance. **The goal isn't to fill in every
field — an unfilled field is meant to show what you haven't been able to
ask about yet.**

## 1. The First Decision: Which Deliverable Are You Building

The source material treats the Account Plan as two distinct deliverables.
Unless you settle this distinction first, neither the page count nor the
density can be decided.

| | **Plan Document** (for the account team) | **Session Materials** (for review) |
|---|---|---|
| Purpose | Strategic plan for upstream engagement | Decision-making in a 30-minute review |
| Audience | Account team, Sales VP, Executive Sponsor | Review conductors (executives) |
| Page count | No constraint. Can exceed 100 pages with legacy assets | **Single-digit pages + Appendix** |
| Updates | Major revision at offsites/APS, minor updates as needed afterward | Created/revised at every APS |
| Density | Written to stand on its own as a document | One message per page |

This procedure **builds both in a single pipeline**. Phases A–C assemble
the Plan Document, and the Session Materials are extracted from it (§7).

## 2. Overall Flow

```
  [事前準備]                    [ワークショップ]           [ワークショップ後]
       │                              │                          │
┌──────▼───────────────┐  ┌───────────▼──────────┐  ┌────────────▼──────────┐
│ Phase A               │  │ Phase B              │  │ Phase C               │
│ 顧客のビジネス状況と  │─▶│ 共通の価値に基づく    │─▶│ 優先順位／数値目標／  │
│ 自社ポジションの理解  │  │ イニシアチブの連携    │  │ 実行アプローチの確認  │
└───────────────────────┘  └──────────────────────┘  └───────────────────────┘
 Corporate Overview          Strategy Map (Step 2)      Prioritization
 SWOT Analysis               Blueprint Map              3 Year Execution Plan
 Strategy Map (Step 1)       Blueprint Summary          Action Plan
 Historical Spend                                       Exec Engagement Plan
 Heatmap                                                Event Plan
 TAM & SOW Analysis                                     Flight Plan
 Influence Map                                          3 Year Projections
 Account Health
 Vision/Strategy for Growth
       │                              │                          │
       └──────────────────────────────┴──────────────────────────┘
                                      │
                        ┌─────────────▼──────────────┐
                        │ Executive Summary          │
                        │ 3 Year Strategy Summary    │
                        │ Management Asks            │
                        │ Challenges & Risk          │
                        └────────────────────────────┘
```

Who produces the material differs by phase. Get this wrong and the
workshop turns into a document-drafting session.

| Phase | Who produces it | When |
|---|---|---|
| A | Prepared in advance by the AE / SC | D-14 to D-3 |
| B | Workshop format with the whole account team | Day of, morning through afternoon |
| C | AE formalizes the workshop's conclusions | Day of (afternoon) to D+3 |
| Exec Summary | AE (by the day before the review) | D+3 to D+7 |

## 3. Step 1 — Preparation (D-14 to D-7)

### 3.1 Confirm the Target and the Team

- The target account and its scope (the entire group, or a specific
  operating company/business unit).
- Participants: AE, SC, partner contacts as needed, and executives (opening
  only).
- Schedule: the source material's standard is **a single day from
  9:00–15:00** (§5.1). If compressing to half a day, secure 90 minutes for
  the Phase B brainstorm and push Phase C to a later date.
- State the goal explicitly: what should be decided by the end of this
  session (e.g., the priority order of Blueprint themes and the next 90
  days of actions).

### 3.2 Inventory Existing Assets

Before creating anything new, look for what already exists internally. The
source material also states that "this is usually found in materials from
past APS, WPS, offsites, etc., so use that as the base."

- Past Account Plans / WPS / proposals / offsite materials
- `accounts/<customer>/account.json` (activity ledger) and generated
  Markdown
- Recent meeting minutes, visit records, and email threads

### 3.3 Gather Information Sources

| Information source | Pages it mainly feeds |
|---|---|
| Securities reports, earnings materials, annual reports | Corporate Overview, SWOT |
| Mid-term management plan | Strategy Map (Step 1), Corporate Overview |
| Customer website, press releases | Corporate Overview, Strategy Map |
| Newspaper/magazine articles, analyst commentary | SWOT, Strategy Map |
| Inquiries to internal product owners / SCs | Heatmap, TAM & SOW |
| Visit records, meeting minutes, business cards | Influence Map, Account Health |
| Past deal history | Historical Spend |

### 3.4 Pre-Distribution (D-3)

- Distribute the full set of Phase A materials to participants.
- Decide and share the day's flow, agenda, and role assignments in
  advance.
- Homework for participants: read the distributed materials / research
  domestic and international examples in the same industry / review who
  they've met with on past customer visits and the corresponding minutes.

## 4. Step 2 — Phase A: Build the Preparation Materials

The purpose, information sources, and common pitfalls for each page.
Template IDs are those defined in
`references/account-planning-template-plan.md`.

### 4.1 Corporate Overview

In addition to a profile of the target company's main businesses,
revenue/profit trends, headcount, and so on, describe **management-level
challenges, future strategy, and statements from executives**. The
management vision / goals / strategy / challenges / initiatives organized
here become the input to the Strategy Map.

- Judgment criterion: a state where only the profile fields are filled in
  is incomplete. If you can't cite even one statement from an executive,
  your information gathering isn't sufficient.

### 4.2 SWOT Analysis

Organize the business environment by splitting it into internal factors
(strengths/weaknesses) and external factors (opportunities/threats).

- Examples of internal factors: product/technical/development capability;
  brand, customer base, regional footprint; management efficiency (cost,
  SCM, speed); organization, talent, sales capability.
- Examples of external factors: economic conditions, exchange rates,
  regulatory trends; competitors and substitutes; changes in market needs;
  business-model change driven by technological innovation.
- Judgment criterion: don't write an opportunity for your own company into
  the "opportunity for the customer" field.

### 4.3 Strategy Map (Step 1 — Through Customer Analysis)

Show the customer's Goal (what the management level requires) / Strategy
(what executives require) / Tactic (what management-level staff require)
as a hierarchy, and, as needed, add the management vision at the top and
an Objective layer below it. For important accounts, **break it down all
the way to initiatives**.

- Attach "whose requirement" (Board / CEO / COO / CFO / CIO …) to each
  item.
- Assumption-based / hypothesis-based items may be included, but
  distinguish their confidence level as described in §11.
- Include initiatives from overseas locations too.
- Initiatives should ideally be large ones aimed at Transformation /
  Innovation, not departmental-optimization improvements.

### 4.4 Historical Spend

Show the past 3 years of results by product. Don't add subscription /
annual-billing figures together with one-time revenue — tally them
separately.

### 4.5 Heatmap

Summarize adoption status (footprint) by layer and by system, near-term
plans, and the areas targeted over the next 3 years. Contrast current
state → 3-year potential with an arrow, and note in each row **which
initiative it ties to** and the competitive situation.

- Three-value rating: company-wide standard / has a foothold and growing /
  almost no penetration.
- Confirm the latest status with internal product owners / SCs and reflect
  it.

### 4.6 TAM & SOW Analysis

Show the customer's TAM (the addressable market size for us) and SOW
(share of wallet) baseline and target as a graph. If the actual TAM
becomes known — e.g., through a disclosure of the customer's IT budget —
that figure may replace the estimate. The baseline is the 3-year average
immediately preceding the 3-year plan; the target is the average over the
3 plan years.

### 4.7 Influence Map

Map the stakeholders across LOB and IT, centered on the Executives
involved in decision-making for the target initiative.

- Always include the business side, not just the IT department.
- Make the decision-making authority, path, role, and Inner Circle
  explicit.
- For important accounts, also list overseas stakeholders.
- The existing `b2b-sales/influence-map` / `influence-map-org` can be used
  as-is.

### 4.8 Account Health

Rate the account's health across 4 dimensions × 5 metrics each, and show
the overall score as a quarterly trend.

| Dimension | Metrics |
|---|---|
| Account Team Effectiveness | Account strategy / lead / Exec Sponsor / support owner / advisor |
| Relationship Quality | Executive Engagement / customer satisfaction / breadth of relationship / partners / participation in customer programs |
| Product Adoption | Footprint / architecture / roadmap / license consumption / number of Blueprints |
| Revenue Performance | SOW / license results / services results / pipeline / revenue |

- Rate each metric on a 3-point scale (needs improvement / standard /
  excellent), with the rating criteria on a separate page.
- Judgment criterion: a rating where everything lines up as "standard"
  isn't really a rating.

### 4.9 Vision/Strategy for Growth

Concisely present the 3-year growth vision and strategy for this account.
Based on an analysis of the customer's management priorities and our
position, show how to deepen the relationship, which business areas to
move into, and which product stack to expand. If an approach to defend an
existing deployment against competitors is needed, touch on that too.

The source material's 4-area structure:

1. Alignment with the customer's transformative business goals (maturity
   and elapsed time of key initiatives)
2. Positioning of our GTM focus areas (additional areas to target)
3. Footprint expansion (into other business units / business processes /
   layers of the stack)
4. Executive Engagement points (executive-to-executive meetings held, next
   ones planned)

## 5. Step 3 — Phase B: The Workshop

### 5.1 Agenda (source material's example, one-day session)

| Time | Duration | Content |
|---|---|---|
| 9:00–9:10 | 10 min | Opening (executive remarks, confirm purpose and outputs) |
| 9:10–9:20 | 10 min | Message from the account owner |
| 9:20–10:20 | 60 min | Review the account situation and present the current Plan |
| 10:20–10:30 | 10 min | Break |
| 10:30–12:00 | 90 min | Map solutions and potential based on the customer's challenges, strategic vision, and CSFs (surface candidate Blueprint themes). Split into teams by product area |
| 12:00–13:00 | 60 min | Lunch |
| 13:00–14:00 | 60 min | Assess potential and prioritize candidate themes |
| 14:00–14:45 | 45 min | Draft the execution plan |
| 14:45–15:00 | 15 min | Closing |

### 5.2 How to Run It

- Run the 10:30 slot as a brainstorm using sticky notes (Post-its).
  Cleaning it up into final form happens in a later step.
- Each product owner surfaces the value they can deliver, both standalone
  and in combination with other products. Value types: value competitors
  can't match / reduced cost to realize / reduced TCO / shorter time to
  realize / avoided realization risk.
- Prioritize solutions that span multiple product areas and can make a
  strong value case.

### 5.3 Output 1: Strategy Map (Step 2 — Mapping Blueprint Themes)

On top of the Strategy Map built in Phase A, map the themes considered
proposable through an upstream approach. **This is the single most
important process in Account Planning.** Surface, among the customer's
Innovation / Transformation initiatives, the areas where our stack can
deliver value.

Putting the analysis-use Strategy Map directly into the report material
often makes it unreadable. For reporting, reformat it into a separate
format (Customer Initiative Alignment) that lines up "customer initiative
× proposed theme × value delivered × product."

### 5.4 Output 2: Blueprint Map

List the mapped themes in a table with one theme per row. Columns follow
the source material:

| Blueprint name | Customer challenge | Proposed solution | Product | Why us (customer value / advantage) | Timing | Amount |

- Write it so that our value is positioned as the solution to the
  customer's business challenge.
- A row that's "just a product name" is a sign the challenge hasn't been
  identified.

### 5.5 Output 3: Blueprint Summary

Detail important themes one theme per page. Fields follow the source
material: customer transformation challenge / solution overview / product
& key initiative / our differentiator / benefit and driver / internal
roles involved / partner / reference case / start date & expected close
date / business sponsor / IT sponsor / target business unit / current
pipeline amount / 3-year potential / deal ID / competitors / related
community.

- "Close" here means **agreement on the Blueprint (proposed theme), not
  winning the deal**. Don't conflate the two.
- As the theme progresses through the stages hypothesis-based → presented
  to customer → joint study, increase the precision of the description.

## 6. Step 4 — Phase C: Priorities and Execution Plan

### 6.1 Prioritization

Rate each initiative on "value to the customer" and "our position," map
them, and prioritize.

- Customer-value axis: strategic fit, economic benefit, intangible
  benefit.
- Our-position axis: footprint potential, customer relationship, partner
  support.
- In the table, line up per initiative: purpose & expected value /
  decision-making stage / key people (sponsor, influencer, decision-maker)
  / our alignment status and track record / 3-year potential / the
  customer's priority.
- Having **both** the 2-axis map and the score table speeds up the
  discussion (with only one, you can't explain "why that position").

### 6.2 3 Year Execution Plan

Diagram the 3-year execution plan per theme/project using key milestones.
Milestone types: event, executive visit, insight delivery, joint study,
roadmap development, deal close. Important themes may be detailed one
theme per page.

### 6.3 Action Plan

For each theme/project, write out the concrete actions to drive it forward
in chronological order. Columns are: assigned date / action / owner / due
date / outcome.

**Must satisfy S.M.A.R.T.**: Specific, Measurable, Attainable, Realistic,
Time-bound.

- The existing `scalar-ae/action-plan` can be used as-is.
- "Consider XX" is not an outcome. Write who's what changes and how.

### 6.4 Executive Engagement Plan

List the engagement plan with customer executives. Columns are: level /
customer-side executive / our-side executive / frequency & date / current
state and goal.

- For recurring engagements, state the frequency; for one-off engagements,
  state the planned timing.
- One per account is enough (no need to make one per theme). Only large
  deals get their own separate one.

### 6.5 Event Plan

Summarize which events (our conferences, private customer events,
executive visits, etc.) are used as an occasion to reach which
executives/key people and to obtain what outcome. Columns are: event /
timing / target customer / our speaker/key person / desired outcome.

### 6.6 Flight Plan

Visualize 3 years of activity on a single page. Represent each theme from
the Blueprint Map as a bubble, with the theme name and amount written
inside it. Close timing on the horizontal axis, amount on the vertical
axis, and color for status (theme approved / turned into a deal / newly
emerged).

### 6.7 3 Year Financial Potential / Projections

Set 3 years of revenue potential, broken out by theme-derived and
regular-pipeline-derived. Don't add subscription annualized values
together with one-time revenue — show the total separately.

## 7. Step 5 — Building the Executive Summary (Session Materials)

Distill the outputs of Phases A–C down to **single-digit pages +
Appendix** for the 30-minute review.

Recommended structure (9 pages):

| # | Page | Source |
|---|---|---|
| 1 | Cover (account name / fiscal year / author / date) | — |
| 2 | Three Year Account Strategy Summary | §7.1 |
| 3 | Customer's management strategy and initiatives (for Strategy Map reporting) | §5.3 |
| 4 | Initiative Alignment (initiatives × proposed themes × products) | §5.3 |
| 5 | Blueprint Map (theme list with amount & timing) | §5.4 |
| 6 | Prioritization (2-axis map) | §6.1 |
| 7 | 3 Year Execution Plan / Flight Plan | §6.2 / §6.6 |
| 8 | Action Plan (next 90 days) | §6.3 |
| 9 | Management Asks | §7.2 |

Move the Phase A analysis (Corporate Overview, SWOT, Heatmap, TAM & SOW,
Influence Map, Account Health) and the Blueprint Summary to the Appendix.

### 7.1 Three Year Account Strategy Summary

Summarize the entire 3-year plan on a single page. Place the 3-year
strategy statement (1–2 sentences) in the center, and line up "current
state" on the left and "3-year target" on the right, using the same set of
items.

Items: revenue (SOW %, current-period results) / customer satisfaction
(loyalty metrics, overall satisfaction, willingness to recommend) /
customer engagement (executive sponsorship, accessible levels, whether
there's a joint plan) / footprint strength. List the key transformation
themes at the top.

- **If the items on the left and right don't correspond, it isn't a
  comparison.** Any item written under "current state" must appear under
  "3 years out" in the same order.

### 7.2 Management Asks

Write the items that are difficult for the account team alone to resolve
while advancing the 3-year plan and that need executive support. Cover
both internal and external asks.

- From whom, and what support is needed
- Why it's needed
- The concrete result/outcome expected from it

"I want resources" by itself isn't an Ask. Only writing the expected
outcome as well makes it something that can be judged.

### 7.3 Account Challenges & Risk Mitigation

Columns are: challenge / impact / mitigation / owner. This pairs with
Management Asks. For risks that don't lead to an Ask, write who does what
by when in the mitigation field.

## 8. Step 6 — Generation in slide-forge

`scripts/scalar/build_account_planning.py` produces two deck specs from
the ledger. The Plan Document and the APS review deck (9 main pages +
Appendix) share the same page definitions, so **fixing one reflects in
both**. The page count isn't fixed — it changes with the number of `deals`
and with `meta.dealExtraPages` / `meta.skipPages` (§9).

**The input is `accounts/<AE>/<customer>/aps.json`.** The script only
holds the figure types, coordinates, and formatting (`LAYOUT`); every
string is read from aps.json. Neither the customer name nor any real name
is written into the script.

`aps.json` structure:

```jsonc
{
  "meta":     { "title": …, "subtitle": …, "planTitle": …, "reviewTitle": …,
                "dealExtraPages":  { "<商談 id>": ["objective-ledger", …] },  // 任意
                "reviewDealPages": ["deal-1", …],                             // 任意
                "skipPages":       ["card-orgchart", …] },                    // 任意
  "sections": { "A": {"title":…, "body":…}, "B": …, "C": …, "E": …, "APX": … },
  "deals":    [ { "id":"1", "company":…, "name":…, "initiative":…,
                  "challenge":…, "solution":…, "diff":…,
                  "people":…, "itsub":…, "deal":…,
                  "amount":…, "period":…, "stage":… } ],
  "dealSource": "商談カード共通の出典行",
  "pages":    { "<ページ id>": { "title":…, "lead":…, "source":…,
                                 "figures": [ {内容だけ}, … ] } }
}
```

`pages.<id>.figures` corresponds 1:1 with the sequence of figures in
`LAYOUT[<id>]` (`governing_message` / `lead_in` / `source_note` are taken
from `title` / `lead` / `source`, so they aren't listed in figures). If the
count doesn't match, it's an error at assembly time.

- `deals[].id` must be written as a **string** (a number is an error).
  Deal numbers are displayed as circled digits ①–⑳, and beyond that as
  `(21)`. Either `amount` or `period` may be empty (no stray separator
  character is left behind).
- `meta.dealExtraPages` (optional): deal ID → list of page IDs to add to
  that deal's chapter (e.g., `objective-ledger`). Which deal gets which
  appendix is a per-customer judgment call, so aps.json holds it.
- `meta.reviewDealPages` (optional): list of page IDs (`deal-<deal
  number>` or a deal appendix page) to expand into the deal slot of the
  executive review Appendix (`REVIEW_APPENDIX`'s `"@deal-pages"`). Which
  deals make it into the executive review is also held in aps.json.
- `meta.skipPages` (optional): drop pages that don't fit the customer from
  the deck. As a plain list, it drops from **both** decks; as `{"plan":
  […], "review": […]}`, it drops only from the specified deck. An unknown
  page ID or deck name is an error at assembly time. `deal-<deal number>`
  also works on deal chapters — if a chapter's contents are entirely
  skipped, the section divider disappears with it. For pages skipped in
  both decks, the data may be removed from `pages`.

```bash
# 1. aps.json から 2 本の仕様を組む
.venv/bin/python scripts/scalar/build_account_planning.py \
  --aps "accounts/<AE>/<顧客>/aps.json" \
  --out "out/account-plan/<顧客>/ap"
#    -> plan.json / review.json

# 2. オフライン検証（API を叩く前に必ず通す）
for f in plan review; do
  .venv/bin/python scripts/build_deck.py --template templates/scalar-2026.json \
    --spec "out/account-plan/<顧客>/ap/$f.json" --dry-run --strict || break
done

# 3. 生成（初回）。既存デッキの更新は 4 へ
.venv/bin/python scripts/build_deck.py \
  --template templates/scalar-2026.json --spec "out/account-plan/<顧客>/ap/plan.json" \
  --title "<顧客> Account Planning Session FY26" --folder <Drive フォルダ ID>

# 4. 既存デッキを同じ URL で更新する（スナップショットが先）
.venv/bin/python scripts/snapshot_version.py <デッキ URL>
.venv/bin/python scripts/build_deck.py \
  --template templates/scalar-2026.json --spec "out/account-plan/<顧客>/ap/plan.json" \
  --into <デッキ URL>

# 5. サムネイルでのビジュアル QA → 修正 → 再生成（skills/slide-qa/SKILL.md）
# 6. QA 用ファイルの後始末
.venv/bin/python scripts/cleanup_qa.py
```

To swap the master, **just change `--template`** (`corporate`,
`aixdevops`, `blank-16x9`, etc.). The page definitions themselves don't
change. The condition that makes this hold is defined in
`references/account-planning-template-plan.md` §2.

> **There's one constraint that the API rejects even when `--dry-run`
> passes.** The Slides API rejects table columns narrower than 32pt
> (0.444in). `build_account_planning.py`'s `_check_columns()` checks for
> this at assembly time. When adding a narrow column like a deal number,
> make sure it's at least 0.45in.

> When updating an existing deck, always take a snapshot with
> `scripts/snapshot_version.py` before pointing `--into` at the existing
> deck. Never make the master template itself the target of `--into`.

## 9. Page List (Master Table)

A list of the Plan Document's 43 body pages (`PLAN_A` 28 / `PLAN_B` 4 /
`PLAN_C` 7 / `PLAN_E` 4). The full deck also adds a cover, 4 chapter
dividers, and a chapter per deal (§9.3 — a divider + 1 overview page per
deal, plus `meta.dealExtraPages` pages if any), so **the page count
changes with the number of `deals` and with `meta.skipPages`**.

The APS review deck is: cover + 9 main pages (○ in the "Review" column =
`REVIEW_MAIN`) + Appendix (divider + 22 "Appendix" pages + the deal pages
from `meta.reviewDealPages`; 3c appears in both the main body and the
Appendix).

**Tables are kept only for "ledgers" and "rating criteria"; everything
else is shown as a diagram** (§9.4). The body of each deal's chapter
(divider and overview) isn't included in the table below. 19 and 20 are
pages added as a deal chapter's appendix via `meta.dealExtraPages`
(`blueprint-ledger` / `blueprint-aidd`, `objective-ledger` /
`objective-aidd` in `LAYOUT`), and they appear in the executive review
only when listed in `meta.reviewDealPages`.

| # | Page | Form | Phase | Review | Source |
|---|---|---|---|---|---|
| 1 | Group structure and our touchpoints | orgchart | A | Appendix | S80 |
| 2a | Operating company org structure and our touchpoints (one page per legal entity) | orgchart | A | Appendix | S84 |
| 2b | IT subsidiary org structure and our touchpoints | orgchart | A | Appendix | S84 |
| 2c | IT subsidiary ↔ each company's ownership mapping | comparison | A | Appendix | S84 |
| 2d | Deal portfolio by group company | mece_tree | A | ○ | S45 |
| 2e | Stakeholders by group company | comparison | A | Appendix | S27 |
| 3 | Financial Trends | metric + hbars | A | Appendix | S81 |
| 3b | Structure of the mid-term management plan | mece_tree | A | Appendix | S15 |
| 3c | Linking the mid-term plan to the proposal | mece_tree | A | ○ + Appendix | S43 / S46 |
| 4 | SWOT Analysis | matrix | A | Appendix | S13 |
| 5 | Strategy Map (Step 1) | outcome_tree | A | — | S15 |
| 6 | Strategy Map (Step 2) | outcome_tree | A/B | — | S38 / S41 |
| 6b | Executive layer and contact status by legal entity | comparison | A | Appendix | S27 |
| 6c | People to meet and leads | Table | A | Appendix | S27 |
| 7 | Customer Business Initiatives | cards | A | Appendix | S44 |
| 8 | Customer Programs / Projects | gantt | A | Appendix | S45 |
| 9 | Historical Spend | hbars | A | — | S18 |
| 10 | Scalar Footprint | layers + cards | A | Appendix | S84 |
| 11 | Heatmap | layers | A | Appendix | S23 / S26 |
| 12 | TAM & SOW Analysis | nested_circles | A | — | S21 / S22 |
| 13 | Influence Map | influence_graph | A | Appendix | S27 |
| 13b | Key people's backgrounds | cards | A | Appendix | S27 |
| 13c | Relationships between people | influence_graph + links | A | Appendix | S27 |
| 14 | Account Health | rating_matrix | A | Appendix | S29 |
| 15 | Account Health rating criteria | Table | A | — | S31 / S32 |
| 16 | Vision / Strategy for Growth | comparison | A | — | S33 |
| 17 | Initiative Alignment | mece_tree | B | — | S43 / S46 |
| 18 | Blueprint Map | Table | B | ○ | S49 |
| 19 | Blueprint Summary (per theme) | cards ×2 rows | B | depends on reviewDealPages | S51 |
| 20 | Objective (per theme) | cards + journey | B | depends on reviewDealPages | S60 / S99 |
| 21 | Prioritization (score) | Table | C | — | S55 |
| 22 | Prioritization (2-axis) | posmap | C | ○ | S56 |
| 23 | 3 Year Execution Plan | gantt | C | ○ | S57 |
| 24 | Engagement Timeline (8 weeks) | gantt | C | — | S59 / S98 |
| 25 | Action Plan | Table | C | ○ | S61 / S62 |
| 26 | Executive Engagement Plan | orgchart | C | — | S63 |
| 27 | Event Plan | timeline | C | — | S65 |
| 28 | Flight Plan | posmap | C | — | S70 |
| 29 | 3 Year Projections | Table | C | — | S67 |
| 30 | 3 Year Account Strategy Summary | exec_summary + before_after | Exec | ○ | S73 |
| 31 | Management Asks | Table | Exec | ○ | S75 |
| 32 | Challenge & Requirement | Table | Exec | ○ | S77 / S105 |
| 33 | Challenges & Risk Mitigation | Table | Exec | Appendix | S86 |

### 9.1 Cross-Referencing by Deal Number

Assign a number to each deal, and **reference the same number** across
Heatmap, Customer Business Initiatives, Blueprint Map, Prioritization, and
Action Plan. Without numbering, each page becomes an isolated table and
can no longer be tracked as a bundle.

**Assign numbers in group-company order.** Deals from the same company end
up adjacent, so when discussing a given company you don't need to hunt
across pages to re-collect them.

The number, company, owning organization, and amount are centrally
managed in aps.json's `deals` array, and every page and every deal chapter
pulls from it (the script holds no strings — §8).

### 9.1.1 Linking to the Mid-Term Management Plan

The mid-term plan is the customer's own published priorities. **If the
proposal can be connected to its wording, the language written in the
internal approval (ringi) becomes the customer's own language.**

- Take the **original text** from primary sources (the mid-term plan's
  release PDF, IR page). Don't substitute a summary article.
- **Look at the pillar structure.** Whether IT sits under the business
  strategy or alongside it changes the internal-approval route.
- Do the linking at the **level of individual statements**, not pillars.
- Don't force a link for a proposal that doesn't connect. The absence of a
  link is itself useful information.

### 9.2 Classification by Group Company

When the counterpart is a corporate group rather than a single parent
company, **classify both deals and stakeholders by company.** Different
companies have different decision-makers and budgets, so lumping them
together makes it impossible to settle on a course of action.

The 3 required pages:

| Page | Figure | What it shows |
|---|---|---|
| Deal portfolio by group company | `mece_tree` | How many deals, and worth how much, at each company |
| Stakeholders by group company | `comparison` | Who's secured, and who's still just a business card, per company |
| IT subsidiary ↔ each company's ownership mapping | `comparison` | The distinction between cross-cutting organizations and per-company implementation teams |

**The IT subsidiary touches every company, so always treat it as a
separate item.** In a group with multiple operating companies, the IT
subsidiary's departments are often split per company, while it also tends
to have cross-cutting organizations such as technology oversight or AI
promotion. Even if you've secured the cross-cutting organization, the deal
won't move unless you've also gotten into the per-company implementation
team. **Include a page that re-reads the official org chart per company so
this distinction is visible.**

### 9.2.1 Finding Who You Should Meet

The account plan isn't just a record of who you've met — it's also **a
mechanism for surfacing who to meet next**. Looking only at the ledger
only turns up people around whoever you've already met.

**Gather the executive roster per legal entity.** In a group, the holding
company, the operating companies, and the IT subsidiary each publish their
own executives as separate legal entities. Lumping them together makes it
impossible to tell which legal entity the executive who owns
implementation belongs to.

0. **Draw one org chart per legal entity.** Consolidating the whole group
   onto one page collapses the department level, so you can't see which
   departments you haven't gotten into.
1. Take the public executive roster per legal entity and overlay our
   contact status.
2. **Pick up concurrent roles.** A holding company CxO may also serve as a
   director at a subsidiary, and that can be the shortest path to an
   introduction.
3. Cross-reference the org chart (which departments exist) with the
   executive roster (who the executives are). **The link between
   department and executive often can't be filled in from public
   information — that's what needs to be confirmed.**
4. **Anchor leads on people you've already contacted.** A "person to meet"
   for whom you can't write "via whom" isn't an actionable item.
5. Treat the public roster as authoritative for titles, and correct any
   stale titles in the ledger.
6. **Once you've decided who to meet, capture their background.** The
   progression of their titles shows what they base their judgment on.
   Predecessor, successor, concurrent roles, and secondment origin are the
   decision-making path itself.
7. **Personal relationships (former boss, friend, faction) are not public
   information.** Separate them with a source line, and don't let
   materials containing such notes go outside the company.

### 9.3 Structuring a Chapter per Deal

Deal details aren't mixed into the overall analysis — **cut a separate
chapter per deal**. Each chapter is:

1. Divider (company name / deal name / amount, timing, stage)
2. Deal overview (6 `cards`: customer challenge / our solution /
   differentiator / customer-side key person / **the IT subsidiary's
   owning organization** / amount, timing, stage)
3. Objective (main deals only; `cards` + `journey`)

Keep the same shape for the chapter contents across every deal. With the
same shape, you can compare "what's still unfilled" across chapters.

### 9.4 Where Tables Are Allowed

A run of tables makes every page look the same and obscures where the
point is. Limit tables to the following 2 cases; make everything else a
diagram.

- **Ledger**: something with an owner and a due date per row that gets
  tracked afterward (Blueprint Map / Action Plan / Management Asks /
  Challenge & Requirement / Risk / Prioritization score / Projections)
- **Rating criteria**: something whose content is the definition of the
  levels itself (Account Health rating criteria)

Guide for what to replace:

| What tends to become a table | Diagram to use |
|---|---|
| Hierarchy, affiliation, reporting line | `orgchart` |
| Connection between top-level goals and downstream initiatives | `outcome_tree` / `mece_tree` |
| State per layer | `layers` |
| Groups of projects with timing | `gantt` / `timeline` |
| Nested magnitudes (market size) | `nested_circles` |
| Comparison of amounts / counts | `hbars` / `vbars` |
| A handful of items explained side by side | `cards` |
| Milestones per fiscal year | `journey` |
| Current vs. target contrast | `before_after` |
| Stakeholders' position and influence | `influence_graph` / `posmap` |

### 9.5 The Customer's 4 Layers

Always place the **customer's program / project layer** between the
initiative and the theme. Skip this and real project names stop
corresponding to proposed themes.

```
顧客イニシアチブ（§9.1 の番号）
  └ 顧客プログラム / プロジェクト（実在する名前で書く）
      └ 提案テーマ（Blueprint）
          └ 案件
```

## 10. Ongoing Update Operations

- Immediately after the Session, reflect what was decided into
  `accounts/<customer>/account.json`. The ledger is the source of truth,
  not the slides.
- Keep the Action Plan filled with the next 90 days at all times. For rows
  past their due date, resolve them as done / not done / canceled before
  removing them.
- As a Blueprint's stage advances, increase the precision of the Blueprint
  Summary's description.
- Don't change the deck's URL. Keep the same link always pointing to the
  latest version.

## 11. Quality Checklist

Before shipping the Session materials.

- [ ] Is it one message per page? Is the title the conclusion?
- [ ] Can facts based on the customer's statements/documents be
      distinguished from our own hypotheses? Are hypotheses explicitly
      labeled as hypotheses?
- [ ] Are the Strategy Map's initiatives tied to the customer's public
      information or the customer's own statements?
- [ ] Is the customer challenge identified for every row of the Blueprint
      Map (no row that's just a product name)?
- [ ] Does the Prioritization's positioning have a corresponding basis
      (the score table)?
- [ ] Does every row of the Action Plan satisfy S.M.A.R.T.? Are owner and
      due date never blank?
- [ ] Is the expected outcome written for the Management Asks?
- [ ] Do the Strategy Summary's "current state" and "3 years out"
      correspond under the same set of items?
- [ ] Are the amount's unit, period, and FX assumption stated explicitly?
- [ ] Has internal-only information (assessments of an individual's
      influence, internal politics, for/against positions) leaked into
      the customer-shared version?
- [ ] Has it passed visual QA via thumbnails (text overflow, overlap,
      contrast)?

## 12. Terminology Mapping from the Source Material

| Source material (Oracle) | Handling in this procedure |
|---|---|
| KAD (Key Account Director) | Account owner / AE |
| GCA / EA | SC / solution architect |
| APS (Account Planning Session) | Unchanged. The planning session that includes an executive review |
| APWS (Account Planning Workshop) | The workshop in §5 |
| Blueprint | An upstream proposed theme. A hypothesis that precedes a deal |
| Blueprint's Close | Agreement on the theme (not winning the deal) |
| Pillar (Tech / Apps, etc.) | Product area |
| Sales Play | Key initiative |
| CVC (Customer Visit Center) | HQ visit / executive visit |
| OOW / Insight | Our conference / insight-delivery activities |
| ULA / ELA Utilization | License contract consumption status |
| SOW (Share of Wallet) | Our share within the customer's IT spend |
| ARR booking | Annualized new contract value |
| InfoMentis / Oracle Sales Methodology | `references/scalar/sales-playbook.md` |
