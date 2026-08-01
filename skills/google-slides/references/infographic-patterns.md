# インフォグラフィクス用コンポジットパターン

> SlideBuilder の低レベルメソッド（`add_shape`, `add_text`, `add_connector` 等）を組み合わせた
> 高レベルパターン集。各パターンは SlideBuilder のメソッドとして実装する。

### 規約

本ドキュメントで使用する識別子:

- **`C`** — `templates/<theme>/theme.json` の `colors` セクションから展開した色定数クラス（SKILL.md Phase 1 参照）
- **`L`** — `templates/<theme>/theme.json` の `layouts` セクションから展開したレイアウト定数クラス
- **`sb`** / **`self`** — `SlideBuilder` インスタンス（パターンは SlideBuilder のメソッドとして実装）

---

## 1. プログレスバー

進捗率をバー表示する。背景バー + 前景バー + ラベル。

```
┌────────────────────────────────┐
│ ██████████████░░░░░░░░  68%    │
└────────────────────────────────┘
```

```python
def add_progress_bar(self, slide_id, x, y, w, h, percent,
                     fill, bg, label=None, label_color=None):
    """プログレスバーを描画する。

    percent: 0〜100 の数値。
    fill: 前景色（RGB dict）。bg: 背景色。
    label: バー右端に表示するテキスト（例: "68%"）。
    """
    # 背景バー（角丸）
    self.add_rounded_rect(slide_id, x, y, w, h, fill=bg)
    # 前景バー（角丸）
    bar_w = max(w * (percent / 100.0), h)  # 最小幅 = 高さ（角丸が潰れない）
    self.add_rounded_rect(slide_id, x, y, bar_w, h, fill=fill)
    # ラベル
    if label:
        self.add_text(slide_id, label,
                      x + w + 0.1, y, 0.6, h,
                      font_size=max(int(h * 40), 10), bold=True,
                      color=label_color or fill,
                      alignment="START", valign="MIDDLE")
```

### 使用例

```python
sid = sb.add_slide()
sb.set_bg(sid, C.background)
sb.add_progress_bar(sid, 1.0, 2.0, 6.0, 0.25, 68,
                    fill=C.primary, bg=C.surfaceLight, label="68%")
```

---

## 2. タイムライン（水平）

時系列イベントを水平線上にマーカーで表示する。テキストは上下交互に配置。

```
         Event A      Event C
            ●────────────●
    ────────●────────────●────────
            ●────────────●
         Event B      Event D
```

```python
def add_timeline_h(self, slide_id, x, y, w, events, line_color=None, marker_color=None):
    """水平タイムラインを描画する。

    events: list of {"label": str, "sublabel": str (optional)}
    テキストは上下交互に配置される。
    """
    lc = line_color or C.border
    mc = marker_color or C.primary
    n = len(events)
    # メインの水平線
    self.add_line(slide_id, x, y, w, color=lc, weight=2.0)
    # イベントマーカーとラベル
    for i, evt in enumerate(events):
        ex = x + (w / (n - 1)) * i if n > 1 else x + w / 2
        # 円マーカー
        self.add_circle(slide_id, ex, y, 0.12, fill=mc)
        # テキスト位置（上下交互）
        if i % 2 == 0:
            ty = y - 0.55  # 上側
        else:
            ty = y + 0.20  # 下側
        self.add_text(slide_id, evt["label"],
                      ex - 0.6, ty, 1.2, 0.30,
                      font_size=12, bold=True, color=C.textTitle,
                      alignment="CENTER", valign="MIDDLE")
        if evt.get("sublabel"):
            offset = -0.25 if i % 2 == 0 else 0.25
            self.add_text(slide_id, evt["sublabel"],
                          ex - 0.8, ty + offset, 1.6, 0.25,
                          font_size=10, color=C.textSecondary,
                          alignment="CENTER", valign="MIDDLE")
```

### 使用例

```python
events = [
    {"label": "2023 Q1", "sublabel": "プロジェクト開始"},
    {"label": "2023 Q3", "sublabel": "MVP リリース"},
    {"label": "2024 Q1", "sublabel": "GA リリース"},
    {"label": "2024 Q3", "sublabel": "100社導入達成"},
]
sb.add_timeline_h(sid, 1.0, 2.5, 8.0, events)
```

---

## 3. タイムライン（垂直）

縦長レイアウト（A4 縦等）向け。上から下にイベントを並べる。

```
    ● ── Event A
    │    詳細テキスト
    │
    ● ── Event B
    │    詳細テキスト
    │
    ● ── Event C
```

```python
def add_timeline_v(self, slide_id, x, y, h, events,
                   line_color=None, marker_color=None):
    """垂直タイムラインを描画する。

    events: list of {"label": str, "sublabel": str (optional)}
    """
    lc = line_color or C.border
    mc = marker_color or C.primary
    n = len(events)
    spacing = h / (n - 1) if n > 1 else 0
    # 垂直線
    self.add_connector(slide_id, x, y, x, y + h, color=lc, weight=2.0)
    # イベントマーカーとラベル
    for i, evt in enumerate(events):
        ey = y + spacing * i
        self.add_circle(slide_id, x, ey, 0.10, fill=mc)
        self.add_text(slide_id, evt["label"],
                      x + 0.25, ey - 0.12, 3.0, 0.25,
                      font_size=12, bold=True, color=C.textTitle)
        if evt.get("sublabel"):
            self.add_text(slide_id, evt["sublabel"],
                          x + 0.25, ey + 0.12, 3.0, 0.20,
                          font_size=10, color=C.textSecondary)
```

