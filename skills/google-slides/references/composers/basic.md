# Basic コンポーザー仕様

basic カテゴリ（6タイプ）のコンポーザー関数仕様。

---

## compose_title

**マスター**: COVER | **パターン**: 独自

表紙スライド。primary色背景にタイトル・サブタイトル・発表者情報を配置。

### レイアウト

```
┌──────────────────────────────────────┐
│                         [Logo] ──→ (8.3, 0.4) w=1.18 h=0.34
│                                      │
│  タイトル ─────────────→ (0.5, 1.3) w=8.9 h=1.2    30pt bold
│  サブタイトル ─────────→ (0.5, 2.6) w=8.9 h=0.5    14pt
│                                      │
│             発表者 / 日付 ──→ (5.9, 3.4) w=3.6      12pt
│  ┌──────────────────────────────────┐│
│  │      decorative bottom band      ││
│  └──────────────────────────────────┘│
└──────────────────────────────────────┘
```

### コード

```python
def compose_title(sb, content, theme, slide_id):
    apply_master_cover(sb, theme, slide_id)
    t = theme["layouts"]["COVER"]["elements"]

    # タイトル
    sb.add_text(f"{slide_id}_title", content["title"],
        t["title"]["x"], t["title"]["y"], t["title"]["w"], t["title"]["h"],
        font=theme["fonts"]["fontFaceTitle"], size=theme["fontSizes"]["coverTitle"],
        color=theme["colors"]["textOnDark"], bold=True)

    # サブタイトル
    if content.get("subtitle"):
        sb.add_text(f"{slide_id}_subtitle", content["subtitle"],
            t["subtitle"]["x"], t["subtitle"]["y"], t["subtitle"]["w"], t["subtitle"]["h"],
            font=theme["fonts"]["fontFaceBody"], size=theme["fontSizes"]["subtitle"],
            color=theme["colors"]["textOnDark"])

    # 発表者 + 日付
    info_parts = []
    if content.get("presenter"): info_parts.append(content["presenter"])
    if content.get("date"): info_parts.append(content["date"])
    if info_parts:
        sb.add_text(f"{slide_id}_info", " | ".join(info_parts),
            t["body"]["x"], t["body"]["y"], t["body"]["w"], t["body"]["h"],
            font=theme["fonts"]["fontFaceBody"], size=theme["fontSizes"]["bodyLevel3"],
            color=theme["colors"]["textOnDark"], align="END")
```

---

## compose_agenda

**マスター**: SECTION | **パターン**: Pattern 7 (Icon+Text Row) 応用

目次スライド。番号付きリストでセクション構成を表示。currentIndex 指定時はハイライト。

### レイアウト

```
┌──────────────────────────────────────┐
│ [Logo] (0.1, 0.2)                    │
│                                      │
│      アジェンダ ──→ (1.4, 1.5) 24pt  │
│      ──────── separator ────────     │
│                                      │
│   1. セクション名 ──→ y=2.2         │
│   2. セクション名 ──→ y=2.6  ← current: primary色  │
│   3. セクション名 ──→ y=3.0         │
│   4. セクション名 ──→ y=3.4         │
│                                      │
│  ┌──────────────────────────────────┐│
│  │      decorative bottom band      ││
│  └──────────────────────────────────┘│
└──────────────────────────────────────┘
```

### コード

