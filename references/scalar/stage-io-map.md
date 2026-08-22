*[日本語](stage-io-map.ja.md)*

# Stage input / output map

Source: the Google Sheet 「ステージごとの商談の進め方」
(`1jFMI1x6-z1xAr9ZRh4-Qx4BLc52WMXK5EOhMhfHdtoU`, last modified 2024-09-01).

This document does **not** replace [`sales-playbook.md`](sales-playbook.md).

| Concern | Source |
|---|---|
| Phase definitions, gate IDs, transition conditions, BANT criteria, the five material types | `sales-playbook.md` (the only source) |
| Who you meet in a stage, what you hand them, what you must come back with | **This document** |

The playbook decides *whether you may move on*; this map holds *the work inside
the stage and its inputs and outputs*. The `scalar-deal-intake` skill uses it to
assign facts pulled out of minutes and email to the right output field.

---

## 1. Stage mapping

The sheet's stage numbers match the playbook's phase numbers for 1–5. Only
number 6 disagrees.

| Sheet stage | Playbook phase | Gate IDs | Note |
|---|---|---|---|
| (none) | 0. Territory / Account Planning | `g0.*` | No rows in the sheet — internal planning before first contact. Form: `templates/sales/stage-0-planning.ja.md` |
| 1. Assessment & Qualification | 1. Assessment & Qualification | `g1.*` | Match |
| 2. Discovery | 2. Discovery | `g2.*` | Match |
| 3. Solution Development | 3. Solution Development | `g3.*` | Match |
| 4. Solution Presentation | 4. Solution Presentation | `g4.*` | Match |
| 5. Resolution | 5. Resolution | `g5.*` | **Sheet rows are empty**; §6 below is filled in from the playbook |
| 6. Close | 6. Delivery / Renewal / Expansion | `h6.*` | **Sheet rows are empty** and the name differs — see §7 |

`meta.stage` in `account.json` takes 0–6 and follows the playbook numbering.
Do not renumber it here.

---

## 2. Stage 1 — Assessment & Qualification

The counterpart is the **person who became the first touchpoint**. The goal is
empathy with Scalar, and reaching the person who actually owns the problem.

| # | Counterpart | Goal | Input (content you bring) | Output (what you take away) |
|---|---|---|---|---|
| 1-1 | First touchpoint | They empathise with Scalar and want to solve the problem together | Company intro — vision, mission | Follow-up questions about Scalar as a company |
| 1-2 | First touchpoint | Their problem and direction line up with Scalar's | Company intro — the problem we exist to solve | Same |
| 1-3 | First touchpoint | They understand Scalar's potential | Company intro — investors, funding raised, case studies | Same |
| 1-4 | First touchpoint | A concrete business problem matches a solution template | (self-assessed with the fit sheet, §8) | The customer has a matching problem **and the person in front of you owns it** |
| 1-5 | First touchpoint | Agreement on the problem and on continuing the evaluation | Problem-fit sheet (§8) | Same |
| 1-6 | First touchpoint | Confirm the deployment timing | Timing-discovery methods (§9) | Budget schedule |
| 1-7 | First touchpoint | Confirm the proposal process; agree milestones and schedule up to the proposal | Interview | Initial influence map / TODOs to close registered in CRM |

**If they are not the owner, stay in this stage until you are introduced to the
owner.** This is stated explicitly in the sheet and is a precondition for stage 2.

### Transition criteria (as written in the sheet)

- The customer has a business problem our product or service can solve → `g1.problem-recognized`
- The decision timeline is within 6 quarters → `g1.timeframe-6q`

The playbook adds `g1.owner-reached`, `g1.linked-to-exec` and
`g1.next-discovery-agreed`. Row 1-4's "is this the owner" maps to `g1.owner-reached`.

---

## 3. Stage 2 — Discovery

The widest set of counterparts. **Internal discussion** (Scalar-side work) and
**customer/partner interviews** alternate.

