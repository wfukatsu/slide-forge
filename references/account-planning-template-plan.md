*[日本語](account-planning-template-plan.ja.md)*

# Account Planning Page Template Implementation Plan

Design and implementation plan for the page templates (`slide-templates/`)
needed to reproduce, in slide-forge, the pages from
`references/account-planning-session.md` (the 47 pages defined by `LAYOUT`
in the existing implementation `scripts/scalar/build_account_planning.py`).

## 1. Purpose and Scope

**Purpose**: register each page of the Account Planning Session as a
reusable template that can be generated just by plugging in customer data.
Furthermore, **make it track changes to the applied slide master's design
without rewriting the template side.**

**In scope**: the 34 new templates in the `slide-templates/account-planning/`
pack (§4), the reuse decisions for existing templates, the design contract
for tracking the master, and the validation procedure.

> Existing implementation reference: for one corporate group, the Account
> Planning deck is assembled directly from the ledger by
> `scripts/scalar/build_account_planning.py`. It isn't templated yet, but
> **each page's coordinates, column widths, and slot composition are
> measured values that have been through real generation and visual QA**,
> so copy from there when building the templates. Don't redecide the
> coordinates from scratch.

**Out of scope**: creating the slide master (`templates/`) → `template-forge`.
Deck generation itself → `google-slides-template`. Ledger design →
`scalar-account-plan`.

## 2. Design for Tracking the Master's Design

This is the core of this plan. Tracking involves 3 layers of differing
nature, each with a different way of achieving it.

### 2.1 How Far the Current Mechanism Auto-Tracks

slide-forge's division of labor already looks like this:

```
 template.json          assemble_spec.py        build_deck.py --template <master>
 （ページの構造）    →   （デッキ仕様）      →   （マスターを適用して生成）
  layout: BLANK                                   colorScheme → colors.Palette
  figures: [...]                                  レイアウト・ロゴ・フッター
  色は意味で指定                                   フォント
```

`scripts/colors.py`'s `Palette` builds diagram colors **from the applied
master's colorScheme**:

| Token | Derived from |
|---|---|
| `primary` | `accent5` |
| `success` / `danger` / `info` / `warning` | `accent1` / `accent2` / `accent3` / `accent4` |
| `text` / `muted` | `dark1` / `dark2` |
| `page` / `surfaceAlt` | `light1` / `light2` |
| `surface` / `border` | Derived from `primary` (lightness computation) |
| `series(n)` | Fixed-order series colors derived from the above |

**In other words, L1 (color/typeface) auto-tracks as long as the template
uses only semantic tokens.** Swapping the master is just a matter of
changing the `build_deck.py --template` argument — the template itself is
never touched.

```bash
# 同じ spec を別マスターで生成する
.venv/bin/python scripts/build_deck.py --template templates/scalar-2026.json --spec out/ap/spec.json --dry-run --strict
.venv/bin/python scripts/build_deck.py --template templates/corporate.json    --spec out/ap/spec.json --dry-run --strict
.venv/bin/python scripts/build_deck.py --template templates/aixdevops.json    --spec out/ap/spec.json --dry-run --strict
```

### 2.2 The 3 Layers of Tracking

| Layer | What changes | How it's achieved | Status |
|---|---|---|---|
| **L1 color / typeface** | Brand color, text color, series colors, font | Automatic via `Palette`'s semantic tokens | **Implemented** |
| **L2 layout selection** | Placing covers, section dividers, etc. onto master-specific layouts | Selected via `slide.layout`. `compatibleLayouts` is **declaration-only and not validated** (not referenced anywhere in `scripts/`) | Partial |
| **L3 coordinates / density** | Shifting a figure's top/bottom edge for masters whose header/footer decoration thickness differs | `masterProfiles` (proposed below) | **Not implemented / added by this plan** |

### 2.3 Rules to Follow for L1/L2 (Required for All Templates)

