"""Slot data for the `slide-templates/pricing` pack (shared by the calculators).

Each calculator's `--slides DIR` writes one JSON file per slide into DIR. The
file is the `--data` input of `scripts/render_slide_template.py`:

    .venv/bin/python scripts/render_slide_template.py \
        --template breakeven-sales-change --data DIR/breakeven-sales-change.json \
        --out pages/020-breakeven.json

With --slides-logic as well, each calculator also writes calculation-logic
slides (the formula, its inputs and intermediate values) for the same numbers.

Numbers come from the calculation. Title, lead, source and the judgement slots
cannot, so they are written as placeholders starting with TODO[lang]; replace
every one before rendering. Lengths fit the templates' `print` density.
"""
from __future__ import annotations
import json, os, re, sys

TODO = {"ja": "【要記入】", "en": "[TODO] "}

TEXT = {
    "ja": {
        "title": "結論を 1 文で", "lead": "対象・期間・単位", "source": "出典と前提（サンプルでないこと）",
        "insight": "表から言えること", "recommendation": "推奨する対応と範囲",
        "expected": "見込み", "verdict": "判定", "no_recovery": "不可（利益が戻らない）",
        "answer": "回答", "impact": "示唆", "other": "その他",
        "questions": ["競合の狙いは何か", "対抗しないと何を失うか", "対抗すると競合はどう動くか", "対抗を限定できるか"],
        "size": "規模", "largest": "最大の値上げ（{s}）",
        "logic_headers": ["項目", "算式と入力", "結果・説明"],
        "f_eve": "総経済価値 = 参照価値（次善の代替品の価格）＋ 正の差別化価値 − 負の差別化価値。差別化価値の比率 = 正味の差別化価値 ÷ 総経済価値。",
        "f_be": "損益分岐販売変化率 = −単位貢献利益の変化 ÷ 変更後の単位貢献利益（単位コスト不変なら −価格変化 ÷（変更前の単位貢献利益 ＋ 価格変化））。",
        "f_re": "対抗が得になる流出率 =（変更前の単位貢献利益 − 変更後の単位貢献利益）÷ 変更前の単位貢献利益。失う数量がこれを超えるときだけ対抗が得。",
        "f_sc": "価格 = 基本料 ＋ Σ（段ごとの件数 × 単価）− 規模別の値引き。価格／価値 = 価格 ÷ その規模の経済的価値。貢献利益 = 売上 − 増分原価。",
        "reference": "参照価値", "tev": "総経済価値", "direct": "直接入力", "sum_row": "参照 ＋ 正 {p} − 負 {n}（差別化価値の比率 {s}）",
        "price0": "現行価格", "cost0": "増分単位コスト", "cm0": "単位貢献利益", "volume": "販売量",
        "baseline": "ベースライン", "incremental": "増分・回避可能コストのみ", "cand": "候補 {p}",
        "need_up": "数量が {v} 以上増える必要", "allow_down": "数量減 {v} まで許容", "never": "利益は戻らない",
        "cm1": "変更後の単位貢献利益", "threshold": "対抗が得になる流出率",
        "base_fee": "基本料 {v}", "neutral": "（中立）", "included": "込み {v}", "disc": "値引き {v}",
        "revenue": "貢献利益 {c}（基準比）", "cost": "増分原価", "cost_def": "{u}あたり {v}、顧客あたり {c}",
        "usage": "従量（{cur}/{u}）", "from": "{n}{u}〜", "dist_def": "規模（{u}）×顧客数: {v}",
        "dist": "顧客分布", "dist_n": "計 {n} 顧客", "value": "経済的価値", "value_by_size": "規模別に {n} 点（{cur}）",
        "assumed": "入力値",
    },
    "en": {
        "title": "one-sentence conclusion", "lead": "scope, period, unit", "source": "source and assumptions",
        "insight": "what the table shows", "recommendation": "recommended response and scope",
        "expected": "expected", "verdict": "verdict", "no_recovery": "No (cannot recover)",
        "answer": "answer", "impact": "implication", "other": "Other",
        "questions": ["What is the rival after?", "What is lost if we hold?",
                      "How will they react?", "Can we confine a response?"],
        "size": "Size", "largest": "Largest rise ({s})",
        "logic_headers": ["Item", "Calculation", "Note"],
        "f_eve": "Total value = reference value + positive − negative differentiation; share = net differentiation ÷ total.",
        "f_be": "Breakeven change = −Δcontribution ÷ new contribution (= −ΔP ÷ (CM + ΔP) if unit cost is unchanged).",
        "f_re": "Matching pays only if the volume lost by holding exceeds (CM before − CM after) ÷ CM before.",
        "f_sc": "Price = base fee + Σ(units per tier × rate) − size discount; price/value = price ÷ value at that size.",
        "reference": "Reference value", "tev": "Total value", "direct": "entered directly", "sum_row": "ref + {p} − {n} (differentiation {s})",
        "price0": "Current price", "cost0": "Incremental unit cost", "cm0": "Unit contribution", "volume": "Volume",
        "baseline": "baseline", "incremental": "incremental, avoidable only", "cand": "Candidate {p}",
        "need_up": "needs volume up {v}+", "allow_down": "can lose up to {v}", "never": "cannot recover",
        "cm1": "Unit contribution after", "threshold": "Loss that justifies matching",
        "base_fee": "base {v}", "neutral": " (neutral)", "included": "{v} included", "disc": "discount {v}",
        "revenue": "contribution {c} vs base", "cost": "Incremental cost", "cost_def": "{v} per {u}, {c} per customer",
        "usage": "usage ({cur}/{u})", "from": "{n} {u}+", "dist_def": "size ({u}) × customers: {v}",
        "dist": "Distribution", "dist_n": "{n} customers", "value": "Economic value", "value_by_size": "{n} points by size ({cur})",
        "assumed": "input",
    },
}


