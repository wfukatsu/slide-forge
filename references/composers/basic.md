*[日本語](basic.ja.md)*

# Basic Composer Specification

Composer function specification for the basic category (6 types).

---

## compose_title

**Master**: COVER | **Pattern**: Custom

Cover slide. Places the title, subtitle, and presenter information on a primary-colored background.

### Layout

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

### Code

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

**Master**: SECTION | **Pattern**: Pattern 7 (Icon+Text Row) applied

Table-of-contents slide. Displays the section structure as a numbered list. When currentIndex is specified, that item is highlighted.

### Layout

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

### Code

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

**Master**: SECTION | **Pattern**: Custom

Section divider. Centers the section number (optional) and title.

### Code

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

**Master**: HIGHLIGHT | **Pattern**: Pattern 8 (Stat Card) + text

Executive summary / conclusion. Emphasizes key points with white text on a dark background.

### Layout

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

### Code

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

**Master**: CLOSING | **Pattern**: Custom

Closing slide. Centers the logo and contact information.

### Placement constraints

The CLOSING master places a decorative band (image) at the bottom. **Contact information and text elements must be placed above the top edge (y coordinate) of the decorative band.**

| Element | Recommended Y position | Note |
|------|-----------|-----|
| "Thank you for your attention" etc. | decorative band y − 0.4" or more | Must not overlap the band |
| Contact information | decorative band y − 0.2" or more | The bottom edge of the text must not be hidden by the band |

> For the Scalar theme, `bottomBand.y = 3.667"`, so contact text should be adjusted to fit within y + h < 3.65".

### Code

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

**Master**: BLANK | **Pattern**: Custom

Appendix cover. Simply displays the "Appendix" title centered.

### Code

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
