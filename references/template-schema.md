# スキーマ定義

`template.json`（テンプレート登録ファイル）と デッキ仕様 JSON の構造。

---

## 1. template.json

`scripts/inspect_template.py` が生成する。手で編集してよいのは `name` / `displayName` /
`roles` / `pageNumber` と、各所の `__*_note` コメントフィールド。それ以外はテンプレートの
実測値なので、テンプレートを更新したら**再解析して上書きする**。

```jsonc
{
  "name": "scalar-2026",                    // テンプレート ID（ファイル名と一致させる）
  "displayName": "Scalar Slide Master 2026",// 人間向け表示名（既定はプレゼンのタイトル）
  "sourceUrl": "https://docs.google.com/presentation/d/…",
  "presentationId": "1shiZp7…",             // 複製元。これが生成の起点
  "generationMode": "copy",

  "pageSize": {
    "widthInches": 10.0,
    "heightInches": 5.625,
    "aspectRatio": "1.778:1"
  },

  // 複製直後に削除するテンプレート同梱スライド。テンプレートを編集したら再解析すること
  "existingSlideIds": ["g3b4087f65e2_0_0", "…"],

  // マスターの colorScheme。dark1/light1/dark2/light2/accent1..6/hyperlink/
  // followed_hyperlink/text1/text2/background1/background2 が入る
  "colors": { "dark1": "#0F172A", "accent5": "#2673BB", "…": "…" },

  // マスターの一覧。マスターが複数あるプレゼンテーションもある（他ファイルから
  // スライドを貼り付けると増える）。既定は 1 つ目（トップレベルの colors /
  // masterDecorations は masters[0] 由来）だが、レイアウトごとにどのマスターに
  // 属するかを layouts.*.masterObjectId がここの objectId で参照する
  "masters": [
    { "objectId": "g1b3a74d17bb_0_0", "displayName": "Scalar Master Slide",
      "colors": { "…": "…" }, "decorations": [{ "…": "…" }] }
  ],

  // ページ番号の描画スタイル。Slides API は SLIDE_NUMBER を生成できないため自前描画する
  "pageNumber": {
    "font": "Arial",
    "fontSize": 7,
    "color": "#666666",
    "align": "END",       // START | CENTER | END
    "startAt": 1
  },

  // マスターが全ページに敷く要素の記録。複製方式では自動継承されるので描画指示ではない
  "masterDecorations": [
    { "type": "image", "objectId": "…", "x": 0.118, "y": 5.197, "w": 1.181, "h": 0.342 }
  ],

  // セマンティックロール → レイアウトキー。推測値なので人間が確認して確定させる
  "roles": {
    "COVER": "TITLE_SLIDE",
    "SECTION": "SLIDE_SUB_SECTION",
    "CONTENT": "DEFAULT_PROPOSAL",
    "TITLE_ONLY": "TITLE_ONLY_PROPOSAL",
    "BLANK": "WHITE",
    "CLOSING": "CLOSE_PAGE"
  },
  // 推測時に見つかった候補一覧。ロール確定後の再確認用に残す
  "roleCandidates": { "CONTENT": ["DEFAULT_PROPOSAL", "DEFAULT_PRESENTATION"] },

  "layouts": {
    "DEFAULT_PROPOSAL": {
      "layoutId": "g1b3a74d17bb_0_19",      // createSlide に渡す ID
      "displayName": "Default - Proposal",
      "placeholders": ["TITLE", "SLIDE_NUMBER", "BODY"],
      // 2カラム/3カラムのレイアウトは BODY を複数持つ: ["TITLE","BODY","BODY#1","BODY#2"]
      // index 0 が "BODY"、以降が "BODY#1"。座標も elements.body / body#1 / body#2 に入る
      "hasPageNumber": true,
      "elements": {                          // 座標はすべてインチ
        "title":       { "x": 0.5, "y": 0.126, "w": 9.0, "h": 0.351 },
        "body":        { "x": 0.5, "y": 0.96,  "w": 9.0, "h": 4.068 },
        "slideNumber": { "x": 9.611, "y": 5.378, "w": 0.222, "h": 0.219 }
      },
      "textStyles": {                        // プレースホルダの既定スタイル（第1階層）
        "title": { "fontFamily": "Noto Sans JP", "fontSize": 20, "color": "theme:DARK1" }
      },
      "decorations": [                       // このレイアウト固有の非プレースホルダ要素
        { "type": "shape", "shapeType": "RECTANGLE", "fill": "theme:ACCENT6",
          "x": 0.367, "y": 0.059, "w": 0.054, "h": 0.398 }
      ]
    }
  }
}
```

