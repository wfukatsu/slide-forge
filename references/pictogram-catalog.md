*[日本語](pictogram-catalog.ja.md)*
# Pictogram Catalog

> A collection of pictogram patterns built from Google Slides API shapes + text.
> Create icon-like elements on slides without needing external images.

### Conventions

Identifiers used in this document:

- **`C`** — the color constant class expanded from the `colors` section of `templates/<theme>/theme.json`
- **`L`** — the layout constant class expanded from the `layouts` section of `templates/<theme>/theme.json`
- **`sb`** / **`self`** — a `SlideBuilder` instance (patterns are implemented as `SlideBuilder` methods)

---

## 1. Overview

### 1.1 What are pictograms?

Instead of image icons, the Google Slides API lets you combine shapes (141 types) to build icon-like visual elements.

Benefits:

- **No external images required** — no Drive API upload needed; everything is done via `batchUpdate` alone
- **Automatically adapts to theme colors** — colors are specified with semantic colors such as `C.primary`, so they update automatically on theme switch
- **No quality loss when resized** — since these are vector shapes, quality is preserved when scaled up or down
- **Can be grouped for combined move/rotate** — `group_objects()` lets you operate on them as one unit
- **Text can be embedded** — placing text inside a shape lets you build labeled icons

### 1.2 Construction patterns

There are three construction patterns:

| Pattern | Description | Complexity | Examples |
|----------|------|--------|-----|
| **Single shape** | Expressed with just one shape | Low | CLOUD, CAN, SHIELD |
| **Shape + text** | Text placed inside a shape | Medium | Badges, labeled icons |
| **Composite shape** | Multiple shapes combined and grouped | High | Server, lock, user |

**Principle**: Express with a single shape whenever possible. Composite pictograms with 3 or more shapes become too complex, so consider using an external image instead.

> **When using an external image, the first choice is the pictogram library under `assets/scalar/pictograms/`**
> (62 Scalar-branded pictograms). It can be tinted with theme colors and pasted in. See `references/icons.md`
> for usage. Business vocabulary such as "information bank," "evidence chain," or "job offer" cannot be
> drawn with shapes, so use the icon library from the start for those. Just be aware this involves
> communication via Drive.

### 1.3 Common helper

The signature shared by all pictogram functions:

```python
def add_pictogram(self, slide_id, picto_type, x, y, size, color=None, label=None):
    """ピクトグラムを配置する共通ディスパッチ関数。

    Args:
        slide_id: スライドID
        picto_type: ピクトグラムタイプ名（例: "database", "cloud", "shield"）
        x, y: 位置（インチ）
        size: サイズ（インチ、正方形ベース）
        color: RGB dict（省略時はテーマのデフォルトカラーを使用）
        label: テキストラベル（省略可）
    Returns:
        shape_id or group_id
    """
    fn = PICTO_REGISTRY.get(picto_type)
    if not fn:
        raise ValueError(f"Unknown pictogram type: {picto_type}")
    return fn(self, slide_id, x, y, size, color=color, label=label)
```

### 1.4 Registry

```python
PICTO_REGISTRY = {
    # データベース・ストレージ
    "database":       picto_database,
    "storage":        picto_storage,
    "document":       picto_document,
    "multi_document": picto_multi_document,
    "cache":          picto_cache,
    # クラウド・ネットワーク
    "cloud":          picto_cloud,
    "cloud_callout":  picto_cloud_callout,
    "network":        picto_network,
    "server":         picto_server,
    "load_balancer":  picto_load_balancer,
    "firewall":       picto_firewall,
    # セキュリティ
    "shield":         picto_shield,
    "lock":           picto_lock,
    "key":            picto_key,
    "check_circle":   picto_check_circle,
    "warning":        picto_warning,
    "ban":            picto_ban,
    # プロセス・フロー
    "process":        picto_process,
    "decision":       picto_decision,
    "start_end":      picto_start_end,
    "manual_input":   picto_manual_input,
    "connector":      picto_connector,
    "preparation":    picto_preparation,
    # ビジネス・ユーザー
    "user":           picto_user,
    "team":           picto_team,
    "building":       picto_building,
    "handshake":      picto_handshake,
    "money":          picto_money,
    "chart_up":       picto_chart_up,
    "target":         picto_target,
    # テクノロジー
    "api":            picto_api,
    "microservice":   picto_microservice,
    "container":      picto_container,
    "queue":          picto_queue,
    "gear":           picto_gear,
    "code":           picto_code,
    "terminal":       picto_terminal,
    # ステータス・インジケーター
    "success":        picto_success,
    "error":          picto_error,
    "info":           picto_info,
    "pending":        picto_pending,
    "star":           picto_star,
}
```

---

## 2. Pictograms by category

### 2.1 Database / storage

| Name | shapeType | Use | Recommended size | Pattern |
|------|-----------|------|----------|---------|
| `database` | `CAN` | Databases in general | 0.5" | Single |
| `storage` | `FLOW_CHART_MAGNETIC_DISK` | Storage / disk | 0.5" | Single |
| `document` | `FLOW_CHART_DOCUMENT` | Document / file | 0.5" | Single |
| `multi_document` | `FLOW_CHART_MULTIDOCUMENT` | Multiple files | 0.6" | Single |
| `cache` | `FLOW_CHART_INTERNAL_STORAGE` | Cache / memory | 0.5" | Single |

#### database — Database

```python
def picto_database(self, slide_id, x, y, size=0.5, color=None, label=None):
    """データベースピクトグラム。CAN（シリンダー）形状。"""
    c = color or C.primary
    w = size
    h = size * 1.2  # シリンダーは縦長
    shape_id = self.add_shape(slide_id, "CAN", x, y, w, h, fill=c)
    if label:
        self.add_text(slide_id, label,
                      x, y + h + 0.05, w, 0.20,
                      font_size=9, color=C.textSecondary,
                      alignment="CENTER", valign="TOP")
    return shape_id
```

#### storage — Storage

```python
def picto_storage(self, slide_id, x, y, size=0.5, color=None, label=None):
    """ストレージピクトグラム。磁気ディスク形状。"""
    c = color or C.primary
    shape_id = self.add_shape(slide_id, "FLOW_CHART_MAGNETIC_DISK",
                              x, y, size, size, fill=c)
    if label:
        self.add_text(slide_id, label,
                      x, y + size + 0.05, size, 0.20,
                      font_size=9, color=C.textSecondary,
                      alignment="CENTER", valign="TOP")
    return shape_id
```

#### document — Document

```python
def picto_document(self, slide_id, x, y, size=0.5, color=None, label=None):
    """ドキュメントピクトグラム。文書形状（波線底辺）。"""
    c = color or C.primary
    w = size * 0.85
    h = size
    shape_id = self.add_shape(slide_id, "FLOW_CHART_DOCUMENT",
                              x + (size - w) / 2, y, w, h, fill=c)
    if label:
        self.add_text(slide_id, label,
                      x, y + h + 0.05, size, 0.20,
                      font_size=9, color=C.textSecondary,
                      alignment="CENTER", valign="TOP")
    return shape_id
```

#### multi_document — Multiple documents

```python
def picto_multi_document(self, slide_id, x, y, size=0.6, color=None, label=None):
    """複数ドキュメントピクトグラム。"""
    c = color or C.primary
    shape_id = self.add_shape(slide_id, "FLOW_CHART_MULTIDOCUMENT",
                              x, y, size, size, fill=c)
    if label:
        self.add_text(slide_id, label,
                      x, y + size + 0.05, size, 0.20,
                      font_size=9, color=C.textSecondary,
                      alignment="CENTER", valign="TOP")
    return shape_id
```

#### cache — Cache

```python
def picto_cache(self, slide_id, x, y, size=0.5, color=None, label=None):
    """キャッシュ/内部ストレージピクトグラム。"""
    c = color or C.accent
    shape_id = self.add_shape(slide_id, "FLOW_CHART_INTERNAL_STORAGE",
                              x, y, size, size, fill=c)
    if label:
        self.add_text(slide_id, label,
                      x, y + size + 0.05, size, 0.20,
                      font_size=9, color=C.textSecondary,
                      alignment="CENTER", valign="TOP")
    return shape_id
```

---

### 2.2 Cloud / network

| Name | shapeType | Use | Recommended size | Pattern |
|------|-----------|------|----------|---------|
| `cloud` | `CLOUD` | Cloud services | 0.6" | Single |
| `cloud_callout` | `CLOUD_CALLOUT` | Cloud annotation | 0.6" | Single |
| `network` | `HEXAGON` | Network / node | 0.5" | Shape + text |
| `server` | `RECTANGLE` + `RECTANGLE` | Server | 0.5" | Composite |
| `load_balancer` | `TRAPEZOID` | Load balancer | 0.6" | Single |
| `firewall` | `RECTANGLE` + `LIGHTNING_BOLT` | Firewall | 0.6" | Composite |

#### cloud — Cloud

