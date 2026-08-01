---
name: google-slides
description: >-
  Google Slides プレゼンテーションおよびインフォグラフィクスを Python + Google Slides API で生成・編集する。
  トリガー: "Google Slides を作って", "スライドを生成", "gslides", "インフォグラフィクスを作って",
  "create Google Slides", "generate slides", "create infographic", Google Slides URL が含まれる場合。
---

# Google Slides プレゼンテーション生成

## Important

- **対象外**: PPTX ファイルの生成（pptx スキル）、Slidev（slidev スキル）
- **ルーティング**: 「スライド作って」のみの場合は Google Drive コンテキストが明示されている場合のみ本スキルを使用
- **`google-slides-template` スキルとの使い分け**:
  - ユーザーが**テンプレート／マスターの URL を持っている**、またはテンプレートのレイアウトに沿ってテキストを流し込むだけでよい → `google-slides-template`（テンプレート解析 → ロール割当 → 複製生成）
  - テンプレートが無い、あるいは**コンポーザー（36 種のスライドタイプ・インフォグラフィクス・アーキテクチャ図）でデザインを組む**必要がある → 本スキル
  - `scalar` テーマの複製方式による生成は `google-slides-template` に移管済み（`templates/scalar-2026.json`）。本スキルに実装は無い
- Python 3.10+ が必要。venv の使用を推奨
- Google Cloud プロジェクトで Slides API と Drive API を有効化済みであること
- OAuth 2.0 Desktop クライアントの credentials.json が配置済みであること
- デザイン原則は `references/design-principles.md` を参照。特に**アクションタイトル原則**と**WCAG コントラスト比**を厳守
- API パターンの詳細は `references/google-slides-api.md` を参照
- テーマファイルは `templates/<theme>/theme.json` に配置
  - **構造上の逸脱**: チェックリスト ST-07 は静的アセットに `assets/` を推奨するが、テーマ JSON はコード生成のテンプレートであり静的バイナリとは性質が異なるため、意図的に `templates/` を使用する
- 画像アセット（ロゴ、アイコン等）は `assets/` に配置。テーマ固有 → `shared/` の順で検索する
  - 対応フォーマット: PNG, JPEG, GIF（直接使用）、SVG（自動 PNG 変換、`cairosvg` 必要）
  - ローカルアセットは Drive API で一時アップロード → 公開 URL 取得 → スライド挿入 → クリーンアップ（`google-slides-api.md` セクション 12.1-12.5 参照）
- **アイコンは 3 系統ある。用途で選ぶ**
  - 汎用の図形 1〜2 個で足りる → `references/pictogram-catalog.md` のシェイプ（通信不要）
  - 業務語彙（情報銀行・証拠チェーン・内定 等）や社外向けの資料 → `assets/shared/icons/` の
    ブランド素材 62 種。`scripts/icons.py` の `IconLibraryMixin` を SlideBuilder に混ぜて
    `add_icon` / `add_icon_row` / `add_icon_flow` / `add_icon_grid` / `add_icon_cards` で置く
    （`references/icon-library.md`）
  - 実在するクラウドサービス（Amazon RDS・GKE・Cosmos DB 等）→ `assets/shared/cloud-icons/` の
    ベンダー公式 1,757 種。`scripts/cloud_icons.py` の `CloudIconMixin` を混ぜて
    `add_cloud_icon` / `_row` / `_flow` / `_grid` / `add_cloud_zone`（`references/cloud-icons.md`）
  - **クラウドアイコンは名前を推測しないこと。** `scripts/cloud_icons.py --search <語>` で引く。
    **色の変更・回転・反転は各社の利用条件で禁止**（API 側に引数を持たせていない）
  - **クラウドアイコンはリポジトリに同梱していない。** 各社の資産で再配布できないため、
    初回だけ `scripts/fetch-cloud-icons.py` で利用者の環境に取り込む（1〜2 分・約 8.6MB）。
    取り込み前に使うと手順を案内するエラーで止まる。`--verify` で取り込み済みか確認できる

## Quick Reference

