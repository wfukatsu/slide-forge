*[English](db-middleware.md)*

# コンポーザー仕様: db-middleware カテゴリ

db-middleware カテゴリ 4 タイプのレンダリング仕様。データフロー・マルチクラウド・ベンチマーク・マイグレーションの DB/ミドルウェア固有スライドを構築する。

> **規約**: `C` = 色定数, `L` = レイアウト定数, `sb` = SlideBuilder インスタンス。
> 座標単位はインチ。ページサイズ: 10.0" x 5.625"。

### クラウドアイコン

`assets/shared/cloud-icons/` にプロバイダ別のアイコンを格納。コンポーザーから `add_image_from_asset()` で参照する。

```
assets/shared/cloud-icons/
  aws/       — AWS サービスアイコン
  gcp/       — GCP サービスアイコン
  azure/     — Azure サービスアイコン
  generic/   — 汎用インフラアイコン
```

```python
# クラウドアイコン挿入パターン（scripts/cloud_icons.py を使う）
def _place_cloud_icon(sb, slide_id, icon, x, y, size=0.45):
    """クラウドアイコンを配置する。icon が None なら何も置かない。

    icon: "aws:ec2" / "s3" / "Cloud SQL" のいずれか（マニフェストの名前）。
          旧仕様の "aws/ec2.png" 形式も受け付けて名前に読み替える。

    名前が見つからない場合は **エラーで落とす**。黙ってバッジに落とすと
    「アイコンが出ない」だけの分かりにくい失敗になるため。
    """
    if not icon:
        return
    if "/" in icon:                      # 旧仕様 "aws/ec2.png" → "aws:ec2"
        vendor, base = icon.split("/", 1)
        icon = f"{vendor}:{base.rsplit('.', 1)[0]}"
    sb.add_cloud_icon(slide_id, icon, x, y, size, label="")
```

> `sb` は `CloudIconMixin` を混ぜた SlideBuilder。名前の探し方・ライセンス上の
> 制約は `references/cloud-icons.md` を参照。ラベルを出さない場合は
> `label=""` を明示する（既定は正式名称が入る）。

---

## 1. compose_data_flow

データフロー（ソース → 処理 → ストア → 出力）をノード+矢印で表示するスライド。

- **マスター**: CONTENT
- **パターン**: Pattern 10/11 (Flow / Decision Flow)
- **レイアウト**: 水平フローダイアグラム + クラウドアイコン付きノード

### コンテンツ領域

| 要素 | X | Y | W | H | 備考 |
|------|----:|----:|----:|----:|------|
| タイトル | 0.323 | 0.303 | 9.354 | 0.437 | CONTENT 標準 |
| フロー領域 | 0.500 | 0.900 | 9.000 | 4.100 | ノード + コネクタ |

### ノードタイプ別スタイル

| type | シェイプ | 色 | 用途 |
|------|---------|-----|------|
| `source` | ROUND_RECTANGLE | `C["accent"]` | データソース（DB、API） |
| `process` | RECTANGLE | `C["primary"]` | Scalar 製品（変換・処理） |
| `store` | ROUND_RECTANGLE | `C["primaryDark"]` | データストア |
| `output` | ROUND_RECTANGLE | `C["success"]` | 出力先（アプリ、レポート） |

### Python コードテンプレート