- `slide.layout` should, in principle, be `BLANK`. Use a master-specific
  layout only when the page depends on the master's decoration (cover,
  section divider). In that case, list the corresponding master's layout
  names in `compatibleLayouts`. Note that this key is currently **only a
  declaration for humans and isn't validated by tooling**; actual
  compatibility is guaranteed by the cross-master validation in §2.5.
- **No hardcoding brand RGB values.** Don't write a literal value like
  `#0B5FFF` into `template.json`. Pass semantic tokens to the Canvas
  primitives.
- **Don't reference the master's object IDs.** Don't write an ID like
  `g1b3a74d17bb_0_0` into the template.
- Assume a page size of 10 × 5.625in (16:9).
- Follow the measured values in `references/layout-contract.md` for the
  safe area:

  ```
  X0 = 0.5   W = 9.0   XE = 9.5
  タイトル       y 0.42 〜 0.48（1 行厳守）
  図の描画領域   y 0.84 〜 4.30（DY0 / DY1）
  要点行         y 4.38（NY）
  出典・補足行   y 4.86（EY）
  y 5.197 以降   マスターのロゴ・フッター領域。触らない
  ```

- Keep the title within 30.5 full-width-equivalent characters (measurable
  with `deckkit.em()`). If it wraps to 2 lines, it exceeds `DY0` and
  overlaps the figure — the most common failure mode.
- Validate representative strings in both Japanese and English. Japanese
  overflows first because of its full-width character width.
- **Table column widths must be 0.45in (32pt) or more.** The Slides API
  rejects columns under 32pt via `updateTableColumnProperties`. This can't
  be caught by `--dry-run` — the 400 only comes back at real generation.
  This is hit when creating a narrow column such as a number column.

Until this lower bound is added to `slide_templates.py`'s validation,
compute the actual size yourself from `colWidths`'s total and width and
check it on the template side (`scripts/scalar/build_account_planning.py`'s
`table()` is a reference implementation).

### 2.4 L3 Proposal: `masterProfiles`

Even at the same 10 × 5.625in, the thickness of the top decoration band or
footer differs by master. Since the current schema is 1 template = 1
geometry, figures get squeezed on masters with thick decoration. To absorb
this, we propose a **backward-compatible additional key**.

```jsonc
{
  "id": "blueprint-map",
  "slide": {                       // 既定ジオメトリ（従来どおり。必須）
    "layout": "BLANK",
    "figures": [ /* ... */ ]
  },
  "masterProfiles": {              // 任意。マスター名 → 差分パッチ
    "corporate": {
      "figures": {
        "1": { "y": 1.75 },        // インデックス指定で該当 figure のキーだけ上書き
        "3": { "y": 4.70 }
      }
    }
  }
}
```

Required changes:

| File | Change |
|---|---|
| `scripts/slide_templates.py` | Add an argument to `render_template(template, data, master=None)`. Deep-merge `masterProfiles[master]` into `slide` before resolving slots. If `master` is unspecified, behavior is exactly the same as today |
| `scripts/render_slide_template.py` | Add `--master <name>` (default geometry if omitted) |
| `scripts/validate_slide_templates.py` | For every declared profile, render → run `build_deck.py --dry-run --strict`. An unregistered master name or a reference to a figure index that doesn't exist in the default is an error |
| `references/template-schema.md` | Add a `masterProfiles` section |

Design constraints:

- `masterProfiles` is **limited to geometry and density parameters**
  (`x` / `y` / `w` / `h` / `size` / `rowH` / `colWidths`). Adding, removing,
  or changing the type of a figure is not allowed. Allowing it would branch
  the template and make it unmaintainable.
- Colors can't be written (there's no need — they auto-track via L1).
- For a master without a profile, the default geometry is used.

