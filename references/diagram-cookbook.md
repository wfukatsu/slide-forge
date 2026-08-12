*[日本語](diagram-cookbook.ja.md)*
# Diagram Recipes

`d` is `diagrams.Canvas`. Coordinates are in inches. The patterns here were all
used in a 55-slide illustration-heavy deck and verified all the way through
thumbnail review.

## Primitives

`Canvas` (`scripts/diagrams.py`):

| Method | Purpose |
|---|---|
| `shape(x, y, w, h, kind=, fill=, stroke=, text=, size=, bold=, color=, align=, valign=, line_spacing=)` | A shape. `fill=None` for no fill |
| `box(...)` | Rounded, light fill, with a border (the default box) |
| `solid(...)` | Filled, bold (a box for headings) |
| `label(...)` | Text with no border and no fill |
| `band(...)` | A background band |
| `line(x1, y1, x2, y2, color=, weight=, dashed=, end_arrow=, start_arrow=)` | A straight line |
| `arrow(x1, y1, x2, y2, ...)` | An arrow (`end_arrow="FILL_ARROW"`) |
| `arrow_shape(x, y, w, h, ...)` | A thick arrow shape (for process flow) |
| `cards(x, y, w, h, items, accent=)` | Side-by-side cards. `items` is `(heading, body)` |
| `flow(x, y, w, h, steps)` | A left-to-right process flow (with arrows) |
| `hbars(x, y, w, rows)` | A horizontal bar chart. `rows` is `(label, value, display string)` |
| `metric(x, y, w, h, value, caption)` | A large number with a caption |

`deckkit`'s composite parts:

| Function | Purpose |
|---|---|
| `zone(d, x, y, w, h, label)` | A region grouping elements together. Content starts at `y+0.34` |
| `banner(d, y, text, tone=)` | A full-width notice. `tone` is info/good/warn/bad |
| `layers(d, x, y, w, items)` | A horizontal layer diagram. `items` is `(name, description, color)` |
| `steps_v(d, x, y, w, items)` | A numbered vertical flow |
| `grid(d, x, y, w, cols, rows, cell_colors=)` | A table. Cells can be colored individually |
| `pills(d, x, y, w, items, per_row=)` | A grid of chips |
| `kv_rows(d, x, y, w, items)` | A 2-column "item → note" list |
| `db(d, x, y, w, h, name, sub=)` | A DB cylinder with a label |
| `xmark(d, cx, cy)` / `checkmark(d, cx, cy)` | A circled X / circled checkmark (center coordinates) |
| `caption(d, x, y, w, text)` | A small caption attached to a diagram |
| `foot(d, points, edition)` | The footer summary line(s) |

Colors come from `d.P` (`Palette`), built from the template's `colors`.

| Purpose | Color to use |
|---|---|
| Our product / primary component | `d.P.primary` |
| Emphasis / top priority | `d.P.primaryDark` |
| Good state / After / OK | `d.P.success` |
| Problem / Before / not OK | `d.P.danger` |
| Secondary system / other category | `d.P.info` |
| Caution / conditional | `d.P.warning` |
| Body text / supplementary | `d.P.text` / `d.P.muted` |

For brightness adjustment, use `lighten(color, 0–1)` / `darken(color, 0–1)`. For
text color over a fill, `readable_on(background color)` picks the higher-contrast
option.

**Cap each slide at 3 colors max.** More colors than that make the meaning
unreadable.


## Pattern quick-reference

