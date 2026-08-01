#!/usr/bin/env python3
"""クラウドアイコンの取り込み（google-slides スキル側の実体を呼ぶ入口）。

アイコンは各ベンダーの資産で再配布できないため、**リポジトリには含めず、
利用者が自分の環境へ取り込む**。取り込みの実装は 1 箇所（google-slides スキルの
`scripts/fetch-cloud-icons.py`）にまとめてあり、両スキルへ同時に配置する。

    .venv/bin/python scripts/fetch-cloud-icons.py            # 3 ベンダーとも取り込む
    .venv/bin/python scripts/fetch-cloud-icons.py --verify   # 取り込み済みか確認
    .venv/bin/python scripts/fetch-cloud-icons.py --help     # 実体のヘルプ

引数はすべてそのまま実体へ渡す。
"""
from __future__ import annotations

import os
import runpy
import sys

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_ROOT = os.path.dirname(SKILL_DIR)

CANDIDATES = [
    os.path.join(SKILLS_ROOT, "google-slides", "scripts", "fetch-cloud-icons.py"),
    os.path.expanduser("~/.claude/skills/google-slides/scripts/fetch-cloud-icons.py"),
]


def main() -> int:
    target = next((p for p in CANDIDATES if os.path.exists(p)), None)
    if not target:
        print(
            "クラウドアイコンの取り込みスクリプトが見つかりません。\n"
            "  期待した場所: " + "\n              ".join(CANDIDATES) + "\n\n"
            "  取り込みの実体は google-slides スキルにあります。同スキルを入れるか、\n"
            "  素材を手で用意する場合は次の 3 つを展開して assets/cloud-icons/ に置き、\n"
            "  cloud-icons.json を作ってください（形式は assets/cloud-icons/README.md）。\n"
            "    AWS   : https://aws.amazon.com/architecture/icons/\n"
            "    Azure : https://learn.microsoft.com/en-us/azure/architecture/icons/\n"
            "    Google: https://cloud.google.com/icons",
            file=sys.stderr)
        return 1

    # 実体は自分の位置から配置先を決める。ここでは引数だけ渡して実行する
    sys.argv[0] = target
    runpy.run_path(target, run_name="__main__")
    return 0


if __name__ == "__main__":
    sys.exit(main())
