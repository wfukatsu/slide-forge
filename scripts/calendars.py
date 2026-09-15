#!/usr/bin/env python3
"""Calendar diagrams (a mixin used together with `diagrams.Canvas`) and the
date engine behind them.

Three layouts, each driven by ISO dates rather than pre-computed coordinates:

    d = Canvas(deck, slide_id, template)
    d.month_calendar(0.5, 1.05, 9.0, 3.65, "2026-09", [
        ["2026-09-14", "2026-09-18", "データ移行検証", "primary", ""],
        ["2026-09-18", "", "判定会議", "danger", "15:00"],
    ], week_start="mon")
    d.day_gantt(0.5, 1.05, 9.0, 3.65, "2026-09-14", "2026-10-14", [
        ["group", "準備フェーズ", "", "", "", 0],
        ["task", "要件確定", "PM", "2026-09-14", "2026-09-18", 1.0],
        ["milestone", "判定会議", "PM", "2026-10-08", "", 0],
    ], today="2026-09-15")
    d.day_agenda(0.5, 1.05, 9.0, 3.65, "2026-09-14", "2026-09-25", [
        ["2026-09-14", "要件定義書のレビュー", "PM", "17:00", "完了"],
    ], today="2026-09-15")

Weekday and holiday handling is shared by all three: Saturday is blue, Sunday
and holidays are red. The colour goes on the date number; the cell or column
gets a light fill. National holidays come from the Cabinet Office CSV bundled
at assets/holidays/jp.csv (refresh it with scripts/update_holidays.py).
Company closures are passed as `extra_holidays`. A year outside the bundled
data prints a warning instead of being guessed.

Every diagram returns the bottom y of the drawn area, like the other parts.
Splitting a period across several slides is not done here — see
scripts/calendar_pages.py, which uses the same engine so its page breaks match
what the diagrams can hold.
"""
from __future__ import annotations

import calendar as _calendar
import csv
import datetime as dt
import sys
from functools import lru_cache
from pathlib import Path

from colors import darken, lighten, readable_on
from _i18n import t, register
from _text import em, fit_em

ROOT = Path(__file__).resolve().parents[1]
HOLIDAY_CSV = ROOT / "assets" / "holidays" / "jp.csv"
WEEKDAYS_JA = "月火水木金土日"

# Period limits of day_gantt. Up to 31 days every column is labelled; up to
# MAX_DAY_COLUMNS only Mondays are; beyond that the columns become weeks.
FULL_LABEL_DAYS = 31
MAX_DAY_COLUMNS = 60
MAX_WEEK_COLUMNS = 26
MIN_GANTT_ROW_H = 0.24
MIN_AGENDA_ROW_H = 0.24

register({
    "not a date: {value}": "日付として読めません: {value}",
    "a date needs a four-digit year (YYYY-MM-DD): {value}":
        "日付には 4 桁の年が必要です（YYYY-MM-DD）: {value}",
    "not a month (YYYY-MM): {value}": "月として読めません（YYYY-MM）: {value}",
    "week_start must be 'mon' or 'sun': {value}":
        "week_start は 'mon' か 'sun' です: {value}",
    "warning: holidays for {year} are not in the bundled data ({lo}-{hi}); "
    "only weekends are treated as days off. Refresh with "
    "scripts/update_holidays.py or pass extra_holidays":
        "警告: {year} 年の祝日は同梱データ（{lo}〜{hi} 年）にありません。"
        "土日だけを休日として扱います。scripts/update_holidays.py で更新するか、"
        "extra_holidays で渡してください",
    "extra_holidays entry must be [date, name] or [start, end, name]: {value}":
        "extra_holidays の要素は [日付, 名前] か [開始, 終了, 名前] です: {value}",
    "event must be [start, end, title, category, time]: {value}":
        "予定は [開始, 終了, 件名, 分類, 時刻] の形式です: {value}",
    "'{title}': the end ({end}) is before the start ({start})":
        "「{title}」: 終了（{end}）が開始（{start}）より前です",
    "unknown category '{cat}' (use primary / success / danger / info / warning / muted)":
        "分類 '{cat}' は使えません（primary / success / danger / info / warning / muted）",
    "month_calendar: h={h} is too short for {n} week rows (needs {need:.2f}in)":
        "month_calendar: h={h} では {n} 週分の行が入りません（{need:.2f}in 必要）",
    "day_gantt: {n} days is too long for day columns (max {max}); use scale='week'":
        "day_gantt: {n} 日は日単位の列に収まりません（最大 {max} 日）。scale='week' にしてください",
    "day_gantt: {n} weeks is too long (max {max}). Split the period or use the "
    "month-level gantt":
        "day_gantt: {n} 週は長すぎます（最大 {max} 週）。期間を分けるか、月単位の gantt を使ってください",
    "scale must be 'auto', 'day' or 'week': {value}":
        "scale は 'auto' / 'day' / 'week' のいずれかです: {value}",
    "gantt row kind must be group / task / milestone: {value}":
        "ガントの行の種類は group / task / milestone のいずれかです: {value}",
    "'{name}': progress must be between 0 and 1: {value}":
        "「{name}」: 進捗は 0〜1 で指定します: {value}",
    "'{name}': {day} is outside the chart period {start}-{end}":
        "「{name}」: {day} は表示期間 {start}〜{end} の外です",
    "{what}: {n} rows do not fit in h={h} (each row needs {min}in). Split the "
    "period with scripts/calendar_pages.py":
        "{what}: {n} 行は h={h} に収まりません（1 行 {min}in 必要）。"
        "scripts/calendar_pages.py で期間を分割してください",
    "the end ({end}) is before the start ({start})":
        "終了（{end}）が開始（{start}）より前です",
    "unknown status '{status}' (use {allowed})":
        "状態 '{status}' は使えません（{allowed}）",
    "day_agenda: needs at least one item":
        "day_agenda: 項目が 1 件以上必要です",
    "day_gantt: needs at least one row": "day_gantt: 行が 1 件以上必要です",
})