| タスク | 参照先 |
|--------|--------|
| デザイン原則・定量基準 | `references/design-principles.md` |
| API パターン・SlideBuilder | `references/google-slides-api.md` |
| デザインレビュー | `references/review-checklist.md` |
| インフォグラフィクスパターン | `references/infographic-patterns.md` |
| テーマ管理（CRUD） | `references/theme-management.md` |
| マスターレジストリ（8種） | `references/master-registry.md` |
| スライドタイプ（36種） | `references/slide-types.md` |
| コンポーザー仕様 | `references/composers/{basic,content,product,usecase,enterprise,db-middleware}.md` |
| デッキパターン（5種） | `references/deck-patterns.md` |
| スライド選択ガイド | `references/slide-selection-guide.md` |
| ピクトグラムカタログ（シェイプで組む） | `references/pictogram-catalog.md` |
| アイコンライブラリ（ブランド素材62種） | `references/icon-library.md` |
| アイコンを探す | `scripts/icons.py --list` / `--search 情報銀行` |
| アイコンのカタログ生成（動く実例） | `scripts/generate-icon-gallery.py` |
| アーキテクチャ図ガイド | `references/architecture-diagram-guide.md` |
| クラウドアイコン（AWS/GCP/Azure 1,757種） | `references/cloud-icons.md` |
| クラウドアイコンを探す | `scripts/cloud_icons.py --search s3` / `--list --vendor aws` |
| クラウドアイコンの取り込み・更新（**初回必須**） | `scripts/fetch-cloud-icons.py` |
| クラウド構成図の生成（動く実例） | `scripts/generate-cloud-architecture.py` |
| 画像アセット（共通） | `assets/shared/{logos,product-logos,icons}/` |
| 画像アセット（テーマ別） | `assets/<theme>/{logos,product-logos,icons}/` |
| テストデータ（5パターン） | `references/test-data/` |
| Scalar ブランドテーマ | `templates/scalar/theme.json` |
| AI x DevOps Study テーマ | `templates/aixdevops/theme.json` |
| 汎用コーポレートテーマ | `templates/corporate/theme.json` |

---

## Phase 0: 環境セットアップ

### 前提条件の確認

1. Python 3.10+ がインストールされているか確認
2. Google Cloud Console で以下が有効か確認:
   - Google Slides API
   - Google Drive API
3. OAuth 2.0 Desktop クライアント ID を作成済みか確認

### credentials の配置

```bash
# スキル内の config/ ディレクトリに配置
# GCP Console からダウンロードした credentials.json を配置する
# config/credentials.json に配置する
# config/token.json は初回実行時に自動生成される
```

### 依存パッケージ

`.venv/` は `~/.claude/venvs/gslides` への**シンボリックリンク**で、`google-slides-template` スキルと共有している。

```bash
cd ~/.claude/skills/google-slides
.venv/bin/python -c "import googleapiclient; print('ok')"
```

壊れている・存在しない場合は共有 venv を作り直してリンクし直す:

```bash
python3 -m venv ~/.claude/venvs/gslides
~/.claude/venvs/gslides/bin/pip install -U -r ~/.claude/venvs/gslides-requirements.txt
for s in google-slides google-slides-template; do
  rm -rf ~/.claude/skills/$s/.venv
  ln -s ~/.claude/venvs/gslides ~/.claude/skills/$s/.venv
done
```

> 依存を追加するときは `~/.claude/venvs/gslides-requirements.txt` を編集する。本スキルの `requirements.txt` は記録用で、実際のインストール元ではない。`cairosvg`（SVG→PNG 変換）は既定で未インストールなので、SVG アセットを使う場合のみ `~/.claude/venvs/gslides/bin/pip install cairosvg` を実行する。

credentials.json が存在しない場合は、以下のメッセージをユーザーに提示し、配置確認が取れるまでスクリプト生成・実行を行わない:

> Google Slides の実行には `config/credentials.json` が必要です。GCP Console からダウンロードして `~/.claude/skills/google-slides/config/` に配置してください。

---

## Phase 1: テーマ読み込み

### テーマ管理（オプション）

テーマの作成・編集・削除・切替が必要な場合は `references/theme-management.md` を参照する。

