*[日本語](sales-playbook.ja.md)*

# Scalar B2B Sales & Proposal Playbook (machine-readable edition)

A machine-readable rendering of Scalar, Inc.'s "B2B sales & proposal activity standard,"
structured so that skills and scripts can reference it. It is the **single source of
truth** shared by `scalar-account-plan` and `scalar-ae-materials`; neither skill
redefines what is written here.

It maps to the structure of the original document (§1 Principles → §3 Process → §4 Forecast →
§5 Material types → §6 Phase requirements → §8 Meeting bodies → §9 Information management → §10 Checkpoints).

---

## 1. Foundational principles for decision-making

Before producing a material, check that it doesn't conflict with these. **A material is not
an end in itself — it is evidence that makes the next decision possible.**

| # | Principle | Implication for material creation |
|---|---|---|
| 1 | Sales is managed probabilistically (touchpoint count, win rate, cycle, TCV) | Don't spend formal-proposal effort on deals with low win rate and low value |
| 2 | Propose from WHAT and WHY | Don't produce materials that answer the customer's requirements with HOW alone. Put the target state and "why now" first |
| 3 | Coach the customer and support their decision-making (Challenger-style) | Customer-facing materials are structured in the order: reframe → reconstruct → reinforce → make it personal → new way → action plan |
| 4 | Build trust first | Include information, options, and risks to avoid beyond your own product. Don't rush the sale |
| 5 | Stages advance on customer agreement, not activity volume | "We explained it" or "we sent the proposal" is not grounds for advancing a stage. Tie the gates in §2 to customer-side evidence |
| 6 | Contract small and fast, and build an expandable channel | Break even a large vision into executable units. Estimate license and services separately |

---

## 2. Phases and stage-transition conditions (gates)

`account.json`'s `meta.stage` takes values 0–6. Each item under `gates` is keyed by the
**gate ID** in the table below (the ID is a stable identifier shared across the ledger,
slides, and skills — do not add or remove them arbitrarily).

### Phase 0 — Territory / Account Planning

Define the target market, customers, use cases, and touchpoints. The internal decision is
"where, why, and who invests time."

| Gate ID | Transition condition |
|---|---|
| `g0.icp-fit` | The target account fits the ICP |
| `g0.hypothesis-defined` | The hypothesized problem, target persona, buying trigger, and touchpoint-acquisition method are defined |
| `g0.capacity-assigned` | The sales effort to invest and the owner are decided |

Main activities: researching the market, regulations, competitors, and the customer's
mid-term management plan and IT strategy / defining the problems and buying triggers where
Scalar could become indispensable / designing persona-specific messaging for CIO, CTO, CDO,
CISO, and LoB / hypothesizing the organization, existing systems, existing vendors, and
partners of priority accounts. **Design the visit goal not as "get an appointment" but as
"the hypothesis to validate" and "the next introduction to obtain."**

### Phase 1 — Assessment & Qualification

Get the customer to recognize their business problem and understand that Scalar has a way
to solve it. At the same time, assess whether the deal is worth investing in.

| Gate ID | Transition condition |
|---|---|
| `g1.problem-recognized` | **The customer themselves** recognizes a problem that Scalar can solve |
| `g1.owner-reached` | Reached the department/owner responsible for the problem, or an introduction has been agreed |
| `g1.linked-to-exec` | The connection to a management/departmental problem has been confirmed |
| `g1.timeframe-6q` | In principle, a decision can be made within 6 quarters |
| `g1.next-discovery-agreed` | The attendees and theme for the next discovery session have been agreed |

### Phase 2 — Discovery

Build trust across the customer's organization and uncover, beyond surface-level requests,
the business goals, root causes, system issues, and buying conditions. **Discovery
continues through to contract.**

| Gate ID | Transition condition |
|---|---|
| `g2.goal-agreed` | The business goal and problem the customer wants to achieve are agreed |
| `g2.requirements-agreed` | The system issues/requirements needed to solve the problem are agreed |
| `g2.three-maps` | The Discovery, System, and Influence maps have been created and validated |
| `g2.buying-process` | The proposal target, attendees, partners, existing environment, and buying process are clear |
| `g2.wps-done` | A WPS has been held and a proposal team including an SA has been formed |

