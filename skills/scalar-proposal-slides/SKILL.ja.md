---
name: scalar-proposal-slides
description: >-
  Build a customer-specific Scalar solution proposal: start from the customer's
  challenges (hearing notes, meeting minutes), map them to ScalarDB / ScalarDL,
  and follow the problem-solving structure — exec summary, challenge agreement,
  solution, effects, PoC plan, costs, risks, next steps.
  Use for: 提案書を作って, 提案スライド, 顧客課題, ソリューション提案,
  〈顧客名〉向けの提案資料.
  Not: introduction decks with no specific customer (scalar-product-slides);
  non-Scalar proposals (google-slides-template); PPTX authoring
  (document-skills:pptx).
---

*[English](SKILL.md)*

# Scalar ソリューション提案スライド

作業ディレクトリ: slide-forge ルート — インストール済みプラグインから実行する場合は
`${CLAUDE_PLUGIN_ROOT}`、ローカルクローンでは `/path/to/slide-forge`
（以下に書く `cd` のパスはローカルクローンを前提とする）。

## 重要事項

- **前提スキル**: `google-slides-template`（同一リポジトリ） — 認証、共有 venv、
  `scalar-2026` テンプレート、描画 API、QA ツールを提供する。本スキルが持つのは
  提案固有の部分 — ヒアリングチェックリスト、課題→製品マッピング、
  提案デッキ構成 — のみである。
- **すべては顧客の課題から始まる。** 課題合意のない提案は製品紹介にすぎない —
  その場合は `scalar-product-slides` に回す。スライドを設計する前にヒアリング材料
  （議事録・メモ・RFP）を集める。分かっていないことは推測ではなく
  「本日確認したい」としてデッキ上に出す。
- **顧客固有の数値を捏造してはならない。** 効果の定量化にはヒアリングに基づく
  算定根拠が必要である。無ければ定性的な効果に留め、定量化は PoC に回す
  （"PoC で実測し稟議材料にする"）。公開事例の数値（ENS 約1/5 など）は
  出典つきなら使える。
- **初回提案には必ずアーキテクチャ図と BOM を含める。** 標準トポロジーは
  3 環境 — 開発（ローカル）/ テスト (aidd-infra-test) / ステージング
  (aidd-infra-staging) — で、**既定は AWS**（顧客の指定がある場合のみ GCP/Azure で
  同じ役割分担を組み直す）。アーキテクチャを構成したら、クラウドサービス一覧と
  Scalar 製品一覧を数量つきで（数量が未指定の場合は月額ライセンス費用も）出力する —
  デッキ上と、最終報告のリスト（proposal-map.md §6）の両方に。
- **提案する前に制約を確認する** —
  `references/scalar/proposal-map.md` §4（ScalarDB/DL が適さないケース）。
  課題を Scalar 製品に無理に当てはめない。適さないと言うことも提案品質の
  一部である。
- **製品事実と価格は OKF バンドルから取る** —
  所在と引用ルールは `references/scalar/okf-bundle.ja.md` にある。機能・エディション・
  バージョン・リリース状況・課金モデル・定価・Pod 数の数え方はそこを引き、記憶で
  書かない。バンドルは公開リポジトリなので数値は引用してよい — **定価（税抜）である旨を
  明示**し、参考見積の材料として扱う。顧客に出す見積は営業担当のレビューを通す。
  「非公開」の項目（3年契約・先払いクレジット・値引き率）は営業担当につなぐ。
- **調査の鮮度**: 事実は `references/scalar/research-2026-08.md` と
  `references/scalar/proposal-map.md`（§3/§5 は 2026-08-05 付）から取る。どちらも
  **3 か月ルール**に従う — 古ければ並列エージェントで再調査する
  （エージェントの構成は scalar-product-slides の SKILL.md の Phase 2 に記載）。
