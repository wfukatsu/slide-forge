#!/usr/bin/env python3
"""顧客ごとの営業活動台帳（account.json）の読み書き・検証・派生。

台帳は **資料生成のための作業台帳**であり、CRM を置き換えるものではない
（references/scalar/sales-playbook.md §8）。ステージ・金額・予定日の正本は CRM。

    accounts/<AE 名>/<顧客名>/account.json

このモジュールが持つのは 4 つの責務だけ:

1. スキーマの検証 — 「確認済みなのに証拠が無い」のような矛盾を弾く
2. `gaps()` — プレイブック §7 の 10 問に答えられない箇所を洗い出す
3. `to_slot_data()` — 各スライドテンプレートの入力 JSON を台帳から作る
4. `action_markdown()` — CRM の Next Action に貼れる形で書き出す

**答えを埋めない。** 未確認は未確認のまま `actions` に送るのがこの台帳の仕事で、
推測を confirmed に格上げすることではない。

    検証:   .venv/bin/python scripts/scalar/account_ledger.py validate <account.json>
    未確認: .venv/bin/python scripts/scalar/account_ledger.py gaps <account.json>
    行動:   .venv/bin/python scripts/scalar/account_ledger.py actions <account.json> --markdown
    雛形:   .venv/bin/python scripts/scalar/account_ledger.py init --ae "<AE 名>" --customer "<顧客名>"
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

REPO_DIR = Path(__file__).resolve().parents[2]
ACCOUNTS_DIR = REPO_DIR / "accounts"

SCHEMA_VERSION = 1


class LedgerError(ValueError):
    """台帳が壊れている（読めない・スキーマ違反）。"""


# --------------------------------------------------------------------- 語彙
# すべて references/scalar/sales-playbook.md に対応する。ここを増やすときは
# プレイブックも直すこと（片方だけ増やすと資料と判断がずれる）。

STAGES: dict[int, str] = {
    0: "Territory / Account Planning",
    1: "Assessment & Qualification",
    2: "Discovery",
    3: "Solution Development",
    4: "Solution Presentation",
    5: "Resolution",
    6: "Delivery / Renewal / Expansion",
}

# ステージ -> [(ゲート ID, 移行条件)]。プレイブック §2 の表と 1 対 1。
GATES: dict[int, list[tuple[str, str]]] = {
    0: [
        ("g0.icp-fit", "対象アカウントが ICP に適合している"),
        ("g0.hypothesis-defined", "想定課題・対象者・購買トリガー・接点獲得方法が定義されている"),
        ("g0.capacity-assigned", "投資する営業工数と担当が決まっている"),
    ],
    1: [
        ("g1.problem-recognized", "Scalar で解決可能な課題を顧客自身が認識している"),
        ("g1.owner-reached", "課題の所有部門・責任者につながっている、または紹介が合意されている"),
        ("g1.linked-to-exec", "経営・部門課題との関係が確認できている"),
        ("g1.timeframe-6q", "原則 6 四半期以内に意思決定可能である"),
        ("g1.next-discovery-agreed", "次回のディスカバリー対象者とテーマが合意されている"),
    ],
    2: [
        ("g2.goal-agreed", "顧客が達成したい業務ゴールと課題を合意している"),
        ("g2.requirements-agreed", "課題を解決するためのシステム課題・要件を合意している"),
        ("g2.three-maps", "ディスカバリー / システム / インフルーエンスの 3 マップが作成・検証されている"),
        ("g2.buying-process", "提案対象・対象者・パートナー・既存環境・購買プロセスが明確である"),
        ("g2.wps-done", "WPS を実施し、SA を含む提案チームが組成されている"),
    ],
    3: [
        ("g3.demo-understood", "デモ / プロトタイプで、できること・できないことを顧客が理解している"),
        ("g3.poc-agreed", "未評価事項に PoC 実施が合意されている"),
        ("g3.value-quotable", "To-Be・要件・概算構成・価値・差別化・概算金額が説明可能である"),
        ("g3.deal-desk", "Deal Desk で提案リスクがレビューされている"),
    ],
    4: [
        ("g4.product-selected", "Scalar 製品が選定されている"),
        ("g4.budget-agreed", "概算予算と購入金額が合意され、予算確保が確認できている"),
        ("g4.partner-decided", "導入パートナーが決定している"),
        ("g4.closing-reviewed", "契約までの課題とタスクを Deal Desk でレビューしている"),
    ],
    5: [
        ("g5.terms-signed", "エンドユーザーと Term & Conditions を締結している"),
        ("g5.channel-open", "パートナー商流がある場合、代理店契約と注文経路が開通している"),
        ("g5.po-received", "注文書を受領している"),
        ("g5.services-contracted", "必要なサービス契約を締結している"),
        ("g5.support-ready", "利用開始までにサポート窓口を開設できる"),
    ],
    6: [
        ("h6.value-realized", "提案時の KPI に対する実績を確認している"),
        ("h6.utilization", "未利用のライセンス・機能がない"),
        ("h6.renewal-risk", "更新日と更新リスクを把握している"),
        ("h6.expansion", "追加ユースケースの候補がある"),
    ],
}

ALL_GATE_IDS = {gid for items in GATES.values() for gid, _ in items}
GATE_LABEL = {gid: label for items in GATES.values() for gid, label in items}

# 表の 1 列に収まる短い呼び名。移行条件の全文は GATE_LABEL 側にある。
GATE_SHORT: dict[str, str] = {
    "g0.icp-fit": "ICP 適合",
    "g0.hypothesis-defined": "仮説の定義",
    "g0.capacity-assigned": "工数と担当",
    "g1.problem-recognized": "顧客の課題認識",
    "g1.owner-reached": "課題所有者に接触",
    "g1.linked-to-exec": "経営課題との関係",
    "g1.timeframe-6q": "6 四半期以内",
    "g1.next-discovery-agreed": "次回テーマ合意",
    "g2.goal-agreed": "業務ゴール合意",
    "g2.requirements-agreed": "要件合意",
    "g2.three-maps": "3 マップ作成",
    "g2.buying-process": "購買プロセス把握",
    "g2.wps-done": "WPS 実施",
    "g3.demo-understood": "デモで実現性理解",
    "g3.poc-agreed": "PoC 合意",
    "g3.value-quotable": "価値と概算金額",
    "g3.deal-desk": "Deal Desk 承認",
    "g4.product-selected": "製品選定",
    "g4.budget-agreed": "予算合意",
    "g4.partner-decided": "パートナー決定",
    "g4.closing-reviewed": "クロージング審査",
    "g5.terms-signed": "T&C 締結",
    "g5.channel-open": "商流開通",
    "g5.po-received": "注文書受領",
    "g5.services-contracted": "サービス契約",
    "g5.support-ready": "サポート開設",
    "h6.value-realized": "価値実現の確認",
    "h6.utilization": "利用状況",
    "h6.renewal-risk": "更新リスク",
    "h6.expansion": "拡張候補",
}

FORECASTS = ("Pipeline", "Best", "Commit", "Closed")
FACT_KINDS = ("said", "observed", "assumed")
GATE_STATUS = ("met", "partial", "unmet")
DISCOVERY_STATUS = ("confirmed", "wip", "missing")
BANT_LEVELS = ("ok", "risk", "unknown")
# proposed = 未確認から自動で起こした候補。期限を入れるまで open にしない
# （期限は AE が顧客に対してする約束なので、こちらが決めない）
ACTION_STATUS = ("proposed", "open", "done", "dropped")
LIVE_ACTIONS = ("proposed", "open")
BUYING_ROLES = ("決裁", "推進", "門番", "利用", "評価", "反対")

BANT_KEYS: tuple[tuple[str, str], ...] = (
    ("budget", "Budget 予算"),
    ("authority", "Authority 決裁"),
    ("needs", "Needs 課題"),
    ("timeframe", "Timeframe 時期"),
)

# MEDDPICC + 「なぜ今か」。discovery-map の並び順もこの順。
DISCOVERY_KEYS: tuple[tuple[str, str], ...] = (
    ("identifiedPain", "課題 I"),
    ("metrics", "指標 M"),
    ("compellingEvent", "決め手 Ce"),
    ("economicBuyer", "決裁者 E"),
    ("decisionCriteria", "評価基準 D"),
    ("decisionProcess", "決裁プロセス P"),
    ("champion", "推進役 C"),
    ("competition", "競合 Co"),
    ("paperProcess", "契約手続 Pa"),
)
DISCOVERY_LABEL = dict(DISCOVERY_KEYS)

# プレイブック §7 の 10 問。(番号, 問い, 判定関数名, 確認相手の目安)
CHECKPOINTS: tuple[tuple[int, str, str, str], ...] = (
    (1, "顧客が達成したい事業成果は何か", "metrics", "課題所有部門の責任者"),
    (2, "なぜ今、意思決定する必要があるのか", "compellingEvent", "Champion"),
    (3, "課題を放置した場合の影響は何か", "pain_chain", "現場担当と上位管理職"),
    (4, "課題と To-Be は顧客と合意できているか", "goal_agreed", "Champion"),
    (5, "なぜ Scalar が必要で、競合や現状維持では不十分なのか", "decision_criteria", "技術評価者"),
    (6, "誰が Champion、決裁者、技術評価者、利用者、反対者、コーチか", "committee", "既知の関与者からの紹介"),
    (7, "予算、決裁、購買、法務、導入のマイルストーンは何か", "bant", "購買・情報システム部門"),
    (8, "パートナーは誰で、なぜ Scalar と組み、何に責任を持つか", "partners", "パートナー営業責任者"),
    (9, "最大のリスクと、それをコントロールする次の行動は何か", "risks", "社内（WPS / Deal Desk）"),
    (10, "今のステージの完了条件を示す顧客側の証拠は何か", "gates", "Champion"),
)

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


# ----------------------------------------------------------------- 入出力

def today() -> str:
    return _dt.date.today().isoformat()


def ledger_path(ae: str, customer: str, *, root: Path | None = None) -> Path:
    """accounts/<AE 名>/<顧客名>/account.json。名前はそのまま使う（正規化しない）。"""
    base = root or ACCOUNTS_DIR
    return base / ae / customer / "account.json"


def load(path: str | os.PathLike) -> dict:
    p = Path(path)
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise LedgerError(f"台帳が見つかりません: {p}") from exc
    except json.JSONDecodeError as exc:
        raise LedgerError(f"台帳の JSON が壊れています: {p}: {exc}") from exc
    if not isinstance(data, dict):
        raise LedgerError(f"台帳はオブジェクトである必要があります: {p}")
    return data


def save(ledger: dict, path: str | os.PathLike) -> Path:
    """`updatedAt` を今日に更新して原子的に書き出す。"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    ledger.setdefault("schemaVersion", SCHEMA_VERSION)
    ledger.setdefault("meta", {})["updatedAt"] = today()
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    tmp.replace(p)
    return p


