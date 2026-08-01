# アーキテクチャ図ガイド

クラウドアイコン（AWS/GCP/Azure）とシェイプを使ったシステム構成図の作成ガイド。

### 規約

本ドキュメントで使用する識別子:

- **`C`** -- `templates/<theme>/theme.json` の `colors` セクションから展開した色定数クラス（SKILL.md Phase 1 参照）
- **`L`** -- `templates/<theme>/theme.json` の `layouts` セクションから展開したレイアウト定数クラス
- **`sb`** / **`self`** -- `SlideBuilder` インスタンス

---

## 1. 概要

### 1.1 目的

Google Slides API を使い、ScalarDB / ScalarDL のシステム構成図を作成する。クラウドベンダーの公式アイコン、ピクトグラム、シェイプ、コネクタを組み合わせて、顧客に分かりやすい構成図を構築する。

構成図は B2B 営業資料やテクニカルドキュメントで頻繁に必要とされる。本ガイドでは、以下を標準化する:

- コンポーネントの色コーディング
- ゾーン（境界）の描画パターン
- コネクタの種類と使い分け
- レイヤー構成のテンプレート
- クラウドアイコンの配置方法

### 1.2 構成要素

| 要素 | 実装方法 | 用途 |
|------|---------|------|
| クラウドアイコン | `add_image_from_asset()` | AWS/GCP/Azure サービス |
| シェイプ | `add_shape()` | コンテナ、ゾーン、プロセス |
| ピクトグラム | シェイプ組み合わせ | DB、サーバー、ユーザー等 |
| コネクタ | `add_connector()` / `add_connected_connector()` | データフロー、通信 |
| テキストラベル | `add_text()` | コンポーネント名、説明 |
| ゾーン（境界） | `add_shape()` + 半透明 | リージョン、VPC、サブネット |

### 1.3 対象スライドタイプ

`architecture` / `deployment_topology` / `integration_overview` / `data_flow` 等のスライドタイプで構成図を描画する。CONTENT マスター（フッター付き）または BLANK マスター（全面使用）を選択する。

| マスター | 描画可能領域 | 用途 |
|---------|------------|------|
| CONTENT | 0.5" -- 9.5" x 0.8" -- 5.0" | フッター・タイトル付き構成図 |
| BLANK | 0.3" -- 9.7" x 0.3" -- 5.3" | 全面構成図（タイトルなし） |

---

## 2. 色コーディング規則

### 2.1 コンポーネント色

`design-principles.md` のセマンティックカラーに準拠した色分け:

| カテゴリ | 色 | Hex | テーマカラー | 用途 |
|---------|-----|-----|-----------|------|
| **自社製品** | Blue | `#2673BB` | `C.primary` | ScalarDB, ScalarDL, Scalar Envoy |
| **自社製品（濃）** | Dark Blue | `#004266` | `C.primaryDark` | 製品のヘッダー、強調 |
| **外部/既存** | Gray | `#666666` | `C.textMuted` | PostgreSQL, MySQL, Cassandra, 既存システム |
| **ユーザー/クライアント** | Orange | `#E8963A` | `C.warning` | ブラウザ、モバイルアプリ、API クライアント |
| **正常フロー** | Green | `#63C045` | `C.success` | データフロー（正常パス） |
| **エラーパス** | Red | `#F4CCCC` 枠 / `#DC2626` 線 | `C.alertRed` 枠 / `C.error` 線 | 障害パス、エラー処理 |
| **注意/新機能** | Gold | `#6B5000` | `C.cautionDark` | 注目ポイント、新機能 |
| **クラウドサービス** | Light Blue | `#0985FC` | `C.accent` | マネージドサービス |

> **注意**: `#BE9000`（`C.cautionYellow`）は白背景でコントラスト比 2.8:1 のため、テキストには使用禁止。ラベルには `C.cautionDark`（`#6B5000`、7:1+）を使う。

### 2.2 色定数の Python 定義

```python
# アーキテクチャ図用の追加色定数
ARCH_COLORS = {
    "scalar_product": hex_to_rgb("#2673BB"),   # C.primary
    "scalar_dark":    hex_to_rgb("#004266"),   # C.primaryDark
    "external":       hex_to_rgb("#666666"),   # C.textMuted
    "client":         hex_to_rgb("#E8963A"),   # C.warning
    "flow_normal":    hex_to_rgb("#63C045"),   # C.success
    "flow_error":     hex_to_rgb("#DC2626"),   # C.error
    "cloud_service":  hex_to_rgb("#0985FC"),   # C.accent
    "caution":        hex_to_rgb("#6B5000"),   # C.cautionDark（テキスト用）
    "zone_border":    hex_to_rgb("#6B7280"),   # C.border
}
```

### 2.3 ゾーン（境界）の色

| ゾーン | 背景色 | 境界線 | 線種 | alpha |
|--------|-------|--------|------|-------|
| クラウドリージョン | `C.backgroundAlt` | `C.border` | `SOLID` | 0.05 |
| VPC / サブネット | `C.surfaceLight` | `C.primary` | `SOLID` | 0.10 |
| オプション境界 | transparent | `C.textMuted` | `DASH` | -- |
| セキュリティゾーン | `C.calloutBg` | `#E74C3C` | `DASH_DOT` | 0.08 |
| 外部ネットワーク | transparent | `C.textMuted` | `DOT` | -- |
| オンプレミス | `C.backgroundAlt` | `C.textMuted` | `SOLID` | 0.06 |
| Kubernetes クラスタ | `C.surfaceLight` | `C.accent` | `SOLID` | 0.08 |

### 2.4 コネクタの色と線種

| フロー種類 | 色 | 線種 | 矢印 | 太さ | 用途 |
|-----------|-----|------|------|------|------|
| データフロー（正常） | `C.success` | `SOLID` | `FILL_ARROW` | 1.5pt | メインのデータパス |
| データフロー（読取） | `C.primary` | `SOLID` | `FILL_ARROW` | 1.0pt | 読み取りクエリ |
| データフロー（書込） | `C.accent` | `SOLID` | `FILL_ARROW` | 1.0pt | 書き込みクエリ |
| エラー/フォールバック | `#E74C3C` | `DASH` | `FILL_ARROW` | 1.0pt | 障害時フロー |
| オプショナル接続 | `C.textMuted` | `DOT` | `STEALTH_ARROW` | 0.75pt | 省略可能な接続 |
| 双方向通信 | `C.primary` | `SOLID` | 両端 `FILL_ARROW` | 1.0pt | gRPC 等の双方向 |
| レプリケーション | `C.success` | `LONG_DASH` | `FILL_ARROW` | 1.0pt | DB レプリカ同期 |
| 管理/監視 | `C.textMuted` | `DASH_DOT` | `STEALTH_ARROW` | 0.75pt | メトリクス、ログ |

---

## 3. レイヤー構成パターン

### 3.1 水平レイヤー（上 → 下）

ScalarDB アーキテクチャで最も一般的なパターン。クライアント → ミドルウェア → ストレージの 3 層構成。

```
 ┌─────────────────────────────────────────┐
 │  Client Layer (Orange)     Y: 1.0"-1.8" │
 │  ┌─────┐  ┌─────┐  ┌─────┐            │
 │  │App 1│  │App 2│  │App 3│            │
 │  └──┬──┘  └──┬──┘  └──┬──┘            │
 └─────┼────────┼────────┼────────────────┘
       ▼        ▼        ▼
 ┌─────────────────────────────────────────┐
 │  Scalar Layer (Blue)      Y: 2.3"-3.3" │
 │  ┌─────────────────────────────────┐    │
 │  │         ScalarDB               │    │
 │  └────────────┬────────────────────┘    │
 └───────────────┼────────────────────────┘
                 ▼
 ┌─────────────────────────────────────────┐
 │  Storage Layer (Gray)     Y: 3.8"-4.6" │
 │  ┌─────┐  ┌─────┐  ┌─────┐            │
 │  │MySQL│  │ PG  │  │Cass.│            │
 │  └─────┘  └─────┘  └─────┘            │
 └─────────────────────────────────────────┘
```

