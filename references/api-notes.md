*[日本語](api-notes.ja.md)*

# Google Slides API constraints and pitfalls

Behavior confirmed through hands-on testing. Much of this is not documented anywhere.

---

## 1. Masters/layouts "cannot be created" but "can be edited"

Among `presentations.batchUpdate` request types, there is no type that **creates a new**
master or layout (no `Request` schema type includes `Master` / `Layout`). The colorScheme
also cannot be changed — attempting it returns `Resetting the color scheme is not supported`.

On the other hand, the contents of an **existing** master/layout can be modified. All of the
following have been confirmed to work by hands-on testing:

| Operation | Possible? |
|------|------|
| Change a shape's fill on a layout (`updateShapeProperties`) | Yes |
| Change the background color of a layout/master (`updatePageProperties`) | Yes |
| Add a shape to a layout (`createShape` + layout ID as `pageObjectId`) | Yes |
| Delete an image/shape on a layout (`deleteObject`) | Yes |
| Change the default font of an empty placeholder (`updateTextStyle`) | Yes |
| Change the color of text on a master | Yes |
| **Create** a new master/layout | No — no such request type |
| Change the colorScheme | No — `Resetting the color scheme is not supported` |
| Change a layout's display name | No |

**Changes are inherited by new slides created from that layout** (verified).

**Consequences**:

- To build materials with a branded design, the basic approach is to duplicate a template
  built in the UI. This is why this skill uses the duplication approach.
- Starting from an existing template, **you can programmatically create derivative masters
  with different color schemes**. However, since the colorScheme itself cannot be changed,
  theme color references such as `theme:ACCENT6` still resolve against the original color
  scheme. When creating a derivative, you must **explicitly override every element that
  references a theme color with an explicit RGB value**.
- You cannot build a master from scratch. A base presentation is always required.

---

## 2. The SLIDE_NUMBER placeholder cannot be generated

Even when `{"layoutPlaceholder": {"type": "SLIDE_NUMBER", "index": 0}}` is passed to
`createSlide`'s `placeholderIdMappings`, it is **silently ignored without an error**. Fetching
the generated slide shows no pageElement of type SLIDE_NUMBER.

```
createSlide with SLIDE_NUMBER mapping: OK       ← returned as success
 element SLIDES_API…_0 {'type': 'TITLE',  …}    ← only TITLE and BODY
 element SLIDES_API…_1 {'type': 'BODY',   …}
```

Page number display is a Google Slides UI-side setting (Insert → Slide numbers); there is no
API equivalent.

**Workaround**: draw a text box yourself at the layout's `slideNumber` coordinates
(`add_page_numbers()`). The original placeholder frame is often only a few mm wide, so a
2-digit page number gets clipped. Keep the right edge fixed, widen the box to at least 0.5in,
then right-align it.

---

## 3. The colorScheme JSON structure differs from everywhere else

Normal color specifications look like `{"opaqueColor": {"rgbColor": {"red": …}}}`, but only
the master's colorScheme has no `rgbColor` level — RGB sits directly under `color`.

```jsonc
// Master colorScheme
{"type": "ACCENT5", "color": {"red": 0.149, "green": 0.451, "blue": 0.733}}

// Shape fill
{"solidFill": {"color": {"rgbColor": {"red": 0.149, …}}, "alpha": 1}}
```

