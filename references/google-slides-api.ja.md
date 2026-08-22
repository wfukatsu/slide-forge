*[English](google-slides-api.md)*
# Google Slides API — 生リファレンス

Slides REST API そのもののリクエスト形・単位・上限・癖をまとめる。

**先に `references/api-notes.md` を読むこと。** 実際に踏んだ失敗とその対処は
そちらにある。この文書は、そこに答えが無く、API 自身の挙動を確かめる必要が
あるときに開く — 送ったことのないリクエストボディ、これから当たりそうな上限、
エンジンが露出していない図形やコネクタのプロパティなど。

**デッキの作り方ではない。** slide-forge は API を手書きしない。
`scripts/build_deck.py` が spec をリクエストに変換し、`scripts/diagrams.py` が
描画し、`scripts/deckkit.py` が記述面である。認証は `scripts/_auth.py`。
以下の Python は説明用で、エンジンの実装ではなくリクエスト JSON を示すための
素の関数である。通常書くべきものは
[diagrams.md](diagrams.md) と [template-schema.md](template-schema.md) を参照。

## 1. 座標系

### EMU（English Metric Units）

```python
EMU = 914400  # 1 inch = 914,400 EMU

def inches(val):
    """インチを EMU に変換する。"""
    return int(val * EMU)
```

### Google Slides vs PowerPoint

| | PowerPoint 16:9 | Google Slides 16:9 | 比率 |
|-|-----------------|---------------------|------|
| 幅 | 13.333" (12,192,000 EMU) | **10.000"** (9,144,000 EMU) | 0.75x |
| 高さ | 7.500" (6,858,000 EMU) | **5.625"** (5,143,500 EMU) | 0.75x |

Google Slides は 16:9 を **10" x 5.625"** に正規化する。PowerPoint 座標からの変換には 0.75 を掛ける。

### 比率ベース座標計算（推奨）

```python
def calc_layout(sw, sh):
    """スライドサイズから比率ベースでレイアウト定数を計算する。"""
    return {
        "MX":          sw * 0.0375,    # マージン: 幅の 3.75%
        "CW":          sw * 0.925,     # コンテンツ幅: 幅の 92.5%
        "TITLE_Y":     sh * 0.067,     # タイトルY: 高さの 6.7%
        "TITLE_H":     sh * 0.067,     # タイトル高さ
        "SEP_Y":       sh * 0.147,     # セパレーターY
        "SEP_W":       sw * 0.856,     # セパレーター幅（theme.json SECTION.separator.w 参照）
        "BODY_TOP":    sh * 0.173,     # ボディ開始Y
        "BODY_BOTTOM": sh * 0.913,     # ボディ終了Y
        "FOOTER_Y":    sh * 0.940,     # フッターY
    }
```

---

## 2. ヘルパー関数

### 色変換

```python
def hex_to_rgb(hex_str):
    """HEX カラーコードを Google Slides API の RGB dict に変換する。"""
    h = hex_str.lstrip("#")
    return {
        "red": int(h[0:2], 16) / 255.0,
        "green": int(h[2:4], 16) / 255.0,
        "blue": int(h[4:6], 16) / 255.0,
    }
```

### スタイルビルダー

```python
def solid_fill(color):
    """RGB dict からソリッドフィルプロパティを生成する。"""
    return {"solidFill": {"color": {"rgbColor": color}}}

def text_style(font_size=18, bold=False, color=None, font_family="M PLUS 1p"):
    """テキストスタイル dict を生成する。"""
    style = {
        "fontSize": {"magnitude": font_size, "unit": "PT"},
        "bold": bold,
        "fontFamily": font_family,
    }
    if color:
        style["foregroundColor"] = {"opaqueColor": {"rgbColor": color}}
    return style
```

---

## 3. リクエストビルダー

### シェイプ作成

```python
def create_shape_request(page_id, shape_id, x, y, w, h):
    """矩形シェイプの作成リクエストを生成する。"""
    return {"createShape": {
        "objectId": shape_id,
        "shapeType": "RECTANGLE",
        "elementProperties": {
            "pageObjectId": page_id,
            "size": {
                "width": {"magnitude": inches(w), "unit": "EMU"},
                "height": {"magnitude": inches(h), "unit": "EMU"},
            },
            "transform": {
                "scaleX": 1, "scaleY": 1,
                "translateX": inches(x), "translateY": inches(y),
                "unit": "EMU",
            },
        },
    }}
```

### テキストボックス作成

```python
def create_textbox_request(page_id, box_id, x, y, w, h):
    """テキストボックスの作成リクエストを生成する。shapeType を TEXT_BOX にする。"""
    return {"createShape": {
        "objectId": box_id,
        "shapeType": "TEXT_BOX",
        "elementProperties": {
            "pageObjectId": page_id,
            "size": {
                "width": {"magnitude": inches(w), "unit": "EMU"},
                "height": {"magnitude": inches(h), "unit": "EMU"},
            },
            "transform": {
                "scaleX": 1, "scaleY": 1,
                "translateX": inches(x), "translateY": inches(y),
                "unit": "EMU",
            },
        },
    }}
```

### テキスト挿入・スタイル適用

```python
def insert_text_request(box_id, text):
    """テキストボックスにテキストを挿入する。insertionIndex=0 で先頭に挿入。"""
    return {"insertText": {"objectId": box_id, "text": text, "insertionIndex": 0}}

def update_text_style_request(box_id, style, start=0, end=None, text=""):
    """テキスト範囲にスタイルを適用する。end 未指定時は text の長さを使用。"""
    end_idx = end if end is not None else len(text)
    return {"updateTextStyle": {
        "objectId": box_id,
        "style": style,
        "textRange": {"type": "FIXED_RANGE", "startIndex": start, "endIndex": end_idx},
        "fields": ",".join(style.keys()),
    }}

def update_paragraph_style_request(box_id, alignment="START", start=0, end=None, text=""):
    """段落のアラインメントを設定する。alignment: START/CENTER/END。"""
    end_idx = end if end is not None else len(text)
    return {"updateParagraphStyle": {
        "objectId": box_id,
        "style": {"alignment": alignment},
        "textRange": {"type": "FIXED_RANGE", "startIndex": start, "endIndex": end_idx},
        "fields": "alignment",
    }}
```

### シェイププロパティ更新

```python
def shape_fill_request(shape_id, color):
    """シェイプの背景色を設定する。"""
    return {"updateShapeProperties": {
        "objectId": shape_id,
        "shapeProperties": {"shapeBackgroundFill": solid_fill(color)},
        "fields": "shapeBackgroundFill.solidFill.color",
    }}

def shape_border_request(shape_id, color, weight=1.0):
    """シェイプの枠線を設定する。weight は PT 単位。"""
    return {"updateShapeProperties": {
        "objectId": shape_id,
        "shapeProperties": {"outline": {
            "outlineFill": solid_fill(color),
            "weight": {"magnitude": weight, "unit": "PT"},
        }},
        "fields": "outline",
    }}

def shape_no_border_request(shape_id):
    """シェイプの枠線を非表示にする。weight=0 はエラーになるため propertyState を使う。"""
    return {"updateShapeProperties": {
        "objectId": shape_id,
        "shapeProperties": {"outline": {"propertyState": "NOT_RENDERED"}},
        "fields": "outline",
    }}
```

