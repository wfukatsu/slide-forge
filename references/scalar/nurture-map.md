*[日本語](nurture-map.ja.md)*

# Nurture process map

Source: the Google Sheet 「ナーチャリング・プラン・シート」
(`1tCpX_dCkr5G9yngl5WB70v-D571GwxWVwotI2co2ho8`, created 2021-11-04, last modified
2024-06-14).

**Freshness warning** — the content was written in 2021 and has barely been updated
since. The product positioning (the ScalarDB problem list, the target segments) is
from then, and **does not include today's main ground: ScalarDB Cluster, ScalarDB
Analytics, transactions across heterogeneous RDBs.** Apply the same **three-month
rule** as `research-2026-08.md`: re-check the positioning and the segments before
relying on them. The stage model (§1–§2) and the sheet's structure (§6) age slowly.

| Concern | Source |
|---|---|
| Stages and gates once a deal exists | [`sales-playbook.md`](sales-playbook.md) / [`stage-io-map.md`](stage-io-map.md) |
| The buyer's state **before** a deal exists, and what content to send | **This document** |
| Problem-to-product mapping and the proposal format | [`proposal-map.md`](proposal-map.md) |

---

## 1. The five nurture stages

The sheet's axis is "Outside-In: What are customers looking for?" — stages are cut
by **what the buyer is looking for, not by what the seller does**.

| | 0. Education | 1. Need | 2. Research | 3. Evaluation | 4. Selection |
|---|---|---|---|---|---|
| **Nurture type** | Pre-MQL → MQL | Pre-MQL → MQL | MQL → SQO / Trials | MQL → SQO / Trials | MQL → SQO / Trials |
| | Re-engagement | Re-engagement | Re-engagement | Re-engagement | Re-engagement |
| **Buyer situation** | Does not feel there is anything to improve when building or replacing a system; the build/replace date is far enough away that they have not thought about it; has no concrete idea yet | Knows what the problem is; no concrete project has started; has not narrowed down which problem to solve | Looking for products and solutions that address the problem | Narrowing down the products and solutions that fit | Deciding to buy |
| **Scalar's goals** | Make the case for what should be fixed at build/replace time, and the business benefit of fixing it | Identify which problem they want to solve | Propose a concrete solution and product for that problem | Make the case for our advantage over competitors | Earn the overall trust the purchase decision needs |
| **Assets / content** | Improvement, benefit and message; product intro; use cases (extract); case studies (extract) | Same | Use cases (detail); case studies (detail) | White paper (technical); product explainer; demo and sample code | ROI / quote tooling; case studies; ROI-bearing use cases; project templates |
| **Question** | Why change? | How change / why now? | How change / why now? | Why us? | Why us? |
| **Funnel** | Awareness / education | Consideration → preference | Consideration → preference | Selection → purchase | Selection → purchase |

### How to read it

- **Stages 0 and 1 carry the buyer from "why change" to "how change / why now"** —
  they are not where you sell the product. Loading them with product detail hands
  HOW to someone who has not accepted the WHAT (playbook §1, principle 2).
- **Re-engagement runs alongside every stage.** Which stage a stalled lead returns
  to is decided by their buyer situation at that moment. Going backwards is not a
  failure.
- Content is shared across 0–1 (extracts), goes to detail at 2, technical proof at
  3, and money at 4. **Do not reuse one deck across all five.**

### Channels and how each is used (not in the sheet; added here)

The sheet carries only *what* to send (Assets / Content) — never **where, or at what
interval**. Five channels are in scope.

| Channel | Mode | Stages it serves | How cadence works | Legal note |
|---|---|---|---|---|
| Email (MA tool) | Push | 0–4 (all) | Designed as an **interval**; the defaults are monthly at stages 0–1, fortnightly at 2, weekly at 3–4 (tightening as the stage rises) | §8 consent, opt-out and disclosure are **mandatory** |
| Webinars and seminars | Event | 1–3 | Designed around **dates**; the invitation rides on the email channel | Co-hosted lists are third-party provision (§8) |
| Owned media and the engineering blog | Pull (search) | 0–3 | Not an interval — **publish and wait**. What you design is the CTA and the route to the next stage | Not a transmission, so outside §8 |
| Community, social and partner referral | Trigger | 1–4 | Not an interval — designed around a **firing condition** (a question appears, a partner raises a case) | Close to 1:1; partner lists fall under §8 |
| Marketing events and speaking slots | Event | 0–2 | Designed around **when a slot is secured**. Few in number, and heavy as a stage-0 reach channel | Business-card handling per §8 |

