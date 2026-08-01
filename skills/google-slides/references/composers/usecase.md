# ユースケースカテゴリ コンポーザー仕様

> usecase カテゴリ 6 タイプのレンダリング仕様。
> 各コンポーザーはマスター関数で共通要素を配置した後、タイプ固有のコンテンツを追加する。

### 規約

- **`C`** — `templates/<theme>/theme.json` の `colors` セクションから展開した色定数クラス
- **`L`** — `templates/<theme>/theme.json` の `layouts` セクションから展開したレイアウト定数クラス
- **`sb`** — `SlideBuilder` インスタンス
- **ページサイズ** — 10.0" x 5.625"（Google Slides 16:9）
- **CONTENT マスター** — title: (0.323, 0.303, 9.354, 0.437), body: y=0.787 ~ y=5.208 (h=4.421")
- **SPLIT_SCREEN マスター** — 左パネル 0~5.0" (primary bg), 右パネル 5.0~10.0" (white bg)
- **HIGHLIGHT マスター** — primary 色全面背景, 白テキスト

---

## 1. usecase_overview — ユースケース全体像

### マスター・パターン

- **マスター**: CONTENT（フッター付き）
- **パターン**: Pattern 7 (Icon+Text Row) + Pattern 6 (Pyramid)

### レイアウト

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

### 座標定数

| 要素 | X | Y | W | H |
|------|-----|-----|------|------|
| タイトル | 0.323 | 0.303 | 9.354 | 0.437 |
| 業界バッジ | 0.500 | 0.850 | 2.000 | 0.300 |
| 課題ラベル | 0.500 | 1.250 | 1.200 | 0.250 |
| 課題テキスト | 0.500 | 1.500 | 9.000 | 0.500 |
| 解決策ラベル | 0.500 | 2.100 | 1.200 | 0.250 |
| 解決策テキスト | 0.500 | 2.350 | 9.000 | 0.500 |
| 成果カード開始 | 0.500 | 3.100 | — | — |

### コード

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

## 2. problem_solution — 課題→解決策の対比

### マスター・パターン

- **マスター**: SPLIT_SCREEN（左右分割 + フッター付き）
- **パターン**: Pattern 9 (Comparison)

### レイアウト

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

### 座標定数

| 要素 | X | Y | W | H |
|------|-----|-----|------|------|
| 左パネル背景 | 0.000 | 0.000 | 5.000 | 5.625 |
| 右パネル背景 | 5.000 | 0.000 | 5.000 | 5.625 |
| 左タイトル | 0.500 | 0.800 | 4.000 | 0.350 |
| 左セパレーター | 0.500 | 1.180 | 2.000 | 0.025 |
| 左箇条書き開始 | 0.500 | 1.350 | 4.000 | — |
| 右タイトル | 5.500 | 0.800 | 4.000 | 0.350 |
| 右セパレーター | 5.500 | 1.180 | 2.000 | 0.025 |
| 右箇条書き開始 | 5.500 | 1.350 | 4.000 | — |
| 箇条書き行高 | — | — | — | 0.450 |

### コード

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

## 3. case_study — 導入事例・ケーススタディ

### マスター・パターン

- **マスター**: CONTENT（フッター付き）
- **パターン**: Pattern 8 (Stat Card) + テキストレイアウト

### レイアウト

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

### 座標定数

| 要素 | X | Y | W | H |
|------|-----|-----|------|------|
| タイトル | 0.323 | 0.303 | 9.354 | 0.437 |
| ロゴ | 0.500 | 0.850 | 0.600 | 0.600 |
| 企業名 | 1.250 | 0.850 | 8.250 | 0.300 |
| 業界ラベル | 1.250 | 1.150 | 8.250 | 0.250 |
| セパレーター | 0.500 | 1.480 | 9.000 | 0.020 |
| 課題テキスト | 0.500 | 1.550 | 9.000 | 0.350 |
| 解決テキスト | 0.500 | 1.950 | 9.000 | 0.350 |
| 成果カード開始 | 0.500 | 2.500 | — | 1.200 |
| 引用テキスト | 0.500 | 3.900 | 9.000 | 0.600 |

### コード

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

## 4. before_after — 導入前後の比較

### マスター・パターン

- **マスター**: SPLIT_SCREEN（左右分割 + フッター付き）
- **パターン**: Pattern 9 (Comparison)

### レイアウト

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

### 座標定数

| 要素 | X | Y | W | H |
|------|-----|-----|------|------|
| 左パネル背景 | 0.000 | 0.000 | 5.000 | 5.625 |
| 右パネル背景 | 5.000 | 0.000 | 5.000 | 5.625 |
| 左タイトル | 0.500 | 0.800 | 4.000 | 0.350 |
| 左セパレーター | 0.500 | 1.180 | 2.000 | 0.025 |
| 左箇条書き開始 | 0.500 | 1.350 | 4.000 | — |
| 右タイトル | 5.500 | 0.800 | 4.000 | 0.350 |
| 右セパレーター | 5.500 | 1.180 | 2.000 | 0.025 |
| 右箇条書き開始 | 5.500 | 1.350 | 4.000 | — |
| 箇条書き行高 | — | — | — | 0.450 |

### コード

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

## 5. roi_impact — ROI・導入効果の数値表示

### マスター・パターン

- **マスター**: HIGHLIGHT（primary 背景、白テキスト）
- **パターン**: Pattern 8 (Stat Card)

### レイアウト

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

### 座標定数

| 要素 | X | Y | W | H |
|------|-----|-----|------|------|
| 背景 | 0.000 | 0.000 | 10.000 | 5.625 |
| タイトル | 0.500 | 0.500 | 9.000 | 0.500 |
| KPI カード領域 | 0.500 | 1.300 | 9.000 | — |
| KPI カード高 | — | — | — | 2.200 |
| サマリーテキスト | 0.500 | 4.200 | 9.000 | 0.500 |

### コード

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

## 6. deployment_steps — 導入ステップ・フェーズ

### マスター・パターン

- **マスター**: CONTENT（フッター付き）
- **パターン**: Pattern 2 (H-Timeline) + Pattern 10 (Flow)

### レイアウト

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

### 座標定数

| 要素 | X | Y | W | H |
|------|-----|-----|------|------|
| タイトル | 0.323 | 0.303 | 9.354 | 0.437 |
| フェーズカード領域 | 0.500 | 0.900 | 9.000 | — |
| フェーズヘッダー高 | — | — | — | 0.700 |
| タスクリスト高 | — | — | — | 動的 |
| カード間ギャップ | — | — | 0.350 | — |
| 矢印コネクタ | — | — | 0.350 | — |

### コード

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

## 共通注意事項

### テキスト制約

| フィールド | 日本語上限 | 英語上限 |
|-----------|----------|---------|
| アクションタイトル | 50文字 | 100文字 |
| 箇条書き1項目 | 40文字 | 80文字 |
| KPI値 | 簡潔（数文字） | 同左 |
| メトリクス数 | 2-4個 | 同左 |
| フェーズ数 | 3-5個 | 同左 |
| スピーカーノート | 200文字 | 400文字 |

### マスター別テキストスタイル

#### CONTENT マスター（usecase_overview, case_study, deployment_steps）

| 要素 | フォント | サイズ | 色 | ウェイト |
|------|---------|-------|-----|---------|
| アクションタイトル | fontFaceTitle | contentTitle pt | textTitle | bold |
| サブヘッダー | fontFaceBody | 14-16pt | textSecondary | bold |
| 本文 | fontFaceBody | 12-13pt | textPrimary | normal |
| フッター | fontFaceEn | 10pt | textMuted | normal |

#### SPLIT_SCREEN マスター（problem_solution, before_after）

| 要素 | フォント | サイズ | 色 | ウェイト |
|------|---------|-------|-----|---------|
| 左パネルタイトル | fontFaceTitle | 20pt | textOnDark (白) | bold |
| 左パネル本文 | fontFaceBody | 13pt | textOnDark (白) | normal |
| 右パネルタイトル | fontFaceTitle | 20pt | textTitle | bold |
| 右パネル本文 | fontFaceBody | 13pt | textPrimary | normal |

#### HIGHLIGHT マスター（roi_impact）

| 要素 | フォント | サイズ | 色 | ウェイト |
|------|---------|-------|-----|---------|
| タイトル | fontFaceTitle | 24pt | textOnDark (白) | bold |
| KPI 数値 | fontFaceAccent | 48pt | textOnDark (白) | bold |
| KPI ラベル | fontFaceBody | 14pt | textOnDark (白) | bold |
| 補足テキスト | fontFaceBody | 11pt | textOnDark (白) | normal |

### カラー運用

- SPLIT_SCREEN の左パネルは primary 背景のため、全テキストは白系（`textOnDark`）を使用
- HIGHLIGHT は primary 全面背景のため、全テキストは白系を使用。カードは半透明白（opacity=0.15）で視覚的区切りを作る
- 成果カード（case_study, usecase_overview）は `add_stat_card` パターンを使用し、上部カラーバーは 0.025" の細線
- 課題ポイントには `C.error`（赤）マーカー、解決ポイントには `C.success`（緑）マーカーでセマンティックカラーを適用
- フェーズカード（deployment_steps）は同系色のグラデーション（淡→濃）で進行を表現

### アクションタイトル例

| NG（ラベル型） | OK（アクションタイトル） |
|:-------------:|:--------------------:|
| 「ユースケース」 | 「金融業界の異種DB統合課題を ScalarDB が解決する」 |
| 「課題と解決策」 | 「手動データ整合管理を自動化し運用工数を80%削減」 |
| 「導入事例」 | 「A社は ScalarDB 導入でトランザクション処理速度を3倍に改善した」 |
| 「導入前後」 | 「DB別の個別実装からAPI統一により開発期間を半減」 |
| 「導入効果」 | 「年間1.2M ドルのコスト削減と99.99% 可用性を同時に達成」 |
| 「導入ステップ」 | 「3フェーズ8週間で本番環境への移行を完了する」 |
