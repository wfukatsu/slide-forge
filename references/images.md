# イメージ図と画像

箇条書きで説明しきれないものを絵にする手段は 5 つある。**まず用途で選ぶこと。**

| 見せたいもの | 使うもの | 特徴 |
|---|---|---|
| 構造・手順・数値の関係 | `diagrams.Canvas`（`flow` / `cards` / `hbars` / `connect`） | 正確。要素どうしの関係が保証される |
| 概念・比喩・登場人物 | `illustrations`（`icon_flow` / `pyramid` / `iceberg` …） | 図形で描く。**ネットワーク不要・毎回同じ絵**・テーマ配色 |
| 業務語彙のアイコン | `icons`（`asset_icon` / `asset_icon_flow` …） | Scalar ブランドの素材 62 種。ブランド準拠。**通信が要る**。→ `icons.md` |
| クラウド構成図 | `cloud_icons`（`cloud_icon` / `cloud_zone` …） | AWS/GCP/Azure 公式 1,757 種。**色・回転の変更は禁止**。→ `cloud-icons.md` |
| 雰囲気・情景・表紙 | `images`（`ai_image` / `image`） | AI 生成か手持ちの画像。表現力は高いが再現性は生成時のキャッシュ頼み |

いずれも `Canvas` のメソッドとして生えているので、同じスライドに混ぜて使える。
座標はすべてインチ、原点はスライド左上、**戻り値は描画領域の下端 y**。

```python
d = Canvas(deck, ref["slideId"], template)
b = d.icon_flow(0.7, 1.1, 8.6, [("person", "利用者"), ("server", "API")])
b = d.label(0.7, b + 0.2, 8.6, 0.3, "…")
```

---

## 1. ピクトグラム（`illustrations`）

30 種。`icon()` は size×size の正方形に描き、`label` を渡すと下にキャプションを付ける。

```
person people server database cloud document documents gear lock shield
browser mobile bot chart clock check cross warning mail key
network code stack folder bulb search sync flag coin chip
```

| 使う場面 | メソッド |
|---|---|
| 1 個だけ置く | `icon(name, x, y, size, color=…, label=…)` |
| 横一列に並べる | `icon_row(x, y, w, items)` |
| 矢印でつないで流れにする | `icon_flow(x, y, w, items)` |
| 格子状に並べる | `icon_grid(x, y, w, items, cols=4)` |

`items` は名前か `(名前, ラベル)`。色は `color=` に 1 色、または要素ごとのリスト。

```python
d.icon_flow(0.5, 1.3, 9.0, [
    ("person", "利用者"), ("browser", "Web アプリ"),
    ("server", "API"), ("database", "台帳"),
], size=0.92)
```

**キャプションの幅は既定で size の 2 倍。** 横に詰めて並べるときは `label_w` を
セル幅に合わせて明示すること。放っておくと隣のキャプションとぶつかり、
`audit_overlaps()` に拾われる。

**`icon_flow` は `w / 個数 − size − 0.2in` の隙間に矢印を引く。** 絵を大きくすると
ここが負になり、右向きのはずの矢印が逆向きに描かれる（`_anchored` な線なので
`audit_connectors()` は拾わない）。隙間が足りないときは `ValueError` で止まるので、
`size` を下げるか `w` を広げるか、矢印の要らない `icon_row` に替える。
狭い枠（表紙や章扉のカードなど）では `icon_row` のほうが収まりがよい。

### ブランドのアイコンを使う場合

`illustrations` の 30 種は汎用の部品なので、「情報銀行」「証拠チェーン」「内定」の
ような業務語彙は描けない。そこは `assets/scalar/pictograms/` のブランド素材（62 種）を使う。
使い方は同じ形で、メソッド名に `asset_` が付く。

```python
d.asset_icon_flow(0.5, 1.15, 9.0, [("job-seeker", "求職者"), ("interview", "面接")])
```

一覧・検索・色の扱い・制約は **`references/icons.md`** にまとめてある。

## 2. 比喩図（`illustrations`）