```python
def compose_data_flow(sb, slide_id, content, theme, page_num, total_pages=None):
    """data_flow スライドを構築する。

    content schema:
        title: str
        nodes: list[{name: str, type: "source"|"process"|"store"|"output",
                      icon: str (opt) — クラウドアイコンパス}]
        flows: list[{from: str, to: str, label: str (opt),
                      style: "solid"|"dashed" (opt)}]
    """
    C = theme["colors"]

    # --- マスター適用 ---
    apply_master_content(sb, theme, slide_id, page_num, total_pages)
    apply_action_title(sb, theme, slide_id, content["title"])

    # --- ノードレイアウト計算 ---
    nodes = content.get("nodes", [])
    flows = content.get("flows", [])
    n = len(nodes)
    if n == 0:
        return

    # 水平配置の座標計算
    flow_x = 0.500
    flow_y = 1.500
    flow_w = 9.000
    box_w = 1.600
    box_h = 1.200
    gap = (flow_w - box_w * n) / max(n - 1, 1) if n > 1 else 0

    # ノードタイプ → 色マッピング
    type_colors = {
        "source":  C["accent"],
        "process": C["primary"],
        "store":   C["primaryDark"],
        "output":  C["success"],
    }
    # ノードタイプ → シェイプマッピング
    type_shapes = {
        "source":  "ROUND_RECTANGLE",
        "process": "RECTANGLE",
        "store":   "ROUND_RECTANGLE",
        "output":  "ROUND_RECTANGLE",
    }

    node_positions = {}  # name -> (cx, cy, x, y)

    for i, node in enumerate(nodes):
        nx = flow_x + i * (box_w + gap)
        ny = flow_y
        fill = type_colors.get(node["type"], C["primary"])
        shape = type_shapes.get(node["type"], "ROUND_RECTANGLE")

        # ノード矩形
        sb.add_shape(slide_id, shape, nx, ny, box_w, box_h, fill=fill)

        # クラウドアイコン（ノード上部に配置）
        icon_path = node.get("icon")
        icon_size = 0.45
        icon_x = nx + (box_w - icon_size) / 2
        icon_y = ny + 0.12
        _place_cloud_icon(sb, slide_id, icon_path, icon_x, icon_y, icon_size)

        # ノード名テキスト（アイコン下）
        text_y = icon_y + icon_size + 0.05
        sb.add_text(slide_id, node["name"],
                    nx + 0.08, text_y, box_w - 0.16, box_h - (text_y - ny) - 0.10,
                    font_size=12, bold=True,
                    color={"red": 1, "green": 1, "blue": 1},
                    alignment="CENTER", valign="TOP")

        center_x = nx + box_w / 2
        center_y = ny + box_h / 2
        node_positions[node["name"]] = (center_x, center_y, nx, ny)

    # --- フロー矢印 ---
    for flow in flows:
        from_pos = node_positions.get(flow["from"])
        to_pos = node_positions.get(flow["to"])
        if not from_pos or not to_pos:
            continue

        fx, fy, fnx, fny = from_pos
        tx, ty, tnx, tny = to_pos
        is_dashed = flow.get("style") == "dashed"

        # 水平方向の矢印（ノード右端 → 次ノード左端）
        start_x = fnx + box_w
        start_y = fy
        end_x = tnx
        end_y = ty

        sb.add_connector(slide_id, start_x, start_y, end_x, end_y,
                         color=C["textMuted"], weight=2.0,
                         end_arrow="FILL_ARROW",
                         dash_style="DASH" if is_dashed else None)

        # フローラベル
        if flow.get("label"):
            mid_x = (start_x + end_x) / 2
            mid_y = start_y - 0.25
            sb.add_text(slide_id, flow["label"],
                        mid_x - 0.50, mid_y, 1.00, 0.20,
                        font_size=9, color=C["textSecondary"],
                        alignment="CENTER", valign="MIDDLE")

    # --- 凡例（下部）---
    legend_y = flow_y + box_h + 0.50
    legend_items = [
        ("source", "データソース", C["accent"]),
        ("process", "Scalar 処理", C["primary"]),
        ("store", "データストア", C["primaryDark"]),
        ("output", "出力先", C["success"]),
    ]
    # 実際に使われたタイプのみ表示
    used_types = {n["type"] for n in nodes}
    legend_items = [item for item in legend_items if item[0] in used_types]

    legend_x = 0.500
    for item_type, label, color in legend_items:
        sb.add_rect(slide_id, legend_x, legend_y + 0.03, 0.20, 0.15, fill=color)
        sb.add_text(slide_id, label,
                    legend_x + 0.28, legend_y, 1.00, 0.20,
                    font_size=9, color=C["textSecondary"],
                    alignment="START", valign="MIDDLE")
        legend_x += 1.50
```

### デザインノート

- ノード数は 3-5 を想定。6 以上の場合は 2 行配置に変更するか、`box_w` を縮小
- `process` ノード（Scalar 製品）は角丸なしの RECTANGLE で他タイプと視覚的に区別
- dashed コネクタはオプション経路（エラーパス等）に使用
- 技術図の色規約: Blue=Scalar, Gray=外部, Orange=ユーザー/クライアント, Green=正常フロー

