*[日本語](enterprise.ja.md)*

# Composer Specification: enterprise Category

Rendering specification for the 4 types in the enterprise category. Builds enterprise-appeal slides for security, ecosystem, SLA, and pricing.

> **Convention**: `C` = color constants, `L` = layout constants, `sb` = SlideBuilder instance.
> Coordinate units are inches. Page size: 10.0" x 5.625".

---

## 1. compose_security_compliance

A slide that lists security certifications and compliance features.

- **Master**: CONTENT
- **Pattern**: Pattern 7 (Icon+Text Row)
- **Layout**: Certification badge row + feature icon grid

### Content Area

| Element | X | Y | W | H | Note |
|------|----:|----:|----:|----:|------|
| Title | 0.323 | 0.303 | 9.354 | 0.437 | CONTENT standard |
| Certification badge row | 0.500 | 0.900 | 9.000 | 0.700 | Certification names arranged horizontally |
| Feature grid | 0.500 | 1.800 | 9.000 | 3.200 | 2 columns x N rows or 3 columns x N rows |

### Python Code Template

```python
def compose_security_compliance(sb, slide_id, content, theme, page_num, total_pages=None):
    """security_compliance スライドを構築する。

    content schema:
        title: str
        certifications: list[str]
        securityFeatures: list[{icon: str, name: str, description: str}]
    """
    C = theme["colors"]
    L = theme["layouts"]["CONTENT"]

    # --- マスター適用 ---
    apply_master_content(sb, theme, slide_id, page_num, total_pages)
    apply_action_title(sb, theme, slide_id, content["title"])

    # --- 認証バッジ行 ---
    certs = content.get("certifications", [])
    n_certs = len(certs)
    if n_certs > 0:
        badge_y = 0.900
        badge_h = 0.550
        badge_gap = 0.20
        total_w = 9.000
        badge_w = (total_w - badge_gap * (n_certs - 1)) / n_certs if n_certs > 1 else total_w

        for i, cert in enumerate(certs):
            bx = 0.500 + i * (badge_w + badge_gap)
            # 認証カード（角丸背景 + テキスト）
            sb.add_rounded_rect(slide_id, bx, badge_y, badge_w, badge_h,
                                fill=C["surfaceLight"],
                                border_color=C["primary"])
            # 上部アクセントバー
            sb.add_rect(slide_id, bx, badge_y, badge_w, 0.025, fill=C["primary"])
            # 認証名
            sb.add_text(slide_id, cert,
                        bx + 0.10, badge_y + 0.05, badge_w - 0.20, badge_h - 0.10,
                        font_size=12, bold=True, color=C["textTitle"],
                        alignment="CENTER", valign="MIDDLE")

    # --- セキュリティ機能グリッド（Pattern 7 応用）---
    features = content.get("securityFeatures", [])
    n_feat = len(features)
    if n_feat == 0:
        return

    grid_x = 0.500
    grid_y = 1.800
    grid_w = 9.000
    grid_h = 3.200

    # 列数を自動決定: 4個以下=2列, 5-6個=3列
    cols = 3 if n_feat > 4 else 2
    rows = (n_feat + cols - 1) // cols
    cell_w = grid_w / cols
    cell_h = min(grid_h / rows, 1.200)
    icon_r = 0.18

    for idx, feat in enumerate(features):
        col = idx % cols
        row = idx // cols
        fx = grid_x + col * cell_w
        fy = grid_y + row * cell_h

        icon_char = feat.get("icon", "\u{1F512}"[0] if False else "S")  # フォールバック
        # アイコンバッジ
        sb.add_badge(slide_id, fx + icon_r + 0.10, fy + icon_r + 0.05,
                     icon_r, feat.get("icon", "S"), fill=C["primary"],
                     text_color=C["textOnDark"])
        # 機能名
        sb.add_text(slide_id, feat["name"],
                    fx + icon_r * 2 + 0.30, fy + 0.02, cell_w - icon_r * 2 - 0.45, 0.30,
                    font_size=13, bold=True, color=C["textTitle"],
                    valign="MIDDLE")
        # 説明
        sb.add_text(slide_id, feat.get("description", ""),
                    fx + icon_r * 2 + 0.30, fy + 0.35, cell_w - icon_r * 2 - 0.45, 0.55,
                    font_size=11, color=C["textSecondary"],
                    valign="TOP")
```

