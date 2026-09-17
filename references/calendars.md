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
| One week by hour | `week_timetable` | 5 or 7 day columns, overlaps side by side |
| Consecutive sprints | `sprint_calendar` | working days per sprint, event days placed automatically |
| A fiscal year at a glance | `year_calendar` | 12 mini months, busy / off / key marks (handout density) |
| Days left to a deadline | `deadline_countdown` | calendar and working days, checkpoints |
| Daily volume over up to a year | `calendar_heatmap` | quantile colours, monthly totals, aggregate cards |
| Who is on duty each day | `shift_roster` | one-character codes, headcount per day |
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
  spans the days, split per week row and marked as a continuation where it
  carries on.
- `category`: `primary / success / danger / info / warning / muted` or empty.
- Bars take lanes first; one-day items fill the rest; the remainder collapses
  into a "+N more" note. Cell titles drop the time before being cut with "…".
- That continuation mark and that note are drawn from the deck's label
  resource (`slide-templates/i18n/`), so they follow its language.
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
- Task captions: the working-day count (on the week scale, the week count as
  well) and the progress percentage, worded from the deck's label resource.
  Milestones are diamonds captioned with the date.
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
             show_empty_days=False,   # a "no plans" row for empty working days
             size=9,
             col_widths=None)         # ratios, default [1.25, 4.35, 1.1, 1.0, 1.3]
```

- `items` are `[date, task, owner, due, status]`. Tasks on one day share a
  merged date cell; an empty due shows "—".
- A run of days off with nothing scheduled collapses into one row naming the
  holidays: the date range, whether it was a weekend or a public holiday, and
  the holiday names. The dates and those two words follow the deck's language;
  the holiday names come from the bundled CSV and stay as published, so an
  English deck still shows them in Japanese.
- `status`: `完了 / 進行中 / 予定 / 遅延 / 中止` or `done / doing / todo / late /
  cancelled`, drawn as a chip with its text.
- Rows are 0.30 in, shrinking to 0.24 in; more rows raise.

```json
{ "type": "day_agenda", "x": 0.5, "y": 1.05, "w": 9.0, "h": 3.65,
  "start": "2026-09-14", "end": "2026-09-25", "today": "2026-09-15",
  "items": [["2026-09-15", "セキュリティ審査の資料提出", "情シス", "12:00", "完了"]] }
```

## week_timetable

```python
d.week_timetable(x, y, w, h, week, events,
                 days=5,                 # 5 (Mon-Fri) or 7
                 start_hour=9, end_hour=18,
                 breaks=None,            # default: one 12:00-13:00 lunch break
                 extra_holidays=None,
                 size=8.5)
```

- `week` is any date in the week; columns start on its Monday.
- `events` are `[date, start, end, title, place, category]` with `HH:MM` times.
  Overlapping events on a day are placed side by side (`assign_tracks`); three
  at once raise.
- Each hour needs 0.30 in; an event must be tall enough for one 8pt line
  (30 minutes at 9–18h on the template's 3.65 in).
- Boxes ≥ 0.62 in show time range, title and place; shorter ones "9:30 title";
  narrow side-by-side boxes the title only.
- Breaks are grey bands on days with nothing scheduled over them; a holiday
  with no events is shaded with its name.

```json
{ "type": "week_timetable", "x": 0.5, "y": 1.05, "w": 9.0, "h": 3.65,
  "week": "2026-10-05", "days": 5, "startHour": 9, "endHour": 18,
  "events": [["2026-10-05", "09:30", "12:00", "オリエンテーション", "大会議室", "primary"]],
  "breaks": [["12:00", "13:00", "昼休憩"]] }
```

## sprint_calendar

```python
d.sprint_calendar(x, y, w, h, start, sprints,
                  length_days=14,        # 7 or 14
                  extra_holidays=None,
                  size=8.5)
```

- `start` must be a Monday. `sprints` are `[number, goal, release]`, laid out
  consecutively; at most 8 week rows (four 2-week or eight 1-week sprints).
- The left panel shows dates, working days and how many weekdays holidays took,
  and the goal (one-week rows fold dates into the second line).
- The first working day is marked as planning (a moved-planning variant if the
  sprint's Monday is off); the last working day as review, or as release in red
  when `release` is true. Those words come from the deck's label resource
  (`slide-templates/i18n/`), so they follow its language.

```json
{ "type": "sprint_calendar", "x": 0.5, "y": 1.05, "w": 9.0, "h": 3.65,
  "start": "2026-09-28", "lengthDays": 14,
  "sprints": [["12", "検索 API の公開", false], ["13", "権限管理の追加", true]] }
```

## year_calendar

```python
d.year_calendar(x, y, w, h, start_month, marks,
                extra_holidays=None,
                size=7)