---

## 2. compose_multi_cloud

マルチクラウド構成（AWS / GCP / Azure + Scalar レイヤ）を表示するスライド。

- **マスター**: CONTENT
- **パターン**: Pattern 10 (Flow) + クラウドアイコン
- **レイアウト**: 上段=Scalar レイヤ、下段=クラウドプロバイダ列（2-3列）

### コンテンツ領域

| 要素 | X | Y | W | H | 備考 |
|------|----:|----:|----:|----:|------|
| タイトル | 0.323 | 0.303 | 9.354 | 0.437 | CONTENT 標準 |
| Scalar レイヤ | 0.500 | 0.900 | 9.000 | 1.100 | 中央帯、primary 背景 |
| クラウド列 | 0.500 | 2.250 | 9.000 | 2.750 | プロバイダ別カード |

### Python コードテンプレート

```python
def compose_multi_cloud(sb, slide_id, content, theme, page_num, total_pages=None):
    """multi_cloud スライドを構築する。

    content schema:
        title: str
        clouds: list[{provider: "aws"|"gcp"|"azure"|"onpremise",
                       services: list[{name: str, icon: str (opt)}]}]
        scalarLayer: {components: list[str]}
    """
    C = theme["colors"]

    # --- マスター適用 ---
    apply_master_content(sb, theme, slide_id, page_num, total_pages)
    apply_action_title(sb, theme, slide_id, content["title"])

    # --- Scalar 統一レイヤ（上段帯）---
    scalar_layer = content.get("scalarLayer", {})
    components = scalar_layer.get("components", [])

    layer_x = 0.500
    layer_y = 0.900
    layer_w = 9.000
    layer_h = 1.100

    # 帯背景
    sb.add_rounded_rect(slide_id, layer_x, layer_y, layer_w, layer_h,
                        fill=C["primary"])

    # Scalar ラベル
    sb.add_text(slide_id, "Scalar Layer",
                layer_x + 0.15, layer_y + 0.05, 2.000, 0.30,
                font_size=12, bold=True, color=C["textOnDark"],
                alignment="START", valign="MIDDLE")

    # コンポーネントを横並び
    n_comp = len(components)
    if n_comp > 0:
        comp_y = layer_y + 0.40
        comp_h = 0.50
        comp_gap = 0.15
        comp_w = (layer_w - 0.30 - comp_gap * (n_comp - 1)) / n_comp

        for i, comp_name in enumerate(components):
            comp_x = layer_x + 0.15 + i * (comp_w + comp_gap)
            sb.add_rounded_rect(slide_id, comp_x, comp_y, comp_w, comp_h,
                                fill=C["primaryDark"])
            sb.add_text(slide_id, comp_name,
                        comp_x + 0.08, comp_y, comp_w - 0.16, comp_h,
                        font_size=11, bold=True, color=C["textOnDark"],
                        alignment="CENTER", valign="MIDDLE")

    # --- 下向き矢印（Scalar レイヤ → クラウド列）---
    arrow_y1 = layer_y + layer_h
    arrow_y2 = layer_y + layer_h + 0.25
    clouds = content.get("clouds", [])
    n_clouds = len(clouds)

    # プロバイダ色マッピング
    provider_colors = {
        "aws":       {"bg": "#FF9900", "text": "#232F3E"},
        "gcp":       {"bg": "#4285F4", "text": "#FFFFFF"},
        "azure":     {"bg": "#0078D4", "text": "#FFFFFF"},
        "onpremise": {"bg": "#6B7280", "text": "#FFFFFF"},
    }

    if n_clouds == 0:
        return

    # --- クラウドプロバイダ列 ---
    cloud_area_x = 0.500
    cloud_area_y = 2.250
    cloud_area_w = 9.000
    cloud_area_h = 2.750
    cloud_gap = 0.300
    cloud_w = (cloud_area_w - cloud_gap * (n_clouds - 1)) / n_clouds

    for i, cloud in enumerate(clouds):
        cx = cloud_area_x + i * (cloud_w + cloud_gap)
        cy = cloud_area_y
        provider = cloud.get("provider", "onpremise")
        pcolor = provider_colors.get(provider, provider_colors["onpremise"])
        bg_rgb = hex_to_rgb(pcolor["bg"])
        text_rgb = hex_to_rgb(pcolor["text"])

        # 下向き矢印（レイヤからカードへ）
        arrow_cx = cx + cloud_w / 2
        sb.add_connector(slide_id,
                         arrow_cx, arrow_y1, arrow_cx, cy,
                         color=C["textMuted"], weight=1.5,
                         end_arrow="FILL_ARROW")

        # プロバイダカード
        sb.add_rounded_rect(slide_id, cx, cy, cloud_w, cloud_area_h,
                            fill=C["background"],
                            border_color=bg_rgb)

        # プロバイダヘッダーバー
        header_h = 0.400
        sb.add_rect(slide_id, cx, cy, cloud_w, header_h, fill=bg_rgb)

        # プロバイダアイコン + 名前
        # クラウド全体を表すアイコンは AWS にしか無い。GCP / Azure は
        # ベンダー色の見出しだけで示す（_place_cloud_icon は None で何もしない）
        icon_path = {"aws": "aws:aws-cloud"}.get(provider)
        icon_size = 0.28
        _place_cloud_icon(sb, slide_id, icon_path,
                          cx + 0.10, cy + (header_h - icon_size) / 2,
                          icon_size)
        provider_label = provider.upper()
        sb.add_text(slide_id, provider_label,
                    cx + 0.10 + icon_size + 0.10, cy,
                    cloud_w - icon_size - 0.35, header_h,
                    font_size=13, bold=True, color=text_rgb,
                    alignment="START", valign="MIDDLE")

        # サービス一覧
        services = cloud.get("services", [])
        svc_y = cy + header_h + 0.15
        for j, svc in enumerate(services):
            sy = svc_y + j * 0.45
            svc_icon = svc.get("icon")
            svc_icon_size = 0.30

            if svc_icon:
                _place_cloud_icon(sb, slide_id, svc_icon,
                                  cx + 0.15, sy, svc_icon_size)
            sb.add_text(slide_id, svc["name"],
                        cx + 0.15 + svc_icon_size + 0.10, sy,
                        cloud_w - svc_icon_size - 0.45, 0.30,
                        font_size=11, color=C["textPrimary"],
                        alignment="START", valign="MIDDLE")
```

