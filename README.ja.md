*[English](README.md)*

# slide-forge

Codex と Claude Code のためのエージェント駆動 Google Slides デッキ生成。共有
Python エンジンの上に、17 の生成/支援スキルと 1 つのエンドツーエンドワークフローを
載せる。コーポレートテンプレートのデッキ、ゼロからのアーキテクチャ図、デザイン
仕様からのテンプレート作成、生成前の検証、任意のサムネイルベース視覚 QA
（既定で有効）、PowerPoint（`.pptx`）エクスポート、見積もり・BOM 向けの
明細スプレッドシート（Excel / Google Spreadsheet）までをカバーする。

```
intake → author (spec JSON or Python) → validate (offline, free) → generate → visual QA (opt-in, default on) → cleanup → PPTX export (opt-in)
                                            ↑____________fix_____________________|
```

## スキル

| スキル | 何をするか |
|---|---|
| `google-slides-template` | 登録済みの Google Slides マスターテンプレートからデッキを生成する: 対話的インテイク、テンプレート解析・登録（`template.json`）、`--dry-run` 検証つきの仕様作成、大規模デッキ向けのページ分割執筆（許可されていれば並列、そうでなければ逐次）、生成。メインのワークフロー。 |
| `google-slides` | コーポレートマスターを使わないゼロからのデッキ生成。仕様パス（`templates/blank-16x9.json` + 同一エンジン）と、コードファーストパス（`deckkit.py` + コネクタの多い図向けのオフラインレイアウト検証）。 |
| `template-forge` | デザイン仕様 — ブランドカラー、フォント、ロゴ、フッター — から**新しいテンプレート（マスター）**を作成・登録する（`scripts/build_template.py`）。Slides API はマスターを作れないため、ベース（Google デフォルトまたは登録済みテンプレート）をコピーしてそのレイアウトを batchUpdate で再スタイルする。ロールは決定的に割り当てられ、結果は `templates/<id>.json` に登録されて、そのまま `google-slides-template` で使える。3 つのデザインプリセット（`templates/presets/`）を同梱。 |
| `slide-template-creator` | 意味づけされた入力スロット・作例・オフライン検証・カタログプレビューを備えた、再利用可能な**1 枚ものコンテンツテンプレート**を作成・登録する。`slide-templates/` 配下に置かれ、Google Slides のマスターからは独立している。 |
| `current-state-analysis` | ユーザー提供の材料に対して**現状分析・課題の特定フレームワーク**を実行し、結果を `analysis` パックで描画する: PEST、Five Forces、業務プロセスのペインポイント、ロジックツリー、KPI ツリー、なぜなぜ分析、フィッシュボーン、パレート、As-Is/To-Be ギャップ分析、インパクト×工数の優先度マトリクス（SWOT / 3C は `marketing-analysis` パックを再利用）。事実は図に、解釈は示唆に置き、出典は必須。各テンプレートのガードレールには手法ごとの誤用パターンを織り込んである。 |
| `analysis-template-creator` | **分析フレームワークのスライドテンプレート**そのもの（`slide-templates/analysis/` パック）とその描画プリミティブ（先例は `fishbone`、`pareto`）を作成・保守する: フレームワーク固有のデザインルール — 1 テンプレート 1 問い、事実/解釈のスロット分離、出典必須、誤用ガードレール — をここで定め、それ以外はすべて `slide-template-creator` のスキーマ・検証・登録ルールに従う。 |
| `b2b-account-maps` | B2B ソフトウェア商談の帰趨を左右する 2 つのアカウントマップを作る: 購買委員会の**インフルエンスマップ**（影響力 × 賛否、チャンピオンを強調表示）と、MEDDPICC の各項目を確認済み / 一部把握 / 推測のままで塗り分ける**ディスカバリーマップ**。加えて委員会テーブル、承認経路、ペインチェーン、そして「誰にいつまでに聞くか」つきのギャップ一覧。8 つのページテンプレートを `b2b-sales` パックとして `slide-templates/` に同梱。顧客提示用ではなく社内の作業成果物。 |
| `scalar-account-plan` | 顧客ごとに 1 つの**営業台帳**（`accounts/<AE>/<customer>/account.json`）を維持する — 発言 / 観察 / 推測のラベルつき事実、購買委員会、MEDDPICC の状況、ペインチェーン、BANT リスク、現在のステージの Exit 条件とその顧客側エビデンス、未完了アクション — そしてそれを **URL の変わらない** 9 ページの活動計画としてレンダリングする（`build_deck.py --into` が既存デッキのページを差し替える）。台帳が答えられないことがそのまま成果物になる: `account_ledger.py gaps` がプレイブックの 10 のレビュー質問を照合し、未回答の質問をすべて「誰に聞くか・期限・完了条件」つきのアクションに変換して実行間で引き継ぎ、スライドと CRM 向け Markdown の両方に書き出す。社内専用。 |
| `scalar-account-planning-session` | 台帳が既にカバーしているアカウントについて、年次の **Account Planning Session** デッキ — アカウントチーム向けのフル Plan Document と 9 ページのエグゼクティブレビューデッキ — を、顧客の公開資料を台帳に加えた 1 つの `aps.json` から作る。各提案を顧客自身の中期経営計画の一文に結びつけ、商談ごとに独立した章を与え、公開されている役員一覧と組織図から法人ごとに**次に誰と会うべきか**を導き、各人名には経由すべき人物を添える。ビルダーが持つのはレイアウトだけで、文字列はすべて gitignore された `accounts/` ツリー配下の `aps.json` にある。社内専用。 |
| `scalar-ae-materials` | 商談フェーズ（0–6）× 相手 × 目的でルーティングして**1 回の訪問の資料**を作り、顧客提示のワンページャー、社内向け訪問計画、WPS ウィンプラン、Deal Desk / 稟議パケットが決して同じファイルにならないようにする。特定個人への評価・競合の弱点・未確認の数字が顧客の目に触れるものへ紛れ込まないことを生成前に確認するチェックを含み、各成果物を Drive の `<root>/<AE name>/<customer name>/{00_活動計画, 01_顧客提示, 02_顧客提案, 90_社内}` に格納する。8 つのページテンプレートを `scalar-ae` パックとして同梱。ルールは `references/scalar/sales-playbook.ja.md` に従う。 |
| `scalar-product-slides` | `scalar-2026` テンプレートによる Scalar Inc. の会社・製品・機能デッキのワークフロー。 |
| `scalar-proposal-slides` | 顧客の課題を起点とする顧客別 Scalar ソリューション提案: ヒアリングチェックリスト、課題→製品マッピング（`references/scalar/proposal-map.ja.md`）、書き換え可能な実例つきの課題解決型提案構成（`scripts/scalar/build_scalar_proposal.py`）。 |
| `drawio-diagrams` | 密度の高いクラウドアーキテクチャ / データフロー / ネットワーク図を draw.io ファイルとして作成し、ヘッドレスで PNG に書き出し（`drawio` CLI）、視覚的に QA してデッキに挿入する。編集可能な `.drawio` はデッキの Drive フォルダにアーカイブされる。 |
| `image-slots` | **既存**デッキの空の画像フレームを AI 生成画像で埋める（`scripts/fill_image_slots.py`）: テンプレート登録と同じ 3 通りの方法でフレームを見つけ（PICTURE プレースホルダー、レイアウトに残された空の画像要素、デッキが使い回しているフレーム）、フレームの形状に合わせて各画像を描き、フレームいっぱいに配置する。任意のデッキ URL に対して単体で動作し — slide-forge が生成していないデッキも含む — 登録済みテンプレートも不要。仕様で管理しているデッキでは、代わりに仕様に `aiImage` を書いて再生成すること。 |
| `slide-qa` | 生成済みデッキのサムネイルベース視覚 QA: 全ページを PNG で取得し、欠陥チェックリストに照らして点検し、修正と再生成のループを回し、最後にローカルの QA ファイルを削除する（`scripts/cleanup_qa.py`）。インテイクでユーザーが選択した場合（既定で有効）に生成スキルから呼ばれるほか、任意のデッキ URL に対して単体でも実行できる。 |
| `pptx-export` | 生成済みデッキを納品形式として PowerPoint（`.pptx`）にエクスポートする（`scripts/export_pptx.py`）: 10MB 制限を自動フォールバックで回避する Drive API エクスポート。ローカルに保存し、任意でデッキの Drive フォルダにもアーカイブする。PPTX 納品が想定される場合はインテイク（出力形式）で選択するか、任意のデッキ URL に対して単体で実行する。ゼロからの PPTX 作成は引き続き `document-skills:pptx` の担当。 |
| `spreadsheets` | 見積もり、BOM、コスト内訳といった明細スプレッドシートを、1 つの JSON 仕様から Excel および/または Google Spreadsheet として生成する（`scripts/build_sheet.py`）: 型付きカラム、金額と小計/税/合計の実数式、`--dry-run` 検証、Spreadsheet の URL を保ったままのインプレース更新。提案デッキのコストスライドの伴走成果物（同じ Drive フォルダ）としても、単体でも使える。実例: `examples/estimate-sample.json`。 |

