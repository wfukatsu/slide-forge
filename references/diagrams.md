*[日本語](diagrams.ja.md)*
# Drawing Diagrams (diagrams.py and the Canvas family)

Usage, drawing conventions, and self-checks for `Canvas` in `scripts/diagrams.py`
and the families mixed into it (charts / illustrations / patterns / icons /
cloud_icons / images / code_block). Colors are built from the template's
`colors`, so diagrams never stray from the theme. Coordinates are in inches; the
return value of a composite part is the bottom y of the drawn area.

```python
from diagrams import Canvas, lighten
ref = deck.add_slide("TITLE_ONLY", title="…")   # BODY を持たないレイアウトが図に向く
d = Canvas(deck, ref["slideId"], template)

d.flow(0.6, 1.0, 8.8, 0.8, ["Inner Loop", "Middle Loop", "Outer Loop"])   # 工程フロー
d.cards(0.5, 2.0, 9.0, 1.5, [("見出し", "本文"), ...])                      # 横並びカード
d.hbars(0.5, 3.6, 7.4, [("従来", 1220, "1,220h"), ("AI駆動", 56, "56h")])   # 横棒グラフ
d.metric(8.0, 3.6, 1.4, 1.0, "22x", "工数削減", color=d.P.success)          # 大きな数値
d.box(...) / d.solid(...) / d.label(...) / d.band(...) / d.arrow(...)       # 基本部品
```

There are 9 approaches (structural diagrams, tables/charts, illustration
diagrams, framework diagrams, event announcements, icons, cloud icons, images,
code blocks), and all of them are just methods on the same `Canvas`, so they can
be mixed on a single slide.
For details per family, see `references/charts.md` / `references/patterns.md` /
`references/events.md` / `references/images.md` / `references/icons.md` /
`references/cloud-icons.md` / `references/code-blocks.md`; for working examples,
see `examples/charts-demo.json` / `examples/patterns-demo.json` /
`examples/event-announcement.json` / `examples/illustration-gallery.json` /
`examples/icon-gallery.json` / `examples/cloud-architecture.json`.

## Illustration diagrams, icons, images

```python
d.icon_flow(0.5, 1.3, 9.0, [("person", "利用者"), ("server", "API"),
                            ("database", "台帳")], size=0.92)
d.asset_icon_flow(0.5, 2.6, 9.0, [("job-seeker", "求職者"), ("interview", "面接"),
                                  ("job-offer", "内定")])
d.pyramid(1.6, 2.4, 6.8, 2.4, ["経営指標", "業務指標", "システム指標"])
d.iceberg(0.5, 1.0, 9.0, 3.6, above=["画面の使い勝手"], below=["データモデル"])
d.image(0.6, 1.1, 4.2, 2.6, "assets/shot.png", fit="contain", caption="管理画面")
d.ai_image(5.2, 1.1, 4.2, 2.6, "夜間に自動でビルドが回っている様子")
```

There are 30 pictograms (`person` `server` `database` `cloud` `lock` `shield`
`bot` …). The metaphor diagrams are `pyramid` / `funnel` / `venn` / `iceberg` /
`balance` / `steps` / `layers` / `hub` / `matrix` / `before_after` /
`comparison` / `journey` / `timeline`.
For account graphs (`influence_graph` / `outcome_tree`), see
[account-graphs.md](account-graphs.md).

Brand icons are in `assets/scalar/pictograms/`, 62 of them (`evidence-chain`
`data-bank` `public-key` `interview` `consent` …). **Business vocabulary like
"data bank," "evidence chain," or "job offer" can't be drawn with
`illustrations`, so use this instead.** Names can be looked up by slug or by
their Japanese name. The assets are single-color, so by default they're tinted
to the template's primary color.

```bash
.venv/bin/python scripts/icons.py --list          # 62 種を一覧
.venv/bin/python scripts/icons.py --search 情報銀行 # 日本語名・英語名・タグで探す
```

Cloud service icons (1,757 official icons across AWS / Google Cloud / Azure) are
the `cloud_icon` family. **Never guess the name — always search and confirm it**
(filenames look like `Arch_Amazon-EC2_64.svg`, and guessing is always wrong).
**Changing color, rotating, or flipping is prohibited by each vendor's terms of
use**, so the API doesn't even expose those arguments.

```bash
.venv/bin/python scripts/cloud_icons.py --search s3            # 別名でも引ける
.venv/bin/python scripts/cloud_icons.py --list --vendor aws --category groups
```

```python
d.cloud_zone(0.45, 1.05, 9.1, 2.5, vendor="aws", title="AWS  ap-northeast-1")
d.cloud_icon_row(1.0, 1.9, 8.0, [("aws:rds", "RDS"), ("aws:simple-storage-service", "S3")])
```

