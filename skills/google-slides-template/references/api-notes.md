# Google Slides API の制約と落とし穴

実測で確認した挙動。ドキュメントに明記されていないものが多い。

---

## 1. マスター/レイアウトは「作れない」が「直せる」

`presentations.batchUpdate` のリクエスト種別に、マスターやレイアウトを**新規作成する**ものは
存在しない（`Request` スキーマに `Master` / `Layout` を含む型は無い）。colorScheme の変更も
できず、試すと `Resetting the color scheme is not supported` が返る。

一方、**既存**のマスター/レイアウトの中身は変更できる。以下はすべて実測で成功を確認した:

| 操作 | 可否 |
|------|------|
| レイアウト上の図形の塗りを変更（`updateShapeProperties`） | ✅ |
| レイアウト/マスターの背景色を変更（`updatePageProperties`） | ✅ |
| レイアウトに図形を追加（`createShape` + `pageObjectId` にレイアウト ID） | ✅ |
| レイアウト上の画像・図形を削除（`deleteObject`） | ✅ |
| 空のプレースホルダの既定フォントを変更（`updateTextStyle`） | ✅ |
| マスター上のテキストの色を変更 | ✅ |
| マスター/レイアウトの**新規作成** | ❌ リクエスト種別が無い |
| colorScheme の変更 | ❌ `Resetting the color scheme is not supported` |
| レイアウトの表示名の変更 | ❌ |

**変更は、そのレイアウトから作った新規スライドに継承される**（検証済み）。

**帰結**:

- ブランドデザインを持つ資料を作るには、UI で作ったテンプレートを複製するのが基本。これが本スキルが複製方式を採る理由。
- 既存テンプレートを土台にすれば、**配色違いの派生マスターをプログラムで作れる**。ただし colorScheme は変えられないので、`theme:ACCENT6` のようなテーマ色参照は元の配色のまま解決される。派生を作る場合は、テーマ色を参照している要素を**すべて明示 RGB で上書き**する必要がある。
- ゼロからマスターを作ることはできない。土台となるプレゼンテーションが必ず要る。

---

## 2. SLIDE_NUMBER プレースホルダは生成できない

`createSlide` の `placeholderIdMappings` に `{"layoutPlaceholder": {"type": "SLIDE_NUMBER", "index": 0}}`
を指定しても、**エラーにならず黙って無視される**。生成されたスライドを取得しても
SLIDE_NUMBER の pageElement は存在しない。

```
createSlide with SLIDE_NUMBER mapping: OK       ← 成功として返る
 element SLIDES_API…_0 {'type': 'TITLE',  …}    ← TITLE と BODY だけ
 element SLIDES_API…_1 {'type': 'BODY',   …}
```

ページ番号の表示は Google Slides の UI 側の設定（挿入 → スライド番号）で、API に等価な操作が無い。

**対処**: レイアウトの `slideNumber` 座標にテキストボックスを自前で描く（`add_page_numbers()`）。
元のプレースホルダ枠は数 mm 幅しかないことが多く、2桁のページ番号が切れる。右端を保ったまま
最小 0.5in に広げてから右揃えにする。

---

## 3. colorScheme の JSON 構造が他と違う

通常の色指定は `{"opaqueColor": {"rgbColor": {"red": …}}}` だが、マスターの colorScheme だけは
`rgbColor` の階層が無く `color` 直下に RGB が入る。

```jsonc
// マスターの colorScheme
{"type": "ACCENT5", "color": {"red": 0.149, "green": 0.451, "blue": 0.733}}

// 図形の塗り
{"solidFill": {"color": {"rgbColor": {"red": 0.149, …}}, "alpha": 1}}
```

`color.rgbColor` を期待するパーサーを書くと、全色が黒（#000000）として取れてしまう。

---

## 3b. `propertyState: NOT_RENDERED` は「色は入っているが描画されない」

塗りや枠線は、色の値を持ったまま非表示にできる。

```jsonc
"shapeBackgroundFill": {
  "propertyState": "NOT_RENDERED",          // ← 透明。下の色は使われない
  "solidFill": {"color": {"themeColor": "LIGHT2"}, "alpha": 1}
}
```

`propertyState` を見ずに `solidFill` の色だけ読むと、**透明な図形を「LIGHT2 で塗られている」と誤認する**。
そこへ `updateShapeProperties` で色を設定すると `propertyState` が実質 RENDERED になり、
図形が不透明になる。全面サイズの矩形でこれをやると、マスターのロゴ・フッターを覆って消してしまう。

テンプレートには「将来の背景差し替え用に置かれた、色だけ入った透明な全面矩形」が入っていることが
実際にある。派生マスターを作るときは、色を書き換える前に必ず `propertyState` を確認すること。

