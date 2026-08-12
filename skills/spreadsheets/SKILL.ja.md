---
name: spreadsheets
description: >-
  Generate line-item spreadsheets — estimates/quotes, BOMs, cost breakdowns,
  comparison tables — as Excel (.xlsx) and/or Google Spreadsheet from one JSON
  spec (scripts/build_sheet.py): typed columns, per-row formulas, a
  subtotal/tax/total summary block, offline validation before any API call.
  The xlsx is the source; the Google Spreadsheet is a Drive conversion of the
  same file, so both outputs always match. Companion deliverable to slide-forge
  decks (deck shows the cost summary, the spreadsheet holds the line items,
  both in the same Drive folder) — and also runs standalone.
  Triggers: "見積もりを作って", "見積書", "明細表", "費用内訳を Excel に",
  "BOM をスプレッドシートに", "Google スプレッドシートで出力", "xlsx で出力",
  "spreadsheets", "make an estimate sheet", "cost breakdown spreadsheet".
  Out of scope: free-form or existing-file xlsx authoring/editing
  (document-skills:xlsx), reading or analyzing spreadsheets, and tables drawn
  inside slides (the deck skills' table figure).
---

*[English](SKILL.md)*

# 明細スプレッドシート（Excel + Google スプレッドシート）

## 重要事項

- **仕様は 1 つ、出力は 2 つ。** JSON 仕様から openpyxl で `.xlsx` を
  ビルドし、`--gsheet` はその同じファイルを Drive 経由で Google
  スプレッドシートに変換する。2 つの出力を別々に作ってはならない —
  常に同一でなければならない。
- **金額は貼り付けた数値ではなく数式にする。** 金額 = 数量 × 単価 を実際の
  数式（`=D{row}*F{row}`）として書き、合計は `SUM` にする。ユーザーは納品
  されたファイルで数量を編集するので、合計はそれに追随しなければならない。
  リテラルの数値を入れるのは、ユーザーが入力として扱うべきセル
  （単価、数量）だけである。
- **修正は仕様に対して行う。** 変更があれば再生成する; タイトルとフォルダが
  同じなら Google スプレッドシートは**その場で**更新される（URL 維持）ため、
  ユーザーが持つリンクは常に 1 つで済む。
- **すべてのコマンドは slide-forge ルートを cwd として実行する** —
  インストール済みプラグインから実行する場合は `${CLAUDE_PLUGIN_ROOT}`、
  ローカルクローンでは `/path/to/slide-forge`。認証と venv はリポジトリ
  ルートで共有される（`config/`、`.venv`）。
- **価格をでっち上げない。** 単価・税率・割引条件はユーザーまたはその資料
  から得る。出典のないものは `○○` プレースホルダのまま残し、注記行と報告で
  明示する — デッキ本文と同じルール。
- **デッキの随伴納品物として**: スプレッドシートが提案書のコストスライド
  （`scalar-proposal-slides` の BOM など）を裏付ける場合は、**デッキの
  Drive フォルダ**に置き、スライドのサマリーとシートの合計を一致させる —
  スライドには 合計 を載せ、シートに 明細 を持たせる。

## クイックリファレンス

| タスク | コマンド |
|------|---------|
| 仕様の検証（オフライン・無料） | `.venv/bin/python scripts/build_sheet.py spec.json --dry-run` |
| xlsx のビルド（→ `out/sheets/<title>.xlsx`） | `.venv/bin/python scripts/build_sheet.py spec.json [--out path.xlsx]` |
| Google スプレッドシートも作成 | `--gsheet [--folder <Drive フォルダ URL/ID>]` |
| 仕様を隣にアーカイブ | `.venv/bin/python scripts/drive_folder.py upload <FOLDER> spec.json` |
| 実例（税サマリーつき見積もり） | `examples/estimate-sample.json` |

## 仕様フォーマット

完全なリファレンスは `build_sheet.py` の docstring にある; 形は次のとおり:

```json
{
  "title": "○○様向け ScalarDB 導入見積もり",
  "sheets": [{
    "name": "見積もり明細",
    "heading": "表の見出し（任意）",
    "note": "有効期限・税区分などの注記（任意）",
    "columns": [
      {"header": "数量", "type": "int", "width": 8},
      {"header": "単価（月額）", "type": "currency"},
      {"header": "金額（月額）", "type": "currency", "formula": "=D{row}*F{row}"}
    ],
    "rows": [[...], "…列数は columns と一致。formula 列は null…"],
    "summary": [
      {"label": "小計", "formula": "=SUM(G{first}:G{last})"},
      {"label": "消費税 (10%)", "formula": "=G{s1}*0.1"},
      {"label": "合計", "formula": "=G{s1}+G{s2}", "emphasis": true}
    ]
  }]
}
```

- `type`: `text`（既定）/ `int` / `currency`（¥#,##0）/ `percent` / `date`
- プレースホルダ: `{row}`（そのデータ行）、`{first}`/`{last}`（データ範囲）、
  `{s1}`, `{s2}`…（サマリー行、前方参照のみ）
- 1 ブックに複数シートを置ける: 明細 を先頭に、その後に 前提条件 / 内訳
  シートを置く — 前提を明記しない見積もりは後で揉めるので、数字が地域・
  為替レート・契約期間・対象外作業に依存する場合は必ず 前提条件 シートを
  含める。

## ワークフロー

1. **作成前に形を確定する**（AskUserQuestion、1 ラウンド、
   `references/interactive-intake.md` §0/§5 の作法に従う）: 明細の粒度と
   元資料; 税の扱い（税抜/税込/税率）; 出力 —
   xlsx のみ / Google Spreadsheet も（既定: 両方。納品先が Google Workspace
   なら Spreadsheet 主体）; Drive フォルダ（デッキの裏付けの場合はデッキの
   フォルダ）。指定済みの項目は飛ばす。
2. **仕様を作成し**、オフラインで検証する: `--dry-run` は列数の不一致、
   未知の type、不正なプレースホルダ参照を API 呼び出しの前に検出する。
3. **ビルド**: Google スプレッドシートが要求された場合は
   `--gsheet --folder <FOLDER>` を付ける。仕様 JSON を同じフォルダに
   アップロードする（Drive フォルダのルール）。
4. **数値を検証する** — 数式は仕様の中ではなくファイル内で計算されるため、
   一度は確認する: 変換後のシートを CSV でエクスポートして 小計/合計 を
   確かめる（`drive.files().export(fileId=…, mimeType="text/csv")` は
   計算済みの値を返す）か、期待される合計を再計算して比較する。数式内の
   列レターの誤りは、これをしない限り静かに見過ごされる。
5. **報告**: ローカルの xlsx パス、Google スプレッドシート URL
   （作成した場合）、Drive フォルダ、そしてユーザーが埋めるべき残りの
   `○○` プレースホルダ。
