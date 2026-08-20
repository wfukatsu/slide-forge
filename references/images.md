*[日本語](images.ja.md)*
# Illustrative Figures and Images

There are 5 ways to draw something that bullet points can't fully explain. **Choose based on
purpose first.**

| What you want to show | What to use | Characteristics |
|---|---|---|
| Structure, procedure, or numeric relationships | `diagrams.Canvas` (`flow` / `cards` / `hbars` / `connect`) | Precise. Relationships between elements are guaranteed |
| Concept, metaphor, characters | `illustrations` (`icon_flow` / `pyramid` / `iceberg` …) | Drawn with shapes. **No network needed, same picture every time**, themed colors |
| Icons for business vocabulary | `icons` (`asset_icon` / `asset_icon_flow` …) | 62 Scalar-branded assets. On-brand. **Requires network access**. See `icons.md` |
| Cloud architecture diagrams | `cloud_icons` (`cloud_icon` / `cloud_zone` …) | 1,757 official AWS/GCP/Azure icons. **Changing color or rotation is forbidden**. See `cloud-icons.md` |
| Mood, scenery, cover art | `images` (`ai_image` / `image`) | AI-generated or your own images. High expressive power, but reproducibility depends entirely on the generation-time cache |

All of these hang off `Canvas` as methods, so they can be mixed on the same slide.
Coordinates are always in inches, the origin is the slide's top-left, and **the return value is
the bottom y of the drawn area**.

```python
d = Canvas(deck, ref["slideId"], template)
b = d.icon_flow(0.7, 1.1, 8.6, [("person", "利用者"), ("server", "API")])
b = d.label(0.7, b + 0.2, 8.6, 0.3, "…")
```

---

## 1. Pictograms (`illustrations`)

30 types. `icon()` draws into a size×size square; pass `label` to add a caption below.

```
person people server database cloud document documents gear lock shield
browser mobile bot chart clock check cross warning mail key
network code stack folder bulb search sync flag coin chip
```

| When to use | Method |
|---|---|
| Place a single one | `icon(name, x, y, size, color=…, label=…)` |
| Line them up horizontally | `icon_row(x, y, w, items)` |
| Connect with arrows into a flow | `icon_flow(x, y, w, items)` |
| Arrange in a grid | `icon_grid(x, y, w, items, cols=4)` |

`items` is a name, or `(name, label)`. Color is a single `color=` value, or a per-element list.

```python
d.icon_flow(0.5, 1.3, 9.0, [
    ("person", "利用者"), ("browser", "Web アプリ"),
    ("server", "API"), ("database", "台帳"),
], size=0.92)
```

**Caption width defaults to twice `size`.** When packing icons tightly side by side, set
`label_w` explicitly to match the cell width. Left alone, captions collide with the neighboring
one and get caught by `audit_overlaps()`.

**`icon_flow` draws its arrow into the gap of `w / count − size − 0.2in`.** If you enlarge the
icons, this can go negative, causing an arrow meant to point right to be drawn backward (since
it's an `_anchored` line, `audit_connectors()` won't catch it). When the gap runs out it stops
with a `ValueError`; either lower `size`, widen `w`, or switch to `icon_row`, which needs no
arrow. In tight frames (e.g. cover or section-divider cards), `icon_row` tends to fit better.

### Using branded icons

Since the 30 types in `illustrations` are generic parts, they can't depict business vocabulary
like "data bank," "evidence chain," or "job offer." For that, use the branded assets (62 types)
in `assets/scalar/pictograms/`. The usage is the same shape, just with `asset_` prefixed to the
method name.

```python
d.asset_icon_flow(0.5, 1.15, 9.0, [("job-seeker", "求職者"), ("interview", "面接")])
```

The catalog, search, color handling, and constraints are all covered in
**`references/icons.md`**.

## 2. Metaphor diagrams (`illustrations`)

