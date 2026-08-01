# マスターレジストリ

8 種類のスライドマスター定義と、各マスターに適用するコンポジットパターン関数の仕様。

スライドタイプ → マスター → レイアウト（theme.json）の対応関係を管理する。

---

## 1. マスター一覧

| マスター | 用途 | 背景 | ヘッダー | フッター | ロゴ | 対応レイアウト |
|---------|------|------|---------|---------|------|--------------|
| **COVER** | 表紙 | primary / グラデ風 | なし | なし | 大（top-right） | `layouts.COVER` |
| **SECTION** | セクション区切り | background + 装飾 | セクションタイトル | なし | 小（top-left） | `layouts.SECTION` |
| **CONTENT** | 一般コンテンツ | background (白) | アクションタイトル | ページ番号・ロゴ・著作権 | 小（footer-left） | `layouts.CONTENT` |
| **QUOTE** | 引用・証言 | surfaceLight | なし | なし | なし | `layouts.BLANK` + 独自構成 |
| **HIGHLIGHT** | 強調・KPI | primary / primaryDark | なし | なし | なし | `layouts.CONTENT_ACCENT` + 独自構成 |
| **SPLIT_SCREEN** | 左右分割 | 左: primary / 右: background | アクションタイトル | ページ番号・ロゴ・著作権 | 小（footer-left） | `layouts.CONTENT` + 独自構成 |
| **CLOSING** | 締め・お問い合わせ | background + 装飾 | なし | なし | 大（center） | `layouts.CLOSING` |
| **BLANK** | 白紙・自由配置 | background | なし | なし | なし | `layouts.BLANK` |

---

## 2. マスターとスライドタイプの対応

### COVER

| スライドタイプ | カテゴリ |
|-------------|---------|
| `title` | basic |

### SECTION

| スライドタイプ | カテゴリ |
|-------------|---------|
| `section_divider` | basic |
| `agenda` | basic |

### CONTENT

最も多くのスライドタイプが使用するメインマスター。

| スライドタイプ | カテゴリ |
|-------------|---------|
| `text_bullets` | content |
| `columns` | content |
| `image_text` | content |
| `chart` | content |
| `table` | content |
| `process_flow` | content |
| `icon_grid` | content |
| `product_overview` | product |
| `architecture` | product |
| `feature_matrix` | product |
| `feature_detail` | product |
| `tech_specs` | product |
| `competitive_compare` | product |
| `roadmap` | product |
| `usecase_overview` | usecase |
| `case_study` | usecase |
| `deployment_steps` | usecase |
| `security_compliance` | enterprise |
| `ecosystem` | enterprise |
| `support_sla` | enterprise |
| `pricing` | enterprise |
| `data_flow` | db-middleware |
| `multi_cloud` | db-middleware |
| `benchmark` | db-middleware |
| `migration_path` | db-middleware |

### QUOTE

| スライドタイプ | カテゴリ |
|-------------|---------|
| `quote` | content |

### HIGHLIGHT

| スライドタイプ | カテゴリ |
|-------------|---------|
| `kpi_highlight` | content |
| `roi_impact` | usecase |
| `summary` | basic |

### SPLIT_SCREEN

| スライドタイプ | カテゴリ |
|-------------|---------|
| `problem_solution` | usecase |
| `before_after` | usecase |

### CLOSING

| スライドタイプ | カテゴリ |
|-------------|---------|
| `closing` | basic |

### BLANK

| スライドタイプ | カテゴリ |
|-------------|---------|
| `appendix` | basic |

---

## 3. コンポジットパターン関数

各マスターの共通要素を適用する関数の仕様。スライドタイプのコンポーザーは、まずマスター関数を呼んで共通要素を配置し、その後にタイプ固有のコンテンツを追加する。

### 3.1 COVER マスター

