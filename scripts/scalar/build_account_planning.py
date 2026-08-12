#!/usr/bin/env python3
"""Assemble the Account Planning Session decks (based on the original FY17 AP Template).

Produces two outputs for two different audiences from the same input:

    plan.json    Plan Document for the account team
    review.json  Executive review summary (9 main pages + Appendix)

**This script only holds figure types, coordinates, and formatting.** All text
comes from the per-customer `accounts/<AE>/<customer>/aps.json` (not tracked in
Git). Never write customer names, real names, or judgments about a person here.

    .venv/bin/python scripts/scalar/build_account_planning.py \\
        --aps "accounts/<AE>/<customer>/aps.json" --out "out/account-plan/<customer>/ap"

See references/account-planning-session.md for how to build aps.json.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

# Coordinate contract (measured values from references/layout-contract.md)
#   governing_message y=0.42 / lead_in y=1.02 / figure top edge 1.50 (with lead) 1.25 (without)
#   figure bottom edge <= 4.80 / so_what 2 lines is y=3.62 h=1.12, 1 line is y=3.92 h=0.88
#   source_note y=4.86
# The Slides API rejects table columns narrower than 32pt (0.444in). Not detectable under --dry-run
MIN_COL_IN = 0.45

N = {str(i): chr(0x2460 + i - 1) for i in range(1, 21)}  # "1"->① … "20"->⑳


def deal_no(deal_id: str) -> str:
    """Circled-number form of a deal number. Above ⑳, falls back to parentheses like (21)."""
    return N.get(deal_id, f"({deal_id})")

# Figures that appear only once per page use a named slot; everything else maps to figures[] in order
SLOT = {"governing_message": ("title", "text"),
        "lead_in": ("lead", "text"),
        "source_note": ("source", "source")}

# The page for a single deal. Keeps the 6-card layout consistent across all deals
DEAL_PAGE_KEYS = [["challenge", "solution", "diff"], ["people", "itsub", "deal"]]
# Default headings. Things that should vary per customer, like what to call the
# IT subsidiary, are overridden via meta.dealPageHeads in aps.json
DEAL_PAGE_HEADS = [["顧客の課題", "当社の解", "差別化要因"],
                   ["顧客側のキーパーソン", "システム子会社の担当組織", "金額・時期・ステージ"]]

LAYOUT: dict[str, list] = {
    "group-orgchart": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("lead_in", {"x": 0.5, "y": 1.02, "w": 9.0}),
        ("orgchart", {"x": 0.5, "y": 1.5, "w": 9.0, "h": 3.05, "size": 8}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "bank-orgchart": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("lead_in", {"x": 0.5, "y": 1.02, "w": 9.0}),
        ("orgchart", {"x": 0.5, "y": 1.5, "w": 9.0, "h": 3.05, "size": 7.5}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "securities-orgchart": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("lead_in", {"x": 0.5, "y": 1.02, "w": 9.0}),
        ("orgchart", {"x": 0.5, "y": 1.5, "w": 9.0, "h": 3.05, "size": 7.5}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "card-orgchart": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("lead_in", {"x": 0.5, "y": 1.02, "w": 9.0}),
        ("orgchart", {"x": 0.5, "y": 1.5, "w": 9.0, "h": 3.05, "size": 7.5}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "itsub-orgchart": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("lead_in", {"x": 0.5, "y": 1.02, "w": 9.0}),
        ("orgchart", {"x": 0.5, "y": 1.5, "w": 9.0, "h": 3.05, "size": 7.5}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "financial-trends": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("lead_in", {"x": 0.5, "y": 1.02, "w": 9.0}),
        ("metric", {"x": 0.5, "y": 1.45, "w": 2.8, "h": 1.2}),
        ("metric", {"x": 3.6, "y": 1.45, "w": 2.8, "h": 1.2}),
        ("metric", {"x": 6.7, "y": 1.45, "w": 2.8, "h": 1.2}),
        ("hbars", {"x": 0.5, "y": 2.9, "w": 9.0, "labelW": 2.0, "rowH": 0.44, "gap": 0.14}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "midterm-plan": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("lead_in", {"x": 0.5, "y": 1.02, "w": 9.0}),
        ("mece_tree", {"x": 0.5, "y": 1.5, "w": 9.0, "h": 2.3, "size": 8}),
        ("so_what", {"x": 0.5, "y": 3.92, "w": 9.0, "h": 0.88}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "plan-alignment": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("lead_in", {"x": 0.5, "y": 1.02, "w": 9.0}),
        ("mece_tree", {"x": 0.5, "y": 1.5, "w": 9.0, "h": 2.3, "size": 8}),
        ("so_what", {"x": 0.5, "y": 3.92, "w": 9.0, "h": 0.88}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "swot": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("matrix", {"x": 0.5, "y": 1.22, "w": 9.0, "h": 3.4, "size": 8.5}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "strategy-map-1": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("lead_in", {"x": 0.5, "y": 1.02, "w": 9.0}),
        ("outcome_tree", {"x": 0.5, "y": 1.5, "w": 9.0, "h": 3.05, "size": 9}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "strategy-map-2": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("lead_in", {"x": 0.5, "y": 1.02, "w": 9.0}),
        ("outcome_tree", {"x": 0.5, "y": 1.5, "w": 9.0, "h": 3.05, "size": 8.5}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "customer-initiatives": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("cards", {"x": 0.5, "y": 1.25, "w": 9.0, "h": 1.55, "titleSize": 9, "bodySize": 8}),
        ("cards", {"x": 0.5, "y": 2.95, "w": 6.0, "h": 1.55, "titleSize": 9, "bodySize": 8}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "customer-programs": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("lead_in", {"x": 0.5, "y": 1.02, "w": 9.0}),
        ("gantt", {"x": 0.5, "y": 1.5, "w": 9.0, "h": 3.05, "size": 8.5, "labelW": 2.3}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "historical-spend": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("hbars", {"x": 0.5, "y": 1.35, "w": 9.0, "labelW": 2.6, "rowH": 0.46, "gap": 0.16}),
        ("so_what", {"x": 0.5, "y": 3.62, "w": 9.0, "h": 1.12}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "scalar-footprint": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("lead_in", {"x": 0.5, "y": 1.02, "w": 9.0}),
        ("layers", {"x": 0.5, "y": 1.42, "w": 9.0, "h": 1.7, "size": 8.5}),
        ("cards", {"x": 0.5, "y": 3.25, "w": 9.0, "h": 1.15, "titleSize": 8.5, "bodySize": 7.5}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "heatmap": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("lead_in", {"x": 0.5, "y": 1.02, "w": 9.0}),
        ("layers", {"x": 0.5, "y": 1.5, "w": 9.0, "h": 3.05, "size": 8.5}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "tam-sow": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("nested_circles", {"x": 0.5, "y": 1.25, "w": 4.3, "h": 3.05, "size": 9}),
        ("so_what", {"x": 5.15, "y": 1.3, "w": 4.35, "h": 1.55, "label": "読み取れること"}),
        ("so_what", {"x": 5.15, "y": 3.0, "w": 4.35, "h": 1.3, "label": "欠けている情報"}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "influence-map": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("lead_in", {"x": 0.5, "y": 1.02, "w": 9.0}),
        ("influence_graph", {"x": 0.5, "y": 1.5, "w": 9.0, "h": 2.2, "size": 8}),
        ("so_what", {"x": 0.5, "y": 3.8, "w": 9.0, "h": 0.98, "label": "凡例", "size": 8}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "key-people-career": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("lead_in", {"x": 0.5, "y": 1.02, "w": 9.0}),
        ("cards", {"x": 0.5, "y": 1.5, "w": 9.0, "h": 1.45,
                   "titleSize": 8.5, "bodySize": 7}),
        ("cards", {"x": 0.5, "y": 3.05, "w": 9.0, "h": 1.45,
                   "titleSize": 8.5, "bodySize": 7}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "key-people-network": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("lead_in", {"x": 0.5, "y": 1.02, "w": 9.0}),
        ("influence_graph", {"x": 0.5, "y": 1.5, "w": 9.0, "h": 2.2, "size": 7.5}),
        ("so_what", {"x": 0.5, "y": 3.8, "w": 9.0, "h": 0.98, "size": 8}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "account-health": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("lead_in", {"x": 0.5, "y": 1.02, "w": 9.0}),
        ("rating_matrix", {"x": 0.5, "y": 1.5, "w": 9.0, "levels": 4, "size": 9, "labelW": 3.6, "rowH": 0.36}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "health-criteria": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("lead_in", {"x": 0.5, "y": 1.02, "w": 9.0}),
        ("table", {"x": 0.5, "y": 1.5, "w": 9.0, "colWidths": [1.75, 1.75, 1.85, 1.75, 1.9], "size": 8, "rowH": 0.52}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "growth-vision": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("comparison", {"x": 0.5, "y": 1.22, "w": 9.0, "h": 2.6, "size": 8.5}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "initiative-alignment": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("lead_in", {"x": 0.5, "y": 1.02, "w": 9.0}),
        ("mece_tree", {"x": 0.5, "y": 1.5, "w": 9.0, "h": 3.05, "size": 8.5}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "blueprint-map": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("table", {"x": 0.5, "y": 1.25, "w": 9.0, "colWidths": [1.8, 0.5, 1.9, 2.5, 0.75, 1.05], "size": 8, "rowH": 0.5}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "blueprint-ledger": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("cards", {"x": 0.5, "y": 1.22, "w": 9.0, "h": 1.55, "titleSize": 9, "bodySize": 7.5}),
        ("cards", {"x": 0.5, "y": 2.92, "w": 9.0, "h": 1.55, "titleSize": 9, "bodySize": 7.5}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "blueprint-aidd": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("cards", {"x": 0.5, "y": 1.22, "w": 9.0, "h": 1.55, "titleSize": 9, "bodySize": 7.5}),
        ("cards", {"x": 0.5, "y": 2.92, "w": 9.0, "h": 1.55, "titleSize": 9, "bodySize": 7.5}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "objective-ledger": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("cards", {"x": 0.5, "y": 1.22, "w": 9.0, "h": 1.3, "titleSize": 10, "bodySize": 8.5}),
        ("journey", {"x": 0.5, "y": 2.65, "w": 9.0, "h": 2.0, "size": 7.5, "sizeTitle": 8.5}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "objective-aidd": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("cards", {"x": 0.5, "y": 1.22, "w": 9.0, "h": 1.3, "titleSize": 10, "bodySize": 8.5}),
        ("journey", {"x": 0.5, "y": 2.65, "w": 9.0, "h": 2.0, "size": 7.5, "sizeTitle": 8.5}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "prioritization-table": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("table", {"x": 0.5, "y": 1.25, "w": 9.0, "colWidths": [0.5, 1.9, 1.2, 1.6, 1.85, 1.0, 0.95], "size": 8, "rowH": 0.6}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "prioritization-map": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("posmap", {"x": 0.5, "y": 1.25, "w": 9.0, "h": 2.3, "size": 9, "bubble": 0.8}),
        ("so_what", {"x": 0.5, "y": 3.62, "w": 9.0, "h": 1.12}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "execution-plan": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("lead_in", {"x": 0.5, "y": 1.02, "w": 9.0}),
        ("gantt", {"x": 0.5, "y": 1.5, "w": 9.0, "h": 3.05, "size": 9}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "engagement-timeline": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("lead_in", {"x": 0.5, "y": 1.02, "w": 9.0}),
        ("gantt", {"x": 0.5, "y": 1.5, "w": 9.0, "h": 3.05, "size": 8.5, "labelW": 2.1}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "action-plan": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("lead_in", {"x": 0.5, "y": 1.02, "w": 9.0}),
        ("table", {"x": 0.5, "y": 1.5, "w": 9.0, "colWidths": [0.5, 2.0, 1.5, 0.6, 0.85, 0.95, 2.6], "size": 8, "rowH": 0.44}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "exec-engagement": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("lead_in", {"x": 0.5, "y": 1.02, "w": 9.0}),
        ("orgchart", {"x": 0.5, "y": 1.5, "w": 9.0, "h": 3.05, "size": 8}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "event-plan": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("timeline", {"x": 0.5, "y": 1.45, "w": 9.0, "size": 9, "sizeTitle": 9.5, "rowH": 1.5}),
        ("so_what", {"x": 0.5, "y": 3.62, "w": 9.0, "h": 1.12}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "flight-plan": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("lead_in", {"x": 0.5, "y": 1.02, "w": 9.0}),
        ("posmap", {"x": 0.5, "y": 1.5, "w": 9.0, "h": 2.3, "size": 9, "bubble": 0.78}),
        ("so_what", {"x": 0.5, "y": 3.92, "w": 9.0, "h": 0.88}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "projections": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("table", {"x": 0.5, "y": 1.25, "w": 9.0, "colWidths": [1.75, 1.15, 0.95, 1.35, 3.8], "size": 8.5, "rowH": 0.44}),
        ("so_what", {"x": 0.5, "y": 3.62, "w": 9.0, "h": 1.12}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "strategy-summary": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("exec_summary", {"x": 0.5, "y": 1.05, "w": 9.0, "h": 1.92}),
        ("before_after", {"x": 0.5, "y": 3.05, "w": 9.0, "h": 1.75, "size": 8.5}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "management-asks": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("table", {"x": 0.5, "y": 1.25, "w": 9.0, "colWidths": [1.25, 2.55, 2.4, 0.85, 1.95], "size": 8, "rowH": 0.6}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "challenge-requirement": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("table", {"x": 0.5, "y": 1.25, "w": 9.0, "colWidths": [2.85, 2.35, 1.3, 0.85, 1.65], "size": 8, "rowH": 0.5}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "risks": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("table", {"x": 0.5, "y": 1.25, "w": 9.0, "colWidths": [3.1, 1.35, 3.35, 1.2], "size": 8, "rowH": 0.52}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "itsub-mapping": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("lead_in", {"x": 0.5, "y": 1.02, "w": 9.0}),
        ("comparison", {"x": 0.5, "y": 1.5, "w": 9.0, "h": 2.35, "size": 7}),
        ("so_what", {"x": 0.5, "y": 3.62, "w": 9.0, "h": 1.12}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "deal-portfolio": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("lead_in", {"x": 0.5, "y": 1.02, "w": 9.0}),
        ("mece_tree", {"x": 0.5, "y": 1.5, "w": 9.0, "h": 3.05, "size": 8}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "officer-coverage": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("lead_in", {"x": 0.5, "y": 1.02, "w": 9.0}),
        ("comparison", {"x": 0.5, "y": 1.5, "w": 9.0, "h": 2.35, "size": 7}),
        ("so_what", {"x": 0.5, "y": 3.92, "w": 9.0, "h": 0.88}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "who-to-meet": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("lead_in", {"x": 0.5, "y": 1.02, "w": 9.0}),
        ("table", {"x": 0.5, "y": 1.5, "w": 9.0,
                   "colWidths": [1.55, 1.6, 2.6, 2.4, 0.85],
                   "size": 8, "rowH": 0.56}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "company-stakeholders": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("lead_in", {"x": 0.5, "y": 1.02, "w": 9.0}),
        ("comparison", {"x": 0.5, "y": 1.5, "w": 9.0, "h": 2.35, "size": 7}),
        ("so_what", {"x": 0.5, "y": 3.92, "w": 9.0, "h": 0.88}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
}

# Page ordering. Section-header titles and body text are taken from aps.json's sections.
# Pages that don't fit a given customer are excluded via meta.skipPages (e.g. when the group structure differs)
PLAN_A = ["group-orgchart", "bank-orgchart", "securities-orgchart", "card-orgchart",
          "itsub-orgchart", "itsub-mapping", "deal-portfolio",
          "company-stakeholders", "officer-coverage", "who-to-meet",
          "financial-trends", "midterm-plan", "plan-alignment", "swot",
          "strategy-map-1", "strategy-map-2", "customer-initiatives",
          "customer-programs", "historical-spend", "scalar-footprint", "heatmap",
          "tam-sow", "influence-map", "key-people-career", "key-people-network",
          "account-health", "health-criteria",
          "growth-vision"]
PLAN_B = ["initiative-alignment", "blueprint-map", "prioritization-table",
          "prioritization-map"]
PLAN_C = ["execution-plan", "engagement-timeline", "action-plan", "exec-engagement",
          "event-plan", "flight-plan", "projections"]
PLAN_E = ["strategy-summary", "management-asks", "challenge-requirement", "risks"]

REVIEW_MAIN = ["strategy-summary", "deal-portfolio", "plan-alignment", "blueprint-map",
               "prioritization-map", "execution-plan", "action-plan", "management-asks",
               "challenge-requirement"]
# "@deal-pages" expands to meta.reviewDealPages (the list of deal-page IDs to
# include in the Appendix). Which deals go into the executive review is a
# per-customer decision, so it's held in aps.json
REVIEW_APPENDIX = ["group-orgchart", "bank-orgchart", "securities-orgchart", "card-orgchart",
                   "itsub-orgchart", "itsub-mapping", "company-stakeholders",
                   "officer-coverage", "who-to-meet",
                   "financial-trends", "midterm-plan", "plan-alignment", "swot", "customer-initiatives", "customer-programs",
                   "scalar-footprint", "heatmap", "influence-map", "account-health", "key-people-career", "key-people-network",
                   "@deal-pages", "risks"]


def _check_columns(fig: dict, where: str) -> None:
    """Check the Slides API's minimum column-width limit at assembly time (not caught by --dry-run)."""
    widths = fig.get("colWidths")
    if not widths:
        return
    headers = fig.get("headers")
    if not headers:
        raise ValueError(f"{where}: colWidths のある表に headers がありません")
    if len(headers) != len(widths):
        raise ValueError(f"{where}: headers が {len(headers)} 列、"
                         f"colWidths が {len(widths)} 列で一致しません")
    scale = fig["w"] / sum(widths)
    thin = [(h, w * scale) for h, w in zip(headers, widths) if w * scale < MIN_COL_IN]
    if thin:
        raise ValueError(f"{where}: 表の列が細すぎます（API 下限 {MIN_COL_IN}in）: "
                         + ", ".join(f"{h}={w:.3f}in" for h, w in thin))