**Only email is designed as an interval.** The rest are event dates, firing conditions,
or publish-and-wait. Each stage of a track records an **interval *or* a trigger**
(`templates/nurture/nurture-track.ja.md`).

The default intervals are a starting point, not a rule — override them to suit the
segment's evaluation cycle, but **record why you changed them** in the track.

> **The same person can sit on several tracks.** Keeping to the per-stage interval
> still means three tracks send three times as much. Cap it at **four sends per
> month to one lead**; past that, decide which track stops.

---

## 2. Mapping to the sales stages (the numbers collide)

**Nurture stages 0–4 and deal stages 0–6 are different things.** Both start at
zero, which is confusing. Always write which one you mean: "nurture 2", "deal 2".

| Nurture stage | Nurture type | Hands off to | In `stage-io-map` |
|---|---|---|---|
| 0. Education | Pre-MQL → MQL | (not a deal yet) | Material for testing deal-0 hypotheses |
| 1. Need | Pre-MQL → MQL | (not a deal yet) | Material for testing deal-0 hypotheses |
| 2. Research | MQL → SQO | **Deal 1. Assessment & Qualification** | §2 |
| 3. Evaluation | MQL → SQO / Trials | Deal 2. Discovery → 3. Solution Development | §3–§4 |
| 4. Selection | MQL → SQO | Deal 4. Solution Presentation | §5 |

### The MQL threshold (not in the sheet; added here)

The sheet **defines neither** MQL nor SQO. **MQL is defined by the buyer's state** —
not by a score, not by behaviour. It uses the same ruler as the stage itself (§1).

| | State | Judgement |
|---|---|---|
| **Pre-MQL** | Does not believe anything needs fixing (stage 0, Education) | — |
| **MQL** | **The buyer can say, in their own words, that they have a problem** (stage 1, Need, or beyond) | This is the threshold |
| **SQO** | The customer themselves recognise the problem as one Scalar can solve | `g1.problem-recognized` |

**The evidence for MQL is what the buyer said** — the body of their enquiry, a question
in a webinar, a community post, free text in a survey. **Repeating a problem we put to
them is not evidence.** Look for whether they describe it as their own situation.

**Behavioural logs (downloads, opens, attendance) infer the state; they do not decide
it.** "Downloaded three papers" is not grounds for MQL. Infer the state from *what* was
downloaded and **record it as an inference** (same confidence discipline as the deal side).

### Hand-off criteria

Past MQL, use the deal-side `g1.*` gates as the hand-off bar
(`sales-playbook.md` §2, phase 1).

| State | What the deal side confirms |
|---|---|
| May approach as MQL → SQO | `g1.problem-recognized` (the customer themselves recognise the problem) |
| May open deal stage 1 | `g1.owner-reached` (reached the problem owner, or an introduction is agreed) |
| May move to deal stage 2 | `g1.timeframe-6q` (a decision within six quarters) |

**"Downloaded a whitepaper" and "attended a webinar" are not grounds for SQO.**
Same principle as the deal side: stages move on customer agreement, not activity.

### The nurture stage does not decide the deal stage to hand into

The table above says **which deal stage's subject matter the lead's interest sits in**;
it does not name the deal stage to open. The deal stage is the **highest stage whose
gates are actually met** (`sales-playbook.md` §2).

Nurture 4 (Selection) needs the most care. The customer's own selection may be well
advanced while our discovery is still zero. That state is not "in deal stage 4" — it is
**"in deal stage 1, with only the customer's clock at stage 4."**

| Handling a lead arriving from nurture 4 | |
|---|---|
| Stage to open | **Deal stage 1.** Judge `g1.*` first |
| Never skipped | `g2.goal-agreed` (agreed business goal) and `decisionCriteria`. A proposal written without those is simply scored against criteria someone else wrote |
| When discovery must be compressed | Record what was dropped as a risk in `deal-log.md` §3. Do not skip it silently |
| Danger sign | The customer brings an RFP, a deadline or a spec and gives no time for discovery — **someone else may already have written the requirements**. Treat it as win-rate evidence |

