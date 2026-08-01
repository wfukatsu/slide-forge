#!/usr/bin/env python3
"""Scalar アイコンライブラリ（`assets/icons/`）。

62 種類の 24px グリッドのピクトグラム。原典は Scalar のブランド素材で、SVG が
正本、PNG はラスタライザが無い環境向けの控え。**単色（#C7C9C9）で描かれている
ので、テンプレートの配色に染めて使う。**

`illustrations` のピクトグラムとの使い分け:

| | `illustrations.icon()` | 本モジュール `asset_icon()` |
|---|---|---|
| 何で描くか | Slides の図形 | ブランド素材の SVG を PNG にして貼る |
| 語彙 | 30 種の汎用（person / server / db …） | 62 種の業務語彙（情報銀行・証拠チェーン…） |
| 通信 | 不要 | 要る（Drive 経由で挿入するため） |
| 見た目 | 素朴 | ブランド準拠 |

    from diagrams import Canvas
    d = Canvas(deck, slide_id, template)
    d.asset_icon("evidence-chain", 0.8, 1.4, 1.0, label="証拠チェーン")
    d.asset_icon_flow(0.7, 2.6, 8.6, [("job-seeker", "求職者"),
                                      ("screening", "書類選考"),
                                      ("interview", "面接"),
                                      ("job-offer", "内定")])

名前は slug（`evidence-chain`）でも日本語名（`証拠チェーン`）でも引ける。
一覧と検索:

    python scripts/icons.py --list
    python scripts/icons.py --search 鍵
    python scripts/icons.py --render 証拠チェーン --color '#2673BB' --out /tmp/x.png

ラスタライズは cairosvg → rsvg-convert → ImageMagick の順に試す
（`requirements.txt` の cairosvg が入っていれば最初で決まる）。どれも無い場合は
同梱の PNG をそのまま使うため、**色の指定は無視される**。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICON_DIR = os.path.join(SKILL_DIR, "assets", "icons")
SVG_DIR = os.path.join(ICON_DIR, "svg")
PNG_DIR = os.path.join(ICON_DIR, "png")
MANIFEST = os.path.join(ICON_DIR, "icons.json")
DEFAULT_CACHE = os.path.join(SKILL_DIR, "cache", "icons")
DEFAULT_PX = 512

_MANIFEST: dict | None = None
_HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


# ---------- マニフェスト ----------

def manifest() -> dict:
    """`assets/icons/icons.json` を読む（プロセス内で 1 回だけ）。"""
    global _MANIFEST
    if _MANIFEST is None:
        if not os.path.exists(MANIFEST):
            raise FileNotFoundError(
                f"アイコンのマニフェストがありません: {MANIFEST}\n"
                "  assets/icons/ が壊れています。スキルを再取得してください。")
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
    """slug / 日本語名 / 英語名 / タグ から slug を返す。曖昧なら候補を挙げて落とす。"""
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
            f"アイコン名 '{name}' が複数に当たります: {sorted(hits)}\n"
            "  slug で指定してください（python scripts/icons.py --search で一覧）")
    near = search(name)[:6]
    raise ValueError(
        f"未知のアイコン '{name}'。"
        + (f"もしかして: {near}" if near else
           "python scripts/icons.py --list で一覧を出せます"))


def search(query: str) -> list[str]:
    """部分一致で slug のリストを返す（日本語名・英語名・タグを見る）。"""
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
        line += f"  ※ 素材の絵が {m['sameArtAs']} と同一"
    return line


# ---------- ラスタライズ ----------

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
    cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=out,
                     output_width=px, output_height=px)
    return True


def _try_cli(svg: str, out: str, px: int) -> bool:
    """rsvg-convert / ImageMagick に投げる。SVG は一時ファイルに落とす。"""
    tmp = None
    try:
        fd, tmp = tempfile.mkstemp(suffix=".svg")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(svg)
        # 出力形式は拡張子ではなく明示で指定する。書き出し先が一時ファイル名
        # （.part）なので、任せると入力の SVG のまま書き出してしまう
        if shutil.which("rsvg-convert"):
            cmd = ["rsvg-convert", "-f", "png", "-w", str(px), "-h", str(px),
                   "-o", out, tmp]
        elif shutil.which("magick"):
            # 内蔵レンダラは 24px のまま描いて拡大するので density で先に大きく描かせる
            cmd = ["magick", "-background", "none", "-density", str(px * 3),
                   tmp, "-resize", f"{px}x{px}", f"PNG:{out}"]
        else:
            return False
        r = subprocess.run(cmd, capture_output=True)
        if r.returncode != 0 or not os.path.exists(out):
            return False
        with open(out, "rb") as f:
            return f.read(8) == b"\x89PNG\r\n\x1a\n"  # 本当に PNG になったか見る
    finally:
        if tmp and os.path.exists(tmp):
            os.unlink(tmp)


def render(name: str, *, color: str | None = None, px: int = DEFAULT_PX,
           cache_dir: str | None = None, force: bool = False) -> str:
    """アイコンを PNG にしてパスを返す。同じ (アイコン, 色, 画素数) ならキャッシュを使う。

    `color` は #RRGGBB。省略すると素材そのままの色（薄いグレー）になる。
    ロゴのように単色でないアイコンは `color` を無視する（マニフェストの
    `recolorable: false`）。
    """
    slug = resolve(name)
    meta = icons()[slug]
    if color:
        if not _HEX_RE.match(color):
            raise ValueError(f"color は #RRGGBB 形式で指定してください: {color}")
        color = color.upper()
        if not meta.get("recolorable", True):
            # ブランド色を持つアイコン（ロゴ）は染めない。勝手に色が変わる方が事故
            print(f"  note: '{slug}' はブランド色で固定のため color={color} は無視します",
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
                    f"SVG をラスタライズできず、同梱 PNG もありません: {slug}\n"
                    "  pip install cairosvg（または brew install librsvg）を実行してください")
            if color:
                print(f"  warn: ラスタライザが無いため '{slug}' を素材の色のまま使います"
                      f"（色 {color} は無視）。pip install cairosvg で解決します",
                      file=sys.stderr)
            shutil.copyfile(fallback, path)
            return path
        os.replace(tmp_out, path)
    finally:
        if os.path.exists(tmp_out):
            os.unlink(tmp_out)
    return path


def cache_key(name: str, color: str | None, px: int) -> str:
    return hashlib.sha256(f"{resolve(name)}|{color}|{px}".encode()).hexdigest()[:12]


# ---------- Canvas に生やすメソッド ----------

class IconLibraryMixin:
    """`Canvas` にブランドアイコンの配置を足すミックスイン。

    座標の規約は `illustrations` のピクトグラムと同じ。size×size の正方形に描き、
    **戻り値は（キャプションを含めた）描画領域の下端 y**。
    """

    def _icon_png(self, name: str, color: str | None, px: int | None) -> str:
        return render(name, color=color, px=px or DEFAULT_PX)

    def asset_icon(self, name: str, x: float, y: float, size: float = 0.8, *,
                   color: str | None = None, label: str | None = None,
                   label_size: float = 9, label_w: float | None = None,
                   label_gap: float = 0.05, bold_label: bool = False,
                   px: int | None = None, alt: str | None = None) -> float:
        """ブランドアイコンを size×size の正方形に貼る。戻り値は下端 y。

        `name` は slug でも日本語名でもよい（`"evidence-chain"` / `"証拠チェーン"`）。
        色を省略するとテンプレートの主色に染める。
        """
        slug = resolve(name)
        meta = icons()[slug]
        c = color or self.P.primary

        if getattr(self.deck, "dry", False):
            # --dry-run: 画像は取りに行けないので、同じ大きさの矩形で座標だけ確かめる
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
        """横一列に等間隔で並べる。items は名前か (名前, ラベル)。"""
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
        """矢印でつないだ流れ図。矢印は絵と絵の隙間にだけ引く。"""
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
        """格子状に並べる。items は名前か (名前, ラベル)。"""
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
        """アイコン付きのカードを並べる。items は (アイコン名, 見出し, 補足)。

        `cards()` の見出しにアイコンを足したもの。1 行に cols 枚。
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
                # 下の余白は 0.16in。これ以上詰めると 2 行の本文が枠に入らなくなる
                self.label(cx + 0.22, ty + icon_size + 0.12, cw - 0.44,
                           ch - icon_size - 0.50, body, size=body_size,
                           align="START", valign="TOP", color=self.P.muted,
                           line_spacing=115)
        return y + h


