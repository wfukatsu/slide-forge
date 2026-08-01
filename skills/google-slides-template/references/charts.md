# 表とグラフ（charts.py）

`diagrams.Canvas` に混ざっている `ChartMixin` の使い方。表は Slides ネイティブの
テーブル、グラフは図形で描く（円グラフだけ SVG → PNG の画像）。座標はインチ、
戻り値はすべて描画領域の下端 y。

```python
from diagrams import Canvas
ref = deck.add_slide("TITLE_ONLY", title="…")
d = Canvas(deck, ref["slideId"], template)

b = d.table(0.5, 1.2, 9.0, ["項目", "従来", "提案"],
            [["構築期間", "6ヶ月", "2ヶ月"], ["運用工数", "3人月", "0.5人月"]])
b = d.vbars(0.5, b + 0.3, 6.0, 3.0, [("2023", 120), ("2024", 210), ("2025", 380)])
```

デッキ仕様（JSON）の `figures` からも同名の type で使える。実例は
`examples/charts-demo.json`（6 種のうち `vbars_stacked` を除く 5 種の動くデモ。
`vbars_stacked` は `examples/patterns-demo.json` にある）。

## どれを使うか

| 見せたいもの | 使うもの | 補足 |
|---|---|---|
| 数値・仕様の正確な比較 | `table` | 生成後にユーザーが編集できる |
| 量の比較（カテゴリ間） | `vbars` / `hbars`(diagrams) | 項目名が長ければ横棒 |
| 量の比較 × 系列（例: 従来 vs 提案） | `vbars_grouped` | 系列 2〜3 まで |
| 合計の推移 × 内訳（例: コスト構成） | `vbars_stacked` | 系列 4 まで。内訳の比較が主なら grouped |
| 時間の変化・傾向 | `linechart` | 複数系列可。**二重軸は作れない**（仕様） |
| 全体に占める構成比 | `pie` | 系列 6 まで。それ以上は「その他」に畳む |
| 1 つの数字を大きく | `metric`(diagrams) | グラフにしない方が強い |

## 共通の設計規約

- **棒の基線はゼロ固定**。負値や途中からの軸は `ValueError`（変化の誇張を防ぐ）。
  折れ線だけ `y_min` / `y_max` を動かせる。
- **系列色は `Palette.series()` の固定順**: 青 → 緑 → 水色 → 赤 → 暗黄。
  この順は色覚多様性の検証（隣接ペアの CVD ΔE ≥ 9.2）を通してある。
  並べ替え・循環はしない。単一系列の棒は primary 一色。
- **文字は本文色**（text / muted）。系列の識別は凡例の色見本が担う。
- 緑と暗黄は白背景とのコントラストが 3:1 未満なので、**凡例と数値の直接
  ラベルを消さないこと**（既定で付く）。
- 出典のある数値にだけ使う。飾りでグラフを置かない。
- 図形ベース（表・棒・折れ線）は `audit_bounds` / `audit_overlaps` /
  `audit_text_fit` と `--dry-run` がそのまま効く。**生成前に必ず通すこと。**

## table — 表

```python
d.table(x, y, w, headers, rows,
        col_widths=None,   # 列幅の比率。例 [2, 1, 1]。省略で等分
        row_h=0.34,        # 最小行高（文字が折り返すと伸びる）
        header_h=0.38,
        size=10, header_size=None,
        aligns=None,       # 列ごとの寄せ。省略で 1 列目 START、残り CENTER
        header_fill=None,  # 見出し行の塗り（既定 primary。文字色は自動）
        zebra=True,        # 偶数行に薄い縞
        border=None)       # 罫線色（既定 border）
```

- Slides ネイティブのテーブルなので**生成後にユーザーが編集できる**（図形で
  組んだ疑似表との一番の違い）。
- `row_h` は最小値。セル内で文字が折り返すと行が伸び、戻り値の下端 y より
  実物が下がる。セルの文字量は `audit_text_fit()` が生成前に検査する。
- 行数が多い表は文字を小さくするより**スライドを分ける**。

## vbars — 縦棒

```python
d.vbars(x, y, w, h, items,      # items: (ラベル, 数値) or (ラベル, 数値, 表示文字列)
        max_value=None,          # 軸の上限（既定はきりのよい数へ切り上げ）
        colors=None,             # 塗り分けは意図があるときだけ（例: 1 本だけ強調）
        unit="",                 # 表示文字列を省略したときの単位（"h" "件" 等）
        bar_ratio=0.62)          # セル幅に対する棒の太さ
```

数値は各棒の上に直接ラベルされる。時系列でも点が 3〜4 個なら折れ線より
縦棒が読みやすい。

## vbars_grouped — グループ縦棒

```python
d.vbars_grouped(x, y, w, h, categories, series,
                # categories: 横軸のラベル ["Q1", "Q2", …]
                # series: [(系列名, [値, …]), …] 値の数は categories と同数
                unit="", legend=True, values=True)
```

系列は 2〜3 まで。4 系列を超えるなら表かグラフの分割を検討する。

