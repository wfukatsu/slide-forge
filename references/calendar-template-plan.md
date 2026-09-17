*[日本語](calendar-template-plan.ja.md)*

# Calendar templates and skill — plan

Research and implementation plan for adding date-driven slides (month calendar,
day-by-day gantt, day-by-day task list, …) as the `slide-templates/calendar/`
pack and the `calendar-slides` skill.

## 1. Goal and scope

**Goal**: from a list of dated events and tasks, generate calendar slides that
handle weekdays, week start, holidays, multi-day items and slide splitting
correctly.

**In scope**: the date engine and drawing primitives (`scripts/calendars.py`),
the `calendar` pack (phased, §4), the `calendar-slides` skill, and the bundled
Japanese holiday data with its refresh script.

**Out of scope**: month-level plans (`planning/gantt-schedule`), equally spaced
milestones (`planning/milestone-timeline`), history (`planning/chronology`),
dependency roadmaps (`nexus/roadmap`), and date-less Now / Next / Later.

## 2. Starting point

| Item | State | Consequence |
|---|---|---|
| `gantt` primitive | arbitrary column labels, fractional columns, 8 rows, used by proposal builders | left untouched; calendar gets its own primitive |
| `$slot` expansion | value substitution only | weekday offsets, 4–6 week rows, holidays and lanes are computed in the primitive |
| Template unit | one template = one slide | splitting a period happens outside templates (page splitter) |
| Holiday data | none | bundle the Cabinet Office CSV (§3.4) |
| Audit | `build_deck.py --dry-run --strict` | zero findings required |

## 3. Research

### 3.1 Conventions

- **Week start**: Monday for Japanese business documents (ISO 8601, weekend on
  the right); Sunday for a wall-calendar look. Outlook defaults to Sunday; Google
  Calendar offers Saturday/Sunday/Monday; CLDR weekData holds regional defaults.
- **ISO week**: week 1 contains the year's first Thursday; show with the year
  (`2026-W53`).
- **Fiscal year**: the Japanese government year runs April–March; make the start
  month a parameter and print actual months next to quarter labels.
- **Colour (Japan)**: weekdays black, Saturday blue, Sunday and holidays red —
  on the date number only; days off get a light fill. Use grey for both weekend
  days in English-language material.
- **Legibility**: calendars cannot meet 18pt projection sizes; treat them as
  handout density (min 9pt, 10–12pt preferred) and change the form for talks.
- **Overflow order**: truncate → an overflow marker ("+N more") with a detail
  page → coarser scale → split into pages with "(1/3)".

### 3.2 Forms and capacity on a 16:9 page (≈ 9.0 × 3.7 in drawing area)

| # | Form | Typical use | One-page capacity | Split unit |
|---|---|---|---|---|
| A | Month grid (week rows) | monthly events, deadlines | ~2 items per day + "+N" | month |
| B | Day gantt | PoC / migration daily plans | 31 days labelled, 60 days with Monday labels, then week columns; ~12 rows | month or group |
| C | Day agenda (rows going down) | next two weeks of actions | ~11 rows | week |
| D | Weekly timetable | training week, booth duty | 9–18h in 1h rows | week |
| E | Quarter / year mini calendars | annual events, fiscal plans | year view is handout-only (7–8pt) | quarter / year |
| F | Sprint calendar | Scrum events | month grid with sprint bands | month |
| G | Deadline countdown | release, renewal | big number + shaded range | page |
| H | Activity heatmap | usage, incidents | 53 × 7 cells, 5 buckets, source required | year |
| I | Shift roster | on-call, event staff | 31 columns × 12 people | team |

### 3.3 Drawing rules adopted

- Multi-day items take lanes at the top of the cell, split per week row, title
  repeated on continuations.
- Gantt: days off shaded behind bars, red today marker and dashed line,
  diamonds for milestones, progress as a darker fill; no dependency arrows.
- Agenda: merged date cells, collapsed runs of days off, status chips with text.

### 3.4 Holiday data

Bundle the Cabinet Office CSV
(`https://www8.cao.go.jp/chosei/shukujitsu/syukujitsu.csv` — Shift_JIS, 1955–,
CC BY-compatible terms) as UTF-8 `assets/holidays/jp.csv`; refresh with
`scripts/update_holidays.py`; no
network at generation time; warn (never guess) for uncovered years; company
closures via `extraHolidays`.