- **テーマ作成**: `templates/<id>/theme.json` を新規作成 + `assets/<id>/` ディレクトリ整備
- **テーマ編集**: 既存の `theme.json` のカラーパレット・フォント・レイアウト座標を更新
- **テーマ削除**: `templates/<id>/` と `assets/<id>/` を削除
- **テーマ切替**: 下記のテーマ選択ステップでテーマ名を指定

### スライドマスター

スライドの種類（表紙、コンテンツ、引用、KPI 強調など）に応じて 8 種類のマスターを使い分ける。詳細は `references/master-registry.md` を参照。

| マスター | 用途 | フッター |
|---------|------|---------|
| COVER | 表紙 | なし |
| SECTION | セクション区切り | なし |
| CONTENT | 一般コンテンツ（最多使用） | ロゴ・著作権・ページ番号 |
| QUOTE | 引用・証言 | なし |
| HIGHLIGHT | KPI・数値強調 | なし |
| SPLIT_SCREEN | 左右分割（問題/解決など） | ロゴ・著作権・ページ番号 |
| CLOSING | 締め・お問い合わせ | なし |
| BLANK | 白紙・自由配置 | なし |

### デッキパターンの選定

スライドデッキ生成時は、まずデッキパターンを決定する。詳細は `references/deck-patterns.md` と `references/slide-selection-guide.md` を参照。

1. ユーザーリクエストからデッキパターンを判定する（`slide-selection-guide.md` セクション 2）

| パターン | 用途 | 枚数目安 |
|---------|------|---------|
| `initial_sales` | 初回営業訪問 | 15-20枚 |
| `technical_deep_dive` | 技術詳細・PoC | 20-25枚 |
| `executive_briefing` | 経営層向け | 8-12枚 |
| `use_case_specific` | 業界特化ユースケース | 15-20枚 |
| `partner_enablement` | パートナー向け | 15-20枚 |

2. 判定できない場合は、ユーザーに 1-2 問で確認する:
   - 「誰向けの、何についてのプレゼンですか？」→ 対象者+製品+業界が判明
   - 必要なら「デッキの目的を選択してください」で候補を提示
   - 回答が曖昧な場合は `initial_sales` をデフォルトとし、その旨をユーザーに通知する

3. パターンが決定したら、テンプレートのスライド構成を展開し、ユーザーリクエストに応じてカスタマイズする

### テーマファイルの選択

1. ユーザーにテーマを確認する（デフォルト: パターン推奨テーマ。未指定時は `scalar`）

| テーマ | 用途 | プライマリ | アクセント |
|--------|------|----------|----------|
| `scalar` | Scalar 社デフォルト。ScalarDB / ScalarDL 営業・技術資料向け（マスター複製方式） | Blue `#2673BB` | Green `#63C045` |
| `aixdevops` | AI x DevOps Study 勉強会・テック系イベント向け（Scalar 共同ブランド。マスター複製方式） | Blue `#2673BB` | Green `#63C045` |
| `corporate` | 汎用コーポレート。社外向け一般資料・提案書向け（マスター複製方式） | Navy `#1E3A5F` | Teal `#0D9488` |

> **Note**: `layouts` セクションの `layoutId` は各テーマのマスタースライドから抽出した値。3テーマとも `master.generationMode` は `"copy"` で、複製方式の実装は `google-slides-template` スキルにある。`CONTENT_ACCENT` / `CLOSING` が null のテーマ（`aixdevops` / `corporate`）は、マスターに該当レイアウトが無いことを示す。`source` が `null` のテーマはマスター未設定。

> **`scalar` テーマ v2.0.0（Scalar Slide Master 2026）**: マスターは `1shiZp7PWWMcpD5Yz2NfZ9Hmd5plZL_C_5ql3mK8yGsI`。`master.generationMode` が `"copy"` のため、**空プレゼンから描き起こすのではなくマスターを複製して生成する**（下記「マスター複製方式」参照）。レイアウトは Proposal 系（提案書・営業資料）と Presentation 系（登壇・勉強会）の2系統。旧マスター（`1TOz10qx…`）の layoutId とは互換性がなく、旧定義は `templates/scalar/theme.json.bak-1TOz10qx-20260729` に退避済み。

