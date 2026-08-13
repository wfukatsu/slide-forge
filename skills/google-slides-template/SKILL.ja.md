---
name: google-slides-template
description: >-
  Duplicate an existing Google Slides template (master deck) and generate a
  presentation that follows its layouts. Confirms template, purpose, outline,
  and length interactively via AskUserQuestion, then covers template analysis
  and registration (template.json), deck generation, and visual QA from
  thumbnails. For designing from scratch without a template, use the
  google-slides skill; for Scalar company/product decks, use the
  scalar-product-slides skill (a dedicated workflow layered on top of this one).
  Triggers: "このテンプレートでスライドを作って", "マスタースライドから生成", "テンプレートを登録",
  "テンプレートを解析", "gslides-template", "create slides from this template",
  "use this master", or when given a Google Slides template URL.
---

*[English](SKILL.md)*

# テンプレート駆動の Google Slides 生成

## 重要事項

- **このスキルのスコープ**: 既存の Google Slides プレゼンテーションを**デザインの正**として複製し、そのレイアウトにテキストを流し込む。
- **すべてのコマンドは slide-forge ルートを cwd として実行する。** 相対パス `scripts/…`、`templates/…`、`.venv/bin/python` はそこから解決される。ルートは、このスキルがインストール済みプラグインから動く場合は `${CLAUDE_PLUGIN_ROOT}`（プレースホルダはインストール先パスに置換される）、ローカルクローンでは `/path/to/slide-forge`。以下のリテラルな `cd` パスはローカルクローンを前提とする — プラグインとしてインストールされている場合はプラグインルートに読み替えること。
- **スコープ外**:
  - テンプレートなしでゼロからデザインする → `google-slides` スキル（コンポーザー、インフォグラフィクス、コードファーストの `deckkit` デッキ）
  - Scalar の会社・製品・機能デッキ → `scalar-product-slides` スキル（本スキルの上に重ねた専用ワークフロー）
  - 顧客固有の Scalar ソリューション提案（課題起点）→ `scalar-proposal-slides` スキル（同じく本スキルの上に重ねたもの）
  - PPTX ファイルをゼロから作る → `document-skills:pptx`。ここで生成したデッキの `.pptx` への書き出し（納品形式）→ `pptx-export` スキル。インテイクの「出力形式」の質問で選ぶ
  - テンプレート自体のデザイン変更 → **Slides API はマスター/レイアウトの作成・編集をサポートしていない。** Google Slides の UI で行うこと。
- Python 3.10 以上が必要。`.venv` は `~/.claude/venvs/gslides` への**シンボリックリンク**で、統合前のスキル群と共有している。依存関係を変更すると、この venv を使うすべてに影響する。
- 認証情報の探索順: `$GSLIDES_CONFIG_DIR` → リポジトリ内の `config/`（正規の場所）→ `~/.claude/skills/google-slides/config/`（レガシーフォールバック）。旧スキルで OAuth 設定済みなら、そのまま変わらず動く。
- **Drive フォルダの規則**: 生成したデッキごとに専用の Drive フォルダを作り、関連ファイルをすべてその下に置く。`.venv/bin/python scripts/drive_folder.py create "<Deck title>" [--parent <URL/ID>]` で作成し、表示された ID を `--folder` として `build_deck.py` に渡し、その後 `drive_folder.py upload <FOLDER_ID> deck.json …` で仕様・`.drawio` ソース・図の PNG を収集する。フォルダ URL はデッキ URL とあわせて報告する。
- 高密度なクラウドアーキテクチャ / データフロー / ネットワーク図（入れ子コンテナ、10 ノード以上）→ 図は `drawio-diagrams` スキルで作図する（draw.io → PNG → `image` 部品として挿入）。
- **ユーザーが既に持っている既存デッキを更新する場合**（新しいコピーを生成する通常フローと違い、同じ URL のままその場で編集する場合）は、先に `.venv/bin/python scripts/snapshot_version.py <URL>` を実行して編集前のリビジョンを記録し、ローカル PPTX バックアップを取り、リビジョン ID をユーザーに報告してから編集する。ロールバックは Slides UI の「ファイル → 変更履歴」から行う。
- **ビジュアル QA は独立したスキル（`slide-qa`）であり、生成時に実行するかどうかを選ぶ。** API レスポンスが正常でも、テキストがあふれていないか、矢印が別の図形をまたいでいないか、コネクタが意味的に正しい図形に接続しているかは分からない — そのため QA の既定は**実行**であり、そのように推奨する。実行の可否はインテイク（Phase 1、`references/interactive-intake.md`）で確定する。ユーザーが実行しないことを選んだ場合は Phase 5 をスキップし、レポートにデッキが未検証である旨を明記し、フォローアップとして `slide-qa` を提案する。QA を実行した場合は、最後にローカルの QA ファイルを削除して終える（`scripts/cleanup_qa.py`）。
- **前提が未指定なら、生成前に `AskUserQuestion` で確定する。** テンプレート・目的・アウトライン・分量は、間違えると全面作り直しになる分岐点である。手順は Phase 1 と `references/interactive-intake.md` にある。ユーザーが既に指定した項目や「お任せ」と言った項目については質問しない — 採用した前提を 1 行で述べて進める。

## クイックリファレンス