def blank(ae: str, customer: str, *, opportunity: str = "") -> dict:
    """最小構成の台帳。空欄は空欄のまま残す（推測で埋めない）。"""
    return {
        "schemaVersion": SCHEMA_VERSION,
        "meta": {
            "ae": ae,
            "customer": customer,
            "opportunity": opportunity,
            "stage": 1,
            "forecast": "Pipeline",
            "amount": "",
            "closeDate": "",
            "updatedAt": today(),
            "drive": {},
            "decks": {},
        },
        "facts": [],
        "people": [],
        "discovery": {key: {"status": "missing", "note": "", "evidence": ""}
                      for key, _ in DISCOVERY_KEYS},
        "painChain": {"lead": "", "chain": [], "evidence": []},
        "decisionPath": None,
        "bant": {key: {"level": "unknown", "note": ""} for key, _ in BANT_KEYS},
        "gates": {},
        "partners": [],
        "risks": [],
        "actions": [],
        "visits": [],
        "winPlan": {"situation": "", "complication": "", "resolution": ""},
    }


# ------------------------------------------------------------------- 検証

def _problem(out: list[str], where: str, message: str) -> None:
    out.append(f"{where}: {message}")


def validate(ledger: dict) -> list[str]:
    """スキーマと内部矛盾を検査する。空欄は問題ではない（未確認は正常な状態）。"""
    out: list[str] = []
    if ledger.get("schemaVersion") != SCHEMA_VERSION:
        _problem(out, "schemaVersion", f"{SCHEMA_VERSION} である必要があります")

    meta = ledger.get("meta")
    if not isinstance(meta, dict):
        _problem(out, "meta", "オブジェクトである必要があります")
        return out
    for key in ("ae", "customer"):
        if not isinstance(meta.get(key), str) or not meta[key].strip():
            _problem(out, f"meta.{key}", "必須です")
    stage = meta.get("stage")
    if stage not in STAGES:
        _problem(out, "meta.stage", f"0〜6 である必要があります（現在: {stage!r}）")
    forecast = meta.get("forecast")
    if forecast not in FORECASTS:
        _problem(out, "meta.forecast", f"{' / '.join(FORECASTS)} のいずれか（現在: {forecast!r}）")
    close = meta.get("closeDate") or ""
    if close and not _DATE_RE.match(close):
        _problem(out, "meta.closeDate", "YYYY-MM-DD 形式で書きます")

    for i, fact in enumerate(_as_list(ledger.get("facts"))):
        where = f"facts[{i}]"
        if not isinstance(fact, dict):
            _problem(out, where, "オブジェクトである必要があります")
            continue
        if fact.get("kind") not in FACT_KINDS:
            _problem(out, where, f"kind は {' / '.join(FACT_KINDS)} のいずれか")
        if not str(fact.get("text", "")).strip():
            _problem(out, where, "text が空です")

    for i, person in enumerate(_as_list(ledger.get("people"))):
        where = f"people[{i}]"
        if not isinstance(person, dict):
            _problem(out, where, "オブジェクトである必要があります")
            continue
        if not str(person.get("name", "")).strip():
            _problem(out, where, "name が空です")
        if person.get("role") not in BUYING_ROLES:
            _problem(out, where, f"role は {' / '.join(BUYING_ROLES)} のいずれか")
        for axis in ("influence", "stance"):
            value = person.get(axis)
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                _problem(out, where, f"{axis} は 0〜1 の数値")
            elif not 0.0 <= float(value) <= 1.0:
                _problem(out, where, f"{axis} は 0〜1 の範囲")
        # 会っていない相手を「中立」として地図に置かない（プレイブックの原則）
        if not str(person.get("met", "")).strip() and person.get("stance") not in (None,):
            if not str(person.get("evidence", "")).strip():
                _problem(out, where,
                         "未面談の相手に stance を置くなら evidence（誰からの伝聞か）が要ります")

    discovery = ledger.get("discovery") or {}
    if not isinstance(discovery, dict):
        _problem(out, "discovery", "オブジェクトである必要があります")
        discovery = {}
    for key, item in discovery.items():
        where = f"discovery.{key}"
        if key not in DISCOVERY_LABEL:
            _problem(out, where, f"未知の項目です（使えるのは {', '.join(DISCOVERY_LABEL)}）")
            continue
        if not isinstance(item, dict):
            _problem(out, where, "オブジェクトである必要があります")
            continue
        if item.get("status") not in DISCOVERY_STATUS:
            _problem(out, where, f"status は {' / '.join(DISCOVERY_STATUS)} のいずれか")
        if item.get("status") == "confirmed" and not str(item.get("evidence", "")).strip():
            _problem(out, where, "confirmed には evidence（誰がいつ言ったか / どの文書か）が必須です")

    bant = ledger.get("bant") or {}
    for key, label in BANT_KEYS:
        item = bant.get(key)
        if not isinstance(item, dict):
            _problem(out, f"bant.{key}", "オブジェクトである必要があります")
            continue
        if item.get("level") not in BANT_LEVELS:
            _problem(out, f"bant.{key}", f"level は {' / '.join(BANT_LEVELS)} のいずれか")

    gates = ledger.get("gates") or {}
    for gid, item in gates.items():
        where = f"gates.{gid}"
        if gid not in ALL_GATE_IDS:
            _problem(out, where, "未知のゲート ID です（sales-playbook.md §2 を参照）")
            continue
        if not isinstance(item, dict):
            _problem(out, where, "オブジェクトである必要があります")
            continue
        if item.get("status") not in GATE_STATUS:
            _problem(out, where, f"status は {' / '.join(GATE_STATUS)} のいずれか")
        if item.get("status") == "met" and not str(item.get("evidence", "")).strip():
            _problem(out, where, "met には顧客側の証拠が必須です（社内の合意は証拠になりません）")

    for i, action in enumerate(_as_list(ledger.get("actions"))):
        where = f"actions[{i}]"
        if not isinstance(action, dict):
            _problem(out, where, "オブジェクトである必要があります")
            continue
        for key in ("what", "whom", "doneWhen"):
            if not str(action.get(key, "")).strip():
                _problem(out, where, f"{key} が空です（完了条件と相手のない行動は載せない）")
        status = action.get("status")
        if status not in ACTION_STATUS:
            _problem(out, where, f"status は {' / '.join(ACTION_STATUS)} のいずれか")
        due = action.get("due") or ""
        if due and not _DATE_RE.match(due):
            _problem(out, where, "due は YYYY-MM-DD 形式で書きます")
        elif not due and status == "open":
            _problem(out, where,
                     "due が空です。期限が決まるまでは status を proposed にする"
                     "（期限のない行動を open のまま残さない）")

    for i, visit in enumerate(_as_list(ledger.get("visits"))):
        where = f"visits[{i}]"
        if not isinstance(visit, dict):
            _problem(out, where, "オブジェクトである必要があります")
            continue
        date = visit.get("date") or ""
        if not _DATE_RE.match(date):
            _problem(out, where, "date は YYYY-MM-DD 形式で書きます")
        if visit.get("status") not in ("planned", "done"):
            _problem(out, where, "status は planned / done のいずれか")

    # フォーキャストの整合。根拠を書けない Commit は Best に落とす（§5）
    if forecast == "Commit":
        weak = [label for key, label in BANT_KEYS
                if (bant.get(key) or {}).get("level") != "ok"]
        if weak:
            _problem(out, "meta.forecast",
                     f"Commit だが BANT に ok でない項目があります: {', '.join(weak)}"
                     "（根拠を書けないなら Best に落とす）")
    return out


