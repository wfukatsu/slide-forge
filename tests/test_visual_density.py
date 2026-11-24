from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import visual_density as vd  # noqa: E402
from unittest.mock import MagicMock  # noqa: E402

from diagrams import Canvas  # noqa: E402


def page(*figs, title="結論を一文で言う", layout="TITLE_ONLY"):
    return {"layout": layout, "title": title, "figures": list(figs)}


def lead(text="導入"):
    return {"type": "lead_in", "x": 0.5, "y": 0.8, "w": 9, "text": text}


FLOW = {"type": "flow", "x": 0.5, "y": 1.5, "w": 9, "steps": ["A", "B"]}


class RunTest(unittest.TestCase):
    def test_three_text_pages_in_a_row_are_reported_once(self):
        found = vd.audit({"slides": [page(lead()), page(lead()), page(lead())]})
        self.assertEqual(len(found), 1)
        self.assertIn("1", found[0])

    def test_a_picture_or_a_section_breaks_the_run(self):
        storyline = page({"type": "storyline", "titles": ["a", "b"]})
        for middle in (page(lead(), FLOW), page(layout="SECTION"), storyline):
            with self.subTest(middle=middle["figures"] or middle["layout"]):
                deck = {"slides": [page(lead()), page(lead()), middle,
                                   page(lead()), page(lead())]}
                self.assertEqual(vd.audit(deck), [])

    def test_cards_with_icons_count_as_a_picture(self):
        cards = {"type": "cards", "items": [["a", "b"]], "icons": ["lock"]}
        bare = {"type": "cards", "items": [["a", "b"]]}
        self.assertTrue(vd.is_picture(cards))
        self.assertFalse(vd.is_picture(bare))


class WordsTest(unittest.TestCase):
    def test_limit_follows_density(self):
        text = "あ" * 180
        slide = page(lead(text), FLOW)
        self.assertEqual(vd.audit({"slides": [slide]}), [])
        self.assertEqual(len(vd.audit({"density": "presentation",
                                       "slides": [slide]})), 1)

    def test_labels_inside_a_picture_are_not_prose(self):
        chart = {"type": "vbars", "labels": ["一月" * 100], "values": [1]}
        self.assertLess(vd.page_width(page(chart)), 20)


class TableTest(unittest.TestCase):
    def test_item_description_table_is_reported(self):
        rows = [["項目", "これは説明の文章として十分に長い一文です"]] * 3
        table = {"type": "table", "headers": ["項目", "説明"], "rows": rows}
        found = vd.audit({"slides": [page(table, FLOW)]})
        self.assertEqual(len(found), 1)
        self.assertIn("3", found[0])

    def test_short_or_wide_tables_are_not(self):
        short = {"type": "table", "rows": [["A", "1"]] * 4}
        wide = {"type": "table", "rows": [["A", "長い説明の文章がここに入ります", "x"]] * 4}
        for t in (short, wide):
            self.assertEqual(vd.audit({"slides": [page(t, FLOW)]}), [])


class KickerTest(unittest.TestCase):
    def test_kickers_on_most_pages_are_reported(self):
        kick = {"type": "so_what", "text": "示唆"}
        deck = {"slides": [page(FLOW, kick) for _ in range(5)]}
        self.assertEqual(len(vd.audit(deck)), 1)


def canvas():
    deck = MagicMock()
    deck.requests = []
    return Canvas(deck, "s1", {"colors": {}})


class CardIconTest(unittest.TestCase):
    def heading_y(self, **kw):
        d = canvas()
        icons, labels = [], {}
        d.icon = lambda name, x, y, size, **k: icons.append((name, y)) or y + size
        orig = d.label
        d.label = lambda x, y, w, h, text, **k: labels.setdefault(text, y) or orig(
            x, y, w, h, text, **k)
        d.cards(0.5, 1.0, 9, 2.0, [("ガバナンス", "本文"), ("業務", "本文")], **kw)
        return icons, labels["ガバナンス"]

    def test_icons_draw_above_and_push_the_heading_down(self):
        icons, with_y = self.heading_y(icons=["lock", None])
        _, bare_y = self.heading_y()
        self.assertEqual([n for n, _ in icons], ["lock"])
        self.assertLess(icons[0][1], with_y)
        self.assertGreater(with_y, bare_y)

    def test_icon_count_must_match(self):
        with self.assertRaises(ValueError):
            canvas().cards(0.5, 1.0, 9, 2.0, [("a", "b")], icons=["lock", "gear"])


if __name__ == "__main__":
    unittest.main()
