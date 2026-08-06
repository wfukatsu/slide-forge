#!/usr/bin/env python3
"""明細表スペック（JSON）から Excel / Google Spreadsheet を生成する。

    python scripts/build_sheet.py spec.json --dry-run          # 検証のみ（オフライン・無料）
    python scripts/build_sheet.py spec.json                    # xlsx を生成（out/sheets/<title>.xlsx）
    python scripts/build_sheet.py spec.json --out path.xlsx
    python scripts/build_sheet.py spec.json --gsheet [--folder <Drive フォルダ URL/ID>]

見積もり・BOM・費用内訳のような「明細 + 集計」の表を 1 つの JSON で記述し、
openpyxl で xlsx を組み立てる。--gsheet を付けると同じ xlsx を Drive へ
変換アップロードして Google Spreadsheet も作る（書式・数式は変換される）。
xlsx が常にソースであり、両出力は同一内容になる。

スペック形式:

    {
      "title": "ブック名（ファイル名・Drive 上の名前になる）",
      "sheets": [{
        "name": "シート名",
        "heading": "表の見出し（任意。1 行目に大きく表示）",
        "note": "注記（任意。有効期限・税区分など）",
        "columns": [
          {"header": "数量", "type": "int", "width": 8},
          {"header": "単価", "type": "currency"},
          {"header": "金額", "type": "currency", "formula": "=D{row}*F{row}"}
        ],
        "rows": [[...], ...],            // 列数は columns と一致。formula 列は null
        "summary": [                      // 任意。明細の下の集計ブロック
          {"label": "小計",        "formula": "=SUM(G{first}:G{last})"},
          {"label": "消費税 (10%)", "formula": "=G{s1}*0.1"},
          {"label": "合計",        "formula": "=G{s1}+G{s2}", "emphasis": true}
        ]
      }]
    }

数式内のプレースホルダ: {row} = その明細行の行番号（列 formula 用）、
{first}/{last} = 明細の先頭・末尾の行番号、{s1}, {s2}, … = 集計 1 行目・
2 行目…の行番号（前方の集計行だけ参照できる）。
type: text（既定）/ int / currency / percent / date。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _auth  # noqa: E402

XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
GSHEET_MIME = "application/vnd.google-apps.spreadsheet"

NUMBER_FORMATS = {
    "text": "@",
    "int": "#,##0",
    "currency": "¥#,##0",
    "percent": "0.0%",
    "date": "yyyy/mm/dd",
}

HEADER_FILL = "1F3864"   # 濃紺。scalar-2026 系の表ヘッダーに合わせた保守的な色
NOTE_COLOR = "808080"

_PLACEHOLDER_RE = re.compile(r"\{(row|first|last|s\d+)\}")


# ---------- 検証 ----------

def validate(spec: dict) -> list[str]:
    errors: list[str] = []
    if not spec.get("title"):
        errors.append("title がありません")
    sheets = spec.get("sheets")
    if not isinstance(sheets, list) or not sheets:
        return errors + ["sheets が空です"]

    for si, sheet in enumerate(sheets):
        where = f"sheets[{si}]"
        if not sheet.get("name"):
            errors.append(f"{where}: name がありません")
        cols = sheet.get("columns") or []
        if not cols:
            errors.append(f"{where}: columns が空です")
        for ci, col in enumerate(cols):
            if not col.get("header"):
                errors.append(f"{where}.columns[{ci}]: header がありません")
            ctype = col.get("type", "text")
            if ctype not in NUMBER_FORMATS:
                errors.append(f"{where}.columns[{ci}]: 未知の type '{ctype}'"
                              f"（使えるのは {'/'.join(NUMBER_FORMATS)}）")
            for m in _PLACEHOLDER_RE.findall(col.get("formula") or ""):
                if m != "row":
                    errors.append(f"{where}.columns[{ci}]: 列 formula で使えるのは "
                                  f"{{row}} のみ（{{{m}}} が指定された）")
        for ri, row in enumerate(sheet.get("rows") or []):
            if len(row) != len(cols):
                errors.append(f"{where}.rows[{ri}]: 列数 {len(row)} が columns の "
                              f"{len(cols)} と一致しません")
        for gi, item in enumerate(sheet.get("summary") or []):
            if not item.get("label") or not item.get("formula"):
                errors.append(f"{where}.summary[{gi}]: label と formula が必須です")
                continue
            for m in _PLACEHOLDER_RE.findall(item["formula"]):
                if m.startswith("s") and int(m[1:]) > gi:
                    errors.append(f"{where}.summary[{gi}]: {{{m}}} は自分より後の"
                                  "集計行を参照しています（前方参照のみ可）")
    return errors


# ---------- xlsx 生成 ----------

def _col_width(col: dict, values: list) -> float:
    if col.get("width"):
        return col["width"]
    # CJK を 2 文字幅として実測から見積もる
    def w(v) -> int:
        s = str(v) if v is not None else ""
        return sum(2 if ord(ch) > 0x2E7F else 1 for ch in s)
    return min(50, max(8, max([w(col["header"])] + [w(v) for v in values]) + 2))


def build_xlsx(spec: dict, path: str) -> None:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    wb.remove(wb.active)
    thin = Side(style="thin", color="BFBFBF")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    for sheet in spec["sheets"]:
        ws = wb.create_sheet(sheet["name"])
        cols = sheet["columns"]
        ncols = len(cols)
        r = 1

        if sheet.get("heading"):
            ws.cell(r, 1, sheet["heading"]).font = Font(size=14, bold=True)
            ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=ncols)
            r += 1
        if sheet.get("note"):
            c = ws.cell(r, 1, sheet["note"])
            c.font = Font(size=9, color=NOTE_COLOR)
            ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=ncols)
            r += 1
        if r > 1:
            r += 1  # 見出しブロックと表の間の空行

        header_row = r
        for ci, col in enumerate(cols, 1):
            c = ws.cell(header_row, ci, col["header"])
            c.font = Font(bold=True, color="FFFFFF")
            c.fill = PatternFill("solid", fgColor=HEADER_FILL)
            c.alignment = Alignment(horizontal="center", vertical="center")
            c.border = border
        ws.freeze_panes = ws.cell(header_row + 1, 1)

        rows = sheet.get("rows") or []
        first = header_row + 1
        last = header_row + len(rows)
        for ri, row in enumerate(rows):
            rr = first + ri
            for ci, (col, value) in enumerate(zip(cols, row), 1):
                if col.get("formula"):
                    value = col["formula"].replace("{row}", str(rr))
                c = ws.cell(rr, ci, value)
                c.border = border
                c.number_format = NUMBER_FORMATS[col.get("type", "text")]
                if col.get("type") in ("int", "currency", "percent"):
                    c.alignment = Alignment(horizontal="right")

        summary_first = last + 1
        for gi, item in enumerate(sheet.get("summary") or []):
            rr = summary_first + gi
            formula = item["formula"].replace("{first}", str(first)).replace(
                "{last}", str(last))
            for m in set(re.findall(r"\{s(\d+)\}", formula)):
                formula = formula.replace(f"{{s{m}}}", str(summary_first + int(m) - 1))
            label = ws.cell(rr, ncols - 1, item["label"])
            label.font = Font(bold=True)
            label.alignment = Alignment(horizontal="right")
            value = ws.cell(rr, ncols, formula)
            value.number_format = NUMBER_FORMATS[cols[-1].get("type", "currency")]
            value.font = Font(bold=True, size=12 if item.get("emphasis") else 11)
            value.border = border
            if item.get("emphasis"):
                value.fill = PatternFill("solid", fgColor="FFF2CC")

        for ci, col in enumerate(cols, 1):
            values = [row[ci - 1] for row in rows]
            ws.column_dimensions[get_column_letter(ci)].width = _col_width(col, values)

    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    wb.save(path)


# ---------- Google Spreadsheet（変換アップロード） ----------

def upload_gsheet(drive, xlsx_path: str, name: str, folder: str | None) -> str:
    """xlsx を Google Spreadsheet に変換して作成する。同名があれば内容を更新する。"""
    from googleapiclient.http import MediaFileUpload
    import drive_folder

    media = MediaFileUpload(xlsx_path, mimetype=XLSX_MIME, resumable=False)
    fid = _auth.folder_id(folder) if folder else None
    q = (f"name = '{drive_folder._escape(name)}' and mimeType = '{GSHEET_MIME}' "
         "and trashed = false")
    if fid:
        q += f" and '{fid}' in parents"
    hits = drive.files().list(q=q, fields="files(id)", pageSize=5).execute().get("files", [])
    if hits:
        f = drive.files().update(
            fileId=hits[0]["id"], media_body=media, fields="id,webViewLink"
        ).execute()
        print("  Google Spreadsheet を更新（同名の既存ファイル）")
    else:
        body: dict = {"name": name, "mimeType": GSHEET_MIME}
        if fid:
            body["parents"] = [fid]
        f = drive.files().create(
            body=body, media_body=media, fields="id,webViewLink"
        ).execute()
    return f["webViewLink"]


def main() -> int:
    p = argparse.ArgumentParser(description="明細表スペックから Excel / Google Spreadsheet を生成する")
    p.add_argument("spec", help="スペック JSON のパス")
    p.add_argument("--out", help="xlsx の出力パス（省略時: out/sheets/<title>.xlsx）")
    p.add_argument("--dry-run", action="store_true", help="検証のみ（生成しない・API を呼ばない）")
    p.add_argument("--gsheet", action="store_true",
                   help="Google Spreadsheet も作成する（xlsx を変換アップロード）")
    p.add_argument("--folder", help="Google Spreadsheet を置く Drive フォルダの URL または ID")
    args = p.parse_args()

    with open(args.spec, encoding="utf-8") as f:
        spec = json.load(f)

    errors = validate(spec)
    if errors:
        print("スペックに問題があります:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    nrows = sum(len(s.get("rows") or []) for s in spec["sheets"])
    print(f"検証 OK: {len(spec['sheets'])} シート / 明細 {nrows} 行")
    if args.dry_run:
        return 0

    safe = re.sub(r'[\\/:*?"<>|\s]+', "_", spec["title"]).strip("_")[:80] or "sheet"
    path = args.out or os.path.join("out", "sheets", f"{safe}.xlsx")
    build_xlsx(spec, path)
    print(f"  XLSX: {path}")

    if args.gsheet or args.folder:
        _, drive = _auth.services()
        url = upload_gsheet(drive, path, spec["title"], args.folder)
        print(f"  Google Spreadsheet: {url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
