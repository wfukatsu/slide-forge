*[English](sheets-link.md)*

# スプレッドシートと連携するデッキ

事業計画のようにシミュレーションする資料では、読み手が変えられるスプレッドシートにスライドの数値を追従させたい。次の3つのスクリプトで扱う。

| 段階 | スクリプト | 役割 |
|---|---|---|
| 1. モデル | `scripts/build_model.py model.json --folder <Drive フォルダ>` | Sheets API で Google スプレッドシートを作る。入力セル、数式の時系列表、シナリオ切替、名前付き範囲、ネイティブのグラフ |
| 2. デッキ | `scripts/build_deck.py … --spec deck.json` | `{{sheet:名前}}` をシートの表示値で埋め、`sheetsChart` をリンク付きグラフとして埋め込む |
| 3. 同期 | `scripts/sync_deck.py <deck> [--dry-run]` | シート変更後に、リンクグラフを更新し、バインドした数値だけをその場で書き換える |

見積・明細は引き続き `build_sheet.py`（xlsx と同一内容）を使う。人がシミュレーションするワークブックには `build_model.py` を使う。

## 1. モデルのスペック（build_model.py）

書式の全体はスクリプトの docstring にある。要点:

- `sheets[].blocks[]` を上から積む: `heading`、`note`、`inputs`（ラベル・単位・値・備考を1行ずつ）、`table`（ラベル・単位・列ごとの値）、`grid`（グラフ用データ。A 列がカテゴリ、系列ごとに1列）。
- リテラルは入力セル（黄色。**再生成しても読み手の入力値を保持**）。`=` で始まる文字列は数式。`"?"` は読み手が後で入れる空の入力セル。
- プレースホルダで数式を読みやすく、行位置の変化に強くする: `{@id}`（入力セル、または表の行の同じ列）、`{@id:FY27}`、`{@id:<}`（前の列）、`{range:id}`、`{range:a..b}`、`{hdr:表}`、`{col}` `{prev}` `{row}` `{first}` `{last}`。
- 列見出しが同じ表は列がそろうので、`"formula": "={@件数}*{@単価}"` がシートをまたいで使える。
- 入力 ID と表の行 ID はすべて**名前付き範囲**になる。
- `charts[]`: `type` は COLUMN / BAR / LINE / AREA / COMBO / PIE、`data` は grid の ID、`stacked`、`labels`、`colors`、`legend`、`vAxisTitle`。`size`（インチ）はスライド上の枠と同じにする。

再生成（同じフォルダに同じタイトル、または `--into`）しても sheetId と chartId は変わらず、スライドのリンクは切れない。入力セルの値も保持する（上書きするときは `--reset-inputs`）。生成後に全シートを読み戻し、`#REF!` `#NAME?` `#DIV/0!` などがあれば失敗にする。

**「スライド出力」シート**を用意し、デッキに出す数値をすべて数式行（`o_fy27_rev` など）として集め、スライドでの見え方の書式（`0.00"億円"`、`#,##0`、`0%`）を付けておく。デッキはこのシートだけを参照するので、何がスライドに出ているかをレビューで確認できる。

## 2. デッキのスペック

```json
{
  "spreadsheet": "https://docs.google.com/spreadsheets/d/<ID>/edit",
  "slides": [{
    "layout": "TITLE_ONLY",
    "title": "FY27 の売上は{{sheet:o_fy27_rev}}",
    "figures": [
      {"type": "table", "headers": ["", "FY27"], "rows": [["売上", "{{sheet:o_fy27_rev}}"]], …},
      {"type": "sheetsChart", "chart": "fy27_quarter", "x": 5.0, "y": 1.45, "w": 4.5, "h": 2.9}
    ]
  }]
}
```

- `{{sheet:名前}}` には名前付き範囲か A1 参照（`'売上'!G8`）を書く。セルの**表示値**に置き換わるので、見え方はシートの書式で決まる。
- `sheetsChart.chart` はモデルスペックのグラフ ID（またはグラフのタイトル、数値の chartId）。`--dry-run` では同じ大きさの仮図形を置くので、重なりの検査は効く。
- `--dry-run` はオフラインのまま。直前の本生成でキャッシュした値（`out/bindings/<id>.json`）か、同じ幅の仮の値を使う。
- 生成後、バインドを含む要素は代替テキストにテンプレートを記録する（`sf-bind:{…}`）。表のセルは行・列で固定する。図形の短い文字列（6文字未満）は、図形のテキスト全体と一致するときだけ記録する。スピーカーノートは値を埋めるが同期の対象外。

## 3. 同期

```bash
.venv/bin/python scripts/snapshot_version.py <deck>      # 既に使われているデッキ
.venv/bin/python scripts/sync_deck.py <deck> --dry-run   # ページごとに 旧 → 新
.venv/bin/python scripts/sync_deck.py <deck>
```

新しい値を古い値の直後に挿入してから古い値を消すので、書式は古い値のものを引き継ぐ。周りの文字列、オブジェクト ID、コメントはそのまま残る。手で書き換えられた箇所は報告して触らない。リンクグラフは `refreshSheetsChart` で更新する。

## 制約

- 数値はその場で変わるが、レイアウトは組み直さない。値が大きく長くなる（`9名` → `120名`）と枠からあふれることがある。変化が大きいときはページを再生成する（`build_deck.py --into <deck> --update-slides N`）。
- Slides API にはリンク付きのテキスト・表がない。同期は代替テキストの記録で成り立っているので、バインドした要素を削除・打ち直すと同期の対象から外れる。
- リンクグラフは PPTX に書き出すと静止画になる（`pptx-export` 参照）。
