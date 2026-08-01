---
name: google-slides-template
description: >-
  既存の Google Slides テンプレート（マスタースライド）を複製して、そのレイアウトに沿った
  プレゼンテーションを生成する。テンプレートの解析・登録（template.json）、デッキ生成、
  サムネイルによる視覚 QA までを扱う。
  トリガー: "このテンプレートでスライドを作って", "マスタースライドから生成", "テンプレートを登録",
  "テンプレートを解析", "gslides-template", "create slides from this template",
  "use this master", Google Slides のテンプレート URL を渡された場合。
---

# テンプレート駆動 Google Slides 生成

## Important

- **このスキルの守備範囲**: 既存の Google Slides プレゼンテーションを**デザインの正**として複製し、そのレイアウトにテキストを流し込む。
- **対象外**:
  - テンプレートを持たずゼロからデザインを組む → `google-slides` スキル（コンポーザー・インフォグラフィクス）
  - PPTX ファイルの生成 → `document-skills:pptx`
  - テンプレート自体のデザイン変更 → **Slides API はマスター/レイアウトの作成・編集をサポートしない**。Google Slides の UI で行うこと。
- Python 3.10+ が必要。`.venv` は `~/.claude/venvs/gslides` への**シンボリックリンク**で、`google-slides` スキルと共有している。依存を変更すると両方に効く。
- 認証情報は `config/credentials.json` → `~/.claude/skills/google-slides/config/` の順に探索する。既存の `google-slides` スキルを設定済みならそのまま使える。
- **視覚確認を省略しない。** API のレスポンスが正常でも、文字のはみ出し・装飾との矢印が他の図形の上を横切っていないか、意味のうえで正しい図形に繋がっているかは判定できない。生成後は必ずサムネイルを取得して目視する。

## Quick Reference

| やること | コマンド |
|---------|---------|
| テンプレートを解析して登録 | `scripts/inspect-template.py <URL> --emit templates/<id>.json --name <id>` |
| レイアウトのサムネイル取得 | `scripts/inspect-template.py <URL> --thumbnails out/layouts` |
| デッキ仕様の検証（API 不要） | `scripts/build-deck.py --template … --spec … --dry-run` |
| デッキ生成 | `scripts/build-deck.py --template … --spec … --title "…"` |
| 生成物の視覚 QA | `scripts/fetch-thumbnails.py <URL> --out out/qa` |
| 画像を AI で生成 | `scripts/images.py --prompt "…" --style flat_vector --out out/x.png` |
| アイコンを探す | `scripts/icons.py --list` / `--search 情報銀行` |
| クラウドアイコンの取り込み（**初回必須**） | `scripts/fetch-cloud-icons.py` |
| クラウドアイコンを探す | `scripts/cloud_icons.py --search s3` / `--list --vendor aws` |
| イメージ図・画像の使い方 | `references/images.md` |
| アイコンライブラリの使い方 | `references/icons.md` |
| クラウドアイコン（AWS/GCP/Azure）の使い方 | `references/cloud-icons.md` |
| イメージ図のカタログ（仕様の実例） | `examples/illustration-gallery.json` |
| アイコンのカタログ（仕様の実例） | `examples/icon-gallery.json` |
| クラウド構成図（仕様の実例） | `examples/cloud-architecture.json` |
| ScalarDB 構成図（Canvas を直に使う実例） | `examples/scalardb-architecture.py` |
| ScalarDL 構成図（3 系統のアイコンを混ぜる実例） | `examples/scalardl-architecture.py` |
| template.json のスキーマ | `references/template-schema.md` |
| API の制約・落とし穴 | `references/api-notes.md` |
| 登録済みテンプレート | `templates/*.json` |

---

## Phase 0: 前提確認

1. Python と依存パッケージ。venv は `google-slides` スキルと共有で、実体は `~/.claude/venvs/gslides`:

```bash
cd ~/.claude/skills/google-slides-template
.venv/bin/python -c "import googleapiclient; print('ok')"
```

壊れている・存在しない場合は共有 venv を作り直してリンクし直す:

```bash
python3 -m venv ~/.claude/venvs/gslides
~/.claude/venvs/gslides/bin/pip install -U -r ~/.claude/venvs/gslides-requirements.txt
for s in google-slides google-slides-template; do
  rm -rf ~/.claude/skills/$s/.venv
  ln -s ../../venvs/gslides ~/.claude/skills/$s/.venv
done
```