| テーマキー | レイアウト名 | 系統 | 用途 |
|-----------|------------|------|------|
| `COVER` | Title Slide | 共通 | 表紙。波装飾＋右上ロゴ |
| `SECTION` | Slide Sub Section | 共通 | 中扉。下線＋波＋左上ロゴ |
| `CONTENT` | Default - Proposal | proposal | 本文の既定。青アクセントバー＋© フッター |
| `CONTENT_ACCENT` | Default - Proposal | proposal | `CONTENT` のエイリアス（後方互換） |
| `TITLE_ONLY` | Title Only - Proposal | proposal | タイトルのみ（提案書系） |
| `CONTENT_PRESENTATION` | Default - Presentation | presentation | 本文。中央寄せタイトル、© なし |
| `TITLE_ONLY_PRESENTATION` | Title Only - Presentation | presentation | タイトルのみ（登壇系） |
| `BLANK` | White | 共通 | 白紙。全面図・インフォグラフィクス向け |
| `CLOSING` | Close Page | 共通 | 裏表紙。プレースホルダ無しの完成レイアウト |

   上記以外のテーマ名が指定された場合は、ユーザーに利用可能なテーマ一覧を提示し、選び直してもらう。

2. `templates/<theme>/theme.json` を Read ツールで読み込む
3. `masterFooter.copyright.text` が空の場合、ユーザーに著作権テキストを確認する（例: `"(C) 2026 Your Company, Inc."`）
4. ユーザーにカスタムアセットフォルダを確認する（省略可）

> アセット画像（ロゴ、アイコン等）を格納したフォルダがあれば指定してください。
> 指定フォルダのアセットが優先され、見つからない場合はスキルデフォルト（`assets/`）にフォールバックします。
> 未指定の場合はスキルデフォルトのみを使用します。

   - パスは絶対パスまたは `~` で始まるパス
   - フォルダ内の構造: `<theme>/<category>/<filename>` または `shared/<category>/<filename>`
   - 未指定の場合 `CUSTOM_ASSETS_DIR = None`

5. 出力先の Google Drive フォルダを確認する（省略可）

> プレゼンテーションを配置する Google Drive フォルダを指定してください。
> フォルダ名、フォルダ URL、またはフォルダ ID で指定できます。
> 未指定の場合はマイドライブのルートに作成されます。

   - URL 例: `https://drive.google.com/drive/folders/1ABC...XYZ`
   - フォルダ名例: `営業資料`
   - 未指定の場合 `OUTPUT_FOLDER_ID = None`

6. テーマから以下を展開する:
   - **C クラス**（色定数）: `colors` セクションから `hex_to_rgb()` で変換
   - **L クラス**（レイアウト定数）: `layouts.CONTENT.elements` から座標を取得
   - **フォント設定**: `fonts` セクションからフォントファミリーを取得

### アセット解決

ロゴやアイコンの画像をスライドに挿入する場合、以下の順でアセットを検索する:

1. `<custom_assets>/<theme>/<category>/<filename>` — ユーザー指定（テーマ固有）
2. `<custom_assets>/shared/<category>/<filename>` — ユーザー指定（共通）
3. `assets/<theme>/<category>/<filename>` — スキルデフォルト（テーマ固有）
4. `assets/shared/<category>/<filename>` — スキルデフォルト（共通）

`CUSTOM_ASSETS_DIR` が未指定の場合、検索順 1-2 はスキップされる。

カテゴリ: `logos`（会社ロゴ）、`product-logos`（製品ロゴ）、`icons`（汎用アイコン）

SVG ファイルは自動的に PNG 変換される（`cairosvg` 必要）。詳細は `references/google-slides-api.md` セクション 12.3 参照。

### テーマの C/L クラス展開例