### Design Notes

- Assumes up to 5 certification badges. For 6 or more, reduce the font size to 10pt
- The top accent bar `0.025"` maintains visual consistency (per design-principles.md)
- Feature icons are unified to `C["primary"]` (60-30-10 rule)

---

## 2. compose_ecosystem

A slide that displays the product's ecosystem and integration partners radiating around a central node.

- **Master**: CONTENT
- **Pattern**: Pattern 12 (Venn) applied / radial layout
- **Layout**: Central product node + category-grouped partners surrounding it

### Content Area

| Element | X | Y | W | H | Note |
|------|----:|----:|----:|----:|------|
| Title | 0.323 | 0.303 | 9.354 | 0.437 | CONTENT standard |
| Center node | 4.400 | 2.250 | 1.200 | 1.200 | Product name + icon |
| Partner area | 0.500 | 0.900 | 9.000 | 4.100 | Radial arrangement |

### Python Code Template

```python
import math

def compose_ecosystem(sb, slide_id, content, theme, page_num, total_pages=None):
    """ecosystem スライドを構築する。

    content schema:
        title: str
        center: {name: str, icon: str (opt)}
        partners: list[{category: str, items: list[{name: str, icon: str (opt)}]}]
    """
    C = theme["colors"]

    # --- マスター適用 ---
    apply_master_content(sb, theme, slide_id, page_num, total_pages)
    apply_action_title(sb, theme, slide_id, content["title"])

    # --- 中央ノード ---
    center = content["center"]
    cx, cy = 5.000, 2.850  # ページ中心（水平）、body 領域の中心（垂直）
    center_r = 0.550

    sb.add_circle(slide_id, cx, cy, center_r, fill=C["primary"])
    sb.add_text(slide_id, center["name"],
                cx - center_r, cy - center_r * 0.5,
                center_r * 2, center_r,
                font_size=14, bold=True, color=C["textOnDark"],
                alignment="CENTER", valign="MIDDLE")

    # --- パートナーカテゴリ配置（放射状）---
    partners = content.get("partners", [])
    n_cat = len(partners)
    if n_cat == 0:
        return

    orbit_r = 1.800  # 中心からカテゴリヘッダまでの距離
    cat_colors = [C["primary"], C["accent"], C["success"],
                  C.get("chart3", C["primary"]), C.get("chart4", C["accent"])]

    for i, cat in enumerate(partners):
        angle = math.radians(90 + (360 / n_cat) * i)  # 上から時計回り
        cat_cx = cx + orbit_r * math.cos(angle)
        cat_cy = cy - orbit_r * math.sin(angle)
        cat_color = cat_colors[i % len(cat_colors)]

        # カテゴリヘッダ（角丸カード）
        cat_w = 1.600
        cat_h = 0.350
        sb.add_rounded_rect(slide_id,
                            cat_cx - cat_w / 2, cat_cy - cat_h / 2,
                            cat_w, cat_h,
                            fill=cat_color)
        sb.add_text(slide_id, cat["category"],
                    cat_cx - cat_w / 2, cat_cy - cat_h / 2,
                    cat_w, cat_h,
                    font_size=11, bold=True, color=C["textOnDark"],
                    alignment="CENTER", valign="MIDDLE")

        # 中心からカテゴリへのコネクタ
        sb.add_connector(slide_id,
                         cx + center_r * math.cos(angle),
                         cy - center_r * math.sin(angle),
                         cat_cx - (cat_w / 2) * math.cos(angle),
                         cat_cy + (cat_h / 2) * math.sin(angle),
                         color=C["border"], weight=1.5)

        # パートナー項目（カテゴリの外側に小テキスト）
        items = cat.get("items", [])
        for j, item in enumerate(items):
            offset = (j - (len(items) - 1) / 2) * 0.30
            ix = cat_cx + offset * math.cos(angle + math.pi / 2)
            iy = cat_cy - offset * math.sin(angle + math.pi / 2)
            # カテゴリから外側方向にオフセット
            outward = 0.35
            ix += outward * math.cos(angle)
            iy -= outward * math.sin(angle)

            sb.add_text(slide_id, item["name"],
                        ix - 0.60, iy - 0.12, 1.20, 0.25,
                        font_size=10, color=C["textPrimary"],
                        alignment="CENTER", valign="MIDDLE")
```