| # | Counterpart | Goal | Input | Output |
|---|---|---|---|---|
| 2-1 | First touchpoint | Find out which executives, departments and people this proposal involves | Interview | Roles and contact details of the departments and people involved; introductions |
| 2-2 | Department director | Get a meeting with the director who owns the escalation and discuss the proposal directly | Interview | From the director: the obstacles to clear before execution |
| 2-3 | Department executive | Get a meeting with the executive who ultimately approves and discuss the proposal directly | Interview | From the executive: the obstacles to clear before execution |
| 2-4 | IT department | Get introduced and hear the system preconditions that would block deployment | Interview | System issues |
| 2-5 | IT department | Hear the existing partners, the possible partners, and each one's territory | Interview | Each partner's role and scope |
| 2-6 | Business department | Hear the problems that must be solved from a business point of view, and the return on investment | Interview | Problems and ROI |
| 2-7 | Partner contact | Hear the conditions (technical, contractual, commercial) for the partner to carry Scalar, and the tasks and touchpoints needed to clear them | Interview | Partner readiness / influence map inside the partner |
| 2-8 | Main contact | Consolidate every interview into a discovery map for the whole customer organisation, centred on the problem | Interviews from 2-1 to 2-7 | Discovery map |
| 2-9 | Internal discussion | Agree internally on the scope we can propose, based on the discovery map | Internal meeting | Proposal scope |
| 2-10 | Main contact | Verify the map and check the scope fits. **If it is too large, agree a minimum scope; if too small, check whether a partner solution closes the gap and agree to propose jointly** | Discovery map / proposal scope | Customer agreement on the problem to solve, on our scope, and on the partner's scope |
| 2-11 | Internal discussion | Turn the in-scope business into system requirements: story map, system architecture, UX design, wireframes, requirements that drive the platform, and align our strengths with the customer's critical problems | Discovery map / proposal scope | Proposal draft (story map / system architecture / UX design / wireframes / additional interview items / system size estimate) |
| 2-12 | Main contact | Raise the bar on requirements using our differentiators; identify the likely competing vendors | Fear scenario / use cases / case studies / competitor overview | Confirmed perception of our differentiators / what the customer values in the use case / competitor list |
| 2-13 | Internal discussion | Write the business proposal | Proposal draft + differentiator perception + priorities + competitor list | Business-department proposal |
| 2-14 | Internal proposal review | Review internally and close every finding | Business-department proposal | Management review |
| 2-15 | Main contact | Agree the proposal's scope, fix the target business, confirm business constraints, system issues and system constraints | Business-department proposal | Agreed scope / constraints |

The three maps (discovery / system / influence) are drawn by the
`b2b-account-maps` skill; feed 2-7 and 2-8 into it.

### Transition criteria (as written in the sheet)

- Detailed requirement confirmation complete
- System issue extraction complete
- **Hold the stage-transition review meeting** → output is "the proposal plan and resource assignment per proposal content"

That review meeting is the **WPS (Win Planning Session)** in playbook §6 and is
judged by `g2.wps-done`.

---

## 4. Stage 3 — Solution Development

Fix the requirements, align on feasibility through demo/PoC, and get a sense of
the money.

| # | Counterpart | Goal | Input | Output |
|---|---|---|---|---|
| 3-1 | Internal discussion | Define functional requirements at outline level | Business-department proposal / agreed scope / constraints | Business flow diagram / function list / data model / system architecture |
| 3-2 | Main contact | Align on the requirement behind each function | Business flow diagram / function list / data model / system architecture | Confirmed functional requirements / whole-system picture |
| 3-3 | IT contact | Confirm the system constraints on each function | Functional requirements / whole-system picture | Constraints / connected systems / infrastructure constraints / security standards / SLA |
| 3-4 | Internal discussion | Define the non-functional requirements | Constraints / connected systems / infrastructure constraints / security standards / SLA | Non-functional requirements per component / infrastructure design / implementation approach |
| 3-5 | Main + IT contact | Confirm the security and operations policies; agree the non-functional requirements | Non-functional requirements / infrastructure design / implementation approach | Confirmed implementation approach / chosen infrastructure (cloud platform, frameworks, …) |
| 3-6 | Main, IT and business contacts | Show a demo or prototype; explain how the product meets the requirements; run a PoC | Demo / product-based presentation / PoC | Feedback on whether the product fits the product and business requirements |
| 3-7 | Someone inside the customer | Draw out the budget for the proposed scope, the ROI target — **the money the approval request needs** | Interview | Target quotation amount |
| 3-8 | Department director | Set up a visit and confirm the proposal matches the division's goals and is agreed internally | Meeting | The director endorses the proposal |
| 3-9 | Department executive | Set up a visit and confirm the proposal matches the company's goals and is agreed internally | Meeting | The executive endorses the proposal |

