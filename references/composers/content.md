*[日本語](content.ja.md)*

# Content Composer Specification

Composer function specification for the content category (9 types).

---

## compose_text_bullets

**Master**: CONTENT | **Pattern**: Direct text placement

Bulleted enumeration of key points. The most basic content slide.

### Layout

```
┌──────────────────────────────────────┐
│  アクションタイトル ─→ 26pt bold     │
│  サブタイトル ────────→ 14pt muted   │
│                                      │
│  ● ブレット項目 1 ──→ 16pt          │
│  ● ブレット項目 2                    │
│  ● ブレット項目 3                    │
│  ● ブレット項目 4                    │
│                                      │
│                                      │
│  脚注 ──────────────→ 10pt muted    │
│  [Logo]  (C) 2026 Scalar    Page 5   │
└──────────────────────────────────────┘
```

### Code

```python
def compose_text_bullets(sb, content, theme, slide_id, page_num):
    apply_master_content(sb, theme, slide_id, page_num)
    apply_action_title(sb, theme, slide_id, content["title"], content.get("subtitle"))
    colors = theme["colors"]
    layout = theme["layouts"]["CONTENT"]

    # 箇条書き
    start_y = layout["elements"]["contentTop"]["y"] + 0.2
    bullet_h = 0.45
    for i, bullet in enumerate(content["bullets"]):
        sb.add_text(f"{slide_id}_bullet_{i}", f"  {bullet}",
            0.5, start_y + i * bullet_h, 9.0, bullet_h,
            font=theme["fonts"]["fontFaceBody"], size=theme["fontSizes"]["bodyLevel1"],
            color=colors["textPrimary"], line_spacing=theme["lineSpacing"]["bodyJapanese"])

    # 脚注
    if content.get("footnote"):
        sb.add_text(f"{slide_id}_footnote", content["footnote"],
            0.5, layout["elements"]["contentBottom"]["y"] - 0.3, 8.5, 0.25,
            font=theme["fonts"]["fontFaceBody"], size=10,
            color=colors["textMuted"])
```

---

## compose_columns

**Master**: CONTENT | **Pattern**: Pattern 9 (Comparison) applied

2-3 column parallel layout. Each column contains an icon, heading, and bullet list.

### Code

```python
def compose_columns(sb, content, theme, slide_id, page_num):
    apply_master_content(sb, theme, slide_id, page_num)
    apply_action_title(sb, theme, slide_id, content["title"])
    colors = theme["colors"]

    cols = content["columns"]
    n = len(cols)
    gap = 0.3
    total_w = 9.0
    col_w = (total_w - gap * (n - 1)) / n
    start_x = 0.5
    start_y = 1.2

    for i, col in enumerate(cols):
        cx = start_x + i * (col_w + gap)

        # カード背景
        sb.add_rounded_rect(f"{slide_id}_card_{i}",
            cx, start_y, col_w, 3.8,
            fill=colors["surfaceLight"], radius=0.08)

        # カラーバー
        sb.add_rect(f"{slide_id}_bar_{i}",
            cx, start_y, col_w, 0.05,
            fill=colors["primary"])

        # アイコン（オプション）
        icon_offset = 0
        if col.get("icon"):
            sb.add_badge(f"{slide_id}_icon_{i}", col["icon"],
                cx + col_w / 2, start_y + 0.25, 0.18,
                fill=colors["primary"], text_color=colors["textOnDark"], size=12)
            icon_offset = 0.5

        # 見出し
        sb.add_text(f"{slide_id}_heading_{i}", col["heading"],
            cx + 0.15, start_y + 0.15 + icon_offset, col_w - 0.3, 0.35,
            font=theme["fonts"]["fontFaceTitle"], size=14,
            color=colors["textTitle"], bold=True, align="CENTER")

        # 箇条書き
        bullet_y = start_y + 0.6 + icon_offset
        for j, bullet in enumerate(col.get("bullets", [])):
            sb.add_text(f"{slide_id}_col{i}_b{j}", f"  {bullet}",
                cx + 0.15, bullet_y + j * 0.38, col_w - 0.3, 0.35,
                font=theme["fonts"]["fontFaceBody"], size=12,
                color=colors["textPrimary"])
```

---

## compose_image_text

**Master**: CONTENT | **Pattern**: Image + text split

