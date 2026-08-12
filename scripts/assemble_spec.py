#!/usr/bin/env python3
"""ページ単位の JSON 断片をつなげて 1 本のデッキ仕様にする。

大きなデッキをサブエージェントで分担生成するときに使う。各エージェントは
`pages/NNN-<slug>.json` に**自分の担当ページだけ**を書き、本体の仕様ファイルには
触らない。衝突しないので並行して書ける。

    python scripts/assemble_spec.py --out deck.json --title "資料タイトル" pages/

断片の中身は次のいずれか:

- スライド 1 枚のオブジェクト  `{"layout": "TITLE_ONLY", "title": "…", "figures": […]}`
- スライドの配列              `[{…}, {…}]`
- 仕様まるごと                `{"slides": [{…}]}`（`title` / `defaults` も拾う）

**並び順はファイル名の昇順**。`010-cover.json` `020-agenda.json` のように
10 刻みで振っておくと、後から間に挟める。
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _i18n import t, register  # noqa: E402

register({
    "Merge per-page spec fragments into one deck spec":
        "ページ単位のスペック断片を 1 つのデッキスペックに統合する",
    "{path}: not readable as JSON: {e}": "{path}: JSON として読めません: {e}",
    "{path}: must be an object or an array":
        "{path}: オブジェクトか配列である必要があります",
    "{path}: 'slides' must be an array":
        "{path}: 'slides' は配列である必要があります",
    "{path}: slides[{i}] is not an object":
        "{path}: slides[{i}] がオブジェクトではありません",
    "{path}: slides[{i}] has no 'layout'":
        "{path}: slides[{i}] に 'layout' がありません",
    "fragment JSON files / directories / globs":
        "断片の JSON / ディレクトリ / グロブ",
    "output spec file": "出力する仕様ファイル",
    "deck title (takes precedence over fragment titles)":
        "デッキのタイトル（断片側の title より優先）",
    "defaults as a JSON string (e.g. '{\"bodyFontSize\": 14}')":
        "defaults を JSON 文字列で指定（例: '{\"bodyFontSize\": 14}'）",
    "no fragments found": "断片が 1 つも見つかりません",
    "  {name}: {n} slides": "  {name}: {n} 枚",
    "--title is required (fragments have no title either)":
        "--title が要ります（断片にも title がありません）",
    "{fragments} fragments → {slides} slides → {out}":
        "{fragments} 断片 → {slides} 枚 → {out}",
    "Next: validate with build_deck.py --dry-run --strict, then generate":
        "次: build_deck.py --dry-run --strict で検証してから生成する",
})


def load_fragment(path: str) -> tuple[list, dict]:
    """断片を (スライドのリスト, 仕様レベルのキー) に正規化する。"""
    with open(path, encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise SystemExit(t("{path}: not readable as JSON: {e}",
                               path=path, e=e))

    if isinstance(data, list):
        slides, top = data, {}
    elif isinstance(data, dict) and "slides" in data:
        slides = data["slides"]
        top = {k: v for k, v in data.items() if k != "slides"}
    elif isinstance(data, dict):
        slides, top = [data], {}
    else:
        raise SystemExit(t("{path}: must be an object or an array", path=path))

    if not isinstance(slides, list):
        raise SystemExit(t("{path}: 'slides' must be an array", path=path))
    for i, s in enumerate(slides):
        if not isinstance(s, dict):
            raise SystemExit(t("{path}: slides[{i}] is not an object",
                               path=path, i=i))
        if "layout" not in s:
            raise SystemExit(t("{path}: slides[{i}] has no 'layout'",
                               path=path, i=i))
    return slides, top


def expand(inputs: list[str]) -> list[str]:
    """ディレクトリなら中の *.json を、グロブならその展開を、昇順で返す。"""
    out: list[str] = []
    for item in inputs:
        if os.path.isdir(item):
            out.extend(sorted(glob.glob(os.path.join(item, "*.json"))))
        elif any(ch in item for ch in "*?["):
            out.extend(sorted(glob.glob(item)))
        else:
            out.append(item)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(
        description=t("Merge per-page spec fragments into one deck spec"))
    ap.add_argument("inputs", nargs="+",
                    help=t("fragment JSON files / directories / globs"))
    ap.add_argument("--out", required=True, help=t("output spec file"))
    ap.add_argument("--title",
                    help=t("deck title (takes precedence over fragment "
                           "titles)"))
    ap.add_argument("--defaults",
                    help=t("defaults as a JSON string "
                           "(e.g. '{\"bodyFontSize\": 14}')"))
    args = ap.parse_args()

    paths = expand(args.inputs)
    if not paths:
        raise SystemExit(t("no fragments found"))

    # "title" をここで先に置くと setdefault が断片の title を拾えなくなる
    spec: dict = {"slides": []}
    for path in paths:
        slides, top = load_fragment(path)
        # 仕様レベルのキーは先に書いたものを優先する（後勝ちだと
        # 末尾の断片が意図せずデッキ全体の既定を塗り替えてしまう）
        for k, v in top.items():
            spec.setdefault(k, v)
        spec["slides"].extend(slides)
        print(t("  {name}: {n} slides", name=os.path.basename(path),
                n=len(slides)), file=sys.stderr)

    if args.title:
        spec["title"] = args.title
    if not spec.get("title"):
        raise SystemExit(t("--title is required (fragments have no title "
                           "either)"))
    if args.defaults:
        spec["defaults"] = json.loads(args.defaults)

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(spec, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(t("{fragments} fragments → {slides} slides → {out}",
            fragments=len(paths), slides=len(spec["slides"]), out=args.out),
          file=sys.stderr)
    print(t("Next: validate with build_deck.py --dry-run --strict, then "
            "generate"), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