---

## 4. シンプル棒グラフ

矩形の高さ/幅をデータ値に比例させたバーチャートを描画する。

```
    100 ┃ ██
        ┃ ██    ██
     50 ┃ ██ ██ ██
        ┃ ██ ██ ██ ██
      0 ┗━━━━━━━━━━━━
         A   B   C   D
```

```python
def add_bar_chart(self, slide_id, x, y, w, h, data,
                  bar_color=None, label_color=None, orientation="vertical"):
    """シンプル棒グラフを描画する。

    data: list of {"label": str, "value": number}
    orientation: "vertical"（縦棒）or "horizontal"（横棒）
    """
    bc = bar_color or C.primary
    lc = label_color or C.textPrimary
    n = len(data)
    max_val = max(d["value"] for d in data) or 1

    if orientation == "vertical":
        bar_w = (w * 0.7) / n
        gap = (w * 0.3) / (n + 1)
        for i, d in enumerate(data):
            bx = x + gap + i * (bar_w + gap)
            bar_h = (d["value"] / max_val) * (h * 0.8)
            by = y + h * 0.8 - bar_h
            # バー
            self.add_rounded_rect(slide_id, bx, by, bar_w, bar_h, fill=bc)
            # 値ラベル（バー上方 0.30" オフセットで重なり防止）
            self.add_text(slide_id, str(d["value"]),
                          bx, by - 0.30, bar_w, 0.25,
                          font_size=10, bold=True, color=bc,
                          alignment="CENTER")
            # カテゴリラベル
            self.add_text(slide_id, d["label"],
                          bx, y + h * 0.82, bar_w, 0.20,
                          font_size=10, color=lc,
                          alignment="CENTER")
    else:  # horizontal
        bar_h = (h * 0.7) / n
        gap = (h * 0.3) / (n + 1)
        for i, d in enumerate(data):
            by = y + gap + i * (bar_h + gap)
            bar_w_actual = (d["value"] / max_val) * (w * 0.65)
            # ラベル
            self.add_text(slide_id, d["label"],
                          x, by, w * 0.25, bar_h,
                          font_size=10, color=lc,
                          alignment="END", valign="MIDDLE")
            # バー
            self.add_rounded_rect(slide_id, x + w * 0.28, by,
                                  bar_w_actual, bar_h, fill=bc)
            # 値（カンマ区切りフォーマット、幅 0.9" 以上で折り返し防止）
            val_str = f"{d['value']:,}" if isinstance(d["value"], (int, float)) else str(d["value"])
            self.add_text(slide_id, val_str,
                          x + w * 0.28 + bar_w_actual + 0.05, by,
                          0.9, bar_h,
                          font_size=10, bold=True, color=bc,
                          valign="MIDDLE")
```

### 使用例

```python
data = [
    {"label": "Q1", "value": 45},
    {"label": "Q2", "value": 72},
    {"label": "Q3", "value": 98},
    {"label": "Q4", "value": 63},
]
sb.add_bar_chart(sid, 1.0, 1.5, 4.0, 3.0, data)
```

---

## 5. ドーナツチャート近似

同心円とセグメント表示でドーナツチャートを近似する。

```
      ┌──────┐
     ╱  30%   ╲
    │    ┌─┐    │
    │    │ │    │  70%
    │    └─┘    │
     ╲         ╱
      └──────┘
```

> **注意**: Google Slides API には円弧（arc）プリミティブがないため、
> 完全なドーナツチャートは不可能。代わりにラベル付き同心円で近似する。

```python
def add_donut(self, slide_id, cx, cy, r, segments,
              center_label=None, center_color=None):
    """ドーナツチャート（同心リング近似）を描画する。

    segments: list of {"label": str, "value": number, "color": RGB dict}
    各セグメントを同心リングで表現し、リング幅は値に比例する。
    最大セグメントが最外リング。中央に合計値やタイトルを表示。
    """
    bg = C.background if hasattr(C, 'background') else {"red": 1, "green": 1, "blue": 1}
    # セグメントを値の大きい順にソート（外側 = 大きいセグメント）
    sorted_segs = sorted(segments, key=lambda s: s["value"], reverse=True)
    total = sum(s["value"] for s in sorted_segs)
    # リング領域: 外周 r から内周 r*0.50 まで
    inner_ratio = 0.50
    ring_space = r * (1 - inner_ratio)
    # 同心円を大→小の順に描画（重ね塗りでリング形成）
    current_r = r
    for seg in sorted_segs:
        self.add_circle(slide_id, cx, cy, current_r, fill=seg["color"])
        ring_width = ring_space * (seg["value"] / total) if total else 0
        current_r -= ring_width
    # 中央の白円（ドーナツの穴）
    inner_r = r * inner_ratio
    self.add_circle(slide_id, cx, cy, inner_r, fill=bg)
    # 中央ラベル
    if center_label:
        self.add_text(slide_id, center_label,
                      cx - inner_r, cy - inner_r * 0.4,
                      inner_r * 2, inner_r * 0.8,
                      font_size=max(int(r * 16), 10), bold=True,
                      color=center_color or C.textTitle,
                      alignment="CENTER", valign="MIDDLE")
    # 凡例（右側に縦に並べる）
    legend_x = cx + r + 0.3
    for i, seg in enumerate(segments):  # 元の順序で表示
        ly = cy - r + i * 0.35
        # 色マーカー
        self.add_rect(slide_id, legend_x, ly + 0.04, 0.18, 0.18,
                      fill=seg["color"])
        # ラベルと値
        pct = int(seg["value"] / total * 100) if total else 0
        self.add_text(slide_id, f'{seg["label"]} ({pct}%)',
                      legend_x + 0.25, ly, 1.5, 0.25,
                      font_size=10, color=C.textPrimary)
```

