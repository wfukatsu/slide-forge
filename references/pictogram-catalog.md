# ピクトグラムカタログ

> Google Slides API のシェイプ＋テキストで構築するピクトグラムパターン集。
> 外部画像不要でスライド上にアイコン的要素を作成する。

### 規約

本ドキュメントで使用する識別子:

- **`C`** — `templates/<theme>/theme.json` の `colors` セクションから展開した色定数クラス
- **`L`** — `templates/<theme>/theme.json` の `layouts` セクションから展開したレイアウト定数クラス
- **`sb`** / **`self`** — `SlideBuilder` インスタンス（パターンは SlideBuilder のメソッドとして実装）

---

## 1. 概要

### 1.1 ピクトグラムとは

Google Slides API では画像アイコンの代わりに、シェイプ（141種）を組み合わせてアイコン的な視覚要素を構築できる。

利点:

- **外部画像不要** — Drive API アップロードが不要。batchUpdate のみで完結
- **テーマカラーに自動適応** — `C.primary` 等のセマンティックカラーで色指定するため、テーマ切替時に自動更新
- **サイズ変更でも劣化しない** — ベクターシェイプのため、拡大・縮小しても品質を維持
- **グループ化して移動・回転可能** — `group_objects()` で一括操作
- **テキスト埋め込み可能** — シェイプ内にテキストを配置して、ラベル付きアイコンを実現

### 1.2 構築パターン

3つの構築パターンがある:

| パターン | 説明 | 複雑度 | 例 |
|----------|------|--------|-----|
| **単一シェイプ** | 1つのシェイプだけで表現 | 低 | CLOUD, CAN, SHIELD |
| **シェイプ＋テキスト** | シェイプ内にテキストを配置 | 中 | バッジ、ラベル付きアイコン |
| **複合シェイプ** | 複数シェイプを組み合わせてグループ化 | 高 | サーバー、ロック、ユーザー |

**原則**: 可能な限り単一シェイプで表現する。3シェイプ以上の複合ピクトグラムは複雑になりすぎるため、外部画像の使用を検討すること。

> **外部画像を使う場合の第一候補は `assets/shared/icons/` のアイコンライブラリ**（Scalar
> ブランドの 62 種）。テーマ色に染めて貼れる。使い方は `references/icon-library.md`。
> 「情報銀行」「証拠チェーン」「内定」のような業務語彙はシェイプでは描けないので、
> 最初からそちらを使う。ただし Drive 経由の通信が発生する点だけ注意する。

### 1.3 共通ヘルパー

全ピクトグラム関数に共通するシグネチャ:

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

### 1.4 レジストリ

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

## 2. カテゴリ別ピクトグラム

### 2.1 データベース・ストレージ

| 名前 | shapeType | 用途 | 推奨サイズ | パターン |
|------|-----------|------|----------|---------|
| `database` | `CAN` | データベース全般 | 0.5" | 単一 |
| `storage` | `FLOW_CHART_MAGNETIC_DISK` | ストレージ・ディスク | 0.5" | 単一 |
| `document` | `FLOW_CHART_DOCUMENT` | ドキュメント・ファイル | 0.5" | 単一 |
| `multi_document` | `FLOW_CHART_MULTIDOCUMENT` | 複数ファイル | 0.6" | 単一 |
| `cache` | `FLOW_CHART_INTERNAL_STORAGE` | キャッシュ・メモリ | 0.5" | 単一 |

#### database — データベース

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

#### storage — ストレージ

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

#### document — ドキュメント

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

#### multi_document — 複数ドキュメント

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

#### cache — キャッシュ

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

### 2.2 クラウド・ネットワーク

| 名前 | shapeType | 用途 | 推奨サイズ | パターン |
|------|-----------|------|----------|---------|
| `cloud` | `CLOUD` | クラウドサービス | 0.6" | 単一 |
| `cloud_callout` | `CLOUD_CALLOUT` | クラウドアノテーション | 0.6" | 単一 |
| `network` | `HEXAGON` | ネットワーク・ノード | 0.5" | シェイプ＋テキスト |
| `server` | `RECTANGLE` + `RECTANGLE` | サーバー | 0.5" | 複合 |
| `load_balancer` | `TRAPEZOID` | ロードバランサー | 0.6" | 単一 |
| `firewall` | `RECTANGLE` + `LIGHTNING_BOLT` | ファイアウォール | 0.6" | 複合 |