```python
def picto_cloud(self, slide_id, x, y, size=0.6, color=None, label=None):
    """クラウドピクトグラム。"""
    c = color or C.primary
    w = size * 1.3  # 雲は横長
    h = size
    shape_id = self.add_shape(slide_id, "CLOUD", x, y, w, h, fill=c)
    if label:
        self.add_text(slide_id, label,
                      x, y + h + 0.05, w, 0.20,
                      font_size=9, color=C.textSecondary,
                      alignment="CENTER", valign="TOP")
    return shape_id
```

#### cloud_callout — Cloud callout

```python
def picto_cloud_callout(self, slide_id, x, y, size=0.6, color=None, label=None):
    """クラウド吹出しピクトグラム。アノテーション用。"""
    c = color or C.calloutBg
    bc = C.calloutBorder
    w = size * 1.3
    h = size
    shape_id = self.add_shape(slide_id, "CLOUD_CALLOUT", x, y, w, h,
                              fill=c, border_color=bc, border_weight=1.5)
    if label:
        # 雲の内部にテキストを配置
        self.add_text(slide_id, label,
                      x + w * 0.15, y + h * 0.15, w * 0.7, h * 0.5,
                      font_size=8, color=C.textPrimary,
                      alignment="CENTER", valign="MIDDLE")
    return shape_id
```

#### network — Network node

```python
def picto_network(self, slide_id, x, y, size=0.5, color=None, label=None):
    """ネットワークノードピクトグラム。六角形。"""
    c = color or C.primary
    shape_id = self.add_shape(slide_id, "HEXAGON", x, y, size, size, fill=c)
    if label:
        self.add_text(slide_id, label,
                      x, y + size + 0.05, size, 0.20,
                      font_size=9, color=C.textSecondary,
                      alignment="CENTER", valign="TOP")
    return shape_id
```

#### server — Server (composite)

```python
def picto_server(self, slide_id, x, y, size=0.5, color=None, label=None):
    """サーバーピクトグラム（複合）。
    矩形の本体 + 内部の小さな矩形（ディスクベイ表現）。
    """
    c = color or C.textMuted
    w = size
    h = size * 1.3
    # 本体
    body_id = self.add_shape(slide_id, "ROUND_RECTANGLE", x, y, w, h,
                             fill=c, border_color=c)
    # ディスクベイ（横線3本）
    line_ids = []
    line_h = 0.03
    line_w = w * 0.6
    lx = x + (w - line_w) / 2
    for i in range(3):
        ly = y + h * 0.2 + i * (h * 0.22)
        lid = self.add_shape(slide_id, "RECTANGLE", lx, ly, line_w, line_h,
                             fill=C.background)
        line_ids.append(lid)
    # LED インジケーター（小さな円）
    led_r = size * 0.06
    led_id = self.add_circle(slide_id, x + w * 0.8, y + h * 0.85,
                             led_r, fill=C.success)
    # グループ化
    all_ids = [body_id] + line_ids + [led_id]
    group_id = self.group_objects(all_ids)
    if label:
        self.add_text(slide_id, label,
                      x, y + h + 0.05, w, 0.20,
                      font_size=9, color=C.textSecondary,
                      alignment="CENTER", valign="TOP")
    return group_id
```

#### load_balancer — Load balancer

```python
def picto_load_balancer(self, slide_id, x, y, size=0.6, color=None, label=None):
    """ロードバランサーピクトグラム。台形（上辺が広い）。"""
    c = color or C.accent
    w = size * 1.2
    h = size * 0.8
    shape_id = self.add_shape(slide_id, "TRAPEZOID", x, y, w, h, fill=c)
    if label:
        self.add_text(slide_id, label,
                      x, y + h + 0.05, w, 0.20,
                      font_size=9, color=C.textSecondary,
                      alignment="CENTER", valign="TOP")
    return shape_id
```

#### firewall — Firewall (composite)

```python
def picto_firewall(self, slide_id, x, y, size=0.6, color=None, label=None):
    """ファイアウォールピクトグラム（複合）。
    矩形（壁）＋ 稲妻（ブロック表現）。
    """
    c = color or C.alertRed
    w = size
    h = size * 0.8
    # 壁（矩形、ストライプ風に border のみ）
    wall_id = self.add_shape(slide_id, "RECTANGLE", x, y, w, h,
                             fill=C.surfaceLight, border_color=c, border_weight=2.0)
    # 稲妻マーク（中央に小さく配置）
    bolt_size = size * 0.35
    bolt_x = x + (w - bolt_size) / 2
    bolt_y = y + (h - bolt_size * 1.2) / 2
    bolt_id = self.add_shape(slide_id, "LIGHTNING_BOLT",
                             bolt_x, bolt_y, bolt_size, bolt_size * 1.2,
                             fill=c)
    group_id = self.group_objects([wall_id, bolt_id])
    if label:
        self.add_text(slide_id, label,
                      x, y + h + 0.05, w, 0.20,
                      font_size=9, color=C.textSecondary,
                      alignment="CENTER", valign="TOP")
    return group_id
```

---

### 2.3 Security

| Name | shapeType | Use | Recommended size | Pattern |
|------|-----------|------|----------|---------|
| `shield` | `PENTAGON` | Security / protection | 0.5" | Single |
| `lock` | `ROUND_RECTANGLE` + `RECTANGLE` | Authentication / encryption | 0.5" | Composite |
| `key` | `PLUS` + `RECTANGLE` | Access key / credential | 0.5" | Composite |
| `check_circle` | `ELLIPSE` + text "✓" | Verified / passed | 0.4" | Shape + text |
| `warning` | `TRIANGLE` + text "!" | Warning / caution | 0.4" | Shape + text |
| `ban` | `NO_SMOKING` | Prohibited / deprecated | 0.4" | Single |

#### shield — Shield

```python
def picto_shield(self, slide_id, x, y, size=0.5, color=None, label=None):
    """シールドピクトグラム。五角形で盾を表現。"""
    c = color or C.primary
    w = size * 0.9
    h = size * 1.1
    shape_id = self.add_shape(slide_id, "PENTAGON",
                              x + (size - w) / 2, y, w, h, fill=c)
    if label:
        self.add_text(slide_id, label,
                      x, y + h + 0.05, size, 0.20,
                      font_size=9, color=C.textSecondary,
                      alignment="CENTER", valign="TOP")
    return shape_id
```

#### lock — Lock (composite)

```python
def picto_lock(self, slide_id, x, y, size=0.5, color=None, label=None):
    """ロックピクトグラム（複合）。
    上部: アーチ（角丸矩形、枠線のみ）= シャックル
    下部: 矩形 = ロック本体
    中央: 小さな円 = 鍵穴
    """
    c = color or C.primary
    w = size * 0.7
    # シャックル（上部のアーチ）
    shackle_w = w * 0.6
    shackle_h = size * 0.4
    shackle_x = x + (size - shackle_w) / 2
    shackle_y = y
    shackle_id = self.add_shape(slide_id, "ROUND_RECTANGLE",
                                shackle_x, shackle_y, shackle_w, shackle_h,
                                border_color=c, border_weight=2.5)
    # ロック本体
    body_w = w
    body_h = size * 0.55
    body_x = x + (size - body_w) / 2
    body_y = y + size * 0.35
    body_id = self.add_shape(slide_id, "ROUND_RECTANGLE",
                             body_x, body_y, body_w, body_h, fill=c)
    # 鍵穴（小さな円）
    hole_r = size * 0.06
    hole_id = self.add_circle(slide_id,
                              x + size / 2, body_y + body_h * 0.4,
                              hole_r, fill=C.background)
    group_id = self.group_objects([shackle_id, body_id, hole_id])
    if label:
        self.add_text(slide_id, label,
                      x, y + size + 0.05, size, 0.20,
                      font_size=9, color=C.textSecondary,
                      alignment="CENTER", valign="TOP")
    return group_id
```

#### key — Key

```python
def picto_key(self, slide_id, x, y, size=0.5, color=None, label=None):
    """鍵ピクトグラム（複合）。
    円（頭部）＋ 矩形（軸部）で鍵を表現。
    """
    c = color or C.cautionYellow
    # 頭部（円）
    head_r = size * 0.18
    head_id = self.add_circle(slide_id,
                              x + size * 0.25, y + size * 0.35,
                              head_r, fill=c, border_color=c)
    # 軸（横長矩形）
    shaft_w = size * 0.55
    shaft_h = size * 0.1
    shaft_x = x + size * 0.35
    shaft_y = y + size * 0.35 - shaft_h / 2
    shaft_id = self.add_shape(slide_id, "RECTANGLE",
                              shaft_x, shaft_y, shaft_w, shaft_h, fill=c)
    group_id = self.group_objects([head_id, shaft_id])
    if label:
        self.add_text(slide_id, label,
                      x, y + size + 0.05, size, 0.20,
                      font_size=9, color=C.textSecondary,
                      alignment="CENTER", valign="TOP")
    return group_id
```

#### check_circle — Verified

