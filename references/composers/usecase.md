*[日本語](usecase.ja.md)*

# Composer Specification: usecase Category

> Rendering specification for the 6 types in the usecase category.
> Each composer places the shared elements via its master function, then adds type-specific content.

### Conventions

- **`C`** — color constant class expanded from the `colors` section of `templates/<theme>/theme.json`
- **`L`** — layout constant class expanded from the `layouts` section of `templates/<theme>/theme.json`
- **`sb`** — `SlideBuilder` instance
- **Page size** — 10.0" x 5.625" (Google Slides 16:9)
- **CONTENT master** — title: (0.323, 0.303, 9.354, 0.437), body: y=0.787 ~ y=5.208 (h=4.421")
- **SPLIT_SCREEN master** — left panel 0~5.0" (primary bg), right panel 5.0~10.0" (white bg)
- **HIGHLIGHT master** — full-bleed primary-color background, white text

---

## 1. usecase_overview — Use case overview

### Master / Pattern

- **Master**: CONTENT (with footer)
- **Pattern**: Pattern 7 (Icon+Text Row) + Pattern 6 (Pyramid)

### Layout

```
┌──────────────────────────────────────────┐
│ [アクションタイトル]                         │ 0.303"
├──────────────────────────────────────────┤ 0.787"
│                                          │
│  業界: ○○    課題:                         │
│  ────────    xxxxxxxxxxxxxxxxx            │
│                                          │
│  解決策:                                   │
│  xxxxxxxxxxxxxxxxxxxxxxxxx                │
│                                          │
│  成果:                                     │
│  ┌──────┐  ┌──────┐  ┌──────┐            │
│  │成果1  │  │成果2  │  │成果3  │            │
│  └──────┘  └──────┘  └──────┘            │
│                                          │
├──────────────────────────────────────────┤
│  [フッター]                                │ 5.208"
└──────────────────────────────────────────┘
```

### Coordinate constants

| Element | X | Y | W | H |
|------|-----|-----|------|------|
| Title | 0.323 | 0.303 | 9.354 | 0.437 |
| Industry badge | 0.500 | 0.850 | 2.000 | 0.300 |
| Challenge label | 0.500 | 1.250 | 1.200 | 0.250 |
| Challenge text | 0.500 | 1.500 | 9.000 | 0.500 |
| Solution label | 0.500 | 2.100 | 1.200 | 0.250 |
| Solution text | 0.500 | 2.350 | 9.000 | 0.500 |
| Outcome card start | 0.500 | 3.100 | — | — |

### Code

```python
def compose_usecase_overview(sb, slide_id, content, theme, page_num, total_pages=None):
    """ユースケース全体像スライドを構築する。

    content: {
        title, industry, challenge, solution,
        outcomes: [str]
    }
    """
    apply_master_content(sb, theme, slide_id, page_num, total_pages)
    apply_action_title(sb, theme, slide_id, content["title"])

    # 業界バッジ
    sb.add_rounded_rect(slide_id, 0.500, 0.850, 2.000, 0.300,
        fill=C.primary)
    sb.add_text(slide_id, content["industry"],
        0.500, 0.850, 2.000, 0.300,
        font_size=12, bold=True,
        color={"red": 1, "green": 1, "blue": 1},
        alignment="CENTER", valign="MIDDLE")

    # 課題セクション
    sb.add_text(slide_id, "課題",
        0.500, 1.250, 1.200, 0.250,
        font_size=12, bold=True, color=C.error,
        alignment="START", valign="MIDDLE")
    sb.add_rect(slide_id, 0.500, 1.510, 9.000, 0.020, fill=C.border)
    sb.add_text(slide_id, content["challenge"],
        0.500, 1.550, 9.000, 0.450,
        font_size=13, color=C.textPrimary,
        alignment="START", valign="TOP")

    # 解決策セクション
    sb.add_text(slide_id, "解決策",
        0.500, 2.100, 1.200, 0.250,
        font_size=12, bold=True, color=C.success,
        alignment="START", valign="MIDDLE")
    sb.add_rect(slide_id, 0.500, 2.360, 9.000, 0.020, fill=C.border)
    sb.add_text(slide_id, content["solution"],
        0.500, 2.400, 9.000, 0.450,
        font_size=13, color=C.textPrimary,
        alignment="START", valign="TOP")

    # 成果カード
    outcomes = content.get("outcomes", [])
    n = len(outcomes)
    if n > 0:
        sb.add_text(slide_id, "成果",
            0.500, 3.000, 1.200, 0.250,
            font_size=12, bold=True, color=C.primary,
            alignment="START", valign="MIDDLE")

        card_gap = 0.250
        card_w = (9.000 - card_gap * (n - 1)) / n
        card_h = 0.800
        card_y = 3.300

        for i, outcome in enumerate(outcomes):
            cx = 0.500 + i * (card_w + card_gap)
            sb.add_rounded_rect(slide_id, cx, card_y, card_w, card_h,
                fill=C.surfaceLight, border_color=C.primary)
            # 上部アクセントバー
            sb.add_rect(slide_id, cx, card_y, card_w, 0.025, fill=C.primary)
            # テキスト
            sb.add_text(slide_id, outcome,
                cx + 0.100, card_y + 0.100, card_w - 0.200, card_h - 0.150,
                font_size=12, color=C.textPrimary,
                alignment="CENTER", valign="MIDDLE")
```

---

## 2. problem_solution — Problem-to-solution contrast

### Master / Pattern

- **Master**: SPLIT_SCREEN (left/right split, with footer)
- **Pattern**: Pattern 9 (Comparison)

### Layout

```
┌──────────────────────┬───────────────────┐
│                      │                   │
│  ← primary 背景 →    │  ← white 背景 →   │
│                      │                   │
│  課題見出し            │  解決策見出し       │
│  ──────              │  ──────           │
│                      │                   │
│  ✗ 課題ポイント1       │  ✓ 解決ポイント1   │
│  ✗ 課題ポイント2       │  ✓ 解決ポイント2   │
│  ✗ 課題ポイント3       │  ✓ 解決ポイント3   │
│                      │                   │
│  (textOnDark)        │  (textPrimary)    │
│                      │                   │
├──────────────────────┴───────────────────┤
│  [フッター: ロゴ | 著作権 | ページ番号]        │ 5.208"
└──────────────────────────────────────────┘
```

### Coordinate constants

| Element | X | Y | W | H |
|------|-----|-----|------|------|
| Left panel background | 0.000 | 0.000 | 5.000 | 5.625 |
| Right panel background | 5.000 | 0.000 | 5.000 | 5.625 |
| Left title | 0.500 | 0.800 | 4.000 | 0.350 |
| Left separator | 0.500 | 1.180 | 2.000 | 0.025 |
| Left bullet start | 0.500 | 1.350 | 4.000 | — |
| Right title | 5.500 | 0.800 | 4.000 | 0.350 |
| Right separator | 5.500 | 1.180 | 2.000 | 0.025 |
| Right bullet start | 5.500 | 1.350 | 4.000 | — |
| Bullet row height | — | — | — | 0.450 |

### Code

```python
def compose_problem_solution(sb, slide_id, content, theme, page_num, total_pages=None):
    """課題→解決策の対比スライドを構築する。

    content: {
        title,
        problem: {heading, points: [str]},
        solution: {heading, points: [str]}
    }
    """
    # 1. SPLIT_SCREEN マスター共通要素
    apply_master_split_screen(sb, theme, slide_id, page_num, total_pages)

    # 2. タイトル（スライド上部、全幅に跨る場合はここで配置）
    # SPLIT_SCREEN ではタイトルを省略するか、左パネル上部に配置
    if content.get("title"):
        sb.add_text(slide_id, content["title"],
            0.500, 0.300, 4.000, 0.350,
            font_size=18, bold=True,
            color={"red": 1, "green": 1, "blue": 1},
            alignment="START", valign="MIDDLE")

    bullet_h = 0.450

    # ── 左パネル（課題）──
    problem = content["problem"]

    # 課題見出し
    sb.add_text(slide_id, problem["heading"],
        0.500, 0.800, 4.000, 0.350,
        font_size=20, bold=True,
        color={"red": 1, "green": 1, "blue": 1},
        alignment="START", valign="MIDDLE")

    # セパレーター
    sb.add_rect(slide_id, 0.500, 1.180, 2.000, 0.025,
        fill={"red": 1, "green": 1, "blue": 1})

    # 課題ポイント（✗ マーカー付き）
    for i, point in enumerate(problem["points"]):
        py = 1.350 + i * bullet_h
        # マーカー
        sb.add_badge(slide_id, 0.620, py + 0.170, 0.10,
            "✗", fill=C.error,
            text_color={"red": 1, "green": 1, "blue": 1})
        # テキスト
        sb.add_text(slide_id, point,
            0.800, py, 3.700, bullet_h,
            font_size=13,
            color={"red": 1, "green": 1, "blue": 1},
            alignment="START", valign="MIDDLE")

    # ── 右パネル（解決策）──
    solution = content["solution"]

    # 解決策見出し
    sb.add_text(slide_id, solution["heading"],
        5.500, 0.800, 4.000, 0.350,
        font_size=20, bold=True, color=C.textTitle,
        alignment="START", valign="MIDDLE")

    # セパレーター
    sb.add_rect(slide_id, 5.500, 1.180, 2.000, 0.025,
        fill=C.primary)

    # 解決策ポイント（✓ マーカー付き）
    for i, point in enumerate(solution["points"]):
        py = 1.350 + i * bullet_h
        # マーカー
        sb.add_badge(slide_id, 5.620, py + 0.170, 0.10,
            "✓", fill=C.success,
            text_color={"red": 1, "green": 1, "blue": 1})
        # テキスト
        sb.add_text(slide_id, point,
            5.800, py, 3.700, bullet_h,
            font_size=13, color=C.textPrimary,
            alignment="START", valign="MIDDLE")
```

---

## 3. case_study — Case study / customer story

### Master / Pattern

- **Master**: CONTENT (with footer)
- **Pattern**: Pattern 8 (Stat Card) + text layout

### Layout

```
┌──────────────────────────────────────────┐
│ [アクションタイトル]                         │ 0.303"
├──────────────────────────────────────────┤ 0.787"
│                                          │
│  [企業ロゴ]  企業名 — 業界                   │
│  ──────────────────                       │
│                                          │
│  課題: xxxxxxxxxxxxxxxxxxxxxxxxxx          │
│  解決: xxxxxxxxxxxxxxxxxxxxxxxxxx          │
│                                          │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  │
│  │  指標値   │  │  指標値   │  │  指標値   │  │
│  │  指標名   │  │  指標名   │  │  指標名   │  │
│  └─────────┘  └─────────┘  └─────────┘  │
│                                          │
│  「顧客の声テキスト」(opt)                    │
│                                          │
├──────────────────────────────────────────┤
│  [フッター]                                │ 5.208"
└──────────────────────────────────────────┘
```

### Coordinate constants

| Element | X | Y | W | H |
|------|-----|-----|------|------|
| Title | 0.323 | 0.303 | 9.354 | 0.437 |
| Logo | 0.500 | 0.850 | 0.600 | 0.600 |
| Company name | 1.250 | 0.850 | 8.250 | 0.300 |
| Industry label | 1.250 | 1.150 | 8.250 | 0.250 |
| Separator | 0.500 | 1.480 | 9.000 | 0.020 |
| Challenge text | 0.500 | 1.550 | 9.000 | 0.350 |
| Solution text | 0.500 | 1.950 | 9.000 | 0.350 |
| Outcome card start | 0.500 | 2.500 | — | 1.200 |
| Quote text | 0.500 | 3.900 | 9.000 | 0.600 |

### Code

```python
def compose_case_study(sb, slide_id, content, theme, page_num, total_pages=None):
    """導入事例スライドを構築する。

    content: {
        title, company, industry, challenge, solution,
        results: [{metric, value, description (opt)}],
        quote (opt), companyLogo (opt)
    }
    """
    apply_master_content(sb, theme, slide_id, page_num, total_pages)
    apply_action_title(sb, theme, slide_id, content["title"])

    # 企業ロゴ（オプション）
    if content.get("companyLogo"):
        sb.add_image_from_asset(slide_id, theme["name"], "logos",
            content["companyLogo"],
            0.500, 0.850, 0.600, 0.600)
        text_x = 1.250
    else:
        text_x = 0.500

    # 企業名
    sb.add_text(slide_id, content["company"],
        text_x, 0.850, 9.500 - text_x, 0.300,
        font_size=18, bold=True, color=C.textTitle,
        alignment="START", valign="MIDDLE")

    # 業界ラベル
    sb.add_text(slide_id, content["industry"],
        text_x, 1.150, 9.500 - text_x, 0.250,
        font_size=12, color=C.textMuted,
        alignment="START", valign="MIDDLE")

    # セパレーター
    sb.add_rect(slide_id, 0.500, 1.480, 9.000, 0.020, fill=C.border)

    # 課題
    sb.add_text(slide_id, f"課題: {content['challenge']}",
        0.500, 1.550, 9.000, 0.350,
        font_size=12, color=C.textPrimary,
        alignment="START", valign="TOP")

    # 解決策
    sb.add_text(slide_id, f"解決策: {content['solution']}",
        0.500, 1.950, 9.000, 0.350,
        font_size=12, color=C.textPrimary,
        alignment="START", valign="TOP")

    # 成果カード（Stat Card パターン）
    results = content.get("results", [])
    n = len(results)
    if n > 0:
        card_gap = 0.300
        card_w = (9.000 - card_gap * (n - 1)) / n
        card_h = 1.200
        card_y = 2.500

        for i, result in enumerate(results):
            cx = 0.500 + i * (card_w + card_gap)
            sb.add_stat_card(slide_id,
                cx, card_y, card_w, card_h,
                result["value"], result["metric"],
                icon_color=C.primary)

    # 顧客の声（オプション）
    if content.get("quote"):
        quote_y = 3.900
        # 左アクセントバー
        sb.add_rect(slide_id, 0.500, quote_y, 0.040, 0.500, fill=C.primary)
        # 引用テキスト
        sb.add_text(slide_id, f"「{content['quote']}」",
            0.650, quote_y, 8.850, 0.500,
            font_size=12, italic=True, color=C.textSecondary,
            alignment="START", valign="MIDDLE")
```

---

## 4. before_after — Before/after comparison

### Master / Pattern

- **Master**: SPLIT_SCREEN (left/right split, with footer)
- **Pattern**: Pattern 9 (Comparison)

### Layout

```
┌──────────────────────┬───────────────────┐
│                      │                   │
│  ← primary 背景 →    │  ← white 背景 →   │
│                      │                   │
│  BEFORE              │  AFTER            │
│  ──────              │  ──────           │
│                      │                   │
│  ✗ ポイント1          │  ✓ ポイント1       │
│  ✗ ポイント2          │  ✓ ポイント2       │
│  ✗ ポイント3          │  ✓ ポイント3       │
│  ✗ ポイント4          │  ✓ ポイント4       │
│                      │                   │
│  (textOnDark)        │  (textPrimary)    │
│                      │                   │
├──────────────────────┴───────────────────┤
│  [フッター: ロゴ | 著作権 | ページ番号]        │ 5.208"
└──────────────────────────────────────────┘
```

### Coordinate constants

| Element | X | Y | W | H |
|------|-----|-----|------|------|
| Left panel background | 0.000 | 0.000 | 5.000 | 5.625 |
| Right panel background | 5.000 | 0.000 | 5.000 | 5.625 |
| Left title | 0.500 | 0.800 | 4.000 | 0.350 |
| Left separator | 0.500 | 1.180 | 2.000 | 0.025 |
| Left bullet start | 0.500 | 1.350 | 4.000 | — |
| Right title | 5.500 | 0.800 | 4.000 | 0.350 |
| Right separator | 5.500 | 1.180 | 2.000 | 0.025 |
| Right bullet start | 5.500 | 1.350 | 4.000 | — |
| Bullet row height | — | — | — | 0.450 |

### Code

```python
def compose_before_after(sb, slide_id, content, theme, page_num, total_pages=None):
    """導入前後の比較スライドを構築する。

    content: {
        title,
        before: {heading, points: [str]},
        after:  {heading, points: [str]}
    }
    """
    # 1. SPLIT_SCREEN マスター共通要素
    apply_master_split_screen(sb, theme, slide_id, page_num, total_pages)

    # 2. タイトル（左パネル上部）
    if content.get("title"):
        sb.add_text(slide_id, content["title"],
            0.500, 0.300, 4.000, 0.350,
            font_size=18, bold=True,
            color={"red": 1, "green": 1, "blue": 1},
            alignment="START", valign="MIDDLE")

    bullet_h = 0.450

    # ── 左パネル（Before）──
    before = content["before"]

    # Before 見出し
    sb.add_text(slide_id, before["heading"],
        0.500, 0.800, 4.000, 0.350,
        font_size=20, bold=True,
        color={"red": 1, "green": 1, "blue": 1},
        alignment="START", valign="MIDDLE")

    # セパレーター
    sb.add_rect(slide_id, 0.500, 1.180, 2.000, 0.025,
        fill={"red": 1, "green": 1, "blue": 1})

    # Before ポイント
    for i, point in enumerate(before["points"]):
        py = 1.350 + i * bullet_h
        sb.add_badge(slide_id, 0.620, py + 0.170, 0.10,
            "✗", fill=C.error,
            text_color={"red": 1, "green": 1, "blue": 1})
        sb.add_text(slide_id, point,
            0.800, py, 3.700, bullet_h,
            font_size=13,
            color={"red": 1, "green": 1, "blue": 1},
            alignment="START", valign="MIDDLE")

    # ── 右パネル（After）──
    after = content["after"]

    # After 見出し
    sb.add_text(slide_id, after["heading"],
        5.500, 0.800, 4.000, 0.350,
        font_size=20, bold=True, color=C.textTitle,
        alignment="START", valign="MIDDLE")

    # セパレーター
    sb.add_rect(slide_id, 5.500, 1.180, 2.000, 0.025,
        fill=C.primary)

    # After ポイント
    for i, point in enumerate(after["points"]):
        py = 1.350 + i * bullet_h
        sb.add_badge(slide_id, 5.620, py + 0.170, 0.10,
            "✓", fill=C.success,
            text_color={"red": 1, "green": 1, "blue": 1})
        sb.add_text(slide_id, point,
            5.800, py, 3.700, bullet_h,
            font_size=13, color=C.textPrimary,
            alignment="START", valign="MIDDLE")

    # 中央の矢印装飾（Before → After の視覚的遷移）
    sb.add_text(slide_id, "→",
        4.600, 2.500, 0.800, 0.500,
        font_size=28, bold=True,
        color=C.primary,
        alignment="CENTER", valign="MIDDLE")
```

---

## 5. roi_impact — ROI / impact metrics display

### Master / Pattern

- **Master**: HIGHLIGHT (primary background, white text)
- **Pattern**: Pattern 8 (Stat Card)

### Layout

```
┌──────────────────────────────────────────┐
│                                          │
│  ← primary 色 全面背景 →                   │
│                                          │
│  [タイトル (opt, 白テキスト)]                 │
│                                          │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  │
│  │   40%    │  │   3x    │  │  $1.2M  │  │
│  │コスト削減 │  │性能向上  │  │年間節約  │  │
│  │ 補足     │  │ 補足     │  │ 補足     │  │
│  └─────────┘  └─────────┘  └─────────┘  │
│                                          │
│  [ROI サマリー (opt)]                       │
│                                          │
└──────────────────────────────────────────┘
```

### Coordinate constants

| Element | X | Y | W | H |
|------|-----|-----|------|------|
| Background | 0.000 | 0.000 | 10.000 | 5.625 |
| Title | 0.500 | 0.500 | 9.000 | 0.500 |
| KPI card area | 0.500 | 1.300 | 9.000 | — |
| KPI card height | — | — | — | 2.200 |
| Summary text | 0.500 | 4.200 | 9.000 | 0.500 |

### Code

```python
def compose_roi_impact(sb, slide_id, content, theme, page_num, total_pages=None):
    """ROI・導入効果の数値表示スライドを構築する。

    content: {
        title (opt),
        metrics: [{value, label, description (opt)}],
        summary (opt)
    }
    """
    # 1. HIGHLIGHT マスター共通要素
    apply_master_highlight(sb, theme, slide_id)

    # 2. タイトル（オプション）
    if content.get("title"):
        sb.add_text(slide_id, content["title"],
            0.500, 0.500, 9.000, 0.500,
            font_size=24, bold=True,
            color={"red": 1, "green": 1, "blue": 1},
            alignment="CENTER", valign="MIDDLE")

    # 3. メトリクスカード
    metrics = content["metrics"]
    n = len(metrics)
    card_gap = 0.400
    card_w = (9.000 - card_gap * (n - 1)) / n
    card_h = 2.200
    card_y = 1.300
    start_x = 0.500

    for i, metric in enumerate(metrics):
        cx = start_x + i * (card_w + card_gap)

        # カード背景（半透明白）
        card_id = sb.add_rounded_rect(slide_id, cx, card_y, card_w, card_h,
            fill={"red": 1, "green": 1, "blue": 1})
        sb.shape_opacity(card_id, 0.15)

        # 値（大きなフォント）
        sb.add_text(slide_id, metric["value"],
            cx, card_y + 0.200, card_w, 0.900,
            font_size=48, bold=True,
            color={"red": 1, "green": 1, "blue": 1},
            alignment="CENTER", valign="MIDDLE")

        # ラベル
        sb.add_text(slide_id, metric["label"],
            cx + 0.100, card_y + 1.200, card_w - 0.200, 0.400,
            font_size=14, bold=True,
            color={"red": 1, "green": 1, "blue": 1},
            alignment="CENTER", valign="TOP")

        # 補足説明（オプション）
        if metric.get("description"):
            sb.add_text(slide_id, metric["description"],
                cx + 0.100, card_y + 1.650, card_w - 0.200, 0.400,
                font_size=11,
                color={"red": 1, "green": 1, "blue": 1},
                alignment="CENTER", valign="TOP")

    # 4. ROI サマリー（オプション）
    if content.get("summary"):
        sb.add_text(slide_id, content["summary"],
            0.500, 4.200, 9.000, 0.500,
            font_size=14,
            color={"red": 1, "green": 1, "blue": 1},
            alignment="CENTER", valign="MIDDLE")
```

---

## 6. deployment_steps — Deployment steps / phases

### Master / Pattern

- **Master**: CONTENT (with footer)
- **Pattern**: Pattern 2 (H-Timeline) + Pattern 10 (Flow)

### Layout

```
┌──────────────────────────────────────────┐
│ [アクションタイトル]                         │ 0.303"
├──────────────────────────────────────────┤ 0.787"
│                                          │
│  Phase 1         Phase 2         Phase 3 │
│  ┌─────────┐     ┌─────────┐     ┌──────│
│  │ フェーズ名│ ──→ │ フェーズ名│ ──→ │ フェー│
│  │ (期間)   │     │ (期間)   │     │ (期間│
│  ├─────────┤     ├─────────┤     ├──────│
│  │ ・タスク1 │     │ ・タスク1 │     │ ・タス│
│  │ ・タスク2 │     │ ・タスク2 │     │ ・タス│
│  │ ・タスク3 │     │ ・タスク3 │     │ ・タス│
│  └─────────┘     └─────────┘     └──────│
│                                          │
├──────────────────────────────────────────┤
│  [フッター]                                │ 5.208"
└──────────────────────────────────────────┘
```

### Coordinate constants

| Element | X | Y | W | H |
|------|-----|-----|------|------|
| Title | 0.323 | 0.303 | 9.354 | 0.437 |
| Phase card area | 0.500 | 0.900 | 9.000 | — |
| Phase header height | — | — | — | 0.700 |
| Task list height | — | — | — | dynamic |
| Card gap | — | — | 0.350 | — |
| Arrow connector | — | — | 0.350 | — |

### Code

```python
def compose_deployment_steps(sb, slide_id, content, theme, page_num, total_pages=None):
    """導入ステップスライドを構築する。

    content: {
        title,
        phases: [{name, duration, tasks: [str]}]
    }
    """
    apply_master_content(sb, theme, slide_id, page_num, total_pages)
    apply_action_title(sb, theme, slide_id, content["title"])

    phases = content["phases"]
    n = len(phases)

    card_area_x = 0.500
    card_area_w = 9.000
    card_gap = 0.350
    card_w = (card_area_w - card_gap * (n - 1)) / n
    card_y = 0.900
    header_h = 0.700
    task_row_h = 0.320

    # 最大タスク数を算出（カード高さを揃えるため）
    max_tasks = max(len(p.get("tasks", [])) for p in phases)
    card_h = header_h + max_tasks * task_row_h + 0.200

    # フェーズ番号の色グラデーション（同系色の段階変化）
    phase_colors = []
    base = C.primary
    for i in range(n):
        t = i / max(n - 1, 1)
        factor = 0.5 + 0.5 * t  # 0.5（淡い）→ 1.0（原色）
        phase_colors.append({
            "red":   base["red"]   * factor,
            "green": base["green"] * factor,
            "blue":  base["blue"]  * factor,
        })

    for i, phase in enumerate(phases):
        cx = card_area_x + i * (card_w + card_gap)
        pc = phase_colors[i]

        # カード背景
        sb.add_rounded_rect(slide_id, cx, card_y, card_w, card_h,
            fill=C.background, border_color=pc)

        # ヘッダー背景
        sb.add_rect(slide_id, cx, card_y, card_w, header_h, fill=pc)

        # フェーズ番号バッジ
        sb.add_badge(slide_id, cx + 0.300, card_y + 0.150, 0.15,
            str(i + 1), fill={"red": 1, "green": 1, "blue": 1},
            text_color=pc)

        # フェーズ名
        sb.add_text(slide_id, phase["name"],
            cx + 0.550, card_y + 0.050, card_w - 0.650, 0.350,
            font_size=13, bold=True,
            color={"red": 1, "green": 1, "blue": 1},
            alignment="START", valign="MIDDLE")

        # 期間
        sb.add_text(slide_id, phase["duration"],
            cx + 0.550, card_y + 0.380, card_w - 0.650, 0.250,
            font_size=10,
            color={"red": 1, "green": 1, "blue": 1},
            alignment="START", valign="MIDDLE")

        # タスクリスト
        tasks = phase.get("tasks", [])
        for ti, task in enumerate(tasks):
            ty = card_y + header_h + 0.100 + ti * task_row_h
            sb.add_text(slide_id, f"• {task}",
                cx + 0.150, ty, card_w - 0.300, task_row_h,
                font_size=11, color=C.textPrimary,
                alignment="START", valign="MIDDLE")

        # フェーズ間矢印コネクタ
        if i < n - 1:
            arrow_x1 = cx + card_w
            arrow_x2 = cx + card_w + card_gap
            arrow_y = card_y + card_h / 2
            sb.add_connector(slide_id,
                arrow_x1, arrow_y, arrow_x2, arrow_y,
                color=C.textMuted, weight=2.0,
                end_arrow="FILL_ARROW")
```

---

## Common notes

### Text constraints

| Field | Japanese limit | English limit |
|-----------|----------|---------|
| Action title | 50 characters | 100 characters |
| Bullet item | 40 characters | 80 characters |
| KPI value | concise (a few characters) | same |
| Number of metrics | 2-4 | same |
| Number of phases | 3-5 | same |
| Speaker notes | 200 characters | 400 characters |

### Text style by master

#### CONTENT master (usecase_overview, case_study, deployment_steps)

| Element | Font | Size | Color | Weight |
|------|---------|-------|-----|---------|
| Action title | fontFaceTitle | contentTitle pt | textTitle | bold |
| Subheader | fontFaceBody | 14-16pt | textSecondary | bold |
| Body | fontFaceBody | 12-13pt | textPrimary | normal |
| Footer | fontFaceEn | 10pt | textMuted | normal |

#### SPLIT_SCREEN master (problem_solution, before_after)

| Element | Font | Size | Color | Weight |
|------|---------|-------|-----|---------|
| Left panel title | fontFaceTitle | 20pt | textOnDark (white) | bold |
| Left panel body | fontFaceBody | 13pt | textOnDark (white) | normal |
| Right panel title | fontFaceTitle | 20pt | textTitle | bold |
| Right panel body | fontFaceBody | 13pt | textPrimary | normal |

#### HIGHLIGHT master (roi_impact)

| Element | Font | Size | Color | Weight |
|------|---------|-------|-----|---------|
| Title | fontFaceTitle | 24pt | textOnDark (white) | bold |
| KPI value | fontFaceAccent | 48pt | textOnDark (white) | bold |
| KPI label | fontFaceBody | 14pt | textOnDark (white) | bold |
| Supplementary text | fontFaceBody | 11pt | textOnDark (white) | normal |

### Color usage

- The SPLIT_SCREEN left panel has a primary background, so all text uses a white variant (`textOnDark`)
- HIGHLIGHT has a full-bleed primary background, so all text uses a white variant. Cards use semi-transparent white (opacity=0.15) to create visual separation
- Outcome cards (case_study, usecase_overview) use the `add_stat_card` pattern, with a 0.025" thin top color bar
- Challenge points use a `C.error` (red) marker and solution points use a `C.success` (green) marker to apply semantic color
- Phase cards (deployment_steps) express progression through a same-hue gradient (light → dark)

### Action title examples

| NG (label-style) | OK (action title) |
|:-------------:|:--------------------:|
| "Use cases" | "ScalarDB solves the heterogeneous-DB integration challenge in the financial industry" |
| "Problem and solution" | "Automating manual data-consistency management cuts operational effort by 80%" |
| "Case study" | "Company A tripled transaction processing speed by adopting ScalarDB" |
| "Before/after" | "Unifying per-DB implementations into a single API halves development time" |
| "Impact" | "Achieving $1.2M in annual cost savings and 99.99% availability simultaneously" |
| "Deployment steps" | "Completing production migration in 3 phases over 8 weeks" |