### ページ背景

```python
def page_bg_request(page_id, color):
    """スライドの背景色を設定する。"""
    return {"updatePageProperties": {
        "objectId": page_id,
        "pageProperties": {"pageBackgroundFill": solid_fill(color)},
        "fields": "pageBackgroundFill.solidFill.color",
    }}
```

---

## 4. バッチ実行

### 500件ずつチャンク分割

Google Slides API の batchUpdate は一度に大量のリクエストを送れるが、安全のため 500 件ずつ分割する。

```python
def execute_batch(slides_service, pres_id, requests, chunk_size=500):
    """リクエストをチャンクに分割して batchUpdate を実行する。"""
    for i in range(0, len(requests), chunk_size):
        chunk = requests[i:i + chunk_size]
        slides_service.presentations().batchUpdate(
            presentationId=pres_id,
            body={"requests": chunk},
        ).execute()
        print(f"  Batch {i // chunk_size + 1}: {len(chunk)} requests sent")
```

### 典型的な main() 構造

```python
def main():
    creds = get_credentials(CREDS_FILE, TOKEN_FILE)
    slides_service = build("slides", "v1", credentials=creds)

    # プレゼンテーション作成（pageSize は作成時のみ指定可能）
    presentation = slides_service.presentations().create(
        body={
            "title": "プレゼンテーションタイトル",
            "pageSize": {
                "width": {"magnitude": inches(10.0), "unit": "EMU"},
                "height": {"magnitude": inches(5.625), "unit": "EMU"},
            },
        }
    ).execute()
    pres_id = presentation["presentationId"]

    # デフォルトの最初のスライドを削除
    first_slide_id = presentation["slides"][0]["objectId"]
    requests.append({"deleteObject": {"objectId": first_slide_id}})

    # ... スライドを構築 ...

    # 一括実行
    execute_batch(slides_service, pres_id, requests)

    url = f"https://docs.google.com/presentation/d/{pres_id}/edit"
    print(f"Done! {len(slide_ids)} slides created.")
    print(f"Open: {url}")
```

---

## 5. Sheets API チャート連携

Google Slides のネイティブチャートは Sheets API と連携が必要。

### linked chart の作成手順

1. Google Sheets でデータとチャートを作成
2. `sheets_service.spreadsheets().get()` でチャート ID を取得
3. `createSheetsChart` リクエストでスライドに埋め込む

```python
def add_linked_chart(slide_id, spreadsheet_id, chart_id, x, y, w, h):
    """Sheets のチャートをスライドに埋め込む。"""
    chart_obj_id = _id("chart")
    requests.append({"createSheetsChart": {
        "objectId": chart_obj_id,
        "spreadsheetId": spreadsheet_id,
        "chartId": chart_id,
        "linkingMode": "LINKED",
        "elementProperties": {
            "pageObjectId": slide_id,
            "size": {
                "width": {"magnitude": inches(w), "unit": "EMU"},
                "height": {"magnitude": inches(h), "unit": "EMU"},
            },
            "transform": {
                "scaleX": 1, "scaleY": 1,
                "translateX": inches(x), "translateY": inches(y),
                "unit": "EMU",
            },
        },
    }})
    return chart_obj_id
```

---

## 6. API 制約・Pitfalls

### 重要な制約

| 制約 | 詳細 |
|------|------|
| pageSize は作成時のみ | `updatePageProperties` では変更不可。`presentations.create` で指定 |
| objectId は5文字以上 | `createSlide`, `createShape` 等の objectId は最低5文字 |
| outline weight > 0 | weight=0 はエラー。非表示には `propertyState: NOT_RENDERED` |
| BLANK レイアウト推奨 | カスタムレイアウトでは BLANK を使い、全要素を自前で配置 |
| 16:9 正規化 | Google Slides は 10" x 5.625" に正規化（PowerPoint の 0.75 倍） |

### レート制限

| 種別 | 上限 |
|------|------|
| 読み取りリクエスト | 300/分/ユーザー |
| 書き込みリクエスト | 60/分/ユーザー |
| batchUpdate | 1回で複数リクエスト可（チャンクサイズ 500 推奨） |

### BLANK vs プレースホルダー

| 方式 | メリット | デメリット |
|------|---------|-----------|
| BLANK + カスタムシェイプ | 完全なレイアウト制御。PPTX と設計共有可能 | テーマ変更の恩恵なし。全座標を自前計算 |
| プレースホルダー | テーマ連動。テーマ変更で自動調整 | 細かいレイアウト制御が困難 |

**推奨:** カスタムレイアウト（36種等）が必要な場合は **BLANK + カスタムシェイプ方式** を採用。

---

## 7. サムネイル取得（視覚的 QA 用）

```python
def export_thumbnails(slides_service, pres_id, output_dir):
    """全スライドの PNG サムネイルをダウンロードする。"""
    import urllib.request
    pres = slides_service.presentations().get(presentationId=pres_id).execute()
    os.makedirs(output_dir, exist_ok=True)
    for i, slide in enumerate(pres["slides"]):
        # ネストされたパラメータはアンダースコア区切りで指定する
        # (ドット区切り {"thumbnailProperties.mimeType": ...} は TypeError になる)
        thumb = slides_service.presentations().pages().getThumbnail(
            presentationId=pres_id,
            pageObjectId=slide["objectId"],
            thumbnailProperties_mimeType="PNG",
            thumbnailProperties_thumbnailSize="LARGE",
        ).execute()
        path = os.path.join(output_dir, f"slide_{i+1}.png")
        urllib.request.urlretrieve(thumb["contentUrl"], path)
    return output_dir
```

### Drive API で共有設定

サムネイル URL はプレゼンテーションが共有されていなくても取得可能だが、外部ツールでの検証には共有設定が必要な場合がある。

```python
def share_presentation(drive_service, pres_id):
    """プレゼンテーションを anyone:reader で共有する。"""
    drive_service.permissions().create(
        fileId=pres_id,
        body={"type": "anyone", "role": "reader"},
    ).execute()
```

---

## 8. 汎用シェイプ作成

### add_shape（任意の shapeType）

```python
def add_shape(slide_id, shape_type, x, y, w, h,
              fill=None, border_color=None, border_weight=1.0):
    """任意の shapeType でシェイプを作成する。"""
    shape_id = _id("shp")
    requests.append({"createShape": {
        "objectId": shape_id,
        "shapeType": shape_type,
        "elementProperties": {
            "pageObjectId": slide_id,
            "size": {
                "width": {"magnitude": inches(w), "unit": "EMU"},
                "height": {"magnitude": inches(h), "unit": "EMU"},
            },
            "transform": {
                "scaleX": 1, "scaleY": 1,
                "translateX": inches(x), "translateY": inches(y),
                "unit": "EMU",
            },
        },
    }})
    if fill:
        requests.append(shape_fill_request(shape_id, fill))
    if border_color:
        requests.append(shape_border_request(shape_id, border_color, border_weight))
    else:
        requests.append(shape_no_border_request(shape_id))
    return shape_id
```