| タスク | コマンド |
|---------|---------|
| 登録済みテンプレートの一覧（対話の選択肢の材料） | `.venv/bin/python scripts/list_templates.py` / `--json` |
| 対話インテイクの手順（AskUserQuestion） | `references/interactive-intake.md` |
| テンプレートの解析と登録（検証済み `roles` は保持） | `.venv/bin/python scripts/inspect_template.py <URL> --emit templates/<id>.json --name <id>` |
| テンプレートが画像を置きたい場所 | `template.json` の `layouts.<KEY>.imageSlots` — 仕様で x/y/w/h を省略すると使われる |
| 本文中の強調 | 行ごとの `{"text": …, "role": "heading"}`、インラインの `**…**` — 「本文中の強調」を参照 |
| レイアウトのサムネイル取得 | `.venv/bin/python scripts/inspect_template.py <URL> --thumbnails out/layouts` |
| デッキ仕様の検証（API 呼び出しなし） | `.venv/bin/python scripts/build_deck.py --template … --spec … --dry-run` |
| デッキの生成 | `.venv/bin/python scripts/build_deck.py --template … --spec … --title "…"` |
| 生成物のビジュアル QA（任意、既定: 実行） | `slide-qa` スキル — `.venv/bin/python scripts/fetch_thumbnails.py <URL> --out out/qa [--pages 9-16]` |
| 検証完了後にローカル QA ファイルを削除 | `.venv/bin/python scripts/cleanup_qa.py` |
| 既存デッキ編集前のバージョンスナップショット | `.venv/bin/python scripts/snapshot_version.py <URL> [--out out/backups]` |
| デッキの Drive フォルダ作成 / 関連ファイル収集 | `.venv/bin/python scripts/drive_folder.py create "<title>"` / `upload <FOLDER> <files…>` |
| 高密度なクラウド/データフロー図（draw.io → PNG） | `drawio-diagrams` スキル + `references/drawio.md` |
| ページ断片を 1 つの仕様に結合 | `.venv/bin/python scripts/assemble_spec.py --out deck.json --title "…" out/<deck>/pages` |
| 大規模デッキのファンアウト生成（サブエージェント） | `references/parallel-generation.md` |
| 検証ゲート（オフラインチェック + サムネイル QA） | `references/validation.md` |
| AI での画像生成 | `.venv/bin/python scripts/images.py --prompt "…" --style flat_vector --out out/x.png` |
| アイコンの検索 | `.venv/bin/python scripts/icons.py --list` / `--search 情報銀行` |
| クラウドアイコンの取得（**初回に一度、必須**） | `.venv/bin/python scripts/fetch_cloud_icons.py` |
| クラウドアイコンの検索 | `.venv/bin/python scripts/cloud_icons.py --search s3` / `--list --vendor aws` |
| 全コンポーネントのカタログ（8 ファミリー・45 タイプを 1 デッキに。実仕様の例付き） | `examples/design-catalog.json` |
| 図の描画（`Canvas`）と作図の作法 | `references/diagrams.md` |
| 表とチャート | `references/charts.md` |
| 表/チャートのカタログ（実仕様の例） | `examples/charts-demo.json` |
| ビジネスフレームワーク図 | `references/patterns.md` |
| フレームワーク図のカタログ（実仕様の例） | `examples/patterns-demo.json` |
| スライドパターン（6 骨格 × 35 本文パターン） | `references/slide-patterns.md` |
| 全パターンの索引（59 スライド、1 枚 1 パターン） | `examples/slide-pattern-index.json` |
| 読み切り（配布資料）スタイルのカタログ（30 スライド） | `examples/read-alone-guide.json` |
| ハイライト付きコードサンプル | `references/code-blocks.md` |
| コードブロックのカタログ（実仕様の例） | `examples/code-blocks-demo.json` |
| デッキアウトラインのテンプレート（課題解決 / 新規事業提案 / 製品紹介 / 講演） | `references/deck-outlines.md` |
| 画像とイラスト図 | `references/images.md` |
| アイコンライブラリ | `references/icons.md` |
| クラウドアイコン（AWS/GCP/Azure） | `references/cloud-icons.md` |
| イラストのカタログ（実仕様の例） | `examples/illustration-gallery.json` |
| アイコンのカタログ（実仕様の例） | `examples/icon-gallery.json` |
| クラウドアーキテクチャ図（実仕様の例） | `examples/cloud-architecture.json` |
| ScalarDB アーキテクチャ（`Canvas` を直接使用） | `examples/scalardb-architecture.py` |
| ScalarDL アーキテクチャ（3 つのアイコンファミリーの混在） | `examples/scalardl-architecture.py` |
| template.json のスキーマ | `references/template-schema.md` |
| API の制約と落とし穴 | `references/api-notes.md` |
| 登録済みテンプレート | `templates/*.json` |

---

## Phase 0: 前提条件

1. Python と依存関係。venv は共有で、実体は `~/.claude/venvs/gslides` にある:

```bash
cd /path/to/slide-forge
.venv/bin/python -c "import googleapiclient; print('ok')"
```

壊れている・存在しない場合は、共有 venv を再構築してリンクし直す。
`~/.claude/venvs/gslides-requirements.txt` が存在しない場合は、先にリポジトリの
`requirements.txt` から種を作る:

```bash
[ -f ~/.claude/venvs/gslides-requirements.txt ] || \
  cp /path/to/slide-forge/requirements.txt ~/.claude/venvs/gslides-requirements.txt
python3 -m venv ~/.claude/venvs/gslides
~/.claude/venvs/gslides/bin/pip install -U -r ~/.claude/venvs/gslides-requirements.txt
rm -rf /path/to/slide-forge/.venv
ln -s ~/.claude/venvs/gslides /path/to/slide-forge/.venv
```

> シンボリックリンクは**絶対パス**で作ること。ディレクトリ自体がシンボリックリンクの
> 環境では、相対リンクは解決に失敗して壊れる。

> 依存を追加するときは `~/.claude/venvs/gslides-requirements.txt` を編集する。
> リポジトリの `requirements.txt` は記録であって、実際のインストール元ではない。

2. 認証: 探索場所のいずれか（`$GSLIDES_CONFIG_DIR` → リポジトリ内の `config/` →
レガシーの `~/.claude/skills/google-slides/config/`）に `credentials.json` が
存在しなければならない。どこにもない場合は、ユーザーに Google Cloud Console で
OAuth 2.0 デスクトップクライアントを作成してもらい、**Slides API と Drive API の
両方を有効化**してもらう。`token.json` は初回実行時に自動生成される。

3. **クラウドアーキテクチャ図を描くときだけ**: AWS / Google Cloud / Azure の
公式アイコンは**再配布できないベンダー資産のため、リポジトリにはコミットされて
いない**。一度だけ取得する:

```bash
.venv/bin/python scripts/fetch_cloud_icons.py          # 1-2 min, ~8.6 MB
.venv/bin/python scripts/fetch_cloud_icons.py --verify # check they are present
```

取得前に `cloud_icon` を使うと、この手順を指すエラーで停止する。取得した資産は
コミットしないこと（`assets/cloud-icons/` は gitignore 済み）。詳細は
`references/cloud-icons.md`。

4. **テンプレートへのアクセス**: 複製には Drive の閲覧 + コピー権限が必要。
「ダウンロード・印刷・コピーを無効にする」が設定された共有ファイルは複製できない。

5. **AI 画像生成（`ai_image` / 表紙画像）を使う場合のみ**、課金設定済みの
`GEMINI_API_KEY` が必要（任意）— 環境変数、または `config/gemini_api_key`
（gitignore 済み）に保存する。図形描画の `illustrations` / `patterns` にキーは不要。

---

## Phase 1: 対話で設計を確定する

前提が未指定の新規デッキでは、**何かを生成する前に `AskUserQuestion` で意思決定を
確定する**。これを省いて 40 枚作ってしまうと、前提が 1 つ違っていただけで全面
作り直しになる。

ユーザーが**使えるテンプレートをまったく持っておらず**、自社ブランド
（色・フォント・ロゴ）に合わせたテンプレートを望む場合は、先に **`template-forge`**
スキルへ引き継ぐ — 新しいマスターを作成・登録してくれるので、その新しい id に
対してここへ戻ってデッキを生成する。

確定すべき意思決定（どれも間違えると作り直しになる）:

| 意思決定 | 既定値 | 間違えたときの影響 |
|---|---|---|
| テンプレート | `scalar-2026` | すべてのレイアウトと色が変わる |
| 目的（Proposal / Presentation ファミリー＋テンプレート密度 `print` / `presentation`） | Proposal + `print` | 文体の合わないデッキになる。テンプレートスライドが誤った密度で描画される |
| アウトラインの型 | 課題解決型 | 話の順序が変わる = 全スライドの並べ替え |
| 分量 | 20 枚前後 | スライドあたりの情報密度が変わる |

手順の要点（詳細・質問の文言・具体的な選択肢は
**`references/interactive-intake.md`** にある）:

1. **選択肢は生きたデータから組み立てる。** テンプレートの選択肢は
   `scripts/list_templates.py` の出力から作る。ハードコードした一覧は、テンプレートの
   追加・削除で腐る。
2. **まとめて訊く。** 1 質問 1 往復にしない。往復は最大 3 回
   （前提 4 問 → 内容 → アウトライン承認）。
3. **アウトライン承認ゲートは決して省略しない。** JSON を書き始める前に、スライド数・
   レイアウト・各スライドの見出しを会話本文で提示して承認を得る。承認後は QA まで
   一気に走り切る。
4. **決して訊かないもの**: 座標、フォントサイズ、コンポーネントの選定、色。
   それらはこのスキルの責務である。ユーザーが既に指定した項目や委ねた項目
   （「お任せ」）も訊かない — ただし採用した前提は明示的に述べる。

```bash
.venv/bin/python scripts/list_templates.py        # human-readable
.venv/bin/python scripts/list_templates.py --json # material for building options
```

---

## Phase 2: テンプレートの解析と登録

**Phase 1 で登録済みテンプレートを選んだ場合、このフェーズは丸ごとスキップする。**
解析・登録は、新しい（未登録の）URL を渡されたときだけ行う。

```bash
.venv/bin/python scripts/inspect_template.py "<template URL>" \
    --emit templates/<id>.json --name <id> --thumbnails out/layouts
```

出力される `template.json` には、ページサイズ、配色、各レイアウトの `layoutId` /
プレースホルダ構造 / 要素座標 / 既定テキストスタイル / 装飾 / **画像スロット**、
そしてテンプレートに同梱されたスライドの ID が含まれる。

既存の `template.json` に上書きで再出力しても、**人が検証済みの `roles` /
`__roles_note` / `name` / `displayName` は保持される**（`--reset-roles` を渡すと
新しい推測で上書きされる）。したがって、いったん roles を確定させた後の再解析は
安全である。

### 画像スロット — テンプレートが画像を置きたい場所

`layouts.<KEY>.imageSlots` は、テンプレートが画像用に確保している枠を記録したもので、
3 つの情報源から見つかる: PICTURE 系プレースホルダ、**レイアウトに残された空の
画像要素**（何も描画されないので装飾ではなくスロットである）、そして同梱スライドが
繰り返し使っている枠。レポートには `imageSlot[N]` として表示される。

**レイアウトにスロットがあるなら、画像はそこに入れる。** デッキ仕様では
`x` / `y` / `w` / `h` を省略すれば `build_deck.py` が埋める（`fit` の既定は
`cover`）。スロットが複数あるときは `"slot": 1` で選ぶ。そうしたレイアウトで画像を
別の場所に置くと `--dry-run` が報告し、`--strict` ではエラーになる。

`aiImage` は**入る予定のスロットに合わせて生成される**: モデルが出力できる
10 種のアスペクト比のうち最も近いものを使い、それでも枠と 2% 以上ずれる場合は、
発生するクロップを説明するプロンプト指示を加えて、被写体がクロップ後も成立する
構図にする。枠の比率はキャッシュキーの一部なので、形の違うスロットへ画像を移すと
その形に合わせて描き直される。詳細は `references/images.md`。

**既に存在する**デッキ（背後に仕様がない、または URL を維持しなければならないもの）
については、`image-slots` スキルが空の枠をその場で埋める。

### roles の検証（必須、人の判断）

`roles` は表示名とプレースホルダ構造から導いた**推測**であり、そのままでは信用
できない。

1. `--thumbnails` が生成した PNG を Read ツールで開き、各レイアウトの実際の見た目を
   確認する
