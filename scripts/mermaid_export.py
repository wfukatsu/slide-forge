#!/usr/bin/env python3
"""Render the mermaid blocks of a Markdown report to PNG (for slide insertion).

    python scripts/mermaid_export.py <report.md> [--out-dir out/nexus/shots]
    python scripts/mermaid_export.py <report.md> --index 2 --out out/x.png
    python scripts/mermaid_export.py <report.md> --list

Built for nexus-architect reports, which carry their structure diagrams as
fenced ```mermaid blocks. Uses the mermaid CLI (`mmdc`, `npm i -g
@mermaid-js/mermaid-cli`), the same way `drawio_export.py` uses the drawio CLI.

**Only structure diagrams are rendered.** `xychart`, `pie` and the other chart
kinds are skipped by default: the numbers behind them are in the report's
tables, and redrawing those with `hbars` / `vbars` / `table` gives a figure
that matches the rest of the deck instead of a foreign-looking image. Pass
`--charts` to render them anyway.

Always open the PNG with the Read tool afterwards. A diagram that renders is
not necessarily a diagram that reads at slide size — wide `graph LR` output in
particular often needs to be split or replaced with a native figure.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _i18n import t, register  # noqa: E402

register({
    "Render a report's mermaid blocks to PNG": "レポートの mermaid ブロックを PNG にする",
    "path of the Markdown report": "Markdown レポートのパス",
    "output directory (default: out/nexus/shots)":
        "出力ディレクトリ（省略時: out/nexus/shots）",
    "output path for a single --index": "--index を 1 つ指定したときの出力パス",
    "which block to render (1-based; default: every structure diagram)":
        "描画するブロック番号（1 始まり。省略時は構造図すべて）",
    "list the blocks and what would be rendered, without rendering":
        "描画せず、ブロックの一覧と対象可否を表示する",
    "also render chart kinds ({kinds})": "チャート系（{kinds}）も描画する",
    "scale factor (default 3; mermaid text is small at slide size)":
        "拡大率（既定 3。mermaid の文字はスライドサイズだと小さい）",
    "mmdc not found. Install it with `npm i -g @mermaid-js/mermaid-cli`":
        "mmdc が見つかりません。`npm i -g @mermaid-js/mermaid-cli` で"
        "インストールしてください",
    "File not found: {path}": "ファイルがありません: {path}",
    "no mermaid blocks in {path}": "{path} に mermaid ブロックはありません",
    "block {i} does not exist ({n} in this report)":
        "ブロック {i} はありません（このレポートには {n} 個）",
    "Render failed for block {i} (exit {code})":
        "ブロック {i} の描画に失敗しました (exit {code})",
    "Cannot read as PNG: {path}": "PNG として読めません: {path}",
    "  {i}: {kind}  -> {status}": "  {i}: {kind}  -> {status}",
    "skipped (chart kind; redraw from the report's table)":
        "対象外（チャート系。レポートの表からネイティブ図に描き直す）",
    "Open these PNGs with the Read tool and verify they read at slide size":
        "これらの PNG を Read で開き、スライドサイズで読めるか確認すること",
})

# Diagram kinds whose data belongs in a native figure instead of an image.
CHART_KINDS = ("xychart", "xychart-beta", "pie", "quadrantChart", "sankey",
               "sankey-beta", "radar", "radar-beta")
DEFAULT_OUT_DIR = os.path.join("out", "nexus", "shots")


def find_mmdc() -> str:
    path = shutil.which("mmdc")
    if not path:
        raise SystemExit(
            t("mmdc not found. Install it with `npm i -g @mermaid-js/mermaid-cli`"))
    return path


def png_size(path: str) -> tuple[int, int]:
    with open(path, "rb") as f:
        head = f.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit(t("Cannot read as PNG: {path}", path=path))
    return struct.unpack(">II", head[16:24])


def blocks(text: str) -> list[dict]:
    """Every fenced mermaid block, with its diagram kind and heading."""
    out: list[dict] = []
    for m in re.finditer(r"```mermaid\n(.*?)```", text, re.S):
        code = m.group(1)
        first = next((ln.strip() for ln in code.splitlines() if ln.strip()), "")
        kind = first.split()[0] if first else ""
        heading = ""
        for line in text[:m.start()].splitlines():
            if line.startswith("#"):
                heading = line.lstrip("#").strip()
        out.append({"index": len(out) + 1, "kind": kind, "heading": heading,
                    "code": code, "isChart": kind in CHART_KINDS})
    return out


def render(block: dict, out_path: str, *, scale: float = 3.0) -> tuple[int, int]:
    mmdc = find_mmdc()
    os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="mermaid-") as tmp:
        src = os.path.join(tmp, "diagram.mmd")
        with open(src, "w", encoding="utf-8") as f:
            f.write(block["code"])
        res = subprocess.run(
            [mmdc, "-i", src, "-o", os.path.abspath(out_path),
             "-b", "white", "-s", str(scale)],
            capture_output=True, text=True, timeout=180)
    if res.returncode != 0 or not os.path.exists(out_path):
        sys.stderr.write(res.stdout + res.stderr)
        raise SystemExit(t("Render failed for block {i} (exit {code})",
                           i=block["index"], code=res.returncode))
    return png_size(out_path)


def main() -> int:
    p = argparse.ArgumentParser(
        description=t("Render a report's mermaid blocks to PNG"))
    p.add_argument("source", help=t("path of the Markdown report"))
    p.add_argument("--out-dir", default=DEFAULT_OUT_DIR,
                   help=t("output directory (default: out/nexus/shots)"))
    p.add_argument("--out", help=t("output path for a single --index"))
    p.add_argument("--index", type=int,
                   help=t("which block to render (1-based; default: every "
                          "structure diagram)"))
    p.add_argument("--list", action="store_true",
                   help=t("list the blocks and what would be rendered, "
                          "without rendering"))
    p.add_argument("--charts", action="store_true",
                   help=t("also render chart kinds ({kinds})",
                          kinds=", ".join(CHART_KINDS[:3]) + ", …"))
    p.add_argument("--scale", type=float, default=3.0,
                   help=t("scale factor (default 3; mermaid text is small at "
                          "slide size)"))
    args = p.parse_args()

    if not os.path.exists(args.source):
        raise SystemExit(t("File not found: {path}", path=args.source))
    with open(args.source, encoding="utf-8", errors="replace") as f:
        found = blocks(f.read())
    if not found:
        print(t("no mermaid blocks in {path}", path=args.source))
        return 0

    wanted = found
    if args.index:
        wanted = [b for b in found if b["index"] == args.index]
        if not wanted:
            raise SystemExit(t("block {i} does not exist ({n} in this report)",
                               i=args.index, n=len(found)))
    elif not args.charts:
        wanted = [b for b in found if not b["isChart"]]

    if args.list:
        for b in found:
            status = ("render" if b in wanted else
                      t("skipped (chart kind; redraw from the report's table)"))
            print(t("  {i}: {kind}  -> {status}",
                    i=b["index"], kind=b["kind"] or "?", status=status))
        return 0

    stem = os.path.splitext(os.path.basename(args.source))[0]
    written = []
    for b in wanted:
        out = args.out if (args.out and args.index) else os.path.join(
            args.out_dir, f"{stem}-{b['index']:02d}.png")
        w, h = render(b, out, scale=args.scale)
        written.append({"path": out, "width": w, "height": h,
                        "kind": b["kind"], "heading": b["heading"]})
        print(f"{out}  ({w}x{h})  {b['kind']}  {b['heading']}")
    if written:
        print(t("Open these PNGs with the Read tool and verify they read at "
                "slide size"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
