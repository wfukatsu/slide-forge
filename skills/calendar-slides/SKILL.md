---
name: calendar-slides
description: >-
  Turn dated tasks and events into calendar slides — month grid (Monday or
  Sunday start), day-by-day gantt, or a day-by-day task list — with Japanese
  holidays, multi-day spans and automatic page splits; also maintains the
  slide-templates/calendar pack.
  Use for: カレンダーでスケジュールを見せたい, 月間予定表, 日単位のガント, 日次タスク一覧,
  calendar slide, monthly calendar, daily gantt.
  Not: month-level plans (planning/gantt-schedule); milestone-only timelines
  (planning/milestone-timeline).
---
*[日本語](SKILL.ja.md)*

# Calendar Slides

Build slides whose axis is the calendar itself, from dated tasks and events.
The date arithmetic — weekday offsets, 4–6 week rows, holidays, bars that wrap
across weeks, working-day counts, page splits — lives in `scripts/calendars.py`
and `scripts/calendar_pages.py`. Never compute calendar coordinates by hand.

Run everything from the slide-forge root with `.venv/bin/python`. Follow
`references/workflow-contract.md` for the deck lifecycle (approve → validate →
generate → QA → deliver).

## Boundaries

| Request | Route |
|---|---|
| Dated events/tasks shown as a month grid, day gantt, or daily task list | this skill |
| Month- or quarter-level plan with column labels only | `planning/gantt-schedule` via `google-slides(-template)` |
| Equally spaced milestones / history | `planning/milestone-timeline`, `planning/chronology` |
| Dependency-driven roadmap | `nexus/roadmap` |
| A whole deck in which calendar pages are only part | the generation skill (`google-slides` / `google-slides-template`), calling this skill's pages |
| A new or changed calendar template or primitive | this skill, section *Maintaining the calendar pack* |

## Templates

| id | Shows | One page holds | Split by `calendar_pages.py` |
|---|---|---|---|
| `month-calendar` | one week per row, events in day cells, multi-day bars | ~2 items per day, then "+N件" | one page per month |
| `daily-gantt` | 1 column = 1 day (≤ 60 days) or 1 ISO week (≤ 26 weeks) | 12 rows | at group boundaries |
| `daily-agenda` | 1 row = 1 task, dates going down | 11 rows (a run of days off counts as 1) | per Monday–Sunday week |
| `weekly-timetable` | day columns × hour rows | 5 or 7 days, 9–18h, two overlapping events | per Monday–Sunday week |
| `sprint-calendar` | sprints as week rows with a goal panel | 8 week rows | every 8 week rows |
| `year-at-a-glance` | 12 mini months with busy / off / key marks | one year (handout density) | one page |
| `deadline-countdown` | days left, working days, checkpoints | deadline within today's month or the next | one page |
| `activity-heatmap` | daily values as week × weekday colours, monthly totals, aggregate cards | 53 weeks | every 52 weeks |
| `shift-roster` | people × days with one-character codes and headcount | 31 days × 12 people | per month, per 12 people |

Choose with [form-selection.md](references/form-selection.md). The limits and
their derivation are in [capacity.md](references/capacity.md). Primitive
arguments are in `references/calendars.md`.

## Workflow

### 1. Intake

Ask in one round, only for what is missing:

- the message: what should the reader conclude (the governing title, ≤ 36
  full-width characters, one line);
- the period (start / end, or months);
- the data: pasted table, CSV, Google Sheet, or an existing document. Google
  Calendar is not imported automatically yet — ask the user to export or paste;
- week start (default `mon`; `sun` when the audience expects a wall calendar);
- company closures beyond national holidays (year-end, summer shutdown);
- the as-of date (`today` highlight and the `source` line);
- deck context: standalone pages or part of a larger deck; master template;
  QA (default: run).

### 2. Normalize

Write `out/<deck>/calendar-data.json` in the `calendar_pages.py` input format
(see its docstring). Rules:

- Dates are `YYYY-MM-DD` (or `YYYY/M/D`). **A date without a year is asked
  about, never guessed.** Relative dates ("来週水曜") are resolved with the user.
- `month-calendar` events: `[start, end, title, category, time]`; empty `end`
  for a one-day item. Category is `primary / success / danger / info /
  warning / muted` or empty.
- `daily-gantt` rows: `["group", name, "", "", "", 0]`,
  `["task", name, owner, start, end, progress 0–1]`,
  `["milestone", name, owner, date, "", 0]`.
