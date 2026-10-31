from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_deck as bd  # noqa: E402
import reading_level as rl  # noqa: E402


def deck(*slides, **top):
    return {"title": "t", "readingLevel": "eli5", "slides": list(slides), **top}


def slide(title="データは金庫にしまう", body=None, **extra):
    s = {"layout": "CONTENT", "title": title, **extra}
    if body is not None:
        s["body"] = body
    return s


class TermTest(unittest.TestCase):
    def test_an_unexplained_acronym_is_reported(self):
        found = rl.audit(deck(slide(body=["APIで注文を受け取る"])))
        self.assertEqual(len(found), 1)
        self.assertIn("'API'", found[0])

    def test_a_bracket_after_or_around_the_term_explains_it(self):
        for line in ("API（ソフト同士の窓口）で受け取る",
                     "ソフト同士の窓口（API）で受け取る",
                     "Orders come in through the API (a front door)"):
            with self.subTest(line=line):
                self.assertEqual(rl.audit(deck(slide(body=[line]))), [])

    def test_only_the_first_use_needs_the_explanation(self):
        spec = deck(slide(body=["API（窓口）で受け取る"]),
                    slide(title="APIは速い", body=["APIを増やす"]))
        self.assertEqual(rl.audit(spec), [])

    def test_explaining_it_later_is_too_late(self):
        spec = deck(slide(body=["APIで受け取る"]),
                    slide(body=["API（窓口）とは"]))
        self.assertEqual(len(rl.audit(spec)), 1)

    def test_plain_terms_are_not_reported(self):
        spec = deck(slide(body=["AIが手伝う"]), plainTerms=["AI"])
        self.assertEqual(rl.audit(spec), [])

    def test_a_placeholder_like_20XX_is_not_a_term(self):
        self.assertEqual(rl.audit(deck(slide(body=["20XX年に始める"]))), [])

    def test_figure_labels_are_read_but_colors_are_not(self):
        fig = {"type": "box", "text": "OCCで守る", "fill": "#FFAA00",
               "color": "theme:ACCENT1"}
        found = rl.audit(deck(slide(figures=[fig])))
        self.assertEqual(len(found), 1)
        self.assertIn("'OCC'", found[0])

    def test_speaker_notes_are_left_alone(self):
        spec = deck(slide(body=["速くなる"], notes="OCC と 2PC の詳細"))
        self.assertEqual(rl.audit(spec), [])


class ShapeTest(unittest.TestCase):
    def test_a_long_title_is_reported(self):
        found = rl.audit(deck(slide(title="あ" * 31)))
        self.assertEqual(len(found), 1)
        self.assertIn("title", found[0])

    def test_a_long_sentence_is_reported_but_two_short_ones_pass(self):
        long = "い" * 41 + "。"
        self.assertEqual(len(rl.audit(deck(slide(body=[long])))), 1)
        two = "い" * 30 + "。" + "う" * 30 + "。"
        self.assertEqual(rl.audit(deck(slide(body=[two]))), [])

    def test_english_is_measured_at_half_width(self):
        sentence = "Your data sits in a safe that only you can open."
        self.assertEqual(rl.audit(deck(slide(body=[sentence]))), [])

    def test_more_than_three_points_is_reported(self):
        found = rl.audit(deck(slide(body=["一", "二", "三", "四"])))
        self.assertEqual(len(found), 1)
        self.assertIn("4", found[0])

    def test_headings_do_not_count_as_points(self):
        body = [{"text": "見出し", "role": "heading"}, "一", "二", "三"]
        self.assertEqual(rl.audit(deck(slide(body=body))), [])

    def test_an_indented_sub_point_is_reported(self):
        found = rl.audit(deck(slide(body=["一", "    細かい話"])))
        self.assertEqual(len(found), 1)
        self.assertIn("細かい話", found[0])


class SpecTest(unittest.TestCase):
    def test_a_standard_deck_is_not_audited(self):
        spec = deck(slide(title="あ" * 50, body=["APIで受ける"] * 5))
        spec["readingLevel"] = "standard"
        self.assertEqual(rl.audit(spec), [])
        del spec["readingLevel"]
        self.assertEqual(rl.audit(spec), [])

    def test_an_unknown_level_and_bad_plain_terms_are_rejected(self):
        problems = rl.check_spec({"readingLevel": "kids", "plainTerms": "AI"})
        self.assertEqual(len(problems), 2)

    def test_validate_figures_carries_the_spec_check(self):
        problems = bd.validate_figures({"readingLevel": "kids", "slides": []}, {})
        self.assertTrue(any("readingLevel" in p for p in problems))


class DryRunTest(unittest.TestCase):
    def run_dry(self, spec):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "deck.json"
            path.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_deck.py"),
                 "--template", str(ROOT / "templates" / "blank-16x9.json"),
                 "--spec", str(path), "--dry-run", "--strict"],
                capture_output=True, text=True, cwd=ROOT)

    def layout(self):
        tpl = json.loads((ROOT / "templates" / "blank-16x9.json")
                         .read_text(encoding="utf-8"))
        roles = tpl.get("roles") or {}
        return "CONTENT" if "CONTENT" in roles else next(iter(tpl["layouts"]))

    def test_strict_dry_run_fails_on_a_finding_and_passes_when_clean(self):
        bad = deck({"layout": self.layout(), "title": "APIで受け取る"})
        result = self.run_dry(bad)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("ELI5", result.stderr)
        good = deck({"layout": self.layout(), "title": "窓口（API）で受け取る"})
        result = self.run_dry(good)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("ELI5", result.stdout)


if __name__ == "__main__":
    unittest.main()
