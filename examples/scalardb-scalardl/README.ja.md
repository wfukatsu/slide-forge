*[English](README.md)*

# 実例: ScalarDB / ScalarDL 製品機能解説

55 枚（うち図解 46 枚）のデッキ。1 機能 1 ページで公開ドキュメントの機能を網羅する構成の見本。

```bash
# 座標検査（API を呼ばない）
python ../../scripts/validate_layout.py deck.py

# 構成の一覧
python ../../scripts/render_deck.py deck.py --dry-run

# 生成
python ../../scripts/render_deck.py deck.py

# 自社マスターで生成する場合
SLIDE_FORGE_TEMPLATE=../../templates/my-brand.json \
    python ../../scripts/render_deck.py deck.py
```

## 構成

| セクション | 枚数 | 内容 |
|---|---|---|
| 1. 全体像 | 3 | 課題、3 層アーキテクチャ、エディション機能マトリクス |
| 2. Core | 12 | トランザクションプロトコル、分離レベル、リカバリ、最適化、データモデル、API |
| 3. Cluster | 14 | クラスタリング、各種インターフェース、認証認可、暗号化、レプリケーション、AI 連携 |
| 4. Analytics | 4 | アーキテクチャ、データカタログ、クエリ実行、認可 |
| 5. 運用 | 5 | データ移行、バックアップ、監視、K8s デプロイ、性能評価 |
| 6. ScalarDL | 6 | 改ざん検知、ハッシュチェーン、署名、相互検証、HashStore、TableStore |
| 7. まとめ | 2 | 使い分け、進め方 |

## 読みどころ

デッキモジュールの書き方の参考として、次のスライドを見るとよい。

| 関数 | 図のパターン |
|---|---|
| `s_problem` | Before/After の 2 パネル対比（`zone` ×2 ＋ 中央の太矢印 ＋ 丸バツ／丸チェック） |
| `s_arch3` | レイヤー図を手描きで構成（層ごとに濃度を変える） |
| `s_editions` | `grid` の `cell_colors` で ●／○／− を色分け |
| `s_cc_phases` | スイムレーン。レーンをまたぐ矢印を実座標で結ぶ |
| `s_recovery` | 条件分岐（`DIAMOND` ＋ Yes/No ＋ 2 つの帰結） |
| `s_optim` | Before/After の帯 ＋ `Canvas.cards` ＋ 回数の可視化 |
| `s_adapters` | 中核から 3 グループへ放射する構成図 |
| `s_exceptions` | 3 分類への分岐（分類ごとに色を割り当てる） |
| `s_oidc` | シーケンス（レーン ＋ 番号付き矢印）＋ 4 段の検証フロー |
| `s_replication` | 3 サイト構成図（`db` の円柱 ＋ サイト間のデータフロー） |
| `s_vector` | パイプラインの一部だけを自社領域として強調 |
| `s_backup` | タイムライン（マーカー ＋ 期間の帯 ＋ 復旧ポイント） |
| `s_catalog` | 階層ツリー（インデント ＋ かぎ線） |
| `s_asset` | ハッシュチェーン（改ざん箇所に丸バツ） |
| `s_next` | 2 列のステップ ＋ 列間の余白を通るエルボー接続 |

## 注意

- **性能数値は載せていない。** 公開ドキュメントに実測値が無いため、ベンチマークのページは
  「測定時に変えるべき変数」を図示し、自環境での実測を促す構成にしている。
  出典のない数値をグラフにしないこと。
- 内容は ScalarDB 3.18 / ScalarDL 3.13 時点の公開ドキュメントに基づく。
  機能の提供状況（GA / Private Preview）とエディションは版ごとに変わるため、
  流用する場合は対象バージョンで確認すること。
- 表紙は TITLE ＋ SUBTITLE だけで構成している。BODY プレースホルダを持つ表紙レイアウトは
  限られるため、可搬性のためにこうしている。