## 4. What to build

Some names below moved between the plan and the code. The function names in
§4.1 are the ones that shipped; the primitive arguments are as planned, and
§§9–11 record where implementation diverged.

### 4.1 Date engine and primitives (`CalendarMixin` in `scripts/calendars.py`)

Pure functions, drawing nothing, so they can be unit-tested:

| Function | Role |
|---|---|
| `month_weeks(year, month, week_start)` | The week × weekday date matrix (4–6 rows), and which cells belong to a neighbouring month |
| `iso_week_label(date)` / `fiscal_quarter(date, start_month)` | Week-number and fiscal-quarter labels |
| `holidays_for(years, extra)` / `is_offday(date, holidays, workdays)` | Whether a day is off, and the holiday's name |
| `business_days(start, end, holidays)` | Working-day count (forms F and G) |
| `pack_lanes(spans, nlanes)` | Split multi-day bars per week row and assign them lanes |
| `choose_scale(start, end)` | Pick day / week granularity from the length of the period (§3.2 B's thresholds) |
| `agenda_entries(start, end, items, holidays)` | The day-by-day rows, with runs of days off collapsed |

Primitives callable from JSON (registered in `build_deck.py::FIGURES`):

| figure | Form | Main arguments |
|---|---|---|
| `month_calendar` | A (including F's overlaid bands) | `month` ("2026-09"), `events`, `weekStart`, `weekNumbers`, `showAdjacent`, `extraHolidays`, `maxPerCell` |
| `day_gantt` | B | `start`, `end`, rows, `today`, `scale` (auto/day/week), `groups` |
| `day_agenda` | C | `start`, `end`, `items`, `columns`, `showEmptyDays` |
| `week_timetable` | D | `week` (the week's first day), `events`, `hours`, `days` |
| `mini_calendars` | E / G | `months`, `marks`, `cols` |
| `calendar_heatmap` | H | `year`, `values`, `buckets` |
| `shift_roster` | I | `start`, `end`, `people`, `codes` |

Rules common to every primitive:

- Dates are accepted only as ISO strings (`YYYY-MM-DD`).
- An out-of-range date, `end < start`, or exceeding capacity raises `ValueError`
  (routed through i18n's `register()`).
- Colours come from the palette tokens. Days off reuse the existing `accent` /
  `muted` tokens rather than introducing new ones.
- The return value is the bottom y of the drawn area, as elsewhere in `Canvas`.

### 4.2 Templates (`slide-templates/calendar/`)

| Phase | id | Display name | Question it answers | Main primitive |
|---|---|---|---|---|
| **P1** | `month-calendar` | Month calendar | What happens on which day this month, and where is it crowded? | `month_calendar` |
| **P1** | `daily-gantt` | Day gantt | How do tasks run in parallel day by day, and when do they end once days off count? | `day_gantt` |
| **P1** | `daily-agenda` | Daily task list | Who does what by when, day by day? | `day_agenda` |
| P2 | `weekly-timetable` | Weekly timetable | What is on this week, at what time and where? | `week_timetable` |
| P2 | `sprint-calendar` | Sprint calendar | What is each sprint's period, working-day count and event dates? | `month_calendar` (overlaid bands) |
| P2 | `year-at-a-glance` | Year calendar | Where do the busy periods and the key dates fall across the year? | `mini_calendars` |
| P2 | `deadline-countdown` | Deadline countdown | How many days — and working days — are left? | `metric` + `mini_calendars` |
| P3 | `activity-heatmap` | Daily heatmap | Which weekdays and periods is the volume concentrated in? | `calendar_heatmap` |
| P3 | `shift-roster` | Shift roster | Who is on each day, and where is cover thin? | `shift_roster` |

- **Week start**: not separate templates for Monday and Sunday, but a
  `weekStart` slot (default `"mon"`). The catalog shows both, so a template
  keeps `example.json` (Monday) beside `example.sun.json` and the catalog
  renders each — whether `examples` needs a key extension was left to be
  confirmed during implementation.
- **Density**: `defaultDensity: "print"`. A presentation variant lowers the
  item count and character limits.
- **inferenceLevel**: `descriptive` throughout. H alone handles figures, so it
  requires `source`.
- **Shared guardrails**, written out concretely in each template:
  - Never mix plan with actuals. A planned figure records in `source` which
    date the plan is from.
  - Mark an unsettled date as provisional (`tentative: true` draws it dashed).
  - Holidays are resolved automatically only for the years the bundled data
    covers; company closures are passed explicitly.
  - Do not cram a cell or a row. Past the limit, split or list it — never
    silently drop items.
  - No real customer or personal names in the examples (this repository is
    public).

### 4.3 The `skills/calendar-slides/` skill

As with `analysis-template-creator`, the shared schema, validation and
registration rules are left to `slide-template-creator`. On top of that it has
two jobs:

1. **Generation (primary)** — take events and tasks and build calendar slides.
   - **Input**: Markdown or CSV tables, Google Sheets, Google Calendar (when
     read over MCP, confirm the calendar and the period with the user first).
   - **Normalization**: dates are put into ISO form, and an ambiguous one
     ("next Wednesday", the year of "9/3") is confirmed rather than guessed.
   - **Choosing the form**: recommend A–I from the question and the length of
     the period (the decision table lives in the skill). Get the user's
     approval before continuing.
   - **Splitting**: `scripts/calendar_pages.py` divides the period into
     per-month, per-week or per-row template inputs.
   - **Validation and generation**: `build_deck.py --dry-run --strict` →
     generate → optionally `slide-qa`. With a master it goes through
     `google-slides-template`, without one through `google-slides`.
2. **Maintenance (secondary)** — the rules specific to adding or changing the
   calendar pack's templates and primitives: the boundary-case list, the
   capacity table, and how to refresh the holiday data.

Bundled files: `SKILL.md` / `SKILL.ja.md` / `references/form-selection.md` (the
form decision table) / `references/capacity.md` (§3.2's capacity table and
thresholds) / `agents/openai.yaml`.

## 5. Verification

### 5.1 Unit tests (`tests/test_calendars.py`, no API)

| Case | Expected |
|---|---|
| 2027-02 (the 1st a Monday, 28 days), Monday start | 4 rows |
| 2026-08 (the 1st a Saturday, 31 days), Monday / Sunday start | 6 rows either way |
| Silver Week, 2026-09 | 9/21 Respect-for-the-Aged Day, 9/22 the citizens' holiday and 9/23 the autumn equinox all resolved |
| ISO weeks across 2026-12-28 – 2027-01-04 | W53 / W1 labels over the year boundary |
| A multi-day event running from month end into the next week | splits into two per-week segments whose lanes do not collide |
| Periods of 31 / 45 / 61 days | `choose_scale` returns day / day (Mondays labelled) / week |
| A year outside the bundled data's range | warns, and fills in no estimate |

### 5.2 Template validation

- `validate_slide_templates.py --pack calendar`, zero audit findings at both
  densities.
- Boundary-size inputs — 5 items on one day, the longest labels, a 6-row month,
  a 31-day period, an 11-row list — kept as `examples/calendar-boundary.json`
  and held to zero findings as well.
- `gantt` is not modified, so no regression is expected in the existing packs;
  `planning` and `scalar-ae` are re-validated anyway.

### 5.3 Visual QA

- Generate the catalog deck and check every page with `slide-qa`,
  concentrating on wrapping in ASCII-heavy labels, the contrast of blue
  Saturdays against red Sundays, breaks in multi-day bars, and where the
  overflow marker sits.
- Confirm batchUpdate splitting holds for the heatmap (~370 shapes).
- Delete the QA files with `cleanup_qa.py` afterwards.

## 6. Registration and surrounding updates

- Registration in `slide-templates/manifest.json`; regenerate
  `references/slide-template-catalog(.ja).md` and update
  `references/i18n/slide-template-catalog.en.json`
  (`build_template_catalog_doc.py`).
- Registration in `build_deck.py::FIGURES`; a new `references/calendars(.ja).md`
  as the primitive reference; an addition to `template-schema`.
- Routing: `commands/forge(.ja).md`, the skill tables in `AGENTS(.ja).md`, and
  the staged-loading table in `references/workflow-contract.md`.
- The pack and template counts and the skill list in `README(.ja).md`; the
  description (skill count) and version in `.claude-plugin/marketplace.json`.
- The English edition of this plan, `calendar-template-plan.md`.

## 7. Order

1. The pure functions in `calendars.py`, the holiday data, and
   `tests/test_calendars.py`.
2. The `month_calendar` / `day_gantt` / `day_agenda` primitives and their
   FIGURES registration.
3. The three P1 templates with examples, validated offline against
   boundary-size inputs.
4. `calendar_pages.py` and the skill documents.
5. Catalog generation and visual QA — take a review here.
6. P2, then P3, added the same way.
7. Surrounding documentation and the version bump.

## 8. Decisions (approved at the sample-deck review, 2026-09-15)

| Topic | Decision |
|---|---|
| First scope | P1 (`month-calendar` / `daily-gantt` / `daily-agenda`) + engine; P2/P3 after review |
| Skill layout | one skill, `calendar-slides`, for generation and maintenance |
| Default week start | `mon`; week numbers only for Monday start |
| Items per day | as many as the lanes allow (1 / 2 / 3 for 6 / 5 / 4 week rows) plus an overflow marker ("+N more"); title before time |
| Gantt scale | all days labelled ≤ 31, Mondays ≤ 60, week columns to 26 weeks |
| Days off | coloured date number plus light fill |
| Holiday data | bundled Cabinet Office CSV; no `jpholiday` dependency |
| Google Calendar import | not in P1 (tables, CSV, Sheets only) |
| Pack | new `calendar` pack; `gantt-schedule` stays in `planning` |

## 9. P1 status (2026-09-15)

Changes from the plan:

- **Titles are one line, ≤ 36 full-width characters.** `governing_message` (17pt
  over 9.0 in) fits ~36.8 per line and a second line covers the calendar header.
- **No `$density` variants in P1**: calendars bottom out at 8.5–9pt; a coarser
  form works better for projection than a larger font.
- **Normalization lives in `calendar_pages.py`** (no separate normalize script);
  `calendars.parse_date` rejects dates without a year.
- `calendar_pages.py` emits rendered slides (`{"slides": [...]}`). Deck specs had
  no `$template` expansion when P1 was written; that is no longer true
  (`build_deck.expand_slide_templates`), but calendars still normalize dates and
  split pages first, so emitting rendered slides remains the right output.
- P1 is commit `a26a338`, on branch `feat/calendar-templates`.

## 10. P2 status (2026-09-15)

Added `weekly-timetable` / `sprint-calendar` / `year-at-a-glance` /
`deadline-countdown`, with the primitives `week_timetable` / `sprint_calendar` /
`year_calendar` / `deadline_countdown`.

Changes from the plan and the prototype:

- **Overlapping events are assigned columns automatically** (`assign_tracks`);
  the prototype had them set by hand. Three or more overlapping events is an
  error — split the page by room or track instead.
- **A 30-minute event is drawn as an empty frame with the label over it.** At
  roughly 0.18in high, Slides' own vertical padding pushed the text outside
  the frame.
- **A sprint's planning, review and release days are placed automatically** on
  the first and last working days. A guardrail says not to use this template
  where the real dates differ.
- **The deadline countdown covers only a deadline in the current or next
  month.** Anything further out belongs in a month calendar or a day gantt.
- The year calendar stays 7pt handout-only, as prototyped; for projection it
  points at `planning/gantt-schedule`.
- P2 is commit `9333528`.

## 11. P3 status (2026-09-15)

Added `activity-heatmap` / `shift-roster` with the primitives
`calendar_heatmap` / `shift_roster`, completing the nine forms in the plan.

Changes from the plan and the prototype:

- **Missing data and zero are distinguished.** A day with no value is white
  with a border, zero takes the lightest fill, and the legend gains a "no data"
  entry only when something is actually missing.
- **The colour breaks are quantiles within the period** (5 levels by default,
  3–7 configurable). The legend prints the break values, and a guardrail says
  not to compare colours against a figure covering a different period.
- **The aggregate cards are computed by the primitive** — weekday averages,
  monthly totals, holiday average. It draws no interpretation.
- **Cell size follows height as well as width.** Over a short period the cells
  would otherwise grow past the available height, so both dimensions decide it,
  and anything under 0.1in is an error.
- **A roster's schedule is passed as one character per day**, which keeps the
  slot JSON short and makes a mismatch with the day count easy to detect.
  Whether a code counts towards headcount is specified per code.
- `calendar_pages.py` splits the heatmap every 52 weeks, and the roster by
  month and by 12 people.

## See also

- [Calendar diagrams (`calendars.py`)](calendars.md)
- [Slide Template Catalog (All 108 Types)](slide-template-catalog.md)
- [Deck workflow contract](workflow-contract.md)
