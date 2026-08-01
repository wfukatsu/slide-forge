# template.json のスキーマ

`scripts/inspect_template.py` が生成する。手で編集してよいのは `name` / `displayName` /
`roles` / `pageNumber` / `drawText` と `__*` のコメントフィールド。それ以外はテンプレートの
実測値なので、**マスターを更新したら再解析して上書きする**。

```jsonc
{
  "name": "my-brand",                       // テンプレート ID（ファイル名と合わせる）
  "displayName": "My Brand Master 2026",    // 人間向け表示名
  "sourceUrl": "https://docs.google.com/presentation/d/…",
  "presentationId": "1abc…",                // 複製元。無い場合は新規プレゼンを作る
  "generationMode": "copy",                 // copy | create

  "pageSize": { "widthInches": 10.0, "heightInches": 5.625, "aspectRatio": "1.778:1" },

  // 複製直後に削除するテンプレート同梱スライド。マスターを編集したら再解析する
  "existingSlideIds": ["g3b40_0_0", "…"],

  // マスターの colorScheme。Palette がここから図解用の色を組む
  // dark1/light1/dark2/light2/accent1..6 が入る
  "colors": { "dark1": "#0F172A", "accent5": "#2673BB", "…": "…" },

  // ページ番号の描画スタイル。API は SLIDE_NUMBER を生成できないため自前描画する
  "pageNumber": { "font": "Arial", "fontSize": 7, "color": "#666666",
                  "align": "END", "startAt": 1 },

  // マスターが全ページに敷く要素の記録。複製方式では自動継承されるので描画指示ではない。
  // 図の下端（DY1）を決める根拠として読む
  "masterDecorations": [
    { "type": "image", "objectId": "…", "x": 0.118, "y": 5.197, "w": 1.181, "h": 0.342 }
  ],

  // セマンティックロール → レイアウトキー。推測値なので人間が確認して確定させる
  "roles": {
    "COVER": "TITLE_SLIDE",
    "SECTION": "SLIDE_SUB_SECTION",
    "CONTENT": "DEFAULT_PROPOSAL",
    "TITLE_ONLY": "TITLE_ONLY_PROPOSAL",   // 図解ページの主役
    "BLANK": "WHITE",
    "CLOSING": "CLOSE_PAGE"
  },
  // 推測時に見つかった候補。ロール確定後の再確認用に残す
  "roleCandidates": { "CONTENT": ["DEFAULT_PROPOSAL", "DEFAULT_PRESENTATION"] },

  "layouts": {
    "DEFAULT_PROPOSAL": {
      "layoutId": "g1b3a_0_19",             // createSlide に渡す ID（複製方式）
      "predefinedLayout": null,             // Google 既定レイアウトを使う場合はこちら
      "displayName": "Default - Proposal",
      "placeholders": ["TITLE", "SLIDE_NUMBER", "BODY"],
      // 2/3 カラムのレイアウトは BODY を複数持つ: ["TITLE","BODY","BODY#1","BODY#2"]
      // index 0 が "BODY"、以降が "BODY#1"。座標も elements.body / body#1 に入る
      "hasPageNumber": true,
      "elements": {                          // 座標はすべてインチ
        "title":       { "x": 0.5, "y": 0.126, "w": 9.0, "h": 0.351, "align": "START" },
        "body":        { "x": 0.5, "y": 0.96,  "w": 9.0, "h": 4.068, "align": "START" },
        "slideNumber": { "x": 9.611, "y": 5.378, "w": 0.222, "h": 0.219, "align": "END" }
      },
      "textStyles": {                        // プレースホルダの既定スタイル
        "title": { "fontFamily": "Noto Sans JP", "fontSize": 20, "bold": false,
                   "color": "theme:DARK1" }
      },
      "decorations": [                       // このレイアウト固有の非プレースホルダ要素
        { "type": "shape", "shapeType": "RECTANGLE", "fill": "theme:ACCENT6",
          "x": 0.367, "y": 0.059, "w": 0.054, "h": 0.398 }
      ]
    }
  }
}
```

## フィールドの読み方

| フィールド | 使いどころ |
|---|---|
| `placeholders` | `title` / `subtitle` / `body` を指定してよいかの判定。ここに無いものを指定するとエラー |
| `elements.title` の `y + h` | 図の上端（`DY0`）を決める根拠 |
| `masterDecorations` の最小 `y` | 図の下端（`DY1`）を決める根拠 |
| `elements.slideNumber` | ページ番号の描画位置。幅が狭いレイアウトが多いので、ビルダーは右端を保ったまま最小 0.5in に広げる |
| `textStyles.title.fontSize` | タイトルが 1 行に収まる文字数の根拠（`TITLE_EM_MAX`） |
| `decorations` に全面サイズの矩形 | マスターのフッターを覆っている可能性を疑う |
| `colors` の `theme:XXX` | テーマ色参照。実際の hex は `colors.accent6` を引く |

## 拡張フィールド

`inspect_template.py` は出力しない。手で足す。

### `drawText` — 座標指定でテキストを描く

プレースホルダを使わず、テキストボックスを座標指定で描く。
**Slides API に要素のサイズを変更するリクエストが無い**ため、Google 既定レイアウト
（`predefinedLayout`）ではタイトルの幅を制御できず折り返してしまう。これを回避する。

```jsonc
"drawText": {
  "title": { "x": 0.5, "y": 0.30, "w": 9.0, "h": 0.46,
             "size": 20, "bold": true, "align": "START", "valign": "MIDDLE",
             "color": "#0F172A", "fontFamily": "Noto Sans JP" },
  "body":  { "x": 0.5, "y": 0.96, "w": 9.0, "h": 4.07,
             "size": 12, "align": "START", "valign": "TOP", "lineSpacing": 120 }
}
```

キーは `title` / `subtitle` / `body` / `bodyx1`（= `BODY#1`）。
`drawText` を持つキーはプレースホルダが割り当てられないため、`placeholders` を
空にしてよい（検査側も `drawText` を指定可能な枠として扱う）。

同梱の `templates/blank-16x9.json` がこの方式で、マスター無しでも図解デッキが作れる。

### `applyElementGeometry` — プレースホルダの位置と書式を寄せる

`true` にすると、実プレースホルダに `elements` の位置と `textStyles` の書式を適用する
（位置・上寄せ・文字サイズ・揃えの 4 点）。幅は変えられないので、幅の制御が必要なら
`drawText` を使う。マスター複製方式ではレイアウト側が既に正しいので指定しない。

## 新しいロールを足す

`roles` は別名テーブルなので自由に増やせる。用途別に系統を持つマスターでは、
系統名をサフィックスにすると読みやすい。

```json
"roles": {
  "CONTENT": "DEFAULT_PROPOSAL",
  "CONTENT_PRESENTATION": "DEFAULT_PRESENTATION",
  "TITLE_ONLY": "TITLE_ONLY_PROPOSAL",
  "TITLE_ONLY_PRESENTATION": "TITLE_ONLY_PRESENTATION"
}
```

ロールを介さず `layout="DEFAULT_PRESENTATION"` とレイアウトキーを直接書いてもよい。
ロールの利点は、テンプレートを差し替えても同じデッキモジュールが使い回せること。
