# クラウドアイコン（AWS / Google Cloud / Azure）

3 ベンダーの公式アイコン **1,757 種**を `assets/cloud-icons/` に置いて使う。
SVG が正本で、使うときに必要な解像度へ焼く。

## 初回セットアップ（1 回だけ）

**アイコンはリポジトリに含めていない。** 各社の資産で再配布が許されていないため、
**利用者が自分の環境へ取り込む**。

```bash
# slide-forge のリポジトリルートへ移動
.venv/bin/python scripts/fetch_cloud_icons.py
```

1〜2 分・約 8.6MB。取り込み済みかは `--verify` で確かめられる。
未取り込みのまま `cloud_icon` を使うと、この手順を案内するエラーで止まる。

**取り込んだ素材はコミットしない**（`.gitignore` 済み）。

```
assets/cloud-icons/
  cloud-icons.json          マニフェスト（名前・別名・カテゴリ・種別・出典）
  aws/<category>/<slug>.svg     860 種
  gcp/<category>/<slug>.svg     251 種
  azure/<category>/<slug>.svg   646 種
cache/cloud-icons/          焼いた PNG（<vendor>-<slug>-<px>.png）
scripts/cloud_icons.py      検索 CLI と Canvas 用ミックスイン
```

素材の取り込み・更新は google-slides スキルの `scripts/fetch_cloud_icons.py` が
**両スキルへまとめて**行う（版の管理を 1 箇所に集約するため）。

## ライセンス（先に読むこと）

3 ベンダーとも「**アーキテクチャ図・研修資料・ドキュメントでの利用**」だけを
許諾している。共通して守ること:

- **色を変えない。回さない。反転しない。縦横比を変えない。**
- **アイコンの近くに製品名を置く**（Azure は明示的に推奨、他社も同様の運用）
- 自社製品・自社サービスを表すのに他社のアイコンを使わない

`cloud_icon()` は**正方形固定・既定でラベルあり**で、色や回転の引数を
そもそも持たない。API の形で違反を防いでいるので、自前で `image()` して
加工しないこと。

| ベンダー | 条件 |
|---|---|
| AWS | https://aws.amazon.com/trademark-guidelines/ |
| Azure | https://learn.microsoft.com/en-us/azure/architecture/icons/ |
| Google Cloud | https://cloud.google.com/icons |

## 他のアイコンとの使い分け

| | `illustrations.icon()` | `icons.asset_icon()` | 本ライブラリ |
|---|---|---|---|
| 対象 | 汎用の概念（サーバ・鍵・雲） | Scalar の業務語彙 | **実在するクラウドサービス** |
| 通信 | 不要 | 要る | 要る |
| 色 | テーマ色 | テーマ色に染める | ベンダー指定の色（**変更不可**） |

構成図に「Amazon RDS」と書くなら本ライブラリ、「データベース」一般なら
`illustrations.icon("database")` を使う。同じスライドに混ぜてよい。

## 名前を探す

```bash
.venv/bin/python scripts/cloud_icons.py --search s3                 # 別名でも引ける
.venv/bin/python scripts/cloud_icons.py --search kubernetes         # 3 ベンダー横断
.venv/bin/python scripts/cloud_icons.py --list --vendor aws --category groups
.venv/bin/python scripts/cloud_icons.py --categories --vendor azure # カテゴリと件数
.venv/bin/python scripts/cloud_icons.py --sources                   # 取り込んだ版
```

指定できる名前は次のとおり。**曖昧・誤字は候補付きのエラーになる**ので、
生成前に気づける。

| 書き方 | 例 |
|---|---|
| `<vendor>:<slug>`（確実） | `aws:ec2` `gcp:bigquery` `azure:cosmos-db` |
| slug だけ | `ec2`（複数ベンダーに当たると落ちる） |
| 通称・別名 | `s3` `eks` `aks` `gke` `vnet` `cosmos` |
| 表示名 | `Amazon Simple Storage Service` `Cloud SQL` |

`kind` は 4 種。`--kind` で絞れる。

| kind | 中身 | 用途 |
|---|---|---|
| `service` | サービス本体（Amazon EC2 等） | 通常はこれ |
| `resource` | サービス内の細かい部品（EC2 インスタンス種別等） | 詳細な図 |
| `group` | 囲い（AWS Cloud / Region / VPC / サブネット） | ゾーンの見出し |
| `category` | カテゴリの代表アイコン | 章扉・分類の図 |

## 使う

`Canvas` のメソッドとして生えている。座標はインチ、**戻り値はラベルを含めた
下端 y**（`illustrations` / `icons` と同じ規約）。

| メソッド | 何をするか |
|---|---|
| `cloud_icon(name, x, y, size, label=…)` | 1 個置く |
| `cloud_icon_row(x, y, w, items)` | 横一列 |
| `cloud_icon_flow(x, y, w, items)` | 矢印でつなぐ |
| `cloud_icon_grid(x, y, w, items, cols=4)` | 格子 |
| `cloud_zone(x, y, w, h, vendor=…, title=…)` | 破線の囲いと見出し |

`items` は名前か `(名前, ラベル)`。ラベルを省くと**正式名称**が入る。