```python
def compose_agenda(sb, content, theme, slide_id):
    apply_master_section(sb, theme, slide_id)
    colors = theme["colors"]

    # タイトル
    sb.add_text(f"{slide_id}_title", content["title"],
        1.438, 1.5, 7.125, 0.590,
        font=theme["fonts"]["fontFaceTitle"], size=theme["fontSizes"]["sectionTitle"],
        color=colors["textTitle"], bold=True)

    # アジェンダ項目
    items = content["items"]
    current = content.get("currentIndex")
    start_y = 2.2
    item_h = 0.40

    for i, item in enumerate(items):
        is_current = (current is not None and i == current)
        text_color = colors["primary"] if is_current else colors["textPrimary"]
        weight = True if is_current else False

        # 番号バッジ
        badge_x = 1.5
        badge_r = 0.14
        fill = colors["primary"] if is_current else colors["surfaceLight"]
        badge_text_color = colors["textOnDark"] if is_current else colors["textPrimary"]
        sb.add_badge(f"{slide_id}_badge_{i}", str(i + 1),
            badge_x, start_y + i * item_h, badge_r,
            fill=fill, text_color=badge_text_color, size=10)

        # 項目テキスト
        sb.add_text(f"{slide_id}_item_{i}", item,
            badge_x + badge_r * 2 + 0.2, start_y + i * item_h - 0.05,
            6.0, item_h,
            font=theme["fonts"]["fontFaceBody"], size=theme["fontSizes"]["bodyLevel1"],
            color=text_color, bold=weight)
```

---

## compose_section_divider

**マスター**: SECTION | **パターン**: 独自

セクション区切り。セクション番号（オプション）とタイトルを中央配置。

### コード

```python
def compose_section_divider(sb, content, theme, slide_id):
    apply_master_section(sb, theme, slide_id)
    t = theme["layouts"]["SECTION"]["elements"]
    colors = theme["colors"]

    # セクション番号（オプション）
    if content.get("sectionNumber"):
        sb.add_text(f"{slide_id}_num", f"Section {content['sectionNumber']}",
            t["title"]["x"], t["title"]["y"] - 0.5, t["title"]["w"], 0.4,
            font=theme["fonts"]["fontFaceEn"], size=theme["fontSizes"]["bodyLevel2"],
            color=colors["primary"], bold=True)

    # セクションタイトル
    sb.add_text(f"{slide_id}_title", content["title"],
        t["title"]["x"], t["title"]["y"], t["title"]["w"], t["title"]["h"],
        font=theme["fonts"]["fontFaceTitle"], size=theme["fontSizes"]["sectionTitle"],
        color=colors["textTitle"], bold=True)

    # サブタイトル（オプション）
    if content.get("subtitle"):
        sb.add_text(f"{slide_id}_subtitle", content["subtitle"],
            t["body"]["x"], t["body"]["y"], t["body"]["w"], t["body"]["h"],
            font=theme["fonts"]["fontFaceBody"], size=theme["fontSizes"]["bodyLevel1"],
            color=colors["textSecondary"])
```

---

## compose_summary

**マスター**: HIGHLIGHT | **パターン**: Pattern 8 (Stat Card) + テキスト

エグゼクティブサマリー / 結論。暗色背景に白テキストでキーポイントを強調。

### レイアウト

```
┌──────────────────────────────────────┐
│ ████████ primary 背景 ████████████████│
│                                      │
│  アクションタイトル ─→ 24pt white bold│
│                                      │
│  ● キーポイント 1 ─────→ 14pt white  │
│  ● キーポイント 2                    │
│  ● キーポイント 3                    │
│                                      │
│  推奨事項:                           │
│    テキスト ──────────→ 12pt white    │
│                                      │
│  ネクストステップ:                    │
│    1. ステップ 1                     │
│    2. ステップ 2                     │
└──────────────────────────────────────┘
```

### コード