Choose the function based on "what you want to communicate." All of them
**return the bottom y of the drawn area**. Place the next block starting from
that value (don't compute y by hand).

| What you want to convey | Function |
|---|---|
| Current state → after resolution, A/B, recommended vs. not recommended | `compare_panels(d, x, y, w, h, left, right)` |
| Who does what (a cross-role flow) | `swimlane(d, x, y, w, lanes, steps)` |
| Timeline, duration, key points in time | `timeline(d, x, y, w, marks, bands=…)` |
| Process flow (highlighting the scope of responsibility) | `pipeline(d, x, y, w, steps, highlight=…)` |
| Numbered steps (vertical) | `steps_v(d, x, y, w, items)` |
| Hierarchy of responsibility | `layers(d, x, y, w, items)` |
| Parent-child relationship / structure | `tree(d, x, y, w, nodes)` |
| Foundation → application (maturity) | `pyramid(d, x, y, w, h, levels)` |
| Population → outcome (narrowing down) | `funnel(d, x, y, w, h, stages)` |
| A closed loop (PDCA) | `cycle(d, x, y, w, h, steps)` |
| Branching conditions and outcomes | `decision(d, x, y, w, question, branches)` |
| Priority / a 4-quadrant view of options | `quadrant(d, x, y, w, h, quads, x_label=…, y_label=…)` |
| Position on two axes (competitive comparison) | `matrix_map(d, x, y, w, h, items, x_label=…, y_label=…)` |
| Phases × lanes planning | `roadmap(d, x, y, w, phases, lanes)` |
| Numbered callouts on a central subject | `callouts(d, x, y, w, h, center, notes)` |
| Comparison table / feature availability | `grid(d, x, y, w, cols, rows, cell_colors=…)` |
| An unordered list of items | `pills(d, x, y, w, items, per_row=…)` |
| Item → note, 2 columns | `kv_rows(d, x, y, w, items)` |
| A checklist with status | `checklist(d, x, y, w, items)` |
| A large number (only when there's a source) | `stats(d, x, y, w, items)` |
| Meaning of colors | `legend(d, x, y, w, items)` |
| 3–4 items explained in parallel | `Canvas.cards(x, y, w, h, items)` |
| Where data lives | `db(d, x, y, w, h, name, sub=…)` |
| Grouping a region | `zone(d, x, y, w, h, label)` |
| A full-width notice / summary | `banner(d, y, text, tone=…)` |

`tone` is one of `primary` / `info` / `good` / `warn` / `bad` / `muted` /
`accent`. `tone_colors(d, tone)` returns (fill, stroke, text color), and
`tone_solid(d, tone)` returns a solid dark color.

For real rendered examples, see `examples/pattern-gallery/deck.py` and the
slides in the generated gallery.

## Connectors (arrows and lines)

**Never hand-write coordinates to connect shapes.** The Slides API doesn't error
even if the endpoints are off, so you won't notice until you generate the deck
and look at the thumbnail.

| Use case | How to write it |
|---|---|
| Shape A → shape B, should follow if moved | `d.connect(a, b)` |
| Shape A → shape B, should align exactly to the edge | `d.link(a, b)` |
| Need a single point on a shape's edge | `d.edge_point(a, (tx, ty), gap=0.04)` |
| Axes, tick marks, leader lines (should NOT touch) | `d.line(..., free=True)` |

```python
a = d.shape(1.0, 1.0, 1.6, 0.6, text="A")     # shape() は objectId を返す
b = d.shape(4.0, 2.0, 1.6, 0.6, text="B")

d.connect(a, b)                    # API のコネクタ。図形に紐づき、動かすと追従する
d.link(a, b, gap=0.04)             # 中心を結ぶ線と辺の交点を端点にする
d.connect(a, b, category="BENT")   # エルボー。1対多のファンアウトで経路が交差しにくい
```

- `connect()` … genuinely **connects** to shapes via `startConnection`/
  `endConnection`. The connection site is chosen automatically from the
  relative position (0=top 1=left 2=bottom 3=right), snapping to the 4
  cardinal points — works cleanly for strictly horizontal/vertical
  relationships.
- `link()` … computes the intersection of the center-to-center line with each
  edge. The endpoint lands exactly on the edge even at an angle. Use this when
  you don't want snapping.
- `d.line()` / `d.arrow()` … raw coordinates. Use for path bends, axes, or any
  line that shouldn't connect to a shape. In that case, add `free=True` to make
  the intent explicit (omitting it fails the check).

The auditor inspects every connector's endpoints and reports any that are
**at least 0.22in away from any shape**, or **embedded at least 0.06in inside a
shape**. Large containers like zones and text boxes are excluded from this
check (an arrow passing through a container is normal).


## Stacking convention

```python
b = layers(d, X0, DY0, W, [...])           # b は下端 y
b = grid(d, X0, b + 0.24, W, cols, rows)   # 前のブロックの下から置く
b = pills(d, X0, b + 0.20, W, items)
banner(d, b + 0.20, "まとめの一行", tone="good")
foot(d, ["・持ち帰ってほしい1行"])
```

Hardcoding a value like `DY0 + 2.7` causes content to get swallowed by the
block below it as content grows. Stacking off return values makes this
structurally impossible.

The auditor also detects overlaps, but **detection is the last line of defense,
not the design.** Stacking with return values is the real fix; the audit exists
to catch what that misses.

`Canvas`'s `cards` / `flow` / `hbars` / `metric` also return the bottom y, so
they stack the same way.

## Notes per pattern

- `compare_panels` … keep the same structure on both sides. Only the difference
  should catch the eye.
- `swimlane` … the 3rd element of `steps` is the lane index. Arrows connect real
  coordinates, so the path stays correct even across lanes.
- `timeline` … positions are a 0.0–1.0 ratio. Put annotations **on the marker's
  own label**. A separate label plus a vertical arrow will overlap another
  marker's caption or the block below.
- `cycle` … inscribed in a rectangle. The radius is auto-computed so boxes don't
  overflow. 4–6 steps.
- `quadrant` / `matrix_map` … **always include axis labels.** An unlabeled 2×2
  can't be interpreted. `matrix_map`'s placement is itself a claim, so don't
  use it without evidence to back it. `y_label` is drawn stacked vertically, so
  keep it to 2–4 characters.
- `pyramid` / `funnel` … put descriptions beside the shape if there's horizontal
  room, inside the segment if not. The description never disappears. Up to 5
  tiers.
- `callouts` … up to 3 annotations per side. The center box is sized to its
  content and vertically centered.
- `decision` … 2–3 branches. The diamond's text isn't placed directly on the
  shape but overlaid as a separate label (direct text gets clipped at the
  edges).
- `stats` … **use only for figures with a source.** Never inflate an estimate
  to look authoritative.
- `legend` … the legend's colors match the shape's own fill. `tone` names can
  be passed directly.
- `checklist` … uses symbols (✓ □ !) in addition to color, so it's still
  legible in monochrome.

---

## Recipes for hand-assembled diagrams

Examples for diagrams that don't have a dedicated function (architecture
diagrams, etc.) or that combine multiple patterns.

### Before/After 2-panel comparison (the internals of compare_panels)

Shows a problem → a solution. The most effective diagram type.

```python
pw = (W - 0.5) / 2
zone(d, X0, DY0, pw, 3.30, "現状：個別に実装",
     stroke=lighten(d.P.danger, 0.6), fill="#FEF7F8")
# ... 左パネルの中身 ...
xmark(d, X0 + pw / 2, DY0 + 1.24)          # 問題箇所に印

d.arrow_shape(X0 + pw + 0.02, DY0 + 1.30, 0.46, 0.5,
              fill=lighten(d.P.primary, 0.7))   # 中央の太矢印

rx = X0 + pw + 0.5
zone(d, rx, DY0, pw, 3.30, "導入後：横断で1回だけ",
     stroke=lighten(d.P.success, 0.5), fill="#F6FCF4")
# ... 右パネルの中身 ...
checkmark(d, rx + pw - 0.30, DY0 + 1.24)
```

Place elements at **the same structure and same position** on both sides. Only
the difference should catch the eye.

## 2. Layer diagram (hierarchy / responsibility)

```python
layers(d, X0, DY0, W, [
    ("アプリ",  "業務アプリケーション",       lighten(d.P.primary, 0.3)),
    ("サーバ",  "SQL / 認証認可 / 暗号化",     d.P.primary),
    ("基盤",    "トランザクション管理",        d.P.primaryDark),
])
```

Top to bottom is "the consuming side → the consumed side." If hand-drawing
layers, make lower tiers darker.

## 3. Process flow

Horizontal (4 steps max):

```python
d.flow(X0, DY0 + 0.4, W, 0.8, ["調査", "設計", "実装", "検証"])
```

Vertical (when you want descriptions attached):

```python
steps_v(d, X0, DY0, 4.2, [
    ("構成を決める", "DB / ノード数 / 配置"),
    ("設定を変える", "分離レベル・最適化"),
    ("測る",        "ベンチマークを実行"),
])
```

For a loop, draw the return arrow as an **elbow running through the gap between
columns** (3 line segments). Never let it cross over body text.

```python
xg = X0 + 4.2 + 0.20                       # 列間の余白
d.line(X0 + 3.6, DY0 + 2.36, xg, DY0 + 2.36, color=d.P.primary, dashed=True)
d.line(xg, DY0 + 0.31, xg, DY0 + 2.36,      color=d.P.primary, dashed=True)
d.arrow(xg, DY0 + 0.31, X0 + 4.4, DY0 + 0.31, color=d.P.primary)
```

## 4. Swimlane (who does what)

**For an arrow crossing lanes, connect the actual start and end coordinates.**
Drawing it horizontally would misrepresent the path.

```python
LX, LW = X0, 1.30                # レーン名の列
CX, CW = X0 + LW + 0.10, XE - (X0 + LW + 0.10)
LH = 1.08
y_a = DY0 + 0.30                 # レーン A
y_b = y_a + LH + 0.34            # レーン B

for ly, nm, col in [(y_a, "レコード", lighten(d.P.primary, 0.5)),
                    (y_b, "台帳",     d.P.primary)]:
    d.shape(LX, ly, LW, LH, kind="ROUND_RECTANGLE", fill=col, stroke=None,
            text=nm, size=9, bold=True, color="#FFFFFF")
    d.shape(CX, ly, CW, LH, kind="ROUND_RECTANGLE",
            fill=lighten(col, 0.94), stroke=lighten(col, 0.78))

# 各ステップの箱を、属するレーンの y に置く
centers = []                     # (左端, 右端, 中心y) を覚えておく
for i, (nm, lane_y) in enumerate([("1. 準備", y_a), ("2. 確定", y_b), ("3. 反映", y_a)]):
    bx = CX + 0.12 + i * 2.4
    d.shape(bx, lane_y + 0.12, 2.2, LH - 0.24, kind="ROUND_RECTANGLE",
            fill=lighten(d.P.primary, 0.78), stroke=None, text=nm, size=9, bold=True)
    centers.append((bx, bx + 2.2, lane_y + LH / 2))

for i in range(len(centers) - 1):
    _, x_end, y1 = centers[i]
    x_start, _, y2 = centers[i + 1]
    d.arrow(x_end + 0.03, y1, x_start - 0.03, y2, color=d.P.primary, weight=1.6)
```

## 5. Branching condition

```python
cx = X0 + 3.15                                     # フローの中心線
d.shape(cx - 1.85, y, 3.70, 0.74, kind="DIAMOND",
        fill=lighten(d.P.warning, 0.68), stroke=None)
d.label(cx - 1.55, y + 0.18, 3.10, 0.42, "条件を満たすか？",
        size=8.5, bold=True, align="CENTER", color=darken(d.P.warning, 0.55))

# No は右下へ（右にパネルがあるなら、その手前で止める）
d.arrow(cx + 1.86, y + 0.37, cx + 1.30 + 0.62, y2 - 0.02, color=d.P.muted)
d.label(cx + 1.72, y + 0.44, 0.50, 0.20, "No", size=8, align="START")
# Yes は真下へ
d.arrow(cx, y + 0.76, cx, y2 - 0.02, color=d.P.primary, weight=1.6)
d.label(cx + 0.06, y + 0.80, 0.50, 0.20, "Yes", size=8, align="START")
```

Text inside a diamond gets clipped at the edges when passed directly. **Overlay
a separate `label` instead.** Keep branch labels (Yes/No) and outcome labels
clear of the arrow path by nudging them outward with `align`.

## 6. Comparison table / capability matrix

```python
def cc(i, j, cell):
    if j == 0:
        return None
    if cell == "●":
        return (lighten(d.P.success, 0.80), darken(d.P.success, 0.45))
    if cell == "○":
        return (lighten(d.P.warning, 0.70), darken(d.P.warning, 0.55))
    return (None, lighten(d.P.muted, 0.45))

grid(d, X0, DY0, W,
     ["機能", "Community", "Standard", "Premium", "提供状況"],
     [["トランザクション", "●", "●", "●", "GA"],
      ["クラスタリング",   "−", "●", "●", "GA"],
      ["SQL",             "−", "−", "●", "GA"]],
     col_w=[3.20, 1.30, 1.40, 1.35, 1.75], row_h=0.255, cell_colors=cc)
```

Add a small legend below the table (`●` = available, `○` = preview, `−` = not
available).

## 7. Architecture diagram (components and communication)

```python
# 3 列構成：クライアント / 中核 / データ
cw = 1.30
for i in range(3):
    d.shape(X0, DY0 + 0.20 + i * 0.44, cw, 0.36, kind="ROUND_RECTANGLE",
            fill=lighten(d.P.primary, 0.86), stroke=lighten(d.P.primary, 0.6),
            text=f"Client {i+1}", size=8)

kx, kw = X0 + cw + 0.40, 5.20
zone(d, kx, DY0, kw, 1.86, "サーバ群")
# ... ノードを並べる ...

dx = kx + kw + 0.40
for i, nm in enumerate(["MySQL", "Cassandra", "DynamoDB"]):
    d.shape(dx, DY0 + 0.20 + i * 0.44, XE - dx, 0.36, kind="ROUND_RECTANGLE",
            fill="#FFFFFF", stroke=lighten(d.P.muted, 0.35), text=nm, size=8)
```

**If a right-edge panel has less than 1.5in of width left, don't put prose in
it.** Move it to a full-width card at the bottom instead (two `zone`s side by
side). A narrow panel always overflows.

## 8. RAG / pipeline (only part of it in-house)

```python
steps = ["文書", "ベクトル化", "ストアに保存", "類似検索", "LLM が回答"]
sw = (W - 0.28 - 0.30 * 4) / 5
for i, s in enumerate(steps):
    sx = X0 + 0.14 + i * (sw + 0.30)
    own = i in (1, 2, 3)                    # 自社が担う範囲
    d.shape(sx, DY0 + 0.38, sw, 0.80, kind="ROUND_RECTANGLE",
            fill=d.P.primary if own else lighten(d.P.muted, 0.88),
            stroke=None if own else lighten(d.P.muted, 0.5),
            text=s, size=8.5, bold=own,
            color="#FFFFFF" if own else d.P.text, line_spacing=110)
    if i < len(steps) - 1:
        d.arrow(sx + sw + 0.03, DY0 + 0.78, sx + sw + 0.27, DY0 + 0.78,
                color=d.P.primary, weight=1.5)
d.label(X0 + 0.14 + sw + 0.30, DY0 + 1.20, sw * 3 + 0.60, 0.20,
        "この範囲を担う", size=8, bold=True, align="CENTER", color=d.P.primaryDark)
```

## 9. Timeline (duration and recovery points)

```python
tl_y = DY0 + 0.78
d.line(X0 + 0.30, tl_y, XE - 0.30, tl_y, color=lighten(d.P.muted, 0.3), weight=1.5)
for mx, label, col in [(0.55, "通常運転", lighten(d.P.muted, 0.2)),
                       (2.40, "停止開始", d.P.warning),
                       (6.30, "復帰",     d.P.primary)]:
    d.shape(X0 + mx, tl_y - 0.09, 0.18, 0.18, kind="ELLIPSE", fill=col, stroke=None)
    d.label(X0 + mx - 0.75, tl_y + 0.16, 1.70, 0.46, label, size=7.5, bold=True,
            align="CENTER", color=darken(col, 0.35))

d.shape(X0 + 2.49, tl_y - 0.34, 3.90, 0.24, kind="ROUND_RECTANGLE",
        fill=lighten(d.P.success, 0.80), stroke=None,
        text="この期間に取得", size=7.5, bold=True, color=darken(d.P.success, 0.45))
mid = X0 + 2.49 + 3.90 / 2
d.arrow(mid, tl_y + 0.72, mid, tl_y + 0.16, color=d.P.danger, weight=1.6)
```

## 10. Hierarchy tree (indented style)

```python
levels = [("カタログ", "最上位", d.P.primaryDark),
          ("データソース", "個々の DB", d.P.primary),
          ("名前空間", "schema / keyspace", lighten(d.P.primary, 0.35)),
          ("テーブル", "実体", lighten(d.P.primary, 0.60))]
for i, (nm, sub, col) in enumerate(levels):
    iy, ind = DY0 + 0.36 + i * 0.56, i * 0.22
    d.shape(X0 + 0.16 + ind, iy, 1.30, 0.32, kind="ROUND_RECTANGLE", fill=col,
            stroke=None, text=nm, size=8.5, bold=True, color="#FFFFFF")
    d.label(X0 + 1.54 + ind, iy + 0.04, 2.4 - ind, 0.26, sub, size=7.5, align="START")
    if i < len(levels) - 1:                      # かぎ線でつなぐ
        d.line(X0 + 0.30 + ind, iy + 0.33, X0 + 0.30 + ind, iy + 0.55, color=d.P.muted)
        d.line(X0 + 0.30 + ind, iy + 0.55, X0 + 0.58 + ind, iy + 0.55, color=d.P.muted)
```

---

## Available shapes

`RECTANGLE` `ROUND_RECTANGLE` `ELLIPSE` `TEXT_BOX` `DIAMOND` `CAN` (cylinder = DB)
`CLOUD` `HEXAGON` `CHEVRON` `PENTAGON` `PARALLELOGRAM` `TRAPEZOID` `PLAQUE`
`FOLDED_CORNER` `ARC` `DONUT` `STAR_5` `HOME_PLATE` `RIGHT_ARROW` `LEFT_RIGHT_ARROW`
`UP_ARROW` `DOWN_ARROW` `BENT_ARROW` `CURVED_RIGHT_ARROW` `NOTCHED_RIGHT_ARROW`
`FLOW_CHART_MAGNETIC_DISK` `WEDGE_ROUND_RECTANGLE_CALLOUT`

## Things not to do

- **Chart a number with no source.** `hbars` / `metric` should only use measured
  or published figures. If none exists, diagram the structure instead (e.g.
  "the variable that would need to change").
- **Draw a lane-crossing arrow horizontally.** It misrepresents the path.
- **Use an arrow shorter than 0.12in.** It won't render and looks like a dot.
- **Redraw the master's logo or footer yourself.** It duplicates what's already there.
- **Use a full-slide-sized opaque rectangle.** It covers and erases the master's footer.
- **Put prose in a narrow panel (under 1.5in).** It always overflows.
- **Use 4+ colors on one slide.** The meaning of color stops being readable.
