---
name: google-slides-template
description: >-
  既存の Google Slides テンプレート（マスタースライド）を複製して、そのレイアウトに沿った
  プレゼンテーションを生成する。テンプレートの解析・登録（template.json）、デッキ生成、
  サムネイルによる視覚 QA までを扱う。テンプレートを使わずゼロからデザインする場合は
  google-slides スキルを使う。
  トリガー: "このテンプレートでスライドを作って", "マスタースライドから生成", "テンプレートを登録",
  "テンプレートを解析", "gslides-template", "create slides from this template",
  "use this master", Google Slides のテンプレート URL を渡された場合。
---

# テンプレート駆動 Google Slides 生成

## Important

- **このスキルの守備範囲**: 既存の Google Slides プレゼンテーションを**デザインの正**として複製し、そのレイアウトにテキストを流し込む。
- **すべてのコマンドはスキルディレクトリ（`~/.claude/skills/google-slides-template`）を cwd として実行する。** `scripts/…` `templates/…` `.venv/bin/python` の相対パスはここを起点に解決される。
- **対象外**:
  - テンプレートを持たずゼロからデザインを組む → `google-slides` スキル（コンポーザー・インフォグラフィクス）
  - Scalar の会社/製品/機能紹介デッキ → `scalar-product-slides` スキル（本スキルの上に載る専用ワークフロー）
  - PPTX ファイルの生成 → `document-skills:pptx`
  - テンプレート自体のデザイン変更 → **Slides API はマスター/レイアウトの作成・編集をサポートしない**。Google Slides の UI で行うこと。
- Python 3.10+ が必要。`.venv` は `~/.claude/venvs/gslides` への**シンボリックリンク**で、`google-slides` スキルと共有している。依存を変更すると両方に効く。
- 認証情報は `config/credentials.json` → `~/.claude/skills/google-slides/config/` の順に探索する。既存の `google-slides` スキルを設定済みならそのまま使える。
- **視覚確認を省略しない。** API のレスポンスが正常でも、文字のはみ出し・装飾との矢印が他の図形の上を横切っていないか、意味のうえで正しい図形に繋がっているかは判定できない。生成後は必ずサムネイルを取得して目視する。

## Quick Reference

| やること | コマンド |
|---------|---------|
| テンプレートを解析して登録 | `.venv/bin/python scripts/inspect-template.py <URL> --emit templates/<id>.json --name <id>` |
| レイアウトのサムネイル取得 | `.venv/bin/python scripts/inspect-template.py <URL> --thumbnails out/layouts` |
| デッキ仕様の検証（API 不要） | `.venv/bin/python scripts/build-deck.py --template … --spec … --dry-run` |
| デッキ生成 | `.venv/bin/python scripts/build-deck.py --template … --spec … --title "…"` |
| 生成物の視覚 QA | `.venv/bin/python scripts/fetch-thumbnails.py <URL> --out out/qa` |
| 画像を AI で生成 | `.venv/bin/python scripts/images.py --prompt "…" --style flat_vector --out out/x.png` |
| アイコンを探す | `.venv/bin/python scripts/icons.py --list` / `--search 情報銀行` |
| クラウドアイコンの取り込み（**初回必須**） | `.venv/bin/python scripts/fetch-cloud-icons.py` |
| クラウドアイコンを探す | `.venv/bin/python scripts/cloud_icons.py --search s3` / `--list --vendor aws` |
| 図解（`Canvas`）の描き方・作図規約 | `references/diagrams.md` |
| 表・グラフの使い方 | `references/charts.md` |
| 表・グラフのカタログ（仕様の実例） | `examples/charts-demo.json` |
| ビジネスフレームワーク図の使い方 | `references/patterns.md` |
| フレームワーク図のカタログ（仕様の実例） | `examples/patterns-demo.json` |
| コードサンプル（ハイライト付き）の使い方 | `references/code-blocks.md` |
| コードブロックのカタログ（仕様の実例） | `examples/code-blocks-demo.json` |
| デッキの構成テンプレート（新規事業提案の 15 セクション等） | `references/deck-outlines.md` |
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

壊れている・存在しない場合は共有 venv を作り直してリンクし直す。
`~/.claude/venvs/gslides-requirements.txt` が存在しない場合は、先にスキル同梱の
`requirements.txt` をコピーして種にする:

```bash
[ -f ~/.claude/venvs/gslides-requirements.txt ] || \
  cp ~/.claude/skills/google-slides-template/requirements.txt ~/.claude/venvs/gslides-requirements.txt
python3 -m venv ~/.claude/venvs/gslides
~/.claude/venvs/gslides/bin/pip install -U -r ~/.claude/venvs/gslides-requirements.txt
for s in google-slides google-slides-template; do
  rm -rf ~/.claude/skills/$s/.venv
  ln -s ~/.claude/venvs/gslides ~/.claude/skills/$s/.venv
done
```

