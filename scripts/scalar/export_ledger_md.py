#!/usr/bin/env python3
"""Dump the entire ledger (account.json) to Markdown.

A deck can only hold 11 slides, but the ledger contains over 100 facts. This
output makes all of it readable by a human. Since **the ledger is the source of
truth**, this Markdown is regenerated every time (never hand-edited).

    .venv/bin/python scripts/scalar/export_ledger_md.py <account.json> --out <path.md>
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import account_ledger as L  # noqa: E402

KIND_LABEL = {"said": "said — 顧客がそう言った",
              "observed": "observed — 文書・記録で確認した",
              "assumed": "assumed — こちらの推測"}

# `|` and newlines in table cells are escaped via the ledger's shared helper (to avoid breaking the table)
_cell = L.md_cell


def render(ledger: dict) -> str:
    meta = ledger.get("meta") or {}
    o: list[str] = []
    w = o.append
    w(f"# {meta.get('customer','')} 商談台帳（全文）\n")
    w(f"商談: {meta.get('opportunity','')} / AE: {meta.get('ae','')} / "
      f"{meta.get('updatedAt','')} 時点\n")
    w("> **台帳（`account.json`）から自動生成している。手で直さないこと。**")
    w("> 直すときは台帳を直して、このファイルを作り直す。\n")
    w("> **社内資料。** 個人の影響力・賛否・社内政治の判断が入っている。顧客にもパートナーにも渡さない。\n")

    stage = meta.get("stage")
    w("## 1. 現在地\n")
    w("| 項目 | 値 |")
    w("|---|---|")
    w(f"| ステージ | {stage} — {L.STAGES.get(stage,'不明')} |")
    w(f"| フォーキャスト | {_cell(meta.get('forecast',''))} |")
    w(f"| 想定 TCV | {_cell(meta.get('amount') or '未確定')} |")
    w(f"| 決定予定日 | {_cell(meta.get('closeDate') or '未確定')} |")
    for k, v in (meta.get("decks") or {}).items():
        w(f"| デッキ: {_cell(k)} | {_cell(v)} |")
    w("")

    w("## 2. ゲート（フェーズ移行条件）\n")
    w("| ゲート | 状態 | 顧客側の証拠 | 担当 |")
    w("|---|---|---|---|")
    for gid, item in (ledger.get("gates") or {}).items():
        label = L.GATE_SHORT.get(gid, gid)
        w(f"| `{gid}` {label} | **{_cell(item.get('status',''))}** | "
          f"{_cell(item.get('evidence') or '未取得')} | {_cell(item.get('owner',''))} |")
    w("")

    w("## 3. BANT\n")
    w("| 項目 | 判定 | 根拠 |")
    w("|---|---|---|")
    for key, label in L.BANT_KEYS:
        it = (ledger.get("bant") or {}).get(key) or {}
        w(f"| {label} | **{_cell(it.get('level',''))}** | {_cell(it.get('note') or '未確認')} |")
    w("")

    w("## 4. ディスカバリー（MEDDPICC ＋ なぜ今か）\n")
    w("| 項目 | 状態 | 分かっていること | 出所 |")
    w("|---|---|---|---|")
    for key, label in L.DISCOVERY_KEYS:
        it = (ledger.get("discovery") or {}).get(key) or {}
        w(f"| {label} | **{_cell(it.get('status',''))}** | {_cell(it.get('note') or '—')} | "
          f"{_cell(it.get('evidence') or '—')} |")
    w("")

    people = [p for p in (ledger.get("people") or []) if isinstance(p, dict)]
    w(f"## 5. 購買委員会（{len(people)} 名）\n")
    w("| 氏名 | 所属・肩書 | 役割 | 影響力 | 賛否 | 接触 | 根拠 |")
    w("|---|---|---|---|---|---|---|")
    for p in people:
        w(f"| {_cell(p.get('name',''))} | {_cell(p.get('fullTitle') or p.get('title',''))} | "
          f"{_cell(p.get('role',''))} | {L._band(p.get('influence'))} | "
          f"{L._stance(p.get('stance'))} | {_cell(p.get('met') or '未接触')} | "
          f"{_cell(p.get('evidence',''))} |")
    w("")
    w("> 全接点（60 名超）は `関与者一覧.md` にある。ここは勘定系の意思決定に直接効く分だけ。\n")

    pain = ledger.get("painChain") or {}
    if pain.get("chain"):
        w("## 6. 課題の連鎖\n")
        w(f"**{pain.get('title','')}**\n")
        w(" → ".join(pain["chain"]) + "\n")
        w("| 段 | 起きていること | 裏付け |")
        w("|---|---|---|")
        for row in pain.get("evidence") or []:
            w("| " + " | ".join(_cell(c) for c in row) + " |")
        w("")

    w("## 7. リスクと打ち手\n")
    w("| リスク | コントロールする次の行動 |")
    w("|---|---|")
    for r in ledger.get("risks") or []:
        w(f"| {_cell(r.get('what',''))} | {_cell(r.get('control') or '**未定**')} |")
    w("")

    w("## 8. パートナー・関係ベンダー\n")
    w("| 名前 | 役割 | 位置づけ |")
    w("|---|---|---|")
    for p in ledger.get("partners") or []:
        w(f"| {_cell(p.get('name',''))} | {_cell(p.get('role',''))} | {_cell(p.get('why',''))} |")
    w("")

    win = ledger.get("winPlan") or {}
    if any(win.get(k) for k in ("situation", "complication", "resolution")):
        w("## 9. 勝ち筋\n")
        if win.get("title"):
            w(f"**{win['title']}**\n")
        w(f"- **顧客ゴール**: {win.get('situation','')}")
        w(f"- **障害**: {win.get('complication','')}")
        w(f"- **勝ち筋**: {win.get('resolution','')}\n")

    live = [a for a in (ledger.get("actions") or [])
            if isinstance(a, dict) and a.get("status") in L.LIVE_ACTIONS]
    w(f"## 10. アクション（未完了 {len(live)} 件）\n")
    w("**期限は AE が顧客に対してする約束。空欄は「まだ約束していない」という意味。**\n")
    w("| # | やること | なぜ必要か | 相手 | 期限 | 完了条件 |")
    w("|---|---|---|---|---|---|")
    for i, a in enumerate(live, 1):
        w(f"| {i} | {_cell(a.get('what',''))} | {_cell(a.get('why',''))} | "
          f"{_cell(a.get('whom',''))} | {_cell(a.get('due') or '**未定**')} | "
          f"{_cell(a.get('doneWhen',''))} |")
    w("")

    visits = sorted([v for v in (ledger.get("visits") or []) if isinstance(v, dict)],
                    key=lambda v: v.get("date", ""))
    w(f"## 11. 面談履歴（{len(visits)} 件）\n")
    w("| 日付 | 状態 | 会った相手 | 当社 | 目的 | 得たこと | 次の一手 |")
    w("|---|---|---|---|---|---|---|")
    for v in visits:
        w(f"| {_cell(v.get('date',''))} | {_cell(v.get('status',''))} | "
          f"{_cell(v.get('attendees',''))} | {_cell(v.get('ours',''))} | "
          f"{_cell(v.get('purpose',''))} | {_cell(v.get('heard') or '—')} | "
          f"{_cell(v.get('next') or '—')} |")
    w("")

    facts = [f for f in (ledger.get("facts") or []) if isinstance(f, dict)]
    w(f"## 12. ファクト全件（{len(facts)} 件）\n")
    w("**`said` / `observed` / `assumed` を混ぜない。** これがこの台帳の背骨。\n")
    for kind in L.FACT_KINDS:
        rows = sorted([f for f in facts if f.get("kind") == kind],
                      key=lambda f: f.get("date", ""))
        w(f"### {KIND_LABEL[kind]}（{len(rows)} 件）\n")
        w("| 日付 | 誰が / どこで | 内容 |")
        w("|---|---|---|")
        for f in rows:
            w(f"| {_cell(f.get('date',''))} | {_cell(f.get('who',''))} | {_cell(f.get('text',''))} |")
        w("")

    gaps = L.gaps(ledger)
    w(f"## 13. 10 問チェックポイントの空白（{len(gaps)} 件）\n")
    w("| # | 問い | やること | 相手 | 完了条件 |")
    w("|---|---|---|---|---|")
    for g in gaps:
        w(f"| {g['id']} | {_cell(g['question'])} | {_cell(g['what'])} | "
          f"{_cell(g['whom'])} | {_cell(g['doneWhen'])} |")
    w("")
    return "\n".join(o) + "\n"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="台帳を Markdown に書き出す")
    p.add_argument("ledger")
    p.add_argument("--out", required=True)
    args = p.parse_args(argv)
    ledger = L.load(args.ledger)
    problems = L.validate(ledger)
    if problems:
        print("台帳に問題があります:", file=sys.stderr)
        for x in problems:
            print(f"  - {x}", file=sys.stderr)
        return 1
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(ledger), encoding="utf-8")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