```python
d = Canvas(deck, ref["slideId"], template)
d.cloud_zone(0.45, 1.05, 9.1, 2.5, vendor="aws", title="AWS  ap-northeast-1")
d.cloud_zone(0.75, 1.5, 8.5, 1.85, title="VPC  10.0.0.0/16", color="#6B7280")
d.cloud_icon_row(1.0, 1.9, 8.0, [
    ("aws:elastic-load-balancing", "ALB"),
    ("aws:elastic-container-service", "ECS Fargate"),
    ("aws:rds", "RDS"), ("aws:simple-storage-service", "S3"),
], size=0.7)
```

デッキ仕様（JSON）からは `figures` の `type` で使う。**ゾーンは中身より先に
書くこと**（後ろに書くと矩形が中身を覆う）。

```json
"figures": [
  { "type": "cloud_zone", "x": 0.45, "y": 1.05, "w": 9.1, "h": 2.5,
    "vendor": "aws", "title": "AWS  ap-northeast-1" },
  { "type": "cloud_icon_row", "x": 1.0, "y": 1.9, "w": 8.0, "size": 0.7,
    "items": [["aws:rds", "RDS"], ["aws:simple-storage-service", "S3"]] }
]
```

動く実例:

- `examples/cloud-architecture.json` — ゾーン・マルチクラウド・データフロー（仕様 JSON）
- `examples/scalardb-architecture.py` — **層を矢印で結ぶ構成図**（Canvas を直に使う）
- `examples/scalardl-architecture.py` — 3 系統のアイコンを混ぜた構成図
  （クラウド公式 + Scalar ブランド + 図形のピクトグラム）

### 矢印で結ぶ構成図は Python で書く

`figures` には線を引く type が無い。アプリ層 → ScalarDB → データベース層のように
**層と層を結ぶ図は `Canvas` を直に使う**（`examples/scalardb-architecture.py`）。
クラウドアイコン・ピクトグラム・ブランドロゴ・コネクタを 1 枚に混ぜられる。

```python
d.cloud_zone(0.9, 3.55, 1.95, 1.5, vendor="aws")
d.cloud_icon("aws:dynamodb", 1.62, 3.89, 0.5, label="DynamoDB")
d.arrow(1.87, 3.23, 1.87, 3.51, color=d.P.muted, _anchored=True)
```

### 自社製品・OSS のアイコンは別で用意する

ベンダーのアイコン集には**そのベンダーのサービスしか無い**。次のものは別手段で描く。

| 描きたいもの | 手段 |
|---|---|
| ScalarDB / ScalarDL | `assets/scalar/product-logos/*.png` を `image()` で貼る |
| 証拠チェーン・改ざん検知・タイムスタンプ | `asset_icon("evidence-chain")` など（`references/icons.md`） |
| Scalar のロゴ | `assets/scalar/logos/*.png`、または `asset_icon("scalar-logo")` |
| 自前運用の PostgreSQL / MySQL / Cassandra | `illustrations.icon("database")` `icon("stack")`（商標の関係でベンダー集には無い） |
| マネージドな DB エンジン | 公式アイコンがある（`aws:aurora-postgresql-instance` / `azure:database-mysql-server` / `azure:managed-instance-apache-cassandra` など） |

`VENDOR_COLOR` / `VENDOR_LABEL` にベンダー色（AWS #FF9900 / GCP #4285F4 /
Azure #0078D4）と表示名が入っている。**枠線と見出しにだけ使う色**で、
アイコンには適用しない。

### `--dry-run` での扱い

`asset_icon` と同じく、**同じ大きさの矩形に置き換えて**座標だけ検査する。
アイコン名の誤りもここで分かるので、生成前に必ず通すこと。

```bash
.venv/bin/python scripts/build_deck.py --template templates/scalar-2026.json \
    --spec deck.json --dry-run
```

## 素材を更新する

取り込みスクリプトは共有エンジンの `scripts/fetch_cloud_icons.py` にある。

```bash
# slide-forge のリポジトリルートで実行
.venv/bin/python scripts/fetch_cloud_icons.py           # 全ベンダー
.venv/bin/python scripts/fetch_cloud_icons.py --vendor azure
.venv/bin/python scripts/fetch_cloud_icons.py --dry-run # URL 確認のみ
```

- 配布 URL は**ベンダーのページから解決する**（AWS は四半期ごと、Azure は
  V21 → V24 のように版が上がる）。ページの作りが変わって拾えないときは
  エラーで止まるので、`SOURCES` の正規表現を直す。
- 取り込み時に全 SVG を試し焼きし、焼けないものだけベンダー同梱の PNG を併置する。
- GCP は core（現行デザイン）> category > legacy（2021 年）の順で重ねている。
  legacy にしか無いサービスも多いので 3 本とも取り込む。

## 制約

- **通信が要る。** Slides は画像を URL からしか取り込めないため Drive を経由する。
  同じアイコンを何枚使ってもアップロードは 1 回（パス単位でキャッシュ）。
- 素材が無い名前は `CloudIconError`。**フォールバックで黙ってテキストバッジに
  落とさない**（旧実装はそれで「アイコンが出ない」事故になっていた）。
- Azure に数点だけ**正方形でないアイコン**がある。`render()` は長辺を指定画素数に
  合わせ、**縦横比は必ず保つ**（幅と高さを両方指定すると引き伸ばされ、
  「変形させない」条件に反するため）。正方形の枠に置くと上下か左右に余白が付く。