### Transition criteria (as written in the sheet)

- A demo or prototype has been shown → `g3.demo-understood`
- The product's coverage has been explained and a PoC is agreed → `g3.poc-agreed`

Row 3-7's target amount feeds `g3.value-quotable` and BANT `budget`.

---

## 5. Stage 4 — Solution Presentation

Lock the delivery structure, the quote and the proposal strategy — partners
included — then present.

| # | Counterpart | Goal | Input | Output |
|---|---|---|---|---|
| 4-1 | Internal discussion | Select the implementation and operations partner | All outputs so far | Partner roles and candidates decided |
| 4-2 | Internal discussion | Write the business + system proposal | All outputs so far | Proposal |
| 4-3 | Partner account manager | Agree to collaborate on the customer proposal | All outputs so far / proposal | Partner NDA signed / development split agreed / operations service agreed |
| 4-4 | Internal discussion | Redefine scope and roles | Proposal / NDA / development split / operations service | Proposal + quotation assumptions + system size (past record, comparable cases) |
| 4-5 | Partner account manager | Agree the delivery and operations structure; request the quote | Proposal + quotation assumptions + system size | Project structure chart / rough quotation / quotation assumptions |
| 4-6 | Internal discussion | Prepare for price pressure (isolate must-have functions, size the optional ones individually) and for competitors (differentiate, neutralise) | Structure chart / rough quotation / assumptions | Proposal strategy for the customer |
| 4-7 | Someone inside the customer | Draw out the budget and ROI target the approval request needs | Interview | Target quotation amount |
| 4-8 | Main contact | Review the proposal, find the gaps, adjust what is missing or excessive | Proposal / rough quotation / assumptions | Proposal revision points / agreement on the final proposal |
| 4-9 | IT contact | Review the proposal, find the gaps, adjust what is missing or excessive | Proposal / rough quotation / assumptions | Proposal revision points / agreement on the final proposal |
| 4-10 | Partner account manager | Re-agree the split of roles, each side's quotation scope, and the target amount | Proposal revision points / final proposal agreement | Final scope / role assignment table / final agreement with the partner on the target price |
| 4-11 | Internal discussion | Produce the detailed quotation | Proposal revision points / final proposal agreement | Final scope / our quotation scope refined |
| 4-12 | Department director | Confirm the proposal matches the division's goals and is agreed internally | Meeting | The director endorses the proposal |
| 4-13 | Department executive | Confirm the proposal matches the company's goals and is agreed internally | Meeting | The executive endorses the proposal |
| 4-14 | Customer stakeholders | Deliver the final proposal | Proposal / detailed quotation / ROI | Final proposal presented |
| 4-15 | Main contact | Get feedback comparing our proposal against the competitors' | Final proposal presented | What is missing for selection / comparison against competitors |
| 4-16 | Main contact | If we are behind, rework the scope and the sizing | What is missing / comparison result | A proposal for the re-pitch |

The quotation is owned by the `spreadsheets` skill and the proposal by
`scalar-proposal-slides`.

### Transition criteria (as written in the sheet)

- Our product is selected → `g4.product-selected`
- Budget and purchase amount are roughly agreed → `g4.budget-agreed`
- The delivery partner is decided → `g4.partner-decided`

---

## 6. Stage 5 — Resolution (sheet empty; filled from the playbook)

**Stage 5 has no rows in the sheet.** The table below is taken from
`sales-playbook.md` §2 phase 5 and is not sheet content.

