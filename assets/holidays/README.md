# Holiday data

`jp.csv` lists Japanese national holidays (including substitute holidays and
citizens' holidays) as `date,name` with ISO dates. `scripts/calendars.py`
reads it to colour days off in the calendar templates.

- Source: 内閣府「国民の祝日」について — <https://www8.cao.go.jp/chosei/shukujitsu/gaiyou.html>
  (CSV: <https://www8.cao.go.jp/chosei/shukujitsu/syukujitsu.csv>)
- Modification: converted from Shift_JIS to UTF-8 and from `YYYY/M/D` to
  `YYYY-MM-DD`; rows sorted by date. No holidays were added or removed.
- Refresh: `.venv/bin/python scripts/update_holidays.py` (`--check` to compare
  only). The Cabinet Office announces the next year's equinox days each
  February, so refresh at least once a year.

Company closures (year-end, summer shutdown) are not part of this file; pass
them to a template as `extraHolidays`.
