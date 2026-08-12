*[日本語](patterns.ja.md)*
# Business Framework Diagrams (patterns.py)

How to use `PatternMixin`, which is mixed into `diagrams.Canvas`. It packages the "shapes" that
are standard in decks for new-business proposals and internal approval requests. All are drawn
purely with shapes, so no keys or network access are required, and colors follow the template's
palette. Coordinates are in inches, and the return value is the bottom y of the drawn area.

These are also available from the deck spec (JSON)'s `figures`, under the same `type` name. A
working example using all 6 kinds is `examples/patterns-demo.json`.

## Which one to use

| What you want to show | What to use | Notes |
|---|---|---|
| Positioning relative to competitors (2 axes) | `posmap` | For a "classification" of quadrants, use `matrix` (illustrations) |
| A phase × duration timeline | `gantt` | Milestones (◆) can be placed too |
| Team/organizational hierarchy | `orgchart` | Up to 8 leaves and depth 3. Split it if you exceed that |
| The overall shape of a business model | `lean_canvas` | Standard 9-block Lean Canvas |
| Nested market-size circles (TAM/SAM/SOM) | `nested_circles` | Only use values that have a source |
| Voice of the customer or key stakeholders | `testimonial` | Only quote things that were actually said |
| Structure of causes (broken out by category) | `fishbone` | 2–6 categories, up to 4 causes each |
| Cost breakdown over time | `vbars_stacked` (charts) | See `references/charts.md` |

## posmap — positioning map

```python
d.posmap(x, y, w, h, points,
         x_axis=("低", "高"),     # horizontal axis end labels (left, right)
         y_axis=("低", "高"),     # vertical axis end labels (bottom, top)
         highlight=None,          # label(s) to highlight (string or list, e.g. "自社")
         highlight_color=None,    # highlight color (default success)
         size=10, bubble=0.72)    # bubble diameter (inches)
```

- `points` is `(label, px, py)`. **px / py are relative coordinates from 0 to 1** (0=left/bottom,
  1=right/top).
- The left/right axis-end labels sit in white boxes on the axis's extension line. Their width is
  sized automatically from the label's character count.
- Placing bubbles too close together gets flagged by `audit_overlaps`. Keep the coordinates
  apart.

```json
{ "type": "posmap", "x": 0.6, "y": 1.15, "w": 6.4, "h": 4.1,
  "points": [["A社", 0.85, 0.15], ["自社", 0.85, 0.85]],
  "xAxis": ["サポートがそこそこ", "サポートが充実"],
  "yAxis": ["導入までが遅い", "導入までが速い"],
  "highlight": "自社" }
```

## gantt — Gantt chart (timeline)

```python
d.gantt(x, y, w, h, columns, rows,
        label_w=None,   # width of the left row-label column (default 20% of w, capped at 1.8)
        colors=None,    # bar colors (list, per row; default primary)
        zebra=True)     # light stripe on even rows
```

- `columns` are the period headings (e.g. `["4月", "5月", "6月"]`).
- `rows` is `(row label, start, end)` or `(row label, start, end, bar label)`.
  Start/end are **decimal values in column units**, where 0 is the left edge of the first column
  and `len(columns)` is the right edge.
- **A row where start == end becomes a milestone (◆)**, with the label placed to its right.
- The bar label goes inside the bar (in reverse text) if it fits, otherwise to the right
  (muted color) if it doesn't.
- Dependency arrows are not represented. If you need to show fine-grained dependencies, use a
  `table` instead.

```json
{ "type": "gantt", "x": 0.5, "y": 1.2, "w": 9.0, "h": 3.6,
  "columns": ["4月", "5月", "6月", "7月"],
  "rows": [["キックオフ", 0.5, 0.5, "キックオフ"],
           ["フェーズ1", 1.0, 2.5, "○○実施"]] }
```

## orgchart — team/organization chart

```python
d.orgchart(x, y, w, h, tree, size=10,
           node_h=None,      # node height (default computed from depth)
           root_fill=None)   # root fill color (default primary)
```

- `tree` is `(label, [children…])`. A child can be nested the same way, a plain string, or
  `{"label": …, "children": […]}`.
