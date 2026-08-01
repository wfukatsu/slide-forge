# テーマ管理ガイド

テーマの作成・編集・削除・切替に関するワークフローと `theme.json` スキーマの仕様。

---

## 1. テーマ一覧

| テーマ ID | 表示名 | プライマリ | アクセント | 生成方式 | 用途 |
|-----------|--------|----------|----------|---------|------|
| `scalar` | Scalar Slide Master 2026 (v2.0.0) | `#2673BB` | `#0985FD` | `copy` | Scalar 社公式。ScalarDB / ScalarDL 営業・技術資料 |
| `aixdevops` | AI x DevOps Study Theme | `#2673BB` | `#63C045` | `copy` | AI x DevOps Study 勉強会・テック系イベント |
| `corporate` | Corporate Master Slide | `#1E3A5F` | `#0D9488` | `copy` | 汎用コーポレート。社外向け一般資料・提案書 |

> **`aixdevops` は Scalar との共同ブランド。** AIxDevOps は独立したブランドではなく `SCALAR | AIxDevOps` のロックアップを持つ共同ブランドで、地色は Scalar ブルー `#2673BB`（表紙・中扉の斜めデザイン）、アクセントはロックアップの緑 `#63C045`。配色は 2026-07-29 に実マスター（`13QHfp9p…`）準拠へ変更した。それ以前は紫 `#5B21B6` / シアン `#06B6D4` の独自パレットだったが、マスターと食い違っていた。旧パレットは `theme.json.bak-20260729` にある。
>
> アクセントの緑 `#63C045` は白背景で 2.29:1 と WCAG AA を大きく下回る。**本文テキストに使わないこと**（装飾・図形の塗り専用）。

> **`corporate` は `aixdevops` テンプレートからの派生**（2026-07-29 生成）。AIxDevOps ワードマーク・区切り線・元デッキ固有画像を削除し、地色を `#1E3A5F`、カラム区切り線を `#BFDBFE` に上書きしてある。SCALAR ロゴと著作権表記は、Scalar の汎用社外向けテンプレートという位置づけのため残している。ブランド中立にしたい場合はロゴ画像も削除すること。
>
> 3テーマとも、かつては scalar 旧マスターの `layoutId` がコピーされたまま残っていた（どのプレゼンテーションにも存在しない無効な値）。2026-07-29 に除去し、実マスターの ID を設定した。旧定義は各 `theme.json.bak-*` にある。
>
> `CONTENT_ACCENT` と `CLOSING` は `aixdevops` / `corporate` のマスターに該当レイアウトが無いため `layoutId` が null のまま。

**生成方式**: `copy` はマスタープレゼンテーションを Drive API で複製してからスライドを積む方式（`master.generationMode: "copy"`）。**実装は `google-slides-template` スキルにあり、本スキルには無い** — `~/.claude/skills/google-slides-template/scripts/build-deck.py` に `templates/scalar-2026.json` を渡して使う。`build` は空プレゼンテーションを `presentations().create()` で作り、BLANK レイアウトから全て描画する従来方式で、本スキルのコンポーザーはこちらを使う。

---

## 2. テーマの作成

### 2.1 手順

1. **テーマ ID を決定**: 英小文字・ハイフンのみ（例: `fintech-event`）
2. **既存テーマをコピー**:

```bash
SKILL_DIR=~/.claude/skills/google-slides
THEME_ID=<新テーマID>

# テンプレートからコピー
cp -r "$SKILL_DIR/templates/corporate" "$SKILL_DIR/templates/$THEME_ID"

# アセットディレクトリ作成
mkdir -p "$SKILL_DIR/assets/$THEME_ID"/{logos,product-logos,icons}
```

3. **theme.json を編集**: 以下のフィールドを更新

| フィールド | 説明 | 例 |
|-----------|------|-----|
| `name` | テーマ ID（ディレクトリ名と一致） | `"fintech-event"` |
| `displayName` | 表示名 | `"FinTech Event Theme"` |
| `description` | テーマの説明 | `"金融テック向けイベントテーマ"` |
| `source` | マスターテンプレートの URL（後述） | Google Slides URL or `null` |
| `colors.*` | カラーパレット（セクション 4 参照） | — |
| `fonts.*` | フォント設定 | — |
| `layouts.*.layoutId` | マスターテンプレートから取得（後述） | — |
| `masterFooter.copyright.text` | 著作権テキスト | `"(C) 2026 Your Corp."` |

4. **マスターテンプレートプレゼンテーションの作成**（推奨）:

