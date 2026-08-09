# 図解を描く（diagrams.py と Canvas ファミリー）

`scripts/diagrams.py` の `Canvas` と、そこに混ざる各ファミリー（charts / illustrations /
patterns / icons / cloud_icons / images / code_block）の使い方・作図規約・自己点検。
テンプレートの `colors` から配色を組み立てるため、テーマから外れない。座標はインチ、
複合部品の戻り値は描画領域の下端 y。

```python
from diagrams import Canvas, lighten
ref = deck.add_slide("TITLE_ONLY", title="…")   # BODY を持たないレイアウトが図に向く
d = Canvas(deck, ref["slideId"], template)

d.flow(0.6, 1.0, 8.8, 0.8, ["Inner Loop", "Middle Loop", "Outer Loop"])   # 工程フロー
d.cards(0.5, 2.0, 9.0, 1.5, [("見出し", "本文"), ...])                      # 横並びカード
d.hbars(0.5, 3.6, 7.4, [("従来", 1220, "1,220h"), ("AI駆動", 56, "56h")])   # 横棒グラフ
d.metric(8.0, 3.6, 1.4, 1.0, "22x", "工数削減", color=d.P.success)          # 大きな数値
d.box(...) / d.solid(...) / d.label(...) / d.band(...) / d.arrow(...)       # 基本部品
```

9 つの手段（構造図・表グラフ・イメージ図・フレームワーク図・イベント案内・アイコン・
クラウドアイコン・画像・コードブロック）はすべて同じ `Canvas` のメソッドなので、
1 枚のスライドに混ぜて使える。
ファミリー別の詳細は `references/charts.md` / `references/patterns.md` /
`references/events.md` / `references/images.md` / `references/icons.md` /
`references/cloud-icons.md` / `references/code-blocks.md`、実例は
`examples/charts-demo.json` / `examples/patterns-demo.json` /
`examples/event-announcement.json` / `examples/illustration-gallery.json` /
`examples/icon-gallery.json` / `examples/cloud-architecture.json`。

## イメージ図・アイコン・画像

```python
d.icon_flow(0.5, 1.3, 9.0, [("person", "利用者"), ("server", "API"),
                            ("database", "台帳")], size=0.92)
d.asset_icon_flow(0.5, 2.6, 9.0, [("job-seeker", "求職者"), ("interview", "面接"),
                                  ("job-offer", "内定")])
d.pyramid(1.6, 2.4, 6.8, 2.4, ["経営指標", "業務指標", "システム指標"])
d.iceberg(0.5, 1.0, 9.0, 3.6, above=["画面の使い勝手"], below=["データモデル"])
d.image(0.6, 1.1, 4.2, 2.6, "assets/shot.png", fit="contain", caption="管理画面")
d.ai_image(5.2, 1.1, 4.2, 2.6, "夜間に自動でビルドが回っている様子")
```

ピクトグラムは 30 種（`person` `server` `database` `cloud` `lock` `shield` `bot` …）。
比喩図は `pyramid` / `funnel` / `venn` / `iceberg` / `balance` / `steps` / `layers` /
`hub` / `matrix` / `before_after` / `journey` / `timeline`。

ブランドのアイコンは `assets/scalar/pictograms/` に 62 種（`evidence-chain` `data-bank`
`public-key` `interview` `consent` …）。**「情報銀行」「証拠チェーン」「内定」の
ような業務語彙は `illustrations` では描けないので、こちらを使う。** 名前は slug でも
日本語名でも引ける。素材は単色なので、既定でテンプレートの主色に染まる。

```bash
.venv/bin/python scripts/icons.py --list          # 62 種を一覧
.venv/bin/python scripts/icons.py --search 情報銀行 # 日本語名・英語名・タグで探す
```

クラウドサービスのアイコン（AWS / Google Cloud / Azure の公式 1,757 種）は
`cloud_icon` 系。**名前は推測せず必ず検索して確かめる**（ファイル名は
`Arch_Amazon-EC2_64.svg` のような形で、勘で書くと必ず外れる）。
**色の変更・回転・反転は各社の利用条件で禁止**なので、引数自体を持たせていない。

```bash
.venv/bin/python scripts/cloud_icons.py --search s3            # 別名でも引ける
.venv/bin/python scripts/cloud_icons.py --list --vendor aws --category groups
```

```python
d.cloud_zone(0.45, 1.05, 9.1, 2.5, vendor="aws", title="AWS  ap-northeast-1")
d.cloud_icon_row(1.0, 1.9, 8.0, [("aws:rds", "RDS"), ("aws:simple-storage-service", "S3")])
```