```python
def compose_summary(sb, content, theme, slide_id):
    apply_master_highlight(sb, theme, slide_id)
    colors = theme["colors"]

    # タイトル
    sb.add_text(f"{slide_id}_title", content["title"],
        0.5, 0.5, 9.0, 0.6,
        font=theme["fonts"]["fontFaceTitle"], size=24,
        color=colors["textOnDark"], bold=True)

    # キーポイント
    y = 1.3
    for i, point in enumerate(content["keyPoints"]):
        sb.add_text(f"{slide_id}_kp_{i}", f"  {point}",
            0.7, y + i * 0.45, 8.5, 0.4,
            font=theme["fonts"]["fontFaceBody"], size=14,
            color=colors["textOnDark"])

    y_offset = 1.3 + len(content["keyPoints"]) * 0.45 + 0.3

    # 推奨事項
    if content.get("recommendation"):
        sb.add_text(f"{slide_id}_rec_label", "推奨事項:",
            0.5, y_offset, 2.0, 0.3,
            font=theme["fonts"]["fontFaceTitle"], size=12,
            color=colors["accent"], bold=True)
        sb.add_text(f"{slide_id}_rec", content["recommendation"],
            0.7, y_offset + 0.3, 8.3, 0.4,
            font=theme["fonts"]["fontFaceBody"], size=12,
            color=colors["textOnDark"])
        y_offset += 0.8

    # ネクストステップ
    if content.get("nextSteps"):
        sb.add_text(f"{slide_id}_ns_label", "ネクストステップ:",
            0.5, y_offset, 3.0, 0.3,
            font=theme["fonts"]["fontFaceTitle"], size=12,
            color=colors["accent"], bold=True)
        for i, step in enumerate(content["nextSteps"]):
            sb.add_text(f"{slide_id}_ns_{i}", f"  {i+1}. {step}",
                0.7, y_offset + 0.3 + i * 0.35, 8.3, 0.3,
                font=theme["fonts"]["fontFaceBody"], size=12,
                color=colors["textOnDark"])
```

---

## compose_closing

**マスター**: CLOSING | **パターン**: 独自

締めスライド。ロゴと連絡先情報を中央配置。

### 配置制約

CLOSING マスターには下部に装飾バンド（画像）が配置される（`theme.json` の `layouts.CLOSING.decorative.bottomBand` 参照）。**連絡先情報やテキスト要素は装飾バンドの上端（y 座標）より上に配置すること。**

| 要素 | 推奨 Y 位置 | 注意 |
|------|-----------|------|
| 「ご清聴ありがとうございました」等 | 装飾バンド y - 0.4" 以上 | バンドに重ならないこと |
| 連絡先情報 | 装飾バンド y - 0.2" 以上 | テキスト最下端がバンドに隠れないこと |

> Scalar テーマの場合、`bottomBand.y = 3.667"` のため、連絡先テキストは y + h < 3.65" に収まるよう調整する。

### コード

```python
def compose_closing(sb, content, theme, slide_id):
    apply_master_closing(sb, theme, slide_id)
    colors = theme["colors"]

    # メッセージ（オプション）
    if content.get("message"):
        sb.add_text(f"{slide_id}_msg", content["message"],
            2.0, 1.5, 6.0, 0.5,
            font=theme["fonts"]["fontFaceBody"], size=16,
            color=colors["textPrimary"], align="CENTER")

    # 連絡先情報
    ci = content.get("contactInfo", {})
    if ci:
        info_lines = []
        if ci.get("name"): info_lines.append(ci["name"])
        if ci.get("email"): info_lines.append(ci["email"])
        if ci.get("phone"): info_lines.append(ci["phone"])
        if ci.get("url"): info_lines.append(ci["url"])

        sb.add_text(f"{slide_id}_contact", "\n".join(info_lines),
            2.5, 3.5, 5.0, 1.5,
            font=theme["fonts"]["fontFaceBody"], size=12,
            color=colors["textSecondary"], align="CENTER",
            line_spacing=180)
```

---

## compose_appendix

**マスター**: BLANK | **パターン**: 独自

付録表紙。シンプルに「Appendix」タイトルを中央表示。

### コード

```python
def compose_appendix(sb, content, theme, slide_id):
    apply_master_blank(sb, theme, slide_id)
    colors = theme["colors"]

    # タイトル
    sb.add_text(f"{slide_id}_title", content.get("title", "Appendix"),
        2.0, 2.0, 6.0, 0.8,
        font=theme["fonts"]["fontFaceTitle"], size=theme["fontSizes"]["sectionTitle"],
        color=colors["textTitle"], bold=True, align="CENTER")

    # サブタイトル
    if content.get("subtitle"):
        sb.add_text(f"{slide_id}_subtitle", content["subtitle"],
            2.0, 3.0, 6.0, 0.5,
            font=theme["fonts"]["fontFaceBody"], size=theme["fontSizes"]["subtitle"],
            color=colors["textSecondary"], align="CENTER")
```