**Alternative (if L3 isn't implemented)**: build every template to fit the
safe area of the master with the thickest decoration. Implementation cost
is zero, but masters with thin decoration end up with excess margin. Since
this affects all 34 templates, it's worth implementing in F2 (§6).

### 2.5 Running Cross-Master Validation Like CI

`validate_slide_templates.py` lets you **swap the master used for
validation** via `--deck-template` (default is `templates/blank-16x9.json`).
Regression testing of master tracking can be run entirely with this one
tool.

```bash
# パック全体を、マスターを変えながら検証する
for m in blank-16x9 scalar-2026 corporate aixdevops; do
  echo "== $m"
  .venv/bin/python scripts/validate_slide_templates.py \
    --pack account-planning --deck-template "templates/$m.json" || exit 1
done
```

**Passing dry-run is not proof that nothing is broken.** Only count it done
once you've gone all the way through real generation → visual thumbnail
inspection (`slide-qa`). Inspect visually with at least `scalar-2026` and
one master whose color tone is furthest away.

## 3. Reuse Decisions for Existing Assets

Always check before creating a new ID:

```bash
.venv/bin/python scripts/list_slide_templates.py
.venv/bin/python scripts/list_slide_templates.py --tag account
```

| AP page | Existing candidate | Verdict |
|---|---|---|
| SWOT Analysis | `marketing-analysis/swot-analysis` | **Reuse as-is** |
| Influence Map | `b2b-sales/influence-map`, `influence-map-org` | **Reuse as-is**. Use `-org` if the org hierarchy is available |
| Action Plan | `scalar-ae/action-plan` | **Reuse as-is**. Only need to confirm the columns correspond to S.M.A.R.T. |
| Prioritization (2-axis) | `marketing-analysis/positioning-map` | **Needs verification**. Reuse if bubble diameter = 3-year potential amount can be expressed; otherwise create `prioritization-matrix` new |
| Blueprint Summary | `scalar-ae/challenge-hypothesis` | **New**. Too different in item count from a single challenge-hypothesis page (15 fields vs. 5 fields) |
| Vision/Strategy for Growth | `scalar-ae/win-plan` | **New**. win-plan is the winning path for an individual deal; this is the account's 3-year growth vision |
| Challenges & Risk | `scalar-ae/bant-risk` | **New**. Generic challenge × mitigation not limited to the 4 BANT axes. Doesn't replace bant-risk |
| 3 Year Execution Plan | `scalar-ae/activity-timeline` | **New**. activity-timeline is past activity history; this is the 3-year future milestones |
| Account Health | — | New |
| Strategy Map | `b2b-sales/discovery-map-tree` | **Needs verification**. The hierarchical-tree primitive might be reusable. The template itself is new |

Decision criterion: "does it answer the same question with the same visual
grammar?" If yes, reuse; create a new ID only when the slots or visual
structure are substantively different.

## 4. New Template Specifications (34 items)

Pack name: `account-planning`. Default `schemaVersion: 1`,
`status: experimental`, `compatibleLayouts: ["BLANK"]` for all items.

Slots common to all templates:

| Slot | Type | Required | Description |
|---|---|---|---|
| `title` | `string` (≤70) | ○ | A title stating the conclusion. Don't put a topic name |
| `source` | `string` (≤160) | ○ if numbers are included | Source, period, unit, FX assumption |

### P0 — Making the Session Materials' 9 Pages Work (9 items)

#### 4.1 `corporate-overview` — Corporate Overview
- Question answered: what kind of company is this customer, and what
  challenges does management face?
- `inferenceLevel`: `descriptive`
- Skeleton: D (upper/lower 2 rows). Profile + business overview on top,
  management challenges below
- Slots: `profile` `tuple[]` (item name, value; 4–8) / `description`
  `string` (≤240) / `challenges` `string[]` (3–5, each ≤80) /
  `competitors` `string[]` (0–6) / `exec_quotes` `tuple[]` (speaker,
  statement; 0–3)
- guardrails: state the source (earnings call, article, etc.) and timing
  for executive statements / a state where only the profile fields are
  filled in is incomplete

#### 4.2 `strategy-map` — Customer Management Strategy Map
- Question answered: how does the customer's Goal / Strategy / Tactic /
  Initiative chain together?
- `inferenceLevel`: `strategic`
- Skeleton: A (full width). A 3–4 layer hierarchical tree, each node
  labeled with the requesting role
- Slots: `layers` `string[]` (layer names, 3–4) / `nodes` `array`
  ([layer index, label, requesting role, confidence]; 6–24) / `edges`
  `array` ([parent index, child index])
- guardrails: set hypothesis nodes to `confidence = "hypothesis"` so
  they're visually distinguished / mark an initiative `confirmed` only when
  it's tied to the customer's public information or their own statement
- Dependency: the hierarchical-tree primitive (verify whether
  `discovery-map-tree` can be reused first)

#### 4.3 `footprint-heatmap` — Adoption Status Heatmap
- Question answered: how far in are we per layer today, and how far are we
  targeting 3 years out?
- `inferenceLevel`: `descriptive`
- Skeleton: A. Rows = layer, columns = current state → 3 years out
  (arrow), initiative linkage, competitor notes
- Slots: `rows` `array` ([layer name, current 0–2, 3 years out 0–2, list of
  initiative numbers, notes]; 4–10) / `legend` `string[3]` (default:
  company-wide standard / has a foothold / no penetration)
- guardrails: the 3 values are only company-wide standard / has a foothold
  and growing / almost no penetration / verify the rating with internal
  product owners / SCs

#### 4.4 `initiative-solution-alignment` — Initiatives × Solutions
- Question answered: which of our capabilities addresses which of the
  customer's initiatives, and how?
- `inferenceLevel`: `strategic`
- Skeleton: A. 3 vertically-aligned bands (customer initiatives → value
  delivered → key deal opportunities)
- Slots: `initiatives` `string[]` (3–6, each ≤40) / `capabilities`
  `string[][]` (value delivered per initiative, each 1–3) /
  `opportunities` `string[][]` (same, each 0–3)
- guardrails: a column that's just a product name isn't allowed. Write the
  value that addresses the customer's challenge

#### 4.5 `blueprint-map` — Proposed Theme List
- Question answered: what themes are we targeting, for how much, and when?
- `inferenceLevel`: `strategic`
- Skeleton: F (table only)
- Slots: `headers` fixed (theme name / customer challenge / proposed
  solution / product / why us / timing / amount) / `rows` `string[][]`
  (3–7 rows, 7 columns, each cell ≤60)
- guardrails: don't include a row with an empty customer challenge / write
  the amount's unit and basis in `source` / Close means the theme is
  agreed, not that the deal is won

#### 4.6 `initiative-prioritization` — Priority Score Table
- Question answered: which initiative do we pursue first, and on what
  basis?
- `inferenceLevel`: `strategic`
- Skeleton: F
- Slots: `headers` fixed (initiative / purpose & expected value /
  decision-making stage / key person / our alignment / 3-year potential /
  customer-side priority) / `rows` `string[][]` (3–7 rows, 7 columns)
- guardrails: write key people as sponsor / influencer / decision-maker
  with their role / only mark customer-side priority as "high" when it's
  based on the customer's own statement / internal only

#### 4.7 `execution-roadmap` — 3 Year Execution Plan
- Question answered: over 3 years, what happens when?
- `inferenceLevel`: `predictive`
- Skeleton: A. Period (12 quarters or 3 years) on the horizontal axis,
  themes as rows, with milestones placed on them
- Slots: `periods` `string[]` (4–12) / `tracks` `string[]` (2–6) /
  `milestones` `array` ([track index, period index, label, type])
- Types: event / executive visit / insight / joint study / roadmap
  development / deal close
- guardrails: leave a note on the slide that this is a projection, not a
  confirmed plan

#### 4.8 `account-strategy-summary` — 3 Year Account Strategy Summary
- Question answered: from the current state to 3 years out, what moves and
  how far?
- `inferenceLevel`: `strategic`
- Skeleton: D. The 3-year strategy statement and key transformation themes
  on top, current state / 3-years-out comparison below
- Slots: `strategy_statement` `string` (≤200) / `themes` `string[]` (2–5) /
  `dimensions` `string[]` (3–5, default: revenue / customer satisfaction /
  engagement / footprint) / `current` `string[][]` (`matchLength:
  dimensions`) / `target` `string[][]` (same)
- guardrails: **`current` and `target` must use the same set of items in
  the same order** (enforced via `matchLength`)

#### 4.9 `management-asks` — Asks to Management
- Question answered: what do we want from management, and what does it
  unlock?
- `inferenceLevel`: `strategic`
- Skeleton: F
- Slots: `headers` fixed (requested of / request content / why it's needed
  / expected outcome / deadline) / `rows` `string[][]` (1–5 rows, 5
  columns)
- guardrails: a row with an empty expected outcome doesn't qualify as an
  Ask / internal only

### P1 — Filling In the Plan Document (7 items)

#### 4.10 `account-health` — Account Health
- A scorecard of 4 dimensions × 5 metrics, plus a quarterly trend.
  Skeleton B
- Slots: `dimensions` `string[4]` / `metrics` `string[4][5]` / `scores`
  `integer[4][5]` (1–3) / `trend` `array` ([quarter, overall score]; 2–8)
- guardrails: a rating where every metric lands on the median isn't really
  a rating / put the rating criteria on a separate page

#### 4.11 `tam-sow-analysis` — TAM and SOW
- TAM by category and SOW baseline/target. Skeleton B (bars on the left,
  narrative on the right)
- Slots: `categories` `string[]` (2–6) / `tam` `number[]` (`matchLength:
  categories`) / `sow_baseline` `number[]` / `sow_target` `number[]` /
  `annual_revenue` `string` / `it_spend` `string`
- guardrails: TAM is an estimate. Replace it if the actual IT budget is
  disclosed, and note that in `source`

#### 4.12 `historical-spend` — Historical Spend
- Past 3 years of results by product. Skeleton B (stacked bars +
  narrative)
- Slots: `periods` `string[]` (2–5) / `series` `array` ([product name,
  value series]; 1–6, value series `matchLength: periods`) /
  `recurring_note` `string`
- guardrails: don't add annualized subscription amounts together with
  one-time revenue

#### 4.13 `growth-vision` — Growth Vision
- Description across 4 areas. Skeleton F or C
- Slots: `areas` `tuple[]` ([area name, description]; 3–5, description
  ≤200)
- Default area names: alignment with the customer's transformation goals /
  positioning of our focus areas / footprint expansion / Executive
  Engagement

#### 4.14 `blueprint-summary` — Single-Page Theme Detail
- 15 fields for one theme. Skeleton F (3×5 cell grid)
- Slots: `blueprint_name` `string` / `cells` `tuple[]` ([field name,
  content]; fixed at 15 items)
- Fields: customer transformation challenge / solution overview / product
  & key initiative / differentiator / benefit / roles involved / key
  initiative / partner / reference case / start date / expected close /
  business sponsor / IT sponsor / target business unit / current pipeline
  · 3-year potential · competitors
- guardrails: Close means the theme is agreed, not that the deal is won /
  raise the precision of the description as the stage advances

#### 4.15 `exec-engagement-plan` — Executive Engagement Plan
- Skeleton F. Columns: level / customer-side executive / our-side
  executive / frequency & date / current state and goal
- `rows` `string[][]` (2–8 rows, 5 columns)
- guardrails: contains real names. Internal only. Don't hand it to the
  customer or partners

#### 4.16 `event-plan` — Event Plan
- Skeleton F. Columns: event / timing / target customer / our-side key
  person / desired outcome
- `rows` `string[][]` (2–8 rows, 5 columns)

### P0b — Added by Cross-Checking Against the Source Material (15 items)

Gaps found by cross-checking the first version's 23 pages against
`FY17_AP_Template_Training_Public.pptx` page by page. Already implemented
in the existing implementation `scripts/scalar/build_account_planning.py`,
and **that page definition becomes the reference geometry when
templating**.

| ID | Source | What it adds |
|---|---|---|
| `customer-initiatives` | S44 | Initiative × **customer-side owner** × purpose/outcome × **the factor creating urgency** |
| `customer-programs` | S45 | The **customer's program / project layer** between initiatives and themes. Write it with real names |
| `strategy-map-step2` | S38 / S41 | Overlay proposed themes **onto the same map as Step 1**. Just add a 4th tier to `outcome_tree` |
| `objective-sheet` | S60 / S99 | Per-theme Customer Benefit / our contribution + **the "result" per year** (not the activity) |
| `challenge-requirement` | S77 / S105 | Challenge / Requirement / Owner / **due date** / Outcome |
| `health-criteria` | S31 / S32 | The rating criteria for each Account Health stage. A score alone can't be verified |
| `financial-trends` | S81 | The customer's performance trend and peer comparison. `metric` ×3 + `hbars` |
| `engagement-timeline` | S59 / S98 | An **8-week, weekly-granularity** timeline. A half-yearly `gantt` can't tell you whether you'll make the next gate in time |
| `scalar-footprint` | S84 | Line up the 4 products (ScalarDB / Saga / Analytics / ScalarDL) as `layers` and the 4 solutions (AI-driven development / RAG / AI-oriented data catalog / multi-cloud foundation) as `cards`, with the **presentation status** attached |
| `group-orgchart` | S80 | Overlay our touchpoints onto the customer group's official org chart |
| `itsub-orgchart` | S84 | The IT subsidiary's official org chart. **The value is in seeing which departments have no touchpoint** |
| `deal-portfolio` | S45 | Deal portfolio by group company (`mece_tree`) |
| `company-stakeholders` | S27 | Stakeholders by group company (`comparison`). Business-card-only contacts don't count as engaged |
| `subsidiary-mapping` | S84 | IT subsidiary ↔ each group company's ownership mapping (`comparison`). Separates cross-cutting organizations from per-company implementation teams |
| `deal-detail` | S51 / S52 | The overview of a single deal (6 `cards`). The body of each deal's chapter |

Fields also added to existing pages:

- **Heatmap**: the linked initiative number and a "competitor / assumption"
  column (S26). Since dots alone can't carry the rationale for the rating,
  `rating_matrix` was replaced with `table`
- **Executive Engagement Plan**: an **our-side executive counterpart**
  column (S64). If it's blank, write it as blank — that's where filing a
  Management Ask comes from
- **Action Plan**: assigned date and due date (S62). Tied to the Blueprint
  by theme number
- **Management Asks**: due date
- **TAM & SOW**: the customer's annual revenue and key competitors (S22 /
  S69)
