# アイコンライブラリ

`assets/scalar/pictograms/` に Scalar ブランドのピクトグラムが **62 種**入っている。24px グリッドの
単色アイコンで、SVG が正本、PNG（512px）はラスタライザが無い環境向けの控え。

```
assets/scalar/pictograms/
  icons.json      名前・日本語名・英語名・検索タグ・染められるか
  svg/<slug>.svg  正本
  png/<slug>.png  控え（512px・素材のグレーのまま）
cache/icons/      染めて書き出した PNG（<slug>-<色>-<px>.png）
```

## `illustrations` のピクトグラムとの使い分け

| | `illustrations.icon()` | `icons.asset_icon()` |
|---|---|---|
| 何で描くか | Slides の図形を組み合わせる | ブランド素材の SVG を PNG にして貼る |
| 語彙 | 30 種の汎用（person / server / database …） | 62 種の業務語彙（情報銀行・証拠チェーン・内定 …） |
| 通信 | 不要 | **要る**（Drive 経由で挿入するため） |
| 見た目 | 素朴。線の太さは自前 | ブランド準拠 |

**社外向けの資料や、語彙が合うものは `asset_icon` を使う。** 「サーバ」「クラウド」の
ような一般的な部品しか要らないときや、オフラインで完結させたいときは
`illustrations.icon()` のままでよい。両者は同じスライドに混ぜても構わない。

## 名前を探す

名前は slug（`evidence-chain`）でも日本語名（`証拠チェーン`）でも英語名でも引ける。
タグにも当たるので「鍵」「sns」のような語からも辿れる。

```bash
.venv/bin/python scripts/icons.py --list            # 62 種を一覧
.venv/bin/python scripts/icons.py --search 情報銀行  # 部分一致で探す
.venv/bin/python scripts/icons.py --search key
```

曖昧な名前（例: `鍵` → public / private / shared）はエラーにして候補を出す。
存在しない名前も候補付きで落とすので、**--dry-run の段階で誤字が分かる。**

一覧を絵で見たいときは（cairosvg と ImageMagick が要る）:

```bash
.venv/bin/python scripts/icons.py --sheet --out out/icons.png --color '#2673BB'
```

## 使う

座標の規約は `illustrations` と同じ。size×size の正方形に描き、**戻り値は
キャプションを含めた下端 y**。

| やりたいこと | メソッド |
|---|---|
| 1 個だけ置く | `asset_icon(name, x, y, size, color=…, label=…)` |
| 横一列に並べる | `asset_icon_row(x, y, w, items)` |
| 矢印でつないで流れにする | `asset_icon_flow(x, y, w, items)` |
| 格子状に並べる | `asset_icon_grid(x, y, w, items, cols=4)` |
| アイコン付きのカードにする | `asset_icon_cards(x, y, w, h, items, cols=3)` |

`items` は名前か `(名前, ラベル)`。`asset_icon_cards` だけ `(名前, 見出し, 補足)`。

```python
d = Canvas(deck, ref["slideId"], template)
b = d.asset_icon_flow(0.5, 1.15, 9.0, [
    ("job-seeker", "求職者"), ("signup", "会員登録"),
    ("screening", "書類選考"), ("interview", "面接"), ("job-offer", "内定"),
], size=0.86)
d.asset_icon("evidence-chain", 0.8, b + 0.3, 1.0, color=d.P.info, label="証拠チェーン")
```

デッキ仕様（JSON）からは `figures` の `type` で使う。

```json
{ "type": "asset_icon_flow", "x": 0.5, "y": 1.15, "w": 9.0, "size": 0.86,
  "items": [["personal-info", "個人情報"], ["consent", "同意"],
            ["data-bank", "情報銀行"]] }
```

`asset_icon` / `asset_icon_row` / `asset_icon_flow` / `asset_icon_grid` /
`asset_icon_cards` の 5 つ。実例は `examples/icon-gallery.json`。

## 色

**素材は薄いグレー（#C7C9C9）の単色。**そのまま貼ると白地で沈むので、既定では
テンプレートの主色（`P.primary`）に染める。`color=` に別の色を渡せば、
`P.success` / `P.danger` のような意味を持たせた色にできる。

- 要素ごとに変えるときは `color=[…]` のリストを渡す（`_row` / `_flow` / `_grid`）。
- 白い部分は「くり抜き」なので染め替えない（`faq` の文字など）。
- `scalar-logo` だけはブランド色を持つため **`color` を無視する**
  （`icons.json` の `recolorable: false`）。単色版の `scalar-logo-mono` は染まる。

## 何が起きているか

1. SVG の `#C7C9C9` を指定色に置換する
2. PNG に焼く（`cairosvg` → `rsvg-convert` → `ImageMagick` の順に試す）
3. `cache/icons/<slug>-<色>-<px>.png` に残す。**同じアイコン・同じ色なら焼き直さない**
4. `images.ImageMixin.image()` に渡す（Drive へ一時アップロード → 挿入 → 後始末）

3 のキャッシュと、`AssetStore` がソースのパス単位で URL を使い回すので、**同じ
アイコンを何枚のスライドで使っても Drive へのアップロードは 1 回**で済む。

ラスタライザがひとつも無い環境では `assets/scalar/pictograms/png/` の素材をそのまま使い、
色の指定は無視して警告を出す。`requirements.txt` の `cairosvg` を入れておくこと。

## 素材側の既知の不備

原典（Drive）の時点で、次の 2 組は**中身が同じ SVG**になっている。プレビュー画像
では別の絵（`private-key` は閉じた目）なので、素材の登録ミスと思われる。

| slug | 絵が同じ相手 |
|---|---|
| `private-key` | `public-key` |
| `new-workflow` | `terms` |

`icons.json` の `sameArtAs` に記録してあり、`--list` にも印が出る。**公開鍵と
秘密鍵を並べて対比させる図では、同じ絵が 2 つ並ぶ。** 色を変えて区別するか、
`illustrations.icon("key")` と混ぜるか、素材の差し替えを依頼すること。

## 制約

- **通信が要る。** Slides は画像を URL からしか取り込めないため、Drive を経由する。
  組織のポリシーで「リンクを知る全員」の共有が禁止されていると挿入できない
  （その場合は `illustrations.icon()` を使う）。
- `--dry-run` では実物を貼れないので、**同じ大きさの矩形に置き換えて**座標だけ
  検査する。名前の誤りと、はみ出し・重なり・キャプションの溢れはここで拾える。
- アイコンは正方形。`asset_icon` の `size` は一辺のインチ数で、0.5〜1.4in が実用範囲。
- キャプションの幅は既定で size の 2 倍。横に詰めるときは `label_w` を明示する
  （`_row` / `_flow` / `_grid` はセル幅から自動で決める）。

## 素材を増やすとき

1. SVG を `assets/scalar/pictograms/svg/<slug>.svg` に置く（24×24 の viewBox、単色 #C7C9C9）
2. `assets/scalar/pictograms/icons.json` に `ja` / `en` / `tags` / `recolorable` / `colors` を足す
3. 控えの PNG を焼く:

```bash
.venv/bin/python -c "
import sys; sys.path.insert(0,'scripts'); import icons, cairosvg, os
s='<slug>'
cairosvg.svg2png(url=f'{icons.SVG_DIR}/{s}.svg', write_to=f'{icons.PNG_DIR}/{s}.png',
                 output_width=512, output_height=512)"
```

色が #C7C9C9 以外の素材は `recolorable: false` にしておくこと。染めると
ブランド色が壊れる。
