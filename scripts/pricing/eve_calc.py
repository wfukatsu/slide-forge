#!/usr/bin/env python3
"""Economic value estimation (EVE) per segment.

Reads a JSON of segments, reference values and value drivers, evaluates each
driver's formula, and prints a per-segment EVE table with differentiation
share and the ordered value profile.

Input JSON (see skills/pricing-strategy/references/economic-value.md):
{
  "unit": "per site per year", "currency": "USD",
  "segments": [{
    "name": "Mid-size manufacturers",
    "reference": {"alternative": "Vendor X + in-house integration", "value": 30000},
    "drivers": [
      {"name": "Integration labor avoided", "type": "monetary", "sign": "+",
       "formula": "hours × rate", "inputs": {"hours": 400, "rate": 90},
       "units": {"hours": "h", "rate": "USD/h"}},     # optional, shown by --slides-logic
      {"name": "Vendor risk", "type": "psychological", "sign": "-", "value": 5000}
    ],
    "price": 24000}]                      # optional: current/candidate price, used by --slides
}

Usage: eve_calc.py --input eve.json [--json] [--lang en|ja] [--slides DIR [--slides-logic]]

--slides DIR writes one economic-value-waterfall slot file per segment for the
slide-forge `pricing` pack (see scripts/pricing/slide_data.py). A driver may carry a
"short" name (12 characters or fewer) for the bar label; more than 5 drivers
are folded into "Other". --slides-logic adds one calculation-logic slide per
segment (each driver's formula with its input values substituted).
"""
from __future__ import annotations
import argparse, ast, json, operator, sys

LABELS = {
    "en": {"title": "Economic value estimation", "segment": "Segment", "ref": "Reference value",
           "alt": "Next-best alternative", "pos": "Positive differentiation", "neg": "Negative differentiation",
           "tev": "Total economic value", "share": "Differentiation share", "driver": "Value driver",
           "type": "Type", "value": "Value", "formula": "Formula", "profile": "Value profile (largest first)",
           "monetary": "monetary", "psychological": "psychological",
           "note": "Economic value is the ceiling of the price range for the segment, not the recommended price."},
    "ja": {"title": "経済的価値推定（EVE）", "segment": "セグメント", "ref": "参照価値",
           "alt": "次善の競合代替品", "pos": "正の差別化価値", "neg": "負の差別化価値",
           "tev": "総経済価値", "share": "差別化価値の比率", "driver": "価値ドライバー",
           "type": "種類", "value": "金額", "formula": "算式", "profile": "価値プロファイル（大きい順）",
           "monetary": "金銭的", "psychological": "心理的",
           "note": "総経済価値はそのセグメントの価格レンジの天井であり、推奨価格ではない。"},
}

_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv,
        ast.Pow: operator.pow, ast.USub: operator.neg}


def safe_eval(expr: str, env: dict) -> float:
    expr = expr.replace("×", "*").replace("÷", "/").replace("−", "-")
    tree = ast.parse(expr, mode="eval")

    def ev(n):
        if isinstance(n, ast.Expression):
            return ev(n.body)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return float(n.value)
        if isinstance(n, ast.Name):
            if n.id not in env:
                raise ValueError(f"unknown input '{n.id}' in formula '{expr}'")
            return float(env[n.id])
        if isinstance(n, ast.BinOp) and type(n.op) in _OPS:
            return _OPS[type(n.op)](ev(n.left), ev(n.right))
        if isinstance(n, ast.UnaryOp) and type(n.op) in _OPS:
            return _OPS[type(n.op)](ev(n.operand))
        raise ValueError(f"unsupported expression in formula '{expr}'")
    return ev(tree)


def compute(spec: dict) -> dict:
    out = {"unit": spec.get("unit", ""), "currency": spec.get("currency", ""), "segments": []}
    for seg in spec["segments"]:
        ref = seg.get("reference", {}) or {}
        ref_val = float(ref.get("value", 0) or 0)
        drivers = []
        pos = neg = 0.0
        for d in seg.get("drivers", []):
            if "value" in d:
                val = float(d["value"])
            elif "formula" in d:
                val = safe_eval(d["formula"], d.get("inputs", {}))
            else:
                raise SystemExit(f"driver '{d.get('name')}' needs 'value' or 'formula'")
            sign = -1.0 if str(d.get("sign", "+")).strip() == "-" else 1.0
            signed = sign * abs(val)
            if signed >= 0:
                pos += signed
            else:
                neg += -signed
            drivers.append({"name": d.get("name", ""), "short": d.get("short"), "type": d.get("type", "monetary"), "sign": "+" if sign > 0 else "-",
                            "value": abs(val), "signed_value": signed, "formula": d.get("formula"), "inputs": d.get("inputs"), "units": d.get("units"),
                            "source": d.get("source")})
        tev = ref_val + pos - neg
        diff = pos - neg
        share = (diff / tev * 100) if tev else None
        profile = sorted(drivers, key=lambda x: -abs(x["signed_value"]))
        out["segments"].append({"name": seg.get("name", ""), "alternative": ref.get("alternative", ""),
                                "reference_value": ref_val, "positive_differentiation": pos,
                                "negative_differentiation": neg, "total_economic_value": tev,
                                "differentiation_share_pct": share, "drivers": drivers, "profile": profile})
    return out


def money(x: float, cur: str) -> str:
    s = f"{x:,.0f}" if abs(x) >= 100 or float(x).is_integer() else f"{x:,.2f}"
    return s + (f" {cur}" if cur else "")


