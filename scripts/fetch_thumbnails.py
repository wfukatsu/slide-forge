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
import random
import sys
import threading
import time
import urllib.request
from collections import deque
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _auth  # noqa: E402
from _i18n import t, register  # noqa: E402

# 1 枚あたり getThumbnail + ダウンロードで 2 往復かかり、逐次だと実測で約 1.0 秒。
# 同時に投げれば速くなるが、getThumbnail は Slides API の「expensive read」に
# 当たり、**ユーザーあたり毎分 60 件**という固定クォータがある
# （超えると HTTP 429 RATE_LIMIT_EXCEEDED）。逐次実行が約 1 秒/枚なのは、
# 事実上このクォータぎりぎりで自然に律速されていたということ。
#
# したがって並列化だけでは大きなデッキで必ず 429 に当たる。毎分 60 件の
# トークンバケットで自前に絞った上で並列に投げる。
#   - 60 枚以下（QA の大半）… 一気に取れる。実測 31 枚が 31s -> 7.3s
#   - 60 枚超            … クォータが下限なので 1 分あたり 60 枚で頭打ち
WORKERS = 8
QUOTA_PER_MINUTE = 55        # 60 に対し、他の処理と競合しても溢れない程度の余裕
QUOTA_WINDOW = 60.0

register({
    "Fetch slide thumbnails": "スライドのサムネイルを取得する",
    "presentation URL or ID": "プレゼンテーションの URL または ID",
    "output directory": "出力ディレクトリ",
    "thumbnail size (default: MEDIUM, ~800px wide)":
        "サムネイルサイズ（既定: MEDIUM = 800px 幅相当）",
    "page numbers to fetch; commas and ranges allowed (e.g. 1,3,5 / 9-16 / 1,4-6)":
        "取得するページ番号。カンマ区切りと範囲が使える（例: 1,3,5 / 9-16 / 1,4-6）",
    "--pages: range is reversed: {part}": "--pages: 範囲が逆です: {part}",
    "  {n} slides exceed the {quota}/min thumbnail quota; this will take about "
    "{minutes:.0f} min":
        "  {n} 枚は毎分 {quota} 件のサムネイル取得クォータを超えるため、"
        "約 {minutes:.0f} 分かかります",
    "  warn: slide {n} hit the rate limit; retrying in {wait:.0f}s "
    "({attempt}/{attempts})":
        "  warn: {n} 枚目がレート制限に当たりました。{wait:.0f} 秒後に再試行 "
        "({attempt}/{attempts})",
})


class _RateLimiter:
    """毎分 N 件までに絞るスライディングウィンドウのトークンバケット。"""

    def __init__(self, per_window: int, window: float):
        self.per_window = per_window
        self.window = window
        self._hits: deque[float] = deque()
        self._lock = threading.Lock()

    def acquire(self) -> None:
        while True:
            with self._lock:
                now = time.monotonic()
                while self._hits and now - self._hits[0] >= self.window:
                    self._hits.popleft()
                if len(self._hits) < self.per_window:
                    self._hits.append(now)
                    return
                wait = self.window - (now - self._hits[0])
            time.sleep(max(wait, 0.05))


def main() -> int:
    p = argparse.ArgumentParser(description=t("Fetch slide thumbnails"))
    p.add_argument("source", help=t("presentation URL or ID"))
    p.add_argument("--out", required=True, help=t("output directory"))
    p.add_argument("--size", default="MEDIUM", choices=["SMALL", "MEDIUM", "LARGE"],
                   help=t("thumbnail size (default: MEDIUM, ~800px wide)"))
    p.add_argument("--pages",
                   help=t("page numbers to fetch; commas and ranges allowed "
                          "(e.g. 1,3,5 / 9-16 / 1,4-6)"))
    args = p.parse_args()

    pres_id = _auth.presentation_id(args.source)
    creds = _auth.get_credentials()   # ワーカーごとのサービス生成で使い回す
    slides, _ = _auth.services(creds)
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
                    raise SystemExit(t("--pages: range is reversed: {part}", part=part))
                wanted.update(range(lo, hi + 1))
            else:
                wanted.add(int(part))

    os.makedirs(args.out, exist_ok=True)
    print(f"{pres.get('title')}: {len(all_slides)} slides")

    targets = [(i, s["objectId"]) for i, s in enumerate(all_slides, 1)
               if not wanted or i in wanted]

    # googleapiclient のサービスは httplib2 の接続を内部で使い回すのでスレッド安全でない。
    # ワーカーごとに 1 つ持たせる（認証情報は使い回してよい）
    local = threading.local()

    def service():
        if not hasattr(local, "slides"):
            local.slides = _auth.services(creds)[0]
        return local.slides

    limiter = _RateLimiter(QUOTA_PER_MINUTE, QUOTA_WINDOW)

    def fetch(target, attempts: int = 5):
        from googleapiclient.errors import HttpError
        i, page_id = target
        for attempt in range(attempts):
            limiter.acquire()
            try:
                res = service().presentations().pages().getThumbnail(
                    presentationId=pres_id,
                    pageObjectId=page_id,
                    thumbnailProperties_mimeType="PNG",
                    thumbnailProperties_thumbnailSize=args.size,
                ).execute()
                break
            except (HttpError, OSError) as e:
                code = getattr(getattr(e, "resp", None), "status", None)
                retryable = isinstance(e, OSError) or code in (429, 500, 502, 503, 504)
                if not retryable or attempt == attempts - 1:
                    raise
                # 自前の絞りを超えて 429 が来るのは、直前の別実行がクォータを
                # 使っている場合。ウィンドウが空くまで待つしかない
                wait = min(60.0, 5.0 * (2 ** attempt)) + random.uniform(0, 3)
                print(t("  warn: slide {n} hit the rate limit; retrying in "
                        "{wait:.0f}s ({attempt}/{attempts})", n=i, wait=wait,
                        attempt=attempt + 1, attempts=attempts - 1),
                      file=sys.stderr)
                time.sleep(wait)
        path = os.path.join(args.out, f"slide-{i:02d}.png")
        urllib.request.urlretrieve(res["contentUrl"], path)   # 直リンクなのでクォータ外
        return path

    if len(targets) > QUOTA_PER_MINUTE:
        print(t("  {n} slides exceed the {quota}/min thumbnail quota; this will "
                "take about {minutes:.0f} min", n=len(targets),
                quota=QUOTA_PER_MINUTE,
                minutes=len(targets) / QUOTA_PER_MINUTE))

    with ThreadPoolExecutor(max_workers=min(WORKERS, len(targets) or 1)) as ex:
        # map は入力順に結果を返すので、出力はページ番号順のまま
        paths = list(ex.map(fetch, targets))
    for path in paths:
        print(f"  {path}")
    print(f"{len(paths)} thumbnails -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
