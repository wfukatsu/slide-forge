# Choosing the calendar form

Pick the form from the reader's question first, then check the period.

| The reader asks | Template | Period that fits one page |
|---|---|---|
| What happens on which day this month, and where is it crowded? | `month-calendar` | one calendar month (split per month) |
| How do the tasks overlap day by day, and when do they end once days off are counted? | `daily-gantt` | ≤ 60 days on day columns; 61 days – 26 weeks on week columns |
| Who does what by when, day by day? | `daily-agenda` | about two weeks, 11 rows (split per week) |
| What happens at which hour and where, this week? | `weekly-timetable` | one week (split per week) |
| How long is each sprint once holidays count, and when are its events? | `sprint-calendar` | 8 week rows |
| Where do the busy periods and key dates fall in the year? | `year-at-a-glance` | 12 months (handout only) |
| How many (working) days are left until the deadline? | `deadline-countdown` | deadline within today's month or the next |
| On which weekdays and in which periods does the volume concentrate? | `activity-heatmap` | up to 53 weeks (split every 52) |
| Who is on duty each day, and which days are short-staffed? | `shift-roster` | 31 days × 12 people (split per month / team) |

## By period length

| Period | Use |
|---|---|
| ≤ 31 days | `daily-gantt` (every day labelled) or `month-calendar` |
| 32–60 days | `daily-gantt` (Mondays labelled) or two `month-calendar` pages |
| 61 days – 26 weeks | `daily-gantt` on week columns |
| > 26 weeks | `planning/gantt-schedule` (month columns) — not this pack |

## Common confusions

- **Many events on few days** (a conference week, a cut-over weekend):
  `month-calendar` would collapse them into "+N件". Use `daily-agenda`, or a
  plain `table` / `event_timetable` for hour-level detail.
- **Deadlines without durations**: a gantt of zero-length bars says nothing —
  use `daily-agenda` (or `month-calendar` with one-day items).
- **Durations without dates** (relative order only): not a calendar. Use
  `planning/milestone-timeline` or `nexus/roadmap`.
- **Mixed audience of projector and handout**: calendar forms are dense
  (8.5–9pt). For a projected talk, keep the month grid or reduce the period,
  and put detail in the appendix.

## When the later forms do not fit

- **Exact daily numbers matter** more than the pattern: the heatmap only shows
  buckets — use a `table` or `linechart` (`charts.md`).
- **Comparing two periods' heatmaps**: colours are per-period quantiles and do
  not line up; chart both series on one `linechart` instead.
- **Intraday or hourly volume**: not a calendar form; use `vbars` / `linechart`.
- **A roster with more than one code per person per day** (split shifts): use
  a `table` — the roster holds one character per cell.

- **A single-day agenda by hour with tracks or rooms** (conference day):
  `event_timetable` (`events.md`), not `weekly-timetable`.
- **Three or more events overlapping** in the timetable: split by room or
  track into separate pages.
- **Sprints of irregular length**: `daily-gantt` with one task row per sprint.
- **A deadline more than a month away**: `month-calendar` pages, or
  `daily-gantt` with the deadline as a milestone.
- **A projected year overview**: `planning/gantt-schedule` (month columns);
  `year-at-a-glance` is too small to read on a screen.