```python
def apply_master_cover(sb, theme, slide_id):
    """
    COVER マスターの共通要素を適用。

    配置する要素:
    - 背景: primary 色でベタ塗り（全面）
    - 装飾バンド: 下部 3.667" から 1.958" の decorative 要素（theme に定義がある場合）
    - ロゴ: top-right に配置（白抜きロゴ推奨）

    コンテンツ領域:
    - title:    (0.500, 1.292) w=8.906 h=1.208
    - subtitle: (0.543, 2.616) w=8.863 h=0.464
    - body:     (5.891, 3.436) w=3.587 h=1.761
    """
    layout = theme["layouts"]["COVER"]
    colors = theme["colors"]

    # 背景色（primary）
    # sb.add_shape("cover_bg", "RECTANGLE",
    #     x=0, y=0, w=PAGE_W, h=PAGE_H,
    #     fill=colors["primary"])

    # ロゴ（白抜き）
    logo = layout["elements"]["logo"]
    # sb.add_image_from_asset(slide_id, theme["name"], "logos",
    #     "brand-logo-white.png",
    #     logo["x"], logo["y"], logo["w"], logo["h"])

    # 装飾バンド（テーマに定義がある場合）
    if "decorative" in layout:
        band = layout["decorative"]["bottomBand"]
        # sb.add_image_from_asset(slide_id, theme["name"], "logos",
        #     "bottom-band.png",
        #     band["x"], band["y"], band["w"], band["h"])
```

**テキストスタイル**:
- タイトル: `fontFaceTitle`, `coverTitle` pt, `textOnDark`, bold
- サブタイトル: `fontFaceBody`, `subtitle` pt, `textOnDark`, normal
- 日付・発表者: `fontFaceBody`, `bodyLevel3` pt, `textOnDark`, normal

### 3.2 SECTION マスター

```python
def apply_master_section(sb, theme, slide_id, page_num=None):
    """
    SECTION マスターの共通要素を適用。

    配置する要素:
    - 背景: background 色
    - 装飾バンド: 下部（COVER と同じ位置）
    - ロゴ: top-left に小さく配置
    - セパレーター: タイトル下に primary 色の水平線
    - ページ番号: 右下

    コンテンツ領域:
    - title: (1.438, 2.039) w=7.125 h=0.590
    - body:  (1.438, 2.759) w=7.125 h=1.088
    """
    layout = theme["layouts"]["SECTION"]
    colors = theme["colors"]

    # ロゴ（カラー版）
    logo = layout["elements"]["logo"]
    # sb.add_image_from_asset(...)

    # セパレーターライン
    sep = layout["elements"]["separator"]
    # sb.add_shape("sep", "RECTANGLE",
    #     x=sep["x"], y=sep["y"], w=sep["w"], h=0.02,
    #     fill=colors[sep["color"]])

    # ページ番号
    if page_num:
        sn = layout["elements"]["slideNumber"]
        # sb.add_text("sn", str(page_num), sn["x"], sn["y"], sn["w"], sn["h"],
        #     font=theme["fonts"]["fontFaceEn"], size=theme["fontSizes"]["slideNumber"],
        #     color=colors["textMuted"], align="END")
```

**テキストスタイル**:
- セクションタイトル: `fontFaceTitle`, `sectionTitle` pt, `textTitle`, bold
- サブテキスト: `fontFaceBody`, `bodyLevel1` pt, `textPrimary`, normal

### 3.3 CONTENT マスター

```python
def apply_master_content(sb, theme, slide_id, page_num, total_pages=None):
    """
    CONTENT マスターの共通要素を適用。
    最も使用頻度の高いマスター。フッター（ロゴ・著作権・ページ番号）を持つ。

    配置する要素:
    - 背景: background 色（白）
    - フッター: ロゴ (footer-left) + 著作権 (center) + ページ番号 (right)

    コンテンツ領域:
    - title:   (0.323, 0.303) w=9.354 h=0.437 — アクションタイトル
    - body:    contentTop(0.787) ～ contentBottom(5.208) = 4.421" の高さ
    """
    layout = theme["layouts"]["CONTENT"]
    footer = theme["masterFooter"]
    colors = theme["colors"]

    # フッターロゴ
    fl = footer["logo"]
    # sb.add_image_from_asset(slide_id, theme["name"], "logos",
    #     "brand-logo-color.png",
    #     fl["x"], fl["y"], fl["w"], fl["h"])

    # 著作権テキスト
    cr = footer["copyright"]
    # sb.add_text("copyright", cr["text"],
    #     cr["x"], cr["y"], cr["w"], cr["h"],
    #     font=cr["font"], size=cr["fontSize"],
    #     color=colors[cr["color"]], align=cr["alignment"])

    # ページ番号
    sn = footer["slideNumber"]
    page_text = f"{page_num}" if not total_pages else f"{page_num}/{total_pages}"
    # sb.add_text("page_num", page_text,
    #     sn["x"], sn["y"], sn["w"], sn["h"],
    #     font=sn["font"], size=sn["fontSize"],
    #     color=colors[sn["color"]], align=sn["alignment"])
```