Google Slides API はテーマ・マスタースライドの作成・編集をサポートしないため、Google Slides UI でテンプレートプレゼンテーションを作成する。

   a. Google Slides で新規プレゼンテーションを作成
   b. スライドサイズを 16:9（ワイドスクリーン）に設定
   c. マスタースライドエディタでレイアウトを定義（COVER, SECTION, CONTENT, CLOSING 等）
   d. ブランドカラー・フォントを設定
   e. プレゼンテーション URL を `source` フィールドに記録
   f. 各レイアウトの `layoutId` を取得して `layouts.*.layoutId` に記録

5. **layoutId の取得方法**:

```python
# マスターテンプレートの layoutId を取得するスクリプト
from googleapiclient.discovery import build
# ... 認証省略 ...
pres = slides_service.presentations().get(
    presentationId="<PRESENTATION_ID>",
    fields="layouts(layoutProperties.displayName,objectId)"
).execute()
for layout in pres.get("layouts", []):
    print(f"{layout['layoutProperties']['displayName']}: {layout['objectId']}")
```

6. **アセットの配置**: ロゴ・アイコン等を `assets/<THEME_ID>/` に配置

### 2.2 マスターテンプレートなしの運用

`source` を `null` に設定すると、BLANK レイアウトのみで全スライドを構築する。マスターテンプレートの恩恵（既定の背景・装飾要素）は得られないが、コンポジットパターン関数（`master-registry.md` 参照）で同等のデザインを実現できる。

```json
{
  "source": null,
  "layouts": {
    "COVER": { "layoutId": null, "background": "primary", ... },
    "CONTENT": { "layoutId": null, "background": "background", ... }
  }
}
```

`layoutId` が `null` のレイアウトでは `BLANK` が自動的に使用される。

---

## 3. テーマの編集

### 3.1 カラーパレットの変更

`colors` セクションの値を変更する。変更時は以下を確認:

- **WCAG AA コントラスト比**: テキスト色と背景色の組み合わせが 4.5:1 以上であること
- **`cautionDark`**: `#BE9000`（`caution`）は白背景で 2.8:1 しかないため、テキストには `cautionDark` を使用
- **チャートカラー**: `chart1`-`chart5` は互いに区別可能な色相にする

コントラスト比の簡易確認:

```python
def contrast_ratio(hex1, hex2):
    """2つの hex カラーの WCAG コントラスト比を計算"""
    def luminance(hex_color):
        r, g, b = int(hex_color[1:3], 16)/255, int(hex_color[3:5], 16)/255, int(hex_color[5:7], 16)/255
        r, g, b = [(c/12.92 if c <= 0.03928 else ((c+0.055)/1.055)**2.4) for c in (r, g, b)]
        return 0.2126*r + 0.7152*g + 0.0722*b
    l1, l2 = luminance(hex1), luminance(hex2)
    return (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)
```

### 3.2 フォントの変更

`fonts` セクションを更新。Google Slides で利用可能なフォントであること。

日本語フォント候補: `Noto Sans JP`, `M PLUS 1p`, `M PLUS Rounded 1c`, `Kosugi Maru`, `Sawarabi Gothic`

### 3.3 レイアウト座標の変更

`layouts.*.elements` の座標（インチ単位）を変更する場合:

- ページサイズ: 10.0" x 5.625"（16:9）
- 要素がページ境界を超えないこと
- `contentTop` ～ `contentBottom` の範囲内にコンテンツが収まること
- フッター要素（`logo`, `copyright`, `slideNumber`）は Y=5.2" 付近に配置

---

## 4. テーマの削除

```bash
SKILL_DIR=~/.claude/skills/google-slides
THEME_ID=<削除するテーマID>

# テンプレートとアセットを削除
rm -rf "$SKILL_DIR/templates/$THEME_ID"
rm -rf "$SKILL_DIR/assets/$THEME_ID"
```

**注意**: `scalar`, `aixdevops`, `corporate` はビルトインテーマ。削除する場合は影響を確認すること。

---

## 5. テーマの切替

### 5.1 コード生成時の切替

Phase 1（テーマ読み込み）でテーマを選択する:

1. ユーザーにテーマを確認（デフォルト: `scalar`）
2. `templates/<theme>/theme.json` を読み込む
3. C クラス（色定数）・L クラス（レイアウト定数）を展開

### 5.2 実行時パラメータでの切替

生成スクリプトの冒頭でテーマパスを変更:

```python
THEME = "aixdevops"  # scalar | aixdevops | corporate | <custom>
theme = json.load(open(f"templates/{THEME}/theme.json"))
```

### 5.3 デッキパターンでのデフォルトテーマ

| デッキパターン | 推奨テーマ |
|--------------|----------|
| `initial_sales` | `scalar` |
| `technical_deep_dive` | `scalar` |
| `executive_briefing` | `corporate` |
| `use_case_specific` | `scalar` |
| `partner_enablement` | `corporate` |

---

