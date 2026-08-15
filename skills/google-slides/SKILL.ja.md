---
name: google-slides
description: >-
  Generate Google Slides presentations and infographics from scratch (no registered
  corporate master) with Python + the Google Slides API, using the shared slide-forge
  engine: spec-driven decks on a blank 16:9 template, or code-first decks with offline
  layout validation for diagram-heavy material.
  Triggers: "Google Slides を作って", "スライドを生成", "gslides", "インフォグラフィクスを作って",
  "create Google Slides", "generate slides", "create infographic", or when a Google Slides
  URL is included.
---
*[English](SKILL.md)*

# Google Slides 生成（ゼロから）

Claude Code を主ホストとする。Codex と Antigravity も同じ共有スキルを利用する。
このファイルを最後まで読んだ後、`references/workflow-contract.md` に従う。機能表に
載るreferenceを事前に全件読み込まない。

## 重要事項

- **スコープ**: 登録済みコーポレートマスターを使わずにデッキを構築する。パスは 2 つあり、どちらも本リポジトリの共有エンジン上で動く:
  - **仕様パス** — `templates/blank-16x9.json` + `scripts/build_deck.py --spec deck.json`。テキスト・図表中心の典型的なデッキ向け
  - **コードファーストパス** — デッキを Python モジュール（`deckkit.py`）として書き、座標をオフラインで検証してから `scripts/render_deck.py` でレンダリングする。図の多い素材向け
- **ルーティング**:
  - ユーザーがテンプレート/マスターの URL を持っている、または既存のコーポレートレイアウトにテキストを流し込みたい → `google-slides-template` スキル
  - Scalar の会社・製品・ユースケースデッキ → `scalar-product-slides` スキル
  - 高密度なクラウドアーキテクチャ / データフロー / ネットワーク図（入れ子コンテナ、10 ノード以上）→ `drawio-diagrams` スキルで作図する（draw.io → PNG → 挿入）。単純な概念図は `diagrams.py` のままでよい
  - PPTX ファイルをゼロから作る → `document-skills:pptx`（ここで生成したデッキの `.pptx` への書き出し → `pptx-export` スキル）
  - 単なる「スライドを作って」という依頼にこのスキルを使うのは、Google Drive / Google Slides の文脈が明示されているときだけ
- **作業ディレクトリ**: slide-forge のルート — インストール済みプラグインから実行する場合は `${CLAUDE_PLUGIN_ROOT}`、ローカルクローンでは `/path/to/slide-forge`。以下のコマンドはすべてそこから実行する（リテラルのパスはローカルクローンを前提とする）。
- **認証**は `scripts/_auth.py` に集約されている。`credentials.json` / `token.json` は `$GSLIDES_CONFIG_DIR` → リポジトリルートの `config/`（正規の場所）→ 旧スキルレイアウト（移行期のフォールバック）の順で探索される。スクリプトごとのインライン認証は決して書かない。
- **ビジュアル QA は独立したスキル（`slide-qa`）であり、生成時に実行するかどうかを選ぶ**（Phase 5）。既定は実行 — 尋ねる際（Phase 1）には実行を推奨する。API レスポンスが正常でも、はみ出しや外れた矢印は分からないからだ。ユーザーが実行しないことを選んだ場合は Phase 5 をスキップし、レポートにデッキが未検証である旨を明記し、フォローアップとして `slide-qa` を提案する。QA を実行した場合は、最後にローカルの QA ファイルを削除して終える（`scripts/cleanup_qa.py`）。
- QA で不合格になったら、**壊れたプレゼンテーションを削除し、修正した仕様/モジュールから再生成する**。生成済みの実物デッキを API の差分編集でパッチしてはならない。
- 削除して再生成する規則が適用されるのは、現在のセッションで生成したデッキだけである。**ユーザーが既に持っている既存デッキを更新する場合**（同じ URL を保ったままスライドをその場で挿入・修正する場合）は、先に `scripts/snapshot_version.py <URL>` を実行して編集前のリビジョンを記録し（keepForever ピンの試行 + ローカル PPTX バックアップ）、リビジョン ID をユーザーに報告してから編集に入る。ロールバックは Slides UI の「ファイル → 変更履歴」から行う。