#### cloud — クラウド

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

#### cloud_callout — クラウド吹出し

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

#### network — ネットワークノード

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

#### server — サーバー（複合）

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

#### load_balancer — ロードバランサー

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

#### firewall — ファイアウォール（複合）

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

### 2.3 セキュリティ

| 名前 | shapeType | 用途 | 推奨サイズ | パターン |
|------|-----------|------|----------|---------|
| `shield` | `PENTAGON` | セキュリティ・保護 | 0.5" | 単一 |
| `lock` | `ROUND_RECTANGLE` + `RECTANGLE` | 認証・暗号化 | 0.5" | 複合 |
| `key` | `PLUS` + `RECTANGLE` | アクセスキー・認証情報 | 0.5" | 複合 |
| `check_circle` | `ELLIPSE` + text "✓" | 検証済み・合格 | 0.4" | シェイプ＋テキスト |
| `warning` | `TRIANGLE` + text "!" | 警告・注意 | 0.4" | シェイプ＋テキスト |
| `ban` | `NO_SMOKING` | 禁止・非推奨 | 0.4" | 単一 |

#### shield — シールド

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

#### lock — ロック（複合）

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

#### key — 鍵

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

#### check_circle — チェック済み

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

#### warning — 警告

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

#### ban — 禁止

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

### 2.4 プロセス・フロー

| 名前 | shapeType | 用途 | 推奨サイズ | パターン |
|------|-----------|------|----------|---------|
| `process` | `FLOW_CHART_PROCESS` | 処理ステップ | 0.5" | 単一 |
| `decision` | `FLOW_CHART_DECISION` | 判断・分岐 | 0.5" | 単一 |
| `start_end` | `FLOW_CHART_TERMINATOR` | 開始/終了 | 0.5" | 単一 |
| `manual_input` | `FLOW_CHART_MANUAL_INPUT` | ユーザー入力 | 0.5" | 単一 |
| `connector` | `FLOW_CHART_CONNECTOR` | 接続点 | 0.3" | 単一 |
| `preparation` | `FLOW_CHART_PREPARATION` | 準備・セットアップ | 0.5" | 単一 |

#### process — 処理

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

#### decision — 判断

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

#### start_end — 開始/終了

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

#### manual_input — ユーザー入力

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

#### connector — 接続点

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

#### preparation — 準備

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

### 2.5 ビジネス・ユーザー

| 名前 | shapeType | 用途 | 推奨サイズ | パターン |
|------|-----------|------|----------|---------|
| `user` | `ELLIPSE` + `TRAPEZOID` | ユーザー・人物 | 0.5" | 複合 |
| `team` | 複数 user | チーム | 1.2" | 複合 |
| `building` | `RECTANGLE` + `TRIANGLE` | 企業・オフィス | 0.6" | 複合 |
| `handshake` | `CURVED_RIGHT_ARROW` x2 | パートナーシップ | 0.6" | 複合 |
| `money` | `ELLIPSE` + text "$"/"¥" | コスト・料金 | 0.4" | シェイプ＋テキスト |
| `chart_up` | `RIGHT_TRIANGLE` | 成長・上昇 | 0.5" | 単一 |
| `target` | `DONUT` + `ELLIPSE` | 目標・ターゲット | 0.5" | 複合 |

#### user — ユーザー（複合）

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

#### team — チーム

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

#### building — ビル/企業（複合）

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

#### handshake — パートナーシップ（複合）

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

#### money — コスト

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

#### chart_up — 成長

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

#### target — ターゲット（複合）

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

### 2.6 テクノロジー

