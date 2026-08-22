---
name: scalar-product-slides
description: >-
  Build Scalar Inc. decks end to end — company introduction, product
  introduction, feature catalog, use cases: confirm deck type, target product and
  audience, research the facts from the official site and developer docs, then
  generate and QA the deck.
  Use for: 製品紹介スライド, 機能紹介スライド, 会社紹介スライド, Scalar 紹介資料,
  ユースケーススライド.
  Not: customer-specific proposals driven by a customer's challenges
  (scalar-proposal-slides); decks about anything other than Scalar
  (google-slides / google-slides-template); PPTX authoring
  (document-skills:pptx).
---

*[English](SKILL.md)*

# Scalar 製品紹介スライド

作業ディレクトリ: slide-forge ルート — インストール済みプラグインから実行する場合は
`${CLAUDE_PLUGIN_ROOT}`、ローカルクローンでは `/path/to/slide-forge`
（以下に書く `cd` のパスはローカルクローンを前提とする）。

## 重要事項

- **前提スキル**: `google-slides-template`（同一リポジトリ） — 認証、共有 venv、
  `scalar-2026` / `scalar-2026-boilerplate` テンプレート、クラウドアイコンを提供する。
  セットアップ・API 制約・描画 API はそちらの SKILL.md に従う。本スキルが持つのは
  Scalar 固有の部分 — デッキ構成、ビルドスクリプト、調査結果 — のみである。
  認証と venv はリポジトリルート（`config/`, `.venv`）で共有する。
- **製品の事実は OKF バンドルから取る。** 機能・エディション・バージョン・
  リリース状況・価格は、Web 調査より先に OKF バンドルを引く — 所在と引用ルールは
  `references/scalar/okf-bundle.ja.md`（バージョンを跨がない、エディションを必ず示す、
  プレビュー状態を明記する）。`pricing/` の数値は公開されている定価なので、
  **定価（税抜）である旨を明示**すれば引用してよい。確定金額としては出さない。
- **事実は調査してから書く。** 会社情報・バージョン・導入事例は
  `references/scalar/research-2026-08.md` を起点とするが、**調査日から 3 か月以上
  経過している場合は再調査する**（下記 Phase 2）。推測で穴を埋めてはならない。
  確認できない項目（資本金など）は載せない。
- **ビジュアル QA は独立スキル（`slide-qa`）であり、生成時に実行有無を選ぶ**
  （Phase 1 で確認する。既定かつ推奨は実行）。実行する場合はそのスキルに従う —
  `scripts/fetch_thumbnails.py` で全ページを取得して検査し、終了後に
  `scripts/cleanup_qa.py` でローカルの QA ファイルを削除する。スキップした場合は
  報告にその旨を明記し、後続として `slide-qa` を提案する。
- **Drive フォルダのルール**（`google-slides-template` と共通）: まずデッキ用の
  Drive フォルダを作成し（`scripts/drive_folder.py create "<title>"`）、その ID を
  出力先フォルダとして渡し、仕様書や図の元データを `drive_folder.py upload` で
  同じフォルダに集約する。フォルダ URL はデッキ URL と併せて報告する。
- **ユーザーが既に持っている既存デッキを更新する場合**（同一 URL のままの
  インプレース編集 — 通常のボイラープレート複製フローではない）は、先に
  `.venv/bin/python scripts/snapshot_version.py <URL>` を実行して編集前の
  リビジョンを記録し、ローカルに PPTX バックアップを取り、編集前にリビジョン ID を
  報告する（`google-slides-template` と共通のルール）。
- **前提が未指定なら、調査より先に `AskUserQuestion` で確定させる**（Phase 1）。
  対話の作法は `references/interactive-intake.md`（セクション 0, 3, 4, 5）に従う。
  本スキル固有なのは質問セットのみである。

## クイックリファレンス

| やること | 使うもの |
|------|-----|
| 前提を対話で確定させる際の作法 | `references/interactive-intake.md`（セクション 0, 3, 4, 5） |
| 会社紹介 + 製品概要 + ユースケースデッキ | `scripts/scalar/build_scalar_intro.py` |
| 機能カタログデッキ（1 機能 = 1 スライド、図解つき） | `scripts/scalar/build_scalar_features.py` |
| 製品機能 / エディション / バージョン / 定価 | `references/scalar/okf-bundle.ja.md` → OKF バンドル |
| 調査済みの事実と落とし穴 | `references/scalar/research-2026-08.md` |
| 実行 | `cd /path/to/slide-forge && .venv/bin/python scripts/scalar/<script>.py [--folder <Drive URL>]` |