## クイックリファレンス

| タスク | 場所 |
|------|-------|
| JSON 仕様からビルド | `scripts/build_deck.py` + `templates/blank-16x9.json` |
| デッキを Python で書く | `scripts/deckkit.py`（+ `examples/pattern-gallery/deck.py`、`examples/scalardb-scalardl/deck.py`） |
| レイアウトをオフラインで検証（API 不要） | `scripts/validate_layout.py` + `references/layout-contract.md` |
| Python デッキをレンダリング | `scripts/render_deck.py` |
| ビジュアル QA（任意、既定: 実行） | `slide-qa` スキル（`scripts/fetch_thumbnails.py` + チェックリスト + クリーンアップ） |
| 検証完了後にローカル QA ファイルを削除 | `scripts/cleanup_qa.py` |
| 既存デッキ編集前のバージョンスナップショット | `scripts/snapshot_version.py` |
| 図（フロー、アーキテクチャ） | `scripts/diagrams.py`（Canvas）+ `references/diagrams.md`、`references/diagram-cookbook.md` |
| 高密度なクラウド/データフロー図（draw.io → PNG） | `drawio-diagrams` スキル + `scripts/drawio_export.py` + `references/drawio.md` |
| デッキごとの Drive フォルダ（作成 / ファイル収集） | `scripts/drive_folder.py` |
| チャートと表 | `scripts/charts.py` + `references/charts.md` |
| 図形描画のピクトグラムとメタファー図 | `scripts/illustrations.py` + `references/pictogram-catalog.md` |
| ビジネスフレームワーク図（posmap、gantt、orgchart…） | `scripts/patterns.py` + `references/patterns.md` |
| ページ骨格と分析図 | `scripts/pages.py` + `references/slide-patterns.md` |
| Scalar ブランドピクトグラム | `scripts/icons.py` + `assets/scalar/pictograms` + `references/icons.md` |
| クラウドベンダーアイコン（AWS/GCP/Azure） | `scripts/cloud_icons.py` + `assets/cloud-icons` + `references/cloud-icons.md` |
| クラウドアイコンの復元（初回） | `scripts/fetch_cloud_icons.py` |
| AI 生成画像（表紙、セクションアート） | `scripts/images.py`（`GEMINI_API_KEY` が必要）+ `references/images.md` |
| API の落とし穴 | `references/google-slides-api.md`、`references/api-notes.md` |
| デッキ構成のレシピ | `references/composers/{basic,content,product,usecase,enterprise,db-middleware}.md` |

---

## Phase 0: 環境確認

1. **venv** — リポジトリルートの `.venv` は共有 venv `~/.claude/venvs/gslides` へのシンボリックリンクである。次で確認する:

   ```bash
   cd /path/to/slide-forge
   .venv/bin/python -c "import googleapiclient; print('ok')"
   ```

   壊れている・存在しない場合は、共有 venv を再構築してリンクし直す。
   `~/.claude/venvs/gslides-requirements.txt` が存在しない場合は、先にリポジトリの
   `requirements.txt` から種を作る（リポジトリ側のファイルは記録であって実際の
   インストール元ではない — 依存を追加するときは
   `~/.claude/venvs/gslides-requirements.txt` を編集する）:

   ```bash
   [ -f ~/.claude/venvs/gslides-requirements.txt ] || \
     cp /path/to/slide-forge/requirements.txt ~/.claude/venvs/gslides-requirements.txt
   python3 -m venv ~/.claude/venvs/gslides
   ~/.claude/venvs/gslides/bin/pip install -U -r ~/.claude/venvs/gslides-requirements.txt
   rm -rf /path/to/slide-forge/.venv
   ln -s ~/.claude/venvs/gslides /path/to/slide-forge/.venv
   ```

   シンボリックリンクは**絶対パス**で作ること — ディレクトリ自体がシンボリックリンクの
   環境では、相対リンクは解決に失敗する。