```python
# theme.json の colors セクションから
class C:
    primary     = hex_to_rgb(theme["colors"]["primary"])
    textTitle   = hex_to_rgb(theme["colors"]["textTitle"])
    textPrimary = hex_to_rgb(theme["colors"]["textPrimary"])
    # ... 他の色も同様

# theme.json の layouts.CONTENT.elements から
class L:
    MX      = theme["layouts"]["CONTENT"]["elements"]["title"]["x"]
    titleX  = theme["layouts"]["CONTENT"]["elements"]["title"]["x"]
    titleY  = theme["layouts"]["CONTENT"]["elements"]["title"]["y"]
    titleW  = theme["layouts"]["CONTENT"]["elements"]["title"]["w"]
    # ... 他のレイアウト定数も同様
```

---

## Phase 2: コード生成

### 出力タイプの判定

ユーザーのリクエストから出力タイプを判定する:

- **スライドデッキ** → デッキパターンテンプレートからスライド構成を展開（`references/deck-patterns.md` 参照）
- **インフォグラフィクス** → カスタムページサイズを選択（`references/google-slides-api.md` セクション17）+ `references/infographic-patterns.md` のコンポジットパターンを使用

インフォグラフィクスの判定基準: 「インフォグラフィクス」「infographic」の明示的な言及、A4/ポスター等の縦長レイアウト指定、データビジュアライゼーション中心の要求。

### デッキパターンからスライド構成の展開

スライドデッキの場合、Phase 1 で決定したデッキパターンのテンプレートからスライド構成を展開する:

1. `references/deck-patterns.md` からパターンの必須/オプションスライド一覧を取得
2. ユーザーリクエストに基づきオプションスライドを追加/削除（`references/slide-selection-guide.md` セクション 4）
3. 各スライドタイプの JSON スキーマを `references/slide-types.md` から取得
4. 各スライドのコンポーザー仕様を `references/composers/<category>.md` から参照してコードを生成

### マスター複製方式（`master.generationMode` が `"copy"` のテーマ）

テーマに `master.presentationId` があり `generationMode` が `"copy"` の場合（`scalar` v2.0.0 以降）、空のプレゼンテーションを作るのではなく、**マスターを複製してから `createSlide(layoutId)` でスライドを積む**方式が正しい。マスターが定義する装飾・ロゴ・© フッターがレイアウトから自動継承されるため、これらを自前で描画してはならない（二重描画になる）。

**この方式の実装は `google-slides-template` スキルに移管済み。** 本スキルには実装を持たない。

```bash
cd ~/.claude/skills/google-slides-template
.venv/bin/python scripts/build-deck.py --template templates/scalar-2026.json \
    --spec deck.json --dry-run                     # 仕様検証（API 呼び出しなし）
.venv/bin/python scripts/build-deck.py --template templates/scalar-2026.json \
    --spec deck.json --title "提案書タイトル" [--folder <URL または ID>]
```

`templates/scalar-2026.json` は本スキルの `templates/scalar/theme.json` と同じマスター（`1shiZp7…`）を指し、レイアウト対応も一致している。役割分担は次の通り:

| | `google-slides`（本スキル） | `google-slides-template` |
|---|---|---|
| 担当 | デザインを組む（36 スライドタイプ・インフォグラフィクス・アーキテクチャ図） | テンプレートのレイアウトにテキストを流し込む |
| 配色・座標の正 | `templates/scalar/theme.json` | `templates/scalar-2026.json` |
| 生成起点 | `presentations().create()` + BLANK 描画 | マスター複製 |

デッキ仕様の書き方、ロール割当、API の制約（`SLIDE_NUMBER` プレースホルダは生成できない、など）は `~/.claude/skills/google-slides-template/references/` を参照する。

### SlideBuilder パターンの使用

コンポーザーでデザインを組む場合（インフォグラフィクス、カスタムページサイズ、`source` が `null` のテーマ）は、`references/google-slides-api.md` の SlideBuilder クラスパターンに従い、Python スクリプトを生成する。

### 生成スクリプトの構造

```python
#!/usr/bin/env python3
"""[タイトル] 生成スクリプト (Google Slides API)"""

# 1. インポートとセットアップ（google-slides-api.md セクション1）
# 2. ヘルパー関数（google-slides-api.md セクション3-4）
# 3. テーマ定数 C / レイアウト定数 L（Phase 1 で展開）
#    CUSTOM_ASSETS_DIR = "/path/to/custom/assets" or None（Phase 1 Step 4）
#    OUTPUT_FOLDER_ID = "folder_id" or None（Phase 1 Step 5）
# 4. SlideBuilder クラス（google-slides-api.md セクション5-6）
# 5. main() でスライドを構築（google-slides-api.md セクション7）
```

