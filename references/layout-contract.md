*[日本語](layout-contract.ja.md)*

# Layout Contract (Coordinates and Measured Values)

Diagram decks break almost entirely because of coordinate mistakes. The
numbers here were **measured from actual generated output** on a 16:9
(10 × 5.625in) template. They are not estimates.

## Coordinate System

- Units are inches. The origin is the top-left of the slide; x increases to the right, y increases downward.
- Internally these are EMU (1in = 914,400 EMU). `_auth.inches()` performs the conversion.
- Google Slides defaults to 10 × 5.625in. Confirm against the template's `pageSize`.

## Safe Area

```
y=0.000  ┌──────────────────────────────────────────┐
         │                                          │
y=0.126  │  ■ TITLE プレースホルダ（h=0.351）        │  ← 1 行なら y=0.48 で終わる
y=0.480  │                                          │
         │  ← ここから下がタイトルの「下」            │
y=0.840  │ ┌──────────────────────────────────────┐ │  DY0：図の上端
         │ │                                      │ │
         │ │        図を描いてよい領域              │ │  高さ 3.46in
         │ │                                      │ │
y=4.300  │ └──────────────────────────────────────┘ │  DY1：図の下端
y=4.380  │  要点行（最大2行 / 10.5pt）               │  NY   ← foot() が描く
y=4.860  │  提供・補足行（1行 / 9pt）                │  EY   ← foot() が描く
y=5.197  │  ■ マスターのロゴ・著作権フッター          │  ← ここから下は触らない
y=5.625  └──────────────────────────────────────────┘

x=0.5 ─────────── 描画幅 W=9.0 ─────────── x=9.5
```

`deckkit` constants: `X0=0.5` `W=9.0` `XE=9.5` `DY0=0.84` `DY1=4.30` `NY=4.38` `EY=4.86`

Labels are center-aligned and tend to spill slightly outside their box, so the checker allows 0.25in of margin on both sides.

## Keep the Title to One Line

**When the title wraps to 2 lines, it crosses `DY0` and overlaps the figure.** This is the single most common way a deck breaks.

The check uses full-width-equivalent character width (full-width = 1.0, half-width = 0.5). Measured at 20pt bold:

| Full-width-equivalent width | Result |
|---|---|
| 31.0 | Fit on one line |
| 33.0 | Wrapped to 2 lines |
| 35.0 / 36.0 | Wrapped to 2 lines |

→ Set the ceiling at **30.5** (`TITLE_EM_MAX`). Measure with `deckkit.em(title)`.

For templates with a different title size, the ceiling changes too. As a rule of thumb, use about 0.95 × `width(pt) ÷ font size(pt)` (for 20pt / 9.0in: 648 ÷ 20 × 0.95 ≈ 30.8).

## Line Count in the Body Placeholder

Google's `lineSpacing` is a **percentage of the font's intrinsic line height**, not an absolute value. Noto Sans JP has a line height of about 1.45em, so the actual height of one line is:

```
行高(in) = フォントサイズ(pt) × 1.45 × lineSpacing(%) ÷ 100 ÷ 72
```

| Setting | Height per line | Lines that fit in h=4.068in |
|---|---|---|
| 13pt / 160% | 0.419in | 9.7 lines |
| 12pt / 120% | 0.290in | 14.0 lines |
| 12pt / 115% | 0.278in | 14.6 lines |

`deckkit`'s default is **12pt / 120% (14 lines max)**. Fitting 12 lines at 13pt / 160% breaks through the footer (this actually happened).

The number of characters per line is `width(pt) ÷ font size(pt)`. At 9.0in / 12pt that's 54 full-width characters. To avoid awkward wraps, stay around 46 full-width characters.

## Height When Stacking Parts

Content inside a `zone` must be drawn at `y + 0.34` or below so it doesn't collide with the heading.

| Part | Standard height | Notes |
|---|---|---|
| `zone` heading | 0.34 | Content starts below this |
| Box (1 line) | 0.30–0.36 | 8–9pt text |
| Box (2 lines) | 0.44–0.52 | Add `line_spacing=105–110` |
| Box (heading + description) | 0.62–0.80 | Heading 0.24 + description |
| `grid` header row | 0.30–0.32 | |
| `grid` data row | 0.245–0.30 | Can be tightened to 0.245 when there are many rows |
| `pills` per row | 0.19–0.28 | `gap` is 0.04–0.08 |
| `Canvas.cards` | 0.72–1.05 | Heading + 2–3 lines of body text |
| `db` (cylinder) | 0.42–0.60 | **The label extends 0.22in below (0.42in if it has a sub-label)** |
| Full-width banner | 0.34–0.52 | |
| Vertical arrow | **0.12 or more** | At 0.10 or less it doesn't render and looks like a dot |

The `db()` label sits outside the shape itself, so include it when computing the bottom edge. Forgetting this causes the checker to fail.

## Patterns That Commonly Break

