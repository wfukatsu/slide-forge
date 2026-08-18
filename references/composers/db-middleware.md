*[日本語](db-middleware.ja.md)*

# Composer Specification: db-middleware Category

Rendering specification for the 4 types in the db-middleware category. Builds DB/middleware-specific slides for data flow, multi-cloud, benchmark, and migration.

> **Convention**: `C` = color constants, `L` = layout constants, `sb` = SlideBuilder instance.
> Coordinate units are inches. Page size: 10.0" x 5.625".

### Cloud Icons

Provider-specific icons are stored under `assets/cloud-icons/` (fetched by `scripts/fetch_cloud_icons.py`;
the directory is gitignored). Composers place them with the `cloud_icon()` helper from `scripts/cloud_icons.py`.

```
assets/cloud-icons/
  aws/       — AWS サービスアイコン
  gcp/       — GCP サービスアイコン
  azure/     — Azure サービスアイコン
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

> `sb` is a SlideBuilder mixed with `CloudIconMixin`. For how names are resolved and the
> licensing constraints, see `references/cloud-icons.md`. When not displaying a label,
> explicitly pass `label=""` (the default shows the official name).

---

## 1. compose_data_flow

A slide that displays the data flow (source → process → store → output) using nodes and arrows.

- **Master**: CONTENT
- **Pattern**: Pattern 10/11 (Flow / Decision Flow)
- **Layout**: Horizontal flow diagram + nodes with cloud icons

### Content Area

| Element | X | Y | W | H | Note |
|------|----:|----:|----:|----:|------|
| Title | 0.323 | 0.303 | 9.354 | 0.437 | CONTENT standard |
| Flow area | 0.500 | 0.900 | 9.000 | 4.100 | Nodes + connectors |

### Style by Node Type

| type | Shape | Color | Purpose |
|------|---------|-----|------|
| `source` | ROUND_RECTANGLE | `C["accent"]` | Data source (DB, API) |
| `process` | RECTANGLE | `C["primary"]` | Scalar product (transform/process) |
| `store` | ROUND_RECTANGLE | `C["primaryDark"]` | Data store |
| `output` | ROUND_RECTANGLE | `C["success"]` | Output destination (app, report) |

### Python Code Template

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

### Design Notes

- Assumes 3-5 nodes. For 6 or more, switch to a 2-row layout or reduce `box_w`
- `process` nodes (Scalar products) use a non-rounded RECTANGLE so they are visually distinct from other types
- Dashed connectors are used for optional paths (e.g. error paths)
- Technical diagram color convention: Blue=Scalar, Gray=External, Orange=User/client, Green=Normal flow

---

## 2. compose_multi_cloud

A slide that displays a multi-cloud configuration (AWS / GCP / Azure + Scalar layer).

- **Master**: CONTENT
- **Pattern**: Pattern 10 (Flow) + cloud icons
- **Layout**: Top row = Scalar layer, bottom row = cloud provider columns (2-3 columns)

### Content Area

| Element | X | Y | W | H | Note |
|------|----:|----:|----:|----:|------|
| Title | 0.323 | 0.303 | 9.354 | 0.437 | CONTENT standard |
| Scalar layer | 0.500 | 0.900 | 9.000 | 1.100 | Center band, primary background |
| Cloud columns | 0.500 | 2.250 | 9.000 | 2.750 | Per-provider cards |

### Python Code Template

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

### Design Notes

- Assumes 2-3 clouds (4 or more providers narrows the card width)
- Uses each provider's brand color in the header for easy visual identification
- Placing the Scalar layer on top visually expresses the "vendor-independent unified layer" concept
- Service icons are loaded from `assets/cloud-icons/{provider}/` (`aws` / `gcp` / `azure`). Falls back to a badge if the asset is missing

---

## 3. compose_benchmark

A slide that displays a benchmark / performance comparison as horizontal bar charts.

- **Master**: CONTENT
- **Pattern**: Pattern 4 (Bar Chart)
- **Layout**: Horizontal bar chart per metric (own product highlighted)

### Content Area

| Element | X | Y | W | H | Note |
|------|----:|----:|----:|----:|------|
| Title | 0.323 | 0.303 | 9.354 | 0.437 | CONTENT standard |
| Chart area | 0.500 | 0.900 | 8.500 | 3.700 | Multiple metrics |
| Source | 0.500 | 4.750 | 9.000 | 0.300 | Benchmark source |

### Python Code Template

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

### Design Notes

- Assumes 1-3 metrics. For 4 or more, the vertical layout becomes dense, so splitting into 2 slides is recommended
- Own product (`isOurs: true`) is clearly distinguished with `C["primary"]` (Scalar Blue); competitors use `C["border"]` (gray)
- Value labels are placed outside the right end of the bar, eliminating reliance on a legend (Tufte principle: maximize the data-ink ratio)
- The source citation is placed at 9pt directly above the footer (to ensure data credibility)

---

## 4. compose_migration_path

A slide that displays the migration path (source → steps → destination) as a horizontal flow + timeline.

- **Master**: CONTENT
- **Pattern**: Pattern 10 (Flow) + Pattern 2 (H-Timeline)
- **Layout**: Left edge = migration source, right edge = migration destination, center = step chain

### Content Area

| Element | X | Y | W | H | Note |
|------|----:|----:|----:|----:|------|
| Title | 0.323 | 0.303 | 9.354 | 0.437 | CONTENT standard |
| Source node | 0.500 | 1.200 | 1.400 | 1.400 | Circle or rounded rect |
| Step chain | 2.200 | 1.500 | 5.600 | 3.200 | Flow + details |
| Destination node | 8.100 | 1.200 | 1.400 | 1.400 | Circle or rounded rect |

### Python Code Template

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

### Design Notes

- Assumes 3-5 steps. For 2 or fewer, a direct arrow + text is sufficient. For 6 or more, boxes become narrow, so switch to a 2-row layout
- The step gradient (accent → primary) visually expresses the direction of progress
- The destination node emphasizes the "goal" with a primary border + accent bar
- Cloud icons are placed at the source/destination via `_place_cloud_icon()`. Example: `"aws/rds.png"` → `"gcp/cloud-spanner.png"`
- Detail text (description + duration) is placed below each step at 9pt. To prevent wrapping, keep each within roughly 15 characters (for Japanese text; see the text constraints table below for language-specific limits)

---

## Common Notes

### CONTENT Master Coordinates (Common to All Composers)

```
タイトル:   (0.323, 0.303) w=9.354 h=0.437
Body 開始:  y=0.787
Body 終了:  y=5.208 (contentBottom)
フッター:   y=5.208 以下（ロゴ・著作権・ページ番号）
```

### Cloud Icon Integration Patterns

| Pattern | Usage Location | Icon Size | Note |
|---------|---------|:----------:|------|
| In-node icon | data_flow node | 0.45" | Centered at top of node |
| Card header icon | multi_cloud provider | 0.28" | Left-aligned within header bar |
| Service list icon | multi_cloud service | 0.30" | Placed to the left of text |
| Endpoint node icon | migration_path source/destination | 0.45" | Centered at top of card |

### Text Constraints

| Element | Japanese Limit | English Limit |
|------|-----------|---------|
| Action title | 50 chars | 100 chars |
| Node name (data_flow) | 10 chars | 20 chars |
| Flow label | 8 chars | 15 chars |
| Provider name | 10 chars | 20 chars |
| Service name | 15 chars | 30 chars |
| Metric name (benchmark) | 15 chars | 30 chars |
| Step name (migration_path) | 8 chars | 16 chars |
| Step detail | 15 chars | 30 chars |

### Technical Diagram Color Coding

```
Blue   (#2673BB / C["primary"])     → Scalar 製品コンポーネント
Gray   (#6B7280 / C["border"])      → 外部/既存コンポーネント
Orange (#E8963A / C["warning"])      → ユーザー/クライアントアプリケーション
Green  (#63C045 / C["success"])     → 正常データフロー / 成功パス
Red    (#DC2626 / C["alertRed"])    → 障害/エラーパス
Dashed lines                        → オプション経路
Solid lines                         → 必須経路
```

### Pattern Mapping

| Composer | Primary Pattern | Secondary Pattern |
|------------|------------|------------|
| `compose_data_flow` | Pattern 10/11 (Flow) | -- |
| `compose_multi_cloud` | Pattern 10 + icons | -- |
| `compose_benchmark` | Pattern 4 (Bar Chart) | -- |
| `compose_migration_path` | Pattern 10 (Flow) | Pattern 2 (Timeline) |
