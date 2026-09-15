from __future__ import annotations

import datetime as dt
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_deck as bd  # noqa: E402
import calendar_pages  # noqa: E402
import calendars as cal  # noqa: E402
from slide_templates import load_example, load_template, render_template  # noqa: E402

D = dt.date
BLANK = json.loads((ROOT / "templates" / "blank-16x9.json").read_text(encoding="utf-8"))


class DateEngineTest(unittest.TestCase):
    """The pure date functions behind the calendar diagrams."""

    def test_month_rows_follow_the_week_start(self) -> None:
        # Feb 2027 starts on a Monday and has 28 days: 4 rows Monday-first
        self.assertEqual(len(cal.month_weeks(2027, 2, "mon")), 4)
        self.assertEqual(len(cal.month_weeks(2027, 2, "sun")), 5)
        # Aug 2026 starts on a Saturday with 31 days: 6 rows either way
        self.assertEqual(len(cal.month_weeks(2026, 8, "mon")), 6)
        self.assertEqual(len(cal.month_weeks(2026, 8, "sun")), 6)
        self.assertEqual(cal.month_weeks(2026, 9, "sun")[0][0].weekday(), 6)
        with self.assertRaises(ValueError):
            cal.month_weeks(2026, 9, "sat")

    def test_bundled_holidays_include_substitute_days(self) -> None:
        hol = cal.holidays_for([2026])
        self.assertEqual(hol[D(2026, 9, 21)], "敬老の日")
        self.assertEqual(hol[D(2026, 9, 22)], "休日")   # citizens' holiday
        self.assertEqual(hol[D(2026, 9, 23)], "秋分の日")
        self.assertIn(D(2026, 5, 6), hol)               # substitute for 5/3 (Sunday)

    def test_business_days_skip_weekends_holidays_and_closures(self) -> None:
        hol = cal.holidays_for([2026])
        self.assertEqual(cal.business_days(D(2026, 9, 16), D(2026, 9, 25), hol), 5)
        closed = cal.holidays_for([2026], [["2026-09-24", "2026-09-25", "創立記念"]])
        self.assertEqual(cal.business_days(D(2026, 9, 16), D(2026, 9, 25), closed), 3)

    def test_iso_week_and_fiscal_quarter_cross_the_new_year(self) -> None:
        self.assertEqual(cal.iso_week_label(D(2026, 12, 28)), "2026-W53")
        self.assertEqual(cal.iso_week_label(D(2027, 1, 4)), "2027-W01")
        self.assertEqual(cal.fiscal_quarter(D(2026, 4, 1)), (2026, 1))
        self.assertEqual(cal.fiscal_quarter(D(2027, 3, 31)), (2026, 4))
        self.assertEqual(cal.fiscal_quarter(D(2026, 1, 15), start_month=1), (2026, 1))

    def test_scale_switches_to_weeks_after_sixty_days(self) -> None:
        start = D(2026, 9, 1)
        self.assertEqual(cal.choose_scale(start, start + dt.timedelta(days=30)), "day")
        self.assertEqual(cal.choose_scale(start, start + dt.timedelta(days=59)), "day")
        self.assertEqual(cal.choose_scale(start, start + dt.timedelta(days=60)), "week")

    def test_dates_need_a_year(self) -> None:
        self.assertEqual(cal.parse_date("2026/9/3"), D(2026, 9, 3))
        self.assertEqual(cal.parse_month("2026/9"), (2026, 9))
        for bad in ("9/3", "", "2026-02-30", "26-09-03"):
            with self.assertRaises(ValueError):
                cal.parse_date(bad)

    def test_lanes_never_collide(self) -> None:
        spans = [(0, 4, "a"), (2, 6, "b"), (3, 3, "c"), (5, 6, "d")]
        placed, overflow = cal.pack_lanes(spans, 2)
        seen = set()
        for lane, (c0, c1, _) in placed:
            for c in range(c0, c1 + 1):
                self.assertNotIn((lane, c), seen)
                seen.add((lane, c))
        self.assertEqual([s[2] for s in overflow], ["c"])

    def test_agenda_collapses_a_run_of_days_off(self) -> None:
        hol = cal.holidays_for([2026])
        items = [["2026-09-18", "判定会議", "PM", "15:00", "予定"],
                 ["2026-09-24", "移行検証", "移行", "", "予定"]]
        entries = cal.agenda_entries("2026-09-18", "2026-09-24", items, hol)
        self.assertEqual([e[0] for e in entries], ["day", "off", "day"])
        self.assertEqual(entries[1][1:], (D(2026, 9, 19), D(2026, 9, 23)))
        with self.assertRaises(ValueError):
            cal.agenda_entries("2026-09-18", "2026-09-24",
                               [["2026-10-01", "範囲外", "", "", "予定"]], hol)


