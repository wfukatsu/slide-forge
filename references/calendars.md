*[日本語](calendars.ja.md)*

# Calendar diagrams (`calendars.py`)

Drawing parts whose input is dates, not coordinates. They are mixed into
`diagrams.Canvas`, registered as spec figures, and used by the
`slide-templates/calendar` pack and the `calendar-slides` skill.

| Want to show | Use | Notes |
|---|---|---|
| A month with events in the day cells | `month_calendar` | Monday or Sunday start; multi-day bars |
| Tasks over days (or weeks) with days off shaded | `day_gantt` | day columns ≤ 60 days, week columns ≤ 26 weeks |
| Tasks listed day by day | `day_agenda` | merged date cells, collapsed days off |
| A month-level plan | `gantt` (`patterns.md`) | column labels only, no dates |

Shared conventions:

- Dates are `YYYY-MM-DD` strings (or `datetime.date`). `YYYY/M/D` is accepted;
  a date without a year raises `ValueError`.
- Saturday numbers are blue, Sunday and holiday numbers red; the cell or column
  gets a light fill. National holidays come from `assets/holidays/jp.csv`
  (refresh with `scripts/update_holidays.py`). A year outside it prints a
  warning and falls back to weekends only.
- `extra_holidays` adds company closures: `[[date, name], ...]` or
  `[[start, end, name], ...]`.
- Each part returns the bottom y. Input that cannot be drawn legibly raises
  `ValueError` — split the period with `scripts/calendar_pages.py`.

## month_calendar

```python
d.month_calendar(x, y, w, h, month, events,
                 week_start="mon",      # "mon" or "sun"
                 week_numbers=None,     # default: True for "mon", False for "sun"
                 extra_holidays=None,
                 size=8.5)
```

- `month` is `"2026-09"`. The grid has 4–6 week rows including adjacent-month
  days (greyed).
- `events` are `[start, end, title, category, time]`. Empty `end` (or `end ==
  start`) is a one-day item written in the cell as "10:00 定例"; otherwise a bar
  spans the days, split per week row, with "（続き）" on continuations.
- `category`: `primary / success / danger / info / warning / muted` or empty.
- Bars take lanes first; one-day items fill the rest; the remainder becomes
  "+N件". Cell titles drop the time before being cut with "…".
- ISO week numbers ("W38") are shown only for Monday start by default.

```json
{ "type": "month_calendar", "x": 0.5, "y": 1.05, "w": 9.0, "h": 3.65,
  "month": "2026-09", "weekStart": "mon",
  "events": [["2026-09-14", "2026-09-18", "データ移行検証", "primary", ""],
             ["2026-09-18", "", "判定会議", "danger", "15:00"]],
  "extraHolidays": [] }
```

## day_gantt

```python
d.day_gantt(x, y, w, h, start, end, rows,
            today=None,          # "2026-09-15": red day label and dashed line
            scale="auto",        # "auto" / "day" / "week"
            label_w=1.8,
            extra_holidays=None,
            size=9)
```

- `rows`: `["group", name]`, `["task", name, owner, start, end, progress]`,
  `["milestone", name, owner, date]`. Template tuples pad unused cells with
  `""` / `0`.
- `scale="auto"`: one column per day up to 60 days (all days labelled up to 31,
  Mondays with ISO week beyond), one column per ISO week up to 26 weeks. Longer
  periods raise — use `gantt` with month columns.
- Days off are shaded behind the bars (week scale: weeks with ≥ 2 holidays).
- Task captions: working days (`5営業日`; week scale `6週・26営業日`) and the
  progress percentage. Milestones are diamonds captioned with the date.
- Each row needs 0.24 in; dates outside `start`–`end` raise.

```json
{ "type": "day_gantt", "x": 0.5, "y": 1.05, "w": 9.0, "h": 3.65,
  "start": "2026-09-14", "end": "2026-10-14", "today": "2026-09-15",
  "rows": [["group", "準備フェーズ", "", "", "", 0],
           ["task", "環境構築", "基盤", "2026-09-16", "2026-09-25", 0.6],
           ["milestone", "判定会議", "PM", "2026-10-08", "", 0]] }
```

## day_agenda

```python
d.day_agenda(x, y, w, h, start, end, items,
             today=None,
             extra_holidays=None,
             show_empty_days=False,   # a "予定なし" row for empty working days
             size=9,
             col_widths=None)         # ratios, default [1.25, 4.35, 1.1, 1.0, 1.3]
```

- `items` are `[date, task, owner, due, status]`. Tasks on one day share a
  merged date cell; an empty due shows "—".
- A run of days off with nothing scheduled collapses into one row naming the
  holidays ("9/19（土） 〜 9/23（水）　土日・祝日（敬老の日・休日・秋分の日）").
- `status`: `完了 / 進行中 / 予定 / 遅延 / 中止` or `done / doing / todo / late /
  cancelled`, drawn as a chip with its text.
- Rows are 0.30 in, shrinking to 0.24 in; more rows raise.

```json
{ "type": "day_agenda", "x": 0.5, "y": 1.05, "w": 9.0, "h": 3.65,
  "start": "2026-09-14", "end": "2026-09-25", "today": "2026-09-15",
  "items": [["2026-09-15", "セキュリティ審査の資料提出", "情シス", "12:00", "完了"]] }
```

## Date engine

Pure functions in `calendars.py`, covered by `tests/test_calendars.py`:

| Function | Returns |
|---|---|
| `parse_date(value)` / `parse_month(value)` | `date` / `(year, month)` |
| `month_weeks(year, month, week_start)` | week rows of 7 dates |
| `holidays_for(years, extra)` | `{date: name}` (bundled + closures) |
| `business_days(start, end, holidays)` | working days, both ends included |
| `iso_week_label(day)` | `"2026-W53"` |
| `fiscal_quarter(day, start_month=4)` | `(fiscal year, quarter)` |
| `choose_scale(start, end)` | `"day"` / `"week"` |
| `pack_lanes(spans, nlanes)` | lane placement and overflow |
| `agenda_entries(start, end, items, holidays)` | day / off / empty rows |

## Splitting across slides

`scripts/calendar_pages.py data.json --out pages.json` turns one dataset into
template slides: one page per month, per Monday–Sunday week (agenda), or per
row chunk at group boundaries (gantt). See its docstring for the input format.
