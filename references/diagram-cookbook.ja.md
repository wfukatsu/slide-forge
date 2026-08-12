*[English](diagram-cookbook.md)*
# 図のレシピ

`d` は `diagrams.Canvas`。座標はインチ。ここに載せたパターンは 55 枚の図解デッキで
実際に使って、サムネイル確認まで通したもの。

## プリミティブ

`Canvas`（`scripts/diagrams.py`）:

| メソッド | 用途 |
|---|---|
| `shape(x, y, w, h, kind=, fill=, stroke=, text=, size=, bold=, color=, align=, valign=, line_spacing=)` | 図形。`fill=None` で塗りなし |
| `box(...)` | 角丸・淡い面・枠あり（既定の箱） |
| `solid(...)` | 塗りつぶし・太字（見出し用の箱） |
| `label(...)` | 枠も塗りもないテキスト |
| `band(...)` | 背景の帯 |
| `line(x1, y1, x2, y2, color=, weight=, dashed=, end_arrow=, start_arrow=)` | 直線 |
| `arrow(x1, y1, x2, y2, ...)` | 矢印（`end_arrow="FILL_ARROW"`） |
| `arrow_shape(x, y, w, h, ...)` | 太い矢印図形（工程の流れ） |
| `cards(x, y, w, h, items, accent=)` | 横並びカード。`items` は `(見出し, 本文)` |
| `flow(x, y, w, h, steps)` | 左→右の工程フロー（矢印つき） |
| `hbars(x, y, w, rows)` | 横棒グラフ。`rows` は `(ラベル, 数値, 表示文字列)` |
| `metric(x, y, w, h, value, caption)` | 大きな数値＋説明 |

`deckkit` の複合パーツ:

| 関数 | 用途 |
|---|---|
| `zone(d, x, y, w, h, label)` | 要素をまとめる領域。中身は `y+0.34` 以降 |
| `banner(d, y, text, tone=)` | 全幅の注意書き。`tone` は info/good/warn/bad |
| `layers(d, x, y, w, items)` | 水平レイヤー図。`items` は `(名前, 説明, 色)` |
| `steps_v(d, x, y, w, items)` | 番号付き縦フロー |
| `grid(d, x, y, w, cols, rows, cell_colors=)` | 表。セルごとに配色可 |
| `pills(d, x, y, w, items, per_row=)` | チップの格子 |
| `kv_rows(d, x, y, w, items)` | 「項目 → 補足」の2列リスト |
| `db(d, x, y, w, h, name, sub=)` | DB の円柱＋ラベル |
| `xmark(d, cx, cy)` / `checkmark(d, cx, cy)` | 丸バツ・丸チェック（中心座標） |
| `caption(d, x, y, w, text)` | 図に添える小さな説明 |
| `foot(d, points, edition)` | 下部の要点行・補足行 |

配色は `d.P`（`Palette`）。テンプレートの `colors` から作られる。

| 用途 | 使う色 |
|---|---|
| 自社製品・主要コンポーネント | `d.P.primary` |
| 強調・最上位 | `d.P.primaryDark` |
| 良い状態・After・可 | `d.P.success` |
| 問題・Before・不可 | `d.P.danger` |
| 副系統・別カテゴリ | `d.P.info` |
| 注意・条件付き | `d.P.warning` |
| 本文・補足 | `d.P.text` / `d.P.muted` |

明度調整は `lighten(色, 0〜1)` / `darken(色, 0〜1)`。塗りの上の文字色は
`readable_on(背景色)` でコントラストの高い方を選べる。

**1 スライド最大 3 色**に抑える。色を増やすと意味が読めなくなる。


## パターン早見表

「何を伝えたいか」から関数を選ぶ。すべて**戻り値は描画領域の下端 y**。
次のブロックはその値を起点に置くこと（手で y を計算しない）。

