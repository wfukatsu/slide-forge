#!/usr/bin/env python3
"""Build references/slide-template-catalog.md from slide-templates/ metadata.

パック別カタログ仕様の生成（build_slide_template_catalog.py）でデッキを作り、
fetch_thumbnails.py で PNG を取り込んだあと、このスクリプトがテンプレートの
メタデータ（description / answers / guardrails / figures）から図入りの
Markdown カタログを書き出す。テンプレートを追加したら再実行するだけでよい。

    .venv/bin/python scripts/build_slide_template_catalog.py --pack <pack> --out out/template-catalog/<pack>.json
    （全パックを 1 つのデッキに結合して build_deck.py で生成）
    .venv/bin/python scripts/fetch_thumbnails.py <URL> --out out/template-catalog/thumbs --size MEDIUM
    （thumbs を references/images/slide-templates/<id>.png に取り込み）
    .venv/bin/python scripts/build_template_catalog_doc.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "slide-templates/manifest.json"
DOC = ROOT / "references/slide-template-catalog.md"
IMG_DIR = ROOT / "references/images/slide-templates"
IMG_REL = "images/slide-templates"

PACK_ORDER = ["marketing-analysis", "b2b-sales", "scalar-ae", "planning", "analysis"]

PACK_INTRO = {
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
    "descriptive": "記述（事実の整理）",
    "diagnostic": "診断（要因・構造の特定）",
    "causal": "因果（原因の主張）",
    "strategic": "戦略（評価と方向づけ）",
}


def load_templates() -> list[dict]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    out = []
    for entry in manifest["templates"]:
        t = json.loads((ROOT / "slide-templates" / entry["path"]).read_text(encoding="utf-8"))
        t["_status"] = entry.get("status", "")
        out.append(t)
    return out


def render_template(t: dict) -> list[str]:
    lines = [f"### {t['displayName']}（`{t['id']}`）", ""]
    img = IMG_DIR / f"{t['id']}.png"
    if img.exists():
        lines += [f"![{t['displayName']}]({IMG_REL}/{t['id']}.png)", ""]
    lines += [t.get("description", ""), ""]
    answers = t.get("answers") or []
    if answers:
        lines += ["**答える問い**: " + " / ".join(answers), ""]
    figs = [f.get("type") for f in t.get("slide", {}).get("figures", []) if f.get("type")]
    meta = [f"**figures**: {', '.join(f'`{f}`' for f in dict.fromkeys(figs))}"]
    level = INFERENCE_LABEL.get(t.get("inferenceLevel", ""), t.get("inferenceLevel", ""))
    if level:
        meta.append(f"**推論レベル**: {level}")
    if t.get("_status"):
        meta.append(f"**status**: {t['_status']}")
    lines += ["  \n".join(meta), ""]
    guardrails = t.get("guardrails") or []
    if guardrails:
        lines += ["使うときの決まり:", ""]
        lines += [f"- {g}" for g in guardrails]
        lines += [""]
    return lines


def main() -> int:
    templates = load_templates()
    by_pack: dict[str, list[dict]] = {}
    for t in templates:
        by_pack.setdefault(t["pack"], []).append(t)

    lines = [
        f"# スライドテンプレート カタログ（全 {len(templates)} 種）",
        "",
        "`slide-templates/` に登録されたテンプレートを実際に 1 枚ずつ生成して",
        "書き出した画像カタログ。**どのテンプレートで 1 枚を作るかを見て選ぶ**ためのもの。",
        "スキーマの書き方は [template-schema.md](template-schema.md)、",
        "汎用ページパターン（骨格・図表の組み方）は",
        "[slide-pattern-catalog.md](slide-pattern-catalog.md) にある。",
        "",
        "各テンプレートの **figures** 行は、そのページが使っている描画部品の `type` 名。",
        "テンプレートは `render_slide_template.py` かデッキ仕様の `$template` で使う。",
        "",
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
        "",
        "| パック | 数 | 何を作るための章か |",
        "|---|---|---|",
    ]
    lines += [
        f"| [{PACK_INTRO[p][0]}](#{p}) | {len(by_pack.get(p, []))} 種 | {PACK_INTRO[p][1].split('。')[0]} |"
        for p in PACK_ORDER
    ]
    lines.append("")

    for pack in PACK_ORDER:
        name, intro = PACK_INTRO[pack]
        lines += [f'<a id="{pack}"></a>', "", f"## {name}（`{pack}`）", "", intro, ""]
        for t in by_pack.get(pack, []):
            lines += render_template(t)

    DOC.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    n_img = len(list(IMG_DIR.glob("*.png"))) if IMG_DIR.exists() else 0
    print(f"wrote {DOC.relative_to(ROOT)} ({len(templates)} templates, {n_img} images)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