> 依存を追加するときは `~/.claude/venvs/gslides-requirements.txt` を編集する。両スキルの `requirements.txt` は記録用で、実際のインストール元ではない。

2. 認証: `config/credentials.json` または `~/.claude/skills/google-slides/config/credentials.json` が必要。無い場合は Google Cloud Console で OAuth 2.0 デスクトップクライアントを作成し、**Slides API と Drive API を有効化**してもらう。`token.json` は初回実行時に自動生成される。

3. **クラウド構成図を作る場合のみ**: AWS / Google Cloud / Azure の公式アイコンは
**各社の資産で再配布できないためリポジトリに同梱していない**。初回だけ取り込む。

```bash
.venv/bin/python scripts/fetch-cloud-icons.py          # 1〜2 分・約 8.6MB
.venv/bin/python scripts/fetch-cloud-icons.py --verify # 取り込み済みか確認
```

取り込み前に `cloud_icon` を使うと、この手順を案内するエラーで止まる。取り込んだ
素材はコミットしない（`.gitignore` 済み）。詳細は `references/cloud-icons.md`。

4. **テンプレートへのアクセス権**: 複製には Drive の閲覧＋コピー権限が必要。「ダウンロード・印刷・コピーを無効にする」設定の共有ファイルは複製できない。

---

## Phase 1: テンプレートの解析と登録

登録済みテンプレートがあれば `templates/` から選ぶ。無ければ URL から解析する。

```bash
.venv/bin/python scripts/inspect-template.py "<テンプレートURL>" \
    --emit templates/<id>.json --name <id> --thumbnails out/layouts
```

出力される `template.json` には、ページサイズ、カラースキーム、全レイアウトの
`layoutId` / プレースホルダ構成 / 要素座標 / 既定テキストスタイル / 装飾要素、
テンプレート同梱スライドの ID が入る。

### ロールの確認（必須・人手）

`roles` は表示名とプレースホルダ構成からの**推測**で、そのままでは信用できない。

1. `--thumbnails` で出力した PNG を Read ツールで開き、各レイアウトの実際の見た目を確認する
2. レポートの「候補 N 件、要確認」と「未割当のロール」を潰す
3. `template.json` の `roles` を編集して確定させ、`__roles_note` に確認日と判断理由を書く

標準ロール名: `COVER` / `SECTION` / `CONTENT` / `TITLE_ONLY` / `BLANK` / `CLOSING`。
テンプレートが用途別に系統を持つ場合（提案書用と登壇用など）は、`CONTENT_PRESENTATION`
のように独自ロールを足してよい。ロールは単なる別名で、レイアウトキーを直接指定することもできる。

> **同じレイアウトが複数の見た目を持つことがある。** 例えば「全面の白い矩形でマスターのフッターを覆う」レイアウトでは、テンプレート側で定義された著作権表記が表示されない。`decorations` に全面サイズの矩形があれば、それを疑うこと。

---

## Phase 2: デッキ仕様の作成

スライド構成を JSON で書く。

```json
{
  "title": "生成するプレゼンテーションのタイトル",
  "slides": [
    { "layout": "COVER", "title": "…", "subtitle": "…", "body": "2026年MM月DD日\n会社名", "notes": "スピーカーノート" },
    { "layout": "SECTION", "title": "セクション名", "body": "補足" },
    { "layout": "CONTENT", "title": "アクションタイトル", "body": ["項目1", "項目2"] },
    { "layout": "CLOSING" }
  ]
}
```

- `layout`: ロール名またはレイアウトキー
- `body`: 文字列（そのまま）または配列（改行で連結）
- `bodies`: 2カラム/3カラムのレイアウト用。`[["左の行1","左の行2"], ["右の行1"]]` のように書くと BODY の index 0,1,2… に順に流し込まれる。`body` とは排他
- `notes`: 任意。スピーカーノート
- **レイアウトが持たないプレースホルダを指定するとエラーになる。** どのレイアウトが何を持つかは `template.json` の `placeholders` を見る。`["TITLE","BODY","BODY#1"]` のように `#N` が付くものは複数カラム。

### タイトルの書き方

タイトルは「何を見せるか」ではなく「何が言えるか」を書く（アクションタイトル原則）。

- 悪い: 「売上推移」
- 良い: 「売上は3四半期連続で前年比 20% 成長」