### Design Notes

- Assumes 3-5 categories. For 6 or more, the layout becomes dense, so either expand `orbit_r` or switch to a 2-tier layout
- The center node's font size is adjusted between 12-16pt depending on product name length
- When using cloud icons for partner items, load them via `add_image_from_asset()` from `shared/cloud-icons/`

---

## 3. compose_support_sla

A slide that displays support plans / SLA tiers as comparison cards.

- **Master**: CONTENT
- **Pattern**: Pattern 9 (Comparison) extended (supports 3 columns)
- **Layout**: 2-3 column comparison cards. The recommended plan is highlighted

### Content Area

| Element | X | Y | W | H | Note |
|------|----:|----:|----:|----:|------|
| Title | 0.323 | 0.303 | 9.354 | 0.437 | CONTENT standard |
| Card area | 0.500 | 0.900 | 9.000 | 4.100 | 2-3 columns evenly spaced |

### Python Code Template

```python
def compose_support_sla(sb, slide_id, content, theme, page_num, total_pages=None):
    """support_sla スライドを構築する。

    content schema:
        title: str
        tiers: list[{name: str, features: list[str], sla: str,
                      responseTime: str, highlighted: bool (opt)}]
    """
    C = theme["colors"]

    # --- マスター適用 ---
    apply_master_content(sb, theme, slide_id, page_num, total_pages)
    apply_action_title(sb, theme, slide_id, content["title"])

    # --- 比較カード ---
    tiers = content.get("tiers", [])
    n_tiers = len(tiers)
    if n_tiers == 0:
        return

    card_area_x = 0.500
    card_area_y = 0.900
    card_area_w = 9.000
    card_area_h = 4.100
    gap = 0.300
    card_w = (card_area_w - gap * (n_tiers - 1)) / n_tiers
    card_h = card_area_h

    for i, tier in enumerate(tiers):
        cx = card_area_x + i * (card_w + gap)
        cy = card_area_y
        is_hl = tier.get("highlighted", False)

        # カード背景
        card_bg = C["surfaceLight"] if is_hl else C["background"]
        card_border = C["primary"] if is_hl else C["border"]
        sb.add_rounded_rect(slide_id, cx, cy, card_w, card_h,
                            fill=card_bg, border_color=card_border)

        # 上部アクセントバー（推奨プランは primary、通常は border）
        bar_color = C["primary"] if is_hl else C["border"]
        sb.add_rect(slide_id, cx, cy, card_w, 0.025, fill=bar_color)

        # プラン名ヘッダー
        header_color = C["primary"] if is_hl else C["textTitle"]
        sb.add_text(slide_id, tier["name"],
                    cx + 0.15, cy + 0.10, card_w - 0.30, 0.40,
                    font_size=16, bold=True, color=header_color,
                    alignment="CENTER", valign="MIDDLE")

        # SLA 数値（大きく表示）
        sla_text = tier.get("sla", "")
        if sla_text:
            sb.add_text(slide_id, sla_text,
                        cx + 0.15, cy + 0.55, card_w - 0.30, 0.50,
                        font_size=28, bold=True, color=C["textTitle"],
                        alignment="CENTER", valign="MIDDLE")
            sb.add_text(slide_id, "SLA",
                        cx + 0.15, cy + 1.00, card_w - 0.30, 0.25,
                        font_size=10, color=C["textMuted"],
                        alignment="CENTER", valign="TOP")

        # 応答時間
        rt_text = tier.get("responseTime", "")
        if rt_text:
            sb.add_text(slide_id, rt_text,
                        cx + 0.15, cy + 1.30, card_w - 0.30, 0.30,
                        font_size=14, bold=True, color=C["accent"],
                        alignment="CENTER", valign="MIDDLE")
            sb.add_text(slide_id, "応答時間",
                        cx + 0.15, cy + 1.55, card_w - 0.30, 0.20,
                        font_size=10, color=C["textMuted"],
                        alignment="CENTER", valign="TOP")

        # 機能一覧（箇条書き）
        features = tier.get("features", [])
        if features:
            bullet_y = cy + 1.90
            bullet_h = card_h - 2.10
            sb.add_bullets(slide_id, features,
                           cx + 0.20, bullet_y, card_w - 0.40, bullet_h,
                           font_size=11, color=C["textPrimary"])

        # 推奨バッジ（ハイライト時）
        if is_hl:
            badge_w = 1.000
            sb.add_rounded_rect(slide_id,
                                cx + (card_w - badge_w) / 2, cy - 0.18,
                                badge_w, 0.30,
                                fill=C["primary"])
            sb.add_text(slide_id, "推奨",
                        cx + (card_w - badge_w) / 2, cy - 0.18,
                        badge_w, 0.30,
                        font_size=10, bold=True, color=C["textOnDark"],
                        alignment="CENTER", valign="MIDDLE")
```

