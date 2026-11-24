from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import _text  # noqa: E402
from diagrams import Canvas  # noqa: E402


def canvas():
    deck = MagicMock()
    deck.requests = []
    return Canvas(deck, "s1", {"colors": {}})


class WrapPhrasesTest(unittest.TestCase):
    def test_number_and_unit_stay_together(self):
        out = _text.wrap_phrases("月 400 時間（年 4,800 時間）", 2.0, 14)
        self.assertTrue(any("年 4,800 時間）" in ln for ln in out.split("\n")))

    def test_breaks_after_particle(self):
        out = _text.wrap_phrases("利用ルールと入力データの基準を定める", 2.0, 15)
        self.assertIn("\n", out)
        self.assertEqual(out.replace("\n", ""), "利用ルールと入力データの基準を定める")
        self.assertFalse(out.split("\n")[1].startswith(("ル", "タ")))

    def test_unchanged_when_fitting_latin_or_manual(self):
        self.assertEqual(_text.wrap_phrases("短い文", 3.0, 12), "短い文")
        self.assertEqual(_text.wrap_phrases("a long latin text " * 5, 1.0, 12),
                         "a long latin text " * 5)
        self.assertEqual(_text.wrap_phrases("手動の\n改行", 0.3, 12), "手動の\n改行")


class CardsFitHeightTest(unittest.TestCase):
    def test_shrinks_only_when_asked(self):
        items = [("見出し", "短い本文")] * 3
        self.assertEqual(canvas().cards(0.5, 1.0, 9.0, 3.0, items), 4.0)
        self.assertLess(canvas().cards(0.5, 1.0, 9.0, 3.0, items, fit_height=True), 2.0)

    def test_never_grows_past_h(self):
        items = [("見出し", "長い本文を入れる " * 20)]
        self.assertEqual(canvas().cards(0.5, 1.0, 3.0, 1.0, items, fit_height=True), 2.0)


class CombochartTest(unittest.TestCase):
    def test_draws_and_returns_bottom(self):
        self.assertEqual(canvas().combochart(
            0.5, 1.0, 9.0, 3.0, ["1", "2"], ("受注", [100, 160]),
            ("p95", [420, 740]), line_unit="ms"), 4.0)

    def test_legend_follows_text_language_not_cli(self):
        d = canvas()
        seen = []
        d._legend_row = lambda x, y, w, entries, **kw: seen.extend(n for n, _ in entries)
        d.combochart(0.5, 1, 9, 3, ["1", "2"], ("受注", [1, 2]), ("p95", [1, 2]))
        self.assertEqual(seen, ["受注（左軸）", "p95 (right axis)"])

    def test_rejects_negative_and_length_mismatch(self):
        with self.assertRaises(ValueError):
            canvas().combochart(0.5, 1, 9, 3, ["1", "2"], ("a", [1, -1]), ("b", [1, 2]))
        with self.assertRaises(ValueError):
            canvas().combochart(0.5, 1, 9, 3, ["1", "2"], ("a", [1]), ("b", [1, 2]))


if __name__ == "__main__":
    unittest.main()