def text(lang: str) -> dict:
    return TEXT.get(lang, TEXT["en"])


def todo(lang: str, key: str) -> str:
    return TODO.get(lang, TODO["en"]) + text(lang)[key]


def common(lang: str) -> dict:
    return {k: todo(lang, k) for k in ("title", "lead", "source")}


def num(x: float) -> str:
    return f"{x:,.0f}" if abs(x) >= 100 or float(x).is_integer() else f"{x:,.2f}"


def pct(x: float, signed: bool = True) -> str:
    if signed and abs(x) < 0.05:
        return "±0.0%"
    return (f"{x:+.1f}%" if signed else f"{x:.0f}%").replace("-", "−")


def u(x: float, unit: str = "") -> str:
    """A number with its unit, e.g. u(1300000, "円") -> "1,300,000 円"."""
    return f"{num(x)} {unit}".strip()


def substitute(formula: str, inputs: dict | None, units: dict | None = None) -> str:
    """Replace input names in a formula with their values and units (longest names first)."""
    out = formula
    for k in sorted(inputs or {}, key=len, reverse=True):
        un = (units or {}).get(k) or ""
        v = f"{float(inputs[k]):,.12g}" + ("" if not un else un if un[0] in "（(" else " " + un)
        out = re.sub(rf"\b{re.escape(k)}\b", v, out)
    return out


LOGIC_ROWS = 6  # calculation-logic table capacity at print density


def logic(lang: str, formula_key: str, rows: list) -> dict:
    T = text(lang)
    return {**common(lang), "formula": T[formula_key], "headers": T["logic_headers"],
            "rows": [[fit(str(c), 72, "logic cell", "shorten the input names") for c in r] for r in rows[:LOGIC_ROWS]]}


def fit(label: str, limit: int, what: str, hint: str = "give it a 'short' name in the input") -> str:
    """Warn (do not truncate) when a label will fail the template's maxLength."""
    if len(label) > limit:
        print(f"slides: {what} '{label}' is longer than {limit} characters; {hint}", file=sys.stderr)
    return label


def write(directory: str, name: str, data: dict) -> None:
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, name + ".json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"slides: wrote {path}", file=sys.stderr)