2. レポートの「候補 N 件、要確認」と「未割り当ての roles」の項目をすべて解消する
3. `template.json` の `roles` を編集して確定し、検証日と根拠を `__roles_note` に
   記録する

`.venv/bin/python scripts/layout_sample.py --template templates/<id>.json`
は、全レイアウトにサンプル文字列を流し込んだカタログデッキを生成する。role の
割り当てを目視で検証するのに使う。

標準の role 名: `COVER` / `SECTION` / `CONTENT` / `TITLE_ONLY` / `BLANK` /
`CLOSING`。テンプレートに用途別ファミリー（提案用と講演用など）がある場合は、
`CONTENT_PRESENTATION` のようなカスタム role を追加してよい。role は単なる別名で
あり、レイアウトキーを直接指定することもできる。

> **同じレイアウトでも見え方が複数ありうる。** たとえばマスターのフッターを覆う
> 全面白色の矩形を持つレイアウトでは、テンプレート側で定義された著作権表記は
> 表示されない。`decorations` に全ページ大の矩形があるときは、これを疑うこと。

---

## Phase 3: デッキ仕様の記述

スライドの構成を JSON で書く。

```json
{
  "title": "Title of the generated presentation",
  "slides": [
    { "layout": "COVER", "title": "…", "subtitle": "…", "body": "2026年MM月DD日\n会社名", "notes": "speaker notes" },
    { "layout": "SECTION", "title": "Section name", "body": "supporting line" },
    { "layout": "CONTENT", "title": "Action title", "body": ["item 1", "item 2"] },
    { "layout": "CLOSING" }
  ]
}
```

- `layout`: role 名またはレイアウトキー
- `body`: 文字列（そのまま使われる）または配列（改行で結合される）
- `bodies`: 2/3 カラムレイアウト用。`[["left line 1","left line 2"], ["right line 1"]]` と書くと、配列が順に BODY インデックス 0, 1, 2… に流し込まれる。`body` とは排他
- `notes`: 任意のスピーカーノート
- **レイアウトが持たないプレースホルダを指定するとエラーになる。** 各レイアウトが何を持つかは `template.json` の `placeholders` を見る。`["TITLE","BODY","BODY#1"]` のように `#N` の付いた項目は複数カラムを示す。

### タイトルの書き方

見せているものではなく、**主張できること**を書く（アクションタイトルの原則）。

- 悪い例: 「売上の推移」
- 良い例: 「売上は 3 四半期連続で前年比 20% 成長」

### 本文中の強調 — 一様なテキストの壁のまま渡さない

10 行が同じ太さで並ぶ本文は読みにくい: 読者は小見出しと、その下にぶら下がる項目を
区別できない。構造を読者に渡すこと。

```json
"body": [
  { "text": "見せていないから変えられるもの", "role": "heading" },
  "    データベースの種類・テーブル構造・インデックス",
  "    使っているフレームワークや言語",
  "",
  { "text": "見せてしまうと変えられなくなるもの", "role": "heading" },
  "    URLの形（/order_tbl のようにテーブル名が出ている）",
  "足すのは簡単で、消すのは難しい。この **非対称性** が基本的な制約です。"
]
```

**使いどころ** — 以下は選択肢ではなく規則である:

- 本文が「小見出し + ぶら下がり項目」の形をしている → 小見出しに
  `role: "heading"` を付ける
- 箇条書きが 6 個以上続く → 2〜3 のまとまりに分け、それぞれに見出しを付ける
- 1 スライドの見出しは最大 **3 つ**。それ以上必要ならスライドを分割するか、内容を
  表にすべきである
- 文中のキーワード 1 語 → `**…**`
- 別のスライドやデッキへの参照 → 同一デッキ内のスライドは `[付録 A-2](#12)`
  （1 始まり）、別デッキは `[付録デッキ](https://…)`。インラインマークアップは
  この 2 つだけで、その他の Markdown はサポートされない
- 本文の 1/4 を超えて強調しない。どこもかしこも強調されているのは、どこも強調
  されていないのと同じである

role は `heading` / `strong` / `note` の 3 つで、見た目はテンプレートの
`bodyRoles` に従う（`references/template-schema.md`）。既定の `heading` は太字 +
上部スペースで、**フォントサイズは変えない**ため、行数の見積もりが崩れない。

### 本文テキスト量の見積もり

プレースホルダの既定フォントは、手作りのデッキ向けに調整された大きめのものが多い。
日本語本文は `bodyFontSize` / `bodyLineSpacing` / `bodySpaceAbove` /
`bodySpaceBelow` で調整する（スライドごと、または `defaults` で全体に）。

```json
{ "defaults": { "bodyFontSize": 13, "bodyLineSpacing": 115,
                "bodySpaceAbove": 0, "bodySpaceBelow": 3 }, "slides": [ ... ] }
```

**テキストがあふれても API はエラーを返さない**ため、`--dry-run` が本文の高さを
見積もり、収まらないときに警告する（`--strict` でエラーになる）。この見積もりは
意図的に保守的で、仕様が段落間隔をテンプレート既定のままにしていると実際の高さは
見積もりより大きくなる — したがって「警告なし」は「たぶん収まる」であって保証では
ない。手で確かめたいときは次の式を使う。

```
paragraph height = wrapped lines × fontSize × 1.2 × (lineSpacing / 100)
                   + spaceAbove + spaceBelow      ← per-paragraph margins add up
capacity         = (body h[in]) × 72 ≥ sum of all paragraph heights
chars per line   = (body w[in] − 0.1×2) × 72 ÷ fontSize   ← count full-width as 1, half-width as 0.5
```

> **見積もりには必ず段落間隔を含めること。** 多くのテンプレートの BODY
> プレースホルダは段落の前後に `spaceAbove` / `spaceBefore` のマージンを持って
> おり、これを無視すると実際の収容量は見積もりの 6 割程度になる。実測例
> （`aixdevops` の CONTENT、本文 9.0 × 4.244 in）:
>
> | 設定 | 収まる段落数 |
> |---|---|
> | 13pt / 140% / 段落間隔は既定（未指定） | **10** |
> | 13pt / 115% / 段落間隔 0 | **18** |
> | 12pt / 115% / 各段落の下に 3pt | **16** |
>
> 空行（`""`）も 1 段落分と同じ高さを消費する。あふれたテキストはフッターと衝突し、
> 切り取られる。

