---
description: >-
  Build the materials for a single customer visit as one continuous flow:
  read the ledger → determine phase and counterpart → route to the material
  type → check for leaked internal information → offline validation →
  generation and Drive placement → visual QA → write back to the ledger and
  update the activity plan → report the action plan
argument-hint: "<customer name> [visit purpose / counterpart / phase] [path to meeting notes or memo]"
---

*[日本語](visit.ja.md)*

# /visit — Visit Materials Pipeline

Starting from `$ARGUMENTS`, run the `scalar-ae-materials` skill flow through
**in one continuous pass, without stopping**. The working directory is the
slide-forge root.

The source of truth for decisions is `references/scalar/sales-playbook.md`.

## Step 1: Read the ledger

```bash
ls accounts/*/<customer name>/account.json
.venv/bin/python scripts/scalar/account_ledger.py validate <account.json>
.venv/bin/python scripts/scalar/account_ledger.py gaps <account.json>
```

If the ledger doesn't exist, run `/account <customer name> new` first (this
may be run from within this command). **Don't ask about assumptions already
in the ledger.**

## Step 2: Ask about only what's missing, in one batch (at most 1 round)

Up to 4 questions via `AskUserQuestion`. Omit items already filled in by the
ledger or the user's instructions.

1. Who will they meet (title, department, first meeting or not)
2. What one statement do we want to get from the customer during this visit
3. What do we want to get internally (approval for proposal investment /
   price approval / SA staffing)
4. Whether to run visual QA after generation (default/recommended is "yes")

State the adopted assumptions in one line before proceeding.

## Step 3: Decide the material type and get the composition approved (gate, do not skip)

Using `scalar-ae-materials`'s Step 2 routing table, pick the material type
from phase × counterpart × purpose. **Customer-facing and internal materials
must always be separate files.**

Present the following in the body text and get approval:

- The list of materials to build (type, slide count, destination folder)
- Each slide's action title
- Any delegation targets, if applicable (formal proposals go to
  `scalar-proposal-slides`, the 3 maps go to `b2b-account-maps`)

**After approval, proceed through to the Step 8 report without further
confirmation.**

## Step 4: Check for leaked internal information (if customer-facing materials exist; do not skip)

Before generation, read the spec body text and run it through the checklist
in `scalar-ae-materials`'s Step 3 (individuals' influence, positions on the
deal, uncontacted stakeholders, competitors' weaknesses, unconfirmed items
stated as fact, figures without a source, pricing/roadmap outside the
disclosure scope). Move anything that applies to the `90_社内` materials.

## Step 5: Write the spec and validate it offline

Build any pages that can be built from the ledger, from the ledger:

```bash
.venv/bin/python scripts/scalar/account_ledger.py slots <account.json> visit-plan \
    --out out/<customer name>/visit-plan.json
.venv/bin/python scripts/render_slide_template.py --template visit-plan \
    --data out/<customer name>/visit-plan.json --out out/<customer name>/visit-plan.slide.json
```

To build `visit-plan`, first write a visit with `status: "planned"` into the
ledger's `visits[]` (date, counterpart, purpose, 3-4 questions, 2-3 expected
objections, referral request).

```bash
.venv/bin/python scripts/assemble_spec.py out/<customer name>/*.slide.json \
    --out out/<customer name>/deck.json --title "<material name>"
.venv/bin/python scripts/build_deck.py --template templates/scalar-2026.json \
    --spec out/<customer name>/deck.json --dry-run --strict
```

Resolve any findings by fixing the data. Do not fix the template.

## Step 6: Generate and place in the correct folder

```bash
.venv/bin/python scripts/scalar/account_workspace.py ensure --ledger <account.json> --json
```

For customer presentation → `01_顧客提示` / for customer proposal →
`02_顧客提案` / for internal explanation → `90_社内`. Also upload the spec
JSON and diagram sources to the same folder. If generation fails, delete the
partial deck from Drive and rebuild.

## Step 7: Visual QA and writing back to the ledger

- If "run it" was chosen in Step 2, inspect using the `slide-qa` skill's
  steps, and always run `.venv/bin/python scripts/cleanup_qa.py` at the end
- If skipped, note explicitly in the report that QA was not performed

Then write back to the ledger (**do not skip**):

1. Add this visit to `visits[]` (after it happens, `status: "done"` plus
   `heard` / `next`)
2. Add newly learned facts to `facts[]` with `kind` attached
3. Record any gates that were satisfied in `gates`, **with evidence from the
   customer side**

```bash
.venv/bin/python scripts/scalar/build_account_plan.py <account.json> --carry-over
```

Since the second and later runs of the activity plan are destructive, first
secure a version with
`.venv/bin/python scripts/snapshot_version.py "<deck URL>"`.

## Step 8: Report

1. **The AE's action plan** — who, what, by when, what condition marks it
   done (`out/account-plan/<customer name>/action-plan.md`)
2. The name, type, URL, and Drive folder of each material produced
3. For customer-facing materials, that the Step 4 check was passed, and what
   was moved to internal
4. QA results, or an explicit note that QA was not performed. That the
   validation files have been deleted
5. If there are materials requiring internal approval, **the decision being
   requested**, in one line (continue / hold / withdraw, discount trade-off,
   staffing required)
6. Final check: finalize / fix wording / add materials / also review the
   activity plan (`/account`)
