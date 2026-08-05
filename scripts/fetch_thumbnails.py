#!/usr/bin/env python3
"""生成したプレゼンテーションのサムネイルを取得する（視覚的 QA 用）。

    python scripts/fetch_thumbnails.py <URL または ID> --out out/qa [--size LARGE]
    python scripts/fetch_thumbnails.py <URL> --out out/qa --pages 1,3,5

取得した PNG は Read ツールで開いて目視確認する。文字の欠け・はみ出し・
装飾との重なりは API レスポンスからは分からないので、この確認を省略しないこと。
"""
from __future__ import annotations

import argparse
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _auth  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description="スライドのサムネイルを取得する")
    p.add_argument("source", help="プレゼンテーションの URL または ID")
    p.add_argument("--out", required=True, help="出力ディレクトリ")
    p.add_argument("--size", default="MEDIUM", choices=["SMALL", "MEDIUM", "LARGE"],
                   help="サムネイルサイズ（既定: MEDIUM = 800px 幅相当）")
    p.add_argument("--pages",
                   help="取得するページ番号。カンマ区切りと範囲が使える（例: 1,3,5 / 9-16 / 1,4-6）")
    args = p.parse_args()

    pres_id = _auth.presentation_id(args.source)
    slides, _ = _auth.services()
    pres = slides.presentations().get(
        presentationId=pres_id, fields="title,slides.objectId"
    ).execute()

    all_slides = pres.get("slides", [])
    wanted = None
    if args.pages:
        # "1,4-6,9" のような指定を受ける。QA を複数のエージェントで分担するとき、
        # 担当範囲を "17-24" のように渡せるほうが取り違えが起きにくい
        wanted = set()
        for part in args.pages.split(","):
            part = part.strip()
            if not part:
                continue
            if "-" in part:
                lo, hi = (int(v) for v in part.split("-", 1))
                if lo > hi:
                    raise SystemExit(f"--pages: 範囲が逆です: {part}")
                wanted.update(range(lo, hi + 1))
            else:
                wanted.add(int(part))

    os.makedirs(args.out, exist_ok=True)
    print(f"{pres.get('title')}: {len(all_slides)} slides")
    count = 0
    for i, s in enumerate(all_slides, 1):
        if wanted and i not in wanted:
            continue
        res = slides.presentations().pages().getThumbnail(
            presentationId=pres_id,
            pageObjectId=s["objectId"],
            thumbnailProperties_mimeType="PNG",
            thumbnailProperties_thumbnailSize=args.size,
        ).execute()
        path = os.path.join(args.out, f"slide-{i:02d}.png")
        urllib.request.urlretrieve(res["contentUrl"], path)
        print(f"  {path}")
        count += 1
    print(f"{count} thumbnails -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
