*[日本語](google-slides-api.ja.md)*
# Google Slides API — Raw Reference

The request shapes, units, limits and quirks of the Slides REST API itself.

**Read `references/api-notes.md` first.** It carries the failures we have
actually hit and their fixes; this file is where you go when the answer is not
there and you need the API's own behaviour — a request body you have not sent
before, a limit you are about to run into, a shape or connector property that
is not exposed by the engine.

**This is not how you build a deck.** slide-forge does not call the API by
hand: `scripts/build_deck.py` turns a spec into requests, `scripts/diagrams.py`
draws, and `scripts/deckkit.py` is the authoring surface. Auth lives in
`scripts/_auth.py`. The Python below is illustrative — plain functions that
show the request JSON, not the engine's own code. See
[diagrams.md](diagrams.md) and [template-schema.md](template-schema.md) for
what you would normally write instead.

## 1. Coordinate system

### EMU (English Metric Units)

```python
EMU = 914400  # 1 inch = 914,400 EMU

def inches(val):
    """インチを EMU に変換する。"""
    return int(val * EMU)
```

### Google Slides vs PowerPoint

| | PowerPoint 16:9 | Google Slides 16:9 | Ratio |
|-|-----------------|---------------------|------|
| Width | 13.333" (12,192,000 EMU) | **10.000"** (9,144,000 EMU) | 0.75x |
| Height | 7.500" (6,858,000 EMU) | **5.625"** (5,143,500 EMU) | 0.75x |

Google Slides normalizes 16:9 to **10" x 5.625"**. Multiply by 0.75 when converting from PowerPoint coordinates.

### Ratio-based coordinate calculation (recommended)

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

## 2. Helper functions

### Color conversion

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

### Style builders

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

## 3. Request builders

### Creating a shape

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

### Creating a text box

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

### Inserting text / applying styles

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

### Updating shape properties

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

### Page background

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

## 4. Batch execution

### Chunking into batches of 500

The Google Slides API's `batchUpdate` can send a large number of requests at once, but for safety they are split into chunks of 500.

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

### A typical main() structure

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

## 5. Sheets API chart integration

A native Google Slides chart requires integration with the Sheets API.

### Steps for creating a linked chart

1. Create the data and chart in Google Sheets
2. Get the chart ID with `sheets_service.spreadsheets().get()`
3. Embed it into the slide with a `createSheetsChart` request

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

## 6. API constraints & pitfalls

### Key constraints

| Constraint | Detail |
|------|------|
| `pageSize` only at creation time | Cannot be changed via `updatePageProperties`; specify it in `presentations.create` |
| `objectId` must be 5+ characters | The `objectId` for `createSlide`, `createShape`, etc. must be at least 5 characters |
| outline weight > 0 | `weight=0` is an error. Use `propertyState: NOT_RENDERED` to hide it |
| BLANK layout recommended | For custom layouts, use BLANK and place every element yourself |
| 16:9 normalization | Google Slides normalizes to 10" x 5.625" (0.75x PowerPoint) |

### Rate limits

| Type | Limit |
|------|------|
| Read requests | 300/min/user |
| Write requests | 60/min/user |
| batchUpdate | Multiple requests allowed per call (chunk size of 500 recommended) |

### BLANK vs placeholders

| Approach | Pros | Cons |
|------|---------|-----------|
| BLANK + custom shapes | Full layout control; design can be shared with PPTX | No benefit from theme changes; all coordinates must be computed manually |
| Placeholders | Theme-linked; automatically adjusts on theme change | Fine-grained layout control is difficult |

**Recommendation:** when custom layouts (36+ types, etc.) are required, adopt the **BLANK + custom shapes approach**.

---

## 7. Retrieving thumbnails (for visual QA)

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

### Configuring sharing via the Drive API

Thumbnail URLs can be retrieved even without the presentation being shared, but external verification tools may sometimes require sharing to be enabled.

