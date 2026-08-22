*[日本語](pictogram-catalog.ja.md)*
# Pictograms and Metaphor Diagrams

`scripts/illustrations.py` draws two things out of shapes alone:

1. **Pictograms** — one meaning as one picture (`person`, `server`, `database`),
   placed with `icon()` / `icon_row()` / `icon_flow()` / `icon_grid()`.
2. **Metaphor diagrams** — the shape of a relationship itself (`pyramid`,
   `funnel`, `iceberg`, `balance`), each a method on `Canvas`.

No image upload, no API key, no network. Colors come from the template's
palette, so a deck regenerates identically and follows a theme change.

**The list of names is not in this file.** It is 3KB of CLI output, read off
the code, and cannot drift:

```bash
.venv/bin/python scripts/illustrations.py --list           # 32 pictograms + 17 diagrams
.venv/bin/python scripts/illustrations.py --search flow    # by name or description
```

This file is the judgment around them: which figure to reach for, how big to
draw it, and what makes one unreadable. For the drawing API see
[diagrams.md](diagrams.md); for photographs and generated pictures see
[images.md](images.md); for Scalar's own brand pictograms — business vocabulary
like "evidence chain" that no generic icon carries — see [icons.md](icons.md).

## 1. When a shape beats a picture

| | Shape-drawn | Image (`d.image` / `d.ai_image`) |
|---|---|---|
| Reproducibility | Identical every run | An AI image differs every time |
| Theme change | Follows it | Has to be regenerated |
| Scaling | Vector, no loss | Resolution-bound |
| Cost | No upload, no key | Drive upload / Gemini key |
| What it can say | A category (a server, a user) | A specific scene, a real screenshot |

Reach for an image when the picture carries information a category cannot — a
product screenshot, a photograph, a mood-setting cover. For anything that means
"there is a database here", a shape is the cheaper and steadier answer.

## 2. Picking the figure

Match the **relationship you are showing**, not the topic you are writing
about. A slide about security is not a `shield`; a slide showing that security
sits under everything else is `layers`.

| What you are showing | Figure |
|---|---|
| A chain of steps, actor to actor | `icon_flow` |
| A set with no order or sequence | `icon_row` / `icon_grid` |
| Rank, with fewer toward the top | `pyramid` |
| Narrowing at every stage | `funnel` |
| Shared ground between 2–3 things | `venn` |
| A visible sliver over a hidden bulk | `iceberg` |
| A trade-off between two options | `balance` |
| Climbing, each step resting on the last | `steps` |
| A stack, each layer carried by the one below | `layers` |
| One centre, many spokes | `hub` |
| Two axes, four quadrants | `matrix` |
| Options side by side | `comparison` |
| The same subject before and after | `before_after` |
| Milestones along a path or a period | `journey` / `timeline` |

If no relationship fits, the content is probably a table or a chart — see
[charts.md](charts.md) and [patterns.md](patterns.md).

## 3. Size

`size` is the side of the square the pictogram is drawn in, in inches.

| Use | Size | Floor | Note |
|---|---|---|---|
| Inline, beside text | 0.30–0.40 | 0.25 | Match the line height |
| Inside a card | 0.40–0.60 | 0.35 | 20–30% of the card width |
| In a grid | 0.50–0.70 | 0.40 | 25–35% of the cell width |
| The slide's main visual | 0.80–1.20 | 0.60 | |
| Hero, on a title slide | 1.50–2.00 | 1.00 | |

The page is 10.0 × 5.625in (Slides normalizes 16:9 to 0.75× PowerPoint's
inches), and diagrams live in y 0.84–4.30 — see `deckkit`'s `X0 / W / DY0 /
DY1`.

Text placed **inside** a shape, by shape size:

| Shape | 1 char | 2–3 chars | 4+ chars |
|---|---|---|---|
| 0.3in | 12pt | 8pt | won't fit |
| 0.4in | 16pt | 10pt | 8pt |
| 0.5in | 18pt | 12pt | 9pt |
| 0.6in | 22pt | 14pt | 10pt |
| 0.8in | 28pt | 18pt | 12pt |
| 1.0in | 36pt | 22pt | 14pt |

**8pt is the floor.** Below about 7pt legibility falls off a cliff, and
`audit_text_fit()` will not save you — it checks that the text fits the box,
not that a reader can make it out.

## 4. Color

Colors are semantic, taken from the palette (`d.P.*`) built from the template's
`colors`. Never hard-code a hex: the point of the palette is that a template
swap carries the deck with it.

| What the element is | Palette entry |
|---|---|
| Our own product | `d.P.primary` |
| An external system | `d.P.muted` |
| The user, the client side | `d.P.warning` (as a fill, see below) |
| Success, the normal path | `d.P.success` |
| Failure, the error path | `d.P.danger` |
| Something new or highlighted | `d.P.info` |
| Background zones and rules | `d.P.surface` / `d.P.border` |

`tone_colors(d, tone)` returns the matching (fill, stroke, text) triple for
`primary` / `info` / `good` / `warn` / `bad` / `muted` / `accent`, and
`tone_solid(d, tone)` the solid version. Prefer them over picking three colors
by hand.

Measured against the scalar-2026 palette on white:

| Color | Hex | Contrast on white | As text |
|---|---|---|---|
| `text` | `#0F172A` | 17.9:1 | yes |
| `primaryDark` | `#194B7A` | 9.0:1 | yes |
| `primary` | `#2673BB` | 4.9:1 | yes |
| `muted` | `#6B7280` | 4.8:1 | yes |
| `danger` | `#EE2155` | 4.2:1 | large text only |
| `info` | `#0985FD` | 3.6:1 | large text only |
| `success` | `#63C045` | 2.3:1 | **fill only** |
| `warning` | `#FFEF24` | 1.2:1 | **fill only** |

