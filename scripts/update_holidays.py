#!/usr/bin/env python3
"""Refresh the bundled Japanese national-holiday data from the Cabinet Office CSV.

    .venv/bin/python scripts/update_holidays.py            # download and rewrite
    .venv/bin/python scripts/update_holidays.py --check    # exit 1 when out of date
    .venv/bin/python scripts/update_holidays.py --from-file syukujitsu.csv

The source is 内閣府「国民の祝日」について (CC BY 4.0 compatible terms). The
Shift_JIS CSV with dates like 2026/9/21 is rewritten as UTF-8 with ISO dates
(`date,name`) to assets/holidays/jp.csv, which scripts/calendars.py reads.
The Cabinet Office publishes the next year's equinox days each February, so
run this once a year (or when calendars.py warns about an uncovered year).
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _i18n import t, register  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "holidays" / "jp.csv"
URL = "https://www8.cao.go.jp/chosei/shukujitsu/syukujitsu.csv"

register({
    "refresh the bundled Japanese holiday CSV": "同梱の日本の祝日 CSV を更新する",
    "only compare; exit 1 when the bundled file differs":
        "比較だけ行い、同梱ファイルと差があれば終了コード 1",
    "read a downloaded CSV instead of fetching": "取得せず、ダウンロード済みの CSV を読む",
    "up to date: {n} holidays ({lo}-{hi})": "最新です: 祝日 {n} 件（{lo}〜{hi} 年）",
    "out of date: bundled {old} holidays, source {new}":
        "更新があります: 同梱 {old} 件、配布元 {new} 件",
    "wrote {path}: {n} holidays ({lo}-{hi})": "{path} に書き出しました: 祝日 {n} 件（{lo}〜{hi} 年）",
})


def convert(raw: bytes) -> list[tuple[str, str]]:
    text = raw.decode("cp932")
    rows = []
    for line in text.splitlines()[1:]:
        if not line.strip():
            continue
        date_s, name = line.split(",", 1)
        y, m, d = (int(p) for p in date_s.split("/"))
        rows.append((dt.date(y, m, d).isoformat(), name.strip()))
    return sorted(rows)


def render(rows: list[tuple[str, str]]) -> str:
    return "date,name\n" + "".join(f"{d},{n}\n" for d, n in rows)


def main() -> int:
    ap = argparse.ArgumentParser(description=t("refresh the bundled Japanese holiday CSV"))
    ap.add_argument("--check", action="store_true",
                    help=t("only compare; exit 1 when the bundled file differs"))
    ap.add_argument("--from-file", help=t("read a downloaded CSV instead of fetching"))
    args = ap.parse_args()

    if args.from_file:
        raw = Path(args.from_file).read_bytes()
    else:
        with urllib.request.urlopen(URL, timeout=30) as res:
            raw = res.read()
    rows = convert(raw)
    body = render(rows)
    lo, hi = rows[0][0][:4], rows[-1][0][:4]
    current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
    if args.check:
        if current == body:
            print(t("up to date: {n} holidays ({lo}-{hi})", n=len(rows), lo=lo, hi=hi))
            return 0
        print(t("out of date: bundled {old} holidays, source {new}",
                old=max(current.count("\n") - 1, 0), new=len(rows)))
        return 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(body, encoding="utf-8")
    print(t("wrote {path}: {n} holidays ({lo}-{hi})", path=OUT.relative_to(ROOT),
            n=len(rows), lo=lo, hi=hi))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