def _as_list(value: Any) -> list:
    return value if isinstance(value, list) else []


# ------------------------------------------------------------------- 未確認

def _discovery_status(ledger: dict, key: str) -> str:
    item = (ledger.get("discovery") or {}).get(key) or {}
    status = item.get("status")
    return status if status in DISCOVERY_STATUS else "missing"


def _current_gates(ledger: dict) -> list[tuple[str, str, dict]]:
    """現ステージのゲートを (ID, 条件, 記録) で返す。記録が無ければ空の dict。"""
    stage = (ledger.get("meta") or {}).get("stage")
    stage = stage if stage in GATES else 1
    recorded = ledger.get("gates") or {}
    return [(gid, label, recorded.get(gid) or {}) for gid, label in GATES[stage]]


def gaps(ledger: dict) -> list[dict]:
    """プレイブック §7 の 10 問のうち、答えられない箇所を返す。

    返すのは**行動の候補**であり、期限は入っていない。期限を決めるのは AE の仕事で、
    `carry_over()` で `actions` に取り込むときに付ける。
    """
    out: list[dict] = []
    meta = ledger.get("meta") or {}
    stage = meta.get("stage") if meta.get("stage") in STAGES else 1

    def add(num: int, what: str, why: str, whom: str, done_when: str) -> None:
        question = next(q for n, q, _, _ in CHECKPOINTS if n == num)
        out.append({
            "id": f"cp{num}",
            "question": question,
            "what": what,
            "why": why,
            "whom": whom,
            "doneWhen": done_when,
        })

    lookup = {n: (q, hint) for n, q, _, hint in CHECKPOINTS}

    if _discovery_status(ledger, "metrics") != "confirmed":
        add(1, "顧客の指標と現状値を取る", "事業成果が数値で言えない",
            lookup[1][1], "指標名と現状値、集計元が分かる")
    if _discovery_status(ledger, "compellingEvent") != "confirmed":
        add(2, "「なぜ今か」を顧客の言葉で確認する", "期日の根拠が無い",
            lookup[2][1], "動かせない期日と、その理由が取れる")

    chain = (ledger.get("painChain") or {}).get("chain") or []
    evidence = (ledger.get("painChain") or {}).get("evidence") or []
    if len(chain) < 3 or len(evidence) < 3:
        add(3, "現場課題から経営数値までの連鎖を裏付ける", "放置コストを示せない",
            lookup[3][1], "各段に出所のある数値が付く")

    goal = (ledger.get("gates") or {}).get("g2.goal-agreed") or {}
    if goal.get("status") != "met":
        add(4, "業務ゴールと To-Be を顧客と合意する", "合意の証拠が無い",
            lookup[4][1], "議事録に顧客の同意発言が残る")

    if _discovery_status(ledger, "decisionCriteria") != "confirmed":
        add(5, "選定条件を聞き出し、当社の差別化を載せる", "勝てる条件が分からない",
            lookup[5][1], "選定条件の一覧と重みが取れる")

    people = _as_list(ledger.get("people"))
    have_roles = {p.get("role") for p in people if isinstance(p, dict)}
    for role in ("決裁", "推進"):
        if role not in have_roles:
            add(6, f"{role}者を特定する", "購買関与者が埋まっていない",
                lookup[6][1], f"{role}者の氏名と役職が分かる")
    unmet = [p.get("name", "?") for p in people
             if isinstance(p, dict) and p.get("role") in ("決裁", "門番")
             and not str(p.get("met", "")).strip()]
    for name in unmet:
        add(6, f"{name} に面談する", "決裁・門番に未接触",
            "Champion 経由で同席を依頼", "面談を実施し、判断基準を聞けた")

    bant = ledger.get("bant") or {}
    for key, label in BANT_KEYS:
        level = (bant.get(key) or {}).get("level")
        if level != "ok":
            add(7, f"{label} を確定させる", f"{label} が {level or 'unknown'}",
                lookup[7][1], "根拠つきで ok と言える状態")

    if stage >= 3 and not _as_list(ledger.get("partners")):
        add(8, "導入パートナーを決める", "提供範囲を埋める体制が無い",
            lookup[8][1], "パートナーと役割・責任が合意できる")

    for risk in _as_list(ledger.get("risks")):
        if isinstance(risk, dict) and not str(risk.get("control", "")).strip():
            add(9, f"リスク「{risk.get('what', '?')}」の打ち手を決める",
                "コントロールする行動が無い", lookup[9][1], "次の一手と担当が決まる")

    for gid, label, item in _current_gates(ledger):
        status = item.get("status")
        if status != "met" or not str(item.get("evidence", "")).strip():
            add(10, f"{gid} を満たす", GATE_SHORT.get(gid, label),
                item.get("owner") or lookup[10][1], "顧客側の証拠を記録できる")

    return out


