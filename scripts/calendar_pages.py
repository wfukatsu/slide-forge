#!/usr/bin/env python3
"""Split calendar data into one-slide inputs for the calendar templates and render them.

    .venv/bin/python scripts/calendar_pages.py data.json --out out/cal/pages.json

data.json:

    {"template": "month-calendar" | "daily-gantt" | "daily-agenda",
     "title": "governing message",          # or "titles": [one per page]
     "source": "2026年9月1日時点の予定",
     "weekStart": "mon", "today": "2026-09-15",
     "extraHolidays": [["2026-12-29", "年末年始休業"]],
     "months": ["2026-09"],                  # month-calendar (optional)
     "start": "2026-09-14", "end": "2026-10-14",   # daily-gantt / daily-agenda
     "events": [...] | "rows": [...] | "items": [...]}

Pages:

- month-calendar — one page per month (from "months", else every month the
  events touch). Each page gets the events that overlap its visible weeks.
- daily-gantt — one period; rows beyond the template's 12 are split into
  pages at group boundaries, repeating the group heading as "（続き）".
  A period longer than 26 weeks is rejected (use planning/gantt-schedule).
- daily-agenda — one page per Monday–Sunday week, and a week that needs more
  than 11 rows is split between days.

Dates may be written 2026-09-03 or 2026/9/3; a date without a year is an
error, never a guess. With several pages and no "titles", the title gets a
"（1/3）" suffix — replace it with a real message per page when you can.
Output is a deck-spec fragment ({"slides": [...]}) for assemble_spec.py /
build_deck.py.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import calendars as cal  # noqa: E402
from _i18n import t, register  # noqa: E402
from slide_templates import load_template, render_template, validate_input  # noqa: E402

GANTT_MAX_ROWS = 12
AGENDA_MAX_ROWS = 11

register({
    "split calendar data into calendar-template slides":
        "カレンダーのデータをカレンダーテンプレートのスライドに分割する",
    "input data JSON": "入力データの JSON",
    "output spec fragment JSON": "出力するスペック断片の JSON",
    "unknown calendar template: {name}": "カレンダーテンプレートではありません: {name}",
    "'{key}' is required for {name}": "{name} には '{key}' が必要です",
    "month-calendar needs 'months' or at least one event":
        "month-calendar には 'months' か 1 件以上の予定が必要です",
    "the period is {n} weeks; daily-gantt holds {max}. Use planning/gantt-schedule "
    "for a month-level plan":
        "期間が {n} 週あります。daily-gantt は {max} 週までです。月単位の計画は "
        "planning/gantt-schedule を使ってください",
    "{day} has {n} items; one agenda page holds {max} rows":
        "{day} に {n} 件あります。日次リスト 1 枚は {max} 行までです",
    "'titles' has {given} entries but there are {pages} pages":
        "'titles' が {given} 件ですが、ページは {pages} 枚です",
    "page {i}: {problems}": "{i} ページ目: {problems}",
    "{n} slides -> {path}": "{n} 枚 -> {path}",
})


def _iso(value) -> str:
    return cal.parse_date(value).isoformat()


def _require(data: dict, key: str, name: str):
    if key not in data:
        raise ValueError(t("'{key}' is required for {name}", key=key, name=name))
    return data[key]


def _extra(data: dict) -> list:
    return [[_iso(d), str(n)] for d, n in data.get("extraHolidays", [])]


def month_pages(data: dict) -> list[dict]:
    week_start = data.get("weekStart", "mon")
    events = []
    for ev in data.get("events", []):
        s, e, title, cat, tm = cal.normalize_event(ev)
        events.append((s, e, title, cat, tm))
    if data.get("months"):
        months = [cal.parse_month(m) for m in data["months"]]
    elif events:
        lo = min(ev[0] for ev in events)
        hi = max(ev[1] or ev[0] for ev in events)
        months, cur = [], (lo.year, lo.month)
        while cur <= (hi.year, hi.month):
            months.append(cur)
            cur = (cur[0] + (cur[1] == 12), cur[1] % 12 + 1)
    else:
        raise ValueError(t("month-calendar needs 'months' or at least one event"))
    pages = []
    for year, month in months:
        weeks = cal.month_weeks(year, month, week_start)
        first, last = weeks[0][0], weeks[-1][-1]
        rows = [[s.isoformat(), e.isoformat() if e else "", title, cat, tm]
                for s, e, title, cat, tm in events if s <= last and (e or s) >= first]
        pages.append({"month": f"{year}-{month:02d}", "weekStart": week_start,
                      "events": rows, "extraHolidays": _extra(data)})
    return pages


def gantt_pages(data: dict) -> list[dict]:
    s = cal.parse_date(_require(data, "start", "daily-gantt"))
    e = cal.parse_date(_require(data, "end", "daily-gantt"))
    if cal.choose_scale(s, e) == "week":
        first = s - dt.timedelta(days=s.weekday())
        nweeks = (e - first).days // 7 + 1
        if nweeks > cal.MAX_WEEK_COLUMNS:
            raise ValueError(t("the period is {n} weeks; daily-gantt holds {max}. Use "
                               "planning/gantt-schedule for a month-level plan",
                               n=nweeks, max=cal.MAX_WEEK_COLUMNS))
    rows = []
    for row in _require(data, "rows", "daily-gantt"):
        kind, *rest = cal.normalize_gantt_row(row)
        if kind == "group":
            rows.append(["group", rest[0], "", "", "", 0])
        elif kind == "task":
            name, owner, ts, te, prog = rest
            rows.append(["task", name, owner, ts.isoformat(), te.isoformat(), prog])
        else:
            name, owner, day = rest
            rows.append(["milestone", name, owner, day.isoformat(), "", 0])
    chunks, current, group = [], [], None
    for row in rows:
        if row[0] == "group":
            group = row
        if len(current) >= GANTT_MAX_ROWS:
            chunks.append(current)
            current = []
            if row[0] != "group" and group is not None:
                current.append(["group", f"（続き）{group[1]}", "", "", "", 0])
        current.append(row)
    if current:
        chunks.append(current)
    base = {"start": s.isoformat(), "end": e.isoformat(),
            "today": _iso(data["today"]) if data.get("today") else "",
            "extraHolidays": _extra(data)}
    return [{**base, "rows": chunk} for chunk in chunks]


def agenda_pages(data: dict) -> list[dict]:
    s = cal.parse_date(_require(data, "start", "daily-agenda"))
    e = cal.parse_date(_require(data, "end", "daily-agenda"))
    extra = _extra(data)
    items = [[_iso(it[0]), *[str(v) for v in list(it[1:]) + [""] * (5 - len(it))]]
             for it in _require(data, "items", "daily-agenda")]
    hol = cal.holidays_for({d.year for d in cal.date_range(s, e)}, extra)
    pages = []
    week_start = s
    while week_start <= e:
        week_end = min(e, week_start + dt.timedelta(days=6 - week_start.weekday()))
        week_items = [it for it in items
                      if week_start.isoformat() <= it[0] <= week_end.isoformat()]
        if week_items:
            entries = cal.agenda_entries(week_start, week_end, week_items, hol)
            chunk, rows = [], 0
            for entry in entries:
                need = max(1, len(entry[2])) if entry[0] == "day" else 1
                if need > AGENDA_MAX_ROWS:
                    raise ValueError(t("{day} has {n} items; one agenda page holds {max} rows",
                                       day=entry[1], n=need, max=AGENDA_MAX_ROWS))
                if rows + need > AGENDA_MAX_ROWS:
                    pages.append(chunk)
                    chunk, rows = [], 0
                chunk.append(entry)
                rows += need
            if chunk:
                pages.append(chunk)
        week_start = week_end + dt.timedelta(days=1)
    out = []
    for chunk in pages:
        # Leading / trailing runs of days off say nothing on their own page
        while chunk and chunk[0][0] == "off":
            chunk = chunk[1:]
        while chunk and chunk[-1][0] == "off":
            chunk = chunk[:-1]
        first, last = chunk[0][1], chunk[-1][1]
        page_items = [it for it in items if first.isoformat() <= it[0] <= last.isoformat()]
        out.append({"start": first.isoformat(), "end": last.isoformat(),
                    "items": page_items,
                    "today": _iso(data["today"]) if data.get("today") else "",
                    "extraHolidays": extra})
    return out


SPLITTERS = {"month-calendar": month_pages, "daily-gantt": gantt_pages,
             "daily-agenda": agenda_pages}


def build_slides(data: dict) -> list[dict]:
    name = data.get("template")
    if name not in SPLITTERS:
        raise ValueError(t("unknown calendar template: {name}", name=name))
    pages = SPLITTERS[name](data)
    titles = data.get("titles")
    if titles is not None and len(titles) != len(pages):
        raise ValueError(t("'titles' has {given} entries but there are {pages} pages",
                           given=len(titles), pages=len(pages)))
    template, _ = load_template(name)
    slides = []
    for i, page in enumerate(pages, 1):
        if titles is not None:
            title = titles[i - 1]
        else:
            title = _require(data, "title", name)
            if len(pages) > 1:
                title = f"{title}（{i}/{len(pages)}）"
        values = {"title": title, "source": _require(data, "source", name), **page}
        problems = validate_input(template, values)
        if problems:
            raise ValueError(t("page {i}: {problems}", i=i, problems="; ".join(problems)))
        slides.append(render_template(template, values))
    return slides


def main() -> int:
    ap = argparse.ArgumentParser(description=t("split calendar data into calendar-template slides"))
    ap.add_argument("data", help=t("input data JSON"))
    ap.add_argument("--out", required=True, help=t("output spec fragment JSON"))
    args = ap.parse_args()
    data = json.loads(Path(args.data).read_text(encoding="utf-8"))
    try:
        slides = build_slides(data)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"slides": slides}, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    print(t("{n} slides -> {path}", n=len(slides), path=out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