# ---------------------------------------------------------------------------
# Date engine (pure functions; no drawing)
# ---------------------------------------------------------------------------

def parse_date(value) -> dt.date:
    """Accept a date, 'YYYY-MM-DD' or 'YYYY/M/D'. A date without a year is rejected."""
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    if not isinstance(value, str) or not value.strip():
        raise ValueError(t("not a date: {value}", value=value))
    parts = value.strip().replace("/", "-").replace(".", "-").split("-")
    if len(parts) != 3 or len(parts[0]) != 4:
        raise ValueError(t("a date needs a four-digit year (YYYY-MM-DD): {value}",
                           value=value))
    try:
        return dt.date(int(parts[0]), int(parts[1]), int(parts[2]))
    except ValueError:
        raise ValueError(t("not a date: {value}", value=value)) from None


def parse_month(value) -> tuple[int, int]:
    """'2026-09' / '2026/9' -> (2026, 9)."""
    parts = str(value).strip().replace("/", "-").split("-")
    try:
        year, month = int(parts[0]), int(parts[1])
        if len(parts) != 2 or len(parts[0]) != 4 or not 1 <= month <= 12:
            raise ValueError
    except (ValueError, IndexError):
        raise ValueError(t("not a month (YYYY-MM): {value}", value=value)) from None
    return year, month


def date_range(start: dt.date, end: dt.date) -> list[dt.date]:
    return [start + dt.timedelta(days=i) for i in range((end - start).days + 1)]


def md(day: dt.date) -> str:
    """'9/14（月）'."""
    return f"{day.month}/{day.day}（{WEEKDAYS_JA[day.weekday()]}）"


@lru_cache(maxsize=1)
def bundled_holidays() -> dict[dt.date, str]:
    """National holidays from the bundled Cabinet Office CSV."""
    out: dict[dt.date, str] = {}
    with HOLIDAY_CSV.open(encoding="utf-8") as f:
        rows = csv.reader(f)
        next(rows, None)
        for date_s, name in rows:
            out[dt.date.fromisoformat(date_s)] = name
    return out


def holiday_coverage() -> tuple[int, int]:
    years = [d.year for d in bundled_holidays()]
    return min(years), max(years)


_WARNED: set[int] = set()


def normalize_extra(extra) -> dict[dt.date, str]:
    """extra_holidays as [[date, name], ...] or [[start, end, name], ...]."""
    out: dict[dt.date, str] = {}
    for entry in extra or []:
        if not isinstance(entry, (list, tuple)) or len(entry) not in (2, 3):
            raise ValueError(t("extra_holidays entry must be [date, name] or "
                               "[start, end, name]: {value}", value=entry))
        if len(entry) == 2:
            out[parse_date(entry[0])] = str(entry[1])
        else:
            for day in date_range(parse_date(entry[0]), parse_date(entry[1])):
                out[day] = str(entry[2])
    return out


def holidays_for(years, extra=None) -> dict[dt.date, str]:
    """Bundled holidays plus company closures. Warns once per uncovered year."""
    lo, hi = holiday_coverage()
    for year in sorted(set(years)):
        if not lo <= year <= hi and year not in _WARNED:
            _WARNED.add(year)
            print(t("warning: holidays for {year} are not in the bundled data "
                    "({lo}-{hi}); only weekends are treated as days off. Refresh "
                    "with scripts/update_holidays.py or pass extra_holidays",
                    year=year, lo=lo, hi=hi), file=sys.stderr)
    merged = dict(bundled_holidays())
    merged.update(normalize_extra(extra))
    return merged


def is_offday(day: dt.date, holidays: dict, workdays=(0, 1, 2, 3, 4)) -> bool:
    return day.weekday() not in workdays or day in holidays