```python
def picto_check_circle(self, slide_id, x, y, size=0.4, color=None, label=None):
    """チェック済みピクトグラム（シェイプ＋テキスト）。
    円 + テキスト "✓"。
    """
    c = color or C.success
    shape_id = self.add_circle(slide_id,
                               x + size / 2, y + size / 2,
                               size / 2, fill=c)
    self.add_text(slide_id, "✓",
                  x, y, size, size,
                  font_size=int(size * 36), bold=True,
                  color=C.background,
                  alignment="CENTER", valign="MIDDLE")
    if label:
        self.add_text(slide_id, label,
                      x, y + size + 0.05, size, 0.20,
                      font_size=9, color=C.textSecondary,
                      alignment="CENTER", valign="TOP")
    return shape_id
```

#### warning — Warning

```python
def picto_warning(self, slide_id, x, y, size=0.4, color=None, label=None):
    """警告ピクトグラム（シェイプ＋テキスト）。
    三角形 + テキスト "!"。
    """
    c = color or C.cautionYellow
    w = size * 1.1
    h = size
    shape_id = self.add_shape(slide_id, "TRIANGLE",
                              x, y, w, h, fill=c)
    self.add_text(slide_id, "!",
                  x, y + h * 0.25, w, h * 0.6,
                  font_size=int(size * 32), bold=True,
                  color=C.background,
                  alignment="CENTER", valign="MIDDLE")
    if label:
        self.add_text(slide_id, label,
                      x, y + h + 0.05, w, 0.20,
                      font_size=9, color=C.textSecondary,
                      alignment="CENTER", valign="TOP")
    return shape_id
```

#### ban — Prohibited

```python
def picto_ban(self, slide_id, x, y, size=0.4, color=None, label=None):
    """禁止ピクトグラム。NO_SMOKING 形状。"""
    c = color or C.alertRed
    shape_id = self.add_shape(slide_id, "NO_SMOKING", x, y, size, size,
                              fill=c, border_color=c)
    if label:
        self.add_text(slide_id, label,
                      x, y + size + 0.05, size, 0.20,
                      font_size=9, color=C.textSecondary,
                      alignment="CENTER", valign="TOP")
    return shape_id
```

---

### 2.4 Process / flow

| Name | shapeType | Use | Recommended size | Pattern |
|------|-----------|------|----------|---------|
| `process` | `FLOW_CHART_PROCESS` | Processing step | 0.5" | Single |
| `decision` | `FLOW_CHART_DECISION` | Decision / branch | 0.5" | Single |
| `start_end` | `FLOW_CHART_TERMINATOR` | Start/end | 0.5" | Single |
| `manual_input` | `FLOW_CHART_MANUAL_INPUT` | User input | 0.5" | Single |
| `connector` | `FLOW_CHART_CONNECTOR` | Connection point | 0.3" | Single |
| `preparation` | `FLOW_CHART_PREPARATION` | Preparation / setup | 0.5" | Single |

#### process — Process

```python
def picto_process(self, slide_id, x, y, size=0.5, color=None, label=None):
    """処理ステップピクトグラム。フローチャート標準の矩形。"""
    c = color or C.primary
    w = size * 1.2
    h = size * 0.8
    shape_id = self.add_shape(slide_id, "FLOW_CHART_PROCESS",
                              x, y, w, h, fill=c)
    if label:
        # ラベルをシェイプ内に配置
        self.add_text(slide_id, label,
                      x + 0.05, y + 0.05, w - 0.1, h - 0.1,
                      font_size=9, color=C.background,
                      alignment="CENTER", valign="MIDDLE")
    return shape_id
```

#### decision — Decision

```python
def picto_decision(self, slide_id, x, y, size=0.5, color=None, label=None):
    """判断・分岐ピクトグラム。ひし形。"""
    c = color or C.accent
    shape_id = self.add_shape(slide_id, "FLOW_CHART_DECISION",
                              x, y, size, size, fill=c)
    if label:
        self.add_text(slide_id, label,
                      x + size * 0.15, y + size * 0.2,
                      size * 0.7, size * 0.6,
                      font_size=8, color=C.background,
                      alignment="CENTER", valign="MIDDLE")
    return shape_id
```

#### start_end — Start/end

```python
def picto_start_end(self, slide_id, x, y, size=0.5, color=None, label=None):
    """開始/終了ピクトグラム。角丸の端子形状。"""
    c = color or C.primary
    w = size * 1.3
    h = size * 0.6
    shape_id = self.add_shape(slide_id, "FLOW_CHART_TERMINATOR",
                              x, y, w, h, fill=c)
    if label:
        self.add_text(slide_id, label,
                      x + 0.05, y, w - 0.1, h,
                      font_size=9, color=C.background,
                      alignment="CENTER", valign="MIDDLE")
    return shape_id
```

#### manual_input — User input

```python
def picto_manual_input(self, slide_id, x, y, size=0.5, color=None, label=None):
    """ユーザー入力ピクトグラム。"""
    c = color or C.cautionYellow
    w = size * 1.2
    h = size * 0.8
    shape_id = self.add_shape(slide_id, "FLOW_CHART_MANUAL_INPUT",
                              x, y, w, h, fill=c)
    if label:
        self.add_text(slide_id, label,
                      x, y + h + 0.05, w, 0.20,
                      font_size=9, color=C.textSecondary,
                      alignment="CENTER", valign="TOP")
    return shape_id
```

#### connector — Connection point

```python
def picto_connector(self, slide_id, x, y, size=0.3, color=None, label=None):
    """接続点ピクトグラム。小さな円形。"""
    c = color or C.border
    shape_id = self.add_shape(slide_id, "FLOW_CHART_CONNECTOR",
                              x, y, size, size, fill=c)
    if label:
        self.add_text(slide_id, label,
                      x, y + size + 0.03, size, 0.18,
                      font_size=8, color=C.textSecondary,
                      alignment="CENTER", valign="TOP")
    return shape_id
```

#### preparation — Preparation

```python
def picto_preparation(self, slide_id, x, y, size=0.5, color=None, label=None):
    """準備ピクトグラム。六角形ベースの準備シンボル。"""
    c = color or C.surfaceLight
    bc = C.primary
    w = size * 1.2
    h = size * 0.8
    shape_id = self.add_shape(slide_id, "FLOW_CHART_PREPARATION",
                              x, y, w, h,
                              fill=c, border_color=bc, border_weight=1.5)
    if label:
        self.add_text(slide_id, label,
                      x + 0.1, y, w - 0.2, h,
                      font_size=9, color=C.textPrimary,
                      alignment="CENTER", valign="MIDDLE")
    return shape_id
```

---

### 2.5 Business / user

| Name | shapeType | Use | Recommended size | Pattern |
|------|-----------|------|----------|---------|
| `user` | `ELLIPSE` + `TRAPEZOID` | User / person | 0.5" | Composite |
| `team` | multiple user | Team | 1.2" | Composite |
| `building` | `RECTANGLE` + `TRIANGLE` | Company / office | 0.6" | Composite |
| `handshake` | `CURVED_RIGHT_ARROW` x2 | Partnership | 0.6" | Composite |
| `money` | `ELLIPSE` + text "$"/"¥" | Cost / pricing | 0.4" | Shape + text |
| `chart_up` | `RIGHT_TRIANGLE` | Growth / increase | 0.5" | Single |
| `target` | `DONUT` + `ELLIPSE` | Goal / target | 0.5" | Composite |

#### user — User (composite)

```python
def picto_user(self, slide_id, x, y, size=0.5, color=None, label=None):
    """ユーザー/人物ピクトグラム（複合）。
    上部: 円（頭）
    下部: 台形（肩〜胴体）
    """
    c = color or C.primary
    cx = x + size / 2
    # 頭（円）
    head_r = size * 0.16
    head_id = self.add_circle(slide_id, cx, y + head_r, head_r, fill=c)
    # 胴体（台形）
    body_w = size * 0.65
    body_h = size * 0.45
    body_x = cx - body_w / 2
    body_y = y + head_r * 2 + size * 0.05
    body_id = self.add_shape(slide_id, "TRAPEZOID",
                             body_x, body_y, body_w, body_h, fill=c)
    group_id = self.group_objects([head_id, body_id])
    if label:
        total_h = head_r * 2 + size * 0.05 + body_h
        self.add_text(slide_id, label,
                      x, y + total_h + 0.05, size, 0.20,
                      font_size=9, color=C.textSecondary,
                      alignment="CENTER", valign="TOP")
    return group_id
```

#### team — Team

```python
def picto_team(self, slide_id, x, y, size=1.2, color=None, label=None):
    """チームピクトグラム。3人のユーザーを横並びに配置。
    中央をやや大きく、左右をやや小さく。
    """
    c = color or C.primary
    unit = size / 3
    ids = []
    # 左
    ids.append(picto_user(self, slide_id, x, y + unit * 0.15,
                          unit * 0.85, color=c))
    # 中央（やや大きく）
    ids.append(picto_user(self, slide_id, x + unit, y,
                          unit, color=c))
    # 右
    ids.append(picto_user(self, slide_id, x + unit * 2, y + unit * 0.15,
                          unit * 0.85, color=c))
    group_id = self.group_objects(ids)
    if label:
        self.add_text(slide_id, label,
                      x, y + size * 0.7 + 0.05, size, 0.20,
                      font_size=9, color=C.textSecondary,
                      alignment="CENTER", valign="TOP")
    return group_id
```

