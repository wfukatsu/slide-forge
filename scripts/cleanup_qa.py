#!/usr/bin/env python3
"""ビジュアル QA で使ったローカル検証ファイル（サムネイル PNG など）を削除する。

    python scripts/cleanup_qa.py                 # out/qa と out/*/qa を削除
    python scripts/cleanup_qa.py out/mydeck/qa   # 指定ディレクトリだけ削除
    python scripts/cleanup_qa.py --dry-run       # 削除対象を表示するだけ

QA が終わったサムネイルは再取得できる一時ファイルなので、結果報告の前に
このスクリプトで消す。誤爆防止のため、リポジトリの out/ 配下しか消さない。
"""
from __future__ import annotations

import argparse
import glob
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _i18n import t, register  # noqa: E402

register({
    "Delete QA verification files such as thumbnails":
        "QA サムネイルなどの検証ファイルを削除する",
    "directories to delete (default: out/qa and out/*/qa)":
        "削除するディレクトリ（省略時: out/qa と out/*/qa）",
    "show targets without deleting": "削除せずに対象を表示する",
    "skip (outside out/): {path}": "skip (out/ の外): {path}",
    "Nothing to delete": "削除対象はありません",
})

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "out")


def default_targets() -> list[str]:
    targets = [os.path.join(OUT_DIR, "qa")]
    targets.extend(sorted(glob.glob(os.path.join(OUT_DIR, "qa-*"))))
    targets.extend(sorted(glob.glob(os.path.join(OUT_DIR, "*", "qa"))))
    return targets


def resolve(path: str) -> str:
    if not os.path.isabs(path):
        path = os.path.join(ROOT, path)
    return os.path.realpath(path)


def main() -> int:
    p = argparse.ArgumentParser(
        description=t("Delete QA verification files such as thumbnails"))
    p.add_argument("paths", nargs="*",
                   help=t("directories to delete (default: out/qa and out/*/qa)"))
    p.add_argument("--dry-run", action="store_true",
                   help=t("show targets without deleting"))
    args = p.parse_args()

    targets = [resolve(p_) for p_ in args.paths] if args.paths else default_targets()
    out_real = os.path.realpath(OUT_DIR)

    removed = 0
    for target in targets:
        # out/ 自体と out/ の外は対象外。QA 出力ディレクトリだけを消す
        if not target.startswith(out_real + os.sep):
            print(t("skip (outside out/): {path}", path=target), file=sys.stderr)
            continue
        if not os.path.isdir(target):
            continue
        n_files = sum(len(fs) for _, _, fs in os.walk(target))
        if args.dry_run:
            print(f"would remove: {target} ({n_files} files)")
        else:
            shutil.rmtree(target)
            print(f"removed: {target} ({n_files} files)")
        removed += 1

    if removed == 0:
        print(t("Nothing to delete"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