Tools: use SPIN (Situation / Problem / Implication / Need-payoff) to dig into the problem.
Drawing the 3 maps is owned by the `b2b-account-maps` skill.

### Phase 3 — Solution Development

Redefine the customer's requirements and design the To-Be, value, specification, and
implementation approach together with Scalar and partners. Use a demo, prototype, and a PoC
where needed, to make sure the customer correctly understands feasibility and constraints.

| Gate ID | Transition condition |
|---|---|
| `g3.demo-understood` | A demo or prototype has been presented, and the customer correctly understands **what it can and cannot do** |
| `g3.poc-agreed` | The customer understands how Scalar's products would address it, and a PoC has been agreed for unevaluated items |
| `g3.value-quotable` | The To-Be, requirements, rough configuration, value, differentiation, and rough price can all be explained |
| `g3.deal-desk` | The proposal risk has been reviewed at Deal Desk |

### Phase 4 — Solution Presentation

Integrate the problem, To-Be, implementation approach, ROI, differentiation, implementation
plan, and price into **a single decision-making story**.

| Gate ID | Transition condition |
|---|---|
| `g4.product-selected` | The Scalar product has been selected |
| `g4.budget-agreed` | The rough budget and purchase amount are agreed, and budget availability is confirmed |
| `g4.partner-decided` | The implementation partner is decided |
| `g4.closing-reviewed` | The issues and tasks remaining to contract have been reviewed at Deal Desk |

Where competition is strong, consider **redefining the requirements** or **neutralizing**
via partner capability. Adapt to the evaluation perspectives not just of the Champion but
also the decision-maker, technical, user, procurement, and legal stakeholders.

### Phase 5 — Resolution

Beyond signing the contract, finalize the conditions, channel, order, support, and future
renewal basics needed to fulfill delivery obligations smoothly.

| Gate ID | Completion condition |
|---|---|
| `g5.terms-signed` | Terms & Conditions have been signed with the end user |
| `g5.channel-open` | Where a partner channel exists, the reseller agreement and order path are open |
| `g5.po-received` | The purchase order has been received |
| `g5.services-contracted` | The necessary services contract(s) have been signed |
| `g5.support-ready` | Support can be opened by the time of go-live |

**Keep license and services separate.** Exchange discounts for something in return — case
study rights, volume, multi-year terms, risk reduction, etc.

### Phase 6 — Delivery / Renewal / Expansion

Realize the value promised at proposal time and drive adoption, renewal, additional
licenses, expansion to other departments, and case-study creation. No fixed gates are set
here; instead, review the following health items quarterly.

`h6.value-realized` (actual results against the KPIs promised at proposal time) /
`h6.utilization` (whether there is unused capacity) / `h6.satisfaction` /
`h6.renewal-risk` (renewal date and renewal risk) / `h6.expansion` (candidate additional
use cases) / `h6.reference` (fulfillment of case-study/reference commitments).

---

## 3. Matrix of the 5 material types × phase

The same deal information must never be shown to everyone using a single material.

| Type | Primary purpose | Primary audience | Required elements |
|---|---|---|---|
| **Internal-facing** | Investment decisions, resource allocation, risk management, stage review | Management, sales, SA, product, legal, finance, delivery | Clear separation of fact vs. hypothesis, evidence, unconfirmed items, risks, owner, deadline, and the decision being requested. **Forwarding to the customer is prohibited** |
| **Customer-facing (informational)** | Information sharing, dialogue, problem exploration, trust-building | Customer contacts, business units, technical staff | Centered on implications for the customer's industry, hypotheses, case studies, and questions. Avoid over-asserting. Not just a product pitch |
| **Customer-facing (proposal)** | Selection, budgeting, internal approval, and contract decisions | Champion, decision-maker, technical evaluator, procurement | Formal and self-contained. Structured so the customer can forward and escalate it internally |
| **Partner-facing (informational)** | Understanding Scalar's value, exploring collaboration potential | Partner sales, SE, business owner | Reusable standard information. Minimize customer-specific confidential information |
| **Partner-facing (proposal)** | Agreement on roles, channel, estimate, and proposal content for a joint deal | Partner deal owner, sales, SE, legal, management | Explicit joint win strategy, RACI, channel, estimate boundaries, IP/confidentiality, and contractual responsibility |

