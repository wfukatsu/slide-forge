#!/usr/bin/env python3
"""クラウドベンダー（AWS / Google Cloud / Azure）の公式アイコンを引く。

素材は `assets/shared/cloud-icons/`（`fetch-cloud-icons.py` が取り込む）。
1,700 種以上あるので、**名前で引けること**がこのモジュールの主目的。

    python scripts/cloud_icons.py --search s3
    python scripts/cloud_icons.py --search kubernetes --vendor gcp
    python scripts/cloud_icons.py --list --vendor aws --category groups
    python scripts/cloud_icons.py --render aws:ec2 --px 512 --out /tmp/ec2.png

名前は次のどれでも引ける。

    aws:ec2          ベンダー付きの slug（一番確実）
    ec2              slug だけ（複数ベンダーに当たると候補を出して落ちる）
    s3               別名（正式名は Amazon Simple Storage Service）
    "Cloud SQL"      表示名

**ライセンス上、色を変えたり回したりしてはならない**ので、Scalar アイコンの
`icons.py` と違って `color` の引数は無い。`render()` は指定した画素数で焼くだけ。

| | `icons.py`（Scalar） | 本モジュール |
|---|---|---|
| 素材 | 単色のピクトグラム 62 種 | ベンダー公式のフルカラー 1,700+ 種 |
| 色 | テーマ色に染める | **素材のまま**（改変禁止） |
| 名前 | slug / 日本語名 | `<vendor>:<slug>` / 別名 / 表示名 |
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

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)

# google-slides は assets/shared/、google-slides-template は assets/ の下に置く
_CANDIDATES = [
    os.path.join(SKILL_DIR, "assets", "shared", "cloud-icons"),
    os.path.join(SKILL_DIR, "assets", "cloud-icons"),
]
ICON_DIR = next((d for d in _CANDIDATES if os.path.exists(d)), _CANDIDATES[0])
MANIFEST = os.path.join(ICON_DIR, "cloud-icons.json")
DEFAULT_CACHE = os.path.join(SKILL_DIR, "cache", "cloud-icons")
DEFAULT_PX = 512
VENDORS = ("aws", "gcp", "azure")
VENDOR_LABEL = {"aws": "AWS", "gcp": "Google Cloud", "azure": "Microsoft Azure"}
# ゾーン枠のラベル等に使うベンダー色（アイコンではなく枠線・見出しの色）
VENDOR_COLOR = {"aws": "#FF9900", "gcp": "#4285F4", "azure": "#0078D4"}

_MANIFEST: dict | None = None


class CloudIconError(RuntimeError):
    pass


# ---------- マニフェスト ----------

def manifest() -> dict:
    global _MANIFEST
    if _MANIFEST is None:
        if not os.path.exists(MANIFEST):
            raise FileNotFoundError(
                "クラウドアイコンがまだ取り込まれていません。\n"
                "  アイコンは各ベンダーの資産のためリポジトリには含めていません。\n"
                "  次のコマンドで自分の環境に取り込んでください（1〜2 分・約 8.6MB）:\n"
                "    ~/.claude/venvs/gslides/bin/python scripts/fetch-cloud-icons.py\n"
                f"  配置先: {ICON_DIR}\n"
                "  詳細: assets/shared/cloud-icons/README.md")
        with open(MANIFEST, encoding="utf-8") as f:
            _MANIFEST = json.load(f)
    return _MANIFEST


def icons() -> dict[str, dict]:
    return manifest()["icons"]


def sources() -> dict:
    return manifest().get("sources", {})


def _norm(s: str) -> str:
    return re.sub(r"[\s_\-]+", "", str(s).strip().lower())


def resolve(name: str, *, vendor: str | None = None) -> str:
    """`aws:ec2` / `ec2` / `s3` / 表示名 から `<vendor>:<slug>` を返す。"""
    table = icons()
    if name in table:
        return name
    key = _norm(name)
    if ":" in name:
        v, rest = name.split(":", 1)
        vendor, key = v.strip().lower(), _norm(rest)

    def pool():
        return {k: m for k, m in table.items()
                if not vendor or m["vendor"] == vendor}

    exact = [k for k, m in pool().items()
             if key in (_norm(m["slug"]), _norm(m["name"]))
             or any(key == _norm(a) for a in m["aliases"])]
    if len(exact) > 1:
        # 「ec2」「vpc」はサービスとグループ枠の両方に当たる。サービスを優先し、
        # さらに slug そのものが一致するものを優先する
        services = [k for k in exact if icons()[k]["kind"] == "service"]
        if services:
            exact = services
        by_slug = [k for k in exact if _norm(icons()[k]["slug"]) == key]
        if by_slug:
            exact = by_slug
    if len(exact) == 1:
        return exact[0]
    if exact:
        raise CloudIconError(
            f"'{name}' が複数に当たります: {sorted(exact)[:8]}\n"
            "  vendor 付きの slug（例 aws:ec2）で指定してください")

    hits = search(name, vendor=vendor)
    if len(hits) == 1:
        return hits[0]
    if hits:
        raise CloudIconError(
            f"'{name}' が複数に当たります（{len(hits)} 件）: {hits[:8]}\n"
            "  vendor 付きの slug で指定するか、--search で絞り込んでください")
    raise CloudIconError(
        f"クラウドアイコン '{name}' が見つかりません。\n"
        "  python scripts/cloud_icons.py --search <語> で探せます")


def search(query: str, *, vendor: str | None = None, category: str | None = None,
           kind: str | None = None) -> list[str]:
    """部分一致で `<vendor>:<slug>` のリストを返す。"""
    key = _norm(query) if query else ""
    out = []
    for k, m in icons().items():
        if vendor and m["vendor"] != vendor:
            continue
        if category and m["category"] != category:
            continue
        if kind and m["kind"] != kind:
            continue
        if not key:
            out.append(k)
            continue
        hay = [m["slug"], m["name"], *m["aliases"]]
        if any(key in _norm(h) for h in hay):
            out.append(k)
    return sorted(out)


def meta(name: str, *, vendor: str | None = None) -> dict:
    return icons()[resolve(name, vendor=vendor)]


def svg_path(name: str, *, vendor: str | None = None) -> str:
    m = meta(name, vendor=vendor)
    return os.path.join(ICON_DIR, m["file"])


def describe(key: str) -> str:
    m = icons()[key]
    kind = "" if m["kind"] == "service" else f"  [{m['kind']}]"
    alias = f"  ({', '.join(m['aliases'][:2])})" if m["aliases"] else ""
    return f"{key:44} {m['name']}{kind}{alias}"


# ---------- ラスタライズ ----------

def _svg_aspect(svg: str) -> float:
    """SVG の縦横比（幅 / 高さ）を返す。読めなければ 1.0。"""
    try:
        with open(svg, encoding="utf-8", errors="replace") as f:
            head = f.read(2000)
    except OSError:
        return 1.0
    m = re.search(r'viewBox="([\d.\-\s]+)"', head)
    if m:
        v = [float(x) for x in m.group(1).split()]
        if len(v) == 4 and v[3]:
            return v[2] / v[3]
    w = re.search(r'\swidth="([\d.]+)', head)
    h = re.search(r'\sheight="([\d.]+)', head)
    if w and h and float(h.group(1)):
        return float(w.group(1)) / float(h.group(1))
    return 1.0


def _rasterize(svg: str, out: str, px: int) -> bool:
    """長辺を px に合わせて焼く。**縦横比は必ず保つ**（改変禁止のため）。

    幅と高さを両方指定すると非正方形のアイコン（Azure に数点ある）が
    引き伸ばされ、ベンダーの利用条件に反する。
    """
    ar = _svg_aspect(svg)
    w = px if ar >= 1 else max(1, round(px * ar))
    h = px if ar <= 1 else max(1, round(px / ar))
    try:
        import cairosvg
        cairosvg.svg2png(url=svg, write_to=out, output_width=w, output_height=h)
        return True
    except Exception:
        pass
    if shutil.which("rsvg-convert"):
        cmd = ["rsvg-convert", "-f", "png", "-w", str(w), "-h", str(h), "-o", out, svg]
    elif shutil.which("magick"):
        cmd = ["magick", "-background", "none", "-density", str(px * 3), svg,
               "-resize", f"{px}x{px}", f"PNG:{out}"]
    else:
        return False
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0 or not os.path.exists(out):
        return False
    with open(out, "rb") as f:
        return f.read(8) == b"\x89PNG\r\n\x1a\n"


def render(name: str, *, px: int = DEFAULT_PX, vendor: str | None = None,
           cache_dir: str | None = None, force: bool = False) -> str:
    """アイコンを PNG にしてパスを返す。同じ (アイコン, 画素数) ならキャッシュを使う。

    **色は変えない。** ベンダーの利用条件で改変が禁止されているため、
    そもそも色を指定する引数を持たない。
    """
    key = resolve(name, vendor=vendor)
    m = icons()[key]
    cache_dir = cache_dir or os.environ.get("GSLIDES_CLOUD_ICON_CACHE", DEFAULT_CACHE)
    os.makedirs(cache_dir, exist_ok=True)
    out = os.path.join(cache_dir, f"{key.replace(':', '-')}-{px}.png")
    if os.path.exists(out) and not force:
        return out

    svg = os.path.join(ICON_DIR, m["file"])
    if not os.path.exists(svg):
        raise CloudIconError(
            f"素材がありません: {svg}\n"
            "  python scripts/fetch-cloud-icons.py で取り込み直してください")

    tmp = out + f".{os.getpid()}.part"
    try:
        if not _rasterize(svg, tmp, px):
            # ベンダー同梱の PNG があればそれを使う（cairosvg で焼けない素材向け）
            if m.get("raster"):
                shutil.copyfile(os.path.join(ICON_DIR, m["raster"]), out)
                return out
            raise CloudIconError(
                f"SVG を PNG にできませんでした: {key}\n"
                "  pip install cairosvg（または brew install librsvg）を実行してください")
        os.replace(tmp, out)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    return out


# ---------- SlideBuilder に混ぜるミックスイン ----------

class CloudIconMixin:
    """`SlideBuilder` にクラウドアイコンの配置を足すミックスイン。

    必要なものは `icons.IconLibraryMixin` と同じ（`add_image` / `add_text` /
    `drive_service` / `_uploaded_assets`、枠を描くなら `add_rect`）。
    両方を同時に混ぜてよい。

    **回転・反転・色変更の引数は用意していない。** ベンダーの利用条件で
    禁止されているため、API として出さないことで事故を防いでいる。
    ラベルは既定で表示する（Azure の「アイコンの近くに製品名を置く」推奨に従う）。
    """

    #: ラベルの既定色
    cloud_label_color = None
    #: アイコンを焼く画素数
    cloud_icon_px = DEFAULT_PX

    def _cloud_upload(self, path: str) -> str:
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
            body={"name": f"gslides-cloud-{os.path.basename(path)}"},
            media_body=media, fields="id").execute()["id"]
        drive.permissions().create(
            fileId=fid, body={"type": "anyone", "role": "reader"}, fields="id"
        ).execute()
        if not hasattr(self, "_uploaded_assets"):
            self._uploaded_assets = []
        self._uploaded_assets.append(fid)
        url = f"https://drive.google.com/uc?export=download&id={fid}"
        cache[path] = url
        return url

    @staticmethod
    def _cloud_rgb(c):
        if c is None or isinstance(c, dict):
            return c
        h = c.lstrip("#")
        return {"red": int(h[0:2], 16) / 255, "green": int(h[2:4], 16) / 255,
                "blue": int(h[4:6], 16) / 255}

    def add_cloud_icon(self, slide_id, name, x, y, size=0.6, *, label=None,
                       label_size=8.5, label_w=None, label_gap=0.05,
                       label_color=None, vendor=None, px=None) -> float:
        """クラウドアイコンを size×size の正方形に貼る。戻り値は下端 y。

        `label` を省略すると**アイコンの正式名称**をラベルにする（ベンダー各社が
        「アイコンの近くに製品名を置く」ことを求めているため）。ラベルを出したく
        ない場合だけ `label=""` を渡す。
        """
        m = meta(name, vendor=vendor)
        path = render(name, px=px or self.cloud_icon_px, vendor=vendor)
        self.add_image(slide_id, self._cloud_upload(path), x, y, size, size)

        text = m["name"] if label is None else label
        bottom = y + size
        if text:
            lw = label_w or size * 2.4
            lines = text.count("\n") + 1
            lh = max(0.22, lines * label_size * 1.45 / 72 + 0.06)
            self.add_text(slide_id, text, x + size / 2 - lw / 2, bottom + label_gap,
                          lw, lh, font_size=label_size,
                          color=self._cloud_rgb(label_color or self.cloud_label_color),
                          alignment="CENTER", valign="TOP")
            bottom += label_gap + lh
        return bottom

    def add_cloud_icon_row(self, slide_id, x, y, w, items, *, size=0.6,
                           label_size=8.5, gap=None, label_color=None,
                           vendor=None, px=None) -> float:
        """横一列に等間隔で並べる。items は名前か (名前, ラベル)。"""
        n = len(items)
        cell = w / n
        bottom = y
        for i, item in enumerate(items):
            name, label = item if isinstance(item, (tuple, list)) else (item, None)
            cx = x + i * cell + cell / 2
            bottom = max(bottom, self.add_cloud_icon(
                slide_id, name, cx - size / 2, y, size, label=label,
                label_size=label_size, label_w=cell - (gap if gap else 0.12),
                label_color=label_color, vendor=vendor, px=px))
        return bottom

    def add_cloud_icon_flow(self, slide_id, x, y, w, items, *, size=0.6,
                            label_size=8.5, arrow_color=None, label_color=None,
                            vendor=None, px=None) -> float:
        """矢印でつないだ流れ図。矢印はアイコンの間の隙間にだけ引く。"""
        n = len(items)
        cell = w / n
        bottom = y
        arrow = getattr(self, "add_arrow", None)
        for i, item in enumerate(items):
            name, label = item if isinstance(item, (tuple, list)) else (item, None)
            cx = x + i * cell + cell / 2
            bottom = max(bottom, self.add_cloud_icon(
                slide_id, name, cx - size / 2, y, size, label=label,
                label_size=label_size, label_w=cell - 0.3,
                label_color=label_color, vendor=vendor, px=px))
            if i < n - 1:
                ax = cx + size / 2 + 0.08
                aw = (cx + cell - size / 2 - 0.08) - ax
                ah = min(0.18, size * 0.28)
                fill = self._cloud_rgb(arrow_color or "#6B7280")
                if arrow:
                    arrow(slide_id, ax, y + size / 2 - ah / 2, aw, ah,
                          direction="right", fill=fill)
                else:
                    self.add_rect(slide_id, ax, y + size / 2 - 0.02, aw, 0.04, fill=fill)
        return bottom

    def add_cloud_icon_grid(self, slide_id, x, y, w, items, *, cols=4, size=0.6,
                            row_gap=0.28, label_size=8.5, label_color=None,
                            vendor=None, px=None) -> float:
        """格子状に並べる。items は名前か (名前, ラベル)。"""
        cell = w / cols
        bottom = y
        row_top = y
        for i, item in enumerate(items):
            if i and i % cols == 0:
                row_top = bottom + row_gap
            name, label = item if isinstance(item, (tuple, list)) else (item, None)
            cx = x + (i % cols) * cell + cell / 2
            bottom = max(bottom if i % cols else row_top, self.add_cloud_icon(
                slide_id, name, cx - size / 2, row_top, size, label=label,
                label_size=label_size, label_w=cell - 0.12,
                label_color=label_color, vendor=vendor, px=px))
        return bottom

    def add_cloud_zone(self, slide_id, x, y, w, h, *, vendor=None, title=None,
                       color=None, fill=None, dash="DASH", title_size=9) -> str:
        """ゾーン（クラウド・リージョン・VPC 等）の枠を描き、左上に見出しを置く。

        枠だけを先に描き、中身は後から重ねる。戻り値は枠の objectId。
        `vendor` を渡すとベンダー色と既定の見出し（例「AWS」）が付く。
        """
        c = color or (VENDOR_COLOR.get(vendor) if vendor else "#6B7280")
        oid = self.add_rect(slide_id, x, y, w, h, fill=self._cloud_rgb(fill),
                            border_color=self._cloud_rgb(c))
        if dash and hasattr(self, "requests"):
            # 点線にする。updateShapeProperties は add_rect の直後に足せばよい
            self.requests.append({"updateShapeProperties": {
                "objectId": oid,
                "shapeProperties": {"outline": {"dashStyle": dash}},
                "fields": "outline.dashStyle"}})
        label = title if title is not None else (VENDOR_LABEL.get(vendor) or "")
        if label:
            self.add_text(slide_id, label, x + 0.1, y + 0.06, min(w - 0.2, 3.0), 0.22,
                          font_size=title_size, bold=True,
                          color=self._cloud_rgb(c), alignment="START", valign="MIDDLE")
        return oid


# ---------- CLI ----------

def main() -> int:
    p = argparse.ArgumentParser(
        description="クラウドベンダーの公式アイコンを引く / 書き出す")
    p.add_argument("--list", action="store_true", help="一覧する")
    p.add_argument("--search", help="名前・別名の部分一致で探す")
    p.add_argument("--vendor", choices=VENDORS, help="ベンダーで絞る")
    p.add_argument("--category", help="カテゴリで絞る")
    p.add_argument("--kind", choices=("service", "resource", "group", "category"),
                   help="種別で絞る")
    p.add_argument("--categories", action="store_true", help="カテゴリの一覧を出す")
    p.add_argument("--render", help="1 個を PNG に書き出す")
    p.add_argument("--px", type=int, default=DEFAULT_PX, help=f"画素数（既定 {DEFAULT_PX}）")
    p.add_argument("--out", help="書き出し先のパス")
    p.add_argument("--force", action="store_true", help="キャッシュを無視して焼き直す")
    p.add_argument("--sources", action="store_true", help="取り込み元の版を表示する")
    args = p.parse_args()

    if args.sources:
        m = manifest()
        print(f"generated: {m.get('generatedAt')}")
        for k, v in m.get("sources", {}).items():
            print(f"  {k:16} {v.get('package')}")
        print(f"\n{m.get('note', '')}")
        for v, url in m.get("terms", {}).items():
            print(f"  {v}: {url}")
        return 0

    if args.categories:
        seen: dict[tuple[str, str], int] = {}
        for m in icons().values():
            if args.vendor and m["vendor"] != args.vendor:
                continue
            seen[(m["vendor"], m["category"])] = seen.get((m["vendor"], m["category"]), 0) + 1
        for (v, c), n in sorted(seen.items()):
            print(f"{v:6} {c:32} {n:4}")
        return 0

    if args.render:
        try:
            path = render(args.render, px=args.px, vendor=args.vendor, force=args.force)
        except (CloudIconError, FileNotFoundError) as e:
            print(str(e), file=sys.stderr)
            return 1
        if args.out:
            os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
            shutil.copyfile(path, args.out)
            path = args.out
        print(path)
        return 0

    hits = search(args.search or "", vendor=args.vendor, category=args.category,
                  kind=args.kind)
    if not hits:
        print(f"該当なし: {args.search}", file=sys.stderr)
        return 1
    for k in hits[:400]:
        print(describe(k))
    if len(hits) > 400:
        print(f"... 他 {len(hits) - 400} 件（--vendor / --category / --kind で絞れます）")
    print(f"\n{len(hits)} / {len(icons())} 件", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
