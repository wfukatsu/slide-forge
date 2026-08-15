---
name: scalar-ae-materials
description: >-
  Build the materials a Scalar Account Executive needs for one customer visit,
  chosen by deal phase and audience: the customer-facing one-pager that opens a
  conversation, the internal visit plan, the WPS win plan that asks for
  proposal investment, and the Deal Desk / internal-approval packet that asks
  for internal approval. Use when asked to prepare for a customer meeting or
  visit; to make materials for a phase-0..6 conversation; to write a visit
  plan, WPS, or Deal Desk material; to get internal resources or approval for
  a deal; or to produce customer-facing / internal-explanation materials.
  Files land under "AE name / customer name" in Drive and every run updates
  the account ledger. Route the standing activity plan to
  `scalar-account-plan`, the formal proposal to `scalar-proposal-slides`, and
  the stakeholder maps to `b2b-account-maps`.
---

*[日本語](SKILL.ja.md)*

# Scalar AE Materials

Use `references/scalar/workflow-contract.md` for shared safety, Drive,
approval, and QA rules. This skill owns only the routing and content rules for
a single visit or internal approval artifact.

**The same deal information must never be shown to everyone through a single
document.** This skill's job is to choose the material type from phase
(0–6) × audience (customer / internal) × purpose, and to build only a
document that satisfies that type's required content.

Working directory: the slide-forge root. Run commands with `.venv/bin/python`.

The source of truth for these decisions is
[references/scalar/sales-playbook.md](../../references/scalar/sales-playbook.md)
(phases and transition conditions in §2, the 5 material types in §3, quality
standards in §4, meeting bodies in §6).

## Boundaries

| Request | Where it goes |
|---|---|
| A full set of materials for one visit | This skill |
| Internal approval / resource acquisition (WPS / Deal Desk / internal approval) | This skill |
| Per-customer activity plan (standing, append-only) | `scalar-account-plan` |
| Annual Account Planning Session (org chart / deal review deck) | `scalar-account-planning-session` |
| Formal proposal / quotation | `scalar-proposal-slides` + `spreadsheets` |
| Stakeholder map / discovery map | `b2b-account-maps` |
| Scalar company/product introduction (not customer-specific) | `scalar-product-slides` |
| Visual inspection of a generated deck | `slide-qa` |

## Step 1: Settle the phase and the audience

**Read the ledger first.** If `accounts/<AE name>/<customer name>/account.json`
exists, the phase, stakeholders, and open items are in it. If it doesn't
exist, create it with Steps 1–2 of `scalar-account-plan`.

```bash
.venv/bin/python scripts/scalar/account_ledger.py validate <account.json>
.venv/bin/python scripts/scalar/account_ledger.py gaps <account.json>
```

Ask only about premises that cannot be pulled from the ledger, in one batch
via `AskUserQuestion` (following the conventions in
`references/interactive-intake.md` §0 and §5):

1. Who will you meet (title / department / first time)?
2. What one statement do you want to get from the customer in this visit?
3. Is there anything you want internally (approval of proposal investment /
   price approval / SA staffing)?

The shared workflow contract settles the QA choice; do not repeat it in this
skill's audience-specific question batch.

## Step 2: Choose the material type (routing)

| Audience / purpose | Phase | What to build | Location | Owner |
|---|---|---|---|---|
| Internal / pre-visit preparation | All | `visit-plan` | `90_社内` | This skill |
| Customer / start a conversation | 0–2 | `challenge-hypothesis` + case study | `01_顧客提示` | This skill |
| Customer / structure the challenge | 2 | Challenge structure diagram, As-Is overview, discussion points | `01_顧客提示` | This skill |
| Internal / decide on proposal investment (WPS) | End of 2 | `win-plan` + 3 maps | `90_社内` | This skill + `b2b-account-maps` |
| Customer / show feasibility | 3 | Demo materials, To-Be, architecture overview | `01_顧客提示` | `scalar-proposal-slides` |
| Customer / agree on a PoC | 3 | PoC proposal, implementation plan | `02_顧客提案` | `scalar-proposal-slides` |
| Internal / approve pricing and contract risk | 3–5 | Deal Desk materials, internal approval | `90_社内` | This skill |
| Customer / selection and budgeting | 4 | Formal proposal, quotation, ROI | `02_顧客提案` | `scalar-proposal-slides` + `spreadsheets` |
| Customer / contract procedures | 5 | Checklist, SOW, purchase order | `02_顧客提案` | `google-slides-template` |
| Internal / renewal and expansion planning | 6 | Health review, renewal plan | `90_社内` | `scalar-account-plan` |

Partner-facing / partner-proposal materials (the remaining 2 types in
playbook §3) have **no dedicated template implemented**. If requested, build
them with `google-slides-template`; pull the required items from playbook §3
and the source material §7.5.

Ask `AskUserQuestion` once, and only when you cannot decide. If the phase is
in the ledger and the audience is specified, decide without asking.