def carry_over(ledger: dict, *, default_due: str = "") -> dict:
    """未完了アクションを残し、`gaps()` の新しい候補を取り込む。

    - 既に同じ `what` の行があれば触らない（AE が付けた期限を上書きしない）
    - 取り込む行の `due` は空のまま。期限は AE が決める（`default_due` で一括指定可）
    """
    actions = _as_list(ledger.get("actions"))
    known = {str(a.get("what", "")).strip() for a in actions if isinstance(a, dict)}
    added = 0
    for gap in gaps(ledger):
        what = gap["what"]
        if what in known:
            continue
        actions.append({
            "what": what,
            "why": gap["why"],
            "whom": gap["whom"],
            "due": default_due,
            "doneWhen": gap["doneWhen"],
            "owner": (ledger.get("meta") or {}).get("ae", ""),
            "status": "open" if default_due else "proposed",
            "from": gap["id"],
        })
        known.add(what)
        added += 1
    ledger["actions"] = actions
    ledger.setdefault("_carryOver", {})["added"] = added
    return ledger


def overdue(ledger: dict, *, on: str | None = None) -> list[dict]:
    """期限切れの未完了アクション。"""
    day = on or today()
    return [a for a in _as_list(ledger.get("actions"))
            if isinstance(a, dict) and a.get("status") == "open"
            and _DATE_RE.match(a.get("due") or "") and a["due"] < day]


