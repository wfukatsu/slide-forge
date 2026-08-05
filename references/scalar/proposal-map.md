# Scalar 提案デッキ設計資料 — 課題→製品マッピングと提案の型（2026-08-05 調査）

**鮮度に注意**: 事例・価格・エディション構成は陳腐化する。
`research-2026-08.md` と同じ **3 ヶ月ルール**（調査日から 3 ヶ月以上経過していたら
再調査してから使う）を適用すること。提案の「型」（§2 の構成・作法）は
腐りにくいので再調査不要。

## 1. 提案前に確定させる項目（ヒアリング）

提案は顧客固有情報が無いと書けない。以下が埋まっているかを最初に確認し、
未取得の項目は **AskUserQuestion で確認するか、デッキ上は「本日確認したい」
という扱いにする**（推測で埋めない）。出典: Y's システム提案書ガイド +
BANT（§6）。

| 分類 | 確認する内容 | デッキでの使い先 |
|---|---|---|
| 課題・目的 | 現状課題は何か。**誰の**課題で、どの程度の強さ・金額規模か | 課題整理・期待効果 |
| 現状システム | システム構成、DB 製品、連携方式（バッチ/API/手作業）、**ScalarDB を迂回した直接書き込みが残るか**（§4 の制約に直結） | 現状・提案構成図 |
| 期待効果 | 期待する定量効果と、その算定材料が取れるか | 期待効果・PoC 成功基準 |
| 体制 | 顧客側の推進体制・運用体制、想定できる稼働 | 体制図 |
| 決裁構造 | 意思決定関与者（DMU）、稟議プロセス、決裁者が誰か | サマリの粒度・比較軸 |
| 予算 | 予算枠の有無・規模感、予算確保のタイミング（年度） | 費用・スケジュール |
| スケジュール | 導入希望時期と、検討開始〜決裁までの商談ステップ | ガント・次のステップ |
| エンプラ特有 | セキュリティ/コンプライアンス要件、非機能要件（可用性・性能）、PoC 実施意向と評価基準 | リスク・PoC 提案 |

## 2. 提案書に入れる項目（構成と作法）

構成の土台は `references/deck-outlines.md`「課題解決型の提案」。それを
B2B 提案書のベストプラクティス（才流・HubSpot・Y's、§6）で補強した標準構成が
`scripts/scalar/build_scalar_proposal.py`（worked example, 20 枚）。

| # | セクション | worked example のスライド | 根拠 |
|---|---|---|---|
| 0 | 表紙 | COVER | — |
| 1 | エグゼクティブサマリ | `exec_summary`（状況→課題→答え+論点） | 決裁者は冒頭しか読まない。結論先出し |
| 2 | 背景と現状 | `icon_flow` + `so_what` | 課題認識の合意形成を解決策より先に |
| 3 | 課題の整理（3 点） | `cards` | 課題は 3 点まで |
| 4 | 課題の構造 | `iceberg`（表出問題/根本原因） | 対症療法との差別化の土台 |
| 5 | 目指す姿とスコープ | `before_after` + スコープ外の明記 | 含まれない業務の明示で期待値制御 |
| 6 | 解決策（製品提案） | 統合レイヤ図（icon_row+帯+矢印） | 文章より構成図。密な図は drawio-diagrams |
| 7 | 課題と打ち手の対応 | `table`（課題→機能→実現状態） | 課題スライドと同順・同文言で対応 |
| 8 | 打ち手の比較 | `table`（代替案との比較） | 「これでないといけない理由」が稟議に必須 |
| 9 | 期待効果 | `before_after`（業務の変化）+ 定量方針 | 機能でなく業務の変化を語る。根拠なき定量は書かない |
| 10 | 導入事例 | `cards` + `source_note` | 興味喚起後に信頼補強（会社紹介は前に出さない） |
| 11 | 導入アプローチ | `journey` + PoC 成功基準 | スモールスタート・Go/No-Go の明示 |
| 12 | スケジュール | `gantt` | 実行可能性の証明 |
| 13 | 体制 | `orgchart` + 役割表（顧客側の負荷明記） | 「工数がかからない」ことを示す |
| 14 | 概算費用 | `table` + `source_note` | 価格は解決策・効果の**後**に置く |
| 15 | リスクと対策 | `table`（懸念→対策） | 決裁者の不安の先回り |
| 16 | 次のステップ | `flow` + `so_what` | 次のアクション明示。送りっぱなしにしない |
| 17 | クロージング | CLOSING | — |

