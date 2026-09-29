#!/usr/bin/env python3
"""Compare candidate price structures across a customer-size distribution.

Each option is a base fee per customer plus a tiered per-unit rate (per seat,
per Pod, per GB ...). For every option the script reports revenue and
contribution over the whole distribution, the change against the baseline
option, the price each customer size pays, and that price as a share of the
customer's economic value. A base fee can be solved so the option is
revenue-neutral (or contribution-neutral) against the baseline.

Input JSON (see skills/pricing-strategy/references/price-structure.md):
{
  "currency": "USD", "period": "per year", "unit_label": "seat",
  "unit_cost": 180,                       # incremental cost per unit per period
  "customer_cost": 0,                     # optional incremental cost per customer
  "distribution": [{"size": 2, "count": 30}, {"size": 10, "count": 15}],
  "value": 11200,                         # economic value per customer (number),
                                          # or {"2": 8000, "10": 15000} by size,
                                          # or {"base": 5000, "per_unit": 600}
  "baseline": "Per-unit only",            # name of the option to compare against
  "options": [
    {"name": "Per-unit only", "tiers": [{"from": 1, "rate": 1140}]},
    {"name": "Two-part", "base_fee": "neutral", "tiers": [{"from": 1, "rate": 600}]},
    {"name": "Volume discount", "tiers": [{"from": 1, "rate": 1140}, {"from": 9, "rate": 570}]},
    {"name": "Platform + included", "base_fee": 3000, "included_units": 4,
     "tiers": [{"from": 1, "rate": 700}]}
  ],
  "neutral_on": "revenue",                # or "contribution" (for "base_fee": "neutral")
  "recovery_size": 10,                    # optional: size of an extra customer used to
                                          # express a contribution loss as deals needed
  "show_sizes": [2, 4, 10, 16]            # optional: columns in the summary table
}

Tiers are incremental (graduated): units from `from` up to the next tier's
`from` - 1 are charged at `rate`. `included_units` are covered by the base fee
and not charged per unit. Optional `min_fee` and `max_fee` clamp the total.
Optional `discounts`, e.g. [{"min_size": 9, "pct": 35}], take a percentage off
the total for customers at or above `min_size` (the largest matching rule wins);
use it to model today's realized prices when large accounts get negotiated
discounts. `show_sizes` may include sizes outside the distribution.

Slides: --slides DIR writes price-structure-compare.json for the slide-forge
`pricing` pack (see scripts/pricing/slide_data.py). Columns are the options (up to 4); give
an option a "short" name (12 characters or fewer) for the column heading. The
metrics describe "recommended" (an option name; default: the first option
other than the baseline). Rows are show_sizes (up to 6). --slides-logic adds
calculation-logic-structure.json: each option's fee definition, costs, the
distribution and the value basis.

Usage: structure_compare.py --input structures.json [--json] [--lang en|ja] [--slides DIR [--slides-logic]]
"""
from __future__ import annotations
import argparse, json, sys

LABELS = {
    "en": {"title": "Price structure comparison", "option": "Option", "revenue": "Revenue",
           "contribution": "Contribution", "vs": "Contribution vs. baseline", "by_size": "Price by customer size",
           "size": "Size ({u})", "customers": "Customers", "value": "Economic value",
           "price": "Price", "share": "Price / value", "base_fee": "base fee {v} (solved: {how}-neutral)",
           "recovery": "{name}: contribution {d} lower than baseline; needs {n:.1f} extra customers of size {s} "
                       "(each contributes {c}) to break even",
           "over": "Sizes where price exceeds economic value: {sizes}",
           "assumption": "Distribution and value are assumptions unless marked confirmed; rerun with actual contract data."},
    "ja": {"title": "価格構造の比較", "option": "案", "revenue": "売上", "contribution": "貢献利益",
           "vs": "貢献利益（基準比）", "by_size": "顧客規模別の価格", "size": "規模（{u}）", "customers": "顧客数",
           "value": "経済的価値", "price": "価格", "share": "価格／価値",
           "base_fee": "基本料 {v}（{how}中立になるよう算出）",
           "recovery": "{name}: 貢献利益が基準より {d} 少ない。規模 {s} の顧客（1 件の貢献利益 {c}）を "
                       "{n:.1f} 件追加で獲得すれば損益分岐",
           "over": "価格が経済的価値を超える規模: {sizes}",
           "assumption": "分布と価値は、確認済みと明記したもの以外は仮定である。実際の契約データで再実行すること。"},
}
NEUTRAL = {"en": {"revenue": "revenue", "contribution": "contribution"}, "ja": {"revenue": "売上", "contribution": "貢献利益"}}


