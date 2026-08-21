from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "nexus"))

import build_nexus_deck as bnd  # noqa: E402
import collect as nx  # noqa: E402

REPORT = """---
title: "システム概要"
schema_version: 1
phase: "Phase 1: Analysis"
skill: analyze
generated_at: "2026-08-18T03:20:00+09:00"
input_files:
  - reports/before/demo/technology-stack.md
---

## サマリー

| 指標 | 値 |
|---|---|
| モジュール | 5 |
| 課題 | 19 |

```mermaid
graph TD
  A --> B
```

### 内訳

本文。
"""


def progress(**phases) -> dict:
    return {
        "$schema": "progress-registry-v1",
        "project_name": "demo",
        "options": {"output_language": "ja", "workflow_type": "legacy",
                    "scalardb_enabled": True},
        "phases": phases,
    }


def phase(status: str, *, outputs=(), summary="", plugin="architect",
          category="analysis") -> dict:
    return {"status": status, "plugin": plugin, "category": category,
            "outputs": list(outputs), "summary": summary,
            "completed_at": "2026-08-18T03:20:49+09:00", "note": ""}


class PartialRunTest(unittest.TestCase):
    """A pipeline that is still running is the normal case, not an error."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name)
        (self.project / "work").mkdir()
        (self.project / "reports" / "01_analysis").mkdir(parents=True)

    def write_progress(self, data: dict) -> None:
        (self.project / "work" / "pipeline-progress.json").write_text(
            json.dumps(data), encoding="utf-8")

    def write_report(self, rel: str = "reports/01_analysis/system-overview.md") -> None:
        path = self.project / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(REPORT, encoding="utf-8")

    def collect(self) -> dict:
        # nexus_root=None and no tools/ in the fixture, so this exercises the
        # pipeline-progress.json path deliberately.
        return nx.collect(str(self.project), None)

    # ---------- status ----------

    def test_unfinished_phases_become_gaps_with_their_command(self):
        self.write_progress(progress(
            analyze=phase("completed", summary="用語 49 語を抽出した"),
            evaluate_mmi=phase("in_progress"),
            redesign=phase("pending"),
            design_api=phase("failed"),
        ))
        data = self.collect()
        kinds = sorted(g["kind"] for g in data["gaps"])
        self.assertEqual(
            kinds, ["phase-failed", "phase-in-progress", "phase-pending"])

    def test_completed_phase_missing_its_output_is_a_gap(self):
        self.write_progress(progress(analyze=phase(
            "completed", summary="…",
            outputs=["reports/01_analysis/system-overview.md",
                     "reports/01_analysis/ubiquitous-language.md"])))
        self.write_report()          # only one of the two declared outputs
        data = self.collect()
        gap = [g for g in data["gaps"] if g["kind"] == "missing-output"]
        self.assertEqual(len(gap), 1)
        self.assertIn("ubiquitous-language.md", gap[0]["detail"])
        written = data["pipelines"]["architect"]["phases"][0]
        self.assertEqual((written["outputsWritten"], written["outputsDeclared"]), (1, 2))

    def test_placeholder_output_is_matched_by_glob_not_reported_missing(self):
        # `domain-story-{domain}.md` is only named once the phase runs; a
        # written report must not show up as a missing output.
        self.write_progress(progress(create_domain_story=phase(
            "completed", summary="…",
            outputs=["reports/04_stories/domain-story-{domain}.md"])))
        self.write_report("reports/04_stories/domain-story-order.md")
        data = self.collect()
        self.assertEqual([g for g in data["gaps"] if g["kind"] == "missing-output"], [])

    def test_no_progress_file_still_inventories_the_reports(self):
        self.write_report()
        data = self.collect()
        self.assertIsNone(data["status"]["source"])
        self.assertEqual([a["kind"] for a in data["artifacts"]], ["analysis"])

    # ---------- artifacts ----------

    def test_report_frontmatter_and_structure_are_extracted(self):
        self.write_progress(progress())
        self.write_report()
        artifact = self.collect()["artifacts"][0]
        self.assertEqual(artifact["title"], "システム概要")
        self.assertEqual(artifact["skill"], "analyze")
        self.assertEqual(artifact["diagrams"], ["graph"])
        self.assertEqual(artifact["tables"], 1)
        self.assertIn("サマリー", artifact["headings"])

    def test_report_extraction_returns_table_rows(self):
        self.write_report()
        out = nx.extract_report(str(self.project),
                                "reports/01_analysis/system-overview.md")
        self.assertEqual(out["tables"][0]["headers"], ["指標", "値"])
        self.assertEqual(out["tables"][0]["rows"][0], ["モジュール", "5"])
        self.assertEqual(out["diagrams"][0]["kind"], "graph")

    def test_ui_mock_names_are_parsed_into_story_and_step(self):
        mock = self.project / "reports/02_spec/ui-mocks/STORY-ORDER-02-confirm.html"
        mock.parent.mkdir(parents=True, exist_ok=True)
        mock.write_text("<html><title>注文確認</title></html>", encoding="utf-8")
        art = [a for a in self.collect()["artifacts"] if a["kind"] == "ui-mock"][0]
        self.assertEqual((art["story"], art["step"], art["title"]),
                         ("STORY-ORDER", 2, "注文確認"))


class DeckSpineTest(unittest.TestCase):
    """Only what the records settle gets a page."""

    def coverage(self, phases: list[dict], gaps=()) -> dict:
        return {
            "schemaVersion": 1,
            "asOf": "2026-08-20T11:20:00+09:00",
            "project": {"name": "demo", "language": "ja"},
            "status": {"source": "pipeline-progress.json"},
            "pipelines": {"architect": {"total": len(phases), "byStatus": {},
                                        "phases": phases},
                          "product": {"total": 0, "byStatus": {}, "phases": []}},
            "artifacts": [],
            "gaps": list(gaps),
        }

    def phase(self, name, status, summary="", outputs=()):
        return {"name": name, "group": "analysis", "plugin": "architect",
                "status": status,
                "optional": False, "stale": False, "summary": summary,
                "note": "", "completedAt": "2026-08-18T03:20:49+09:00",
                "command": f"/architect:{name}",
                "outputs": [{"path": p, "exists": True} for p in outputs],
                "outputsWritten": len(outputs), "outputsDeclared": len(outputs)}

    def test_phase_without_a_recorded_summary_gets_no_digest(self):
        L = bnd.LABELS["ja"]
        self.assertIsNone(bnd.digest_page(
            self.phase("analyze", "completed"), L, "print"))
        self.assertIsNotNone(bnd.digest_page(
            self.phase("analyze", "completed", "用語 49 語を抽出した。"), L, "print"))

    def test_coverage_page_counts_every_status(self):
        phases = [self.phase("a", "completed", "x。"), self.phase("b", "pending"),
                  self.phase("c", "skipped")]
        cov = self.coverage(phases)
        slide = bnd.coverage_page(cov, bnd.LABELS["ja"],
                                  bnd.scope(cov, bnd.LABELS["ja"]), "print")
        bars = [f for f in slide["figures"] if f["type"] == "hbars"][0]
        self.assertEqual({row[0] for row in bars["items"]}, {"完了", "未着手", "スキップ"})

    def test_the_denominator_is_one_pipeline_core_tier_not_the_sum(self):
        # architect (2 core + 1 extension) and product (2) are separate
        # pipelines; "1 of 5" would describe no real thing.
        arch = [self.phase("a", "completed", "x。"), self.phase("b", "pending")]
        ext = dict(self.phase("codegen", "pending"), tier="extension")
        prod = [dict(self.phase("v", "pending"), plugin="product"),
                dict(self.phase("m", "pending"), plugin="product")]
        cov = self.coverage(arch + [ext])
        cov["pipelines"]["product"] = {"total": 2, "byStatus": {}, "phases": prod}
        sc = bnd.scope(cov, bnd.LABELS["ja"])
        self.assertEqual((sc["plugin"], sc["total"]), ("architect", 2))
        self.assertIn("拡張フェーズ 1 件", sc["others"])
        self.assertIn("product", sc["others"])

    def test_gap_without_a_command_says_so_instead_of_guessing(self):
        cov = self.coverage([], gaps=[{"kind": "open-question", "plugin": None,
                                       "phase": None, "detail": "assumptions.md",
                                       "command": None}])
        slide = bnd.open_questions_page(cov, bnd.LABELS["ja"], "print")
        table = [f for f in slide["figures"] if f["type"] == "table"][0]
        self.assertEqual(table["rows"][0][2], bnd.LABELS["ja"]["gapFixUnknown"])


if __name__ == "__main__":
    unittest.main()