- **姉妹スキルと共通のルール**（google-slides-template の SKILL.md 参照）:
  デッキごとの Drive フォルダ（`scripts/drive_folder.py`）、インプレース編集前の
  バージョンスナップショット（`scripts/snapshot_version.py`）、`slide-qa` スキルに
  よるビジュアル QA — インテイク時に実行有無を選び、既定は実行、終了後に
  `scripts/cleanup_qa.py` で QA ファイルを削除 — と、対話インテイクの作法
  （`references/interactive-intake.md` セクション 0, 3, 4, 5）。

## クイックリファレンス

| やること | 使うもの |
|------|-----|
| ヒアリングチェックリスト / 提案構成 / 課題→製品マップ / 制約 / 価格 / 標準環境 + BOM | `references/scalar/proposal-map.md` |
| AE に渡すヒアリング様式（記入用） | `templates/sales/hearing-sheet.ja.md`（製品非依存）+ `templates/sales/products/scalar.ja.md`（Scalar 適合判定） |
| ヒアリングシートの Excel / Google Spreadsheet 化と読み戻し | `hearing-sheet` スキル（`scripts/hearing/hearing_sheet.py`） |
| 足りない情報を顧客に聞くためのスライド | `hearing-slides` スキル |
| 提案デッキビルダー（実例。アーキテクチャ + BOM 込み 23 スライド） | `scripts/scalar/build_scalar_proposal.py` |
| 環境図の元データ（3 環境、AWS） | `examples/scalar-proposal-envs.drawio` → `scripts/drawio_export.py` で PNG 化 |
| 製品機能 / エディション / バージョン / 定価 / Pod 数の数え方 | `references/scalar/okf-bundle.ja.md` → OKF バンドル |
| 調査済みの会社・製品の事実 + 落とし穴 | `references/scalar/research-2026-08.md` |
| セクション順の根拠（課題解決型アウトライン） | `references/deck-outlines.md` |
| 実行 | `cd /path/to/slide-forge && .venv/bin/python scripts/scalar/build_scalar_proposal.py [--folder <Drive URL>]` |
| まず検証（API 呼び出しなし） | 同じコマンドに `--dry-run` — デッキを作らずに座標とテキスト収まりの検査を実行 |

## Phase 1: 課題材料を集め、前提を確定させる

`references/interactive-intake.md` のセクション 0/3/4/5 に従う。1 バッチで聞く:

| # | header | 質問 | 選択肢 |
|---|---|---|---|
| 1 | 課題の材料 | 顧客課題の材料はありますか? | 議事録・ヒアリングメモを渡す(ファイル/貼り付け) / 口頭でこれから説明 / まだ無い(ヒアリング項目の提示から始める) |
| 2 | 課題カテゴリ | 主な課題はどれに近いですか? | proposal-map.md §3 の A〜H から材料に合いそうな 3 つ + その他(複数選択可) |
| 3 | 提案の段階 | どの段階の提案ですか? | 初回提案(課題合意が主目的) / PoC 提案(スコープ・成功基準まで) / 本導入提案(費用・体制を確定粒度で) |
| 4 | 決裁者 | 主な読み手は? | 経営層・決裁者 / 情報システム部門 / 業務部門 / 混合 |

- 材料が先: 議事録・メモがあれば **Q2 を聞く前に読み**、ありそうなカテゴリを
  選択肢の description で事前に選んでおく。
- まだ何も分かっていない場合は、デッキを無理に作らず、ヒアリング様式
  （`templates/sales/hearing-sheet.ja.md` + `templates/sales/products/scalar.ja.md`）
  を成果物として渡す。どの節が提案書のどこになるかはシート §14.3、
  背後のチェックリストは proposal-map.md §1。
- 記入済みのヒアリングシートがあれば先に読む。§4.2 / §5 が現状構成図と BOM の
  数量を、製品補遺 §B / §C がリスクスライドに載せるべき制約を持っている。
  `hearing.json` で持っている場合は、設計の前に `hearing_sheet.py gaps` を実行する。
  **`未確認` はデッキ上「本日確認したいこと」にする**（推測で埋めない）。
  `推定` は事実としてではなく、こちらの理解として書く。