作法（デッキ全体）:

- **課題は顧客の言葉で書く**。ヒアリング由来であることを明記し、「認識が違えば
  今日直したい」という一文を添える（課題合意そのものが商談の目的）
- **効果の定量値は算定根拠を添えられるものだけ**。無ければ定性で書き、
  「PoC で実測して稟議材料にする」という筋書きに乗せる
- **公表事例の数値だけを使う**（ENS 法定帳票 約1/5、常石造船 MVP 実質 3 ヶ月・
  導入工数 70% 削減など）。出典は `source_note` と話者ノートに残す
- 中長期ロードマップ・詳細機能説明は Appendix へ（本編を薄く保つ）

## 3. 課題カテゴリ → 製品マッピング

顧客の課題を聞いたらまずここに当てる。当てはまらない・§4 に該当する場合は
無理に Scalar 製品に着地させない（正直に伝えるのも提案の質）。

| カテゴリ | 顧客の悩みの言い回し（例） | 製品・機能 | 事例（公表） |
|---|---|---|---|
| A. 複数 DB のサイロ化・分散データ統合 | 「部門ごとにアプリと DB がバラバラ」「サイロ化で複雑になったシステムをシンプルにしたい」 | ScalarDB（統一 API で異種 DB を仮想統合、マイグレーション不要）。SQL/GraphQL は Premium。横断分析は Analytics | 大手放送局（コンテンツデータ管理）、LayerX Ai Workforce（2024.10） |
| B. マイクロサービス間のデータ一貫性 | 「サービス分割したら DB 間の整合性が取れない」 | ScalarDB 分散 ACID（厳格な直列化可能性）、2 フェーズコミット I/F | 常石造船（分割サービス間の整合性担保） |
| C. レガシー/メインフレーム移行 | 「モノリスがブラックボックス化して十数年刷新できない」「COBOL 資産の移行はデータ連携の信頼性が壁」 | ScalarDB の DB 非依存 I/F + `--import`（既存テーブル取込）。NSW 共同の Copy Book→JSON 変換 | 常石造船（MVP 実質 3 ヶ月・工数 70% 削減, MONOist）、NSW モダナイゼーション |
| D. 生成 AI / RAG の社内データ活用 | 「散在データを AI に使いたいが接続開発と一貫性が課題」 | ScalarDB RAG サポート、ベクトル検索（Premium・プレビュー） | LayerX Ai Workforce、常石造船（AI エージェントのデータアクセス基盤） |
| E. 改ざん検知・証拠保全・監査証跡 | 「データが改ざんされていないことを 10 年以上証明し続けたい」「規制対応の監査証跡が要る」 | ScalarDL（BFT 検知・追記型台帳・Ledger+Auditor・数万 TPS） | トヨタ PCE（知財証拠保全, Azure）、トヨタファイナンシャルサービス実証 |
| F. 環境価値・トレーサビリティ（GX） | 「再エネの環境価値を第三者検証可能な形で記録・追跡したい」 | ScalarDL（発電・需要データの保全と紐付け） | J-POWER 環境価値 PF（2025.1〜）、コーポレート PPA 実証（2026.4） |
| G. 需要変動に耐える基幹系 | 「利用者数の増減が読めず、柔軟に拡張・縮小したい」 | Scalar DLT（ScalarDB+ScalarDL、最小構成から拡張） | ENS 新電力共通受付（さるぼぼコインプラン）、ENS 電力量 30 分値（法定帳票 約1/5） |
| H. マルチクラウドのデータ管理 | 「クラウド間・リージョン間でデータを管理したい」 | ScalarDB（クラウド非依存）、リモートレプリケーション（プレビュー） | 公表事例なし（事例を求められたら正直に伝える） |

## 4. 提案してはいけない・注意すべきケース（docs の制約）

比較表・リスク対策・話者ノートに反映する。隠すと PoC で露見して信頼を失う。