### デザインノート

- クラウド数は 2-3 を想定（4 プロバイダ以上はカード幅が狭くなる）
- 各プロバイダのブランドカラーをヘッダーに使用し、視覚的に識別しやすくする
- Scalar レイヤを上段に配置することで「ベンダー非依存の統一レイヤ」を視覚的に表現
- サービスアイコンは `assets/shared/cloud-icons/{provider}/` から読み込み。アセットが無い場合はバッジにフォールバック

---

## 3. compose_benchmark

ベンチマーク・性能比較を横棒グラフで表示するスライド。

- **マスター**: CONTENT
- **パターン**: Pattern 4 (Bar Chart)
- **レイアウト**: 指標ごとの横棒グラフ（自社製品をハイライト）

### コンテンツ領域

| 要素 | X | Y | W | H | 備考 |
|------|----:|----:|----:|----:|------|
| タイトル | 0.323 | 0.303 | 9.354 | 0.437 | CONTENT 標準 |
| チャート領域 | 0.500 | 0.900 | 8.500 | 3.700 | 複数メトリクス |
| ソース | 0.500 | 4.750 | 9.000 | 0.300 | ベンチマーク出典 |

### Python コードテンプレート

```python
def compose_benchmark(sb, slide_id, content, theme, page_num, total_pages=None):
    """benchmark スライドを構築する。

    content schema:
        title: str
        metrics: list[{
            name: str,
            unit: str,
            results: list[{product: str, value: number, isOurs: bool (opt)}]
        }]
        source: str (opt)
    """
    C = theme["colors"]

    # --- マスター適用 ---
    apply_master_content(sb, theme, slide_id, page_num, total_pages)
    apply_action_title(sb, theme, slide_id, content["title"])

    # --- ベンチマーク棒グラフ ---
    metrics = content.get("metrics", [])
    n_metrics = len(metrics)
    if n_metrics == 0:
        return

    chart_x = 0.500
    chart_y = 0.900
    chart_w = 8.500
    has_source = bool(content.get("source"))
    chart_h = 3.700 if has_source else 4.100

    # メトリクスごとにセクション分割
    section_h = chart_h / n_metrics
    section_gap = 0.20  # メトリクス間のギャップ

    for mi, metric in enumerate(metrics):
        my = chart_y + mi * section_h
        results = metric.get("results", [])
        n_results = len(results)
        if n_results == 0:
            continue

        max_val = max(r["value"] for r in results) or 1

        # メトリクス名 + 単位
        sb.add_text(slide_id, f'{metric["name"]} ({metric["unit"]})',
                    chart_x, my, chart_w, 0.30,
                    font_size=12, bold=True, color=C["textTitle"],
                    alignment="START", valign="MIDDLE")

        # 横棒グラフ
        bar_y_start = my + 0.35
        bar_area_h = section_h - 0.35 - section_gap
        bar_h = min(bar_area_h / n_results * 0.75, 0.35)
        bar_gap = (bar_area_h - bar_h * n_results) / max(n_results, 1)

        label_w = 1.500  # 製品名ラベル幅
        bar_max_w = chart_w - label_w - 1.000  # 値ラベル分の余白

        for ri, result in enumerate(results):
            ry = bar_y_start + ri * (bar_h + bar_gap)
            is_ours = result.get("isOurs", False)
            bar_color = C["primary"] if is_ours else C["border"]
            text_color = C["textTitle"] if is_ours else C["textSecondary"]

            # 製品名ラベル
            sb.add_text(slide_id, result["product"],
                        chart_x, ry, label_w, bar_h,
                        font_size=11, bold=is_ours, color=text_color,
                        alignment="END", valign="MIDDLE")

            # 棒グラフ
            bar_w = (result["value"] / max_val) * bar_max_w
            bar_x = chart_x + label_w + 0.15
            sb.add_rounded_rect(slide_id, bar_x, ry, bar_w, bar_h,
                                fill=bar_color)

            # 値ラベル
            val_text = f'{result["value"]} {metric["unit"]}'
            sb.add_text(slide_id, val_text,
                        bar_x + bar_w + 0.08, ry, 1.000, bar_h,
                        font_size=10, bold=is_ours, color=bar_color,
                        alignment="START", valign="MIDDLE")

    # --- ソース出典 ---
    if has_source:
        sb.add_text(slide_id, f'Source: {content["source"]}',
                    0.500, 4.750, 9.000, 0.300,
                    font_size=9, color=C["textMuted"],
                    alignment="START", valign="MIDDLE")
```