# ------------------------------------------------------------- スロット生成

def _fit(text: Any, limit: int) -> str:
    """テンプレートの maxLength に収める。切り詰めたことが分かるよう … を残す。"""
    s = "" if text is None else str(text).replace("\n", " ").strip()
    if len(s) <= limit:
        return s
    return s[: max(1, limit - 1)] + "…"


def _source(ledger: dict, extra: str = "") -> str:
    meta = ledger.get("meta") or {}
    parts = [f"{meta.get('customer', '')} 商談台帳（{meta.get('updatedAt', today())} 時点）"]
    if extra:
        parts.append(extra)
    return _fit(" / ".join(p for p in parts if p), 160)


def _stage_label(ledger: dict) -> str:
    stage = (ledger.get("meta") or {}).get("stage")
    return f"フェーズ {stage} — {STAGES[stage]}" if stage in STAGES else "フェーズ 不明"


def _short(person: dict, limit: int = 6) -> str:
    """influence-map のラベルは 6 文字まで。`short` があればそれを使う。"""
    return _fit(person.get("short") or person.get("name", ""), limit)


def _page_account_snapshot(ledger: dict) -> dict | None:
    meta = ledger.get("meta") or {}
    champion = next((p for p in _as_list(ledger.get("people"))
                     if isinstance(p, dict) and p.get("role") == "推進"), None)
    buyer = next((p for p in _as_list(ledger.get("people"))
                  if isinstance(p, dict) and p.get("role") == "決裁"), None)
    next_gate = next((f"{gid} — {label}" for gid, label, item in _current_gates(ledger)
                      if item.get("status") != "met"), "現ステージの条件は充足")
    rows = [
        ["顧客 / 商談名", _fit(f"{meta.get('customer', '')} / {meta.get('opportunity', '')}", 46)],
        ["Champion", _fit(_person_line(champion), 46)],
        ["決裁者", _fit(_person_line(buyer), 46)],
        ["次のゲート", _fit(next_gate, 46)],
    ]
    return {
        "title": _fit(meta.get("headline") or _default_headline(ledger), 70),
        "headline": [
            ["ステージ", _fit(f"{meta.get('stage')} {STAGES.get(meta.get('stage'), '')}", 24)],
            ["フォーキャスト", _fit(meta.get("forecast", ""), 24)],
            ["想定 TCV", _fit(meta.get("amount") or "未確定", 24)],
            ["決定予定日", _fit(meta.get("closeDate") or "未確定", 24)],
        ],
        "rows": rows,
        "source": _source(ledger),
    }


def _person_line(person: dict | None) -> str:
    if not person:
        return "未特定"
    bits = [person.get("name", "")]
    if person.get("title"):
        bits.append(f"（{person['title']}）")
    if not str(person.get("met", "")).strip():
        bits.append(" — 未面談")
    return "".join(bits)


def _default_headline(ledger: dict) -> str:
    unmet = [gid for gid, _, item in _current_gates(ledger) if item.get("status") != "met"]
    if not unmet:
        return f"{_stage_label(ledger)} の条件は充足。次ステージの判断に進む"
    return f"{_stage_label(ledger)}。未達 {len(unmet)} 件が次の一手を決める"


def _page_phase_gate(ledger: dict) -> dict | None:
    rows = []
    for gid, label, item in _current_gates(ledger):
        rows.append([
            _fit(f"{gid} {GATE_SHORT.get(gid, label)}", 40),
            _fit(item.get("status") or "unmet", 40),
            _fit(item.get("evidence") or "未取得", 40),
            _fit(item.get("owner") or (ledger.get("meta") or {}).get("ae", ""), 40),
        ])
    if len(rows) < 3:
        return None
    rows = rows[:6]
    unmet = sum(1 for r in rows if r[1] != "met")
    title = (f"{len(rows)} 条件のうち {unmet} 件が未達。証拠が取れるまでステージは上げない"
             if unmet else "全条件が顧客側の証拠つきで充足。次ステージに進める")
    return {
        "title": _fit(title, 70),
        "stage": _fit(f"{_stage_label(ledger)} / 判定日 {today()}", 60),
        "gates": rows,
        "source": _source(ledger),
    }