| 伝えたいこと | 関数 |
|---|---|
| 現状 → 解決後、A / B、推奨と非推奨 | `compare_panels(d, x, y, w, h, left, right)` |
| 誰が何をするか（担当をまたぐ流れ） | `swimlane(d, x, y, w, lanes, steps)` |
| 時系列・期間・重要な時点 | `timeline(d, x, y, w, marks, bands=…)` |
| 工程の流れ（担当範囲を強調） | `pipeline(d, x, y, w, steps, highlight=…)` |
| 番号つきの手順（縦） | `steps_v(d, x, y, w, items)` |
| 責務の階層 | `layers(d, x, y, w, items)` |
| 親子関係・構造 | `tree(d, x, y, w, nodes)` |
| 土台 → 応用（成熟度） | `pyramid(d, x, y, w, h, levels)` |
| 母数 → 結果（絞り込み） | `funnel(d, x, y, w, h, stages)` |
| 閉じた繰り返し（PDCA） | `cycle(d, x, y, w, h, steps)` |
| 条件分岐と帰結 | `decision(d, x, y, w, question, branches)` |
| 優先度・打ち手の4象限 | `quadrant(d, x, y, w, h, quads, x_label=…, y_label=…)` |
| 2軸上の位置づけ（競合比較） | `matrix_map(d, x, y, w, h, items, x_label=…, y_label=…)` |
| フェーズ × レーンの計画 | `roadmap(d, x, y, w, phases, lanes)` |
| 中央の対象への番号つき注釈 | `callouts(d, x, y, w, h, center, notes)` |
| 対応表・可否 | `grid(d, x, y, w, cols, rows, cell_colors=…)` |
| 順序のない列挙 | `pills(d, x, y, w, items, per_row=…)` |
| 項目 → 補足の2列 | `kv_rows(d, x, y, w, items)` |
| 状態つきの確認項目 | `checklist(d, x, y, w, items)` |
| 大きな数値（出典がある場合のみ） | `stats(d, x, y, w, items)` |
| 色の意味 | `legend(d, x, y, w, items)` |
| 3〜4項目の並列説明 | `Canvas.cards(x, y, w, h, items)` |
| データの所在 | `db(d, x, y, w, h, name, sub=…)` |
| 領域のグループ化 | `zone(d, x, y, w, h, label)` |
| 全幅の注意書き・要約 | `banner(d, y, text, tone=…)` |

`tone` は `primary` / `info` / `good` / `warn` / `bad` / `muted` / `accent`。
配色は `tone_colors(d, tone)` が (塗り, 枠, 文字色)、`tone_solid(d, tone)` が濃い単色を返す。

実際の描画例は `examples/pattern-gallery/deck.py` と、生成したギャラリーのスライドを見る。

## コネクタ（矢印・線）

**図形どうしを結ぶときに座標を手で書かない。** 端点がずれていても Slides API は
エラーにしないため、生成してサムネイルを見るまで気づけない。

| 用途 | 書き方 |
|---|---|
| 図形 A → 図形 B（追従してほしい） | `d.connect(a, b)` |
| 図形 A → 図形 B（辺にぴたりと合わせたい） | `d.link(a, b)` |
| 図形の辺の一点が欲しい | `d.edge_point(a, (tx, ty), gap=0.04)` |
| 軸・目盛り・引き出し線（接しないのが正しい） | `d.line(..., free=True)` |

```python
a = d.shape(1.0, 1.0, 1.6, 0.6, text="A")     # shape() は objectId を返す
b = d.shape(4.0, 2.0, 1.6, 0.6, text="B")

d.connect(a, b)                    # API のコネクタ。図形に紐づき、動かすと追従する
d.link(a, b, gap=0.04)             # 中心を結ぶ線と辺の交点を端点にする
d.connect(a, b, category="BENT")   # エルボー。1対多のファンアウトで経路が交差しにくい
```

- `connect()` … `startConnection` / `endConnection` で図形に**本当に接続**する。
  接続サイトは位置関係から自動で決まる（0=上 1=左 2=下 3=右）。上下左右の 4 点に
  スナップするため、真横・真上下の関係にきれいに効く。