2. **認証情報** — `config/credentials.json` が存在することを確認する（OAuth 2.0 デスクトップクライアント。GCP プロジェクトで Slides API と Drive API が有効化済みであること）。`config/token.json` は初回実行時にブラウザ認証フローで作成される。`credentials.json` がない場合は停止してユーザーに配置を依頼する — 確認できるまでは何も生成・実行しない。

3. **任意の機能**（デッキが必要とする場合のみ確認する）:
   - クラウドアイコン: 同梱されていない（ベンダーのライセンス条項が再配布を禁じている）。`.venv/bin/python scripts/cloud_icons.py --list --vendor aws | head` で確認し、なければ `.venv/bin/python scripts/fetch_cloud_icons.py` を一度実行する（約 1〜2 分）。
   - AI 画像: `images.py` には `GEMINI_API_KEY` が必要（環境変数、または gitignore 済みの `config/gemini_api_key` ファイル）。未設定なのにデッキが生成画像を求める場合は、`illustrations.py` にフォールバックするかユーザーに確認する。

---

## Phase 1: パスの選択

| | 仕様パス | コードファーストパス |
|---|---|---|
| 記述するもの | `deck.json`（JSON 仕様） | `deck.py`（Python モジュール） |
| 向いているもの | 典型的なデッキ: テキストページ、標準的な図、チャート、ページパターン | コネクタの多いアーキテクチャ図、高密度なカスタム描画、端点や重なりの精度が問われるすべて |
| 検証 | `build_deck.py --dry-run --strict` | `validate_layout.py`（オフラインの形状チェック） |
| 生成 | `build_deck.py` | `render_deck.py` |

指針: 既定は**仕様パス**。コネクタの多いアーキテクチャ/フロー図が中心のデッキでは**コードファースト**に切り替える — オフラインバリデータは、仕様の dry-run では見えないコネクタ端点・重なり・はみ出しを検査できる。

あわせてユーザーと決める（質問は最大 1〜2 個）: 想定読者と目的、おおよそのページ数、出力先の Drive フォルダ（URL/ID、任意）、著作権表記・フッター文言（あれば）、生成後にビジュアル QA を実行するか（既定かつ推奨: 実行。Phase 5 参照）。構成の検討には `references/deck-outlines.md` と `references/composers/` が使える。

---

## Phase 2: 作成

### 仕様パス

`templates/blank-16x9.json` に対して `deck.json` を書く。図表の機能はすべて仕様から使える: 図（`diagrams.py` の Canvas）、チャート/表（`charts.py`）、図形描画のピクトグラムとメタファー図（`illustrations.py`）、ビジネスフレームワーク図（`patterns.py`）、ページ骨格と分析図（`pages.py`）、Scalar ピクトグラム（`icons.py`）、クラウドアイコン（`cloud_icons.py`）、AI 画像（`images.py`）。仕様の書式は `references/template-schema.md` を、各部品は各モジュールのリファレンスを参照する。

### コードファーストパス

デッキモジュールを書く: 1 モジュール = 1 デッキ、1 スライド 1 関数とし、`deckkit` の `slide()` / `plain()` で登録する。座標はインチ単位で原点は左上。`d` は `diagrams.Canvas` である。動く実例から始めること:

- `examples/pattern-gallery/deck.py` — 利用可能な部品ごとに 1 スライド
- `examples/scalardb-scalardl/deck.py` — 実際の製品/アーキテクチャデッキ

コントラクトの規則（フッターセーフエリア、タイトル高さ、コネクタの接続）は `references/layout-contract.md`、作図レシピは `references/diagram-cookbook.md` にある。

### 設計原則（両パス共通）