### 便利メソッド

```python
def add_circle(slide_id, cx, cy, r, fill=None, border_color=None):
    """円を追加する。cx, cy は中心座標、r は半径（インチ）。"""
    return add_shape(slide_id, "ELLIPSE",
                          cx - r, cy - r, 2 * r, 2 * r,
                          fill=fill, border_color=border_color)

def add_rounded_rect(slide_id, x, y, w, h,
                     fill=None, border_color=None):
    """角丸矩形を追加する。"""
    return add_shape(slide_id, "ROUND_RECTANGLE", x, y, w, h,
                          fill=fill, border_color=border_color)

def add_arrow(slide_id, x, y, w, h, direction="right", fill=None):
    """矢印シェイプを追加する。direction: right/left/up/down/left_right/up_down/quad。"""
    arrow_types = {
        "right":      "RIGHT_ARROW",
        "left":       "LEFT_ARROW",
        "up":         "UP_ARROW",
        "down":       "DOWN_ARROW",
        "left_right": "LEFT_RIGHT_ARROW",
        "up_down":    "UP_DOWN_ARROW",
        "quad":       "QUAD_ARROW",
    }
    return add_shape(slide_id, arrow_types[direction], x, y, w, h,
                          fill=fill)

def add_diamond(slide_id, cx, cy, size, fill=None, border_color=None):
    """ひし形を追加する。cx, cy は中心座標、size は対角線の半分。"""
    return add_shape(slide_id, "DIAMOND",
                          cx - size, cy - size, 2 * size, 2 * size,
                          fill=fill, border_color=border_color)

def add_speech_bubble(slide_id, x, y, w, h, text, fill=None,
                      style="rect", text_color=None, font_size=10):
    """吹出しシェイプを追加しテキストを挿入する。style: rect/rounded/ellipse/cloud。
    セクション6の add_callout（青バー付きコールアウトボックス）とは別物。
    テキストはシェイプ自体に insertText で挿入する（重複テキストボックスを作らない）。
    """
    callout_types = {
        "rect":    "WEDGE_RECTANGLE_CALLOUT",
        "rounded": "WEDGE_ROUND_RECTANGLE_CALLOUT",
        "ellipse": "WEDGE_ELLIPSE_CALLOUT",
        "cloud":   "CLOUD_CALLOUT",
    }
    shape_id = add_shape(slide_id, callout_types[style], x, y, w, h,
                              fill=fill)
    # シェイプ自体にテキストを挿入（別テキストボックスを重ねない）
    requests.append(insert_text_request(shape_id, text))
    style_dict = text_style(font_size, False, text_color)
    requests.append(update_text_style_request(shape_id, style_dict, 0, len(text), text))
    requests.append(update_paragraph_style_request(shape_id, "CENTER", 0, len(text), text))
    requests.append({"updateShapeProperties": {
        "objectId": shape_id,
        "shapeProperties": {"contentAlignment": "MIDDLE"},
        "fields": "contentAlignment",
    }})
    return shape_id

def add_star(slide_id, cx, cy, r, points=5, fill=None):
    """星形を追加する。points: 4/5/6/7/8/10/12/16/24/32。"""
    star_types = {
        4: "STAR_4", 5: "STAR_5", 6: "STAR_6", 7: "STAR_7",
        8: "STAR_8", 10: "STAR_10", 12: "STAR_12", 16: "STAR_16",
        24: "STAR_24", 32: "STAR_32",
    }
    return add_shape(slide_id, star_types[points],
                          cx - r, cy - r, 2 * r, 2 * r, fill=fill)

def add_polygon(slide_id, cx, cy, r, sides, fill=None, border_color=None):
    """正多角形を追加する。sides: 3(三角)/5(五角)/6(六角)/7/8/10/12。"""
    poly_types = {
        3: "TRIANGLE", 5: "PENTAGON", 6: "HEXAGON", 7: "HEPTAGON",
        8: "OCTAGON", 10: "DECAGON", 12: "DODECAGON",
    }
    return add_shape(slide_id, poly_types[sides],
                          cx - r, cy - r, 2 * r, 2 * r,
                          fill=fill, border_color=border_color)

def add_cylinder(slide_id, x, y, w, h, fill=None, border_color=None):
    """シリンダー（DB アイコン用）を追加する。"""
    return add_shape(slide_id, "CAN", x, y, w, h,
                          fill=fill, border_color=border_color)

def add_chevron(slide_id, x, y, w, h, fill=None):
    """シェブロン（プロセスステップ用）を追加する。"""
    return add_shape(slide_id, "CHEVRON", x, y, w, h, fill=fill)

def add_badge(slide_id, cx, cy, r, text, fill, text_color):
    """円バッジ（円 + 中央テキスト）を追加する。"""
    add_circle(slide_id, cx, cy, r, fill=fill)
    add_text(slide_id, text,
                  cx - r, cy - r, 2 * r, 2 * r,
                  font_size=max(int(r * 28), 10), bold=True,
                  color=text_color, alignment="CENTER", valign="MIDDLE")
```

### シェイプタイプ 完全リファレンス（全141タイプ）

> `add_shape(slide_id, shape_type, x, y, w, h, ...)` の `shape_type` に指定可能な全値。
> `TYPE_UNSPECIFIED` と `CUSTOM` は createShape では使用不可のため除外。

#### 基本図形（33）

| shapeType | 説明 |
|-----------|------|
| `RECTANGLE` | 矩形 |
| `ROUND_RECTANGLE` | 角丸矩形 |
| `ROUND_1_RECTANGLE` | 1角のみ角丸の矩形 |
| `ROUND_2_DIAGONAL_RECTANGLE` | 対角2角の角丸矩形 |
| `ROUND_2_SAME_RECTANGLE` | 同側2角の角丸矩形 |
| `SNIP_1_RECTANGLE` | 1角カットの矩形 |
| `SNIP_2_DIAGONAL_RECTANGLE` | 対角2角カットの矩形 |
| `SNIP_2_SAME_RECTANGLE` | 同側2角カットの矩形 |
| `SNIP_ROUND_RECTANGLE` | 1角カット＋1角丸の矩形 |
| `ELLIPSE` | 楕円 / 円（w=h で真円） |
| `ARC` | 円弧 |
| `CHORD` | 弦（弓形） |
| `PIE` | 扇形（パイ） |
| `BLOCK_ARC` | ブロック円弧 |
| `TRIANGLE` | 三角形 |
| `RIGHT_TRIANGLE` | 直角三角形 |
| `DIAMOND` | ひし形 |
| `PARALLELOGRAM` | 平行四辺形 |
| `TRAPEZOID` | 台形 |
| `PENTAGON` | 五角形 |
| `HEXAGON` | 六角形 |
| `HEPTAGON` | 七角形 |
| `OCTAGON` | 八角形 |
| `DECAGON` | 十角形 |
| `DODECAGON` | 十二角形 |
| `BEVEL` | ベベル（額縁風） |
| `CAN` | シリンダー（缶） |
| `CUBE` | 立方体 |
| `DONUT` | ドーナツ |
| `FRAME` | フレーム |
| `HALF_FRAME` | ハーフフレーム |
| `CORNER` | コーナー |
| `DIAGONAL_STRIPE` | 対角ストライプ |

