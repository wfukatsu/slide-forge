*[English](research-2026-08.md)*

# Scalar 製品・会社 調査まとめ(2026-08-01 実施)

**鮮度に注意**: 本ファイルは 2026-08-01 時点の公開情報。バージョン・ニュース・事例は
陳腐化するため、**調査日から 3 か月以上経過していたら再調査してから使うこと**
(調査エージェントを scalar-labs.com / developers.scalar-labs.com へ並行で出す)。

## 会社(出典: scalar-labs.com/ja/company, STARTUP DB)

- 株式会社Scalar (Scalar, Inc.)。設立 2017年12月。東京(神楽坂)・札幌・サンフランシスコ(US Scalar Labs)
- 代表: 深津 航 (Founder/代表取締役CEO)、山田 浩之 (Founder/代表取締役CTO) ※boilerplate 公式スライド準拠
- 米国法人 CEO: Joe McCunney。従業員 約50名(2026年7月, STARTUP DB)
- ビジョン「データマネジメントの未来を創る」/ タグライン "Absolute data reliability"
- バリュー: Quality Obsessed / Customer Focus / Frontier Spirit
- 沿革: 2018.10 ScalarDB OSS 公開 → 2019 FIBC グランプリ → 2022.11 シリーズA 15億円 →
  2022-23 VLDB 2年連続採択 → 2023.12 執行役員体制強化
- **資本金は一次情報で未確認 → 記載しない**

## 直近トピックス(2025-2026)

- 2026.05 ScalarDB 3.18(ABAC 強化・OIDC・Spanner 対応・ワンフェーズコミット拡張)
- 2026.03 ScalarDL 3.13(ネームスペース管理・Java 21)※ニュースでは 4 月表記、リリースノートは 3/25
- 2026.01 Kong 社パートナーシップ / 2025.12 ScalarDB 3.17 / 2025.10 MCP Server・ゼンリン協業
- 2025.06 NSW メインフレームモダナイゼーション強化 / 2025.04 コーポレート PPA 実証

## ScalarDB(最新 3.18.0, 2026-05-01)

- Universal HTAP エンジン。Core(OSS/Apache 2.0)+ Cluster(商用/K8s)+ Analytics(商用/Spark)
- Consensus Commit による DB 非依存 ACID。対応: RDBMS(MySQL/PostgreSQL/Oracle/SQL Server/Db2 等)、
  NewSQL(Aurora/AlloyDB/Spanner/TiDB/YugabyteDB)、NoSQL(DynamoDB/Cassandra/Cosmos DB)
- 機能 15: ACID/マルチストレージ/2PC(マイクロサービス)/Cluster/SQL/GraphQL/認証認可/暗号化/
  ABAC/ベクトル検索/非トランザクショナル/リモートレプリケーション/Analytics/MCP Server/--import
- 料金例(Marketplace, Pod=2vCPU/4GB): Standard $1.40/h、Premium $2.79/h (AWS)

## ScalarDL(最新 3.13.0, 2026-03-25)

- ビザンチン故障検知ミドルウェア。2 管理ドメイン(Ledger+Auditor)・数万 TPS・ACID
- 機能 9: BFT検知/Ledger/Auditor/Contract/Function/TableStore(3.12)/HashStore(3.12)/
  ネームスペース(3.13)/Asset Proof
- エディション: Ledger=Community、Ledger(BYOL)/Auditor(BYOL)=Enterprise

## ユースケース・公表事例

- トヨタ自動車 PCE(ScalarDL/Azure, 知財証拠保全)※boilerplate に公式スライドあり
- 大手放送局 コンテンツデータ管理(ScalarDB)※boilerplate に公式スライドあり
- ENS 電力量30分値(ScalarDB): **法定帳票業務 1/5 — 唯一の公表定量効果**
- J-POWER 環境価値PF(ScalarDL, 2025.1〜) / NSW COBOL移行(ScalarDB) / LayerX Ai Workforce(ScalarDB, 2024.10)
- トヨタファイナンシャルサービス実証(2020.3) / NTT Digital・ドコモ Web3 提携(2023.7, 詳細不明)
- 常石造船 基幹システム刷新(ScalarDB + Kong Konnect, 2026.6.10 発表, 2026-08-02 調査):
  15年以上稼働のモノリスを AI 駆動開発で刷新。現状分析・再設計 2 日、MVP 実質 3 ヶ月、
  IT 担当 2 名が Scalar に常駐、ビジネスドメイン単位の 9 マイクロサービス構成。
  出典: prtimes.jp/main/html/rd/p/000000071.000037795.html /
  atmarkit.itmedia.co.jp/ait/articles/2606/29/news054.html /
  jp.konghq.com/news/kong-tsuneishi-ai-core-system-modernization
- パターン: DB=サイロ統合・マイクロサービス一貫性・レガシー移行・マルチクラウド・生成AI基盤・大量データ /
  DL=改ざん検知・監査証跡・トレーサビリティ・ブロックチェーン代替

## 既知の落とし穴(スライド化するとき)

1. **SQL インターフェースのエディション所属に表記揺れ**(features: Premium / pricing: Standard)。
   features 表準拠 + 要確認注記にする