| # | Counterpart | Goal | Input | Output |
|---|---|---|---|---|
| 5-1 | Customer procurement / legal | Sign the Terms & Conditions | Final proposal / detailed quotation | Signed contract (`g5.terms-signed`) |
| 5-2 | Partner | Where a partner channel exists, open the reseller agreement and ordering route | Role assignment table / channel plan | Reseller agreement and ordering route (`g5.channel-open`) |
| 5-3 | Customer procurement | Receive the purchase order | Signed contract / quotation | Purchase order (`g5.po-received`) |
| 5-4 | Customer / partner | Sign the services contracts required | SOW draft | Services contract (`g5.services-contracted`) |
| 5-5 | Internal (support) | Be able to open the support desk before go-live | Contract terms / rollout plan | Support desk (`g5.support-ready`) |

**Quote licences and services separately.** Trade discounts against something —
a reference, volume, a multi-year term, reduced risk (playbook §2, phase 5).

---

## 7. Stage 6 — Close / Delivery (sheet empty; the names disagree)

The sheet's heading is "6. Close" with no rows. The playbook's phase 6 is
**Delivery / Renewal / Expansion**, which has no fixed gates and is reviewed
quarterly against health items:

`h6.value-realized` (actuals against the KPIs in the proposal), `h6.utilization`
(anything unused), `h6.satisfaction`, `h6.renewal-risk` (renewal date and risk),
`h6.expansion` (candidate additional use cases), `h6.reference` (delivering on
the reference commitment).

**Do not read the sheet's "Close" as "done at the order".** In the playbook,
realising the value, renewing and expanding are all inside one phase.

---

## 8. Problem-fit sheet (input to 1-5)

Judge, in conversation with the person in front of you, whether their problem is
one Scalar can solve.

### Scalar IST (consent management, personal data)

| # | Target company | Description | How to check |
|---|---|---|---|
| 1 | Companies subject to the Act on the Protection of Personal Information | Consent documents do not follow APPI or the revised Civil Code | Vague purposes of use, a broad set of collected fields, many third-party recipients |
| 2 | Companies pushing data utilisation | They use personal data for personalised services and optimisation | They run personalised services |
| 3 | Companies with membership registration | There is a user registration mechanism; often with products needing software updates, or where customers publish information themselves | Customer information is submitted at registration |
| 4 | Companies where third-party provision is core | Their product or service does not work without providing data to third parties | Intermediaries (travel, recruiting), advertising and media, financial and insurance services — B2B2C platform intermediaries |
| 5 | Companies whose business model is data distribution | The model assumes information flowing between businesses or individuals | Smart cities, community platforms |
| 6 | Companies offering B2C services | B2C operators | Mobile games, membership services, D2C |

### ScalarDB

| # | Target company | Description | How to check |
|---|---|---|---|
| 1 | Developers considering Azure Cosmos DB | Cosmos DB does not support ACID transactions across partitions; ScalarDB provides them on top of it | Ask whether they need transaction management on Cosmos DB |
| 2 | Developers considering AWS DynamoDB | DynamoDB does not support mixed read/write transactions; ScalarDB provides them on top of it | Ask whether they need transaction management on DynamoDB |

> **Caution — out of date.** The ScalarDB section has only two rows and still
> frames the pitch as transactions on a single NoSQL store. It does not cover
> today's main ground: **transactions across heterogeneous databases, breaking up
> existing RDB silos, ScalarDB Analytics, and ScalarDB Cluster.** Do not
> disqualify a stage-1 account merely because it fits neither row; refresh the
> criteria with the current positioning before relying on them. This caution is
> not in the sheet.

---

## 9. How to find out when the customer will deploy (input to 1-6)

| # | Method | Steps |
|---|---|---|
| 1 | Read the mid-term management plan | Before the visit, work out which year of the plan they are in. **Year 1** — detailed planning: they survey in H1 and fix the execution timing in H2; establish yourself as an advisor and get inside. **Year 2** — building and executing: pitch replacing the existing stack. **Year 3** — hitting and correcting the plan: get into the next mid-term plan, or aim at leftover budget with a small, near-R&D system. Also extract the problems in the plan's themes that match our solution, and for each match confirm which year it is scheduled for. Read the annual securities report too, and check whether a **large intangible asset has recently been booked** — investment tends to be held back after one. |
| 2 | Ask the contact | Work back from the fiscal year end to estimate when next year's planned budget is fixed (generally one month before year end). Execution approvals go through regular management meetings, so find out which bodies meet. Ask the contact for the escalation timing and deadline and reconcile them with the fiscal year end. Ask who holds execution authority **by amount and by investment type**. |
| 3 | Ask the partner | Ask a partner staffed at the customer about the budget escalation timing and the conditions for execution approval. |