The same holds for nurture 2 and 3: **do not copy the nurture number into the deal
stage**. The nurture stage marks where the buyer's interest is; the deal stage marks
what has been agreed. They are different rulers.

---

## 3. Product layer — ScalarDB

The sheet restates the five stages as five product-side questions.

| Nurture stage | Product-side question |
|---|---|
| 0. Education | Where their thinking stands |
| 1. Need | The problem that surfaces |
| 2. Research | Presenting how to solve it |
| 3. Evaluation | Proving feasibility and differentiation |
| 4. Selection | Proving return on investment |

### 0. Where their thinking stands (who this targets)

- Considering building a cloud-native system
- Wants to make internal systems fit for DX
- Wants to scale up a database that started small
- Considering breaking the system into microservices

### 1. The problem that surfaces

Only the first row differs between the AWS tab and the Azure tab.

| # | Problem | AWS tab | Azure tab |
|---|---|:-:|:-:|
| 1 | Adopting NoSQL for schemalessness leaves weak transaction management | ✔ | — |
| 2 | With NoSQL you cannot manage transactions across tables or partitions | ✔ | — |
| 3 | Adopting Cosmos DB for schemalessness means no cross-partition transactions | — | ✔ |
| 4 | Building on one specific cloud narrows the options and blocks migration to another | ✔ | ✔ |
| 5 | Decoupling the databases when moving to microservices makes consistency a problem | ✔ | ✔ |
| 6 | Picking the best database per service means consistency cannot be held across them | ✔ | ✔ |
| 7 | Loosely coupled microservices lose consistency between services | ✔ | ✔ |
| 8 | Migrating clouds to cut cost forces a redesign because the databases differ | ✔ | ✔ |
| 9 | Different databases per purpose means no transaction management across them | ✔ | ✔ |

### 2. Presenting how to solve it

- Use cases ScalarDB solves
- How ScalarDB is actually used inside a case study, and to what effect
- Demos matching those use cases and case studies

### 3. Proving feasibility and differentiation

- The technical backing
- How ScalarDB is actually used
- Sample code matching the use cases and case studies
- Technical commentary on the sample code and demos

### 4. Proving return on investment

- Reference architectures per cloud
- Deployment script templates
- The skills assumed
- Project templates per cloud
- A cost estimation tool

---

## 4. Segment layer — the one worked example

**`AWS #001` is the only segment written through to story and content.** Every
other segment has a row and no substance. Read `AWS #001` as the format.

### AWS #001 — struggling with running MySQL

| Stage | Segment-specific heading |
|---|---|
| 0. Education | Struggling with running MySQL |
| 1. Need | Implementing with MySQL + DynamoDB |
| 2. Research | How to solve the problems of MySQL + DynamoDB |
| 3. Evaluation | How to build a system connecting MySQL + DynamoDB with ScalarDB |
| 4. Selection | What is needed to estimate the cost of a MySQL + DynamoDB project on ScalarDB |

**Story** (the buyer's narrative, not the seller's pitch)

| Stage | Story |
|---|---|
| 0 | They started small on MySQL, but each application came to use the columns differently, so building an API meant giving one column several meanings. Shared and general-purpose columns exist; each application reinterprets what a column means; the column count keeps growing with every new application |
| 1 | Offloading part of the MySQL data to DynamoDB creates new problems: the data structure changes on the way out; the shared fields between MySQL and DynamoDB drift on update; mixed read/write across several DynamoDB tables is not possible |
| 2 | Show what MySQL + DynamoDB can do. Give a demo and sample code so it becomes concrete |
| 3 | Explain concretely how ScalarDB manages transactions across different databases. Explain in detail how to develop an application connecting MySQL + DynamoDB, and how to build one with Spring Boot |
| 4 | Present the skills, the AWS architecture and the costing method needed to run the project, so that they **can take it to internal approval and execute** |

**Content** (what actually gets built and sent for that story)

