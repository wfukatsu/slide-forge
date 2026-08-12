#!/usr/bin/env python3
"""Build the bilingual slide-template catalog from slide-templates/ metadata.

One run writes both languages:

  - references/slide-template-catalog.md     (English)
  - references/slide-template-catalog.ja.md  (Japanese)

Japanese text comes straight from each template.json (displayName /
description / answers / guardrails). English text comes from the sidecar
references/i18n/slide-template-catalog.en.json; a template with no entry
there falls back to its Japanese text with a warning, so adding a template
never breaks the build — add its English strings to the sidecar when ready.

Regeneration flow (after building the catalog deck and importing thumbnails
to references/images/slide-templates/<id>.png):

    .venv/bin/python scripts/build_template_catalog_doc.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "slide-templates/manifest.json"
DOC_EN = ROOT / "references/slide-template-catalog.md"
DOC_JA = ROOT / "references/slide-template-catalog.ja.md"
I18N = ROOT / "references/i18n/slide-template-catalog.en.json"
IMG_DIR = ROOT / "references/images/slide-templates"
IMG_REL = "images/slide-templates"

PACK_ORDER = ["marketing-analysis", "b2b-sales", "scalar-ae", "planning", "analysis"]

PACK_INTRO_JA = {
    "marketing-analysis": (
        "マーケティング分析パック",
        "市場・顧客・施策効果を分析するページ群。戦略（SWOT / 3C / TAM-SAM-SOM / "
        "ポジショニング）から顧客理解（RFM / コホート）、行動（ファネル）、"
        "効果検証（A/B テスト）までを 1 枚ずつのフォーマットにしている。",
    ),
    "b2b-sales": (
        "B2B セールスパック",
        "商談のステークホルダー構造とディスカバリー（課題探索）を可視化するページ群。"
        "誰が意思決定に効くのか・何がまだ聞けていないのかを 1 枚で共有する。",
    ),
    "scalar-ae": (
        "Scalar AE パック",
        "Scalar のアカウントエグゼクティブが商談レビュー・活動計画で使う定型ページ群。"
        "account.json（商談台帳）の内容をそのまま流し込める前提で設計されている。"
        "唯一の stable パック。",
    ),
    "planning": (
        "計画パック",
        "時間軸を持つ計画を示すページ群。線表（ガント）・年表・マイルストーンの "
        "3 形式で、粒度と用途が異なる。",
    ),
    "analysis": (
        "現状分析パック",
        "コンサルティングの現状分析・課題特定フレームワークをページ化した群。"
        "構造分解（ロジックツリー / KPI ツリー）、根本原因（なぜなぜ / 特性要因図）、"
        "定量絞り込み（パレート図）、ギャップ・業務フロー、外部環境（PEST / 5 フォース）、"
        "優先順位づけまでを揃えている。current-state-analysis スキルが使う。",
    ),
}

INFERENCE_LABEL = {
    "ja": {
        "descriptive": "記述（事実の整理）",
        "diagnostic": "診断（要因・構造の特定）",
        "causal": "因果（原因の主張）",
        "strategic": "戦略（評価と方向づけ）",
    },
    "en": {
        "descriptive": "Descriptive (organizing facts)",
        "diagnostic": "Diagnostic (identifying factors and structure)",
        "causal": "Causal (asserting causes)",
        "strategic": "Strategic (evaluation and direction-setting)",
    },
}

REGEN_FENCE = {
    "ja": [
        "```bash",
        "# このカタログを作り直す（テンプレートを追加したときも同じ手順）",
        "for pack in marketing-analysis b2b-sales scalar-ae planning analysis; do",
        "  .venv/bin/python scripts/build_slide_template_catalog.py \\",
        "      --pack $pack --out out/template-catalog/$pack.json",
        "done",
        "# 5 つの spec の slides を 1 つに結合して build_deck.py で生成し、",
        "# fetch_thumbnails.py の PNG を references/images/slide-templates/<id>.png に配置",
        ".venv/bin/python scripts/build_template_catalog_doc.py",
        "```",
    ],
    "en": [
        "```bash",
        "# Rebuild this catalog (same steps when adding a template)",
        "for pack in marketing-analysis b2b-sales scalar-ae planning analysis; do",
        "  .venv/bin/python scripts/build_slide_template_catalog.py \\",
        "      --pack $pack --out out/template-catalog/$pack.json",
        "done",
        "# Merge the 5 specs' slides into one deck, generate with build_deck.py,",
        "# then place the fetch_thumbnails.py PNGs at references/images/slide-templates/<id>.png",
        ".venv/bin/python scripts/build_template_catalog_doc.py",
        "```",
    ],
}


def load_templates() -> list[dict]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    out = []
    for entry in manifest["templates"]:
        t = json.loads((ROOT / "slide-templates" / entry["path"]).read_text(encoding="utf-8"))
        t["_status"] = entry.get("status", "")
        out.append(t)
    return out


def load_i18n() -> dict:
    if not I18N.exists():
        print(f"  warn: {I18N.relative_to(ROOT)} not found; English output will "
              "fall back to Japanese text", file=sys.stderr)
        return {"packs": {}, "templates": {}}
    return json.loads(I18N.read_text(encoding="utf-8"))


def template_strings(t: dict, lang: str, i18n: dict) -> dict:
    """displayName / description / answers / guardrails for one template."""
    ja = {
        "displayName": t["displayName"],
        "description": t.get("description", ""),
        "answers": " / ".join(t.get("answers") or []),
        "guardrails": t.get("guardrails") or [],
    }
    if lang == "ja":
        return ja
    en = i18n.get("templates", {}).get(t["id"])
    if not en:
        print(f"  warn: no English strings for template {t['id']!r}; "
              "falling back to Japanese", file=sys.stderr)
        return ja
    out = {k: en.get(k) or ja[k] for k in ("displayName", "description", "answers")}
    en_g = en.get("guardrails") or []
    if len(en_g) != len(ja["guardrails"]):
        print(f"  warn: guardrail count mismatch for {t['id']!r} "
              f"(ja={len(ja['guardrails'])} en={len(en_g)}); using Japanese",
              file=sys.stderr)
        out["guardrails"] = ja["guardrails"]
    else:
        out["guardrails"] = en_g
    return out


def pack_strings(pack: str, lang: str, i18n: dict) -> dict:
    name_ja, intro_ja = PACK_INTRO_JA[pack]
    ja = {"name": name_ja, "intro": intro_ja, "short": intro_ja.split("。")[0]}
    if lang == "ja":
        return ja
    en = i18n.get("packs", {}).get(pack)
    if not en:
        print(f"  warn: no English strings for pack {pack!r}; falling back to "
              "Japanese", file=sys.stderr)
        return ja
    return {"name": en.get("name") or ja["name"],
            "intro": en.get("intro") or ja["intro"],
            "short": en.get("short") or ja["short"]}


def render_template(t: dict, lang: str, i18n: dict) -> list[str]:
    s = template_strings(t, lang, i18n)
    if lang == "ja":
        head = f"### {s['displayName']}（`{t['id']}`）"
        answers_label, guard_label, inference_label = "**答える問い**", "使うときの決まり:", "**推論レベル**"
    else:
        head = f"### {s['displayName']} (`{t['id']}`)"
        answers_label, guard_label, inference_label = "**Answers**", "Guardrails:", "**Inference level**"
    lines = [head, ""]
    img = IMG_DIR / f"{t['id']}.png"
    if img.exists():
        lines += [f"![{s['displayName']}]({IMG_REL}/{t['id']}.png)", ""]
    lines += [s["description"], ""]
    if s["answers"]:
        lines += [f"{answers_label}: {s['answers']}", ""]
    figs = [f.get("type") for f in t.get("slide", {}).get("figures", []) if f.get("type")]
    meta = [f"**figures**: {', '.join(f'`{f}`' for f in dict.fromkeys(figs))}"]
    level = INFERENCE_LABEL[lang].get(t.get("inferenceLevel", ""), t.get("inferenceLevel", ""))
    if level:
        meta.append(f"{inference_label}: {level}")
    if t.get("_status"):
        meta.append(f"**status**: {t['_status']}")
    lines += ["  \n".join(meta), ""]
    if s["guardrails"]:
        lines += [guard_label, ""]
        lines += [f"- {g}" for g in s["guardrails"]]
        lines += [""]
    return lines


def render(lang: str, templates: list[dict], i18n: dict) -> str:
    by_pack: dict[str, list[dict]] = {}
    for t in templates:
        by_pack.setdefault(t["pack"], []).append(t)
    n = len(templates)

    if lang == "ja":
        header = [
            "*[English](slide-template-catalog.md)*",
            "",
            f"# スライドテンプレート カタログ（全 {n} 種）",
            "",
            "`slide-templates/` に登録されたテンプレートを実際に 1 枚ずつ生成して",
            "書き出した画像カタログ。**どのテンプレートで 1 枚を作るかを見て選ぶ**ためのもの。",
            "スキーマの書き方は [template-schema.md](template-schema.ja.md)、",
            "汎用ページパターン（骨格・図表の組み方）は",
            "[slide-pattern-catalog.md](slide-pattern-catalog.ja.md) にある。",
            "",
            "各テンプレートの **figures** 行は、そのページが使っている描画部品の `type` 名。",
            "テンプレートは `render_slide_template.py` かデッキ仕様の `$template` で使う。",
            "",
            *REGEN_FENCE["ja"],
            "",
            "| パック | 数 | 何を作るための章か |",
            "|---|---|---|",
        ]
        count_word = "種"
    else:
        header = [
            "*[日本語](slide-template-catalog.ja.md)*",
            "",
            f"# Slide Template Catalog (All {n} Types)",
            "",
            "An image catalog generated by actually rendering each template registered under",
            "`slide-templates/` one page at a time. Its purpose is to **let you look at the output and choose which template to use for a given slide**.",
            "For how to write the schema, see [template-schema.md](template-schema.md);",
            "for generic page patterns (skeletons and figure composition), see",
            "[slide-pattern-catalog.md](slide-pattern-catalog.md).",
            "",
            "Each template's **figures** line lists the `type` names of the drawing components used on that page.",
            "Templates are used via `render_slide_template.py` or the `$template` field in a deck spec.",
            "",
            *REGEN_FENCE["en"],
            "",
            "| Pack | Count | What this section is for |",
            "|---|---|---|",
        ]
        count_word = "types"

    lines = list(header)
    for p in PACK_ORDER:
        s = pack_strings(p, lang, i18n)
        lines.append(f"| [{s['name']}](#{p}) | {len(by_pack.get(p, []))} {count_word} | {s['short']} |")
    lines.append("")

    for p in PACK_ORDER:
        s = pack_strings(p, lang, i18n)
        if lang == "ja":
            head = f"## {s['name']}（`{p}`）"
        else:
            head = f"## {s['name']} (`{p}`)"
        lines += [f'<a id="{p}"></a>', "", head, "", s["intro"], ""]
        for t in by_pack.get(p, []):
            lines += render_template(t, lang, i18n)

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    templates = load_templates()
    i18n = load_i18n()
    DOC_EN.write_text(render("en", templates, i18n), encoding="utf-8")
    DOC_JA.write_text(render("ja", templates, i18n), encoding="utf-8")
    n_img = len(list(IMG_DIR.glob("*.png"))) if IMG_DIR.exists() else 0
    print(f"wrote {DOC_EN.relative_to(ROOT)} + {DOC_JA.relative_to(ROOT)} "
          f"({len(templates)} templates, {n_img} images)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