```

- Twelve months from `start_month` ("2026-04" for a Japanese fiscal year), in
  two rows of six. Numbers are 7pt: a handout form.
- `marks` are `[start, end, label, kind]`; `busy` fills the range blue, `off`
  red, `key` circles the start date (end empty). Dates outside the 12 months
  raise.
- The legend lists each kind with its labels; closures you also want as red
  numbers go in `extra_holidays`.

```json
{ "type": "year_calendar", "x": 0.5, "y": 1.05, "w": 9.0, "h": 3.65,
  "startMonth": "2026-04",
  "marks": [["2026-04-01", "2026-04-24", "決算", "busy"],
            ["2026-06-25", "", "株主総会", "key"]] }
```

## deadline_countdown

```python
d.deadline_countdown(x, y, w, h, deadline, today, label,
                     checkpoints=None,   # up to 3 [date, name]
                     extra_holidays=None)
```

- Calendar days left (`deadline - today`) in large type, working days from
  today to the day before the deadline, and each checkpoint with the number of
  days until it, worded in the deck's language.
- The right side shows today's month and the next with the remaining days
  filled; the deadline must fall in one of them (otherwise use
  `month_calendar` / `day_gantt`). Needs h ≥ 3.3 in.

```json
{ "type": "deadline_countdown", "x": 0.5, "y": 1.05, "w": 9.0, "h": 3.65,
  "deadline": "2026-10-14", "today": "2026-09-15", "label": "本番切替まで",
  "checkpoints": [["2026-09-18", "判定会議"]] }
```

## calendar_heatmap

```python
d.calendar_heatmap(x, y, w, h, start, end, values,
                   unit=None,          # default from the deck's label resource
                   levels=5,           # 3-7 quantile buckets
                   monthly=True,       # monthly totals strip under the grid
                   summary=True,       # three aggregate cards
                   extra_holidays=None)
```

- `values` are `[[date, number], ...]` (≥ 0, one per day) within `start`–`end`,
  at most 53 weeks. Columns are Monday-first weeks, rows weekdays.
- Colours are quantiles of the values present, so they are relative to the
  period. A day without a value is white with an outline — not zero.
- The legend shows the bucket bounds; the monthly strip centres one bar under
  each month; the cards show the busiest and quietest weekday (holidays
  excluded), month totals, and the holiday average. No interpretation is drawn.
- Cells shrink to fit the height (max 0.26 in); below 0.1 in it raises — turn
  off `monthly` or `summary`.

```json
{ "type": "calendar_heatmap", "x": 0.5, "y": 1.05, "w": 9.0, "h": 3.65,
  "start": "2025-04-01", "end": "2026-03-31", "unit": "件",
  "values": [["2025-04-01", 42], ["2025-04-02", 38]] }
```

## shift_roster

```python
d.shift_roster(x, y, w, h, start, end, people, codes,
               min_staff=0,          # days below this headcount turn red
               extra_holidays=None,
               size=8.5)
```

- `people` are `[name, schedule]`; the schedule is one code character per day
  (`"日日夜休…"`), exactly as long as the period (≤ 31 days, ≤ 12 people).
- `codes` are `[code, label, colour, counts]`; colour is `primary / dark /
  success / danger / info / warning / muted`, `counts` marks codes that count as
  on duty for the headcount row and the per-person totals.
- The legend is drawn from `codes` (plus the shortage colour when `min_staff`
  is set).

```json
{ "type": "shift_roster", "x": 0.5, "y": 1.05, "w": 9.0, "h": 3.65,
  "start": "2026-10-01", "end": "2026-10-03", "minStaff": 1,
  "people": [["運用 A", "日夜休"], ["運用 B", "休日日"]],
  "codes": [["日", "日勤", "primary", true], ["夜", "夜勤", "dark", true],
            ["休", "休み", "muted", false]] }
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
| `parse_time(value)` / `format_time(hours)` | `9.5` / `"9:30"` |
| `assign_tracks(intervals)` | (track, tracks in its overlap cluster) per interval |
| `sprint_ranges(start, count, length_days)` | consecutive sprint date ranges |
| `months_from(start_month, count)` | `[(year, month), ...]` |
| `quantile_cuts(values, levels)` / `bucket_of(value, cuts)` | bucket bounds / bucket index |
| `normalize_series(values)` | `{date: number}` |
| `normalize_roster(start, end, people, codes)` / `roster_totals(rows, codes)` | validated roster / (per day, per person) |

## Splitting across slides

`scripts/calendar_pages.py data.json --out pages.json` turns one dataset into
template slides: one page per month (month calendar, roster — rosters also per
12 people), per Monday–Sunday week (agenda, timetable), per row chunk at group
boundaries (gantt), per 8 week rows (sprints), or per 52 weeks (heatmap). The
year and countdown forms are one page each. See its docstring for the input
format.

## See also

- [Drawing Diagrams (diagrams.py and the Canvas family)](diagrams.md)
- [Tables and charts (charts.py)](charts.md)
- [Business Framework Diagrams (patterns.py)](patterns.md)
- [Slide Template Catalog (All 108 Types)](slide-template-catalog.md)
