#!/usr/bin/env python3
"""Deterministic evals for the shared agent/skill prompt contracts."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CASES_PATH = ROOT / "references" / "agent-contract-evals.json"


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        raise AssertionError(f"missing file: {relative}")
    return path.read_text(encoding="utf-8")


def evaluate_cases() -> list[str]:
    failures: list[str] = []
    payload = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    for case in payload["cases"]:
        corpus = "\n".join(read(name) for name in case["files"])
        missing = [token for token in case["requires"] if token not in corpus]
        if missing:
            failures.append(f"{case['name']}: missing {missing}")
    return failures


def evaluate_structure() -> list[str]:
    failures: list[str] = []

    skill = ROOT / "skills" / "google-slides-template" / "SKILL.md"
    if len(skill.read_text(encoding="utf-8").splitlines()) > 200:
        failures.append("google-slides-template/SKILL.md exceeds 200 lines")
    if skill.stat().st_size > 15_000:
        failures.append("google-slides-template/SKILL.md exceeds 15 KB")

    marketplace = json.loads(read(".claude-plugin/marketplace.json"))
    plugin = marketplace["plugins"][0]
    if marketplace["metadata"]["version"] != plugin["version"]:
        failures.append("marketplace metadata/plugin versions differ")
    if len(plugin["skills"]) != 19:
        failures.append(f"Claude plugin exposes {len(plugin['skills'])} skills, expected 19")
    for key, description in (
        ("metadata.description", marketplace["metadata"]["description"]),
        ("plugins[0].description", plugin["description"]),
    ):
        if len(description) > 500:
            failures.append(f"{key} exceeds 500 characters")

    scalar_files = [
        "skills/scalar-product-slides/SKILL.md",
        "skills/scalar-proposal-slides/SKILL.md",
        "skills/scalar-account-plan/SKILL.md",
        "skills/scalar-account-planning-session/SKILL.md",
        "skills/scalar-ae-materials/SKILL.md",
    ]
    forbidden_duplicates = (
        "Visual QA is a separate skill",
        "Shared rules with the sibling skills",
        "Drive folder rule (shared",
    )
    for name in scalar_files:
        text = read(name)
        for duplicate in forbidden_duplicates:
            if duplicate in text:
                failures.append(f"{name}: duplicated shared rule {duplicate!r}")

    return failures


def main() -> int:
    failures = evaluate_cases() + evaluate_structure()
    if failures:
        print("Agent contract eval FAILED:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1
    case_count = len(json.loads(CASES_PATH.read_text(encoding="utf-8"))["cases"])
    print(f"Agent contract eval OK: {case_count} scenarios + structural checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
