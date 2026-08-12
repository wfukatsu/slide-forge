---
name: b2b-account-maps
description: >-
  Build the two account maps a B2B software deal turns on: an influence map of
  the buying committee (who decides, who blocks, who can be moved) and a
  discovery map of what is confirmed versus still assumed. Use when asked to map
  stakeholders, a buying committee, decision makers or an approval path; to
  qualify or review a deal (MEDDPICC, discovery, pipeline review); to work out
  what is still unknown before writing a proposal; or to turn hearing notes and
  meeting minutes into those maps as slides. Produces slides from the
  `b2b-sales` templates in `slide-templates/`. Route the proposal deck itself to
  `scalar-proposal-slides` or `google-slides-template`, and new reusable page
  templates to `slide-template-creator`.
---
*[日本語](SKILL.ja.md)*

# B2B Account Maps

Two maps, one purpose: knowing whether this deal can actually close, and what
to do next. The influence map answers **who**; the discovery map answers **what
we still do not know**.

Run all commands from the slide-forge repository root. Use `.venv/bin/python`.

## Boundaries

| Request | Route |
|---|---|
| Who decides / who blocks / approval path | this skill |
| What is confirmed vs assumed, what to ask next | this skill |
| The customer-facing proposal deck | `scalar-proposal-slides` / `google-slides-template` |
| A new reusable one-slide template | `slide-template-creator` |
| Visual check of a generated deck | `slide-qa` |

These maps are **internal working artifacts**. They record judgements about
named individuals at a customer, so do not hand them to the customer and do not
paste them into a proposal deck.

## The eight pages

All live in the `b2b-sales` pack (`slide-templates/b2b-sales/`).

| Template | Answers |
|---|---|
| `influence-map` | Who has to be moved for this to get decided (two axes: influence × for/against) |
| `buying-committee` | Who is involved, and how far have we gotten access to them |
| `decision-structure` | In what order does approval move up, and where does it stall |
| `discovery-map` | What is confirmed, and what is still a hypothesis |
| `pain-chain` | Which executive-level number does the frontline problem actually move |
| `discovery-gaps` | Who to confirm what with next |
| `influence-map-org` | Who reports to whom, and where influence and support concentrate (org structure) |
| `discovery-map-tree` | What the customer's goal rests on, and where our offering lands (Goal/Strategy/Tactics) |

```bash
.venv/bin/python scripts/list_slide_templates.py --pack b2b-sales
```

A worked deck using all eight against one fictional account is
`examples/b2b-account-review.json` — cover, exec summary, the two maps and
their supporting pages, in the order a review actually runs:

```bash
.venv/bin/python scripts/build_deck.py \
    --template templates/scalar-2026.json --spec examples/b2b-account-review.json --dry-run --strict
```

Use the pair that fits the ask. A pipeline review usually wants
`discovery-map` + `discovery-gaps`; a stalled deal usually wants
`influence-map` + `decision-structure`.

### The two structural pages, and cases with many stakeholders

`influence-map-org` and `discovery-map-tree` show **connections**. Where the
two-axis `influence-map` shows "whose influence is greatest," these show "who
reports to whom." Where MEDDPICC's `discovery-map` shows "what is confirmed,"
these show "what supports what."

Both are built from a single JSON. Once stakeholders/items exceed 9, do not
cram them onto the slide — **output the full graph to draw.io, and put an
extracted version on the slide**:

```bash
.venv/bin/python scripts/build_account_graph.py <graph.json> --out out/<account>.drawio
.venv/bin/python scripts/drawio_export.py out/<account>.drawio --out out/<account>.png --scale 2
```

Extraction is done by `account_graph.extract()`. People/items that were
dropped are printed to stdout, and their count must always be written into
the template's `more` slot as "see the draw.io version for the other N."
The data model and extraction rules are in
[references/account-graphs.md](../../references/account-graphs.md).

## Workflow

### 1. Intake

Work from what the user already has — hearing notes, meeting minutes, CRM
exports — before asking anything. Then ask only for what is missing, in one
round:

- which map is wanted, and for which account and opportunity;
- the people already met, with role and what they actually said;
- the customer's own numbers for the problem, if any surfaced;
- the deal's current stage and the decision or date being chased.

Do not invent people, titles, or positions. A stakeholder nobody has met is
`missing` on the discovery map, not a neutral dot on the influence map.

### 2. Separate what was heard from what was inferred

Go through the material once and label every statement: **said by the customer**,
**observed** (a document, an org chart, a sent quote), or **assumed by us**.
Only the first two can become `confirmed`. This pass is what makes the maps
worth anything — read
[discovery-map.md](references/discovery-map.md) for the status rules.

### 3. Place people, and say why

For the influence map, place each person on influence (vertical) × stance
(horizontal) and be able to name the evidence for both coordinates. Influence
is what actually moved a past decision, not seniority.
[influence-map.md](references/influence-map.md) covers the buying roles,
how to read stance from what was said, and the common traps.

### 4. Author and validate offline

Render a template with the account's data, then validate before generating:

```bash
.venv/bin/python scripts/render_slide_template.py \
  --template influence-map --data out/<account>-influence.json --out out/<account>-slide.json
.venv/bin/python scripts/build_deck.py \
  --template templates/scalar-2026.json --spec out/<account>-deck.json --dry-run --strict
```

The audit catches bubbles that cover each other's labels, table rows that do
not match their headers, and text that overflows. Fix the data — usually by
shortening a label or separating two people who sit on the same spot — rather
than the template.

### 5. Generate and check

Generate, then run `slide-qa` on the result. On the influence map, check the
squint test: the person to move next should be the first thing seen.

Both graph pages need one check the offline audit cannot make for you.
**Enlarge a connector and confirm it touches the card.** A card is three
stacked cells and only the middle one is full width — the tier badge is
right-aligned, the influence and owner bands left-aligned — so a line aimed at
the card's outer edge lands in the blank beside a band and the page reads as
though nothing is connected. The figures attach to the body box for exactly
this reason; verify it survived any change to the card design. Same check on
the `.drawio`, where an edge must take the body cell id and not the group's
([references/account-graphs.md](../../references/account-graphs.md)).

Then read the page as a whole: every card reachable from the top, no arrow
crossing a card it does not belong to, and the omission note present whenever
`extract()` dropped anything.

### 6. Report

Report the account, which maps were produced, the deck URL, and — the part that
matters — **the shortest list of things that must be confirmed next**, taken
from `discovery-gaps`.

## Rules

- **Evidence or nothing.** Every position and every `confirmed` needs a source:
  who said it, when. `source` slots are required for exactly this reason.
- **Do not turn absence into neutrality.** Unmet stakeholders belong in the
  gaps, not in the middle of the map.
- **Influence is demonstrated, not titled.** Place on evidence of past
  decisions.
- **A pain chain is a causal claim.** Each link needs its own support; say so
  when a link is the customer's estimate rather than a measurement.
- **Keep the maps current or delete them.** A stale influence map is worse than
  none — it launders old assumptions as fact.
- Store working files under ignored `out/` paths, never in the repository.