class PhaseTwoEngineTest(unittest.TestCase):
    """Pure functions behind the timetable, sprint, year and countdown forms."""

    def test_times_parse_and_format(self) -> None:
        self.assertEqual(cal.parse_time("9:30"), 9.5)
        self.assertEqual(cal.parse_time("24:00"), 24.0)
        self.assertEqual(cal.format_time(13.5), "13:30")
        for bad in ("930", "25:00", "9:60", ""):
            with self.assertRaises(ValueError):
                cal.parse_time(bad)

    def test_overlapping_events_share_tracks(self) -> None:
        tracks = cal.assign_tracks([(13, 17), (15, 16), (9, 12), (12, 13)])
        self.assertEqual(tracks, [(0, 2), (1, 2), (0, 1), (0, 1)])
        three = cal.assign_tracks([(9, 12), (10, 11), (10.5, 11.5)])
        self.assertEqual(max(n for _, n in three), 3)

    def test_sprints_lose_working_days_to_holidays(self) -> None:
        hol = cal.holidays_for([2026])
        ranges = cal.sprint_ranges("2026-09-28", 4)
        self.assertEqual(ranges[1], (D(2026, 10, 12), D(2026, 10, 25)))
        work = [cal.business_days(s, e, hol) for s, e in ranges]
        self.assertEqual(work, [10, 9, 9, 10])   # スポーツの日, 文化の日

    def test_fiscal_year_months_cross_the_new_year(self) -> None:
        months = cal.months_from("2026-04")
        self.assertEqual((months[0], months[8], months[11]), ((2026, 4), (2026, 12), (2027, 3)))

    def test_countdown_counts_calendar_and_working_days(self) -> None:
        hol = cal.holidays_for([2026])
        today, deadline = D(2026, 9, 15), D(2026, 10, 14)
        self.assertEqual((deadline - today).days, 29)
        self.assertEqual(cal.business_days(today, deadline - dt.timedelta(days=1), hol), 17)


class PhaseThreeEngineTest(unittest.TestCase):
    """Pure functions behind the heatmap and the shift roster."""

    def test_quantile_buckets(self) -> None:
        cuts = cal.quantile_cuts(list(range(100)), 5)
        self.assertEqual(cuts, [20, 40, 60, 80])
        self.assertEqual([cal.bucket_of(v, cuts) for v in (0, 20, 21, 99)], [0, 0, 1, 4])
        self.assertEqual(cal.quantile_cuts([], 5), [])

    def test_series_rejects_negative_and_duplicate_days(self) -> None:
        self.assertEqual(cal.normalize_series([["2026/9/1", 3]]), {D(2026, 9, 1): 3.0})
        for bad in ([["2026-09-01", -1]], [["2026-09-01", 1], ["2026-09-01", 2]],
                    [["2026-09-01", True]], [["2026-09-01"]]):
            with self.assertRaises(ValueError):
                cal.normalize_series(bad)

    def test_roster_counts_only_counting_codes(self) -> None:
        codes = [["日", "日勤", "primary", True], ["夜", "夜勤", "dark", True],
                 ["休", "休み", "muted", False]]
        days, code_map, rows = cal.normalize_roster(
            "2026-10-01", "2026-10-03", [["A", "日夜休"], ["B", "休日日"]], codes)
        self.assertEqual(len(days), 3)
        self.assertEqual(cal.roster_totals(rows, code_map), ([1, 2, 1], [2, 2]))
        with self.assertRaises(ValueError):
            cal.normalize_roster("2026-10-01", "2026-10-03", [["A", "日夜"]], codes)
        with self.assertRaises(ValueError):
            cal.normalize_roster("2026-10-01", "2026-10-03", [["A", "日夜X"]], codes)