**迷ったら `illustrations`。** AI 生成は表現力が高い代わりに、課金済みの
`GEMINI_API_KEY` が要る（画像モデルは無料枠のクォータが 0）。図形で描くほうは
オフラインで動き、テンプレートの配色に必ず従い、何度作り直しても同じ絵になる。

**回転した図形に文字を入れてはいけない。** 台形などを 180 度回して使うとき、
`text=` を渡すと文字も一緒に逆さまになる。図形は `text` 無しで描き、`label()` を
重ねること（`shape()` は 0/90/270 度以外の回転に文字を入れると警告する）。

デッキ仕様（JSON）からは `figures` で使える。`--dry-run` は API を呼ばずに
図を座標へ展開して検査する（`--strict` を併用すると警告 1 件でもエラー終了）。

```json
{ "layout": "TITLE_ONLY_PROPOSAL", "title": "…",
  "figures": [
    { "type": "icon_flow", "x": 0.5, "y": 1.3, "w": 9.0,
      "items": [["person", "利用者"], ["database", "台帳"]] },
    { "type": "asset_icon_flow", "x": 0.5, "y": 3.1, "w": 9.0,
      "items": [["personal-info", "個人情報"], ["data-bank", "情報銀行"]] }
  ] }
```

## 表・グラフ・コードブロック

表と本格的なグラフは `charts`（同じ Canvas に生えている。`references/charts.md`）。
表はネイティブテーブルなので生成後にユーザーが編集できる。棒・折れ線は基線ゼロ・
系列色固定（色覚検証済みの並び）・数値の直接ラベルという規約込みで描かれる。

```python
d.table(0.5, 1.2, 9.0, ["項目", "従来", "提案"], [["構築期間", "6ヶ月", "2ヶ月"]])
d.vbars(0.5, 1.2, 6.0, 3.2, [("2023", 120), ("2024", 210), ("2025", 380)])
d.vbars_grouped(0.5, 1.2, 9.0, 3.4, ["Q1", "Q2"],
                [("従来", [40, 42]), ("提案", [18, 12])], unit="h")
d.linechart(0.5, 1.2, 9.0, 3.2, ["1月", "2月", "3月"],
            [("p95", [320, 180, 90])], unit="ms")
d.pie(0.7, 1.3, 2.8, [("移行済み", 62), ("移行中", 23), ("未着手", 15)])
```

コードサンプルは `code_block`（`references/code-blocks.md`）。等幅 + ハイライト付き、
角は直角。高さは実効行高（`行数 × size × ls × 1.45 / 72 + 0.14in`）で見積もる。

```python
d.code_block(0.5, 1.0, 6.1, 2.9, code, lang="java")  # java/graphql/json/bash
```

## 図形を結ぶ線

**図形どうしを結ぶ線は座標で書かない。** `createLine` は座標をそのまま受け取るだけで
図形との位置関係を検証しないため、端点がずれていても API はエラーにしない。
「矢印が図形から浮いている / 枠に食い込んでいる」は生成してサムネイルを見るまで気づけない。

```python
a = d.shape(1.0, 1.0, 1.6, 0.6, text="A")    # shape() 系は objectId を返す
b = d.shape(4.0, 2.0, 1.6, 0.6, text="B")

d.connect(a, b)                  # API のコネクタとして接続。図形を動かすと線が追従する
d.connect(a, b, category="BENT") # エルボー。1対多のファンアウトで経路が交差しにくい
d.link(a, b)                     # 中心を結ぶ線と辺の交点を端点にする（斜めでもぴたり）
d.edge_point(a, (tx, ty), gap=0.04)          # 辺の一点だけ欲しいとき
d.line(..., free=True)           # 軸・目盛り・引き出し線など、接しないのが正しい線
```

| 用途 | 使うもの |
|---|---|
| 図形 A → B。動かしても追従してほしい | `d.connect(a, b)` |
| 図形 A → B。辺にぴたりと合わせたい | `d.link(a, b)` |
| 経路の折れ点・軸・引き出し線 | `d.line(..., free=True)` |

`connect()` の接続サイトは位置関係から自動で決まる（0=上 1=左 2=下 3=右）。
`audit_connectors()` は、どの図形からも 0.22in 以上離れた端点と、図形の内部に
0.06in 以上食い込んだ端点を返す。ゾーンのような大きな容器とテキストボックスは
判定から外れる（矢印が容器の中を通るのは正常なため）。**生成前に必ず呼ぶこと。**

## 自己点検（audit 4 種・生成前に必ず呼ぶ）

どれも座標だけで分かる不具合で、放っておくとサムネイルを見るまで気づけない。

```python
for msg in (d.audit_bounds() + d.audit_connectors()
            + d.audit_overlaps() + d.audit_text_fit()):
    print(msg)
```

