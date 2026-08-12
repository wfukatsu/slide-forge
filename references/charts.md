*[日本語](charts.ja.md)*

# Tables and charts (charts.py)

How to use `ChartMixin`, which is mixed into `diagrams.Canvas`. Tables use Slides-native
tables; charts are drawn as shapes (only pie charts are rendered as SVG → PNG images).
Coordinates are in inches, and every return value is the y-coordinate of the bottom edge of
the drawn area.

```python
from diagrams import Canvas
ref = deck.add_slide("TITLE_ONLY", title="…")
d = Canvas(deck, ref["slideId"], template)

b = d.table(0.5, 1.2, 9.0, ["Item", "Before", "Proposed"],
            [["Build time", "6 months", "2 months"], ["Ops effort", "3 person-months", "0.5 person-months"]])
b = d.vbars(0.5, b + 0.3, 6.0, 3.0, [("2023", 120), ("2024", 210), ("2025", 380)])
```

These can also be used from a deck spec's (JSON) `figures` under the same type name. Working
examples live in `examples/charts-demo.json` (a live demo of 5 of the 6 types, excluding
`vbars_stacked`; `vbars_stacked` is in `examples/patterns-demo.json`).

## Which one to use

| What you want to show | Use | Notes |
|---|---|---|
| Precise comparison of numbers/specs | `table` | Users can edit it after generation |
| Comparing quantities (across categories) | `vbars` / `hbars` (diagrams) | Use horizontal bars if item names are long |
| Comparing quantities × series (e.g., before vs. proposed) | `vbars_grouped` | Up to 2–3 series |
| Total trend × breakdown (e.g., cost composition) | `vbars_stacked` | Up to 4 series. Use grouped if comparing the breakdown is the main point |
| Change/trend over time | `linechart` | Multiple series allowed. **A dual axis cannot be made** (by design) |
| Share of a whole | `pie` | Up to 6 series. Fold anything beyond that into "Other" |
| Concentration of factors (80:20) | `pareto` | Auto-sorted by descending value. "Other" always goes last |
| A single number, large | `metric` (diagrams) | Stronger without turning it into a chart |

## Shared design conventions

- **The bar baseline is fixed at zero.** Negative values or a truncated axis raise
  `ValueError` (to prevent exaggerating change). Only line charts allow moving
  `y_min` / `y_max`.
- **Series colors follow the fixed order of `Palette.series()`**: blue → green → cyan →
  red → dark yellow. This order has been validated for color-vision diversity (adjacent-pair
  CVD ΔE ≥ 9.2). Do not reorder or cycle it. A single-series bar chart uses primary alone.
- **Text uses body colors** (text / muted). Series identification is carried by the legend's
  color swatches.
- Green and dark yellow have contrast under 3:1 against a white background, so **do not
  remove the legend and direct value labels** (they are on by default).
- Only use charts for numbers that have a source. Do not place a chart purely for decoration.
- For shape-based figures (table, bar, line), `audit_bounds` / `audit_overlaps` /
  `audit_text_fit` and `--dry-run` apply as-is. **Always run them before generating.**

## table

```python
d.table(x, y, w, headers, rows,
        col_widths=None,   # column-width ratios, e.g. [2, 1, 1]. Even split if omitted
        row_h=0.34,        # minimum row height (grows if text wraps)
        header_h=0.38,
        size=10, header_size=None,
        aligns=None,       # per-column alignment. Defaults to START for column 1, CENTER for the rest
        header_fill=None,  # header row fill (default: primary; text color chosen automatically)
        zebra=True,        # light stripe on even rows
        border=None)       # border color (default: border)
```

- Because this is a Slides-native table, **users can edit it after generation** (the key
  difference from a pseudo-table built out of shapes).
- `row_h` is a minimum. When text wraps inside a cell, the row grows and the actual result
  extends below the returned bottom-edge y. `audit_text_fit()` checks cell text volume before
  generation.
- For a table with many rows, **split across slides** rather than shrinking the font.

## vbars — vertical bars

```python
d.vbars(x, y, w, h, items,      # items: (label, value) or (label, value, display string)
        max_value=None,          # axis ceiling (defaults to rounding up to a clean number)
        colors=None,             # only color-code with intent (e.g., highlighting a single bar)
        unit="",                 # unit used when the display string is omitted ("h", "items", etc.)
        bar_ratio=0.62)          # bar thickness relative to cell width
```

Values are labeled directly above each bar. Even for a time series, if there are only 3–4
points, vertical bars read more easily than a line chart.

## vbars_grouped — grouped vertical bars

```python
d.vbars_grouped(x, y, w, h, categories, series,
                # categories: x-axis labels ["Q1", "Q2", …]
                # series: [(series name, [values, …]), …] — value count must match categories
                unit="", legend=True, values=True)
```

Up to 2–3 series. Beyond 4 series, consider a table or splitting the chart.

## vbars_stacked — stacked vertical bars

```python
d.vbars_stacked(x, y, w, h, categories, series,
                # categories: x-axis labels ["2024", "2025", …]
                # series: [(series name, [values, …]), …]; the first series is stacked from the bottom
                unit="",
                values=False,   # value at the center of each segment (only for segments tall enough)
                totals=True,    # label the total directly above the bar
                legend=True)
```

- A diagram that shows "trend of the total" and "composition of the breakdown" at once. **If
  the main goal is comparing series within the breakdown, use `vbars_grouped`** (stacking
  misaligns baselines and makes it easy to misread increases/decreases within a tier).
