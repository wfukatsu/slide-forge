---
name: scalar-deal-intake
description: >-
  Turn raw deal material — meeting minutes, email threads, Slack, CRM exports,
  customer documents — into per-stage records and a hearing sheet. Extracts facts
  with a source and a confidence level, never invents an answer, and turns every
  gap into a question with an owner and a due date.
  Use for: 議事録を整理して, メールから商談情報をまとめて, ヒアリングシートを埋めて,
  ステージごとに整理して, ステージを上げてよいかの判断.
  Not: the ledger and activity plan (scalar-account-plan); one visit's materials
  (scalar-ae-materials); the maps (b2b-account-maps); the proposal
  (scalar-proposal-slides).
---

*[日本語](SKILL.ja.md)*

# Scalar Deal Intake

Raw material in, structured stage records out. This skill does **not** generate
slides. It produces Markdown under `accounts/<AE>/<customer>/stages/`, which the
deck-building skills then read.

Working directory: the slide-forge root.

Sources of truth — this skill redefines neither:

| Concern | Source |
|---|---|
| Phases, gate IDs, transition conditions, BANT criteria, material types | [`references/scalar/sales-playbook.md`](../../references/scalar/sales-playbook.md) |
| Who you meet per stage, what you hand them, what output you must come back with | [`references/scalar/stage-io-map.md`](../../references/scalar/stage-io-map.md) |
| Safety, Drive, approval and QA rules | [`references/scalar/workflow-contract.md`](../../references/scalar/workflow-contract.md) |

## Boundaries

| Request | Where it goes |
|---|---|
| Organise minutes / email into stage records; fill the hearing sheet | This skill |
| Work out what is unconfirmed and who to ask | This skill |
| Update the `account.json` ledger and the activity-plan deck | `scalar-account-plan` |
| Materials for one visit, WPS, Deal Desk, 稟議 | `scalar-ae-materials` |
| Draw the discovery / system / influence maps | `b2b-account-maps` |
| Formal customer proposal, quotation | `scalar-proposal-slides`, `spreadsheets` |
| Annual Account Planning Session decks | `scalar-account-planning-session` |
| Nurturing a lead before a deal exists (nurture 0–4) | `scalar-nurture-intake` |

## These records are internal

They hold named individuals, their stance, and judgements about them.
**Never hand them to the customer or a partner.** They live under `accounts/`,
which is gitignored — do not commit a filled record.

## Workflow

### 1. Read everything supplied first

Read the minutes, email, Slack export, CRM export and customer documents before
asking anything. Accept local paths, pasted text, Drive URLs (read with the
Google Drive tools) and Gmail threads. If the material is thin, say so rather
than filling gaps from assumption.

Record every input in the record's "反映済みの入力" row: filename or subject,
date, and who spoke. **A fact without a source does not go in.**

### 2. Locate the account and the stage

```bash
ls accounts/<AE>/<customer>/
```

If `account.json` exists, take the AE, customer, stage and known people from it:

```bash
.venv/bin/python scripts/scalar/account_ledger.py gaps accounts/<AE>/<customer>/account.json
```

If it does not exist, ask for the AE name and customer name only — infer the
stage from the material against `stage-io-map.md` §1, and state the inference.

A single meeting often spans stages. **Route each fact to the stage that owns
that output**, not to the meeting's stage. A constraint heard during a stage-2
visit belongs in the stage-3 constraints table if that is where the output lives.

### 3. Prepare the record files

Copy only what is needed from `templates/sales/`. **Every deal gets a
`deal-log.md`**, whatever the stage.

```bash
mkdir -p accounts/<AE>/<customer>/stages
cp templates/sales/deal-log.ja.md      accounts/<AE>/<customer>/stages/deal-log.md
cp templates/sales/hearing-sheet.ja.md accounts/<AE>/<customer>/stages/hearing-sheet.md
cp templates/sales/stage-2-discovery.ja.md accounts/<AE>/<customer>/stages/stage-2-discovery.md
# product-fit addendum for whichever product is under consideration
cp templates/sales/products/scalar.ja.md accounts/<AE>/<customer>/stages/product-fit-scalar.md
```

The hearing sheet is **product-neutral** — it collects the customer's facts
only. Product-fit judgments (which challenge category, which constraints
disqualify the fit, sizing, edition) live in the per-product addendum under
`templates/sales/products/` (rules: `templates/sales/products/README.md`).
Feed the sheet's §4.2 / §5 answers into the addendum's B / C / D sections;
write the addendum's verdict back into the sheet's §1.

**To move the hearing sheet between formats, use the `hearing-sheet` skill** —
it keeps `hearing.json` as the record, renders Markdown / Excel / Google
Spreadsheet from it, and reads a filled-in one back. This skill fills the
record from minutes and email; **handing a sheet out and taking it back is
`hearing-sheet`'s job**. Both use the same confidence vocabulary.

Two kinds of form. Do not mix them.

| | Stage record (`stage-*.md`) | Deal log (`deal-log.md`) |
|---|---|---|
| Holds | Where things stand now | What happened, when |
| Updated | When that stage's content changes | One row appended per intake |
| Source of truth for | Gate verdicts, requirements, constraints, agreements | Amount, close date, forecast, risks, loss reason |