Places an image and text in a left/right split. The left/right sides can be swapped via imagePosition.

### Code

```python
def compose_image_text(sb, content, theme, slide_id, page_num):
    apply_master_content(sb, theme, slide_id, page_num)
    apply_action_title(sb, theme, slide_id, content["title"])
    colors = theme["colors"]

    pos = content.get("imagePosition", "right")
    img_w = 4.5
    text_w = 4.2
    gap = 0.3
    start_y = 1.0
    area_h = 3.8

    if pos == "right":
        text_x, img_x = 0.5, 5.2
    else:
        img_x, text_x = 0.5, 5.2

    # テキスト
    sb.add_text(f"{slide_id}_text", content["text"],
        text_x, start_y, text_w, 1.5,
        font=theme["fonts"]["fontFaceBody"], size=14,
        color=colors["textPrimary"], line_spacing=theme["lineSpacing"]["bodyJapanese"])

    # 箇条書き（オプション）
    if content.get("bullets"):
        bullet_y = start_y + 1.8
        for i, b in enumerate(content["bullets"]):
            sb.add_text(f"{slide_id}_b_{i}", f"  {b}",
                text_x, bullet_y + i * 0.4, text_w, 0.35,
                font=theme["fonts"]["fontFaceBody"], size=12,
                color=colors["textPrimary"])

    # 画像
    # sb.add_image_from_asset(slide_id, ..., content["imageAsset"],
    #     img_x, start_y, img_w, area_h)
```

---

## compose_chart

**Master**: CONTENT | **Pattern**: Sheets API integration

Creates data in Google Sheets and embeds a chart.

### Code

```python
def compose_chart(sb, content, theme, slide_id, page_num):
    apply_master_content(sb, theme, slide_id, page_num)
    apply_action_title(sb, theme, slide_id, content["title"])

    # チャートは Sheets API 連携で作成
    # 1. gspread でスプレッドシートにデータ書き込み
    # 2. Sheets API でチャート作成
    # 3. createSheetsChart でスライドに埋め込み

    chart_x, chart_y = 0.5, 1.0
    chart_w, chart_h = 9.0, 3.5

    # sb.add_sheets_chart(slide_id, spreadsheet_id, chart_id,
    #     chart_x, chart_y, chart_w, chart_h)

    # ソース表記
    if content.get("options", {}).get("source"):
        sb.add_text(f"{slide_id}_source", f"Source: {content['options']['source']}",
            0.5, 4.8, 8.0, 0.25,
            font=theme["fonts"]["fontFaceEn"], size=10,
            color=theme["colors"]["textMuted"])
```

---

## compose_table

**Master**: CONTENT | **Pattern**: Direct Table API

Displays data in table format. Header and alternating rows are colored using theme colors.

### Code

```python
def compose_table(sb, content, theme, slide_id, page_num):
    apply_master_content(sb, theme, slide_id, page_num)
    apply_action_title(sb, theme, slide_id, content["title"])
    colors = theme["colors"]
    ts = theme["tableStyle"]

    headers = content["headers"]
    rows = content["rows"]
    n_cols = len(headers)
    n_rows = len(rows) + 1  # +1 for header

    table_x, table_y = 0.5, 1.0
    table_w, table_h = 9.0, min(n_rows * 0.45, 3.8)

    sb.add_table(f"{slide_id}_table",
        table_x, table_y, table_w, table_h,
        n_rows, n_cols)

    # ヘッダー行
    for j, h in enumerate(headers):
        sb.set_table_cell(f"{slide_id}_table", 0, j, h,
            fill=colors[ts["headerFill"]],
            text_color=colors[ts["headerTextColor"]],
            font=ts["cellFont"], size=ts["headerFontSize"], bold=ts["headerBold"])

    # データ行
    for i, row in enumerate(rows):
        fill = colors[ts["altRowFill"]] if i % 2 == 1 else None
        for j, cell in enumerate(row):
            sb.set_table_cell(f"{slide_id}_table", i + 1, j, cell,
                fill=fill,
                font=ts["cellFont"], size=ts["cellFontSize"])

    # 脚注
    if content.get("footnote"):
        sb.add_text(f"{slide_id}_footnote", content["footnote"],
            0.5, table_y + table_h + 0.15, 8.5, 0.25,
            font=theme["fonts"]["fontFaceBody"], size=10,
            color=colors["textMuted"])
```

