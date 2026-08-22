*[日本語](content.ja.md)*
# Composing the Content Pages

The general-purpose body pages: bullets, columns, image-and-text, chart, table,
KPI, process, quote, icon grid. Each one below says what it is for and what to
build it from today — a placeholder layout, a figure on a BLANK page, or a
registered slide template.

Figures go on a page with no body placeholder:

```python
ref = deck.add_slide("TITLE_ONLY", title="…")
d = Canvas(deck, ref["slideId"], template)
d.flow(0.5, 1.3, 9.0, 0.8, ["受付", "審査", "記録"])
```

See [diagrams.md](../diagrams.md) for the figure families,
[template-schema.md](../template-schema.md) for the spec form, and
`list_slide_templates.py` for the 92 ready-made pages.

## Bullets

Key points as an enumeration — the default body page, and the one to stop
reaching for once a page has structure worth showing.

**Build it with**: `layout="CONTENT"`, `body` as a list. `body_font_size=12`
and `body_line_spacing=120` fit about 14 lines; past that, split the page.

Three to five bullets. A seven-bullet page is two pages that have not been
separated yet.

## Columns

Two or three parallel tracks — options, audiences, phases — that the reader is
meant to compare across rather than read down.

**Build it with**: the `cards` figure (heading plus body per card), or the
template's TWO_COLUMN / THREE_COLUMN layout when the content is plain text.
For an explicit comparison, `comparison` gives each column the same rows.

## Image and text

A picture on one side, the reading on the other. Use it when the picture is
evidence — a screenshot, a photograph — not decoration.

**Build it with**: `d.image(...)` on one half and `d.label(...)` on the other,
or the `architecture-exhibit` template (image plus the points to read off it).
`fit="contain"` keeps the whole frame visible; `"cover"` crops to fill.

## Chart

Numbers that mean something as a shape: a trend, a share, a ranking.

**Build it with**: the chart figures — `vbars`, `hbars`, `linechart`, `pie`,
`waterfall`, `pareto`. They draw natively, with no Sheets round-trip. See
[charts.md](../charts.md).

Every number needs a `source_note`. A chart with no source is an assertion.

## Table

Data whose value is in the individual cells, not in a shape.

**Build it with**: the `table` figure — `headers`, `rows`, `colWidths`, `size`.
Column widths are a real constraint: the figure audit rejects a cell whose text
overruns its column, and it is measured in full-width equivalents, so a Latin
string and a Japanese one of the same length are not the same width.

For a dense evaluation table, `dense-comparison-table`; for claims against
evidence, `claim-evidence-table`.

## KPI highlight

One or a few numbers, large enough to be the point of the page.

**Build it with**: the `metric` figure (`value`, `caption`), or the `score-card`
/ `score-breakdown` templates for a scored evaluation. Put no more than four on
a page — a fifth turns them back into a table.

## Process flow

Three to five steps in order, connected.

**Build it with**: the `flow` figure for plain steps, `icon_flow` when each
step has an actor worth a pictogram, `steps` when each step rests on the last,
and `gantt-schedule` when the steps have dates.

## Quote

A customer's own words. Its force comes from being verbatim and attributed.

**Build it with**: the `testimonial` figure. Never paraphrase into it; if you
cannot quote exactly and name the source, it is not a quote.

## Icon grid

Three to six items of equal weight, each with a picture and a label.

**Build it with**: `icon_grid` (`cols`, `size`), or `icon_row` for a single
row. Names come from `illustrations.py --list`; sizing and captions are in
[pictogram-catalog.md](../pictogram-catalog.md).
