# アイコンライブラリ

`assets/shared/icons/` に Scalar ブランドのピクトグラムが **62 種**入っている。24px
グリッドの単色アイコンで、SVG が正本、PNG（512px）はラスタライザが無い環境向けの控え。

```
assets/shared/icons/
  icons.json      名前・日本語名・英語名・検索タグ・染められるか
  svg/<slug>.svg  正本
  png/<slug>.png  控え（512px・素材のグレーのまま）
cache/icons/      染めて書き出した PNG（<slug>-<色>-<px>.png）
scripts/icons.py  検索 CLI と SlideBuilder 用ミックスイン
```

## シェイプで組むピクトグラムとの使い分け

| | `pictogram-catalog.md`（シェイプ） | 本ライブラリ（`add_icon`） |
|---|---|---|
| 何で描くか | Slides のシェイプ 141 種を組み合わせる | ブランド素材の SVG を PNG にして貼る |
| 語彙 | 汎用（cloud / shield / server …） | 62 種の業務語彙（情報銀行・証拠チェーン・内定 …） |
| 通信 | 不要（batchUpdate だけで完結） | **要る**（Drive へ一時アップロード） |
| 見た目 | 素朴。3 シェイプ以上は破綻しやすい | ブランド準拠 |

**社外向けの資料、語彙が合うもの、3 シェイプ以上必要になるものは本ライブラリを使う。**
`pictogram-catalog.md` の「3シェイプ以上の複合ピクトグラムは外部画像の使用を検討」は
まさにこれのこと。単純な図形 1 個で足りるならシェイプのままでよい。

**ロゴは対象外。** `scalar-logo` / `scalar-logo-mono` も入っているが、これは 24px の
古いマーク。ロゴを置くときは `assets/<theme>/logos/` の高解像度アセットを
`add_image_from_asset()` で使うこと。

## 名前を探す

名前は slug（`evidence-chain`）でも日本語名（`証拠チェーン`）でも英語名でも引ける。
タグにも当たるので「鍵」「sns」のような語からも辿れる。

```bash
~/.claude/venvs/gslides/bin/python scripts/icons.py --list            # 62 種を一覧
~/.claude/venvs/gslides/bin/python scripts/icons.py --search 情報銀行  # 部分一致で探す
~/.claude/venvs/gslides/bin/python scripts/icons.py --search key
```

曖昧な名前（例: `鍵` → public / private / shared）はエラーにして候補を出す。
存在しない名前も候補付きで落とすので、**生成前に誤字が分かる。**

全アイコンを 1 枚の PNG で見たいとき（cairosvg と ImageMagick が要る）:

```bash
python scripts/icons.py --sheet --out out/icons.png --color '#2673BB'
```

## SlideBuilder に混ぜる

```python
import sys, os
sys.path.insert(0, os.path.join(SKILL_DIR, "scripts"))
from icons import IconLibraryMixin

class SlideBuilder(IconLibraryMixin):
    def __init__(self, drive_service):
        ...
        self.drive_service = drive_service      # 必須（Drive へ一時アップロードする）
        self._uploaded_assets = []              # 必須（cleanup 対象）
        self.icon_color = C.primary             # アイコンの既定色
        self.icon_label_color = C.textMuted     # キャプションの既定色
```

ミックスインが使う SlideBuilder のメソッド:

| メソッド | 用途 | 無い場合 |
|---|---|---|
| `add_image` | アイコン本体 | 必須 |
| `add_text` | キャプション・カードの文言 | 必須 |
| `add_arrow` | `add_icon_flow` の矢印 | 細い矩形（`add_rect`）で代用 |
| `add_rounded_rect` | `add_icon_cards` の枠 | `add_rect` で代用 |

色は **`#RRGGBB` でも `hex_to_rgb()` の dict でもよい**（内部で相互変換する）。
テーマ定数 `C.primary` をそのまま渡せる。

## 使う

座標はインチ、原点はスライド左上。**戻り値はキャプションを含めた下端 y** なので、
次のブロックはその値を起点に置く。