### 生成前に必ず検証する

```bash
.venv/bin/python scripts/build_deck.py --template templates/<id>.json \
    --spec deck.json --dry-run
```

これは API 呼び出しなしで、レイアウトの解決とプレースホルダの整合性を検査する。
本番実行の前に必ず通すこと。`--strict` を付けると図表監査の警告 1 件でもエラー終了
する（CI 的な生成前ゲートとして推奨）。このゲートとサムネイル QA の関係は
`references/validation.md` を参照。

### デッキが 12 枚を超えるなら、仕様をページ断片に分割する

アウトラインとアクションタイトルが確定したら、
**`references/parallel-generation.md`** に従う。ホストとセッションが許すなら
サブエージェントを使い、そうでなければ同文書の Codex 逐次フォールバックを使う。
どちらのパスも 2〜3 枚のスライド断片を書き、自己検証し、`assemble_spec.py` で
結合する。

```bash
mkdir -p out/<deck>/pages          # each agent writes exactly one 0120-*.json
.venv/bin/python scripts/assemble_spec.py \
    --out out/<deck>/deck.json --title "Deck title" out/<deck>/pages
```

**決して委譲してはならない仕事が 4 つある: アウトライン、タイトル、数値の出典確認、
そして結合。** これらを分割するとスライド間のロジックと出典の一貫性が壊れる。
10 枚未満ではファンアウトのオーバーヘッドの方が高くつく — 仕様は自分で書くこと。

---

## Phase 4: 生成

```bash
.venv/bin/python scripts/build_deck.py \
    --template templates/<id>.json --spec deck.json \
    --title "Deck title" [--folder "<Drive folder URL or ID>"]
```

処理の手順:

1. `drive.files().copy()` でテンプレートを複製する
2. テンプレートに同梱されたスライドを削除する
3. `createSlide(layoutId)` + `placeholderIdMappings` で各スライドを作成し、`insertText` で流し込む
4. ページ番号をテキストボックスとして描画する（`--no-page-numbers` で抑止）
5. `batchUpdate` を 500 件ずつのチャンクで実行する（一時的な 5xx / 429 は指数バックオフでリトライ）
6. スピーカーノートや画像サイズ補正がある場合は、プレゼンテーションを再取得して 2 回目の `batchUpdate` で適用する（どちらも作成後にしか存在しない情報を必要とする）
7. 画像を一時アップロードしていた場合は Drive から削除し、公開共有を取り消す

**テンプレート側の装飾・ロゴ・フッターはコピーに自動的に引き継がれる — 自分で
描いてはならない**（二重描画になる）。`template.json` の `masterDecorations` は
「既に描かれているもの」の記録であって、描画指示ではない。

### 視覚的に見せる 9 つの方法 — まず目的で選ぶ

| 見せたいもの | 使うもの | 特徴 |
|---|---|---|
| 構造・手順・数値の関係 | `diagrams.Canvas`（`references/diagrams.md`） | 精密。要素間の関係が保証される |
| 表とチャート（比較・推移・構成） | `charts`（`table` / `vbars` / `vbars_stacked` / `linechart` / `pie` …） | 表はネイティブで後から編集できる。ゼロ基線・系列色固定などの作法が組み込み |
| 概念・メタファー・登場人物 | `illustrations`（`icon_flow` / `pyramid` / `iceberg` …） | 図形で描く。**キー不要・決定的な出力**、テーマ色 |
| ビジネスフレームワークの定番 | `patterns`（`posmap` / `gantt` / `orgchart` / `lean_canvas` / `nested_circles` / `testimonial`） | 提案書・稟議の標準図。キー不要、テーマ色 |
| ページ骨格と分析図 | `pages`（`governing_message` / `lead_in` / `so_what` / `source_note` / `exhibit_frame` / `waterfall` / `rating_matrix` …） | ページの組み方そのもの。用途によって密度だけが変わる。キー不要、テーマ色 |
| ドメイン語彙のアイコン | `icons`（`asset_icon` / `asset_icon_flow` …） | 62 のブランド資産。ブランド準拠。**ネットワーク必須** |
| クラウドアーキテクチャ図 | `cloud_icons`（`cloud_icon` / `cloud_zone` …） | AWS/GCP/Azure 公式アイコン 1,757 個。**再着色・回転は厳禁**。ネットワーク必須 |
| 雰囲気・情景・表紙 | `images`（`ai_image` / `image`） | AI 生成またはローカル画像。**まず `imageSlots` を確認 — レイアウトが枠を確保しているなら x/y/w/h を省略してそこに収める**。その場合 `aiImage` は枠の形に合わせて生成され、枠を満たす |
| コードサンプル | `code_block`（java / graphql / json / bash） | 等幅 + VS Code Dark+ 風ハイライト。**角丸なし** |

9 つはすべて同じ `Canvas` のメソッドなので、1 枚のスライド上で混在できる。
デッキ仕様（JSON）からは `figures` として使える。**詳細 — コード例、
コンポーネント一覧、作図・レイアウトの作法、`build_deck.py` をライブラリとして
使う方法 — は `references/diagrams.md` を読むこと。** ファミリー別の使い方:
`references/charts.md` / `references/patterns.md` /
`references/slide-patterns.md` / `references/images.md` / `references/icons.md`
/ `references/cloud-icons.md` / `references/code-blocks.md`。実例は `examples/`
のデモ仕様。

### 作図の要点（詳細と根拠は `references/diagrams.md`）