### ローカルアセットの挿入

ロゴやアイコン画像をスライドに挿入する場合、`add_image_from_asset()` を使用する（`google-slides-api.md` セクション 12.4 参照）。

`CUSTOM_ASSETS_DIR` が指定されている場合、`sb.custom_assets_dir` に設定することでカスタムアセットが優先検索される。

```python
# カスタムアセットフォルダが指定されている場合
sb.custom_assets_dir = CUSTOM_ASSETS_DIR  # None でも可

# ローカルアセットをスライドに挿入（カスタム → スキルデフォルトの順で検索）
sb.add_image_from_asset(sid, "scalar", "logos", "scalar-logo.png",
                        0.3, 0.2, 1.0, 0.5)

# main() の最後で必ずクリーンアップ
sb.cleanup_uploaded_assets()
```

CDN URL が利用可能な場合は従来の `add_image()` を優先する。ローカルアセットは CDN にない画像（ブランドロゴ、カスタムアイコン等）に使用する。

### デザイン原則の適用（必須）

コード生成時に以下を厳守する（`references/design-principles.md` 参照）:

1. **アクションタイトル**: 全コンテンツスライドのタイトルは結論文にする（ラベル型禁止）
2. **フォントサイズ**（営業/トレーニング資料基準）: 本文 >= 12pt、タイトル >= 20pt、著作権/ページ番号 >= 7pt、ソース出典 >= 10pt（詳細は `references/design-principles.md` セクション2・8参照）
3. **コントラスト比**: 通常テキスト 4.5:1 以上（WCAG AA）
4. **コンテンツ密度**: 箇条書き最大6個、1スライド=1メッセージ
4.5. **コネクタ**: 図形どうしを結ぶ線は座標で直接書かず、シェイプ接続コネクタ
   （`add_connected_connector`。`startConnection` / `endConnection` で図形に紐づく）を使う。
   Slides API は線の座標を検証しないため、端点がずれていてもエラーにならず、
   サムネイルを見るまで「矢印が図形から浮いている」ことに気づけない。
   軸・目盛り・引き出し線など図形に接しないのが正しい線は、その旨をコメントで明示する
5. **カラー**: 60-30-10 ルール、1スライド最大3色
6. **日本語タイポグラフィ**: 行間 185-200%、1行 30-35文字

### テキスト制約

| 要素 | 日本語上限 | 英語上限 |
|------|-----------|---------|
| 表紙タイトル | 16文字 | 40文字 |
| アクションタイトル | 50文字 | 100文字 |
| ブレット項目 | 40文字 | 80文字 |
| スピーカーノート | 200文字 | 400文字 |

---

## Phase 3: 実行

### スクリプトの実行

```bash
# venv をアクティベートして実行
source .venv/bin/activate
python generate-slides.py
```

### 初回実行時

- ブラウザが開き、Google アカウントでの認証を求められる
- 認証後、`config/token.json` が自動生成される
- 次回以降は token.json を使って自動認証

### 出力先フォルダへの配置

`OUTPUT_FOLDER_ID` が指定されている場合、スクリプト実行後にプレゼンテーションを指定フォルダに移動する（`google-slides-api.md` セクション 12.6 参照）。

```python
# スクリプト実行後
if OUTPUT_FOLDER_ID:
    move_to_folder(drive_service, pres_id, OUTPUT_FOLDER_ID)
```

### 出力

- コンソールに Google Slides の URL が表示される
- URL をユーザーに提示する

---

## Phase 4: 視覚的 QA

### サムネイル取得

生成したプレゼンテーションの各スライドのサムネイルを取得してレビューする。

```python
# サムネイル取得の方法は google-slides-api.md セクション10 を参照
```

### サブエージェントによるレビュー

1. サムネイル PNG を取得
2. 各スライドの画像を確認し、以下をチェック:
   - テキストがスライド境界内に収まっているか
   - フォントサイズが適切か（小さすぎないか）
   - カラーの一貫性
   - テキストの不自然な折り返しがないか