def is_red(day: dt.date, holidays: dict) -> bool:
    """Sunday or a holiday (the red date convention)."""
    return day.weekday() == 6 or day in holidays


def business_days(start: dt.date, end: dt.date, holidays: dict,
                  workdays=(0, 1, 2, 3, 4)) -> int:
    """Working days in [start, end], both ends included."""
    return sum(1 for d in date_range(start, end) if not is_offday(d, holidays, workdays))


def month_weeks(year: int, month: int, week_start: str = "mon") -> list[list[dt.date]]:
    """The month as week rows of 7 dates (4 to 6 rows), including adjacent-month days."""
    if week_start not in ("mon", "sun"):
        raise ValueError(t("week_start must be 'mon' or 'sun': {value}", value=week_start))
    first = 0 if week_start == "mon" else 6
    return _calendar.Calendar(first).monthdatescalendar(year, month)


def iso_week_label(day: dt.date, *, with_year: bool = True) -> str:
    """'2026-W53' (the ISO year can differ from the calendar year near New Year)."""
    year, week, _ = day.isocalendar()
    return f"{year}-W{week:02d}" if with_year else f"W{week}"


def fiscal_quarter(day: dt.date, start_month: int = 4) -> tuple[int, int]:
    """(fiscal year, quarter). The fiscal year is named after the year it starts in."""
    fy = day.year if day.month >= start_month else day.year - 1
    return fy, (day.month - start_month) % 12 // 3 + 1


def choose_scale(start: dt.date, end: dt.date) -> str:
    """'day' up to MAX_DAY_COLUMNS days, 'week' beyond."""
    return "day" if (end - start).days + 1 <= MAX_DAY_COLUMNS else "week"


def pack_lanes(spans, nlanes: int):
    """Assign each span (c0, c1, payload) the lowest lane free over its columns.

    Spans are placed longest-first within the same start column. Returns
    (placed, overflow): placed is [(lane, span)], overflow is spans with no
    free lane.
    """
    occupied: dict[int, set[int]] = {}
    placed, overflow = [], []
    for span in sorted(spans, key=lambda s: (s[0], -(s[1] - s[0]))):
        c0, c1 = span[0], span[1]
        lane = next((l for l in range(nlanes)
                     if all(l not in occupied.get(c, set()) for c in range(c0, c1 + 1))),
                    None)
        if lane is None:
            overflow.append(span)
            continue
        for c in range(c0, c1 + 1):
            occupied.setdefault(c, set()).add(lane)
        placed.append((lane, span))
    return placed, overflow


def normalize_event(entry) -> tuple:
    """[start, end, title, category, time] -> (start, end|None, title, category, time)."""
    if not isinstance(entry, (list, tuple)) or not 1 <= len(entry) <= 5:
        raise ValueError(t("event must be [start, end, title, category, time]: {value}",
                           value=entry))
    row = list(entry) + [""] * (5 - len(entry))
    start = parse_date(row[0])
    end = parse_date(row[1]) if row[1] else None
    title = str(row[2])
    if end is not None and end < start:
        raise ValueError(t("'{title}': the end ({end}) is before the start ({start})",
                           title=title, end=end, start=start))
    if end == start:
        end = None
    return start, end, title, str(row[3] or ""), str(row[4] or "")


def normalize_gantt_row(row) -> tuple:
    """-> ("group", name) / ("task", name, owner, start, end, progress) / ("milestone", name, owner, date)."""
    if not isinstance(row, (list, tuple)) or not row:
        raise ValueError(t("gantt row kind must be group / task / milestone: {value}",
                           value=row))
    kind = row[0]
    cells = list(row) + [""] * (6 - len(row))
    name, owner = str(cells[1]), str(cells[2] or "")
    if kind == "group":
        return ("group", name)
    if kind == "task":
        start, end = parse_date(cells[3]), parse_date(cells[4])
        if end < start:
            raise ValueError(t("'{title}': the end ({end}) is before the start ({start})",
                               title=name, end=end, start=start))
        prog = cells[5] if cells[5] not in ("", None) else 0
        if not isinstance(prog, (int, float)) or not 0 <= prog <= 1:
            raise ValueError(t("'{name}': progress must be between 0 and 1: {value}",
                               name=name, value=prog))
        return ("task", name, owner, start, end, float(prog))
    if kind == "milestone":
        return ("milestone", name, owner, parse_date(cells[3]))
    raise ValueError(t("gantt row kind must be group / task / milestone: {value}",
                       value=kind))