- Making the label a two-line `"role\nname"` gives the typical org-chart look.
- Column width is auto-allocated by leaf count. **Below 0.85in per column raises `ValueError`.**
  For trees with many leaves (over 8) or deep nesting (4+ levels), split into multiple
  orgcharts, one per department.

```json
{ "type": "orgchart", "x": 0.7, "y": 1.2, "w": 8.6, "h": 3.6,
  "tree": ["PJ責任者\n山田", [["営業担当\n佐藤", []],
           ["開発担当\n鈴木", [["○○担当\n高橋", []]]]]] }
```

## lean_canvas — Lean Canvas

```python
d.lean_canvas(x, y, w, h, blocks, size=9, title_size=9.5)
```

- `blocks` is a dict mapping key → content (a string, or a list of strings). There are 9 keys:
  `problem` / `solution` / `key_metrics` / `uvp` (unique value proposition) /
  `advantage` (unfair advantage) / `channels` / `segments` (customer segments) /
  `cost` (cost structure) / `revenue` (revenue streams).
- A block whose key is missing is drawn with just an empty frame. An unknown key raises
  `ValueError`.
- **Summarize each block to 2–3 items, roughly 15 characters per item, before passing it in.**
  Long text in all 9 blocks is guaranteed to overflow (caught by `audit_text_fit`).

## nested_circles — nested circles (TAM / SAM / SOM)

```python
d.nested_circles(x, y, w, h, rings, size=10, colors=None)
```

- `rings` is ordered **from the outside in**: `(label, displayed value)` or a plain string. 2 or
  more.
- The circles are stacked with their bottoms aligned, with a leader line to the label and value
  on the right.
- Only use values that have a source (attach a separate label such as "※ per XX research" for
  market size).

```json
{ "type": "nested_circles", "x": 0.7, "y": 1.2, "w": 8.6, "h": 4.0,
  "rings": [["○○市場の総規模", "1.2兆円"],
            ["当社ターゲット市場", "800億円"],
            ["20XX年の獲得目標", "12億円"]] }
```

## testimonial — voice of the customer or key stakeholder

```python
d.testimonial(x, y, w, h, quote, name,
              role=None,      # title (can be multi-line, e.g. "company\ndept role")
              points=None,    # bullet points to place below the quote
              icon="person",  # pictogram on the left (from illustrations' ICONS)
              quote_size=13)
```

- A person pictogram plus name/title on the left, the quote (in " " quotes, dark primary color)
  on the right.
- Passing `points` adds a divider line and bullets below the quote.
- **Only use quotes from real statements.** Never fabricate a "voice" without an actual
  interview or hearing record.

## fishbone — cause-and-effect diagram (fishbone)

```python
d.fishbone(x, y, w, h, problem, categories,
           # problem: the issue placed at the head (right end, the effect)
           # categories: [(category name, [cause, …]), …], distributed alternately above/below
           size=9,
           head_w=None)    # head box width (default min(1.6, w×0.18))
```

- Between 2 and 6 categories, with **up to 4** causes per category (exceeding it raises
  `ValueError`). Consolidate any overflow before passing it in. This diagram is for identifying
  likely causes, not proving exhaustive coverage.
- Because Slides can't place diagonal text, only the spine's diagonal lines remain diagonal;
  causes are laid out as horizontal bullet lists along them — a simplified form, not the
  textbook diagonal "bones."
- Align category names to a single breakdown framework (e.g. the 4 Ms: man, machine, method,
  material) and don't mix frameworks (the `audit_*` checks can't catch this — it's the author's
  responsibility).

```json
{ "type": "fishbone", "x": 0.5, "y": 1.05, "w": 9.0, "h": 3.0,
  "problem": "月次締めが5営業日超",
  "categories": [["人", ["経理の属人化", "承認者の兼務"]],
                 ["プロセス", ["紙の請求書回付", "締め後の遡り修正"]],
                 ["システム", ["手作業の転記", "システム間の二重入力"]]] }
```

## Common notes

- After drawing, always run `audit_bounds` / `audit_overlaps` / `audit_text_fit`
  (this happens automatically via `--dry-run` when going through a deck spec).
- Every figure here only supplies the "shape of the framework" — **the quality of the content
  is the author's responsibility.** Note that putting unsubstantiated content into a lean canvas
  or posmap is especially misleading precisely because the shape looks so authoritative.
