#!/usr/bin/env python3
"""Breakeven sales analysis for candidate prices.

For each candidate price, computes the sales change needed to keep total
contribution equal to the baseline, plus the profit impact under a set of
assumed volume responses. Uses only incremental costs.

Input JSON (see skills/pricing-strategy/references/financial-analysis.md):
{
  "currency": "USD", "unit": "per seat per year",
  "baseline": {"price": 100, "unit_cost": 40, "volume": 1000},
  "volume_unit": "seats",                 # optional, shown by --slides-logic
  "candidates": [{"price": 90}, {"price": 110, "unit_cost": 42},
                 {"price": 120, "incremental_fixed_cost": 20000}],
  "volume_scenarios_pct": [-30, -15, 0, 15, 30]
}

Reactive mode (matching a competitor's cut): add "reactive": true to the JSON
or pass --reactive. For each candidate below the baseline it also reports the
volume loss (if you do NOT match) above which matching pays:
(CM_before - CM_after) / CM_before, i.e. -ΔP / CM when unit cost is unchanged.

Cannibalization mode: an input with a "cannibalization" block (see
skills/pricing-strategy/references/financial-analysis.md).

Slides: --slides DIR writes slot data for the slide-forge `pricing` pack
(see scripts/pricing/slide_data.py): breakeven-sales-change.json (up to 5 candidates) and,
in reactive mode, competitor-response.json. A candidate may carry "expected"
and "verdict" strings for the slide's judgement columns, and the spec may
carry "expected_loss" (e.g. "15–25%") for the competitor-response slide.
--slides-logic adds calculation-logic-breakeven.json (and, in reactive mode,
calculation-logic-reactive.json) showing each formula with the numbers in it.

Usage:
  breakeven.py --input prices.json [--json] [--lang en|ja] [--slides DIR [--slides-logic]]
  breakeven.py --price 100 --cost 40 --candidates 90,110,120 [--volume 1000] [--json]
"""
from __future__ import annotations
import argparse, json, math, sys

LABELS = {
    "en": {
        "title": "Breakeven analysis of candidate prices",
        "baseline": "Baseline",
        "candidate": "Candidate price",
        "change": "Price change",
        "cm": "Contribution margin / unit",
        "be": "Breakeven sales change",
        "be_units": "Breakeven volume",
        "reading_cut": "needs volume up by at least {be:.1f}% to match baseline contribution",
        "reading_inc": "keeps baseline contribution as long as volume falls by no more than {be:.1f}%",
        "reading_none": "breaks even at the baseline volume",
        "reading_infeasible": "cannot break even: the price change wipes out the contribution margin",
        "profit": "Contribution change vs. baseline by volume response",
        "volume_resp": "Volume response",
        "fixed": "incl. incremental fixed cost {fc}",
        "reading": "Reading",
        "volume": "volume",
        "scen_note": "% vs. baseline volume",
        "values_in": "values in {cur}",
        "note": "Only incremental costs are used. Sunk and allocated costs are excluded by design.",
        "reactive_title": "Reactive price change (matching a competitor)",
        "reactive_col": "Matching pays only if volume lost by NOT matching exceeds",
        "reactive_reading": "hold at {p0} unless you would lose more than {t:.1f}% of volume by not matching",
    },
    "ja": {
        "title": "候補価格の損益分岐分析",
        "baseline": "ベースライン",
        "candidate": "候補価格",
        "change": "価格変化",
        "cm": "単位あたり貢献利益",
        "be": "損益分岐販売変化率",
        "be_units": "損益分岐販売量",
        "reading_cut": "ベースラインと同じ貢献利益を保つには販売量が {be:.1f}% 以上増える必要がある",
        "reading_inc": "販売量の減少が {be:.1f}% 以内ならベースラインの貢献利益を維持できる",
        "reading_none": "ベースラインと同じ販売量で損益分岐する",
        "reading_infeasible": "損益分岐に到達できない（価格変化で貢献利益が消える）",
        "profit": "販売量の反応別の貢献利益の増減（ベースライン比）",
        "volume_resp": "販売量の反応",
        "fixed": "増分固定費 {fc} を含む",
        "reading": "読み方",
        "volume": "販売量",
        "scen_note": "ベースラインの販売量に対する変化率",
        "values_in": "単位 {cur}",
        "note": "増分コストのみを使用。埋没費用・配賦費用は意図的に除外している。",
        "reactive_title": "反応的価格変更（競合への追随）",
        "reactive_col": "追随しない場合の販売損失がこれを超えるときだけ追随が得",
        "reactive_reading": "追随しないことで失う販売量が {t:.1f}% を超えない限り {p0} を維持する方が得",
    },
}