| Stage | Content |
|---|---|
| 0 | An architecture holding cross-search key columns in MySQL and the detail records in DynamoDB: (1) list on the first screen, filtered in MySQL; (2) detail screen, read from DynamoDB. The use case "offload to NoSQL" — split detail fields out of a bloated MySQL into DynamoDB as key-value. Building the API through ScalarDB holds consistency and makes swapping the backing database smooth. Where cross-search and detail data overlap, what used to be synced eventually can now be updated consistently. **Offloading part of MySQL to DynamoDB may cut cost (hypothesis)** |
| 1 | A proposed MySQL + DynamoDB implementation: how to migrate to DynamoDB while keeping the MySQL data, with DynamoDB's benefits and its problems (different interfaces; no transactions across the two; no mixed read/write transactions), then show that ScalarDB solves them |
| 2 | Demo and sample code (MySQL + DynamoDB using ScalarDB on AWS; a content-metadata management demo) |
| 3 | Product material; detailed commentary on the demo and sample code; how to use ScalarDB; the value proposition; per-feature explainers |
| 4 | AWS architecture diagram; list of AWS services used; ScalarDB licence estimate sheet; AWS estimate sheet; project template; development method; operations and monitoring method |

> In the sheet, stage 0 ends with "may cut cost (hypothesis)" — **left explicitly as
> a hypothesis**. Do not put unverified numbers into content. Labelling it this way
> is correct and worth copying.

---

## 5. Segment list (Target Segments tab)

Columns: Product / Epic / Cloud Service / Segment No. / the situation the segment is
in / business / technology / industry / business function / application /
infrastructure / notes. This tab defines **the horizontal axis (who to aim at)**,
not the vertical one.

### ScalarDB — segments cut by cloud and technology

| Segment No. | Epic | Cloud | Situation | Attributes |
|---|---|---|---|---|
| AWS #001 | Building a web application on AWS | AWS | Started small on MySQL; each application uses the columns differently, so an API needs one column to carry several meanings | Business: users running or about to build a small-start web app · Tech: MySQL · App: API-based · Infra: AWS |
| AWS #002 | Same | AWS | On DynamoDB, tables multiplied as features grew. Where tables are managed per application user, consistency must now be held across applications and users | Tech: DynamoDB · App: API · Infra: AWS |
| AWS #003 | Same | AWS | Using DynamoDB via ScalarDB; wants full-text search over the DynamoDB data and is considering Elasticsearch | Same |
| AWS #004 | Same | AWS | Deployed ScalarDB on DynamoDB; now planning operations and monitoring for production | Same |
| AWS #005 | Same | AWS | Deployed ScalarDB on DynamoDB; wants to encrypt individual data items | Same |
| AWS #006 | Build light on an RDBMS, move to a distributed database once requirements settle (small-start scenario) | AWS | Planning development on MySQL; wants to move onto a distributed database and optimise cost once user numbers grow | Tech: MySQL and other relatively small databases |
| AWS #007 | Building web/native applications on MongoDB | AWS | Started small on MongoDB; performance problems as users grew. Considering sharding but wants to know whether there is another way | Tech: MongoDB · **Note: check whether a MongoDB edition of ScalarDB is planned** |
| AWS #008 | Shipping data to a graph database | AWS | Uses ScalarDB but also wants to write data into a graph database | Tech: ScalarDB users |
| AWS #009 | Hybrid DynamoDB and RDBMS | AWS | Wants to use RDBMS and NoSQL together on AWS — keeping the existing RDBMS while gaining what NoSQL offers | — |
| AWS #009<br>**(duplicate ID)** | CQRS / Saga pattern | AWS | With CQRS, DynamoDB and Aurora only sync eventually; Saga is complex to implement. Wants CQRS and Saga handled as microservice transactions by ScalarDB | Tech: ScalarDB users |
| Azure #001 | Cosmos DB transaction limits | Azure | Has been using Cosmos DB and finds the lack of cross-container transactions inconvenient | Tech: Cosmos DB |
| Azure #002 | Social app development on Cosmos DB | Azure | An RDBMS does not scale for a social app, so they want NoSQL — but believe NoSQL is weak on transactional consistency and want a better way | Tech: evaluating Cosmos DB |
| Azure #003 | Shipping data to a graph database | Azure | Uses ScalarDB but also wants to write into a graph database, via the Gremlin API | Tech: ScalarDB users |
| Common #001 | Cosmos DB or DynamoDB | Undecided | The web app is decided; internally either Azure or AWS is available. Wants a managed database and needs the pros and cons of Cosmos DB versus DynamoDB | Tech: wants a managed database service |
| **(unnumbered)** | Shrinking as usage declines | To be confirmed | Runs on-premises, container-based NoSQL (e.g. Cassandra); usage is falling and utilisation is down, but the fixed system cost remains, so they are considering shrinking the database | Tech: Cassandra |
| **(unnumbered)** | Workflow system evaluation | — | **Row exists, no content** | — |

