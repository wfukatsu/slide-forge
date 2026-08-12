#!/usr/bin/env python3
"""Build references/slide-pattern-catalog.md from examples/slide-pattern-index.json.

Sections and pattern pages are derived from the spec itself, so adding a page to
the spec and re-running this is all it takes to extend the catalog. Slide numbers
are never hard-coded; the slug for a page is matched on a stable title fragment.

    .venv/bin/python scripts/build_deck.py \
        --template templates/scalar-2026.json --spec examples/slide-pattern-index.json
    .venv/bin/python scripts/fetch_thumbnails.py <URL> --out out/patterns --size MEDIUM
    .venv/bin/python scripts/build_pattern_catalog.py --thumbs out/patterns
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "examples/slide-pattern-index.json"
DOC = ROOT / "references/slide-pattern-catalog.md"
IMG_DIR = ROOT / "references/images/slide-patterns"
IMG_REL = "images/slide-patterns"

# 見出しに含まれる安定した語 -> 画像ファイル名。番号ではなく語で対応づけるので、
# ページを差し込んでも既存の画像名は変わらない。
SLUGS = [
    ("骨格A", "skeleton-a-full-width"), ("骨格B", "skeleton-b-figure-left-kicker-right"),
    ("骨格C", "skeleton-c-two-figures"), ("骨格D", "skeleton-d-two-rows"),
    ("骨格E", "skeleton-e-full-width-kicker-band"), ("骨格F", "skeleton-f-text-only"),
    ("エグゼクティブサマリー", "exec-summary"), ("アジェンダ", "agenda"),
    ("ストーリーライン", "storyline"), ("ゴーストデッキ", "ghost-deck"),
    ("推移:", "trend"), ("増減分解", "waterfall"), ("構成比", "composition-pie"),
    ("内訳の推移", "stacked-trend"), ("系列比較", "grouped-comparison"),
    ("KPI", "kpi"), ("図表番号つき", "exhibit-numbered"),
    ("2 案比較", "two-option-compare"), ("多案比較", "multi-option-comparison"),
    ("多案 × 基準", "rating-matrix"), ("ポジショニング", "positioning-map"),
    ("天秤", "balance"), ("仕様比較表", "spec-table"),
    ("ロジックツリー", "logic-tree"), ("階層と絞り込み", "pyramid-funnel"),
    ("積層", "layers"), ("プロセス", "process-flow"), ("中心と放射", "hub-radial"),
    ("4 象限", "quadrant-matrix"), ("重なりと深層", "venn-iceberg"),
    ("スケジュール", "gantt-schedule"), ("ロードマップ", "roadmap"),
    ("体制図", "org-chart"), ("市場規模", "market-sizing"),
    ("リーンキャンバス", "lean-canvas"),
    ("現場の声", "testimonial"), ("事例カード", "case-cards"),
    ("システム構成", "cloud-architecture"), ("コードサンプル", "code-sample"),
    ("ピクトグラム一覧", "pictogram-grid"),
    ("意思決定事項", "decisions"), ("次のステップ", "next-steps"), ("付録:", "appendix-index"),
]

# 短い見出しと、lead_in を持たないページの使いどころ
NAME = {
    "exec-summary": "エグゼクティブサマリー", "agenda": "アジェンダ",
    "storyline": "ストーリーライン", "ghost-deck": "ゴーストデッキ",
    "trend": "推移", "waterfall": "増減分解", "composition-pie": "構成比",
    "stacked-trend": "内訳の推移", "grouped-comparison": "系列比較",
    "kpi": "KPI", "exhibit-numbered": "図表番号つき",
    "two-option-compare": "2 案比較", "multi-option-comparison": "多案比較",
    "rating-matrix": "多案 × 基準", "positioning-map": "ポジショニング",
    "balance": "天秤", "spec-table": "仕様比較表",
    "logic-tree": "ロジックツリー", "pyramid-funnel": "階層と絞り込み",
    "layers": "積層", "process-flow": "プロセス", "hub-radial": "中心と放射",
    "quadrant-matrix": "4 象限", "venn-iceberg": "重なりと深層",
    "gantt-schedule": "スケジュール", "roadmap": "ロードマップ",
    "org-chart": "体制図", "market-sizing": "市場規模", "lean-canvas": "リーンキャンバス",
    "testimonial": "現場の声", "case-cards": "事例カード",
    "cloud-architecture": "システム構成", "code-sample": "コードサンプル",
    "pictogram-grid": "ピクトグラム一覧",
    "decisions": "意思決定事項", "next-steps": "次のステップ", "appendix-index": "付録",
}

USE = {
    "exec-summary": "冒頭専用。SCR（状況 → 課題 → 答え）で、この 1 枚だけ読めば意思決定できる状態にする。論点は 5 個まで。",
    "agenda": "章と枚数を先に示し、読者が全体量を把握できるようにする。行数が多いなら分野で割る。",
    "two-option-compare": "現行と提案を左右に対置する。2 案ならこれで足り、評価マトリクスは要らない。",
    "positioning-map": "2 軸上の位置関係を見せる。4 象限への「分類」を見せたいなら `matrix` を使う。",
    "balance": "2 案のトレードオフを重みとして見せる。定量比較ではなく、判断の傾きを示す図。",
    "spec-table": "数値と条件を正確に並べる。図にすると精度が落ちる内容は表のままにする。",
    "logic-tree": "論点を漏れなく重複なく分解する。深さ 4 超はエラー。MECE かどうかは描く側の責任。",
    "pyramid-funnel": "指標の階層（ピラミッド）と件数の減衰（ファネル）を並べる。",
    "layers": "システムの責務を層で示す。層の順序そのものが主張になる。",
    "process-flow": "工程の流れと段階を示す。`flow` / `steps` / `icon_flow` を粒度で使い分ける。",
    "hub-radial": "1 つの基盤が複数業務を支える構図。放射の本数は 6 本前後まで。",
    "quadrant-matrix": "施策を 2 軸で位置づけて優先順位を作る。競合との位置関係なら `posmap`。",
    "venn-iceberg": "条件の交わり（ベン図）と、表に出ない要因（氷山）を組み合わせる。",
    "gantt-schedule": "工程を時間軸に並べる。段階移行など「止めない」計画の説明に向く。",
    "roadmap": "段階の道のりを示す。`journey` は体験の起伏、`timeline` は時点の列。",
    "org-chart": "責任者と役割を明示する。論点の分解は `mece_tree` で、体制はこちら。",
    "market-sizing": "対象範囲を入れ子で示す（TAM / SAM / SOM）。外側から順に渡す。",
    "lean-canvas": "事業の全体像を 1 枚に収める。項目を埋めきれない段階では使わない。",
    "testimonial": "数値では出ない痛点を引用で示す。定量ページの後ろに置くと効く。",
    "case-cards": "打ち手をカードで並べ、全体像を掴ませる。個々の詳細は付録へ。",
    "cloud-architecture": "クラウド公式アイコンで配置を示す。**ベンダーアイコンの取得が必要**（下記参照）。",
    "pictogram-grid": "業務語彙をアイコンで整理する。用語集の代わりに冒頭へ置ける。",
    "decisions": "何に Yes/No を言えばよいかを 1 枚に。会議の出口をここで定義する。",
    "next-steps": "誰がいつまでに何をするか。主語と期限の無い行は書かない。",
    "appendix-index": "図表一覧で本文からの参照先を示す。`exhibit_frame` の番号と対応させる。",
}

SECTION_INTRO = {
    "骨格 6 種":
        "ページの**組み方**そのもの。どの図を使うかより先に、この 6 種のどれで組むかを決める。\n"
        "標準は骨格B（左図＋右示唆）。座標は [slide-patterns.md](slide-patterns.md) の「骨格の標準座標」にそのまま使える値がある。",
    "構成ページ":
        "デッキ全体の骨組みを作るページ。`storyline` と `ghost` は成果物であると同時に、"
        "清書前に論旨を検証する設計の道具でもある。",
    "定量ページ（推移・構成・増減）":
        "数字で主張するページ。**すべて出典行が要る**（`source_note` は空出典で `ValueError`）。"
        "二重軸・基線ずらしは部品が拒否する。",
    "比較・評価ページ":
        "案を並べて選ばせるページ。2 案なら対置、3 案以上なら `comparison`、"
        "3 案前後 × 基準 4 前後なら評価マトリクス、正確さが要るなら表。",
    "構造・論理ページ": "関係を図にするページ。数値ではなく**構造**が主張になる。",
    "計画・体制ページ": "時間と人を示すページ。いつ・誰が・どの範囲かを扱う。",
    "定性・技術ページ": "数値以外で語るページ。引用・事例・構成図・コードなど。",
    "締め・付録ページ": "意思決定と、その後を扱うページ。本編を薄く、付録を厚くするのが原則。",
}

SHORT = {
    "骨格 6 種": "ページの組み方", "構成ページ": "デッキの骨組み",
    "定量ページ（推移・構成・増減）": "数字で主張する", "比較・評価ページ": "案を並べて選ばせる",
    "構造・論理ページ": "関係を図にする", "計画・体制ページ": "時間と人を示す",
    "定性・技術ページ": "数値以外で語る", "締め・付録ページ": "意思決定とその後",
}


def slug_for(title: str) -> str | None:
    # 長い語から照合する。"推移:" は "内訳の推移:" にも含まれるので、宣言順に
    # 前方一致させると 2 ページが同じスラグに潰れる。
    for frag, slug in sorted(SLUGS, key=lambda p: -len(p[0])):
        if frag in title:
            return slug
    return None


def fig_text(slide: dict, kind: str) -> str:
    for f in slide.get("figures", []):
        if f.get("type") == kind and isinstance(f.get("text"), str):
            return f["text"]
    return ""


def fig_types(slide: dict) -> list[str]:
    seen, out = set(), []
    for f in slide.get("figures", []):
        t = f.get("type")
        if t and t not in seen:
            seen.add(t)
            out.append(t)
    return out


def sections(slides: list) -> list[dict]:
    """SECTION 見出しで区切り、パターンのページだけを拾う。"""
    out, cur = [], None
    for i, s in enumerate(slides):
        lay = s.get("layout")
        if lay == "SECTION":
            cur = {"name": s.get("title", "").split(". ", 1)[-1], "items": []}
            out.append(cur)
            continue
        if cur is None:
            continue
        title = s.get("title", "")
        if lay in ("COVER", "CLOSING", "CONTENT") or title.startswith("パターン索引"):
            continue
        cur["items"].append(i)
    return out


def anchor(i: int, name: str) -> str:
    a = re.sub(r"[（）・\s]", "", name)
    return f"#{i}-{a}"


def main() -> int:
    ap = argparse.ArgumentParser(description="Build the slide pattern catalog")
    ap.add_argument("--thumbs", help="directory of slide-NN.png thumbnails to import")
    args = ap.parse_args()

    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    S = spec["slides"]
    secs = sections(S)

    # 画像の取り込み（--thumbs 指定時のみ）。スライド番号は 1 始まり。
    if args.thumbs:
        src = Path(args.thumbs)
        IMG_DIR.mkdir(parents=True, exist_ok=True)
        n = 0
        for sec in secs:
            for i in sec["items"]:
                slug = slug_for(S[i].get("title") or fig_text(S[i], "governing_message"))
                if slug is None:
                    print(f"  warn: no slug for slides[{i}]: {S[i].get('title')!r}",
                          file=sys.stderr)
                    continue
                png = src / f"slide-{i + 1:02}.png"
                if not png.exists():
                    print(f"  warn: missing {png}", file=sys.stderr)
                    continue
                shutil.copy2(png, IMG_DIR / f"{slug}.png")
                n += 1
        print(f"  imported {n} thumbnails -> {IMG_DIR.relative_to(ROOT)}")

    L: list[str] = []
    w = L.append
    total = sum(len(s["items"]) for s in secs)

    w(f"# スライドパターン カタログ（実物 {total} 種）")
    w("")
    w("`examples/slide-pattern-index.json` を実際に生成して 1 枚ずつ書き出した画像カタログ。")
    w("**どのページが作れるかを見て選ぶ**ためのもので、組み方の規則そのものは")
    w("[slide-patterns.md](slide-patterns.md)、図表部品の詳細は")
    w("[patterns.md](patterns.md) / [charts.md](charts.md) / [diagrams.md](diagrams.md) にある。")
    w("")
    w("各パターンの **figures** 行が、デッキ仕様（JSON）の `figures` にそのまま書く `type` 名。")
    w("")
    w("> 画像はリポジトリにコミットしてある。パターンを追加・変更したときは、")
    w("> 下のコマンドで作り直して画像ごとコミットし直すこと。")
    w("")
    w("```bash")
    w("# このカタログを作る（パターンを足したときも同じ手順）")
    w(".venv/bin/python scripts/build_deck.py \\")
    w("    --template templates/scalar-2026.json --spec examples/slide-pattern-index.json")
    w(".venv/bin/python scripts/fetch_thumbnails.py <生成された URL> --out out/patterns --size MEDIUM")
    w(".venv/bin/python scripts/build_pattern_catalog.py --thumbs out/patterns")
    w("```")
    w("")
    w("| 分類 | 数 | 何を選ぶための章か |")
    w("|---|---|---|")
    for i, sec in enumerate(secs, 1):
        w(f"| [{i}. {sec['name']}]({anchor(i, sec['name'])}) | {len(sec['items'])} "
          f"| {SHORT.get(sec['name'], '')} |")
    w("")
    w("> 「システム構成」だけはクラウドベンダーの公式アイコンを描くため、")
    w("> 事前に `.venv/bin/python scripts/fetch_cloud_icons.py` が必要。")
    w("> アイコンは再配布が許されないためリポジトリには含めていない")
    w("> （[assets/cloud-icons/README.md](../assets/cloud-icons/README.md)）。")
    w("")

    for i, sec in enumerate(secs, 1):
        w(f"## {i}. {sec['name']}")
        w("")
        w(SECTION_INTRO.get(sec["name"], ""))
        w("")
        for idx in sec["items"]:
            s = S[idx]
            title = s.get("title") or fig_text(s, "governing_message")
            slug = slug_for(title)
            if slug is None:
                continue
            if slug in NAME:
                head = NAME[slug]
                sample = title.split(":", 1)[1].strip() if ":" in title else ""
            else:
                head = (title.split("｜")[0].strip() + "｜"
                        + title.split("｜")[1].split("—")[0].strip()
                        if "｜" in title else title)
                sample = ""
            w(f"### {head}")
            w("")
            w(f"![{head}]({IMG_REL}/{slug}.png)")
            w("")
            desc = fig_text(s, "lead_in") or USE.get(slug, "")
            if desc:
                w(desc)
                w("")
            if sample and sample[:12] not in desc:
                w(f"見出しの例: 「{sample}」")
                w("")
            w("**figures**: " + " / ".join(f"`{t}`" for t in fig_types(s)))
            w("")

    w("---")
    w("")
    w("画像は `examples/slide-pattern-index.json` の生成結果"
      "（`scalar-2026` テンプレート、MEDIUM サムネイル）。")
    w("パターンを足すときは、そのスペックにページを 1 枚足してから上のコマンドで作り直す。")
    w("")

    DOC.write_text("\n".join(L), encoding="utf-8")
    print(f"  wrote {DOC.relative_to(ROOT)} ({total} patterns, {len(secs)} sections)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
