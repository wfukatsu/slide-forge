# クラウドアイコン（AWS / Google Cloud / Azure）

3 ベンダーの公式アイコン **1,757 種**を `assets/shared/cloud-icons/` に置いて使う。
SVG が正本で、使うときに必要な解像度へ焼く。

## 初回セットアップ（1 回だけ）

**アイコンはリポジトリに含めていない。** 各社の資産で再配布が許されていないため、
**利用者が自分の環境へ取り込む**。

```bash
cd ~/.claude/skills/google-slides
~/.claude/venvs/gslides/bin/python scripts/fetch-cloud-icons.py
```

1〜2 分・約 8.6MB。`google-slides-template` スキルにも同時に配置される。
取り込み済みかは `--verify` で確かめられる。未取り込みのまま `cloud_icons` を
使うと、この手順を案内するエラーで止まる。

**取り込んだ素材はコミットしない**（`.gitignore` 済み）。

```
assets/shared/cloud-icons/
  cloud-icons.json          マニフェスト（名前・別名・カテゴリ・種別・出典）
  aws/<category>/<slug>.svg     860 種
  gcp/<category>/<slug>.svg     251 種
  azure/<category>/<slug>.svg   646 種
cache/cloud-icons/          焼いた PNG（<vendor>-<slug>-<px>.png）
scripts/cloud_icons.py      検索 CLI と SlideBuilder 用ミックスイン
scripts/fetch-cloud-icons.py 素材の取り込み・更新
```

## ライセンス（先に読むこと）

3 ベンダーとも「**アーキテクチャ図・研修資料・ドキュメントでの利用**」だけを
許諾している。共通して守ること:

- **色を変えない。回さない。反転しない。縦横比を変えない。**
- **アイコンの近くに製品名を置く**（Azure は明示的に推奨、他社も同様の運用）
- 自社製品・自社サービスを表すのに他社のアイコンを使わない

`add_cloud_icon()` は**正方形固定・既定でラベルあり**で、色や回転の引数を
そもそも持たない。API の形で違反を防いでいるので、自前で `add_image` して
加工しないこと。

| ベンダー | 条件 |
|---|---|
| AWS | https://aws.amazon.com/trademark-guidelines/ |
| Azure | https://learn.microsoft.com/en-us/azure/architecture/icons/ |
| Google Cloud | https://cloud.google.com/icons |

## シェイプで組むピクトグラムとの使い分け

| | `pictogram-catalog.md` | 本ライブラリ |
|---|---|---|
| 対象 | 汎用の概念（サーバ・鍵・雲） | **実在するクラウドサービス** |
| 通信 | 不要 | 要る（Drive 経由） |
| 色 | テーマ色に合わせる | ベンダー指定の色（変更不可） |

構成図に「Amazon RDS」と書くなら本ライブラリ、「データベース」一般なら
シェイプか Scalar アイコン（`icon-library.md`）を使う。

## 名前を探す

```bash
P=~/.claude/venvs/gslides/bin/python
$P scripts/cloud_icons.py --search s3                 # 別名でも引ける
$P scripts/cloud_icons.py --search kubernetes         # 3 ベンダー横断
$P scripts/cloud_icons.py --list --vendor aws --category groups
$P scripts/cloud_icons.py --categories --vendor azure # カテゴリと件数
$P scripts/cloud_icons.py --sources                   # 取り込んだ版
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

## SlideBuilder に混ぜる

```python
import sys, os
sys.path.insert(0, os.path.join(SKILL_DIR, "scripts"))
from cloud_icons import CloudIconMixin, VENDOR_COLOR, VENDOR_LABEL

class SlideBuilder(CloudIconMixin):        # icons.IconLibraryMixin と併用可
    def __init__(self, drive_service):
        ...
        self.drive_service = drive_service   # 必須
        self._uploaded_assets = []           # 必須（cleanup 対象）
        self.cloud_label_color = C.textMuted
```

| メソッド | 何をするか |
|---|---|
| `add_cloud_icon(sid, name, x, y, size, label=…)` | 1 個置く。戻り値は下端 y |
| `add_cloud_icon_row(sid, x, y, w, items)` | 横一列 |
| `add_cloud_icon_flow(sid, x, y, w, items)` | 矢印でつなぐ |
| `add_cloud_icon_grid(sid, x, y, w, items, cols=4)` | 格子 |
| `add_cloud_zone(sid, x, y, w, h, vendor=…, title=…)` | 破線の囲いと見出し |

`items` は名前か `(名前, ラベル)`。ラベルを省くと**正式名称**が入る。

```python
sb.add_cloud_zone(sid, 0.45, 1.1, 9.1, 2.5, vendor="aws", title="AWS  ap-northeast-1")
sb.add_cloud_zone(sid, 0.75, 1.5, 8.5, 1.85, title="VPC  10.0.0.0/16")
sb.add_cloud_icon_row(sid, 1.0, 1.9, 8.0, [
    ("aws:elastic-load-balancing", "ALB"),
    ("aws:elastic-container-service", "ECS Fargate"),
    ("aws:rds", "RDS"), ("aws:simple-storage-service", "S3"),
], size=0.7)
```

動く実例は **`scripts/generate-cloud-architecture.py`**。

### 描く順番と塗りの注意

- **ゾーンは中身より先に描く。** 後から描くと矩形が中身を覆う。
- **枠だけの矩形は塗りを明示的に消す。** `fill` を渡さないだけだと Slides の
  既定色（薄いグレー）が残り、囲いのはずが板になる。

```python
oid = self.add_rect(sid, x, y, w, h, border_color=c)
self.requests.append({"updateShapeProperties": {
    "objectId": oid,
    "shapeProperties": {"shapeBackgroundFill": {"propertyState": "NOT_RENDERED"},
                        "outline": {"dashStyle": "DASH"}},
    "fields": "shapeBackgroundFill,outline.dashStyle"}})
```

`VENDOR_COLOR` / `VENDOR_LABEL` にベンダー色（AWS #FF9900 / GCP #4285F4 /
Azure #0078D4）と表示名が入っている。**枠線と見出しにだけ使う色**で、
アイコンには適用しない。

## 素材を更新する

```bash
python scripts/fetch-cloud-icons.py              # 3 ベンダーとも最新へ
python scripts/fetch-cloud-icons.py --vendor azure
python scripts/fetch-cloud-icons.py --dry-run    # URL の解決だけ確認
```

- 配布 URL は**ベンダーのページから解決する**（AWS は四半期ごと、Azure は
  V21 → V24 のように版が上がる）。ページの作りが変わって拾えないときは
  エラーで止まるので、`SOURCES` の正規表現を直す。
- google-slides と google-slides-template の**両スキルへ同時に配置**する。
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