- **生成前に必ず 4 つの監査をすべて呼ぶ。** `audit_bounds()`（枠外の図形）/ `audit_connectors()`（浮いた・埋もれた矢印）/ `audit_overlaps()`（隠れたテキスト、衝突するラベル）/ `audit_text_fit()`（ボックスに対して多すぎるテキスト）。いずれも座標だけから検出できる欠陥であり、放置するとサムネイルで初めて見つかることになる。
- **図形どうしを結ぶ線は決して座標で描かない。** 次の基準で選ぶ。

| 目的 | 使うもの |
|---|---|
| 図形 A → B。移動に追従してほしい | `d.connect(a, b)` |
| 図形 A → B。辺の上に正確に載せたい | `d.link(a, b)` |
| 折れた経路、軸、引き出し線 | `d.line(..., free=True)` |

- **回転した図形の中にテキストを入れない。** 図形は `text` なしで描き、`label()` を重ねる。
- **迷ったら `illustrations` を使う。** オフラインで動き、常にテンプレートの色に従う。課金設定済みの `GEMINI_API_KEY` が要るのは AI 生成（`ai_image`）だけである。
- `--dry-run` は API 呼び出しなしで図表を座標に展開して監査する（`--strict` は警告 1 件でエラー終了）。

---

## Phase 5: ビジュアル QA（任意 — `slide-qa` スキル）

このフェーズは**インテイクで QA の実行を選んだ場合（既定）**に実行する。実行しない
ことを選んだ場合はスキップし、レポートにビジュアル検証を行っていない旨を明示し、
フォローアップとして `slide-qa` スキルを提案する。

手順 — サムネイル取得、点検の優先順位、チェックリスト、修正ループ、クリーンアップ —
は **`slide-qa` スキル**が所管する。それに従うこと。要点:

```bash
.venv/bin/python scripts/fetch_thumbnails.py "<generated deck URL>" --out out/qa --size LARGE
# … inspect with Read, fix the spec and regenerate on any defect …
.venv/bin/python scripts/cleanup_qa.py   # always delete the local QA files when done
```

- デッキが 15 枚を超える場合は、`--pages 9-16` でサブエージェントに QA を分割する
  （1 体あたり 6〜8 枚、所見はテキストのみで返す —
  `references/parallel-generation.md`）。
- 欠陥が見つかったら `deck.json` またはレイアウト選択を修正して**再生成する**。
  実物にパッチしてはならない。置き換えられたデッキは Drive から削除する
  （`drive.files().delete(fileId=…)`）— ユーザーが持つ URL は常にちょうど 1 つ。
- チェックリストの全文と報告の規則は `references/validation.md` にある。

**結果を見せる前に自分で QA を通すこと。** 目視すれば防げた欠陥をユーザーに
見つけさせてはならない。その上で、まだ調整の余地があるなら `AskUserQuestion` で
提示する:「確定 / 文言の調整 / 図の見せ方の変更 / 枚数の調整」
（`references/interactive-intake.md` の第 4 節）。作り直す場合は、**先に古い実物を
Drive から削除**してから再生成する。

---

## エラー対応

| 症状 | 原因と対処 |
|------|-----------|
| `プレゼンテーション ID を抽出できません` | 想定外の URL 形式。`/presentation/d/<ID>/` の `<ID>` を直接渡す |
| `credentials.json が見つかりません` | Phase 0 の認証設定。Slides API と Drive API の両方が有効か確認する |
| `RefreshError` / `invalid_grant` | 認証トークンの期限切れ。使用中の設定ディレクトリから `token.json`（`config/token.json`、またはレガシーの `~/.claude/skills/google-slides/config/token.json`）を削除して再実行すると、ブラウザでの再認証フローが始まる |
| コピー時の 403 | テンプレートにコピー権限がない。オーナーに「閲覧者（コピー可）」を依頼する |
| `Invalid requests[N].createSlide: layout not found` | `template.json` が古い。テンプレートが編集された可能性が高い。再解析する |
| ページ番号が出ない | Slides API は SLIDE_NUMBER プレースホルダをインスタンス化できない。`add_page_numbers()` が呼ばれているか確認する |
| フッターが二重になる | テンプレートが既に提供しているフッターを自分でも描いた。自分の描画を除去する |
| テキストが途中で切れる | プレースホルダの高さ不足。`--dry-run` が「body needs about Npt」と報告する。テキストを減らす、`bodyFontSize` を下げる、またはスライドを分割する |
| 本文が一様なテキストの壁になっている | 小見出しに `role: "heading"` を付ける（「本文中の強調」を参照） |
| セクション/表紙スライドで画像が変な位置にある | 使わなかった `imageSlots` の枠がそのレイアウトにある。仕様で x/y/w/h を省略する（`--dry-run` が報告する） |
| `type 'aiImage' is missing required keys: ['x','y','w','h']` | そのレイアウトには画像スロットがないため、座標は自分で決める |

**失敗時の原則**: 生成の途中で失敗したデッキは削除し（テンプレートのコピーは既に
Drive に存在している）、仕様を修正して**ゼロから作り直す**。作りかけの実物への
部分的なパッチは再現性がなく、コピー方式の生成では再実行のほうが速い。

---

## ファイル構成

パスはすべてリポジトリルート `/path/to/slide-forge` からの相対パスである。