## エンドツーエンドワークフロー

`forge` ワークフローはパイプライン全体を 1 つの連続した流れとして実行する:
適切な生成スキルへのルーティング → 対話的インテイク（視覚 QA と出力形式の
選択を含む）→ アウトライン承認 → 仕様 + オフライン検証 → 生成 →
`slide-qa` による視覚 QA（選択時）→ QA ファイルの後片付け → `pptx-export` に
よる PPTX エクスポート（選択時）→ 最終報告。

- Codex: `forge` スキルを名前で呼び出す。
- Claude Code: `/forge` または `/slide-forge:forge` を使う。

### Account Executive ワークフロー

成果物がデッキではなく AE の次のアクションになる営業側は、さらに 2 つの
コマンドがカバーする:

- `/account <顧客名>` — 顧客の活動計画を作成・更新する。台帳を読み、直近の
  ミーティングで分かったことを記録し、プレイブックの 10 のレビュー質問を
  照合し、未回答のものを期限つきアクションに変換して、同じ活動計画デッキの
  中身を差し替える（共有リンクはそのまま使い続けられる）。
- `/visit <顧客名>` — 1 回の訪問を準備する。フェーズ × 相手から適切な資料
  タイプへルーティングし、顧客提示物と社内資料をファイルもフォルダも分けた
  まま生成・格納し、訪問結果を台帳へ書き戻して活動計画を更新する。

