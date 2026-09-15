# Calendar capacity and thresholds

All figures assume the portable page: 10 × 5.625 in, `governing_message` at
y 0.42, the calendar at x 0.5, y 1.05, w 9.0, h 3.65, and the source line at
y 4.85. The constants live in `scripts/calendars.py`; the unit tests and the
page splitter read the same values.

## Title

`governing_message` is 17pt over 9.0 in: about 36.8 full-width characters per
line. A second line reaches y ≈ 1.28 and covers the calendar header, so every
calendar template caps `title` at **36** characters.

## month-calendar

| Item | Value |
|---|---|
| Header row | 0.26 in |
| Week rows | 4–6 → 0.85 / 0.68 / 0.57 in each |
| Day number row | 0.23 in (9pt bold) |
| Event lane | 0.19 in (8.5pt), `int((row − 0.25) / 0.19)` lanes → 3 / 2 / 1 |
| Cell width | 1.23 in with week numbers (Monday start), 1.29 in without |
| Title in a cell | ~8 full-width characters; the time is dropped first, then "…" |
| Overflow | the last free lane shows "+N件"; with no free lane it goes to the top-right corner |

A 6-row month has only one lane per day. When a month with 6 rows is busy,
move detail to a `daily-agenda` page rather than accept "+N件" everywhere.

## daily-gantt

| Item | Value |
|---|---|
| Header | 0.62 in (month band 0.22 + two label rows) |
| Label column | 1.8 in; "name（owner）" is cut to fit |
| Day columns | 7.2 in ÷ days → 0.23 in at 31 days, 0.12 in at 60 |
| Labels | every day ≤ 31 days; Mondays only (date + ISO week) for 32–60 |
| Week columns | 61 days – 26 weeks (0.28 in each); heading `W38` over the Monday's day |
| Rows | ≥ 0.24 in each → 12 rows maximum |
| Week shading | a week with ≥ 2 holidays or closures on weekdays |

## daily-agenda

| Item | Value |
|---|---|
| Header | 0.30 in |
| Rows | ≤ 0.30 in, ≥ 0.24 in → 11 rows at full height, 14 at the floor |
| Slot cap | 11 items; the splitter counts collapsed day-off rows too |
| Columns (ratio) | date 1.25 · task 4.35 · owner 1.1 · due 1.0 · status 1.3 |
| Task text | ~24 characters at 9pt before "…" |

## Holiday data

`assets/holidays/jp.csv` covers 1955 through the latest year the Cabinet Office
has published (the following year appears each February). Outside that range
only weekends are days off and a warning is printed once per year.