def unit_charge(units: float, tiers: list[dict]) -> float:
    tiers = sorted(tiers, key=lambda t: t.get("from", 1))
    total = 0.0
    for i, t in enumerate(tiers):
        lo = t.get("from", 1)
        hi = tiers[i + 1]["from"] - 1 if i + 1 < len(tiers) else float("inf")
        n = max(0.0, min(units, hi) - lo + 1)
        total += n * t["rate"]
    return total


def price_of(opt: dict, size: float, base_fee: float) -> float:
    billable = max(0.0, size - opt.get("included_units", 0))
    p = base_fee + unit_charge(billable, opt.get("tiers", []))
    if "min_fee" in opt:
        p = max(p, opt["min_fee"])
    if "max_fee" in opt:
        p = min(p, opt["max_fee"])
    rules = [d for d in opt.get("discounts", []) if size >= d["min_size"]]
    if rules:
        p *= 1 - max(rules, key=lambda d: d["min_size"])["pct"] / 100
    return p


def value_of(spec, size: float) -> float | None:
    if spec is None:
        return None
    if isinstance(spec, (int, float)):
        return float(spec)
    if "per_unit" in spec or "base" in spec:
        return spec.get("base", 0) + spec.get("per_unit", 0) * size
    key = str(int(size)) if float(size).is_integer() else str(size)
    return spec.get(key)


def evaluate(spec: dict) -> dict:
    dist = spec["distribution"]
    ucost, ccost = spec.get("unit_cost", 0), spec.get("customer_cost", 0)
    cost = lambda s: s * ucost + ccost
    opts = spec["options"]
    names = [o["name"] for o in opts]
    base_name = spec.get("baseline", names[0])
    if base_name not in names:
        sys.exit(f"baseline '{base_name}' is not among options {names}")
    base_opt = next(o for o in opts if o["name"] == base_name)
    if base_opt.get("base_fee") == "neutral":
        sys.exit("the baseline option cannot have base_fee 'neutral'")

    def totals(opt, fee):
        rev = sum(price_of(opt, d["size"], fee) * d["count"] for d in dist)
        con = sum((price_of(opt, d["size"], fee) - cost(d["size"])) * d["count"] for d in dist)
        return rev, con

    b_rev, b_con = totals(base_opt, base_opt.get("base_fee", 0))
    neutral_on = spec.get("neutral_on", "revenue")
    results = []
    for o in opts:
        fee, solved = o.get("base_fee", 0), None
        if fee == "neutral":
            if "min_fee" in o or "max_fee" in o:
                sys.exit(f"option '{o['name']}': base_fee 'neutral' cannot be combined with min_fee/max_fee")
            r0, c0 = totals(o, 0)
            r1, c1 = totals(o, 1)
            fee = ((b_rev - r0) / (r1 - r0)) if neutral_on == "revenue" else ((b_con - c0) / (c1 - c0))
            solved = neutral_on
        rev, con = totals(o, fee)
        rows = []
        for d in dist:
            p, v = price_of(o, d["size"], fee), value_of(spec.get("value"), d["size"])
            rows.append({"size": d["size"], "customers": d["count"], "price": p, "value": v,
                         "price_to_value_pct": (p / v * 100) if v else None})
        res = {"name": o["name"], "base_fee": fee, "base_fee_solved": solved, "revenue": rev,
               "contribution": con, "contribution_change": con - b_con,
               "contribution_change_pct": ((con - b_con) / b_con * 100) if b_con else None,
               "by_size": rows, "sizes_over_value": [r["size"] for r in rows
                                                     if r["price_to_value_pct"] and r["price_to_value_pct"] > 100]}
        rs = spec.get("recovery_size")
        if rs is not None and b_con - con > 0.5:
            per = price_of(o, rs, fee) - cost(rs)
            res["recovery"] = {"size": rs, "contribution_per_customer": per,
                               "customers_needed": (b_con - con) / per if per > 0 else None}
        res["price_at"] = (lambda s, o=o, fee=fee: price_of(o, s, fee))
        results.append(res)
    return {"currency": spec.get("currency", ""), "period": spec.get("period", ""),
            "unit_label": spec.get("unit_label", "unit"), "baseline": base_name,
            "neutral_on": neutral_on, "options": results}