#### 矢印（21）

| shapeType | 説明 |
|-----------|------|
| `RIGHT_ARROW` | 右矢印 |
| `LEFT_ARROW` | 左矢印 |
| `UP_ARROW` | 上矢印 |
| `DOWN_ARROW` | 下矢印 |
| `LEFT_RIGHT_ARROW` | 左右矢印 |
| `UP_DOWN_ARROW` | 上下矢印 |
| `LEFT_RIGHT_UP_ARROW` | 左右上矢印 |
| `LEFT_UP_ARROW` | 左上矢印 |
| `QUAD_ARROW` | 四方向矢印 |
| `BENT_ARROW` | 屈折矢印 |
| `BENT_UP_ARROW` | 上向き屈折矢印 |
| `CURVED_DOWN_ARROW` | 曲線下矢印 |
| `CURVED_LEFT_ARROW` | 曲線左矢印 |
| `CURVED_RIGHT_ARROW` | 曲線右矢印 |
| `CURVED_UP_ARROW` | 曲線上矢印 |
| `NOTCHED_RIGHT_ARROW` | ノッチ右矢印 |
| `STRIPED_RIGHT_ARROW` | ストライプ右矢印 |
| `UTURN_ARROW` | Uターン矢印 |
| `ARROW_EAST` | 東矢印（細い） |
| `ARROW_NORTH_EAST` | 北東矢印（細い） |
| `ARROW_NORTH` | 北矢印（細い） |

#### 矢印コールアウト（7）

| shapeType | 説明 |
|-----------|------|
| `RIGHT_ARROW_CALLOUT` | 右矢印コールアウト |
| `LEFT_ARROW_CALLOUT` | 左矢印コールアウト |
| `UP_ARROW_CALLOUT` | 上矢印コールアウト |
| `DOWN_ARROW_CALLOUT` | 下矢印コールアウト |
| `LEFT_RIGHT_ARROW_CALLOUT` | 左右矢印コールアウト |
| `QUAD_ARROW_CALLOUT` | 四方向矢印コールアウト |
| `WEDGE_RECTANGLE_CALLOUT` | 矩形吹出し |

#### 吹出し（3）

| shapeType | 説明 |
|-----------|------|
| `WEDGE_ELLIPSE_CALLOUT` | 楕円吹出し |
| `WEDGE_ROUND_RECTANGLE_CALLOUT` | 角丸矩形吹出し |
| `CLOUD_CALLOUT` | 雲形吹出し |

#### ブラケット・ブレース（6）

| shapeType | 説明 |
|-----------|------|
| `LEFT_BRACKET` | 左角括弧 |
| `RIGHT_BRACKET` | 右角括弧 |
| `LEFT_BRACE` | 左波括弧 |
| `RIGHT_BRACE` | 右波括弧 |
| `BRACE_PAIR` | 波括弧ペア |
| `BRACKET_PAIR` | 角括弧ペア |

#### 星・リボン・装飾（18）

| shapeType | 説明 |
|-----------|------|
| `STAR_4` | 4頂点星 |
| `STAR_5` | 5頂点星 |
| `STAR_6` | 6頂点星（ダビデの星） |
| `STAR_7` | 7頂点星 |
| `STAR_8` | 8頂点星 |
| `STAR_10` | 10頂点星 |
| `STAR_12` | 12頂点星 |
| `STAR_16` | 16頂点星 |
| `STAR_24` | 24頂点星 |
| `STAR_32` | 32頂点星 |
| `STARBURST` | スターバースト |
| `RIBBON` | リボン |
| `RIBBON_2` | リボン 2 |
| `ELLIPSE_RIBBON` | 楕円リボン |
| `ELLIPSE_RIBBON_2` | 楕円リボン 2 |
| `HEART` | ハート |
| `SUN` | 太陽 |
| `MOON` | 月 |

#### 装飾・記号（12）

| shapeType | 説明 |
|-----------|------|
| `CLOUD` | 雲 |
| `LIGHTNING_BOLT` | 稲妻 |
| `SMILEY_FACE` | スマイリー |
| `NO_SMOKING` | 禁止マーク |
| `FOLDED_CORNER` | 折り曲げ角 |
| `CHEVRON` | シェブロン |
| `HOME_PLATE` | ホームプレート |
| `PLAQUE` | プレート |
| `TEARDROP` | ティアドロップ |
| `SPEECH` | スピーチ |
| `DOUBLE_WAVE` | 二重波 |
| `WAVE` | 波 |

#### スクロール・シール（4）

| shapeType | 説明 |
|-----------|------|
| `HORIZONTAL_SCROLL` | 水平スクロール |
| `VERTICAL_SCROLL` | 垂直スクロール |
| `IRREGULAR_SEAL_1` | 爆発1（不規則シール） |
| `IRREGULAR_SEAL_2` | 爆発2（不規則シール） |

#### 数学記号（7）

| shapeType | 説明 |
|-----------|------|
| `MATH_PLUS` | プラス |
| `MATH_MINUS` | マイナス |
| `MATH_MULTIPLY` | 掛ける |
| `MATH_DIVIDE` | 割る |
| `MATH_EQUAL` | イコール |
| `MATH_NOT_EQUAL` | ノットイコール |
| `PLUS` | 十字（プラス型シェイプ） |

#### フローチャート（29）

| shapeType | 説明 |
|-----------|------|
| `FLOW_CHART_PROCESS` | 処理 |
| `FLOW_CHART_ALTERNATE_PROCESS` | 代替処理 |
| `FLOW_CHART_DECISION` | 判断 |
| `FLOW_CHART_INPUT_OUTPUT` | 入出力（データ） |
| `FLOW_CHART_PREDEFINED_PROCESS` | 定義済み処理 |
| `FLOW_CHART_INTERNAL_STORAGE` | 内部記憶 |
| `FLOW_CHART_DOCUMENT` | 文書 |
| `FLOW_CHART_MULTIDOCUMENT` | 複数文書 |
| `FLOW_CHART_TERMINATOR` | 端子（開始/終了） |
| `FLOW_CHART_PREPARATION` | 準備 |
| `FLOW_CHART_MANUAL_INPUT` | 手動入力 |
| `FLOW_CHART_MANUAL_OPERATION` | 手動操作 |
| `FLOW_CHART_CONNECTOR` | 接続子 |
| `FLOW_CHART_OFFPAGE_CONNECTOR` | 別ページ接続子 |
| `FLOW_CHART_PUNCHED_CARD` | パンチカード |
| `FLOW_CHART_PUNCHED_TAPE` | パンチテープ |
| `FLOW_CHART_SUMMING_JUNCTION` | 加算接合 |
| `FLOW_CHART_OR` | OR |
| `FLOW_CHART_COLLATE` | 照合 |
| `FLOW_CHART_SORT` | ソート |
| `FLOW_CHART_EXTRACT` | 抽出 |
| `FLOW_CHART_MERGE` | マージ |
| `FLOW_CHART_ONLINE_STORAGE` | オンライン記憶 |
| `FLOW_CHART_OFFLINE_STORAGE` | オフライン記憶 |
| `FLOW_CHART_MAGNETIC_TAPE` | 磁気テープ |
| `FLOW_CHART_MAGNETIC_DISK` | 磁気ディスク |
| `FLOW_CHART_MAGNETIC_DRUM` | 磁気ドラム |
| `FLOW_CHART_DISPLAY` | 表示 |
| `FLOW_CHART_DELAY` | 遅延 |