### 本文の分量を見積もる

プレースホルダの既定フォントは手書き向けに大きめのことが多い。日本語の本文は `bodyFontSize` と `bodyLineSpacing` で調整する（スライド単位、または `defaults` で一括）。

```json
{ "defaults": { "bodyFontSize": 14, "bodyLineSpacing": 150 }, "slides": [ ... ] }
```

収まるかどうかは、この式で見積もる。**API は文字が溢れてもエラーを返さない**ので、生成前に計算しておく。

```
1行の高さ  = fontSize × 1.2 × (lineSpacing / 100)     ← 1.2 は ascent+descent 分
収容行数   = (body の h[in] − 0.05×2) × 72 ÷ 1行の高さ
1行の文字数 = (body の w[in] − 0.1×2) × 72 ÷ fontSize   ← 全角を 1、半角を 0.5 として数える
```

例（`scalar-2026` の CONTENT、body は 9.0 × 4.068 in、14pt / 150%）→ **11行が上限**。
折り返した行も 1 行として数えること。溢れるとフッターに重なって切れる。

### 生成前に必ず検証する

```bash
.venv/bin/python scripts/build-deck.py --template templates/<id>.json \
    --spec deck.json --dry-run
```

API を一切呼ばずに、レイアウト解決とプレースホルダ整合をチェックする。ここを通してから本番実行する。

---

## Phase 3: 生成

```bash
.venv/bin/python scripts/build-deck.py \
    --template templates/<id>.json --spec deck.json \
    --title "資料タイトル" [--folder "<DriveフォルダURLまたはID>"]
```

処理の流れ:

1. `drive.files().copy()` でテンプレートを複製
2. テンプレート同梱スライドを削除
3. `createSlide(layoutId)` + `placeholderIdMappings` でスライドを作り、`insertText` で埋める
4. ページ番号をテキストボックスで描画（`--no-page-numbers` で抑制）
5. `batchUpdate` を 500 件ずつ実行（一時的な 5xx / 429 は指数バックオフで再試行）
6. スピーカーノートと画像の寸法補正があれば、プレゼンを取得し直して 2 回目の
   `batchUpdate` で適用する（どちらも作成後にしか分からない情報を使うため）
7. 画像を一時アップロードしていれば Drive から削除し、公開共有を外す

**テンプレート側の装飾・ロゴ・フッターは複製で自動継承されるので、自前で描いてはならない**（二重描画になる）。`template.json` の `masterDecorations` は「何が既に描かれているか」の記録であって、描画指示ではない。

### 絵で見せる手段は 5 つある。まず用途で選ぶ

| 見せたいもの | 使うもの | 特徴 |
|---|---|---|
| 構造・手順・数値の関係 | `diagrams.Canvas`（下記「図解を描く」） | 正確。要素どうしの関係が保証される |
| 概念・比喩・登場人物 | `illustrations`（`icon_flow` / `pyramid` / `iceberg` …） | 図形で描く。**キー不要・毎回同じ絵**・テーマ配色 |
| 業務語彙のアイコン | `icons`（`asset_icon` / `asset_icon_flow` …） | ブランド素材 62 種。ブランド準拠。**通信が要る** |
| クラウド構成図 | `cloud_icons`（`cloud_icon` / `cloud_zone` …） | AWS/GCP/Azure 公式 1,757 種。**色・回転の変更は禁止**。通信が要る |
| 雰囲気・情景・表紙 | `images`（`ai_image` / `image`） | AI 生成か手持ちの画像 |

5 つとも同じ `Canvas` のメソッドなので、1 枚のスライドに混ぜて使える。
詳細は `references/images.md` / `references/icons.md` / `references/cloud-icons.md`、
実例は `examples/illustration-gallery.json` / `examples/icon-gallery.json` /
`examples/cloud-architecture.json`。

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

ブランドのアイコンは `assets/icons/` に 62 種（`evidence-chain` `data-bank`
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
図を座標へ展開して検査する。

```json
{ "layout": "TITLE_ONLY_PROPOSAL", "title": "…",
  "figures": [
    { "type": "icon_flow", "x": 0.5, "y": 1.3, "w": 9.0,
      "items": [["person", "利用者"], ["database", "台帳"]] },
    { "type": "asset_icon_flow", "x": 0.5, "y": 3.1, "w": 9.0,
      "items": [["personal-info", "個人情報"], ["data-bank", "情報銀行"]] }
  ] }
```

