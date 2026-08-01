#!/usr/bin/env python3
"""Scalar アイコンライブラリ（`assets/shared/icons/`）。

62 種類の 24px グリッドのピクトグラム。原典は Scalar のブランド素材で、SVG が
正本、PNG はラスタライザが無い環境向けの控え。**単色（#C7C9C9）で描かれている
ので、テーマの配色に染めて使う。**

`references/pictogram-catalog.md` のピクトグラムとの使い分け:

| | シェイプで組むピクトグラム | 本モジュール `add_icon()` |
|---|---|---|
| 何で描くか | Slides のシェイプ（141 種）を組み合わせる | ブランド素材の SVG を PNG にして貼る |
| 語彙 | 汎用（cloud / shield / server …） | 62 種の業務語彙（情報銀行・証拠チェーン…） |
| 通信 | 不要（batchUpdate だけで完結） | 要る（Drive へ一時アップロードするため） |
| 見た目 | 素朴。3 シェイプ以上は破綻しやすい | ブランド準拠 |

SlideBuilder に混ぜて使う（`references/icon-library.md` に詳細）:

    import sys; sys.path.insert(0, "<skill>/scripts")
    from icons import IconLibraryMixin

    class SlideBuilder(IconLibraryMixin):
        ...
    sb.icon_color = C.primary          # 既定色（省略時は素材のグレー）
    sb.add_icon(sid, "evidence-chain", 0.8, 1.4, 1.0, label="証拠チェーン")
    sb.add_icon_flow(sid, 0.7, 2.6, 8.6, [("job-seeker", "求職者"),
                                          ("interview", "面接")])

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
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICON_DIR = os.path.join(SKILL_DIR, "assets", "shared", "icons")
SVG_DIR = os.path.join(ICON_DIR, "svg")
PNG_DIR = os.path.join(ICON_DIR, "png")
MANIFEST = os.path.join(ICON_DIR, "icons.json")
DEFAULT_CACHE = os.path.join(SKILL_DIR, "cache", "icons")
DEFAULT_PX = 512

_MANIFEST: dict | None = None
_HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


# ---------- マニフェスト ----------

def manifest() -> dict:
    """`assets/shared/icons/icons.json` を読む（プロセス内で 1 回だけ）。"""
    global _MANIFEST
    if _MANIFEST is None:
        if not os.path.exists(MANIFEST):
            raise FileNotFoundError(
                f"アイコンのマニフェストがありません: {MANIFEST}\n"
                "  assets/shared/icons/ が壊れています。スキルを再取得してください。")
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


# ---------- SlideBuilder に混ぜるミックスイン ----------

class IconLibraryMixin:
    """`SlideBuilder` にブランドアイコンの配置を足すミックスイン。

    必要なもの:

    - `self.add_image(slide_id, url, x, y, w, h)` … 本スキルの標準メソッド
    - `self.add_text(slide_id, text, x, y, w, h, *, font_size, color, alignment)`
    - `self.drive_service` … Drive へ一時アップロードするため
    - `self._uploaded_assets` … 後始末の対象。無ければ自動で作る

    矢印付きの `add_icon_flow` は `add_arrow`、カードの `add_icon_cards` は
    `add_rounded_rect`（無ければ `add_rect`）を使う。どれも本スキルの
    `references/google-slides-api.md` にある標準メソッド。

    座標はインチ、原点はスライド左上。**戻り値はキャプションを含めた下端 y**
    なので、次のブロックはその値を起点に置く。
    """

    #: 既定のアイコン色。テーマの主色を入れておく（例: sb.icon_color = C.primary）
    icon_color = None
    #: キャプションの既定色
    icon_label_color = None

    # -- 色 --
    # 本スキルの add_* は色を {"red":…,"green":…,"blue":…} で受け取るが、SVG を
    # 染めるには "#RRGGBB" が要る。どちらで渡されても動くよう両方向に変換する。

    @staticmethod
    def _icon_hex(c):
        if c is None or isinstance(c, str):
            return c
        return "#%02X%02X%02X" % tuple(
            round(c.get(k, 0) * 255) for k in ("red", "green", "blue"))

    @staticmethod
    def _icon_rgb(c):
        if c is None or isinstance(c, dict):
            return c
        h = c.lstrip("#")
        return {"red": int(h[0:2], 16) / 255,
                "green": int(h[2:4], 16) / 255,
                "blue": int(h[4:6], 16) / 255}

    # -- 内部 --

    def _icon_upload(self, path: str) -> str:
        """アイコン PNG を Drive に上げて公開 URL を返す。同じパスは 1 回だけ上げる。"""
        cache = getattr(self, "_icon_urls", None)
        if cache is None:
            cache = self._icon_urls = {}
        if path in cache:
            return cache[path]

        drive = getattr(self, "drive_service", None)
        if drive is None:
            raise RuntimeError(
                "SlideBuilder に drive_service がありません。"
                "build('drive', 'v3', credentials=creds) を self.drive_service に入れてください")
        from googleapiclient.http import MediaFileUpload
        media = MediaFileUpload(path, mimetype="image/png", resumable=False)
        fid = drive.files().create(
            body={"name": f"gslides-icon-{os.path.basename(path)}"},
            media_body=media, fields="id").execute()["id"]
        # createImage は URL を匿名で取りに行くため、公開共有が要る
        drive.permissions().create(
            fileId=fid, body={"type": "anyone", "role": "reader"}, fields="id"
        ).execute()
        if not hasattr(self, "_uploaded_assets"):
            self._uploaded_assets = []
        self._uploaded_assets.append(fid)

        url = f"https://drive.google.com/uc?export=download&id={fid}"
        cache[path] = url
        return url

    def _icon_label(self, slide_id, x, y, w, h, text, size, color):
        return self.add_text(slide_id, text, x, y, w, h, font_size=size,
                             color=self._icon_rgb(color or self.icon_label_color),
                             alignment="CENTER", valign="TOP")

    # -- 配置 --

    def add_icon(self, slide_id, name, x, y, size=0.8, *, color=None,
                 label=None, label_size=9, label_w=None, label_gap=0.05,
                 label_color=None, px=None) -> float:
        """ブランドアイコンを size×size の正方形に貼る。戻り値は下端 y。

        `name` は slug でも日本語名でもよい（`"evidence-chain"` / `"証拠チェーン"`）。
        色を省略すると `self.icon_color`（未設定なら素材のグレー）。
        """
        path = render(name, color=self._icon_hex(color or self.icon_color),
                      px=px or DEFAULT_PX)
        self.add_image(slide_id, self._icon_upload(path), x, y, size, size)

        bottom = y + size
        if label:
            lw = label_w or size * 2
            lines = label.count("\n") + 1
            lh = max(0.24, lines * label_size * 1.45 / 72 + 0.06)
            self._icon_label(slide_id, x + size / 2 - lw / 2, bottom + label_gap,
                             lw, lh, label, label_size, label_color)
            bottom += label_gap + lh
        return bottom

    def add_icon_row(self, slide_id, x, y, w, items, *, size=0.82, color=None,
                     label_size=9.5, gap=None, label_color=None, px=None) -> float:
        """横一列に等間隔で並べる。items は名前か (名前, ラベル)。"""
        n = len(items)
        cell = w / n
        bottom = y
        for i, item in enumerate(items):
            name, label = item if isinstance(item, (tuple, list)) else (item, None)
            c = color[i] if isinstance(color, (list, tuple)) else color
            cx = x + i * cell + cell / 2
            bottom = max(bottom, self.add_icon(
                slide_id, name, cx - size / 2, y, size, color=c, label=label,
                label_size=label_size, label_w=cell - (gap if gap else 0.16),
                label_color=label_color, px=px))
        return bottom

    def add_icon_flow(self, slide_id, x, y, w, items, *, size=0.82, color=None,
                      label_size=9.5, arrow_color=None, label_color=None,
                      px=None) -> float:
        """矢印でつないだ流れ図。矢印は絵と絵の隙間にだけ引く。"""
        n = len(items)
        cell = w / n
        bottom = y
        arrow = getattr(self, "add_arrow", None)
        for i, item in enumerate(items):
            name, label = item if isinstance(item, (tuple, list)) else (item, None)
            c = color[i] if isinstance(color, (list, tuple)) else color
            cx = x + i * cell + cell / 2
            bottom = max(bottom, self.add_icon(
                slide_id, name, cx - size / 2, y, size, color=c, label=label,
                label_size=label_size, label_w=cell - 0.5,
                label_color=label_color, px=px))
            if i < n - 1:
                ax = cx + size / 2 + 0.10
                aw = (cx + cell - size / 2 - 0.10) - ax
                ah = min(0.22, size * 0.28)
                fill = self._icon_rgb(
                    arrow_color
                    or (color if isinstance(color, (str, dict)) else None)
                    or self.icon_color)
                if arrow:
                    arrow(slide_id, ax, y + size / 2 - ah / 2, aw, ah,
                          direction="right", fill=fill)
                else:  # add_arrow を持たない SlideBuilder では細い矩形で代用する
                    self.add_rect(slide_id, ax, y + size / 2 - 0.02, aw, 0.04,
                                  fill=fill)
        return bottom

    def add_icon_grid(self, slide_id, x, y, w, items, *, cols=4, size=0.72,
                      row_gap=0.30, color=None, label_size=9, label_color=None,
                      px=None) -> float:
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
            bottom = max(bottom if i % cols else row_top, self.add_icon(
                slide_id, name, cx - size / 2, row_top, size, color=c, label=label,
                label_size=label_size, label_w=cell - 0.14,
                label_color=label_color, px=px))
        return bottom

    def add_icon_cards(self, slide_id, x, y, w, h, items, *, cols=3, gap=0.24,
                       icon_size=0.62, color=None, title_size=11.5, body_size=9.5,
                       fill=None, border_color=None, title_color=None,
                       body_color=None, px=None) -> float:
        """アイコン付きのカードを並べる。items は (アイコン名, 見出し, 補足)。"""
        n = len(items)
        rows = (n + cols - 1) // cols
        cw = (w - gap * (cols - 1)) / cols
        ch = (h - gap * (rows - 1)) / rows
        card = getattr(self, "add_rounded_rect", None) or self.add_rect
        for i, item in enumerate(items):
            name, title, body = (list(item) + [None, None])[:3]
            cx = x + (i % cols) * (cw + gap)
            cy = y + (i // cols) * (ch + gap)
            c = color[i] if isinstance(color, (list, tuple)) else (color or self.icon_color)
            card(slide_id, cx, cy, cw, ch, fill=self._icon_rgb(fill),
                 border_color=self._icon_rgb(border_color))
            self.add_icon(slide_id, name, cx + 0.22, cy + 0.22, icon_size,
                          color=c, px=px)
            self.add_text(slide_id, title, cx + 0.22 + icon_size + 0.16, cy + 0.22,
                          cw - icon_size - 0.6, 0.34, font_size=title_size,
                          bold=True, color=self._icon_rgb(title_color),
                          alignment="START", valign="MIDDLE")
            if body:
                # 下の余白は 0.16in。これ以上詰めると 2 行の本文が枠に入らなくなる
                self.add_text(slide_id, body, cx + 0.22, cy + 0.22 + icon_size + 0.12,
                              cw - 0.44, ch - icon_size - 0.50, font_size=body_size,
                              color=self._icon_rgb(body_color), alignment="START",
                              valign="TOP")
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