**テキストスタイル**:
- アクションタイトル: `fontFaceTitle`, `contentTitle` pt, `textTitle`, bold
- サブタイトル: `fontFaceBody`, `subtitle` pt, `textSecondary`, normal
- 本文: `fontFaceBody`, `bodyLevel1` pt, `textPrimary`, normal, lineSpacing=`bodyJapanese`

**アクションタイトル原則**: コンテンツスライドのタイトルは必ず結論文にする（ラベル型禁止）。

| NG（ラベル型） | OK（アクションタイトル） |
|:-------------:|:--------------------:|
| 「売上推移」 | 「前年比 130% の売上成長を達成」 |
| 「機能一覧」 | 「3つの差別化機能が競合優位性を実現」 |
| 「導入効果」 | 「運用コスト 40% 削減を実現」 |

### 3.4 QUOTE マスター

```python
def apply_master_quote(sb, theme, slide_id):
    """
    QUOTE マスターの共通要素を適用。
    BLANK レイアウトをベースに、引用スタイルの装飾を追加。

    配置する要素:
    - 背景: surfaceLight 色（淡い背景）
    - 引用符マーク: 大きなダブルクォート（装飾用）
    - 左ボーダー: primary 色の縦線（accent bar）

    コンテンツ領域:
    - quote_text: (1.5, 1.5) w=7.0 h=2.0 — 引用テキスト
    - attribution: (1.5, 3.8) w=7.0 h=0.5 — 発言者名・役職
    - company_logo: (1.5, 4.5) w=2.0 h=0.5 — 企業ロゴ（オプション）
    """
    colors = theme["colors"]

    # 背景
    # sb.add_shape("quote_bg", "RECTANGLE",
    #     x=0, y=0, w=PAGE_W, h=PAGE_H,
    #     fill=colors["surfaceLight"])

    # 左アクセントバー
    # sb.add_shape("accent_bar", "RECTANGLE",
    #     x=1.0, y=1.2, w=0.06, h=3.2,
    #     fill=colors["primary"])

    # 引用符装飾（大きなダブルクォート）
    # sb.add_text("quote_mark", "\u201C",
    #     1.0, 0.8, 1.0, 1.0,
    #     font=theme["fonts"]["fontFaceAccent"], size=72,
    #     color=colors["primary"], bold=False, opacity=0.2)
```

**テキストスタイル**:
- 引用テキスト: `fontFaceBody`, 20pt, `textPrimary`, italic, lineSpacing=200
- 発言者名: `fontFaceBody`, 14pt, `textTitle`, bold
- 役職・所属: `fontFaceBody`, 12pt, `textMuted`, normal

### 3.5 HIGHLIGHT マスター

```python
def apply_master_highlight(sb, theme, slide_id):
    """
    HIGHLIGHT マスターの共通要素を適用。
    CONTENT_ACCENT レイアウトをベースに、暗色背景で KPI・数値を強調。

    配置する要素:
    - 背景: primary 色（暗い背景）
    - アクセントバー: 左上に縦線（CONTENT_ACCENT の accentBar）

    コンテンツ領域:
    - 全コンテンツは白系テキスト（textOnDark）で表示
    - KPI 数値: 48-72pt の大きなフォント
    - 補足テキスト: 14-16pt
    """
    layout = theme["layouts"].get("CONTENT_ACCENT", theme["layouts"]["BLANK"])
    colors = theme["colors"]

    # 背景色（primary）
    # sb.add_shape("highlight_bg", "RECTANGLE",
    #     x=0, y=0, w=PAGE_W, h=PAGE_H,
    #     fill=colors["primary"])

    # アクセントバー
    if "accentBar" in layout.get("elements", {}):
        bar = layout["elements"]["accentBar"]
        # sb.add_shape("accent_bar", "RECTANGLE",
        #     x=bar["x"], y=bar["y"], w=bar["w"], h=bar["h"],
        #     fill=colors["accent"])
```

**テキストスタイル**:
- KPI 数値: `fontFaceAccent`, 48-72pt, `textOnDark`, bold
- KPI ラベル: `fontFaceBody`, 14pt, `textOnDark`, normal
- 補足テキスト: `fontFaceBody`, 12pt, `textOnDark`, normal, opacity=0.8

### 3.6 SPLIT_SCREEN マスター

