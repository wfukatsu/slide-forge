from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import slide_templates as st  # noqa: E402


def render(template_id, data, lang=None):
    template, _ = st.load_template(template_id)
    return st.render_template(template, data, lang=lang)


class SlotDefaultLanguageTest(unittest.TestCase):
    """A slot default is a label too: it prints on the slide, so it follows lang."""

    PARETO = {
        "title": "障害の発生原因",
        "items": [["設定ミス", 42], ["通信断", 28], ["権限不備", 19]],
        "insight": "上位 2 件で約 7 割",
        "source": "運用記録",
    }

    def unit_texts(self, slide):
        """Every string the rendered slide carries, flattened."""
        out = []

        def walk(node):
            if isinstance(node, dict):
                for v in node.values():
                    walk(v)
            elif isinstance(node, list):
                for v in node:
                    walk(v)
            elif isinstance(node, str):
                out.append(node)
        walk(slide)
        return out

    def test_a_defaulted_unit_follows_the_language(self):
        ja = self.unit_texts(render("pareto-analysis", self.PARETO))
        en = self.unit_texts(render("pareto-analysis", self.PARETO, lang="en"))
        self.assertIn("件", ja)
        self.assertIn("items", en)
        self.assertNotIn("件", en)

    def test_the_caller_can_still_pass_its_own_unit(self):
        data = dict(self.PARETO, unit="cases")
        texts = self.unit_texts(render("pareto-analysis", data))
        self.assertIn("cases", texts)
        self.assertNotIn("件", texts)

    def test_a_defaulted_axis_pair_follows_the_language(self):
        data = {"title": "優先度", "items": [["A", 0.2, 0.8], ["B", 0.7, 0.3]],
                "insight": "右上から着手する", "source": "社内検討"}
        en = self.unit_texts(render("priority-matrix", data, lang="en"))
        self.assertIn("Hard to do", en)
        self.assertIn("High impact", en)

    def test_validation_sees_the_resolved_string_not_the_marker(self):
        # The default is {"$t": …} on disk; validate_input must type-check the
        # resolved string, or a "type": "string" slot would be rejected.
        slide = render("pareto-analysis", self.PARETO, lang="en")
        self.assertNotIn("$t", str(slide))


if __name__ == "__main__":
    unittest.main()