```python
def share_presentation(drive_service, pres_id):
    """プレゼンテーションを anyone:reader で共有する。"""
    drive_service.permissions().create(
        fileId=pres_id,
        body={"type": "anyone", "role": "reader"},
    ).execute()
```

---

## 8. General-purpose shape creation

### add_shape (any shapeType)

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

### Convenience methods

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

### Complete shapeType reference (all 141 types)

> All values that can be passed as `shape_type` to `add_shape(slide_id, shape_type, x, y, w, h, ...)`.
> `TYPE_UNSPECIFIED` and `CUSTOM` are excluded because they cannot be used with `createShape`.

#### Basic shapes (33)

| shapeType | Description |
|-----------|------|
| `RECTANGLE` | Rectangle |
| `ROUND_RECTANGLE` | Rounded rectangle |
| `ROUND_1_RECTANGLE` | Rectangle with one rounded corner |
| `ROUND_2_DIAGONAL_RECTANGLE` | Rectangle with two diagonal rounded corners |
| `ROUND_2_SAME_RECTANGLE` | Rectangle with two same-side rounded corners |
| `SNIP_1_RECTANGLE` | Rectangle with one cut corner |
| `SNIP_2_DIAGONAL_RECTANGLE` | Rectangle with two diagonal cut corners |
| `SNIP_2_SAME_RECTANGLE` | Rectangle with two same-side cut corners |
| `SNIP_ROUND_RECTANGLE` | Rectangle with one cut corner and one rounded corner |
| `ELLIPSE` | Ellipse / circle (a true circle when w=h) |
| `ARC` | Arc |
| `CHORD` | Chord (bowtie segment) |
| `PIE` | Pie / sector |
| `BLOCK_ARC` | Block arc |
| `TRIANGLE` | Triangle |
| `RIGHT_TRIANGLE` | Right triangle |
| `DIAMOND` | Diamond |
| `PARALLELOGRAM` | Parallelogram |
| `TRAPEZOID` | Trapezoid |
| `PENTAGON` | Pentagon |
| `HEXAGON` | Hexagon |
| `HEPTAGON` | Heptagon |
| `OCTAGON` | Octagon |
| `DECAGON` | Decagon |
| `DODECAGON` | Dodecagon |
| `BEVEL` | Bevel (frame-like) |
| `CAN` | Cylinder (can) |
| `CUBE` | Cube |
| `DONUT` | Donut |
| `FRAME` | Frame |
| `HALF_FRAME` | Half frame |
| `CORNER` | Corner |
| `DIAGONAL_STRIPE` | Diagonal stripe |

#### Arrows (21)

| shapeType | Description |
|-----------|------|
| `RIGHT_ARROW` | Right arrow |
| `LEFT_ARROW` | Left arrow |
| `UP_ARROW` | Up arrow |
| `DOWN_ARROW` | Down arrow |
| `LEFT_RIGHT_ARROW` | Left-right arrow |
| `UP_DOWN_ARROW` | Up-down arrow |
| `LEFT_RIGHT_UP_ARROW` | Left-right-up arrow |
| `LEFT_UP_ARROW` | Left-up arrow |
| `QUAD_ARROW` | Four-directional arrow |
| `BENT_ARROW` | Bent arrow |
| `BENT_UP_ARROW` | Bent-up arrow |
| `CURVED_DOWN_ARROW` | Curved-down arrow |
| `CURVED_LEFT_ARROW` | Curved-left arrow |
| `CURVED_RIGHT_ARROW` | Curved-right arrow |
| `CURVED_UP_ARROW` | Curved-up arrow |
| `NOTCHED_RIGHT_ARROW` | Notched right arrow |
| `STRIPED_RIGHT_ARROW` | Striped right arrow |
| `UTURN_ARROW` | U-turn arrow |
| `ARROW_EAST` | East arrow (thin) |
| `ARROW_NORTH_EAST` | Northeast arrow (thin) |
| `ARROW_NORTH` | North arrow (thin) |

#### Arrow callouts (7)