def _page_bant_risk(ledger: dict) -> dict | None:
    bant = ledger.get("bant") or {}
    items = []
    for key, label in BANT_KEYS:
        entry = bant.get(key) or {}
        level = entry.get("level") or "unknown"
        note = entry.get("note") or "未確認"
        items.append([_fit(label, 16), _fit(f"{level} — {note}", 80)])
    weak = [label for key, label in BANT_KEYS
            if (bant.get(key) or {}).get("level") != "ok"]
    if weak:
        insight = f"{'・'.join(l.split()[0] for l in weak)} が未確定。{(ledger.get('meta') or {}).get('forecast')} 以上には上げない。"
    else:
        insight = "4 項目とも根拠つきで ok。Commit の条件を満たしている。"
    return {
        "title": _fit(_bant_title(weak), 70),
        "items": items,
        "insight": _fit(insight, 110),
        "source": _source(ledger),
    }


def _bant_title(weak: list[str]) -> str:
    if not weak:
        return "BANT は 4 項目とも確定済み。残るリスクは提供側にある"
    names = "・".join(l.split()[0] for l in weak)
    return f"{names} が未確定のまま。ここが商談を止める"


def _page_action_plan(ledger: dict) -> dict | None:
    rows = []
    for action in _as_list(ledger.get("actions")):
        if not isinstance(action, dict) or action.get("status") not in LIVE_ACTIONS:
            continue
        rows.append([
            _fit(action.get("what"), 36),
            _fit(action.get("why"), 36),
            _fit(action.get("whom"), 36),
            _fit(action.get("due") or "未定", 36),
            _fit(action.get("doneWhen"), 36),
        ])
    if len(rows) < 3:
        return None
    rows = rows[:6]
    unanswered = sorted({g["id"] for g in gaps(ledger)},
                        key=lambda s: int(s[2:]))
    lead = (f"10 問チェックポイントのうち {'・'.join('#' + s[2:] for s in unanswered)} が空白。"
            if unanswered else "未確認の論点は解消済み。実行の期限だけ管理する。")
    return {
        "title": _fit(_action_title(rows), 70),
        "lead": _fit(lead, 100),
        "actions": rows,
        "source": _source(ledger),
    }


def _action_title(rows: list[list[str]]) -> str:
    dues = sorted(r[3] for r in rows if _DATE_RE.match(r[3]))
    if dues:
        return f"直近の期限は {dues[0]}。この {len(rows)} 件が片付くまでステージは上げない"
    return f"未確認を潰す {len(rows)} 件。まず期限を入れる"


def _page_activity_timeline(ledger: dict) -> dict | None:
    done = [v for v in _as_list(ledger.get("visits"))
            if isinstance(v, dict) and v.get("status") == "done" and v.get("date")]
    done.sort(key=lambda v: v["date"])
    if len(done) < 3:
        return None
    recent = done[-6:]
    milestones = [[_fit(_md(v["date"]), 10),
                   _fit(v.get("label") or v.get("purpose") or v.get("next") or "面談", 16)]
                  for v in recent]
    rows = [[_fit(_md(v["date"]), 44),
             _fit(v.get("attendees") or "", 44),
             _fit(v.get("heard") or v.get("next") or "", 44)]
            for v in done[-4:]]
    if len(rows) < 2:
        return None
    return {
        "title": _fit(_timeline_title(done), 70),
        "milestones": milestones,
        "rows": rows,
        "source": _source(ledger),
    }


def _md(date: str) -> str:
    return date[5:].replace("-", "/") if _DATE_RE.match(date) else date


def _timeline_title(visits: list[dict]) -> str:
    last = visits[-1]["date"]
    try:
        days = (_dt.date.today() - _dt.date.fromisoformat(last)).days
    except ValueError:
        days = 0
    if days > 30:
        return f"最終接触から {days} 日空いている。接点を作り直すところから始める"
    return f"{len(visits)} 回の面談で課題は取れた。残るのは決裁と期日"


def _page_discovery_map(ledger: dict) -> dict | None:
    discovery = ledger.get("discovery") or {}
    items = []
    for n, (key, label) in enumerate(DISCOVERY_KEYS, start=1):
        entry = discovery.get(key)
        if not isinstance(entry, dict):
            continue
        items.append([n, _fit(label, 16),
                      _fit(entry.get("note") or "未確認", 34),
                      _fit(entry.get("status") or "missing", 9)])
    if len(items) < 4:
        return None
    items = items[:8]
    missing = [i[1] for i in items if i[3] == "missing"]
    insight = (f"{'・'.join(missing[:3])} が空白のまま。ここが埋まるまで提案書は書かない。"
               if missing else "空白は解消済み。提案書の作成に進める。")
    return {
        "title": _fit(_discovery_title(items), 70),
        "items": items,
        "insight": _fit(insight, 110),
        "source": _source(ledger),
    }


def _discovery_title(items: list[list]) -> str:
    confirmed = sum(1 for i in items if i[3] == "confirmed")
    return f"{len(items)} 項目のうち確認済みは {confirmed} 件。残りは仮説のまま"


def _page_pain_chain(ledger: dict) -> dict | None:
    pain = ledger.get("painChain") or {}
    chain = [_fit(c, 18) for c in _as_list(pain.get("chain"))][:5]
    evidence = [[_fit(cell, 40) for cell in row][:3]
                for row in _as_list(pain.get("evidence"))][:5]
    if len(chain) < 3 or len(evidence) < 3:
        return None
    return {
        "title": _fit(pain.get("title") or f"{chain[0]}が{chain[-1]}に効いている", 70),
        "lead": _fit(pain.get("lead") or "現場の作業が経営指標に届くまでを、各段の裏付けとあわせて辿る。", 100),
        "chain": chain,
        "evidence": evidence,
        "source": _source(ledger, "連鎖は仮説を含む。各段の算定方法は台帳を参照"),
    }


