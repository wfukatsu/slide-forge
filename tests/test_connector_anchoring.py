"""Arrows that join boxes must meet the boxes' edges.

A hand-typed arrow marked _anchored used to be exempt from the endpoint
check, so an arrow that stopped short of a box or ended on its caption
passed the audit and only showed up in the rendered deck. vlink() / hlink()
/ elbow() compute the ends from the boxes instead.
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


def ends(c, oid):
    conn = next(x for x in c.connectors if x["oid"] == oid)
    return conn["p1"], conn["p2"]


class AnchoredAuditTest(unittest.TestCase):
    def test_floating_anchored_arrow_is_reported(self):
        c = canvas()
        c.shape(1.0, 1.0, 1.0, 0.5)
        c.shape(1.0, 2.5, 1.0, 0.5)
        # stops 0.3in short of the lower box
        c.arrow(1.5, 1.5, 1.5, 2.2, _anchored=True)
        self.assertEqual(len(c.audit_connectors()), 1)

    def test_arrow_ending_on_a_caption_is_reported(self):
        c = canvas()
        c.shape(1.0, 1.0, 1.0, 0.5)
        c.label(1.0, 2.5, 1.0, 0.3, "caption")
        c.arrow(1.5, 1.5, 1.5, 2.5, _anchored=True)
        self.assertEqual(len(c.audit_connectors()), 1)

    def test_small_deliberate_air_gap_passes(self):
        c = canvas()
        c.shape(1.0, 1.0, 1.0, 0.5)
        c.shape(1.0, 2.5, 1.0, 0.5)
        c.arrow(1.5, 1.56, 1.5, 2.44, _anchored=True)
        self.assertEqual(c.audit_connectors(), [])

    def test_free_lines_stay_exempt(self):
        c = canvas()
        c.shape(1.0, 1.0, 1.0, 0.5)
        c.line(4.0, 4.0, 5.0, 4.0, free=True)
        self.assertEqual(c.audit_connectors(), [])


class VlinkHlinkTest(unittest.TestCase):
    def test_vlink_meets_both_edges(self):
        c = canvas()
        a = c.shape(1.0, 1.0, 1.0, 0.5)
        b = c.shape(0.5, 2.0, 4.0, 0.5)
        p1, p2 = ends(c, c.vlink(a, b))
        self.assertEqual(p1, (1.5, 1.5))     # narrower box's centre, its bottom
        self.assertEqual(p2, (1.5, 2.0))     # wide band's top
        self.assertEqual(c.audit_connectors(), [])

    def test_vlink_upward(self):
        c = canvas()
        a = c.shape(1.0, 3.0, 1.0, 0.5)
        b = c.shape(1.0, 1.0, 1.0, 0.5)
        p1, p2 = ends(c, c.vlink(a, b))
        self.assertEqual((p1[1], p2[1]), (3.0, 1.5))

    def test_parallel_arrows_into_one_band(self):
        c = canvas()
        band = c.shape(0.5, 2.0, 6.0, 0.5)
        xs = []
        for i in range(3):
            box = c.shape(0.5 + i * 2.1, 1.0, 1.8, 0.5)
            xs.append(ends(c, c.vlink(box, band))[0][0])
        self.assertEqual(len(set(xs)), 3)    # no convergence on one point

    def test_vlink_refuses_boxes_that_do_not_overlap(self):
        c = canvas()
        a = c.shape(1.0, 1.0, 1.0, 0.5)
        b = c.shape(4.0, 2.0, 1.0, 0.5)
        with self.assertRaises(ValueError):
            c.vlink(a, b)

    def test_hlink_uses_the_shorter_box(self):
        c = canvas()
        btn = c.shape(1.0, 2.0, 1.0, 0.4)
        panel = c.shape(3.0, 1.0, 1.5, 3.0)
        p1, p2 = ends(c, c.hlink(btn, panel))
        self.assertEqual(p1, (2.0, 2.2))
        self.assertEqual(p2, (3.0, 2.2))


class ElbowTest(unittest.TestCase):
    def test_elbow_meets_both_boxes(self):
        c = canvas()
        a = c.shape(1.0, 3.0, 1.0, 0.6)
        b = c.shape(4.0, 1.0, 1.0, 0.6)
        segs = c.elbow(a, b)
        self.assertEqual(len(segs), 3)
        self.assertEqual(ends(c, segs[0])[0], (2.0, 3.3))
        self.assertEqual(ends(c, segs[2])[1], (4.0, 1.3))
        self.assertEqual(c.audit_connectors(), [])


class NodeTest(unittest.TestCase):
    def test_node_returns_a_box_arrows_can_join(self):
        c = canvas()
        top = c.node(1.0, 1.0, 1.2, 0.8, "App", icon="server")
        db = c.node(1.0, 2.5, 1.2, 0.8, "DB", icon="database")
        c.vlink(top, db)
        self.assertEqual(c.audit_connectors(), [])

    def test_node_takes_one_picture(self):
        c = canvas()
        with self.assertRaises(ValueError):
            c.node(1.0, 1.0, 1.0, 1.0, "x", icon="server",
                   asset_icon="agent")


if __name__ == "__main__":
    unittest.main()