| 名前 | shapeType | 用途 | 推奨サイズ | パターン |
|------|-----------|------|----------|---------|
| `api` | `ROUND_RECTANGLE` + text "API" | API エンドポイント | 0.5" | シェイプ＋テキスト |
| `microservice` | `HEXAGON` + text | マイクロサービス | 0.5" | シェイプ＋テキスト |
| `container` | `CUBE` | コンテナ・Docker | 0.5" | 単一 |
| `queue` | `CHEVRON` x3 | メッセージキュー | 0.6" | 複合 |
| `gear` | `STAR_8` | 設定・エンジン | 0.5" | 単一 |
| `code` | `FOLDED_CORNER` | コード・スクリプト | 0.5" | 単一 |
| `terminal` | `ROUND_RECTANGLE` + text "> _" | CLI・ターミナル | 0.6" | シェイプ＋テキスト |

#### api — API エンドポイント

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

#### microservice — マイクロサービス

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

#### container — コンテナ

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

#### queue — メッセージキュー（複合）

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

#### gear — 設定・エンジン

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

#### code — コード/スクリプト

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

#### terminal — ターミナル

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

### 2.7 ステータス・インジケーター

| 名前 | shapeType | 用途 | デフォルトカラー | パターン |
|------|-----------|------|--------------|---------|
| `success` | `ELLIPSE` + "✓" | 成功 | `C.success` (green) | シェイプ＋テキスト |
| `error` | `ELLIPSE` + "✗" | エラー | `C.alertRed` | シェイプ＋テキスト |
| `warning` | `TRIANGLE` + "!" | 警告 | `C.cautionYellow` | シェイプ＋テキスト |
| `info` | `ELLIPSE` + "i" | 情報 | `C.primary` (blue) | シェイプ＋テキスト |
| `pending` | `DONUT` | 処理中 | `C.accent` | 単一 |
| `star` | `STAR_5` | お気に入り・重要 | `C.cautionYellow` | 単一 |

> **注意**: `success` は `check_circle`（2.3節）と同一実装。`warning` も 2.3 節と同一。
> ここではステータス表示に特化した用途でのカラーデフォルトを示す。

#### error — エラー

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

#### info — 情報

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

#### pending — 処理中

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

#### star — 重要

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

## 3. 複合ピクトグラムの構築ガイドライン

### 3.1 設計原則

複合ピクトグラム（2つ以上のシェイプの組み合わせ）を構築する際の原則:

1. **シェイプ数は最大3つ** — それ以上は視覚的に複雑になりすぎる
2. **必ず `group_objects()` でグループ化** — 移動・回転を一括操作可能にする
3. **Z-order に注意** — 後から追加したシェイプが前面に来る（先に背景を追加）
4. **サイズは比率で計算** — `size` パラメータに対する比率でサブシェイプの座標を算出
5. **ラベルはグループ外** — ラベルテキストはグループに含めない（グループ後に追加）

### 3.2 構築テンプレート

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

### 3.3 サーバーラック（応用例）

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

## 4. テーマカラーの適用

### 4.1 セマンティックカラーマッピング

ピクトグラムの色はコンテンツの文脈に応じて使い分ける。テーマの `C` オブジェクトのセマンティックカラーを使用する。

| ピクトグラムの文脈 | 使用カラー | HEX（scalar テーマ） | 例 |
|---|---|---|---|
| 自社製品 | `C.primary` | `#2673BB` (blue) | ScalarDB, ScalarDL のアイコン |
| 外部システム | `C.textMuted` | `#666666` (gray) | PostgreSQL, MySQL, Cassandra |
| ユーザー/クライアント | `C.cautionYellow` | `#BE9000` (orange) | ブラウザ、モバイルアプリ |
| 成功・正常フロー | `C.success` | `#63C045` (green) | 正常パス、合格 |
| エラー・障害 | `C.alertRed` | `#F4CCCC` (red) | 障害パス、エラー |
| 新機能・アクセント | `C.accent` | `#0985FC` (cyan/blue) | 新機能ハイライト |
| 補助要素 | `C.surfaceLight` | `#F0F4F8` (light gray) | 背景ゾーン、枠 |

### 4.2 塗りと線のルール