```python
def compose_horizontal_layers(self, slide_id, layers):
    """水平レイヤー構成図を描画する。

    layers: [
        {
            "name": "Client Layer",
            "color": ARCH_COLORS["client"],
            "y": 1.0, "h": 0.8,
            "components": [
                {"name": "App 1", "shape": "ROUND_RECTANGLE", "x": 1.5, "w": 1.2, "h": 0.5},
                {"name": "App 2", "shape": "ROUND_RECTANGLE", "x": 4.0, "w": 1.2, "h": 0.5},
            ]
        },
        ...
    ]
    """
    for layer in layers:
        # レイヤー境界（ゾーン）
        zone_id = self.add_zone(slide_id, layer["name"],
                                0.5, layer["y"], 9.0, layer["h"],
                                border_color=layer["color"])
        # コンポーネント
        comp_y = layer["y"] + (layer["h"] - layer["components"][0].get("h", 0.5)) / 2
        for comp in layer["components"]:
            cw = comp.get("w", 1.2)
            ch = comp.get("h", 0.5)
            shape = comp.get("shape", "ROUND_RECTANGLE")
            sid = self.add_shape(slide_id, shape,
                                 comp["x"], comp_y, cw, ch,
                                 fill=layer["color"])
            self.add_text(slide_id, comp["name"],
                          comp["x"], comp_y, cw, ch,
                          font_size=10, bold=True,
                          color={"red": 1, "green": 1, "blue": 1},
                          alignment="CENTER", valign="MIDDLE")
```

### 3.2 左右分割（入力 → 処理 → 出力）

データパイプラインや ETL フローに適したパターン。

```
 ┌─────┐    ┌──────────┐    ┌─────┐
 │Input│───▶│Processing │───▶│Output│
 │(Orange)  │(Blue)     │    │(Green)
 └─────┘    └──────────┘    └─────┘
```

```python
def compose_lr_flow(self, slide_id, stages):
    """左→右フロー構成図を描画する。

    stages: [
        {"name": "データ取込", "color": ARCH_COLORS["client"], "w": 1.5},
        {"name": "ScalarDB\n変換処理", "color": ARCH_COLORS["scalar_product"], "w": 2.5},
        {"name": "分析基盤", "color": ARCH_COLORS["flow_normal"], "w": 1.5},
    ]
    """
    total_w = sum(s["w"] for s in stages)
    gap = 0.6
    total_gap = gap * (len(stages) - 1)
    start_x = (10.0 - total_w - total_gap) / 2
    cy = 2.8  # 垂直中央
    box_h = 1.0
    prev_x_end = None

    for stage in stages:
        sx = start_x
        # コネクタ（前のステージとの間）
        if prev_x_end is not None:
            self.add_connector(slide_id,
                               prev_x_end, cy + box_h / 2,
                               sx, cy + box_h / 2,
                               color=C.textMuted, weight=1.5,
                               end_arrow="FILL_ARROW")
        self.add_rounded_rect(slide_id, sx, cy, stage["w"], box_h,
                              fill=stage["color"])
        self.add_text(slide_id, stage["name"],
                      sx, cy, stage["w"], box_h,
                      font_size=11, bold=True,
                      color={"red": 1, "green": 1, "blue": 1},
                      alignment="CENTER", valign="MIDDLE")
        prev_x_end = sx + stage["w"]
        start_x = prev_x_end + gap
```

### 3.3 ハブ & スポーク

ScalarDB を中心に据え、周囲のサービスと接続するパターン。

```
         ┌──────┐
         │ App  │
         └──┬───┘
            │
 ┌──────┐   ▼   ┌──────┐
 │Cache │◄─[DB]─▶│Queue │
 └──────┘   ▲   └──────┘
            │
         ┌──┴───┐
         │Store │
         └──────┘
```

```python
def compose_hub_spoke(self, slide_id, hub, spokes):
    """ハブ&スポーク構成図を描画する。

    hub: {"name": "ScalarDB", "x": 4.5, "y": 2.5, "w": 1.5, "h": 0.8}
    spokes: [
        {"name": "App Server", "direction": "top", "color": ARCH_COLORS["client"]},
        {"name": "PostgreSQL", "direction": "bottom", "color": ARCH_COLORS["external"]},
        {"name": "Redis Cache", "direction": "left", "color": ARCH_COLORS["external"]},
        {"name": "Kafka", "direction": "right", "color": ARCH_COLORS["cloud_service"]},
    ]
    """
    import math
    hx, hy, hw, hh = hub["x"], hub["y"], hub["w"], hub["h"]
    hcx, hcy = hx + hw / 2, hy + hh / 2

    # ハブ描画
    self.add_rounded_rect(slide_id, hx, hy, hw, hh,
                          fill=ARCH_COLORS["scalar_product"])
    self.add_text(slide_id, hub["name"],
                  hx, hy, hw, hh,
                  font_size=12, bold=True,
                  color={"red": 1, "green": 1, "blue": 1},
                  alignment="CENTER", valign="MIDDLE")

    # スポーク描画
    direction_offsets = {
        "top":    (0, -1.5),
        "bottom": (0,  1.5),
        "left":  (-2.5, 0),
        "right": ( 2.5, 0),
    }
    spoke_w, spoke_h = 1.2, 0.5
    for spoke in spokes:
        dx, dy = direction_offsets[spoke["direction"]]
        sx = hcx + dx - spoke_w / 2
        sy = hcy + dy - spoke_h / 2
        color = spoke.get("color", ARCH_COLORS["external"])
        self.add_rounded_rect(slide_id, sx, sy, spoke_w, spoke_h, fill=color)
        self.add_text(slide_id, spoke["name"],
                      sx, sy, spoke_w, spoke_h,
                      font_size=10, bold=True,
                      color={"red": 1, "green": 1, "blue": 1},
                      alignment="CENTER", valign="MIDDLE")
        # コネクタ（スポーク → ハブ）
        self.add_connector(slide_id,
                           sx + spoke_w / 2, sy + spoke_h / 2,
                           hcx, hcy,
                           color=ARCH_COLORS["flow_normal"], weight=1.0,
                           end_arrow="FILL_ARROW")
```

### 3.4 マルチクラウド分割

左右にクラウドリージョンゾーンを配置し、中央で ScalarDB が接続するパターン。

```
 ┌── AWS Region ──────┐    ┌── GCP Region ─────┐
 │  ┌─────┐           │    │          ┌──────┐ │
 │  │ RDS │◄──┐       │    │    ┌────▶│Spanner│ │
 │  └─────┘   │       │    │    │     └──────┘ │
 │          ┌─┴──────┐│    │┌───┴────┐         │
 │          │ScalarDB││◄──▶││ScalarDB│         │
 │          └────────┘│    │└────────┘         │
 └────────────────────┘    └───────────────────┘
```

---

## 4. クラウドアイコンの使用

**この節の実装は `references/cloud-icons.md` に移した。** 素材は
`assets/shared/cloud-icons/`（AWS 860 / GCP 251 / Azure 646 = 1,757 種の SVG）で、
`scripts/cloud_icons.py` の `CloudIconMixin` を SlideBuilder に混ぜて使う。

### 4.1 最低限これだけ

```python
from cloud_icons import CloudIconMixin, VENDOR_COLOR, VENDOR_LABEL

class SlideBuilder(CloudIconMixin):
    ...                                     # drive_service と _uploaded_assets が要る

sb.add_cloud_zone(sid, 0.45, 1.1, 9.1, 2.5, vendor="aws", title="AWS  ap-northeast-1")
sb.add_cloud_zone(sid, 0.75, 1.5, 8.5, 1.85, title="VPC  10.0.0.0/16")
sb.add_cloud_icon_row(sid, 1.0, 1.9, 8.0, [
    ("aws:elastic-load-balancing", "ALB"),
    ("aws:elastic-container-service", "ECS Fargate"),
    ("aws:rds", "RDS"),
    ("aws:simple-storage-service", "S3"),
], size=0.7)
```

| メソッド | 何をするか |
|---|---|
| `add_cloud_icon(sid, name, x, y, size, label=…)` | 1 個置く。戻り値は下端 y |
| `add_cloud_icon_row / _flow / _grid` | 横一列 / 矢印つなぎ / 格子 |
| `add_cloud_zone(sid, x, y, w, h, vendor=…, title=…)` | 破線の囲いと見出し |

動く実例: `scripts/generate-cloud-architecture.py`

### 4.2 名前の指定と探し方

**アイコン名は推測しないこと。** ファイル名は
`Arch_Amazon-EC2_64.svg` や `00606-icon-service-Azure-Synapse-Analytics.svg` の
ような形で、勘で書くと必ず外れる。マニフェストから引く。

```bash
~/.claude/venvs/gslides/bin/python scripts/cloud_icons.py --search s3
~/.claude/venvs/gslides/bin/python scripts/cloud_icons.py --list --vendor aws --category compute
```

