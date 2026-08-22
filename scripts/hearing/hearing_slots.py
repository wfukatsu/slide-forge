#!/usr/bin/env python3
"""Turn the gaps in a hearing sheet into slide-template data.

    .venv/bin/python scripts/hearing/hearing_slots.py <hearing.json> hearing-agenda \
        --out out/hearing/agenda.json [--section 4] [--limit 5]

Mirrors `scripts/scalar/account_ledger.py`'s `to_slot_data`: one builder per
page, and **a page with nothing to say returns nothing** rather than being
built with blanks. The output feeds `scripts/render_slide_template.py`.

Every page here is customer-facing, so the builders read only what survives
the customer filter — the internal sections and the source/confidence columns
never reach a slide.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
sys.path.insert(0, SCRIPTS)
sys.path.insert(0, HERE)

import model as M  # noqa: E402
import hearing_sheet as H  # noqa: E402

SOURCE_NOTE = "ヒアリングシートの未確認項目より（{updated}時点）"


class NoMaterial(Exception):
    """Not enough in the sheet to build this page honestly."""


def _customer_gaps(doc: dict, section: str | None) -> list[dict]:
    """Gaps that may be shown to the customer."""
    kept, _ = M.customer_blocks(doc)
    safe = {q["id"] for b in kept if b["kind"] == "questions" for q in b["questions"]}
    return [g for g in H.gaps(doc, stage=section) if g["id"] in safe]


def _source(doc: dict) -> str:
    updated = (doc.get("meta") or {}).get("updated") or ""
    return SOURCE_NOTE.format(updated=updated + " " if updated else "")


def _ordered(gaps: list[dict]) -> list[dict]:
    """Ticked questions first — that is the AE saying "ask this one"."""
    return sorted(gaps, key=lambda g: (not g["ask"], g["section"], g["id"]))


def page_hearing_agenda(doc: dict, *, section: str | None = None,
                        limit: int = 5, **_: object) -> dict | None:
    rows = _ordered(_customer_gaps(doc, section))[:limit]
    if len(rows) < 3:
        raise NoMaterial("未確認が 3 件未満。議題にするほどの空きが無い")
    return {
        "title": "本日うかがいたいこと",
        "lead": "こちらで埋められていない論点です。分かる範囲で結構です。",
        "items": [[r["text"][:40], (r["followup"].get("why") or "提案の前提になるため")[:40]]
                  for r in rows],
        "ask": "分からない項目は、どなたにうかがえばよいかだけ教えてください。",
        "source": _source(doc),
    }


def page_hypothesis_check(doc: dict, *, section: str | None = None,
                          limit: int = 3, **_: object) -> dict | None:
    rows = [g for g in _customer_gaps(doc, section) if g["confidence"] == "推定"][:limit]
    if len(rows) < 2:
        raise NoMaterial(
            "確度が『推定』の行が 2 件未満。確認してもらう理解がまだ無い"
            "（推測で埋めて作らないこと）")
    return {
        "title": "こちらの理解に、違っている点はありませんか",
        "lead": "これまでのお話からこちらが理解した内容です。違っていれば訂正してください。",
        "items": [[r["sectionTitle"][:16], (r["answer"] or r["text"])[:68]] for r in rows],
        "ask": "実感と違うものはどれですか。違う場合、実際はどうなっていますか。",
        "source": _source(doc),
    }


def page_fill_in_sheet(doc: dict, *, section: str | None = None,
                       limit: int = 6, **_: object) -> dict | None:
    rows = _ordered(_customer_gaps(doc, section))[:limit]
    if len(rows) < 3:
        raise NoMaterial("未確認が 3 件未満。記入欄にするほどの空きが無い")
    return {
        "title": "この場でご記入いただきたい項目",
        "lead": "分かる範囲で結構です。分からない欄は空のままで構いません。",
        "items": [[r["text"][:44], ""] for r in rows],
        "source": _source(doc),
    }


def page_collect_cta(doc: dict, *, where: str | None = None, **_: object) -> dict | None:
    renders = (doc.get("meta") or {}).get("renders") or {}
    target = where or renders.get("gsheet")
    if not target:
        raise NoMaterial(
            "回答先が無い。先に render --format gsheet --audience customer で"
            "顧客配布版を作るか、--where で回答先を渡すこと")
    return {
        "title": "ご記入いただいた内容を、次回の構成案と概算費用の前提にします",
        "lead": "いただいた回答をもとに、構成案をお持ちします。",
        "steps": ["シートにご記入", "こちらで構成案を作成", "次回に構成をご提示"],
        "where": target[:120],
        "source": _source(doc),
    }


def page_collect_qr(doc: dict, *, where: str | None = None,
                    qr_path: str | None = None, **_: object) -> dict | None:
    import qr as QR

    renders = (doc.get("meta") or {}).get("renders") or {}
    url = where or renders.get("gsheet")
    if not url:
        raise NoMaterial("回答先の URL が無い。--where で渡すこと")
    path, real = QR.build(url, qr_path or os.path.join("out", "hearing", "qr.png"))
    if not real:
        print("qrcode が入っていないため QR はプレースホルダ。"
              '実物にするには pip install "qrcode[pil]"', file=sys.stderr)
    return {
        "title": "アンケートへのご協力をお願いします",
        "lead": "いただいた回答は、次回お持ちする資料の前提にします。",
        "qr": path,
        # The URL is always spelled out: there is always a seat where the QR will not scan.
        "where": f"{url} （QR が読めない場合はこちらから）"[:120],
        "source": _source(doc),
    }


PAGES = {
    "hearing-agenda": page_hearing_agenda,
    "hypothesis-check": page_hypothesis_check,
    "fill-in-sheet": page_fill_in_sheet,
    "collect-cta": page_collect_cta,
    "collect-qr": page_collect_qr,
    # event-poll is built from a nurture segment's situations, not from a
    # customer's sheet — templates/nurture/segment-sheet.ja.md §1 is its input.
}


def to_slot_data(doc: dict, page_id: str, **kwargs) -> dict | None:
    builder = PAGES.get(page_id)
    if builder is None:
        raise M.HearingError(
            f"ヒアリングシートから作れないページです: {page_id}"
            f"（作れるのは {', '.join(sorted(PAGES))}）")
    return builder(doc, **kwargs)


def main() -> int:
    p = argparse.ArgumentParser(description="ヒアリングシートからスライドの slot データを作る")
    p.add_argument("json")
    p.add_argument("page", choices=sorted(PAGES))
    p.add_argument("--out", required=True)
    p.add_argument("--section", help="節番号で絞る（例: 4）")
    p.add_argument("--limit", type=int)
    p.add_argument("--where", help="回答先（URL や依頼文）")
    p.add_argument("--qr-path", help="QR PNG の出力先")
    args = p.parse_args()

    doc = H.load(args.json)
    kwargs: dict = {k: v for k, v in
                    (("section", args.section), ("where", args.where),
                     ("qr_path", args.qr_path), ("limit", args.limit))
                    if v is not None}
    try:
        data = to_slot_data(doc, args.page, **kwargs)
    except NoMaterial as exc:
        print(f"作らなかった: {exc}", file=sys.stderr)
        return 2
    H.save(data, args.out)
    print(f"出力: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