---

## 6. ピラミッド

上から下に幅が広がる台形の積み重ね。階層構造やファネルを表現する。

```
          ┌──┐
         ╱    ╲
        ╱      ╲
       ┌────────┐
      ╱          ╲
     ╱            ╲
    ┌──────────────┐
```

> Google Slides API に台形を自動配置する機能はないため、`TRAPEZOID` シェイプを
> 段ごとにサイズ調整して積み重ねる。

```python
def add_pyramid(self, slide_id, x, y, w, h, levels, colors=None):
    """ピラミッドを描画する。

    levels: list of str（上から順にラベル）。
    colors: list of RGB dict（levels と同数）。None の場合は C.primary を基準に
            上段（暗: primary×0.4）→下段（明: primary×1.0）のグラデーションを自動生成する。
            白テキストとのコントラスト比 4.5:1 以上を保証。
    """
    n = len(levels)
    level_h = h / n
    # 色が未指定の場合、primary を暗→原色にスケーリング（白テキスト対応）
    if not colors:
        base = C.primary
        colors = []
        for i in range(n):
            t = i / max(n - 1, 1)  # 0.0（最上段=暗）→ 1.0（最下段=原色）
            factor = 0.4 + 0.6 * t  # 0.4（暗い）→ 1.0（primary 原色）
            colors.append({
                "red":   base["red"]   * factor,
                "green": base["green"] * factor,
                "blue":  base["blue"]  * factor,
            })
    for i, label in enumerate(levels):
        # 上段ほど狭く、下段ほど広い
        ratio_top = (i + 0.3) / (n + 0.3)
        ratio_bottom = (i + 1.3) / (n + 0.3)
        lw = w * (ratio_top + ratio_bottom) / 2
        lx = x + (w - lw) / 2
        ly = y + i * level_h
        fill = colors[i]
        self.add_shape(slide_id, "TRAPEZOID", lx, ly, lw, level_h * 0.92,
                       fill=fill)
        # ラベル
        self.add_text(slide_id, label,
                      lx, ly, lw, level_h * 0.92,
                      font_size=12, bold=True,
                      color={"red": 1, "green": 1, "blue": 1},
                      alignment="CENTER", valign="MIDDLE")
```

### 使用例

```python
levels = ["戦略", "設計", "実装", "運用"]
colors = [
    hex_to_rgb("#1B2A4A"),
    hex_to_rgb("#2D4A7A"),
    hex_to_rgb("#4A7AB5"),
    hex_to_rgb("#7AAAE0"),
]
sb.add_pyramid(sid, 2.5, 0.8, 5.0, 4.0, levels, colors)
```

---

## 7. アイコン + テキスト行

円アイコン（文字/数字入り）+ タイトル + 説明を横に並べるパターン。

```
    ◉ タイトル A        ◉ タイトル B        ◉ タイトル C
      説明テキスト        説明テキスト        説明テキスト
```

```python
def add_icon_text_row(self, slide_id, x, y, items, icon_r=0.2):
    """アイコン+テキスト行を横に並べる。

    items: list of {"icon": str, "title": str, "desc": str, "color": RGB dict}
    icon: 円内に表示する1〜2文字（数字やイニシャル）。
    """
    n = len(items)
    item_w = (10.0 - 2 * x) / n if n > 0 else 3.0
    for i, item in enumerate(items):
        ix = x + i * item_w
        ic = item.get("color", C.primary)
        # 円アイコン
        self.add_badge(slide_id, ix + icon_r, y + icon_r,
                       icon_r, item["icon"], fill=ic,
                       text_color={"red": 1, "green": 1, "blue": 1})
        # タイトル
        self.add_text(slide_id, item["title"],
                      ix + icon_r * 2 + 0.15, y, item_w - icon_r * 2 - 0.2, 0.30,
                      font_size=12, bold=True, color=C.textTitle, valign="MIDDLE")
        # 説明
        self.add_text(slide_id, item["desc"],
                      ix, y + icon_r * 2 + 0.15, item_w - 0.1, 0.60,
                      font_size=10, color=C.textSecondary)
```

### 使用例

```python
items = [
    {"icon": "1", "title": "高可用性", "desc": "99.99% SLA を保証", "color": C.primary},
    {"icon": "2", "title": "低レイテンシ", "desc": "P99 < 5ms の応答", "color": C.accent},
    {"icon": "3", "title": "線形拡張", "desc": "ノード追加で性能向上", "color": C.success},
]
sb.add_icon_text_row(sid, 0.5, 2.0, items)
```

---

## 8. 統計カード

大きな数値 + ラベル + 色付きアクセントの統計カード。