#### テキスト（1）

| shapeType | 説明 |
|-----------|------|
| `TEXT_BOX` | テキストボックス（`add_text()` で自動使用される） |

> **注意**: `CUSTOM` と `TYPE_UNSPECIFIED` は `createShape` では使用不可。
> `CUSTOM` は UI で作成されたカスタム図形を API から読み取るときにのみ出現する。

---

## 9. 画像挿入

### add_image

```python
def add_image(slide_id, image_url, x, y, w, h):
    """公開 URL から画像を挿入する。"""
    img_id = _id("img")
    requests.append({"createImage": {
        "objectId": img_id,
        "url": image_url,
        "elementProperties": {
            "pageObjectId": slide_id,
            "size": {
                "width": {"magnitude": inches(w), "unit": "EMU"},
                "height": {"magnitude": inches(h), "unit": "EMU"},
            },
            "transform": {
                "scaleX": 1, "scaleY": 1,
                "translateX": inches(x), "translateY": inches(y),
                "unit": "EMU",
            },
        },
    }})
    return img_id
```

### 制約

| 項目 | 制限 |
|------|------|
| 対応フォーマット | PNG, JPEG, GIF |
| 最大ファイルサイズ | 50 MB |
| 最大ピクセル数 | 25 メガピクセル |
| URL 要件 | 公開アクセス可能な HTTPS URL |
| SVG | 非対応（PNG に変換してから挿入） |

### Google Drive 上の画像を使う場合

Drive 上の画像は直接 URL で挿入できない。以下のいずれかで対応:

1. Drive API で一時的に公開共有 → URL で挿入 → 共有解除
2. Drive API でダウンロード → ローカルサーバーから配信 → URL で挿入

### 9.1 ローカルアセットの Drive API アップロード

ローカルの画像ファイル（ロゴ、アイコン等）をスライドに挿入するには、Drive API で一時アップロードし公開 URL を取得する。OAuth スコープ `drive.file` は既にセクション1で設定済み。

```python
def upload_asset(drive_service, file_path, mime_type=None):
    """ローカル画像を Drive にアップロードし、公開 URL を返す。
    使用後に delete_uploaded_asset() で削除すること。"""
    from googleapiclient.http import MediaFileUpload
    import mimetypes

    if mime_type is None:
        mime_type, _ = mimetypes.guess_type(file_path)

    media = MediaFileUpload(file_path, mimetype=mime_type)
    file_meta = {"name": os.path.basename(file_path)}
    uploaded = drive_service.files().create(
        body=file_meta, media_body=media, fields="id"
    ).execute()
    file_id = uploaded["id"]

    # anyone:reader で一時共有
    drive_service.permissions().create(
        fileId=file_id,
        body={"type": "anyone", "role": "reader"},
    ).execute()

    # Slides API 用の直接ダウンロード URL
    url = f"https://drive.google.com/uc?id={file_id}&export=download"
    return file_id, url


def delete_uploaded_asset(drive_service, file_id):
    """アップロードしたアセットを Drive から削除する。"""
    drive_service.files().delete(fileId=file_id).execute()
```

### 9.2 SVG → PNG 変換

Google Slides API は SVG 非対応のため、PNG に変換してからアップロードする。

```python
def convert_svg_to_png(svg_path, png_path=None, width=512):
    """SVG を PNG に変換する。cairosvg が必要。"""
    import cairosvg
    if png_path is None:
        png_path = svg_path.rsplit(".", 1)[0] + ".png"
    cairosvg.svg2png(url=svg_path, write_to=png_path, output_width=width)
    return png_path
```

### 9.3 アセット解決ヘルパー

カスタムアセットフォルダ（ユーザー指定）→ スキルデフォルト（`assets/`）の順でアセットを検索する。

```python
SKILL_ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")

def resolve_asset(theme_name, category, filename, custom_assets_dir=None):
    """アセットファイルを検索する。
    検索順: ユーザー指定(テーマ) → ユーザー指定(shared) → スキル(テーマ) → スキル(shared)。
    SVG の場合は自動的に PNG 変換する。

    theme_name: "scalar", "aixdevops", "corporate" 等
    category: "logos", "product-logos", "icons"
    filename: "scalar-logo.png", "scalardb.svg" 等
    custom_assets_dir: ユーザー指定のカスタムアセットフォルダパス（None で省略）
    """
    candidates = []
    if custom_assets_dir:
        candidates.append(os.path.join(custom_assets_dir, theme_name, category, filename))
        candidates.append(os.path.join(custom_assets_dir, "shared", category, filename))
    candidates.append(os.path.join(SKILL_ASSETS_DIR, theme_name, category, filename))
    candidates.append(os.path.join(SKILL_ASSETS_DIR, "shared", category, filename))
    for path in candidates:
        if os.path.exists(path):
            if path.lower().endswith(".svg"):
                return convert_svg_to_png(path)
            return path
    return None
```

### 9.4 アセットアップロード補助: add_image_from_asset

```python
def add_image_from_asset(slide_id, theme_name, category, filename, x, y, w, h):
    """ローカルアセットを解決 → Drive アップロード → スライドに挿入。
    アップロードした file_id を _uploaded_assets に記録。
    custom_assets_dir が設定されている場合、カスタムフォルダを優先検索する。

    使用例:
        add_image_from_asset(sid, "scalar", "logos", "scalar-logo.png",
                                0.3, 0.2, 1.0, 0.5)
    """
    path = resolve_asset(theme_name, category, filename,
                         custom_assets_dir=custom_assets_dir)
    if path is None:
        raise FileNotFoundError(f"Asset not found: {category}/{filename}")
    file_id, url = upload_asset(drive_service, path)
    _uploaded_assets.append(file_id)
    return add_image(slide_id, url, x, y, w, h)
```

> **注意**: アップロードした file id は後始末のためリストに保持する。`drive_service` は `build("drive", "v3", credentials=creds)` で取得する。

### 9.5 クリーンアップ

```python
def cleanup_uploaded_assets():
    """Drive にアップロードした一時アセットを全て削除する。
    main() の最後（execute_batch 後）に呼び出す。"""
    for file_id in _uploaded_assets:
        try:
            delete_uploaded_asset(drive_service, file_id)
        except Exception:
            pass
    _uploaded_assets.clear()
```

### 9.6 出力先フォルダ

プレゼンテーションを指定の Google Drive フォルダに配置するためのヘルパー関数。