### 図解を描く

箇条書きだけで説明しきれない内容は `scripts/diagrams.py` の `Canvas` で図にする。
テンプレートの `colors` から配色を組み立てるため、テーマから外れない。

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

for msg in (d.audit_connectors()      # 浮いた線・埋まった線
            + d.audit_overlaps()      # 文字が図形に隠れている／文字どうしがぶつかっている
            + d.audit_text_fit()):    # 枠に対して文字が多すぎる
    print(msg)
```

**生成前にこの 4 つを必ず呼ぶ。** どれも座標だけで分かる不具合で、放っておくと
サムネイルを見るまで気づけない。

```python
for msg in (d.audit_bounds() + d.audit_connectors()
            + d.audit_overlaps() + d.audit_text_fit()):
    print(msg)
```

| 検査 | 拾うもの |
|---|---|
| `audit_bounds()` | スライドの外へ出た図形・線の端点 |
| `audit_connectors()` | 端点がどの図形にも接していない／図形に埋まっている矢印 |
| `audit_overlaps()` | 後から描いた図形に隠れた文字、ラベルどうしの衝突 |
| `audit_text_fit()` | 枠からはみ出して切れる文字と、最終行に 1 文字だけ残る折り返し |

`audit_bounds()` は複合パーツで効く。`pyramid` や `funnel` のように与えられた枠から
自分で座標を計算する部品は、**枠が正しくても中身が外へ突き抜ける**ことがあり、
図形単位で見ないと拾えない。

`audit_overlaps()` は Slides の描画順（後の要素が上）を使う。バナーやゾーンを
直前のブロックに重ねてしまう典型的な事故がこれで落ちる。入れ子（ゾーンの中に
中身を置く）は正常なので報告しない。

| 用途 | 使うもの |
|---|---|
| 図形 A → B。動かしても追従してほしい | `d.connect(a, b)` |
| 図形 A → B。辺にぴたりと合わせたい | `d.link(a, b)` |
| 経路の折れ点・軸・引き出し線 | `d.line(..., free=True)` |

`connect()` の接続サイトは位置関係から自動で決まる（0=上 1=左 2=下 3=右）。
`audit_connectors()` は、どの図形からも 0.22in 以上離れた端点と、図形の内部に
0.06in 以上食い込んだ端点を返す。ゾーンのような大きな容器とテキストボックスは
判定から外れる（矢印が容器の中を通るのは正常なため）。**生成前に必ず呼ぶこと。**

`d.P` はテンプレート由来のパレット（`primary` / `success` / `danger` / `info` / `muted` /
`surface` / `border` / `text`）。`readable_on()` で背景に応じた文字色を自動で選ぶ。

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
収まるよう自分で縮ませる（`stats` / `metric` は枠高からフォントサイズを算出している）。

**直線のアクセントバーを重ねる矩形は角を丸めない。** 上端・左端にバー（細い
`RECTANGLE`）を敷くカードは、本体も `RECTANGLE` で描く。角丸の縁と直線バーの端が
噛み合わず、不揃いに見える（`cards()` はこの規約で直角になっている）。バーを持たない
単独のチップ・帯は角丸のままでよい。

### レイアウトに収まらない内容を足す場合

プレースホルダだけで足りないときは、`build-deck.py` をライブラリとして使い、返ってきた `slideId` に対して図形を足す:

```python
import sys; sys.path.insert(0, "scripts")
from importlib.machinery import SourceFileLoader
bd = SourceFileLoader("bd", "scripts/build-deck.py").load_module()