ScalarDB:

- **アプリが ScalarDB を迂回して DB に直接書く構成は不可**（分離レベルの保証が
  崩れる）。既存系からの直接書き込みが残る移行期の設計は要検討事項として明示する
- 抽象化レイヤーゆえ **DB 固有機能（PL/SQL 等）・全データ型は使えない**
- Core は OLTP（多数の小さな読み書き）想定。**分析クエリは ScalarDB Analytics 経由**
- 下位 DB に管理者級権限が必要（MySQL: CREATE/DROP/ALTER 等、Oracle: ANY 系）
- 環境要件: JDK LTS（8/11/17/21）、Cluster は Kubernetes 1.32–1.35。
  Db2 for z/OS 非対応、Spanner は PostgreSQL 方言のみ
- 認証認可は Enterprise、暗号化・ABAC・SQL/GraphQL・ベクトル検索は Premium
  （Community に無い機能を Community 前提の提案に書かない）

ScalarDL:

- 改ざんの**検知**であり**防止**ではない（誇張しない）
- 検知の完全性は Ledger + Auditor の **2 独立管理ドメイン運用が前提**
- 台帳外で行われたデータ操作は対象外（アプリをコントラクト経由に載せ替える）
- 内部で ScalarDB を使用（DB 対応・制約は ScalarDB に従う）

## 5. 価格・エディション（2026-08-05 時点）

| 製品 | 課金 | 備考 |
|---|---|---|
| ScalarDB Community | 無料（Apache 2.0） | 商用機能なし |
| ScalarDB Enterprise Standard | AWS $1.40/h・GCP $1.50/h、BYOL ¥100,000/月（税抜） | クラスタリング・認証認可・非トランザクショナル |
| ScalarDB Enterprise Premium | AWS $2.79/h・GCP $2.89/h、BYOL ¥200,000/月（税抜） | + SQL/GraphQL・暗号化・ABAC/ベクトル検索/レプリケーション（プレビュー） |
| ScalarDL Ledger / Auditor | 各 $1.40/h（AWS。Auditor は Ledger と同時購入必須）、BYOL は個別問い合わせ | — |

- 時間課金の単位は Marketplace ページから確認できず（`research-2026-08.md` は
  Pod=2vCPU/4GB と記録。デッキには「×Pod 数〜」程度に留め、確定額を書かない）
- ScalarDB Analytics の価格は公表確認できず（不明）。Azure Marketplace の
  従量課金提供は不明（BYOL コンテナ記載と非提供記載が混在）
- 概算費用スライドには必ず `source_note`（AWS Marketplace 公表値+時点）を置く

## 6. 出典

提案の型: 才流 提案書テンプレート https://sairu.co.jp/method/3543/ /
才流 稟議書 https://sairu.co.jp/method/18438/ / 才流 営業資料改善
https://sairu.co.jp/method/5296/ / HubSpot https://blog.hubspot.jp/sales/proposal-formula /
Y's https://ysinc.co.jp/blog/system-proposal-guide/ / BANT
https://cyber-synapse.com/business-knowledge/sales_strategy/how-to-use-bant-for-sales-interview/

製品・制約: https://scalardb.scalar-labs.com/docs/latest/overview/ /
…/design/ / …/requirements/ / https://scalardl.scalar-labs.com/docs/latest/overview/ /
…/requirements/ / https://www.scalar-labs.com/ja/scalardb / …/ja/scalardl / …/ja/pricing

事例: 常石造船 https://prtimes.jp/main/html/rd/p/000000071.000037795.html +
https://monoist.itmedia.co.jp/mn/articles/2606/25/news030.html（工数 70% 削減） /
トヨタ PCE https://prtimes.jp/main/html/rd/p/000000031.000037795.html /
J-POWER https://www.jpower.co.jp/news_release/2025/01/news250106.html +
https://www.jpower.co.jp/news/2026/04/news260417_1.html /
LayerX https://prtimes.jp/main/html/rd/p/000000376.000036528.html /
ENS https://prtimes.jp/main/html/rd/p/000000006.000037795.html /
NSW https://www.nsw.co.jp/topics/news_detail.html?eid=763
