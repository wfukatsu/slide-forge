# 製品調査サマリ(スライド用)

## ScalarDB (最新 3.18.0, 2026-05-01)
- Universal HTAP エンジン。アプリとDBの間のミドルウェア。異種複数DBを仮想統合し、DB横断ACIDトランザクション+リアルタイム分析
- コンポーネント:
  - Core (OSS, Apache 2.0): DB抽象化+アダプタ。独自プロトコル Consensus Commit
  - Cluster (商用): K8s上のクラスタリング。認証認可・暗号化・ABAC。CRUD/SQL/GraphQL/ベクトル検索
  - Analytics (商用): Spark ベース OLAP。ScalarDB管理外DBも横断分析可
- 対応DB: MySQL, PostgreSQL, Oracle, SQL Server, Db2, MariaDB, SQLite / Aurora, AlloyDB, Spanner(3.18), TiDB, YugabyteDB / DynamoDB, Cassandra, Cosmos DB / (プレビュー) S3, Blob, GCS
- インターフェース: Java API, SQL(JDBC/Spring Data), GraphQL, .NET SDK, gRPC
- エディション: Community(無料OSS) / Enterprise Standard / Enterprise Premium
  - Standard: クラスタリング、認証認可、非トランザクショナル操作
  - Premium: +SQL/GraphQL, 暗号化, ABAC, ベクトル検索(3.15), リモートレプリケーション(3.16)
  - Analytics は別途 (3.14+)
- 機能の流れ: 3.14 暗号化/Analytics → 3.15 ABAC/ベクトル検索 → 3.16 レプリケーション → 3.17 スキーマ変更ゼロ導入 → 3.18 ワンフェーズコミット最適化/Spanner対応
- 料金(マーケットプレイス, Pod=2vCPU/4GB): Standard $1.40/h(AWS), Premium $2.79/h(AWS)。BYOL相談

## ScalarDL (最新 3.13.0, 2026-03-25)
- ビザンチン障害検知ミドルウェア。改ざんを「防止」でなく「検知」— tamper-evident DB
- ブロックチェーン比較: 管理ドメイン最小2つで検知成立、数万TPSまでリニアスケール、運用負荷小
- ACID準拠、正確なファイナリティ、線形化可能一貫性。内部でScalarDB活用しDB非依存
- アーキテクチャ: Ledger(実行・コミット、追記型台帳) + Auditor(別管理ドメインで順序付け・検証、相互監視)。クライアントが両者の応答を突き合わせ改ざん検知
- Asset(資産データ) + Contract(秘密鍵で署名されたビジネスロジック)
- エディション: Community / Enterprise。料金: Ledger $1.40/h, Auditor $1.40/h (AWS)

## developers.scalar-labs.com
- ScalarDB / ScalarDL の2製品ポータル。実体は scalardb.scalar-labs.com / scalardl.scalar-labs.com

## 注意
- SQL IFの所属エディション表記に揺れ(features: Premium / pricing: Standard) → スライドでは「Enterprise で提供」程度にぼかすか Premium 準拠
- ScalarDB Cloud の存在は未確認 → 記載しない