### ScalarDB / ScalarDL — segments cut by industry and function (no Segment No.)

| Epic | Situation | Business attribute | Industry | Function |
|---|---|---|---|---|
| Workflow from the drafting stage | Unstructured documents flow continuously between branches and head office; they want workflow from the drafting stage | Companies with many branches | Banking, securities, insurance | Internal audit |
| Workflow from the drafting stage | Same | Same | Retail (drugstores, convenience stores, big-box) | — |
| Workflow from the drafting stage | Same | Same | Automotive (dealers, service shops) | — |
| Cross-company document circulation | They want to digitise the documents and circulation processes exchanged with agencies while preserving evidentiality | Companies with many agencies | Non-life insurance | Invoicing agencies |
| Cross-company document circulation | Same | Companies with many agencies | Life insurance | — |
| Cross-company document circulation | Same | Companies with many agencies | Credit cards (merchants) | — |
| Cross-company document circulation | They want to digitise the documents and circulation processes exchanged with suppliers while preserving evidentiality | Companies with many suppliers | Systems integrators | — |
| Cross-company document circulation | Same | Companies with many suppliers | Electrical manufacturers | — |
| Cross-company document circulation | Same | Companies with many suppliers | Printing and publishing | — |
| Cross-company document circulation | Same | Companies with many suppliers | Trading companies | — |
| Cross-company document circulation | Same | Companies with many suppliers | Construction | — |
| Cross-company document circulation | Unstructured documents flow continuously between subsidiaries/affiliates and the parent; they want workflow from the drafting stage | Companies with many subsidiaries | Automotive manufacturers | — |
| Cross-company document circulation | Same | Companies with many subsidiaries | Trading companies | — |
| Cross-company document circulation | Same | Companies with many subsidiaries | Telecommunications | — |

### ScalarDL

| Segment No. | Epic | Situation |
|---|---|---|
| HLF #001 | How it differs from blockchain | There are many kinds of blockchain and the differences are unclear; they want to know how ScalarDL differs from Hyperledger Fabric and others |

---

## 6. Content ledger (Contents ID tab)

The sheet has **only a header row — nothing registered.** The columns are:

| Column | Meaning |
|---|---|
| Contents ID | Identifier |
| Content name | |
| Content goal | What state this content puts the buyer in |
| Product / solution | (spans three merged columns) |
| Prerequisites | What the reader is assumed to know or face |
| Description | |

The matching form is `templates/nurture/content-inventory.ja.md`, which **adds stage
and segment columns** — without them you cannot tell which track and which step a
piece of content belongs to.

---

## 7. What the sheet leaves unfinished

This sheet **stopped mid-design.** Know the following before using it.

| # | Where | State |
|---|---|---|
| 1 | Working note on the Target Segments tab | "Fill this in by next week. Decide priorities in the week of 11/8!" and "write power scripts (branching on the story and the questions the customer will have, the way a salesperson would speak)" — **a TODO from November 2021, still there** |
| 2 | Duplicate Segment No. `AWS #009` | Both "hybrid DynamoDB and RDBMS" and "CQRS / Saga pattern" carry it. **One must be renumbered** |
| 3 | Unnumbered segments | "Shrinking as usage declines", "workflow system evaluation", and all 14 ScalarDB/ScalarDL industry rows |
| 4 | Empty story and content | Every segment except `AWS #001`. The Azure tab's `Azure #001` has headings only |
| 5 | Workflow product tab | Only the heading "訴求ポイント" (pitch points); no content |
| 6 | Contents ID tab | Header only, zero entries |
| 7 | Data-entry slip on the non-life insurance row | The "business" column repeats the situation text instead of "companies with many agencies" |
| 8 | Stale positioning | §3's problem list is from 2021, centred on Cosmos DB / DynamoDB / Cassandra / MongoDB. It has **no ScalarDB Cluster, no ScalarDB Analytics, no cross-RDB transactions, no breaking up existing RDB silos** — the same staleness flagged for the fit sheet in `stage-io-map.md` §8 |
| 9 | No MQL / SQO definition | Nothing says when marketing hands over to sales (§2 borrows the deal-side gates) |
| 10 | No metrics | No targets anywhere — conversion rate, lead volume, SQO rate |
| 11 | Nothing on the legality of sending | The design assumes email, yet consent, opt-out, disclosure and non-Japan leads appear nowhere |
| 12 | No channels, no cadence | Only *what* to send; never **where, or at what interval** |