| Method | What it shows | Key arguments |
|---|---|---|
| `pyramid(x,y,w,h,levels)` | Hierarchy — fewer and higher-ranked toward the top | `captions=` for a note to the right of each tier |
| `funnel(x,y,w,h,stages)` | Narrowing down, with a count attached per stage | `stages=[(label, value)]` |
| `venn(x,y,w,h,sets)` | Overlap. 2 or 3 sets | `center=` for a label in the shared area |
| `iceberg(x,y,w,h,above,below)` | The small visible part vs. the bulk underwater | `art_ratio=` for the split between art and text |
| `balance(x,y,w,h,left,right)` | Comparing two options | `tilt=1` weights the right side heavier |
| `steps(x,y,w,h,items)` | Climbing through stages | Left is first, right is last |
| `layers(x,y,w,h,items)` | Stacked layers, e.g. a technology stack | `items=[(label, note)]` |
| `hub(x,y,w,h,center,spokes)` | A center with radiating spokes | For when the center is the main subject |
| `matrix(x,y,w,h,quadrants)` | Positioning across 4 quadrants | Order: top-left, top-right, bottom-left, bottom-right. Axes are `(bottom, top)` `(left, right)` |
| `before_after(x,y,w,h,before,after)` | Side-by-side contrast | An arrow appears in the middle. A 2-column specialization of `comparison` |
| `comparison(x,y,w,h,columns)` | Lining up N options side by side | `columns=[(heading, [item…])]`. `arrows=True` only for a transition; `highlight=i` emphasizes the recommended option |
| `influence_graph(x,y,w,h,people)` | Laying out stakeholders in an org structure | Role = top band / influence = bottom band / stance = fill / not yet met = dashed. `links` for peer relationships, `more` for an omitted count. Data is validated by `account_graph.py` |
| `outcome_tree(x,y,w,h,nodes)` | The support relationships of Goal / Strategy / Tactics | `edges` go from the supporting side to the supported side. **Tiers are graph depth, not fixed tiers**. Multiple parents allowed |
| `journey(x,y,w,h,milestones)` | A path, alternating above and below | `milestones=[(heading, note)]` |
| `timeline(x,y,w,items)` | A horizontal chronology | `items=[(point in time, heading)]` |

**When writing a JSON spec, positional arguments like `levels` / `stages` / `sets` / `spokes` /
`milestones` are all passed under the key name used in the `FIGURES` definition (usually
`items`).** The Python signature's argument names don't carry over as-is (though ones with
distinct names on the `FIGURES` side too, like `hub`'s `center` or `iceberg`'s `above` /
`below`, stay unchanged).

### Content that spills outside the frame

`pyramid(captions=…)` and `funnel`'s value labels use the space **just outside the right edge of
`x + w`**. Leave that margin when deciding `w`. If you don't, `audit_bounds()` fails with "goes
outside the slide."

### Trapezoids are not drawn with `TRAPEZOID`

Slides' `TRAPEZOID` has its **top-edge inset fixed at height × 0.25**, and neither width nor
scaleY can change it (measured empirically; `api-notes.md` section 15). Stacking a pyramid or
funnel whose width differs tier by tier with this shape makes the slope change from tier to
tier, producing a jagged outline.

So `pyramid` / `funnel` draw each tier as 3 parts: a center rectangle plus a right-angle triangle
on each side (`_taper()`). Each tier's top edge is aligned to the tier above's bottom edge, so
the outline connects in one continuous line. Use `_taper()` too if you want to draw your own
trapezoid.

### Never put text on a rotated shape

Shapes like the pentagon (`shield`) are used rotated 180 degrees. **Rotating it also rotates any
text inside, rendering it upside down.** Draw the shape with no `text`, and overlay the text
separately via `label()`. `shape()` warns if text is added to a rotation other than 0/90/270
degrees.