| パス | 役割 |
|------|------|
| `scripts/_auth.py` | OAuth（探索: `$GSLIDES_CONFIG_DIR` → `config/` → レガシー）、単位変換、色変換、URL → ID 抽出 |
| `scripts/inspect_template.py` | テンプレート解析 → `template.json`、レイアウトサムネイルの取得 |
| `scripts/build_deck.py` | テンプレートコピー → デッキ生成（`TemplateDeck`）。仕様の検証（`--dry-run` / `--strict`）もここが所管 |
| `scripts/fetch_thumbnails.py` | ビジュアル QA 用のサムネイル取得（`slide-qa` スキル経由で使用）。`--pages 9-16` で範囲を絞る（分割 QA 用）。`--size SMALL/MEDIUM/LARGE` |
| `scripts/cleanup_qa.py` | 検証完了後にローカル QA ファイルを削除（`out/qa`、`out/qa-*`、`out/*/qa`。触るのは `out/` のみ）。`--dry-run` でプレビュー |
| `scripts/assemble_spec.py` | ページ単位の JSON 断片を昇順に連結して 1 つのデッキ仕様にする。ファンアウト生成のアセンブラ |
| `scripts/layout_sample.py` | レイアウトごとに 1 枚のサンプルデッキを生成する。role 割り当ての目視検証用 |
| `scripts/list_templates.py` | 登録済みテンプレートの一覧（roles、レイアウト数、同梱スライド数）。対話でのテンプレート選択肢の材料。`--json` あり |
| `scripts/fetch_cloud_icons.py` | AWS/GCP/Azure 公式アイコンセットを `assets/cloud-icons/`（gitignore 済み）へ一度だけ取得する。`--verify` で存在確認 |
| `scripts/diagrams.py` | 作図プリミティブ（`Canvas`）: フロー、カード、hbar チャート、図形コネクタ（`connect` / `link`）、回転と透過、コードブロック（`code_block`、ハイライト付き、角丸なし）、`font` 選択、自己監査（`audit_bounds` / `audit_connectors` / `audit_overlaps` / `audit_text_fit`） |
| `scripts/charts.py` | 表とチャート（`ChartMixin`）: ネイティブ表、vbars、グループ vbars、`vbars_stacked`、折れ線、円/ドーナツ。ゼロ基線と CVD 検証済みの固定系列色を実装で強制 |
| `scripts/illustrations.py` | イラスト図（`IllustrationMixin`）: ピクトグラム 30 種とメタファー図 12 種。図形のみ — キー不要、ネットワーク不要 |
| `scripts/patterns.py` | ビジネスフレームワーク図（`PatternMixin`）: posmap / gantt / orgchart / lean_canvas / nested_circles / testimonial。キー不要、ネットワーク不要 |
| `scripts/pages.py` | ページ部品と分析図（`PageMixin`）: governing_message / lead_in / so_what / source_note / exhibit_frame（骨格）+ mece_tree / waterfall / rating_matrix（分析）+ exec_summary / storyline / ghost（デッキ設計）の 11 部品。空の出典と合計不一致を実装で阻止。キー不要、ネットワーク不要 |
| `scripts/icons.py` | アイコンライブラリ（`IconLibraryMixin`）: `assets/scalar/pictograms/` の SVG を再着色付きで PNG にレンダリングして配置する。検索/一覧の CLI も兼ねる |
| `scripts/cloud_icons.py` | クラウドアイコン（`CloudIconMixin`）: AWS/GCP/Azure 公式 SVG を**再着色せずに**レンダリングする。検索 CLI も兼ねる |
| `scripts/images.py` | 画像（`ImageMixin`）: AI 生成（Gemini、キャッシュ付き）とローカル/URL/Drive 画像の挿入。単体の CLI としても動く |
| `scripts/colors.py` | 色ユーティリティ（`Palette` / `lighten` / `readable_on`）。diagrams / charts / illustrations / patterns / images で共有 |
| `scripts/deckkit.py`、`scripts/render_deck.py`、`scripts/validate_layout.py` | `google-slides` スキルのコードファーストパス（Python のデッキモジュール、オフライン座標検証）。リポジトリは共通でエントリポイントが違う — `references/validation.md` 参照 |
| `config/` | `credentials.json` / `token.json` の正規の置き場所 |
| `assets/scalar/pictograms/` | Scalar ブランドアイコン 62 個（`icons.json` + `svg/` + バックアップの `png/`） |
| `assets/scalar/logos/`、`assets/scalar/product-logos/` | Scalar / ScalarDB / ScalarDL のロゴ（PNG と SVG） |
| `assets/cloud-icons/` | AWS / Google Cloud / Azure 公式アイコン 1,757 個（`cloud-icons.json` + `<vendor>/<category>/*.svg`）。gitignore 済み。`scripts/fetch_cloud_icons.py` で復元 |
| `references/template-schema.md` | `template.json` とデッキ仕様 JSON のスキーマ |
| `references/diagrams.md` | 図の描画（`Canvas`）: ファミリー別のコード例、線の接続、4 つの監査、色とレイアウトの作法、ライブラリとしての使い方 |
| `references/charts.md` | 表とチャート（`charts.py`）: 使い方とデザインの作法 |
| `references/patterns.md` | ビジネスフレームワーク図（`patterns.py`） |
| `references/slide-patterns.md` | スライドパターン（`pages.py`）: 6 骨格の**標準座標**、作法の根拠、講演用と配布用の密度、アンチパターン |
| `references/parallel-generation.md` | 大規模デッキのページ単位ファンアウト: 分割してはならない仕事、モデル選択、QA の分割 |
| `references/validation.md` | 2 つの検証ゲート: オフライン座標チェック（`--dry-run` / `validate_layout.py`）とサムネイル QA — 各ゲートが捕まえるもの、目でしか捕まえられないもの、修正ループ、報告の規則 |
| `references/code-blocks.md` | コードブロック（`code_block`）: 使い方と高さの見積もり |
| `references/interactive-intake.md` | 対話インテイク: AskUserQuestion の質問セット、アウトライン承認ゲート、決して訊かないもの |
| `references/deck-outlines.md` | デッキアウトラインのテンプレート（課題解決 / 15 節構成の新規事業提案 / 製品紹介 / 講演）。インテイクの「アウトライン」選択肢はここから来る |
| `references/images.md` | 画像とイラスト: 使い分け、メソッド全一覧 |
| `references/icons.md` | アイコンライブラリ: 検索、色、制約、資産の追加 |
| `references/cloud-icons.md` | クラウドアイコン: 検索、描画 API、ライセンス条項、更新手順 |
| `references/api-notes.md` | 実測で判明した Google Slides API の制約と落とし穴 |
| `examples/design-catalog.json` | **全コンポーネントのカタログ**（49 スライド）: 8 ファミリー、`FIGURES` 45 タイプ中 44 を実際に描画。`aiImage` だけは課金設定済み `GEMINI_API_KEY` が要るため仕様のみ（キーがあればそのスライドを `aiImage` に戻して再生成）。どのビジュアルを使うか迷ったら、まずこれを生成して見る |
| `examples/read-alone-guide.json` | **読み切り（配布資料）スタイルのカタログ**（30 スライド）: `pages.py` の全 11 部品とアンチパターン集を、架空のケース（「受注処理コスト削減」）で実演。**密度とスタイルを学ぶ**ためのデッキ |
| `examples/slide-pattern-index.json` | **全スライドパターンの索引**（59 スライド）: 6 骨格 × 目的別 35 ページ、1 枚 1 パターン。**見て選ぶ**ためのデッキ。ユーザーに使うページを指してもらう場面では、これを生成して見せる |
| `examples/illustration-gallery.json` | 全ピクトグラム・全メタファー図・画像配置を使ったデッキ仕様（実例） |
| `examples/icon-gallery.json` | 全アイコンと 5 つの `asset_icon_*` メソッドを使ったデッキ仕様（実例） |
| `examples/cloud-architecture.json` | クラウドアーキテクチャ図のデッキ仕様（ゾーン、マルチクラウド、データフロー）（実例） |
| `examples/scalardb-architecture.py` | ScalarDB アーキテクチャ: クラウドアイコン + ロゴ + コネクタを `Canvas` で構成 |
| `examples/scalardl-architecture.py` | ScalarDL アーキテクチャ（4 層 / Auditor トポロジー / 改ざん検知フロー）: 3 つのアイコンファミリーの混在 |
| `templates/*.json` | 登録済みテンプレート |
| `templates/scalar-2026.json` | Scalar Slide Master 2026（8 レイアウト、Proposal / Presentation ファミリー） |
| `templates/scalar-2026-boilerplate.json` | Scalar Slide Master 2026 + 定型スライド 12 枚（会社概要、CEO プロフィール、製品概要、顧客、事例、…）。レイアウトは `scalar-2026` と同一で、違いは同梱スライドのみ。`--keep-existing` と組み合わせて残す。2026-08-01 登録 |
| `templates/aixdevops.json` | AIxDevOps Theme（Scalar 共同ブランド。22 レイアウト、2/3 カラム、Proposal / Presentation ファミリー、QR コード付き `CLOSING`。2026-08-01 再解析） |
| `templates/corporate.json` | Corporate Master（aixdevops から派生: ネイビー配色、ブランド要素を除去） |
| `templates/themes/*.json` | `google-slides` コンポーザーパス用のデザイントークンテーマ（`scalar.json`、`aixdevops.json`、`corporate.json`） |