`aws:ec2`（vendor 付き slug）/ `s3`（別名）/ `Cloud SQL`（表示名）のどれでも
引ける。**見つからない名前はエラーになる**（黙ってテキストバッジに落ちない）。

### 4.3 ゾーン（囲い）

- ベンダー色は枠線と見出しにだけ使う（`VENDOR_COLOR`）。アイコンには適用しない
- **ゾーンは中身より先に描く。** 後から描くと矩形が中身を覆う
- **枠だけの矩形は塗りを明示的に消す**（`shapeBackgroundFill: NOT_RENDERED`）。
  渡さないだけだと Slides の既定色が残り、囲いのはずが板になる
- 囲いそのもののアイコン（AWS Cloud / Region / VPC / サブネット）は
  `--kind group` で引ける。見出しの左に添えると分かりやすい

### 4.4 ライセンス（重要）

3 ベンダーとも「アーキテクチャ図・研修資料・ドキュメントでの利用」のみ許諾。
**色の変更・回転・反転・変形は禁止**で、アイコンの近くに製品名を置くことが
求められる。`add_cloud_icon` は正方形固定・既定でラベルありにしてあり、色や
回転の引数を持たない。**自前で `add_image` して加工しないこと。**

詳細と出典は `references/cloud-icons.md`。

## 5. コンポーネントシェイプ

### 5.1 標準コンポーネント

構成図で使用する標準的なコンポーネントシェイプ。

| コンポーネント | shapeType | サイズ目安 | 色 |
|-------------|-----------|----------|-----|
| アプリケーション | `ROUND_RECTANGLE` | 1.2" x 0.5" | コンテキスト依存 |
| データベース | `CAN` | 0.6" x 0.7" | gray (外部) / blue (自社) |
| ロードバランサ | `HEXAGON` | 0.5" x 0.5" | cloud_service |
| サーバー | `RECTANGLE` | 1.0" x 0.5" | コンテキスト依存 |
| キュー/メッセージ | `CHEVRON` | 0.8" x 0.4" | external |
| 判断/ルーティング | `DIAMOND` | 0.6" x 0.6" | コンテキスト依存 |
| ユーザー | `ELLIPSE` | 0.5" x 0.5" | client (orange) |
| Kubernetes Pod | `ROUND_RECTANGLE` | 0.8" x 0.4" | accent |
| ファイアウォール | `RECTANGLE` + 赤枠 | 0.5" x 0.3" | alertRed 枠 |

### 5.2 コンポーネント描画関数

```python
def add_component(self, slide_id, name, comp_type, x, y,
                  w=None, h=None, color=None, sublabel=None):
    """標準コンポーネントを描画する。

    comp_type: "app" | "database" | "loadbalancer" | "server" |
               "queue" | "user" | "pod" | "firewall"
    """
    defaults = {
        "app":          ("ROUND_RECTANGLE", 1.2, 0.5, ARCH_COLORS["scalar_product"]),
        "database":     ("CAN",             0.6, 0.7, ARCH_COLORS["external"]),
        "loadbalancer": ("HEXAGON",         0.5, 0.5, ARCH_COLORS["cloud_service"]),
        "server":       ("RECTANGLE",       1.0, 0.5, ARCH_COLORS["external"]),
        "queue":        ("CHEVRON",         0.8, 0.4, ARCH_COLORS["external"]),
        "user":         ("ELLIPSE",         0.5, 0.5, ARCH_COLORS["client"]),
        "pod":          ("ROUND_RECTANGLE", 0.8, 0.4, ARCH_COLORS["cloud_service"]),
        "firewall":     ("RECTANGLE",       0.5, 0.3, hex_to_rgb("#E74C3C")),
    }
    shape, dw, dh, dc = defaults.get(comp_type, defaults["app"])
    w = w or dw
    h = h or dh
    fill = color or dc

    shape_id = self.add_shape(slide_id, shape, x, y, w, h, fill=fill)

    # テキスト（シェイプ内に配置）
    fs = 9 if len(name) > 12 else 10
    self.add_text(slide_id, name,
                  x, y, w, h,
                  font_size=fs, bold=True,
                  color={"red": 1, "green": 1, "blue": 1},
                  alignment="CENTER", valign="MIDDLE")

    # サブラベル（シェイプの下に配置）
    if sublabel:
        self.add_text(slide_id, sublabel,
                      x - 0.1, y + h + 0.02, w + 0.2, 0.18,
                      font_size=8, color=C.textSecondary,
                      alignment="CENTER")
    return shape_id
```

### 5.3 ScalarDB 専用コンポーネント

```python
def add_scalardb_component(self, slide_id, x, y, w=2.0, h=0.6,
                           variant="standard"):
    """ScalarDB コンポーネントを描画する。

    variant: "standard" | "cluster" | "compact"
    """
    if variant == "cluster":
        # クラスタ表現（影付き重ね矩形）
        self.add_rounded_rect(slide_id, x + 0.06, y + 0.06, w, h,
                              fill=ARCH_COLORS["scalar_dark"])
        self.add_rounded_rect(slide_id, x + 0.03, y + 0.03, w, h,
                              fill=ARCH_COLORS["scalar_dark"])
    shape_id = self.add_rounded_rect(slide_id, x, y, w, h,
                                     fill=ARCH_COLORS["scalar_product"])
    label = "ScalarDB" if variant != "compact" else "SDB"
    fs = 12 if variant != "compact" else 9
    self.add_text(slide_id, label,
                  x, y, w, h,
                  font_size=fs, bold=True,
                  color={"red": 1, "green": 1, "blue": 1},
                  alignment="CENTER", valign="MIDDLE")
    return shape_id


def add_scalardl_component(self, slide_id, x, y, w=2.0, h=0.6):
    """ScalarDL コンポーネントを描画する。"""
    shape_id = self.add_rounded_rect(slide_id, x, y, w, h,
                                     fill=ARCH_COLORS["scalar_product"])
    self.add_text(slide_id, "ScalarDL",
                  x, y, w, h,
                  font_size=12, bold=True,
                  color={"red": 1, "green": 1, "blue": 1},
                  alignment="CENTER", valign="MIDDLE")
    return shape_id
```

---

## 6. ゾーン・境界の描画

### 6.1 ゾーンの作成

```python
def add_zone(self, slide_id, label, x, y, w, h,
             fill_color=None, border_color=None,
             border_dash="SOLID", alpha=0.08,
             label_position="top-left"):
    """ゾーン（領域境界）を描画する。

    半透明の背景矩形 + 境界線 + ラベルで構成する。
    Z-order を背面に設定し、コンポーネントの下に配置する。

    label_position: "top-left" | "top-center" | "top-right"
    """
    # 背景矩形（半透明）
    fill = fill_color or hex_to_rgb(C.backgroundAlt) if isinstance(C.backgroundAlt, str) else (fill_color or C.backgroundAlt)
    bg_id = self.add_rounded_rect(slide_id, x, y, w, h,
                                  fill=fill,
                                  border_color=border_color or C.border)
    # 透明度設定
    self.shape_opacity(bg_id, alpha)
    # Z-order を背面に
    self.set_z_order(bg_id, "SEND_TO_BACK")

    # 境界線の破線スタイル
    if border_dash != "SOLID":
        self.requests.append({"updateShapeProperties": {
            "objectId": bg_id,
            "shapeProperties": {
                "outline": {
                    "dashStyle": border_dash,
                }
            },
            "fields": "outline.dashStyle",
        }})

    # ラベル
    label_color = border_color or C.textMuted
    if label_position == "top-left":
        self.add_text(slide_id, label,
                      x + 0.1, y + 0.05, w * 0.5, 0.2,
                      font_size=9, bold=True, color=label_color)
    elif label_position == "top-center":
        self.add_text(slide_id, label,
                      x, y + 0.05, w, 0.2,
                      font_size=9, bold=True, color=label_color,
                      alignment="CENTER")
    elif label_position == "top-right":
        self.add_text(slide_id, label,
                      x + w * 0.5, y + 0.05, w * 0.5 - 0.1, 0.2,
                      font_size=9, bold=True, color=label_color,
                      alignment="END")

    return bg_id
```

### 6.2 入れ子ゾーン

リージョン > VPC > サブネット > AZ のような入れ子構造を描画する。