def analyze(spec: dict) -> dict:
    b = spec["baseline"]
    p0, c0 = float(b["price"]), float(b["unit_cost"])
    v0 = b.get("volume")
    v0 = float(v0) if v0 is not None else None
    cm0 = p0 - c0
    if cm0 <= 0:
        raise SystemExit("baseline contribution margin must be positive")
    scenarios = spec.get("volume_scenarios_pct") or [-30, -15, 0, 15, 30]
    out = {"currency": spec.get("currency", ""), "unit": spec.get("unit", ""),
           "baseline": {"price": p0, "unit_cost": c0, "cm": cm0, "cm_pct": cm0 / p0 * 100, "volume": v0},
           "scenarios_pct": scenarios, "candidates": []}
    for cand in spec["candidates"]:
        p1 = float(cand["price"])
        c1 = float(cand.get("unit_cost", c0))
        fc = float(cand.get("incremental_fixed_cost", 0.0))
        cm1 = p1 - c1
        d_cm = cm1 - cm0
        row = {"price": p1, "unit_cost": c1, "cm": cm1, "cm_pct": (cm1 / p1 * 100) if p1 else None,
               "price_change_pct": (p1 - p0) / p0 * 100, "incremental_fixed_cost": fc}
        if cm1 <= 0:
            row["breakeven_pct"] = None
            row["feasible"] = False
        else:
            be = -d_cm / cm1 * 100  # = -ΔCM / new CM
            row["breakeven_pct"] = be
            row["feasible"] = True
            if v0 is not None:
                be_units = v0 * be / 100 + (fc / cm1 if fc else 0.0)
                row["breakeven_units"] = be_units
                row["breakeven_volume"] = v0 + be_units
                row["breakeven_pct_incl_fixed"] = be_units / v0 * 100
        if v0 is not None and cm1 > 0:
            base_contrib = v0 * cm0
            row["profit_by_scenario"] = []
            for s in scenarios:
                v1 = v0 * (1 + s / 100)
                delta = v1 * cm1 - fc - base_contrib
                row["profit_by_scenario"].append({"volume_pct": s, "volume": v1, "delta_contribution": delta})
        if spec.get("reactive") and cm1 < cm0:
            row["reactive_threshold_pct"] = (cm0 - cm1) / cm0 * 100
        out["candidates"].append(row)
    out["reactive"] = bool(spec.get("reactive"))
    return out


def fmt_money(x: float, cur: str) -> str:
    s = f"{x:,.2f}" if abs(x) < 1000 else f"{x:,.0f}"
    return f"{s} {cur}".strip()