def render_md(res: dict, lang: str) -> str:
    L = LABELS.get(lang, LABELS["en"])
    cur = res["currency"]
    lines = [f"### {L['title']}" + (f" ({res['unit']})" if res["unit"] else ""), "",
             f"| {L['segment']} | {L['alt']} | {L['ref']} | {L['pos']} | {L['neg']} | {L['tev']} | {L['share']} |",
             "|---|---|---|---|---|---|---|"]
    for s in res["segments"]:
        share = f"{s['differentiation_share_pct']:.0f}%" if s["differentiation_share_pct"] is not None else "—"
        lines.append(f"| {s['name']} | {s['alternative']} | {money(s['reference_value'], cur)} | +{money(s['positive_differentiation'], cur)} | −{money(s['negative_differentiation'], cur)} | {money(s['total_economic_value'], cur)} | {share} |")
    for s in res["segments"]:
        lines += ["", f"#### {s['name']} — {L['profile']}", "",
                  f"| {L['driver']} | {L['type']} | {L['value']} | {L['formula']} |", "|---|---|---|---|"]
        for d in s["profile"]:
            f = d["formula"] or ""
            if d["inputs"]:
                f += " (" + ", ".join(f"{k}={v}" for k, v in d["inputs"].items()) + ")"
            lines.append(f"| {d['name']} | {L.get(d['type'], d['type'])} | {'−' if d['sign'] == '-' else '+'}{money(d['value'], cur)} | {f} |")
    lines += ["", L["note"]]
    return "\n".join(lines)


def slides(res: dict, spec: dict, lang: str, directory: str, with_logic: bool = False) -> None:
    """One economic-value-waterfall per segment (slide-forge `pricing` pack)."""
    import slide_data as sl
    T = sl.text(lang)
    for i, (s, seg) in enumerate(zip(res["segments"], spec["segments"]), 1):
        ds = sorted(s["drivers"], key=lambda d: (d["signed_value"] < 0, -abs(d["signed_value"])))
        if len(ds) > 5:  # the template holds 7 bars: reference + 5 drivers + total
            rest = sum(d["signed_value"] for d in ds[4:])
            ds = ds[:4] + [{"name": T["other"], "signed_value": rest}]
        items = [["参照価値" if lang == "ja" else "Reference",
                  s["reference_value"], "total"]]
        items += [[sl.fit(d.get("short") or d["name"], 12, "driver"), d["signed_value"], "delta"] for d in ds]
        items.append(["総経済価値" if lang == "ja" else "Total value", s["total_economic_value"], "total"])
        data = {**sl.common(lang), "items": items}
        price = seg.get("price")
        cur = f"（{res['currency']}）" if lang == "ja" else f" ({res['currency']})"
        if res["currency"]:
            data["priceLabel"] = ("価格" if lang == "ja" else "Price") + cur
            data["incentiveLabel"] = ("顧客に残す価値" if lang == "ja" else "Customer incentive") + cur
        data["priceValue"] = sl.num(price) if price is not None else sl.TODO.get(lang, sl.TODO["en"]).strip()
        data["incentiveValue"] = (sl.num(s["total_economic_value"] - price) if price is not None
                                  else sl.TODO.get(lang, sl.TODO["en"]).strip())
        share = s["differentiation_share_pct"]
        data["shareValue"] = sl.pct(share, signed=False) if share is not None else "—"
        sl.write(directory, f"economic-value-waterfall-{i}", data)
        if with_logic:
            cur = res["currency"]
            rows = [[T["reference"], s["alternative"], sl.u(s["reference_value"], cur)]]
            ld = s["profile"]
            if len(ld) > sl.LOGIC_ROWS - 2:  # keep the reference and total rows
                k = sl.LOGIC_ROWS - 3
                rest = ld[k:]
                ld = ld[:k] + [{"name": T["other"], "formula": None,
                                "signed_value": sum(d["signed_value"] for d in rest),
                                "folded": "・".join(d.get("short") or d["name"] for d in rest)}]
            for d in ld:
                how = (d["folded"] if d.get("folded") else
                       sl.substitute(d["formula"], d.get("inputs"), d.get("units")) if d.get("formula") else T["direct"])
                rows.append([d.get("short") or d["name"], how, ("+" if d["signed_value"] >= 0 else "−") + sl.u(abs(d["signed_value"]), cur)])
            share = s["differentiation_share_pct"]
            rows.append([T["tev"], T["sum_row"].format(p=sl.u(s["positive_differentiation"], cur),
                                                     n=sl.u(s["negative_differentiation"], cur),
                                                     s=sl.pct(share, signed=False) if share is not None else "—"),
                         sl.u(s["total_economic_value"], cur)])
            sl.write(directory, f"calculation-logic-economic-value-{i}", sl.logic(lang, "f_eve", rows))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", required=True)
    ap.add_argument("--lang", default="en")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--slides", metavar="DIR", help="also write slide-forge slot data (pricing pack) into DIR")
    ap.add_argument("--slides-logic", action="store_true", help="with --slides, also write calculation-logic slides")
    a = ap.parse_args()
    if a.slides_logic and not a.slides:
        ap.error("--slides-logic needs --slides DIR")
    spec = json.load(open(a.input, encoding="utf-8"))
    res = compute(spec)
    print(json.dumps(res, ensure_ascii=False, indent=2) if a.json else render_md(res, a.lang))
    if a.slides:
        slides(res, spec, a.lang, a.slides, a.slides_logic)
    return 0


if __name__ == "__main__":
    sys.exit(main())
