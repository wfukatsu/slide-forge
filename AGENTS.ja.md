*[English](AGENTS.md)*

# slide-forge エージェント向け指示

Claude Code を主ホスト兼配布経路とする。Codex は同じ共有 Python エンジンと
`.agents/skills/` からリンクされた同じ `skills/` を利用する。動作の正本は
`commands/`、共有 `skills/`、`references/workflow-contract.md` とし、この文書は
薄い Codex 互換レイヤーに保つ。

## 実行環境

- Python コマンドはリポジトリルートから `.venv/bin/python` で実行する。
- OAuth 認証情報・トークン・生成ファイル・キャッシュは Git に含めない。
- `GSLIDES_LANG=ja` は日本語の CLI 出力が有用な場合にのみ使う。生成される
  コンテンツには影響しない。
- ユーザー所有の既存デッキを変更する前に、該当スキルの
  スナップショット / バージョン記録ルールに従う。

## スキルルーティング

該当するスキルを使い、作業前に必ずその `SKILL.md` を最後まで読むこと:

| 依頼内容 | スキル |
|---|---|
| デッキ生成をエンドツーエンドで一括実行 | `forge` |
| 登録済みテンプレート / マスターを使う | `google-slides-template` |
| コーポレートマスターなしのデッキ | `google-slides` |
| テンプレートの作成・登録 | `template-forge` |
| 再利用可能な 1 枚ものコンテンツテンプレートの作成・登録 | `slide-template-creator` |
| 提供素材からの現状分析 / 課題特定 | `current-state-analysis` |
| 分析フレームワークのスライドテンプレートの作成・変更 | `analysis-template-creator` |
| B2B の関与者マップ / ディスカバリー整理 | `b2b-account-maps` |
| 顧客ごとの活動計画・商談台帳（AE の行動計画） | `scalar-account-plan` |
| Account Planning Session（年次・半期の棚卸しと役員レビュー） | `scalar-account-planning-session` |
| 訪問 1 回分の資料 / 社内承認資料（WPS・Deal Desk） | `scalar-ae-materials` |
| Scalar の製品・会社紹介デッキ | `scalar-product-slides` |
| Scalar の顧客向け提案書 | `scalar-proposal-slides` |
| 密な draw.io 図 | `drawio-diagrams` |
| 既存の画像枠への埋め込み | `image-slots` |
| サムネイルによるビジュアル QA | `slide-qa` |
| Google Slides の PPTX エクスポート | `pptx-export` |
| 見積もり / BOM スプレッドシート | `spreadsheets` |
| 画像生成・出力先スイッチの変更 | `settings` |
| nexus-architect のレポート・UI モックの説明スライド化 | `nexus-report-slides` |

スキル選択後は、未選択のスキルや記載されたreferenceを一括で読み込まない。
`references/workflow-contract.md` の段階読込表に従う。

## ホストツール互換性

共有スキルドキュメントの一部には Claude Code の用語が残っている。Codex では
次の対応を適用する:

- テキストに対する `Read`: `rg`、`sed` などの読み取り専用シェルコマンドを使う。
- PNG/JPEG に対する `Read`: ローカルの画像表示ツールで実際のピクセルを確認する。
  ファイル名や API の成功はビジュアル QA ではない。
- `Write` / `Edit`: リポジトリ内のファイルには `apply_patch` を使う。
- `Bash`: リポジトリルートを `cwd` としてシェル実行ツールを使う。
- `Grep` / `Glob`: まず `rg` / `rg --files` を使う。
- `WebFetch` / `WebSearch`: 利用可能な Web ツールを使う。製品に関する事実や
  技術ドキュメントには公式の一次情報源を優先する。
- `AskUserQuestion` / `ask_question`: チャットで質問する。相互排他的な選択肢は
  番号付きリストで提示し、ユーザーの番号入力を待つ。複数選択はカンマ区切りの
  番号を受け付ける。スキルが承認ゲートを要求している箇所で無断に選択しない。
- `Task` / `Subagent` / `Parallel`: 並列エージェントは、現在のホストと
  セッション指示が明示的に許可している場合にのみ使う。それ以外は
  `references/parallel-generation.md` の逐次フォールバックに従う。
- `${CLAUDE_PLUGIN_ROOT}`: このリポジトリルートとして解決する。Codex では
  この変数が設定されている前提を置かない。

Codex の詳細なセットアップと既知の差異は
`references/codex-compatibility.md` にある。

## 安全性と検証

- API 書き込みの前に、ドキュメント化されたオフラインの
  `--dry-run` / レイアウト検証を実行する。
- `config/credentials.json`・`config/token.json`・API キーファイルの内容を
  決して公開しない。
- `accounts/` には顧客ごとの営業台帳がある — 実在する個人の名前と、その人物に
  関する判断が含まれる。Git では無視対象であり、決してコミットせず、顧客向け
  成果物に貼り付けず、`00_活動計画` / `90_社内` の Drive フォルダを顧客や
  パートナーと共有しない。
- 生成したページフラグメントと QA サムネイルは、無視対象の `out/` パス配下に置く。
- API 応答の成功はビジュアル QA ではない。QA を選択した場合はサムネイルを
  確認し、完了報告の前に `scripts/cleanup_qa.py` を実行する。