> シンボリックリンクは**絶対パス**で張ること。スキルディレクトリ自体がシンボリックリンクの
> 環境では、相対パスのリンクは解決に失敗して壊れる。

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

5. **AI 画像生成（`ai_image` / 表紙画像）を使う場合のみ**、課金済みの `GEMINI_API_KEY` が必要（任意）。図形で描く `illustrations` / `patterns` はキー不要。

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

`.venv/bin/python scripts/layout-sample.py --template templates/<id>.json` で、全レイアウトに
サンプル文字列を流し込んだカタログデッキを生成できる。ロール割当の目視検証に使う。

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
`--strict` を併用すると、図の検査で警告が 1 件でも出たらエラー終了する（生成前の CI 的チェックに推奨）。

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

### 絵で見せる手段は 8 つある。まず用途で選ぶ

| 見せたいもの | 使うもの | 特徴 |
|---|---|---|
| 構造・手順・数値の関係 | `diagrams.Canvas`（`references/diagrams.md`） | 正確。要素どうしの関係が保証される |
| 表・グラフ（比較・推移・構成比） | `charts`（`table` / `vbars` / `vbars_stacked` / `linechart` / `pie` …） | 表はネイティブで後から編集可。基線ゼロ・系列色固定などの規約込み |
| 概念・比喩・登場人物 | `illustrations`（`icon_flow` / `pyramid` / `iceberg` …） | 図形で描く。**キー不要・毎回同じ絵**・テーマ配色 |
| ビジネスフレームワークの型 | `patterns`（`posmap` / `gantt` / `orgchart` / `lean_canvas` / `nested_circles` / `testimonial`） | 新規事業提案・稟議の定番図。キー不要・テーマ配色 |
| 業務語彙のアイコン | `icons`（`asset_icon` / `asset_icon_flow` …） | ブランド素材 62 種。ブランド準拠。**通信が要る** |
| クラウド構成図 | `cloud_icons`（`cloud_icon` / `cloud_zone` …） | AWS/GCP/Azure 公式 1,757 種。**色・回転の変更は禁止**。通信が要る |
| 雰囲気・情景・表紙 | `images`（`ai_image` / `image`） | AI 生成か手持ちの画像 |
| コードサンプル | `code_block`（java / graphql / json / bash） | 等幅 + VS Code Dark+ 風ハイライト。**角は直角** |

8 つとも同じ `Canvas` のメソッドなので、1 枚のスライドに混ぜて使える。デッキ仕様（JSON）
からは `figures` で使える。**描き方の詳細（コード例・部品一覧・作図とレイアウトの規約・
`build-deck.py` をライブラリとして使う方法）は `references/diagrams.md` を読むこと。**
ファミリー別の使い方は `references/charts.md` / `references/patterns.md` /
`references/images.md` / `references/icons.md` / `references/cloud-icons.md` /
`references/code-blocks.md`、実例は `examples/` の各デモ仕様。

### 図解の要点（詳細と根拠は `references/diagrams.md`）

- **生成前に audit 4 種を必ず呼ぶ。** `audit_bounds()`（枠外の図形）/ `audit_connectors()`（浮いた・埋まった矢印）/ `audit_overlaps()`（隠れた文字・ラベル衝突）/ `audit_text_fit()`（枠に対して文字が多すぎる）。どれも座標だけで分かる不具合で、放っておくとサムネイルを見るまで気づけない。
- **図形どうしを結ぶ線は座標で書かない。** 使い分けは次のとおり。

| 用途 | 使うもの |
|---|---|
| 図形 A → B。動かしても追従してほしい | `d.connect(a, b)` |
| 図形 A → B。辺にぴたりと合わせたい | `d.link(a, b)` |
| 経路の折れ点・軸・引き出し線 | `d.line(..., free=True)` |

- **回転した図形に文字を入れてはいけない。** 図形は `text` 無しで描き、`label()` を重ねる。
- **迷ったら `illustrations`。** オフラインで動き、テンプレートの配色に必ず従う。AI 生成（`ai_image`）だけは課金済みの `GEMINI_API_KEY` が要る。
- `--dry-run` は API を呼ばずに図を座標へ展開して検査する（`--strict` で警告 1 件でもエラー終了）。

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
| `RefreshError` / `invalid_grant` | 認証トークンの失効。`~/.claude/skills/google-slides/config/token.json` を削除して再実行するとブラウザで再認証される |
| copy で 403 | テンプレートのコピー権限が無い。所有者に「閲覧者（コピー可）」を依頼 |
| `Invalid requests[N].createSlide: layout not found` | `template.json` が古い。テンプレートが編集された可能性。再解析する |
| ページ番号が出ない | Slides API は SLIDE_NUMBER プレースホルダを生成できない。`add_page_numbers()` を呼んでいるか確認 |
| フッターが二重 | テンプレート由来のフッターを自前でも描いている。自前描画をやめる |
| 文字が途中で切れる | プレースホルダの高さ不足。文量を減らすか、`BODY` を持つ別レイアウトに変える |

