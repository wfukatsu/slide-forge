---
name: template-forge
description: >-
  Create and register a brand-new Google Slides master from a design spec — brand
  colors, fonts, logo, footer — without touching the Slides UI, registered as
  templates/<id>.json and ready for google-slides-template to generate against.
  Design input comes from interactive brand tokens, extraction from existing
  material (site / logo / deck), or a bundled preset.
  Use for: 新しいテンプレートを作って, ブランドに合わせたマスターを作成,
  会社カラーのテンプレート, create a new master.
  Not: hand-tuning an existing master's design (Slides UI); PPTX/.potx templates
  (document-skills:pptx); generating decks from a template
  (google-slides-template).
---

*[English](SKILL.md)*

# Template Forge — 新しいスライドテンプレート（マスター）の作成

## 重要事項

- **Slides API はマスター/レイアウトの作成・改名ができない**
  （`references/api-notes.md` §1）。したがって本スキルは*派生*で作る:
  ベースをコピーし、ベースが持つ既存のレイアウトページを再スタイルする。
  使わないベースレイアウトはファイル内に残るが、未登録なので無害である。
  ロール名は `templates/<id>.json` のエイリアス表にのみ存在する。
- **ベースの colorScheme は不変** — すべての色は明示 RGB として書き込む。
  Slides UI のカラーピッカーにはベースのテーマパレットが表示され続けるが、
  それは想定どおりの挙動である（`templates/corporate.json` と同じ）。
- **すべてのコマンドは slide-forge ルートを cwd として実行する** —
  インストール済みプラグインから実行する場合は `${CLAUDE_PLUGIN_ROOT}`、
  ローカルクローンでは `/path/to/slide-forge`。認証と venv はリポジトリ
  ルートで共有される（`config/`、`.venv`）。
- **目視検証なしにテンプレートを引き渡さない。** ロール割り当ては決定的だが、
  帯とプレースホルダの重なり、フォントのレンダリング、コントラストは目で
  しか判断できない: 完了報告の前に、必ずレイアウトカタログ + `slide-qa`
  スキル（Phase 5）を実行する。
- **修正はデザイン仕様に対して行う。** 欠陥を見つけたら仕様を編集し、
  `--replace` で再ビルドする（再ビルド成功後、置き換えられた旧マスターを
  Drive から削除する）。生成済みマスターを Slides UI で直接直してはならない
  — 仕様からフォークしてしまう。
- **フォントは Slides のフォントメニューに存在するものに限る**（Google
  Fonts）。未知の名前は黙ってフォールバックする。既知の安全なフォント:
  Noto Sans JP, Noto Serif JP, M PLUS 1p, Zen Maru Gothic, BIZ UDPGothic
  （日本語）; Montserrat, Roboto, Open Sans, Lato, Source Sans Pro（欧文）。
  それ以外はカタログデッキで確認する。

## クイックリファレンス

| タスク | コマンド |
|------|---------|
| デザイン仕様の検証（オフライン・無料） | `.venv/bin/python scripts/build_template.py --spec design.json --dry-run` |
| ビルド + 自動登録 | `.venv/bin/python scripts/build_template.py --spec design.json [--folder <URL/ID>]` |
| 仕様修正後の再ビルド（json の URL は維持、旧マスターは削除） | `--replace` を付ける |
| blank ではなく登録済みテンプレートから派生 | `--base <template-id>`（または仕様内の `"base"`） |
| 目視確認用のレイアウトカタログ | `.venv/bin/python scripts/layout_sample.py --template templates/<id>.json` |
| プリセット（name/logo/footer 以外が揃った完全仕様） | `templates/presets/{navy-consulting,tech-dark,warm-minimal}.json` |

## デザイン仕様のフォーマット

```jsonc
{
  "name": "acme-2026",                    // [a-z0-9-], becomes templates/<name>.json
  "displayName": "ACME Master Template",
  "base": "blank",                        // "blank" (Google default) | template id | Slides URL/ID
  "brand": {
    "colors": {                           // all #RRGGBB, all 9 required
      "primary": "#0B3D91", "primaryDark": "#062A66", "accent": "#F59E0B",
      "background": "#FFFFFF", "backgroundAlt": "#F5F7FA",
      "textTitle": "#0B1F3A", "textBody": "#1F2937",
      "textMuted": "#666666", "textOnDark": "#FFFFFF"
    },
    "fonts": { "heading": "Montserrat", "body": "Noto Sans JP" },
    "logo": { "source": "assets/acme.png", "onDark": "assets/acme-white.png" },  // optional
    "footer": { "text": "© 2026 ACME Inc.", "fontSize": 7 }                      // optional
  },
  "style": {
    "coverStyle": "band-bottom",          // band-bottom | band-left | minimal
    "sectionStyle": "dark",               // dark (primary bg) | rule (light bg + accent rule)
    "pageNumbers": true
  },
  "derive": {                             // only when base is a registered template
    "colorMap": { "#1E3A5F": "primary" }, // base's explicit RGB -> semantic token
    "deleteObjects": ["<objectId>"]       // brand elements to remove from the base
  }
}
```

標準の 6 ロールは常に生成される: COVER / SECTION / CONTENT /
TITLE_ONLY / BLANK / CLOSING（blank ベースでは、CLOSING は MAIN_POINT
レイアウトを再スタイルしたもの）。

## ワークフロー

### Phase 1: インテイク（AskUserQuestion、interactive-intake.md の作法に従う）

1 ラウンドにまとめて聞く。既に指定済みの項目は飛ばす:

| # | header | 質問 | 選択肢 |
|---|---|---|---|
| 1 | デザイン入力 | デザインは何から決めますか? | 対話で指定(色・フォントを聞く)/ 既存資料から抽出(サイト URL・ロゴ・既存デッキ)/ プリセット(3 種を配色の一言つきで提示) |
| 2 | ベース | どのマスターをベースにしますか? | blank — Google 既定(推奨・既定)/ `list_templates.py` の登録テンプレートから派生 |
| 3 | ロゴ | ロゴ画像はありますか? | ある(パスをもらう。濃色背景用があればそれも)/ ない(文字のみ) |
| 4 | フッター | フッター表記は? | © 表記を入れる(文言をもらう)/ 入れない |

テンプレート名（`[a-z0-9-]`）はブランド/会社名から導出する; 独立した質問
にはせず、アウトラインの中で確認する。

### Phase 2: デザイン仕様の作成

- **対話の場合**: 回答を上記スキーマに当てはめる。作成しながらコントラストを
  確認する: background 上の textBody と primary 上の textOnDark は、いずれも
  ≥ 4.5:1 でなければならない（`colors.py` にヘルパーがある; なければ
  カタログで目視確認する）。
- **抽出はコードではなくエージェントの判断で行う**: サイト URL なら
  WebFetch して CSS 変数やロゴからブランドカラーを読み取る; ロゴファイル
  なら画像を Read して支配的な色（primary）と補助のアクセントを選ぶ;
  既存デッキなら `inspect_template.py <URL>` を実行してカラーレポートを
  取り込む。最も近いプリセットの骨格にマージする。
- **プリセットの場合**: `templates/presets/<preset>.json` をコピーし、
  `name` / `displayName` / `logo` / `footer.text` を埋める。
- パレット（hex + 役割）、フォント、スタイルの選択を 1 つのサマリー
  ブロックにまとめて提示し、ビルド前に承認を得る。

### Phase 3: オフライン検証

```bash
.venv/bin/python scripts/build_template.py --spec out/<name>-design.json --dry-run
```

エラー（色の不足、不正な hex、ロゴファイルの欠落、未知の enum）を修正する。

### Phase 4: ビルドと登録

```bash
.venv/bin/python scripts/drive_folder.py create "<displayName>"   # Drive folder rule
.venv/bin/python scripts/build_template.py --spec out/<name>-design.json --folder <FOLDER_ID>
```

これによりスタイル済みマスターが作成され、決定的なロールと来歴
（`derivedFrom`、日付つきノート）を持つ `templates/<name>.json` が登録され、
ページ番号のジオメトリが注入され、次のステップが表示される。デザイン仕様も
同じフォルダにアップロードする
（`drive_folder.py upload <FOLDER> out/<name>-design.json`）。

### Phase 5: カタログと目視 QA（省略不可）

```bash
.venv/bin/python scripts/layout_sample.py --template templates/<name>.json --folder <FOLDER_ID>
```

その後、カタログデッキに対して **slide-qa** スキルを実行する。標準
チェックリストに加えるテンプレート固有の確認項目:

- [ ] 帯やバーがプレースホルダのテキストに重なっていない
- [ ] 表紙: タイトル/サブタイトルが判読でき、ロゴが引き伸ばされていない（アスペクト比維持）
- [ ] セクション: 背景に対するタイトルのコントラストが ≥ 4.5:1; アクセントの罫線がタイトルの下にある
- [ ] コンテンツ: 本文テキストが本文フォントで表示されている（黙ってフォールバックしていたらフォント名が間違っていた証拠）
- [ ] フッターとページ番号が両方見えていて、二重になっておらず、切れてもいない
- [ ] クロージング: 暗い背景の上でテキストと onDark ロゴが判読できる

### Phase 6: 修正ループ

デザイン仕様を編集 → `--dry-run` → `--replace` で再ビルド（成功後、旧
マスターは Drive から削除され、`templates/<name>.json` はその場で上書き
される）→ 影響のあったレイアウトについて Phase 5 を再実行する。置き換え
られたカタログデッキは Drive から削除する。

### Phase 7: 報告と引き継ぎ

報告内容: マスター URL、カタログデッキ URL、Drive フォルダ URL、
`templates/<name>.json` のパス、パレットのサマリー。デッキの生成は
**google-slides-template** スキルで行うことを明記する: 新しい id は
`list_templates.py` に表示され、`build_deck.py --template templates/<name>.json`
で利用できる。ローカルのサムネイルは `cleanup_qa.py` で削除する。ロゴを
挿入できなかった場合（組織の共有ポリシー）はその旨を伝え、Slides UI での
手動配置を案内する。

## 制約（関係する場面で明示する）

- レイアウトの構成はベースのものに固定される — レイアウトの追加・削除・
  改名はできない。レイアウトの種類を増やしたい場合は、blank ではなく
  より豊富な登録済みテンプレートから派生させる。
- Slides UI のテーマカラーピッカーはベースのパレットのまま
  （colorScheme は API から変更不可）; スタイルはすべて明示 RGB。
- SLIDE_NUMBER プレースホルダは作成できない — ページ番号は本スキルが
  注入するジオメトリを使い、生成時に `build_deck.py` が描画する。
- ロゴの挿入には、画像が一時的に匿名取得可能である必要がある
  （AssetStore がアップロード/共有/クリーンアップを行う）; 組織ポリシー
  によりブロックされることがあり、その場合ビルドは警告を出してロゴなしで
  続行する。