def build_page(pid: str, data: dict, extra: dict | None = None) -> dict:
    """Assemble one page by inserting aps.json content into LAYOUT's figure order."""
    if pid not in LAYOUT:
        raise ValueError(f"LAYOUT に '{pid}' がありません")
    content = list(data.get("figures", []))
    figures, i = [], 0
    for kind, geom in LAYOUT[pid]:
        fig = {"type": kind, **geom}
        if kind in SLOT:
            slot, field = SLOT[kind]
            if slot not in data:
                raise ValueError(f"{pid}: '{slot}' がありません")
            fig[field] = data[slot]
        elif extra is not None and kind in extra:
            fig.update(extra[kind])
        else:
            if i >= len(content):
                raise ValueError(f"{pid}: figures が {len(content)} 件しかありません")
            fig.update(content[i])
            i += 1
        _check_columns(fig, f"{pid}/{kind}")
        figures.append(fig)
    if extra is None and i != len(content):
        raise ValueError(f"{pid}: figures が {len(content) - i} 件余っています")
    return {"layout": "BLANK", "figures": figures}


def money_when(d: dict, sep: str = " / ") -> str:
    """A single line of amount / timing. Avoids leaving a bare separator if either is empty."""
    return sep.join(v for v in (d["amount"], d["period"]) if v)