---

## compose_kpi_highlight

**Master**: HIGHLIGHT | **Pattern**: Pattern 8 (Stat Card)

Emphasized display of KPIs / key metrics. Large numbers on a dark background.

### KPI value font size guidelines

Adjust the font size according to the character count of the value so that the KPI value does not wrap relative to the card width.

| Card width | Value character count | Max font size | Example |
|---------|----------|----------------|-----|
| 2.0-2.2" | 4 chars or fewer | 32pt | "3x", "<5ms" |
| 2.0-2.2" | 5-6 chars | 28pt | "99.99%", "$1.2M" |
| 2.0-2.2" | 7 chars or more | 24pt | "99.999%" |
| 2.8" | 4 chars or fewer | 56pt | "3x", "100%" |
| 2.8" | 5-6 chars | 48pt | "<5ms", "99.9%" |
| 2.8" | 7 chars or more | 40pt | "99.999%", "$1.2M" |
| 3.0"+ | 7 chars or fewer | 56pt | — |
| 3.0"+ | 8 chars or more | 44pt | — |

> **Note**: Century Gothic (fontFaceAccent) is not monospaced, so "%" and "." are narrower than "M" or "W". The values above are safe upper bounds based on empirical measurement.

### Code

```python
def compose_kpi_highlight(sb, content, theme, slide_id):
    apply_master_highlight(sb, theme, slide_id)
    colors = theme["colors"]

    # タイトル（オプション）
    if content.get("title"):
        sb.add_text(f"{slide_id}_title", content["title"],
            0.5, 0.4, 9.0, 0.5,
            font=theme["fonts"]["fontFaceTitle"], size=20,
            color=colors["textOnDark"], bold=True, align="CENTER")

    kpis = content["kpis"]
    n = len(kpis)
    card_w = min(2.8, (9.0 - 0.3 * (n - 1)) / n)
    total_w = card_w * n + 0.3 * (n - 1)
    start_x = (10.0 - total_w) / 2
    card_y = 1.5
    card_h = 3.0

    for i, kpi in enumerate(kpis):
        cx = start_x + i * (card_w + 0.3)

        # 数値
        sb.add_text(f"{slide_id}_val_{i}", kpi["value"],
            cx, card_y, card_w, 1.5,
            font=theme["fonts"]["fontFaceAccent"], size=56,
            color=colors["textOnDark"], bold=True, align="CENTER",
            valign="BOTTOM")

        # ラベル
        sb.add_text(f"{slide_id}_label_{i}", kpi["label"],
            cx, card_y + 1.6, card_w, 0.4,
            font=theme["fonts"]["fontFaceBody"], size=14,
            color=colors["textOnDark"], align="CENTER")

        # 説明（オプション）
        if kpi.get("description"):
            sb.add_text(f"{slide_id}_desc_{i}", kpi["description"],
                cx, card_y + 2.1, card_w, 0.5,
                font=theme["fonts"]["fontFaceBody"], size=11,
                color=colors["textOnDark"], align="CENTER", opacity=0.8)
```

---

## compose_process_flow

**Master**: CONTENT | **Pattern**: Pattern 10 (Flow Diagram)

Process flow. 3-5 steps arranged horizontally and connected with arrows.

### Code