```python
import re

def resolve_folder_id(drive_service, folder_spec):
    """フォルダ指定を folder_id に解決する。

    folder_spec: 以下のいずれか
      - フォルダ URL: "https://drive.google.com/drive/folders/1ABC...XYZ"
      - フォルダ ID: "1ABC...XYZ"（英数字+アンダースコア+ハイフン）
      - フォルダ名: "営業資料"（drive.file スコープではベストエフォート）

    Returns: folder_id (str) or None
    """
    if not folder_spec:
        return None

    # URL からフォルダ ID を抽出
    url_match = re.search(r"/folders/([a-zA-Z0-9_-]+)", folder_spec)
    if url_match:
        return url_match.group(1)

    # フォルダ ID パターン（英数字+アンダースコア+ハイフン、10文字以上）
    if re.match(r"^[a-zA-Z0-9_-]{10,}$", folder_spec):
        return folder_spec

    # フォルダ名で検索（drive.file スコープではベストエフォート）
    results = drive_service.files().list(
        q=f"name = '{folder_spec}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false",
        fields="files(id, name)",
        pageSize=1,
    ).execute()
    files = results.get("files", [])
    if files:
        return files[0]["id"]
    return None


def create_folder(drive_service, folder_name, parent_id=None):
    """Google Drive にフォルダを作成する。

    parent_id: 親フォルダ ID。None の場合はマイドライブ直下。
    Returns: 作成されたフォルダの ID
    """
    metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
    }
    if parent_id:
        metadata["parents"] = [parent_id]
    folder = drive_service.files().create(
        body=metadata, fields="id"
    ).execute()
    return folder["id"]


def move_to_folder(drive_service, file_id, folder_id):
    """プレゼンテーションを指定フォルダに移動する。

    file_id: プレゼンテーション ID
    folder_id: 移動先フォルダ ID
    """
    # 現在の親フォルダを取得
    file = drive_service.files().get(
        fileId=file_id, fields="parents"
    ).execute()
    previous_parents = ",".join(file.get("parents", []))
    # 新しいフォルダに移動
    drive_service.files().update(
        fileId=file_id,
        addParents=folder_id,
        removeParents=previous_parents,
        fields="id, parents",
    ).execute()
```

> **注意**: `drive.file` スコープは自アプリが作成したファイルのみ操作可能。既存フォルダの名前検索は結果が返らない場合がある。フォルダ URL / ID 指定を推奨し、名前検索はベストエフォートとする。

### 典型的な使用フロー

```python
# main() 内
CUSTOM_ASSETS_DIR = "/path/to/custom/assets"  # or None
OUTPUT_FOLDER_ID = "1ABC...XYZ"  # or None

creds = get_credentials(CREDS_FILE, TOKEN_FILE)
slides_service = build("slides", "v1", credentials=creds)
drive_service = build("drive", "v3", credentials=creds)

_uploaded_assets = []
custom_assets_dir = CUSTOM_ASSETS_DIR

# スライド構築
sid = add_slide()
add_image_from_asset(sid, "scalar", "logos", "scalar-logo.png",
                        0.3, 0.2, 1.0, 0.5)

# 一括実行
execute_batch(slides_service, pres_id, requests)

# クリーンアップ（必須）
cleanup_uploaded_assets()

# 出力先フォルダに移動
if OUTPUT_FOLDER_ID:
    move_to_folder(drive_service, pres_id, OUTPUT_FOLDER_ID)
```

---

## 10. テーブル作成

### add_table

```python
def add_table(slide_id, rows, cols, x, y, w, h,
              data=None, header_fill=None):
    """テーブルを作成し、オプションでデータとヘッダースタイルを適用する。

    data: list of lists (行×列) のテキストデータ。None の場合は空テーブル。
    header_fill: 1行目の背景色（RGB dict）。
    """
    table_id = _id("tbl")
    requests.append({"createTable": {
        "objectId": table_id,
        "rows": rows,
        "columns": cols,
        "elementProperties": {
            "pageObjectId": slide_id,
            "size": {
                "width": {"magnitude": inches(w), "unit": "EMU"},
                "height": {"magnitude": inches(h), "unit": "EMU"},
            },
            "transform": {
                "scaleX": 1, "scaleY": 1,
                "translateX": inches(x), "translateY": inches(y),
                "unit": "EMU",
            },
        },
    }})
    # セルにテキストを挿入
    if data:
        for r, row_data in enumerate(data):
            for c, cell_text in enumerate(row_data):
                requests.append({"insertText": {
                    "objectId": table_id,
                    "cellLocation": {"rowIndex": r, "columnIndex": c},
                    "text": str(cell_text),
                    "insertionIndex": 0,
                }})
    # ヘッダー行の背景色
    if header_fill:
        for c in range(cols):
            requests.append({"updateTableCellProperties": {
                "objectId": table_id,
                "tableRange": {
                    "location": {"rowIndex": 0, "columnIndex": c},
                    "rowSpan": 1, "columnSpan": 1,
                },
                "tableCellProperties": {
                    "tableCellBackgroundFill": solid_fill(header_fill),
                },
                "fields": "tableCellBackgroundFill",
            }})
    return table_id
```

### テーブルのテキストスタイル適用

```python
def style_table_cell(table_id, row, col, style):
    """テーブルセルのテキストにスタイルを適用する。"""
    requests.append({"updateTextStyle": {
        "objectId": table_id,
        "cellLocation": {"rowIndex": row, "columnIndex": col},
        "style": style,
        "textRange": {"type": "ALL"},
        "fields": ",".join(style.keys()),
    }})
```

### 注意事項

- `createTable` はテーブルの行高さ・列幅を均等分割で作成する
- セル結合は `mergeTableCells` リクエストで実行可能
- テーブル位置の微調整は `updatePageElementTransform` で行う
- **`header_fill` 使用時は必ず白文字を適用する**: `header_fill` で色付き背景を設定した場合、デフォルトの黒テキストは読みにくい。以下のように `style_table_cell` でヘッダー行の全セルに白太字を適用すること:

```python
tbl_id = add_table(sid, rows, cols, x, y, w, h, data=data, header_fill=C.tableHeader)
style_w = text_style(10, True, C.WHITE, "Arial")
for c in range(cols):
    style_table_cell(tbl_id, 0, c, style_w)
```

---

## 11. コネクタ線・矢印付き線

2種類のコネクタを用途で使い分ける:

| メソッド | 用途 | シェイプ移動時 |
|---------|------|-------------|
| `add_connector` | 座標指定の自由配置線（フロー図パターン10等） | 追従しない |
| `add_connected_connector` | シェイプ接続線（分岐フローパターン11等） | 自動追従 |

### connectionSiteIndex リファレンス

全シェイプ共通で 4 サイト。ROUND_RECTANGLE, DIAMOND, FLOW_CHART_TERMINATOR で実測確認済み。

```
         0 (TOP)
          ┃
  1 (LEFT)╋━━ 3 (RIGHT)
          ┃
       2 (BOTTOM)
```

```python
CONN_TOP, CONN_LEFT, CONN_BOTTOM, CONN_RIGHT = 0, 1, 2, 3
```

> **注意**: `presentations.get()` の `connectionSites` フィールドは空配列を返す。
> サイト数の確認は実際に接続を試行して `HttpError` を捕捉するのが唯一の方法。

### add_connector