```
    ┌─────────────┐
    │  ●           │
    │   99.9%      │
    │   可用性      │
    └─────────────┘
```

```python
def add_stat_card(self, slide_id, x, y, w, h, value, label,
                  icon_color=None, bg=None, border=None):
    """統計カードを描画する。

    value: 大きく表示する数値/テキスト（例: "99.9%", "3x", "<5ms"）。
    label: 値の説明ラベル。
    アクセントバー（上部カラーバー）は不使用。ボーダー色で差別化する。
    """
    card_bg = bg or C.background
    # カード背景（ボーダーのみ。アクセントバーは使わない）
    self.add_rounded_rect(slide_id, x, y, w, h,
                          fill=card_bg,
                          border_color=border or C.border)
    # 値（大きなフォント）
    self.add_text(slide_id, value,
                  x + 0.1, y + h * 0.20, w - 0.2, h * 0.45,
                  font_size=28, bold=True, color=C.textTitle,
                  alignment="CENTER", valign="MIDDLE")
    # ラベル
    self.add_text(slide_id, label,
                  x + 0.1, y + h * 0.65, w - 0.2, h * 0.25,
                  font_size=10, color=C.textSecondary,
                  alignment="CENTER", valign="TOP")
```

### 使用例（3枚並べ）

```python
sid = sb.add_slide()
sb.set_bg(sid, C.background)
stats = [
    ("99.9%", "可用性 SLA", C.primary),
    ("< 5ms", "P99 レイテンシ", C.accent),
    ("3x", "スループット向上", C.success),
]
card_w = 2.5
gap = 0.4
start_x = (10.0 - (card_w * 3 + gap * 2)) / 2
for i, (val, lbl, clr) in enumerate(stats):
    sb.add_stat_card(sid, start_x + i * (card_w + gap), 1.5,
                     card_w, 2.0, val, lbl, icon_color=clr)
```

---

## 9. 比較表（2列）

左右に色分けされたカードで2つの選択肢を比較する。

```
    ┌───────────┐    ┌───────────┐
    │  Option A  │    │  Option B  │
    │            │    │            │
    │  ・利点1    │    │  ・利点1    │
    │  ・利点2    │    │  ・利点2    │
    │  ・利点3    │    │  ・利点3    │
    └───────────┘    └───────────┘
```

```python
def add_comparison(self, slide_id, x, y, w, h, left, right):
    """2列比較レイアウトを描画する。

    left / right: {"title": str, "color": RGB, "items": list of str}
    """
    gap = 0.3
    col_w = (w - gap) / 2

    for i, side in enumerate([left, right]):
        cx = x + i * (col_w + gap)
        # カード背景
        self.add_rounded_rect(slide_id, cx, y, col_w, h,
                              fill=C.background, border_color=side["color"])
        # ヘッダーバー
        self.add_rect(slide_id, cx, y, col_w, 0.05, fill=side["color"])
        # タイトル
        self.add_text(slide_id, side["title"],
                      cx + 0.15, y + 0.15, col_w - 0.3, 0.35,
                      font_size=15, bold=True, color=side["color"],
                      alignment="CENTER")
        # 箇条書き
        if side.get("items"):
            self.add_bullets(slide_id, side["items"],
                             cx + 0.2, y + 0.60, col_w - 0.4, h - 0.75,
                             font_size=12, color=C.textPrimary)
```

### 使用例

```python
left = {
    "title": "ScalarDB",
    "color": C.primary,
    "items": ["ACID トランザクション", "マルチDB対応", "SQLインターフェース"],
}
right = {
    "title": "従来方式",
    "color": C.textMuted,
    "items": ["結果整合性のみ", "DB ごとに個別実装", "独自 API 必須"],
}
sb.add_comparison(sid, 0.5, 1.2, 9.0, 3.5, left, right)
```

---

## 10. フローダイアグラム

矩形/角丸 + 矢印コネクタでプロセスフローを表現する。

```
    ┌──────┐     ┌──────┐     ┌──────┐
    │ Step1 │ ──→ │ Step2 │ ──→ │ Step3 │
    └──────┘     └──────┘     └──────┘
```

```python
def add_flow_diagram(self, slide_id, x, y, steps,
                     box_w=1.8, box_h=0.6, gap=0.5,
                     orientation="horizontal"):
    """フローダイアグラムを描画する。

    steps: list of {"label": str, "shape": "rect"|"rounded"|"diamond" (default "rounded"),
                     "color": RGB dict (optional)}
    orientation: "horizontal" or "vertical"
    """
    shape_map = {
        "rect": "RECTANGLE",
        "rounded": "ROUND_RECTANGLE",
        "diamond": "DIAMOND",
    }
    positions = []
    for i, step in enumerate(steps):
        if orientation == "horizontal":
            sx = x + i * (box_w + gap)
            sy = y
        else:
            sx = x
            sy = y + i * (box_h + gap)
        shape_type = shape_map.get(step.get("shape", "rounded"), "ROUND_RECTANGLE")
        fill = step.get("color", C.primary)
        self.add_shape(slide_id, shape_type, sx, sy, box_w, box_h, fill=fill)
        self.add_text(slide_id, step["label"],
                      sx, sy, box_w, box_h,
                      font_size=12, bold=True,
                      color={"red": 1, "green": 1, "blue": 1},
                      alignment="CENTER", valign="MIDDLE")
        positions.append((sx, sy))

    # 矢印コネクタ
    for i in range(len(positions) - 1):
        sx1, sy1 = positions[i]
        sx2, sy2 = positions[i + 1]
        if orientation == "horizontal":
            self.add_connector(slide_id,
                               sx1 + box_w, sy1 + box_h / 2,
                               sx2, sy2 + box_h / 2,
                               color=C.textMuted, weight=1.5,
                               end_arrow="FILL_ARROW")
        else:
            self.add_connector(slide_id,
                               sx1 + box_w / 2, sy1 + box_h,
                               sx2 + box_w / 2, sy2,
                               color=C.textMuted, weight=1.5,
                               end_arrow="FILL_ARROW")
```