### フィールドの読み方

| フィールド | 使いどころ |
|-----------|-----------|
| `placeholders` | デッキ仕様で `title` / `subtitle` / `body` を指定してよいかの判定に使う。ここに無いものを指定するとエラー |
| `elements.body` | 追加の図形を描くときの上端・左右マージンの基準 |
| `elements.slideNumber` | ページ番号の描画位置。幅が狭いレイアウトが多いので、ビルダーは右端を保ったまま最小 0.5in に広げる |
| `textStyles` | テンプレートが想定する文字サイズ。ここより大幅に大きい文字を入れると溢れる |
| `decorations` | 全面サイズの矩形があれば、マスターのフッターを覆っている可能性を疑う |
| `colors` の `theme:XXX` | 色が `theme:ACCENT6` のように出るのはテーマ色参照。実際の hex は `colors.accent6` を引く |

---

## 2. デッキ仕様 JSON

```jsonc
{
  "title": "生成するプレゼンテーションのタイトル",   // --title で上書き可
  "slides": [
    {
      "layout": "CONTENT",        // 必須。ロール名またはレイアウトキー
      "title": "…",               // 任意。レイアウトが TITLE を持つ場合のみ
      "subtitle": "…",            // 任意。レイアウトが SUBTITLE を持つ場合のみ
      "body": ["行1", "行2"],      // 任意。文字列または配列（改行で連結）
      "notes": "スピーカーノート",  // 任意
      // 本文の見た目。slide 単位、または spec の "defaults" で一括指定できる。
      // spaceAbove / spaceBelow はプレースホルダ既定の段落間隔を上書きする。
      // 既定のままだと収容行数が見積もりから大きくずれるテンプレートが多い
      "bodyFontSize": 13,
      "bodyLineSpacing": 115,
      "bodySpaceAbove": 0,
      "bodySpaceBelow": 3
    },
    {
      "layout": "THREE_COLUMN",
      "title": "3つの観点",
      // 複数カラムのレイアウトは bodies で BODY index 0,1,2… に順に流し込む。
      // body と bodies は排他。body は bodies=[body] と等価
      "bodies": [["観点A", "説明"], ["観点B", "説明"], ["観点C", "説明"]]
    },
    {
      "layout": "TITLE_ONLY_PROPOSAL",
      "title": "利用者から台帳まで",
      // 任意。プレースホルダの上に図・画像を重ねる。座標はすべてインチ
      "figures": [
        { "type": "icon_flow", "x": 0.5, "y": 1.3, "w": 9.0, "size": 0.92,
          "items": [["person", "利用者"], ["database", "台帳"]] },
        { "type": "image", "x": 0.5, "y": 3.2, "w": 4.0, "h": 1.6,
          "source": "assets/shot.png", "fit": "cover", "caption": "管理画面" }
      ]
    }
  ]
}
```

### `figures` の書き方

`type` は `scripts/build_deck.py` の `FIGURES` にある名前。値は「位置引数として
渡すキーの並び」と対応していて、それ以外のキーは **camelCase → snake_case** に
直してキーワード引数として渡される（`labelSize` → `label_size`）。