## vbars_stacked — 積み上げ縦棒

```python
d.vbars_stacked(x, y, w, h, categories, series,
                # categories: 横軸のラベル ["2024", "2025", …]
                # series: [(系列名, [値, …]), …] 下から最初の系列を積む
                unit="",
                values=False,   # セグメント中央の数値（入る高さの段だけ描く）
                totals=True,    # 合計を棒の上に直接ラベル
                legend=True)
```

- 「合計の推移」と「内訳の構成」を同時に見せる図。**内訳の系列間比較が主目的なら
  `vbars_grouped` を使う**（積み上げは基線が揃わず段の増減を読み違えやすい）。
- 系列は 4 まで。超えるなら「その他」に畳んでから渡す。
- 軸目盛りを描かないので上限は最大合計の 1.05 倍（`_nice_ceil` の切り上げで
  上半分が空くのを避けるため）。`max_value` で明示もできる。

## linechart — 折れ線

```python
d.linechart(x, y, w, h, labels, series,
            # labels: 横軸 ["1月", "2月", …] / series: [(系列名, [値, …]), …]
            y_min=0, y_max=None,  # 省略時は目盛りが丸い数字になるよう自動
            grid=4,               # 横グリッドの分割数
            unit="",              # 最上段の目盛りにだけ付く（"ms" 等）
            markers=True,
            end_values=False,     # 各系列の最後の点にだけ数値を添える
            axis_w=0.6)           # 目盛り列の幅。長い目盛りは自動で広がる
```

- **軸は 1 本**。スケールの違う 2 つの量（件数と金額など）を 1 枚に重ねる
  API は意図的に無い。グラフを 2 つ並べるか、基準を揃えて指数化する。
- 全点に数値ラベルは付けない（`end_values` で終端だけ）。

## pie — 円 / ドーナツ

```python
d.pie(x, y, size, items,        # items: [(ラベル, 数値), …]。size は直径（インチ）
      donut=True,
      unit="",                   # 付けると凡例が「名前 62件（62%）」形式になる
      legend_w=2.4,              # 右側の凡例の幅
      bg="#FFFFFF")              # ドーナツの穴と切れ目の色。白背景以外では合わせる
```

- Slides API には角度を指定できる扇形が無いため、円の部分だけ SVG を PNG に
  焼いて貼る（cairosvg か rsvg-convert が必要。アイコンと同じ経路）。
  `--dry-run` では同じ大きさの円形プレースホルダに置き換えて座標だけ検査する。
- 凡例は右側に図形で描くので文字の検査は通常どおり効く。
- 12 時から時計回りに、**渡した順**で描く（勝手に並べ替えない）。
- 系列が 7 つ以上なら警告が出る。「その他」に畳むか棒グラフへ。

## デッキ仕様（JSON）から使う

```json
{ "layout": "TITLE_ONLY", "title": "アクションタイトル",
  "figures": [
    { "type": "table", "x": 0.5, "y": 1.2, "w": 9.0,
      "headers": ["項目", "従来", "提案"],
      "rows": [["構築期間", "6ヶ月", "2ヶ月"]],
      "colWidths": [1.4, 2, 2], "rowH": 0.5 },
    { "type": "vbars", "x": 1.2, "y": 1.3, "w": 5.4, "h": 3.4,
      "items": [["2023", 120], ["2024", 210], ["2025", 380]] },
    { "type": "vbars_grouped", "x": 0.7, "y": 1.25, "w": 8.6, "h": 3.5,
      "categories": ["Q1", "Q2"],
      "series": [["従来", [40, 42]], ["提案", [18, 12]]], "unit": "h" },
    { "type": "linechart", "x": 0.6, "y": 1.25, "w": 8.8, "h": 3.5,
      "labels": ["1月", "2月", "3月"],
      "series": [["p95", [320, 240, 90]]], "unit": "ms", "endValues": true },
    { "type": "pie", "x": 1.2, "y": 1.35, "size": 3.2,
      "items": [["移行済み", 62], ["移行中", 23], ["未着手", 15]] }
  ] }
```

キーは snake_case でも camelCase でもよい（`colWidths` → `col_widths`）。

## 落とし穴

- **表の実高は伸びる。** `row_h` は最小値。下に別の部品を置くときは戻り値の
  下端 y に余裕を足すか、セルの文字量を `--dry-run` の検査で先に潰す。
- **円グラフは画像なので生成後に Slides 上で編集できない。** 数値を直したい
  ときは仕様を直して作り直す（このスキルの流儀どおり）。
- **`vbars` の `h` には数値ラベル（0.24in）とカテゴリラベル（0.30in）が
  含まれる。** プロット部だけの高さではない。h < 0.94 だとエラーになる。
- 折れ線の目盛り幅（`axis_w`）は目盛り文字列から自動で広がるが、その分
  プロットが狭くなる。桁の大きい値は `unit` で単位を外に出して桁を減らす
  （例: 12,000ms → 12s、3,400万円 → 単位を「百万円」に）。