### 使用例

```python
steps = [
    {"label": "データ取得", "shape": "rounded", "color": hex_to_rgb("#4A7AB5")},
    {"label": "変換処理", "shape": "rect", "color": hex_to_rgb("#2D4A7A")},
    {"label": "検証", "shape": "diamond", "color": hex_to_rgb("#E8963A")},
    {"label": "保存", "shape": "rounded", "color": hex_to_rgb("#1B2A4A")},
]
sb.add_flow_diagram(sid, 0.8, 2.0, steps, box_w=1.8, box_h=0.7, gap=0.5)
```

---

## 11. 分岐フローダイアグラム

条件分岐（Yes/No）を含むフローチャート。プロセス・判定・開始/終了ノードを自由配置し、エッジで接続する。
ノード座標はユーザーが明示指定する（自動レイアウトは行わない）。

```
    ┌───────┐
    │ Start │
    └───┬───┘
        ▼
    ◇ 条件A ◇
   Yes╱     ╲No
     ▼       ▼
  ┌──────┐ ┌──────┐
  │処理 B │ │処理 C │
  └──┬───┘ └──┬───┘
     └────┬────┘
          ▼
    ┌───────┐
    │  End  │
    └───────┘
```

```python
def add_decision_flow(self, slide_id, nodes, edges,
                      box_w=1.6, box_h=0.5, diamond_size=0.45):
    """分岐フローダイアグラムを描画する（シェイプ接続コネクタ使用）。

    nodes: list of {"id": int, "label": str, "type": "process"|"decision"|"start"|"end",
                     "x": float, "y": float, "color": RGB dict (optional)}
    edges: list of {"from": int, "to": int, "label": str (optional, e.g. "Yes"/"No")}

    ノードタイプと対応シェイプ:
      process  → ROUND_RECTANGLE (box_w x box_h)
      decision → DIAMOND (diamond_size*2 x diamond_size*2)
      start/end → FLOW_CHART_TERMINATOR (box_w x box_h)

    connectionSiteIndex: 0=top, 1=left, 2=bottom, 3=right
    """
    CONN_TOP, CONN_LEFT, CONN_BOTTOM, CONN_RIGHT = 0, 1, 2, 3
    shape_map = {
        "process":  "ROUND_RECTANGLE",
        "decision": "DIAMOND",
        "start":    "FLOW_CHART_TERMINATOR",
        "end":      "FLOW_CHART_TERMINATOR",
    }
    # ノード描画 — shape_id を記録
    shape_ids = {}
    centers = {}
    for node in nodes:
        ntype = node.get("type", "process")
        shape = shape_map.get(ntype, "ROUND_RECTANGLE")
        fill = node.get("color", C.primary)
        if ntype == "decision":
            nw, nh = diamond_size * 2, diamond_size * 2
        else:
            nw, nh = box_w, box_h
        nx, ny = node["x"], node["y"]
        sid = self.add_shape(slide_id, shape, nx, ny, nw, nh, fill=fill)
        shape_ids[node["id"]] = sid
        # ラベル
        fs = 10 if ntype == "decision" else 12
        self.add_text(slide_id, node["label"],
                      nx, ny, nw, nh,
                      font_size=fs, bold=True,
                      color={"red": 1, "green": 1, "blue": 1},
                      alignment="CENTER", valign="MIDDLE")
        centers[node["id"]] = (nx + nw / 2, ny + nh / 2)

    # エッジ描画（シェイプ接続コネクタ）
    for edge in edges:
        fc = centers[edge["from"]]
        tc = centers[edge["to"]]
        dx = tc[0] - fc[0]
        dy = tc[1] - fc[1]
        # 接続方向を自動判定 → connectionSiteIndex
        if abs(dx) > abs(dy):
            if dx > 0:  # 右方向
                start_site, end_site = CONN_RIGHT, CONN_LEFT
            else:       # 左方向
                start_site, end_site = CONN_LEFT, CONN_RIGHT
        else:
            if dy > 0:  # 下方向
                start_site, end_site = CONN_BOTTOM, CONN_TOP
            else:       # 上方向
                start_site, end_site = CONN_TOP, CONN_BOTTOM
        self.add_connected_connector(
            slide_id,
            shape_ids[edge["from"]], start_site,
            shape_ids[edge["to"]], end_site,
            color=C.textMuted, weight=1.5,
            end_arrow="FILL_ARROW")
        # エッジラベル（中点に表示）
        if edge.get("label"):
            mx = (fc[0] + tc[0]) / 2
            my = (fc[1] + tc[1]) / 2
            lw = 0.7  # 幅 0.5 では英単語が折り返される
            # 水平エッジはラベルを少し上にオフセット
            offset_y = -0.2 if abs(dx) > abs(dy) else 0
            offset_x = 0.15 if abs(dy) >= abs(dx) else 0
            self.add_text(slide_id, edge["label"],
                          mx - lw / 2 + offset_x, my - 0.12 + offset_y,
                          lw, 0.25,
                          font_size=9, bold=True, color=C.textSecondary,
                          alignment="CENTER", valign="MIDDLE")
```

