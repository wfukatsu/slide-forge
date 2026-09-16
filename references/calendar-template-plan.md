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
- **Overflow order**: truncate → "+N件" with a detail page → coarser scale → split
  into pages with "(1/3)".

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

Bundle the Cabinet Office CSV (Shift_JIS, 1955–, CC BY-compatible terms) as
UTF-8 `assets/holidays/jp.csv`; refresh with `scripts/update_holidays.py`; no
network at generation time; warn (never guess) for uncovered years; company
closures via `extraHolidays`.

## 4. What to build

- `scripts/calendars.py`: pure date functions (`month_weeks`, `iso_week_label`,
  `fiscal_quarter`, `holidays_for`, `business_days`, `pack_lanes`, `choose_scale`,
  `agenda_entries`) and the `CalendarMixin` primitives registered in
  `build_deck.py::FIGURES`.
- Templates:

| Phase | id | Question |
|---|---|---|
| **P1** | `month-calendar` | What happens on which day this month, and where is it crowded? |
| **P1** | `daily-gantt` | How do tasks overlap day by day, and when do they end once days off count? |
| **P1** | `daily-agenda` | Who does what by when, day by day? |
| P2 | `weekly-timetable`, `sprint-calendar`, `year-at-a-glance`, `deadline-countdown` | |
| P3 | `activity-heatmap`, `shift-roster` | |

- Skill `skills/calendar-slides/`: intake → normalize → choose form → split →
  approve → validate/generate → QA, plus pack maintenance rules.

## 5. Verification

Unit tests (4/6-row months, silver week holidays, ISO week across New Year,
multi-day lanes, 31/45/61-day scales, uncovered years), zero-finding template
validation including boundary inputs, and thumbnail QA of the catalog deck.

## 6. Registration

Manifest, catalog docs and English sidecar, FIGURES, `references/calendars.md`,
routing tables (forge, AGENTS, GEMINI, workflow contract), README counts and
skill tables, marketplace skill list.

## 7. Order

Engine and tests → P1 primitives → P1 templates → splitter and skill → catalog
and QA (review) → P2 → P3 → docs and release.

## 8. Decisions (approved at the sample-deck review, 2026-09-15)

| Topic | Decision |
|---|---|
| First scope | P1 (`month-calendar` / `daily-gantt` / `daily-agenda`) + engine; P2/P3 after review |
| Skill layout | one skill, `calendar-slides`, for generation and maintenance |
| Default week start | `mon`; week numbers only for Monday start |
| Items per day | as many as the lanes allow (1 / 2 / 3 for 6 / 5 / 4 week rows) + "+N件"; title before time |
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
- P2 templates are not started; `form-selection.md` in the skill lists fallbacks.