| What was done | What happened | The fix |
|---|---|---|
| 13 lines at 13pt / 160% | The last line overlapped the footer | 12pt / 120%, 14 lines max |
| A 33-character title | Wrapped to 2 lines and covered the figure | Keep to ≤ 30.5 full-width characters |
| Right panel width of 1.15in | Text overflowed the box | Redistribute the widths. If too narrow, move it to a full-width card below |
| Drew an arrow horizontally across lanes | The arrow appeared to end in mid-air | Connect the actual start/end coordinates (a diagonal line is fine) |
| Placed a label directly above the arrow | It overlapped the rule and became unreadable | Set `align` to START/END to push it outward |
| Routed the loop-back arrow over the body text | It crossed through the text | Route it through the gutter between columns as an elbow (three line segments) |
| Drew an arrow at 0.10in | It looked like a dot | Use 0.12in or more |
| Specified arrow endpoints by coordinate | It floated off the shape or was buried inside it | Use `connect()` or `link()` to reference the shape |
| Let a label spill outside its `zone` | It overlapped the block below (e.g. a table header row) | Keep supplementary text inside the marker or box |

## What the Checker Sees and Doesn't See

`validate_layout.py` catches 8 kinds of defects that can be determined from coordinates alone.

| Sees | What it checks |
|---|---|
| Overflow | The figure extends past the footer area (`DY1`) or off the left/right edges |
| Title | Wraps to 2 lines and encroaches on the figure area |
| Drawing exceptions | Errors in coordinate arithmetic |
| Layout | Inconsistent role names or placeholders |
| Connectors | An endpoint isn't attached to any shape, or is buried inside one |
| **Hidden** | An opaque shape drawn **after** some text covers that text |
| **Collision** | Unfilled labels overlap within the area where their text actually renders |
| **Text overflow** | The required line count exceeds the height of the box |

Hidden-text detection uses Slides' draw order (later elements sit on top). This catches the common mistake of a banner or zone overlapping the block drawn right before it. Nesting (placing content inside a zone) is normal and is not reported. Collision detection uses **the area the text actually occupies**, not the bounding box — using the box would produce a flood of false positives whenever a label with generous padding merely brushes its neighbor.

**What it doesn't see** (requires eyeballing the thumbnail):

- Whether an arrow **crosses over** another shape (presence of a connection is detectable; route quality is not)
- Whether an arrow connects to the "correct" shape (an accidental A→C connection meant to be A→B won't be flagged)
- Contrast, and whether the figure actually communicates what it's meant to

## Don't Divide a Region by Fixed Ratios

Allocating a box's height by a fixed split — "0.7in for the heading," "52% for the number" — crushes the content when the box is small and cuts off text. This has actually broken four components.

| Component | How it broke | The fix |
|---|---|---|
| `Canvas.cards` | Took the body area as `h - 0.70`; at `h=0.82` only 0.12in remained for the body and it got cut off | Relaxed to `h - 0.58` |
| `stats` / `Canvas.metric` | The number's font size was fixed, so a short box caused overflow that collided with the description | **Compute the font size from the box height and auto-shrink** |
| `cycle` | With a small radius, opposing boxes collided | Auto-adjust box width to match the radius |

**Components should shrink themselves to fit the space they're given** rather than trusting the caller's numbers and overflowing. When writing a new component, shrink `h` to an extreme and confirm it still passes `audit_text_fit()`.

## For a Different Page Size

```python
configure_layout(page_w=13.333, page_h=7.5, margin=0.6,
                 diagram_top=1.0, diagram_bottom=5.9,
                 note_y=6.0, edition_y=6.5, title_em_max=40)
```

How to decide the values:

1. `diagram_top` = the template's `elements.title` `y + h`, plus about 0.3
2. `diagram_bottom` = the smallest `y` among `masterDecorations`, minus about 0.9 (leaving room for 2 lines of the takeaway row)
3. `title_em_max` = `title width(pt) ÷ title font size(pt)` × 0.95

After configuring, confirm both that `validate_layout.py` passes and that the thumbnail shows no actual breakage.

## API-Side Constraints

- **There's no request that resizes an element after the fact.** `updatePageElementTransform` only changes position and scale. Placeholders in a `predefinedLayout` have a fixed width, so if you need the title to reliably fit on one line, draw it as a coordinate-positioned text box with the template's `drawText` instead.
- A `SLIDE_NUMBER` placeholder cannot be generated. `add_page_numbers()` draws it manually.
- `batchUpdate` gets **slower the more it's split up**, so send as few batches as possible (measured values in `references/api-notes.md` §8). `build_deck.py`'s `_batches()` automatically splits at a ceiling of 10,000 requests / 5MB (`MAX_REQUESTS_PER_BATCH` / `MAX_BATCH_BYTES`). A 55-page diagram deck runs about 6,000 requests, so it usually fits in a single batch.
- The `objectId` of speaker notes isn't known until after the slide is created, so it's fetched again and sent as a second request after the main `batchUpdate` (handled by `commit()`).
- A full-size opaque rectangle will cover and hide the master's footer.
- **The API does not error out if a connector's endpoints are misaligned.** `createLine` accepts coordinates as-is and does not validate them against shape positions. To bind a connector to a shape, use `startConnection` / `endConnection` in `updateLineProperties` (this is what `Canvas.connect()` does). Connection sites are the same across all shapes: 0=top, 1=left, 2=bottom, 3=right.