#### building — Building/company (composite)

```python
def picto_building(self, slide_id, x, y, size=0.6, color=None, label=None):
    """企業・ビルピクトグラム（複合）。
    矩形（ビル本体）＋ 三角形（屋根）＋ 小矩形（窓）。
    """
    c = color or C.textMuted
    w = size * 0.7
    bx = x + (size - w) / 2
    # 屋根（三角形）
    roof_h = size * 0.25
    roof_id = self.add_shape(slide_id, "TRIANGLE",
                             bx, y, w, roof_h, fill=c)
    # 本体（矩形）
    body_h = size * 0.65
    body_y = y + roof_h - 0.01  # わずかに重ねる
    body_id = self.add_shape(slide_id, "RECTANGLE",
                             bx, body_y, w, body_h, fill=c)
    # 窓（小矩形 x4）— 2x2 グリッド
    win_ids = []
    win_w = w * 0.2
    win_h = body_h * 0.2
    for row in range(2):
        for col in range(2):
            wx = bx + w * 0.15 + col * (w * 0.45)
            wy = body_y + body_h * 0.15 + row * (body_h * 0.35)
            wid = self.add_shape(slide_id, "RECTANGLE",
                                 wx, wy, win_w, win_h, fill=C.background)
            win_ids.append(wid)
    group_id = self.group_objects([roof_id, body_id] + win_ids)
    if label:
        self.add_text(slide_id, label,
                      x, y + size + 0.05, size, 0.20,
                      font_size=9, color=C.textSecondary,
                      alignment="CENTER", valign="TOP")
    return group_id
```

#### handshake — Partnership (composite)

```python
def picto_handshake(self, slide_id, x, y, size=0.6, color=None, label=None):
    """パートナーシップ/握手ピクトグラム（複合）。
    2つの曲線矢印を向かい合わせに配置。
    """
    c = color or C.primary
    c2 = C.accent
    arrow_w = size * 0.5
    arrow_h = size * 0.4
    # 左から右への矢印
    left_id = self.add_shape(slide_id, "CURVED_RIGHT_ARROW",
                             x, y + size * 0.1, arrow_w, arrow_h, fill=c)
    # 右から左への矢印
    right_id = self.add_shape(slide_id, "CURVED_LEFT_ARROW",
                              x + size * 0.35, y + size * 0.1,
                              arrow_w, arrow_h, fill=c2)
    group_id = self.group_objects([left_id, right_id])
    if label:
        self.add_text(slide_id, label,
                      x, y + size * 0.6, size, 0.20,
                      font_size=9, color=C.textSecondary,
                      alignment="CENTER", valign="TOP")
    return group_id
```

#### money — Cost

```python
def picto_money(self, slide_id, x, y, size=0.4, color=None, label=None,
                currency="¥"):
    """コスト/料金ピクトグラム（シェイプ＋テキスト）。
    円 + 通貨記号テキスト。
    """
    c = color or C.success
    shape_id = self.add_circle(slide_id,
                               x + size / 2, y + size / 2,
                               size / 2, fill=c)
    self.add_text(slide_id, currency,
                  x, y, size, size,
                  font_size=int(size * 36), bold=True,
                  color=C.background,
                  alignment="CENTER", valign="MIDDLE")
    if label:
        self.add_text(slide_id, label,
                      x, y + size + 0.05, size, 0.20,
                      font_size=9, color=C.textSecondary,
                      alignment="CENTER", valign="TOP")
    return shape_id
```

#### chart_up — Growth

```python
def picto_chart_up(self, slide_id, x, y, size=0.5, color=None, label=None):
    """成長・上昇ピクトグラム。直角三角形。"""
    c = color or C.success
    shape_id = self.add_shape(slide_id, "RIGHT_TRIANGLE",
                              x, y, size, size, fill=c)
    if label:
        self.add_text(slide_id, label,
                      x, y + size + 0.05, size, 0.20,
                      font_size=9, color=C.textSecondary,
                      alignment="CENTER", valign="TOP")
    return shape_id
```

#### target — Target (composite)

```python
def picto_target(self, slide_id, x, y, size=0.5, color=None, label=None):
    """ターゲット/目標ピクトグラム（複合）。
    ドーナツ（外輪）＋ 円（中心点）。
    """
    c = color or C.alertRed
    cx = x + size / 2
    cy = y + size / 2
    # 外輪（ドーナツ）
    outer_id = self.add_shape(slide_id, "DONUT",
                              x, y, size, size, fill=c)
    # 中心点（小さな円）
    inner_r = size * 0.12
    inner_id = self.add_circle(slide_id, cx, cy, inner_r, fill=c)
    group_id = self.group_objects([outer_id, inner_id])
    if label:
        self.add_text(slide_id, label,
                      x, y + size + 0.05, size, 0.20,
                      font_size=9, color=C.textSecondary,
                      alignment="CENTER", valign="TOP")
    return group_id
```

---

### 2.6 Technology

| Name | shapeType | Use | Recommended size | Pattern |
|------|-----------|------|----------|---------|
| `api` | `ROUND_RECTANGLE` + text "API" | API endpoint | 0.5" | Shape + text |
| `microservice` | `HEXAGON` + text | Microservice | 0.5" | Shape + text |
| `container` | `CUBE` | Container / Docker | 0.5" | Single |
| `queue` | `CHEVRON` x3 | Message queue | 0.6" | Composite |
| `gear` | `STAR_8` | Configuration / engine | 0.5" | Single |
| `code` | `FOLDED_CORNER` | Code / script | 0.5" | Single |
| `terminal` | `ROUND_RECTANGLE` + text "> _" | CLI / terminal | 0.6" | Shape + text |

#### api — API endpoint

```python
def picto_api(self, slide_id, x, y, size=0.5, color=None, label=None):
    """API エンドポイントピクトグラム（シェイプ＋テキスト）。
    角丸矩形 + "API" テキスト。
    """
    c = color or C.primary
    w = size * 1.2
    h = size * 0.7
    shape_id = self.add_shape(slide_id, "ROUND_RECTANGLE",
                              x, y, w, h, fill=c)
    self.add_text(slide_id, "API",
                  x, y, w, h,
                  font_size=int(size * 22), bold=True,
                  color=C.background, font_family="Courier New",
                  alignment="CENTER", valign="MIDDLE")
    if label:
        self.add_text(slide_id, label,
                      x, y + h + 0.05, w, 0.20,
                      font_size=9, color=C.textSecondary,
                      alignment="CENTER", valign="TOP")
    return shape_id
```

#### microservice — Microservice

```python
def picto_microservice(self, slide_id, x, y, size=0.5, color=None, label=None,
                       text="MS"):
    """マイクロサービスピクトグラム（シェイプ＋テキスト）。
    六角形 + テキスト。text パラメータで内部テキストを変更可能。
    """
    c = color or C.accent
    shape_id = self.add_shape(slide_id, "HEXAGON",
                              x, y, size, size, fill=c)
    self.add_text(slide_id, text,
                  x, y, size, size,
                  font_size=int(size * 20), bold=True,
                  color=C.background,
                  alignment="CENTER", valign="MIDDLE")
    if label:
        self.add_text(slide_id, label,
                      x, y + size + 0.05, size, 0.20,
                      font_size=9, color=C.textSecondary,
                      alignment="CENTER", valign="TOP")
    return shape_id
```

#### container — Container

```python
def picto_container(self, slide_id, x, y, size=0.5, color=None, label=None):
    """コンテナ/Dockerピクトグラム。立方体。"""
    c = color or C.accent
    shape_id = self.add_shape(slide_id, "CUBE", x, y, size, size, fill=c)
    if label:
        self.add_text(slide_id, label,
                      x, y + size + 0.05, size, 0.20,
                      font_size=9, color=C.textSecondary,
                      alignment="CENTER", valign="TOP")
    return shape_id
```

#### queue — Message queue (composite)

```python
def picto_queue(self, slide_id, x, y, size=0.6, color=None, label=None):
    """メッセージキューピクトグラム（複合）。
    3つの重なるシェブロンで「流れ」を表現。
    """
    c = color or C.accent
    chevron_w = size * 0.35
    chevron_h = size * 0.5
    ids = []
    for i in range(3):
        cx = x + i * (chevron_w * 0.7)
        cy = y + (size - chevron_h) / 2
        # 後ろほど薄く
        alpha_factor = 0.4 + 0.3 * i  # 0.4, 0.7, 1.0
        cid = self.add_shape(slide_id, "CHEVRON",
                             cx, cy, chevron_w, chevron_h, fill=c)
        # 注意: alpha は直接設定不可。代替として色の明度で段階表現
        ids.append(cid)
    group_id = self.group_objects(ids)
    if label:
        self.add_text(slide_id, label,
                      x, y + size * 0.5 + chevron_h / 2 + 0.05,
                      size, 0.20,
                      font_size=9, color=C.textSecondary,
                      alignment="CENTER", valign="TOP")
    return group_id
```

#### gear — Configuration / engine