両スクリプトは 2 つの CLI フラグを受け付ける: `--folder <Drive フォルダ URL>`
（省略可。省略時はマイドライブ直下にデッキを作成する）と `--dry-run`
（API を呼ばずにオフラインで検証する）。

## Phase 1: デッキ種別と前提を対話で確定させる

調査の**前に**決める。デッキ種別を誤ると調査のやり直しになる（会社紹介と
機能カタログでは必要な事実が異なる）。`references/interactive-intake.md` の
セクション 0（いつ聞くか）、3（アウトライン承認ゲート）、4（生成後の確認）、
5（聞き方の禁止事項）に従う。
**質問は 1 バッチでまとめて聞く。1 問ずつの往復はしない。**

質問セット（本スキル固有。ラウンド 1 の 4 問は一度に聞く）:

| # | header | 質問 | 選択肢 |
|---|---|---|---|
| 1 | デッキ種別 | どのデッキ種別か? | 会社紹介 + 製品概要（`build_scalar_intro.py`、公式ボイラープレートのスライドを再利用） / 機能カタログ（`build_scalar_features.py`、1 機能 = 1 スライド） / ユースケース特化（機能カタログを業種で絞り込み） |
| 2 | 対象製品 | どの製品か? | ScalarDB / ScalarDL / 両方 |
| 3 | 想定読者 | 誰が見るか? | 顧客（初回商談・営業） / エンジニア（評価・PoC） / 経営層（投資判断） / パートナー（販売支援） |
| 4 | 調査 | 事実の鮮度はどこまで必要か? | `references/scalar/research-2026-08.md` をそのまま使う / 再調査する（Phase 2 を実行） |

- **Q4 を勝手に決めてはならない。** 調査日から 3 か月以上経過している場合は
  「再調査する」を推奨として先頭に置き、`description` に理由（調査日と経過月数）を
  明記する。
- この 4 問で 1 ラウンドとする。未指定なら、出力先 Drive フォルダ、表紙の日付、
  言語（日本語 / 英語）、生成後にビジュアル QA を実行するか（既定かつ推奨は実行。
  スキップするとデッキは未検証のまま納品される）を 2 ラウンド目でまとめて聞く
  （`--folder` なしの場合、デッキはマイドライブ直下に作成される）。
- **聞いてはならないこと**: 図の構成方法、座標、色、どの機能にどの図を使うか。
  これらは `FEATURES_DB` / `FEATURES_DL` とデザイン規約で固定されている。

種別と対象が確定したら、**スライドアウトライン（ページ数と各スライドの見出し）を
提示し、生成前に承認を得る**。`build_plan()` を書き換える前にこのゲートを通す。

## Phase 2: 調査

`references/scalar/research-2026-08.md` を読み、十分新しければそのまま使う。
古い場合や新しい情報が必要な場合は、調査エージェントを**並列で**起動する:

1. 会社情報・ニュース: https://scalar-labs.com/ja/（会社情報 / ニュース）、
   プレスリリース検索
2. 製品技術: https://developers.scalar-labs.com/ → 実際のドキュメントは
   https://scalardb.scalar-labs.com/docs/latest/ と
   https://scalardl.scalar-labs.com/docs/latest/ にある
   （features / overview / design / releases から入り、個別の機能ページを辿る）
3. ユースケース・導入事例: ニュースフィードの事例カテゴリ + Web 検索
   （専用の事例ページは存在しない）

エージェントには必ず指示する: 出典 URL を明記する、不明な点は不明と明示する、
推測しない。結果で `references/scalar/` を更新し、調査日を書き換える。
**スライド化する前に、落とし穴リスト（references ファイルの末尾）を毎回確認する。**

## Phase 3: デッキ種別ごとの作り方

種別は Phase 1 で確定済み。以下はそれを作るための実装メモである。

### A. 会社紹介デッキ（`scripts/scalar/build_scalar_intro.py`）

`templates/scalar-2026-boilerplate.json` を `keep_existing=True` で複製し、
**公式ボイラープレートのスライドを残したまま**（会社概要 VISION、経営陣、製品概要、
顧客ロゴ、トヨタ / 放送局の導入事例、クロージング）、調査に基づく生成スライドを
その間に挿入する。経営陣の写真や顧客ロゴは再現できないため、必ずこの方式を取る。

- 同梱 12 スライドのうち、プレースホルダーの表紙（位置 1）とサブセクション見出し
  （位置 10）を削除する
- 表紙の文言は `replaceAllText` で置換する（"<Presentation Title>" など）
- 生成スライドは `add_slide(..., index=最終位置)` で挿入する。
  **最終的なページ順を 1 つのリスト（`build_plan()`）で宣言し、昇順に挿入する —
  これで insertionIndex の計算が単純になる**