| メソッド | 何を見せる図か | 主な引数 |
|---|---|---|
| `pyramid(x,y,w,h,levels)` | 階層。上ほど少数・上位 | `captions=` で各段の右に補足 |
| `funnel(x,y,w,h,stages)` | 絞り込み。段ごとに数を添える | `stages=[(ラベル, 値)]` |
| `venn(x,y,w,h,sets)` | 重なり。2 個か 3 個 | `center=` で共通部分のラベル |
| `iceberg(x,y,w,h,above,below)` | 見えている一部と水面下の大半 | `art_ratio=` で絵と文字の配分 |
| `balance(x,y,w,h,left,right)` | 2 案の比較 | `tilt=1` で右が重い |
| `steps(x,y,w,h,items)` | 段階を踏んで上がる | 左が最初、右が最後 |
| `layers(x,y,w,h,items)` | 積層。技術スタック等 | `items=[(ラベル, 補足)]` |
| `hub(x,y,w,h,center,spokes)` | 中心と放射 | 中心が主役のとき |
| `matrix(x,y,w,h,quadrants)` | 4 象限で位置づける | 左上・右上・左下・右下の順。軸は `(下, 上)` `(左, 右)` |
| `before_after(x,y,w,h,before,after)` | 左右の対比 | 中央に矢印が入る |
| `journey(x,y,w,h,milestones)` | 道のり。上下交互に配置 | `milestones=[(見出し, 補足)]` |
| `timeline(x,y,w,items)` | 横方向の時系列 | `items=[(時点, 見出し)]` |

**JSON 仕様で書く場合、`levels` / `stages` / `sets` / `spokes` / `milestones` の
ような位置引数はすべて `FIGURES` 定義のキー名（多くは `items`）で渡す。**
Python のシグネチャの引数名のままでは通らない（`hub` の `center`、`iceberg` の
`above` / `below` のように `FIGURES` 側も固有名のものはそのまま）。

### 枠の外に出るもの

`pyramid(captions=…)` と `funnel` の値表示は、**`x + w` の右外側**を使う。
その分の余白を残して `w` を決めること。残さないと `audit_bounds()` が
「スライドの外に出ています」で落とす。

### 台形は `TRAPEZOID` で描いていない

Slides の `TRAPEZOID` は**上底の食い込みが「高さ × 0.25」に固定**で、幅でも
scaleY でも変えられない（実測。`api-notes.md` セクション 15）。段ごとに幅が違う
ピラミッドやファネルをこれで積むと、段ごとに傾きが変わって輪郭がギザギザになる。

そこで `pyramid` / `funnel` は「中央の矩形＋左右の直角三角形」の 3 部品で
1 段を描いている（`_taper()`）。各段の上底をひとつ上の段の下底に合わせているので、
輪郭は一直線につながる。自分で台形を描きたいときも `_taper()` を使うこと。

### 回転した図形に文字を入れてはいけない

五角形（`shield`）などは 180 度回して使っている。**回すと中の文字も一緒に回り、
上下逆さまに出る。** 図形は `text` 無しで描き、文字は別に `label()` を重ねること。
`shape()` は 0/90/270 度以外の回転に文字を入れると警告する。

`label(rotation=270)` で意図的に縦にすることはできるが、**日本語では使わないこと。**
文字が横倒しになって読みにくい。縦のラベルが要るときは 1 文字ずつ改行して積む
（`matrix` の縦軸ラベルはこの方式）。

---

## 3. 画像（`images`）

### 手持ちの画像を貼る

```python
d.image(0.6, 1.1, 4.2, 2.6, "assets/screenshot.png", fit="contain",
        caption="管理画面", outline="#D6E4F2")
```

キャプションの位置は `caption_at` で決める。

- `"image"`（既定）… 画像の実際の下端。1 枚だけ置くときはこちら
- `"box"` … 枠の下端。**画像を横に並べるときはこちら**。`fit` が違うと画像の
  下端がずれるため、既定のままだとキャプションの高さが揃わない

`source` は次のいずれか。

- ローカルのパス（**実行時のカレントディレクトリから解決される**）
- `http(s)://…` の URL
- Drive のファイル URL、または `drive:<fileId>`

| `fit` | 挙動 |
|---|---|
| `contain`（`image()` の既定） | 比率を保って枠内に収める。余白ができる |
| `cover` | 枠を埋め、はみ出す分を切り落とす |
| `stretch` | 枠に合わせて引き伸ばす（比率が崩れる） |

**`ai_image()` の既定は `cover`**（枠を埋める）。生成比は枠と完全には一致しない
ため、`contain` だと余白にテンプレートの地が覗く。「枠に合わせて生成する」を参照。

Slides が受け付けるのは **PNG / JPEG / GIF のみ**、50MB 未満・25 メガピクセル未満。
それ以外は挿入前にエラーにする。

### テンプレートに画像枠があるなら、そこに置く

**座標を自分で決める前に、レイアウトの `imageSlots` を見ること。** 表紙・章扉・
事例紹介のようなレイアウトは「ここに絵を入れる」枠を持っていることが多く、
そこを外すとテンプレートのデザインから浮く。