```python
def add_nested_zones(self, slide_id, zones):
    """入れ子ゾーンを描画する。外側から内側の順に配置する。

    zones: [
        {"label": "AWS ap-northeast-1", "x": 0.5, "y": 0.8, "w": 8.5, "h": 4.0,
         "fill": C.backgroundAlt, "border": C.border,
         "dash": "SOLID", "alpha": 0.05},
        {"label": "VPC 10.0.0.0/16", "x": 0.8, "y": 1.2, "w": 7.9, "h": 3.4,
         "fill": C.surfaceLight, "border": C.primary,
         "dash": "SOLID", "alpha": 0.08},
        {"label": "Private Subnet", "x": 1.1, "y": 1.6, "w": 3.5, "h": 2.8,
         "fill": C.calloutBg, "border": C.accent,
         "dash": "SOLID", "alpha": 0.06},
    ]
    """
    zone_ids = []
    for zone in zones:
        zid = self.add_zone(
            slide_id, zone["label"],
            zone["x"], zone["y"], zone["w"], zone["h"],
            fill_color=zone.get("fill"),
            border_color=zone.get("border"),
            border_dash=zone.get("dash", "SOLID"),
            alpha=zone.get("alpha", 0.08),
        )
        zone_ids.append(zid)
    return zone_ids
```

### 6.3 Z-order 管理ルール

構成図の要素は以下の順序で描画する:

| 描画順 | 要素 | Z-order 操作 | 理由 |
|--------|------|-------------|------|
| 1（最初） | ゾーン背景（外側） | `SEND_TO_BACK` | 最背面 |
| 2 | ゾーン背景（内側） | `SEND_TO_BACK` しない | 外側の上に重なる |
| 3 | コネクタ | -- | 中間層 |
| 4 | コンポーネント（シェイプ/アイコン） | -- | コネクタの上 |
| 5（最後） | テキストラベル | `BRING_TO_FRONT` | 最前面 |

> **重要**: ゾーンは外側から内側の順に `add_zone()` し、外側のみ `SEND_TO_BACK` する。内側ゾーンは自然な描画順で外側の上に配置される。

---

## 7. コネクタの描画

### 7.1 データフローコネクタ

```python
def add_data_flow(self, slide_id, from_x, from_y, to_x, to_y,
                  flow_type="normal", label=None):
    """データフローコネクタを描画する。

    flow_type: "normal" | "read" | "write" | "error" |
               "optional" | "bidirectional" | "replication" | "monitor"
    """
    styles = {
        "normal": {
            "color": ARCH_COLORS["flow_normal"],
            "dash": "SOLID", "weight": 1.5,
            "start_arrow": None, "end_arrow": "FILL_ARROW",
        },
        "read": {
            "color": ARCH_COLORS["scalar_product"],
            "dash": "SOLID", "weight": 1.0,
            "start_arrow": None, "end_arrow": "FILL_ARROW",
        },
        "write": {
            "color": ARCH_COLORS["cloud_service"],
            "dash": "SOLID", "weight": 1.0,
            "start_arrow": None, "end_arrow": "FILL_ARROW",
        },
        "error": {
            "color": ARCH_COLORS["flow_error"],
            "dash": "DASH", "weight": 1.0,
            "start_arrow": None, "end_arrow": "FILL_ARROW",
        },
        "optional": {
            "color": ARCH_COLORS["external"],
            "dash": "DOT", "weight": 0.75,
            "start_arrow": None, "end_arrow": "STEALTH_ARROW",
        },
        "bidirectional": {
            "color": ARCH_COLORS["scalar_product"],
            "dash": "SOLID", "weight": 1.0,
            "start_arrow": "FILL_ARROW", "end_arrow": "FILL_ARROW",
        },
        "replication": {
            "color": ARCH_COLORS["flow_normal"],
            "dash": "LONG_DASH", "weight": 1.0,
            "start_arrow": None, "end_arrow": "FILL_ARROW",
        },
        "monitor": {
            "color": ARCH_COLORS["external"],
            "dash": "DASH_DOT", "weight": 0.75,
            "start_arrow": None, "end_arrow": "STEALTH_ARROW",
        },
    }
    s = styles[flow_type]
    conn_id = self.add_connector(
        slide_id, from_x, from_y, to_x, to_y,
        color=s["color"], weight=s["weight"],
        start_arrow=s["start_arrow"],
        end_arrow=s["end_arrow"],
        dash_style=s["dash"],
    )

    # ラベル（コネクタの中点に配置）
    if label:
        mx = (from_x + to_x) / 2
        my = (from_y + to_y) / 2
        # 水平線はラベルを少し上にオフセット
        is_horizontal = abs(to_y - from_y) < abs(to_x - from_x)
        offset_y = -0.18 if is_horizontal else 0
        offset_x = 0.12 if not is_horizontal else 0
        self.add_text(slide_id, label,
                      mx - 0.4 + offset_x, my - 0.1 + offset_y, 0.8, 0.2,
                      font_size=8, color=s["color"],
                      alignment="CENTER", valign="MIDDLE")
    return conn_id
```

### 7.2 シェイプ接続コネクタ

シェイプ同士を接続するコネクタ。シェイプを移動しても自動追従する。

```python
def add_connected_data_flow(self, slide_id,
                            from_shape_id, from_site,
                            to_shape_id, to_site,
                            flow_type="normal", label=None):
    """シェイプ接続コネクタを描画する。

    connectionSiteIndex: 0=TOP, 1=LEFT, 2=BOTTOM, 3=RIGHT
    """
    CONN_TOP, CONN_LEFT, CONN_BOTTOM, CONN_RIGHT = 0, 1, 2, 3
    styles = {
        "normal":  {"color": ARCH_COLORS["flow_normal"], "dash": "SOLID", "weight": 1.5},
        "read":    {"color": ARCH_COLORS["scalar_product"], "dash": "SOLID", "weight": 1.0},
        "write":   {"color": ARCH_COLORS["cloud_service"], "dash": "SOLID", "weight": 1.0},
        "error":   {"color": ARCH_COLORS["flow_error"], "dash": "DASH", "weight": 1.0},
    }
    s = styles.get(flow_type, styles["normal"])
    return self.add_connected_connector(
        slide_id,
        from_shape_id, from_site,
        to_shape_id, to_site,
        color=s["color"], weight=s["weight"],
        end_arrow="FILL_ARROW",
        dash_style=s["dash"],
    )
```

### 7.3 フローラベルの配置

コネクタ上にプロトコル名やデータ型を表示する。

```python
def add_flow_label(self, slide_id, from_x, from_y, to_x, to_y,
                   label, color=None):
    """コネクタの中点にフローラベルを配置する。

    使用例: "gRPC", "HTTPS", "JDBC", "Kafka", "TCP/IP"
    """
    mx = (from_x + to_x) / 2
    my = (from_y + to_y) / 2
    lc = color or C.textSecondary
    # 背景付きラベル（可読性向上）
    label_w = max(len(label) * 0.08, 0.5)
    bg_id = self.add_rounded_rect(slide_id,
                                  mx - label_w / 2, my - 0.1,
                                  label_w, 0.2,
                                  fill=C.background,
                                  border_color=C.border)
    self.add_text(slide_id, label,
                  mx - label_w / 2, my - 0.1, label_w, 0.2,
                  font_size=7, color=lc,
                  alignment="CENTER", valign="MIDDLE")
```

---

## 8. 座標計算ヘルパー

### 8.1 グリッドシステム

```python
class ArchGrid:
    """アーキテクチャ図用のグリッド計算ヘルパー。

    スライドの描画可能領域をグリッドに分割し、
    コンポーネントの配置座標を計算する。
    """

    def __init__(self, x_start=0.5, y_start=0.8,
                 x_end=9.5, y_end=5.0,
                 cols=6, rows=4):
        """グリッドを初期化する。

        x_start, y_start: 左上座標（インチ）
        x_end, y_end: 右下座標（インチ）
        cols, rows: グリッドの列数・行数
        """
        self.x_start = x_start
        self.y_start = y_start
        self.x_end = x_end
        self.y_end = y_end
        self.cols = cols
        self.rows = rows
        self.cell_w = (x_end - x_start) / cols
        self.cell_h = (y_end - y_start) / rows

    def pos(self, col, row):
        """グリッド座標 → インチ座標（セル左上）。"""
        return (self.x_start + col * self.cell_w,
                self.y_start + row * self.cell_h)

    def center(self, col, row, span_cols=1, span_rows=1):
        """グリッドセルの中心座標。"""
        x = self.x_start + col * self.cell_w + span_cols * self.cell_w / 2
        y = self.y_start + row * self.cell_h + span_rows * self.cell_h / 2
        return (x, y)

    def rect(self, col, row, span_cols=1, span_rows=1, margin=0.05):
        """グリッドセルの矩形座標 (x, y, w, h) を返す。margin でパディング。"""
        x = self.x_start + col * self.cell_w + margin
        y = self.y_start + row * self.cell_h + margin
        w = span_cols * self.cell_w - 2 * margin
        h = span_rows * self.cell_h - 2 * margin
        return (x, y, w, h)
```