### Design Notes

- Assumes 2-3 plans (4 or more narrows the card width and causes bullet text to wrap)
- Set `highlighted: true` on only one recommended plan
- SLA value is emphasized at 28pt like a stat card. Visual hierarchy within the card: plan name > SLA > response time > features
- Card width for a 2-column layout: `(9.0 - 0.3) / 2 = 4.35"`; for 3 columns: `(9.0 - 0.6) / 3 = 2.80"`

---

## 4. compose_pricing

A slide that displays pricing tiers as comparison cards.

- **Master**: CONTENT
- **Pattern**: Pattern 9 (Comparison) extended (supports 3 columns)
- **Layout**: 2-3 column pricing cards. The recommended plan is highlighted

### Content Area

| Element | X | Y | W | H | Note |
|------|----:|----:|----:|----:|------|
| Title | 0.323 | 0.303 | 9.354 | 0.437 | CONTENT standard |
| Card area | 0.500 | 0.900 | 9.000 | 3.700 | 2-3 columns evenly spaced |
| Footnote | 0.500 | 4.750 | 9.000 | 0.300 | Optional |

### Python Code Template

```python
def compose_pricing(sb, slide_id, content, theme, page_num, total_pages=None):
    """pricing スライドを構築する。

    content schema:
        title: str
        plans: list[{name: str, price: str, features: list[str],
                      highlighted: bool (opt)}]
        footnote: str (opt)
    """
    C = theme["colors"]

    # --- マスター適用 ---
    apply_master_content(sb, theme, slide_id, page_num, total_pages)
    apply_action_title(sb, theme, slide_id, content["title"])

    # --- 脚注の有無でカード領域高さを調整 ---
    has_footnote = bool(content.get("footnote"))
    card_area_h = 3.700 if has_footnote else 4.100

    # --- 料金カード ---
    plans = content.get("plans", [])
    n_plans = len(plans)
    if n_plans == 0:
        return

    card_area_x = 0.500
    card_area_y = 0.900
    card_area_w = 9.000
    gap = 0.300
    card_w = (card_area_w - gap * (n_plans - 1)) / n_plans
    card_h = card_area_h

    for i, plan in enumerate(plans):
        cx = card_area_x + i * (card_w + gap)
        cy = card_area_y
        is_hl = plan.get("highlighted", False)

        # カード背景
        card_bg = C["surfaceLight"] if is_hl else C["background"]
        card_border = C["primary"] if is_hl else C["border"]
        sb.add_rounded_rect(slide_id, cx, cy, card_w, card_h,
                            fill=card_bg, border_color=card_border)

        # 上部アクセントバー
        bar_color = C["primary"] if is_hl else C["border"]
        sb.add_rect(slide_id, cx, cy, card_w, 0.025, fill=bar_color)

        # プラン名
        header_color = C["primary"] if is_hl else C["textTitle"]
        sb.add_text(slide_id, plan["name"],
                    cx + 0.15, cy + 0.10, card_w - 0.30, 0.35,
                    font_size=15, bold=True, color=header_color,
                    alignment="CENTER", valign="MIDDLE")

        # 価格（大きく表示）
        sb.add_text(slide_id, plan["price"],
                    cx + 0.15, cy + 0.50, card_w - 0.30, 0.55,
                    font_size=28, bold=True, color=C["textTitle"],
                    alignment="CENTER", valign="MIDDLE")

        # セパレーター
        sep_y = cy + 1.15
        sb.add_rect(slide_id, cx + 0.20, sep_y, card_w - 0.40, 0.010,
                    fill=C["border"])

        # 機能一覧
        features = plan.get("features", [])
        if features:
            bullet_y = sep_y + 0.10
            bullet_h = card_h - 1.35
            sb.add_bullets(slide_id, features,
                           cx + 0.20, bullet_y, card_w - 0.40, bullet_h,
                           font_size=11, color=C["textPrimary"])

        # 推奨バッジ（ハイライト時）
        if is_hl:
            badge_w = 1.000
            sb.add_rounded_rect(slide_id,
                                cx + (card_w - badge_w) / 2, cy - 0.18,
                                badge_w, 0.30,
                                fill=C["primary"])
            sb.add_text(slide_id, "推奨",
                        cx + (card_w - badge_w) / 2, cy - 0.18,
                        badge_w, 0.30,
                        font_size=10, bold=True, color=C["textOnDark"],
                        alignment="CENTER", valign="MIDDLE")

    # --- 脚注 ---
    if has_footnote:
        sb.add_text(slide_id, content["footnote"],
                    0.500, 4.750, 9.000, 0.300,
                    font_size=10, color=C["textMuted"],
                    alignment="START", valign="MIDDLE")
```

