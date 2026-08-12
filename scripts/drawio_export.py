#!/usr/bin/env python3
"""Export a draw.io (.drawio) file to PNG (for inserting into slides).

    python scripts/drawio_export.py <in.drawio> [--out out/diagrams/x.png]
        [--scale 2] [--page N] [--transparent] [--border 4]

Uses the drawio desktop CLI's headless export (`/opt/homebrew/bin/drawio`,
installed via `brew install --cask drawio`; falls back to the in-app binary
if that's missing). The PNG is cropped to the bounding box of the drawn
content, not the page size.

Always visually verify the exported PNG with the Read tool: a nonexistent
resIcon / shape name doesn't raise an error — it's rendered as a "plain
colored square" instead, which can't be detected from the CLI's return
value. See references/drawio.md for notation and verified styles.
"""
from __future__ import annotations

import argparse
import os
import shutil
import struct
import subprocess
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _i18n import t, register  # noqa: E402

register({
    "drawio CLI not found. Install it with `brew install --cask drawio`":
        "drawio CLI が見つかりません。`brew install --cask drawio` で"
        "インストールしてください",
    "Invalid XML: {path}: {error}": "XML が不正です: {path}: {error}",
    "Root element is not mxfile: <{tag}>": "ルート要素が mxfile ではありません: <{tag}>",
    "No diagram element found": "diagram 要素がありません",
    "Cannot read as PNG: {path}": "PNG として読めません: {path}",
    "Export a .drawio file to PNG": ".drawio を PNG に書き出す",
    "Path of the .drawio file": ".drawio ファイルのパス",
    "Output PNG path (default: .png next to the input)":
        "出力 PNG のパス（省略時: 入力と同じ場所に .png）",
    "Scale factor (default 2; use 2 or more for full-slide figures)":
        "拡大率（既定 2。スライド全面に使う図は 2 以上を推奨）",
    "Page number to export (1-based; default: the first page)":
        "書き出すページ番号（1 始まり。省略時は 1 ページ目）",
    "Make the background transparent": "背景を透過にする",
    "Margin around the figure in px (default 4; keeps edge lines from "
    "being clipped)":
        "図の周囲の余白 px（既定 4。端の線が欠けるのを防ぐ）",
    "File not found: {path}": "ファイルがありません: {path}",
    "Export failed (exit {code})": "エクスポートに失敗しました (exit {code})",
    "Open this PNG with the Read tool and verify it visually "
    "(unknown shape names render as plain squares)":
        "この PNG を Read で開いて目視確認すること"
        "（未知のシェイプ名は無地の四角になる）",
})

APP_BINARY = "/Applications/draw.io.app/Contents/MacOS/draw.io"


def find_drawio() -> str:
    path = shutil.which("drawio") or (APP_BINARY if os.path.exists(APP_BINARY) else None)
    if not path:
        raise SystemExit(
            t("drawio CLI not found. Install it with `brew install --cask drawio`")
        )
    return path


def check_xml(path: str) -> None:
    """Check that the file is well-formed and has an mxfile structure before exporting."""
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as e:
        raise SystemExit(t("Invalid XML: {path}: {error}", path=path, error=e))
    if root.tag != "mxfile":
        raise SystemExit(t("Root element is not mxfile: <{tag}>", tag=root.tag))
    if root.find("diagram") is None:
        raise SystemExit(t("No diagram element found"))


def png_size(path: str) -> tuple[int, int]:
    with open(path, "rb") as f:
        head = f.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit(t("Cannot read as PNG: {path}", path=path))
    w, h = struct.unpack(">II", head[16:24])
    return w, h


def main() -> int:
    p = argparse.ArgumentParser(description=t("Export a .drawio file to PNG"))
    p.add_argument("source", help=t("Path of the .drawio file"))
    p.add_argument("--out", help=t("Output PNG path (default: .png next to the input)"))
    p.add_argument("--scale", type=float, default=2.0,
                   help=t("Scale factor (default 2; use 2 or more for "
                          "full-slide figures)"))
    p.add_argument("--page", type=int,
                   help=t("Page number to export (1-based; default: the first page)"))
    p.add_argument("--transparent", action="store_true",
                   help=t("Make the background transparent"))
    p.add_argument("--border", type=int, default=4,
                   help=t("Margin around the figure in px (default 4; keeps edge "
                          "lines from being clipped)"))
    args = p.parse_args()

    if not os.path.exists(args.source):
        raise SystemExit(t("File not found: {path}", path=args.source))
    check_xml(args.source)

    out = args.out or os.path.splitext(args.source)[0] + ".png"
    out_dir = os.path.dirname(os.path.abspath(out))
    os.makedirs(out_dir, exist_ok=True)

    cmd = [find_drawio(), "-x", "-f", "png",
           "-s", str(args.scale), "-b", str(args.border), "-o", out]
    if args.page:
        cmd += ["-p", str(args.page)]
    if args.transparent:
        cmd.append("-t")
    cmd.append(args.source)

    res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if res.returncode != 0 or not os.path.exists(out):
        sys.stderr.write(res.stdout + res.stderr)
        raise SystemExit(t("Export failed (exit {code})", code=res.returncode))

    w, h = png_size(out)
    print(f"{out}  ({w}x{h})")
    print(t("Open this PNG with the Read tool and verify it visually "
            "(unknown shape names render as plain squares)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