Where a number or a confidence level disagrees, **`deal-log.md` wins**.

If the file already exists, **snapshot it before editing** (`cp x.md x.md.bak-YYYYMMDD`)
and append rather than overwrite. Existing rows with a source are never deleted
by this skill; a fact that turned out wrong is struck through with the correction
and its source, so the history stays readable.

### 4. Extract facts into the tables

One row is one fact. Every row carries a source and a confidence level:

| Level | Meaning |
|---|---|
| `確認済` | Stated by the customer, or in a document from them |
| `推定` | Our inference — write the basis next to it |
| `未確認` | Not asked yet |

Rules, from playbook §4:

- Put the customer's own words in the "顧客の発言" column. Our reading goes in a
  separate column, labelled as ours.
- **Never promote `推定` to `確認済`.** Do not fill a blank to make the table
  look complete — a blank with an owner and a due date is the useful output.
- Internal discussion results and customer agreement are different rows. "We
  agreed internally on the scope" is not "the customer agreed the scope".
- Numbers (budget, ROI, sizing) carry their basis and assumptions.
- A metric needs **both a baseline and a target**. "Cut costs" alone stays `未確認`.

Match the ledger's vocabulary. The conversion table is `hearing-sheet.ja.md` §14.2.

| Use | Vocabulary |
|---|---|
| Gate verdict | `met` / `partial` / `unmet` |
| MEDDPICC coverage (stage 2 §10) | `confirmed` / `wip` / `missing` |
| BANT | `ok` / `risk` / `unknown` |
| Fact kind | `said` / `observed` / `assumed` |
| Forecast | `Pipeline` / `Best` / `Commit` / `Closed` |

### Three places every intake touches

1. `deal-log.md` §1 — one row per meeting (attendees, what was decided, both sides'
   homework, next date, temperature).
   **When the stage changed that time, add a row to the stage-transition table in
   §1 too** (date, from/to, the gate used, the customer-side evidence) — without it
   there is no cycle time.
2. `deal-log.md` §3 — newly surfaced risks. **Not the same as unknowns**, which are
   things an interview would answer
3. The stage record — the fields that got filled this time

When new material contradicts an existing record, log it in the contradiction table
in `deal-log.md` §1. **Never overwrite silently.**

### 5. Judge the gates on customer-side evidence

Fill the transition table at the bottom of the stage record. A gate passes only
with **evidence from the customer's side** — who said what, when. "We explained
it" and "we sent the proposal" are not evidence (playbook §1, principle 5).

Where the sheet's criteria and the playbook's gates differ, the record already
notes which rows came from the sheet. Judge every gate in the table, not just
the sheet rows.

### 6. Turn gaps into actions

Every `未確認` becomes a row in the record's action table and in hearing-sheet
§12: what is unknown, who can answer it, by when, and who asks. Choose the
counterpart from the `stage-io-map` row that owns that output — the map already
says who holds each answer.

Then tick the "聞く" boxes in the hearing sheet for the next visit.

### The forecast is set by evidence

When updating the `deal-log.md` header, drop a `Commit` to `Best` unless all of
the following hold (playbook §4):

- §2's close plan runs to the contract date and its tasks are **agreed with the customer**
- Every "影響: 大" risk in §3 is closed, or its next action is agreed with the customer
- Stage 4 §12's paper process has a "要否" and a duration for each step

### On a loss or a hold

Do not close the deal until `deal-log.md` §4 is filled — **wins included** (what
decided it, what material worked, what to repeat next time): the real cause, the
criterion that decided it, which stage's missed check let it through, and the
conditions for coming back. **"Price was too high" is not a root cause.**

### 7. Report the diff

Tell the user, in Japanese:

1. Which files were created or updated, and what was added
2. Which gates now pass, with the evidence — and which still do not
3. The top unconfirmed items with their counterpart and due date
4. Anything in the material that contradicts an existing record

Then point at the next step: `scalar-account-plan` to fold the result into
`account.json` and refresh the activity plan, or `scalar-ae-materials` to build
the material for the next visit.

## Refusals and cautions

- Do not answer "what stage is this deal in" from activity volume. Stage moves
  on customer agreement (playbook §1, principle 5).
- Do not judge a stage-1 account unfit merely because it matches neither
  ScalarDB row in the fit sheet — those two rows are out of date
  (`stage-io-map.md` §8).
- Do not read the sheet's "6. Close" as the end of the deal. Playbook phase 6
  runs through delivery, renewal and expansion (`stage-io-map.md` §7).
- If the material contains a price, a competitor's weakness, or a judgement
  about a named person, it stays in these records and out of anything the
  customer sees.
- Do not fill the competitor table with vendors only. **Status quo, building it
  in-house, and extending the incumbent** are always three of the rows (stage 2 §8).
- Only write that a Champion exists when fewer than three of the five validation
  rows in stage 2 §1 are still unverified. Title and enthusiasm do not qualify.
- If a PoC record leaves "what the customer does next if it passes" blank, that
  PoC is not evidence for raising the forecast.