- **アクションタイトル**: すべてのコンテンツスライドのタイトルは、ラベルではなく結論の文にする
- **コネクタは図形に接続する**。自由座標の線として描かない — API は線の端点を検証しないため、外れた矢印は QA まで見えない
- 本文 12pt 以上、タイトル 20pt 以上。WCAG AA コントラスト（4.5:1）。箇条書きは最大 6 個程度、1 スライド 1 メッセージ、60-30-10 の配色規則
- クラウドアイコン名を推測しない — `scripts/cloud_icons.py --search <term>` で検索する。ベンダーアイコンの再着色・回転・反転はライセンス条項で禁止されている
- 原則の全体とスライド種別ごとの指針: `references/google-slides-api.md`、`references/composers/`、`references/slide-patterns.md`

---

## Phase 3: 検証（あらゆる API 呼び出しの前に）

仕様パス:

```bash
.venv/bin/python scripts/build_deck.py --template templates/blank-16x9.json \
    --spec deck.json --dry-run --strict
```

コードファーストパス:

```bash
.venv/bin/python scripts/validate_layout.py path/to/deck.py \
    --template templates/blank-16x9.json
```

`validate_layout.py` はオフラインで無料である — フッターへの侵入、スライド外にはみ出た形状、タイトルの折り返し、コネクタ端点（外れ・埋没）、テキストを持つ図形どうしの部分的な重なり、テキストのあふれを検査する。終了コード 1 は「修正して再実行」の意味である。検証は決してスキップしない（`render_deck.py` には `--skip-validate` があるが使わないこと）。

---

## Phase 4: 生成

仕様パス:

```bash
.venv/bin/python scripts/build_deck.py --template templates/blank-16x9.json \
    --spec deck.json --title "Deck title" [--folder <DRIVE_FOLDER_URL_OR_ID>]
```

コードファーストパス:

```bash
.venv/bin/python scripts/render_deck.py path/to/deck.py --title "Deck title" \
    [--folder <URL/ID>] [--only 1-5]
```

`--only` はページ範囲だけをレンダリングし、安価な試作に使える。初回実行時はブラウザが開いて OAuth を行い、`config/token.json` が書き出される。スクリプトはプレゼンテーションの URL を表示する — ユーザーに伝えること。

**Drive フォルダの規則**: 生成したデッキごとに専用の Drive フォルダを作り、関連ファイルはすべてその下に置く。先にフォルダを作成し、その中へ生成し、最後にソース類を収集する:

```bash
.venv/bin/python scripts/drive_folder.py create "<Deck title>" [--parent <URL/ID>]
# pass the printed ID as --folder to build_deck.py / render_deck.py, then:
.venv/bin/python scripts/drive_folder.py upload <FOLDER_ID> deck.json figures/*.drawio out/diagrams/*.png
```

ユーザーが後で再生成・編集できるものをアップロードする: 仕様（`deck.json`）またはデッキモジュール（`deck.py`）、`.drawio` ソース、書き出した図の PNG。QA サムネイルはローカルに留める。フォルダ URL はプレゼンテーション URL とあわせて報告する。

大規模なデッキでは、ページ単位でサブエージェントにファンアウトできる。分割してよいもの・いけないものは `references/parallel-generation.md` を参照。

---

## Phase 5: ビジュアル QA（任意 — `slide-qa` スキル）

Phase 1 でユーザーが QA を選んだ場合（既定）に実行する。実行しないことを選んだ場合は
このフェーズをスキップし、レポートにビジュアル検証を行っていない旨を明記し、
フォローアップとして `slide-qa` スキルを提案する。

手順は **`slide-qa` スキル**が所管する — それに従うこと。要点:

```bash
.venv/bin/python scripts/fetch_thumbnails.py <URL or ID> --out out/qa --size LARGE
# … inspect every PNG with Read …
.venv/bin/python scripts/cleanup_qa.py   # always delete the local QA files when done
```

チェック項目: テキストの切れや枠からのあふれ、装飾要素との重なり、外れたコネクタ矢印、読めないコントラスト、不自然な改行位置。これらは API レスポンスからは見えない。

不合格が出た場合: 仕様/モジュールを修正し、Phase 3 の検証を再実行し、**壊れたプレゼンテーションを削除して再生成する**。サムネイルがきれいになるまで繰り返し、QA ファイルを片付けてから最終 URL を報告する。
