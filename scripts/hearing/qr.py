#!/usr/bin/env python3
"""Make the QR PNG for a collect-qr page.

    python scripts/hearing/qr.py "https://docs.google.com/..." --out out/hearing/qr.png

`qrcode` is optional. When it is missing this writes a clearly-marked
placeholder carrying the URL as text instead of failing, so the deck still
builds and the gap is visible on the page rather than silent — the same
fallback shape the icon pipeline uses for `cairosvg`.

    pip install "qrcode[pil]"     # to get a real QR
"""
from __future__ import annotations

import argparse
import os
import sys

PLACEHOLDER_NOTE = "QR 未生成"


def available() -> bool:
    try:
        import qrcode  # noqa: F401
    except ImportError:
        return False
    return True


def _placeholder(url: str, path: str, size: int) -> str:
    """A bordered square that says the QR is missing and prints the URL."""
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (size, size), "white")
    d = ImageDraw.Draw(img)
    d.rectangle([4, 4, size - 5, size - 5], outline="#B00020", width=6)
    lines = [PLACEHOLDER_NOTE, "", *(url[i:i + 28] for i in range(0, min(len(url), 112), 28))]
    y = size // 2 - len(lines) * 8
    for line in lines:
        d.text((18, y), line, fill="#B00020")
        y += 16
    img.save(path)
    return path


def build(url: str, path: str, *, size: int = 600) -> tuple[str, bool]:
    """Write the QR (or the placeholder) to `path`. Returns (path, is_real_qr)."""
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    if not available():
        return _placeholder(url, path, size), False

    import qrcode

    qr = qrcode.QRCode(box_size=10, border=2,
                       error_correction=qrcode.constants.ERROR_CORRECT_M)
    qr.add_data(url)
    qr.make(fit=True)
    qr.make_image(fill_color="black", back_color="white").resize((size, size)).save(path)
    return path, True


def main() -> int:
    p = argparse.ArgumentParser(description="回答先の QR コードを作る")
    p.add_argument("url")
    p.add_argument("--out", required=True)
    p.add_argument("--size", type=int, default=600)
    args = p.parse_args()

    path, real = build(args.url, args.out, size=args.size)
    print(f"出力: {path}")
    if not real:
        print("qrcode が入っていないため、プレースホルダを書き出した。", file=sys.stderr)
        print('  実際の QR にするには: pip install "qrcode[pil]"', file=sys.stderr)
        print("  このまま資料に載せない。URL は so_what 側に必ず併記すること。", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