```python
def apply_master_split_screen(sb, theme, slide_id, page_num, total_pages=None):
    """
    SPLIT_SCREEN マスターの共通要素を適用。
    CONTENT レイアウトをベースに、左右分割の背景を追加。

    配置する要素:
    - 左半分: primary 色の背景（0 ～ 5.0"）
    - 右半分: background 色の背景（5.0" ～ 10.0"）
    - フッター: CONTENT マスターと同じ（ロゴ・著作権・ページ番号）

    コンテンツ領域:
    - left_panel:  (0.5, 0.8) w=4.0 — 暗色背景上のコンテンツ（textOnDark）
    - right_panel: (5.5, 0.8) w=4.0 — 明色背景上のコンテンツ（textPrimary）
    """
    colors = theme["colors"]

    # 左パネル背景
    # sb.add_shape("left_bg", "RECTANGLE",
    #     x=0, y=0, w=5.0, h=PAGE_H,
    #     fill=colors["primary"])

    # 右パネル背景（明示的に白を設定）
    # sb.add_shape("right_bg", "RECTANGLE",
    #     x=5.0, y=0, w=5.0, h=PAGE_H,
    #     fill=colors["background"])

    # フッター（CONTENT マスターと共通）
    apply_master_content_footer(sb, theme, slide_id, page_num, total_pages)
```

**テキストスタイル**:
- 左パネルタイトル: `fontFaceTitle`, 24pt, `textOnDark`, bold
- 左パネル本文: `fontFaceBody`, 14pt, `textOnDark`, normal
- 右パネルタイトル: `fontFaceTitle`, 24pt, `textTitle`, bold
- 右パネル本文: `fontFaceBody`, 14pt, `textPrimary`, normal

### 3.7 CLOSING マスター

```python
def apply_master_closing(sb, theme, slide_id):
    """
    CLOSING マスターの共通要素を適用。

    配置する要素:
    - 背景: background 色
    - 装飾バンド: 下部（COVER と同じ位置）
    - ロゴ: 中央に大きく配置

    コンテンツ領域:
    - contact_text: (2.5, 3.5) w=5.0 h=1.0 — 連絡先等（オプション）
    """
    layout = theme["layouts"]["CLOSING"]

    # ロゴ（中央、大）
    logo = layout["elements"]["logo"]
    # sb.add_image_from_asset(slide_id, theme["name"], "logos",
    #     "brand-logo-color.png",
    #     logo["x"], logo["y"], logo["w"], logo["h"])

    # 装飾バンド
    if "decorative" in layout:
        band = layout["decorative"]["bottomBand"]
        # sb.add_image_from_asset(...)
```

**テキストスタイル**:
- お問い合わせテキスト: `fontFaceBody`, 14pt, `textPrimary`, normal, align=CENTER
- URL / メール: `fontFaceEn`, 12pt, `primary`, normal

### 3.8 BLANK マスター

```python
def apply_master_blank(sb, theme, slide_id):
    """
    BLANK マスターの共通要素を適用。
    最小限の要素のみ。自由配置用。

    配置する要素:
    - 背景: background 色（白）
    - （他の要素なし）

    コンテンツ領域:
    - 全面 (0.5, 0.5) ～ (9.5, 5.125) が利用可能
    """
    # BLANK は背景色のみ。追加要素なし。
    pass
```

---

## 4. 共通ヘルパー関数

### 4.1 フッター適用

CONTENT マスターと SPLIT_SCREEN マスターで共有されるフッター要素。

```python
def apply_master_content_footer(sb, theme, slide_id, page_num, total_pages=None):
    """
    共通フッター要素を適用。
    CONTENT マスターと SPLIT_SCREEN マスターで使用。

    要素:
    - ロゴ: footer-left (0.118, 5.197) w=1.181 h=0.342
    - 著作権: center (2.000, 5.378) w=6.083 h=0.219
    - ページ番号: right (9.569, 5.378) w=0.264 h=0.219
    """
    footer = theme["masterFooter"]
    colors = theme["colors"]

    # ロゴ
    fl = footer["logo"]
    # sb.add_image_from_asset(...)

    # 著作権
    cr = footer["copyright"]
    if cr["text"]:
        pass  # sb.add_text(...)

    # ページ番号
    sn = footer["slideNumber"]
    page_text = f"{page_num}" if not total_pages else f"{page_num}/{total_pages}"
    # sb.add_text(...)
```

### 4.2 アクションタイトル適用

CONTENT マスター系のタイトルを適用。

