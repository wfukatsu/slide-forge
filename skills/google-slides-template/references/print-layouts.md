# 印刷物用デッキの型（mckinsey.py）

`diagrams.Canvas` に混ざっている `McKinseyMixin` の使い方。マッキンゼー流の
コンサルティング資料の作法を部品にしたもので、**読者が独りで読み切る資料**
（配布・提出・稟議）で使う。登壇用デッキ（1 枚 1 メッセージ・文字少なめ）には
使わない——設計思想が逆向きで、混ぜるとどちらの良さも消える。

デッキ仕様（JSON）の `figures` からも同名の type で使える。実例は
`examples/print-deck-catalog.json`（全 10 部品＋アンチパターンを使った 30 枚の動くデモ。
そのまま複製して自分の題材に置き換える出発点になる）。

## 設計の根拠（2026-08 調査）

出典: [Deckary: Consulting Slide Standards](https://deckary.com/blog/consulting-slide-standards)、
[Slideworks: Action Titles](https://slideworks.io/resources/how-to-write-action-titles-like-mckinsey)、
[A1 Slides: McKinsey Presentation Framework](https://a1slides.com/mckinsey-presentation-framework/)、
[Analyst Academy: Takeaway Boxes](https://www.theanalystacademy.com/takeaway-boxes-when-to-use/)

- **アクションタイトルは 15 語（全角 40 字/行）以内・2 行まで・能動態。**
  「何を見せるか」ではなく「何が言えるか」。タイトルだけを順に読むと
  デッキ全体の論旨になる（横の論理）。
- **縦の論理**: タイトルと図は不可分。図を隠してタイトルだけ読んでも、
  タイトルを隠して図だけ見ても、同じ結論に着地しなければならない。
- **数値の主張には必ず出典行。** 1 つでも出どころ不明の数字があると全体が疑われる。
- **示唆ボックス（kicker）は 2 割以下。** タイトルの焼き直し・図に無い新情報は書かない。
- **ピラミッド原則**: 結論を先に（エグゼクティブサマリー）、根拠は MECE に分解。
- **ゴーストデッキ**: 清書の前に骨子（タイトル・図表の当て・データの状態）で
  論旨を検証する。

## どれを使うか

| 見せたいもの | 使うもの | 補足 |
|---|---|---|
| 結論を先に置く 1 枚 | `exec_summary` | SCR（状況→課題→答え）。冒頭専用 |
| タイトルの連なり＝論旨 | `storyline` | 設計の検証・目次・章扉に |
| 清書前の骨子 | `ghost` | データ状態（確定/作成中/未取得）つき |
| 論点の分解 | `mece_tree` | 横方向のロジックツリー。体制図は `orgchart` |
| BLANK で組むタイトル | `governing_message` | TITLE プレースホルダがあるならそちら |
| 図の読み方の導入 | `lead_in` | タイトル直下 1〜2 行 |
| 図の非自明な含意 | `so_what` | 使用は全体の 2 割以下 |
| 出典・注記 | `source_note` | 数値のある全スライドに必須 |
| 図表番号つきの枠 | `exhibit_frame` | 本文・付録から参照する図に |
| 増減の橋渡し | `waterfall` | 合計の不一致は ValueError |
| 案の比較（3 案×基準） | `rating_matrix` | ドット式。白黒印刷に耐える |

## ページの標準形（定量スライド）

```python
d = Canvas(deck, slide_id, template)
b = d.governing_message(0.5, 0.45, 9.0, "手作業コストは業界中央値の 2.4 倍")
b = d.lead_in(0.5, b + 0.06, 9.0, "同業 12 社の公開データと自社実績の比較。")
inner = d.exhibit_frame(0.5, b + 0.15, 5.9, 2.9, 1, "1 件あたり処理コスト")
d.vbars(inner[0] + 0.2, inner[1] + 0.1, inner[2] - 0.4, inner[3] - 0.2, [...])
d.so_what(6.6, b + 0.15, 2.9, 2.9, "差の大半は受付・照合に由来する")
d.source_note(0.5, 4.85, 9.0, "各社 IR 資料（2025 年度）",
              notes=["※1 間接費は含まない"])
```

積み上げ規約どおり各部品は下端 y を返す。**例外は `exhibit_frame` だけ**で、
中身を描くための内側領域 `(x, y, w, h)` を返す。JSON から使う場合は内側領域を
受け取れないため、枠だけ描いて中身は座標を手で合わせる（目安: x+0.2 / ヘッダー下 +0.45）。

## 部品ごとの要点

### governing_message — アクションタイトル

- 全角 40 字/行 × 2 行を超えると警告。テンプレートに TITLE があるレイアウトでは
  そちらを使い、この部品は BLANK で 1 枚を丸ごと組むときに使う。

### lead_in — 導入文

- 「この図を何のために見るか」を 1〜2 行。登壇用では口頭で言えばよいので不要。
- 高さは文字数から自動計算する（行送り 125% を織り込み済み）。

### so_what — 示唆ボックス

- `points` で箇条書きの補足を足せる。`accent` で色を変えられる（悪い例の赤など）。
- 書いてはいけないもの: タイトルの焼き直し／図に無い新情報／複数の主張。

### source_note — 出典・注記行

- `source` が空だと `ValueError`。**出典を書けない数字は載せない**を実装で強制。
- `notes` は「※1 …」形式の注記。出典より上に並ぶ。`prefix` で「根拠」等に変更可。

### exhibit_frame — 図表枠

- 番号は呼び出し側で通し管理する（部品は採番しない）。
- 1 枚 1 図で参照が発生しない資料には不要。

### mece_tree — ロジックツリー

- 深さ 4 超・1 列 1.1in 未満・葉が入らない高さは `ValueError`。
- 分解が MECE か（漏れなく・重複なく）は**描く側の責任**。部品は形しか保証しない。

### waterfall — ウォーターフォール

- `items` は `(ラベル, 値, "total"|"delta")`。先頭は `total` 必須。
- **最後の total が積算と合わないと `ValueError`**（データの取り違えを止める）。
- 合計=primary 青。増減の色は `good` で決める: `good="up"`（既定。売上・利益の橋、
  増加が緑）か `good="down"`（コスト・リードタイム削減の橋、減少が緑）。
  符号だけで塗るとコスト文脈で「削減＝赤」になり意味が逆転する。
- 基線ゼロ固定（負の領域は不可）。

### rating_matrix — 評価マトリクス

- 値は 0〜levels の整数。ハーヴェイボール（部分塗りの円）は Slides API に
  扇形が無く描けないため、**塗りドットの数**で表す。白黒印刷でも判別できる。
- 2 案の比較なら `before_after`（illustrations）で足りる。

### exec_summary — エグゼクティブサマリー

- `points`（答えを支える論点）は 5 個まで。それ以上に分かれるなら章立てを見直す。
- 「この 1 枚だけ読めば意思決定できる」が合格条件。

### storyline — 横の論理

- `titles` は文字列か `(ページ番号, タイトル)`。`highlight` で現在地を示せる。
- 成果物（目次・章扉）と設計の道具（論旨の検証）を兼ねる。

### ghost — ゴーストデッキ

- 状態は `confirmed`（緑）/ `wip`（黄）/ `missing`（赤）。
- **「未取得」が残ったまま清書に入らない**ためのチェックボードで、成果物ではない。

## アンチパターン（部品が止めるもの・人が見るもの）

| 失敗 | 検出 |
|---|---|
| 出典なしの数値 | `source_note` が空出典で `ValueError` |
| ウォーターフォールの合計不一致 | `waterfall` が `ValueError` |
| 棒グラフの基線ずらし | `charts` 側で禁止（`ValueError`） |
| 二重軸で相関を演出 | `linechart` は意図的に非対応 |
| 3 行タイトル | `governing_message` が警告 |
| 文字溢れ・重なり | `audit_text_fit` / `audit_overlaps`（`--dry-run --strict`） |
| タイトルがテーマだけ／1 枚 2 主張／示唆の乱用 | 機械検出不可。`examples/print-deck-catalog.json` のアンチパターン章を目安に人が見る |

## 落とし穴

- **`size` キーの意味が type で違う。** icon 系・pie ではインチ（空間量）、
  `table` などではフォント pt。仕様の検証はこの区別を織り込み済み。
- `exhibit_frame` を JSON から使うときの中身は手座標。ずれたら `--dry-run` の
  `audit_overlaps` が拾うので、警告を見てから直せばよい。
- ハーヴェイボール・角度指定の扇形は描けない（`pie` が画像なのと同じ制約）。
- 印刷は 1 枚ずつ横向きが前提。ページサイズは複製方式では変えられない
  （`references/api-notes.md` セクション 7）。A4 縦の紙面が必要なら
  このスキルの守備範囲外。