Writing a parser that expects `color.rgbColor` will end up reading every color as black
(#000000).

---

## 3b. `propertyState: NOT_RENDERED` means "the color is present but not drawn"

Fills and borders can hold a color value while remaining hidden.

```jsonc
"shapeBackgroundFill": {
  "propertyState": "NOT_RENDERED",          // ← transparent. The color below is unused
  "solidFill": {"color": {"themeColor": "LIGHT2"}, "alpha": 1}
}
```

If you read only the `solidFill` color without checking `propertyState`, you will
**mistake a transparent shape for one "filled with LIGHT2."** Setting a color via
`updateShapeProperties` on it effectively flips `propertyState` to RENDERED, making the
shape opaque. Doing this on a full-page-size rectangle covers up and hides the master's
logo/footer.

Templates in practice do contain "full-page transparent rectangles carrying only a color,
placed for future background swaps." When creating a derivative master, always check
`propertyState` before overwriting a color.

Possible values are `RENDERED` / `NOT_RENDERED` / `INHERIT`. If the key itself is absent, the
element is rendered.

## 4. Channels with a value of 0 are omitted entirely

`{"red": 1, "blue": 1}` means "green is 0" (magenta). `{"blue": 1}` is pure blue. Reading
with `c["green"]` raises a KeyError, so always use `c.get("green", 0)`.

Black `#000000` is represented as the empty object `{"rgbColor": {}}`.

---

## 5. Coordinates must be multiplied by the transform's scale

`size` is the element's raw dimensions; the actual displayed size is that value multiplied by
`transform.scaleX` / `scaleY`. Position is `transform.translateX` / `translateY`. The unit is
EMU (1 inch = 914400 EMU).

```python
w = size.width.magnitude * transform.scaleX / 914400   # inches
x = transform.translateX / 914400
```

Ignoring scale leads to misreading the dimensions of a scaled shape.

---

## 6. The speaker notes objectId is only known after the slide is created

The notes frame's `speakerNotesObjectId` is not included in `createSlide`'s response, nor can
it be referenced within a `batchUpdate` request.

**Workaround**: run the `batchUpdate` that creates the slide → call `presentations().get()`
to fetch `slides.slideProperties.notesPage.notesProperties.speakerNotesObjectId` → call
`insertText` in a second `batchUpdate`.

---

## 7. pageSize can only be set at creation time

It can only be set in the body of `presentations().create()`. There is no way to change it
after creation.

Since the duplication approach carries over the template's page size as-is, this constraint
is not an issue. Conversely, if you want a page size different from the template's, you
cannot use the duplication approach.

---

## 8. Batch batchUpdate calls into as few requests as possible

**The more you split it, the slower it gets.** Hands-on measurements with the request count
held constant (8,000 requests, a fresh presentation each time):

| Split | # of batches | Time | Per request |
|---|---|---|---|
| 500 at a time | 16 | 18.2s | 2.28 ms |
| 2,000 at a time | 4 | 12.2s | 1.52 ms |
| No split | 1 | **6.3s** | 0.79 ms |

Since the fixed cost per batch is only 0.1–0.25 seconds, this gap looks less like round-trip
overhead and more like the server re-finalizing a revision per batch.

**Do not parallelize.** Concurrent batchUpdate calls against the same presentation contend
with each other and end up slower (4-way parallel at 2,000 requests each: 20.1s vs. 12.2s
sequential).

The ceiling is the 10MB request body limit shared across Google APIs. A shape request
measures roughly 288 bytes, so nearly 30,000 fit (30,305 requests / 7.5MB sent as a single
batch succeeded in 20.0s). `build_deck._batches()` cuts at 10,000 requests / 5MB with a
safety margin.

Requests are applied **in the order sent**, so an ordering like "create the shape → insert
text → apply style" is preserved even when split across batches.

### Don't send values that match the default

Since duration is roughly proportional to request count, cutting requests you don't need to
send is a direct speedup. Measured defaults immediately after `createShape`:

| shapeType | Fill/border | contentAlignment | Paragraph alignment |
|---|---|---|---|
| `TEXT_BOX` | Both `NOT_RENDERED` | `TOP` | `START` |
| Everything else | Theme-derived (not `NOT_RENDERED`) | `MIDDLE` | `CENTER` |

`diagrams.Canvas.shape()` skips `updateShapeProperties` / `updateParagraphStyle` calls that
would just set these same values. This cuts roughly 19% off request count in a real deck.

---

## 9. Thumbnail fetching also works on layouts/masters

The `pageObjectId` for `presentations.pages.getThumbnail` accepts not just slide IDs but
also layout and master objectIds. Useful for visually checking a template's layouts.

Sizes are `SMALL` / `MEDIUM` (~800px wide) / `LARGE` (~1600px wide). Use LARGE and crop when
checking fine detail (e.g., a 7pt page number).

`contentUrl` expires quickly, so download immediately after fetching it.

### Quota is 60 requests per minute

getThumbnail is classified as an **expensive read** in the Slides API and carries a fixed
quota of `ExpensiveReadRequestsPerMinutePerUser = 60`. Exceeding it returns HTTP 429
`RATE_LIMIT_EXCEEDED`.

Each thumbnail takes about 2 round trips (API + download) and roughly 1.0 second, so
sequential execution is effectively already rate-limited right at this quota. If
parallelizing, **throttle to 60 requests per minute yourself**
(`fetch_thumbnails.py` uses a 55-per-minute token bucket plus exponential backoff on 429).
Firing requests in parallel without throttling always fails partway through for decks over
60 slides.

---

## 10. Duplication requires copy permission

`drive.files().copy()` returns 403 for files where the sharing setting "Disable download,
print, and copy for viewers and commenters" is enabled. Either ask the template owner to
disable that setting, or keep a copy of the template in your own Drive.

Note that `files.copy` on templates with many slides (dozens) **does in practice sometimes
return a temporary 500 Internal Error or a read timeout**. Retrying gets it through
(`build_deck.py`'s `_retry()` catches 5xx / 429 with exponential backoff).

- **When a 500 is returned**, the file was not created (confirmed by testing)
- **When the client times out**, the copy may have actually completed server-side, leaving
  an **orphaned file in Drive** (confirmed by testing). When you retry after a timeout, check
  whether two files with the same name now exist and clean up.

---

## 11. `createImage` ignores the specified size and preserves aspect ratio

Even when frame dimensions are passed via `elementProperties.size`, **the image is placed
scaled down to fit the frame while keeping its original aspect ratio** (i.e., it is always
"contain"). Filling the frame exactly cannot be achieved at creation time.

Measured example (a 1200×675 image inserted into a 4.30×2.90in frame):

```
Requested: w=4.30 h=2.90         → Result: w=4.30 h=2.42  (ratio 1.778 = original image)
```

Furthermore, `size.magnitude` is replaced not with the value you passed but with a value
derived from the image, and the shrinking is expressed in `transform.scaleX/scaleY`. So
achieving "exactly fills the frame" requires 3 steps.

1. Insert with `createImage`
2. Read the **generated element's `size.magnitude`** via `presentations().get()`
3. Re-set `scale = frame dimensions / magnitude` via `updatePageElementTransform`
   (`applyMode: "ABSOLUTE"`)

`build_deck.py`'s `_post_pass()` does this (piggybacking on the same second `batchUpdate`
that writes the speaker notes).

`cropProperties` **only crops the source image and does not affect the element's dimensions.**
If the cropped result's aspect ratio doesn't match the element's aspect ratio, the content
gets stretched. Correctly doing "crop the overflow to fill the frame" requires both crop and
the transform override above.

## 11b. `createImage`'s URL is fetched anonymously

Slides fetches the `url` itself. **Being accessible to you, authenticated, is not enough —
anyone with the link needs to be able to view it.** When using a Drive file, first attach
`permissions().create({"type": "anyone", "role": "reader"})`.

Since the image is **copied into the presentation** at insert time, deleting the source file
or revoking its public access after `batchUpdate` succeeds does not break the display. It is
safe to clean up temporary files right there (`images.AssetStore.cleanup()`).

Accepted formats are PNG / JPEG / GIF only, under 50MB and under 25 megapixels.

## 12. Rotating a shape also rotates the text inside it

`AffineTransform` has no rotation-angle field; rotation is expressed via
`scaleX / scaleY / shearX / shearY`.

```
x' = scaleX·x + shearX·y + translateX      For rotation by θ:
y' = shearY·x + scaleY·y + translateY        scaleX = scaleY = cosθ
                                             shearX = -sinθ, shearY = sinθ
```

To rotate around the center, set translate to
`cx - (cosθ·w/2 - sinθ·h/2)`, `cy - (sinθ·w/2 + cosθ·h/2)`.

**There is no way to rotate only the text.** When rotating a trapezoid (`TRAPEZOID` defaults
to a narrow top edge) by 180 degrees to use it as a "trapezoid with a wide top edge," the
text inserted via `insertText` also comes out upside down. Keep the shape and the text as
separate elements. `diagrams.Canvas.shape()` warns when text is placed inside a rotation
other than 0/90/270 degrees.

## 13. Fill alpha can be specified

`solidFill`'s `alpha` works over 0–1 (e.g., overlapping Venn diagram circles). However, if
`fields` specifies only `shapeBackgroundFill.solidFill.color`, alpha is not applied — you
must specify `shapeBackgroundFill.solidFill` instead.

## 14. Text frames have default inner padding

When estimating text wrapping, don't use the frame width as-is. Slides text frames have a
default **inner padding of 0.1in left/right and 0.05in top/bottom**, so the width available
for characters is narrower by that amount.

```
Characters per line = (frame width[in] − 0.1×2) × 72 ÷ font size[pt]
```

Calculating without subtracting the padding overestimates capacity by 1–2 characters, causing
strings that actually wrap to be misjudged as "fits on one line" (measured example: 10
full-width characters in a 1.62in / 11pt frame wrap, but the formula without padding
subtracted yields "10.6 characters fit").

On the other hand, **do not subtract padding for the vertical direction.** Slides draws text
that overflows the frame vertically without clipping it, so subtracting the top/bottom
padding too causes single-line labels to be misdetected across the board (measured example: a
single 9.5pt line in a 0.24in frame displays fine).

## 15. `TRAPEZOID`'s slope cannot be changed

The top-edge inset is fixed at **displayed height × 0.25** (on each side). Measured:

| Raw box | scaleY | Displayed height | Top edge | Bottom edge |
|---|---|---|---|---|
| 4.0 × 1.4in | 1.0 | 1.40in | 3.30in | 4.00in |
| 4.0 × 2.8in | 0.5 | 1.40in | 3.30in | 4.00in |

Both have a total inset of 0.70in = 0.25 × 1.40 × 2. **The ratio does not change whether you
change the width or squash it via scaleY** (the second row was an experiment aimed at testing
"if it's computed from the raw height, it should be 1.40in" — it was not). The API has no way
to pass a shape adjustment value (OOXML's `adj`).

**Consequence**: for diagrams like pyramids or funnels where you want to set the top and
bottom edges yourself, `TRAPEZOID` cannot be used. Even when each tier has the same height, a
different width changes the slope, so stacking them produces a jagged outline.

**Workaround**: draw with 3 parts — "a center rectangle + right triangles on each side"
(`illustrations.IllustrationMixin._taper()`). `RIGHT_TRIANGLE` defaults to having its right
angle at the **bottom-left**, and negating `scaleX` / `scaleY` mirrors it to produce any of
the 4 corner orientations.

```
default         flip_x          flip_y          flip_x+flip_y
■               　■             ■■              ■■
■■              ■■             ■               　■
```

Measured orientation: the default has "the vertical edge on the left, the hypotenuse running
from top-left to bottom-right."

Note that `TRAPEZOID`'s default orientation has **a narrow top edge and a wide bottom edge**.
Rotating 180 degrees reverses this, but the text inside also flips upside down together with
it (section 12).