- ページ番号: 同梱スライドの SLIDE_NUMBER は自動で追従する。生成スライドは
  `draw_page_number()`（1 スライド用）で最終位置の番号を描く。
  `add_page_numbers()` は使わない — 連番を前提としており、挿入方式とは
  相性が悪い

### B. 機能カタログデッキ（`scripts/scalar/build_scalar_features.py`）

`templates/scalar-2026.json` から生成する「1 機能 = 1 スライド」のカタログ。
機能スライドはすべて同一レイアウトを共有する:

- 左（x 0.5–5.75）: **図解**（機能ごとの `fig_*` 関数）+ 下端に 1 行キャプション
- 右（x 6.0–9.5）: **機能概要**カード（目安 200 字以内）
- 下部: **ユースケース**行（2 列の箇条書き、各項目は目安 28 字以内）+
  **強み**帯（目安 100 字以内）
- 右上: エディション、導入バージョン、プレビュー状態
- スピーカーノート: 出典 URL と制限事項

機能データは dict のリスト `FEATURES_DB` / `FEATURES_DL`
（`title` / `figure` / `overview` / `usecases` / `value` / `edition` / `notes`）にある。
機能の追加・削除・文言変更はここを編集する。各セクションの冒頭には 2×2 の
機能マップを置く。

### デザイン規約（両方式共通）

- **直線のアクセントバーを持つ矩形は角丸にしない**（`RECTANGLE`）。バーのない
  チップや帯は角丸でよい（google-slides-template の SKILL.md と同じルール）
- タイトルはアクションタイトル（「何を主張できるか」）。
  「機能名 — 一言の価値」の形が収まりがよい
- 図解は `illustrations` のピクトグラム、`_pill`（角丸チップ）、`cloud_zone`、
  `_anchored` 矢印で構成する。公式クラウドアイコンは改変してはならない

## Phase 4: 生成と QA

```bash
cd /path/to/slide-forge
.venv/bin/python scripts/scalar/build_scalar_features.py --dry-run   # audits only, no API
.venv/bin/python scripts/scalar/build_scalar_features.py [--folder <URL>]
```

1. スクリプトはコミット前に全スライドで `audit_bounds / audit_connectors /
   audit_overlaps / audit_text_fit` を実行し、"audit:" 行を出力する（GSLIDES_LANG=ja では "検査:"）。
   **いずれかの検査が発火したら、仕様を直して再ビルドする**（パッチ修正より速い）。
   再ビルドの前に旧デッキを Drive から削除する
2. **ユーザーがビジュアル QA を選んだ場合（既定）**、`slide-qa` スキルを実行する:
   `scripts/fetch_thumbnails.py` で全ページを取得し、Read で検査し（はみ出し、
   重なり、レイアウト選択ミス）、終了後に `scripts/cleanup_qa.py` でローカルの
   QA ファイルを削除する。QA をスキップした場合は報告にその旨を明記し、後続として
   `slide-qa` を提案する
3. **再ビルドすると URL が変わる。** 新しい URL をユーザーに伝え、旧デッキの扱い
   （削除）を明示する
4. 結果を提示する前に自分で QA を通す。改善の余地があれば `AskUserQuestion` で
   提案する: 「確定 / 文言調整 / 図の変更 / 機能の追加・削除」
   （`interactive-intake.md` セクション 4）

## ファイル構成

| パス | 役割 |
|------|------|
| `scripts/scalar/build_scalar_intro.py` | 会社紹介デッキビルダー（ボイラープレート + 挿入方式。27 スライドの実例） |
| `scripts/scalar/build_scalar_features.py` | 機能カタログデッキビルダー（図解つき 24 機能。31 スライドの実例） |
| `templates/scalar-2026.json` | Scalar 2026 テンプレート（生成デッキ用） |
| `templates/scalar-2026-boilerplate.json` | Scalar 2026 ボイラープレートテンプレート（公式同梱スライド） |
| `assets/scalar/{logos,product-logos,pictograms}` | ブランド素材（会社・製品ロゴ、ピクトグラム） |
| `references/scalar/okf-bundle.ja.md` | OKF バンドルの所在と、製品事実・価格の引用ルール |
| `references/scalar/research-2026-08.md` | 調査済みの事実（会社・製品・事例）とスライド作成の落とし穴 6 件 |

スクリプトは「そのまま再実行できる実例」であり、構成を変えるときはこの
2 スクリプトを編集するのが最短経路である。google-slides-template 由来の
アーキテクチャ図の実例 `examples/scalardb-architecture.py` /
`examples/scalardl-architecture.py` も併用できる。