### 8.2 等間隔配置

```python
def distribute_evenly(start, end, count, item_size=0):
    """N 個の要素を start-end 間で等間隔に配置する。

    Returns: list of x 座標（各要素の左端）。
    item_size: 各要素の幅。0 の場合は点として扱う。
    """
    if count <= 0:
        return []
    if count == 1:
        return [start + (end - start - item_size) / 2]
    total_items = count * item_size
    total_gaps = end - start - total_items
    gap = total_gaps / (count + 1)
    return [start + gap + i * (item_size + gap) for i in range(count)]


def distribute_components(self, slide_id, components, y, zone_x=0.5, zone_w=9.0):
    """コンポーネントを横方向に等間隔配置する。

    components: [{"name": str, "type": str, "w": float, "h": float, "color": RGB}]
    y: 配置する Y 座標
    """
    comp_w = components[0].get("w", 1.2)
    positions = distribute_evenly(zone_x, zone_x + zone_w,
                                  len(components), comp_w)
    shape_ids = []
    for i, comp in enumerate(components):
        cw = comp.get("w", comp_w)
        ch = comp.get("h", 0.5)
        sid = self.add_component(slide_id, comp["name"],
                                 comp.get("type", "app"),
                                 positions[i], y, cw, ch,
                                 color=comp.get("color"))
        shape_ids.append(sid)
    return shape_ids
```

### 8.3 コネクタ端点計算

```python
def connector_endpoint(x, y, w, h, direction):
    """コンポーネントの辺の中点を計算する。

    direction: "top" | "bottom" | "left" | "right"
    Returns: (x, y) 端点座標
    """
    endpoints = {
        "top":    (x + w / 2, y),
        "bottom": (x + w / 2, y + h),
        "left":   (x,         y + h / 2),
        "right":  (x + w,     y + h / 2),
    }
    return endpoints[direction]


def connect_components(self, slide_id,
                       from_x, from_y, from_w, from_h, from_dir,
                       to_x, to_y, to_w, to_h, to_dir,
                       flow_type="normal", label=None):
    """2 つのコンポーネント間にデータフローコネクタを配置する。

    辺の中点を自動計算してコネクタを描画する。
    """
    fx, fy = connector_endpoint(from_x, from_y, from_w, from_h, from_dir)
    tx, ty = connector_endpoint(to_x, to_y, to_w, to_h, to_dir)
    return self.add_data_flow(slide_id, fx, fy, tx, ty,
                              flow_type=flow_type, label=label)
```

---

## 9. 典型的な構成パターン

### 9.1 ScalarDB 3 層アーキテクチャ

Client --> ScalarDB --> Multi-DB backend の標準構成。

```python
def compose_scalardb_3tier(self, slide_id):
    """ScalarDB 3 層アーキテクチャ構成図を描画する。"""
    grid = ArchGrid(x_start=0.5, y_start=0.9, x_end=9.5, y_end=4.9,
                    cols=6, rows=3)

    # --- Layer 1: Client (orange) ---
    client_zone = self.add_zone(slide_id, "Application Layer",
                                0.5, 0.9, 9.0, 1.1,
                                fill_color=hex_to_rgb("#FFF5E6"),
                                border_color=ARCH_COLORS["client"],
                                alpha=0.15)
    apps = [
        {"name": "Web App", "type": "app", "w": 1.3, "h": 0.5,
         "color": ARCH_COLORS["client"]},
        {"name": "API Server", "type": "app", "w": 1.3, "h": 0.5,
         "color": ARCH_COLORS["client"]},
        {"name": "Batch Job", "type": "app", "w": 1.3, "h": 0.5,
         "color": ARCH_COLORS["client"]},
    ]
    app_xs = distribute_evenly(0.8, 9.2, 3, 1.3)
    app_y = 1.15
    for i, app in enumerate(apps):
        self.add_component(slide_id, app["name"], app["type"],
                           app_xs[i], app_y, app["w"], app["h"],
                           color=app["color"])

    # --- Layer 2: ScalarDB (blue) ---
    scalar_zone = self.add_zone(slide_id, "ScalarDB Layer",
                                0.5, 2.3, 9.0, 1.0,
                                fill_color=hex_to_rgb("#E8F0FE"),
                                border_color=ARCH_COLORS["scalar_product"],
                                alpha=0.12)
    sdb_x, sdb_y, sdb_w, sdb_h = 3.5, 2.5, 3.0, 0.6
    self.add_scalardb_component(slide_id, sdb_x, sdb_y, sdb_w, sdb_h,
                                variant="cluster")

    # --- Layer 3: Storage (gray) ---
    storage_zone = self.add_zone(slide_id, "Storage Layer",
                                 0.5, 3.6, 9.0, 1.3,
                                 fill_color=hex_to_rgb("#F5F5F5"),
                                 border_color=ARCH_COLORS["external"],
                                 alpha=0.12)
    dbs = [
        {"name": "MySQL", "type": "database", "w": 0.7, "h": 0.8,
         "color": ARCH_COLORS["external"]},
        {"name": "PostgreSQL", "type": "database", "w": 0.7, "h": 0.8,
         "color": ARCH_COLORS["external"]},
        {"name": "Cassandra", "type": "database", "w": 0.7, "h": 0.8,
         "color": ARCH_COLORS["external"]},
    ]
    db_xs = distribute_evenly(1.5, 8.5, 3, 0.7)
    db_y = 3.75
    for i, db in enumerate(dbs):
        self.add_component(slide_id, db["name"], db["type"],
                           db_xs[i], db_y, db["w"], db["h"],
                           color=db["color"])

    # --- Connectors ---
    # Apps -> ScalarDB
    for ax in app_xs:
        self.add_data_flow(slide_id,
                           ax + 0.65, app_y + 0.5,
                           sdb_x + sdb_w / 2, sdb_y,
                           flow_type="normal")
    # ScalarDB -> DBs
    for dx in db_xs:
        self.add_data_flow(slide_id,
                           sdb_x + sdb_w / 2, sdb_y + sdb_h,
                           dx + 0.35, db_y,
                           flow_type="read")
```

### 9.2 ScalarDB + マルチクラウド

ScalarDB が AWS と GCP にまたがるマルチクラウド構成。

```python
def compose_scalardb_multicloud(self, slide_id):
    """ScalarDB マルチクラウド構成図を描画する。"""
    # --- AWS Region Zone (左半分) ---
    self.add_zone(slide_id, "",
                  0.3, 0.9, 4.5, 4.0,
                  fill_color=hex_to_rgb("#FFF5E6"),
                  border_color=hex_to_rgb("#FF9900"),
                  alpha=0.06)
    self.add_vendor_zone_label(slide_id, "aws", "ap-northeast-1",
                               0.3, 0.9)

    # AWS VPC
    self.add_zone(slide_id, "VPC",
                  0.5, 1.3, 4.1, 3.4,
                  fill_color=C.surfaceLight,
                  border_color=C.primary,
                  alpha=0.08)

    # ScalarDB on AWS
    sdb_aws = self.add_scalardb_component(slide_id, 1.5, 2.2, 2.0, 0.6)
    # RDS (AWS)
    self.add_component(slide_id, "Amazon\nRDS", "database",
                       2.0, 3.5, 0.8, 0.9,
                       color=ARCH_COLORS["external"])

    # --- GCP Region Zone (右半分) ---
    self.add_zone(slide_id, "",
                  5.2, 0.9, 4.5, 4.0,
                  fill_color=hex_to_rgb("#E8F0FE"),
                  border_color=hex_to_rgb("#4285F4"),
                  alpha=0.06)
    self.add_vendor_zone_label(slide_id, "gcp", "asia-northeast1",
                               5.2, 0.9)

    # GCP VPC
    self.add_zone(slide_id, "VPC",
                  5.4, 1.3, 4.1, 3.4,
                  fill_color=C.surfaceLight,
                  border_color=C.primary,
                  alpha=0.08)

    # ScalarDB on GCP
    sdb_gcp = self.add_scalardb_component(slide_id, 6.5, 2.2, 2.0, 0.6)
    # Cloud Spanner (GCP)
    self.add_component(slide_id, "Cloud\nSpanner", "database",
                       7.0, 3.5, 0.8, 0.9,
                       color=ARCH_COLORS["external"])

    # --- Cross-cloud connector ---
    self.add_data_flow(slide_id,
                       3.5, 2.5, 6.5, 2.5,
                       flow_type="bidirectional",
                       label="gRPC")

    # --- ScalarDB -> DB connectors ---
    self.add_data_flow(slide_id,
                       2.5, 2.8, 2.4, 3.5,
                       flow_type="read", label="JDBC")
    self.add_data_flow(slide_id,
                       7.5, 2.8, 7.4, 3.5,
                       flow_type="read", label="gRPC")
```

