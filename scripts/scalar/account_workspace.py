#!/usr/bin/env python3
"""Drive 上の「AE 名 / 顧客名」ワークスペースを冪等に用意する。

    <ルート>/<AE 名>/<顧客名>/
      00_活動計画/   活動計画デッキ（URL 不変で更新）、account.json のコピー
      01_顧客提示/   顧客提示用
      02_顧客提案/   顧客提案用（正式提案・見積）
      90_社内/       社内説明用（訪問計画・WPS・Deal Desk・稟議）

ルートフォルダは `config/sales.json` に覚える（`config/` は .gitignore 済み）。
初回だけ `--root` で指定すれば、以降は省略できる。

**このスクリプトは削除を一切しない。** Drive の整理は人が行う。

    初回:   .venv/bin/python scripts/scalar/account_workspace.py ensure \
                --ae "山田 一郎" --customer "テスト商事株式会社" --root "<Drive フォルダ URL>"
    2 回目: .venv/bin/python scripts/scalar/account_workspace.py ensure \
                --ae "山田 一郎" --customer "テスト商事株式会社"
    設定:   .venv/bin/python scripts/scalar/account_workspace.py config --show
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_DIR / "scripts"))

import _auth  # noqa: E402
from drive_folder import ensure_folder, folder_url  # noqa: E402

sys.path.insert(0, str(REPO_DIR / "scripts" / "scalar"))
import account_ledger as ledger_mod  # noqa: E402

CONFIG_PATH = REPO_DIR / "config" / "sales.json"

# 番号を付けるのは Drive の並び順を固定するため。名前は変えない
# （変えると既存フォルダを再利用できず、同じ用途のフォルダが二つできる）。
SUBFOLDERS: tuple[str, ...] = (
    "00_活動計画",
    "01_顧客提示",
    "02_顧客提案",
    "90_社内",
)

# 資料種別 → 置き場。scalar-ae-materials スキルが参照する
PLACEMENT: dict[str, str] = {
    "activity-plan": "00_活動計画",
    "customer-facing": "01_顧客提示",
    "customer-proposal": "02_顧客提案",
    "internal": "90_社内",
}


class WorkspaceError(RuntimeError):
    pass


# ------------------------------------------------------------------- 設定

def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {}
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise WorkspaceError(f"config/sales.json が壊れています: {exc}") from exc


def save_config(config: dict) -> Path:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
    return CONFIG_PATH


def resolve_root(root: str | None = None) -> str:
    """ルートフォルダ ID を返す。`--root` が来ていれば設定に覚える。"""
    config = load_config()
    if root:
        rid = _auth.folder_id(root)
        if not rid:
            raise WorkspaceError(f"ルートフォルダの URL / ID を解釈できません: {root}")
        if config.get("driveRoot") != rid:
            config["driveRoot"] = rid
            save_config(config)
        return rid
    rid = config.get("driveRoot")
    if not rid:
        raise WorkspaceError(
            "ルートフォルダが未設定です。初回だけ --root <Drive フォルダ URL> を"
            "指定してください（config/sales.json に保存します）")
    return rid


# --------------------------------------------------------------- 階層作成

def ensure(ae: str, customer: str, *, root: str | None = None,
           drive=None) -> dict:
    """`<ルート>/<AE>/<顧客>/{4 つのサブフォルダ}` を冪等に用意し、ID を返す。"""
    if not ae.strip() or not customer.strip():
        raise WorkspaceError("AE 名と顧客名は必須です")
    root_id = resolve_root(root)
    if drive is None:
        _, drive = _auth.services()

    created: list[str] = []
    ae_id, made = ensure_folder(drive, ae, root_id)
    if made:
        created.append(ae)
    customer_id, made = ensure_folder(drive, customer, ae_id)
    if made:
        created.append(f"{ae}/{customer}")

    out = {"root": root_id, "ae": ae_id, "customer": customer_id}
    for name in SUBFOLDERS:
        fid, made = ensure_folder(drive, name, customer_id)
        out[name] = fid
        if made:
            created.append(f"{ae}/{customer}/{name}")
    out["_created"] = created
    return out


def folder_for(workspace: dict, kind: str) -> str:
    """資料種別からフォルダ ID を引く。"""
    name = PLACEMENT.get(kind)
    if name is None:
        raise WorkspaceError(
            f"未知の資料種別です: {kind}（使えるのは {', '.join(sorted(PLACEMENT))}）")
    return workspace[name]


def attach_to_ledger(ledger: dict, workspace: dict) -> dict:
    """フォルダ ID を台帳の meta.drive に控える（次回の API 検索を省くため）。"""
    drive = ledger.setdefault("meta", {}).setdefault("drive", {})
    for key, value in workspace.items():
        if key.startswith("_"):
            continue
        drive[key] = value
    return ledger


# -------------------------------------------------------------------- CLI

def _cmd_ensure(args) -> int:
    ledger = None
    ae, customer = args.ae, args.customer
    if args.ledger:
        ledger = ledger_mod.load(args.ledger)
        meta = ledger.get("meta") or {}
        ae = ae or meta.get("ae")
        customer = customer or meta.get("customer")
    if not ae or not customer:
        print("ERROR: --ae と --customer（または --ledger）が必要です", file=sys.stderr)
        return 1

    workspace = ensure(ae, customer, root=args.root)
    for name in workspace.pop("_created"):
        print(f"  作成: {name}")
    print(f"顧客フォルダ: {folder_url(workspace['customer'])}")
    for name in SUBFOLDERS:
        print(f"  {name}: {folder_url(workspace[name])}")

    if ledger is not None:
        attach_to_ledger(ledger, workspace)
        ledger_mod.save(ledger, args.ledger)
        print(f"台帳に控えました: {args.ledger}")
    if args.json:
        print(json.dumps(workspace, ensure_ascii=False, indent=2))
    return 0


def _cmd_config(args) -> int:
    config = load_config()
    changed = False
    if args.set_root:
        config["driveRoot"] = _auth.folder_id(args.set_root)
        changed = True
    if args.set_ae:
        config["defaultAe"] = args.set_ae
        changed = True
    if changed:
        save_config(config)
        print(f"wrote {CONFIG_PATH}")
    if not config:
        print("未設定です（ensure --root <URL> で保存されます）")
        return 0
    print(json.dumps(config, ensure_ascii=False, indent=2))
    if config.get("driveRoot"):
        print(f"ルート: {folder_url(config['driveRoot'])}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Drive の「AE 名 / 顧客名」ワークスペースを用意する")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("ensure", help="階層を冪等に作る")
    p.add_argument("--ae")
    p.add_argument("--customer")
    p.add_argument("--root", help="ルートフォルダ URL / ID（初回のみ。以降は設定を使う）")
    p.add_argument("--ledger", help="account.json のパス。フォルダ ID を控える")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=_cmd_ensure)

    p = sub.add_parser("config", help="保存済みの設定を見る / 変える")
    p.add_argument("--show", action="store_true", help="（既定の動作）")
    p.add_argument("--set-root")
    p.add_argument("--set-ae")
    p.set_defaults(func=_cmd_config)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (WorkspaceError, ledger_mod.LedgerError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