- `link()` … 中心どうしを結ぶ直線と辺の交点を計算する。斜めの位置関係でも
  端点がぴたりと辺に乗る。スナップさせたくないときはこちら。
- `d.line()` / `d.arrow()` … 座標直指定。経路の折れ点や軸など、図形に接続しない線に使う。
  この場合は `free=True` を付けて意図を明示する（付けないと検査で落ちる）。

検査器は全コネクタの端点を調べ、**どの図形からも 0.22in 以上離れている**もの、
**図形の内部に 0.06in 以上埋まっている**ものを報告する。ゾーンのような大きな容器と
テキストボックスは判定から外れる（矢印が容器の中を通るのは正常なため）。


## 積み方の約束

```python
b = layers(d, X0, DY0, W, [...])           # b は下端 y
b = grid(d, X0, b + 0.24, W, cols, rows)   # 前のブロックの下から置く
b = pills(d, X0, b + 0.20, W, items)
banner(d, b + 0.20, "まとめの一行", tone="good")
foot(d, ["・持ち帰ってほしい1行"])
```

手で `DY0 + 2.7` のような値を書くと、内容が増えたときに下のブロックへ潜り込む。
戻り値を使って積めば、この事故は構造的に起きない。

検査器は重なりも検出するが、**検出は最後の砦であって設計ではない**。
戻り値で積むのが本筋で、検査はその取りこぼしを拾うためにある。

`Canvas` の `cards` / `flow` / `hbars` / `metric` も下端 y を返すので、
同じように積める。

## パターン別のメモ

- `compare_panels` … 左右で同じ構造にする。差分だけが目に入る。
- `swimlane` … `steps` の第3要素がレーン index。矢印は実座標を結ぶので、
  レーンをまたいでも経路が正しい。
- `timeline` … 位置は 0.0〜1.0 の比率。補足は**マーカーのラベルに持たせる**。
  別ラベル＋縦矢印にすると、他のマーカーの説明文や下のブロックに重なる。
- `cycle` … 矩形に内接させる。半径は箱がはみ出さないよう自動で決まる。
  ステップは 4〜6 個。
- `quadrant` / `matrix_map` … **軸ラベルを必ず入れる**。軸のない 2×2 は解釈できない。
  `matrix_map` の配置は主張そのものなので、根拠を示せないなら使わない。
  `y_label` は縦に積まれて描かれるため 2〜4 文字にする。
- `pyramid` / `funnel` … 横に余白があれば説明を横に、なければ段の中に入れる。
  説明が消えることはない。段は 5 つまで。
- `callouts` … 注釈は片側 3 個まで。中央の箱は内容に合わせた高さで上下中央に置かれる。
- `decision` … 分岐は 2〜3 個。菱形の文字は図形に直接入れず別ラベルを重ねている
  （直接入れると端が切れる）。
- `stats` … **出典のある数値にだけ使う。** 推測値を大きく見せてはいけない。
- `legend` … 凡例の色は図形と同じ塗りを出す。`tone` 名をそのまま渡せる。
- `checklist` … 色だけでなく記号（✓ □ !）も併用しているので、モノクロでも読める。

---

## 手で組む場合のレシピ

関数になっていない図（構成図など）や、パターンを組み合わせる場合の例。

### Before / After の 2 パネル対比（compare_panels の中身）

課題 → 解決を示す。最も効く図。

```python
pw = (W - 0.5) / 2
zone(d, X0, DY0, pw, 3.30, "現状：個別に実装",
     stroke=lighten(d.P.danger, 0.6), fill="#FEF7F8")
# ... 左パネルの中身 ...
xmark(d, X0 + pw / 2, DY0 + 1.24)          # 問題箇所に印

d.arrow_shape(X0 + pw + 0.02, DY0 + 1.30, 0.46, 0.5,
              fill=lighten(d.P.primary, 0.7))   # 中央の太矢印

rx = X0 + pw + 0.5
zone(d, rx, DY0, pw, 3.30, "導入後：横断で1回だけ",
     stroke=lighten(d.P.success, 0.5), fill="#F6FCF4")
# ... 右パネルの中身 ...
checkmark(d, rx + pw - 0.30, DY0 + 1.24)
```