### What gets produced by phase

The `slide-forge` implementation status is noted alongside. **"Upcoming" means the template
is not yet implemented**, and for now such materials are written using the generic template
(`google-slides-template`).

| Phase | Internal-facing | Customer-facing (informational) | Customer-facing (proposal) |
|---|---|---|---|
| 0 | Territory plan / ICP / account plan / persona hypotheses | Industry trend & problem hypothesis materials, company introduction, case study collection | **In principle, not yet produced** (if there is a planning discussion, state the hypotheses explicitly as a "discussion-point summary") |
| 1 | Visit plan (`visit-plan`), qualification notes, meeting minutes, deal registration form | Company/product introduction by customer, related case studies, problem-hypothesis one-pager (`challenge-hypothesis`) | Discussion-theme summary, initial concept memo (1-3 pages) |
| 2 | 3 maps (`b2b-account-maps`), WPS (`win-plan`), problem/requirements ledger, buying process | Discovery guide, problem structure diagram, As-Is overview, discussion points, case studies from other companies | Discovery-results confirmation document, concept design/PoC proposal |
| 3 | Solution Strategy, requirements ledger, architecture, ROI model, competitive analysis, Deal Desk materials | Demo materials, To-Be concept, technical explanation, architecture overview, FAQ | PoC proposal/implementation plan, concept proposal, rough estimate (`scalar-proposal-slides` / `spreadsheets`) |
| 4 | Final proposal review, price approval, forecast, closing plan | Executive summary, individual supplements, FAQ, demo results report | **Formal proposal**, quotation, implementation plan, ROI/TCO, internal-escalation-support version (`scalar-proposal-slides`) |
| 5 | Contract terms summary, approval workflow, delivery-obligation checklist, order handoff document | Contract/implementation-kickoff checklist, FAQ, support guide | Final quotation, purchase order, contract-attached specification, SOW |
| 6 | Order handoff document, health review, renewal plan, expansion account plan | Implementation kickoff, regular reporting, usage status, roadmap sharing | Renewal proposal, additional licenses, expansion to other departments, additional services proposal |

Partner-facing (informational) and partner-facing (proposal) are defined in §6 of the
original document, but the `slide-forge` template implementation is **upcoming**. See §7.5
of the original document for the items that must always be included in a joint proposal
policy document.

### Check to avoid mixing up material types

When producing a customer-facing (informational) or customer-facing (proposal) material,
always check before generating it:

- Does it contain descriptions of individuals' influence, stances, or internal politics? (→ information that belongs only in internal-facing materials)
- Does it name a competitor's weakness directly?
- Is an unconfirmed item written as if it were confirmed? (frame it as "to be confirmed today")
- Is the handling of pricing/roadmap information within what's appropriate to disclose to that audience?

---

## 4. Quality standards common to all materials (original §5.1)

- State the purpose, target audience, and the decision or reaction expected, up front
- Distinguish fact, customer statement, analysis, hypothesis, and proposal
- Do not break the causal chain of As-Is → problem → impact → To-Be → implementation approach
- Show the effect on business outcomes, risk reduction, revenue, cost, and time — not features
- Record the assumptions, scope, version, creation date, and owner of every diagram/table
- Attach a calculation basis and assumptions to any figure for price, effect, or performance
- Properly classify and control the distribution of customer names, personal names, competitive information, pricing, and contract information
- State the next action, owner, due date, and completion condition explicitly
- Never leave behind old customer names, amounts, configurations, or notes from a reused template

---

## 5. Forecast and deal risk (original §4)

| Category | Definition |
|---|---|
| `Pipeline` | Risk is not yet sufficiently understood |
| `Best` | Risk is understood, but not controllable by us |
| `Commit` | Risk is understood and controllable through **actions agreed by both us and the customer** |
| `Closed` | Contract/order is complete |

`account.json`'s `meta.forecast` takes one of these 4 values. **A `Commit` that cannot be
backed by evidence should be downgraded to `Best`.**

Each BANT item corresponds to the ledger's `bant`, and `level` takes `ok` / `risk` / `unknown`:

| Key | What to confirm | Condition for `ok` |
|---|---|---|
| `budget` | Budget line, budget name, amount, and date funds become available | All 4 have been obtained from customer statements or documents |
| `authority` | Roles and decision criteria of the escalator, decision-maker, evaluator, procurement, and legal | The decision-maker is identified and their decision criteria are known |
| `needs` | Whether the problem and economic impact are clear, and whether the selection criteria require Scalar | Our differentiation is included in the selection criteria |
| `timeframe` | The go-live date and the decision/contract milestones worked back from it | The reverse-engineered schedule is agreed with the customer |

---

## 6. Meeting bodies (original §8)

| Meeting | Timing | Purpose | Output |
|---|---|---|---|
| Account Planning Session | Quarterly / at priority-account updates | Account strategy and investment allocation | Account plan, touchpoint plan |
| WPS (Win Planning Session) | At Discovery completion, or when the win strategy changes | Deal win strategy and proposal-investment decision | Stage-transition decision, proposal team, risk countermeasures |
| Deal Desk | After Solution Development, after formal proposal, or on contract exceptions | Approval of technical, pricing, contract, and delivery risk | Approval conditions, required fixes, closing decision |
| Forecast Review | Weekly | Landing forecast and gap countermeasures | Pipeline/Best/Commit, next actions |
| Customer Success Review | Quarterly | Confirming outcomes, satisfaction, renewal, and expansion | Health status, improvements, renewal/expansion plan |

---

## 7. The 10 operational checkpoint questions and their ledger fields

10 questions that **must always be answerable** at every review (original §10).
`account_ledger.gaps()` uses this table as the basis for converting unanswerable questions
into candidate actions.

| # | Question | Ledger field | Who to act on it when unmet |
|---|---|---|---|
| 1 | What business outcome does the customer want to achieve | `discovery.metrics` | The owner of the department that owns the problem |
| 2 | Why does the decision need to be made now | `discovery.compellingEvent` | Champion |
| 3 | What is the impact of leaving the problem unaddressed | `painChain` | The frontline owner and their manager |
| 4 | Is the problem and the To-Be agreed with the customer | `gates.g2.goal-agreed` | Champion |
| 5 | Why is Scalar needed, and why are competitors or the status quo insufficient | `discovery.decisionCriteria` | Technical evaluator |
| 6 | Who are the Champion, decision-maker, technical evaluator, user, opponent, and coach | `people[]` (`role` and `stance`) | Introduction from a known stakeholder |
| 7 | What are the budget, decision, procurement, legal, and implementation milestones | `bant`, `discovery.decisionProcess` | Procurement / IT department |
| 8 | Who is the partner, why are they partnering with Scalar, and what are they responsible for | `partners[]` | Partner sales owner |
| 9 | What is the biggest risk, and what is the next action to control it | `risks[]` → `actions[]` | Internal (WPS / Deal Desk) |
| 10 | What **customer-side evidence** demonstrates the completion condition of the current stage | `evidence` under `gates[<current stage>]` | Champion |

**Do not fill in answers.** Leave unconfirmed items unconfirmed, and put them into
`actions[]` with a person to confirm with and a deadline. This becomes the AE's action plan.

---

## 8. Information management (original §9)

- Treat the CRM as the **single source of truth** for deal stage, amount, expected date,
  activity, and Next Action. slide-forge's `account.json` is a working ledger for material
  generation, and does not replace the CRM.
- Store contracts and formal documents received from the customer in the managed folder tied to the deal
- Keep the customer name, deal name, date, amount, and stage consistent across the CRM, meeting minutes, and files
- When a stage changes, register the required deliverables and a **link to the transition evidence**
- Before sharing with a partner, confirm the sharing permissions, NDA, purpose, and re-sharing rights for customer information

### Where things live in slide-forge

```
<Drive ルート>/<AE 名>/<顧客名>/
  00_活動計画/   活動計画デッキ（URL 不変で更新）、account.json のコピー
  01_顧客提示/   顧客提示用
  02_顧客提案/   顧客提案用（正式提案・見積）
  90_社内/       社内説明用（訪問計画・WPS・Deal Desk・稟議）
```

The contents of `00_活動計画` and `90_社内` are **never given to the customer**. When
sharing with the customer, share the files in `01_顧客提示` / `02_顧客提案` individually.