### 使用例

```python
nodes = [
    {"id": 0, "label": "開始",     "type": "start",    "x": 2.5, "y": 0.5},
    {"id": 1, "label": "データ検証", "type": "decision", "x": 2.3, "y": 1.5,
     "color": C.warning},
    {"id": 2, "label": "処理実行",  "type": "process",  "x": 0.5, "y": 3.0},
    {"id": 3, "label": "エラー処理", "type": "process",  "x": 4.5, "y": 3.0,
     "color": C.error},
    {"id": 4, "label": "完了",     "type": "end",      "x": 2.5, "y": 4.5},
]
edges = [
    {"from": 0, "to": 1},
    {"from": 1, "to": 2, "label": "Yes"},
    {"from": 1, "to": 3, "label": "No"},
    {"from": 2, "to": 4},
    {"from": 3, "to": 4},
]
sb.add_decision_flow(sid, nodes, edges)
```

---

## 12. ベン図

2〜3 つの集合の重なりを半透明の円で可視化する。各円にラベルを配置し、
中央の重複領域にオプションの共通ラベルを表示する。

```
      ┌─────────┐
    ╱   A   ╲╱   B   ╲
    │         ╳         │
    ╲       ╱╲       ╱
      └─────────┘
           A∩B
```

```python
def add_venn(self, slide_id, cx, cy, r, sets,
             overlap_label=None, opacity=0.4):
    """ベン図を描画する。

    cx, cy: 全体の中心座標。r: 各円の半径。
    sets: list of {"label": str, "color": RGB dict} (2〜3個)
    overlap_label: 重複領域に表示するテキスト（オプション）。
    opacity: 円の透明度（0.0〜1.0）。デフォルト 0.4。

    2円: 左右に r*0.6 オフセット。
    3円: 120度間隔で r*0.55 オフセット（正三角形配置）。
    """
    import math
    n = len(sets)
    positions = []
    if n == 2:
        offset = r * 0.6
        positions = [(cx - offset, cy), (cx + offset, cy)]
    elif n == 3:
        offset = r * 0.55
        for i in range(3):
            angle = math.radians(90 + 120 * i)  # 上から時計回り
            px = cx + offset * math.cos(angle)
            py = cy - offset * math.sin(angle)
            positions.append((px, py))
    else:
        raise ValueError("sets must contain 2 or 3 items")

    # 円を描画（半透明）
    for i, s in enumerate(sets):
        px, py = positions[i]
        circle_id = self.add_circle(slide_id, px, py, r, fill=s["color"])
        self.shape_opacity(circle_id, opacity)

    # ラベル（各円の外側方向に配置）
    for i, s in enumerate(sets):
        px, py = positions[i]
        dx = px - cx
        dy = py - cy
        dist = math.sqrt(dx * dx + dy * dy) if (dx or dy) else 1
        label_offset = r * 0.75
        lx = px + (dx / dist) * label_offset if dist > 0.01 else px
        ly = py + (dy / dist) * label_offset if dist > 0.01 else py - r
        self.add_text(slide_id, s["label"],
                      lx - 0.8, ly - 0.15, 1.6, 0.30,
                      font_size=12, bold=True, color=s["color"],
                      alignment="CENTER", valign="MIDDLE")

    # 重複ラベル（全体中心）
    if overlap_label:
        self.add_text(slide_id, overlap_label,
                      cx - 0.8, cy - 0.15, 1.6, 0.30,
                      font_size=11, bold=True, color=C.textTitle,
                      alignment="CENTER", valign="MIDDLE")
```

### 使用例（2円）

```python
sets = [
    {"label": "ScalarDB",  "color": C.primary},
    {"label": "ScalarDL",  "color": C.accent},
]
sb.add_venn(sid, 5.0, 3.0, 1.5, sets, overlap_label="統合管理")
```

### 使用例（3円）

```python
sets = [
    {"label": "可用性",   "color": hex_to_rgb("#4A7AB5")},
    {"label": "一貫性",   "color": hex_to_rgb("#E8963A")},
    {"label": "分断耐性", "color": hex_to_rgb("#5AA05A")},
]
sb.add_venn(sid, 5.0, 3.0, 1.3, sets, overlap_label="CAP 定理")
```

---

## パターン選択ガイド

| データの性質 | 推奨パターン |
|-------------|-------------|
| 進捗・達成率 | プログレスバー（1.） |
| 時系列イベント（横型） | タイムライン水平（2.） |
| 時系列イベント（縦長） | タイムライン垂直（3.） |
| 数値比較（カテゴリ別） | シンプル棒グラフ（4.） |
| 構成比・割合 | ドーナツチャート（5.） |
| 階層・ファネル | ピラミッド（6.） |
| 機能紹介（3-4個） | アイコン+テキスト行（7.） |
| KPI・数値ハイライト | 統計カード（8.） |
| 二者比較 | 比較表（9.） |
| プロセスフロー | フローダイアグラム（10.） |
| 条件分岐フロー | 分岐フローダイアグラム（11.） |
| 集合の重なり・共通領域 | ベン図（12.） |