def _page_influence_map(ledger: dict) -> dict | None:
    people = [p for p in _as_list(ledger.get("people")) if isinstance(p, dict)]
    if len(people) < 3:
        return None
    stakeholders = [[_short(p), float(p.get("stance", 0.5)), float(p.get("influence", 0.5))]
                    for p in people[:9]]
    champion = next((p for p in people if p.get("role") == "推進"), None)
    if champion is None:
        return None
    unmet = [_short(p) for p in people
             if p.get("role") in ("決裁", "門番") and not str(p.get("met", "")).strip()]
    insight = (f"{'・'.join(unmet[:2])} に未接触。{_short(champion)}に同席を依頼して接点を作る。"
               if unmet else f"{_short(champion)}を軸に、決裁者への説明を組み立てる。")
    return {
        "title": _fit(_influence_title(people, champion), 70),
        "stakeholders": stakeholders,
        "xAxis": ["反対寄り", "支持寄り"],
        "yAxis": ["影響力が小さい", "影響力が大きい"],
        "champion": _short(champion),
        "insight": _fit(insight, 120),
        "source": _source(ledger, "位置は面談時の発言と過去の意思決定に基づく判断"),
    }


def _influence_title(people: list[dict], champion: dict) -> str:
    top = max(people, key=lambda p: float(p.get("influence", 0)))
    if top is champion:
        return f"最も影響力があるのは{_short(champion, 10)}。ここを軸に決裁へ上げる"
    return f"決裁を握るのは{_short(top, 10)}、動かす鍵は{_short(champion, 10)}にある"


def _page_buying_committee(ledger: dict) -> dict | None:
    people = [p for p in _as_list(ledger.get("people")) if isinstance(p, dict)]
    if len(people) < 3:
        return None
    members = [[_fit(f"{p.get('title', '')} {p.get('name', '')}".strip(), 22),
                _fit(p.get("role", ""), 22),
                _fit(p.get("influenceLabel") or _band(p.get("influence")), 22),
                _fit(p.get("stanceLabel") or _stance(p.get("stance")), 22),
                _fit(p.get("met") or "未接触", 22)]
               for p in people[:7]]
    unmet = [m[0] for m in members if m[4] == "未接触"]
    insight = (f"{'・'.join(unmet[:2])} に会えていない。同席を依頼して接点を作る。"
               if unmet else "主要な関与者には接触済み。判断基準の確認に進む。")
    return {
        "title": _fit(f"{len(members)} 名のうち {len(unmet)} 名が未接触" if unmet
                      else "主要な関与者に接触済み", 70),
        "members": members,
        "insight": _fit(insight, 120),
        "source": _source(ledger, "面談日は台帳の visits を参照"),
    }


def _band(value: Any) -> str:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return "不明"
    return "大" if v >= 0.67 else ("中" if v >= 0.34 else "小")


def _stance(value: Any) -> str:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return "不明"
    return "支持" if v >= 0.67 else ("中立" if v >= 0.34 else "懸念")


def _page_discovery_gaps(ledger: dict) -> dict | None:
    rows = []
    for action in _as_list(ledger.get("actions")):
        if not isinstance(action, dict) or action.get("status") not in LIVE_ACTIONS:
            continue
        rows.append([_fit(action.get("what"), 40), _fit(action.get("why"), 40),
                     _fit(action.get("whom"), 40), _fit(action.get("due") or "未定", 40)])
    if len(rows) < 3:
        return None
    return {
        "title": _fit("次に確認すべきことを、相手と期限まで決める", 70),
        "lead": _fit("質問の量ではなく順序で決まる。上から順に潰す。", 100),
        "gaps": rows[:6],
        "source": _source(ledger),
    }


def _page_visit_plan(ledger: dict) -> dict | None:
    planned = [v for v in _as_list(ledger.get("visits"))
               if isinstance(v, dict) and v.get("status") == "planned"]
    if not planned:
        return None
    visit = sorted(planned, key=lambda v: v.get("date") or "")[0]
    questions = [_fit(q, 44) for q in _as_list(visit.get("questions"))][:4]
    objections = [[_fit(o[0], 20), _fit(o[1], 52)]
                  for o in _as_list(visit.get("objections"))
                  if isinstance(o, (list, tuple)) and len(o) >= 2][:3]
    if len(questions) < 3 or len(objections) < 2:
        return None
    meta = ledger.get("meta") or {}
    context = " / ".join(p for p in [
        visit.get("date", ""), visit.get("attendees", ""),
        f"当社 {visit.get('ours', meta.get('ae', ''))}", _stage_label(ledger)] if p)
    return {
        "title": _fit(visit.get("purpose") or "この訪問で得たい一言を書く", 70),
        "context": _fit(context, 120),
        "questions": questions,
        "ask": _fit(visit.get("ask") or "次に紹介してほしい人物・部門と、その理由を書く", 90),
        "objections": objections,
        "source": _source(ledger),
    }


def _page_win_plan(ledger: dict) -> dict | None:
    win = ledger.get("winPlan") or {}
    if not all(str(win.get(k, "")).strip()
               for k in ("situation", "complication", "resolution")):
        return None
    risks = [[_fit(r.get("what"), 46), _fit(r.get("control"), 46)]
             for r in _as_list(ledger.get("risks"))
             if isinstance(r, dict) and str(r.get("control", "")).strip()][:3]
    if len(risks) < 2:
        return None
    return {
        "title": _fit(win.get("title") or "勝ち筋と、潰すべき最大のリスク", 70),
        "situation": _fit(win["situation"], 84),
        "complication": _fit(win["complication"], 84),
        "resolution": _fit(win["resolution"], 84),
        "risks": risks,
        "source": _source(ledger),
    }


PAGES: dict[str, Any] = {
    "account-snapshot": _page_account_snapshot,
    "phase-gate": _page_phase_gate,
    "bant-risk": _page_bant_risk,
    "action-plan": _page_action_plan,
    "activity-timeline": _page_activity_timeline,
    "discovery-map": _page_discovery_map,
    "pain-chain": _page_pain_chain,
    "influence-map": _page_influence_map,
    "buying-committee": _page_buying_committee,
    "discovery-gaps": _page_discovery_gaps,
    "visit-plan": _page_visit_plan,
    "win-plan": _page_win_plan,
}