3. 問題がある場合はスクリプトを修正して再実行（例: テキストが枠外にはみ出している → フォントサイズ縮小、要素が重なっている → 座標調整、色が見にくい → コントラスト比修正）

### 修正ループ

問題を発見 → スクリプト修正 → 再実行 → サムネイル再取得 → 確認、を必要に応じて繰り返す。

---

## Phase 5: デザインレビュー（オプション）

ユーザーが求めた場合、または高品質が必要な場合に実施する。

### レビュー手順

`references/review-checklist.md` に従い、4ステップでレビューを実施:

1. **サムネイル俯瞰**: 全スライドの視覚的リズム確認
2. **ストーリーラインテスト**: アクションタイトルの論理的流れ確認
3. **個別チェック**: フォントサイズ、コントラスト比、コンテンツ密度の定量チェック
4. **スクイントテスト**: 目を細めて視覚的階層を確認

### レビュー出力

`references/review-checklist.md` の出力テンプレートに従い、以下を報告:
- 総合評価表（6カテゴリ）
- 定量サマリー
- 指摘一覧（Critical / Major / Minor）
- 改善優先度

---

## Dependencies

### 必須

| パッケージ | バージョン | 用途 |
|-----------|-----------|------|
| google-auth-oauthlib | >=1.2.0 | OAuth 2.0 認証 |
| google-auth-httplib2 | >=0.2.0 | HTTP トランスポート |
| google-api-python-client | >=2.120.0 | Google API クライアント |

### オプション

| パッケージ | 用途 |
|-----------|------|
| gspread | Sheets API でチャートデータを管理する場合 |
| cairosvg | SVG → PNG 変換（`assets/` の SVG アセット使用時） |

### ファイル

| ファイル | 必須 | 用途 |
|---------|------|------|
| `config/credentials.json` | Yes | OAuth クライアント設定 |
| `config/token.json` | Auto | アクセス/リフレッシュトークン（自動生成） |

---

## スキル内ファイル