**When unsure, use `illustrations`.** AI generation is more expressive but
requires a paid `GEMINI_API_KEY` (the image model has zero free-tier quota).
Shape-based drawing works offline, always follows the template's colors, and
produces the same result no matter how many times you regenerate it.

**Never put text on a rotated shape.** When using a trapezoid rotated 180
degrees, for example, passing `text=` also flips the text upside down. Draw the
shape without `text` and overlay a `label()` instead (`shape()` warns if you
pass text with a rotation other than 0/90/270 degrees).

From a deck spec (JSON), these are used via `figures`. `--dry-run` expands the
figures to coordinates and checks them without calling the API (combine with
`--strict` to exit with an error on even a single warning).

```json
{ "layout": "TITLE_ONLY_PROPOSAL", "title": "…",
  "figures": [
    { "type": "icon_flow", "x": 0.5, "y": 1.3, "w": 9.0,
      "items": [["person", "利用者"], ["database", "台帳"]] },
    { "type": "asset_icon_flow", "x": 0.5, "y": 3.1, "w": 9.0,
      "items": [["personal-info", "個人情報"], ["data-bank", "情報銀行"]] }
  ] }
```

## Tables, charts, and code blocks

Tables and full-fledged charts are in `charts` (mixed into the same Canvas —
see `references/charts.md`). Tables are native Slides tables, so users can edit
them after generation. Bar and line charts are drawn with a zero baseline,
fixed series colors (a colorblind-verified order), and direct value labels as
a matter of convention.

```python
d.table(0.5, 1.2, 9.0, ["項目", "従来", "提案"], [["構築期間", "6ヶ月", "2ヶ月"]])
d.vbars(0.5, 1.2, 6.0, 3.2, [("2023", 120), ("2024", 210), ("2025", 380)])
d.vbars_grouped(0.5, 1.2, 9.0, 3.4, ["Q1", "Q2"],
                [("従来", [40, 42]), ("提案", [18, 12])], unit="h")
d.linechart(0.5, 1.2, 9.0, 3.2, ["1月", "2月", "3月"],
            [("p95", [320, 180, 90])], unit="ms")
d.pie(0.7, 1.3, 2.8, [("移行済み", 62), ("移行中", 23), ("未着手", 15)])
```

On a page carrying a lot of information, `text_margin` (inches) tightens the
inner margin of the text so more fits in the same box. Slides has no field for
that padding, so it is produced with a negative indent (`references/api-notes.md`
§14). Pass it per call, or set `d.text_margin` once for the whole canvas.

```python
d.text_margin = 0.02                       # every shape and cell on this slide
d.table(0.5, 1.2, 9.0, headers, rows, text_margin=0.02)   # this table only
```

Code samples use `code_block` (`references/code-blocks.md`): monospace with
highlighting, square corners. Estimate the height from the effective line
height (`lines × size × ls × 1.45 / 72 + 0.14in`).

```python
d.code_block(0.5, 1.0, 6.1, 2.9, code, lang="java")  # java/graphql/json/bash
```

## Lines connecting shapes

**Never write a line connecting two shapes using raw coordinates.** `createLine`
just takes coordinates as given without validating them against any shape, so
the API won't error even if the endpoints are off. "The arrow floats away from
the shape / digs into its border" is something you can only notice by
generating the deck and looking at the thumbnail.

```python
a = d.shape(1.0, 1.0, 1.6, 0.6, text="A")    # shape() 系は objectId を返す
b = d.shape(4.0, 2.0, 1.6, 0.6, text="B")

d.connect(a, b)                  # API のコネクタとして接続。図形を動かすと線が追従する
d.connect(a, b, category="BENT") # エルボー。1対多のファンアウトで経路が交差しにくい
d.link(a, b)                     # 中心を結ぶ線と辺の交点を端点にする（斜めでもぴたり）
d.edge_point(a, (tx, ty), gap=0.04)          # 辺の一点だけ欲しいとき
d.line(..., free=True)           # 軸・目盛り・引き出し線など、接しないのが正しい線
```

| Use case | What to use |
|---|---|
| Shape A → B, should follow if moved | `d.connect(a, b)` |
| Shape A → B, should align exactly to the edge | `d.link(a, b)` |
| Waypoints, axes, leader lines | `d.line(..., free=True)` |

`connect()`'s connection sites are determined automatically from the relative
position (0=top, 1=left, 2=bottom, 3=right). `audit_connectors()` returns
endpoints that are more than 0.22in away from any shape, and endpoints that are
embedded more than 0.06in inside a shape. Large containers like zones and text
boxes are excluded from this check (an arrow passing through a container is
normal). **Always call this before generating.**