| shapeType | Description |
|-----------|------|
| `RIGHT_ARROW_CALLOUT` | Right arrow callout |
| `LEFT_ARROW_CALLOUT` | Left arrow callout |
| `UP_ARROW_CALLOUT` | Up arrow callout |
| `DOWN_ARROW_CALLOUT` | Down arrow callout |
| `LEFT_RIGHT_ARROW_CALLOUT` | Left-right arrow callout |
| `QUAD_ARROW_CALLOUT` | Four-directional arrow callout |
| `WEDGE_RECTANGLE_CALLOUT` | Rectangular speech bubble |

#### Speech bubbles (3)

| shapeType | Description |
|-----------|------|
| `WEDGE_ELLIPSE_CALLOUT` | Oval speech bubble |
| `WEDGE_ROUND_RECTANGLE_CALLOUT` | Rounded-rectangle speech bubble |
| `CLOUD_CALLOUT` | Cloud-shaped speech bubble |

#### Brackets / braces (6)

| shapeType | Description |
|-----------|------|
| `LEFT_BRACKET` | Left bracket |
| `RIGHT_BRACKET` | Right bracket |
| `LEFT_BRACE` | Left brace |
| `RIGHT_BRACE` | Right brace |
| `BRACE_PAIR` | Brace pair |
| `BRACKET_PAIR` | Bracket pair |

#### Stars, ribbons, and decorations (18)

| shapeType | Description |
|-----------|------|
| `STAR_4` | 4-point star |
| `STAR_5` | 5-point star |
| `STAR_6` | 6-point star (Star of David) |
| `STAR_7` | 7-point star |
| `STAR_8` | 8-point star |
| `STAR_10` | 10-point star |
| `STAR_12` | 12-point star |
| `STAR_16` | 16-point star |
| `STAR_24` | 24-point star |
| `STAR_32` | 32-point star |
| `STARBURST` | Starburst |
| `RIBBON` | Ribbon |
| `RIBBON_2` | Ribbon 2 |
| `ELLIPSE_RIBBON` | Oval ribbon |
| `ELLIPSE_RIBBON_2` | Oval ribbon 2 |
| `HEART` | Heart |
| `SUN` | Sun |
| `MOON` | Moon |

#### Decorations / symbols (12)

| shapeType | Description |
|-----------|------|
| `CLOUD` | Cloud |
| `LIGHTNING_BOLT` | Lightning bolt |
| `SMILEY_FACE` | Smiley face |
| `NO_SMOKING` | Prohibition symbol |
| `FOLDED_CORNER` | Folded corner |
| `CHEVRON` | Chevron |
| `HOME_PLATE` | Home plate |
| `PLAQUE` | Plaque |
| `TEARDROP` | Teardrop |
| `SPEECH` | Speech |
| `DOUBLE_WAVE` | Double wave |
| `WAVE` | Wave |

#### Scrolls / seals (4)

| shapeType | Description |
|-----------|------|
| `HORIZONTAL_SCROLL` | Horizontal scroll |
| `VERTICAL_SCROLL` | Vertical scroll |
| `IRREGULAR_SEAL_1` | Explosion 1 (irregular seal) |
| `IRREGULAR_SEAL_2` | Explosion 2 (irregular seal) |

#### Math symbols (7)

| shapeType | Description |
|-----------|------|
| `MATH_PLUS` | Plus |
| `MATH_MINUS` | Minus |
| `MATH_MULTIPLY` | Multiply |
| `MATH_DIVIDE` | Divide |
| `MATH_EQUAL` | Equal |
| `MATH_NOT_EQUAL` | Not equal |
| `PLUS` | Cross (plus-shaped shape) |

#### Flowchart (29)

