---
name: hearing-sheet
description: >-
  Keep the hearing sheet as data and move it between Markdown, Excel and Google
  Spreadsheet in both directions — hand one to a customer or partner to fill in,
  read the answers back, and report what is still unconfirmed. Product-neutral;
  product-fit judgements live in templates/sales/products/.
  Use for: ヒアリングシートを作って, ヒアリング項目を Excel で,
  スプレッドシートで顧客に渡したい, 記入してもらったシートを取り込んで,
  何が聞けていないか.
  Not: slides that do the asking (hearing-slides); minutes and email into the
  record (scalar-deal-intake).
---

*[日本語](SKILL.ja.md)*

# Hearing Sheet I/O

Read `references/hearing-kit.md` first — the record, the merge rule, the
customer filter and the command list are all there, and **this skill does not
restate them**. This file owns only the workflow and the decisions.

Working directory: the slide-forge root. Run everything with `.venv/bin/python`.

## Boundaries

| Request | Where it goes |
|---|---|
| A hearing sheet in md / xlsx / Google Spreadsheet, in either direction | This skill |
| What is still unconfirmed, and who can answer it | This skill (`gaps`) |
| Slides that ask the open questions | `hearing-slides` |
| Minutes, email or a CRM export → the record | `scalar-deal-intake` |
| Whether the product fits, and which edition | `templates/sales/products/<product>.ja.md` (a person judges; only the verdict lands here) |
| Gate and BANT judgements | `references/scalar/sales-playbook.md` |
| A quote or a BOM spreadsheet | `spreadsheets` |
| The proposal deck | `scalar-proposal-slides` |

## Step 1: Find or start the record

```bash
ls accounts/<AE>/<customer>/stages/hearing.json
```

If it is missing, start it from the blank form — and from the product addendum
when a product is already in play:

```bash
.venv/bin/python scripts/hearing/hearing_sheet.py init \
    templates/sales/hearing-sheet.ja.md \
    --out accounts/<AE>/<customer>/stages/hearing.json --product scalar
```

**Do not start a second record for the same deal.** One deal, one
`hearing.json`, one Google Spreadsheet link.

If a filled-in Markdown sheet already exists from before this skill, `init`
from that file instead of the blank template — the answers come across, and the
IDs are assigned then.

## Step 2: Decide the surface from who is filling it in

Ask in one batch only what you cannot infer (`references/interactive-intake.md`
§0 and §5):

| # | header | Question | Options |
|---|---|---|---|
| 1 | Who fills it in | Who is going to write in this sheet? | We do, from minutes / The customer / A partner / Attendees at an event |
| 2 | Format | Which surface? | Google Spreadsheet (shared link, read back) / Excel (mail it, read the returned file) / Markdown (internal only) |
| 3 | Audience | Is this going outside? | Internal / Handed to the customer (drops the internal columns and sections) |

Decide it yourself when the request already says so. A sheet the customer
writes in is a Google Spreadsheet or an Excel file, never Markdown.

```bash
.venv/bin/python scripts/hearing/hearing_sheet.py render <json> --format gsheet \
    --audience customer --folder <Drive folder URL>
```

Put a customer-facing sheet in `01_顧客提示`; an internal one stays out of the
customer folders entirely (`sales-playbook.md` §8).

**Before handing anything over, run the playbook §3 check by eye.** The
`--audience customer` filter removes columns and sections; it cannot tell that a
question is phrased in a way you would not want quoted back.

## Step 3: Read what came back

```bash
cp <json> <json>.baseline-YYYYMMDD          # keep the baseline before rendering
.venv/bin/python scripts/hearing/hearing_sheet.py read <surface|URL> \
    --into <json> --baseline <json>.baseline-YYYYMMDD --dry-run
```

Run `--dry-run` first and read the change list. Then drop it to write.

- **A conflict stops the merge.** Do not reach for `--take` to make the message
  go away: look at both values, decide which is true, and say why in the report.
- An ID that is not in the record means a row was added or the ID column was
  edited. Ask before inventing a question to match it.
- Answers arrive as the customer wrote them. **Keep their words in 回答**; your
  reading of them belongs in the stage record, not in this cell.
- Confidence is not raised by an answer appearing. `確認済` needs the customer
  to have said it or a document to carry it — if you inferred it, it is `推定`.

## Step 4: Report what is still open

```bash
.venv/bin/python scripts/hearing/hearing_sheet.py gaps <json> [--section 4]
```

Report, in Japanese:

1. What changed, and where it came from
2. What is still `未確認`, grouped by section, with who can answer it
3. Anything answered as `推定` — these are what `hypothesis-check` will confirm
4. Conflicts, with both values and no resolution invented
5. What the gaps block downstream — §4.2 and §5 gate the architecture diagram
   and the BOM in `scalar-proposal-slides`; §14.3 maps each section to the
   proposal slide it feeds

Then offer `hearing-slides` for the questions worth asking in person.

## Files

| Path | Role |
|---|---|
| `scripts/hearing/hearing_sheet.py` | init / render / read / gaps / validate |
| `scripts/hearing/model.py` | the document shape, the Markdown parser and renderer |
| `templates/sales/hearing-sheet.ja.md` | the blank form (product-neutral) |
| `templates/sales/products/` | product-fit addenda |
| `references/hearing-kit.md` | shared rules (record, merge, customer filter, storage) |
