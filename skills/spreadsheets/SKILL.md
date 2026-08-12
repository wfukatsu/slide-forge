---
name: spreadsheets
description: >-
  Generate line-item spreadsheets — estimates/quotes, BOMs, cost breakdowns,
  comparison tables — as Excel (.xlsx) and/or Google Spreadsheet from one JSON
  spec (scripts/build_sheet.py): typed columns, per-row formulas, a
  subtotal/tax/total summary block, offline validation before any API call.
  The xlsx is the source; the Google Spreadsheet is a Drive conversion of the
  same file, so both outputs always match. Companion deliverable to slide-forge
  decks (deck shows the cost summary, the spreadsheet holds the line items,
  both in the same Drive folder) — and also runs standalone.
  Triggers: "見積もりを作って", "見積書", "明細表", "費用内訳を Excel に",
  "BOM をスプレッドシートに", "Google スプレッドシートで出力", "xlsx で出力",
  "spreadsheets", "make an estimate sheet", "cost breakdown spreadsheet".
  Out of scope: free-form or existing-file xlsx authoring/editing
  (document-skills:xlsx), reading or analyzing spreadsheets, and tables drawn
  inside slides (the deck skills' table figure).
---

*[日本語](SKILL.ja.md)*

# Line-item Spreadsheets (Excel + Google Spreadsheet)

## Important

- **One spec, two outputs.** The JSON spec builds the `.xlsx` with openpyxl;
  `--gsheet` converts that same file into a Google Spreadsheet via Drive.
  Never author the two outputs separately — they must stay identical.
- **Amounts are formulas, not pasted numbers.** Amount = quantity × unit price
  as a real formula (`=D{row}*F{row}`), totals as `SUM`. The user will edit
  quantities in the delivered file and the totals must follow. Only put
  literal numbers in cells the user should treat as input (unit price,
  quantity).
- **Fixes happen in the spec.** Regenerate on any change; with the same title
  and folder, the Google Spreadsheet is updated **in place** (URL preserved),
  so the user always holds one link.
- **Run every command from the slide-forge root as cwd** — `${CLAUDE_PLUGIN_ROOT}`
  when running from an installed plugin, `/path/to/slide-forge` on a
  local clone. Auth and the venv are shared at the repo root (`config/`, `.venv`).
- **Never invent prices.** Unit prices, tax rates, and discount terms come
  from the user or their material. Anything unsourced stays a `○○` placeholder
  flagged in the note row and the report — same rule as deck content.
- **Companion to a deck**: when the spreadsheet backs a proposal's cost slide
  (`scalar-proposal-slides` BOM, etc.), put it in the **deck's Drive folder**
  and keep slide summary and sheet totals consistent — the slide shows the
  total, the sheet carries the line items.

## Quick Reference

| Task | Command |
|------|---------|
| Validate the spec (offline, free) | `.venv/bin/python scripts/build_sheet.py spec.json --dry-run` |
| Build xlsx (→ `out/sheets/<title>.xlsx`) | `.venv/bin/python scripts/build_sheet.py spec.json [--out path.xlsx]` |
| Also create the Google Spreadsheet | `--gsheet [--folder <Drive folder URL/ID>]` |
| Archive the spec next to it | `.venv/bin/python scripts/drive_folder.py upload <FOLDER> spec.json` |
| Worked example (estimate with tax summary) | `examples/estimate-sample.json` |

## Spec format

Full reference in the `build_sheet.py` docstring; the shape:

```json
{
  "title": "○○様向け ScalarDB 導入見積もり",
  "sheets": [{
    "name": "見積もり明細",
    "heading": "表の見出し（任意）",
    "note": "有効期限・税区分などの注記（任意）",
    "columns": [
      {"header": "数量", "type": "int", "width": 8},
      {"header": "単価（月額）", "type": "currency"},
      {"header": "金額（月額）", "type": "currency", "formula": "=D{row}*F{row}"}
    ],
    "rows": [[...], "…列数は columns と一致。formula 列は null…"],
    "summary": [
      {"label": "小計", "formula": "=SUM(G{first}:G{last})"},
      {"label": "消費税 (10%)", "formula": "=G{s1}*0.1"},
      {"label": "合計", "formula": "=G{s1}+G{s2}", "emphasis": true}
    ]
  }]
}
```

- `type`: `text` (default) / `int` / `currency` (¥#,##0) / `percent` / `date`
- Placeholders: `{row}` (that data row), `{first}`/`{last}` (data range),
  `{s1}`, `{s2}`… (summary rows, forward references only)
- Multiple sheets per book: put the line-item sheet first, then
  assumptions / breakdown sheets — estimates without stated assumptions get
  disputed later, so include an assumptions sheet whenever the numbers depend
  on region, exchange rate, contract term, or excluded work.

## Workflow

1. **Settle the shape before authoring** (AskUserQuestion, one round,
   following `references/interactive-intake.md` §0/§5 manners): line-item
   granularity and source material; tax handling (excl./incl. tax/rate);
   output — xlsx only / Google Spreadsheet too (default: both; lead with the
   Spreadsheet when the recipient is on Google Workspace); Drive folder (the
   deck's folder when this backs a deck). Skip anything already specified.
2. **Author the spec** and validate offline: `--dry-run` catches column-count
   mismatches, unknown types, and bad placeholder references before any
   API call.
3. **Build**: add `--gsheet --folder <FOLDER>` when a Google Spreadsheet was
   requested. Upload the spec JSON to the same folder (Drive folder rule).
4. **Verify the numbers** — formulas compute in the file, not in the spec, so
   check them once: export the converted sheet as CSV and confirm the
   subtotal/total (`drive.files().export(fileId=…, mimeType="text/csv")`
   returns computed values), or recompute the expected totals and compare. A
   wrong column letter in a formula is silent otherwise.
5. **Report**: local xlsx path, Google Spreadsheet URL (when created), the
   Drive folder, and any `○○` placeholders still to be filled by the user.