## 6. theme.json スキーマリファレンス

### トップレベル構造

```json
{
  "name": "string (required) — テーマ ID。ディレクトリ名と一致",
  "displayName": "string (required) — 表示名",
  "version": "string — セマンティックバージョン",
  "description": "string — テーマの説明",
  "source": "string|null — マスターテンプレートプレゼンテーション URL",

  "pageSize": { "/* セクション 6.1 */" },
  "colors": { "/* セクション 6.2 */" },
  "fonts": { "/* セクション 6.3 */" },
  "fontSizes": { "/* セクション 6.4 */" },
  "fontWeights": { "/* セクション 6.5 */" },
  "lineSpacing": { "/* セクション 6.6 */" },
  "layouts": { "/* セクション 6.7 */" },
  "masterFooter": { "/* セクション 6.8 */" },
  "columnLayouts": { "/* セクション 6.9 */" },
  "borders": { "/* セクション 6.10 */" },
  "tableStyle": { "/* セクション 6.11 */" },
  "pptxScheme": { "/* セクション 6.12 */" },
  "pptxFonts": { "/* セクション 6.13 */" }
}
```

### 6.1 pageSize

```json
{
  "width": 9144000,
  "height": 5143500,
  "widthInches": 10.0,
  "heightInches": 5.625,
  "aspectRatio": "16:9",
  "unit": "EMU"
}
```

固定値。16:9 アスペクト比。Google Slides の EMU 表現。

### 6.2 colors

| キー | 必須 | 説明 |
|------|:----:|------|
| `dark1`, `light1`, `dark2`, `light2` | Yes | テーマ基本色 |
| `accent1`-`accent6` | Yes | アクセントカラー 6 色 |
| `primary` | Yes | ブランドプライマリカラー |
| `primaryDark` | Yes | プライマリの暗色バリエーション |
| `accent` | Yes | セマンティックアクセント |
| `success` | Yes | 成功・肯定を示す色 |
| `textPrimary` | Yes | 本文テキスト色 |
| `textTitle` | Yes | タイトルテキスト色 |
| `textOnDark` | Yes | 暗色背景上のテキスト色 |
| `textMuted` | Yes | 控えめなテキスト色（WCAG AA 準拠要） |
| `textSecondary` | Yes | 二次テキスト色 |
| `background` | Yes | 背景色 |
| `backgroundAlt` | Yes | 代替背景色 |
| `surfaceLight` | Yes | 明るいサーフェス色 |
| `border` | Yes | ボーダー色 |
| `calloutBg`, `calloutBorder` | Yes | コールアウト背景・ボーダー |
| `cautionDark` | Yes | 注意色（テキスト用、高コントラスト） |
| `tableHeader`, `tableHeaderText` | Yes | テーブルヘッダー |
| `tableDataCell`, `tableRowHeader`, `tableRowAlt` | Yes | テーブルセル |
| `highlightYellow`, `successGreen`, `successGreenDark`, `alertRed`, `cautionYellow` | Yes | ステータスカラー |
| `chart1`-`chart5` | Yes | チャート用カラーパレット |

### 6.3 fonts

| キー | 必須 | 説明 | デフォルト |
|------|:----:|------|----------|
| `fontFaceTitle` | Yes | タイトル用フォント | `"Noto Sans JP"` |
| `fontFaceBody` | Yes | 本文用フォント | `"M PLUS 1p"` |
| `fontFaceEn` | Yes | 英語テキスト用フォント | `"Arial"` |
| `fontFaceMono` | Yes | 等幅フォント | `"Courier New"` |
| `fontFaceAccent` | Yes | アクセント用フォント | `"Century Gothic"` |
| `fontFallback` | Yes | フォールバック | `"M PLUS 1p, Arial"` |

### 6.4 fontSizes

単位: ポイント (pt)。

| キー | 値 | 用途 |
|------|---:|------|
| `coverTitle` | 30 | 表紙タイトル |
| `contentTitle` | 26 | コンテンツスライドタイトル |
| `sectionTitle` | 24 | セクション区切りタイトル |
| `masterTitle` | 20 | マスターレベルタイトル |
| `bodyLevel1`-`bodyLevel5` | 16-8 | 本文レベル別 |
| `slideNumber` | 7 | ページ番号 |
| `copyright` | 7 | 著作権表示 |

### 6.4b master（マスター複製方式のテーマのみ）

```json
"master": {
  "presentationId": "string — マスタープレゼンテーションの ID",
  "presentationTitle": "string — マスターのタイトル（人間向け）",
  "masterObjectId": "string — マスターページの objectId",
  "generationMode": "copy — Drive API で複製してから createSlide する",
  "sampleSlideIds": ["string — 複製直後に削除するサンプルスライドの objectId"],
  "previousSource": "string|null — 旧マスターの URL（移行履歴用）"
}
```