### Design Notes

- The pricing table uses the same comparison-card pattern as support_sla, but the price is placed as the largest visual element (28pt bold)
- Maintains the visual hierarchy of plan name > price > feature list
- The footnote is used for notes such as tax exclusions or conditions (10pt, `textMuted`)
- For more than 3 columns, switching to a table layout (`compose_table`) is recommended

---

## Common Notes

### CONTENT Master Coordinates (Common to All Composers)

```
タイトル:   (0.323, 0.303) w=9.354 h=0.437
Body 開始:  y=0.787
Body 終了:  y=5.208 (contentBottom)
フッター:   y=5.208 以下（ロゴ・著作権・ページ番号）
```

### Text Constraints

| Element | Japanese Limit | English Limit |
|------|-----------|---------|
| Action title | 50 chars | 100 chars |
| Certification name (security_compliance) | 20 chars | 40 chars |
| Category name (ecosystem) | 12 chars | 24 chars |
| Plan name (support_sla / pricing) | 12 chars | 24 chars |
| Feature bullet | 40 chars | 80 chars |
| Footnote | 60 chars | 120 chars |

### Pattern Mapping

| Composer | Primary Pattern | Secondary Pattern |
|------------|------------|------------|
| `compose_security_compliance` | Pattern 7 (Icon+Text) | -- |
| `compose_ecosystem` | Pattern 12 (Venn) | -- |
| `compose_support_sla` | Pattern 9 (Comparison) | Pattern 8 (Stat Card) |
| `compose_pricing` | Pattern 9 (Comparison) | -- |