取りうる値は `RENDERED` / `NOT_RENDERED` / `INHERIT`。キー自体が無い場合は描画される。

## 4. 値が 0 のチャンネルはキーごと省略される

`{"red": 1, "blue": 1}` は「緑が 0」を意味する（マゼンタ）。`{"blue": 1}` は純青。
`c["green"]` で読むと KeyError になるので、必ず `c.get("green", 0)` を使う。

黒 `#000000` は `{"rgbColor": {}}` という空オブジェクトになる。

---

## 5. 座標は transform の scale を掛ける必要がある

`size` は要素の素の大きさで、実際の表示サイズは `transform.scaleX` / `scaleY` を掛けた値。
位置は `transform.translateX` / `translateY`。単位は EMU（1 inch = 914400 EMU）。

```python
w = size.width.magnitude * transform.scaleX / 914400   # インチ
x = transform.translateX / 914400
```

scale を無視すると、拡大縮小された図形の寸法を取り違える。

---

## 6. スピーカーノートの objectId はスライド作成後にしか分からない

ノート枠の `speakerNotesObjectId` は `createSlide` のレスポンスに含まれず、`batchUpdate` の
リクエスト内で参照することもできない。

**対処**: スライドを作る `batchUpdate` を実行 → `presentations().get()` で
`slides.slideProperties.notesPage.notesProperties.speakerNotesObjectId` を取得 →
2 回目の `batchUpdate` で `insertText` する。

---

## 7. pageSize は作成時にしか指定できない

`presentations().create()` の body でのみ設定可能。作成後の変更手段が無い。

複製方式ではテンプレートのページサイズをそのまま引き継ぐため、この制約は問題にならない。
逆に、テンプレートと違うページサイズにしたい場合は複製方式を使えない。

---

## 8. batchUpdate は 500 件ずつに分ける

1 リクエストあたりの上限は明示されていないが、大量に送ると失敗しやすい。500 件ずつのチャンクに
分割して逐次実行するのが安全。リクエストは**送った順に**適用されるので、
「図形を作る → テキストを入れる → スタイルを当てる」の順序は保たれる。

---

## 9. サムネイル取得はレイアウト/マスターにも効く

`presentations.pages.getThumbnail` の `pageObjectId` には、スライドだけでなく
レイアウトやマスターの objectId も渡せる。テンプレートのレイアウトを目視確認するのに使える。

サイズは `SMALL` / `MEDIUM`（約 800px 幅）/ `LARGE`（約 1600px 幅）。
細部（7pt のページ番号など）を確認するときは LARGE を取って切り出す。

`contentUrl` は短時間で失効するので、取得したらすぐダウンロードする。

---

## 10. 複製にはコピー権限が必要

`drive.files().copy()` は、共有設定で「閲覧者・コメント投稿者に…ダウンロード、印刷、コピーを
無効にする」が有効なファイルに対して 403 を返す。テンプレートの所有者に設定解除を依頼するか、
自分の Drive にテンプレートの複製を1つ持っておく。

なお `files.copy` は、枚数の多いテンプレート（数十枚）で **一時的に 500 Internal Error や
読み取りタイムアウトを返すことが実際にある**。リトライすれば通る
（`build-deck.py` の `_retry()` が 5xx / 429 を指数バックオフで拾う）。

- **500 が返った場合**、ファイルは作られていない（実測）
- **クライアント側でタイムアウトした場合**、サーバ側では複製が完了していて
  **孤立したファイルが Drive に残る**（実測）。タイムアウトで作り直したときは、
  同名のファイルが 2 つ無いか確認して片付けること

---

## 11. `createImage` は指定サイズを無視して縦横比を保つ

`elementProperties.size` に枠の寸法を渡しても、**画像は元の縦横比のまま、その枠に
収まるよう縮小されて配置される**（＝常に「contain」）。枠を埋める配置は作成時には
実現できない。

実測（1200×675 の画像を 4.30×2.90in の枠に挿入）:

```
要求: w=4.30 h=2.90              → 結果: w=4.30 h=2.42  （比率 1.778 = 元画像）
```

さらに `size.magnitude` は渡した値ではなく画像由来の値に置き換えられ、縮小は
`transform.scaleX/scaleY` に入る。したがって「枠ぴったり」にするには 3 段階が要る。

1. `createImage` で挿入する
2. `presentations().get()` で **生成された要素の `size.magnitude`** を読む
3. `updatePageElementTransform`（`applyMode: "ABSOLUTE"`）で
   `scale = 枠の寸法 / magnitude` を設定し直す

`build-deck.py` の `_post_pass()` がこれをやっている（スピーカーノートの書き込みと
同じ 2 回目の batchUpdate に相乗りする）。

