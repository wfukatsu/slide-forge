*[日本語](sheets-link.ja.md)*

# Decks linked to a spreadsheet

A business plan or any simulation deck needs its numbers to follow a
spreadsheet the reader can change. Three scripts cover it:

| Step | Script | What it does |
|---|---|---|
| 1. Model | `scripts/build_model.py model.json --folder <Drive folder>` | Builds a Google Spreadsheet through the Sheets API: input cells, time-series tables of formulas, a scenario switch, named ranges, native charts |
| 2. Deck | `scripts/build_deck.py … --spec deck.json` | Fills `{{sheet:NAME}}` with the sheet's formatted values and embeds `sheetsChart` figures as linked charts |
| 3. Sync | `scripts/sync_deck.py <deck> [--dry-run]` | After the sheet changes: refreshes the linked charts and rewrites only the bound numbers, in place |

`build_sheet.py` is still the tool for line-item estimates (xlsx parity). Use
`build_model.py` when the workbook is something people simulate in.

## 1. The model spec (build_model.py)

The full format is in the script's docstring. The shape:

- `sheets[].blocks[]` stack down the sheet: `heading`, `note`, `inputs`
  (label / unit / value / note, one per row), `table` (label, unit, then one
  column per header), `grid` (chart data: categories in column A, one column
  per series).
- A literal is an input (yellow, and **kept across rebuilds**); a string
  starting with `=` is a formula; `"?"` is an empty input the reader still
  has to fill in.
- Placeholders keep formulas readable and layout-proof:
  `{@id}` (an input, or a row's cell in the current column), `{@id:FY27}`,
  `{@id:<}` (previous column), `{range:id}`, `{range:a..b}`, `{hdr:table}`,
  `{col}` `{prev}` `{row}` `{first}` `{last}`.
- Tables that share column headers line up column for column, so
  `"formula": "={@count}*{@price}"` works across sheets.
- Every input id and table-row id becomes a **named range**.
- `charts[]`: `type` COLUMN / BAR / LINE / AREA / COMBO / PIE, `data` = a grid
  id, `stacked`, `labels`, `colors`, `legend`, `vAxisTitle`. Set `size`
  (inches) to the box the chart will take on the slide.

Rebuilds (same title in the same folder, or `--into`) keep every sheetId and
chartId — linked slides keep working — and keep the values readers typed into
input cells (`--reset-inputs` to overwrite them). The build reads every sheet
back and fails on `#REF!` / `#NAME?` / `#DIV/0!` and friends.

Keep a **"slide output" sheet**: one `inputs` block of formula rows
(`o_fy27_rev`, …) holding every number the deck shows, formatted the way the
slide should read (`0.00"億円"`, `#,##0`, `0%`). The deck then binds only to
that sheet, and reviewers can see exactly what feeds the slides.

## 2. The deck spec

```json
{
  "spreadsheet": "https://docs.google.com/spreadsheets/d/<ID>/edit",
  "slides": [{
    "layout": "TITLE_ONLY",
    "title": "FY27 の売上は{{sheet:o_fy27_rev}}",
    "figures": [
      {"type": "table", "headers": ["", "FY27"], "rows": [["売上", "{{sheet:o_fy27_rev}}"]], …},
      {"type": "sheetsChart", "chart": "fy27_quarter", "x": 5.0, "y": 1.45, "w": 4.5, "h": 2.9}
    ]
  }]
}
```

- `{{sheet:NAME}}` takes a named range or an A1 reference (`'売上'!G8`) and
  becomes the cell's **formatted** value — the sheet decides how it reads.
- `sheetsChart.chart` is the chart id from the model spec (or the chart's
  title, or its numeric chartId). `--dry-run` draws a placeholder of the same
  size, so overlaps are still audited.
- `--dry-run` stays offline: it uses the values cached by the last live build
  (`out/bindings/<id>.json`), or a same-width stand-in.
- After building, each element holding a binding records its template in its
  alt text (`sf-bind:{…}`). Table cells are pinned to their row and column;
  short shape text (under 6 characters) is tagged only when it is the whole
  of the shape's text. Speaker notes are filled in but not tracked.

## 3. Sync

```bash
.venv/bin/python scripts/snapshot_version.py <deck>      # a deck people already use
.venv/bin/python scripts/sync_deck.py <deck> --dry-run   # old → new, per page
.venv/bin/python scripts/sync_deck.py <deck>
```

Each bound span is replaced by inserting the new value right after the old one
(so it inherits the old value's style) and deleting the old one; the rest of
the text, object ids and comments stay. A span whose text was edited by hand
is reported and left alone. Linked charts are refreshed with
`refreshSheetsChart`.

## Limits

- A bound number changes in place, but the layout does not reflow: a value
  that grows much longer (`9名` → `120名`) can overflow its box. Rebuild the
  page (`build_deck.py --into <deck> --update-slides N`) when a change is
  large.
- The Slides API has no linked text or tables; the alt-text tag is what makes
  sync possible. Deleting or retyping a bound element drops it from sync.
- Linked charts export to PPTX as static images (see `pptx-export`).
