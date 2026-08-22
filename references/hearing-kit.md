*[日本語](hearing-kit.ja.md)*

# Hearing kit — shared rules for `hearing-sheet` and `hearing-slides`

Two skills share one record. This file owns what both of them must obey; neither
skill redefines any of it.

| Concern | Owner |
|---|---|
| The record, the three surfaces, merging, the customer filter | **this file** |
| Which questions exist at all | `templates/sales/hearing-sheet.ja.md` (+ `templates/sales/products/`) |
| Phases, gates, BANT thresholds, the five material types | `references/scalar/sales-playbook.md` |
| Reading minutes and email into the record | `scalar-deal-intake` |
| Product fit (categories, disqualifying constraints, edition) | `templates/sales/products/<product>.ja.md` |

## 1. The JSON is the record

`accounts/<AE>/<customer>/stages/hearing.json`. Markdown, Excel and the Google
Spreadsheet are **renders of it**, and each can be read back, because every
question carries a stable ID (`4.2-05`).

```
templates/sales/hearing-sheet.ja.md ──init──▶ hearing.json ──render──▶ md / xlsx / gsheet
                                                    ▲                        │
                                                    └────────read────────────┘
```

- **The ID column is the join.** Never renumber it, never sort rows by hand in a
  surface that will be read back, never delete the column.
- The vocabulary is the one the rest of the toolchain already uses:
  `確認済` / `推定` / `未確認`, converted to the ledger's `confirmed` / `wip` /
  `missing` by the table in `hearing-sheet.ja.md` §14.2. **Do not invent a
  fourth value.**
- §12 (the unconfirmed list) and §13 (what to confirm back) are **derived**.
  They follow the confidences; nobody keeps them in step by hand. Editing the
  follow-up columns in those tables writes back onto the question.

## 2. Merging never overwrites silently

`read` compares the surface against the record and, when both have moved on for
the same cell, **reports a conflict and writes nothing**:

```bash
.venv/bin/python scripts/hearing/hearing_sheet.py read <surface> --into hearing.json \
    --baseline <the json as it was when the surface was rendered>
```

- Keep the baseline. Without `--baseline` a stale surface silently reverts newer
  answers, and the customer's edits and yours cannot be told apart.
- `--take sheet` / `--take json` resolves a conflict, and only ever on purpose.
- Same discipline as `deal-log.md` §1's contradiction table: a disagreement is
  recorded, not resolved by whoever wrote last.
- **Re-rendering a Google Spreadsheet replaces its contents.** Always `read`
  before you `render` over one somebody may have filled in.

## 3. The customer-facing surface is filtered, not trusted

`--audience customer` drops the internal columns (出典 / 確度) and every section
whose heading is marked `customerSafe: false` — by default the buying committee,
partners, the competition, our own BANT judgement and the mapping tables.

**That is a mechanical filter, not the review.** Playbook §3's check still
applies by eye before anything is handed over:

- no judgement about an individual's influence, stance or "not yet contacted"
- no named competitor weakness
- nothing unconfirmed written as though it were confirmed
- no figure without a source
- pricing and roadmap within what this audience may see

## 4. Where the answers live

| What | Where |
|---|---|
| A named customer's answers | `accounts/<AE>/<customer>/stages/` only |
| Event answers | aggregated to type and count first, then `accounts/_nurture/` |
| Consent and opt-out records | MA / CRM. **Never** in this repo (`nurture-map.md` §8) |

`accounts/` is gitignored. **Never commit a filled-in sheet**, and never hand
one to a customer or partner without the customer filter.

An event answer that identifies a person or a company is not a segment signal —
it is a deal. Route it to `scalar-deal-intake` (`scalar-nurture-intake` §2).

## 5. Commands

Run everything from the slide-forge root with `.venv/bin/python`.

| Task | Command |
|---|---|
| Start the record | `scripts/hearing/hearing_sheet.py init templates/sales/hearing-sheet.ja.md --out <json>` |
| Add a product addendum | same, with `--section-prefix scalar- --no-derived` on `templates/sales/products/scalar.ja.md` |
| Render | `scripts/hearing/hearing_sheet.py render <json> --format md / xlsx / gsheet [--audience customer]` |
| Validate a spreadsheet render offline | add `--dry-run` (no API calls) |
| Read back | `scripts/hearing/hearing_sheet.py read <surface> --into <json> --baseline <prev json>` |
| What is still open | `scripts/hearing/hearing_sheet.py gaps <json> [--section 4]` |
| Slide data | `scripts/hearing/hearing_slots.py <json> <page> --out <data.json>` |
| QR for a collect page | `scripts/hearing/qr.py <url> --out out/hearing/qr.png` |

`render --format gsheet` updates the file with the same name in the same folder
**in place**, so the URL survives. Keep one link per deal.