### デザインノート

- メトリクス数は 1-3 を想定。4 以上は縦方向が密になるため、2 スライドに分割を推奨
- 自社製品（`isOurs: true`）は `C["primary"]`（Scalar Blue）、競合は `C["border"]`（グレー）で明確に区別
- 値ラベルをバー右端の外側に配置し、凡例への依存を排除（Tufte 原則: Data-Ink Ratio 最大化）
- ソース出典は 9pt でフッター直上に配置（データの信頼性担保）

---

## 4. compose_migration_path

マイグレーションパス（移行元 → ステップ群 → 移行先）を水平フロー+タイムラインで表示するスライド。

- **マスター**: CONTENT
- **パターン**: Pattern 10 (Flow) + Pattern 2 (H-Timeline)
- **レイアウト**: 左端=移行元、右端=移行先、中央=ステップチェーン

### コンテンツ領域

| 要素 | X | Y | W | H | 備考 |
|------|----:|----:|----:|----:|------|
| タイトル | 0.323 | 0.303 | 9.354 | 0.437 | CONTENT 標準 |
| 移行元ノード | 0.500 | 1.200 | 1.400 | 1.400 | 円形 or 角丸 |
| ステップチェーン | 2.200 | 1.500 | 5.600 | 3.200 | フロー + 詳細 |
| 移行先ノード | 8.100 | 1.200 | 1.400 | 1.400 | 円形 or 角丸 |

### Python コードテンプレート