- 未指定なら 2 ラウンド目で聞く: 出力先 Drive フォルダ、表紙の日付、言語、
  クラウド（既定は AWS — 顧客のクラウドが不明なときは質問せず、採用した既定を
  明示する）、生成後にビジュアル QA を実行するか（既定かつ推奨は実行。
  スキップするとデッキは未検証のまま納品される）。
- **聞いてはならないこと**: 図の構成、座標、色、どの部品がどのセクションを
  描くか — 実例とデザイン規約で固定されている。

その後、**スライドアウトライン（ページ数 + 各スライドのアクションタイトル、
課題→製品マッピングを明示）を提示し、生成前に承認を得る**
（interactive-intake.md §3 のアウトラインゲート）。

## Phase 2: 課題を製品にマッピングする

1. 合意した各課題を proposal-map.md §3 のカテゴリ（A–H）に分類し、同じ行から
   製品・機能の行と公開事例を引く。
2. §4（適さないケース）を確認する — 直接書き込みによるバイパス、DB 固有機能、
   OLAP 専用ワークロード、「改ざん防止」という表現、Community エディションの
   不足。該当があればリスクスライドの項目として出すか、正直にスコープ外にする。
3. §3/§5 と research-2026-08.md の鮮度（3 か月ルール）を確認する。古ければ
   調査エージェントを再実行し、スライドを書く前に research-2026-08.md 末尾の
   落とし穴リストを確認する。

## Phase 2.5: アーキテクチャと BOM を構成する

1. 標準の 3 環境トポロジー（proposal-map.md §6）から始める:
   開発（ローカル, Community・無料）→ テスト aidd-infra-test（Cluster 1 Pod）→
   ステージング aidd-infra-staging（Cluster 3 Pod）、既定は AWS。環境名・サイズ・
   本番環境はヒアリングに合わせて調整する。
2. 図は `examples/scalar-proposal-envs.drawio` から作る（編集 →
   `scripts/drawio_export.py` → PNG を Read。drawio-diagrams スキルのルールが
   適用される: 検証済みシェイプ名のみ使用、目視確認は必須）。
3. BOM を導出する: 環境ごとに、クラウドサービスと Scalar 製品を数量つきで挙げる。
   数量が顧客指定でない場合は §6 の計算式で月額ライセンス費用を算出する。
   Premium 機能や ScalarDL は単価が変わる（§5/§6）。
4. **顧客が編集可能な見積もりを必要とする場合**（明細付きの見積もり） —
   本導入提案で典型、またはユーザーが求めたとき — `spreadsheets` スキルで
   BOM から作成し（Excel / Google スプレッドシート、数量 × 単価と税の実数式入り）、
   デッキの Drive フォルダに入れる。費用スライドはサマリーを保持し、明細は
   スプレッドシートが担う。両者の合計は一致していなければならない。

これまでビルダーの中にしか無かった節に、登録済みテンプレートができた。
図形を手で並べ直さず、こちらを使う。

| 節 | テンプレート（パック） |
|---|---|
| 課題の構造 | `iceberg-challenge`（`proposal`） |
| 課題 → 解決のマッピング | `challenge-solution-map`（`proposal`） |
| 目指す姿とスコープ | `scope-in-out`（`proposal`） |
| 期待効果 | `outcome-before-after`（`proposal`） |
| PoC の目的と合否基準 | `poc-plan`（`proposal`） |
| 事例 | `case-study-card` / `case-study-detail` / `case-fit`（`case-studies`） |
| ネクストステップ | `next-step-customer`（`proposal`） |