### 9.3 ScalarDL ブロックチェーン連携

```python
def compose_scalardl_ledger(self, slide_id):
    """ScalarDL Ledger 構成図を描画する。"""
    # Client Apps
    self.add_component(slide_id, "Client SDK", "app",
                       4.0, 0.9, 2.0, 0.5,
                       color=ARCH_COLORS["client"])

    # ScalarDL
    self.add_scalardl_component(slide_id, 3.5, 2.0, 3.0, 0.6)

    # Ledger / Auditor
    self.add_component(slide_id, "Ledger", "database",
                       2.0, 3.3, 1.0, 0.8,
                       color=ARCH_COLORS["scalar_product"],
                       sublabel="改ざん検知台帳")
    self.add_component(slide_id, "Auditor", "database",
                       7.0, 3.3, 1.0, 0.8,
                       color=ARCH_COLORS["scalar_dark"],
                       sublabel="独立監査台帳")

    # Connectors
    self.add_data_flow(slide_id, 5.0, 1.4, 5.0, 2.0,
                       flow_type="normal", label="gRPC")
    self.add_data_flow(slide_id, 4.0, 2.6, 2.5, 3.3,
                       flow_type="write", label="書込")
    self.add_data_flow(slide_id, 6.0, 2.6, 7.5, 3.3,
                       flow_type="write", label="監査")
    # 検証コネクタ（双方向）
    self.add_data_flow(slide_id, 3.0, 3.7, 7.0, 3.7,
                       flow_type="bidirectional", label="Byzantine\nFault Detection")
```

### 9.4 マイクロサービス with ScalarDB

複数のマイクロサービスが ScalarDB で分散トランザクションを実行する構成。

```python
def compose_microservices_scalardb(self, slide_id):
    """マイクロサービス + ScalarDB 構成図を描画する。"""
    # API Gateway
    self.add_component(slide_id, "API Gateway", "loadbalancer",
                       4.25, 0.9, 1.5, 0.5,
                       color=ARCH_COLORS["cloud_service"])

    # Microservices (3 services)
    services = ["Order\nService", "Payment\nService", "Inventory\nService"]
    svc_xs = distribute_evenly(0.8, 9.2, 3, 1.5)
    for i, svc in enumerate(services):
        self.add_component(slide_id, svc, "app",
                           svc_xs[i], 1.8, 1.5, 0.6,
                           color=ARCH_COLORS["scalar_product"])

    # ScalarDB (central coordinator)
    self.add_scalardb_component(slide_id, 3.0, 3.0, 4.0, 0.6,
                                variant="cluster")

    # Databases (per-service)
    db_names = ["Order DB\n(MySQL)", "Payment DB\n(PostgreSQL)", "Inventory DB\n(DynamoDB)"]
    db_xs = distribute_evenly(0.8, 9.2, 3, 0.8)
    for i, db in enumerate(db_names):
        self.add_component(slide_id, db, "database",
                           db_xs[i] + 0.35, 4.0, 0.8, 0.9,
                           color=ARCH_COLORS["external"])

    # Connectors: Gateway -> Services
    for sx in svc_xs:
        self.add_data_flow(slide_id,
                           5.0, 1.4, sx + 0.75, 1.8,
                           flow_type="normal")
    # Connectors: Services -> ScalarDB
    for sx in svc_xs:
        self.add_data_flow(slide_id,
                           sx + 0.75, 2.4, 5.0, 3.0,
                           flow_type="read")
    # Connectors: ScalarDB -> DBs
    for dx in db_xs:
        self.add_data_flow(slide_id,
                           5.0, 3.6, dx + 0.75, 4.0,
                           flow_type="write")
```

### 9.5 ハイブリッドクラウド（オンプレ + クラウド）

```python
def compose_hybrid_cloud(self, slide_id):
    """ハイブリッドクラウド構成図（オンプレ + AWS）を描画する。"""
    # --- On-premises Zone ---
    self.add_zone(slide_id, "On-premises Data Center",
                  0.3, 0.9, 4.3, 4.0,
                  fill_color=hex_to_rgb("#F0F0F0"),
                  border_color=ARCH_COLORS["external"],
                  alpha=0.10)

    self.add_component(slide_id, "Legacy\nApplication", "app",
                       1.0, 1.5, 1.5, 0.6,
                       color=ARCH_COLORS["external"])
    self.add_component(slide_id, "Oracle DB", "database",
                       1.2, 3.0, 0.8, 0.9,
                       color=ARCH_COLORS["external"])
    self.add_component(slide_id, "ScalarDB\nBridge", "app",
                       3.0, 2.3, 1.3, 0.6,
                       color=ARCH_COLORS["scalar_product"])

    # --- AWS Cloud Zone ---
    self.add_zone(slide_id, "",
                  5.0, 0.9, 4.7, 4.0,
                  fill_color=hex_to_rgb("#FFF5E6"),
                  border_color=hex_to_rgb("#FF9900"),
                  alpha=0.06)
    self.add_vendor_zone_label(slide_id, "aws", "ap-northeast-1",
                               5.0, 0.9)

    self.add_scalardb_component(slide_id, 5.8, 1.8, 2.5, 0.6)
    self.add_component(slide_id, "Amazon\nRDS", "database",
                       5.5, 3.2, 0.8, 0.9,
                       color=ARCH_COLORS["external"])
    self.add_component(slide_id, "Amazon\nDynamoDB", "database",
                       8.0, 3.2, 0.8, 0.9,
                       color=ARCH_COLORS["external"])

    # --- VPN / Direct Connect ---
    self.add_data_flow(slide_id, 4.3, 2.6, 5.8, 2.1,
                       flow_type="bidirectional",
                       label="VPN /\nDirect Connect")

    # On-prem connectors
    self.add_data_flow(slide_id, 1.75, 2.1, 3.0, 2.5,
                       flow_type="normal")
    self.add_data_flow(slide_id, 3.0, 2.9, 1.6, 3.0,
                       flow_type="read")

    # AWS connectors
    self.add_data_flow(slide_id, 7.05, 2.4, 5.9, 3.2,
                       flow_type="read")
    self.add_data_flow(slide_id, 7.05, 2.4, 8.4, 3.2,
                       flow_type="read")
```

---

## 10. 凡例（レジェンド）の追加

### 10.1 色凡例

構成図の右下または下部に色の意味を説明する凡例を配置する。

```python
def add_architecture_legend(self, slide_id, x=7.0, y=4.5,
                            items=None):
    """構成図の凡例を追加する。

    items: [{"label": str, "color": RGB, "shape": str}]
    shape: "rect" | "line_solid" | "line_dash" | "line_dot"
    """
    if items is None:
        items = [
            {"label": "Scalar 製品", "color": ARCH_COLORS["scalar_product"], "shape": "rect"},
            {"label": "外部サービス", "color": ARCH_COLORS["external"], "shape": "rect"},
            {"label": "クライアント", "color": ARCH_COLORS["client"], "shape": "rect"},
            {"label": "データフロー", "color": ARCH_COLORS["flow_normal"], "shape": "line_solid"},
            {"label": "エラーパス", "color": ARCH_COLORS["flow_error"], "shape": "line_dash"},
        ]

    row_h = 0.22
    total_h = len(items) * row_h + 0.15
    # 凡例枠
    self.add_rounded_rect(slide_id, x, y, 2.5, total_h,
                          fill=C.background,
                          border_color=C.border)
    # タイトル
    self.add_text(slide_id, "Legend",
                  x + 0.1, y + 0.03, 1.0, 0.18,
                  font_size=8, bold=True, color=C.textTitle)

    for i, item in enumerate(items):
        iy = y + 0.18 + i * row_h
        if item["shape"] == "rect":
            self.add_rect(slide_id, x + 0.1, iy + 0.03,
                          0.2, 0.14, fill=item["color"])
        elif item["shape"] == "line_solid":
            self.add_connector(slide_id,
                               x + 0.1, iy + 0.10,
                               x + 0.3, iy + 0.10,
                               color=item["color"], weight=1.5)
        elif item["shape"] == "line_dash":
            self.add_connector(slide_id,
                               x + 0.1, iy + 0.10,
                               x + 0.3, iy + 0.10,
                               color=item["color"], weight=1.0,
                               dash_style="DASH")
        elif item["shape"] == "line_dot":
            self.add_connector(slide_id,
                               x + 0.1, iy + 0.10,
                               x + 0.3, iy + 0.10,
                               color=item["color"], weight=0.75,
                               dash_style="DOT")
        # ラベル
        self.add_text(slide_id, item["label"],
                      x + 0.4, iy, 1.8, row_h,
                      font_size=8, color=C.textPrimary,
                      valign="MIDDLE")
```

