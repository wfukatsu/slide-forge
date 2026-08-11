#!/usr/bin/env python3
"""台帳（account.json）を Markdown に丸ごと書き出す。

デッキは 11 枚しか載らないが、台帳には 100 件を超えるファクトが入っている。
その全部を人が読める形にするための出力。**台帳が正本**なので、この Markdown は
毎回作り直す（手で直さない）。

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
    w(f"| フォーキャスト | {meta.get('forecast','')} |")
    w(f"| 想定 TCV | {meta.get('amount') or '未確定'} |")
    w(f"| 決定予定日 | {meta.get('closeDate') or '未確定'} |")
    for k, v in (meta.get("decks") or {}).items():
        w(f"| デッキ: {k} | {v} |")
    w("")

    w("## 2. ゲート（フェーズ移行条件）\n")
    w("| ゲート | 状態 | 顧客側の証拠 | 担当 |")
    w("|---|---|---|---|")
    for gid, item in (ledger.get("gates") or {}).items():
        label = L.GATE_SHORT.get(gid, gid)
        w(f"| `{gid}` {label} | **{item.get('status','')}** | "
          f"{item.get('evidence') or '未取得'} | {item.get('owner','')} |")
    w("")

    w("## 3. BANT\n")
    w("| 項目 | 判定 | 根拠 |")
    w("|---|---|---|")
    for key, label in L.BANT_KEYS:
        it = (ledger.get("bant") or {}).get(key) or {}
        w(f"| {label} | **{it.get('level','')}** | {it.get('note') or '未確認'} |")
    w("")

    w("## 4. ディスカバリー（MEDDPICC ＋ なぜ今か）\n")
    w("| 項目 | 状態 | 分かっていること | 出所 |")
    w("|---|---|---|---|")
    for key, label in L.DISCOVERY_KEYS:
        it = (ledger.get("discovery") or {}).get(key) or {}
        w(f"| {label} | **{it.get('status','')}** | {it.get('note') or '—'} | "
          f"{it.get('evidence') or '—'} |")
    w("")

    people = [p for p in (ledger.get("people") or []) if isinstance(p, dict)]
    w(f"## 5. 購買委員会（{len(people)} 名）\n")
    w("| 氏名 | 所属・肩書 | 役割 | 影響力 | 賛否 | 接触 | 根拠 |")
    w("|---|---|---|---|---|---|---|")
    for p in people:
        w(f"| {p.get('name','')} | {p.get('fullTitle') or p.get('title','')} | "
          f"{p.get('role','')} | {L._band(p.get('influence'))} | "
          f"{L._stance(p.get('stance'))} | {p.get('met') or '未接触'} | "
          f"{p.get('evidence','')} |")
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
            w("| " + " | ".join(str(c) for c in row) + " |")
        w("")

    w("## 7. リスクと打ち手\n")
    w("| リスク | コントロールする次の行動 |")
    w("|---|---|")
    for r in ledger.get("risks") or []:
        w(f"| {r.get('what','')} | {r.get('control') or '**未定**'} |")
    w("")

    w("## 8. パートナー・関係ベンダー\n")
    w("| 名前 | 役割 | 位置づけ |")
    w("|---|---|---|")
    for p in ledger.get("partners") or []:
        w(f"| {p.get('name','')} | {p.get('role','')} | {p.get('why','')} |")
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
        w(f"| {i} | {a.get('what','')} | {a.get('why','')} | {a.get('whom','')} | "
          f"{a.get('due') or '**未定**'} | {a.get('doneWhen','')} |")
    w("")

    visits = sorted([v for v in (ledger.get("visits") or []) if isinstance(v, dict)],
                    key=lambda v: v.get("date", ""))
    w(f"## 11. 面談履歴（{len(visits)} 件）\n")
    w("| 日付 | 状態 | 会った相手 | 当社 | 目的 | 得たこと | 次の一手 |")
    w("|---|---|---|---|---|---|---|")
    for v in visits:
        w(f"| {v.get('date','')} | {v.get('status','')} | {v.get('attendees','')} | "
          f"{v.get('ours','')} | {v.get('purpose','')} | {v.get('heard') or '—'} | "
          f"{v.get('next') or '—'} |")
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
            w(f"| {f.get('date','')} | {f.get('who','')} | {f.get('text','')} |")
        w("")

    gaps = L.gaps(ledger)
    w(f"## 13. 10 問チェックポイントの空白（{len(gaps)} 件）\n")
    w("| # | 問い | やること | 相手 | 完了条件 |")
    w("|---|---|---|---|---|")
    for g in gaps:
        w(f"| {g['id']} | {g['question']} | {g['what']} | {g['whom']} | {g['doneWhen']} |")
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