| 系統 | `type` |
|---|---|
| ピクトグラム | `icon` `icon_row` `icon_flow` `icon_grid` |
| 比喩図 | `pyramid` `funnel` `venn` `iceberg` `balance` `steps` `layers` `hub` `matrix` `before_after` `journey` `timeline` |
| ブランドのアイコン | `asset_icon` `asset_icon_row` `asset_icon_flow` `asset_icon_grid` `asset_icon_cards` |
| クラウドアイコン | `cloud_icon` `cloud_icon_row` `cloud_icon_flow` `cloud_icon_grid` `cloud_zone` |
| 構造図 | `band` `cards` `flow` `hbars` `metric` |
| 表・グラフ | `table` `vbars` `vbars_grouped` `vbars_stacked` `linechart` `pie` |
| フレームワーク図 | `posmap` `gantt` `orgchart` `lean_canvas` `nested_circles` `testimonial` |
| イベント案内 | `event_mode_badge` `event_overview` `event_timetable` `event_speakers` `event_access` |
| コード | `code_block` |
| 画像 | `image` `aiImage` |

各 `type` の引数は `references/images.md` / `references/icons.md` /
`references/cloud-icons.md` / `references/charts.md`（表・グラフ）/
`references/patterns.md`（フレームワーク図）/ `references/events.md`（イベント案内）/
`references/code-blocks.md`（コード）、
動く実例は `examples/illustration-gallery.json` /
`examples/icon-gallery.json` / `examples/cloud-architecture.json` /
`examples/charts-demo.json` / `examples/patterns-demo.json` /
`examples/event-announcement.json` / `examples/code-blocks-demo.json`。

**`cloud_zone` と `band` は中身より先に書くこと。** 後ろに書くと矩形が中身を覆う。

`band` は塗りだけの矩形で、図の下地に使う。青一色の表紙・章扉に白いカードを敷いて
その上にピクトグラムを置く、といった用途向け。既定は角丸なので、テンプレート同梱の
図版と揃えたいときは `"kind": "RECTANGLE"` を渡す。

```json
{ "type": "band", "x": 0.5, "y": 2.85, "w": 3.25, "h": 2.34,
  "fill": "#FFFFFF", "kind": "RECTANGLE" },
{ "type": "icon_grid", "x": 0.74, "y": 3.04, "w": 2.77, "cols": 2,
  "size": 0.8, "color": "#2673BB", "items": ["bot", "documents", "database", "lock"] }
```

### `build_deck.py --dry-run` が検証すること

スライドのプレースホルダについて:

- `layout` が `roles` または `layouts` のキーとして解決できるか
- 指定した `title` / `subtitle` に対応するプレースホルダをレイアウトが持つか
- `body` / `bodies` が排他で、`bodies` の要素数がレイアウトの BODY 枠数以下か

`figures` について（**API を一切呼ばずに**）:

- `type` が既知で、必要なキーが揃っているか
- 座標が数値で、宣言した枠がページに収まっているか
- 実際に座標へ展開したうえで、はみ出し・重なり・文字溢れが無いか
  （`audit_bounds` / `audit_connectors` / `audit_overlaps` / `audit_text_fit`）

**画像（`image` / `aiImage`）は実物を取りに行く必要があるため、この検査からは
外れる。** 座標の妥当性だけが見られる。ブランドのアイコン（`asset_icon*`）と
クラウドアイコン（`cloud_icon*`）は**同じ大きさの矩形に置き換えて**検査するので、
アイコン名の誤りも含めて検査が効く。

エラーは全件まとめて報告され、終了コード 1 を返す。図の検査結果は既定では警告
（終了コード 0）で、`--strict` を付けると 1 件でも失敗にする。

---

## 3. 新しいロールを足す

`roles` は単なる別名テーブルなので、標準6ロール以外を自由に追加できる。用途別に系統を持つ
テンプレートでは、系統名をサフィックスにすると仕様が読みやすくなる。

```json
"roles": {
  "CONTENT": "DEFAULT_PROPOSAL",
  "CONTENT_PRESENTATION": "DEFAULT_PRESENTATION",
  "TITLE_ONLY": "TITLE_ONLY_PROPOSAL",
  "TITLE_ONLY_PRESENTATION": "TITLE_ONLY_PRESENTATION"
}
```

ロールを介さず `"layout": "DEFAULT_PRESENTATION"` とレイアウトキーを直接書いてもよい。
ロールの利点は、テンプレートを差し替えても同じデッキ仕様が使い回せることにある。