### 10.2 コネクタ凡例

```python
def add_connector_legend(self, slide_id, x=7.0, y=4.0):
    """コネクタ種別の凡例を追加する。"""
    items = [
        {"label": "正常フロー",     "color": ARCH_COLORS["flow_normal"],  "shape": "line_solid"},
        {"label": "読取クエリ",     "color": ARCH_COLORS["scalar_product"], "shape": "line_solid"},
        {"label": "書込クエリ",     "color": ARCH_COLORS["cloud_service"],  "shape": "line_solid"},
        {"label": "エラーパス",     "color": ARCH_COLORS["flow_error"],   "shape": "line_dash"},
        {"label": "オプショナル",   "color": ARCH_COLORS["external"],      "shape": "line_dot"},
    ]
    self.add_architecture_legend(slide_id, x, y, items)
```

---

## 11. ベストプラクティス

### 11.1 レイヤーの数

- **推奨**: 3 -- 4 レイヤー
- **最大**: 5 レイヤー（それ以上はスライドを分割）
- 各レイヤーの高さは最低 0.8"、推奨 1.0" 以上

### 11.2 コンポーネント数

- **1 スライドの上限**: 12 -- 15 コンポーネント
- **ラベル文字数**: コンポーネント名 15 文字以内（日本語）
- **コネクタ数**: 最大 15 -- 20 本（それ以上は複雑すぎる）
- **ゾーン数**: 最大 4 -- 5 個

### 11.3 フォントサイズ下限

| 要素 | 最小 | 推奨 |
|------|------|------|
| コンポーネント名 | 9pt | 10-12pt |
| ゾーンラベル | 9pt | 9-10pt |
| コネクタラベル | 7pt | 8pt |
| フローラベル（プロトコル名） | 7pt | 7-8pt |
| 凡例テキスト | 8pt | 8-9pt |
| サブラベル | 8pt | 8-9pt |

> **原則**: 7pt 未満のテキストは禁止。構成図はラベルが小さくなりがちなため、8pt 以上を目標とする。

### 11.4 Z-order の管理

1. **最背面**: ゾーン背景（`SEND_TO_BACK`）
2. **中間**: コネクタ
3. **前面**: コンポーネント（シェイプ、アイコン）
4. **最前面**: テキストラベル（`BRING_TO_FRONT`）

描画順序で自然に Z-order が決まるため、ゾーン → コネクタ → コンポーネント → ラベルの順に描画する。

### 11.5 描画可能領域

Google Slides のページサイズ 10.0" x 5.625" を考慮:

| マスター | 有効領域 | 備考 |
|---------|---------|------|
| CONTENT | 0.5" -- 9.5" x 0.8" -- 5.0" | タイトル + フッター考慮 |
| BLANK | 0.3" -- 9.7" x 0.3" -- 5.3" | マージンのみ |
| CONTENT（図のみ） | 0.5" -- 9.5" x 0.8" -- 5.2" | フッターはあるが図は重ならない前提 |

### 11.6 コネクタの交差回避

- 水平レイヤー構成では、コネクタは基本的に**垂直方向**（上下）のみ
- 交差が避けられない場合は、一方を `DASH` にして区別
- 複雑なフローはフローダイアグラム（`infographic-patterns.md` パターン 10/11）に分離

### 11.7 テキストの可読性

- コンポーネント名は白テキスト（`#FFFFFF`）を基本とし、塗り色とのコントラスト比 4.5:1 以上を確保
- 薄い色のコンポーネントには `C.textTitle`（`#004266`）を使用
- ゾーンラベルはゾーンの `border_color` と同色にして視覚的統一を図る

---

## 12. 完全な構成図例: ScalarDB + AWS

以下は、ScalarDB を AWS 上にデプロイした構成図の完全な Python コード例。
CONTENT マスター（タイトル + フッター付き）を使用する。

```python
def compose_scalardb_aws_full(self):
    """ScalarDB + AWS 構成図のフルコード例。

    描画内容:
    - AWS Region ゾーン
    - VPC ゾーン（入れ子）
    - EC2 インスタンス上の ScalarDB クラスタ
    - RDS MySQL (Primary + Read Replica)
    - Application Load Balancer
    - クライアントアプリケーション
    - データフローコネクタ（正常 + エラー）
    - 凡例
    """
    # --- スライド作成 ---
    sid = self.add_content_slide(
        "ScalarDB は AWS 上で異種 DB 間の ACID トランザクションを実現する"
    )

    # ===========================
    # ゾーン描画（外側 → 内側）
    # ===========================

    # AWS Region
    aws_zone = self.add_zone(sid, "",
                             0.4, 1.1, 8.8, 3.9,
                             fill_color=hex_to_rgb("#FFF8EE"),
                             border_color=hex_to_rgb("#FF9900"),
                             alpha=0.06)
    self.add_vendor_zone_label(sid, "aws", "ap-northeast-1", 0.4, 1.1)

    # VPC
    vpc_zone = self.add_zone(sid, "VPC  10.0.0.0/16",
                             0.6, 1.5, 8.4, 3.3,
                             fill_color=C.surfaceLight,
                             border_color=C.primary,
                             alpha=0.08)

    # Private Subnet A
    subnet_a = self.add_zone(sid, "Private Subnet A (AZ-a)",
                             0.8, 1.9, 3.8, 2.7,
                             fill_color=C.calloutBg,
                             border_color=C.accent,
                             border_dash="SOLID",
                             alpha=0.06)

    # Private Subnet B
    subnet_b = self.add_zone(sid, "Private Subnet B (AZ-c)",
                             4.9, 1.9, 4.0, 2.7,
                             fill_color=C.calloutBg,
                             border_color=C.accent,
                             border_dash="SOLID",
                             alpha=0.06)

    # ===========================
    # コンポーネント描画
    # ===========================

    # Client (スライド上部、ゾーン外)
    client_x, client_y = 3.5, 0.4
    client_w, client_h = 3.0, 0.5
    self.add_component(sid, "Application (ScalarDB SDK)", "app",
                       client_x, client_y, client_w, client_h,
                       color=ARCH_COLORS["client"])

    # ALB (Application Load Balancer)
    alb_x, alb_y = 4.25, 1.55
    alb_w, alb_h = 1.5, 0.3
    self.add_component(sid, "ALB", "loadbalancer",
                       alb_x, alb_y, alb_w, alb_h,
                       color=ARCH_COLORS["cloud_service"])

    # ScalarDB Cluster (Subnet A)
    sdb1_x, sdb1_y = 1.2, 2.4
    sdb1_w, sdb1_h = 1.5, 0.5
    self.add_component(sid, "ScalarDB\nNode 1", "app",
                       sdb1_x, sdb1_y, sdb1_w, sdb1_h,
                       color=ARCH_COLORS["scalar_product"])

    sdb2_x, sdb2_y = 1.2, 3.1
    sdb2_w, sdb2_h = 1.5, 0.5
    self.add_component(sid, "ScalarDB\nNode 2", "app",
                       sdb2_x, sdb2_y, sdb2_w, sdb2_h,
                       color=ARCH_COLORS["scalar_product"])

    # Envoy Proxy
    envoy_x, envoy_y = 3.2, 2.7
    envoy_w, envoy_h = 1.0, 0.5
    self.add_component(sid, "Scalar\nEnvoy", "app",
                       envoy_x, envoy_y, envoy_w, envoy_h,
                       color=ARCH_COLORS["scalar_dark"])

    # RDS Primary (Subnet B)
    rds1_x, rds1_y = 5.5, 2.3
    rds1_w, rds1_h = 0.8, 0.9
    self.add_component(sid, "RDS\nPrimary", "database",
                       rds1_x, rds1_y, rds1_w, rds1_h,
                       color=ARCH_COLORS["external"],
                       sublabel="MySQL 8.0")

    # RDS Read Replica (Subnet B)
    rds2_x, rds2_y = 7.5, 2.3
    rds2_w, rds2_h = 0.8, 0.9
    self.add_component(sid, "RDS\nReplica", "database",
                       rds2_x, rds2_y, rds2_w, rds2_h,
                       color=ARCH_COLORS["external"],
                       sublabel="Read Replica")

    # ===========================
    # コネクタ描画
    # ===========================

    # Client -> ALB (正常フロー)
    self.add_data_flow(sid,
                       client_x + client_w / 2, client_y + client_h,
                       alb_x + alb_w / 2, alb_y,
                       flow_type="normal", label="gRPC")

    # ALB -> ScalarDB Node 1
    self.add_data_flow(sid,
                       alb_x, alb_y + alb_h,
                       sdb1_x + sdb1_w / 2, sdb1_y,
                       flow_type="normal")

    # ALB -> ScalarDB Node 2
    self.add_data_flow(sid,
                       alb_x, alb_y + alb_h,
                       sdb2_x + sdb2_w / 2, sdb2_y,
                       flow_type="normal")

    # ScalarDB -> Envoy
    self.add_data_flow(sid,
                       sdb1_x + sdb1_w, sdb1_y + sdb1_h / 2,
                       envoy_x, envoy_y + envoy_h / 2,
                       flow_type="read")

    # Envoy -> RDS Primary (書込)
    self.add_data_flow(sid,
                       envoy_x + envoy_w, envoy_y + envoy_h / 2,
                       rds1_x, rds1_y + rds1_h / 2,
                       flow_type="write", label="JDBC")

    # RDS Primary -> RDS Replica (レプリケーション)
    self.add_data_flow(sid,
                       rds1_x + rds1_w, rds1_y + rds1_h / 2,
                       rds2_x, rds2_y + rds2_h / 2,
                       flow_type="replication", label="Replication")

    # エラーパス: ScalarDB -> Client (障害時フォールバック)
    self.add_data_flow(sid,
                       sdb2_x + sdb2_w / 2, sdb2_y + sdb2_h,
                       client_x, client_y + client_h,
                       flow_type="error", label="Error\nResponse")

    # ===========================
    # 凡例
    # ===========================
    self.add_architecture_legend(sid, x=7.0, y=4.0, items=[
        {"label": "Scalar 製品",   "color": ARCH_COLORS["scalar_product"], "shape": "rect"},
        {"label": "クライアント",   "color": ARCH_COLORS["client"],         "shape": "rect"},
        {"label": "AWS サービス",   "color": ARCH_COLORS["external"],       "shape": "rect"},
        {"label": "正常フロー",     "color": ARCH_COLORS["flow_normal"],    "shape": "line_solid"},
        {"label": "エラーパス",     "color": ARCH_COLORS["flow_error"],     "shape": "line_dash"},
    ])

    return sid
```

