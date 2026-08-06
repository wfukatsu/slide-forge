#!/usr/bin/env python3
"""クラウドベンダー（AWS / Google Cloud / Azure）の公式アイコンを引く。

素材は `assets/cloud-icons/`。取り込みは `scripts/fetch_cloud_icons.py` で行う
（gitignore 対象。リポジトリ取得後に 1 回実行して復元する）。

    python scripts/cloud_icons.py --search s3
    python scripts/cloud_icons.py --list --vendor aws --category groups
    python scripts/cloud_icons.py --render aws:ec2 --px 512 --out out/ec2.png

名前は `aws:ec2` / `ec2` / `s3`（別名）/ `Cloud SQL`（表示名）のどれでも引ける。

**ライセンス上、色を変えたり回したりしてはならない**ので、Scalar アイコンの
`icons.py` と違って `color` の引数は無い。`render()` は指定した画素数で焼くだけ。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)

sys.path.insert(0, SCRIPT_DIR)
from _i18n import t, register  # noqa: E402

register({
    "Cloud icons have not been fetched yet.\n"
    "  The icons are vendor assets, so they are not included in the repository.\n"
    "  Fetch them into your environment with this command (1-2 min, ~8.6MB):\n"
    "    .venv/bin/python scripts/fetch_cloud_icons.py\n"
    "  Destination: {dir}\n"
    "  Details: assets/cloud-icons/README.md":
        "クラウドアイコンがまだ取り込まれていません。\n"
        "  アイコンは各ベンダーの資産のためリポジトリには含めていません。\n"
        "  次のコマンドで自分の環境に取り込んでください（1〜2 分・約 8.6MB）:\n"
        "    .venv/bin/python scripts/fetch_cloud_icons.py\n"
        "  配置先: {dir}\n"
        "  詳細: assets/cloud-icons/README.md",
    "'{name}' matches multiple icons: {hits}\n"
    "  Specify a vendor-qualified slug (e.g. aws:ec2)":
        "'{name}' が複数に当たります: {hits}\n"
        "  vendor 付きの slug（例 aws:ec2）で指定してください",
    "'{name}' matches multiple icons ({count} hits): {hits}\n"
    "  Specify a vendor-qualified slug or narrow it down with --search":
        "'{name}' が複数に当たります（{count} 件）: {hits}\n"
        "  vendor 付きの slug で指定するか、--search で絞り込んでください",
    "Cloud icon '{name}' not found.\n"
    "  Search with: python scripts/cloud_icons.py --search <word>":
        "クラウドアイコン '{name}' が見つかりません。\n"
        "  python scripts/cloud_icons.py --search <語> で探せます",
    "Asset file missing: {path}": "素材がありません: {path}",
    "Could not convert the SVG to PNG: {key}\n  Run pip install cairosvg":
        "SVG を PNG にできませんでした: {key}\n"
        "  pip install cairosvg を実行してください",
    "Look up the official cloud vendor icons": "クラウドベンダーの公式アイコンを引く",
    "List icons": "一覧する",
    "Search by partial match on name or alias": "名前・別名の部分一致で探す",
    "Filter by vendor": "ベンダーで絞る",
    "Filter by category": "カテゴリで絞る",
    "List the categories": "カテゴリの一覧を出す",
    "Export one icon to PNG": "1 個を PNG に書き出す",
    "Output file path": "書き出し先のパス",
    "Show the versions of the fetched packages": "取り込み元の版を表示する",
    "No matches: {query}": "該当なし: {query}",
    "... {count} more (narrow down with --vendor / --category / --kind)":
        "... 他 {count} 件（--vendor / --category / --kind で絞れます）",
    "\n{shown} / {total} icons": "\n{shown} / {total} 件",
})

ICON_DIR = os.path.join(SKILL_DIR, "assets", "cloud-icons")
MANIFEST = os.path.join(ICON_DIR, "cloud-icons.json")
DEFAULT_CACHE = os.path.join(SKILL_DIR, "cache", "cloud-icons")
DEFAULT_PX = 512
VENDORS = ("aws", "gcp", "azure")
VENDOR_LABEL = {"aws": "AWS", "gcp": "Google Cloud", "azure": "Microsoft Azure"}
# ゾーン枠の線・見出しに使うベンダー色（アイコン自体は染めない）
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
                t("Cloud icons have not been fetched yet.\n"
                  "  The icons are vendor assets, so they are not included in the repository.\n"
                  "  Fetch them into your environment with this command (1-2 min, ~8.6MB):\n"
                  "    .venv/bin/python scripts/fetch_cloud_icons.py\n"
                  "  Destination: {dir}\n"
                  "  Details: assets/cloud-icons/README.md", dir=ICON_DIR))
        with open(MANIFEST, encoding="utf-8") as f:
            _MANIFEST = json.load(f)
    return _MANIFEST


def icons() -> dict[str, dict]:
    return manifest()["icons"]


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

    pool = {k: m for k, m in table.items() if not vendor or m["vendor"] == vendor}
    exact = [k for k, m in pool.items()
             if key in (_norm(m["slug"]), _norm(m["name"]))
             or any(key == _norm(a) for a in m["aliases"])]
    if len(exact) > 1:
        # 「ec2」「vpc」はサービスとグループ枠の両方に当たる。サービスを優先し、
        # さらに slug そのものが一致するものを優先する
        services = [k for k in exact if table[k]["kind"] == "service"]
        if services:
            exact = services
        by_slug = [k for k in exact if _norm(table[k]["slug"]) == key]
        if by_slug:
            exact = by_slug
    if len(exact) == 1:
        return exact[0]
    if exact:
        raise CloudIconError(
            t("'{name}' matches multiple icons: {hits}\n"
              "  Specify a vendor-qualified slug (e.g. aws:ec2)",
              name=name, hits=sorted(exact)[:8]))

    hits = search(name, vendor=vendor)
    if len(hits) == 1:
        return hits[0]
    if hits:
        raise CloudIconError(
            t("'{name}' matches multiple icons ({count} hits): {hits}\n"
              "  Specify a vendor-qualified slug or narrow it down with --search",
              name=name, count=len(hits), hits=hits[:8]))
    raise CloudIconError(
        t("Cloud icon '{name}' not found.\n"
          "  Search with: python scripts/cloud_icons.py --search <word>", name=name))


def search(query: str, *, vendor: str | None = None, category: str | None = None,
           kind: str | None = None) -> list[str]:
    key = _norm(query) if query else ""
    out = []
    for k, m in icons().items():
        if vendor and m["vendor"] != vendor:
            continue
        if category and m["category"] != category:
            continue
        if kind and m["kind"] != kind:
            continue
        if not key or any(key in _norm(h) for h in [m["slug"], m["name"], *m["aliases"]]):
            out.append(k)
    return sorted(out)


def meta(name: str, *, vendor: str | None = None) -> dict:
    return icons()[resolve(name, vendor=vendor)]


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
    """アイコンを PNG にしてパスを返す。**色は変えない**（改変禁止のため）。"""
    key = resolve(name, vendor=vendor)
    m = icons()[key]
    cache_dir = cache_dir or os.environ.get("GSLIDES_CLOUD_ICON_CACHE", DEFAULT_CACHE)
    os.makedirs(cache_dir, exist_ok=True)
    out = os.path.join(cache_dir, f"{key.replace(':', '-')}-{px}.png")
    if os.path.exists(out) and not force:
        return out

    svg = os.path.join(ICON_DIR, m["file"])
    if not os.path.exists(svg):
        raise CloudIconError(t("Asset file missing: {path}", path=svg))
    tmp = out + f".{os.getpid()}.part"
    try:
        if not _rasterize(svg, tmp, px):
            if m.get("raster"):
                shutil.copyfile(os.path.join(ICON_DIR, m["raster"]), out)
                return out
            raise CloudIconError(
                t("Could not convert the SVG to PNG: {key}\n"
                  "  Run pip install cairosvg", key=key))
        os.replace(tmp, out)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    return out


# ---------- Canvas に生やすメソッド ----------

class CloudIconMixin:
    """`Canvas` にクラウドアイコンの配置を足すミックスイン。

    座標の規約は `illustrations` / `icons` と同じ。size×size の正方形に貼り、
    **戻り値はラベルを含めた下端 y**。

    **回転・反転・色変更の引数は用意していない。** ベンダーの利用条件で禁止
    されているため、API として出さないことで事故を防いでいる。ラベルは既定で
    正式名称を表示する（各社が「アイコンの近くに製品名を」と求めているため）。
    """

    #: アイコンを焼く画素数
    cloud_icon_px = DEFAULT_PX

    def cloud_icon(self, name: str, x: float, y: float, size: float = 0.6, *,
                   label: str | None = None, label_size: float = 8.5,
                   label_w: float | None = None, label_gap: float = 0.05,
                   label_color=None, vendor: str | None = None,
                   px: int | None = None) -> float:
        """クラウドアイコンを size×size の正方形に貼る。戻り値は下端 y。

        `label` を省略すると正式名称（例「Amazon EC2」）を下に置く。ラベルを
        出したくないときだけ `label=""` を渡す。
        """
        m = meta(name, vendor=vendor)
        if getattr(self.deck, "dry", False):
            # --dry-run: 画像は取りに行けないので同じ大きさの矩形で座標だけ確かめる
            self.shape(x, y, size, size, kind="RECTANGLE",
                       fill=self.P.surfaceAlt, stroke=self.P.border)
        else:
            path = render(name, px=px or self.cloud_icon_px, vendor=vendor)
            self.image(x, y, size, size, path, fit="contain", alt=m["name"])

        text = m["name"] if label is None else label
        bottom = y + size
        if text:
            lw = label_w or size * 2.4
            lines = text.count("\n") + 1
            lh = max(0.22, lines * label_size * 1.45 / 72 + 0.06)
            self.label(x + size / 2 - lw / 2, bottom + label_gap, lw, lh, text,
                       size=label_size, align="CENTER", valign="TOP",
                       color=label_color or self.P.text, line_spacing=110)
            bottom += label_gap + lh
        return bottom

    def cloud_icon_row(self, x: float, y: float, w: float, items, *,
                       size: float = 0.6, label_size: float = 8.5,
                       gap: float | None = None, vendor: str | None = None,
                       px: int | None = None) -> float:
        """横一列に等間隔で並べる。items は名前か (名前, ラベル)。"""
        n = len(items)
        cell = w / n
        bottom = y
        for i, item in enumerate(items):
            name, label = item if isinstance(item, (tuple, list)) else (item, None)
            cx = x + i * cell + cell / 2
            bottom = max(bottom, self.cloud_icon(
                name, cx - size / 2, y, size, label=label, label_size=label_size,
                label_w=cell - (gap if gap else 0.12), vendor=vendor, px=px))
        return bottom

    def cloud_icon_flow(self, x: float, y: float, w: float, items, *,
                        size: float = 0.6, label_size: float = 8.5,
                        arrow_color=None, vendor: str | None = None,
                        px: int | None = None) -> float:
        """矢印でつないだ流れ図。矢印はアイコンの間の隙間にだけ引く。"""
        n = len(items)
        cell = w / n
        bottom = y
        for i, item in enumerate(items):
            name, label = item if isinstance(item, (tuple, list)) else (item, None)
            cx = x + i * cell + cell / 2
            bottom = max(bottom, self.cloud_icon(
                name, cx - size / 2, y, size, label=label, label_size=label_size,
                label_w=cell - 0.3, vendor=vendor, px=px))
            if i < n - 1:
                ay = y + size / 2
                self.arrow(cx + size / 2 + 0.08, ay, cx + cell - size / 2 - 0.08, ay,
                           color=arrow_color or self.P.muted, weight=1.25,
                           _anchored=True)
        return bottom

    def cloud_icon_grid(self, x: float, y: float, w: float, items, *, cols: int = 4,
                        size: float = 0.6, row_gap: float = 0.28,
                        label_size: float = 8.5, vendor: str | None = None,
                        px: int | None = None) -> float:
        """格子状に並べる。items は名前か (名前, ラベル)。"""
        cell = w / cols
        bottom = y
        row_top = y
        for i, item in enumerate(items):
            if i and i % cols == 0:
                row_top = bottom + row_gap
            name, label = item if isinstance(item, (tuple, list)) else (item, None)
            cx = x + (i % cols) * cell + cell / 2
            bottom = max(bottom if i % cols else row_top, self.cloud_icon(
                name, cx - size / 2, row_top, size, label=label,
                label_size=label_size, label_w=cell - 0.12, vendor=vendor, px=px))
        return bottom

    def cloud_zone(self, x: float, y: float, w: float, h: float, *,
                   vendor: str | None = None, title: str | None = None,
                   color: str | None = None, fill=None, dash: str = "DASH",
                   title_size: float = 9) -> float:
        """ゾーン（クラウド・リージョン・VPC 等）の枠と左上の見出しを描く。

        **枠を先に描いてから中身を重ねること。** 後から描くと中身が隠れる。
        戻り値は枠の下端 y。
        """
        c = color or (VENDOR_COLOR.get(vendor) if vendor else self.P.muted)
        self.shape(x, y, w, h, kind="RECTANGLE", fill=fill, stroke=c,
                   dash=dash, stroke_weight=1.0)
        text = title if title is not None else (VENDOR_LABEL.get(vendor) or "")
        if text:
            self.label(x + 0.1, y + 0.06, min(w - 0.2, 3.2), 0.24, text,
                       size=title_size, bold=True, align="START", valign="MIDDLE",
                       color=c)
        return y + h


# ---------- CLI ----------

def main() -> int:
    p = argparse.ArgumentParser(description=t("Look up the official cloud vendor icons"))
    p.add_argument("--list", action="store_true", help=t("List icons"))
    p.add_argument("--search", help=t("Search by partial match on name or alias"))
    p.add_argument("--vendor", choices=VENDORS, help=t("Filter by vendor"))
    p.add_argument("--category", help=t("Filter by category"))
    p.add_argument("--kind", choices=("service", "resource", "group", "category"))
    p.add_argument("--categories", action="store_true", help=t("List the categories"))
    p.add_argument("--render", help=t("Export one icon to PNG"))
    p.add_argument("--px", type=int, default=DEFAULT_PX)
    p.add_argument("--out", help=t("Output file path"))
    p.add_argument("--force", action="store_true")
    p.add_argument("--sources", action="store_true",
                   help=t("Show the versions of the fetched packages"))
    args = p.parse_args()

    if args.sources:
        m = manifest()
        print(f"generated: {m.get('generatedAt')}")
        for k, v in m.get("sources", {}).items():
            print(f"  {k:16} {v.get('package')}")
        print(f"\n{m.get('note', '')}")
        return 0

    if args.categories:
        seen: dict[tuple[str, str], int] = {}
        for m in icons().values():
            if args.vendor and m["vendor"] != args.vendor:
                continue
            k = (m["vendor"], m["category"])
            seen[k] = seen.get(k, 0) + 1
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
        print(t("No matches: {query}", query=args.search), file=sys.stderr)
        return 1
    for k in hits[:400]:
        print(describe(k))
    if len(hits) > 400:
        print(t("... {count} more (narrow down with --vendor / --category / --kind)",
                count=len(hits) - 400))
    print(t("\n{shown} / {total} icons", shown=len(hits), total=len(icons())),
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