- Up to 4 series. Fold anything beyond that into "Other" before passing it in.
- Since axis ticks are not drawn, the ceiling defaults to 1.05× the maximum total (to avoid
  leaving the upper half empty due to `_nice_ceil`'s rounding up). Can also be set explicitly
  via `max_value`.

## linechart

```python
d.linechart(x, y, w, h, labels, series,
            # labels: x-axis ["Jan", "Feb", …] / series: [(series name, [values, …]), …]
            y_min=0, y_max=None,  # auto-chosen for round tick values if omitted
            grid=4,               # number of horizontal grid divisions
            unit="",              # attached only to the topmost tick ("ms", etc.)
            markers=True,
            end_values=False,     # attach a value only at the last point of each series
            axis_w=0.6)           # tick-label column width; widens automatically for long ticks
```

- **A single axis only.** There is deliberately no API for overlaying two quantities with
  different scales (e.g., counts and dollars) on one chart. Either place two charts
  side-by-side or normalize to a common index.
- Not every point gets a value label (only the endpoint, via `end_values`).

## pie

```python
d.pie(x, y, size, items,        # items: [(label, value), …]. size is the diameter (inches)
      donut=True,
      unit="",                   # when set, the legend reads "Name 62 (62%)"
      legend_w=2.4,              # width of the legend on the right
      bg="#FFFFFF")              # color of the donut hole and gap; match if not on a white background
```

- Since the Slides API has no way to specify an angled sector, only the circular part is
  rendered as SVG baked to PNG and pasted in (requires cairosvg or rsvg-convert — the same
  path as icons). `--dry-run` substitutes an equal-sized circular placeholder and checks only
  the coordinates.
- The legend is drawn as shapes on the right, so text checking works as usual.
- Drawn clockwise from 12 o'clock, **in the order passed in** (never reordered automatically).
- A warning fires if there are 7 or more series. Fold into "Other" or switch to a bar chart.

## pareto

```python
d.pareto(x, y, w, h, items,     # items: [(label, value), …]. Positive numbers only
         unit="",                # attached to the raw-value label inside each bar ("items", etc.)
         threshold=80,           # cumulative-% reference line. 0 to hide
         axis_w=0.6)             # tick-label column width
```

- **Automatically sorted in descending order of value** (the definition of a Pareto chart;
  the input order is not preserved). Only items labeled "その他"/"other" are placed last
  regardless of magnitude.
- In keeping with the no-dual-axis rule, bars = composition (%) and the line = cumulative
  composition (%) both sit on **the same 0–100% axis**. Raw values are labeled inside the
  bars, cumulative % is labeled above the points.
- 3–10 items. Fold anything beyond that into "Other" before passing it in (`ValueError`
  otherwise).
- Used for prioritizing issues (which factor to tackle first). If you only want to show
  composition, use `pie` or `vbars`.

```json
{ "type": "pareto", "x": 0.7, "y": 1.05, "w": 8.6, "h": 3.0,
  "items": [["Input errors", 42], ["Unclear spec", 31], ["Integration errors", 12],
            ["Other", 15]], "unit": "cases" }
```

## Using it from a deck spec (JSON)

```json
{ "layout": "TITLE_ONLY", "title": "Action-oriented title",
  "figures": [
    { "type": "table", "x": 0.5, "y": 1.2, "w": 9.0,
      "headers": ["Item", "Before", "Proposed"],
      "rows": [["Build time", "6 months", "2 months"]],
      "colWidths": [1.4, 2, 2], "rowH": 0.5 },
    { "type": "vbars", "x": 1.2, "y": 1.3, "w": 5.4, "h": 3.4,
      "items": [["2023", 120], ["2024", 210], ["2025", 380]] },
    { "type": "vbars_grouped", "x": 0.7, "y": 1.25, "w": 8.6, "h": 3.5,
      "categories": ["Q1", "Q2"],
      "series": [["Before", [40, 42]], ["Proposed", [18, 12]]], "unit": "h" },
    { "type": "linechart", "x": 0.6, "y": 1.25, "w": 8.8, "h": 3.5,
      "labels": ["Jan", "Feb", "Mar"],
      "series": [["p95", [320, 240, 90]]], "unit": "ms", "endValues": true },
    { "type": "pie", "x": 1.2, "y": 1.35, "size": 3.2,
      "items": [["Migrated", 62], ["In progress", 23], ["Not started", 15]] }
  ] }
```

Keys can be either snake_case or camelCase (`colWidths` → `col_widths`).

## Pitfalls

- **A table's actual height grows.** `row_h` is a minimum. When placing another part below
  it, either add margin to the returned bottom-edge y, or use `--dry-run`'s check to trim
  cell text volume beforehand.
- **Lowering `row_h` does not shrink rows.** Slides table rows have a minimum inner height
  tied to the font (measured: size 9 → ~0.34in, size 10 → ~0.36in). Trying to fit a
  many-row table onto one slide by lowering `row_h` doesn't work, so **split across
  slides** instead.
- **A table's bottom edge stops at the footer band, not the page edge.** If a table extends
  into the band where the master places the logo and © notice (y=5.20in and below on
  scalar-2026), the logo becomes unreadable. `--dry-run` estimates height from row count
  (`min_table_row_h`) and **errors out** on tables that overlap this band. As a rule of
  thumb, **around 10 rows per slide is the ceiling**. Layouts that cover the footer with a
  full-page white rectangle (the `*_PRESENTATION` family) are exempt from this check.
- **A pie chart is an image, so it cannot be edited in Slides after generation.** To change a
  value, edit the spec and regenerate (per this skill's convention).
- **`vbars`'s `h` includes the value label (0.24in) and the category label (0.30in).** It is
  not just the plot area's height. `h < 0.94` raises an error.
- A line chart's tick-label width (`axis_w`) automatically widens based on the tick strings,
  which narrows the plot area accordingly. For large-magnitude values, move the unit out via
  `unit` to cut digits (e.g., 12,000ms → 12s, ¥34,000,000 → use "millions of yen" as the
  unit).