```json
{ "layout": "SECTION", "title": "第1章 …",
  "figures": [ { "type": "aiImage", "prompt": "…", "style": "isometric" } ] }
```

`x` / `y` / `w` / `h` を省略すると `build_deck.py` が枠の座標を埋め、`fit` も
`"cover"` にする（枠は縦横比までデザインなので、余白付きで収めるより枠を
埋めるほうが合う）。枠が複数あるレイアウトでは `"slot": 1` のように選ぶ。

`aiImage` なら、**絵そのものも枠に合わせて生成される**（枠の比に最も近い比率で
描き、切り取られる分を見越した構図をモデルに指示する）。詳しくは
「枠に合わせて生成する」。

```bash
# どのレイアウトにどんな枠があるかを見る
python scripts/inspect_template.py <URL>        # レポートに imageSlot[N] が出る
```

枠があるのに別の場所へ置くと `--dry-run` が警告する（`--strict` ならエラー）。
枠が無いレイアウトでは、これまでどおり座標を自分で決める。

**もう出来ているデッキ**の空き枠を埋めるなら `scripts/fill_image_slots.py`
（`image-slots` スキル）。仕様の無いデッキや、URL を変えられないデッキが対象。

```bash
python scripts/fill_image_slots.py <URL> --dry-run   # どの枠が埋まるかを見る
python scripts/fill_image_slots.py <URL>
```

### AI で生成する

```python
d.ai_image(5.2, 1.1, 4.2, 2.6,
           "自律型エージェントが夜間にビルドを回している様子",
           style="flat_vector")
```

```bash
# 単体で試す（--show-prompt なら API を呼ばずにプロンプトだけ見られる）
python scripts/images.py --prompt "…" --style flat_vector \
    --template templates/aixdevops.json --out out/hero.png
```

| `style` | 向いている用途 |
|---|---|
| `flat_vector`（既定） | ビジネス資料の挿絵全般。線画＋テーマ配色 |
| `line_art` | 軽い装飾。文字の邪魔をしない |
| `isometric` | システム構成・インフラの俯瞰 |
| `blueprint` | 技術的な設計の比喩 |
| `paper` | 柔らかい印象の扉 |
| `photo` | 表紙・セクション扉の背景。本文の説明図には不向き |

- プロンプトには**テンプレートの配色**（`d._template_colors` 由来）と、
  「文字・ロゴを描かない」「余白を取る」といった制約が自動で足される。
- `aspect` を省略すると**枠に合わせて生成される**。詳しくは次項。
- 生成物は `cache/images/<hash>.png` にキャッシュされる。キーは
  (モデル, スタイル, 比率, プロンプト全文)。**同じ指定ならデッキを作り直しても
  同じ絵が出る。** プロンプトはサイドカーの `.json` に残る。
- `GEMINI_API_KEY` が必要。既定のモデルは `gemini-3.1-flash-image`
  （`GSLIDES_IMAGE_MODEL` で変更可）。

> **画像モデルは無料枠のクォータが 0。** キーが無料枠のプロジェクトのものだと
> `HTTP 429 / limit: 0` が返る。課金を有効にしたプロジェクトの API キーが要る。
> 図形で描く `illustrations` のほうはキー無しで動く。

### 枠に合わせて生成する

`aspect` を省略すると、置き先の枠（テンプレートの `imageSlots` でも、自分で
決めた座標でも）に合わせて生成される。ただし**モデルが作れる比率は 10 種類しか
無い**ので、枠とぴったり同じ比率にはならない。

そこで次の 2 つで埋めている。

1. 枠の比に**最も近い比率**で生成する
2. 残った差は `fit="cover"` の切り取りで埋める。`ai_image` の `fit` は既定が
   `cover` で、枠を必ず埋める（`contain` だと余白にテンプレートの地が覗く）

切り取りは中央から行われるため、主題が端に寄っていると欠ける。これを避けるため、
比率のずれが 2% を超える場合は**切り取られる分を見越した構図**をプロンプトで
指示する（「1.13:1 の枠に入り、左右が約 9% 切られる。主題は中央に寄せ、端には
残したいものを置かない」）。生成時に次のように出る。

```
  note: 1.13:1 の枠に対して 5:4 で生成します（切り取りで主題が欠けない構図を指示済み）
```

枠の比はプロンプト全文に入るのでキャッシュキーにも効く。**同じ絵を別の比率の枠に
置くと作り直しになる**（その枠のための構図で描き直される）。