```python
def picto_gear(self, slide_id, x, y, size=0.5, color=None, label=None):
    """設定/エンジンピクトグラム。8頂点星でギアを表現。"""
    c = color or C.textMuted
    shape_id = self.add_shape(slide_id, "STAR_8", x, y, size, size, fill=c)
    # 中央に穴を表現する小さな円
    hole_r = size * 0.12
    self.add_circle(slide_id,
                    x + size / 2, y + size / 2,
                    hole_r, fill=C.background)
    if label:
        self.add_text(slide_id, label,
                      x, y + size + 0.05, size, 0.20,
                      font_size=9, color=C.textSecondary,
                      alignment="CENTER", valign="TOP")
    return shape_id
```

#### code — Code / script

```python
def picto_code(self, slide_id, x, y, size=0.5, color=None, label=None):
    """コード/スクリプトピクトグラム。折り曲げ角付きの文書。"""
    c = color or C.surfaceLight
    bc = C.primary
    w = size * 0.85
    h = size
    shape_id = self.add_shape(slide_id, "FOLDED_CORNER",
                              x + (size - w) / 2, y, w, h,
                              fill=c, border_color=bc, border_weight=1.0)
    # コード風テキスト
    self.add_text(slide_id, "{ }",
                  x + (size - w) / 2 + 0.05, y + h * 0.3,
                  w - 0.1, h * 0.4,
                  font_size=int(size * 24), bold=True,
                  color=C.primary, font_family="Courier New",
                  alignment="CENTER", valign="MIDDLE")
    if label:
        self.add_text(slide_id, label,
                      x, y + h + 0.05, size, 0.20,
                      font_size=9, color=C.textSecondary,
                      alignment="CENTER", valign="TOP")
    return shape_id
```

#### terminal — Terminal

```python
def picto_terminal(self, slide_id, x, y, size=0.6, color=None, label=None):
    """CLI/ターミナルピクトグラム（シェイプ＋テキスト）。
    暗い背景の角丸矩形 + プロンプトテキスト "> _"。
    """
    c = color or hex_to_rgb("#1E293B")  # ダーク背景
    w = size * 1.3
    h = size * 0.85
    shape_id = self.add_shape(slide_id, "ROUND_RECTANGLE",
                              x, y, w, h, fill=c)
    # ウィンドウ装飾（タイトルバー的な小さなドット3つ）— テキストで表現
    self.add_text(slide_id, "●  ●  ●",
                  x + 0.08, y + 0.04, w * 0.5, 0.15,
                  font_size=5, color=C.textMuted,
                  alignment="START", valign="TOP")
    # プロンプトテキスト
    self.add_text(slide_id, "> _",
                  x + 0.1, y + h * 0.3, w - 0.2, h * 0.5,
                  font_size=int(size * 18), bold=False,
                  color=C.success, font_family="Courier New",
                  alignment="START", valign="MIDDLE")
    if label:
        self.add_text(slide_id, label,
                      x, y + h + 0.05, w, 0.20,
                      font_size=9, color=C.textSecondary,
                      alignment="CENTER", valign="TOP")
    return shape_id
```

---

### 2.7 Status / indicator

| Name | shapeType | Use | Default color | Pattern |
|------|-----------|------|--------------|---------|
| `success` | `ELLIPSE` + "✓" | Success | `C.success` (green) | Shape + text |
| `error` | `ELLIPSE` + "✗" | Error | `C.alertRed` | Shape + text |
| `warning` | `TRIANGLE` + "!" | Warning | `C.cautionYellow` | Shape + text |
| `info` | `ELLIPSE` + "i" | Information | `C.primary` (blue) | Shape + text |
| `pending` | `DONUT` | In progress | `C.accent` | Single |
| `star` | `STAR_5` | Favorite / important | `C.cautionYellow` | Single |

> **Note**: `success` uses the same implementation as `check_circle` (section 2.3). `warning` is also
> identical to the one in section 2.3. This section shows the default color specialized for status-display
> use cases.

#### error — Error

```python
def picto_error(self, slide_id, x, y, size=0.4, color=None, label=None):
    """エラーピクトグラム（シェイプ＋テキスト）。"""
    c = color or hex_to_rgb(C.alertRed)
    shape_id = self.add_circle(slide_id,
                               x + size / 2, y + size / 2,
                               size / 2, fill=c)
    self.add_text(slide_id, "✗",
                  x, y, size, size,
                  font_size=int(size * 36), bold=True,
                  color=C.background,
                  alignment="CENTER", valign="MIDDLE")
    if label:
        self.add_text(slide_id, label,
                      x, y + size + 0.05, size, 0.20,
                      font_size=9, color=C.textSecondary,
                      alignment="CENTER", valign="TOP")
    return shape_id
```

#### info — Information

```python
def picto_info(self, slide_id, x, y, size=0.4, color=None, label=None):
    """情報ピクトグラム（シェイプ＋テキスト）。"""
    c = color or C.primary
    shape_id = self.add_circle(slide_id,
                               x + size / 2, y + size / 2,
                               size / 2, fill=c)
    self.add_text(slide_id, "i",
                  x, y, size, size,
                  font_size=int(size * 36), bold=True,
                  color=C.background, font_family="Century Gothic",
                  alignment="CENTER", valign="MIDDLE")
    if label:
        self.add_text(slide_id, label,
                      x, y + size + 0.05, size, 0.20,
                      font_size=9, color=C.textSecondary,
                      alignment="CENTER", valign="TOP")
    return shape_id
```

#### pending — In progress

```python
def picto_pending(self, slide_id, x, y, size=0.4, color=None, label=None):
    """処理中ピクトグラム。ドーナツ形状でスピナーを暗示。"""
    c = color or C.accent
    shape_id = self.add_shape(slide_id, "DONUT", x, y, size, size, fill=c)
    if label:
        self.add_text(slide_id, label,
                      x, y + size + 0.05, size, 0.20,
                      font_size=9, color=C.textSecondary,
                      alignment="CENTER", valign="TOP")
    return shape_id
```

#### star — Important

```python
def picto_star(self, slide_id, x, y, size=0.4, color=None, label=None):
    """重要/お気に入りピクトグラム。5頂点星。"""
    c = color or hex_to_rgb("#BE9000")  # cautionYellow
    shape_id = self.add_shape(slide_id, "STAR_5", x, y, size, size, fill=c)
    if label:
        self.add_text(slide_id, label,
                      x, y + size + 0.05, size, 0.20,
                      font_size=9, color=C.textSecondary,
                      alignment="CENTER", valign="TOP")
    return shape_id
```

---

## 3. Guidelines for building composite pictograms

### 3.1 Design principles

Principles for building composite pictograms (a combination of two or more shapes):

1. **Cap the shape count at 3** — anything more becomes too visually complex
2. **Always group with `group_objects()`** — this makes move/rotate operations possible as a single unit
3. **Watch the Z-order** — shapes added later come to the front (add the background first)
4. **Compute sizes as ratios** — derive sub-shape coordinates as ratios of the `size` parameter
5. **Keep the label outside the group** — do not include the label text in the group (add it after grouping)

### 3.2 Construction template

```python
def picto_composite_template(self, slide_id, x, y, size, color=None, label=None):
    """複合ピクトグラムのテンプレート。

    構築手順:
    1. メイン色を決定（color or デフォルト）
    2. サブシェイプの座標をサイズ比率で計算
    3. 背景シェイプから順に追加（Z-order）
    4. group_objects() でグループ化
    5. ラベルを追加（グループ外）
    6. group_id を返す
    """
    c = color or C.primary
    ids = []

    # 1. 背景レイヤー（最背面）
    bg_id = self.add_shape(slide_id, "ROUND_RECTANGLE",
                           x, y, size, size, fill=C.surfaceLight)
    ids.append(bg_id)

    # 2. メインシェイプ
    main_w = size * 0.6
    main_h = size * 0.5
    main_x = x + (size - main_w) / 2
    main_y = y + (size - main_h) / 2
    main_id = self.add_shape(slide_id, "RECTANGLE",
                             main_x, main_y, main_w, main_h, fill=c)
    ids.append(main_id)

    # 3. 装飾シェイプ（最前面）
    deco_r = size * 0.08
    deco_id = self.add_circle(slide_id,
                              x + size * 0.8, y + size * 0.2,
                              deco_r, fill=C.success)
    ids.append(deco_id)

    # グループ化
    group_id = self.group_objects(ids)

    # ラベル（グループ外）
    if label:
        self.add_text(slide_id, label,
                      x, y + size + 0.05, size, 0.20,
                      font_size=9, color=C.textSecondary,
                      alignment="CENTER", valign="TOP")
    return group_id
```

### 3.3 Server rack (applied example)

```
┌──────────────┐
│ ═══════════  │  ← ディスクベイ1
│ ═══════════  │  ← ディスクベイ2
│ ═══════════  │  ← ディスクベイ3
│         ● ● │  ← LED
└──────────────┘
```

