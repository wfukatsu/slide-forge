*[English](product.md)*

# プロダクトカテゴリ コンポーザー仕様

> product カテゴリ 7 タイプのレンダリング仕様。
> 各コンポーザーはマスター関数で共通要素を配置した後、タイプ固有のコンテンツを追加する。

### 規約

- **`C`** — `templates/<theme>/theme.json` の `colors` セクションから展開した色定数クラス
- **`L`** — `templates/<theme>/theme.json` の `layouts` セクションから展開したレイアウト定数クラス
- **`sb`** — `SlideBuilder` インスタンス
- **ページサイズ** — 10.0" x 5.625"（Google Slides 16:9）
- **CONTENT マスター** — title: (0.323, 0.303, 9.354, 0.437), body: y=0.787 ~ y=5.208 (h=4.421")

---

## 1. product_overview — 製品全体像・価値提案

### マスター・パターン

- **マスター**: CONTENT（フッター付き）
- **パターン**: Pattern 7 (Icon+Text Row) + Pattern 8 (Stat Card)

### レイアウト

```
┌──────────────────────────────────────────┐
│ [アクションタイトル]                         │ 0.303"
├──────────────────────────────────────────┤ 0.787"
│  ┌─────────┐                             │
│  │ ロゴ     │  製品名                      │
│  │         │  キャッチコピー（tagline）      │
│  └─────────┘                             │ ~1.6"
├──────────────────────────────────────────┤
│  ◉ 機能A        ◉ 機能B        ◉ 機能C    │
│    説明            説明            説明      │
│                                          │
│  (keyFeatures: 3-4個を均等配置)            │
├──────────────────────────────────────────┤
│  [フッター: ロゴ | 著作権 | ページ番号]        │ 5.208"
└──────────────────────────────────────────┘
```

### 座標定数

| 要素 | X | Y | W | H |
|------|-----|-----|------|------|
| タイトル | 0.323 | 0.303 | 9.354 | 0.437 |
| ロゴ | 0.500 | 0.900 | 1.200 | 0.600 |
| 製品名 | 1.850 | 0.900 | 7.500 | 0.350 |
| tagline | 1.850 | 1.280 | 7.500 | 0.280 |
| 機能行 | 0.500 | 2.000 | — | — |
| フッター | — | 5.208 | — | — |

### コード

```python
def compose_product_overview(sb, slide_id, content, theme, page_num, total_pages=None):
    """製品全体像スライドを構築する。

    content: {
        title, productName, tagline,
        keyFeatures: [{icon, name, description}],
        productLogo (opt)
    }
    """
    # 1. CONTENT マスター共通要素
    apply_master_content(sb, theme, slide_id, page_num, total_pages)
    apply_action_title(sb, theme, slide_id, content["title"])

    # 2. 製品ロゴ（オプション）
    logo_w = 1.200
    if content.get("productLogo"):
        sb.add_image_from_asset(slide_id, theme["name"], "product-logos",
            content["productLogo"],
            0.500, 0.900, logo_w, 0.600)
        text_x = 1.850
    else:
        text_x = 0.500
        logo_w = 0

    # 3. 製品名
    sb.add_text(slide_id, content["productName"],
        text_x, 0.900, 9.354 - text_x + 0.323, 0.350,
        font_size=24, bold=True, color=C.textTitle,
        alignment="START", valign="MIDDLE")

    # 4. キャッチコピー
    sb.add_text(slide_id, content["tagline"],
        text_x, 1.280, 9.354 - text_x + 0.323, 0.280,
        font_size=14, color=C.textSecondary,
        alignment="START", valign="TOP")

    # 5. 主要機能（Icon+Text Row パターン）
    features = content["keyFeatures"]
    sb.add_icon_text_row(slide_id, 0.500, 2.000, [
        {
            "icon": f.get("icon", str(i + 1)),
            "title": f["name"],
            "desc": f["description"],
            "color": C.primary,
        }
        for i, f in enumerate(features)
    ], icon_r=0.20)
```

---

## 2. architecture — システムアーキテクチャ図

### マスター・パターン

- **マスター**: CONTENT（フッター付き）
- **パターン**: Pattern 10/11 (Flow / Decision Flow)

### レイアウト

```
┌──────────────────────────────────────────┐
│ [アクションタイトル]                         │ 0.303"
├──────────────────────────────────────────┤ 0.787"
│                                          │
│  ┌──────────────── Layer 1 ─────────────┐│
│  │ [comp]  [comp]  [comp]               ││
│  └──────────────────────────────────────┘│
│       │         │         │              │
│       ▼         ▼         ▼              │
│  ┌──────────────── Layer 2 ─────────────┐│
│  │ [comp]  [comp]                       ││
│  └──────────────────────────────────────┘│
│       │         │                        │
│       ▼         ▼                        │
│  ┌──────────────── Layer 3 ─────────────┐│
│  │ [comp]  [comp]  [comp]               ││
│  └──────────────────────────────────────┘│
│                                          │
├──────────────────────────────────────────┤
│  [フッター]                                │ 5.208"
└──────────────────────────────────────────┘
```

### カラーコーディング

| コンポーネントタイプ | 色 | 用途 |
|---------------------|-----|------|
| `scalar` | `C.primary` (Blue) | Scalar 製品コンポーネント |
| `external` | `C.textMuted` (Gray) | 外部・既存コンポーネント |
| `client` | `C.warning` (Orange) | ユーザー・クライアントアプリ |
| 正常フロー (solid) | `C.success` (Green) | 正常データフロー |
| エラーパス (solid) | `C.error` (Red) | 障害・エラーパス |
| オプション境界 (dashed) | `C.border` | 任意の境界線 |

### 座標定数

| 要素 | X | Y | W | H |
|------|-----|-----|------|------|
| タイトル | 0.323 | 0.303 | 9.354 | 0.437 |
| body 領域 | 0.500 | 0.787 | 9.000 | 4.421 |
| レイヤーラベル幅 | — | — | 9.000 | 0.250 |
| コンポーネントボックス | — | — | 1.400 | 0.500 |

### コード

```python
def compose_architecture(sb, slide_id, content, theme, page_num, total_pages=None):
    """アーキテクチャ図スライドを構築する。

    content: {
        title,
        layers: [{name, components: [{name, type, icon}]}],
        connections: [{from, to, label, style}]
    }
    """
    apply_master_content(sb, theme, slide_id, page_num, total_pages)
    apply_action_title(sb, theme, slide_id, content["title"])

    # カラーマッピング
    type_colors = {
        "scalar":   C.primary,
        "external": C.textMuted,
        "client":   C.warning,
    }

    layers = content["layers"]
    n_layers = len(layers)
    body_top = 0.787
    body_h = 4.421
    layer_gap = 0.15
    layer_h = (body_h - layer_gap * (n_layers - 1)) / n_layers
    comp_h = 0.500
    comp_gap = 0.25

    # コンポーネント位置を記録（コネクタ用）
    comp_positions = {}

    for li, layer in enumerate(layers):
        ly = body_top + li * (layer_h + layer_gap)
        comps = layer["components"]
        n_comps = len(comps)

        # レイヤー背景（薄い矩形）
        sb.add_rounded_rect(slide_id, 0.500, ly, 9.000, layer_h,
            fill=C.surfaceLight, border_color=C.border)

        # レイヤーラベル（左上）
        sb.add_text(slide_id, layer["name"],
            0.600, ly + 0.05, 2.000, 0.250,
            font_size=10, bold=True, color=C.textMuted,
            alignment="START", valign="MIDDLE")

        # コンポーネント配置（レイヤー内中央に均等配置）
        comp_w = min(1.400, (8.500 - comp_gap * (n_comps - 1)) / n_comps)
        total_w = comp_w * n_comps + comp_gap * (n_comps - 1)
        start_x = 0.500 + (9.000 - total_w) / 2
        comp_y = ly + 0.350  # レイヤーラベルの下

        for ci, comp in enumerate(comps):
            cx = start_x + ci * (comp_w + comp_gap)
            fill = type_colors.get(comp.get("type", "scalar"), C.primary)

            # クラウドアイコン（オプション）
            if comp.get("icon"):
                sb.add_image_from_asset(slide_id, "shared", "cloud-icons",
                    comp["icon"],
                    cx + comp_w / 2 - 0.15, comp_y - 0.05, 0.30, 0.30)

            # コンポーネントボックス
            sb.add_shape(slide_id, "ROUND_RECTANGLE",
                cx, comp_y, comp_w, comp_h, fill=fill)
            sb.add_text(slide_id, comp["name"],
                cx, comp_y, comp_w, comp_h,
                font_size=11, bold=True,
                color={"red": 1, "green": 1, "blue": 1},
                alignment="CENTER", valign="MIDDLE")

            # 位置記録
            comp_positions[comp["name"]] = {
                "x": cx, "y": comp_y,
                "w": comp_w, "h": comp_h,
                "cx": cx + comp_w / 2,
                "cy": comp_y + comp_h / 2,
            }

    # コネクタ
    for conn in content.get("connections", []):
        f = comp_positions.get(conn["from"])
        t = comp_positions.get(conn["to"])
        if not f or not t:
            continue
        style = conn.get("style", "solid")
        conn_color = C.success if style == "solid" else C.border
        dash_style = "DASH" if style == "dashed" else "SOLID"

        # 垂直方向が主（上→下レイヤー間）
        if abs(t["cy"] - f["cy"]) > abs(t["cx"] - f["cx"]):
            sx, sy = f["cx"], f["y"] + f["h"]
            ex, ey = t["cx"], t["y"]
        else:
            sx, sy = f["x"] + f["w"], f["cy"]
            ex, ey = t["x"], t["cy"]

        sb.add_connector(slide_id, sx, sy, ex, ey,
            color=conn_color, weight=1.5,
            end_arrow="FILL_ARROW",
            dash_style=dash_style)

        if conn.get("label"):
            mx, my = (sx + ex) / 2, (sy + ey) / 2
            sb.add_text(slide_id, conn["label"],
                mx - 0.4, my - 0.12, 0.8, 0.25,
                font_size=9, color=C.textSecondary,
                alignment="CENTER", valign="MIDDLE")
```

---

## 3. feature_matrix — 機能比較マトリクス

### マスター・パターン

- **マスター**: CONTENT（フッター付き）
- **パターン**: Table 拡張（チェックマーク / バツマーク付き）

### レイアウト

```
┌──────────────────────────────────────────┐
│ [アクションタイトル]                         │ 0.303"
├──────────────────────────────────────────┤ 0.787"
│                                          │
│  機能＼製品     │ ScalarDB │ 製品B │ 製品C │
│  ──────────────┼──────────┼──────┼──────│
│  機能1          │   ✓      │  ✓   │  △   │
│  機能2          │   ✓      │  ×   │  ✓   │
│  機能3          │   ✓      │  ✓   │  ×   │
│  ...           │          │      │      │
│                                          │
├──────────────────────────────────────────┤
│  [フッター]                                │ 5.208"
└──────────────────────────────────────────┘
```

### 座標定数

| 要素 | X | Y | W | H |
|------|-----|-----|------|------|
| タイトル | 0.323 | 0.303 | 9.354 | 0.437 |
| テーブル | 0.500 | 0.900 | 9.000 | 動的 |
| ヘッダー行高 | — | — | — | 0.400 |
| データ行高 | — | — | — | 0.350 |
| 機能名列幅 | — | — | 2.500 | — |

### コード

```python
def compose_feature_matrix(sb, slide_id, content, theme, page_num, total_pages=None):
    """機能比較マトリクスを構築する。

    content: {
        title,
        features: [str],
        products: [{name, values: ["yes"|"no"|"partial"|str]}]
    }
    """
    apply_master_content(sb, theme, slide_id, page_num, total_pages)
    apply_action_title(sb, theme, slide_id, content["title"])

    features = content["features"]
    products = content["products"]
    n_features = len(features)
    n_products = len(products)

    # テーブル寸法
    table_x = 0.500
    table_y = 0.900
    table_w = 9.000
    header_h = 0.400
    row_h = 0.350
    feature_col_w = 2.500
    product_col_w = (table_w - feature_col_w) / n_products

    # 値→表示文字のマッピング
    value_map = {
        "yes": ("✓", C.success),
        "no": ("✗", C.error),
        "partial": ("△", C.warning),
    }

    # ヘッダー行背景
    sb.add_rect(slide_id, table_x, table_y, table_w, header_h,
        fill=C.primary)

    # ヘッダー: 機能列
    sb.add_text(slide_id, "機能",
        table_x, table_y, feature_col_w, header_h,
        font_size=12, bold=True,
        color={"red": 1, "green": 1, "blue": 1},
        alignment="CENTER", valign="MIDDLE")

    # ヘッダー: 製品列
    for pi, product in enumerate(products):
        px = table_x + feature_col_w + pi * product_col_w
        sb.add_text(slide_id, product["name"],
            px, table_y, product_col_w, header_h,
            font_size=12, bold=True,
            color={"red": 1, "green": 1, "blue": 1},
            alignment="CENTER", valign="MIDDLE")

    # データ行
    for fi, feature in enumerate(features):
        ry = table_y + header_h + fi * row_h
        row_bg = C.background if fi % 2 == 0 else C.surfaceLight

        # 行背景（ゼブラ）
        sb.add_rect(slide_id, table_x, ry, table_w, row_h, fill=row_bg)

        # 機能名
        sb.add_text(slide_id, feature,
            table_x + 0.100, ry, feature_col_w - 0.100, row_h,
            font_size=11, color=C.textPrimary,
            alignment="START", valign="MIDDLE")

        # 値セル
        for pi, product in enumerate(products):
            px = table_x + feature_col_w + pi * product_col_w
            raw_val = product["values"][fi] if fi < len(product["values"]) else ""
            display, color = value_map.get(raw_val, (raw_val, C.textPrimary))

            sb.add_text(slide_id, display,
                px, ry, product_col_w, row_h,
                font_size=14 if raw_val in value_map else 11,
                bold=raw_val in value_map,
                color=color,
                alignment="CENTER", valign="MIDDLE")

    # 自社製品列のハイライト（isOurs フラグに相当する列を強調）
    for pi, product in enumerate(products):
        if product.get("isOurs"):
            px = table_x + feature_col_w + pi * product_col_w
            total_h = header_h + n_features * row_h
            sb.add_rect(slide_id, px, table_y, product_col_w, total_h,
                fill=None, border_color=C.primary, border_weight=2.5)
```

---

## 4. feature_detail — 個別機能の詳細説明

### マスター・パターン

- **マスター**: CONTENT（フッター付き）
- **パターン**: Pattern 7 (Icon+Text Row) — 左テキスト + 右図のレイアウト

### レイアウト

```
┌──────────────────────────────────────────┐
│ [アクションタイトル]                         │ 0.303"
├───────────────────┬──────────────────────┤ 0.787"
│                   │                      │
│  機能名            │   ┌──────────────┐   │
│  ──────            │   │              │   │
│  説明テキスト       │   │  図/アセット   │   │
│                   │   │              │   │
│  ✓ メリット1       │   └──────────────┘   │
│  ✓ メリット2       │                      │
│  ✓ メリット3       │                      │
│                   │                      │
│  技術詳細(opt)     │                      │
│                   │                      │
├───────────────────┴──────────────────────┤
│  [フッター]                                │ 5.208"
└──────────────────────────────────────────┘
```

### 座標定数

| 要素 | X | Y | W | H |
|------|-----|-----|------|------|
| タイトル | 0.323 | 0.303 | 9.354 | 0.437 |
| 左パネル | 0.500 | 0.787 | 4.200 | 4.421 |
| 右パネル（図） | 5.000 | 1.000 | 4.500 | 3.500 |
| 機能名 | 0.500 | 0.850 | 4.200 | 0.350 |
| 説明テキスト | 0.500 | 1.250 | 4.200 | 0.800 |
| メリット開始Y | — | 2.150 | 4.200 | — |
| 技術詳細Y | — | 3.800 | 4.200 | 1.000 |

### コード

```python
def compose_feature_detail(sb, slide_id, content, theme, page_num, total_pages=None):
    """個別機能の詳細スライドを構築する。

    content: {
        title, featureName, description,
        benefits: [str],
        technicalDetail (opt), diagram (opt)
    }
    """
    apply_master_content(sb, theme, slide_id, page_num, total_pages)
    apply_action_title(sb, theme, slide_id, content["title"])

    has_diagram = bool(content.get("diagram"))
    text_w = 4.200 if has_diagram else 9.000

    # 機能名（サブヘッダー）
    sb.add_text(slide_id, content["featureName"],
        0.500, 0.850, text_w, 0.350,
        font_size=20, bold=True, color=C.primary,
        alignment="START", valign="MIDDLE")

    # セパレーター
    sb.add_rect(slide_id, 0.500, 1.220, min(text_w, 2.000), 0.025,
        fill=C.primary)

    # 説明テキスト
    sb.add_text(slide_id, content["description"],
        0.500, 1.300, text_w, 0.800,
        font_size=13, color=C.textPrimary,
        alignment="START", valign="TOP")

    # メリット（箇条書き）
    benefits = content.get("benefits", [])
    bullet_y = 2.200
    for i, benefit in enumerate(benefits):
        by = bullet_y + i * 0.350
        # チェックマークバッジ
        sb.add_badge(slide_id, 0.620, by + 0.130, 0.10,
            "✓", fill=C.success,
            text_color={"red": 1, "green": 1, "blue": 1})
        # テキスト
        sb.add_text(slide_id, benefit,
            0.800, by, text_w - 0.300, 0.320,
            font_size=12, color=C.textPrimary,
            alignment="START", valign="MIDDLE")

    # 技術詳細（オプション）
    if content.get("technicalDetail"):
        tech_y = bullet_y + len(benefits) * 0.350 + 0.200
        sb.add_rounded_rect(slide_id, 0.500, tech_y, text_w, 0.900,
            fill=C.surfaceLight, border_color=C.border)
        sb.add_text(slide_id, content["technicalDetail"],
            0.600, tech_y + 0.050, text_w - 0.200, 0.800,
            font_size=11, color=C.textSecondary,
            alignment="START", valign="TOP")

    # 図（オプション）
    if has_diagram:
        sb.add_image_from_asset(slide_id, theme["name"], "icons",
            content["diagram"],
            5.000, 1.000, 4.500, 3.500)
```

---

## 5. tech_specs — 技術仕様・スペック一覧

### マスター・パターン

- **マスター**: CONTENT（フッター付き）
- **パターン**: Table 拡張（カテゴリごとにグルーピング）

### レイアウト

```
┌──────────────────────────────────────────┐
│ [アクションタイトル]                         │ 0.303"
├──────────────────────────────────────────┤ 0.787"
│                                          │
│  ▸ カテゴリ A                              │
│  ┌──────────────┬───────────────────────┐│
│  │ 項目1         │ 値1                   ││
│  │ 項目2         │ 値2                   ││
│  └──────────────┴───────────────────────┘│
│                                          │
│  ▸ カテゴリ B                              │
│  ┌──────────────┬───────────────────────┐│
│  │ 項目3         │ 値3                   ││
│  │ 項目4         │ 値4                   ││
│  └──────────────┴───────────────────────┘│
│                                          │
├──────────────────────────────────────────┤
│  [フッター]                                │ 5.208"
└──────────────────────────────────────────┘
```

### 座標定数

| 要素 | X | Y | W | H |
|------|-----|-----|------|------|
| タイトル | 0.323 | 0.303 | 9.354 | 0.437 |
| テーブル領域 | 0.500 | 0.850 | 9.000 | 動的 |
| カテゴリヘッダー高 | — | — | — | 0.300 |
| データ行高 | — | — | — | 0.300 |
| 項目名列幅 | — | — | 3.000 | — |
| 値列幅 | — | — | 6.000 | — |

### コード

```python
def compose_tech_specs(sb, slide_id, content, theme, page_num, total_pages=None):
    """技術仕様スライドを構築する。

    content: {
        title,
        categories: [{name, specs: [{item, value}]}]
    }
    """
    apply_master_content(sb, theme, slide_id, page_num, total_pages)
    apply_action_title(sb, theme, slide_id, content["title"])

    table_x = 0.500
    table_w = 9.000
    item_col_w = 3.000
    value_col_w = table_w - item_col_w
    cat_h = 0.300
    row_h = 0.300
    current_y = 0.850

    for cat in content["categories"]:
        # カテゴリヘッダー
        sb.add_rect(slide_id, table_x, current_y, table_w, cat_h,
            fill=C.primary)
        sb.add_text(slide_id, cat["name"],
            table_x + 0.150, current_y, table_w - 0.300, cat_h,
            font_size=12, bold=True,
            color={"red": 1, "green": 1, "blue": 1},
            alignment="START", valign="MIDDLE")
        current_y += cat_h

        # スペック行
        for si, spec in enumerate(cat["specs"]):
            row_bg = C.background if si % 2 == 0 else C.surfaceLight
            sb.add_rect(slide_id, table_x, current_y, table_w, row_h,
                fill=row_bg)

            # 項目名
            sb.add_text(slide_id, spec["item"],
                table_x + 0.150, current_y, item_col_w - 0.150, row_h,
                font_size=11, bold=True, color=C.textTitle,
                alignment="START", valign="MIDDLE")

            # 値
            sb.add_text(slide_id, spec["value"],
                table_x + item_col_w, current_y, value_col_w - 0.100, row_h,
                font_size=11, color=C.textPrimary,
                alignment="START", valign="MIDDLE")

            current_y += row_h

        # カテゴリ間スペース
        current_y += 0.100
```

---

## 6. competitive_compare — 競合比較表

### マスター・パターン

- **マスター**: CONTENT（フッター付き）
- **パターン**: Pattern 9 (Comparison) — 表形式の拡張版

### レイアウト

```
┌──────────────────────────────────────────┐
│ [アクションタイトル]                         │ 0.303"
├──────────────────────────────────────────┤ 0.787"
│                                          │
│  比較軸＼      │ ★自社    │ 競合A  │ 競合B │
│  ──────────────┼─────────┼───────┼──────│
│  軸1           │ ████    │ ██    │ █    │
│  軸2           │ ████    │ ███   │ ███  │
│  軸3           │ ████    │ █     │ ██   │
│  ...          │         │       │      │
│                                          │
│  ★ = 自社製品（ハイライト列）                 │
│                                          │
├──────────────────────────────────────────┤
│  [フッター]                                │ 5.208"
└──────────────────────────────────────────┘
```

### 座標定数

| 要素 | X | Y | W | H |
|------|-----|-----|------|------|
| タイトル | 0.323 | 0.303 | 9.354 | 0.437 |
| テーブル | 0.500 | 0.900 | 9.000 | 動的 |
| ヘッダー行高 | — | — | — | 0.400 |
| データ行高 | — | — | — | 0.380 |
| 軸名列幅 | — | — | 2.200 | — |

### コード

```python
def compose_competitive_compare(sb, slide_id, content, theme, page_num, total_pages=None):
    """競合比較スライドを構築する。

    content: {
        title,
        dimensions: [str],
        competitors: [{name, isOurs (opt), values: [str]}]
    }
    """
    apply_master_content(sb, theme, slide_id, page_num, total_pages)
    apply_action_title(sb, theme, slide_id, content["title"])

    dims = content["dimensions"]
    comps = content["competitors"]
    n_dims = len(dims)
    n_comps = len(comps)

    table_x = 0.500
    table_y = 0.900
    table_w = 9.000
    header_h = 0.400
    row_h = 0.380
    dim_col_w = 2.200
    comp_col_w = (table_w - dim_col_w) / n_comps

    # ヘッダー行
    sb.add_rect(slide_id, table_x, table_y, table_w, header_h,
        fill=C.primary)

    # 比較軸ラベル
    sb.add_text(slide_id, "",
        table_x, table_y, dim_col_w, header_h,
        font_size=12, bold=True,
        color={"red": 1, "green": 1, "blue": 1},
        alignment="CENTER", valign="MIDDLE")

    # 競合ヘッダー
    for ci, comp in enumerate(comps):
        cx = table_x + dim_col_w + ci * comp_col_w
        label = f"★ {comp['name']}" if comp.get("isOurs") else comp["name"]
        sb.add_text(slide_id, label,
            cx, table_y, comp_col_w, header_h,
            font_size=12, bold=True,
            color={"red": 1, "green": 1, "blue": 1},
            alignment="CENTER", valign="MIDDLE")

    # データ行
    for di, dim in enumerate(dims):
        ry = table_y + header_h + di * row_h
        row_bg = C.background if di % 2 == 0 else C.surfaceLight

        sb.add_rect(slide_id, table_x, ry, table_w, row_h, fill=row_bg)

        # 軸名
        sb.add_text(slide_id, dim,
            table_x + 0.100, ry, dim_col_w - 0.100, row_h,
            font_size=11, bold=True, color=C.textTitle,
            alignment="START", valign="MIDDLE")

        # 各競合の値
        for ci, comp in enumerate(comps):
            cx = table_x + dim_col_w + ci * comp_col_w
            val = comp["values"][di] if di < len(comp["values"]) else ""
            text_color = C.primary if comp.get("isOurs") else C.textPrimary

            sb.add_text(slide_id, val,
                cx, ry, comp_col_w, row_h,
                font_size=11, color=text_color,
                bold=comp.get("isOurs", False),
                alignment="CENTER", valign="MIDDLE")

    # 自社列のハイライト枠
    for ci, comp in enumerate(comps):
        if comp.get("isOurs"):
            cx = table_x + dim_col_w + ci * comp_col_w
            total_h = header_h + n_dims * row_h
            sb.add_rect(slide_id, cx, table_y, comp_col_w, total_h,
                fill=None, border_color=C.primary, border_weight=2.5)
```

---

## 7. roadmap — 製品ロードマップ・タイムライン

### マスター・パターン

- **マスター**: CONTENT（フッター付き）
- **パターン**: Pattern 2 (H-Timeline)

### レイアウト

```
┌──────────────────────────────────────────┐
│ [アクションタイトル]                         │ 0.303"
├──────────────────────────────────────────┤ 0.787"
│                                          │
│       Q1 2025        Q3 2025             │
│  ───────●──────────────●─────────────    │
│         │              │                 │
│    ┌────┴────┐    ┌────┴────┐            │
│    │ Feature │    │ Feature │            │
│    │ 説明    │    │ 説明    │            │
│    └─────────┘    └─────────┘            │
│                                          │
│  ● completed  ○ in_progress  ◦ planned   │
│                                          │
├──────────────────────────────────────────┤
│  [フッター]                                │ 5.208"
└──────────────────────────────────────────┘
```

### ステータスの視覚表現

| ステータス | マーカー色 | カード背景 |
|-----------|----------|----------|
| `completed` | `C.success` | `C.surfaceLight` |
| `in_progress` | `C.primary` | `C.background` (白枠付き) |
| `planned` | `C.textMuted` | `C.background` (破線枠) |

### 座標定数

| 要素 | X | Y | W | H |
|------|-----|-----|------|------|
| タイトル | 0.323 | 0.303 | 9.354 | 0.437 |
| タイムライン軸 | 0.700 | 2.200 | 8.600 | — |
| カード幅 | — | — | 1.500 | 1.200 |
| 凡例Y | — | 4.700 | — | — |

### コード

```python
def compose_roadmap(sb, slide_id, content, theme, page_num, total_pages=None):
    """ロードマップスライドを構築する。

    content: {
        title,
        milestones: [{date, title, description (opt), status (opt)}]
    }
    """
    apply_master_content(sb, theme, slide_id, page_num, total_pages)
    apply_action_title(sb, theme, slide_id, content["title"])

    milestones = content["milestones"]
    n = len(milestones)

    # ステータス色マッピング
    status_colors = {
        "completed":   C.success,
        "in_progress": C.primary,
        "planned":     C.textMuted,
    }

    # タイムライン軸
    timeline_x = 0.700
    timeline_w = 8.600
    timeline_y = 2.200

    # タイムラインイベントを作成
    events = [{"label": m["date"], "sublabel": m.get("title", "")}
              for m in milestones]

    # マーカー色を個別設定するため、自前で描画
    # メインの水平線
    sb.add_line(slide_id, timeline_x, timeline_y, timeline_w,
        color=C.border, weight=2.5)

    card_w = min(1.500, (timeline_w * 0.85) / max(n, 1))
    card_h = 1.200

    for i, ms in enumerate(milestones):
        status = ms.get("status", "planned")
        marker_color = status_colors.get(status, C.textMuted)
        ex = timeline_x + (timeline_w / (n - 1)) * i if n > 1 else timeline_x + timeline_w / 2

        # マーカー円
        sb.add_circle(slide_id, ex, timeline_y, 0.12, fill=marker_color)

        # 日付ラベル（上下交互）
        if i % 2 == 0:
            date_y = timeline_y - 0.45
            card_y = timeline_y + 0.30
        else:
            date_y = timeline_y + 0.20
            card_y = timeline_y - card_h - 0.30

        sb.add_text(slide_id, ms["date"],
            ex - card_w / 2, date_y, card_w, 0.30,
            font_size=11, bold=True, color=marker_color,
            alignment="CENTER", valign="MIDDLE")

        # マイルストーンカード
        card_bg = C.surfaceLight if status == "completed" else C.background
        border_style = "DASH" if status == "planned" else "SOLID"
        sb.add_rounded_rect(slide_id, ex - card_w / 2, card_y, card_w, card_h,
            fill=card_bg, border_color=marker_color)

        # カード内タイトル
        sb.add_text(slide_id, ms["title"],
            ex - card_w / 2 + 0.08, card_y + 0.08, card_w - 0.16, 0.300,
            font_size=11, bold=True, color=C.textTitle,
            alignment="START", valign="TOP")

        # カード内説明（オプション）
        if ms.get("description"):
            sb.add_text(slide_id, ms["description"],
                ex - card_w / 2 + 0.08, card_y + 0.400, card_w - 0.16, card_h - 0.480,
                font_size=10, color=C.textSecondary,
                alignment="START", valign="TOP")

    # 凡例
    legend_y = 4.700
    legend_items = [
        ("●", "completed", C.success),
        ("●", "in_progress", C.primary),
        ("○", "planned", C.textMuted),
    ]
    legend_x = 0.700
    for li, (marker, label, color) in enumerate(legend_items):
        lx = legend_x + li * 2.200
        sb.add_text(slide_id, f"{marker} {label}",
            lx, legend_y, 2.000, 0.250,
            font_size=10, color=color,
            alignment="START", valign="MIDDLE")
```

---

## 共通注意事項

### テキスト制約

| フィールド | 日本語上限 | 英語上限 |
|-----------|----------|---------|
| アクションタイトル | 50文字 | 100文字 |
| 機能名 | 20文字 | 40文字 |
| 箇条書き1項目 | 40文字 | 80文字 |
| KPI値 | 簡潔（数文字） | 同左 |
| スピーカーノート | 200文字 | 400文字 |

### カラー運用

- アーキテクチャ図のカラーコーディングは必ず凡例で説明すること
- 競合比較表では自社製品列を `C.primary` でハイライト
- ロードマップのステータスは3色（緑/青/グレー）で統一
- 1スライド最大3色（60-30-10 ルール）。テーブル系は行ゼブラ＋ヘッダー色で3色を消費するため追加アクセントは最小限に

### アクションタイトル例

| NG（ラベル型） | OK（アクションタイトル） |
|:-------------:|:--------------------:|
| 「製品概要」 | 「ScalarDB は異種DB間のACIDトランザクションを統一するミドルウェアである」 |
| 「アーキテクチャ」 | 「3層分離アーキテクチャが既存DBを無変更で統合する」 |
| 「機能比較」 | 「ScalarDB は全6機能を網羅し競合に対し圧倒的優位を持つ」 |
| 「技術仕様」 | 「P99レイテンシ5ms未満を実現する低オーバーヘッド設計」 |
| 「競合比較」 | 「4つの評価軸すべてで競合を上回る唯一の製品」 |
| 「ロードマップ」 | 「2026年内にマルチリージョン対応を完了し市場優位を確立する」 |
