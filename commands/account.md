---
description: >-
  Create, update, or query a per-customer activity plan: prepare the ledger →
  ingest materials → validate → convert unconfirmed items into actions →
  update the activity plan deck at the same URL → report what to confirm next
argument-hint: "<customer name> [new | update | show] [path to meeting notes or memo]"
---

*[日本語](account.ja.md)*

# /account — Customer Activity Plan

Starting from `$ARGUMENTS`, run the `scalar-account-plan` skill flow through
**without stopping partway**. The working directory is the slide-forge root.

This command handles **internal materials**. The ledger and the activity plan
deck are never handed to the customer.

## Step 0: Decide the mode

Decide from the arguments. Only ask once via `AskUserQuestion` if it's unclear.

| Argument | What to do |
|---|---|
| `new` / no ledger exists | Create the ledger, set up the Drive hierarchy, generate the first deck |
| `update` (default) / meeting notes attached | Append to the ledger, replace the deck at the same URL |
| `show` | Read the ledger and report the status. **No writes, no generation** |

The AE name comes from `defaultAe` in `config/sales.json`; if absent, ask the user.

## Step 1: Read or create the ledger

```bash
ls accounts/*/<customer name>/account.json
```

If it doesn't exist, create it per step 1 of `scalar-account-plan` and set up
the Drive hierarchy. **Always confirm with the user if the Drive root is not
configured** (never create it under My Drive root on your own).

For `show`, read it here, answer using the Step 6 format, and stop.

## Step 2: Ingest materials (read before asking)

Read any meeting notes, memos, or emails passed as arguments first. After
reading, ask about only the missing items, **in a single round**, via
`AskUserQuestion`.

When writing to the ledger, always attach `facts[].kind` — `said` (the
customer said it) / `observed` (confirmed in a document) / `assumed` (our
inference). **`assumed` can never become `confirmed`.**

## Step 3: Validate (do not skip)

```bash
.venv/bin/python scripts/scalar/account_ledger.py validate accounts/<AE>/<customer name>/account.json
```

If contradictions surface, **fix the ledger**. Do not relax validation.

## Step 4: Turn unconfirmed items into actions

```bash
.venv/bin/python scripts/scalar/account_ledger.py gaps accounts/<AE>/<customer name>/account.json
```

For each item that comes up, confirm **only the deadline** with the user (the
deadline is the AE's commitment, not something we decide). Don't fill in the
answers yourself.

## Step 5: Build / replace the deck

```bash
# Validate (no API calls)
.venv/bin/python scripts/scalar/build_account_plan.py <account.json> --dry-run --strict
```

- **First time**: generate with `--folder <ID of 00_活動計画>` attached
- **Subsequent times**: first secure a version with
  `scripts/snapshot_version.py "<deck URL>"`, then run with `--carry-over`.
  The deck URL does not change

```bash
.venv/bin/python scripts/scalar/build_account_plan.py <account.json> --carry-over
```

Then perform a visual inspection with the `slide-qa` skill and clean up with
`scripts/cleanup_qa.py`. Upload the ledger and `action-plan.md` to `00_活動計画`.

## Step 6: Report

1. **What to confirm next** (who, by when, what condition marks it done) — this is the main point
2. The stage/forecast and its basis. What changed since last time
3. The activity plan deck URL and the Drive folder URL
4. Pages dropped due to insufficient material, and what information is missing
5. Final check: finalize / fix a deadline / change the page structure / also
   produce visit materials (`/visit`)