- `daily-agenda` items: `[date, task, owner, due, status]`; status is
  `完了 / 進行中 / 予定 / 遅延 / 中止` (or `done / doing / todo / late / cancelled`).
- `weekly-timetable` events: `[date, start HH:MM, end HH:MM, title, place, category]`.
- `sprint-calendar` sprints: `[number, goal, release true/false]`, with `start`
  on a Monday and `lengthDays` 7 or 14.
- `year-at-a-glance` marks: `[start, end, label, busy|off|key]` from `startMonth`.
- `deadline-countdown`: `label`, `deadline`, `today` (required), up to three
  `checkpoints` `[date, name]`.
- `activity-heatmap` values: `[date, number ≥ 0]`, one per day; leave missing
  days out instead of writing 0. `source` must state period, definition and unit.
- `shift-roster` people: `[name, schedule]` with one code character per day;
  codes: `[code, label, colour, counts]`; `minStaff` from the staffing standard.
- Keep plan and actuals apart; progress needs an as-of date in `source`.

### 3. Split and approve

```bash
.venv/bin/python scripts/calendar_pages.py out/<deck>/calendar-data.json \
    --out out/<deck>/pages/200-calendar.json
```

Show the page count, each page's period, and each title. A generated
"（1/3）" suffix is a placeholder: propose a real message per page (pass them
as `titles`). Get approval before generating.

### 4. Validate and generate

Combine with the rest of the deck when needed (`scripts/assemble_spec.py`),
then:

```bash
.venv/bin/python scripts/build_deck.py --template templates/blank-16x9.json \
    --spec out/<deck>/deck.json --dry-run --strict
.venv/bin/python scripts/drive_folder.py create "<deck title>"
.venv/bin/python scripts/build_deck.py --template templates/blank-16x9.json \
    --spec out/<deck>/deck.json --title "<deck title>" --folder <FOLDER_ID>
```

Calendar pages use the `BLANK` layout and palette tokens, so any registered
master works in place of `blank-16x9.json`. A primitive error (date outside the
period, too many rows, unknown status) stops the dry run — fix the data, not the
template. Upload `calendar-data.json` and the spec to the folder.

### 5. Visual QA

Run `slide-qa`. Calendar-specific checks: the day/column the "+N件" belongs to,
bars split at week rows with "（続き）", Saturday blue / Sunday-holiday red,
holiday shading not hiding bars, captions not colliding with the today line,
and the title staying on one line.

### 6. Report

Deck and folder URLs, pages and periods, any year outside the bundled holiday
data (the scripts print a warning), QA result and cleanup.

## Maintaining the calendar pack

Schema, validation, registration and compatibility follow
[`slide-template-creator`](../slide-template-creator/SKILL.md). In addition:

1. **Dates in, coordinates out.** Slots take ISO strings; all calendar math is
   in `calendars.py` pure functions (unit-tested in `tests/test_calendars.py`).
   Add a pure function and a test before drawing with it.
2. **Double the guard.** Slot limits keep the example audit clean; the
   primitive raises `ValueError` for input that would be unreadable (rows too
   short, period too long, date outside the period). `calendar_pages.py` must
   split at the same limits — change both together.
3. **Boundary inputs** every change must pass (`tests/test_calendars.py`
   covers them): a 4-row month (2027-02, Monday start), 6-row months (2026-08),
   Sunday start, a bar wrapping a week and a month, "+N件" in a cell with a bar,
   a 31/60/61-day gantt, a 26-week gantt with year-end closures, an agenda with
   a collapsed holiday run, and the longest title.
4. **Holidays.** Never hand-edit `assets/holidays/jp.csv`; run
   `scripts/update_holidays.py` (yearly, after the Cabinet Office publishes the
   next year's equinox days in February).
5. **Validate** `validate_slide_templates.py --pack calendar`, the unit tests,
   and — when a shared primitive changed — every pack. Then generate the
   catalog (`build_slide_template_catalog.py --pack calendar`), run
   `slide-qa`, and refresh `references/images/slide-templates/<id>.png` and the
   catalog doc.

All nine forms of the plan (`references/calendar-template-plan.ja.md`) are built.

## Safety

- Calendars often carry people's names and private appointments. Keep real
  data under ignored `out/` paths; examples use invented, role-based names.
- Do not present a plan as a commitment: the `source` line states the as-of
  date and that dates are planned.