```python
def picto_server_rack(self, slide_id, x, y, size=0.8, color=None, label=None):
    """サーバーラックピクトグラム（応用的な複合例）。
    本体 + ディスクベイ3段 + LEDインジケーター2個。

    注意: シェイプ数が多い（6個）ため、大きなグリッドでの使用は
    API リクエスト数増加に注意。
    """
    c = color or C.textMuted
    w = size * 0.7
    h = size
    bx = x + (size - w) / 2
    ids = []

    # 本体
    body_id = self.add_shape(slide_id, "ROUND_RECTANGLE",
                             bx, y, w, h, fill=c)
    ids.append(body_id)

    # ディスクベイ（横線3本）
    bay_w = w * 0.7
    bay_h = h * 0.04
    bay_x = bx + (w - bay_w) / 2
    for i in range(3):
        bay_y = y + h * 0.15 + i * (h * 0.2)
        bid = self.add_shape(slide_id, "RECTANGLE",
                             bay_x, bay_y, bay_w, bay_h,
                             fill=C.background)
        ids.append(bid)

    # LED（緑 + 青）
    led_r = size * 0.04
    led_y = y + h * 0.85
    led1 = self.add_circle(slide_id, bx + w * 0.7, led_y, led_r,
                           fill=C.success)
    led2 = self.add_circle(slide_id, bx + w * 0.85, led_y, led_r,
                           fill=C.accent)
    ids.extend([led1, led2])

    group_id = self.group_objects(ids)
    if label:
        self.add_text(slide_id, label,
                      x, y + h + 0.05, size, 0.20,
                      font_size=9, color=C.textSecondary,
                      alignment="CENTER", valign="TOP")
    return group_id
```

---

## 4. Applying theme colors

### 4.1 Semantic color mapping

The color of a pictogram should be chosen according to the context of the content. Use the semantic colors on the theme's `C` object.

| Pictogram context | Color to use | HEX (scalar theme) | Examples |
|---|---|---|---|
| Own product | `C.primary` | `#2673BB` (blue) | ScalarDB, ScalarDL icons |
| External system | `C.textMuted` | `#666666` (gray) | PostgreSQL, MySQL, Cassandra |
| User/client | `C.cautionYellow` | `#BE9000` (orange) | Browser, mobile app |
| Success / normal flow | `C.success` | `#63C045` (green) | Normal path, pass |
| Error / failure | `C.alertRed` | `#F4CCCC` (red) | Failure path, error |
| New feature / accent | `C.accent` | `#0985FC` (cyan/blue) | Highlighting a new feature |
| Supporting element | `C.surfaceLight` | `#F0F4F8` (light gray) | Background zones, borders |

### 4.2 Fill and stroke rules

| Style | Use | Setting method |
|---------|------|---------|
| **Solid fill** | Main pictogram | `fill=c, border_color=c` (border of the same color) |
| **Outline only** | Supporting element | `border_color=c` only (`fill=None`) |
| **Light fill + dark border** | A supporting element you want to emphasize | `fill=C.surfaceLight, border_color=c` |
| **On a dark background** | Slide with a dark background | `fill=C.background` (white) + `border_color=c` |
| **On a gray background** | Inside a gray background zone | `fill=C.background` (white) + `border_color=C.primary` |

```python
# ソリッド塗りの例（メインアイコン）
self.add_shape(slide_id, "CAN", x, y, w, h, fill=C.primary)

# アウトラインの例（補助アイコン）
self.add_shape(slide_id, "ROUND_RECTANGLE", x, y, w, h,
               border_color=C.primary, border_weight=1.5)

# 薄い塗り＋ボーダーの例
self.add_shape(slide_id, "HEXAGON", x, y, w, h,
               fill=C.surfaceLight, border_color=C.primary, border_weight=1.0)
```

### 4.3 Contrast requirements

Maintain WCAG AA compliance (contrast ratio of 4.5:1 or higher):