| shapeType | Description |
|-----------|------|
| `FLOW_CHART_PROCESS` | Process |
| `FLOW_CHART_ALTERNATE_PROCESS` | Alternate process |
| `FLOW_CHART_DECISION` | Decision |
| `FLOW_CHART_INPUT_OUTPUT` | Input/output (data) |
| `FLOW_CHART_PREDEFINED_PROCESS` | Predefined process |
| `FLOW_CHART_INTERNAL_STORAGE` | Internal storage |
| `FLOW_CHART_DOCUMENT` | Document |
| `FLOW_CHART_MULTIDOCUMENT` | Multiple documents |
| `FLOW_CHART_TERMINATOR` | Terminator (start/end) |
| `FLOW_CHART_PREPARATION` | Preparation |
| `FLOW_CHART_MANUAL_INPUT` | Manual input |
| `FLOW_CHART_MANUAL_OPERATION` | Manual operation |
| `FLOW_CHART_CONNECTOR` | Connector |
| `FLOW_CHART_OFFPAGE_CONNECTOR` | Off-page connector |
| `FLOW_CHART_PUNCHED_CARD` | Punched card |
| `FLOW_CHART_PUNCHED_TAPE` | Punched tape |
| `FLOW_CHART_SUMMING_JUNCTION` | Summing junction |
| `FLOW_CHART_OR` | OR |
| `FLOW_CHART_COLLATE` | Collate |
| `FLOW_CHART_SORT` | Sort |
| `FLOW_CHART_EXTRACT` | Extract |
| `FLOW_CHART_MERGE` | Merge |
| `FLOW_CHART_ONLINE_STORAGE` | Online storage |
| `FLOW_CHART_OFFLINE_STORAGE` | Offline storage |
| `FLOW_CHART_MAGNETIC_TAPE` | Magnetic tape |
| `FLOW_CHART_MAGNETIC_DISK` | Magnetic disk |
| `FLOW_CHART_MAGNETIC_DRUM` | Magnetic drum |
| `FLOW_CHART_DISPLAY` | Display |
| `FLOW_CHART_DELAY` | Delay |

#### Text (1)

| shapeType | Description |
|-----------|------|
| `TEXT_BOX` | Text box (used automatically by `add_text()`) |

> **Note**: `CUSTOM` and `TYPE_UNSPECIFIED` cannot be used with `createShape`.
> `CUSTOM` only appears when reading a custom shape created in the UI back via the API.

---

## 9. Inserting images

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

### Constraints

| Item | Limit |
|------|------|
| Supported formats | PNG, JPEG, GIF |
| Maximum file size | 50 MB |
| Maximum pixel count | 25 megapixels |
| URL requirement | A publicly accessible HTTPS URL |
| SVG | Not supported (convert to PNG before inserting) |

### Using images stored in Google Drive

Images in Drive cannot be inserted directly by URL. Use one of the following approaches:

1. Temporarily share it publicly via the Drive API → insert by URL → revoke sharing
2. Download it via the Drive API → serve it from a local server → insert by URL

### 9.1 Uploading local assets via the Drive API

To insert a local image file (a logo, icon, etc.) into a slide, temporarily upload it via the Drive API to obtain a public URL. The `drive.file` OAuth scope was already configured in section 1.

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

### 9.2 SVG → PNG conversion

Since the Google Slides API does not support SVG, convert it to PNG before uploading.

```python
def convert_svg_to_png(svg_path, png_path=None, width=512):
    """SVG を PNG に変換する。cairosvg が必要。"""
    import cairosvg
    if png_path is None:
        png_path = svg_path.rsplit(".", 1)[0] + ".png"
    cairosvg.svg2png(url=svg_path, write_to=png_path, output_width=width)
    return png_path
```

### 9.3 Asset resolution helper

Searches for assets in order: the custom asset folder (user-specified) → the skill's default folder (`assets/`).

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

### 9.4 Asset upload helper: add_image_from_asset

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

> **Note**: keep the uploaded file ids in a list so they can be cleaned up, and build `drive_service` with `build("drive", "v3", credentials=creds)`.

### 9.5 Cleanup

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

### 9.6 Destination folder

Helper functions for placing the presentation into a specified Google Drive folder.

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

> **Note**: the `drive.file` scope can only operate on files your own app created. Searching for an existing folder by name may return no results. Prefer specifying the folder URL / ID, and treat name search as best-effort only.