比率を自分で決めたいときは `aspect` を明示する。その場合、枠と合っているかは
指定した側の責任とみなし、構図の指示は付けない。

### 何が起きているか（ローカル画像の場合）

1. 存在・形式・サイズを検査する（ローカル完結。ここで弾かれた指定は
   `d.image()` の呼び出し位置で例外になる）
2. Drive への一時アップロードと「リンクを知る全員が閲覧可」の付与を
   **別スレッドに投げる**（`AssetStore.defer()`）。`createImage` は URL を
   **匿名で**取りに行くため、認証済みの自分がアクセスできるだけでは足りない
3. 実寸はローカルのファイルから読むので、URL の確定を待たずに配置を決められる。
   `createImage` は `url` を空にしたまま組み立てておく
4. `commit()` の冒頭で全アップロードの完了を待ち、`url` を埋める
   （`AssetStore.flush()`）。同じソースは何枚貼っても 1 回しか上げない
5. `batchUpdate` で挿入する（Slides が画像をプレゼンテーション内へコピーする）
6. その直後に一時ファイルを削除し、既存ファイルに付けた公開共有を外す
   （`AssetStore.cleanup()`。並列に実行する）

アップロードは 1 枚あたり実測 3.1 秒（アップロード 1.9s ＋ 共有設定 1.2s）かかる。
描画の途中で 1 枚ずつ同期に待つと画像 10 枚のデッキで 30 秒以上が画像だけに消えるため、
2〜4 の形で裏に回している（実測 37.3s → 16.9s）。

リモート（http / Drive）のソースは実寸を読むのに URL 自体が要るので、ここは
同期に解決する。

組織のポリシーで「リンクを知る全員」が禁止されていると 2 が失敗する。その場合は
あらかじめ公開されている URL を渡すか、`illustrations` で描くこと。

中断した実行の後始末は `atexit` に登録してある。飛行中のアップロードも待ってから
畳むので、公開状態の一時ファイルは残らない。

---

## デッキ仕様（JSON）から使う

`build_deck.py` の spec で、スライドに `figures` を足せる。

```json
{
  "layout": "TITLE_ONLY_PROPOSAL",
  "title": "利用者から台帳まで",
  "figures": [
    { "type": "icon_flow", "x": 0.5, "y": 1.3, "w": 9.0, "size": 0.92,
      "items": [["person", "利用者"], ["server", "API"], ["database", "台帳"]] },
    { "type": "image", "x": 0.5, "y": 3.2, "w": 4.0, "h": 1.6,
      "source": "assets/shot.png", "fit": "cover" },
    { "type": "aiImage", "x": 5.0, "y": 3.2, "w": 4.0, "h": 1.6,
      "prompt": "夜間に自動でビルドが回っている様子", "style": "flat_vector" }
  ]
}
```

- `type` の正は `scripts/build_deck.py` の `FIGURES` 辞書（45 種）。
  系統別の一覧は `references/template-schema.md` を参照。
- 位置引数以外のキーは **camelCase → snake_case** に直して渡される
  （`labelSize` → `label_size`、`xAxis` → `x_axis`）。
- `--dry-run` は API を一切呼ばずに図を座標へ展開し、はみ出し・重なり・文字溢れを
  検査する。**画像は実物を取りに行く必要があるため検査対象外。**

---

## 生成前に必ず通す 4 つの検査

```python
for msg in (d.audit_bounds()        # スライドの外に出た図形
            + d.audit_connectors()  # 浮いた線・埋まった線
            + d.audit_overlaps()    # 隠れた文字・ぶつかった文字
            + d.audit_text_fit()):  # 文字の溢れと、みっともない折り返し
    print(msg)
```

`audit_text_fit()` は 2 種類を見る。

1. **溢れ** … 枠に対して文字が多く、はみ出して読めなくなるもの
2. **孤立行** … 折り返した最後の行に 1 文字しか残らないもの（「…デプロ / イ」）。
   収まってはいるが明らかに不格好で、枠を数 mm 広げれば消える

1 行に入る文字数は **Slides のテキスト枠の左右インセット（各 0.1in）を引いて**
見積もる。引かないと 1〜2 字多く入る計算になり、実際には折り返しているのに
検査が素通りする。

`build_deck.py` は spec から生成するとき、これを自動で回して結果を表示する。
`--strict` を付けると 1 件でも出たら終了コードを 1 にする。

`audit_bounds()` は図の部品が枠の外へ突き抜けたときに効く。部品は与えられた枠から
自分で座標を計算するため、**枠が正しくても中身が外へ出る**ことがあり、これは
図形単位で見ないと拾えない。