`generationMode` が `"copy"` のテーマで実際に生成するときは、`google-slides-template` スキルの
`scripts/build-deck.py` に対応する `templates/<id>.json` を渡す。本スキル側の `master` ブロックは、
どのマスターに紐づくテーマかを記録するメタデータとして持つ。

### 既存テーマを複製方式に対応させる手順

`master.presentationId` が null のテーマ（`aixdevops` / `corporate`）を対応させる場合:

1. **マスターとなるプレゼンテーションを用意する。** Slides API はマスター/レイアウトを
   新規作成できないので、ここだけは Google Slides の UI での作業か、既存プレゼンの流用が要る。
   既にそのテーマで使っている資料があれば、それをマスターにするのが最も早い。
2. **解析して登録する。**

   ```bash
   cd ~/.claude/skills/google-slides-template
   .venv/bin/python scripts/inspect-template.py "<マスターURL>" \
       --emit templates/<theme>.json --name <theme> --thumbnails out/layouts
   ```

3. **`roles` を目視で確認・修正する**（`google-slides-template/SKILL.md` Phase 1）。
4. **本スキルの theme.json を更新する。**
   - `source` … マスターの URL
   - `master.presentationId` / `presentationTitle` / `masterObjectId` / `sampleSlideIds`
   - `master.generationMode` … `"copy"`
   - `master.counterpartTemplate` … 手順 2 で作った JSON のパス
   - `layouts.*.layoutId` … 解析結果の実 ID
   - `colors` … マスターの colorScheme と食い違っていれば合わせる
5. 生成して視覚確認する（`build-deck.py` → `fetch-thumbnails.py`）。

> **配色違いの派生マスターを作る場合**: 既存マスターを複製して図形の色を塗り替えることは
> API で可能（実測確認済み）。ただし colorScheme 自体は変更できないため、`theme:ACCENT6` の
> ようなテーマ色参照は元の配色で解決される。テーマ色を参照している要素をすべて明示 RGB で
> 上書きする必要がある。詳細は `google-slides-template/references/api-notes.md` セクション 1。

マスター側でスライドやレイアウトを増減させた場合は、両方を更新すること:

1. `google-slides-template` で再解析 — `scripts/inspect-template.py <URL> --emit templates/<id>.json`
2. 本スキルの `master.sampleSlideIds` と `layouts.*.layoutId` を突き合わせて更新

`sampleSlideIds` / `existingSlideIds` が実際のマスターと食い違うと、複製時に不要なスライドが
残るか警告が出る。

### 6.5-6.6 fontWeights / lineSpacing

```json
"fontWeights": { "title": "bold", "body": "normal" },
"lineSpacing": { "title": 100, "body": 115, "bodyJapanese": 185 }
```

### 6.7 layouts

レイアウト定義。各レイアウトの構造:

```json
{
  "id": "string — レイアウト表示名",
  "layoutId": "string|null — Google Slides API の layoutObjectId",
  "family": "string — common|proposal|presentation。レイアウト系統",
  "aliasOf": "string — オプション。別キーと同一レイアウトの場合の参照先",
  "background": "string — colors キーまたは hex",
  "hasFooter": "boolean",
  "hasPageNumber": "boolean",
  "hasLogo": "boolean",
  "logoPosition": "string — top-right|top-left|footer-left|center",
  "placeholders": ["TITLE", "SUBTITLE", "BODY", "SLIDE_NUMBER"],
  "elements": {
    "title": { "x": 0.0, "y": 0.0, "w": 0.0, "h": 0.0 },
    "...": "..."
  },
  "decorative": { "/* オプション。背景バンド等 */" }
}
```

### 6.8-6.13 その他セクション

`masterFooter`, `columnLayouts`, `borders`, `tableStyle` は共通レイアウトパラメータ。`pptxScheme`, `pptxFonts` は PPTX エクスポート互換用。

---

## 7. 新テーマ作成チェックリスト

- [ ] テーマ ID を決定（英小文字・ハイフンのみ）
- [ ] `templates/<id>/theme.json` を作成
- [ ] `name` と `displayName` を設定
- [ ] カラーパレットを定義（`primary`, `accent` 必須）
- [ ] WCAG AA コントラスト比を確認（テキスト色 vs 背景色）
- [ ] フォントを設定（Google Slides で利用可能なフォント）
- [ ] `assets/<id>/` ディレクトリを作成
- [ ] ロゴファイルを `assets/<id>/logos/` に配置
- [ ] マスターテンプレートプレゼンテーションを作成（推奨）
- [ ] `layoutId` を取得して記録
- [ ] `masterFooter.copyright.text` を設定
- [ ] テスト生成を実行して確認