**失敗時の原則**: 生成途中で失敗したデッキ（テンプレート複製済みのもの）は Drive から削除し、
仕様を直して**最初から作り直す**。中途半端な生成物への部分修正は再現性がなく、
複製方式の生成は再実行のほうが速い。

---

## ファイル構成

| パス | 役割 |
|------|------|
| `scripts/_auth.py` | OAuth 認証・単位変換・色変換・URL から ID 抽出 |
| `scripts/inspect-template.py` | テンプレート解析 → `template.json` 生成、レイアウトサムネイル取得 |
| `scripts/build-deck.py` | テンプレート複製 → デッキ生成（`TemplateDeck`）。仕様検証も担当 |
| `scripts/fetch-thumbnails.py` | 生成物のサムネイル取得（視覚 QA 用） |
| `scripts/layout-sample.py` | 全レイアウトを 1 枚ずつ並べたレイアウトサンプルの生成。ロール割当の目視検証に使う |
| `scripts/diagrams.py` | 図解プリミティブ（`Canvas`）。フロー・カード・横棒グラフ・図形接続コネクタ（`connect` / `link`）・回転と半透明・コードブロック（`code_block`。ハイライト付き・直角）・`font` 指定・自己点検（`audit_bounds` / `audit_connectors` / `audit_overlaps` / `audit_text_fit`） |
| `scripts/charts.py` | 表とグラフ（`ChartMixin`）。ネイティブテーブル・縦棒・グループ縦棒・積み上げ縦棒（`vbars_stacked`）・折れ線・円/ドーナツ。基線ゼロ・系列色固定（CVD 検証済み）などの規約を実装で強制する |
| `scripts/illustrations.py` | イメージ図（`IllustrationMixin`）。ピクトグラム 30 種と比喩図 12 種。図形だけで描くのでキーもネットワークも不要 |
| `scripts/patterns.py` | ビジネスフレームワーク図（`PatternMixin`）。posmap / gantt / orgchart / lean_canvas / nested_circles / testimonial の 6 種。キーもネットワークも不要 |
| `scripts/icons.py` | アイコンライブラリ（`IconLibraryMixin`）。`assets/icons/` の SVG を色を変えて PNG に焼き、スライドへ貼る。検索・一覧の CLI も持つ |
| `scripts/cloud_icons.py` | クラウドアイコン（`CloudIconMixin`）。AWS/GCP/Azure の公式 SVG を**色を変えずに**焼いて貼る。検索 CLI も持つ |
| `scripts/images.py` | 画像（`ImageMixin`）。AI 生成（Gemini・キャッシュ付き）と、ローカル/URL/Drive の画像の挿入。単体 CLI としても動く |
| `scripts/colors.py` | 配色ユーティリティ（`Palette` / `lighten` / `readable_on`）。diagrams / charts / illustrations / patterns / images の 5 つで共有 |
| `assets/icons/` | Scalar ブランドのアイコン 62 種（`icons.json` + `svg/` + 控えの `png/`） |
| `assets/brand/` | Scalar / ScalarDB / ScalarDL のロゴ（`logos/` `product-logos/`。PNG と SVG） |
| `assets/cloud-icons/` | AWS / Google Cloud / Azure の公式アイコン 1,757 種（`cloud-icons.json` + `<vendor>/<category>/*.svg`）。取り込みは `scripts/fetch-cloud-icons.py`（実体は google-slides スキル側と共有） |
| `references/template-schema.md` | `template.json` と デッキ仕様 JSON のスキーマ |
| `references/diagrams.md` | 図解の描き方（`Canvas`）。8 手段のコード例・線の接続・audit 4 種・配色とレイアウトの規約・ライブラリ利用 |
| `references/charts.md` | 表・グラフ（`charts.py`）の使い方と設計規約 |
| `references/patterns.md` | ビジネスフレームワーク図（`patterns.py`）の使い方 |
| `references/code-blocks.md` | コードブロック（`code_block`）の使い方と高さの見積もり |
| `references/deck-outlines.md` | デッキの構成テンプレート（新規事業提案の 15 セクション等） |
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