def by_company(deals: list) -> list:
    """Return mece_tree branches with deals grouped by company."""
    order, groups = [], {}
    for d in deals:
        if d["company"] not in groups:
            order.append(d["company"])
            groups[d["company"]] = []
        groups[d["company"]].append(f"{deal_no(d['id'])} {d['name']}\n{money_when(d)}")
    return [[c, groups[c]] for c in order]


def deal_page(d: dict, source: str, heads: list | None = None) -> dict:
    """The overview page for one deal. The 6-card layout is identical across all deals."""
    heads = heads or DEAL_PAGE_HEADS
    if (len(heads) != len(DEAL_PAGE_KEYS)
            or any(len(row) != len(keys)
                   for row, keys in zip(heads, DEAL_PAGE_KEYS))):
        shape = " + ".join(str(len(k)) for k in DEAL_PAGE_KEYS)
        raise ValueError(f"meta.dealPageHeads は {len(DEAL_PAGE_KEYS)} 行"
                         f"（{shape} 列）で書いてください")
    lacking = [k for keys in DEAL_PAGE_KEYS for k in keys if k not in d]
    if lacking:
        raise ValueError(f"deals（id={d['id']}）に次のキーがありません: "
                         + ", ".join(lacking))
    return {"layout": "BLANK", "figures": [
        {"type": "governing_message", "x": 0.5, "y": 0.42, "w": 9.0,
         "text": f"商談 {deal_no(d['id'])} の全体像 — {d['company']}／{d['name']}"},
        *[{"type": "cards", "x": 0.5, "y": y, "w": 9.0, "h": 1.55,
           "titleSize": 9, "bodySize": 7.5,
           "items": [[h, d[k]] for h, k in zip(row_heads, row_keys)]}
          for y, row_heads, row_keys in zip((1.22, 2.92), heads, DEAL_PAGE_KEYS)],
        {"type": "source_note", "x": 0.5, "y": 4.86, "w": 9.0, "source": source},
    ]}


