*[日本語](events.ja.md)*
# Event Announcement Diagrams (events.py)

Usage of `EventMixin`, mixed into `diagrams.Canvas`. It codifies the parts commonly
needed for seminar / study-group / conference announcement decks, supporting all
three formats: **online, in-person (offline), and hybrid**. Everything is drawn
with shapes only, so no API keys or network access are needed, and colors follow
the template's palette. Coordinates are in inches; the return value is the
bottom y of the drawn area.

Also usable from a deck spec (JSON) via the same type names under `figures`. See
`examples/event-announcement.json` (a 4-slide demo: online / offline / hybrid /
program).

**Content must always come from the user's material.** Never fill in dates,
venues, URLs, or speaker names on your own. For an unconfirmed URL, use wording
like "details will be sent after registration."

## Which one to use

| What to show | Use | Notes |
|---|---|---|
| A format label | `event_mode_badge` | Also added automatically via `event_overview`'s `mode` |
| Date/time, venue, fee, capacity | `event_overview` | An item list with pictograms |
| Program (time × content) | `event_timetable` | Rule of thumb: up to 8 rows per slide |
| Speaker lineup | `event_speakers` | Up to 5 people per row; wrap to 2 rows beyond that |
| How to attend (venue / streaming) | `event_access` | `mode="hybrid"` places two panels side by side |

Pictograms commonly used for event announcements: `calendar` (date/time), `pin`
(venue), `browser` (streaming), `coin` (fee), `people` (capacity), `mail`
(registration), `clock` (reception/deadline).

## event_overview — Event overview

```python
d.event_overview(x, y, w, rows,
                 mode=None,      # "online" / "offline" / "hybrid"。渡すと先頭にバッジ
                 size=11, term_w=1.15, icon_size=0.34, row_h=0.5)
```

- `rows` is a list of `[pictogram name, item, value]`.
- If a value wraps to 2 lines, widen `row_h` (it isn't widened automatically —
  overflow is caught by `audit_text_fit`).

```json
{ "type": "event_overview", "x": 0.5, "y": 1.15, "w": 4.4, "mode": "online",
  "rows": [
    ["calendar", "日時", "2026年9月18日(金) 15:00–17:00"],
    ["browser",  "配信", "Zoom ウェビナー"],
    ["coin",     "参加費", "無料（事前登録制）"]
  ] }
```

## event_timetable — Program

```python
d.event_timetable(x, y, w, rows,
                  size=11, time_w=1.55, row_h=0.42, zebra=True)
```

- `rows` is `[time, content]` or `[time, content, speaker]`. Time is drawn as-is
  from a string like `"15:00–15:30"`.
- The speaker column's width is derived automatically from the longest name.
  For long content, rewrite it to be shorter rather than letting it wrap in the
  content column (a length that fits on one line reads best).
- When there are many rows, split into 2 slides rather than compressing
  `row_h` (rule of thumb: up to 8 rows per slide).

## event_speakers — Speaker cards

```python
d.event_speakers(x, y, w, speakers,
                 size=10, icon="person", gap=0.24)
```

- `speakers` is `[name, title]` or `[name, title, talk title]`. **Up to 5 people
  per row** (for 6 or more, call it twice to wrap into 2 rows).
- Height is fixed (1.28 up through title, 1.62 with a talk title). Place the
  next block starting from the returned y.
- Use only **confirmed information about real speakers** for names and titles.

## event_access — How-to-attend panel

```python
d.event_access(x, y, w, h, mode="hybrid",
               venue={"name": …, "address": …, "access": …},   # offline / hybrid
               online={"platform": …, "url": …, "note": …},    # online / hybrid
               size=10.5)
```

- `mode="offline"` shows only the venue panel (`venue` required), `"online"`
  shows only the streaming panel (`online` required), `"hybrid"` shows both
  side by side (both required).
- Decide the panel height by hand based on row count: heading 0.62 + 0.34 per
  row. For 3 rows (name / address / access), h ≥ 1.7; for hybrid with 2 rows
  each, h ≥ 1.4.
- `venue.access` (e.g. nearest station) and `online.note` (e.g. archived
  recording) are optional.

```json
{ "type": "event_access", "x": 0.5, "y": 3.75, "w": 9.0, "h": 1.4,
  "mode": "hybrid",
  "venue":  {"name": "○○カンファレンスセンター 3F", "address": "東京都港区○○ 1-2-3"},
  "online": {"platform": "Zoom ウェビナー", "url": "視聴 URL は申込後にご案内"} }
```

## event_mode_badge — Format badge

```python
d.event_mode_badge(x, y, mode, label=None, size=10)
```

Default wording is "Online Event" / "In-Person Event" / "Hybrid Event." Use
`label` to swap in something like "Online Event (Free)." When `mode` is passed
to `event_overview`, this is called internally, so using it standalone is mainly
for placing just a badge on the cover or closing slide.

## Layout convention (fitting one TITLE_ONLY slide)

- **Overview + how to attend**: `event_overview` (left, w 4.4) + `event_access`
  (right, w 4.35).
- **Hybrid overview**: `event_overview` full-width (w 8.9) at the top, with
  `event_access mode="hybrid"` (w 9.0, h 1.4) below.
- **Program + speakers**: `event_timetable` (w 9.0, 5 rows) with `event_speakers`
  (w 9.0, 3 people) below it — see the 4th example.