def agenda_entries(start, end, items, holidays: dict, *,
                   show_empty_days: bool = False) -> list[tuple]:
    """Group agenda items by day and collapse runs of empty days off.

    Returns ("day", date, [(task, owner, due, status), ...]),
    ("off", first, last) for a run of days off with nothing scheduled, and
    ("empty", date, []) for an empty working day when show_empty_days is set.
    """
    s, e = parse_date(start), parse_date(end)
    if e < s:
        raise ValueError(t("the end ({end}) is before the start ({start})", end=e, start=s))
    by_day: dict[dt.date, list] = {}
    for item in items:
        row = list(item) + [""] * (5 - len(item))
        day = parse_date(row[0])
        if not s <= day <= e:
            raise ValueError(t("'{name}': {day} is outside the chart period {start}-{end}",
                               name=row[1], day=day, start=s, end=e))
        by_day.setdefault(day, []).append(tuple(str(v) for v in row[1:5]))
    out: list[tuple] = []
    run: list[dt.date] = []

    def flush():
        if run:
            out.append(("off", run[0], run[-1]))
            run.clear()

    for day in date_range(s, e):
        if day in by_day:
            flush()
            out.append(("day", day, by_day[day]))
        elif is_offday(day, holidays):
            run.append(day)
        else:
            flush()
            if show_empty_days:
                out.append(("empty", day, []))
    flush()
    return out


def agenda_rows(entries) -> int:
    return sum(max(1, len(e[2])) if e[0] == "day" else 1 for e in entries)


# Status label -> palette role. Japanese and English labels are both accepted.
_STATUS = {
    "完了": "success", "done": "success",
    "進行中": "primary", "doing": "primary",
    "予定": "todo", "todo": "todo",
    "遅延": "danger", "late": "danger",
    "中止": "muted", "cancelled": "muted",
}


# ---------------------------------------------------------------------------
# Drawing
# ---------------------------------------------------------------------------

