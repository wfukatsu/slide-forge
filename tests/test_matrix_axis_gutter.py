"""The 2x2 matrix sizes its y-axis gutter from the labels it is given.

The gutter used to be a fixed 0.44in, which holds about 3.5 half-width
characters at 9pt. Japanese 内 / 外 are one em each and fit, so an English
deck was the first to notice: "Internal" wrapped mid-word as "Intern / al".
These check the gutter is wide enough for the text rather than a fixed size,
without pinning the exact arithmetic.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_deck as bd  # noqa: E402
from _text import em  # noqa: E402
from diagrams import Canvas  # noqa: E402

EMU_PER_INCH = 914400
X, Y, W, H = 1.1, 1.05, 7.8, 2.9
SIZE = 11                      # matrix() default; axis labels draw at SIZE - 2
FLOOR = 0.44                   # the historical fixed gutter, kept as a minimum


def gutter(y_axis) -> float:
    """Width reserved left of the grid, in inches.

    The first shape drawn at or right of X starts at x + gutter, so the
    difference is what the axis labels reserved.
    """
    deck = bd._StubDeck()
    Canvas(deck, "slide", {}).matrix(X, Y, W, H, ["a", "b", "c", "d"],
                                     x_axis=("L", "R"), y_axis=y_axis,
                                     size=SIZE)
    xs = [r["createShape"]["elementProperties"]["transform"]["translateX"]
          / EMU_PER_INCH
          for r in deck.requests if "createShape" in r]
    return min(x for x in xs if x >= X) - X


class MatrixAxisGutterTest(unittest.TestCase):
    def test_short_labels_keep_the_original_gutter(self):
        # Decks whose labels already fit must not shift, so the floor holds.
        self.assertAlmostEqual(gutter(("内", "外")), FLOOR, places=2)

    def test_a_long_label_gets_room_for_its_text(self):
        labels = ("Internal", "External")
        text_in = max(em(s) for s in labels) * (SIZE - 2) / 72.0
        # Wide enough for the glyphs themselves, which is what stops Slides
        # breaking the word across two lines.
        self.assertGreater(gutter(labels), text_in)
        self.assertGreater(gutter(labels), FLOOR)

    def test_the_gutter_never_eats_the_grid(self):
        # An absurd label must not squeeze the quadrants out of existence.
        self.assertLessEqual(gutter(("X" * 200, "Y" * 200)), W * 0.25 + 0.01)

    def test_japanese_and_english_of_the_same_length_agree(self):
        # The measure is full-width equivalents, not character count: four
        # half-width characters take the same room as two full-width ones.
        self.assertAlmostEqual(gutter(("abcd", "efgh")),
                               gutter(("内外", "上下")), places=2)


if __name__ == "__main__":
    unittest.main()