def render_md(res: dict, lang: str) -> str:
    L = LABELS.get(lang, LABELS["en"])
    cur = res["currency"]
    b = res["baseline"]
    lines = [f"### {L['title']}", "",
             f"{L['baseline']}: {fmt_money(b['price'], cur)} {res['unit']} — {L['cm']} {fmt_money(b['cm'], cur)} ({b['cm_pct']:.1f}%)"
             + (f", {L['volume']} {b['volume']:,.0f}" if b['volume'] else ""), ""]
    lines.append(f"| {L['candidate']} | {L['change']} | {L['cm']} | {L['be']} | " + ("" if not b["volume"] else f"{L['be_units']} | ") + f"{L['reading']} |")
    lines.append("|---|---|---|---|" + ("" if not b["volume"] else "---|") + "---|")
    for r in res["candidates"]:
        chg = f"{r['price_change_pct']:+.1f}%"
        if not r["feasible"]:
            be_s, read = "—", L["reading_infeasible"]
        else:
            be = r.get("breakeven_pct_incl_fixed", r["breakeven_pct"]) if r["incremental_fixed_cost"] else r["breakeven_pct"]
            be_s = f"{r['breakeven_pct']:+.1f}%"
            if abs(be) < 1e-9:
                read = L["reading_none"]
            elif be > 0:
                read = L["reading_cut"].format(be=be)
            else:
                read = L["reading_inc"].format(be=-be)
            if r["incremental_fixed_cost"] and "breakeven_pct_incl_fixed" in r:
                be_s += f" ({r['breakeven_pct_incl_fixed']:+.1f}% {L['fixed'].format(fc=fmt_money(r['incremental_fixed_cost'], cur))})"
        vol_s = f"{math.ceil(r['breakeven_volume'] - 1e-9):,} | " if (b["volume"] and r.get("breakeven_volume") is not None) else ("— | " if b["volume"] else "")
        lines.append(f"| {fmt_money(r['price'], cur)} | {chg} | {fmt_money(r['cm'], cur)} ({r['cm_pct']:.1f}%) | {be_s} | {vol_s}{read} |")
    if b["volume"]:
        lines += ["", f"#### {L['profit']}", ""]
        head = f"| {L['candidate']} | " + " | ".join(f"{s:+g}%" for s in res["scenarios_pct"]) + " |"
        lines.append(head)
        lines.append("|---|" + "---|" * len(res["scenarios_pct"]))
        for r in res["candidates"]:
            if "profit_by_scenario" not in r:
                lines.append(f"| {fmt_money(r['price'], cur)} | " + " | ".join("—" for _ in res["scenarios_pct"]) + " |")
                continue
            cells = [f"{s['delta_contribution']:+,.0f}" for s in r["profit_by_scenario"]]
            lines.append(f"| {fmt_money(r['price'], cur)} | " + " | ".join(cells) + " |")
        lines.append("")
        lines.append(f"({L['volume_resp']}: {L['scen_note']}" + (f"; {L['values_in'].format(cur=cur)}" if cur else "") + ")")
    lines += ["", L["note"]]
    return "\n".join(lines)


CANN_LABELS = {
    "en": {"title": "Cannibalization analysis of a new lower tier", "full": "Existing tier",
           "lite": "New tier price", "cm": "Contribution / unit", "net": "Net replacement (new units per downgrade)",
           "gross": "Gross replacement (new-tier units per existing-tier unit)", "need": "New-tier units needed to break even",
           "rate": "downgrade rate", "downgrades": "downgrades", "infeasible": "new tier has no positive contribution",
           "note": "Net ratio = (CM_full − CM_new) ÷ CM_new: new customers needed to offset one downgrade. "
                   "Gross ratio = CM_full ÷ CM_new: new-tier units equal to one existing-tier unit. State which one you quote."},
    "ja": {"title": "新しい下位プランによる共食いの分析", "full": "既存プラン",
           "lite": "新プランの価格", "cm": "単位あたり貢献利益", "net": "純増換算（ダウングレード 1 件を埋める新規数）",
           "gross": "総量換算（既存 1 台に相当する新プラン台数）", "need": "損益分岐に必要な新プランの新規販売数",
           "rate": "ダウングレード率", "downgrades": "ダウングレード件数", "infeasible": "新プランの貢献利益が正でない",
           "note": "純増換算 = (既存の貢献利益 − 新プランの貢献利益) ÷ 新プランの貢献利益（ダウングレード 1 件を埋める新規顧客数）。"
                   "総量換算 = 既存の貢献利益 ÷ 新プランの貢献利益（既存 1 台と同じ貢献利益になる新プラン台数）。どちらの値かを必ず明記する。"},
}


def analyze_cannibalization(c: dict) -> dict:
    full = c["full"]
    pf, cf = float(full["price"]), float(full["unit_cost"])
    vf = float(full["volume"]) if full.get("volume") is not None else None
    cmf = pf - cf
    rates = c.get("downgrade_rates_pct") or [5, 10, 20]
    fc = float(c.get("lite_fixed_cost", 0) or 0)
    rows = []
    for cand in c["lite_candidates"]:
        pl = float(cand["price"]); cl = float(cand.get("unit_cost", cf)); cml = pl - cl
        r = {"price": pl, "unit_cost": cl, "cm": cml}
        if cml <= 0:
            r["feasible"] = False
        else:
            r["feasible"] = True
            r["net_ratio"] = (cmf - cml) / cml
            r["gross_ratio"] = cmf / cml
            if vf is not None:
                r["by_rate"] = []
                for rt in rates:
                    d = vf * rt / 100
                    need = (d * (cmf - cml) + fc) / cml
                    r["by_rate"].append({"downgrade_rate_pct": rt, "downgrades": d, "new_units_needed": need})
        rows.append(r)
    return {"mode": "cannibalization", "full": {"price": pf, "unit_cost": cf, "cm": cmf, "volume": vf},
            "lite_fixed_cost": fc, "rates": rates, "candidates": rows}


