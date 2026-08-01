# ScalarDL 機能調査サマリ(スライド用・2026-08-01)

最新: 3.13 (3.13.0 = 2026-03-25)。エディション: Ledger=Community、Ledger(BYOL)/Auditor(BYOL)=Enterprise。

1. ビザンチン故障検知: 改ざん含む任意の故障を「検知」。独立2ノード(Ledger+Auditor)で成立。Ordering→Commit→Validation の3段階。UC: GDPR/CCPA真正性証明、サプライチェーン監査証跡、監査ログ保全。VP: ブロックチェーン(最低4〜数千ノード)に対し2管理ドメイン+数万TPS+ACID/finality。
2. Ledger: アセット(asset_id+age)の履歴列を追記専用で管理、ハッシュチェーンで削除・更新を検知。get/put/scan。namespace対応。UC: 取引ログ・監査証跡、改ざん検知が必要な業務レコード。VP: 既存DBの上に被せるだけで追記型台帳。Community。
3. Auditor: 別管理ドメインの独立検証ノード。事前順序付け+コミット後検証。validateLedger で INCONSISTENT_STATES。UC: 第三者検証体制、規制産業監査、管理者不正の検知。VP: 2ノードでBFT検知、低コスト高性能。Enterprise のみ。
4. Contract: 基底クラス継承の Java プログラム。所有者秘密鍵で署名、所有者のみ実行可。決定性必須。ネスト実行はACID。getClientIdentityKey でアクセス制御。UC: 資産移転ロジック、署名で実行者制限、複合トランザクション。VP: データだけでなく処理の改ざんも検知。
5. Function: 可変データ(更新・削除可)を ScalarDB IF で操作、Contract と単一ACIDトランザクションで原子実行。UC: 決済(残高=Function、証跡=Contract)、台帳と業務DBの一貫性。VP: 二重管理の不整合リスクを排除。
6. TableStore (3.12): SQL IF のテーブル台帳。CREATE TABLE/INSERT/SELECT/UPDATE/JOIN、セカンダリインデックス、history() で全履歴、bootstrap で事前定義コントラクト自動登録=コントラクト開発不要。UC: DB感覚の改ざん検知アプリ、監査照会、SQL資産活用。VP: ローコードで改ざん検知テーブル。両エディション。
7. HashStore (3.12): デジタル証拠保全特化。オブジェクト真正性(put/get/compare-object-versions)+コレクション真正性(create/add/remove/get-collection-history)。ハッシュのみ台帳格納。UC: ファイル完全性検証、監査対象セットの不正除去検知、chain of custody。VP: ノーコード・大容量ファイル対応の証拠保全。両エディション。
8. ネームスペース管理 (3.13): アセット/クレデンシャル/コントラクトを namespace で分離。Cross-namespace access と Restricted access の2モデル。UC: SaaSテナント分離、複数システムの1 Ledger集約。VP: テナントごとに台帳を建てるコスト削減。両エディション。
9. Asset Proof: 実行時に Ledger が生成する暗号学的証拠(ID/age/nonce/ハッシュ/署名)をクライアント側に保全。UC: Auditor なし構成の事後改ざん対策、否認防止。VP: Ledger 単体でも改ざんハードルを大幅に上げる軽量保証。

補足: validateLedger API、認証はデジタル署名/HMAC、DB非依存(ScalarDB継承)、Java SDK 3種+gRPC。
注意: SQL サポートは独立機能でなく TableStore。Auditor=Enterprise は libraries-and-tools のコンポーネント表由来。
