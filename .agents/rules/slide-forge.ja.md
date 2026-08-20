*[English](slide-forge.md)*

# slide-forge Project Guidelines for Antigravity

このリポジトリは、Google Slides デッキ生成・インフォグラフィックス作成・Visual QA・PPTX変換・スプレッドシート作成のための統合エンジン（`slide-forge`）です。Claude Code を主ホスト兼配布経路とします。Antigravity は同じ共有 `skills/`、`commands/`、`references/workflow-contract.md` を使う薄い互換レイヤーであり、ここへワークフローロジックを複製しません。

## 1. 実行環境ルール

- **Python バージョン / venv**:
  スクリプトを実行する際は、必ずプロジェクト直下の仮想環境 `.venv/bin/python` を使用してください。
  ```bash
  .venv/bin/python scripts/<script_name>.py [args]
  ```
- **言語設定**:
  スクリプトの出力言語を日本語にする場合は、環境変数 `GSLIDES_LANG=ja` を設定してください。
- **設定・認証情報**:
  OAuth認証情報 (`config/credentials.json`, `config/token.json`) や Gemini API キー (`config/gemini_api_key` または `GEMINI_API_KEY`) を使用します。認証エラーが発生した場合は、プロンプトの指示に従って再認証スクリプトを実行します。

## 2. スキルの活用

スライド作成・編集・検証などのタスク依頼を受信した場合は、`.agents/skills/` 内にある該当スキルの `SKILL.md` を読み込み、その手順に従って実行してください。

生成スキルは1つだけ選んで最後まで読み、その後は `references/workflow-contract.md` が有効化するreferenceの該当節だけを読みます。リンクされたマニュアルやカタログを事前に全件読み込みません。

| タスク / 目的 | 使用する Skill (`.agents/skills/`) |
|---|---|
| デッキ生成を一連の流れで一括実行（パイプライン） | `forge` |
| 登録テンプレート/マスターを使ったスライド作成 | `google-slides-template` |
| ゼロからのスライド生成（マスター無し） | `google-slides` |
| 新規マスターテンプレートの作成・登録 | `template-forge` |
| 再利用可能な 1 枚ものコンテンツテンプレートの作成・登録 | `slide-template-creator` |
| 提供素材からの現状分析・課題特定 | `current-state-analysis` |
| 分析フレームワークのスライドテンプレートの作成・変更 | `analysis-template-creator` |
| Scalar 社製品・提案スライドの作成 | `scalar-product-slides`, `scalar-proposal-slides` |
| 顧客ごとの活動計画・訪問資料（AE の営業活動） | `scalar-account-plan`, `scalar-ae-materials` |
| Account Planning Session（年次の組織図・商談棚卸しデッキ） | `scalar-account-planning-session` |
| B2B 商談の関与者マップ・ディスカバリーマップ作成 | `b2b-account-maps` |
| draw.io による密なアーキテクチャ図作成 | `drawio-diagrams` |
| 画像枠の自動埋め込み (AI画像生成含む) | `image-slots` |
| サムネイルベースの視覚的検証（Visual QA） | `slide-qa` |
| PowerPoint (`.pptx`) 形式へのエクスポート | `pptx-export` |
| 見積もり明細などのスプレッドシート生成 | `spreadsheets` |
| 画像生成・出力先スイッチの変更 | `settings` |

## 3. インタラクティブ質問

前提条件のヒアリングや、Visual QAの実施有無、PPTX書き出しの要否などを確認する際は、Antigravity の `ask_question` ツールを積極的に活用してユーザーに選択肢を提示してください。
