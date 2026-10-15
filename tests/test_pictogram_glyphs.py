"""Glyphs inside pictograms must sit on the shape's centre.

A pictogram is about 0.3in wide; with Slides' default 0.1in text inset a
glyph typed into it gets a frame about 0.1in wide and drifts off centre,
wraps, or is shrunk by the fitter. The warning sign's "!" sat in a
triangle's text frame, which Slides places off the triangle's centre line.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_deck as bd  # noqa: E402
from diagrams import Canvas  # noqa: E402


def canvas():
    return Canvas(bd._StubDeck(), "slide", {})


class GlyphTest(unittest.TestCase):
    def test_warning_mark_is_drawn_on_the_centre_line(self):
        c = canvas()
        c.icon("warning", 1.0, 1.0, 0.3)
        self.assertFalse(c.texts, "the ! must not be text in the triangle")
        marks = [r for r in c.rects.values() if r[4] in ("ROUND_RECTANGLE",
                                                         "ELLIPSE")]
        self.assertEqual(len(marks), 2)
        for x, y, w, h, _ in marks:
            self.assertAlmostEqual(x + w / 2, 1.15, places=6)

    def test_typed_glyphs_have_no_inset(self):
        for name in ("check", "cross", "code", "coin"):
            c = canvas()
            c.icon(name, 1.0, 1.0, 0.3)
            glyph = [t for t in c.texts.values() if t.get("text")]
            self.assertEqual(len(glyph), 1, name)
            self.assertEqual(glyph[0]["inset"], 0.0, name)
            self.assertEqual(glyph[0]["align"], "CENTER", name)
            self.assertEqual(c.fit_notes, [], name)


if __name__ == "__main__":
    unittest.main()