## Self-checks (4 audits, always call before generating)

All of these catch defects detectable from coordinates alone, which otherwise go
unnoticed until you look at the thumbnail.

```python
for msg in (d.audit_bounds() + d.audit_connectors()
            + d.audit_overlaps() + d.audit_text_fit()):
    print(msg)
```

| Check | Catches |
|---|---|
| `audit_bounds()` | Shapes or line endpoints that fall outside the slide |
| `audit_connectors()` | Arrows whose endpoints don't touch any shape, or are buried inside one |
| `audit_overlaps()` | Text hidden by a later shape, colliding labels, and **lines running across text** |
| `audit_text_fit()` | Text that overflows and is clipped by its box, and wrapped text leaving a single character on the last line |

`audit_bounds()` matters for composite parts. Components like `pyramid` or
`funnel`, which compute their own coordinates from a given frame, can have the
frame be correct while the contents poke outside it — something only caught by
checking per-shape.

`audit_overlaps()` uses the Slides draw order (later elements are on top). This
catches the classic mistake of a banner or zone overlapping the block placed
right before it. Nesting (placing contents inside a zone) is normal, so it's
not reported.

**It also checks overlap between lines and text.** Whether arrows, connectors,
or grid lines run across a character is judged by the crossing length between
the line segment and "the box the character actually occupies" (reported once
it exceeds `LINE_CROSS_MIN` = 0.06in). An arrowhead grazing the edge of a
character is normal and isn't flagged.

Draw order matters here too. **Drawing a line first and then covering it with a
filled shape** (as `hub()` does — it draws lines from the center to each node's
center, then places the node boxes afterward) means the line is hidden under the
fill and isn't reported. The judgment is based on whether an opaque shape drawn
after the line covers that text.

Suppression only happens when the fill shape **fully covers** the text's
bounding box. Partial coverage is still reported — the design favors catching
too much over missing something, and lets a human make the final call.

## Color and layout conventions

`d.P` is the template-derived palette (`primary` / `success` / `danger` / `info`
/ `muted` / `surface` / `border` / `text`, plus `primaryDark` / `warning` /
`surfaceAlt` / `white`). `readable_on()` automatically picks a legible text
color for a given background.

**Decide vertical position from the previous block's return value.** `cards` /
`flow` / `hbars` / `metric` return the bottom y of the drawn area, so place the
next block starting from that value. Hardcoding a value like `2.7` causes the
next block to get swallowed as content grows.

```python
b = d.cards(0.5, 0.9, 9.0, 1.0, items)     # b は下端 y
b = d.hbars(0.5, b + 0.2, 9.0, rows)       # 前のブロックの下から置く
d.label(0.5, b + 0.2, 9.0, 0.3, "まとめ")
```

Finally, confirm the bottom edge fits within the body area (for `scalar-2026`'s
`TITLE_ONLY`, that's y = 5.02).

**Text inside a box should be written with line breaks anticipating wrapping.**
A card heading that wraps to 2 lines will crowd into the body text. Rule of
thumb: "width[in] × 72 ÷ font size" characters (1 for full-width, 0.5 for
half-width). `audit_text_fit()` catches overflow using this same calculation.

**Don't allocate a box's contents by a fixed ratio of its height.** Assignments
like "0.7in for the heading" or "52% for the value" cause content to get
crushed and text to be clipped when the box is small. A custom component should
shrink its own contents to fit the given area (`metric` derives its font size
from the box height).

**A rectangle stacked with a straight accent bar shouldn't have rounded
corners.** For a card with a bar (a thin `RECTANGLE`) laid along its top or
left edge, the body must also be a `RECTANGLE`. A rounded edge and a straight
bar's end don't align cleanly and look mismatched (`cards()` is square-cornered
for exactly this reason). A standalone chip or band without a bar can stay
rounded.

## Adding content that doesn't fit the layout

When placeholders alone aren't enough, use `build_deck.py` as a library and add
shapes to the returned `slideId`:

```python
import sys; sys.path.insert(0, "scripts")
from importlib.machinery import SourceFileLoader
bd = SourceFileLoader("bd", "scripts/build_deck.py").load_module()

template = bd.load_template("templates/<id>.json")
deck = bd.TemplateDeck.create(template, title="…", folder=None)
ref = deck.add_slide("CONTENT", title="…")
deck.requests.append({"createShape": {..., "elementProperties": {"pageObjectId": ref["slideId"], ...}}})
deck.add_page_numbers()
print(deck.commit())
```

Keep coordinates between the equivalent of `contentTop` (the `body` y) in
`layouts.<KEY>.elements` of `template.json` and the footer position. Use the
`colors` keys so the colors stay within the template's palette.