| やりたいこと | メソッド |
|---|---|
| 1 個だけ置く | `add_icon(slide_id, name, x, y, size, color=…, label=…)` |
| 横一列に並べる | `add_icon_row(slide_id, x, y, w, items)` |
| 矢印でつないで流れにする | `add_icon_flow(slide_id, x, y, w, items)` |
| 格子状に並べる | `add_icon_grid(slide_id, x, y, w, items, cols=4)` |
| アイコン付きのカードにする | `add_icon_cards(slide_id, x, y, w, h, items, cols=3)` |

`items` は名前か `(名前, ラベル)`。`add_icon_cards` だけ `(名前, 見出し, 補足)`。

```python
b = sb.add_icon_flow(sid, 0.5, 1.35, 9.0, [
    ("job-seeker", "求職者"), ("signup", "会員登録"),
    ("screening", "書類選考"), ("interview", "面接"), ("job-offer", "内定"),
], size=0.86)
sb.add_icon(sid, "evidence-chain", 0.8, b + 0.3, 1.0, color=C.accent,
            label="証拠チェーン")
```

動く実例は **`scripts/generate-icon-gallery.py`**（全 62 種 + 5 メソッドのカタログを
生成する。SlideBuilder にミックスインを混ぜる書き方もこれが手本）。

## 色

**素材は薄いグレー（#C7C9C9）の単色。**そのまま貼ると白地で沈むので、
`self.icon_color` にテーマの主色を入れておくか、`color=` で明示する。

- 要素ごとに変えるときは `color=[…]` のリストを渡す（`_row` / `_flow` / `_grid`）。
- 白い部分は「くり抜き」なので染め替えない（`faq` の文字など）。
- `scalar-logo` だけはブランド色を持つため **`color` を無視する**
  （`icons.json` の `recolorable: false`）。単色版の `scalar-logo-mono` は染まる。

## 何が起きているか

1. SVG の `#C7C9C9` を指定色に置換する
2. PNG に焼く（`cairosvg` → `rsvg-convert` → `ImageMagick` の順に試す）
3. `cache/icons/<slug>-<色>-<px>.png` に残す。**同じアイコン・同じ色なら焼き直さない**
4. Drive に上げて `anyone:reader` で共有し、その URL を `createImage` に渡す
5. `cleanup_uploaded_assets()` で削除する（`self._uploaded_assets` に記録済み）

3 のキャッシュに加え、ミックスインが**同じ PNG のアップロードを 1 回にまとめる**ので、
同じアイコンを何枚のスライドで使っても Drive への往復は 1 回で済む。

ラスタライザがひとつも無い環境では `assets/shared/icons/png/` の素材をそのまま使い、
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
シェイプのピクトグラムと混ぜるか、素材の差し替えを依頼すること。

## 制約

- **通信が要る。** Slides は画像を URL からしか取り込めないため、Drive を経由する。
  組織のポリシーで「リンクを知る全員」の共有が禁止されていると挿入できない
  （その場合は `pictogram-catalog.md` のシェイプで組む）。
- アイコンは正方形。`size` は一辺のインチ数で、0.5〜1.4in が実用範囲。
- キャプションの幅は既定で size の 2 倍。横に詰めるときは `label_w` を明示する
  （`_row` / `_flow` / `_grid` はセル幅から自動で決める）。
- `add_image` は指定サイズによらず元の縦横比を保つ。アイコンは正方形なので
  正方形の枠に置く限りズレない。

## 素材を増やすとき

1. SVG を `assets/shared/icons/svg/<slug>.svg` に置く（24×24 の viewBox、単色 #C7C9C9）
2. `assets/shared/icons/icons.json` に `ja` / `en` / `tags` / `recolorable` / `colors` を足す
3. 控えの PNG を焼く:

```bash
~/.claude/venvs/gslides/bin/python -c "
import sys; sys.path.insert(0,'scripts'); import icons, cairosvg
s='<slug>'
cairosvg.svg2png(url=f'{icons.SVG_DIR}/{s}.svg', write_to=f'{icons.PNG_DIR}/{s}.png',
                 output_width=512, output_height=512)"
```

色が #C7C9C9 以外の素材は `recolorable: false` にしておくこと。染めると
ブランド色が壊れる。同じライブラリが `google-slides-template` スキルの
`assets/icons/` にもあるので、**素材を足したら両方に反映すること。**