| 検査 | 拾うもの |
|---|---|
| `audit_bounds()` | スライドの外へ出た図形・線の端点 |
| `audit_connectors()` | 端点がどの図形にも接していない／図形に埋まっている矢印 |
| `audit_overlaps()` | 後から描いた図形に隠れた文字、ラベルどうしの衝突、**文字の上を走る線** |
| `audit_text_fit()` | 枠からはみ出して切れる文字と、最終行に 1 文字だけ残る折り返し |

`audit_bounds()` は複合パーツで効く。`pyramid` や `funnel` のように与えられた枠から
自分で座標を計算する部品は、**枠が正しくても中身が外へ突き抜ける**ことがあり、
図形単位で見ないと拾えない。

`audit_overlaps()` は Slides の描画順（後の要素が上）を使う。バナーやゾーンを
直前のブロックに重ねてしまう典型的な事故がこれで落ちる。入れ子（ゾーンの中に
中身を置く）は正常なので報告しない。

**線と文字の重なりも見る。** 矢印・コネクタ・グリッド線が字の上を走っていないかを、
線分と「字が実際に載る矩形」の交差長で判定する（`LINE_CROSS_MIN` = 0.06in を
超えたら報告）。矢印の先が字の縁を掠るのは正常なので落ちない。

ここでも描画順を見ている。**線を引いてから上に塗り図形を被せる**描き方
（`hub()` は中心から各ノードの中心へ線を伸ばし、後からノードの箱を置く）では
線は塗りに隠れて見えないので、報告しない。線より後に描かれた不透明な図形が
その文字を覆っているかどうかで判断する。

抑制するのは、その塗り図形が**文字の矩形を完全に覆っている**ときだけ。部分的にしか
覆っていない場合は報告する。見落とすより、判断を人に戻すほうを選んでいる。

## 配色とレイアウトの規約

`d.P` はテンプレート由来のパレット（`primary` / `success` / `danger` / `info` / `muted` /
`surface` / `border` / `text`。ほかに `primaryDark` / `warning` / `surfaceAlt` / `white`
も持つ）。`readable_on()` で背景に応じた文字色を自動で選ぶ。

**縦位置は前のブロックの戻り値で決めること。** `cards` / `flow` / `hbars` / `metric` は
描画領域の下端 y を返すので、次のブロックはその値を起点に置く。手で `2.7` のような
値を書くと、内容が増えたときに下のブロックへ潜り込む。

```python
b = d.cards(0.5, 0.9, 9.0, 1.0, items)     # b は下端 y
b = d.hbars(0.5, b + 0.2, 9.0, rows)       # 前のブロックの下から置く
d.label(0.5, b + 0.2, 9.0, 0.3, "まとめ")
```

下端が本文領域（`scalar-2026` の `TITLE_ONLY` なら y = 5.02 まで）に収まるかは
最後に確認する。

**枠の中の文字は折り返しを見越して改行位置まで書く。** カード見出しが2行になると本文に食い込む。
目安は「幅[in] × 72 ÷ フォントサイズ」文字（全角1・半角0.5）。`audit_text_fit()` が
この計算で溢れを拾う。

**箱の高さに対して固定比率で中身を割り当てない。** 「見出しに 0.7in」「数値に 52%」の
ような配分は、箱が小さいと中身が潰れて文字が切れる。自作の部品は与えられた領域に
収まるよう自分で縮ませる（`metric` は枠高からフォントサイズを算出している）。

**直線のアクセントバーを重ねる矩形は角を丸めない。** 上端・左端にバー（細い
`RECTANGLE`）を敷くカードは、本体も `RECTANGLE` で描く。角丸の縁と直線バーの端が
噛み合わず、不揃いに見える（`cards()` はこの規約で直角になっている）。バーを持たない
単独のチップ・帯は角丸のままでよい。

## レイアウトに収まらない内容を足す場合

プレースホルダだけで足りないときは、`build_deck.py` をライブラリとして使い、返ってきた `slideId` に対して図形を足す:

```python
import sys; sys.path.insert(0, "scripts")
from importlib.machinery import SourceFileLoader
bd = SourceFileLoader("bd", "scripts/build_deck.py").load_module()

template = bd.load_template("templates/<id>.json")
deck = bd.TemplateDeck.create(template, title="…", folder=None)
ref = deck.add_slide("CONTENT", title="…")
deck.requests.append({"createShape": {..., "elementProperties": {"pageObjectId": ref["slideId"], ...}}})
deck.add_page_numbers()
print(deck.commit())
```

座標は `template.json` の `layouts.<KEY>.elements` の `contentTop` 相当（`body` の y）と
フッター位置の間に収める。色は `colors` のキーを使い、テンプレートの配色から外れないようにする。