---

## 10. Closing milestone

The sheet says only: **confirm BANT** (Budget / Authority / Needs / Timeframe).
The conditions under which each may be called `ok` live in `sales-playbook.md`
§5. **Do not redefine them here.**

> **Caution — what the sheet is missing.** The ledger (`discovery` in
> `account.json`) carries a deal as MEDDPICC plus "why now": `identifiedPain`,
> `metrics`, `compellingEvent`, `economicBuyer`, `decisionCriteria`,
> `decisionProcess`, `champion`, `competition`, `paperProcess`. The sheet has no
> rows corresponding to **Metrics, Economic Buyer or Paper Process**.
> `paperProcess` in particular — vendor registration, credit and anti-social
> checks, the information-security review, legal, acceptance and payment terms —
> never appears in the sheet, yet in a Japanese enterprise it is what sets the
> elapsed time from final proposal to close. The record forms make up for this in
> stage 2 §10 (MEDDPICC coverage) and stage 4 §12 (paper process). This caution is
> not in the sheet.

---

## 11. Output chain

Which output becomes the input to what comes next. `scalar-deal-intake` uses
this chain to work backwards to the inputs missing in the current stage.

```
[1] Problem-fit sheet ─┐
    Timing discovery   ├→ Budget schedule / initial influence map
    Interview         ─┘        │
                                ▼
[2] Interviews everywhere → Discovery map → Proposal scope (internal)
                                │                  │
                                └──→ verify with customer ┘
                                        ▼
                    Proposal draft (story map / architecture / UX /
                    wireframes / further interview items / size estimate)
                                        │
                    + differentiator perception, priorities, competitor list
                                        ▼
                    Business-department proposal → internal review
                                        ▼
                    Agreed scope / constraints
                                        ▼
[3] Business flow / function list / data model / architecture
                                        ▼
                    Confirmed functional requirements / whole-system picture
                                        ▼
                    Constraints, connected systems, infra constraints, security, SLA
                                        ▼
                    Non-functional requirements / infra design / approach
                                        ▼
                    Demo & PoC fit feedback + target quotation amount
                                        ▼
[4] Partner roles → proposal → NDA, development split, operations service
                                        ▼
                    Quotation assumptions + system size
                                        ▼
                    Structure chart / rough quotation → proposal strategy
                                        ▼
                    Proposal revision points / final proposal agreement
                                        ▼
                    Final scope / role table / detailed quotation
                                        ▼
                    Final presentation → competitor comparison → (re-pitch if behind)
                                        ▼
[5] Contract / channel / purchase order / services contract / support desk
                                        ▼
[6] Value realised, utilisation, renewal, expansion, reference (h6.*)
```

---

## 12. Which tool for what

| Task | Use |
|---|---|
| Fill stage records from minutes and email | `scalar-deal-intake` skill |
| The record forms themselves | `templates/sales/*.ja.md` (listed in that directory's README) |
| Meeting history, close plan, risks, loss reason | `templates/sales/deal-log.ja.md` |
| Internal planning before first contact (phase 0) | `templates/sales/stage-0-planning.ja.md` |
| Nurturing a lead before a deal exists (nurture 0–4) | `scalar-nurture-intake` skill ([`nurture-map.md`](nurture-map.md)) |
| Deciding whether the stage may advance | `sales-playbook.md` §2 gates |
| Updating the ledger (`account.json`) and the activity-plan deck | `scalar-account-plan` |
| Materials for one visit | `scalar-ae-materials` |
| Drawing the three maps | `b2b-account-maps` |
| Formal proposal and quotation | `scalar-proposal-slides` / `spreadsheets` |