```python
def apply_action_title(sb, theme, slide_id, title_text, subtitle_text=None):
    """
    アクションタイトルとサブタイトルを配置。

    Parameters:
        title_text: アクションタイトル（結論文）。50文字（ja）/ 100文字（en）以内
        subtitle_text: サブタイトル（オプション）
    """
    layout = theme["layouts"]["CONTENT"]
    t = layout["elements"]["title"]

    # タイトル
    # sb.add_text("title", title_text,
    #     t["x"], t["y"], t["w"], t["h"],
    #     font=theme["fonts"]["fontFaceTitle"],
    #     size=theme["fontSizes"]["contentTitle"],
    #     color=theme["colors"]["textTitle"],
    #     bold=True)

    # サブタイトル（オプション）
    if subtitle_text:
        st = layout["elements"]["subtitle"]
        # sb.add_text("subtitle", subtitle_text,
        #     st["x"], st["y"], st["w"], st["h"],
        #     font=theme["fonts"]["fontFaceBody"],
        #     size=theme["fontSizes"]["subtitle"],
        #     color=theme["colors"]["textSecondary"])
```

---

## 5. マスター選択ロジック

コンテンツからマスターを自動判定するためのガイドライン。

### 5.1 判定フロー

```
1. スライドタイプが明示指定されている場合
   → セクション 2 の対応表からマスターを取得

2. デッキパターンが指定されている場合
   → パターンの structure からスライドタイプを取得 → マスター決定

3. コンテンツベースの自動判定:
   a. 1つの大きな数値 + 補足テキスト → HIGHLIGHT
   b. 引用文 + 発言者 → QUOTE
   c. 左右対比の構造 → SPLIT_SCREEN
   d. プレゼンテーション冒頭 → COVER
   e. セクション区切り → SECTION
   f. プレゼンテーション末尾 → CLOSING
   g. その他コンテンツ → CONTENT（デフォルト）
```

### 5.2 マスター選択の優先順位

1. **明示指定**: ユーザーまたはスライドタイプ定義による指定が最優先
2. **デッキパターン**: パターンの構造定義に従う
3. **コンテンツ分析**: 上記 3. の判定フロー
4. **デフォルト**: 判定不能な場合は CONTENT マスターを使用

---

## 6. レイアウト座標リファレンス

### 6.1 ページサイズ

```
幅: 10.000" (9,144,000 EMU)
高: 5.625"  (5,143,500 EMU)
アスペクト比: 16:9
```

### 6.2 共通マージン

```
左マージン: 0.323" (CONTENT) / 0.500" (COVER, 汎用)
右マージン: ~0.323" (CONTENT) / ~0.500" (汎用)
上マージン: 0.303" (CONTENT title top)
フッター Y: 5.208" (CONTENT logo top) / 5.378" (copyright/page number)
```

### 6.3 コンテンツ領域サイズ

| マスター | X開始 | Y開始 | 幅 | 高さ | 備考 |
|---------|------:|------:|---:|-----:|------|
| COVER | 0.500 | 1.292 | 8.906 | 2.144 | title + subtitle |
| SECTION | 1.438 | 2.039 | 7.125 | 1.808 | title + body |
| CONTENT | 0.323 | 0.787 | 9.354 | 4.421 | フル body 領域 |
| QUOTE | 1.500 | 1.500 | 7.000 | 3.000 | quote + attribution |
| HIGHLIGHT | 0.500 | 0.500 | 9.000 | 4.500 | 全面利用 |
| SPLIT_SCREEN | 0.500/5.500 | 0.800 | 4.000/4.000 | 4.000 | 左右パネル |
| CLOSING | 3.307 | 2.323 | 3.385 | 0.979 | ロゴ領域のみ |
| BLANK | 0.500 | 0.500 | 9.000 | 4.625 | 全面利用 |

---

## 7. 装飾要素

### 7.1 底部バンド

COVER, SECTION, CLOSING で使用される装飾画像バンド。

```json
{
  "bottomBand": {
    "x": 0.000,
    "y": 3.667,
    "w": 10.000,
    "h": 1.958,
    "type": "image"
  }
}
```

テーマのアセットに `bottom-band.png` が存在する場合に適用。存在しない場合はスキップ。

### 7.2 アクセントバー

CONTENT_ACCENT / HIGHLIGHT で使用される左上の縦線。

```json
{
  "accentBar": {
    "x": 0.367,
    "y": 0.059,
    "w": 0.054,
    "h": 0.398,
    "fill": "primary"
  }
}
```

### 7.3 セパレーター

SECTION で使用されるタイトル下の水平線。

```json
{
  "separator": {
    "x": 1.438,
    "y": 2.686,
    "w": 8.562,
    "h": 0,
    "color": "primary",
    "weight": 2.25
  }
}
```