`label(rotation=270)` can be used to intentionally make text vertical, but **don't use it for
Japanese.** The characters end up sideways and hard to read. When a vertical label is needed,
stack it one character per line (this is how `matrix`'s vertical-axis label is done).

---

## 3. Images (`images`)

### Placing an existing image

```python
d.image(0.6, 1.1, 4.2, 2.6, "assets/screenshot.png", fit="contain",
        caption="管理画面", outline="#D6E4F2")
```

The caption's position is controlled by `caption_at`.

- `"image"` (default) — the image's actual bottom edge. Use this when placing a single image
- `"box"` — the frame's bottom edge. **Use this when placing images side by side**. When `fit`
  differs, the images' bottom edges shift, so with the default setting caption heights won't
  line up

`source` is one of:

- A local path (**resolved from the current working directory at runtime**)
- An `http(s)://…` URL
- A Drive file URL, or `drive:<fileId>`

| `fit` | Behavior |
|---|---|
| `contain` (`image()`'s default) | Fits within the frame preserving aspect ratio. Leaves margins |
| `cover` | Fills the frame, cropping whatever overflows |
| `stretch` | Stretches to fit the frame (distorts aspect ratio) |

**`ai_image()`'s default is `cover`** (fills the frame). Since the generated aspect ratio never
matches the frame exactly, `contain` would expose the template's background in the margins. See
"Generating to match the frame."

Slides only accepts **PNG / JPEG / GIF**, under 50MB and under 25 megapixels. Anything else
errors out before insertion.

### If the template has an image slot, place it there

**Check the layout's `imageSlots` before deciding coordinates yourself.** Layouts like covers,
section dividers, or case-study introductions often carry a "put the picture here" slot, and
missing it makes the result look detached from the template's design.

```json
{ "layout": "SECTION", "title": "第1章 …",
  "figures": [ { "type": "aiImage", "prompt": "…", "style": "isometric" } ] }
```

Omitting `x` / `y` / `w` / `h` lets `build_deck.py` fill in the slot's coordinates, and also
sets `fit` to `"cover"` (since the slot's aspect ratio is itself part of the design, filling the
slot suits it better than fitting with margins). For a layout with multiple slots, select one
with e.g. `"slot": 1`.

For `aiImage`, **the artwork itself is generated to match the slot** (drawn at the ratio closest
to the slot's, with the composition instructed to account for what will be cropped). See
"Generating to match the frame" for details.

```bash
# See which layouts have which slots
python scripts/inspect_template.py <URL>        # the report shows imageSlot[N]
```

If a slot exists but you place the image elsewhere, `--dry-run` warns (`--strict` turns it into
an error). For layouts without a slot, decide the coordinates yourself as before.

To fill empty slots in **a deck that's already been built**, use `scripts/fill_image_slots.py`
(the `image-slots` skill). This targets decks with no spec, or decks whose URL can't change.

```bash
python scripts/fill_image_slots.py <URL> --dry-run   # see which slots would be filled
python scripts/fill_image_slots.py <URL>
```

### Generating with AI

```python
d.ai_image(5.2, 1.1, 4.2, 2.6,
           "自律型エージェントが夜間にビルドを回している様子",
           style="flat_vector")
```

```bash
# Try it standalone (--show-prompt shows just the prompt, without calling the API)
python scripts/images.py --prompt "…" --style flat_vector \
    --template templates/aixdevops.json --out out/hero.png
```

| `style` | Suited for |
|---|---|
| `flat_vector` (default) | General illustration for business materials. Line art with the theme's colors |
| `line_art` | Light decoration. Doesn't compete with the text |
| `isometric` | System architecture or infrastructure overviews |
| `blueprint` | Technical-design metaphors |
| `paper` | A softer feel for section dividers |
| `photo` | Backgrounds for covers or section dividers. Not suited for explanatory figures in body text |

- The prompt automatically has **the template's color palette** appended (sourced from
  `d._template_colors`), along with constraints like "don't draw text or logos" and "leave
  margins."
- Omitting `aspect` **generates it to match the frame**. See the next section for details.
- Output is cached at `cache/images/<hash>.png`. The key is
  (model, style, aspect ratio, full prompt text). **The same spec produces the same picture even
  if you rebuild the deck.** The prompt is kept in a sidecar `.json`.
- Requires `GEMINI_API_KEY`. The default model is `gemini-3.1-flash-image`
  (changeable via `GSLIDES_IMAGE_MODEL`).

> **The image model has zero free-tier quota.** If the key belongs to a free-tier project, it
> returns `HTTP 429 / limit: 0`. You need an API key from a project with billing enabled.
> The shape-based `illustrations` still works without any key.

> **Generation can be switched off entirely** — `imageGeneration: false` in
> `config/settings.json` (`.venv/bin/python scripts/settings.py --image-generation off`).
> `generate()` then refuses before the cache lookup, `build_deck.py` rejects `aiImage` during
> spec validation, and `fill_image_slots.py` stops before reading the deck. Check it with
> `scripts/settings.py --show` before offering AI imagery. See `references/settings.md`.

### Generating to match the frame

Omitting `aspect` generates the image to match the destination frame (whether that's a
template's `imageSlots` or coordinates you chose yourself). However, **the model can only
produce 10 aspect ratios**, so it never matches the frame's ratio exactly.

The gap is closed with two steps:

1. Generate at the ratio **closest to the frame's**
2. Fill the remaining difference by cropping with `fit="cover"`. `ai_image`'s `fit` defaults to
   `cover` and always fills the frame (`contain` would expose the template's background in the
   margins)

Cropping happens from the center, so a subject positioned near an edge can get clipped. To avoid
this, whenever the ratio mismatch exceeds 2%, the prompt is given **a composition instruction
that accounts for what will be cropped** ("fits into a 1.13:1 frame with about 9% cropped off
the left and right; keep the subject centered, and don't put anything you want to keep near the
edges"). At generation time it prints something like:

```
  note: 1.13:1 の枠に対して 5:4 で生成します（切り取りで主題が欠けない構図を指示済み）
```

Since the frame's ratio is embedded in the full prompt text, it also affects the cache key.
**Placing the same image into a differently-shaped frame triggers a regeneration** (redrawn with
a composition suited to that frame).

To choose the ratio yourself, set `aspect` explicitly. In that case, matching it to the frame is
treated as your responsibility, and no composition instruction is added.

### What happens under the hood (for local images)

1. Existence, format, and size are checked (entirely local; a rejected spec raises an exception
   at the `d.image()` call site)
2. A temporary upload to Drive plus granting "anyone with the link can view" is **dispatched to a
   separate thread** (`AssetStore.defer()`). `createImage` fetches the URL **anonymously**, so
   being able to access it as your authenticated self isn't enough
3. Since real dimensions are read from the local file, placement can be decided without waiting
   for the URL to resolve. `createImage` is assembled with `url` left empty for now
4. At the start of `commit()`, it waits for every upload to finish and fills in `url`
   (`AssetStore.flush()`). The same source is uploaded only once no matter how many times it's
   pasted
5. Inserted via `batchUpdate` (Slides copies the image into the presentation)
6. Immediately after, the temporary file is deleted and any public sharing added for existing
   files is revoked (`AssetStore.cleanup()`, run in parallel)

An upload measures 3.1 seconds per image in practice (1.9s upload + 1.2s setting sharing). If
each image were awaited synchronously mid-render, a 10-image deck would burn over 30 seconds on
images alone, so steps 2–4 are pushed to the background instead (measured 37.3s → 16.9s).

Remote (http / Drive) sources need the URL itself to read the real dimensions, so those are
resolved synchronously.

If your organization's policy forbids "anyone with the link" sharing, step 2 fails. In that
case, either pass a URL that's already public, or draw with `illustrations` instead.

Cleanup for an interrupted run is registered with `atexit`. It waits for any in-flight uploads
before shutting down, so no temporary file is left in a public state.

---

## Using it from a deck spec (JSON)

In `build_deck.py`'s spec, a slide can be given `figures`.

```json
{
  "layout": "TITLE_ONLY_PROPOSAL",
  "title": "利用者から台帳まで",
  "figures": [
    { "type": "icon_flow", "x": 0.5, "y": 1.3, "w": 9.0, "size": 0.92,
      "items": [["person", "利用者"], ["server", "API"], ["database", "台帳"]] },
    { "type": "image", "x": 0.5, "y": 3.2, "w": 4.0, "h": 1.6,
      "source": "assets/shot.png", "fit": "cover" },
    { "type": "aiImage", "x": 5.0, "y": 3.2, "w": 4.0, "h": 1.6,
      "prompt": "夜間に自動でビルドが回っている様子", "style": "flat_vector" }
  ]
}
```

- The canonical `type` list lives in `scripts/build_deck.py`'s `FIGURES` dict (45 types). See
  `references/template-schema.md` for the list grouped by family.
- Keys other than the positional arguments are converted from **camelCase to snake_case** before
  being passed through (`labelSize` → `label_size`, `xAxis` → `x_axis`).
- `--dry-run` expands the figures into coordinates without calling the API at all, checking for
  overflow, overlap, and text spillover. **Images require fetching the real file, so they're
  excluded from this check.**

---

## The 4 checks to always run before generating

```python
for msg in (d.audit_bounds()        # shapes that go outside the slide
            + d.audit_connectors()  # dangling or overlapping lines
            + d.audit_overlaps()    # hidden or colliding text
            + d.audit_text_fit()):  # text overflow, and ugly wrapping
    print(msg)
```

`audit_text_fit()` checks two kinds of problems.

1. **Overflow** — too much text for the frame, spilling out and becoming unreadable
2. **Orphan lines** — a wrapped last line with only a single character left ("…デプロ / イ").
   It technically fits, but is obviously unsightly, and widening the frame by a few mm fixes it

The number of characters that fit on one line is estimated **after subtracting Slides' text-box
left/right insets (0.1in each)**. Without subtracting them, the estimate allows 1–2 extra
characters, so the check passes even though the text actually wraps.

`build_deck.py` runs this automatically when generating from a spec, and prints the results.
Adding `--strict` makes it exit with code 1 if even one issue is found.

`audit_bounds()` catches figure parts that poke outside their frame. Since parts compute their
own coordinates from the given frame, **content can go outside even when the frame itself is
correct**, and this can only be caught by looking at each figure individually.
