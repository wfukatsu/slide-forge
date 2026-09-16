from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_deck as bd  # noqa: E402
from diagrams import Canvas  # noqa: E402


FLOW = {"type": "flow", "x": 0.5, "y": 1.0, "w": 9.0, "h": 0.8,
        "items": ["intake", "author", "validate"]}
TABLE = {"type": "table", "x": 0.5, "y": 1.0, "w": 9.0,
         "headers": ["step", "who"], "rows": [["intake", "human"]]}


def canvas():
    return Canvas(bd._StubDeck(), "slide", {})


class GroupModeTest(unittest.TestCase):
    def test_off_unless_asked(self):
        self.assertFalse(bd._group_mode({}, {}))

    def test_defaults_apply_to_every_slide(self):
        self.assertTrue(bd._group_mode({"defaults": {"group": True}}, {}))

    def test_slide_wins_over_defaults(self):
        self.assertTrue(
            bd._group_mode({"defaults": {"group": False}}, {"group": True}))
        self.assertFalse(
            bd._group_mode({"defaults": {"group": True}}, {"group": False}))


class FigureGroupingTest(unittest.TestCase):
    def test_a_composite_figure_becomes_one_group(self):
        c = canvas()
        bd.draw_figures(c, [FLOW], group=True)
        self.assertEqual(len(c.deck.pending_groups), 1)
        # every box and arrow the flow drew, and nothing else
        self.assertEqual(sorted(c.deck.pending_groups[0]),
                         sorted(oid for oid, _ in c.elements))

    def test_each_figure_groups_separately(self):
        c = canvas()
        bd.draw_figures(c, [FLOW, dict(FLOW, y=3.0)], group=True)
        self.assertEqual(len(c.deck.pending_groups), 2)
        first, second = c.deck.pending_groups
        self.assertFalse(set(first) & set(second))

    def test_nothing_is_grouped_by_default(self):
        c = canvas()
        bd.draw_figures(c, [FLOW])
        self.assertEqual(c.deck.pending_groups, [])

    def test_a_figure_can_opt_out(self):
        c = canvas()
        bd.draw_figures(c, [dict(FLOW, group=False)], group=True)
        self.assertEqual(c.deck.pending_groups, [])

    def test_a_table_is_never_grouped(self):
        # The API refuses to group tables, so the figure must be left alone
        c = canvas()
        bd.draw_figures(c, [TABLE], group=True)
        self.assertEqual(c.deck.pending_groups, [])

    def test_a_table_is_left_out_of_a_mixed_slide(self):
        c = canvas()
        bd.draw_figures(c, [FLOW, TABLE], group=True)
        self.assertEqual(len(c.deck.pending_groups), 1)
        tables = {oid for oid, kind in c.elements if kind == "TABLE"}
        self.assertTrue(tables)
        self.assertFalse(tables & set(c.deck.pending_groups[0]))

    def test_the_group_key_never_reaches_the_figure_function(self):
        # It is not a drawing argument; leaking it raises TypeError
        _, kwargs = bd._figure_args(dict(FLOW, group=True))
        self.assertNotIn("group", kwargs)


class ElementRegistryTest(unittest.TestCase):
    def test_lines_are_registered(self):
        # Lines live only in `connectors`; without registering them here, a
        # flow's arrows would be missing from its group
        c = canvas()
        c.line(0.5, 1.0, 2.0, 1.0)
        self.assertEqual([kind for _, kind in c.elements], ["LINE"])

    def test_tables_and_images_are_recorded_but_marked(self):
        c = canvas()
        c.table(0.5, 1.0, 9.0, ["a", "b"], [["1", "2"]])
        self.assertIn("TABLE", [kind for _, kind in c.elements])
        self.assertIn("TABLE", bd.UNGROUPABLE)
        self.assertIn("IMAGE", bd.UNGROUPABLE)


if __name__ == "__main__":
    unittest.main()