def deal_section(d: dict) -> dict:
    """The section header for each deal. Puts the company name first to make it clear whose deal this is."""
    return {"layout": "SECTION",
            "title": f"商談 {deal_no(d['id'])}　{d['company']}／{d['name']}",
            "body": f"顧客イニシアチブ: {d['initiative']}　／　"
                    f"{money_when(d, ' ／ ')} ／ {d['stage']}"}


DECKS = ("plan", "review")


def skipped_pages(meta: dict) -> dict:
    """meta.skipPages -- pages to exclude from a given deck.

    A list excludes from both decks; a {"plan": [...], "review": [...]} dict
    excludes only from the specified deck. Data stays in the ledger, so the
    exclusion decision is reversible. Whether page IDs actually exist is checked
    in build() (so typos aren't silently ignored).
    """
    spec = meta.get("skipPages") or {}
    if isinstance(spec, list):
        spec = {"plan": spec, "review": spec}
    if not isinstance(spec, dict):
        raise ValueError('meta.skipPages はページ ID のリストか '
                         '{"plan": [...], "review": [...]} で書いてください')
    bad = [k for k in spec if k not in DECKS]
    if bad:
        raise ValueError("meta.skipPages のデッキ名が不正です: " + ", ".join(bad)
                         + "。使えるのは plan / review だけです")
    return {k: set(spec.get(k) or []) for k in DECKS}