### Typical usage flow

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

## 10. Creating tables

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

### Applying text styles to a table

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

### Notes

- `createTable` creates the table with row heights and column widths split evenly
- Cell merging can be done with a `mergeTableCells` request
- Fine-tune table position with `updatePageElementTransform`
- **Always apply white text when using `header_fill`**: when a colored background is set with `header_fill`, the default black text becomes hard to read. Apply bold white text to every cell in the header row using `style_table_cell`, as shown below:

```python
tbl_id = add_table(sid, rows, cols, x, y, w, h, data=data, header_fill=C.tableHeader)
style_w = text_style(10, True, C.WHITE, "Arial")
for c in range(cols):
    style_table_cell(tbl_id, 0, c, style_w)
```

---

## 11. Connector lines / arrow-tipped lines

Two kinds of connector are used for different purposes:

| Method | Use | Behavior when a shape is moved |
|---------|------|-------------|
| `add_connector` | Freely-positioned line by coordinates (e.g., flow diagram pattern 10) | Does not follow |
| `add_connected_connector` | A line connecting shapes (e.g., branching flow pattern 11) | Follows automatically |

### connectionSiteIndex reference

Every shape shares 4 sites. Verified empirically on ROUND_RECTANGLE, DIAMOND, and FLOW_CHART_TERMINATOR.

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

> **Note**: the `connectionSites` field returned by `presentations.get()` is an empty array.
> The only way to confirm the number of sites is to actually attempt a connection and catch the `HttpError`.

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

### Arrowhead types

| Value | Shape |
|----|------|
| `NONE` | None |
| `STEALTH_ARROW` | Stealth (thin triangle) |
| `FILL_ARROW` | Filled triangle |
| `OPEN_ARROW` | Open (outline) triangle |
| `FILL_CIRCLE` | Filled circle |
| `FILL_DIAMOND` | Filled diamond |
| `FILL_SQUARE` | Filled square |

### Dash styles

| Value | Rendering |
|----|------|
| `SOLID` | ──── |
| `DASH` | ── ── |
| `DOT` | ·· ·· |
| `DASH_DOT` | ── · ── |
| `LONG_DASH` | ─── ─── |
| `LONG_DASH_DOT` | ─── · ─── |

---

## 12. Style extensions

### Gradient fills

> **Constraint**: in the Google Slides API, `shapeBackgroundFill.gradientFill` is **read-only** (GET only).
> Setting a gradient via the API is limited to `solidFill`.

### Gradient approximation (overlapping semi-transparent rectangles)

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

Another approach: copy a template slide with a gradient created in the UI using `duplicateObject`.

### Opacity (alpha)

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

### Rotation

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

### Drop shadow

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

## 13. Grouping and Z-order

### Grouping

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

### Z-order operations

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

### Notes

- All objects passed to `groupObjects` must be on the same slide
- Once grouped, the entire group can be moved/rotated via `group_id`
- Z-order is only meaningful within the same slide

---

## 14. Custom page sizes

### Presets

| Format | Width (in) | Height (in) | Use |
|-------------|---------|----------|------|
| 16:9 (default) | 10.000 | 5.625 | Slide presentations |
| A4 portrait | 8.270 | 11.690 | Print infographics |
| Letter portrait | 8.500 | 11.000 | US letter portrait |
| Square | 10.000 | 10.000 | Square format for social media |
| Poster | 11.000 | 17.000 | Posters |

### Specifying pageSize (only at presentations.create)

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

### Coordinate scaling

For custom page sizes (A4 portrait, poster, etc.), use a different set of ratios than the `calc_layout` in section 2 (which targets 16:9 slides):

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

> **Usage guide**: use `calc_layout()` (section 2) for 16:9 slides, and `calc_layout_custom()` for custom sizes such as A4 portrait or posters.

> **Important**: `pageSize` can only be specified when the presentation is created (`presentations.create`). It cannot be changed afterward.