左右で**同じ構造・同じ位置**に要素を置く。差分だけが目に入る。

## 2. レイヤー図（階層・責務）

```python
layers(d, X0, DY0, W, [
    ("アプリ",  "業務アプリケーション",       lighten(d.P.primary, 0.3)),
    ("サーバ",  "SQL / 認証認可 / 暗号化",     d.P.primary),
    ("基盤",    "トランザクション管理",        d.P.primaryDark),
])
```

上から下へ「利用する側 → される側」。手描きで層を分けるなら、下位ほど濃くする。

## 3. 工程フロー

横（4 段以内）:

```python
d.flow(X0, DY0 + 0.4, W, 0.8, ["調査", "設計", "実装", "検証"])
```

縦（説明を付けたい場合）:

```python
steps_v(d, X0, DY0, 4.2, [
    ("構成を決める", "DB / ノード数 / 配置"),
    ("設定を変える", "分離レベル・最適化"),
    ("測る",        "ベンチマークを実行"),
])
```

ループにするなら、戻りの矢印は**列間の余白を通るエルボー**（3 本の線）で引く。
本文の上を横切らせない。

```python
xg = X0 + 4.2 + 0.20                       # 列間の余白
d.line(X0 + 3.6, DY0 + 2.36, xg, DY0 + 2.36, color=d.P.primary, dashed=True)
d.line(xg, DY0 + 0.31, xg, DY0 + 2.36,      color=d.P.primary, dashed=True)
d.arrow(xg, DY0 + 0.31, X0 + 4.4, DY0 + 0.31, color=d.P.primary)
```

## 4. スイムレーン（誰が何をするか）

**レーンをまたぐ矢印は、始点と終点の実座標を結ぶ。** 水平に引くと経路が嘘になる。

```python
LX, LW = X0, 1.30                # レーン名の列
CX, CW = X0 + LW + 0.10, XE - (X0 + LW + 0.10)
LH = 1.08
y_a = DY0 + 0.30                 # レーン A
y_b = y_a + LH + 0.34            # レーン B

for ly, nm, col in [(y_a, "レコード", lighten(d.P.primary, 0.5)),
                    (y_b, "台帳",     d.P.primary)]:
    d.shape(LX, ly, LW, LH, kind="ROUND_RECTANGLE", fill=col, stroke=None,
            text=nm, size=9, bold=True, color="#FFFFFF")
    d.shape(CX, ly, CW, LH, kind="ROUND_RECTANGLE",
            fill=lighten(col, 0.94), stroke=lighten(col, 0.78))

# 各ステップの箱を、属するレーンの y に置く
centers = []                     # (左端, 右端, 中心y) を覚えておく
for i, (nm, lane_y) in enumerate([("1. 準備", y_a), ("2. 確定", y_b), ("3. 反映", y_a)]):
    bx = CX + 0.12 + i * 2.4
    d.shape(bx, lane_y + 0.12, 2.2, LH - 0.24, kind="ROUND_RECTANGLE",
            fill=lighten(d.P.primary, 0.78), stroke=None, text=nm, size=9, bold=True)
    centers.append((bx, bx + 2.2, lane_y + LH / 2))

for i in range(len(centers) - 1):
    _, x_end, y1 = centers[i]
    x_start, _, y2 = centers[i + 1]
    d.arrow(x_end + 0.03, y1, x_start - 0.03, y2, color=d.P.primary, weight=1.6)
```

## 5. 条件分岐