class TemplateRenderTest(unittest.TestCase):
    """Each calendar template's example draws with zero audit findings."""

    TEMPLATES = ("month-calendar", "daily-gantt", "daily-agenda", "weekly-timetable",
                 "sprint-calendar", "year-at-a-glance", "deadline-countdown",
                 "activity-heatmap", "shift-roster")

    def test_phase_three_boundaries_pass_the_audit(self) -> None:
        short_values = [[d.isoformat(), (d.day * 7) % 23]
                        for d in cal.date_range(D(2026, 7, 1), D(2026, 9, 30))
                        if d.day != 15]
        twelve = [[f"担当{n:02d}", ("日夜休待" * 8)[n:n + 14]] for n in range(12)]
        cases = [
            ("activity-heatmap", {"start": "2026-07-01", "end": "2026-09-30",
                                  "values": short_values, "levels": 3}),
            ("activity-heatmap", {"monthly": False, "summary": False}),
            ("shift-roster", {"start": "2026-10-01", "end": "2026-10-14", "people": twelve,
                              "codes": [["日", "日勤", "primary", True],
                                        ["夜", "夜勤", "dark", True],
                                        ["休", "休み", "muted", False],
                                        ["待", "待機", "warning", False]],
                              "minStaff": 0}),
        ]
        for template_id, override in cases:
            with self.subTest(template_id, **{k: str(v)[:20] for k, v in override.items()}):
                self.assertEqual(self._audit(template_id, **override), [])

    def test_phase_three_rejects_unreadable_input(self) -> None:
        cases = {
            "activity-heatmap": {"end": "2026-06-30"},
            "shift-roster": {"end": "2026-11-01"},
        }
        for template_id, override in cases.items():
            with self.subTest(template_id):
                self.assertTrue(self._audit(template_id, **override))

    def _audit(self, template_id: str, **override) -> list[str]:
        template, _ = load_template(template_id)
        example, _ = load_example(template_id)
        slide = render_template(template, {**example, **override})
        return bd.audit_figures(BLANK, {"slides": [slide]})

    def test_phase_two_boundaries_pass_the_audit(self) -> None:
        cases = [
            ("weekly-timetable", {"days": 7, "week": "2026-10-12", "events": [
                ["2026-10-17", "10:00", "10:30", "短い打合せ", "", ""],
                ["2026-10-12", "09:00", "11:00", "祝日出勤", "本社", "danger"]]}),
            ("weekly-timetable", {"week": "2026-09-21", "events": [
                ["2026-09-24", "09:00", "12:00", "連休明け定例", "会議室", ""]]}),
            ("sprint-calendar", {"lengthDays": 7, "sprints": [
                [str(n), f"ゴール {n}", n % 2 == 0] for n in range(1, 9)]}),
            ("deadline-countdown", {"today": "2026-12-20", "deadline": "2027-01-08",
                                    "label": "年明けの本番リリースまで", "checkpoints": []}),
        ]
        for template_id, override in cases:
            with self.subTest(template_id, **{k: str(v)[:20] for k, v in override.items()}):
                self.assertEqual(self._audit(template_id, **override), [])

    def test_phase_two_rejects_unreadable_input(self) -> None:
        cases = {
            "weekly-timetable": {"events": [
                ["2026-10-05", "10:00", "12:00", "A", "", ""],
                ["2026-10-05", "10:30", "11:30", "B", "", ""],
                ["2026-10-05", "11:00", "11:45", "C", "", ""]]},
            "sprint-calendar": {"start": "2026-09-29"},
            "year-at-a-glance": {"marks": [["2027-04-01", "", "範囲外", "key"]]},
            "deadline-countdown": {"deadline": "2026-12-01"},
        }
        for template_id, override in cases.items():
            with self.subTest(template_id):
                self.assertTrue(self._audit(template_id, **override))

    def test_examples_pass_the_figure_audit(self) -> None:
        for template_id in self.TEMPLATES:
            with self.subTest(template_id):
                template, _ = load_template(template_id)
                example, _ = load_example(template_id)
                slide = render_template(template, example)
                self.assertEqual(bd.audit_figures(BLANK, {"slides": [slide]}), [])

    def test_longest_title_stays_clear_of_the_calendar(self) -> None:
        for template_id in self.TEMPLATES:
            with self.subTest(template_id):
                template, _ = load_template(template_id)
                example, _ = load_example(template_id)
                limit = template["slots"]["title"]["maxLength"]
                slide = render_template(template, {**example, "title": "あ" * limit})
                self.assertEqual(bd.audit_figures(BLANK, {"slides": [slide]}), [])

    def test_sunday_start_and_boundary_months_pass_the_audit(self) -> None:
        template, _ = load_template("month-calendar")
        example, _ = load_example("month-calendar")
        for month, start in (("2026-09", "sun"), ("2026-08", "mon"), ("2027-02", "mon")):
            with self.subTest(month=month, week_start=start):
                data = {**example, "month": month, "weekStart": start}
                slide = render_template(template, data)
                self.assertEqual(bd.audit_figures(BLANK, {"slides": [slide]}), [])

    def test_week_scale_gantt_passes_the_audit(self) -> None:
        template, _ = load_template("daily-gantt")
        data = {
            "title": "週単位に切り替わる長期計画",
            "start": "2026-09-07", "end": "2027-03-05",
            "rows": [["group", "開発", "", "", "", 0],
                     ["task", "基本設計", "設計", "2026-09-07", "2026-10-16", 0.3],
                     ["task", "結合テスト", "QA", "2027-01-04", "2027-02-05", 0],
                     ["milestone", "本番リリース", "全員", "2027-02-22", "", 0]],
            "today": "2026-09-15",
            "extraHolidays": [["2026-12-29", "年末年始"], ["2026-12-30", "年末年始"]],
            "source": "テスト用データ",
        }
        slide = render_template(template, data)
        self.assertEqual(bd.audit_figures(BLANK, {"slides": [slide]}), [])

    def test_primitives_reject_unreadable_input(self) -> None:
        cases = {
            "daily-gantt": {"rows": [["task", "範囲外", "", "2026-11-01", "2026-11-02", 0]]},
            "month-calendar": {"events": [["2026-09-01", "", "件名", "purple", ""]]},
            "daily-agenda": {"items": [["2026-09-14", "作業", "", "", "保留"]]},
        }
        for template_id, override in cases.items():
            with self.subTest(template_id):
                template, _ = load_template(template_id)
                example, _ = load_example(template_id)
                slide = render_template(template, {**example, **override})
                findings = bd.audit_figures(BLANK, {"slides": [slide]})
                self.assertTrue(findings, template_id)