def render_cann_md(res: dict, lang: str, cur: str) -> str:
    L = CANN_LABELS.get(lang, CANN_LABELS["en"])
    f = res["full"]
    out = [f"### {L['title']}", "",
           f"{L['full']}: {fmt_money(f['price'], cur)} — {L['cm']} {fmt_money(f['cm'], cur)}"
           + (f", volume {f['volume']:,.0f}" if f["volume"] else ""), "",
           f"| {L['lite']} | {L['cm']} | {L['net']} | {L['gross']} |", "|---|---|---|---|"]
    for r in res["candidates"]:
        if not r["feasible"]:
            out.append(f"| {fmt_money(r['price'], cur)} | {fmt_money(r['cm'], cur)} | {L['infeasible']} | — |")
        else:
            out.append(f"| {fmt_money(r['price'], cur)} | {fmt_money(r['cm'], cur)} | {r['net_ratio']:.2f} | {r['gross_ratio']:.2f} |")
    if f["volume"]:
        out += ["", f"#### {L['need']}", "",
                f"| {L['lite']} | " + " | ".join(f"{L['rate']} {x}%" for x in res["rates"]) + " |",
                "|---|" + "---|" * len(res["rates"])]
        for r in res["candidates"]:
            if not r.get("by_rate"):
                continue
            out.append(f"| {fmt_money(r['price'], cur)} | " + " | ".join(
                f"{b['new_units_needed']:,.1f} ({b['downgrades']:,.0f} {L['downgrades']})" for b in r["by_rate"]) + " |")
    out += ["", L["note"]]
    return "\n".join(out)


def slides(res: dict, spec: dict, lang: str, directory: str, with_logic: bool = False) -> None:
    """Slot data for breakeven-sales-change (and competitor-response when reactive)."""
    import slide_data as sl
    T = sl.text(lang)
    todo = sl.TODO.get(lang, sl.TODO["en"]).strip()
    cands = res["candidates"]
    if len(cands) > 5:
        print(f"slides: the slide holds 5 candidates; using the first 5 of {len(cands)}", file=sys.stderr)
    rows = []
    if len(cands) < 2:
        print("slides: breakeven-sales-change needs 2 or more candidates; skipped", file=sys.stderr)
    for c, src in list(zip(cands, spec["candidates"]))[:5]:
        be = c.get("breakeven_pct")
        rows.append([sl.num(c["price"]), sl.pct(c["price_change_pct"]), sl.num(c["cm"]),
                     sl.pct(be) if be is not None else "—",
                     src.get("expected", todo),
                     src.get("verdict", todo if c["feasible"] else T["no_recovery"])])
    if len(rows) >= 2:
        sl.write(directory, "breakeven-sales-change",
                 {**sl.common(lang), "rows": rows, "insight": sl.todo(lang, "insight")})
    reactive = [c for c in cands if "reactive_threshold_pct" in c]
    if res["reactive"] and reactive:
        rows = [[q, todo, todo] for q in T["questions"]]
        sl.write(directory, "competitor-response",
                 {**sl.common(lang), "rows": rows,
                  "thresholdValue": sl.pct(reactive[0]["reactive_threshold_pct"], signed=False),
                  "expectedValue": spec.get("expected_loss", todo),
                  "recommendation": sl.todo(lang, "recommendation")})
    if with_logic:
        logic_slides(res, lang, directory, sl, T, spec.get("volume_unit", ""))