template = bd.load_template("templates/<id>.json")
deck = bd.TemplateDeck.create(template, title="…", folder=None)
ref = deck.add_slide("CONTENT", title="…")
deck.requests.append({"createShape": {..., "elementProperties": {"pageObjectId": ref["slideId"], ...}}})
deck.add_page_numbers()
print(deck.commit())
```

座標は `template.json` の `layouts.<KEY>.elements` の `contentTop` 相当（`body` の y）と
フッター位置の間に収める。色は `colors` のキーを使い、テンプレートの配色から外れないようにする。

---

## Phase 4: 視覚的 QA（省略禁止）

```bash
.venv/bin/python scripts/fetch-thumbnails.py "<生成物のURL>" --out out/qa
```

出力された PNG を Read ツールで開き、最低限これを確認する:

- [ ] 文字がプレースホルダからはみ出していない・省略されていない
- [ ] テンプレートの装飾（帯・図形）とテキストが重なっていない
- [ ] ページ番号が正しい位置に出ている（2桁でも切れていない）
- [ ] ロゴ・フッターが二重に描かれていない
- [ ] 意図したレイアウトが使われている（Proposal 系と Presentation 系の取り違えなど）

問題があれば `deck.json` かレイアウト選択を直して**生成し直す**。既存の生成物を部分修正するより、
仕様を直して作り直すほうが速く、再現性がある。

不要になった生成物は Drive から削除する（`drive.files().delete(fileId=…)`）。検証で作った中間デッキを残さない。

---

## エラー対応

| 症状 | 原因と対処 |
|------|-----------|
| `プレゼンテーション ID を抽出できません` | URL の形が想定外。`/presentation/d/<ID>/` の `<ID>` を直接渡す |
| `credentials.json が見つかりません` | Phase 0 の認証設定。Slides API と Drive API の両方が有効か確認 |
| copy で 403 | テンプレートのコピー権限が無い。所有者に「閲覧者（コピー可）」を依頼 |
| `Invalid requests[N].createSlide: layout not found` | `template.json` が古い。テンプレートが編集された可能性。再解析する |
| ページ番号が出ない | Slides API は SLIDE_NUMBER プレースホルダを生成できない。`add_page_numbers()` を呼んでいるか確認 |
| フッターが二重 | テンプレート由来のフッターを自前でも描いている。自前描画をやめる |
| 文字が途中で切れる | プレースホルダの高さ不足。文量を減らすか、`BODY` を持つ別レイアウトに変える |

---

## ファイル構成

| パス | 役割 |
|------|------|
| `scripts/_auth.py` | OAuth 認証・単位変換・色変換・URL から ID 抽出 |
| `scripts/inspect-template.py` | テンプレート解析 → `template.json` 生成、レイアウトサムネイル取得 |
| `scripts/build-deck.py` | テンプレート複製 → デッキ生成（`TemplateDeck`）。仕様検証も担当 |
| `scripts/fetch-thumbnails.py` | 生成物のサムネイル取得（視覚 QA 用） |
| `scripts/diagrams.py` | 図解プリミティブ（`Canvas`）。フロー・カード・横棒グラフ・図形接続コネクタ（`connect` / `link`）・回転と半透明・自己点検（`audit_bounds` / `audit_connectors` / `audit_overlaps` / `audit_text_fit`） |
| `scripts/illustrations.py` | イメージ図（`IllustrationMixin`）。ピクトグラム 30 種と比喩図 12 種。図形だけで描くのでキーもネットワークも不要 |
| `scripts/icons.py` | アイコンライブラリ（`IconLibraryMixin`）。`assets/icons/` の SVG を色を変えて PNG に焼き、スライドへ貼る。検索・一覧の CLI も持つ |
| `scripts/cloud_icons.py` | クラウドアイコン（`CloudIconMixin`）。AWS/GCP/Azure の公式 SVG を**色を変えずに**焼いて貼る。検索 CLI も持つ |
| `scripts/images.py` | 画像（`ImageMixin`）。AI 生成（Gemini・キャッシュ付き）と、ローカル/URL/Drive の画像の挿入。単体 CLI としても動く |
| `scripts/colors.py` | 配色ユーティリティ（`Palette` / `lighten` / `readable_on`）。上記 4 つが共有する |
| `assets/icons/` | Scalar ブランドのアイコン 62 種（`icons.json` + `svg/` + 控えの `png/`） |
| `assets/brand/` | Scalar / ScalarDB / ScalarDL のロゴ（`logos/` `product-logos/`。PNG と SVG） |
| `assets/cloud-icons/` | AWS / Google Cloud / Azure の公式アイコン 1,757 種（`cloud-icons.json` + `<vendor>/<category>/*.svg`）。取り込みは google-slides スキルの `fetch-cloud-icons.py` |
| `references/template-schema.md` | `template.json` と デッキ仕様 JSON のスキーマ |
| `references/images.md` | イメージ図・画像の使い分けと全メソッドの一覧 |
| `references/icons.md` | アイコンライブラリの引き方・色・制約・素材の足し方 |
| `references/cloud-icons.md` | クラウドアイコンの引き方・作図 API・ライセンス条件・更新手順 |
| `references/api-notes.md` | Google Slides API の制約・実測で判明した落とし穴 |
| `examples/illustration-gallery.json` | 全ピクトグラム・全比喩図・画像配置を使ったデッキ仕様（動く実例） |
| `examples/icon-gallery.json` | 全アイコンと `asset_icon_*` の 5 メソッドを使ったデッキ仕様（動く実例） |
| `examples/cloud-architecture.json` | クラウド構成図（ゾーン・マルチクラウド・データフロー）のデッキ仕様（動く実例） |
| `examples/scalardb-architecture.py` | ScalarDB の構成図。クラウドアイコン + ロゴ + コネクタを Canvas で組む実例 |
| `examples/scalardl-architecture.py` | ScalarDL の構成図（4層 / Auditor 構成 / 改ざん検知の流れ）。3 系統のアイコンを混ぜる実例 |
| `templates/*.json` | 登録済みテンプレート |
| `templates/scalar-2026.json` | Scalar Slide Master 2026（8レイアウト・Proposal / Presentation の2系統） |
| `templates/scalar-2026-boilerplate.json` | Scalar Slide Master 2026 + 定型スライド12枚（会社概要・代表プロフィール・製品概要・導入顧客・事例など）。レイアウトは `scalar-2026` と完全に同一で、差分は同梱スライドのみ。`--keep-existing` で定型スライドを残して使う。2026-08-01 登録 |
| `templates/aixdevops.json` | AIxDevOps Theme（Scalar 共同ブランド。22レイアウト・2/3カラム・Proposal / Presentation の2系統・QR コード付き `CLOSING`。2026-08-01 再解析） |
| `templates/corporate.json` | Corporate Master（aixdevops から派生。ネイビー基調、ブランド要素を除去） |

## 既存テンプレートから配色違いの派生マスターを作る

Slides API は**マスター/レイアウトを新規作成できないが、既存のものは変更できる**（`references/api-notes.md` セクション1）。既に良いテンプレートがあれば、それを複製して配色とブランド要素だけ差し替えた派生マスターを作れる。`templates/corporate.json` はこの方法で `aixdevops` から作った。

手順:

1. `drive.files().copy()` でテンプレートを複製し、同梱スライドを全削除する
2. **ブランド固有の要素を `deleteObject` で消す**（ワードマーク、専用ロゴ、元デッキのスクリーンショット等）。objectId は Drive のコピーでも保持されるので、解析結果の ID をそのまま使える
3. **テーマ色を参照している要素を明示 RGB で上書きする**。`colorScheme` は API で変更できないため、`theme:ACCENT5` のままだと元の配色で解決されてしまう
4. `inspect-template.py` で解析 → `roles` を確認 → 登録
5. サムネイルで目視確認する

> **色を書き換える前に `propertyState` を必ず確認すること。** テンプレートには「色だけ入った透明な全面矩形」（`propertyState: NOT_RENDERED`）が置かれていることがあり、そこを塗ると不透明になってマスターのロゴ・フッターを覆い隠す。詳細は `references/api-notes.md` セクション 3b。

## `google-slides` スキルとの関係

`templates/scalar-2026.json` と、`google-slides` スキルの `templates/scalar/theme.json` は
**同じマスター（`1shiZp7…`）を指す**。役割が違うので両方存在する。

| | 本スキル | `google-slides` |
|---|---|---|
| 担当 | テンプレートのレイアウトにテキストを流し込む | コンポーザーでデザインを組む（36 スライドタイプ・インフォグラフィクス・アーキテクチャ図） |
| 生成起点 | マスター複製（`build-deck.py`） | `presentations().create()` + BLANK 描画 |
| 保持する情報 | レイアウト構造・座標・ロール割当 | 設計トークン（フォントサイズ階層・表スタイル・チャート色など） |

複製方式の生成は**本スキルにのみ実装がある**（`google-slides` 側の `create-from-master.py` は
本スキルへ統合済みで削除された）。

マスターを更新したときは両方を追従させる:

1. `scripts/inspect-template.py <URL> --emit templates/scalar-2026.json --name scalar-2026` で再解析
2. `roles` を再確認して確定
3. `google-slides` の `templates/scalar/theme.json` の `layouts.*.layoutId` と `master.sampleSlideIds` を突き合わせて更新