class CalendarPagesTest(unittest.TestCase):
    """scripts/calendar_pages.py splits a period the way the templates can hold it."""

    def test_agenda_splits_by_week(self) -> None:
        items = [[f"2026-09-{d:02d}", f"作業 {d}", "PM", "", "予定"]
                 for d in (14, 15, 16, 24, 25, 28, 29)]
        slides = calendar_pages.build_slides({
            "template": "daily-agenda", "title": "9月後半の作業", "source": "テスト",
            "start": "2026-09-14", "end": "2026-10-02", "items": items})
        self.assertEqual(len(slides), 3)
        agenda = [f for f in slides[0]["figures"] if f["type"] == "day_agenda"][0]
        self.assertEqual((agenda["start"], agenda["end"]), ("2026-09-14", "2026-09-16"))
        title = [f for f in slides[0]["figures"] if f["type"] == "governing_message"][0]
        self.assertTrue(title["text"].endswith("（1/3）"))

    def test_month_calendar_makes_one_page_per_month(self) -> None:
        slides = calendar_pages.build_slides({
            "template": "month-calendar", "titles": ["9月", "10月"], "source": "テスト",
            "events": [["2026/9/25", "2026/10/2", "切替準備", "success", ""],
                       ["2026/10/14", "", "本番切替", "danger", ""]]})
        months = [[f for f in s["figures"] if f["type"] == "month_calendar"][0]["month"]
                  for s in slides]
        self.assertEqual(months, ["2026-09", "2026-10"])

    def test_gantt_rejects_a_period_longer_than_26_weeks(self) -> None:
        with self.assertRaises(ValueError):
            calendar_pages.build_slides({
                "template": "daily-gantt", "title": "長すぎる", "source": "テスト",
                "start": "2026-04-01", "end": "2027-03-31",
                "rows": [["task", "全体", "", "2026-04-01", "2027-03-31", 0]]})

    def test_timetable_makes_one_page_per_week(self) -> None:
        slides = calendar_pages.build_slides({
            "template": "weekly-timetable", "title": "研修 2 週間", "source": "テスト",
            "events": [["2026/10/5", "9:00", "12:00", "講義", "A", ""],
                       ["2026-10-14", "13:00", "15:00", "演習", "B", "success"]]})
        weeks = [[f for f in s["figures"] if f["type"] == "week_timetable"][0]["week"]
                 for s in slides]
        self.assertEqual(weeks, ["2026-10-05", "2026-10-12"])

    def test_sprints_split_every_eight_weeks(self) -> None:
        slides = calendar_pages.build_slides({
            "template": "sprint-calendar", "title": "下期スプリント", "source": "テスト",
            "start": "2026-09-28",
            "sprints": [[str(n), f"ゴール {n}", False] for n in range(12, 18)]})
        starts = [[f for f in s["figures"] if f["type"] == "sprint_calendar"][0]["start"]
                  for s in slides]
        self.assertEqual(starts, ["2026-09-28", "2026-11-23"])

    def test_roster_splits_by_month_and_team(self) -> None:
        days = cal.date_range(D(2026, 10, 20), D(2026, 11, 10))
        people = [[f"担当{n:02d}", "日" * len(days)] for n in range(14)]
        slides = calendar_pages.build_slides({
            "template": "shift-roster", "title": "当番表", "source": "テスト",
            "start": "2026-10-20", "end": "2026-11-10", "people": people,
            "codes": [["日", "日勤", "primary", True]]})
        figs = [[f for f in s["figures"] if f["type"] == "shift_roster"][0] for s in slides]
        self.assertEqual([(f["start"], len(f["people"])) for f in figs],
                         [("2026-10-20", 12), ("2026-10-20", 2),
                          ("2026-11-01", 12), ("2026-11-01", 2)])
        self.assertEqual(len(figs[0]["people"][0][1]), 12)

    def test_heatmap_splits_every_52_weeks(self) -> None:
        values = [[d.isoformat(), 1] for d in cal.date_range(D(2025, 1, 1), D(2026, 6, 30))]
        slides = calendar_pages.build_slides({
            "template": "activity-heatmap", "title": "長期の件数", "source": "テスト",
            "start": "2025-01-01", "end": "2026-06-30", "values": values})
        figs = [[f for f in s["figures"] if f["type"] == "calendar_heatmap"][0] for s in slides]
        self.assertEqual([(f["start"], f["end"]) for f in figs],
                         [("2025-01-01", "2025-12-30"), ("2025-12-31", "2026-06-30")])

    def test_gantt_repeats_the_group_heading_across_pages(self) -> None:
        rows = [["group", "開発", "", "", "", 0]] + [
            ["task", f"作業{i}", "", "2026-09-14", "2026-09-18", 0] for i in range(14)]
        slides = calendar_pages.build_slides({
            "template": "daily-gantt", "title": "作業一覧", "source": "テスト",
            "start": "2026-09-14", "end": "2026-10-14", "rows": rows})
        self.assertEqual(len(slides), 2)
        second = [f for f in slides[1]["figures"] if f["type"] == "day_gantt"][0]
        self.assertEqual(second["rows"][0][:2], ["group", "（続き）開発"])


if __name__ == "__main__":
    unittest.main()
