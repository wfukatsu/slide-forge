*[日本語](deck-outlines.ja.md)*

# Deck Structure Templates

Before "what diagram to draw" comes "what order to talk in." Standard deck
structures and a mapping of the components each section uses. You may thin
out the structure, but **keep the order** (if the points supporting the
conclusion don't come first, the later slides have nothing to stand on).

The procedure for deciding which one to use through dialogue is in
`references/interactive-intake.md`. The headings here become the choices
directly.

| Type | Best fit | Standard page count |
|---|---|---|
| [Problem-Solving Proposal](#problem-solving-proposal-sales-and-deployment-proposals) | Sales / deployment proposals. Starts from the counterpart's challenges | 12–20 |
| [New Business / Initiative Internal Proposal](#new-business-and-initiative-internal-proposal-ringi-approval) | Ringi approval, investment decisions. Read by approvers | 20–60 |
| [Product and Service Introduction](#product-and-service-introduction) | First visit, product explanation | 10–20 |
| [Conference Talks and Study Sessions](#conference-talks-and-study-sessions-technical-deep-dive) | External talks, internal study sessions | 15–30 |

---

## Problem-Solving Proposal (Sales and Deployment Proposals)

The most commonly used type. **Start with the counterpart's challenges and
put your own company's story later.** A deck that opens with "Our
company…" gets closed before anyone reads it.

| # | Section | Main slides and components used |
|---|---|---|
| 0 | Cover and agenda | `COVER` + `table` (table of contents) |
| 1 | Background and current state | `before_after`, `icon_flow` (current workflow), `metric` |
| 2 | Challenges | `cards` (narrow down to 3 points), `hbars` / `vbars` (quantify the size of the challenge), `iceberg` (visible problems and root causes) |
| 3 | Approach | `flow` / `steps` (overview of the approach), `layers` (composition), `cloud_zone` + `cloud_icon_row` (architecture diagram) |
| 4 | Expected impact | `vbars_grouped` (before vs. proposed), `metric`, `table` (breakdown of quantitative impact) |
| 5 | Timeline | `gantt`, `journey` (phases) |
| 6 | Team and cost | `orgchart`, `table` (cost items), `vbars_stacked` (cost breakdown) |
| 7 | Next steps | `flow` (what to decide today → until next time) |

- **Limit challenges to 3 points.** Listing 5 dilutes all of them.
- For impact figures, **always attach the calculation basis in `label`**.
  If there's no basis, don't write the number.
- A deck that doesn't touch on cost won't reach a decision. Show at least a
  rough range.

---

## Product and Service Introduction

| # | Section | Main slides and components used |
|---|---|---|
| 0 | Cover | `COVER` |
| 1 | Customer challenges | `cards`, `icon_flow` |
| 2 | Product positioning | `posmap`, `venn` (value proposition) |
| 3 | Key features (3) | `asset_icon_cards` / `cards` |
| 4 | Architecture | `layers`, `cloud_zone` + `cloud_icon_flow`, `code_block` |
| 5 | Case studies | `testimonial`, `metric`, `before_after` |
| 6 | Next steps | `flow`, `journey` |

- **Fix the number of key features at 3.** A full feature list belongs in
  the Appendix, not here.
- In Japanese-language decks, don't label the feature band "Value
  Proposition" — use the Japanese term 特長 instead.

---

## Conference Talks and Study Sessions (Technical Deep Dive)

Use Presentation-family layouts (`CONTENT_PRESENTATION` /
`TITLE_ONLY_PRESENTATION`). **One message per slide.** This isn't meant to
be read like a document, so keep body text to at most 3 bullet lines.

| # | Section | Main slides and components used |
|---|---|---|
| 0 | Cover and self-introduction | `COVER`, `asset_icon` + `cards` |
| 1 | What we'll cover today | `table` (agenda), `flow` |
| 2 | Context and background | `icon_flow`, `timeline` |
| 3 | Main content (3–5 chapters) | Divide chapters with `SECTION`. Per chapter: `layers` / `code_block` / `linechart` |
| 4 | Demo and examples | `code_block`, `cloud_icon_flow` |
| 5 | Summary | `cards` (3 takeaways) |
| 6 | References | `table` (list of URLs) |

- Insert a `SECTION` between chapters. Without it, the audience loses track
  of where they are.
- Trim code down to **an amount readable on screen** (see the height
  estimate in `references/code-blocks.md`).

---

## New Business and Initiative Internal Proposal (Ringi Approval)

Source: the 15-section structure from 才流 (Sairu)'s "New Business Internal
Meeting Presentation Template," mapped onto this skill's components. A deck
aimed at internal approval follows the order "Market potential →
Competition → Revenue → Risk → Team," preemptively addressing the
approvers' concerns.

| # | Section | Main slides and components used |
|---|---|---|
| 0 | Cover and agenda | `COVER` layout + `table` (2-column table of contents) |
| 1 | Background | `before_after` (current state → impact of the new business), `cards` |
| 2 | Challenges and market potential | `table` (customer interviews, purchase examples), `cards` + `arrow` (pain points → challenges) |
| 3 | Target and market size | `posmap` (segmentation), `table` (persona comparison), `nested_circles` (TAM/SAM/SOM), `linechart` (market trend) |
| 4 | Business overview | `lean_canvas`, `cards` (pricing plans), `venn` (value proposition), `table` (elevator pitch, journey map), `pyramid` (measures by customer segment), `steps` (staged rollout design) |
| 5 | Voice of the customer | `testimonial`, `cards` + `arrow` (voices → insights) |
| 6 | Competitive landscape | `table` (competitor list, KBF comparison), `posmap` (2 slides: current state / after entry) |
| 7 | Schedule | `flow` or `journey` (mid- to long-term roadmap), `table` (list of initiatives), `gantt` (execution plan) |
| 8 | Profitability | `vbars` / `linechart` (P&L, sales plan), `flow` + `metric` (KPI chain), `table` (KPI detail) |
| 9 | Investment and cost | `table` (list of cost items), `vbars_stacked` (cost breakdown over time) |
| 10 | Risk and exit line | `linechart` (best / worst case scenarios), `cards` + `arrow` (factors → countermeasures) |
| 11 | Team structure | `orgchart` (project structure), `table` (role assignments) |
| 12 | Execution approach | `orgchart` (post-expansion structure), `table` (division of work) |
| 13 | Related regulations | `table` (Q&A format) |
| 14 | Voices of key people and experts | `testimonial` |
| 15 | Alignment with company-wide strategy | `cards` + `arrow` (mid-term plan goals → contribution) |

Usage tips:

- Use the `SECTION`-role layout for section breaks (don't draw them
  yourself).
- Sections 8–10 are what approvers look at first. Always attach a source or
  calculation basis for numbers in `label`.
- Splitting the positioning map into "current state" and "after entry (with
  our company)" conveys the impact of entry (don't cram it into one
  slide).
- All 15 sections together run to 60+ slides. For a 15-minute board
  meeting, narrow down to sections 1, 3, 4, 8, and 10, and move the rest to
  the Appendix.

### Use the business-plan pack for revenue, investment, risk, and structure

Sections 8-12 take the same shape every time, so `slide-templates/business-plan/`
carries eight ready-made templates. Fill semantic slots instead of recomposing
from primitives:

| Section | Template | What it answers |
|---|---|---|
| 8 Profitability | `revenue-plan` | What revenue and profit in each year, and when it turns profitable |
| 8 Profitability | `sales-buildup` | Which drivers add up to planned revenue, and which one it depends on |
| 9 Investment and cost | `cost-structure` | How much is needed, and what the money is spent on in what order |
| 9 Investment and cost | `break-even` | How much must be sold to stop losing money, and how much room the plan has |
| 9 Investment and cost | `roi-payback` | When the money is recovered, and whether it holds up as an investment |
| 10 Risk | `scenario-comparison` | How far results move when assumptions move, and whether the worst case is acceptable |
| 10 Risk | `risk-register` | What could break the plan, how it is handled, and what makes us stop |
| 11-12 Structure | `execution-structure` | Who executes it, and how many people each role needs |

```bash
.venv/bin/python scripts/render_slide_template.py \
    --template revenue-plan --data my-pl.json --out out/pl.json \
    --density print          # print = written plan, presentation = board meeting
```

The numeric tie-outs are stated in each template's guardrails. Always hold them:
the total of `sales-buildup` equals revenue in `revenue-plan`, personnel cost in
`cost-structure` equals the headcount in `execution-structure`, and the base case
of `scenario-comparison` equals `revenue-plan`.