## 既存テンプレートから色替えマスターを派生させる

Slides API は**マスター/レイアウトを作成できないが、既存のものは変更できる**
（`references/api-notes.md` 第 1 節）。良いテンプレートが既にあるなら、それを複製して
色とブランド要素だけを差し替え、派生マスターを作れる。`templates/corporate.json` は
この方法で `aixdevops` から作られた。

> この手順は現在自動化されている: **`template-forge`** スキル /
> `scripts/build_template.py` が、デザイン仕様から派生の全工程（あるいは Google の
> 既定マスターをゼロからスタイリングする工程）を登録まで含めて実行する。
> 以下の手動手順は、その中身のリファレンスとして残している。

手順:

1. `drive.files().copy()` でテンプレートを複製し、同梱スライドをすべて削除する
2. **ブランド固有の要素を `deleteObject` で削除する**（ワードマーク、製品ロゴ、元デッキのスクリーンショット、…）。オブジェクト ID は Drive のコピーで維持されるため、解析時の ID をそのまま使える
3. **テーマ色を参照するすべての要素を明示的な RGB で上書きする。** `colorScheme` は API で変更できないため、`theme:ACCENT5` のまま残したものは元のパレットに解決される
4. `inspect_template.py` で解析 → `roles` を検証 → 登録
5. サムネイルで目視検証する

> **色を書き換える前に必ず `propertyState` を確認すること。** テンプレートには
> 「色情報だけを持つ透明な全面矩形」（`propertyState: NOT_RENDERED`）が含まれる
> ことがあり、これを塗ると不透明になってマスターのロゴとフッターを覆ってしまう。
> 詳細は `references/api-notes.md` 第 3b 節。

## `google-slides` スキルとの関係

両スキルは現在この 1 つのリポジトリに同居し、`scripts/`、`assets/`、`config/`、
`templates/` を共有している。同じエンジンに対する 2 つのエントリポイントである:

| | このスキル | `google-slides` |
|---|---|---|
| アプローチ | テンプレート駆動: 既存マスターのレイアウトにテキストを流し込む | ゼロから: ブランク/16:9 テンプレート上のコンポーザー、インフォグラフィクス、アーキテクチャ図、さらにコードファーストの `deckkit` パス（Python のデッキモジュールを `render_deck.py` でレンダリング） |
| 生成の起点 | マスターのコピー（`scripts/build_deck.py`） | `presentations().create()` + BLANK への描画 / `render_deck.py` |
| デザインの正 | `templates/<id>.json`（レイアウト構造、座標、role 割り当て） | `templates/themes/*.json` のデザイントークン（フォント階層、表スタイル、チャート色）と `deckkit` のレイアウト定数 |
| オフライン検証 | `build_deck.py --dry-run --strict` | `validate_layout.py`（`references/validation.md` 参照） |

`templates/scalar-2026.json` と `templates/themes/scalar.json` は**同じマスター
（`1shiZp7…`）を指している**。上記のとおり役割が違うため、両方が存在する。
コピー方式の生成は**このスキルのパスにのみ**実装されている（`build_deck.py`）。

マスター自体が更新されたときは、両者を同期させること:

1. 再解析: `.venv/bin/python scripts/inspect_template.py <URL> --emit templates/scalar-2026.json --name scalar-2026`
2. `roles` を再検証して確定する
3. `templates/themes/scalar.json` の `layouts.*.layoutId` と `master.sampleSlideIds` を突き合わせて更新する