```python
def compose_process_flow(sb, content, theme, slide_id, page_num):
    apply_master_content(sb, theme, slide_id, page_num)
    apply_action_title(sb, theme, slide_id, content["title"])
    colors = theme["colors"]

    steps = content["steps"]
    n = len(steps)
    box_w = 1.8
    box_h = 1.2
    gap = 0.5
    total_w = box_w * n + gap * (n - 1)
    start_x = (10.0 - total_w) / 2
    box_y = 2.0

    for i, step in enumerate(steps):
        bx = start_x + i * (box_w + gap)

        # ボックス
        sb.add_rounded_rect(f"{slide_id}_box_{i}",
            bx, box_y, box_w, box_h,
            fill=colors["surfaceLight"], radius=0.08,
            border_color=colors["primary"], border_weight=1.5)

        # アイコン（オプション）
        if step.get("icon"):
            sb.add_badge(f"{slide_id}_icon_{i}", step["icon"],
                bx + box_w / 2, box_y + 0.25, 0.15,
                fill=colors["primary"], text_color=colors["textOnDark"], size=10)

        # ステップ名
        icon_offset = 0.4 if step.get("icon") else 0.15
        sb.add_text(f"{slide_id}_name_{i}", step["name"],
            bx + 0.1, box_y + icon_offset, box_w - 0.2, 0.35,
            font=theme["fonts"]["fontFaceTitle"], size=12,
            color=colors["textTitle"], bold=True, align="CENTER")

        # 説明
        if step.get("description"):
            sb.add_text(f"{slide_id}_desc_{i}", step["description"],
                bx + 0.1, box_y + icon_offset + 0.35, box_w - 0.2, 0.5,
                font=theme["fonts"]["fontFaceBody"], size=10,
                color=colors["textSecondary"], align="CENTER")

        # 矢印コネクタ（最後以外）
        if i < n - 1:
            sb.add_connector(f"{slide_id}_arrow_{i}",
                bx + box_w, box_y + box_h / 2,
                bx + box_w + gap, box_y + box_h / 2,
                color=colors["primary"], weight=2, end_arrow="FILL_ARROW")
```

---

## compose_quote

**Master**: QUOTE | **Pattern**: Custom

Quotation / customer testimonial. Large quote text and speaker information on a light background.

### Code

```python
def compose_quote(sb, content, theme, slide_id):
    apply_master_quote(sb, theme, slide_id)
    colors = theme["colors"]

    # 引用テキスト
    sb.add_text(f"{slide_id}_quote", content["quoteText"],
        1.5, 1.2, 7.0, 2.2,
        font=theme["fonts"]["fontFaceBody"], size=20,
        color=colors["textPrimary"], italic=True,
        line_spacing=200)

    # 発言者名
    sb.add_text(f"{slide_id}_name", f"-- {content['attribution']}",
        1.5, 3.6, 5.0, 0.35,
        font=theme["fonts"]["fontFaceBody"], size=14,
        color=colors["textTitle"], bold=True)

    # 役職（オプション）
    if content.get("role"):
        role_text = content["role"]
        if content.get("company"):
            role_text += f", {content['company']}"
        sb.add_text(f"{slide_id}_role", role_text,
            1.5, 3.95, 5.0, 0.3,
            font=theme["fonts"]["fontFaceBody"], size=12,
            color=colors["textMuted"])

    # 企業ロゴ（オプション）
    if content.get("companyLogo"):
        pass  # sb.add_image_from_asset(...)
```

---

## compose_icon_grid

**Master**: CONTENT | **Pattern**: Pattern 7 (Icon+Text Row)

Icon + text grid. Arranges 3-6 items in 2-3 columns x 1-2 rows.

### Code

```python
def compose_icon_grid(sb, content, theme, slide_id, page_num):
    apply_master_content(sb, theme, slide_id, page_num)
    apply_action_title(sb, theme, slide_id, content["title"])
    colors = theme["colors"]

    items = content["items"]
    n = len(items)
    cols = 3 if n > 4 else min(n, 3)
    rows_count = (n + cols - 1) // cols

    cell_w = 8.5 / cols
    cell_h = 3.5 / rows_count
    start_x = 0.75
    start_y = 1.2

    for idx, item in enumerate(items):
        row = idx // cols
        col = idx % cols
        ix = start_x + col * cell_w
        iy = start_y + row * cell_h

        # アイコンバッジ
        sb.add_badge(f"{slide_id}_icon_{idx}", item["icon"],
            ix + cell_w / 2, iy + 0.25, 0.22,
            fill=colors["primary"], text_color=colors["textOnDark"], size=14)

        # ラベル
        sb.add_text(f"{slide_id}_label_{idx}", item["label"],
            ix + 0.1, iy + 0.6, cell_w - 0.2, 0.3,
            font=theme["fonts"]["fontFaceTitle"], size=13,
            color=colors["textTitle"], bold=True, align="CENTER")

        # 説明（オプション）
        if item.get("description"):
            sb.add_text(f"{slide_id}_desc_{idx}", item["description"],
                ix + 0.1, iy + 0.95, cell_w - 0.2, 0.6,
                font=theme["fonts"]["fontFaceBody"], size=10,
                color=colors["textSecondary"], align="CENTER")
```
