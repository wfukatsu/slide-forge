---
name: scalar-account-planning-session
description: >-
  Build the Account Planning Session (APS) decks for a customer a Scalar
  Account Executive already keeps a ledger for: a full Plan Document for the
  account team and a nine-page executive review deck, from one aps.json.
  Works out who to meet next per legal entity from published officer lists
  and org charts, ties the proposals to the customer's own mid-term
  management plan, and gives a chapter to each deal. Use for an APS
  (an annual/semi-annual account review, or executive review materials), or
  when asked to map a customer group's organisation, officers or key people.
  The per-visit ledger and the activity-plan deck stay in
  `scalar-account-plan`; one visit's materials go to `scalar-ae-materials`.
---

*[日本語](SKILL.ja.md)*

# Scalar Account Planning Session

APS is an **annual/semi-annual account review**, not the activity plan
(`scalar-account-plan`) that gets updated after every visit — the two differ
in lifespan and input, so don't mix them.

| | Activity plan deck | APS deck (this skill) |
|---|---|---|
| Purpose | Where things stand now and what to do next | Annual/semi-annual review and executive review |
| Update cadence | Every visit | Every APS |
| Input | `account.json` (the ledger) | `aps.json` (the ledger + the customer's public information) |
| Skill | `scalar-account-plan` | This skill |

**A ledger is a prerequisite.** How to build the ledger, verify it, and turn
unknowns into actions is covered in
[`scalar-account-plan`](../scalar-account-plan/SKILL.md) §1–4.
**This skill does not redefine any of that.**

The working directory is the slide-forge root. Commands run via
`.venv/bin/python`.

The source for judgment calls is
[references/scalar/sales-playbook.md](../../references/scalar/sales-playbook.md).
Page definitions and the judgment criteria for each page are in
[references/account-planning-session.md](../../references/account-planning-session.md).
**Neither is redefined by this skill.**

> [references/account-planning-template-plan.md](../../references/account-planning-template-plan.md)
> is a **plan document that is not yet implemented**. There is no
> `slide-templates/account-planning` pack; the real thing runs on
> `LAYOUT` + `aps.json`. Only the master-independent design contract (§2) and
> the column-width floor are current spec — the template list is a future
> idea.

## Boundaries

| Request | Goes to |
|---|---|
| Create / update APS materials | This skill |
| Create/append the ledger, answer status questions | `scalar-account-plan` |
| Materials for a single visit / WPS / Deal Desk | `scalar-ae-materials` |
| Drawing a stakeholder map / discovery map itself | `b2b-account-maps` |
| The formal proposal document for the customer | `scalar-proposal-slides` |
| Visual inspection of a generated deck | `slide-qa` |

## This is internal material

APS records judgments about named individuals (influence, for/against,
uncontacted, career history, personal relationships). **Never hand it to the
customer or a partner.** On Drive, `00_活動計画` and `90_社内` are also not
shared.

## Deliverables and where they live

| Deliverable | Contents | Audience |
|---|---|---|
| Plan Document | All pages: analysis, a chapter per deal, execution plan | The account team |
| APS review deck | 9-page main deck + Appendix | Executive review (30 min) |

```
accounts/<AE>/<顧客>/
  account.json   Per-visit facts (managed by scalar-account-plan)
  aps.json       APS deck content (headings, figure contents, deals, officer roster, section-divider considerations)
                 ★ Both are gitignored. Never commit these
```

**Never write the customer's name or real names into the script.**
`build_account_planning.py` only holds figure types, coordinates, and
formatting (`LAYOUT`); all strings are read from `aps.json`.

## Workflow

### 1. Fill in the aps.json fields

Some fields cannot be filled from the ledger alone. **Follow the order.**

1. Take whatever can be taken from the ledger (`account.json`)
2. For anything missing, take it from the **customer's public information**
   (IR materials, org charts, mid-term management plan, earnings summary).
   Once taken, write it back into the ledger's `facts` as `observed`
3. Anything still unobtainable gets **marked "not yet obtained."** Never fill
   it with a guess

The officer roster and org chart are the core of step 2 (§4, §5).

### 2. Tie it to the mid-term management plan

The mid-term plan is **the priority the customer published themselves.** If
a proposal can be connected to it, the language used in the internal
approval process becomes the customer's own language.

- **Take the original text from primary sources.** The mid-term plan's
  release PDF and the relevant IR page. Do not substitute a summary article.
  Put the original wording directly on the slide (paraphrasing breaks the
  connection)
- **Look at the pillar structure.** Whether IT sits under the business
  strategy or is placed as a parallel pillar **changes the approval route.**
  If parallel, you can move on the CIO line without waiting for business-side
  agreement
- **Tie at the statement level, not the pillar level.** Anchor to the
  specific sentence describing "what changes and how," not to a pillar
  heading like an investment figure
- **Don't force a tie that doesn't exist.** A proposal that can't be tied is
  itself information — it means it isn't riding on the customer's priorities
  — and that becomes material for reworking the proposal or judging its
  timing

Output is 2 pages (both `mece_tree`):

| Page | What it shows |
|---|---|
| Mid-term management plan structure | Relationship between pillars; where IT sits |
| Tying the mid-term plan to the proposal | Mid-term plan statement (original text) → our proposal, connected to the main deck by deal number |

### 3. When the counterpart is a corporate group

When facing a group (bank, securities, card, IT subsidiary) rather than a
single parent company, **classify both deals and stakeholders by company.**
Different companies have different decision-makers and budgets — lumping
them together leaves you without a clear next move.

- **Number deals in group-company order** (`aps.json`'s `deals[]`) so deals
  for the same company sit next to each other
- **Give each deal its own chapter**: a section divider (company name / deal
  name / amount, timing, stage) plus 6 overview cards. **Keep the same
  template across every deal** so you can compare "what's missing where"
  across chapters
- **Treat the systems subsidiary separately.** It touches the whole group, so
  give it a page that separates the per-company owning division from the
  cross-cutting organizations (technology headquarters, AI promotion, etc).
  Covering the cross-cutting organization is not enough if you haven't
  reached the per-company implementation team — the deal won't move

### 4. Org charts come from primary sources, one page per legal entity

Read the org chart (PDF/PNG) on the customer's IR / company-information page
and overlay our touchpoints on it. **Never draw the org chart from ledger
titles alone** — departments with no touchpoint disappear from the diagram,
and you lose **the most important information: seeing where the blanks
are.**

**When facing a group, draw one page per legal entity.** Cramming the whole
group into one page flattens each company's department level and hides which
departments haven't been reached. Keep the holding company's group structure
chart separate from the operating company's and IT subsidiary's org charts.

- Org charts often exist only as PDFs or images. If unreadable, an
  organizational-change news release can substitute (it states new
  departments, renames, transfers)
- **Also pick up where people came from.** Personnel-transfer releases
  sometimes list the seconding origin, which reveals who actually controls
  that company's systems division

### 5. Find who to meet (the other half of APS)

An account plan is not a record of people already met. It is also **a
mechanism for surfacing who to meet next.** Looking only at the ledger
surfaces nothing but the people already reached.

**Take the officer roster per legal entity.** A corporate group discloses
officers separately for the holding company, operating company, and IT
subsidiary as distinct legal entities. Treating the group as one "customer"
loses track of which entity actually has the officer who owns
implementation.

Sources (all public information):

| What | Where from |
|---|---|
| Officer names and titles | Each entity's "company overview" / "officer list" |
| Title changes / new appointments | "Notice of officer changes" news releases |
| Department list | Org chart (§4) |
| Areas of responsibility | The holding company's CxO list sometimes states owned departments |

To do:

1. **Take the officer roster per legal entity and overlay our contact
   status.** Seeing contacted / not-contacted broken out by entity reveals
   which entity has thin coverage
2. **Always pick up dual appointments.** A holding-company CxO may also serve
   as a subsidiary director. **That becomes the shortest introduction path**,
   so note it on the org chart too
3. **Cross-reference the org chart against the officer roster.** The org
   chart tells you only "which departments exist"; the roster tells you only
   "who is an officer." **Public information often can't fill the link
   between department and officer, and that gap becomes the confirmation
   item itself** ("ask which department the officer owns")
4. **Anchor leads on people already contacted.** A "person to meet" with no
   traceable path ("via whom") is not actionable. If you can't state a
   starting point, build one first
5. **Treat the public roster as authoritative on titles.** If the ledger's
   title is stale, fix the ledger

Output is 2 pages:

| Page | Figure | What it shows |
|---|---|---|
| Officer layer and contact status by entity | `comparison` | Officer count, contacted, and uncontacted key figures per entity |
| People to meet and leads | Table (register) | Who / why / **via whom** / by when |

### 6. Career history and relationships

Once you know who to meet, pin down **what that person bases their judgment
on.** Title alone doesn't tell you where your explanation will land.

- **Trace the title history.** What positions a decision-maker held in the
  past, what they decided, and what they said publicly is the strongest
  material for predicting their current reaction. Sources: officer-change
  releases, newspaper personnel columns, interview articles
- **Pick up predecessors/successors, dual appointments, and secondment
  origins.** "Where is the predecessor now" and "does the holding company's
  officer also sit as the subsidiary's director" both become decision-making
  routes
- **Personal relationships (former boss, friend, faction) can only be
  obtained through meetings or internally.** Never mix these with public
  information — always separate them by source line. **The moment this kind
  of content enters the material, it can no longer leave the company**

Output is 2 pages:

| Page | Figure | What it shows |
|---|---|---|
| Key people's career history | `cards` | One card per person: title history and the judgment habits it reveals |
| Relationships among people | `influence_graph` + `links` | Dual appointments, predecessor/successor, and personal relationships overlaid on the report line |

`links` **can only connect people at the same hierarchy level** (crossing a
level breaks the build). Put cross-level relationships in the `more` note
instead.

Once stakeholders exceed 9 people, output the full version to draw.io.
Procedure is in [`scalar-account-plan`](../scalar-account-plan/SKILL.md) §7.
**Always use `--layout grouped` for a corporate group.**

### 7. Prefer figures over tables

Keep tables only for "registers" (items with an owner and a due date to
track later) and "judgment criteria." Everything else becomes a figure. The
mapping table is in
[account-planning-session.md §9.4](../../references/account-planning-session.md).

### 8. Generate the two decks

```bash
# 1. aps.json から 2 本の仕様を組む（plan.json / review.json）
.venv/bin/python scripts/scalar/build_account_planning.py \
    --aps "accounts/<AE>/<顧客>/aps.json" --out "out/account-plan/<顧客>/ap"

# 2. オフライン検証。両方通してから API を叩く
for f in plan review; do
  .venv/bin/python scripts/build_deck.py --template templates/scalar-2026.json \
      --spec "out/account-plan/<顧客>/ap/$f.json" --dry-run --strict || break
done

# 3a. 初回。plan / review を別々のデッキとして作る（2 本とも作ること）
.venv/bin/python scripts/build_deck.py --template templates/scalar-2026.json \
    --spec "out/account-plan/<顧客>/ap/plan.json" \
    --title "<顧客> Account Planning Session FY26" --folder <00_活動計画 の ID>
.venv/bin/python scripts/build_deck.py --template templates/scalar-2026.json \
    --spec "out/account-plan/<顧客>/ap/review.json" \
    --title "<顧客> APS レビュー資料 FY26" --folder <00_活動計画 の ID>

# 3b. 2 回目以降（破壊的。スナップショットが先）。2 本とも差し替える
for f in plan review; do
  .venv/bin/python scripts/snapshot_version.py "<$f のデッキ URL>"
  .venv/bin/python scripts/build_deck.py --template templates/scalar-2026.json \
      --spec "out/account-plan/<顧客>/ap/$f.json" --into "<$f のデッキ URL>"
done
```

**Write the two URLs into the ledger's `meta.decks.accountPlanningSession` /
`meta.decks.apsReview` by hand.** `build_account_planning.py` doesn't
read/write the ledger, so this step isn't automated.

**A page with insufficient material does not drop out automatically.** The
activity-plan deck silently drops pages that have no material, but if APS's
page order references a page ID missing from `aps.json`, the build stops
with an error.

**`aps.json`'s `meta.skipPages` is the first way to remove pages.** Only
edit the script's page order (`PLAN_A` / `REVIEW_*`) when changing the page
structure across all customers.

- A list of page IDs removes them from **both decks**; `{"plan": [...],
  "review": [...]}` removes them from **only the specified deck**
- This also applies to deal chapters (`deal-<deal number>`). If every page
  inside a chapter is skipped, **the section divider drops too**
- A nonexistent page ID or an invalid deck name stops the build with a
  `ValueError` (typos are never silently ignored)
- For pages skipped in both decks, it's fine to delete the data from `pages`
  too (leaving it in place keeps the option to bring it back)

**Per-customer structural decisions also live in `aps.json`'s `meta`**
(never hard-coded in the script):

| Key | What it decides | Example |
|---|---|---|
| `meta.dealExtraPages` | Appendix pages appended after a deal chapter's section divider (deal ID → page ID list) | `{"1": ["objective-ledger"]}` |
| `meta.reviewDealPages` | List of deal page IDs to include in the executive-review Appendix | `["deal-1", "deal-3", "objective-ledger"]` |

Page IDs are generic role names (`bank-orgchart` / `securities-orgchart` /
`itsub-orgchart` / `itsub-mapping`, etc) and never contain the customer's
name.

The `--into` prohibitions (e.g. never make the template master the
replacement target) are the same as
[`scalar-account-plan`](../scalar-account-plan/SKILL.md) §5.

### 9. Visual inspection and reporting

Check the thumbnails with `slide-qa`, then run `scripts/cleanup_qa.py` when
done.

```bash
.venv/bin/python scripts/drive_folder.py upload <00_活動計画 の ID> \
    accounts/<AE>/<顧客>/aps.json \
    out/account-plan/<顧客>/ap/plan.json out/account-plan/<顧客>/ap/review.json
```

Always include in the report:

1. Both deck URLs and the Drive folder URL
2. **Items filled in from public information** and **items still left as
   "not yet obtained"**
3. **Who to meet next** (who, via whom, by when)
4. Any titles/facts that diverged from the ledger (whether to fix the ledger
   is the AE's call)

## Pitfalls

- **There is one constraint that passes `--dry-run` but still gets rejected
  by the API.** The Slides API rejects table columns narrower than 32pt
  (0.45in). This bites on narrow columns like deal numbers.
  `build_account_planning.py`'s `_check_columns()` checks for this at build
  time
- `batchUpdate` is atomic, so a mid-way failure never breaks the existing
  deck. Just fix it and rebuild
- **State any due date placed in APS explicitly in the source line as "the
  proposal made at this APS."** Leave the ledger's `actions` without a due
  date until the AE has agreed one with the customer, then enter it into the
  ledger

## Rules

- **Never fill in an answer.** Fields missing from the ledger get filled from
  public information or marked "not yet obtained." A field that can't be
  filled is itself pointing at something APS needs to decide.
- **Never stop at a record of people already met.** Derive **who to meet**
  from the public officer roster, with a lead anchored on someone already
  contacted. If no anchor can be stated, building one first is the action.
- **Separate public information from internal sources by source line.**
  Material containing personal relationships can never leave the company.
- **The ledger is the source of truth.** Facts learned during APS get
  written back into `account.json` too.
- Never commit `accounts/` (it contains customer names, personal names, and
  judgments). Keep working files under the gitignored `out/`.