```python
cx = X0 + 3.15                                     # フローの中心線
d.shape(cx - 1.85, y, 3.70, 0.74, kind="DIAMOND",
        fill=lighten(d.P.warning, 0.68), stroke=None)
d.label(cx - 1.55, y + 0.18, 3.10, 0.42, "条件を満たすか？",
        size=8.5, bold=True, align="CENTER", color=darken(d.P.warning, 0.55))

# No は右下へ（右にパネルがあるなら、その手前で止める）
d.arrow(cx + 1.86, y + 0.37, cx + 1.30 + 0.62, y2 - 0.02, color=d.P.muted)
d.label(cx + 1.72, y + 0.44, 0.50, 0.20, "No", size=8, align="START")
# Yes は真下へ
d.arrow(cx, y + 0.76, cx, y2 - 0.02, color=d.P.primary, weight=1.6)
d.label(cx + 0.06, y + 0.80, 0.50, 0.20, "Yes", size=8, align="START")
```

菱形の中の文字は `DIAMOND` に直接入れると端が切れる。**別の `label` で重ねる。**
分岐ラベル（Yes/No）と結果ラベルは、矢印の経路を避けて `align` で外側へ寄せる。

## 6. 対応表・可否マトリクス

```python
def cc(i, j, cell):
    if j == 0:
        return None
    if cell == "●":
        return (lighten(d.P.success, 0.80), darken(d.P.success, 0.45))
    if cell == "○":
        return (lighten(d.P.warning, 0.70), darken(d.P.warning, 0.55))
    return (None, lighten(d.P.muted, 0.45))

grid(d, X0, DY0, W,
     ["機能", "Community", "Standard", "Premium", "提供状況"],
     [["トランザクション", "●", "●", "●", "GA"],
      ["クラスタリング",   "−", "●", "●", "GA"],
      ["SQL",             "−", "−", "●", "GA"]],
     col_w=[3.20, 1.30, 1.40, 1.35, 1.75], row_h=0.255, cell_colors=cc)
```

凡例（`●`＝提供、`○`＝プレビュー、`−`＝非提供）を表の下に小さく添える。

## 7. 構成図（コンポーネントと通信）

```python
# 3 列構成：クライアント / 中核 / データ
cw = 1.30
for i in range(3):
    d.shape(X0, DY0 + 0.20 + i * 0.44, cw, 0.36, kind="ROUND_RECTANGLE",
            fill=lighten(d.P.primary, 0.86), stroke=lighten(d.P.primary, 0.6),
            text=f"Client {i+1}", size=8)

kx, kw = X0 + cw + 0.40, 5.20
zone(d, kx, DY0, kw, 1.86, "サーバ群")
# ... ノードを並べる ...

dx = kx + kw + 0.40
for i, nm in enumerate(["MySQL", "Cassandra", "DynamoDB"]):
    d.shape(dx, DY0 + 0.20 + i * 0.44, XE - dx, 0.36, kind="ROUND_RECTANGLE",
            fill="#FFFFFF", stroke=lighten(d.P.muted, 0.35), text=nm, size=8)
```

**右端のパネルに 1.5in 未満の幅しか残らないなら、そこに文章を置かない。**
下段の全幅カード（`zone` を 2 つ横並び）に移す。狭いパネルは必ず溢れる。

## 8. RAG / パイプライン（一部だけ自社領域）

```python
steps = ["文書", "ベクトル化", "ストアに保存", "類似検索", "LLM が回答"]
sw = (W - 0.28 - 0.30 * 4) / 5
for i, s in enumerate(steps):
    sx = X0 + 0.14 + i * (sw + 0.30)
    own = i in (1, 2, 3)                    # 自社が担う範囲
    d.shape(sx, DY0 + 0.38, sw, 0.80, kind="ROUND_RECTANGLE",
            fill=d.P.primary if own else lighten(d.P.muted, 0.88),
            stroke=None if own else lighten(d.P.muted, 0.5),
            text=s, size=8.5, bold=own,
            color="#FFFFFF" if own else d.P.text, line_spacing=110)
    if i < len(steps) - 1:
        d.arrow(sx + sw + 0.03, DY0 + 0.78, sx + sw + 0.27, DY0 + 0.78,
                color=d.P.primary, weight=1.5)
d.label(X0 + 0.14 + sw + 0.30, DY0 + 1.20, sw * 3 + 0.60, 0.20,
        "この範囲を担う", size=8, bold=True, align="CENTER", color=d.P.primaryDark)
```