def build(aps: dict) -> tuple[dict, dict]:
    meta, deals, pages = aps["meta"], aps["deals"], aps["pages"]
    for d in deals:
        if not isinstance(d.get("id"), str) or not d["id"]:
            raise ValueError('deals[].id は文字列で書いてください（例: "1"）: '
                             f"{d.get('id')!r}")
    deal_ids = {d["id"] for d in deals}
    known = set(LAYOUT) | {f"deal-{i}" for i in deal_ids}

    skip = skipped_pages(meta)
    for deck, keys in skip.items():
        unknown = sorted(keys - known)
        if unknown:
            raise ValueError(
                f"meta.skipPages の {deck} に知らないページ ID があります: "
                + ", ".join(unknown)
                + "。ページ ID か deal-<商談番号> のタイポを確認してください")
    skip_both = skip["plan"] & skip["review"]

    # Which deal-chapter appendix pages and which deal pages go into the executive
    # review Appendix are per-customer decisions, so they're held in aps.json (meta)
    deal_extra = meta.get("dealExtraPages") or {}
    bad = sorted(set(deal_extra) - deal_ids)
    if bad:
        raise ValueError("meta.dealExtraPages に存在しない商談 ID があります: "
                         + ", ".join(bad))
    bad = sorted({k for v in deal_extra.values() for k in v} - set(LAYOUT))
    if bad:
        raise ValueError("meta.dealExtraPages に知らないページ ID があります: "
                         + ", ".join(bad))
    review_deal_pages = meta.get("reviewDealPages") or []
    bad = sorted(set(review_deal_pages) - known)
    if bad:
        raise ValueError("meta.reviewDealPages に知らないページ ID があります: "
                         + ", ".join(bad))
    review_appendix = [k for key in REVIEW_APPENDIX
                       for k in (review_deal_pages if key == "@deal-pages"
                                 else [key])]

    sec = {k: {"layout": "SECTION", "title": v["title"], "body": v["body"]}
           for k, v in aps["sections"].items()}
    cover = {"layout": "COVER", "title": meta["title"], "subtitle": meta["subtitle"]}

    needed = [*PLAN_A, *PLAN_B, *PLAN_C, *PLAN_E, *REVIEW_MAIN, *review_appendix,
              *(k for v in deal_extra.values() for k in v)]
    missing = [k for k in dict.fromkeys(needed)
               if k in LAYOUT and k not in pages and k not in skip_both]
    if missing:
        raise ValueError(
            "aps.json の pages に次のページがありません: " + ", ".join(missing)
            + "。ページを足すか、PLAN_A / REVIEW_* の並びから外すか、"
              "meta.skipPages で両方のデッキから外してください")

    # Pages excluded from both decks are not assembled (fine even if removed from pages)
    P = {pid: build_page(pid, pages[pid])
         for pid in pages if pid != "deal-portfolio" and pid not in skip_both}
    if "deal-portfolio" in pages and "deal-portfolio" not in skip_both:
        P["deal-portfolio"] = build_page(
            "deal-portfolio", pages["deal-portfolio"],
            extra={"mece_tree": {"tree": [pages["deal-portfolio"]["root"],
                                          by_company(deals)]}})
    for d in deals:
        P[f"deal-{d['id']}"] = deal_page(d, aps["dealSource"],
                                        meta.get("dealPageHeads"))

    def deal_chapters(deck: str) -> list:
        """The chapter for each deal. Drops the section header too if all its content is skipped."""
        out = []
        for d in deals:
            keys = [f"deal-{d['id']}", *deal_extra.get(d["id"], [])]
            body = [P[k] for k in keys if k not in skip[deck]]
            if body:
                out += [deal_section(d), *body]
        return out

    def block(deck: str, section: dict, keys: list) -> list:
        """Section header + body. Drops the section header too if the whole body is skipped."""
        body = [P[k] for k in keys if k not in skip[deck]]
        return [section, *body] if body else []

    plan = {"title": meta["planTitle"],
            "slides": [cover, *block("plan", sec["A"], PLAN_A),
                       *block("plan", sec["B"], PLAN_B),
                       *deal_chapters("plan"),
                       *block("plan", sec["C"], PLAN_C),
                       *block("plan", sec["E"], PLAN_E)]}
    review = {"title": meta["reviewTitle"],
              "slides": [cover,
                         *[P[k] for k in REVIEW_MAIN if k not in skip["review"]],
                         *block("review", sec["APX"], review_appendix)]}
    return plan, review


def main() -> int:
    ap = argparse.ArgumentParser(description="Build the Account Planning Session decks")
    ap.add_argument("--aps", required=True, help="accounts/<AE>/<顧客>/aps.json")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    aps = json.loads(Path(args.aps).read_text(encoding="utf-8"))
    plan, review = build(aps)
    for deck, keys in skipped_pages(aps["meta"]).items():
        if keys:
            print(f"{deck}: 載せないページ {', '.join(sorted(keys))}（meta.skipPages）")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for name, spec in (("plan", plan), ("review", review)):
        path = out / f"{name}.json"
        path.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
        print(f"{name}: {len(spec['slides'])} slides -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
