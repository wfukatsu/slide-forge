#!/usr/bin/env python3
"""Screenshot a local HTML file to PNG with headless Chrome (for slide insertion).

    python scripts/html_shot.py <page.html> [--out out/nexus/shots/x.png]
        [--width 1280] [--height 900] [--scale 2]

Built for the self-contained UI mocks a nexus-architect product run writes to
`reports/02_spec/ui-mocks/`, and usable for any local page (a consolidated
`full-report.html`, a rendered chart). Shells out the same way
`drawio_export.py` shells out to the drawio CLI: find the binary, fail with a
plain message when it is missing, verify the PNG that comes back.

Chrome captures the **window**, so a page taller than `--height` is clipped at
the fold. That is usually the right frame for a slide; raise `--height` when a
mock has to be shown whole. There is no full-page flag in the CLI, and adding a
DevTools-protocol client to get one is not worth the dependency here.

Chrome writes the PNG and then does not exit (both `--headless` and
`--headless=new`, macOS, verified 2026-08), so this waits for the file to stop
growing and terminates the process itself rather than blocking forever.

Always open the PNG with the Read tool afterwards: a mock that failed to load
its inline CSS still screenshots successfully, as a page of unstyled text.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _i18n import t, register  # noqa: E402

register({
    "Screenshot a local HTML file to PNG": "ローカルの HTML を PNG に撮る",
    "path of the .html file": ".html ファイルのパス",
    "output PNG path (default: .png next to the input)":
        "出力 PNG のパス（省略時: 入力と同じ場所に .png）",
    "viewport width in px (default 1280)": "ビューポート幅 px（既定 1280）",
    "viewport height in px (default 900)": "ビューポート高さ px（既定 900）",
    "device pixel ratio (default 2; keeps text legible when scaled down "
    "into a slide)":
        "デバイスピクセル比（既定 2。スライドに縮小して置いても文字が読める）",
    "Chrome not found. Install Google Chrome, or set $CHROME_BINARY":
        "Chrome が見つかりません。Google Chrome を入れるか $CHROME_BINARY を"
        "設定してください",
    "File not found: {path}": "ファイルがありません: {path}",
    "Screenshot failed (exit {code})": "スクリーンショットに失敗しました (exit {code})",
    "Cannot read as PNG: {path}": "PNG として読めません: {path}",
    "Screenshot timed out after {n}s and wrote nothing": 
        "{n} 秒待ってもスクリーンショットが書き出されませんでした",
    "Open this PNG with the Read tool and verify it visually "
    "(a page that failed to style itself still screenshots fine)":
        "この PNG を Read で開いて目視確認すること"
        "（スタイルが当たらなかったページでも撮影自体は成功する）",
})

MAC_BINARY = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
DEFAULT_TIMEOUT = 90


def find_chrome() -> str:
    env = os.environ.get("CHROME_BINARY")
    candidates = [env] if env else []
    candidates += [shutil.which("google-chrome"), shutil.which("chromium"),
                   shutil.which("chrome"), MAC_BINARY]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    raise SystemExit(t("Chrome not found. Install Google Chrome, or set "
                       "$CHROME_BINARY"))


def png_size(path: str) -> tuple[int, int]:
    with open(path, "rb") as f:
        head = f.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit(t("Cannot read as PNG: {path}", path=path))
    return struct.unpack(">II", head[16:24])


def shot(source: str, out: str, *, width: int = 1280, height: int = 900,
         scale: float = 2.0, timeout: int = DEFAULT_TIMEOUT) -> tuple[int, int]:
    """Capture *source* to *out* and return the PNG's pixel size."""
    chrome = find_chrome()
    out = os.path.abspath(out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    if os.path.exists(out):
        os.remove(out)          # so a stale file cannot be mistaken for success
    # A throwaway profile keeps this out of the user's real Chrome profile and
    # lets two captures run at once without fighting over the profile lock.
    with tempfile.TemporaryDirectory(prefix="html-shot-") as profile:
        cmd = [chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars",
               "--no-first-run", "--no-default-browser-check",
               f"--user-data-dir={profile}",
               f"--window-size={width},{height}",
               f"--force-device-scale-factor={scale}",
               f"--screenshot={out}", "file://" + os.path.abspath(source)]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True)
        # Chrome writes the PNG and then keeps running (its updater keeps the
        # process alive), so waiting for exit would hang. Wait for the file to
        # stop growing instead, then stop the process.
        deadline = time.time() + timeout
        last = -1
        try:
            while time.time() < deadline:
                if proc.poll() is not None:
                    break
                if os.path.exists(out):
                    size = os.path.getsize(out)
                    if size and size == last:
                        break
                    last = size
                time.sleep(0.4)
        finally:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill()
    if not os.path.exists(out):
        err = (proc.stderr.read() if proc.stderr else "") or ""
        sys.stderr.write(err[-2000:])
        raise SystemExit(t("Screenshot timed out after {n}s and wrote nothing",
                           n=timeout))
    return png_size(out)


def main() -> int:
    p = argparse.ArgumentParser(description=t("Screenshot a local HTML file to PNG"))
    p.add_argument("source", help=t("path of the .html file"))
    p.add_argument("--out", help=t("output PNG path (default: .png next to the input)"))
    p.add_argument("--width", type=int, default=1280,
                   help=t("viewport width in px (default 1280)"))
    p.add_argument("--height", type=int, default=900,
                   help=t("viewport height in px (default 900)"))
    p.add_argument("--scale", type=float, default=2.0,
                   help=t("device pixel ratio (default 2; keeps text legible "
                          "when scaled down into a slide)"))
    p.add_argument("--json", action="store_true", help=argparse.SUPPRESS)
    args = p.parse_args()

    if not os.path.exists(args.source):
        raise SystemExit(t("File not found: {path}", path=args.source))
    out = args.out or os.path.splitext(args.source)[0] + ".png"
    w, h = shot(args.source, out, width=args.width, height=args.height,
                scale=args.scale)
    if args.json:
        print(json.dumps({"path": out, "width": w, "height": h}))
        return 0
    print(f"{out}  ({w}x{h})")
    print(t("Open this PNG with the Read tool and verify it visually "
            "(a page that failed to style itself still screenshots fine)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