## 9. タイムライン（期間と復旧ポイント）

```python
tl_y = DY0 + 0.78
d.line(X0 + 0.30, tl_y, XE - 0.30, tl_y, color=lighten(d.P.muted, 0.3), weight=1.5)
for mx, label, col in [(0.55, "通常運転", lighten(d.P.muted, 0.2)),
                       (2.40, "停止開始", d.P.warning),
                       (6.30, "復帰",     d.P.primary)]:
    d.shape(X0 + mx, tl_y - 0.09, 0.18, 0.18, kind="ELLIPSE", fill=col, stroke=None)
    d.label(X0 + mx - 0.75, tl_y + 0.16, 1.70, 0.46, label, size=7.5, bold=True,
            align="CENTER", color=darken(col, 0.35))

d.shape(X0 + 2.49, tl_y - 0.34, 3.90, 0.24, kind="ROUND_RECTANGLE",
        fill=lighten(d.P.success, 0.80), stroke=None,
        text="この期間に取得", size=7.5, bold=True, color=darken(d.P.success, 0.45))
mid = X0 + 2.49 + 3.90 / 2
d.arrow(mid, tl_y + 0.72, mid, tl_y + 0.16, color=d.P.danger, weight=1.6)
```

## 10. 階層ツリー（インデント式）

```python
levels = [("カタログ", "最上位", d.P.primaryDark),
          ("データソース", "個々の DB", d.P.primary),
          ("名前空間", "schema / keyspace", lighten(d.P.primary, 0.35)),
          ("テーブル", "実体", lighten(d.P.primary, 0.60))]
for i, (nm, sub, col) in enumerate(levels):
    iy, ind = DY0 + 0.36 + i * 0.56, i * 0.22
    d.shape(X0 + 0.16 + ind, iy, 1.30, 0.32, kind="ROUND_RECTANGLE", fill=col,
            stroke=None, text=nm, size=8.5, bold=True, color="#FFFFFF")
    d.label(X0 + 1.54 + ind, iy + 0.04, 2.4 - ind, 0.26, sub, size=7.5, align="START")
    if i < len(levels) - 1:                      # かぎ線でつなぐ
        d.line(X0 + 0.30 + ind, iy + 0.33, X0 + 0.30 + ind, iy + 0.55, color=d.P.muted)
        d.line(X0 + 0.30 + ind, iy + 0.55, X0 + 0.58 + ind, iy + 0.55, color=d.P.muted)
```

---

## 使える図形

`RECTANGLE` `ROUND_RECTANGLE` `ELLIPSE` `TEXT_BOX` `DIAMOND` `CAN`（円柱＝DB）
`CLOUD` `HEXAGON` `CHEVRON` `PENTAGON` `PARALLELOGRAM` `TRAPEZOID` `PLAQUE`
`FOLDED_CORNER` `ARC` `DONUT` `STAR_5` `HOME_PLATE` `RIGHT_ARROW` `LEFT_RIGHT_ARROW`
`UP_ARROW` `DOWN_ARROW` `BENT_ARROW` `CURVED_RIGHT_ARROW` `NOTCHED_RIGHT_ARROW`
`FLOW_CHART_MAGNETIC_DISK` `WEDGE_ROUND_RECTANGLE_CALLOUT`

## やってはいけないこと

- **出典のない数値をグラフにする。** `hbars` / `metric` は実測値か公表値だけに使う。
  無い場合は「変えるべき変数」など構造を図にする。
- **レーンをまたぐ矢印を水平に引く。** 経路が嘘になる。
- **0.12in 未満の矢印。** 描画されず点のように見える。
- **マスター由来のロゴ・フッターを自分で描く。** 二重になる。
- **全面サイズの不透明な矩形。** マスターのフッターを覆って消す。
- **狭いパネル（1.5in 未満）に文章を置く。** 必ず溢れる。
- **1 スライドに 4 色以上。** 色の意味が読めなくなる。
