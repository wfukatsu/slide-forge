from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_deck as bd  # noqa: E402
from diagrams import DEFAULT_LABEL_LANG, Canvas  # noqa: E402


def canvas(lang=None):
    deck = bd._StubDeck()
    if lang:
        deck.lang = lang
    return Canvas(deck, "slide", {})


class CanvasLabelTest(unittest.TestCase):
    def test_the_canvas_takes_its_language_from_the_deck(self):
        self.assertEqual(canvas("en")._label("pages.source"), "Source")
        self.assertEqual(canvas()._label("pages.source"), "出典")

    def test_a_deck_without_a_language_falls_back_to_the_default(self):
        self.assertEqual(canvas().lang, DEFAULT_LABEL_LANG)

    def test_the_callers_own_word_wins(self):
        # A caller that passes a label is not asking for a translation.
        self.assertEqual(canvas("en")._label("pages.source", "参考"), "参考")

    def test_every_drawing_label_exists_in_both_languages(self):
        keys = ["pages.so_what", "pages.source", "pages.exhibit",
                "iceberg.above", "iceberg.below", "charts.pie_alt",
                "calendars.week", "calendars.sprint", "calendars.count_unit"]
        ja, en = canvas(), canvas("en")
        for key in keys:
            with self.subTest(key=key):
                # resolve_label falls back to Japanese, so an English string
                # equal to the Japanese one means the entry is missing.
                self.assertNotEqual(ja._label(key), en._label(key))


class SpecLanguageTest(unittest.TestCase):
    DATA = {"title": "現状とあるべき姿",
            "asis": ["手作業の突合が残る", "復旧が属人化"],
            "tobe": ["突合を自動化", "手順を文書化"],
            "gaps": [["自動化の不足", "突合スクリプトが未整備"]],
            "source": "現場ヒアリング"}

    def spec(self, lang=None):
        spec = {"slides": [{"$template": "gap-analysis", "data": dict(self.DATA)}]}
        if lang:
            spec["lang"] = lang
        return spec

    def titles(self, spec):
        _, problems = bd.expand_slide_templates(spec)
        self.assertEqual(problems, [])
        figure = next(f for f in spec["slides"][0]["figures"] if "beforeTitle" in f)
        return figure["beforeTitle"], figure["afterTitle"]

    def test_a_spec_level_language_reaches_the_template_labels(self):
        self.assertEqual(self.titles(self.spec("en")),
                         ("As-Is (current)", "To-Be (target)"))

    def test_the_default_stays_japanese(self):
        self.assertEqual(self.titles(self.spec()),
                         ("As-Is（現状）", "To-Be（あるべき姿）"))

    def test_a_slide_can_override_the_spec(self):
        spec = self.spec("ja")
        spec["slides"][0]["lang"] = "en"
        self.assertEqual(self.titles(spec), ("As-Is (current)", "To-Be (target)"))


if __name__ == "__main__":
    unittest.main()