def fmt(x: float, cur: str) -> str:
    return f"{x:,.0f} {cur}".strip()


def markdown(r: dict, spec: dict, lang: str) -> str:
    L = LABELS.get(lang, LABELS["en"])
    cur = r["currency"]
    sizes = spec.get("show_sizes") or [d["size"] for d in spec["distribution"]]
    out = [f"## {L['title']}" + (f" ({r['period']})" if r["period"] else ""), ""]
    head = [L["option"], L["revenue"], L["contribution"], L["vs"]] + [
        f"{L['size'].format(u=r['unit_label'])} {s}" for s in sizes]
    out += ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for o in r["options"]:
        name = o["name"]
        if o["base_fee_solved"]:
            name += "<br>" + L["base_fee"].format(v=fmt(o["base_fee"], cur),
                                                  how=NEUTRAL.get(lang, NEUTRAL["en"])[o["base_fee_solved"]])
        pct = o["contribution_change_pct"]
        cells = [name, fmt(o["revenue"], cur), fmt(o["contribution"], cur),
                 f"{pct:+.1f}%" if pct is not None else "—"]
        by = {row["size"]: row for row in o["by_size"]}
        for s in sizes:
            row = by.get(s)
            if row is None:
                p, v = o["price_at"](s), value_of(spec.get("value"), s)
                row = {"price": p, "price_to_value_pct": (p / v * 100) if v else None}
            share = f" ({row['price_to_value_pct']:.0f}%)" if row["price_to_value_pct"] is not None else ""
            cells.append(fmt(row["price"], cur) + share)
        out.append("| " + " | ".join(cells) + " |")
    out.append("")
    if spec.get("value") is not None:
        out.append(f"( ) = {L['share']}")
        out.append("")
    for o in r["options"]:
        if o["sizes_over_value"]:
            out.append(f"- {o['name']}: " + L["over"].format(sizes=", ".join(str(s) for s in o["sizes_over_value"])))
        rec = o.get("recovery")
        if rec and rec["customers_needed"] is not None:
            out.append("- " + L["recovery"].format(name=o["name"], d=fmt(-o["contribution_change"], cur),
                                                   s=rec["size"], c=fmt(rec["contribution_per_customer"], cur),
                                                   n=rec["customers_needed"]))
    out += ["", f"_{L['assumption']}_"]
    return "\n".join(out)


def slides(r: dict, spec: dict, lang: str, directory: str, with_logic: bool = False) -> None:
    """Slot data for price-structure-compare."""
    import slide_data as sl
    T = sl.text(lang)
    opts = r["options"][:4]
    short = {o["name"]: o.get("short", o["name"]) for o in spec["options"]}
    rec_name = spec.get("recommended") or next(o["name"] for o in r["options"] if o["name"] != r["baseline"])
    rec = next(o for o in r["options"] if o["name"] == rec_name)
    base = next(o for o in r["options"] if o["name"] == r["baseline"])
    sizes = (spec.get("show_sizes") or [d["size"] for d in spec["distribution"]])[:6]
    unit = r["unit_label"]
    rows, worst = [], None
    for s in sizes:
        v = value_of(spec.get("value"), s)
        cells = [f"{s} {unit}"]
        for o in opts:
            p = o["price_at"](s)
            cells.append(sl.num(p) + (f"（{p / v * 100:.0f}%）" if v else ""))
        rows.append(cells)
        b = base["price_at"](s)
        if b:
            up = (rec["price_at"](s) - b) / b * 100
            if worst is None or up > worst[0]:
                worst = (up, s)
    data = {**sl.common(lang), "headers": [T["size"]] + [sl.fit(short[o["name"]], 12, "option") for o in opts], "rows": rows}
    pct = rec["contribution_change_pct"]
    data["impactValue"] = sl.pct(pct) if pct is not None else "—"
    if worst:
        data["riskValue"] = sl.pct(worst[0])
        data["riskLabel"] = T["largest"].format(s=f"{worst[1]} {unit}")
    else:
        data["riskValue"] = "—"
    data["recommendation"] = sl.todo(lang, "recommendation")
    sl.write(directory, "price-structure-compare", data)
    if with_logic:
        logic_slide(r, spec, lang, directory, sl, T, short)


