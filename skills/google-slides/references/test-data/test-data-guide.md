# テストデータ

Google Slides スキルのスライド生成テスト用サンプル `slide_content.json` ファイル集。

5つのデッキパターンのそれぞれに対応するサンプルデータを用意し、36種類のスライドタイプを完全にカバーしている。

---

## ファイル一覧

| ファイル名 | デッキパターン | テーマ | スライド数 | 対象シナリオ |
|-----------|:----------:|:-----:|:--------:|-----------|
| `initial-sales-scalar.json` | initial_sales (P1) | scalar | 16枚 | ScalarDB 初回営業（金融業界） |
| `technical-deep-dive-scalar.json` | technical_deep_dive (P2) | scalar | 23枚 | ScalarDB 技術詳細プレゼン |
| `executive-briefing-corporate.json` | executive_briefing (P3) | corporate | 12枚 | ScalarDB 経営層向けブリーフィング |
| `use-case-specific-scalar.json` | use_case_specific (P4) | scalar | 22枚 | ScalarDB × 小売業界ユースケース |
| `partner-enablement-corporate.json` | partner_enablement (P5) | corporate | 20枚 | ScalarDB パートナー向け販売支援 |

---

## 36タイプ カバレッジ表

全36スライドタイプが、5つのテストデータ合計で最低1回は使用されている。

### basic (6)

| タイプ | P1 | P2 | P3 | P4 | P5 |
|--------|:--:|:--:|:--:|:--:|:--:|
| `title` | #0 | #0 | #0 | #0 | #0 |
| `agenda` | #1 | #1 | — | #1 | #1 |
| `section_divider` | — | #2,#6,#10,#14,#17 | — | #2,#5,#10,#14 | #2,#7,#11 |
| `summary` | #14 | #20 | #10 | #20 | #18 |
| `closing` | #15 | #21 | #11 | #21 | #19 |
| `appendix` | — | #22 | — | — | — |

### content (9)

| タイプ | P1 | P2 | P3 | P4 | P5 |
|--------|:--:|:--:|:--:|:--:|:--:|
| `text_bullets` | #2 | — | #1 | #4 | — |
| `columns` | — | — | — | #16 | — |
| `image_text` | — | — | — | — | #17 |
| `chart` | — | — | #9 | — | — |
| `table` | — | — | — | #15 | — |
| `kpi_highlight` | #7 | — | #4 | #12 | — |
| `process_flow` | — | — | — | #17 | — |
| `quote` | — | — | — | #18 | — |
| `icon_grid` | — | — | — | — | #16 |

### product (7)

| タイプ | P1 | P2 | P3 | P4 | P5 |
|--------|:--:|:--:|:--:|:--:|:--:|
| `product_overview` | #4 | — | #3 | #7 | #3 |
| `architecture` | #5 | #3 | — | #8 | #4 |
| `feature_matrix` | #6 | — | — | — | #5 |
| `feature_detail` | — | #7,#8,#9 | — | — | — |
| `tech_specs` | — | #5 | — | — | — |
| `competitive_compare` | #9 | — | #7 | — | #6 |
| `roadmap` | — | — | #8 | — | — |

### usecase (6)

| タイプ | P1 | P2 | P3 | P4 | P5 |
|--------|:--:|:--:|:--:|:--:|:--:|
| `usecase_overview` | #10 | — | — | #3 | #8 |
| `problem_solution` | #3 | — | #2 | #6 | — |
| `case_study` | #8 | — | #5 | #11 | #9,#10 |
| `before_after` | — | — | — | #9 | — |
| `roi_impact` | #11 | — | #6 | #13 | — |
| `deployment_steps` | #12 | #12 | — | #19 | #15 |

### enterprise (4)

| タイプ | P1 | P2 | P3 | P4 | P5 |
|--------|:--:|:--:|:--:|:--:|:--:|
| `security_compliance` | — | #16 | — | — | — |
| `ecosystem` | — | #18 | — | — | #13 |
| `support_sla` | — | #19 | — | — | #14 |
| `pricing` | #13 | — | — | — | #12 |

### db-middleware (4)

| タイプ | P1 | P2 | P3 | P4 | P5 |
|--------|:--:|:--:|:--:|:--:|:--:|
| `data_flow` | — | #4 | — | — | — |
| `multi_cloud` | — | #11 | — | — | — |
| `benchmark` | — | #15 | — | — | — |
| `migration_path` | — | #13 | — | — | — |

---

## データ品質チェックリスト

各テストデータファイルは以下の品質基準を満たしている:

- [x] `metadata` フィールドが正しい `deckPattern`, `theme`, `product`, `language`, `copyright` を含む
- [x] 各スライドの `type` が `slide-types.md` に定義された36タイプのいずれか
- [x] 各スライドの `master` が `master-registry.md` のマッピングに準拠
- [x] `content` フィールドが各タイプのスキーマに準拠
- [x] 表紙タイトルが16文字以内
- [x] アクションタイトルが50文字以内（結論文スタイル）
- [x] 箇条書き項目が各40文字以内
- [x] スピーカーノートが各200文字以内
- [x] 5ファイル合計で36タイプすべてをカバー
- [x] 各パターンの必須スライドがすべて含まれている
- [x] スライド構成順序が `deck-patterns.md` に準拠
- [x] ScalarDB の実製品情報に基づいたリアルなサンプルデータ

---

## テスト実行方法

### 前提条件

- Python 3.10 以上
- Google Slides API の認証設定完了（`config/credentials.json` 配置済み）
- venv セットアップ済み（`source .venv/bin/activate`）

### 実行手順

テストデータはスキル（Claude Code の `/google-slides` コマンド）経由で使用する。
テストデータの JSON をスキルに渡し、各デッキパターンの生成結果を検証する。

```bash
# ショーケース（全パターン網羅テスト）の生成
source .venv/bin/activate
python scripts/generate-pattern-showcase.py
```

### 期待される結果

- 各テストデータから Google Slides プレゼンテーションが正常に生成される
- スライド数がテストデータの `slides` 配列の長さと一致する
- 各マスターのレイアウト（背景色、フッター有無等）が正しく適用される
- テキストがスライド上に正しく配置され、文字切れがない
- `speakerNotes` がスピーカーノートとして設定される

---

## 更新履歴

| 日付 | 内容 |
|------|------|
| 2026-02-22 | 初版作成: 5デッキパターン×36タイプの完全カバレッジテストデータ |