### 組み合わせ例

インフォグラフィクス1ページに複数パターンを配置する例:

```python
# A4 縦のインフォグラフィクス
pres = create_presentation(slides_service, "年次レポート", page_size="A4")
sid = sb.add_slide()
sb.set_bg(sid, C.background)

# 上部: タイトル
sb.add_text(sid, "2025年度 成果レポート", 0.5, 0.3, 7.27, 0.5,
            font_size=24, bold=True, color=C.textTitle)

# KPI カード（3列）
for i, (val, lbl, clr) in enumerate([
    ("150%", "売上達成率", C.primary),
    ("98.5%", "顧客満足度", C.accent),
    ("42件", "新規契約", C.success),
]):
    sb.add_stat_card(sid, 0.5 + i * 2.5, 1.2, 2.2, 1.5, val, lbl, icon_color=clr)

# 中部: 棒グラフ
sb.add_bar_chart(sid, 0.5, 3.2, 7.27, 2.5,
                 [{"label": "Q1", "value": 120}, {"label": "Q2", "value": 180},
                  {"label": "Q3", "value": 210}, {"label": "Q4", "value": 250}])

# 下部: タイムライン
sb.add_timeline_h(sid, 0.5, 6.5, 7.27,
                  [{"label": "4月", "sublabel": "新体制"},
                   {"label": "7月", "sublabel": "新製品"},
                   {"label": "10月", "sublabel": "海外展開"},
                   {"label": "1月", "sublabel": "IPO 準備"}])

# フロー（最下部）
sb.add_flow_diagram(sid, 0.5, 8.0,
                    [{"label": "計画"}, {"label": "実行"},
                     {"label": "評価"}, {"label": "改善"}],
                    box_w=1.5, box_h=0.5, gap=0.35)
```

---

## デザインガイドライン（パターン共通）

レビューの反復テストで確認された、インフォグラフィクスパターン生成時の必須ガイドライン。

### フォントサイズ最小基準

| パターン要素 | 最小 | 推奨 |
|-------------|------|------|
| チャートラベル（棒グラフ軸/値） | 10pt | 12pt |
| 凡例テキスト（ドーナツ等） | 10pt | 11pt |
| タイムラインラベル | 12pt | 12-14pt |
| タイムラインサブラベル | 10pt | 10-11pt |
| フローダイアグラムテキスト | 12pt | 12-14pt |
| ピラミッドラベル | 12pt | 14pt |
| 統計カードラベル | 10pt | 11pt |
| プログレスバーラベル | 10pt | 11pt |
| アイコン行タイトル | 12pt | 12-14pt |
| アイコン行説明文 | 10pt | 10-11pt |
| 比較カード箇条書き | 12pt | 12pt |
| 比較カードタイトル | 15pt | 15-16pt |
| 分岐フローテキスト | 10pt | 12pt |
| 分岐フローエッジラベル | 9pt | 9-10pt |
| ベン図ラベル | 12pt | 12-14pt |
| ベン図重複ラベル | 11pt | 11-12pt |

> **原則**: 8pt 以下のテキストは禁止。最低 9pt、可能な限り 10pt 以上。

### テキスト折り返し防止

| レイアウト | 列幅目安 | 10pt 最大文字数 |
|-----------|---------|---------------|
| 4列均等（16:9） | ~2.3" | 15文字 |
| 3列均等（16:9） | ~3.0" | 20文字 |
| 2列比較（幅5.5"） | ~2.3" | 13文字（箇条書き） |

- 日本語+英数混植は実測幅が大きいため、半角英数を含む場合は1-2文字短く見積もる
- テキストが折り返す場合: (1) 表現を短縮 → (2) フォントサイズ縮小 → (3) 列幅拡大、の順で対応

### カラー運用

- **フローダイアグラム**: 同系色の段階変化（例: `#7AAAE0` → `#4A7AB5` → `#2D4A7A` → `#1B2A4A`）を推奨。ランダム配色は禁止
- **ドーナツチャート凡例**: 各セグメントを色相で区別する（同系色の明度差のみでは不可）
- **アイコン行バッジ**: 統一色（primary）を推奨。4色以上は 60-30-10 ルール違反
- **caution/warning 色のテキスト**: `#BE9000`（ゴールド）は白背景でコントラスト不足。ラベルには `#6B5000` 等のダーク版を使用
- **分岐フロー decision ノード**: `C.warning`（黄/橙）で注意喚起。process ノードと明確に区別する
- **ベン図**: 各円は色相を分離する（例: 青/橙/緑）。同系色は重なり領域で判別不能

### 横棒グラフの値ラベル

- 値テキストボックス幅は **0.9" 以上**。0.5" では "50,000" 等の5桁以上数値が折り返す
- 数値はカンマ区切りフォーマット（`f"{value:,}"`）で表示する
- フォントサイズ 10pt、Bold で値の視認性を確保

### コンテンツ密度（空白回避）

インフォグラフィクスパターンを単独で使用する場合、スライド下半分が空白になりやすい。以下の対策を適用する:

| 対策 | 適用例 |
|------|--------|
| 補足説明テキスト | フローダイアグラムの各ステップ下に説明文を追加 |
| セパレーターライン | アイコン行の下にライン + 説明段落 |
| 複数パターンの組み合わせ | 統計カード（上部）+ 棒グラフ（下部） |
| サブタイトル/出典追加 | 空白領域にデータソースや補足情報 |

> **原則**: スライドのホワイトスペースは 15-55% が適正範囲。55% 超は「コンテンツ不足」と判断し、補足情報を追加する。

### 放射状レイアウト（エコシステム等）

中心に配置するロゴ/ラベルと、その周囲に配置する衛星要素（パートナー、機能等）の配置ルール:

- 中心座標（cy）は `L.bodyY + 2.0"` 以上で設定（タイトル領域との重複を防ぐ）
- 衛星要素の軌道半径（orbit_r）は **1.6" 以下**（スライド端からのはみ出し防止）
- 衛星要素のフォントサイズは **9pt 以上**（10pt 以上推奨）

### 統計カード

- アクセントバー（上部カラーバー）は**不使用**。ボーダー色のみでカード間の差別化を行う
- バッジ（小円）も不要（視覚ノイズ）
- 値の y オフセットは `h * 0.20` で上部に余裕を確保

### 比較カード

- カードの高さは **コンテンツ量 + 余白 0.5"** で算出。過大な高さは空白を生む
- 箇条書き 4 項目の場合: カード高さ **2.0-2.5"** が適正
- タイトルは 15pt 以上で強い視覚的階層を確保

### タイトルスライド

- テキストは **光学的中心**（幾何学的中心よりやや上）に配置
- 16:9 スライド（高さ 5.625"）の場合: タイトル y = **1.8-2.0"** が適正

### 外部画像の活用

Google Slides API の `add_image()` は URL 指定で外部画像を挿入できる。アイコンやロゴを活用してインフォグラフィクスの訴求力を高める。

> **外部依存**: 以下 CDN URL は外部サービスに依存する。**推奨アプローチは `add_badge()` によるテキストアイコン**（外部依存なし）。CDN 画像はオプションとして使用し、`add_image()` 失敗時は必ず `add_badge()` にフォールバックすること。

#### アイコン画像ソース

| ソース | ライセンス | URL パターン | 備考 |
|--------|-----------|-------------|------|
| Google Material Icons | Apache 2.0 | `https://fonts.gstatic.com/s/i/short-term/release/materialsymbolsoutlined/{name}/default/48px.svg` | **SVG → PNG 変換必要** |
| Simple Icons | CC0 | `https://cdn.simpleicons.org/{name}/{color}` | ブランドロゴ向け |
| Iconify CDN | 個別確認 | `https://api.iconify.design/{set}/{name}.svg` | **SVG → PNG 変換必要** |

> **注意**: Google Slides API は SVG 画像を直接挿入できない。SVG ソースを使用する場合は
> PNG に変換してからアップロードするか、PNG を直接提供するソースを使用すること。

#### パターンとの組み合わせ例

**アイコン行（パターン7）でアイコン画像を使用:**

```python
# 円バッジの代わりに画像アイコンを使用
for i, item in enumerate(items):
    ix = x + i * item_w
    icon_url = item.get("icon_url")
    if icon_url:
        # 画像アイコン（正方形にフィット）
        img_size = icon_r * 2
        sb.add_image(sid, icon_url, ix, y, img_size, img_size)
    else:
        # フォールバック: 従来の円バッジ
        sb.add_badge(sid, ix + icon_r, y + icon_r, icon_r,
                     item["icon"], fill=item.get("color", C.primary),
                     text_color={"red": 1, "green": 1, "blue": 1})
```

**タイムライン（パターン2-3）にイベント画像を追加:**

```python
# 水平タイムラインのイベントに画像を追加配置
for i, evt in enumerate(events):
    ex = x + (w / (n - 1)) * i if n > 1 else x + w / 2
    # 通常のマーカーとラベルを描画後...
    if evt.get("image_url"):
        img_y = y - 1.2 if i % 2 == 0 else y + 0.5
        sb.add_image(sid, evt["image_url"],
                     ex - 0.4, img_y, 0.8, 0.8)
```

**ローカルアセットからの挿入（CDN 不要）:**

`assets/` ディレクトリに配置したローカル画像を使用する場合は、`resolve_asset()` + `upload_asset()` で Drive API 経由で挿入する（`google-slides-api.md` セクション 12.1-12.5 参照）。

```python
# CDN の代わりにローカルアセットを使用
# custom_assets_dir が設定されている場合、カスタムフォルダを優先検索する
path = resolve_asset("scalar", "icons", "database.png",
                     custom_assets_dir=CUSTOM_ASSETS_DIR)
if path:
    file_id, url = upload_asset(drive_service, path)
    sb.add_image(sid, url, x, y, w, h)

# または add_image_from_asset() で一括処理（推奨）
# sb.custom_assets_dir が設定済みなら自動的にカスタムフォルダを検索
sb.add_image_from_asset(sid, "scalar", "product-logos", "scalardb.png",
                        0.5, 0.3, 1.2, 0.6)
```

> **推奨**: CDN URL が利用不可で、かつ `add_badge()` では表現できない画像（ブランドロゴ、製品スクリーンショット等）にローカルアセットを使用する。使用後は `sb.cleanup_uploaded_assets()` で Drive の一時ファイルを削除すること。