**How each is handled here**

| # | Handling |
|---|---|
| 7 | Not patched (a data-entry error in the source sheet; fix it in the sheet) |
| 8 | Not patched, but **§3 and §7-8 state explicitly that the messaging is dated** |
| 9 | **Patched.** §2 defines the MQL threshold as a **buyer state** (reaching stage 1, Need); past that, the deal side's `g1.*` apply |
| 10 | **The shell and the measurement source.** `templates/nurture/nurture-track.ja.md` §9 has the metrics table; the **targets stay empty** until one or two quarters of actuals exist (a decision on Scalar's side) |
| 11 | **The list of points is added in §8.** The judgement is not — legal must confirm |
| 12 | **Patched.** The five in-scope channels and how cadence works are in §1; the track template carries an interval-or-trigger field |

For the MQL threshold (9) and the targets (10), **do not put in placeholder values**.
Do not write what has not been decided as though it had been.

---

## 8. Delivery prerequisites — consent, opt-out, disclosure (not in the sheet; added here)

**The source sheet says nothing about the legality of sending.** The design assumes
email delivery, so settle this before a track goes live. **What follows is a list of
points to check, not legal advice — get legal to confirm before operating.**

### Act on Regulation of Transmission of Specified Electronic Mail (特定電子メール法)

| Point | What to confirm |
|---|---|
| Opt-in | Prior consent is required as a rule. Record and retain the date, the method, and who consented |
| Business-card and similar exceptions | Sending to an address notified on a business card, or to an existing business counterparty, may fall under an exception. **Work out which reach channel rests on which basis, channel by channel** |
| Disclosure | Show the sender's name, the opt-out contact, the sender's address, and a complaints/enquiries contact in the body |
| Opt-out | Never send again to someone who has opted out. **Make sure they are excluded from Re-Engagement** — it runs alongside every stage (§1), which is where this leaks |

### Act on the Protection of Personal Information

| Point | What to confirm |
|---|---|
| Purpose of use | Does the purpose notified or published at collection cover nurture delivery |
| Third-party provision | For lists obtained via co-hosted events or partners, does the use stay inside the consent given at the source |
| Retention | Where the consent and opt-out records are held, and for how long |

### Leads outside Japan

The EU/UK (GDPR / PECR) and the US (CAN-SPAM) differ. **Do not assume the Japanese
requirements carry over.** Check separately before including them.

### Where the records live

Consent and opt-out records are **tied to individuals**. `accounts/_nurture/` holds
types only, so **they do not go there** — keep them in MA/CRM. What goes in the nurture
files is the type-level fact of **which consent basis each reach channel rests on**
(`templates/nurture/segment-sheet.ja.md` §4).

---

## 9. Which tool for what

| Task | Use |
|---|---|
| Read signals and fill the segments, tracks and ledger | `scalar-nurture-intake` skill |
| Define a segment | `templates/nurture/segment-sheet.ja.md` |
| Design one segment's five nurture stages | `templates/nurture/nurture-track.ja.md` |
| Keep content in a ledger | `templates/nurture/content-inventory.ja.md` |
| Stage records once a deal exists | `templates/sales/` (`stage-io-map.md`) |
| Problem-to-product mapping and the proposal format | `proposal-map.md` |
| Company and product decks | `scalar-product-slides` skill |
| Customer-specific proposal | `scalar-proposal-slides` skill |