---

## 13. 構成図スライドタイプとの統合

### 13.1 slide_content.json での指定

構成図スライドは `architecture` タイプとして `slide_content.json` に記述する。

```json
{
    "index": 5,
    "type": "architecture",
    "content": {
        "title": "ScalarDB は AWS 上で異種 DB 間の ACID トランザクションを実現する",
        "pattern": "3tier",
        "cloud": "aws",
        "region": "ap-northeast-1",
        "layers": [
            {
                "name": "Application Layer",
                "components": [
                    {"name": "Web App", "type": "app"},
                    {"name": "API Server", "type": "app"}
                ]
            },
            {
                "name": "ScalarDB Layer",
                "components": [
                    {"name": "ScalarDB", "type": "scalardb", "variant": "cluster"}
                ]
            },
            {
                "name": "Storage Layer",
                "components": [
                    {"name": "RDS MySQL", "type": "database"},
                    {"name": "DynamoDB", "type": "database"}
                ]
            }
        ],
        "connections": [
            {"from": "Web App", "to": "ScalarDB", "flow": "normal"},
            {"from": "ScalarDB", "to": "RDS MySQL", "flow": "write", "label": "JDBC"},
            {"from": "ScalarDB", "to": "DynamoDB", "flow": "write", "label": "DynamoDB API"}
        ]
    },
    "speakerNotes": "ScalarDB は AWS 上のマネージド DB サービス間で分散トランザクションを実現します。"
}
```

### 13.2 パターンと compose 関数の対応

| pattern 値 | compose 関数 | 用途 |
|-----------|------------|------|
| `3tier` | `compose_scalardb_3tier()` | 3 層アーキテクチャ |
| `multicloud` | `compose_scalardb_multicloud()` | マルチクラウド |
| `hybrid` | `compose_hybrid_cloud()` | オンプレ + クラウド |
| `microservices` | `compose_microservices_scalardb()` | マイクロサービス |
| `ledger` | `compose_scalardl_ledger()` | ScalarDL 台帳 |
| `hub_spoke` | `compose_hub_spoke()` | ハブ & スポーク |
| `lr_flow` | `compose_lr_flow()` | 左右フロー |
| `custom` | -- | カスタム（手動座標指定） |

---

## 14. トラブルシューティング

### 14.1 よくある問題

| 問題 | 原因 | 解決策 |
|------|------|--------|
| ゾーンがコンポーネントの上に表示される | Z-order 未設定 | `set_z_order(zone_id, "SEND_TO_BACK")` |
| コネクタが表示されない | 幅/高さが 0 | `add_connector` は自動で 1 EMU にフォールバック |
| アイコンが見つからない | ファイル未配置 | フォールバックのテキストバッジを使用 |
| テキストが切れる | コンポーネントが小さすぎる | `font_size` を下げるか `w`/`h` を拡大 |
| 半透明ゾーンが不透明 | `alpha` 値が高い | `alpha=0.05` -- `0.10` に調整 |
| コネクタが交差する | レイアウトの問題 | レイヤー構成を見直し、コネクタ方向を統一 |
| 凡例がはみ出す | 配置位置の問題 | フッター領域を避け、描画可能領域内に配置 |

### 14.2 パフォーマンス

- 構成図 1 スライドあたりの API リクエスト数: 通常 80 -- 200 件
- コンポーネント 15 個 + コネクタ 20 本 + ゾーン 5 個 = 約 150 リクエスト
- `batchUpdate` のチャンクサイズ 500 件以内に収まるため、通常は 1 バッチで処理可能

### 14.3 デバッグのヒント

```python
# 座標デバッグ: グリッドを可視化する
def debug_grid(self, slide_id, grid):
    """グリッド線を薄い灰色で描画する（デバッグ用）。"""
    light_gray = hex_to_rgb("#E0E0E0")
    for col in range(grid.cols + 1):
        x = grid.x_start + col * grid.cell_w
        self.add_connector(slide_id, x, grid.y_start, x, grid.y_end,
                           color=light_gray, weight=0.5,
                           dash_style="DOT")
    for row in range(grid.rows + 1):
        y = grid.y_start + row * grid.cell_h
        self.add_connector(slide_id, grid.x_start, y, grid.x_end, y,
                           color=light_gray, weight=0.5,
                           dash_style="DOT")
```

---

## 15. チェックリスト

構成図を作成する際に確認するべき項目:

### デザイン

- [ ] コンポーネント数が 15 以下
- [ ] コネクタ数が 20 以下
- [ ] レイヤー数が 5 以下
- [ ] 全テキストが 7pt 以上（推奨 8pt 以上）
- [ ] 色コーディング規則に準拠（青=自社、灰=外部、橙=クライアント）
- [ ] ホワイトスペースが 15% 以上確保

### 技術

- [ ] ゾーンは外側から内側の順に描画
- [ ] ゾーンに `SEND_TO_BACK` を適用
- [ ] コネクタの端点がコンポーネントの辺に接続
- [ ] アイコン未配置時のフォールバック処理がある
- [ ] 凡例が描画可能領域内に収まっている

### コンテンツ

- [ ] タイトルがアクションタイトル（結論文）
- [ ] 全コンポーネントにラベルがある
- [ ] データフローの方向が矢印で明示されている
- [ ] プロトコル名（gRPC, JDBC 等）がラベル表示されている
- [ ] スピーカーノートに構成の説明がある