class CalendarMixin:
    """Mixin that adds calendar diagrams to `Canvas`."""

    # ---- shared helpers ----

    def _cal_text(self, x, y, w, h, text, *, size=9, color=None, bold=False,
                  align="START", valign="MIDDLE", margin=0.02):
        return self.shape(x, y, w, h, kind="TEXT_BOX", text=text, size=size,
                          color=color or self.P.text, bold=bold, align=align,
                          valign=valign, text_margin=margin)

    @staticmethod
    def _cal_fit(text, w, size, margin=0.1):
        return fit_em(text, max((w - 2 * margin) * 72 / size * 0.95, 1))

    def _cal_num_color(self, day, holidays):
        if is_red(day, holidays):
            return darken(self.P.danger, 0.12)
        if day.weekday() == 5:
            return darken(self.P.info, 0.18)
        return self.P.text

    def _cal_off_fill(self, day, holidays):
        if is_red(day, holidays):
            return lighten(self.P.danger, 0.90)
        if day.weekday() == 5:
            return lighten(self.P.info, 0.90)
        return None

    def _cal_color(self, category, *, bar=False):
        P = self.P
        chips = {"": P.primary, "primary": P.primary, "success": P.success,
                 "danger": P.danger, "info": P.info,
                 "warning": darken(P.warning, 0.30), "muted": P.muted}
        if category not in chips:
            raise ValueError(t("unknown category '{cat}' (use primary / success / "
                               "danger / info / warning / muted)", cat=category))
        if not bar:
            return chips[category]
        bars = {"": lighten(P.primary, 0.25), "primary": lighten(P.primary, 0.25),
                "success": darken(P.success, 0.25), "danger": P.danger,
                "info": darken(P.info, 0.10), "warning": darken(P.warning, 0.35),
                "muted": P.muted}
        return bars[category]

    def _cal_weekday_color(self, wd):
        if wd == 6:
            return darken(self.P.danger, 0.12)
        if wd == 5:
            return darken(self.P.info, 0.18)
        return self.P.text

    # ---- A. month calendar ----

    def month_calendar(self, x, y, w, h, month, events, *, week_start="mon",
                       week_numbers=None, extra_holidays=None, size=8.5) -> float:
        """Month grid with one week per row. Returns the bottom y.

        events are [start, end, title, category, time]. An empty end is a
        one-day event written in the day cell ("10:00 定例"); an end after the
        start is drawn as a bar across the days, split at each week row and
        marked "（続き）" where it continues. Bars take lanes first; one-day
        events fill the remaining lanes, and whatever does not fit becomes
        "+N件". A title too long for the cell drops its time first, then is
        cut with "…".

        week_numbers defaults to True for Monday-start (ISO weeks) and False
        for Sunday-start, where ISO numbering would not line up with the rows.
        """
        P = self.P
        year, mon = parse_month(month)
        weeks = month_weeks(year, mon, week_start)
        if week_numbers is None:
            week_numbers = week_start == "mon"
        evs = [normalize_event(e) for e in events]
        for ev in evs:
            self._cal_color(ev[3])
        hol = holidays_for({d.year for wk in weeks for d in wk}, extra_holidays)

        head_h, date_h, lane_h = 0.26, 0.23, 0.19
        rh = (h - head_h) / len(weeks)
        nl = int((rh - date_h - 0.02) / lane_h)
        if nl < 1:
            raise ValueError(t("month_calendar: h={h} is too short for {n} week rows "
                               "(needs {need:.2f}in)", h=h, n=len(weeks),
                               need=head_h + len(weeks) * (date_h + lane_h + 0.02)))
        order = list(range(7)) if week_start == "mon" else [6, 0, 1, 2, 3, 4, 5]
        wn_w = 0.40 if week_numbers else 0.0
        gx, cw = x + wn_w, (w - wn_w) / 7
        hdr = lighten(P.primary, 0.86)

        if week_numbers:
            self.shape(x, y, wn_w, head_h, fill=hdr, stroke=P.white, text="週",
                       size=8, color=P.muted, text_margin=0.0)
        for c, wd in enumerate(order):
            self.shape(gx + c * cw, y, cw, head_h, fill=hdr, stroke=P.white,
                       text=WEEKDAYS_JA[wd], size=9, bold=True,
                       color=self._cal_weekday_color(wd))

        for r, week in enumerate(weeks):
            ry = y + head_h + r * rh
            if week_numbers:
                monday = week[0] if week_start == "mon" else week[1]
                self.shape(x, ry, wn_w, rh, fill=P.surfaceAlt, stroke=P.white,
                           text=iso_week_label(monday, with_year=False), size=8,
                           color=P.muted, valign="TOP", text_margin=0.02)
            for c, day in enumerate(week):
                fill = ((self._cal_off_fill(day, hol) or P.white)
                        if day.month == mon else "#F1F2F4")
                self.shape(gx + c * cw, ry, cw, rh, fill=fill, stroke=P.border,
                           stroke_weight=0.75)

            spans = []
            for s, e, title, cat, _tm in evs:
                if e is None:
                    continue
                a, b = max(s, week[0]), min(e, week[6])
                if a <= b:
                    spans.append((week.index(a), week.index(b), (title, cat, a == s, b == e)))
            placed, overflow = pack_lanes(spans, nl)
            occupied = [set() for _ in range(7)]
            more = [0] * 7
            for lane, (c0, c1, _p) in placed:
                for c in range(c0, c1 + 1):
                    occupied[c].add(lane)
            for c0, c1, _p in overflow:
                for c in range(c0, c1 + 1):
                    more[c] += 1
            for lane, (c0, c1, (title, cat, head, tail)) in placed:
                bx = gx + c0 * cw + (0.04 if head else 0.0)
                bw = (c1 - c0 + 1) * cw - (0.04 if head else 0.0) - (0.04 if tail else 0.0)
                label = title if head else f"（続き）{title}"
                fill = self._cal_color(cat, bar=True)
                self.shape(bx, ry + date_h + lane * lane_h + 0.015, bw, lane_h - 0.03,
                           kind="ROUND_RECTANGLE" if (head and tail) else "RECTANGLE",
                           fill=fill, text=self._cal_fit(label, bw, size, 0.05),
                           size=size, color=readable_on(fill), align="START",
                           text_margin=0.05)

            for c, day in enumerate(week):
                cx = gx + c * cw
                adjacent = day.month != mon
                first = day.day == 1 or (r == 0 and c == 0)
                self._cal_text(cx + 0.02, ry + 0.01, 0.46, date_h,
                               f"{day.month}/{day.day}" if first else str(day.day),
                               size=9, bold=True, margin=0.04,
                               color=P.muted if adjacent else self._cal_num_color(day, hol))
                singles = [ev for ev in evs if ev[1] is None and ev[0] == day]
                free = [l for l in range(nl) if l not in occupied[c]]
                extra = more[c]
                if len(singles) + extra > len(free):
                    shown = singles[:max(len(free) - 1, 0)]
                    extra += len(singles) - len(shown)
                else:
                    shown = singles
                for lane, (_s, _e, title, cat, tm) in zip(free, shown):
                    ly = ry + date_h + lane * lane_h
                    self.shape(cx + 0.06, ly + 0.045, 0.05, lane_h - 0.09,
                               fill=self._cal_color(cat))
                    text = f"{tm} {title}" if tm else title
                    if em(text) > (cw - 0.19) * 72 / size * 0.95:
                        text = title
                    self._cal_text(cx + 0.13, ly, cw - 0.15, lane_h,
                                   self._cal_fit(text, cw - 0.15, size, 0.02),
                                   size=size, color=P.muted if adjacent else P.text)
                corner = None if adjacent else hol.get(day)
                if extra:
                    if len(free) > len(shown):
                        ly = ry + date_h + free[len(shown)] * lane_h
                        self._cal_text(cx + 0.06, ly, cw - 0.1, lane_h, f"+{extra}件",
                                       size=size, bold=True, color=P.primaryDark)
                    else:
                        corner = f"+{extra}件"
                if corner:
                    self._cal_text(cx + 0.42, ry + 0.01, cw - 0.46, date_h,
                                   self._cal_fit(corner, cw - 0.46, 8, 0.02), size=8,
                                   align="END",
                                   color=(P.primaryDark if corner.startswith("+")
                                          else darken(P.danger, 0.12)))
        return y + h

    # ---- B. day gantt ----

    def day_gantt(self, x, y, w, h, start, end, rows, *, today=None, scale="auto",
                  label_w=1.8, extra_holidays=None, size=9) -> float:
        """Gantt chart over a date range. Returns the bottom y.

        rows are ["group", name], ["task", name, owner, start, end, progress]
        or ["milestone", name, owner, date]. Template tuples may pad the
        unused cells with "" / 0.

        scale="auto" uses one column per day up to 60 days (every day labelled
        up to 31, Mondays only beyond) and one column per ISO week up to 26
        weeks. Days off are shaded behind the bars; the caption to the right of
        a bar is its working-day count (and weeks, on the week scale).
        """
        P = self.P
        s, e = parse_date(start), parse_date(end)
        if e < s:
            raise ValueError(t("the end ({end}) is before the start ({start})", end=e, start=s))
        ndays = (e - s).days + 1
        if scale == "auto":
            scale = choose_scale(s, e)
        if scale not in ("day", "week"):
            raise ValueError(t("scale must be 'auto', 'day' or 'week': {value}", value=scale))
        if scale == "day":
            if ndays > MAX_DAY_COLUMNS:
                raise ValueError(t("day_gantt: {n} days is too long for day columns "
                                   "(max {max}); use scale='week'", n=ndays,
                                   max=MAX_DAY_COLUMNS))
            cols = date_range(s, e)

            def index_of(day):
                return (day - s).days
        else:
            first = s - dt.timedelta(days=s.weekday())
            nweeks = (e - first).days // 7 + 1
            if nweeks > MAX_WEEK_COLUMNS:
                raise ValueError(t("day_gantt: {n} weeks is too long (max {max}). Split "
                                   "the period or use the month-level gantt",
                                   n=nweeks, max=MAX_WEEK_COLUMNS))
            cols = [first + dt.timedelta(weeks=i) for i in range(nweeks)]

            def index_of(day):
                return (day - first).days // 7

        norm = [normalize_gantt_row(r) for r in rows]
        if not norm:
            raise ValueError(t("day_gantt: needs at least one row"))
        for row in norm:
            dates = {"task": row[3:5], "milestone": row[3:4]}.get(row[0], ())
            for day in dates:
                if not s <= day <= e:
                    raise ValueError(t("'{name}': {day} is outside the chart period "
                                       "{start}-{end}", name=row[1], day=day, start=s, end=e))
        head_h = 0.62
        body_y, body_h = y + head_h, h - head_h
        rh = body_h / len(norm)
        if rh < MIN_GANTT_ROW_H:
            raise ValueError(t("{what}: {n} rows do not fit in h={h} (each row needs "
                               "{min}in). Split the period with scripts/calendar_pages.py",
                               what="day_gantt", n=len(norm), h=h, min=MIN_GANTT_ROW_H))
        hol = holidays_for(range(s.year, e.year + 1), extra_holidays)
        tday = parse_date(today) if today else None
        tx, tw = x + label_w, w - label_w
        n = len(cols)
        cu = tw / n
        sparse = scale == "day" and ndays > FULL_LABEL_DAYS

        def col_fill(c):
            if scale == "day":
                return self._cal_off_fill(c, hol)
            workweek = date_range(c, c + dt.timedelta(days=4))
            return lighten(P.danger, 0.90) if sum(1 for d in workweek if d in hol) >= 2 else None

        def month_key(c):
            mid = c if scale == "day" else c + dt.timedelta(days=3)
            return mid.year, mid.month

        self._cal_text(x, y + 0.22, label_w, 0.4, "タスク（担当）", size=size,
                       bold=True, color=P.muted, margin=0.04)
        i = 0
        while i < n:
            j = i
            while j + 1 < n and month_key(cols[j + 1]) == month_key(cols[i]):
                j += 1
            yy, mm = month_key(cols[i])
            segw = (j - i + 1) * cu
            label = ""
            for cand in (f"{yy}年{mm}月", f"{mm}月"):
                if em(cand) * 8.5 / 72 * 1.1 + 0.06 <= segw:
                    label = cand
                    break
            self.shape(tx + i * cu, y, segw, 0.22, fill=P.primary, stroke=P.white,
                       text=label or None, size=8.5, bold=True, color=P.white,
                       text_margin=0.02)
            i = j + 1

        today_idx = index_of(tday) if tday and s <= tday <= e else None
        for i, c in enumerate(cols):
            fill = col_fill(c)
            if fill:
                self.shape(tx + i * cu, y + 0.22, cu, 0.4, fill=fill)
        for i, c in enumerate(cols):
            cx = tx + i * cu
            if sparse:
                # Label each week once, from its Monday (or the first column when
                # the range starts mid-week and there is room for the label)
                if c.weekday() != 0 and i != 0:
                    continue
                span = min(7 - c.weekday(), n - i)
                if span < 3:
                    continue
                self._cal_text(cx, y + 0.225, span * cu, 0.2, f"{c.month}/{c.day}",
                               size=8, bold=True, margin=0.02,
                               color=self._cal_num_color(c, hol))
                self._cal_text(cx, y + 0.42, span * cu, 0.2,
                               iso_week_label(c, with_year=False), size=8,
                               color=P.muted, margin=0.02)
                continue
            if scale == "day":
                top, sub, color = str(c.day), WEEKDAYS_JA[c.weekday()], self._cal_num_color(c, hol)
            else:
                top, sub, color = iso_week_label(c, with_year=False), str(c.day), P.text
            if today_idx == i:
                self.shape(cx + 0.005, y + 0.225, cu - 0.01, 0.2, kind="ROUND_RECTANGLE",
                           fill=P.danger, text=top, size=8, bold=True, color=P.white,
                           text_margin=0.0)
            else:
                self._cal_text(cx, y + 0.225, cu, 0.2, top, size=8, bold=True,
                               align="CENTER", margin=0.0, color=color)
            self._cal_text(cx, y + 0.42, cu, 0.2, sub, size=8, align="CENTER",
                           margin=0.0, color=color)

        for i, c in enumerate(cols):
            fill = col_fill(c)
            if fill:
                self.shape(tx + i * cu, body_y, cu, body_h, fill=fill)
        self.line(x, y + h, x + w, y + h, color=P.border, weight=1.0, free=True)

        for r, row in enumerate(norm):
            ry = body_y + r * rh
            cy = ry + rh / 2
            if row[0] == "group":
                self.shape(x, ry + 0.02, w, rh - 0.04, fill=lighten(P.primary, 0.88),
                           text=self._cal_fit(row[1], w, size, 0.08), size=size,
                           bold=True, color=P.primaryDark, align="START",
                           text_margin=0.08)
                continue
            name, owner = row[1], row[2]
            label = f"{name}（{owner}）" if owner else name
            self._cal_text(x + 0.14, ry, label_w - 0.18, rh,
                           self._cal_fit(label, label_w - 0.18, size, 0.04),
                           size=size, margin=0.04)
            if row[0] == "task":
                ts, te, prog = row[3], row[4], row[5]
                i0, i1 = index_of(ts), index_of(te)
                bx, bw = tx + i0 * cu + 0.01, (i1 - i0 + 1) * cu - 0.02
                bh = min(0.18, rh * 0.62)
                self.shape(bx, cy - bh / 2, bw, bh, kind="ROUND_RECTANGLE",
                           fill=lighten(P.primary, 0.55))
                if prog > 0:
                    self.shape(bx, cy - bh / 2, bw * prog, bh, kind="ROUND_RECTANGLE",
                               fill=P.primary)
                biz = business_days(ts, te, hol)
                cap = (f"{biz}営業日" if scale == "day"
                       else f"{i1 - i0 + 1}週・{biz}営業日")
                if prog:
                    cap += f" · {int(round(prog * 100))}%"
                self._cal_caption(bx, bx + bw, cy, cap, x, x + w, size=8,
                                  color=P.muted, bold=False)
            else:
                day = row[3]
                i0 = index_of(day)
                if scale == "day":
                    mx = tx + (i0 + 0.5) * cu
                else:
                    mx = tx + (i0 + (day - cols[i0]).days / 7 + 1 / 14) * cu
                ms = 0.19
                self.shape(mx - ms / 2, cy - ms / 2, ms, ms, kind="DIAMOND", fill=P.danger)
                self._cal_caption(mx - ms / 2, mx + ms / 2, cy, md(day), x, x + w,
                                  size=8.5, color=darken(P.danger, 0.15), bold=True)

        if today_idx is not None:
            if scale == "day":
                lx = tx + (today_idx + 0.5) * cu
            else:
                lx = tx + (today_idx + (tday - cols[today_idx]).days / 7 + 1 / 14) * cu
            self.line(lx, body_y, lx, y + h, color=P.danger, weight=1.5, dashed=True,
                      free=True)
        return y + h

    def _cal_caption(self, left, right, cy, text, xmin, xmax, *, size, color, bold):
        """Caption right of [left, right], or left of it when it would leave the frame."""
        need = em(text) * size / 72 * 1.1 + 0.08
        if right + 0.04 + need <= xmax:
            self._cal_text(right + 0.04, cy - 0.12, need, 0.24, text, size=size,
                           color=color, bold=bold)
        else:
            self._cal_text(max(xmin, left - 0.04 - need), cy - 0.12, need, 0.24, text,
                           size=size, color=color, bold=bold, align="END")

    # ---- C. day agenda ----

    def day_agenda(self, x, y, w, h, start, end, items, *, today=None,
                   extra_holidays=None, show_empty_days=False, size=9,
                   col_widths=None) -> float:
        """Task list with one row per task, going down day by day. Returns the bottom y.

        items are [date, task, owner, due, status]. Tasks on the same day share
        a merged date cell; a run of days off with nothing scheduled collapses
        into one row naming the holidays. status is 完了 / 進行中 / 予定 / 遅延 /
        中止 (or done / doing / todo / late / cancelled) and is shown as a chip
        with its text, not colour alone.
        """
        P = self.P
        if not items:
            raise ValueError(t("day_agenda: needs at least one item"))
        s, e = parse_date(start), parse_date(end)
        hol = holidays_for({d.year for d in date_range(s, e)} if e >= s else {s.year},
                           extra_holidays)
        entries = agenda_entries(s, e, items, hol, show_empty_days=show_empty_days)
        for entry in entries:
            if entry[0] != "day":
                continue
            for _task, _owner, _due, status in entry[2]:
                if status not in _STATUS:
                    raise ValueError(t("unknown status '{status}' (use {allowed})",
                                       status=status, allowed=" / ".join(_STATUS)))
        tday = parse_date(today) if today else None
        hh = 0.3
        nrows = agenda_rows(entries)
        rh = min(0.3, (h - hh) / nrows)
        if rh < MIN_AGENDA_ROW_H:
            raise ValueError(t("{what}: {n} rows do not fit in h={h} (each row needs "
                               "{min}in). Split the period with scripts/calendar_pages.py",
                               what="day_agenda", n=nrows, h=h, min=MIN_AGENDA_ROW_H))
        ratios = col_widths or [1.25, 4.35, 1.1, 1.0, 1.3]
        widths = [w * r / sum(ratios) for r in ratios]
        heads = ["日付", "内容", "担当", "期日", "状態"]
        cx = x
        for wd, head in zip(widths, heads):
            self.shape(cx, y, wd, hh, fill=P.primary, stroke=P.white, text=head,
                       size=size, bold=True, color=P.white)
            cx += wd
        chips = {"success": (P.success, None), "primary": (P.primary, None),
                 "todo": (P.surfaceAlt, P.text), "danger": (P.danger, None),
                 "muted": ("#E5E7EB", P.muted)}
        yy = y + hh
        for entry in entries:
            if entry[0] in ("off", "empty"):
                a, b = entry[1], entry[2] if entry[0] == "off" else entry[1]
                if entry[0] == "off":
                    days = date_range(a, b)
                    names = "・".join(dict.fromkeys(hol[d] for d in days if d in hol))
                    kinds = "・".join(k for k in ("土日" if any(d.weekday() >= 5 for d in days) else "",
                                                  "祝日" if names else "") if k)
                    when = md(a) if a == b else f"{md(a)} 〜 {md(b)}"
                    text = f"{when}　{kinds}" + (f"（{names}）" if names else "")
                    fill, color = lighten(P.danger, 0.92), darken(P.danger, 0.15)
                else:
                    text = f"{md(a)}　予定なし"
                    fill, color = P.surfaceAlt, P.muted
                self.shape(x, yy, w, rh, fill=fill, stroke=P.border, stroke_weight=0.5,
                           text=self._cal_fit(text, w, size, 0.1), size=size,
                           color=color, align="START", text_margin=0.1)
                yy += rh
                continue
            day, rows_ = entry[1], entry[2]
            span = rh * len(rows_)
            is_today = day == tday
            self.shape(x, yy, widths[0], span,
                       fill=lighten(P.danger, 0.85) if is_today else P.white,
                       stroke=P.border, stroke_weight=0.5,
                       text=md(day) + ("\n今日" if is_today and len(rows_) > 1 else ""),
                       size=size, bold=True,
                       color=darken(P.danger, 0.15) if is_today else self._cal_num_color(day, hol))
            for k, (task, owner, due, status) in enumerate(rows_):
                ry = yy + k * rh
                cx = x + widths[0]
                for wd, val, align in zip(widths[1:4], (task, owner, due or "—"),
                                          ("START", "CENTER", "CENTER")):
                    self.shape(cx, ry, wd, rh, fill=P.white, stroke=P.border,
                               stroke_weight=0.5, text=self._cal_fit(val, wd, size, 0.08),
                               size=size, align=align, text_margin=0.08)
                    cx += wd
                self.shape(cx, ry, widths[4], rh, fill=P.white, stroke=P.border,
                           stroke_weight=0.5)
                fill, tc = chips[_STATUS[status]]
                pad = min(0.2, widths[4] * 0.15)
                self.shape(cx + pad, ry + 0.045, widths[4] - 2 * pad, rh - 0.09,
                           kind="ROUND_RECTANGLE", fill=fill, text=status,
                           size=size - 0.5, bold=True, color=tc or readable_on(fill),
                           text_margin=0.0)
            yy += span
        return yy
