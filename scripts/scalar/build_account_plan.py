#!/usr/bin/env python3
"""Assemble a per-customer activity plan deck from the ledger (account.json).

    account.json → slot input per page → slide-templates → deck spec →
    build_deck (first run) / build_deck --into (subsequent runs, URL unchanged)

**The ledger is the source of truth.** The deck is just a rendering of the ledger,
so never edit slides directly. If something needs to change, fix the ledger and
rebuild.

Pages lacking sufficient material are **automatically dropped**. We don't build
thin pages with blanks filled in (what's missing shows up via
`account_ledger.py gaps` and on the action-plan page).

    Validate: .venv/bin/python scripts/scalar/build_account_plan.py examples/account-sample.json --dry-run --strict
    First run: .venv/bin/python scripts/scalar/build_account_plan.py <account.json> --folder <ID of 00_活動計画>
    Update:   .venv/bin/python scripts/scalar/build_account_plan.py <account.json>
            (if the ledger has meta.decks.activityPlan, this automatically behaves like --into)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_DIR / "scripts"))
sys.path.insert(0, str(REPO_DIR / "scripts" / "scalar"))

import _auth  # noqa: E402
import build_deck as bd  # noqa: E402
from slide_templates import load_template as load_slide_template  # noqa: E402
from slide_templates import render_template  # noqa: E402

import account_ledger as ledger_mod  # noqa: E402

DEFAULT_TEMPLATE = REPO_DIR / "templates" / "scalar-2026.json"

# Default composition of the activity plan. The reading order is meaningful:
# where are we now -> what hasn't been achieved -> what's at risk -> what's unknown ->
# why it works -> who to mobilize -> who we've reached -> what to do next
DEFAULT_PAGES: tuple[str, ...] = (
    "account-snapshot",
    "phase-gate",
    "bant-risk",
    "discovery-map",
    "pain-chain",
    "influence-map",
    "buying-committee",
    "activity-timeline",
    "action-plan",
)

# Pages not included by default in the activity plan, but addable via --pages
# (materials for a single visit / single WPS, with a different lifespan than the
# standing activity plan)
OPTIONAL_PAGES: tuple[str, ...] = ("visit-plan", "win-plan", "discovery-gaps")


class BuildError(RuntimeError):
    pass


def cover_slide(ledger: dict) -> dict:
    meta = ledger.get("meta") or {}
    return {
        "layout": "COVER",
        "title": f"{meta.get('customer', '')} 活動計画",
        "subtitle": (f"{meta.get('opportunity', '')} / {ledger_mod._stage_label(ledger)} / "
                     f"{meta.get('forecast', '')} / "
                     f"{meta.get('updatedAt', ledger_mod.today())} 時点 — 社内資料"),
    }


def deck_title(ledger: dict) -> str:
    meta = ledger.get("meta") or {}
    return f"{meta.get('customer', '')} 活動計画（{meta.get('ae', '')}）"


def build_spec(ledger: dict, pages: list[str]) -> tuple[dict, list[str], list[str]]:
    """Return the deck spec and (pages used, pages dropped for lack of material)."""
    slides = [cover_slide(ledger)]
    used: list[str] = []
    skipped: list[str] = []
    for page_id in pages:
        data = ledger_mod.to_slot_data(ledger, page_id)
        if data is None:
            skipped.append(page_id)
            continue
        template, _ = load_slide_template(page_id)
        slides.append(render_template(template, data))
        used.append(page_id)
    return {"title": deck_title(ledger), "slides": slides}, used, skipped


def _validate_spec(template: dict, spec: dict, *, strict: bool) -> list[str]:
    notes = bd.resolve_image_slots(template, spec)
    for note in notes:
        print(f"  {note}")
    problems = bd.validate_spec(template, spec)
    problems += bd.validate_figures(spec, template.get("pageSize", {}), template)
    if problems:
        raise BuildError("仕様に問題があります:\n  - " + "\n  - ".join(problems))
    findings = bd.audit_figures(template, spec)
    if findings:
        print(f"\n図の検査で {len(findings)} 件の指摘:", file=sys.stderr)
        for finding in findings:
            print(f"  - {finding}", file=sys.stderr)
        if strict:
            raise BuildError(
                "検査に指摘があります。**テンプレートではなく台帳のデータを直す**"
                "（ラベルを短くする / 同じ位置に重なった人を離す）")
    return findings


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="台帳から活動計画デッキを組み立てる")
    p.add_argument("ledger", help="account.json のパス")
    p.add_argument("--template", default=str(DEFAULT_TEMPLATE))
    p.add_argument("--pages",
                   help="ページ ID をカンマ区切りで指定（既定は "
                        + ",".join(DEFAULT_PAGES) + "）")
    p.add_argument("--folder", help="初回生成時の出力先 Drive フォルダ（00_活動計画）")
    p.add_argument("--into", help="差し替える既存デッキ。省略時は台帳の "
                                  "meta.decks.activityPlan を使う")
    p.add_argument("--new", action="store_true",
                   help="台帳にデッキ URL があっても新規に作る（URL が変わる）")
    p.add_argument("--out-dir", default=None,
                   help="仕様・アクションプランの出力先（既定は out/account-plan/<顧客名>）")
    p.add_argument("--carry-over", action="store_true",
                   help="未確認の論点を actions に取り込んでから作る（台帳を書き換える）")
    p.add_argument("--dry-run", action="store_true", help="API を呼ばず検証だけ行う")
    p.add_argument("--strict", action="store_true", help="図の検査に指摘があれば失敗する")
    args = p.parse_args(argv)

    ledger = ledger_mod.load(args.ledger)
    problems = ledger_mod.validate(ledger)
    if problems:
        print("台帳に問題があります:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1

    if args.carry_over:
        ledger_mod.carry_over(ledger)
        ledger_mod.save(ledger, args.ledger)
        added = (ledger.get("_carryOver") or {}).get("added", 0)
        print(f"  未確認から {added} 件を actions に取り込みました")

    pages = ([s.strip() for s in args.pages.split(",") if s.strip()]
             if args.pages else list(DEFAULT_PAGES))
    unknown = [pid for pid in pages if pid not in ledger_mod.PAGES]
    if unknown:
        print(f"ERROR: 台帳から作れないページです: {', '.join(unknown)}", file=sys.stderr)
        return 1

    spec, used, skipped = build_spec(ledger, pages)
    if len(used) < 2:
        print("ERROR: 作れるページが 2 枚未満です。台帳に情報を足してください"
              f"（作れたのは {', '.join(used) or 'なし'}）", file=sys.stderr)
        return 1

    meta = ledger.get("meta") or {}
    out_dir = Path(args.out_dir) if args.out_dir else (
        REPO_DIR / "out" / "account-plan" / str(meta.get("customer", "account")))
    out_dir.mkdir(parents=True, exist_ok=True)
    spec_path = out_dir / "deck.json"
    spec_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8")
    actions_path = out_dir / "action-plan.md"
    actions_path.write_text(ledger_mod.action_markdown(ledger), encoding="utf-8")

    print(f"  ページ: {len(spec['slides'])} 枚（表紙 + {', '.join(used)}）")
    if skipped:
        print(f"  材料不足で落としたページ: {', '.join(skipped)}")
    print(f"  仕様: {spec_path}")
    print(f"  アクションプラン: {actions_path}")

    template = bd.load_template(args.template)
    findings = _validate_spec(template, spec, strict=args.strict)

    if args.dry_run:
        print(f"OK: {len(spec['slides'])} 枚の仕様はテンプレートと整合しています")
        if not findings:
            print("図の検査（はみ出し・重なり・文字あふれ）: 問題なし")
        _report_gaps(ledger)
        return 0

    into = args.into or (None if args.new else (meta.get("decks") or {}).get("activityPlan"))
    title = deck_title(ledger)
    if into:
        deck = bd.TemplateDeck.open(
            template, into, title=title,
            layouts=[s["layout"] for s in spec["slides"]])
    else:
        deck = bd.TemplateDeck.create(template, title=title, folder=args.folder)

    warnings = bd.build_from_spec(deck, spec)
    deck.add_page_numbers()
    url = deck.commit()

    ledger.setdefault("meta", {}).setdefault("decks", {})["activityPlan"] = url
    ledger_mod.save(ledger, args.ledger)

    print(f"完了: {len(deck.slide_ids)} 枚。{'差し替え' if into else '新規作成'}")
    for warning in warnings:
        print(f"  - {warning}", file=sys.stderr)
    print(f"活動計画: {url}")
    _report_gaps(ledger)
    return 1 if (warnings and args.strict) else 0


def _report_gaps(ledger: dict) -> None:
    """What matters in the report is not the URL but "what to confirm next"."""
    gaps = ledger_mod.gaps(ledger)
    if not gaps:
        print("\n次に確認すべきこと: なし（10 問すべてに答えられる状態）")
        return
    print(f"\n次に確認すべきこと（{len(gaps)} 件）:")
    for gap in gaps[:6]:
        print(f"  [{gap['id']}] {gap['what']} → {gap['whom']}")
    if len(gaps) > 6:
        print(f"  ほか {len(gaps) - 6} 件は action-plan.md を参照")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (BuildError, ledger_mod.LedgerError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