`cropProperties` は**元画像を切り取るだけで、要素の寸法には影響しない**。切り取った
結果の比率と要素の比率が合っていないと中身が引き伸ばされる。「はみ出しを切って枠を
埋める」を正しくやるには、crop と上記の transform 上書きの両方が必要。

## 11b. `createImage` の URL は匿名で取得される

`url` は Slides 側が取りに行く。**認証済みの自分がアクセスできるだけでは足りず、
リンクを知る全員が閲覧できる必要がある。** Drive のファイルを使う場合は
`permissions().create({"type": "anyone", "role": "reader"})` を先に付ける。

挿入時に画像は**プレゼンテーション内へコピーされる**ので、`batchUpdate` の成功後は
元ファイルを削除しても公開を解除しても表示は壊れない。一時ファイルはその場で畳むのが
安全（`images.AssetStore.cleanup()`）。

受け付ける形式は PNG / JPEG / GIF のみ、50MB 未満・25 メガピクセル未満。

## 12. 図形を回すと中の文字も回る

`AffineTransform` に回転角のフィールドは無く、`scaleX / scaleY / shearX / shearY` で表す。

```
x' = scaleX·x + shearX·y + translateX      θ 回転:
y' = shearY·x + scaleY·y + translateY        scaleX = scaleY = cosθ
                                             shearX = -sinθ, shearY = sinθ
```

中心を保って回すには、translate を
`cx - (cosθ·w/2 - sinθ·h/2)`, `cy - (sinθ·w/2 + cosθ·h/2)` にする。

**テキストだけを回さない方法は無い。** 台形（`TRAPEZOID` は既定で上底が狭い）を
180 度回して「上底が広い台形」として使うとき、`insertText` した文字も上下逆さまに出る。
図形と文字は別の要素に分けること。`diagrams.Canvas.shape()` は 0/90/270 度以外の
回転に文字を入れると警告する。

## 13. 塗りの alpha は指定できる

`solidFill` の `alpha` は 0〜1 で効く（ベン図の重なりなど）。ただし `fields` に
`shapeBackgroundFill.solidFill.color` だけを指定すると alpha が反映されないため、
`shapeBackgroundFill.solidFill` を指定すること。

## 14. テキスト枠には既定の内側余白がある

テキストの折り返しを見積もるとき、枠の幅をそのまま使ってはいけない。Slides の
テキスト枠には既定で **左右 0.1in / 上下 0.05in の内側余白**があり、文字が使える
幅はその分狭い。

```
1行に入る文字数 = (枠の幅[in] − 0.1×2) × 72 ÷ フォントサイズ[pt]
```

引かずに計算すると 1〜2 字多く入る勘定になり、実際には折り返している文字列を
「1 行に収まる」と誤判定する（実測: 1.62in / 11pt の枠に全角 10 字を入れると
折り返すが、余白を引かない式では「10.6 字入る」と出る）。

一方、**縦方向は引かないこと。** Slides は枠から縦に溢れた文字を切り取らずに
そのまま描くため、上下余白まで差し引くと 1 行のラベルが軒並み誤検知になる
（実測: 0.24in の枠に 9.5pt の 1 行は問題なく表示される）。

## 15. `TRAPEZOID` の傾きは変えられない

上底の食い込みは **表示上の高さ × 0.25**（左右それぞれ）で固定されている。実測:

| 素の箱 | scaleY | 表示高さ | 上底 | 下底 |
|---|---|---|---|---|
| 4.0 × 1.4in | 1.0 | 1.40in | 3.30in | 4.00in |
| 4.0 × 2.8in | 0.5 | 1.40in | 3.30in | 4.00in |

どちらも食い込み計 0.70in = 0.25 × 1.40 × 2。**幅を変えても scaleY で潰しても
比率は変わらない**（2 行目は「素の高さで計算されるなら 1.40in になるはず」を
狙った実験で、そうはならなかった）。API に図形の調整値（OOXML の `adj`）を
渡す手段は無い。

**帰結**: ピラミッドやファネルのように「上底と下底を自分で決めたい」図に
`TRAPEZOID` は使えない。段ごとに高さが同じでも幅が違えば傾きが変わるため、
積み上げると輪郭がギザギザになる。

**対処**: 「中央の矩形＋左右の直角三角形」の 3 部品で描く
（`illustrations.IllustrationMixin._taper()`）。`RIGHT_TRIANGLE` は既定で
直角が**左下**にあり、`scaleX` / `scaleY` を負にする鏡像で 4 隅どの向きも作れる。

```
既定            flip_x          flip_y          flip_x+flip_y
■               　■             ■■              ■■
■■              ■■             ■               　■
```

向きの実測結果: 既定は「垂直な辺が左、斜辺が左上→右下」。

なお `TRAPEZOID` の既定の向きは**上底が狭く下底が広い**。180 度回すと逆になるが、
中の文字も一緒に逆さまになる（セクション 12）。
