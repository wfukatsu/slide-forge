from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_deck as bd  # noqa: E402
import diagrams  # noqa: E402
from diagrams import Canvas  # noqa: E402


def shape_type(canvas, oid):
    for r in canvas.deck.requests:
        if "createShape" in r and r["createShape"]["objectId"] == oid:
            return r["createShape"]["shapeType"]
    raise AssertionError(f"no createShape for {oid}")


class CornerTest(unittest.TestCase):
    def setUp(self):
        self.canvas = Canvas(bd._StubDeck(), "slide", {})

    def test_a_chip_stays_rounded(self):
        oid = self.canvas.shape(0, 0, 1.6, 0.32, kind="ROUND_RECTANGLE")
        self.assertEqual(shape_type(self.canvas, oid), "ROUND_RECTANGLE")

    def test_a_wide_thin_band_stays_rounded(self):
        # The shorter side decides, so a full-width band keeps its corners
        oid = self.canvas.band(0.5, 1.0, 9.0, 0.44)
        self.assertEqual(shape_type(self.canvas, oid), "ROUND_RECTANGLE")

    def test_a_large_box_squares_off(self):
        oid = self.canvas.box(0.5, 1.0, 3.0, 2.0)
        self.assertEqual(shape_type(self.canvas, oid), "RECTANGLE")

    def test_the_threshold_is_inclusive(self):
        side = diagrams.MAX_ROUND_SIDE
        keep = self.canvas.shape(0, 0, 2.0, side, kind="ROUND_RECTANGLE")
        drop = self.canvas.shape(0, 3.0, 2.0, side + 0.01, kind="ROUND_RECTANGLE")
        self.assertEqual(shape_type(self.canvas, keep), "ROUND_RECTANGLE")
        self.assertEqual(shape_type(self.canvas, drop), "RECTANGLE")

    def test_the_recorded_geometry_matches_what_was_drawn(self):
        oid = self.canvas.solid(0.5, 1.0, 3.0, 1.2, "見出し")
        self.assertEqual(self.canvas.rects[oid][4], "RECTANGLE")
        self.assertEqual(self.canvas.texts[oid]["kind"], "RECTANGLE")

    def test_other_kinds_are_untouched(self):
        for kind in ("ELLIPSE", "DIAMOND", "CAN", "TEXT_BOX"):
            oid = self.canvas.shape(0, 0, 3.0, 2.0, kind=kind)
            self.assertEqual(shape_type(self.canvas, oid), kind)

    def test_round_variants_square_off_too(self):
        oid = self.canvas.shape(0, 0, 3.0, 2.0, kind="ROUND_2_SAME_RECTANGLE")
        self.assertEqual(shape_type(self.canvas, oid), "RECTANGLE")


if __name__ == "__main__":
    unittest.main()