## Step 3: Check that customer-facing material isn't mixed with internal information (do not skip)

**Before** generating material to hand to the customer (`01_顧客提示` /
`02_顧客提案`), read the spec body and confirm the following:

- [ ] No judgments about an individual's influence, position, or "not yet
  contacted" status are included
- [ ] No competitor weaknesses are named (assume the customer will pass this
  along to the competitor)
- [ ] No unconfirmed item is written as if it were confirmed
  → Rephrase it as "would like to confirm today." Do not fill it in with a guess
- [ ] No figure without a source is included (cite sources for public case studies)
- [ ] Pricing / roadmap information is within what is allowed to be disclosed
  to this audience

The `challenge-hypothesis` guardrails say the same thing. If even one item
applies, move that content into a `90_社内` document instead.

## Step 4: Write the spec and validate it offline

Build pages that can be built from the ledger, from the ledger (don't
hand-copy):

```bash
.venv/bin/python scripts/scalar/account_ledger.py slots <account.json> visit-plan \
    --out out/<顧客名>/visit-plan.json
.venv/bin/python scripts/render_slide_template.py --template visit-plan \
    --data out/<顧客名>/visit-plan.json --out out/<顧客名>/visit-plan.slide.json
```

`visit-plan` is built from the `visits[]` entries in the ledger whose
`status` is `"planned"`. Write the visit's purpose, questions, and expected
objections into the ledger first, and the material follows from the ledger.

Pages not in the ledger (e.g. customer-facing case studies) are written from a
`slide-templates` template or a pattern from
`references/slide-pattern-catalog.md`. Assemble and validate:

```bash
.venv/bin/python scripts/assemble_spec.py out/<顧客名>/*.slide.json \
    --out out/<顧客名>/deck.json --title "<資料名>"
.venv/bin/python scripts/build_deck.py --template templates/scalar-2026.json \
    --spec out/<顧客名>/deck.json --dry-run --strict
```

If findings come back, **fix the data** (shorten the wording, separate
people). Don't fix the template.

## Step 5: Generate and place it in the correct folder

```bash
.venv/bin/python scripts/scalar/account_workspace.py ensure --ledger <account.json> --json
```

From the returned IDs, choose `--folder` per the Step 2 location table:

| Type | Folder |
|---|---|
| Customer-facing | `01_顧客提示` |
| Customer proposal | `02_顧客提案` |
| Internal explanation | `90_社内` |
| Activity plan | `00_活動計画` |

```bash
.venv/bin/python scripts/build_deck.py --template templates/scalar-2026.json \
    --spec out/<顧客名>/deck.json --folder <フォルダ ID>
.venv/bin/python scripts/drive_folder.py upload <フォルダ ID> out/<顧客名>/deck.json
```

**Never place it in the wrong folder.** If an internal document ends up in
`01_顧客提示`, an individual's private judgments go straight to the customer
when the folder is shared.

## Step 6: Material-specific QA

Apply the shared QA procedure. For customer-facing material, repeat the Step 3
leakage check against the rendered thumbnails.

## Step 7: Write back to the ledger (do not skip)

**Don't stop at making the visit materials.** Write back what you made and
what was decided in it to the ledger, and update the activity plan. This is
the only mechanism that keeps the visit materials and the activity plan from
drifting apart.

1. Add this visit to `visits[]` (`status: "planned"` before the visit;
   `status: "done"` with `heard` / `next` filled in after it happens)
2. Add newly learned facts to `facts[]`, tagged with `kind`
3. Record any gates that were satisfied in `gates`, **with evidence from the
   customer side**
4. Turn open items into actions with Steps 4–5 of `scalar-account-plan`, and
   replace the activity plan

```bash
.venv/bin/python scripts/scalar/build_account_plan.py <account.json> --carry-over
```

## Step 8: Report

1. The name, type, deck URL, and Drive folder of each material produced
2. For customer-facing material: confirmation that the Step 3 check was
   passed, and which items were moved out for being internal
3. The QA result (or that it was not performed)
4. **The AE's action plan** — who, what, by when, and what completion looks
   like (`out/account-plan/<customer name>/action-plan.md`)
5. For material requesting internal approval: **what decision is being
   asked for**, in one line (continue / hold / withdraw, discount cost,
   staffing required)

## Rules

- **Never mistake the audience.** The material type is determined by the
  reader. When in doubt, default to internal.
- **Stage advances on customer agreement, not on activity volume.** Do not
  treat "we explained it" or "we handed over a document" as grounds for
  advancing the stage (playbook §1, principle 5).
- **Never skip WHAT/WHY.** Don't produce material that answers the
  customer's requirements with HOW alone.
- **Never fill gaps with guesses.** Present unconfirmed items as "would like
  to confirm today" in the material.
- **Back every figure with a source.** Don't include a number you can't cite
  a source for.
- Don't leave a previous customer's name, amount, structure, or notes behind
  from an old template (playbook §4).
- Do not commit `accounts/` or `config/`. Keep working files under `out/`.
