*[日本語](icons.ja.md)*
# Icon Library

`assets/scalar/pictograms/` contains **62** Scalar-branded pictograms. They are single-color
icons on a 24px grid; the SVG is the source of truth, and the PNG (512px) is a fallback for
environments without a rasterizer.

```
assets/scalar/pictograms/
  icons.json      name, Japanese name, English name, search tags, whether it can be recolored
  svg/<slug>.svg  source of truth
  png/<slug>.png  fallback (512px, kept in the material's original gray)
cache/icons/      recolored PNGs written out (<slug>-<color>-<px>.png)
```

## Choosing between this and `illustrations` pictograms

| | `illustrations.icon()` | `icons.asset_icon()` |
|---|---|---|
| How it's drawn | Combines Slides shapes | Renders the brand SVG asset to a PNG and pastes it |
| Vocabulary | 30 generic terms (person / server / database …) | 62 domain terms (data bank, evidence chain, job offer …) |
| Network access | Not required | **Required** (inserted via Drive) |
| Look | Plain. You control the line weight | On-brand |

**Use `asset_icon` for externally facing materials, or whenever the vocabulary matches.**
When you only need generic parts like "server" or "cloud", or you need everything to work
offline, stick with `illustrations.icon()`. The two can be mixed freely on the same slide.

## Finding a name

A name can be looked up by slug (`evidence-chain`), by its Japanese name (`証拠チェーン`), or by
its English name. Tags are matched too, so words like "key" or "sns" also resolve.

```bash
.venv/bin/python scripts/icons.py --list            # list all 62
.venv/bin/python scripts/icons.py --search 情報銀行  # partial match search
.venv/bin/python scripts/icons.py --search key
```

An ambiguous name (e.g. `鍵` → public / private / shared) errors out and lists the candidates.
A nonexistent name also fails with candidates attached, so **typos surface at the `--dry-run`
stage.**

To view the whole catalog as an image (requires cairosvg and ImageMagick):

```bash
.venv/bin/python scripts/icons.py --sheet --out out/icons.png --color '#2673BB'
```

## Using it

The coordinate convention is the same as `illustrations`: draws into a size×size square, and
**the return value is the bottom y including the caption**.

| What you want to do | Method |
|---|---|
| Place a single icon | `asset_icon(name, x, y, size, color=…, label=…)` |
| Line them up horizontally | `asset_icon_row(x, y, w, items)` |
| Connect with arrows into a flow | `asset_icon_flow(x, y, w, items)` |
| Arrange in a grid | `asset_icon_grid(x, y, w, items, cols=4)` |
| Turn into cards with icons | `asset_icon_cards(x, y, w, h, items, cols=3)` |

`items` is a name, or `(name, label)`. `asset_icon_cards` alone takes `(name, heading, note)`.

```python
d = Canvas(deck, ref["slideId"], template)
b = d.asset_icon_flow(0.5, 1.15, 9.0, [
    ("job-seeker", "求職者"), ("signup", "会員登録"),
    ("screening", "書類選考"), ("interview", "面接"), ("job-offer", "内定"),
], size=0.86)
d.asset_icon("evidence-chain", 0.8, b + 0.3, 1.0, color=d.P.info, label="証拠チェーン")
```

From a deck spec (JSON), use the `type` field under `figures`.

```json
{ "type": "asset_icon_flow", "x": 0.5, "y": 1.15, "w": 9.0, "size": 0.86,
  "items": [["personal-info", "個人情報"], ["consent", "同意"],
            ["data-bank", "情報銀行"]] }
```

Five types: `asset_icon` / `asset_icon_row` / `asset_icon_flow` / `asset_icon_grid` /
`asset_icon_cards`. A working example is `examples/icon-gallery.json`.

## Color

**The source material is a single light gray (#C7C9C9).** Pasted as-is it sinks into a white
background, so by default it's recolored to the template's primary color (`P.primary`). Pass a
different color via `color=` to give it a meaning, such as `P.success` / `P.danger`.

- To vary the color per element, pass a `color=[…]` list (`_row` / `_flow` / `_grid`).
- White areas are "cutouts" and are never recolored (e.g. the text inside `faq`).
- `scalar-logo` alone carries a brand color, so it **ignores `color`**
  (`recolorable: false` in `icons.json`). The single-color variant `scalar-logo-mono` does
  get recolored.

## What happens under the hood

1. Replace `#C7C9C9` in the SVG with the requested color
2. Rasterize to PNG (tries `cairosvg` → `rsvg-convert` → `ImageMagick`, in that order)
3. Leave it in `cache/icons/<slug>-<color>-<px>.png`. **The same icon in the same color is
   never rasterized twice**
4. Hand it to `images.ImageMixin.image()` (temporary upload to Drive → insertion →
   cleanup)

Thanks to the cache in step 3, and because `AssetStore` reuses URLs per source path, **the same
icon used across any number of slides is uploaded to Drive only once.**

In an environment with no rasterizer at all, the assets under `assets/scalar/pictograms/png/`
are used as-is, the color argument is ignored, and a warning is printed. Make sure `cairosvg`
from `requirements.txt` is installed.

## Known defects in the source material

At the source (Drive), the following two pairs turn out to be **the same SVG content**. Since
the preview images show different artwork (`private-key` has closed eyes), this looks like a
registration mistake in the material.

| slug | Shares artwork with |
|---|---|
| `private-key` | `public-key` |
| `new-workflow` | `terms` |

This is recorded in `sameArtAs` in `icons.json`, and `--list` flags it too. **In a diagram that
places the public key and private key side by side for comparison, the same artwork will appear
twice.** Distinguish them with color, mix in `illustrations.icon("key")`, or request that the
source material be replaced.

## Constraints

- **Network access is required.** Since Slides can only ingest images from a URL, it goes
  through Drive. If your organization's policy forbids "anyone with the link" sharing,
  insertion fails (fall back to `illustrations.icon()` in that case).
- `--dry-run` can't paste the real artwork, so it **substitutes a rectangle of the same
  size** and checks only the coordinates. This catches name typos, overflow, overlap, and
  caption spillover.
- Icons are square. `asset_icon`'s `size` is the side length in inches; 0.5–1.4in is the
  practical range.
- Caption width defaults to twice `size`. When packing icons tightly, set `label_w` explicitly
  (`_row` / `_flow` / `_grid` derive it automatically from the cell width).

## Adding new material

1. Place the SVG at `assets/scalar/pictograms/svg/<slug>.svg` (24×24 viewBox, single color
   #C7C9C9)
2. Add `ja` / `en` / `tags` / `recolorable` / `colors` to `assets/scalar/pictograms/icons.json`
3. Bake the fallback PNG:

```bash
.venv/bin/python -c "
import sys; sys.path.insert(0,'scripts'); import icons, cairosvg, os
s='<slug>'
cairosvg.svg2png(url=f'{icons.SVG_DIR}/{s}.svg', write_to=f'{icons.PNG_DIR}/{s}.png',
                 output_width=512, output_height=512)"
```

For material whose color is anything other than #C7C9C9, set `recolorable: false`. Recoloring
it would break the brand color.
