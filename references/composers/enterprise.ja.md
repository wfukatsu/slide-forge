*[English](enterprise.md)*

# コンポーザー仕様: enterprise カテゴリ

enterprise カテゴリ 4 タイプのレンダリング仕様。セキュリティ・エコシステム・SLA・料金のエンタープライズ訴求スライドを構築する。

> **規約**: `C` = 色定数, `L` = レイアウト定数, `sb` = SlideBuilder インスタンス。
> 座標単位はインチ。ページサイズ: 10.0" x 5.625"。

---

## 1. compose_security_compliance

セキュリティ認証・コンプライアンス機能を一覧表示するスライド。

- **マスター**: CONTENT
- **パターン**: Pattern 7 (Icon+Text Row)
- **レイアウト**: 認証バッジ行 + 機能アイコングリッド

### コンテンツ領域

| 要素 | X | Y | W | H | 備考 |
|------|----:|----:|----:|----:|------|
| タイトル | 0.323 | 0.303 | 9.354 | 0.437 | CONTENT 標準 |
| 認証バッジ行 | 0.500 | 0.900 | 9.000 | 0.700 | 認証名を横並び |
| 機能グリッド | 0.500 | 1.800 | 9.000 | 3.200 | 2列 x N行 or 3列 x N行 |

### Python コードテンプレート

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

### デザインノート

- 認証バッジは最大 5 個を想定。6 個以上の場合はフォントサイズを 10pt に縮小
- 上部アクセントバー `0.025"` で統一感を確保（design-principles.md 準拠）
- 機能アイコンは `C["primary"]` に統一（60-30-10 ルール）

---

## 2. compose_ecosystem

製品を中心としたエコシステム・連携パートナーを放射状に表示するスライド。

- **マスター**: CONTENT
- **パターン**: Pattern 12 (Venn) 応用 / 放射レイアウト
- **レイアウト**: 中央に製品ノード + 周囲にカテゴリ別パートナー

### コンテンツ領域

| 要素 | X | Y | W | H | 備考 |
|------|----:|----:|----:|----:|------|
| タイトル | 0.323 | 0.303 | 9.354 | 0.437 | CONTENT 標準 |
| 中央ノード | 4.400 | 2.250 | 1.200 | 1.200 | 製品名 + アイコン |
| パートナー領域 | 0.500 | 0.900 | 9.000 | 4.100 | 放射配置 |

### Python コードテンプレート

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

### デザインノート

- カテゴリ数は 3-5 を想定。6 以上は配置が密になるため `orbit_r` を拡大するか 2 段構成に変更
- 中心ノードのフォントサイズは製品名の長さに応じて 12-16pt で調整
- パートナー項目にクラウドアイコンを使う場合は `add_image_from_asset()` で `shared/cloud-icons/` から読み込む

---

## 3. compose_support_sla

サポートプラン・SLA 体系を比較カード形式で表示するスライド。

- **マスター**: CONTENT
- **パターン**: Pattern 9 (Comparison) 拡張（3列対応）
- **レイアウト**: 2-3 列の比較カード。推奨プランはハイライト表示

### コンテンツ領域

| 要素 | X | Y | W | H | 備考 |
|------|----:|----:|----:|----:|------|
| タイトル | 0.323 | 0.303 | 9.354 | 0.437 | CONTENT 標準 |
| カード領域 | 0.500 | 0.900 | 9.000 | 4.100 | 2-3列均等配置 |

### Python コードテンプレート

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

### デザインノート

- プラン数は 2-3 を想定（4 以上はカード幅が狭くなり箇条書きが折り返す）
- 推奨プランの `highlighted: true` は 1 つのみに設定
- SLA 数値は 28pt で統計カード風に強調。カード内の視覚的階層: プラン名 > SLA > 応答時間 > 機能
- 2 列レイアウト時のカード幅: `(9.0 - 0.3) / 2 = 4.35"`、3 列: `(9.0 - 0.6) / 3 = 2.80"`

---

## 4. compose_pricing

料金体系を比較カード形式で表示するスライド。

- **マスター**: CONTENT
- **パターン**: Pattern 9 (Comparison) 拡張（3列対応）
- **レイアウト**: 2-3 列の料金カード。推奨プランはハイライト表示

### コンテンツ領域

| 要素 | X | Y | W | H | 備考 |
|------|----:|----:|----:|----:|------|
| タイトル | 0.323 | 0.303 | 9.354 | 0.437 | CONTENT 標準 |
| カード領域 | 0.500 | 0.900 | 9.000 | 3.700 | 2-3列均等配置 |
| 脚注 | 0.500 | 4.750 | 9.000 | 0.300 | オプション |

### Python コードテンプレート

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

### デザインノート

- 料金表は support_sla と同じ比較カードパターンだが、価格を最大の視覚要素（28pt Bold）として配置
- プラン名 > 価格 > 機能一覧の視覚的階層を維持
- 脚注は税別表示・条件等の注記に使用（10pt、`textMuted`）
- 3 列超の場合はテーブル形式（`compose_table`）への切替を推奨

---

## 共通事項

### CONTENT マスター座標（全コンポーザー共通）

```
タイトル:   (0.323, 0.303) w=9.354 h=0.437
Body 開始:  y=0.787
Body 終了:  y=5.208 (contentBottom)
フッター:   y=5.208 以下（ロゴ・著作権・ページ番号）
```

### テキスト制約

| 要素 | 日本語上限 | 英語上限 |
|------|-----------|---------|
| アクションタイトル | 50文字 | 100文字 |
| 認証名（security_compliance） | 20文字 | 40文字 |
| カテゴリ名（ecosystem） | 12文字 | 24文字 |
| プラン名（support_sla / pricing） | 12文字 | 24文字 |
| 機能箇条書き | 40文字 | 80文字 |
| 脚注 | 60文字 | 120文字 |

### パターンマッピング

| コンポーザー | 主要パターン | 補助パターン |
|------------|------------|------------|
| `compose_security_compliance` | Pattern 7 (Icon+Text) | -- |
| `compose_ecosystem` | Pattern 12 (Venn) | -- |
| `compose_support_sla` | Pattern 9 (Comparison) | Pattern 8 (Stat Card) |
| `compose_pricing` | Pattern 9 (Comparison) | -- |