- **Corporate Overview**: key competitors (S80's KEY COMPETITORS)
- **Blueprint Summary**: one theme per page. Don't combine them onto one
  page

### P0c — Replacing Tables with Diagrams

A run of tables makes every page look the same and buries the point.
**Keep tables only for "ledgers" (something with an owner and a due date
that's tracked afterward) and "rating criteria."** The mapping table is in
`references/account-planning-session.md` §9.4, "Where Tables Are Allowed."

The existing implementation went from 20 tables → 8 tables, replaced with
the following diagrams: `orgchart` / `outcome_tree` / `mece_tree` /
`layers` / `gantt` / `timeline` / `nested_circles` / `hbars` / `cards` /
`journey` / `before_after` / `influence_graph`. Use the same assignment
when templating.

**Always take the official org chart from primary sources.** Read the org
chart (PDF/PNG) on the customer's IR / company-information page and
overlay our touchpoints. Drawing up an org chart from ledger titles alone
makes departments with no touchpoint disappear from the diagram, **losing
the single most important piece of information: seeing the blank spots.**

Deliberately not adopted: the **Create / Evolve / Protect classification**
(S47) degenerates to all-Create while the footprint is 0 across every
layer. The **Appendix's collection of blank templates** (S79) is
unnecessary since a generation script exists.

### P2 — Speeds Up Discussion If Present (3 items)

#### 4.17 `flight-plan` — Flight Plan
- Horizontal axis = close timing, vertical axis = amount, bubble = theme,
  color = status. Skeleton A
- Slots: `bubbles` `array` ([theme name, period index, amount, status];
  2–10) / `periods` `string[]` / `statuses` `string[3]`
- guardrails: a projection. Always include a legend that distinguishes it
  from confirmed deals

#### 4.18 `revenue-projection` — 3 Year Financial Projections
- Skeleton B. Potential by year and by category
- guardrails: tally annualized values separately. State the assumptions
  (FX, period, unit) explicitly in `source`

#### 4.19 `risk-mitigation` — Challenges and Risk Mitigation
- Skeleton F. Columns: challenge / impact / mitigation / owner
- `rows` `string[][]` (2–8 rows, 4 columns)
- guardrails: doesn't replace `scalar-ae/bant-risk`. Use that one for risks
  that fit within BANT

## 5. Deciding on New Primitives

Prefer what already exists in `scripts/patterns.py` / `pages.py` /
`charts.py` / `illustrations.py`. **Only add a new primitive when all 3
conditions hold**: the same low-level drawing repeats across multiple
templates, the domain input needs function-level validation, and it can be
named and reused independently of any one template.

| Candidate | Templates using it | Verdict |
|---|---|---|
| Hierarchical tree (with layer labels) | `strategy-map` | Read `discovery-map-tree`'s implementation first. Not needed as new if reusable |
| 3-value heatmap row (with current→future arrow) | `footprint-heatmap` | **New candidate**. Add once there's a prospect of use in 2+ templates |
| Current/target comparison panel | `account-strategy-summary`, `growth-vision` | **New candidate**. Condition is met since it's used by 2 items |
| Bubble chart (3 variables + category color) | `flight-plan`, (`positioning-map` extension) | **Needs investigation**. `positioning-map`'s implementation may already suffice |
| Cell grid (field name + content lattice) | `blueprint-summary` | Only 1 item. Try substituting `table` first |

## 6. Implementation Phases

| Phase | Content | Outcome |
|---|---|---|
| **F0** Investigation | Read the implementations of `discovery-map-tree` / `positioning-map` / `action-plan` and settle whether they're reusable. Resolve the "needs verification" items in §3 | A finalized reuse-decision table |
| **F1** 9 P0 templates | Start with the table/band/comparison-panel group (4.4–4.6, 4.8, 4.9). The diagram group (4.2, 4.3, 4.7) waits on F0's conclusion | The Session Materials' 9 pages can be generated |
| **F2** L3 `masterProfiles` | The 4 file changes in §2.4. Make F1's 9 items the first profile targets | Master differences can be absorbed by the template |
| **F3** 7 P1 templates | Plan Document side | Fills in the Appendix |
| **F4** 3 P2 templates | Flight Plan, etc. | Visualizations for discussion are complete |
| **F5** Catalog and documentation | Generate the pack catalog and link to it from `skills/scalar-account-planning-session/SKILL.md` | Goes into operational use |

F1 and F2 are independent. F1 can ship without waiting for F2 (it works
with just the default geometry).

## 7. Acceptance Criteria

Each template only has its `status` raised above `experimental` once all
of the following are satisfied.

- [ ] `scripts/validate_slide_templates.py --id <id>` passes with zero findings
- [ ] `example.json` fills every required slot and stays within the declared limits
- [ ] `example.json`'s `source` **explicitly states that it's sample data**
- [ ] A template that includes numbers has a `source` slot
- [ ] `answers` (the question answered) and `inferenceLevel` are declared
- [ ] `guardrails` states the most likely misreading for that page
- [ ] Doesn't break when generated at the slot's minimum or maximum (boundary test)
- [ ] Doesn't break with representative strings in either Japanese or English
- [ ] Passes visual thumbnail inspection on **both** `scalar-2026` and one
      master whose color tone is furthest away (text overflow / overlap /
      contrast / footer collision)
- [ ] Contains no literal brand RGB values or master object IDs (confirm with grep)

## 8. Verification Procedure

```bash
# 単体
.venv/bin/python scripts/validate_slide_templates.py --id blueprint-map
.venv/bin/python scripts/render_slide_template.py \
  --template blueprint-map \
  --data slide-templates/account-planning/blueprint-map/example.json \
  --out out/blueprint-map.json

# パック一括（マスター横断。§2.5）
for m in blank-16x9 scalar-2026 corporate aixdevops; do
  .venv/bin/python scripts/validate_slide_templates.py \
    --pack account-planning --deck-template "templates/$m.json" || exit 1
done

# カタログ
.venv/bin/python scripts/build_slide_template_catalog.py \
  --pack account-planning --out out/account-planning-catalog.json

# 実生成 → ビジュアル QA → 後始末
.venv/bin/python scripts/build_deck.py \
  --template templates/scalar-2026.json --spec out/account-planning-catalog.json \
  --title "Account Planning テンプレートカタログ"
# skills/slide-qa/SKILL.md に従って目視
.venv/bin/python scripts/cleanup_qa.py
```

When you find a break, **fix the template, the example, or the shared
primitive — not the generated output — and regenerate.** Don't hand-fix
the generated slides.

## 9. Safety

- The `account-planning` pack has pages such as
  `initiative-prioritization`, `exec-engagement-plan`, `management-asks`,
  `account-health`, and `risk-mitigation` that contain **an individual's
  real name and internal judgments about that person**. Always write
  "Internal material. Don't hand it to the customer or partners." in these
  pages' `guardrails`.
- Customer data lives under `accounts/`. `accounts/` is outside Git's
  control. Don't put real customer data into a template's `example.json`.
- Always make `example.json` fictional data, and declare via `source` that
  it's a sample.

## 10. Open Issues

| # | Issue | Who decides | Rough deadline |
|---|---|---|---|
| 1 | Whether to implement `masterProfiles` (L3), or settle for the alternative of fitting to the thickest master | — | On F1 completion |
| 2 | Whether `positioning-map` can be reused for the Prioritization 2-axis (bubble diameter = amount) | — | F0 |
| 3 | Whether `discovery-map-tree`'s hierarchical primitive can be reused for `strategy-map` | — | F0 |
| 4 | Whether to fix the Session Materials' default page count at 9, or make it variable by account size | — | F1 |
| 5 | Whether to fold the `account-planning` pack into `scalar-ae`, or keep it as an independent pack | — | F5 |
| 6 | Whether to enforce `compatibleLayouts` with the validator, or leave it declaration-only | — | F2 |

## 11. References

- `references/account-planning-session.md` — the procedure and page definitions
- `skills/slide-template-creator/SKILL.md` — the template-creation workflow
- `skills/slide-template-creator/references/template-schema.md` — the schema
- `skills/slide-template-creator/references/design-rules.md` — skeleton, density, sources
- `references/layout-contract.md` — measured coordinates and safe area
- `references/slide-patterns.md` — the definitions of skeletons A–F
- `scripts/colors.py` — `Palette` (master colorScheme → semantic tokens)
- `scripts/scalar/build_account_planning.py` — the implemented page definitions (reference geometry)