| スタイル | 用途 | 設定方法 |
|---------|------|---------|
| **ソリッド塗り** | メインのピクトグラム | `fill=c, border_color=c`（同色ボーダー） |
| **アウトライン** | 補助的な要素 | `border_color=c` のみ（`fill=None`） |
| **薄い塗り + 濃いボーダー** | 強調したい補助要素 | `fill=C.surfaceLight, border_color=c` |
| **ダーク背景上** | 背景が暗いスライド | `fill=C.background`（白）+ `border_color=c` |
| **グレー背景上** | 灰色の背景ゾーン内 | `fill=C.background`（白）+ `border_color=C.primary` |

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

### 4.3 コントラスト要件

WCAG AA 準拠（コントラスト比 4.5:1 以上）を維持する:

| 背景色 | テキスト/アイコン色 | コントラスト比 | 判定 |
|--------|-------------------|-------------|------|
| `#FFFFFF` (white) | `C.primary` (#2673BB) | 5.2:1 | OK |
| `#FFFFFF` (white) | `C.textMuted` (#666666) | 5.7:1 | OK |
| `#FFFFFF` (white) | `C.success` (#63C045) | 3.3:1 | NG — テキストには不可 |
| `C.primary` (#2673BB) | `#FFFFFF` (white) | 5.2:1 | OK |
| `C.surfaceLight` (#F0F4F8) | `C.primary` (#2673BB) | 4.6:1 | OK |

> **重要**: `C.success`（緑）はシェイプの塗り色としては使用可能だが、その上のテキストは白を使用すること。テキスト色として単独使用はコントラスト不足になる場合がある。

---

## 5. サイズガイドライン

### 5.1 用途別推奨サイズ

| 用途 | 推奨サイズ | 最小サイズ | 備考 |
|------|----------|----------|------|
| インライン（テキスト横） | 0.3"-0.4" | 0.25" | テキストの行高に合わせる |
| カード内アイコン | 0.4"-0.6" | 0.35" | カード幅の 20-30% |
| グリッドアイコン | 0.5"-0.7" | 0.4" | グリッドセル幅の 25-35% |
| メインビジュアル | 0.8"-1.2" | 0.6" | スライド中央の主要要素 |
| ヒーローアイコン | 1.5"-2.0" | 1.0" | タイトルスライド等の大型アイコン |

### 5.2 Google Slides 座標系での注意

Google Slides の座標系は **10.0" x 5.625"**（PowerPoint の 0.75 倍）。推奨サイズは全てこの座標系でのインチ値。

```python
# サイズ計算のヘルパー
SLIDE_W = 10.0   # inches
SLIDE_H = 5.625  # inches

def relative_size(base_size, scale=1.0):
    """基準サイズからスケール係数で算出する。"""
    return base_size * scale
```

### 5.3 内部テキストのフォントサイズ目安

シェイプ内にテキストを配置する場合のフォントサイズ:

| シェイプサイズ | テキスト1文字 | テキスト2-3文字 | テキスト4文字以上 |
|-------------|-------------|--------------|---------------|
| 0.3" | 12pt | 8pt | 使用不可 |
| 0.4" | 16pt | 10pt | 8pt |
| 0.5" | 18pt | 12pt | 9pt |
| 0.6" | 22pt | 14pt | 10pt |
| 0.8" | 28pt | 18pt | 12pt |
| 1.0" | 36pt | 22pt | 14pt |

> **最小フォントサイズ**: ピクトグラム内テキストは **8pt 以上** を厳守（7pt 未満は視認性が著しく低下する）。

---

## 6. グリッドレイアウトパターン

### 6.1 アイコングリッド (2x3)

2行 x 3列のピクトグラムグリッド。各セルにアイコン＋タイトル＋説明を配置する。

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

### 使用例

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

### 6.2 横並びアイコン (1xN)

1行に N 個のピクトグラムを水平配置する。ステップ表示や比較に使用。

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

### 使用例

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

### 6.3 フローチャートとピクトグラムの組み合わせ

フローチャートのノードをピクトグラムに置き換える応用パターン。

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

## 7. スライドタイプとの対応

各スライドタイプでよく使用されるピクトグラムの一覧。コンポーザ関数からの参照に使用する。

| スライドタイプ | 推奨ピクトグラム | 用途 |
|---|---|---|
| `icon_grid` | 全カテゴリから選択 | グリッド内のアイコン |
| `architecture` | database, cloud, server, container, api, firewall, load_balancer | アーキテクチャ図のノード |
| `product_overview` | target, gear, check_circle, star, shield | 製品特徴のアイコン |
| `feature_matrix` | check_circle, error, warning, ban | 機能有無の表示 |
| `security_compliance` | shield, lock, key, check_circle, ban | セキュリティ要素 |
| `deployment_steps` | process, gear, cloud, container, code, terminal | デプロイ手順 |
| `ecosystem` | network, handshake, api, cloud, microservice | エコシステム連携 |
| `data_flow` | database, queue, cache, process, connector | データフロー図 |
| `multi_cloud` | cloud（複数色）, database, server | マルチクラウド構成 |
| `comparison` | check_circle, error, star | 比較表のマーカー |
| `kpi_dashboard` | chart_up, money, target, success | KPIカードのアイコン |
| `timeline` | process, start_end, decision | タイムラインのマーカー |

### スライドタイプごとの配色パターン

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

## 8. Unicode テキストアイコン（簡易代替）

シェイプを使わずに、テキストランに Unicode 文字を含めることで簡易的なアイコンを表現する方法。シェイプのピクトグラムほど自由度はないが、テキスト中にインラインでアイコンを挿入したい場合に有用。

### 8.1 推奨 Unicode アイコン一覧

| 文字 | Unicode | 用途 | フォント互換性 |
|------|---------|------|------------|
| ✓ | U+2713 | 成功・対応 | 高 |
| ✗ | U+2717 | 失敗・非対応 | 高 |
| ● | U+25CF | マーカー・ドット | 高 |
| ○ | U+25CB | 空マーカー | 高 |
| ▶ | U+25B6 | 再生・次へ | 高 |
| ◆ | U+25C6 | 強調マーカー | 高 |
| ★ | U+2605 | 重要・お気に入り | 高 |
| ☆ | U+2606 | 未評価 | 高 |
| ⚡ | U+26A1 | 高速・パフォーマンス | 中 |
| ⚙ | U+2699 | 設定・ギア | 中 |
| ⬆ | U+2B06 | 上昇・改善 | 高 |
| ⬇ | U+2B07 | 下降・削減 | 高 |
| → | U+2192 | フロー・方向 | 高 |
| ∞ | U+221E | 無制限 | 高 |

### 8.2 テキスト内での使用例

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

### 8.3 フォント互換性の注意

- **高互換性**（Arial, Noto Sans JP で表示可能）: ✓ ✗ ● ○ ▶ ◆ ★ → ∞
- **中互換性**（一部フォントで文字化けの可能性）: ⚡ ⚙ 🔒 🔑
- **低互換性**（カラー絵文字、環境依存）: 🚀 💡 📊 🎯

> **推奨**: テキスト内アイコンには高互換性の Unicode 文字を使用する。中・低互換性の文字はシェイプピクトグラムで代替すること。

---

## 9. API リクエスト数の最適化

### 9.1 リクエスト数の目安

| パターン | 1個あたりのリクエスト数 | 備考 |
|---------|---------------------|------|
| 単一シェイプ | 2-3 | createShape + fill + border |
| シェイプ＋テキスト | 5-7 | shape + fill + textbox + insert + style |
| 複合（2シェイプ） | 6-8 | shape x2 + fills + groupObjects |
| 複合（3シェイプ） | 9-12 | shape x3 + fills + groupObjects |
| ラベル付き | +4 | textbox + insert + style + paragraph |

### 9.2 最適化のヒント

1. **グリッド内は単一シェイプを優先** — 6セルのグリッドで複合ピクトグラムを使うと 50+ リクエストになる
2. **500リクエスト制限に注意** — batchUpdate の推奨チャンクサイズは 500。ピクトグラムの多用で超過しないこと
3. **ラベルの省略** — グリッド下のテキストで十分な場合、ピクトグラム自体のラベルは省略可能
4. **Unicode アイコンの活用** — 単純なマーカー（✓/✗）はテキストで代替してリクエスト数を削減

### 9.3 リクエスト数の見積もり

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

## 10. 使用上の注意

### 10.1 一般的な注意事項

1. **過度な複合化を避ける** — 3シェイプ以上の複合ピクトグラムは複雑になりすぎる。それ以上の精密さが必要な場合は外部画像（Drive API 経由のアップロード）を検討すること

2. **テキスト内アイコン** — Unicode 記号（✓ ✗ ● ★ 等）をテキストランに含めることで、シェイプ不要の簡易アイコンも実現可能。セクション 8 を参照

3. **一貫性の維持** — 同一スライド内では同じ構築パターンで統一する。単一シェイプと複合シェイプを混在させない

4. **コントラスト確保** — WCAG AA 準拠（4.5:1 以上）。白背景にはアウトライン付き or ソリッド塗り、ダーク背景には白塗り + カラーボーダー

5. **グループ化の徹底** — 複合ピクトグラムは必ず `group_objects()` でグループ化する。グループ化しないと移動時にバラバラになる

### 10.2 パフォーマンスの注意

6. **API リクエスト数** — ピクトグラムはシェイプ作成 + スタイル設定で複数リクエストを消費する。大量のピクトグラムを使用する場合は batchUpdate のチャンクサイズ（500件）に注意

7. **レンダリング負荷** — 多数のシェイプはブラウザでのレンダリングが重くなる。1スライドあたりのシェイプ数は **50個以下** を推奨

### 10.3 デザインの注意

8. **同一サイズの使用** — グリッド内では全ピクトグラムを同じ `size` パラメータで作成する。サイズが不揃いだと視覚的にバランスが崩れる

9. **余白の確保** — ピクトグラム間には最低 0.15" の余白を確保する。密集配置は視認性を低下させる

10. **色の統一** — 1スライド内で使用する色は **3色以下**（60-30-10 ルール）。ピクトグラムの色もこのルールに従う

---

## 付録 A. ピクトグラム対応表（クイックリファレンス）

| タイプ名 | shapeType | パターン | デフォルト色 | 推奨サイズ |
|---------|-----------|---------|------------|----------|
| `database` | CAN | 単一 | primary | 0.5" |
| `storage` | FLOW_CHART_MAGNETIC_DISK | 単一 | primary | 0.5" |
| `document` | FLOW_CHART_DOCUMENT | 単一 | primary | 0.5" |
| `multi_document` | FLOW_CHART_MULTIDOCUMENT | 単一 | primary | 0.6" |
| `cache` | FLOW_CHART_INTERNAL_STORAGE | 単一 | accent | 0.5" |
| `cloud` | CLOUD | 単一 | primary | 0.6" |
| `cloud_callout` | CLOUD_CALLOUT | 単一 | calloutBg | 0.6" |
| `network` | HEXAGON | S+T | primary | 0.5" |
| `server` | ROUND_RECT + RECT x3 + ELLIPSE | 複合 | textMuted | 0.5" |
| `load_balancer` | TRAPEZOID | 単一 | accent | 0.6" |
| `firewall` | RECT + LIGHTNING_BOLT | 複合 | alertRed | 0.6" |
| `shield` | PENTAGON | 単一 | primary | 0.5" |
| `lock` | ROUND_RECT x2 + ELLIPSE | 複合 | primary | 0.5" |
| `key` | ELLIPSE + RECTANGLE | 複合 | cautionYellow | 0.5" |
| `check_circle` | ELLIPSE + "✓" | S+T | success | 0.4" |
| `warning` | TRIANGLE + "!" | S+T | cautionYellow | 0.4" |
| `ban` | NO_SMOKING | 単一 | alertRed | 0.4" |
| `process` | FLOW_CHART_PROCESS | 単一 | primary | 0.5" |
| `decision` | FLOW_CHART_DECISION | 単一 | accent | 0.5" |
| `start_end` | FLOW_CHART_TERMINATOR | 単一 | primary | 0.5" |
| `manual_input` | FLOW_CHART_MANUAL_INPUT | 単一 | cautionYellow | 0.5" |
| `connector` | FLOW_CHART_CONNECTOR | 単一 | border | 0.3" |
| `preparation` | FLOW_CHART_PREPARATION | 単一 | surfaceLight | 0.5" |
| `user` | ELLIPSE + TRAPEZOID | 複合 | primary | 0.5" |
| `team` | user x3 | 複合 | primary | 1.2" |
| `building` | RECT + TRIANGLE + RECT x4 | 複合 | textMuted | 0.6" |
| `handshake` | CURVED_*_ARROW x2 | 複合 | primary | 0.6" |
| `money` | ELLIPSE + "¥" | S+T | success | 0.4" |
| `chart_up` | RIGHT_TRIANGLE | 単一 | success | 0.5" |
| `target` | DONUT + ELLIPSE | 複合 | alertRed | 0.5" |
| `api` | ROUND_RECT + "API" | S+T | primary | 0.5" |
| `microservice` | HEXAGON + text | S+T | accent | 0.5" |
| `container` | CUBE | 単一 | accent | 0.5" |
| `queue` | CHEVRON x3 | 複合 | accent | 0.6" |
| `gear` | STAR_8 + ELLIPSE | 複合 | textMuted | 0.5" |
| `code` | FOLDED_CORNER + "{ }" | S+T | surfaceLight | 0.5" |
| `terminal` | ROUND_RECT + "> _" | S+T | dark | 0.6" |
| `success` | ELLIPSE + "✓" | S+T | success | 0.4" |
| `error` | ELLIPSE + "✗" | S+T | alertRed | 0.4" |
| `info` | ELLIPSE + "i" | S+T | primary | 0.4" |
| `pending` | DONUT | 単一 | accent | 0.4" |
| `star` | STAR_5 | 単一 | cautionYellow | 0.4" |

> **凡例**: S+T = シェイプ＋テキスト、複合 = 複数シェイプ（group_objects 必要）

---

## 付録 B. shapeType 選定チートシート

ピクトグラム設計時に、概念から shapeType を選ぶための逆引き表。

| 表現したい概念 | 推奨 shapeType | 代替候補 |
|--------------|---------------|---------|
| データベース | `CAN` | `FLOW_CHART_MAGNETIC_DISK` |
| ファイル/文書 | `FLOW_CHART_DOCUMENT` | `FOLDED_CORNER` |
| クラウド | `CLOUD` | `CLOUD_CALLOUT` |
| サーバー/マシン | `ROUND_RECTANGLE`（複合） | `RECTANGLE` |
| セキュリティ | `PENTAGON` | `FLOW_CHART_PREPARATION` |
| 認証/暗号 | `ROUND_RECTANGLE`（複合でロック） | — |
| 処理ステップ | `FLOW_CHART_PROCESS` | `RECTANGLE` |
| 判断/分岐 | `FLOW_CHART_DECISION` | `DIAMOND` |
| 人物 | `ELLIPSE` + `TRAPEZOID`（複合） | — |
| 企業/建物 | `RECTANGLE` + `TRIANGLE`（複合） | — |
| API/サービス | `ROUND_RECTANGLE` + text | `HEXAGON` + text |
| コンテナ | `CUBE` | `ROUND_RECTANGLE` |
| 設定/ギア | `STAR_8` | `SUN` |
| 成功 | `ELLIPSE` + "✓" | Unicode ✓ |
| エラー | `ELLIPSE` + "✗" | `NO_SMOKING` |
| 警告 | `TRIANGLE` + "!" | Unicode ⚠ |
| 方向/フロー | `RIGHT_ARROW` 系 | `CHEVRON` |
| コスト/金額 | `ELLIPSE` + "¥"/"$" | — |
| ネットワーク | `HEXAGON` | `OCTAGON` |
| キュー/ストリーム | `CHEVRON`（複合） | `RIGHT_ARROW` |
| 目標/ターゲット | `DONUT` + `ELLIPSE`（複合） | `STAR_5` |
| 重要/優先 | `STAR_5` | `STARBURST` |
| 禁止 | `NO_SMOKING` | `MATH_MULTIPLY` |
| 高速/パフォーマンス | `LIGHTNING_BOLT` | Unicode ⚡ |
