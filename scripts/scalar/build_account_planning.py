#!/usr/bin/env python3
"""Account Planning Session のデッキを組む（元資料 FY17 AP Template 準拠）。

同じ入力から読み手の違う 2 本を出す:

    plan.json    アカウントチームのための Plan Document
    review.json  役員レビュー用サマリー（本編 9 ページ + Appendix）

**このスクリプトは図の種類・座標・書式だけを持つ。** 文字列は顧客ごとの
`accounts/<AE>/<顧客>/aps.json`（Git 管理外）から読む。顧客名・実名・その人物
への判断をここに書かないこと。

    .venv/bin/python scripts/scalar/build_account_planning.py \\
        --aps "accounts/<AE>/<顧客>/aps.json" --out "out/account-plan/<顧客>/ap"

aps.json の作り方は references/account-planning-session.md を参照。
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

# 座標契約（references/layout-contract.md の実測値）
#   governing_message y=0.42 / lead_in y=1.02 / 図の上端 1.50（lead あり）1.25（なし）
#   図の下端 <= 4.80 / so_what 2 行は y=3.62 h=1.12、1 行は y=3.92 h=0.88
#   source_note y=4.86
# Slides API は幅 32pt (0.444in) 未満の表列を拒否する。--dry-run では検出できない
MIN_COL_IN = 0.45

N = {k: c for k, c in zip("123456789", "①②③④⑤⑥⑦⑧⑨")}

# ページに 1 つしか出ない図は名前付きスロット、それ以外は figures[] の順で対応する
SLOT = {"governing_message": ("title", "text"),
        "lead_in": ("lead", "text"),
        "source_note": ("source", "source")}

# 商談 1 件のページ。カード 6 枚の型を全商談で揃える
DEAL_PAGE_KEYS = [["challenge", "solution", "diff"], ["people", "jri", "deal"]]
# 既定の見出し。IT 子会社の呼び名など顧客ごとに変えたいものは aps.json の
# meta.dealPageHeads で上書きする
DEAL_PAGE_HEADS = [["顧客の課題", "当社の解", "差別化要因"],
                   ["顧客側のキーパーソン", "システム子会社の担当組織", "金額・時期・ステージ"]]

LAYOUT: dict[str, list] = {
    "group-orgchart": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("lead_in", {"x": 0.5, "y": 1.02, "w": 9.0}),
        ("orgchart", {"x": 0.5, "y": 1.5, "w": 9.0, "h": 3.05, "size": 8}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "smbc-orgchart": [
        ("governing_message", {"x": 0.5, "y": 0.42, "w": 9.0}),
        ("lead_in", {"x": 0.5, "y": 1.02, "w": 9.0}),
        ("orgchart", {"x": 0.5, "y": 1.5, "w": 9.0, "h": 3.05, "size": 7.5}),
        ("source_note", {"x": 0.5, "y": 4.86, "w": 9.0}),
    ],
    "nikko-orgchart": [
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
    "jri-orgchart": [
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
    "jri-mapping": [
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

# ページの並び。中扉の見出しと考慮点は aps.json の sections から取る
PLAN_A = ["group-orgchart", "smbc-orgchart", "nikko-orgchart", "card-orgchart",
          "jri-orgchart", "jri-mapping", "deal-portfolio",
          "company-stakeholders", "officer-coverage", "who-to-meet",
          "financial-trends", "swot",
          "strategy-map-1", "strategy-map-2", "customer-initiatives",
          "customer-programs", "historical-spend", "scalar-footprint", "heatmap",
          "tam-sow", "influence-map", "account-health", "health-criteria",
          "growth-vision"]
PLAN_B = ["initiative-alignment", "blueprint-map", "prioritization-table",
          "prioritization-map"]
PLAN_C = ["execution-plan", "engagement-timeline", "action-plan", "exec-engagement",
          "event-plan", "flight-plan", "projections"]
PLAN_E = ["strategy-summary", "management-asks", "challenge-requirement", "risks"]

# 商談ごとの章。中扉 + 全体像、主要な商談には Objective も付ける
DEAL_EXTRA = {"1": ["objective-ledger"], "3": ["objective-aidd"]}

REVIEW_MAIN = ["strategy-summary", "deal-portfolio", "strategy-map-2", "blueprint-map",
               "prioritization-map", "execution-plan", "action-plan", "management-asks",
               "challenge-requirement"]
REVIEW_APPENDIX = ["group-orgchart", "smbc-orgchart", "nikko-orgchart", "card-orgchart",
                   "jri-orgchart", "jri-mapping", "company-stakeholders",
                   "officer-coverage", "who-to-meet",
                   "financial-trends", "swot", "customer-initiatives", "customer-programs",
                   "scalar-footprint", "heatmap", "influence-map", "account-health",
                   "deal-1", "deal-3", "objective-ledger", "risks"]


def _check_columns(fig: dict, where: str) -> None:
    """Slides API の列幅下限を組み立て時に検査する（--dry-run では出ない）。"""
    widths = fig.get("colWidths")
    if not widths:
        return
    scale = fig["w"] / sum(widths)
    thin = [(h, w * scale) for h, w in zip(fig["headers"], widths) if w * scale < MIN_COL_IN]
    if thin:
        raise ValueError(f"{where}: 表の列が細すぎます（API 下限 {MIN_COL_IN}in）: "
                         + ", ".join(f"{h}={w:.3f}in" for h, w in thin))


def build_page(pid: str, data: dict, extra: dict | None = None) -> dict:
    """LAYOUT の図の並びに、aps.json の内容を差し込んで 1 ページにする。"""
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


def by_company(deals: list) -> list:
    """商談を会社ごとにまとめた mece_tree の枝を返す。"""
    order, groups = [], {}
    for d in deals:
        if d["company"] not in groups:
            order.append(d["company"])
            groups[d["company"]] = []
        groups[d["company"]].append(
            f"{N[d['id']]} {d['name']}\n{d['amount']} / {d['period']}")
    return [[c, groups[c]] for c in order]


def deal_page(d: dict, source: str, heads: list | None = None) -> dict:
    """商談 1 件の全体像。カード 6 枚の型は全商談で同じにする。"""
    heads = heads or DEAL_PAGE_HEADS
    return {"layout": "BLANK", "figures": [
        {"type": "governing_message", "x": 0.5, "y": 0.42, "w": 9.0,
         "text": f"商談 {N[d['id']]} の全体像 — {d['company']}／{d['name']}"},
        *[{"type": "cards", "x": 0.5, "y": y, "w": 9.0, "h": 1.55,
           "titleSize": 9, "bodySize": 7.5,
           "items": [[h, d[k]] for h, k in zip(heads, keys)]}
          for y, heads, keys in zip((1.22, 2.92), heads, DEAL_PAGE_KEYS)],
        {"type": "source_note", "x": 0.5, "y": 4.86, "w": 9.0, "source": source},
    ]}


def deal_section(d: dict) -> dict:
    """商談ごとの中扉。会社名を先に置いて、どの会社の話かを明示する。"""
    return {"layout": "SECTION",
            "title": f"商談 {N[d['id']]}　{d['company']}／{d['name']}",
            "body": f"顧客イニシアチブ: {d['initiative']}　／　"
                    f"{d['amount']} ／ {d['period']} ／ {d['stage']}"}


def build(aps: dict) -> tuple[dict, dict]:
    meta, deals, pages = aps["meta"], aps["deals"], aps["pages"]
    sec = {k: {"layout": "SECTION", "title": v["title"], "body": v["body"]}
           for k, v in aps["sections"].items()}
    cover = {"layout": "COVER", "title": meta["title"], "subtitle": meta["subtitle"]}

    P = {pid: build_page(pid, pages[pid]) for pid in pages if pid != "deal-portfolio"}
    P["deal-portfolio"] = build_page(
        "deal-portfolio", pages["deal-portfolio"],
        extra={"mece_tree": {"tree": [pages["deal-portfolio"]["root"], by_company(deals)]}})
    for d in deals:
        P[f"deal-{d['id']}"] = deal_page(d, aps["dealSource"],
                                        meta.get("dealPageHeads"))

    chapters = []
    for d in deals:
        chapters.append(deal_section(d))
        chapters.append(P[f"deal-{d['id']}"])
        chapters += [P[k] for k in DEAL_EXTRA.get(d["id"], [])]

    plan = {"title": meta["planTitle"],
            "slides": [cover, sec["A"], *[P[k] for k in PLAN_A],
                       sec["B"], *[P[k] for k in PLAN_B],
                       *chapters,
                       sec["C"], *[P[k] for k in PLAN_C],
                       sec["E"], *[P[k] for k in PLAN_E]]}
    review = {"title": meta["reviewTitle"],
              "slides": [cover, *[P[k] for k in REVIEW_MAIN],
                         sec["APX"], *[P[k] for k in REVIEW_APPENDIX]]}
    return plan, review


def main() -> int:
    ap = argparse.ArgumentParser(description="Build the Account Planning Session decks")
    ap.add_argument("--aps", required=True, help="accounts/<AE>/<顧客>/aps.json")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    aps = json.loads(Path(args.aps).read_text(encoding="utf-8"))
    plan, review = build(aps)

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