> `success` and `warning` are fills, not text colors. Green-on-white and
> yellow-on-white both fail AA. Put white or `text` on top of them instead.

Fill and stroke:

| Style | Use | Call |
|---|---|---|
| Solid | The main element | `fill=c, stroke=None` |
| Outline only | A supporting element | `fill=None, stroke=c` |
| Pale fill, dark edge | A supporting element worth emphasis | `fill=lighten(c, 0.85), stroke=c` |
| On a dark band | Anything over a dark background | `fill=d.P.page, stroke=c` |

## 5. Rows, grids and flows

```python
d.icon_row(0.5, 1.3, 9.0, [("person", "利用者"), ("browser", "アプリ"),
                           ("database", "台帳")], size=0.8)
d.icon_grid(0.5, 1.3, 9.0, ["server", "cloud", "lock", "chart"], cols=4)
d.icon_flow(0.5, 2.6, 9.0, [("person", "申込"), ("bot", "審査"),
                            ("database", "記録")], size=0.92)
```

`icon_flow` needs room between the pictograms for its arrows, and refuses to
draw rather than overlap them: if `size` leaves no gap it raises with the
maximum size that would fit. Either take that size, widen `w`, or drop to
`icon_row`, which has no arrows to fit.

Captions collide before pictograms do. **Run `audit_overlaps()` and
`audit_text_fit()` after drawing** — a long label under a 0.5in icon is the
usual cause, and it is caught at coordinate time, before any API call.

## 6. Unicode marks, without a shape

For an inline marker, a character in the text run costs nothing and needs no
figure at all.

| Char | Code | Use | Renders in Noto Sans JP / Arial |
|---|---|---|---|
| ✓ | U+2713 | supported, done | reliably |
| ✗ | U+2717 | unsupported, failed | reliably |
| ● ○ | U+25CF / U+25CB | filled / empty marker | reliably |
| ▶ | U+25B6 | next, play | reliably |
| ◆ | U+25C6 | emphasis marker | reliably |
| ★ ☆ | U+2605 / U+2606 | rated / unrated | reliably |
| → | U+2192 | flow, direction | reliably |
| ⬆ ⬇ | U+2B06 / U+2B07 | up, down | reliably |
| ∞ | U+221E | unbounded | reliably |
| ⚡ ⚙ | U+26A1 / U+2699 | fast / settings | patchy — prefer a pictogram |

Color emoji (🚀 💡 📊) render differently per platform and should not carry
meaning on a slide.

## 7. What a figure costs in requests

`batchUpdate` is chunked at 500 requests, and a pictogram-heavy page adds up
faster than it looks.

| | Requests each |
|---|---|
| A plain shape | 2–3 |
| A shape carrying text | 5–7 |
| Add a caption below it | +4 |

A 6-cell `icon_grid` with captions is therefore 40–60 requests on its own. Two
levers: leave the per-icon caption off when the text beside the grid already
says it, and use a Unicode mark instead of a shape for ✓/✗ markers.

## 8. Notes

- **Three shapes is the ceiling** for one composite pictogram. Past that it
  reads as clutter rather than as a symbol.
- **Later shapes are drawn in front.** Add the background first; the audit's
  hidden-text check exists because this is easy to get backwards.
- **Size sub-shapes as ratios of `size`**, never as absolute inches, or the
  pictogram falls apart at a different scale.
- **A label belongs outside the figure**, not inside the shape, unless it is
  one or two characters.

## Appendix. shapeType cheat sheet

Concept → Slides `shapeType`, for when you draw a custom shape with
`d.shape(..., kind=...)` rather than using a ready-made pictogram.

| To express | shapeType | Alternative |
|---|---|---|
| Database | `CAN` | `FLOW_CHART_MAGNETIC_DISK` |
| File, document | `FLOW_CHART_DOCUMENT` | `FOLDED_CORNER` |
| Cloud | `CLOUD` | `CLOUD_CALLOUT` |
| Server, machine | `ROUND_RECTANGLE` | `RECTANGLE` |
| Security | `PENTAGON` | `FLOW_CHART_PREPARATION` |
| Processing step | `FLOW_CHART_PROCESS` | `RECTANGLE` |
| Decision, branch | `FLOW_CHART_DECISION` | `DIAMOND` |
| API, service | `ROUND_RECTANGLE` + text | `HEXAGON` + text |
| Container | `CUBE` | `ROUND_RECTANGLE` |
| Network | `HEXAGON` | `OCTAGON` |
| Queue, stream | `CHEVRON` | `RIGHT_ARROW` |
| Goal, target | `DONUT` | `STAR_5` |
| Important, priority | `STAR_5` | `STARBURST` |
| Prohibited | `NO_SMOKING` | `MATH_MULTIPLY` |
| Fast, performance | `LIGHTNING_BOLT` | Unicode ⚡ |
| Direction, flow | `RIGHT_ARROW` family | `CHEVRON` |
