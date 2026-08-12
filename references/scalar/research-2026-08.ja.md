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