どちらも情報源は `accounts/<AE 名>/<顧客名>/account.json`（git-ignored）に
一本化し、出力は `<Drive ルート>/<AE 名>/<顧客名>/` 配下に格納する。
Drive ルートは最初に一度だけ聞かれ、`config/sales.json` に記憶される。
フェーズ、ゲート ID、5 つの資料タイプ、10 のチェックポイントはすべて
`references/scalar/sales-playbook.ja.md` にある。

## リポジトリ構成

```
.agents/      Codex のスキル発見用リンクと Codex ネイティブの forge スキル
AGENTS.md     Codex 向けプロジェクトルールとホストツール互換マッピング
skills/       Codex と Claude Code が共用する SKILL.md 定義
commands/     Claude Code スラッシュコマンド (/forge, /account, /visit)
accounts/     顧客ごとの営業台帳 (git-ignored。コミット禁止)
scripts/      共有エンジン — 1 つのインポート可能なパッケージ
  _auth.py        OAuth ヘルパー (Slides + Drive)
  build_deck.py   テンプレート駆動ジェネレーター (TemplateDeck)。--dry-run 検証
  diagrams.py     Canvas 描画ハブ (下記の mixin を集約)
  charts.py illustrations.py patterns.py pages.py events.py   図表ライブラリ
  icons.py cloud_icons.py images.py                 ピクトグラム、ベンダーアイコン、AI 画像
  inspect_template.py assemble_spec.py layout_sample.py list_templates.py
  account_graph.py build_account_graph.py   インフルエンス / ディスカバリーグラフ -> .drawio
  scalar/account_ledger.py       顧客ごとの営業台帳: 検証、gaps、スロットデータ
  scalar/account_workspace.py    Drive ツリー <root>/<AE>/<customer>/… (冪等)
  scalar/build_account_plan.py   台帳 -> 活動計画デッキ (更新後も同じ URL)
  export_template_master.py import_template_master.py   同梱マスター <-> Drive
  fetch_thumbnails.py cleanup_qa.py fetch_cloud_icons.py export_pptx.py
  build_sheet.py  明細スプレッドシート (xlsx + Google Spreadsheet)
  deckkit.py render_deck.py validate_layout.py      コードファーストパス (オフライン検証)
  drawio_export.py drive_folder.py snapshot_version.py   draw.io 書き出し、Drive フォルダ、バージョンスナップショット
  scalar/         Scalar デッキビルダー
templates/    登録済みマスター (scalar-2026*, aixdevops, corporate) + blank-16x9 + themes/ + presets/ (template-forge のデザインプリセット)
  masters/        マスター .pptx をここに置いてインポートする (gitignored。同ディレクトリの README 参照)
slide-templates/ 再利用可能な 1 枚ものコンテンツテンプレート + レジストリ
assets/       scalar/ (ブランド: ピクトグラム、ロゴ、製品ロゴ), cloud-icons/ (gitignored)
references/   エンジン・ワークフロー・ホスト互換のドキュメント
  images/slide-patterns/  パターンカタログ画像 (コミット済み。セットアップ 6 で再生成)
  i18n/           生成される 2 つのカタログ用の英語サイドカー文字列
examples/     実行可能な仕様カタログとコードファーストのサンプルデッキ
config/       credentials.json + token.json (gitignored, 0600)
cache/ out/   一時レンダーキャッシュと QA 出力 (gitignored)
```