def to_slot_data(ledger: dict, page_id: str) -> dict | None:
    """スライドテンプレート 1 枚分の入力を作る。材料が足りなければ None。

    None を返したページは**デッキから落とす**。空欄を埋めた薄いページを作らない。
    """
    builder = PAGES.get(page_id)
    if builder is None:
        raise LedgerError(
            f"台帳から作れないページです: {page_id}（作れるのは {', '.join(sorted(PAGES))}）")
    return builder(ledger)


def available_pages(ledger: dict) -> list[str]:
    return [pid for pid in PAGES if to_slot_data(ledger, pid) is not None]


# ------------------------------------------------------------ Markdown 出力

def action_markdown(ledger: dict) -> str:
    """CRM の Next Action に貼れる形。期限順、期限切れには ⚠ を付ける。"""
    meta = ledger.get("meta") or {}
    open_actions = [a for a in _as_list(ledger.get("actions"))
                    if isinstance(a, dict) and a.get("status") in LIVE_ACTIONS]
    open_actions.sort(key=lambda a: (a.get("due") or "9999-99-99", a.get("what") or ""))
    day = today()
    lines = [
        f"# {meta.get('customer', '')} — アクションプラン",
        "",
        f"- 担当 AE: {meta.get('ae', '')}",
        f"- 商談: {meta.get('opportunity', '')}",
        f"- ステージ: {_stage_label(ledger)} / フォーキャスト: {meta.get('forecast', '')}",
        f"- 更新日: {meta.get('updatedAt', day)}",
        "",
        "| 未確認・やること | なぜ重要か | 相手 | 期限 | 完了条件 |",
        "|---|---|---|---|---|",
    ]
    for action in open_actions:
        due = action.get("due") or "未定"
        if _DATE_RE.match(due) and due < day:
            due = f"⚠ {due}"
        lines.append("| " + " | ".join([
            str(action.get("what", "")), str(action.get("why", "")),
            str(action.get("whom", "")), due, str(action.get("doneWhen", "")),
        ]) + " |")
    if not open_actions:
        lines.append("| （未完了のアクションなし） | | | | |")

    remaining = gaps(ledger)
    if remaining:
        lines += ["", "## まだ答えられない問い（プレイブック §7）", ""]
        seen: set[str] = set()
        for gap in remaining:
            if gap["question"] in seen:
                continue
            seen.add(gap["question"])
            lines.append(f"- **{gap['id']}** {gap['question']} → {gap['whom']} に確認")
    return "\n".join(lines) + "\n"


# -------------------------------------------------------------------- CLI

def _cmd_validate(args) -> int:
    ledger = load(args.path)
    problems = validate(ledger)
    if problems:
        for problem in problems:
            print(f"ERROR: {problem}", file=sys.stderr)
        return 1
    meta = ledger.get("meta") or {}
    print(f"OK: {meta.get('customer')} / {_stage_label(ledger)} / "
          f"{meta.get('forecast')} — 作れるページ: {', '.join(available_pages(ledger)) or 'なし'}")
    late = overdue(ledger)
    if late:
        print(f"  注意: 期限切れのアクションが {len(late)} 件あります", file=sys.stderr)
    return 0


def _cmd_gaps(args) -> int:
    ledger = load(args.path)
    found = gaps(ledger)
    if args.json:
        print(json.dumps(found, ensure_ascii=False, indent=2))
        return 0
    if not found:
        print("答えられない問いはありません")
        return 0
    for gap in found:
        print(f"[{gap['id']}] {gap['what']}  — {gap['why']} / {gap['whom']} / "
              f"完了条件: {gap['doneWhen']}")
    return 0


def _cmd_actions(args) -> int:
    ledger = load(args.path)
    if args.carry_over:
        carry_over(ledger)
        save(ledger, args.path)
    text = action_markdown(ledger)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(text, end="")
    return 0


def _cmd_slots(args) -> int:
    ledger = load(args.path)
    data = to_slot_data(ledger, args.page)
    if data is None:
        print(f"材料が足りません: {args.page}", file=sys.stderr)
        return 2
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                                  encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0


def _cmd_init(args) -> int:
    path = Path(args.out) if args.out else ledger_path(args.ae, args.customer)
    if path.exists() and not args.force:
        print(f"既にあります（上書きするなら --force）: {path}", file=sys.stderr)
        return 1
    save(blank(args.ae, args.customer, opportunity=args.opportunity or ""), path)
    print(f"wrote {path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="顧客ごとの営業活動台帳を扱う")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("validate", help="スキーマと内部矛盾を検査する")
    p.add_argument("path")
    p.set_defaults(func=_cmd_validate)

    p = sub.add_parser("gaps", help="10 問のうち答えられない箇所を出す")
    p.add_argument("path")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=_cmd_gaps)

    p = sub.add_parser("actions", help="アクションプランを Markdown で出す")
    p.add_argument("path")
    p.add_argument("--out")
    p.add_argument("--carry-over", action="store_true",
                   help="gaps() の候補を actions に取り込んでから出力する（台帳を書き換える）")
    p.set_defaults(func=_cmd_actions)

    p = sub.add_parser("slots", help="スライドテンプレート 1 枚分の入力を出す")
    p.add_argument("path")
    p.add_argument("page", choices=sorted(PAGES))
    p.add_argument("--out")
    p.set_defaults(func=_cmd_slots)

    p = sub.add_parser("init", help="空の台帳を作る")
    p.add_argument("--ae", required=True)
    p.add_argument("--customer", required=True)
    p.add_argument("--opportunity")
    p.add_argument("--out")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=_cmd_init)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except LedgerError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