| Background color | Text/icon color | Contrast ratio | Verdict |
|--------|-------------------|-------------|------|
| `#FFFFFF` (white) | `C.primary` (#2673BB) | 5.2:1 | OK |
| `#FFFFFF` (white) | `C.textMuted` (#666666) | 5.7:1 | OK |
| `#FFFFFF` (white) | `C.success` (#63C045) | 3.3:1 | NG — not usable for text |
| `C.primary` (#2673BB) | `#FFFFFF` (white) | 5.2:1 | OK |
| `C.surfaceLight` (#F0F4F8) | `C.primary` (#2673BB) | 4.6:1 | OK |

> **Important**: `C.success` (green) can be used as a shape fill color, but any text on top of it must be
> white. Using it alone as a text color can result in insufficient contrast.

---

## 5. Sizing guidelines

### 5.1 Recommended sizes by use case

| Use case | Recommended size | Minimum size | Notes |
|------|----------|----------|------|
| Inline (next to text) | 0.3"-0.4" | 0.25" | Match the text line height |
| Icon inside a card | 0.4"-0.6" | 0.35" | 20-30% of the card width |
| Grid icon | 0.5"-0.7" | 0.4" | 25-35% of the grid cell width |
| Main visual | 0.8"-1.2" | 0.6" | The primary element centered on a slide |
| Hero icon | 1.5"-2.0" | 1.0" | Large icons on title slides, etc. |

### 5.2 Note on the Google Slides coordinate system

The Google Slides coordinate system is **10.0" x 5.625"** (0.75x PowerPoint's). All recommended sizes above are inch values in this coordinate system.

```python
# サイズ計算のヘルパー
SLIDE_W = 10.0   # inches
SLIDE_H = 5.625  # inches

def relative_size(base_size, scale=1.0):
    """基準サイズからスケール係数で算出する。"""
    return base_size * scale
```

### 5.3 Guidance for internal text font size

Font sizes when placing text inside a shape:

| Shape size | 1 character | 2-3 characters | 4+ characters |
|-------------|-------------|--------------|---------------|
| 0.3" | 12pt | 8pt | Not usable |
| 0.4" | 16pt | 10pt | 8pt |
| 0.5" | 18pt | 12pt | 9pt |
| 0.6" | 22pt | 14pt | 10pt |
| 0.8" | 28pt | 18pt | 12pt |
| 1.0" | 36pt | 22pt | 14pt |

> **Minimum font size**: text inside a pictogram must be **8pt or larger** (below 7pt, legibility drops sharply).

---

## 6. Grid layout patterns

### 6.1 Icon grid (2x3)

A 2-row x 3-column pictogram grid. Each cell holds an icon, a title, and a description.

```
┌─────────┐ ┌─────────┐ ┌─────────┐
│   [DB]   │ │  [API]  │ │ [Cloud] │
│ データ層  │ │ API連携  │ │ クラウド │
│ 説明文   │ │ 説明文   │ │ 説明文   │
├─────────┤ ├─────────┤ ├─────────┤
│ [Shield] │ │ [Gear]  │ │ [Check] │
│ セキュリ  │ │  設定    │ │  監視    │
│ 説明文   │ │ 説明文   │ │ 説明文   │
└─────────┘ └─────────┘ └─────────┘
```

```python
def add_picto_grid(self, slide_id, items, x_start, y_start,
                   cols=3, rows=2, cell_w=2.5, cell_h=1.5, icon_size=0.5):
    """ピクトグラムグリッドを配置する。

    Args:
        slide_id: スライドID
        items: list of {"picto": str, "title": str, "desc": str (optional)}
        x_start, y_start: グリッド左上の座標（インチ）
        cols, rows: 列数・行数
        cell_w, cell_h: セル幅・高さ（インチ）
        icon_size: ピクトグラムサイズ（インチ）

    最大表示数: cols * rows。items がそれを超える場合は切り捨て。
    """
    max_items = cols * rows
    for i, item in enumerate(items[:max_items]):
        col = i % cols
        row = i // cols
        # セル中央のX座標
        cx = x_start + col * cell_w + cell_w / 2
        cy = y_start + row * cell_h

        # ピクトグラム配置（中央揃え）
        self.add_pictogram(slide_id, item["picto"],
                           cx - icon_size / 2, cy, icon_size,
                           color=item.get("color"))

        # タイトル
        self.add_text(slide_id, item["title"],
                      cx - cell_w / 2 + 0.1, cy + icon_size + 0.08,
                      cell_w - 0.2, 0.25,
                      font_size=12, bold=True, color=C.textTitle,
                      alignment="CENTER", valign="TOP")

        # 説明（オプション）
        if item.get("desc"):
            self.add_text(slide_id, item["desc"],
                          cx - cell_w / 2 + 0.1, cy + icon_size + 0.35,
                          cell_w - 0.2, 0.40,
                          font_size=10, color=C.textSecondary,
                          alignment="CENTER", valign="TOP")
```

### Example usage

```python
sid = self.add_content_slide("ScalarDB の主要機能")
items = [
    {"picto": "database",     "title": "トランザクション",
     "desc": "分散ACID\nトランザクション"},
    {"picto": "api",          "title": "統一API",
     "desc": "DB非依存の\n共通インターフェース"},
    {"picto": "cloud",        "title": "マルチクラウド",
     "desc": "AWS/GCP/Azure\n対応"},
    {"picto": "shield",       "title": "セキュリティ",
     "desc": "暗号化＋\nアクセス制御"},
    {"picto": "gear",         "title": "自動管理",
     "desc": "運用自動化\nツール"},
    {"picto": "check_circle", "title": "高可用性",
     "desc": "99.99% SLA\n保証"},
]
self.add_picto_grid(sid, items,
                    x_start=L.MX, y_start=L.bodyY + 0.1,
                    cols=3, rows=2,
                    cell_w=(L.CW / 3), cell_h=2.0,
                    icon_size=0.5)
```

---

### 6.2 Horizontal icon row (1xN)

Lay out N pictograms horizontally in a single row. Used for step displays or comparisons.

```
[Step1] ──→ [Step2] ──→ [Step3] ──→ [Step4]
```

```python
def add_picto_row(self, slide_id, items, x_start, y, total_w,
                  icon_size=0.5, show_arrows=True):
    """ピクトグラムを横一列に配置する。

    Args:
        items: list of {"picto": str, "title": str}
        x_start: 開始X座標
        y: Y座標
        total_w: 全体幅
        icon_size: ピクトグラムサイズ
        show_arrows: アイテム間に矢印を表示するか
    """
    n = len(items)
    spacing = total_w / n

    for i, item in enumerate(items):
        cx = x_start + i * spacing + spacing / 2

        # ピクトグラム
        self.add_pictogram(slide_id, item["picto"],
                           cx - icon_size / 2, y, icon_size,
                           color=item.get("color"))

        # タイトル
        self.add_text(slide_id, item["title"],
                      cx - spacing / 2 + 0.1, y + icon_size + 0.08,
                      spacing - 0.2, 0.25,
                      font_size=10, bold=True, color=C.textTitle,
                      alignment="CENTER", valign="TOP")

        # 矢印（最後のアイテム以外）
        if show_arrows and i < n - 1:
            arrow_x = cx + icon_size / 2 + 0.05
            arrow_w = spacing - icon_size - 0.1
            arrow_y = y + icon_size / 2 - 0.05
            self.add_shape(slide_id, "RIGHT_ARROW",
                           arrow_x, arrow_y, arrow_w, 0.10,
                           fill=C.border)
```

### Example usage

```python
sid = self.add_content_slide("デプロイフロー")
steps = [
    {"picto": "code",      "title": "コード"},
    {"picto": "container", "title": "ビルド"},
    {"picto": "gear",      "title": "テスト"},
    {"picto": "cloud",     "title": "デプロイ"},
]
self.add_picto_row(sid, steps,
                   x_start=L.MX, y=L.bodyY + 0.5,
                   total_w=L.CW, icon_size=0.5)
```

---

### 6.3 Combining a flowchart with pictograms

An applied pattern that replaces flowchart nodes with pictograms.

```python
def add_picto_flow(self, slide_id, nodes, x_start, y_start,
                   total_w, icon_size=0.5, direction="horizontal"):
    """ピクトグラムベースのフローチャートを配置する。

    Args:
        nodes: list of {
            "picto": str,
            "title": str,
            "type": "normal" | "decision" | "start" | "end"
        }
        direction: "horizontal" | "vertical"
    """
    n = len(nodes)

    if direction == "horizontal":
        spacing = total_w / n
        for i, node in enumerate(nodes):
            cx = x_start + i * spacing + spacing / 2
            ny = y_start

            # ノード種別に応じたスタイル
            node_color = {
                "start": C.success,
                "end": C.alertRed,
                "decision": C.accent,
                "normal": C.primary,
            }.get(node.get("type", "normal"), C.primary)

            # ピクトグラム
            self.add_pictogram(slide_id, node["picto"],
                               cx - icon_size / 2, ny, icon_size,
                               color=node_color)

            # タイトル
            self.add_text(slide_id, node["title"],
                          cx - spacing / 2, ny + icon_size + 0.08,
                          spacing, 0.25,
                          font_size=10, bold=True, color=C.textTitle,
                          alignment="CENTER", valign="TOP")

            # コネクター（最後以外）
            if i < n - 1:
                arrow_x = cx + icon_size / 2 + 0.05
                arrow_w = spacing - icon_size - 0.1
                self.add_line(slide_id,
                              arrow_x, ny + icon_size / 2,
                              arrow_w, color=C.border, weight=1.5)

    elif direction == "vertical":
        spacing = 1.2  # 固定間隔
        for i, node in enumerate(nodes):
            ny = y_start + i * spacing
            cx = x_start + total_w / 2

            node_color = {
                "start": C.success,
                "end": C.alertRed,
                "decision": C.accent,
                "normal": C.primary,
            }.get(node.get("type", "normal"), C.primary)

            self.add_pictogram(slide_id, node["picto"],
                               cx - icon_size / 2, ny, icon_size,
                               color=node_color)
            self.add_text(slide_id, node["title"],
                          cx + icon_size / 2 + 0.15, ny,
                          total_w / 2, icon_size,
                          font_size=10, bold=True, color=C.textTitle,
                          alignment="START", valign="MIDDLE")

            # 垂直コネクター（最後以外）
            if i < n - 1:
                self.add_connector(slide_id,
                                   cx, ny + icon_size,
                                   cx, ny + spacing,
                                   color=C.border, weight=1.5)
```

---

## 7. Mapping to slide types

A list of pictograms commonly used for each slide type, intended for reference by composer functions.

| Slide type | Recommended pictograms | Use |
|---|---|---|
| `icon_grid` | Selected from all categories | Icons within the grid |
| `architecture` | database, cloud, server, container, api, firewall, load_balancer | Nodes in architecture diagrams |
| `product_overview` | target, gear, check_circle, star, shield | Icons for product features |
| `feature_matrix` | check_circle, error, warning, ban | Indicating feature availability |
| `security_compliance` | shield, lock, key, check_circle, ban | Security elements |
| `deployment_steps` | process, gear, cloud, container, code, terminal | Deployment steps |
| `ecosystem` | network, handshake, api, cloud, microservice | Ecosystem integrations |
| `data_flow` | database, queue, cache, process, connector | Data flow diagrams |
| `multi_cloud` | cloud (multiple colors), database, server | Multi-cloud configurations |
| `comparison` | check_circle, error, star | Markers in comparison tables |
| `kpi_dashboard` | chart_up, money, target, success | Icons for KPI cards |
| `timeline` | process, start_end, decision | Timeline markers |

### Color patterns by slide type

```python
# architecture スライドの典型的な配色
ARCH_COLORS = {
    "database":      C.primary,      # ScalarDB = 自社製品 → blue
    "server":        C.textMuted,    # 外部サーバー → gray
    "cloud":         C.accent,       # クラウド環境 → cyan
    "api":           C.primary,      # 自社 API → blue
    "firewall":      C.alertRed,     # セキュリティ → red
    "load_balancer": C.success,      # ネットワーク → green
    "container":     C.accent,       # コンテナ → cyan
}

# feature_matrix スライドの配色
FEATURE_COLORS = {
    "check_circle":  C.success,      # 対応済み → green
    "error":         C.alertRed,     # 非対応 → red
    "warning":       C.cautionYellow, # 一部対応 → yellow
    "star":          C.cautionYellow, # 優位機能 → yellow
}
```

---

## 8. Unicode text icons (a simple alternative)

A way to express a simple icon by embedding a Unicode character in a text run, without using a shape. This offers less flexibility than a shape pictogram, but is useful when you want to insert an icon inline within running text.

### 8.1 Recommended Unicode icon list

| Character | Unicode | Use | Font compatibility |
|------|---------|------|------------|
| ✓ | U+2713 | Success / supported | High |
| ✗ | U+2717 | Failure / unsupported | High |
| ● | U+25CF | Marker / dot | High |
| ○ | U+25CB | Empty marker | High |
| ▶ | U+25B6 | Play / next | High |
| ◆ | U+25C6 | Emphasis marker | High |
| ★ | U+2605 | Important / favorite | High |
| ☆ | U+2606 | Not yet rated | High |
| ⚡ | U+26A1 | Fast / performance | Medium |
| ⚙ | U+2699 | Settings / gear | Medium |
| ⬆ | U+2B06 | Increase / improvement | High |
| ⬇ | U+2B07 | Decrease / reduction | High |
| → | U+2192 | Flow / direction | High |
| ∞ | U+221E | Unlimited | High |

### 8.2 Example usage in text

```python
# 箇条書きのプレフィックスとして
items = [
    "✓ ACID トランザクション対応",
    "✓ マルチクラウド対応",
    "✗ レガシー DB 非対応",
]
self.add_bullets(slide_id, items, L.MX, L.bodyY, L.CW, 2.0)

# KPI カードのバリュー表示
self.add_text(slide_id, "⬆ 99.9%",
              x, y, w, h,
              font_size=28, bold=True, color=C.success)
```

### 8.3 Notes on font compatibility

- **High compatibility** (renders in Arial, Noto Sans JP): ✓ ✗ ● ○ ▶ ◆ ★ → ∞
- **Medium compatibility** (may not render correctly in some fonts): ⚡ ⚙ 🔒 🔑
- **Low compatibility** (color emoji, environment-dependent): 🚀 💡 📊 🎯

> **Recommendation**: use high-compatibility Unicode characters for in-text icons. Use shape pictograms
> instead for medium- and low-compatibility characters.

---

## 9. Optimizing the number of API requests

### 9.1 Approximate request counts

| Pattern | Requests per instance | Notes |
|---------|---------------------|------|
| Single shape | 2-3 | createShape + fill + border |
| Shape + text | 5-7 | shape + fill + textbox + insert + style |
| Composite (2 shapes) | 6-8 | shape x2 + fills + groupObjects |
| Composite (3 shapes) | 9-12 | shape x3 + fills + groupObjects |
| With label | +4 | textbox + insert + style + paragraph |

### 9.2 Optimization tips

1. **Prefer single shapes inside grids** — using a composite pictogram in a 6-cell grid can produce 50+ requests
2. **Mind the 500-request limit** — the recommended `batchUpdate` chunk size is 500. Avoid exceeding it through heavy pictogram use
3. **Omit labels where possible** — if the text below the grid is already sufficient, the pictogram's own label can be omitted
4. **Leverage Unicode icons** — replace simple markers (✓/✗) with text to reduce request count

### 9.3 Estimating request counts

```python
def estimate_picto_requests(items, has_labels=True, pattern="single"):
    """ピクトグラムグリッドのリクエスト数を見積もる。"""
    per_item = {
        "single": 3,      # shape + fill + border
        "text": 7,        # shape + fill + textbox + insert + style + alignment + valign
        "composite_2": 8, # 2 shapes + fills + group
        "composite_3": 12, # 3 shapes + fills + group
    }[pattern]
    if has_labels:
        per_item += 4  # label textbox
    return len(items) * per_item
```

---

## 10. Usage notes

### 10.1 General notes

1. **Avoid over-compositing** — composite pictograms with 3 or more shapes become too complex. If more precision is required than that, consider an external image (uploaded via the Drive API)

2. **In-text icons** — including Unicode symbols (✓ ✗ ● ★, etc.) in a text run can also achieve a simple icon without a shape. See section 8

3. **Maintain consistency** — use the same construction pattern throughout a given slide. Do not mix single shapes and composite shapes

4. **Ensure contrast** — comply with WCAG AA (4.5:1 or higher). Use an outline or solid fill on a white background, and a white fill with a colored border on a dark background

5. **Always group** — composite pictograms must always be grouped with `group_objects()`. Without grouping, the pieces will scatter when moved

### 10.2 Performance notes

6. **API request count** — pictograms consume multiple requests for shape creation plus style settings. When using many pictograms, be mindful of the `batchUpdate` chunk size (500 requests)

7. **Rendering load** — a large number of shapes increases browser rendering load. We recommend no more than **50 shapes** per slide

### 10.3 Design notes

8. **Use a uniform size** — create all pictograms in a grid with the same `size` parameter. Inconsistent sizes throw off the visual balance

9. **Ensure spacing** — keep at least 0.15" of spacing between pictograms. Dense placement reduces legibility

10. **Keep colors consistent** — use **3 colors or fewer** per slide (the 60-30-10 rule). Pictogram colors should follow this rule as well

---

## Appendix A. Pictogram reference table (quick reference)

| Type name | shapeType | Pattern | Default color | Recommended size |
|---------|-----------|---------|------------|----------|
| `database` | CAN | Single | primary | 0.5" |
| `storage` | FLOW_CHART_MAGNETIC_DISK | Single | primary | 0.5" |
| `document` | FLOW_CHART_DOCUMENT | Single | primary | 0.5" |
| `multi_document` | FLOW_CHART_MULTIDOCUMENT | Single | primary | 0.6" |
| `cache` | FLOW_CHART_INTERNAL_STORAGE | Single | accent | 0.5" |
| `cloud` | CLOUD | Single | primary | 0.6" |
| `cloud_callout` | CLOUD_CALLOUT | Single | calloutBg | 0.6" |
| `network` | HEXAGON | S+T | primary | 0.5" |
| `server` | ROUND_RECT + RECT x3 + ELLIPSE | Composite | textMuted | 0.5" |
| `load_balancer` | TRAPEZOID | Single | accent | 0.6" |
| `firewall` | RECT + LIGHTNING_BOLT | Composite | alertRed | 0.6" |
| `shield` | PENTAGON | Single | primary | 0.5" |
| `lock` | ROUND_RECT x2 + ELLIPSE | Composite | primary | 0.5" |
| `key` | ELLIPSE + RECTANGLE | Composite | cautionYellow | 0.5" |
| `check_circle` | ELLIPSE + "✓" | S+T | success | 0.4" |
| `warning` | TRIANGLE + "!" | S+T | cautionYellow | 0.4" |
| `ban` | NO_SMOKING | Single | alertRed | 0.4" |
| `process` | FLOW_CHART_PROCESS | Single | primary | 0.5" |
| `decision` | FLOW_CHART_DECISION | Single | accent | 0.5" |
| `start_end` | FLOW_CHART_TERMINATOR | Single | primary | 0.5" |
| `manual_input` | FLOW_CHART_MANUAL_INPUT | Single | cautionYellow | 0.5" |
| `connector` | FLOW_CHART_CONNECTOR | Single | border | 0.3" |
| `preparation` | FLOW_CHART_PREPARATION | Single | surfaceLight | 0.5" |
| `user` | ELLIPSE + TRAPEZOID | Composite | primary | 0.5" |
| `team` | user x3 | Composite | primary | 1.2" |
| `building` | RECT + TRIANGLE + RECT x4 | Composite | textMuted | 0.6" |
| `handshake` | CURVED_*_ARROW x2 | Composite | primary | 0.6" |
| `money` | ELLIPSE + "¥" | S+T | success | 0.4" |
| `chart_up` | RIGHT_TRIANGLE | Single | success | 0.5" |
| `target` | DONUT + ELLIPSE | Composite | alertRed | 0.5" |
| `api` | ROUND_RECT + "API" | S+T | primary | 0.5" |
| `microservice` | HEXAGON + text | S+T | accent | 0.5" |
| `container` | CUBE | Single | accent | 0.5" |
| `queue` | CHEVRON x3 | Composite | accent | 0.6" |
| `gear` | STAR_8 + ELLIPSE | Composite | textMuted | 0.5" |
| `code` | FOLDED_CORNER + "{ }" | S+T | surfaceLight | 0.5" |
| `terminal` | ROUND_RECT + "> _" | S+T | dark | 0.6" |
| `success` | ELLIPSE + "✓" | S+T | success | 0.4" |
| `error` | ELLIPSE + "✗" | S+T | alertRed | 0.4" |
| `info` | ELLIPSE + "i" | S+T | primary | 0.4" |
| `pending` | DONUT | Single | accent | 0.4" |
| `star` | STAR_5 | Single | cautionYellow | 0.4" |

> **Legend**: S+T = shape + text, Composite = multiple shapes (requires `group_objects`)

---

## Appendix B. shapeType selection cheat sheet

A reverse lookup from concept to shapeType, for use when designing a pictogram.

| Concept to express | Recommended shapeType | Alternative candidates |
|--------------|---------------|---------|
| Database | `CAN` | `FLOW_CHART_MAGNETIC_DISK` |
| File / document | `FLOW_CHART_DOCUMENT` | `FOLDED_CORNER` |
| Cloud | `CLOUD` | `CLOUD_CALLOUT` |
| Server / machine | `ROUND_RECTANGLE` (composite) | `RECTANGLE` |
| Security | `PENTAGON` | `FLOW_CHART_PREPARATION` |
| Authentication / encryption | `ROUND_RECTANGLE` (composite lock) | — |
| Processing step | `FLOW_CHART_PROCESS` | `RECTANGLE` |
| Decision / branch | `FLOW_CHART_DECISION` | `DIAMOND` |
| Person | `ELLIPSE` + `TRAPEZOID` (composite) | — |
| Company / building | `RECTANGLE` + `TRIANGLE` (composite) | — |
| API / service | `ROUND_RECTANGLE` + text | `HEXAGON` + text |
| Container | `CUBE` | `ROUND_RECTANGLE` |
| Settings / gear | `STAR_8` | `SUN` |
| Success | `ELLIPSE` + "✓" | Unicode ✓ |
| Error | `ELLIPSE` + "✗" | `NO_SMOKING` |
| Warning | `TRIANGLE` + "!" | Unicode ⚠ |
| Direction / flow | `RIGHT_ARROW` family | `CHEVRON` |
| Cost / amount | `ELLIPSE` + "¥"/"$" | — |
| Network | `HEXAGON` | `OCTAGON` |
| Queue / stream | `CHEVRON` (composite) | `RIGHT_ARROW` |
| Goal / target | `DONUT` + `ELLIPSE` (composite) | `STAR_5` |
| Important / priority | `STAR_5` | `STARBURST` |
| Prohibited | `NO_SMOKING` | `MATH_MULTIPLY` |
| Fast / performance | `LIGHTNING_BOLT` | Unicode ⚡ |
