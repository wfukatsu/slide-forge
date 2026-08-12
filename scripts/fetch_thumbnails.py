#!/usr/bin/env python3
"""Fetches thumbnails of a generated presentation (for visual QA).

    python scripts/fetch_thumbnails.py <URL or ID> --out out/qa [--size LARGE]
    python scripts/fetch_thumbnails.py <URL> --out out/qa --pages 1,3,5

Open the fetched PNGs with the Read tool and eyeball them. Clipped text,
overflow, and overlap with decorations can't be told from the API response
alone, so don't skip this check.
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

# Each slide costs 2 round trips (getThumbnail + download), which measured
# about 1.0s sequentially. Firing requests concurrently would speed this up,
# but getThumbnail counts as an "expensive read" in the Slides API and
# carries a fixed quota of **60 requests per user per minute** (exceeding it
# returns HTTP 429 RATE_LIMIT_EXCEEDED). The ~1s/slide sequential rate was,
# in effect, already self-throttling right at this quota's edge.
#
# So parallelizing alone will always hit 429 on large decks. Throttle with
# our own 60-per-minute token bucket, then fire requests in parallel on top
# of it.
#   - 60 slides or fewer (most QA runs) … fetched in one burst. Measured: 31
#     slides went from 31s -> 7.3s
#   - more than 60 slides … the quota is the hard floor, capped at 60/min
WORKERS = 8
QUOTA_PER_MINUTE = 55        # margin below 60 so it won't overflow even under contention with other work
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
    """Sliding-window token bucket that throttles to N requests per minute."""

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
    creds = _auth.get_credentials()   # reused when building a per-worker service
    slides, _ = _auth.services(creds)
    pres = slides.presentations().get(
        presentationId=pres_id, fields="title,slides.objectId"
    ).execute()

    all_slides = pres.get("slides", [])
    wanted = None
    if args.pages:
        # Accepts a spec like "1,4-6,9". When splitting QA across multiple
        # agents, passing a range like "17-24" for each agent's slice reduces
        # mix-ups
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

    # googleapiclient's service reuses an httplib2 connection internally, so
    # it isn't thread-safe. Give each worker its own instance (credentials
    # can be shared)
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
                # A 429 beyond our own throttle means another run just before
                # this one used up the quota. Nothing to do but wait for the
                # window to clear
                wait = min(60.0, 5.0 * (2 ** attempt)) + random.uniform(0, 3)
                print(t("  warn: slide {n} hit the rate limit; retrying in "
                        "{wait:.0f}s ({attempt}/{attempts})", n=i, wait=wait,
                        attempt=attempt + 1, attempts=attempts - 1),
                      file=sys.stderr)
                time.sleep(wait)
        path = os.path.join(args.out, f"slide-{i:02d}.png")
        urllib.request.urlretrieve(res["contentUrl"], path)   # direct link, so it's outside the quota
        return path

    if len(targets) > QUOTA_PER_MINUTE:
        print(t("  {n} slides exceed the {quota}/min thumbnail quota; this will "
                "take about {minutes:.0f} min", n=len(targets),
                quota=QUOTA_PER_MINUTE,
                minutes=len(targets) / QUOTA_PER_MINUTE))

    with ThreadPoolExecutor(max_workers=min(WORKERS, len(targets) or 1)) as ex:
        # map returns results in input order, so the output stays in
        # page-number order
        paths = list(ex.map(fetch, targets))
    for path in paths:
        print(f"  {path}")
    print(f"{len(paths)} thumbnails -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