def logic_slides(res: dict, lang: str, directory: str, sl, T: dict, vunit: str = "") -> None:
    b = res["baseline"]
    p0, c0, cm0 = b["price"], b["unit_cost"], b["cm"]
    cur = res["currency"]
    m = lambda x: sl.u(x, cur)  # noqa: E731 - money with its currency
    head = [[T["cm0"], f"{m(p0)} − {m(c0)}（{T['cost0']}）", f"{m(cm0)}（{b['cm_pct']:.1f}%）"]]
    if b["volume"] is not None and len(head) + len(res["candidates"]) < sl.LOGIC_ROWS:
        head.append([T["volume"], sl.u(b["volume"], vunit), T["baseline"]])
    rows = list(head)
    for c in res["candidates"][:sl.LOGIC_ROWS - len(head)]:
        name = T["cand"].format(p=m(c["price"]))
        be = c.get("breakeven_pct")
        if be is None:
            rows.append([name, f"{m(c['price'])} − {m(c['unit_cost'])} ≤ 0", T["never"]])
            continue
        dp = c["price"] - p0
        if c["unit_cost"] == c0:
            how = f"{m(-dp)} ÷ ({m(cm0)} {'+' if dp >= 0 else '−'} {m(abs(dp))}) = {sl.pct(be)}"
        else:
            how = f"{m(-(c['cm'] - cm0))} ÷ {m(c['cm'])} = {sl.pct(be)}"
        how = how.replace("-", "−")
        note = T["need_up"] if be > 0 else T["allow_down"]
        rows.append([name, how, note.format(v=f"{abs(be):.1f}%")])
    sl.write(directory, "calculation-logic-breakeven", sl.logic(lang, "f_be", rows))
    reactive = [c for c in res["candidates"] if "reactive_threshold_pct" in c]
    if res["reactive"] and reactive:
        rows = [[T["cm0"], f"{m(p0)} − {m(c0)}", m(cm0)]]
        for c in reactive[:sl.LOGIC_ROWS - 1]:
            rows.append([T["cand"].format(p=m(c["price"])),
                         f"({m(cm0)} − {m(c['cm'])}) ÷ {m(cm0)} = {c['reactive_threshold_pct']:.1f}%",
                         T["threshold"]])
        sl.write(directory, "calculation-logic-reactive", sl.logic(lang, "f_re", rows))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", help="JSON spec file")
    ap.add_argument("--price", type=float, help="baseline price")
    ap.add_argument("--cost", type=float, help="baseline incremental unit cost")
    ap.add_argument("--volume", type=float, help="baseline volume (optional)")
    ap.add_argument("--candidates", help="comma-separated candidate prices")
    ap.add_argument("--currency", default="")
    ap.add_argument("--unit", default="")
    ap.add_argument("--lang", default="en", help="label language for markdown (en, ja)")
    ap.add_argument("--json", action="store_true", help="print JSON instead of markdown")
    ap.add_argument("--reactive", action="store_true", help="also report the reactive (match-a-competitor) threshold")
    ap.add_argument("--slides", metavar="DIR", help="also write slide-forge slot data (pricing pack) into DIR")
    ap.add_argument("--slides-logic", action="store_true", help="with --slides, also write calculation-logic slides")
    a = ap.parse_args()
    if a.slides_logic and not a.slides:
        ap.error("--slides-logic needs --slides DIR")
    if a.input:
        spec = json.load(open(a.input, encoding="utf-8"))
    elif a.price is not None and a.cost is not None and a.candidates:
        spec = {"currency": a.currency, "unit": a.unit,
                "baseline": {"price": a.price, "unit_cost": a.cost, "volume": a.volume},
                "candidates": [{"price": float(x)} for x in a.candidates.split(",") if x.strip()]}
    else:
        ap.error("give --input or --price/--cost/--candidates")
    if a.reactive:
        spec["reactive"] = True
    if "cannibalization" in spec:
        res = analyze_cannibalization(spec["cannibalization"])
        print(json.dumps(res, ensure_ascii=False, indent=2) if a.json
              else render_cann_md(res, a.lang, spec.get("currency", "")))
        if "baseline" not in spec:
            return 0
        print()
    res = analyze(spec)
    if a.slides:
        slides(res, spec, a.lang, a.slides, a.slides_logic)
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print(render_md(res, a.lang))
        rows = [c for c in res["candidates"] if "reactive_threshold_pct" in c]
        if res["reactive"] and rows:
            L = LABELS.get(a.lang, LABELS["en"]); cur = res["currency"]
            print(f"\n#### {L['reactive_title']}\n")
            print(f"| {L['candidate']} | {L['reactive_col']} | {L['reading']} |\n|---|---|---|")
            for c in rows:
                print(f"| {fmt_money(c['price'], cur)} | {c['reactive_threshold_pct']:.1f}% | "
                      + L["reactive_reading"].format(p0=fmt_money(res['baseline']['price'], cur), t=c["reactive_threshold_pct"]) + " |")
    return 0


if __name__ == "__main__":
    sys.exit(main())