```python
def add_connector(slide_id, x1, y1, x2, y2,
                  color=None, weight=1.0,
                  start_arrow=None, end_arrow=None,
                  dash_style="SOLID"):
    """2点間のコネクタ線を作成する。対角線・斜め線・水平線・垂直線すべてに対応。

    水平線（y1==y2）や垂直線（x1==x2）の場合、幅/高さ 0 は API エラーとなるため
    magnitude を最小値 1 EMU にフォールバックする。
    start_arrow / end_arrow: NONE, STEALTH_ARROW, FILL_ARROW,
                             OPEN_ARROW, FILL_CIRCLE, FILL_DIAMOND 等
    dash_style: SOLID, DASH, DOT, DASH_DOT, LONG_DASH, LONG_DASH_DOT
    """
    line_id = _id("conn")
    # 左上原点とサイズを計算
    lx, ly = min(x1, x2), min(y1, y2)
    lw, lh = abs(x2 - x1), abs(y2 - y1)
    # 方向に応じた scaleX/scaleY（右下方向を正とする）
    sx = 1 if x2 >= x1 else -1
    sy = 1 if y2 >= y1 else -1
    requests.append({"createLine": {
        "objectId": line_id,
        "lineCategory": "STRAIGHT",
        "elementProperties": {
            "pageObjectId": slide_id,
            "size": {
                "width": {"magnitude": inches(lw) if lw > 0 else 1, "unit": "EMU"},
                "height": {"magnitude": inches(lh) if lh > 0 else 1, "unit": "EMU"},
            },
            "transform": {
                "scaleX": sx, "scaleY": sy,
                "translateX": inches(x1 if sx > 0 else x2),
                "translateY": inches(y1 if sy > 0 else y2),
                "unit": "EMU",
            },
        },
    }})
    # 線のプロパティ
    line_props = {
        "weight": {"magnitude": weight, "unit": "PT"},
        "dashStyle": dash_style,
    }
    fields = ["weight", "dashStyle"]
    if color:
        line_props["lineFill"] = solid_fill(color)
        fields.append("lineFill")
    if start_arrow:
        line_props["startArrow"] = start_arrow
        fields.append("startArrow")
    if end_arrow:
        line_props["endArrow"] = end_arrow
        fields.append("endArrow")
    requests.append({"updateLineProperties": {
        "objectId": line_id,
        "lineProperties": line_props,
        "fields": ",".join(fields),
    }})
    return line_id
```

### add_connected_connector

```python
# connectionSiteIndex マッピング（全シェイプ共通）:
#   0 = TOP, 1 = LEFT, 2 = BOTTOM, 3 = RIGHT
CONN_TOP, CONN_LEFT, CONN_BOTTOM, CONN_RIGHT = 0, 1, 2, 3

def add_connected_connector(slide_id,
                            start_shape_id, start_site,
                            end_shape_id, end_site,
                            color=None, weight=1.0,
                            end_arrow="FILL_ARROW",
                            dash_style="SOLID",
                            line_category="BENT"):
    """2つのシェイプを接続するコネクタ線を作成する。

    start_shape_id / end_shape_id: add_shape() 等が返す objectId。
    start_site / end_site: connectionSiteIndex (0=top, 1=left, 2=bottom, 3=right)。
    line_category: "BENT"（エルボー、デフォルト）or "STRAIGHT"（直線）。
        BENT はファンアウト（1対多接続）でプロフェッショナルな外観。
        STRAIGHT は垂直/水平の直接接続（1対1）に使用。
    Google Slides が自動的にシェイプの接続ポイントにスナップする。
    """
    line_id = _id("cconn")
    # 仮の位置で作成（接続設定後に自動調整される）
    requests.append({"createLine": {
        "objectId": line_id,
        "lineCategory": line_category,
        "elementProperties": {
            "pageObjectId": slide_id,
            "size": {
                "width": {"magnitude": inches(0.1), "unit": "EMU"},
                "height": {"magnitude": inches(0.1), "unit": "EMU"},
            },
            "transform": {
                "scaleX": 1, "scaleY": 1,
                "translateX": 0, "translateY": 0,
                "unit": "EMU",
            },
        },
    }})
    line_props = {
        "startConnection": {
            "connectedObjectId": start_shape_id,
            "connectionSiteIndex": start_site,
        },
        "endConnection": {
            "connectedObjectId": end_shape_id,
            "connectionSiteIndex": end_site,
        },
        "weight": {"magnitude": weight, "unit": "PT"},
        "dashStyle": dash_style,
    }
    fields = ["startConnection", "endConnection", "weight", "dashStyle"]
    if color:
        line_props["lineFill"] = solid_fill(color)
        fields.append("lineFill")
    if end_arrow:
        line_props["endArrow"] = end_arrow
        fields.append("endArrow")
    requests.append({"updateLineProperties": {
        "objectId": line_id,
        "lineProperties": line_props,
        "fields": ",".join(fields),
    }})
    return line_id
```

### 矢印ヘッドタイプ

| 値 | 形状 |
|----|------|
| `NONE` | なし |
| `STEALTH_ARROW` | ステルス（細い三角） |
| `FILL_ARROW` | 塗りつぶし三角 |
| `OPEN_ARROW` | 白抜き三角 |
| `FILL_CIRCLE` | 塗りつぶし円 |
| `FILL_DIAMOND` | 塗りつぶしひし形 |
| `FILL_SQUARE` | 塗りつぶし四角 |

### 破線スタイル

| 値 | 描画 |
|----|------|
| `SOLID` | ──── |
| `DASH` | ── ── |
| `DOT` | ·· ·· |
| `DASH_DOT` | ── · ── |
| `LONG_DASH` | ─── ─── |
| `LONG_DASH_DOT` | ─── · ─── |

---

## 12. スタイル拡張

### グラデーション塗り

> **制約**: Google Slides API では `shapeBackgroundFill.gradientFill` は**読み取り専用**（GET のみ）。
> API からのグラデーション設定は `solidFill` に限定される。

### グラデーション近似（半透明矩形の重ね合わせ）

```python
def add_gradient_fill(slide_id, x, y, w, h,
                      color_start, color_end, steps=5):
    """半透明矩形の重ね合わせでグラデーションを近似する。

    color_start / color_end: RGB dict。
    steps: 分割数（多いほど滑らか、リクエスト数も増加）。
    """
    strip_w = w / steps
    for i in range(steps):
        # color_start → color_end を線形補間
        t = i / max(steps - 1, 1)
        blended = {
            "red":   color_start["red"]   * (1 - t) + color_end["red"]   * t,
            "green": color_start["green"] * (1 - t) + color_end["green"] * t,
            "blue":  color_start["blue"]  * (1 - t) + color_end["blue"]  * t,
        }
        add_rect(slide_id, x + i * strip_w, y, strip_w + 0.01, h,
                      fill=blended)
```

もう一つの方法: UI で作成したグラデーション付きテンプレートスライドを `duplicateObject` でコピーする。

### 透明度（alpha）