# ---------- CLI ----------

def _contact_sheet(out: str, color: str | None, px: int) -> int:
    """全アイコンを 1 枚の PNG に並べる（見比べ用）。cairosvg が要る。"""
    try:
        import cairosvg  # noqa: F401
    except Exception:
        print("一覧画像の生成には cairosvg が必要です（pip install cairosvg）",
              file=sys.stderr)
        return 1
    if not shutil.which("magick"):
        print("一覧画像の合成には ImageMagick が必要です（brew install imagemagick）",
              file=sys.stderr)
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
    p = argparse.ArgumentParser(description="Scalar アイコンライブラリを引く / 書き出す")
    p.add_argument("--list", action="store_true", help="全アイコンを一覧する")
    p.add_argument("--search", help="日本語名・英語名・タグの部分一致で探す")
    p.add_argument("--render", help="1 個を PNG に書き出す（slug でも日本語名でも可）")
    p.add_argument("--sheet", action="store_true",
                   help="全アイコンを 1 枚に並べた PNG を作る（--out が要る）")
    p.add_argument("--color", help="染める色 #RRGGBB（省略で素材のグレー）")
    p.add_argument("--px", type=int, default=DEFAULT_PX, help=f"書き出す画素数（既定 {DEFAULT_PX}）")
    p.add_argument("--out", help="書き出し先のパス")
    p.add_argument("--force", action="store_true", help="キャッシュを無視して作り直す")
    args = p.parse_args()

    if args.sheet:
        if not args.out:
            print("--sheet には --out が要ります", file=sys.stderr)
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
        print(f"該当なし: {args.search}", file=sys.stderr)
        return 1
    for s in slugs:
        print(describe(s))
    print(f"\n{len(slugs)} / {len(icons())} 件", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