事例ページには**顧客の公開許諾と、日付つきの出典**が要る。どちらも
`templates/marketing/case-study.ja.md` §1・§3 が持つ。
**許諾が「未取得」の事例を顧客提示物に載せない。**

## Phase 3: デッキを組む

`scripts/scalar/build_scalar_proposal.py` は標準構成を体現した実例
（架空の製造業シナリオ、アーキテクチャ + BOM 込み 23 スライド）である —
セクションごとの根拠は proposal-map.md §2 にある。実際の提案を作るには、
スクリプト冒頭の `PROPOSAL` dict
（customer, summary, challenges, mapping, alternatives, effects, cases,
journey, gantt, team, costs, risks, next）だけをヒアリング結果で書き換え、
以下を守る:

- 課題スライドは 3 項目以内、順序と文言はマッピング表と揃える
- 代替案比較表の比較軸は、顧客の実際の KBF（提案を何で評価するか）に書き換える
- 事例はマッピングしたカテゴリ（§3）から選び、出典はスピーカーノートに入れる
- 費用の数値は §5 のもののみを `source_note` つきで使う。それ以外は
  「個別お見積り」のままにする
- 密度の高いアーキテクチャ図（10 ノード以上、クラウド固有）→ `drawio-diagrams`
  スキルで作図し、組み込みのソリューション図の代わりに画像として挿入する

デザイン規約は scalar-product-slides と共通: アクションタイトル、アクセントバー
付きカードは角を丸めない、ピクトグラムは `illustrations` から。

## Phase 4: 生成と QA

```bash
cd /path/to/slide-forge
.venv/bin/python scripts/scalar/build_scalar_proposal.py --dry-run   # audits only, no API
.venv/bin/python scripts/scalar/build_scalar_proposal.py [--folder <URL>]
```

1. スクリプトは描画した全スライドで `audit_*` の "audit:" 行を出力する。
   **いずれかの検査が発火したら、データ・仕様を直して再ビルドする**
   （先に旧デッキを Drive から削除する。再ビルドすると URL が変わる —
   ユーザーに伝える）。
2. **ユーザーがビジュアル QA を選んだ場合（既定）**、`slide-qa` スキルを実行する:
   `scripts/fetch_thumbnails.py` で全ページを取得し、Read で検査し、終了後に
   `scripts/cleanup_qa.py` でローカルの QA ファイルを削除する。
   QA をスキップした場合は報告にその旨を明記し、後で `slide-qa` を提案する。
3. 提案固有のコンテンツ QA: ヒアリング根拠のない顧客固有の数値がないこと、
   出典注記のない事例・価格がないこと、課題の文言がスライド 3 / 7（整理と対応表）で
   一致していること、スコープ外の明記があること。
4. 最終報告には、デッキ / フォルダの URL と併せて BOM のリスト（環境ごとの
   クラウドサービス。Scalar 製品は数量と月額費用つき）を含める — ビルダーが
   `=== Bill of Materials (BOM) ===` として出力する。
5. `AskUserQuestion` で後続を提案する（interactive-intake.md §4）:
   確定 / 文言調整 / 事例差し替え / セクション追加・削除。

## ファイル構成

| パス | 役割 |
|------|------|
| `scripts/scalar/build_scalar_proposal.py` | 提案デッキビルダー（実例。顧客ごとに `PROPOSAL` を書き換える） |
| `references/scalar/proposal-map.md` | ヒアリング項目、提案構成とその根拠、課題→製品マップ、制約、価格 |
| `references/scalar/okf-bundle.ja.md` | OKF バンドルの所在と、製品事実・価格の引用ルール |
| `references/scalar/research-2026-08.md` | 会社・製品の事実、事例、スライドの落とし穴（scalar-product-slides と共有） |
| `examples/scalar-proposal-envs.drawio` / `.png` | 3 環境アーキテクチャ図の元データと書き出し（顧客ごとに書き換える） |
| `templates/scalar-2026.json` | Scalar 2026 テンプレート |