```python
def shape_opacity(shape_id, alpha):
    """シェイプの背景塗りに透明度を設定する。alpha: 0.0（透明）〜 1.0（不透明）。
    前提: add_shape(fill=...) で solidFill が設定済みであること。fill 未設定のシェイプには効果なし。

    推奨 alpha 値:
    - 暗色背景上の白カード: 0.20 以上（0.15 は視認困難）
    - 白背景上の薄色カード: 0.05-0.15
    - ベン図の円: 0.30-0.40
    """
    requests.append({"updateShapeProperties": {
        "objectId": shape_id,
        "shapeProperties": {
            "shapeBackgroundFill": {
                "solidFill": {
                    "alpha": alpha,
                },
            },
        },
        "fields": "shapeBackgroundFill.solidFill.alpha",
    }})
```

### 回転

```python
def shape_rotation(shape_id, angle_deg, x=None, y=None, w=None, h=None):
    """シェイプをその場（中心基準）で回転させる。angle_deg: 回転角度（度、時計回りが正）。

    x, y, w, h: createShape 時に指定したシェイプの位置・サイズ（インチ）。
    4つ全て指定時は ABSOLUTE モードで中心基準の正確な in-place 回転を行う。
    未指定時は RELATIVE モード（原点基準のため位置がずれる場合がある）。

    使用例:
        # createShape 時と同じ座標を渡す
        add_shape(slide_id, "RECTANGLE", x=2.0, y=1.5, w=3.0, h=2.0, fill=C.primary)
        shape_rotation(shape_id, 45, x=2.0, y=1.5, w=3.0, h=2.0)
    """
    import math
    rad = math.radians(angle_deg)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)

    if x is not None and y is not None and w is not None and h is not None:
        # ABSOLUTE モード: ローカル座標 (0,0)-(W,H) → ページ座標への変換行列
        # ローカル中心 (W/2, H/2) がページ中心 (X+W/2, Y+H/2) に写るよう translate を算出
        x_emu = inches(x)
        y_emu = inches(y)
        w_emu = inches(w)
        h_emu = inches(h)
        tx = x_emu + w_emu / 2 * (1 - cos_a) + h_emu / 2 * sin_a
        ty = y_emu + h_emu / 2 * (1 - cos_a) - w_emu / 2 * sin_a
        requests.append({"updatePageElementTransform": {
            "objectId": shape_id,
            "applyMode": "ABSOLUTE",
            "transform": {
                "scaleX": cos_a,
                "scaleY": cos_a,
                "shearX": -sin_a,
                "shearY": sin_a,
                "translateX": tx,
                "translateY": ty,
                "unit": "EMU",
            },
        }})
    else:
        # RELATIVE モード（原点基準回転。小角度やデコレーション用途向け）
        requests.append({"updatePageElementTransform": {
            "objectId": shape_id,
            "applyMode": "RELATIVE",
            "transform": {
                "scaleX": cos_a,
                "scaleY": cos_a,
                "shearX": -sin_a,
                "shearY": sin_a,
                "translateX": 0,
                "translateY": 0,
                "unit": "EMU",
            },
        }})
```

### ドロップシャドウ

```python
def shape_shadow(shape_id, blur_radius=3.0, offset_x=2.0, offset_y=2.0,
                 color=None, alpha=0.3):
    """シェイプにドロップシャドウを適用する。単位は PT。"""
    shadow_color = color or {"red": 0, "green": 0, "blue": 0}
    requests.append({"updateShapeProperties": {
        "objectId": shape_id,
        "shapeProperties": {
            "shadow": {
                "type": "OUTER",
                "transform": {
                    "scaleX": 1, "scaleY": 1,
                    "translateX": offset_x * 12700,  # PT → EMU
                    "translateY": offset_y * 12700,
                    "unit": "EMU",
                },
                "alignment": "BOTTOM_LEFT",
                "blurRadius": {"magnitude": blur_radius, "unit": "PT"},
                "color": {"rgbColor": shadow_color},
                "alpha": alpha,
                "rotateWithShape": True,
                "propertyState": "RENDERED",
            },
        },
        "fields": "shadow",
    }})
```

---

## 13. グループ化と Z-order

### グループ化

```python
def group_objects(object_ids):
    """複数のオブジェクトをグループ化する。object_ids: list of objectId。
    全オブジェクトは同一スライド上にある必要がある。
    """
    group_id = _id("grp")
    requests.append({"groupObjects": {
        "groupObjectId": group_id,
        "childrenObjectIds": object_ids,
    }})
    return group_id
```

### Z-order 操作

```python
def set_z_order(shape_id, operation):
    """シェイプの重なり順を変更する。

    operation: BRING_TO_FRONT, BRING_FORWARD, SEND_BACKWARD, SEND_TO_BACK
    """
    requests.append({"updatePageElementsZOrder": {
        "pageElementObjectIds": [shape_id],
        "operation": operation,
    }})
```

### 注意事項

- `groupObjects` のオブジェクトはすべて同一スライド上にある必要がある
- グループ化後は `group_id` でグループ全体を移動・回転できる
- Z-order は同一スライド内でのみ有効

---

## 14. カスタムページサイズ

### プリセット

| フォーマット | 幅 (in) | 高さ (in) | 用途 |
|-------------|---------|----------|------|
| 16:9（デフォルト） | 10.000 | 5.625 | スライドプレゼンテーション |
| A4 縦 | 8.270 | 11.690 | 印刷用インフォグラフィクス |
| Letter 縦 | 8.500 | 11.000 | US レター縦 |
| Square | 10.000 | 10.000 | SNS 用正方形 |
| Poster | 11.000 | 17.000 | ポスター |

### pageSize 指定（presentations.create 時のみ）

```python
PAGE_SIZES = {
    "16:9":    (10.000, 5.625),
    "A4":      (8.270, 11.690),
    "letter":  (8.500, 11.000),
    "square":  (10.000, 10.000),
    "poster":  (11.000, 17.000),
}

def create_presentation(slides_service, title, page_size="16:9"):
    """カスタムページサイズでプレゼンテーションを作成する。"""
    w, h = PAGE_SIZES[page_size]
    presentation = slides_service.presentations().create(
        body={
            "title": title,
            "pageSize": {
                "width": {"magnitude": inches(w), "unit": "EMU"},
                "height": {"magnitude": inches(h), "unit": "EMU"},
            },
        }
    ).execute()
    return presentation
```

### 座標のスケーリング

カスタムページサイズ（A4縦、ポスター等）では、セクション2の `calc_layout`（16:9スライド向け）とは異なる比率を使う:

```python
def calc_layout_custom(sw, sh):
    """カスタムページサイズ用のレイアウト定数を計算する。
    縦長ページでタイトル・本文領域を広く取るための比率設定。
    16:9 スライド用にはセクション 2 の calc_layout() を使うこと。
    """
    return {
        "MX":          sw * 0.0375,
        "CW":          sw * 0.925,
        "TITLE_Y":     sh * 0.030,
        "TITLE_H":     sh * 0.050,
        "BODY_TOP":    sh * 0.100,
        "BODY_BOTTOM": sh * 0.950,
        "FOOTER_Y":    sh * 0.965,
    }
```

> **使い分け**: 16:9スライドには `calc_layout()`（セクション2）、A4縦やポスター等のカスタムサイズには `calc_layout_custom()` を使用する。

> **重要**: `pageSize` はプレゼンテーション作成時（`presentations.create`）にのみ指定可能。作成後の変更は不可。