| ファイル | 行数 | 内容 |
|---------|------|------|
| `SKILL.md` | ~450 | メインエントリポイント（本ファイル） |
| `references/design-principles.md` | ~400 | デザイン原則クイックリファレンス |
| `references/google-slides-api.md` | ~1770 | API パターン・SlideBuilder ガイド（全141シェイプタイプ、シェイプ接続コネクタ、アセット管理対応） |
| `references/infographic-patterns.md` | ~1040 | インフォグラフィクス用コンポジットパターン（12種＋外部画像ガイド） |
| `references/review-checklist.md` | ~170 | デザインレビューチェックリスト |
| `references/theme-management.md` | ~320 | テーマ CRUD ワークフロー・theme.json スキーマ |
| `references/master-registry.md` | ~610 | 8マスター定義・コンポジットパターン関数・選択ロジック |
| `references/slide-types.md` | ~800 | 36スライドタイプレジストリ・JSON スキーマ・テキスト制約 |
| `references/composers/basic.md` | ~310 | 基本コンポーザー6種（title, agenda, section_divider, summary, closing, appendix） |
| `references/composers/content.md` | ~460 | コンテンツコンポーザー9種（text_bullets, columns, chart, table, kpi_highlight 等） |
| `references/composers/product.md` | ~910 | 製品コンポーザー7種（product_overview, architecture, feature_matrix 等） |
| `references/composers/usecase.md` | ~820 | ユースケースコンポーザー6種（usecase_overview, problem_solution, case_study 等） |
| `references/composers/enterprise.md` | ~500 | エンタープライズコンポーザー4種（security_compliance, ecosystem, support_sla, pricing） |
| `references/composers/db-middleware.md` | ~710 | DB/ミドルウェアコンポーザー4種（data_flow, multi_cloud, benchmark, migration_path） |
| `references/deck-patterns.md` | ~560 | 5デッキパターン構成テンプレート・カスタマイズルール・ストーリーライン設計原則 |
| `references/slide-selection-guide.md` | ~510 | デッキパターン判定ロジック・スライドタイプ選定ヒューリスティクス・ヒアリングフロー |
| `references/pictogram-catalog.md` | ~1840 | 40+ピクトグラム（7カテゴリ）・コンポジット構築・テーマカラー適用・サイズガイドライン |
| `references/architecture-diagram-guide.md` | ~1660 | クラウド構成図ガイド・色コーディング・コネクタ・ゾーン描画・5典型パターン・E2E例 |
| `references/test-data/` | — | テスト用 slide_content.json（5パターン×テーマ）+ ガイド |
| `assets/` | — | 画像アセット（テーマ別・共通のロゴ、製品ロゴ、アイコン） |
| `references/cloud-icons.md` | ~180 | クラウドアイコンの引き方・作図 API・ライセンス条件・素材の更新手順 |
| `references/icon-library.md` | ~150 | Scalar ブランドアイコン 62 種の引き方・色・制約 |
| `assets/shared/cloud-icons/` | — | クラウドベンダー公式アイコン 1,757 種（SVG + マニフェスト） |
| `assets/shared/icons/` | — | Scalar ブランドのピクトグラム 62 種（SVG + PNG + マニフェスト） |
| `fetch-thumbnails.py` | ~90 | サムネイル取得スクリプト（視覚的 QA 用） |
| `scripts/generate-pattern-showcase.py` | ~2500 | 全パターンショーケース生成スクリプト |
| `scripts/fetch-cloud-icons.py` | ~380 | クラウドアイコンの取り込み・更新（URL 解決 + マニフェスト生成。両スキルへ配置） |
| `scripts/cloud_icons.py` | ~400 | クラウドアイコンの検索 CLI と `CloudIconMixin` |
| `scripts/icons.py` | ~430 | Scalar アイコンの検索 CLI と `IconLibraryMixin` |
| `scripts/generate-icon-gallery.py` | ~300 | Scalar アイコンのカタログ生成（動く実例） |
| `scripts/generate-cloud-architecture.py` | ~160 | クラウド構成図の生成（動く実例） |
| `requirements.txt` | ~10 | Python 依存パッケージ一覧 |
| `config/credentials.json` | — | OAuth クライアント設定（ユーザー配置） |
| `config/token.json` | — | アクセス/リフレッシュトークン（自動生成） |
| `templates/scalar/theme.json` | ~295 | Scalar ブランドテンプレート |
| `templates/aixdevops/theme.json` | ~295 | AI x DevOps Study テーマ |
| `templates/corporate/theme.json` | ~295 | 汎用コーポレートテーマ |

### 読み込み優先度

- **常に読む**: `SKILL.md`（本ファイル）
- **デッキパターン選定時に読む**: `references/deck-patterns.md` + `references/slide-selection-guide.md`
- **コード生成時に読む**: `references/google-slides-api.md` + `references/design-principles.md`
- **マスター選択時に読む**: `references/master-registry.md`
- **スライドタイプ選定時に読む**: `references/slide-types.md`
- **コンポーザー実装時に読む**: `references/composers/<category>.md`（該当カテゴリのみ）
- **ピクトグラム使用時に読む**: `references/pictogram-catalog.md`
- **アーキテクチャ図作成時に読む**: `references/architecture-diagram-guide.md` + `references/google-slides-api.md` セクション 8（コネクタ）
- **インフォグラフィクス生成時に読む**: `references/infographic-patterns.md` + `references/google-slides-api.md`
- **アセット挿入時に読む**: `references/google-slides-api.md` セクション 12.1-12.5
- **テーマ管理時に読む**: `references/theme-management.md`
- **テーマ適用時に読む**: `templates/<theme>/theme.json`
- **レビュー時に読む**: `references/review-checklist.md`
- **クラウドアイコン使用時**: `assets/shared/cloud-icons/` + `references/google-slides-api.md` セクション 12.4
- **テスト・検証時に読む**: `references/test-data/test-data-guide.md` + 該当パターンの JSON
- **ショーケース生成**: `source .venv/bin/activate && python scripts/generate-pattern-showcase.py`

不要なファイルは読み込まず、必要になった時点で Read ツールで参照する。
