"""The pricing-strategy calculators (scripts/pricing/) and the slide data they emit.

The numbers come from the skill's worked example
(skills/pricing-strategy/references/worked-example.md), so a regression in the
arithmetic shows up as a mismatch with the documented results.
"""
from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "pricing"))

import breakeven  # noqa: E402
import eve_calc  # noqa: E402
import slide_data  # noqa: E402
import slide_templates as st  # noqa: E402
import structure_compare  # noqa: E402

EVE_SPEC = {
    "unit": "1 システムあたり年額", "currency": "USD",
    "segments": [{
        "name": "新規サービス開発（Standard）", "price": 45600,
        "reference": {"alternative": "自前での整合性制御の実装と保守", "value": 84000},
        "drivers": [
            {"name": "整合性障害の削減", "short": "障害の削減", "type": "monetary", "sign": "+",
             "formula": "incidents × cost × reduction",
             "inputs": {"incidents": 4, "cost": 20000, "reduction": 0.5},
             "units": {"incidents": "件", "cost": "USD", "reduction": "（削減率）"}},
            {"name": "DB 変更時の改修回避", "short": "改修の回避", "type": "monetary", "sign": "+",
             "formula": "months × rate", "inputs": {"months": 2, "rate": 12000}},
            {"name": "学習・導入工数", "short": "学習・導入", "type": "monetary", "sign": "-",
             "formula": "months × rate", "inputs": {"months": 2, "rate": 12000}},
            {"name": "運用の追加負担", "short": "運用の負担", "type": "monetary", "sign": "-",
             "formula": "months × rate", "inputs": {"months": 1, "rate": 12000}},
        ]}],
}

PRICE_SPEC = {
    "currency": "USD", "unit": "1 ノードあたり月額", "volume_unit": "ノード",
    "baseline": {"price": 1000, "unit_cost": 150, "volume": 100},
    "candidates": [{"price": 800}, {"price": 900}, {"price": 1100}, {"price": 1200}],
}

STRUCTURE_SPEC = {
    "currency": "USD", "period": "年額", "unit_label": "ノード", "unit_cost": 1800,
    "distribution": [{"size": 2, "count": 30}, {"size": 4, "count": 30}, {"size": 6, "count": 20},
                     {"size": 10, "count": 15}, {"size": 16, "count": 5}],
    "value": 112000, "baseline": "現行",
    "options": [
        {"name": "現行", "tiers": [{"from": 1, "rate": 11400}]},
        {"name": "A: 二部料金", "base_fee": "neutral", "tiers": [{"from": 1, "rate": 6000}]},
        {"name": "B: 段階割引", "tiers": [{"from": 1, "rate": 11400}, {"from": 9, "rate": 5700}]},
    ],
    "recovery_size": 10, "show_sizes": [2, 4, 10, 16],
}


class EconomicValueTest(unittest.TestCase):
    def test_total_value_and_differentiation_share(self):
        seg = eve_calc.compute(EVE_SPEC)["segments"][0]
        self.assertEqual(seg["total_economic_value"], 112000)
        self.assertEqual(round(seg["differentiation_share_pct"]), 25)

    def test_division_sign_is_accepted_in_formulas(self):
        self.assertEqual(eve_calc.safe_eval("a ÷ b × c", {"a": 10, "b": 4, "c": 2}), 5)


class BreakevenTest(unittest.TestCase):
    def test_breakeven_sales_change_per_candidate(self):
        res = breakeven.analyze(PRICE_SPEC)
        got = [round(c["breakeven_pct"], 1) for c in res["candidates"]]
        self.assertEqual(got, [30.8, 13.3, -10.5, -19.0])

    def test_reactive_threshold(self):
        res = breakeven.analyze({"baseline": {"price": 12, "unit_cost": 2},
                                 "candidates": [{"price": 8}], "reactive": True})
        self.assertAlmostEqual(res["candidates"][0]["reactive_threshold_pct"], 40.0)


class StructureTest(unittest.TestCase):
    def test_revenue_neutral_base_fee_and_recovery(self):
        opts = {o["name"]: o for o in structure_compare.evaluate(STRUCTURE_SPEC)["options"]}
        self.assertEqual(round(opts["A: 二部料金"]["base_fee"]), 28620)
        self.assertAlmostEqual(opts["A: 二部料金"]["contribution_change"], 0, places=3)
        self.assertEqual(round(opts["B: 段階割引"]["contribution_change_pct"], 1), -7.8)
        self.assertEqual(round(opts["B: 段階割引"]["recovery"]["customers_needed"], 1), 4.7)


class SlideDataTest(unittest.TestCase):
    """--slides output must satisfy the pricing pack's slot contracts."""

    def render_all(self, directory: Path) -> list[str]:
        rendered = []
        for path in sorted(directory.glob("*.json")):
            # calculation-logic-<what>[-N] and economic-value-waterfall-N share
            # one template each; the suffix only tells the pages apart.
            template_id = ("calculation-logic" if path.stem.startswith("calculation-logic")
                           else path.stem.rstrip("-0123456789"))
            template, _ = st.load_template(template_id)
            st.render_template(template, json.loads(path.read_text(encoding="utf-8")),
                               density="print", lang="ja")
            rendered.append(path.stem)
        return rendered

    def test_every_calculator_writes_renderable_slot_data(self):
        with tempfile.TemporaryDirectory() as tmp, redirect_stderr(io.StringIO()):
            out = Path(tmp)
            eve_calc.slides(eve_calc.compute(EVE_SPEC), EVE_SPEC, "ja", tmp, True)
            spec = dict(PRICE_SPEC, reactive=True)
            breakeven.slides(breakeven.analyze(spec), spec, "ja", tmp, True)
            structure_compare.slides(structure_compare.evaluate(STRUCTURE_SPEC), STRUCTURE_SPEC,
                                     "ja", tmp, True)
            rendered = self.render_all(out)
        self.assertEqual(rendered, [
            "breakeven-sales-change", "calculation-logic-breakeven",
            "calculation-logic-economic-value-1", "calculation-logic-reactive",
            "calculation-logic-structure", "competitor-response",
            "economic-value-waterfall-1", "price-structure-compare"])

    def test_calculation_logic_carries_units(self):
        with tempfile.TemporaryDirectory() as tmp, redirect_stderr(io.StringIO()):
            eve_calc.slides(eve_calc.compute(EVE_SPEC), EVE_SPEC, "ja", tmp, True)
            breakeven.slides(breakeven.analyze(PRICE_SPEC), PRICE_SPEC, "ja", tmp, True)
            eve = json.loads((Path(tmp) / "calculation-logic-economic-value-1.json").read_text())
            be = json.loads((Path(tmp) / "calculation-logic-breakeven.json").read_text())
        cells = [c for row in eve["rows"] for c in row]
        self.assertIn("4 件 × 20,000 USD × 0.5（削減率）", cells)
        self.assertIn("84,000 USD", cells)
        be_cells = [c for row in be["rows"] for c in row]
        self.assertIn("100 ノード", be_cells)
        self.assertTrue(any("850 USD" in c for c in be_cells))

    def test_small_inputs_are_not_rounded_away(self):
        self.assertEqual(slide_data.substitute("prob × loss", {"prob": 0.005, "loss": 1e9}),
                         "0.005 × 1,000,000,000")

    def test_zero_change_reads_as_plus_minus(self):
        self.assertEqual(slide_data.pct(0.0), "±0.0%")
        self.assertEqual(slide_data.pct(-7.8), "−7.8%")


if __name__ == "__main__":
    unittest.main()