```python
def compose_migration_path(sb, slide_id, content, theme, page_num, total_pages=None):
    """migration_path スライドを構築する。

    content schema:
        title: str
        from: {name: str, icon: str (opt)}
        to: {name: str, icon: str (opt)}
        steps: list[{name: str, description: str (opt), duration: str (opt)}]
    """
    C = theme["colors"]

    # --- マスター適用 ---
    apply_master_content(sb, theme, slide_id, page_num, total_pages)
    apply_action_title(sb, theme, slide_id, content["title"])

    # --- 移行元ノード ---
    from_node = content.get("from", {})
    from_x = 0.500
    from_y = 1.800
    node_w = 1.400
    node_h = 1.400

    # 移行元カード
    sb.add_rounded_rect(slide_id, from_x, from_y, node_w, node_h,
                        fill=C["backgroundAlt"],
                        border_color=C["border"])
    # アイコン
    from_icon = from_node.get("icon")
    icon_size = 0.45
    icon_x = from_x + (node_w - icon_size) / 2
    icon_y = from_y + 0.15
    _place_cloud_icon(sb, slide_id, from_icon, icon_x, icon_y, icon_size)
    # 名前
    sb.add_text(slide_id, from_node.get("name", ""),
                from_x + 0.08, from_y + 0.65, node_w - 0.16, 0.60,
                font_size=12, bold=True, color=C["textTitle"],
                alignment="CENTER", valign="TOP")

    # --- 移行先ノード ---
    to_node = content.get("to", {})
    to_x = 8.100
    to_y = 1.800

    # 移行先カード（primary ボーダーで強調）
    sb.add_rounded_rect(slide_id, to_x, to_y, node_w, node_h,
                        fill=C["surfaceLight"],
                        border_color=C["primary"])
    sb.add_rect(slide_id, to_x, to_y, node_w, 0.025, fill=C["primary"])
    # アイコン
    to_icon = to_node.get("icon")
    icon_x = to_x + (node_w - icon_size) / 2
    _place_cloud_icon(sb, slide_id, to_icon, icon_x, icon_y, icon_size)
    # 名前
    sb.add_text(slide_id, to_node.get("name", ""),
                to_x + 0.08, to_y + 0.65, node_w - 0.16, 0.60,
                font_size=12, bold=True, color=C["primary"],
                alignment="CENTER", valign="TOP")

    # --- 中央ステップチェーン ---
    steps = content.get("steps", [])
    n_steps = len(steps)
    if n_steps == 0:
        # ステップなし: 直接矢印
        sb.add_connector(slide_id,
                         from_x + node_w, from_y + node_h / 2,
                         to_x, to_y + node_h / 2,
                         color=C["primary"], weight=2.0,
                         end_arrow="FILL_ARROW")
        return

    # ステップ配置
    chain_x = 2.200
    chain_w = 5.600
    step_box_w = 1.200
    step_box_h = 0.600
    step_gap = (chain_w - step_box_w * n_steps) / max(n_steps - 1, 1) if n_steps > 1 else 0
    chain_center_y = from_y + node_h / 2

    # 移行元 → 最初のステップ 矢印
    first_step_x = chain_x
    sb.add_connector(slide_id,
                     from_x + node_w, chain_center_y,
                     first_step_x, chain_center_y,
                     color=C["textMuted"], weight=1.5,
                     end_arrow="FILL_ARROW")

    step_positions = []

    for i, step in enumerate(steps):
        sx = chain_x + i * (step_box_w + step_gap)
        sy = chain_center_y - step_box_h / 2

        # ステップ進行色（グラデーション: 淡→濃）
        t = i / max(n_steps - 1, 1)
        step_color_r = C["accent"]["red"] * (1 - t) + C["primary"]["red"] * t
        step_color_g = C["accent"]["green"] * (1 - t) + C["primary"]["green"] * t
        step_color_b = C["accent"]["blue"] * (1 - t) + C["primary"]["blue"] * t
        step_color = {"red": step_color_r, "green": step_color_g, "blue": step_color_b}

        # ステップボックス
        sb.add_shape(slide_id, "ROUND_RECTANGLE", sx, sy, step_box_w, step_box_h,
                     fill=step_color)

        # ステップ番号 + 名前
        step_label = f"{i + 1}. {step['name']}"
        sb.add_text(slide_id, step_label,
                    sx + 0.05, sy, step_box_w - 0.10, step_box_h,
                    font_size=11, bold=True,
                    color={"red": 1, "green": 1, "blue": 1},
                    alignment="CENTER", valign="MIDDLE")

        # 詳細テキスト（ボックスの下）
        desc = step.get("description", "")
        duration = step.get("duration", "")
        detail_parts = []
        if desc:
            detail_parts.append(desc)
        if duration:
            detail_parts.append(duration)
        if detail_parts:
            detail_text = " | ".join(detail_parts)
            sb.add_text(slide_id, detail_text,
                        sx - 0.10, sy + step_box_h + 0.10,
                        step_box_w + 0.20, 0.40,
                        font_size=9, color=C["textSecondary"],
                        alignment="CENTER", valign="TOP")

        step_positions.append((sx, sy))

        # ステップ間矢印
        if i > 0:
            prev_sx = step_positions[i - 1][0]
            sb.add_connector(slide_id,
                             prev_sx + step_box_w, chain_center_y,
                             sx, chain_center_y,
                             color=C["textMuted"], weight=1.5,
                             end_arrow="FILL_ARROW")

    # 最後のステップ → 移行先 矢印
    last_sx = step_positions[-1][0]
    sb.add_connector(slide_id,
                     last_sx + step_box_w, chain_center_y,
                     to_x, chain_center_y,
                     color=C["textMuted"], weight=1.5,
                     end_arrow="FILL_ARROW")
```

