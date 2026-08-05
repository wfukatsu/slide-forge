#!/usr/bin/env python3
"""デッキモジュールの座標を、Google Slides API を呼ばずに検査する。

    python scripts/validate_layout.py path/to/mydeck.py [--template templates/x.json]

検査する内容:

1. 図形がフッター領域（DY1 より下）に侵入していないか
   → 侵入するとマスターのロゴ・著作権表示・要点行と重なる
2. 図形がスライドの左右外に出ていないか
3. タイトルが 1 行に収まるか
   → 2 行になるとタイトルが図の領域を侵食する
4. 描画中に例外が出ないか（座標計算のミスをここで捕まえる）
5. レイアウト名がテンプレートで解決できるか、プレースホルダが存在するか
6. コネクタ（矢印・線）の端点が図形に接しているか
   → どの図形からも離れている / 図形の内部に埋まっている端点を検出する
7. 文字を持つ図形どうしが部分的に重なっていないか（入れ子は許す）
8. 枠に対して文字が多すぎないか（溢れた文字は切れて見える）

API を叩かないので無料・即時。生成する前に必ず通すこと。
終了コードは問題があれば 1、なければ 0。
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import deckkit  # noqa: E402
from diagrams import Canvas  # noqa: E402

# ラベルは中央寄せの都合で枠から僅かにはみ出すことがあるため、左右は少し緩める
LEFT_SLACK, RIGHT_SLACK = 0.25, 0.25

# コネクタの判定しきい値は diagrams.Canvas.CONN_* にある

FILLABLE = {"TITLE", "SUBTITLE", "BODY"}


def load_deck_module(path: str):
    """デッキモジュールを読み込み、SLIDES を返す。"""
    path = os.path.abspath(path)
    if not os.path.exists(path):
        raise SystemExit(f"デッキモジュールが見つかりません: {path}")
    # デッキ側が `from deckkit import *` できるよう、モジュールのディレクトリも通す
    sys.path.insert(0, os.path.dirname(path))
    deckkit.reset()
    spec = importlib.util.spec_from_file_location("_deck", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    slides = getattr(mod, "SLIDES", None) or deckkit.SLIDES
    if not slides:
        raise SystemExit(f"{path} にスライドが登録されていません（slide() / plain() を呼ぶこと）")
    return mod, list(slides)


class FakeDeck:
    """API を持たないダミー。Canvas が積むリクエストを捨てる。"""

    def __init__(self):
        self.requests = []


class TrackedCanvas(Canvas):
    """描画された図形の外接範囲を記録する Canvas。"""

    def __init__(self, template):
        super().__init__(FakeDeck(), "offline", template)
        self.bottom = 0.0
        self.right = 0.0
        self.left = 99.0

    def _elem_props(self, x, y, w, h, *args, **kwargs):
        # 下部の固定要素（要点行・エディション行）は意図した位置なので除外する
        if not deckkit.FOOT_MODE[0]:
            self.bottom = max(self.bottom, y + h)
            self.right = max(self.right, x + w)
            self.left = min(self.left, x)
        return super()._elem_props(x, y, w, h, *args, **kwargs)


def resolve_layout(template: dict, key: str):
    resolved = template.get("roles", {}).get(key, key)
    return resolved, template.get("layouts", {}).get(resolved)


def check(template: dict, slides: list[dict]) -> list[str]:
    problems: list[str] = []
    bottom_max = deckkit.DY1
    left_min = deckkit.X0 - LEFT_SLACK
    right_max = deckkit.XE + RIGHT_SLACK

    for i, s in enumerate(slides, 1):
        title = s.get("title") or ""
        key = s.get("layout")
        resolved, layout = resolve_layout(template, key)

        # --- レイアウトとプレースホルダ ---
        if layout is None:
            problems.append(f"{i:2d} レイアウト '{key}' がテンプレートで解決できません")
        else:
            # drawText で座標指定描画されるものも、指定可能な枠として扱う
            declared = list(layout.get("placeholders", []))
            for dk in layout.get("drawText", {}):
                name = dk.upper().replace("X", "#") if dk[-1].isdigit() else dk.upper()
                if name not in declared:
                    declared.append(name)
            for ph in ("TITLE", "SUBTITLE"):
                if s.get(ph.lower()) is not None and ph not in declared:
                    problems.append(
                        f"{i:2d} レイアウト '{key}' は {ph} を持ちません（保持: {declared}）")
            slots = [p for p in declared if p.split("#")[0] == "BODY"]
            bodies = s.get("bodies")
            if bodies is None and s.get("body") is not None:
                bodies = [s["body"]]
            if bodies is not None and len(bodies) > len(slots):
                problems.append(
                    f"{i:2d} レイアウト '{key}' の BODY は {len(slots)} 枠ですが "
                    f"{len(bodies)} 個指定されています")

        # --- タイトルの折り返し ---
        if s.get("draw") and title and not deckkit.fits_one_line(title):
            problems.append(
                f"{i:2d} タイトルが2行になり図と重なります"
                f"（em={deckkit.em(title):.1f} > {deckkit.TITLE_EM_MAX}）: {title}")

        # --- 描画とはみ出し ---
        if not s.get("draw"):
            continue
        c = TrackedCanvas(template)
        try:
            s["draw"](c)
        except Exception as e:  # noqa: BLE001
            problems.append(f"{i:2d} 描画で例外: {type(e).__name__}: {e}")
            continue
        finally:
            deckkit.FOOT_MODE[0] = False
        if c.bottom > bottom_max + 0.001:
            problems.append(
                f"{i:2d} 図がフッター領域にはみ出します"
                f"（bottom={c.bottom:.2f} > {bottom_max}）: {title}")
        if c.right > right_max or c.left < left_min:
            problems.append(
                f"{i:2d} 図が左右にはみ出します"
                f"（left={c.left:.2f} right={c.right:.2f}）: {title}")
        for msg in (c.audit_connectors() + c.audit_overlaps()
                    + c.audit_text_fit()):     # 実装は diagrams.Canvas 側
            problems.append(f"{i:2d} {msg}: {title}")
    return problems


def main() -> int:
    p = argparse.ArgumentParser(description="デッキの座標をオフラインで検査する")
    p.add_argument("deck", help="デッキモジュールの .py")
    p.add_argument("--template", help="template.json（省略時はデッキの TEMPLATE を使う）")
    p.add_argument("--quiet", action="store_true", help="問題がなければ何も出力しない")
    args = p.parse_args()

    mod, slides = load_deck_module(args.deck)
    if args.template:
        template = json.load(open(args.template, encoding="utf-8"))
    else:
        template = getattr(mod, "TEMPLATE", None)
        if template is None:
            raise SystemExit("--template を指定するか、デッキに TEMPLATE を定義してください")

    problems = check(template, slides)
    drawn = sum(1 for s in slides if s.get("draw"))
    if problems:
        print(f"検査: {len(slides)} 枚（図あり {drawn} 枚）", file=sys.stderr)
        print(f"問題 {len(problems)} 件:", file=sys.stderr)
        for msg in problems:
            print("  " + msg, file=sys.stderr)
        return 1
    if not args.quiet:
        print(f"検査: {len(slides)} 枚（図あり {drawn} 枚）")
        print("OK: はみ出し・タイトル折返し・レイアウト不整合なし")
    return 0


if __name__ == "__main__":
    sys.exit(main())