## Claude Code プラグインとしてのインストール

このリポジトリはプラグインマーケットプレイスを兼ねる
（`.claude-plugin/marketplace.json`、17 スキルすべてを束ねた 1 プラグイン）:

```
/plugin marketplace add wfukatsu/slide-forge
/plugin install slide-forge@slide-forge
```

スキルは `slide-forge:<skill-name>` として、パイプラインコマンドは
`/slide-forge:forge` として使えるようになる。インストール後、プラグイン
ルート（`${CLAUDE_PLUGIN_ROOT}`）の中で後述のセットアップを実行すること —
venv、OAuth 認証情報、クラウドアイコンはマシンローカルであり、同梱されない。
別の方法として、リポジトリをクローンして `skills/*` を `~/.claude/skills/`
にシンボリックリンクしてもよい（開発中に使っている構成）。ただし 2 つの
方法はどちらか一方だけを選ぶこと。両方使うとスキルが二重に列挙される。

## Codex での利用

Codex も同じスキルと Python エンジンを使う。リポジトリのクローンでは、
`.agents/skills/` のエントリが 17 の生成/支援スキルすべてと、エンドツー
エンドの `forge` スキルを公開する。リポジトリルートから Codex を起動し、
`forge` を名前で呼び出せばよい。Claude 固有の `/slide-forge:forge`
コマンドやプラグインマーケットプレイスのマニフェストは不要。

プロジェクト全体の Codex 向け指示は `AGENTS.md` にある。ホストツールの
マッピング、エージェント委譲が使えない環境向けの逐次フォールバック、
セットアップの詳細は
[`references/codex-compatibility.md`](references/codex-compatibility.md)
に記載している。

`.agents/skills/*` のシンボリックリンクは `skills/*` を指しているため、
Codex と Claude Code はコピーを二重管理せず、同じスキル定義を読む。

リポジトリルートから、Codex に `forge`・`google-slides`・`slide-qa`
スキルの列挙や利用を頼んで、スキル発見を確認するとよい。Codex に
Claude プラグインのインストールは不要。

## 動作要件

- **Python 3.10+**（macOS / Linux）
- Google Slides / Drive のファイルを作成できる Google アカウント
- **draw.io desktop** — `drawio-diagrams` スキルでのみ必要:
  `brew install --cask drawio`（エクスポートスクリプトは
  `/Applications/draw.io.app` のアプリバンドル内バイナリも見つける）
- Gemini API キー — 任意の AI 画像生成でのみ必要

## セットアップ

コマンドはすべて slide-forge のルートから実行する: Codex やローカルの
Claude 構成ではクローンしたディレクトリ、Claude プラグインとしての
インストールでは `${CLAUDE_PLUGIN_ROOT}`。