2. **プレビュー明記**: ABAC(私的プレビュー・日本のみ)/ リモートレプリケーション(私的プレビュー)/
   ベクトル検索(公開プレビュー)
3. **「スキーマ変更ゼロ」という表現は docs に無い** → 正式には Schema Loader `--import`(既存テーブルのインポート)
4. **ScalarDL の「SQL 対応」の正式な姿は TableStore**(独立機能名ではない)
5. 導入事例の専用ページは無い(ニュース/ブログのみ)。定量効果は ENS 1/5 のみ
6. 認証認可も features 表(Standard 以上)と個別ページ(Premium タグ)で揺れ → features 表準拠 + 注記

## 追補調査(2026-08-24 実施) — 上記の 08-01 版から変わった点

- **ScalarDB 3.19 リリース(リリースノート 2026-08-02 / プレスリリース 2026-08-03〜04)**
  出典: https://prtimes.jp/main/html/rd/p/000000078.000037795.html /
  https://scalardb.scalar-labs.com/docs/latest/releases/release-notes/
  1. **新コンポーネント「ScalarDB Saga」を提供開始**(プレビューではない)。複数サービスを
     またぐ Saga / TCC のワークフローを実行・管理するエンジン兼オーケストレータ。
     実行状況・状態遷移を一元管理し、失敗時の再実行・補償処理を制御する。
     対応ユースケース: 外部 API/SaaS を含む業務処理・人の承認やバッチを含む長時間処理・
     非同期処理やリソース事前確保。**旧メモの「3.19.0-alpha.1 で未GA」は正式版で解消**
  2. 複数 ScalarDB Cluster をまたぐ 2PC を **1 フェーズで書ける新インターフェース**
     (Transaction Coordinator ノード / Cluster クライアント SDK の Global Transaction API)
  3. **ScalarDB Manager 刷新**(Cluster 稼働状況・設定・スキーマ・バックエンド DB を一画面で)
  4. **ScalarDB Analytics: WHERE 句のプッシュダウン対応**で転送量削減・クエリ高速化
  5. Enterprise 版に属性ベース認証・OpenTelemetry 対応を追加
  - ロードマップ: Quarkus など MicroProfile 準拠フレームワーク連携 /
    Analytics の **AI 活用データカタログ生成・管理機能**

- **ScalarDL 3.14 リリース(2026-08-06)** 出典: https://prtimes.jp/main/html/rd/p/000000079.000037795.html
  正しさの保証に不要と判断されたメタデータ(Ledger のトランザクションログ・Auditor の
  リクエストログ)を**自動パージ**でき、長期運用のストレージ使用量・保存コストを低減。
  既存環境のメタデータを消去するツールも提供

- **エディション名称の正**: 公式は **Community / Enterprise Standard / Enterprise Premium**。
  「ScalarDB Enterprise Edition」という単独の製品名は公式サイトに無く、商用エディションの
  総称として使うこと。公式製品ページ(scalar-labs.com/ja/products)の製品は
  **ScalarDB と ScalarDL の 2 つ**で、Saga / Analytics は ScalarDB のコンポーネント扱い

- **会社所在地の表記揺れ**: 3.19 プレスリリースの会社紹介は「東京とサンフランシスコ」。
  boilerplate 公式スライドは「東京、札幌、サンフランシスコ」。**公式スライド準拠でよい**

- **公表事例の追加確認**
  - トヨタ自動車 PCE: Box / SharePoint のファイル変更イベント検知 → ハッシュ計算 →
    ScalarDL に順序付きで記録 → 1 日 1 回タイムスタンプ付与。WHEN / SEQUENCE / WHAT を
    10 年超証明。PCE(Proof Chain of Evidence)として SaaS 外販。基盤は Microsoft Azure。
    最初のユースケースは発明の先使用権の証明
    出典: boilerplate 公式スライド / https://news.microsoft.com/ja-jp/2022/03/31/220331-proof-chain-of-evidence/
  - 大手放送局: オンプレのシングル DB の課題(機動的スキーマ変更不可・ピークアクセス・
    未 API 化)→ 公開領域をクラウドへ。IT 部門が番組情報を RDBMS で統括、制作局ごとの
    コンテンツ/メタデータは NoSQL。ScalarDB が両者をまたぐ整合性を担保、アクセスは API 化。
    **企業名は非公開。資料上は必ず「大手放送局様」と表記**
    出典: boilerplate 公式スライド(スライド 10 の全文を 2026-08-24 に取得)
  - 常石造船: プレスリリース本文は「**十数年**にわたり肥大化したモノリス」。
    「15 年以上」は二次情報。一次情報に合わせるなら**十数年**を使う

## 落とし穴の追加(7 以降)

7. **ScalarDB Saga を「未GA / プレビュー」と書かない**。3.19 で提供開始済み(2026-08)
8. **「ScalarDB Enterprise Edition」を単独の製品名として断定しない**。
   正式には Enterprise Standard / Enterprise Premium
9. **ベクトル検索は Enterprise Premium・プレビュー**。図に「ベクトルストア」を置くときは
   プレビューである旨を添える
10. **Analytics の AI データカタログは開発中**(3.19 の「今後の展望」)。提供済みと書かない