def logic_slide(r: dict, spec: dict, lang: str, directory: str, sl, T: dict, short: dict) -> None:
    cur, un = r["currency"], r["unit_label"]
    m = lambda x: sl.u(x, cur)  # noqa: E731 - money with its currency
    frm = lambda n: T["from"].format(n=sl.num(n), u=un)  # noqa: E731 - a size with its unit
    rows = []
    for o, src in list(zip(r["options"], spec["options"]))[:4]:  # up to 4 options, then context rows while room
        parts = []
        if o["base_fee"]:
            parts.append(T["base_fee"].format(v=m(o["base_fee"])) + (T["neutral"] if o["base_fee_solved"] else ""))
        if src.get("included_units"):
            parts.append(T["included"].format(v=sl.u(src["included_units"], un)))
        parts.append(T["usage"].format(cur=cur, u=un)
                     + "／".join(f"{frm(t['from'])} {sl.num(t['rate'])}" for t in src.get("tiers", [])))
        if src.get("discounts"):
            parts.append(T["disc"].format(v="／".join(f"{frm(d['min_size'])} {d['pct']}%" for d in src["discounts"])))
        pct = o["contribution_change_pct"]
        rows.append([short[o["name"]], "＋".join(parts), T["revenue"].format(c=sl.pct(pct) if pct is not None else "—")])
    dist = spec["distribution"]
    rows.append([T["cost"], T["cost_def"].format(u=un, v=m(spec.get("unit_cost", 0)), c=m(spec.get("customer_cost", 0))),
                 T["incremental"]])
    rows.append([T["dist"], T["dist_def"].format(u=un, v=", ".join(f"{d['size']}×{d['count']}" for d in dist)),
                 T["dist_n"].format(n=sum(d["count"] for d in dist))])
    v = spec.get("value")
    if v is not None and len(rows) < sl.LOGIC_ROWS:
        desc = (m(v) if isinstance(v, (int, float)) else
                T["value_by_size"].format(n=len(v), cur=cur) if "base" not in v else
                f"{m(v['base'])} ＋ {m(v['per_unit'])} × size")
        rows.append([T["value"], desc, T["assumed"]])
    sl.write(directory, "calculation-logic-structure", sl.logic(lang, "f_sc", rows))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", required=True, help="JSON spec file")
    ap.add_argument("--lang", default="en", help="label language for markdown (en, ja)")
    ap.add_argument("--json", action="store_true", help="print JSON instead of markdown")
    ap.add_argument("--slides", metavar="DIR", help="also write slide-forge slot data (pricing pack) into DIR")
    ap.add_argument("--slides-logic", action="store_true", help="with --slides, also write a calculation-logic slide")
    a = ap.parse_args()
    if a.slides_logic and not a.slides:
        ap.error("--slides-logic needs --slides DIR")
    with open(a.input, encoding="utf-8") as f:
        spec = json.load(f)
    r = evaluate(spec)
    if a.slides:
        slides(r, spec, a.lang, a.slides, a.slides_logic)
    if a.json:
        for o in r["options"]:
            o.pop("price_at", None)
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        print(markdown(r, spec, a.lang))
    return 0


if __name__ == "__main__":
    sys.exit(main())
