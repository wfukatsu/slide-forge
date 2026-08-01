---
name: scalar-product-slides
description: >-
  株式会社Scalar の会社紹介・製品紹介・機能紹介・ユースケースの Google Slides を、
  公式サイト/developers ドキュメントの調査から生成・QA まで一貫して作る。
  google-slides-template スキル(scalar-2026 テンプレート)の上に載る Scalar 専用ワークフロー。
  トリガー: "製品紹介スライドを作って", "機能紹介スライド", "会社紹介スライド",
  "Scalar 紹介資料", "ユースケーススライド", "scalar-product-slides",
  "ScalarDB/ScalarDL の紹介資料を作って"。
  対象外: PPTX 生成(scalar-slides / document-skills:pptx)、Scalar 以外の内容のスライド。
---

# Scalar 製品紹介スライド生成

## Important

- **前提スキル**: `google-slides-template`(認証・共有 venv・`scalar-2026` / `scalar-2026-boilerplate`
  テンプレート・クラウドアイコン)。セットアップ手順・API の制約・作図 API はすべてそちらの
  SKILL.md に従う。本スキルは「Scalar 紹介資料に特化した構成・生成スクリプト・調査知見」を持つ。
- **事実は調査してから書く。** 会社情報・バージョン・事例は `references/research-2026-08.md` が
  出発点だが、**調査日から 3 か月以上経過していたら再調査**(下記 Phase 1)。推測で埋めない。
  不明な項目(資本金など)は載せない。
- **視覚 QA を省略しない**(`fetch-thumbnails.py` で全ページ目視)。

## Quick Reference

| やること | 使うもの |
|---------|---------|
| 会社紹介 + 製品概要 + ユースケースのデッキ | `scripts/build_scalar_intro.py` |
| 機能紹介デッキ(1機能=1スライド・図解付き) | `scripts/build_scalar_features.py` |
| 調査済みの事実・落とし穴 | `references/research-2026-08.md` |
| 実行 | `cd ~/.claude/skills/google-slides-template && .venv/bin/python <script> [--folder <Drive URL>]` |

## Phase 1: 調査

`references/research-2026-08.md` を読み、鮮度が十分ならそのまま使う。古い場合や
新しい情報が要る場合は、調査エージェントを**並行で**出す:

1. 会社情報・ニュース: https://scalar-labs.com/ja/ (company / news)、プレスリリース検索
2. 製品技術: https://developers.scalar-labs.com/ → 実体は
   https://scalardb.scalar-labs.com/docs/latest/ と https://scalardl.scalar-labs.com/docs/latest/
   (features / overview / design / releases を起点に個別機能ページへ)
3. ユースケース・事例: ニュースの事例カテゴリ + 検索(専用の事例ページは存在しない)

エージェントには「出典 URL 付き・不明は不明と明記・推測禁止」を必ず指示する。
調査結果で `references/` を更新し、調査日を書き換える。
**落とし穴リスト(references 末尾)は毎回スライド化の前に確認すること。**

## Phase 2: デッキの型を選ぶ

### A. 会社紹介デッキ(`build_scalar_intro.py`)

`scalar-2026-boilerplate` を `keep_existing=True` で複製し、**公式の定型スライド
(会社概要 VISION・役員構成・製品概要・導入顧客ロゴ・トヨタ/放送局事例・クロージング)を
活かして**、調査に基づく生成スライドを挿入する方式。役員写真・顧客ロゴは再現できないので、
必ずこの方式を使う。

- 同梱 12 枚のうちプレースホルダ表紙(位置 1)とサブセクション見出し(位置 10)は削除する
- 表紙の文言は `replaceAllText` で置換("<Presentation Title>" など)
- 生成スライドは `add_slide(..., index=最終位置)` で挿入。**最終ページ順を 1 つのリスト
  (`build_plan()`)で宣言し、昇順に挿入すれば insertionIndex の計算が単純になる**
- ページ番号: 同梱スライドは SLIDE_NUMBER が自動追従する。生成スライドは
  `draw_page_number()`(単票版)で最終位置の番号を描く。`add_page_numbers()` は
  挿入方式とは相性が悪い(連番前提)ので使わない

### B. 機能紹介デッキ(`build_scalar_features.py`)

`scalar-2026` から生成する「1機能=1スライド」のカタログ。全機能スライドが共通レイアウト:

- 左(x 0.5–5.75): **図解**(機能ごとの `fig_*` 関数)+ 下端にキャプション 1 行
- 右(x 6.0–9.5): **機能概要**カード(≦ 200 字目安)
- 下段: **ユースケース**行(箇条書きを 2 カラム、各 ≦ 28 字目安)+
  **特長** 帯(≦ 100 字目安)
- 右上: エディション・導入バージョン・プレビュー状態
- スピーカーノート: 出典 URL と制限事項

機能データは `FEATURES_DB` / `FEATURES_DL` の dict リスト
(`title` / `figure` / `overview` / `usecases` / `value` / `edition` / `notes`)。
機能の増減・文言修正はここを編集する。各セクション冒頭に 2×2 の機能マップを置く。

### デザイン規約(両方式共通)

- **直線のアクセントバーを重ねる矩形は角を丸めない**(`RECTANGLE`)。バーの無い
  チップ・帯は角丸でよい(google-slides-template SKILL.md の規約と同じ)
- タイトルはアクションタイトル(「何が言えるか」)。「機能名 — 価値の一言」の形が収まりがよい
- 図解は `illustrations` のピクトグラム + `_pill`(角丸チップ)+ `cloud_zone` +
  `_anchored` 矢印で組む。クラウド公式アイコンは改変禁止

## Phase 3: 生成と QA

```bash
cd ~/.claude/skills/google-slides-template
.venv/bin/python ~/.claude/skills/scalar-product-slides/scripts/build_scalar_features.py [--folder <URL>]
```

1. スクリプトは commit 前に `audit_bounds / audit_connectors / audit_overlaps / audit_text_fit`
   を全スライドで実行し「検査:」行を出す。**検査が出たら仕様を直して作り直す**
   (部分修正より速い)。作り直す前に旧デッキを Drive から削除する
2. `fetch-thumbnails.py` で全ページ取得し、Read で目視(はみ出し・重なり・レイアウト取り違え)
3. **作り直すと URL が変わる**。ユーザーに新 URL を伝え、旧デッキの扱い(削除)を明示する

## ファイル構成

| パス | 役割 |
|------|------|
| `scripts/build_scalar_intro.py` | 会社紹介デッキ生成(boilerplate + 挿入方式、27 枚構成の実例) |
| `scripts/build_scalar_features.py` | 機能紹介デッキ生成(図解付き 24 機能、31 枚構成の実例) |
| `references/research-2026-08.md` | 調査済みの事実(会社・製品・事例)と、スライド化の落とし穴 6 項目 |

スクリプトは「そのまま再実行できる実例」であり、構成を変えるときも
この 2 本を出発点に編集するのが最短。google-slides-template 側の
`examples/scalardb-architecture.py` / `scalardl-architecture.py`(構成図の実例)も併用できる。
