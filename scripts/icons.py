#!/usr/bin/env python3
"""Scalar icon library (`assets/scalar/pictograms/`).

62 pictograms on a 24px grid. Sourced from Scalar's brand assets; SVG is
the canonical form, PNG is a fallback for environments without a
rasterizer. **Drawn in a single color (#C7C9C9), meant to be tinted to
match the template's palette.**

How this compares to the pictograms in `illustrations`:

| | `illustrations.icon()` | this module's `asset_icon()` |
|---|---|---|
| How it's drawn | Slides shapes | Brand SVG assets converted to PNG and pasted in |
| Vocabulary | 30 generic terms (person / server / db …) | 62 business terms (information bank, evidence chain, …) |
| Network access | Not needed | Needed (inserted via Drive) |
| Look | Plain | On-brand |

    from diagrams import Canvas
    d = Canvas(deck, slide_id, template)
    d.asset_icon("evidence-chain", 0.8, 1.4, 1.0, label="証拠チェーン")
    d.asset_icon_flow(0.7, 2.6, 8.6, [("job-seeker", "求職者"),
                                      ("screening", "書類選考"),
                                      ("interview", "面接"),
                                      ("job-offer", "内定")])

Names can be looked up by slug (`evidence-chain`) or by Japanese name
(`証拠チェーン`). Listing and search:

    .venv/bin/python scripts/icons.py --list
    .venv/bin/python scripts/icons.py --search 鍵
    .venv/bin/python scripts/icons.py --render 証拠チェーン --color '#2673BB' --out /tmp/x.png

Rasterization is tried in this order: cairosvg → rsvg-convert →
ImageMagick (if cairosvg from `requirements.txt` is installed, it wins
first). If none are available, the bundled PNG is used as-is, so
**the color argument is ignored**.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _i18n import t, register  # noqa: E402

register({
    "Icon manifest not found: {path}\n"
    "  assets/scalar/pictograms/ is broken; re-fetch the repo.":
        "アイコンのマニフェストがありません: {path}\n"
        "  assets/scalar/pictograms/ is broken; re-fetch the repo.",
    "Icon name '{name}' matches multiple icons: {hits}\n"
    "  Specify a slug (.venv/bin/python scripts/icons.py --search lists candidates)":
        "アイコン名 '{name}' が複数に当たります: {hits}\n"
        "  slug で指定してください（.venv/bin/python scripts/icons.py --search で一覧）",
    "Unknown icon '{name}'. Did you mean: {near}":
        "未知のアイコン '{name}'。もしかして: {near}",
    "Unknown icon '{name}'. Run .venv/bin/python scripts/icons.py --list to see all icons":
        "未知のアイコン '{name}'。.venv/bin/python scripts/icons.py --list で一覧を出せます",
    "  * artwork identical to {slug}": "  ※ 素材の絵が {slug} と同一",
    "  warn: cairosvg conversion failed ({error}); trying rsvg-convert / magick":
        "  warn: cairosvg での変換に失敗しました（{error}）。"
        "rsvg-convert / magick を試します",
    "color must be in #RRGGBB format: {color}":
        "color は #RRGGBB 形式で指定してください: {color}",
    "  note: '{slug}' keeps its fixed brand colors; ignoring color={color}":
        "  note: '{slug}' はブランド色で固定のため color={color} は無視します",
    "Cannot rasterize the SVG and no bundled PNG exists: {slug}\n"
    "  Run pip install cairosvg (or brew install librsvg)":
        "SVG をラスタライズできず、同梱 PNG もありません: {slug}\n"
        "  pip install cairosvg（または brew install librsvg）を実行してください",
    "  warn: no rasterizer available; using '{slug}' in its source color"
    " (color {color} ignored). pip install cairosvg fixes this":
        "  warn: ラスタライザが無いため '{slug}' を素材の色のまま使います"
        "（色 {color} は無視）。pip install cairosvg で解決します",
    "Generating the contact sheet requires cairosvg (pip install cairosvg)":
        "一覧画像の生成には cairosvg が必要です（pip install cairosvg）",
    "Compositing the contact sheet requires ImageMagick (brew install imagemagick)":
        "一覧画像の合成には ImageMagick が必要です（brew install imagemagick）",
    "Look up / export the Scalar icon library":
        "Scalar アイコンライブラリを引く / 書き出す",
    "List all icons": "全アイコンを一覧する",
    "Search by partial match on Japanese name, English name, or tags":
        "日本語名・英語名・タグの部分一致で探す",
    "Export one icon to PNG (slug or Japanese name)":
        "1 個を PNG に書き出す（slug でも日本語名でも可）",
    "Build one PNG contact sheet of all icons (requires --out)":
        "全アイコンを 1 枚に並べた PNG を作る（--out が要る）",
    "Tint color #RRGGBB (defaults to the source gray)":
        "染める色 #RRGGBB（省略で素材のグレー）",
    "Output size in pixels (default {px})": "書き出す画素数（既定 {px}）",
    "Output file path": "書き出し先のパス",
    "Ignore the cache and rebuild": "キャッシュを無視して作り直す",
    "--sheet requires --out": "--sheet には --out が要ります",
    "No matches: {query}": "該当なし: {query}",
    "\n{shown} / {total} icons": "\n{shown} / {total} 件",
})

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Brand pictograms live under assets/scalar/ so the generic engine stays
# brand-neutral; point this at another directory to swap the icon set.
ICON_DIR = os.path.join(SKILL_DIR, "assets", "scalar", "pictograms")
SVG_DIR = os.path.join(ICON_DIR, "svg")
PNG_DIR = os.path.join(ICON_DIR, "png")
MANIFEST = os.path.join(ICON_DIR, "icons.json")
DEFAULT_CACHE = os.path.join(SKILL_DIR, "cache", "icons")
DEFAULT_PX = 512

_MANIFEST: dict | None = None
_HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


# ---------- Manifest ----------

def manifest() -> dict:
    """Reads `assets/scalar/pictograms/icons.json` (only once per process)."""
    global _MANIFEST
    if _MANIFEST is None:
        if not os.path.exists(MANIFEST):
            raise FileNotFoundError(
                t("Icon manifest not found: {path}\n"
                  "  assets/scalar/pictograms/ is broken; re-fetch the repo.",
                  path=MANIFEST))
        with open(MANIFEST, encoding="utf-8") as f:
            _MANIFEST = json.load(f)
    return _MANIFEST


def icons() -> dict[str, dict]:
    return manifest()["icons"]


def source_color() -> str:
    return manifest().get("sourceColor", "#C7C9C9")


def _norm(s: str) -> str:
    return str(s).strip().lower().replace("_", "-").replace(" ", "")


def resolve(name: str) -> str:
    """Resolves a slug from a slug / Japanese name / English name / tag.
    Raises with candidate suggestions listed if the match is ambiguous."""
    table = icons()
    if name in table:
        return name
    key = _norm(name)
    for slug, meta in table.items():
        if key in (_norm(slug), _norm(meta["ja"]), _norm(meta["en"])):
            return slug
    hits = [s for s, m in table.items()
            if key in _norm(m["ja"]) or key in _norm(m["en"]) or key in _norm(s)
            or any(key == _norm(t) for t in m["tags"])]
    if len(hits) == 1:
        return hits[0]
    if hits:
        raise ValueError(
            t("Icon name '{name}' matches multiple icons: {hits}\n"
              "  Specify a slug (.venv/bin/python scripts/icons.py --search lists candidates)",
              name=name, hits=sorted(hits)))
    near = search(name)[:6]
    if near:
        raise ValueError(t("Unknown icon '{name}'. Did you mean: {near}",
                           name=name, near=near))
    raise ValueError(
        t("Unknown icon '{name}'. Run .venv/bin/python scripts/icons.py --list to see all icons",
          name=name))


def search(query: str) -> list[str]:
    """Returns a list of slugs matched by partial match (checks Japanese name, English name, and tags)."""
    key = _norm(query)
    if not key:
        return sorted(icons())
    out = []
    for slug, meta in icons().items():
        hay = [slug, meta["ja"], meta["en"], *meta["tags"]]
        if any(key in _norm(h) for h in hay):
            out.append(slug)
    return out


def describe(slug: str) -> str:
    m = icons()[slug]
    line = f"{slug:26} {m['ja']:20} {m['en']}"
    if m.get("sameArtAs"):
        line += t("  * artwork identical to {slug}", slug=m["sameArtAs"])
    return line


# ---------- Rasterization ----------

class RasterizeError(RuntimeError):
    pass


def _recolored_svg(slug: str, color: str | None) -> str:
    with open(os.path.join(SVG_DIR, f"{slug}.svg"), encoding="utf-8") as f:
        body = f.read()
    if not color:
        return body
    src = source_color()
    return re.sub(re.escape(src), color, body, flags=re.IGNORECASE)


def _try_cairosvg(svg: str, out: str, px: int) -> bool:
    try:
        import cairosvg
    except Exception:
        return False
    try:
        cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=out,
                         output_width=px, output_height=px)
    except Exception as e:
        # Conversion failures (e.g. unsupported SVG features) also fall through to the CLI fallback
        print(t("  warn: cairosvg conversion failed ({error}); "
                "trying rsvg-convert / magick", error=e), file=sys.stderr)
        return False
    return True


def _try_cli(svg: str, out: str, px: int) -> bool:
    """Dispatches to rsvg-convert / ImageMagick. Writes the SVG to a temp file first."""
    tmp = None
    try:
        fd, tmp = tempfile.mkstemp(suffix=".svg")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(svg)
        # Specify the output format explicitly rather than relying on the
        # extension. Since the output path is a temp filename (.part),
        # leaving it to guesswork would just write out the input SVG unchanged
        if shutil.which("rsvg-convert"):
            cmd = ["rsvg-convert", "-f", "png", "-w", str(px), "-h", str(px),
                   "-o", out, tmp]
        elif shutil.which("magick"):
            # The built-in renderer draws at 24px and then scales up, so use
            # density to render large from the start
            cmd = ["magick", "-background", "none", "-density", str(px * 3),
                   tmp, "-resize", f"{px}x{px}", f"PNG:{out}"]
        else:
            return False
        r = subprocess.run(cmd, capture_output=True)
        if r.returncode != 0 or not os.path.exists(out):
            return False
        with open(out, "rb") as f:
            return f.read(8) == b"\x89PNG\r\n\x1a\n"  # check whether it actually became a PNG
    finally:
        if tmp and os.path.exists(tmp):
            os.unlink(tmp)


def render(name: str, *, color: str | None = None, px: int = DEFAULT_PX,
           cache_dir: str | None = None, force: bool = False) -> str:
    """Renders the icon to PNG and returns the path. Reuses the cache for the same (icon, color, pixel size).

    `color` is #RRGGBB. If omitted, the source color (light gray) is used
    as-is. Icons that aren't single-colored, like logos, ignore `color`
    (per the manifest's `recolorable: false`).
    """
    slug = resolve(name)
    meta = icons()[slug]
    if color:
        if not _HEX_RE.match(color):
            raise ValueError(t("color must be in #RRGGBB format: {color}", color=color))
        color = color.upper()
        if not meta.get("recolorable", True):
            # Icons with fixed brand colors (logos) aren't tinted. Changing
            # their color unexpectedly would be a mistake
            print(t("  note: '{slug}' keeps its fixed brand colors; "
                    "ignoring color={color}", slug=slug, color=color),
                  file=sys.stderr)
            color = None

    cache_dir = cache_dir or os.environ.get("GSLIDES_ICON_CACHE", DEFAULT_CACHE)
    os.makedirs(cache_dir, exist_ok=True)
    tag = (color or "src").lstrip("#")
    path = os.path.join(cache_dir, f"{slug}-{tag}-{px}.png")
    if os.path.exists(path) and not force:
        return path

    svg = _recolored_svg(slug, color)
    tmp_out = path + f".{os.getpid()}.part"
    try:
        if not (_try_cairosvg(svg, tmp_out, px) or _try_cli(svg, tmp_out, px)):
            fallback = os.path.join(PNG_DIR, f"{slug}.png")
            if not os.path.exists(fallback):
                raise RasterizeError(
                    t("Cannot rasterize the SVG and no bundled PNG exists: {slug}\n"
                      "  Run pip install cairosvg (or brew install librsvg)",
                      slug=slug))
            if color:
                print(t("  warn: no rasterizer available; using '{slug}' in its "
                        "source color (color {color} ignored). "
                        "pip install cairosvg fixes this", slug=slug, color=color),
                      file=sys.stderr)
            shutil.copyfile(fallback, path)
            return path
        os.replace(tmp_out, path)
    finally:
        if os.path.exists(tmp_out):
            os.unlink(tmp_out)
    return path


# ---------- Methods added to Canvas ----------

class IconLibraryMixin:
    """Mixin that adds brand-icon placement to `Canvas`.

    Coordinate conventions match the `illustrations` pictograms. Draws into
    a size×size square, and **returns the bottom y of the drawn area
    (including the caption)**.
    """

    def _icon_png(self, name: str, color: str | None, px: int | None) -> str:
        return render(name, color=color, px=px or DEFAULT_PX)

    def asset_icon(self, name: str, x: float, y: float, size: float = 0.8, *,
                   color: str | None = None, label: str | None = None,
                   label_size: float = 9, label_w: float | None = None,
                   label_gap: float = 0.05, bold_label: bool = False,
                   px: int | None = None, alt: str | None = None) -> float:
        """Places a brand icon into a size×size square. Returns the bottom y.

        `name` may be a slug or a Japanese name (`"evidence-chain"` /
        `"証拠チェーン"`). If color is omitted, it's tinted to the template's
        primary color.
        """
        slug = resolve(name)
        meta = icons()[slug]
        c = color or self.P.primary

        if getattr(self.deck, "dry", False):
            # --dry-run: images can't be fetched, so just verify coordinates
            # with a same-sized rectangle
            self.shape(x, y, size, size, kind="RECTANGLE", fill=c, stroke=None)
        else:
            self.image(x, y, size, size, self._icon_png(slug, c, px),
                       fit="contain", alt=alt or meta["ja"])

        bottom = y + size
        if label:
            lw = label_w or size * 2
            lines = label.count("\n") + 1
            lh = max(0.24, lines * label_size * 1.45 / 72 + 0.06)
            self.label(x + size / 2 - lw / 2, bottom + label_gap, lw, lh, label,
                       size=label_size, align="CENTER", valign="TOP",
                       color=self.P.text, bold=bold_label, line_spacing=110)
            bottom += label_gap + lh
        return bottom

    def asset_icon_row(self, x: float, y: float, w: float, items, *,
                       size: float = 0.82, color=None, label_size: float = 9.5,
                       gap: float | None = None, px: int | None = None) -> float:
        """Lays items out in an evenly spaced row. items is a name or a (name, label) tuple."""
        n = len(items)
        cell = w / n
        bottom = y
        for i, item in enumerate(items):
            name, label = item if isinstance(item, (tuple, list)) else (item, None)
            c = color[i] if isinstance(color, (list, tuple)) else color
            cx = x + i * cell + cell / 2
            bottom = max(bottom, self.asset_icon(
                name, cx - size / 2, y, size, color=c, label=label,
                label_size=label_size, label_w=cell - (gap if gap else 0.16), px=px))
        return bottom

    def asset_icon_flow(self, x: float, y: float, w: float, items, *,
                        size: float = 0.82, color=None, label_size: float = 9.5,
                        arrow_color=None, px: int | None = None) -> float:
        """Flow diagram connected with arrows. Arrows are only drawn in the gaps between icons."""
        n = len(items)
        cell = w / n
        bottom = y
        for i, item in enumerate(items):
            name, label = item if isinstance(item, (tuple, list)) else (item, None)
            c = color[i] if isinstance(color, (list, tuple)) else color
            cx = x + i * cell + cell / 2
            bottom = max(bottom, self.asset_icon(
                name, cx - size / 2, y, size, color=c, label=label,
                label_size=label_size, label_w=cell - 0.5, px=px))
            if i < n - 1:
                ay = y + size / 2
                self.arrow(cx + size / 2 + 0.10, ay, cx + cell - size / 2 - 0.10, ay,
                           color=arrow_color or self.P.primary, weight=1.5,
                           _anchored=True)
        return bottom

    def asset_icon_grid(self, x: float, y: float, w: float, items, *, cols: int = 4,
                        size: float = 0.72, row_gap: float = 0.30, color=None,
                        label_size: float = 9, px: int | None = None) -> float:
        """Lays items out in a grid. items is a name or a (name, label) tuple."""
        cell = w / cols
        bottom = y
        row_top = y
        for i, item in enumerate(items):
            if i and i % cols == 0:
                row_top = bottom + row_gap
            name, label = item if isinstance(item, (tuple, list)) else (item, None)
            c = color[i] if isinstance(color, (list, tuple)) else color
            cx = x + (i % cols) * cell + cell / 2
            bottom = max(bottom if i % cols else row_top, self.asset_icon(
                name, cx - size / 2, row_top, size, color=c, label=label,
                label_size=label_size, label_w=cell - 0.14, px=px))
        return bottom

    def asset_icon_cards(self, x: float, y: float, w: float, h: float, items, *,
                         cols: int = 3, gap: float = 0.24, icon_size: float = 0.62,
                         color=None, title_size: float = 11.5,
                         body_size: float = 9.5, fill=None, stroke=None,
                         px: int | None = None) -> float:
        """Lays out cards with icons. items is (icon name, title, body).

        Like `cards()`'s headings but with an icon added. cols cards per row.
        """
        from colors import lighten
        n = len(items)
        rows = (n + cols - 1) // cols
        cw = (w - gap * (cols - 1)) / cols
        ch = (h - gap * (rows - 1)) / rows
        for i, item in enumerate(items):
            name, title, body = (list(item) + [None, None])[:3]
            cx = x + (i % cols) * (cw + gap)
            cy = y + (i // cols) * (ch + gap)
            c = color[i] if isinstance(color, (list, tuple)) else (color or self.P.primary)
            self.shape(cx, cy, cw, ch, kind="ROUND_RECTANGLE",
                       fill=fill or self.P.surface,
                       stroke=stroke if stroke is not None else self.P.border)
            self.asset_icon(name, cx + 0.22, cy + 0.22, icon_size, color=c, px=px)
            ty = cy + 0.22
            self.label(cx + 0.22 + icon_size + 0.16, ty, cw - icon_size - 0.6,
                       0.34, title, size=title_size, bold=True, align="START",
                       valign="MIDDLE", color=self.P.text)
            if body:
                # Bottom margin is 0.16in. Any tighter and a 2-line body won't fit in the frame
                self.label(cx + 0.22, ty + icon_size + 0.12, cw - 0.44,
                           ch - icon_size - 0.50, body, size=body_size,
                           align="START", valign="TOP", color=self.P.muted,
                           line_spacing=115)
        return y + h


# ---------- CLI ----------

def _contact_sheet(out: str, color: str | None, px: int) -> int:
    """Lays out all icons on one PNG (for side-by-side comparison). Requires cairosvg."""
    try:
        import cairosvg  # noqa: F401
    except Exception:
        print(t("Generating the contact sheet requires cairosvg (pip install cairosvg)"),
              file=sys.stderr)
        return 1
    if not shutil.which("magick"):
        print(t("Compositing the contact sheet requires ImageMagick "
                "(brew install imagemagick)"), file=sys.stderr)
        return 1
    slugs = sorted(icons())
    tiles = [render(s, color=color, px=px) for s in slugs]
    cols = 8
    rows = [tiles[i:i + cols] for i in range(0, len(tiles), cols)]
    with tempfile.TemporaryDirectory() as td:
        strips = []
        for i, row in enumerate(rows):
            strip = os.path.join(td, f"r{i}.png")
            subprocess.run(["magick", *row, "+append", strip], check=True)
            strips.append(strip)
        subprocess.run(["magick", *strips, "-append", "-background", "white",
                        "-alpha", "remove", "-alpha", "off", out], check=True)
    print(f"{out}  ({len(slugs)} icons / {cols} cols)")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=t("Look up / export the Scalar icon library"))
    p.add_argument("--list", action="store_true", help=t("List all icons"))
    p.add_argument("--search",
                   help=t("Search by partial match on Japanese name, English name, or tags"))
    p.add_argument("--render", help=t("Export one icon to PNG (slug or Japanese name)"))
    p.add_argument("--sheet", action="store_true",
                   help=t("Build one PNG contact sheet of all icons (requires --out)"))
    p.add_argument("--color", help=t("Tint color #RRGGBB (defaults to the source gray)"))
    p.add_argument("--px", type=int, default=DEFAULT_PX,
                   help=t("Output size in pixels (default {px})", px=DEFAULT_PX))
    p.add_argument("--out", help=t("Output file path"))
    p.add_argument("--force", action="store_true", help=t("Ignore the cache and rebuild"))
    args = p.parse_args()

    if args.sheet:
        if not args.out:
            print(t("--sheet requires --out"), file=sys.stderr)
            return 1
        return _contact_sheet(args.out, args.color, min(args.px, 128))

    if args.render:
        try:
            path = render(args.render, color=args.color, px=args.px, force=args.force)
        except (ValueError, RasterizeError) as e:
            print(str(e), file=sys.stderr)
            return 1
        if args.out:
            os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
            shutil.copyfile(path, args.out)
            path = args.out
        print(path)
        return 0

    slugs = search(args.search) if args.search else sorted(icons())
    if not slugs:
        print(t("No matches: {query}", query=args.search), file=sys.stderr)
        return 1
    for s in slugs:
        print(describe(s))
    print(t("\n{shown} / {total} icons", shown=len(slugs), total=len(icons())),
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