### デザインノート

- ステップ数は 3-5 を想定。2 以下は直接矢印+テキストで十分。6 以上はボックスが狭くなるため 2 行配置に変更
- ステップのグラデーション（accent → primary）で進行方向を視覚的に表現
- 移行先ノードは primary ボーダー + アクセントバーで「ゴール」を強調
- クラウドアイコンは `_place_cloud_icon()` で移行元/移行先に配置。例: `"aws/rds.png"` → `"gcp/cloud-spanner.png"`
- 詳細テキスト（description + duration）はステップ下に 9pt で配置。折り返し防止のため各 15 文字以内を推奨

---

## 共通事項

### CONTENT マスター座標（全コンポーザー共通）

```
タイトル:   (0.323, 0.303) w=9.354 h=0.437
Body 開始:  y=0.787
Body 終了:  y=5.208 (contentBottom)
フッター:   y=5.208 以下（ロゴ・著作権・ページ番号）
```

### クラウドアイコン統合パターン

| パターン | 使用場所 | アイコンサイズ | 備考 |
|---------|---------|:----------:|------|
| ノード内アイコン | data_flow ノード | 0.45" | ノード上部に中央配置 |
| カードヘッダーアイコン | multi_cloud プロバイダ | 0.28" | ヘッダーバー内に左寄せ |
| サービスリストアイコン | multi_cloud サービス | 0.30" | テキスト左に配置 |
| 端点ノードアイコン | migration_path 移行元/先 | 0.45" | カード上部に中央配置 |

### テキスト制約

| 要素 | 日本語上限 | 英語上限 |
|------|-----------|---------|
| アクションタイトル | 50文字 | 100文字 |
| ノード名（data_flow） | 10文字 | 20文字 |
| フローラベル | 8文字 | 15文字 |
| プロバイダ名 | 10文字 | 20文字 |
| サービス名 | 15文字 | 30文字 |
| メトリクス名（benchmark） | 15文字 | 30文字 |
| ステップ名（migration_path） | 8文字 | 16文字 |
| ステップ詳細 | 15文字 | 30文字 |

### 技術図カラーコーディング

```
Blue   (#2673BB / C["primary"])     → Scalar 製品コンポーネント
Gray   (#6B7280 / C["border"])      → 外部/既存コンポーネント
Orange (#E8963A / C["warning"])      → ユーザー/クライアントアプリケーション
Green  (#63C045 / C["success"])     → 正常データフロー / 成功パス
Red    (#DC2626 / C["alertRed"])    → 障害/エラーパス
Dashed lines                        → オプション経路
Solid lines                         → 必須経路
```

### パターンマッピング

| コンポーザー | 主要パターン | 補助パターン |
|------------|------------|------------|
| `compose_data_flow` | Pattern 10/11 (Flow) | -- |
| `compose_multi_cloud` | Pattern 10 + アイコン | -- |
| `compose_benchmark` | Pattern 4 (Bar Chart) | -- |
| `compose_migration_path` | Pattern 10 (Flow) | Pattern 2 (Timeline) |