**一部のものはコミットされておらず、各自のマシン上で生成する** — クラウド
ベンダーアイコンとスライドマスターがそれにあたる。サイズが大きい（マスターは
1 つ 6–8MB）、マシン固有、あるいは当方に再配布権がないため、リポジトリは
ファイルそのものではなく生成する手段を同梱している。クローンは、必要な
下記の手順を実行して初めてフルに使える状態になる。

| ここで生成されるもの | コミットしない理由 | 手順 |
|---|---|---|
| `assets/cloud-icons/` | AWS / Google Cloud / Azure が再配布を許可していない | [4](#4-クラウドベンダーアイコンクラウドアーキテクチャ図を描く場合のみ) |
| `templates/masters/*.pptx` | 1 つ 6–8MB。マスターは*自分の* Drive にあって初めてコピーできる | [5](#5-スライドマスターcopy-モードのテンプレート用) |

### 1. Python 環境

リポジトリはルート直下の `.venv` を前提とする。ローカル環境が最も簡単な
クロスホスト構成になる:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

アップグレード時に置き換えられうる Claude プラグインインストールでは、
実体の環境をプラグインルートの外に置くと都合がよい。共有の venv を作り、
絶対パスのシンボリックリンクで `.venv` からそこを指す。歴史的な
`~/.claude/venvs/gslides` の場所も引き続きサポートされるが、Codex にも
エンジンにも必須ではない。

### 2. Google Cloud OAuth クライアント（初回のみ）

エンジンは OAuth デスクトップクライアント経由で、**あなた自身として**
Slides + Drive API を呼び出す（スコープ: `auth/presentations`、
`auth/drive`）。[Google Cloud Console](https://console.cloud.google.com/) で:

1. プロジェクトを作成する（または既存のものを選ぶ）。
2. **APIs & Services → Library** — **Google Slides API** と
   **Google Drive API** を有効化する。
3. **APIs & Services → OAuth consent screen** — アプリを設定する
   （Workspace 組織なら Internal。External でも動作する — アプリが
   Testing の間は自分をテストユーザーに追加すること）。
4. **APIs & Services → Credentials → Create credentials → OAuth client ID →
   Desktop app** — JSON をダウンロードして `config/credentials.json` として
   保存する（`chmod 600`）。認証情報を別の場所に置く場合は
   `$GSLIDES_CONFIG_DIR` でディレクトリを上書きできる。

### 3. 初回実行と確認

```bash
.venv/bin/python scripts/list_templates.py
```

CLI メッセージは既定で英語。日本語にするには `GSLIDES_LANG=ja` を設定する
（`export GSLIDES_LANG=ja`、またはコマンドごとに指定）。これはスクリプトの
端末出力にだけ効き、生成されるデッキやスプレッドシートの内容には決して
影響しない。

初回の呼び出しではブラウザに同意画面が開き、`config/token.json` が書き
出される（以後は自動更新）。テンプレート一覧が表示されれば認証は成功。

### 4. クラウドベンダーアイコン（クラウドアーキテクチャ図を描く場合のみ）

AWS / Google Cloud / Azure のアイコンセットはベンダーの資産であり、
**コミットされていない**。一度だけ取得する:

```bash
.venv/bin/python scripts/fetch_cloud_icons.py
```

### 5. スライドマスター（`copy` モードのテンプレート用）

`scalar-2026`、`scalar-2026-boilerplate`、`corporate`、`aixdevops` は
`generationMode: copy` のテンプレートで、生成は実在する Google Slides
プレゼンテーションの複製として行われる。`templates/<id>.json` はそれを
*指している*だけなので、フレッシュなクローンでは、マスターが自分の
Drive に存在するまでこれらのテンプレートは動かない。

マスター自体は**コミットされていない** — 1 つ 6–8MB あり、マスターは
自分の Drive にあって初めて意味を持つ。以下から該当するものを選ぶ:

**a. 自分で作る。** `template-forge` スキルがデザイン仕様 — ブランド
カラー、フォント、ロゴ、フッター — から新しいマスターを作成・登録し、
そのまま `google-slides-template` で使える。他には何も要らない。既存の
コーポレートデッキを使わないならこの道。

```bash
.venv/bin/python scripts/build_template.py --help
```

**b. Drive に既にあるマスターを登録する。** 一度解析し、推測された
ロールを手で確認する:

```bash
.venv/bin/python scripts/inspect_template.py <URL> --emit templates/<id>.json --name <id>
```

**c. マスターの `.pptx` をインポートする。** `templates/masters/<id>.pptx`
として保存し、アップロードと再登録を一度に行う:

```bash
.venv/bin/python scripts/import_template_master.py --all
# or one at a time
.venv/bin/python scripts/import_template_master.py --id scalar-2026
```

`.pptx` をインポートすると Slides はすべてのレイアウト・マスター・装飾に
新しいオブジェクト ID を発行するため、スクリプトはインポートされた
プレゼンテーションに対して `inspect_template.py` を再実行し、その結果で
`templates/<id>.json` を上書きする。人手で確認済みの**ロール割り当ては
保持され**、識別子だけが移る。以後 `templates/*.json` はローカル変更
ありと表示されるはずだが、それはあなたのマシン上の登録情報であり、
コミットして戻すものではない。

既にマスターへの編集権限があるなら、
`scripts/export_template_master.py --all` でチームメイト向けに書き出せる。Drive は 10MB を超える
Docs-editors ファイルのエクスポートを拒否する（`exportSizeLimitExceeded`）
ため、それより大きいマスターは Slides の UI から手動でダウンロードする
（File > Download > Microsoft PowerPoint）。制限内に収めるために
スライドを削除しては**いけない**: Slides はどのスライドからも使われて
いないレイアウトを落とすため — `aixdevops` はこれで登録済みレイアウトを
3 つ失う — また `existingSlideIds` に列挙された同梱スライドはこれらの
テンプレートが提供する価値の一部でもある。
[`templates/masters/README.md`](templates/masters/README.md) を参照。

`blank-16x9` は `generationMode: create` でマスターを必要としないため、
`google-slides` の仕様パスとすべての `--dry-run` 検証は素のクローンでも
動く。

### 6. スライドパターンカタログ画像

[`references/slide-pattern-catalog.md`](references/slide-pattern-catalog.ja.md)
は全 43 ページパターンをレンダリング済み画像つきで見せる。テキストも画像
（約 2MB、`references/images/slide-patterns/` 配下）もコミット済みなので、
素のクローンでも図入りで読める。パターンを追加したり描画が変わったりした
ときは、カタログを再生成して画像ごとコミットする:

```bash
.venv/bin/python scripts/build_deck.py \
    --template templates/scalar-2026.json --spec examples/slide-pattern-index.json
.venv/bin/python scripts/fetch_thumbnails.py <URL printed above> --out out/patterns --size MEDIUM
.venv/bin/python scripts/build_pattern_catalog.py --thumbs out/patterns
```

再生成には動作する `scalar-2026` マスター（手順 5）と、3 つのクラウド
アーキテクチャパターンについてはベンダーアイコン（手順 4）が必要。

どちらのカタログ生成器もバイリンガルで、1 回の実行で英語版を元のパスに、
日本語版をその `.ja.md` の隣ファイルに書き出す。日本語テキストはソース
データ（パターン仕様 / 各 `template.json`）から、英語テキストは
`references/i18n/` 配下のサイドカーから来る。サイドカーにエントリのない
新しいパターンやテンプレートは警告つきで日本語にフォールバックするので、
追加時には英語文字列もそこへ足すこと。

スライドテンプレートカタログ
（[`references/slide-template-catalog.md`](references/slide-template-catalog.ja.md)、
画像は `references/images/slide-templates/` 配下、こちらもコミット済み）も
同じ仕組みで動く: `scripts/build_slide_template_catalog.py` で各パックの
カタログ仕様を組み、デッキを生成し、サムネイルを取得し、
`scripts/build_template_catalog_doc.py` を実行する — 再生成コマンドは
その文書の冒頭にある。

### 7. 任意: AI 画像生成

`scripts/images.py` を使うには、`GEMINI_API_KEY` を設定するか、キーを
`config/gemini_api_key` に保存する（OAuth ファイル同様 gitignored）。
キーは**課金設定済み**プロジェクトのものであること — 画像モデルには
無料枠のクォータがない。

### 各スキルに必要なもの

| スキル | venv + OAuth | スライドマスター | クラウドアイコン | draw.io CLI | Gemini キー |
|---|---|---|---|---|---|
| `google-slides-template` | ✔ | ✔ copy モードのテンプレートで必要 | クラウド図を描くとき | — | 任意 |
| `google-slides` | ✔ | —（blank-16x9 は不要） | クラウド図を描くとき | — | 任意 |
| `scalar-product-slides` | ✔ | ✔ scalar-2026 | クラウド図を描くとき | — | — |
| `scalar-proposal-slides` | ✔ | ✔ scalar-2026 | — | 同梱の環境図を編集するとき | — |
| `drawio-diagrams` | ✔（デッキ挿入時） | — | — | ✔ | — |
| `slide-qa` | ✔ | — | — | — | — |
| `pptx-export` | ✔ | — | — | — | — |
| `spreadsheets` | ✔（OAuth は Google Spreadsheet 出力時のみ） | — | — | — | — |
| `template-forge` | ✔ | コピーする場合はベースのマスター | — | — | — |

秘密情報の衛生: `config/`（認証情報、トークン、API キー）、`out/`、
`cache/`、`assets/cloud-icons/` は gitignored — マシンローカルなものが
コミットされることはない。マスターデッキの Drive 共有は制限したままに
すること。それらのファイル ID は `templates/*.json` に現れる。マスターも
コミットされない: `templates/masters/` は gitignored なので、そこに置いた
マスター .pptx はローカルに留まる。マスターを共有する前には中身を確認する
こと — `scalar-2026-boilerplate` は会社紹介や顧客提示用のスライドを含む。

## クイックスタート（テンプレート駆動）

```bash
.venv/bin/python scripts/list_templates.py                 # registered templates
.venv/bin/python scripts/build_deck.py \
    --template templates/scalar-2026.json --spec deck.json --dry-run --strict
.venv/bin/python scripts/build_deck.py \
    --template templates/scalar-2026.json --spec deck.json
.venv/bin/python scripts/fetch_thumbnails.py <URL> --out out/qa   # visual QA (slide-qa skill)
.venv/bin/python scripts/cleanup_qa.py                            # delete QA files when done
.venv/bin/python scripts/export_pptx.py <URL> --folder <FOLDER>   # optional PPTX delivery (pptx-export skill)
```

新しいマスターの登録: `scripts/inspect_template.py <URL> --emit templates/<id>.json --name <id>`
を実行し、推測されたロールを手で確認する（google-slides-template スキル参照）。

## クイックスタート（コードファースト）

デッキは 1 つの Python モジュール、関数は 1 枚のスライド。
`examples/pattern-gallery/deck.py` と `references/diagram-cookbook.ja.md`
を参照。

```bash
.venv/bin/python scripts/validate_layout.py mydeck.py   # offline checks, no API calls
.venv/bin/python scripts/render_deck.py     mydeck.py   # validates, then generates
```

`validate_layout.py` は、フッターへの侵入、スライド外のジオメトリ、
タイトルの折り返し、浮いた/埋もれたコネクタ端点、後から描かれた図形の
背後に隠れたテキスト、テキストのあふれを — API 呼び出しの前に — 検出する。
これが判定できないこと（矢印の経路、コントラスト、図が伝わるかどうか）を
担うのが `slide-qa` スキルのサムネイル QA:
`references/validation.ja.md` を参照。

## スライドパターンカタログ

どんな形のページが作れるか?
[`references/slide-pattern-catalog.md`](references/slide-pattern-catalog.ja.md)
を参照 — 43 パターンを 8 分類で、それぞれレンダリング済み画像・使いどころ・
仕様に書く `figures` の type 名つきで並べてある。背後のレイアウトルールは
[`references/slide-patterns.md`](references/slide-patterns.ja.md) にある。

| 分類 | パターン数 | 選びどころ |
|---|---|---|
| 骨格 6 種 | 6 | ページそのものの組み方 |
| 構成ページ | 4 | デッキの足場 — サマリー、アジェンダ、ストーリーライン、ゴースト |
| 定量ページ | 7 | 数字で論じる |
| 比較・評価ページ | 6 | 選択肢を並べて比べる |
| 構造・論理ページ | 7 | 関係を見えるようにする |
| 計画・体制ページ | 5 | 時間と体制 |
| 定性・技術ページ | 5 | 数字でないものすべて |
| 締め・付録ページ | 3 | 決定とその後 |

これらのページパターンに加えて、`slide-templates/` には 6 つのパック
（marketing-analysis、b2b-sales、scalar-ae、planning、analysis、read-alone）で
45 の既製 1 枚ものテンプレートが登録されている。それぞれレンダリング済み画像、
答える問い、ガードレールつきで
[`references/slide-template-catalog.md`](references/slide-template-catalog.ja.md)
にカタログ化されている。read-alone パックのテンプレートは `$density`
バリアントを持ち、同じテンプレートが高密度の配布資料（`print`）と低密度の
登壇スライド（`presentation`）のどちらでも描画できる。密度はインテイクの
「用途」の回答か `render_slide_template.py --density` で選ぶ。

## サンプル

`examples/` 配下の仕様はすべて **`templates/scalar-2026.json`** に対して
書かれており、それに対してはクリーンに検証を通る。
`templates/blank-16x9.json` には移植できない — そのテンプレートには TITLE
プレースホルダーがなく、`CLOSING` ロールも宣言していないため、同じ仕様が
数十件の指摘を報告する。`corporate` と `aixdevops` は一部を受け付け、
`scalar-2026` はすべてを受け付ける。

```bash
.venv/bin/python scripts/build_deck.py \
    --template templates/scalar-2026.json --spec examples/<name>.json --dry-run --strict
```

| サンプル | 枚数 | 見せるもの |
|---|---|---|
| `charts-demo.json` | 5 | 表とグラフ — `charts.py` のカタログ |
| `patterns-demo.json` | 7 | `patterns.py` のレイアウトパターン |
| `illustration-gallery.json` | 13 | `illustrations.py` のコンセプト図 |
| `icon-gallery.json` | 10 | ピクトグラムライブラリ（`icons.py`） |
| `code-blocks-demo.json` | 2 | シンタックスハイライトつきコードブロック |
| `event-announcement.json` | 4 | セミナー / カンファレンス告知の部品 |
| `read-alone-guide.json` | 30 | 配布・読み切り資料向けの密度パターン |
| `design-catalog.json` | 49 | デザインパターンのフルカタログ †|
| `slide-pattern-index.json` | 60 | 1 パターン 1 ページの索引 — 1 枚 = 1 パターン †|
| `cloud-architecture.json` | 6 | クラウドアーキテクチャ図 †|
| `b2b-account-review.json` | 13 | `b2b-sales` の 8 テンプレートすべてで組んだアカウントレビューの実例 — 表紙、エグゼクティブサマリー、2 軸/MEDDPICC 形式と構造形式の両マップ、それらを支えるページ |
| `estimate-sample.json` | 2 シート | `spreadsheets` スキル用の明細見積もり ‡|

† `cloud_icon*` / `cloud_zone` の図を描くため、先にベンダーアイコンが必要 —
AWS、Google Cloud、Azure が再配布を許可していないためリポジトリには
含まれない。ない状態で `--dry-run` を実行すると
`Cloud icons have not been fetched yet` と報告される。
`.venv/bin/python scripts/fetch_cloud_icons.py` を一度実行すること
（[`assets/cloud-icons/README.md`](assets/cloud-icons/README.md) 参照）。
上記の他のサンプルはすべて素のクローンで検証を通る。

‡ デッキではなくスプレッドシート — 代わりに `build_sheet.py` に通す:
`.venv/bin/python scripts/build_sheet.py --dry-run examples/estimate-sample.json`

コードファーストのデッキは仕様ではなく Python モジュールで、`scalar-2026`
に対して直接生成する:

| サンプル | 見せるもの |
|---|---|
| `examples/scalardb-architecture.py` | ScalarDB アーキテクチャ — クラウドアイコン、ピクトグラム、ブランドロゴ、コネクタを 1 枚に † |
| `examples/scalardl-architecture.py` | ScalarDL アーキテクチャ、同じ組み合わせ † |
| `examples/pattern-gallery/deck.py` | `deckkit.py` のコードファーストパス |

## ライセンス

MIT。クラウドベンダーアイコンは各ベンダーの資産のままであり、それぞれの
利用条件の下でローカルに取得される（`references/cloud-icons.ja.md` 参照）。
