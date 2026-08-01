# デッキパターンガイド

Scalar, Inc. の B2B 製品（ScalarDB / ScalarDL）向け Google Slides プレゼンテーション生成で使用する 5 つのデッキパターンの仕様。

各パターンは、対象オーディエンス・ストーリーライン・スライド構成テンプレートを定義し、Claude がコンテンツ生成時にパターンを参照して最適なスライド構成を決定する。

---

## 1. パターン一覧

| パターン ID | パターン名 | 用途 | 枚数目安 | 推奨テーマ |
|:----------:|-----------|------|:--------:|:---------:|
| P1 | `initial_sales` | 初回営業訪問 | 15-20枚 | `scalar` |
| P2 | `technical_deep_dive` | 技術詳細プレゼン | 20-25枚 | `scalar` |
| P3 | `executive_briefing` | 経営層向け | 8-12枚 | `corporate` |
| P4 | `use_case_specific` | 業界特化ユースケース | 15-20枚 | `scalar` |
| P5 | `partner_enablement` | パートナー向け | 15-20枚 | `corporate` |

---

## 2. 各パターンの構成

### 2.1 initial_sales (P1)

- **目的**: 初回訪問で製品価値を簡潔に伝え、次のステップ（PoC/技術検証）につなげる
- **対象**: 営業担当者、IT部門マネージャー
- **ストーリーライン**: SCR (Situation-Complication-Resolution) フレームワーク
- **トーン**: ビジネス価値中心。技術詳細は概要レベルに留め、興味喚起に注力

#### スライド構成テンプレート

| # | type | master | 内容 | 必須 |
|--:|------|--------|------|:----:|
| 1 | `title` | COVER | 表紙: 製品名+対象業界 | Yes |
| 2 | `agenda` | SECTION | アジェンダ: 3-4項目 | No |
| 3 | `text_bullets` | CONTENT | 業界の課題: 3-4個の具体的課題 | Yes |
| 4 | `problem_solution` | SPLIT_SCREEN | 課題→解決策の対比 | Yes |
| 5 | `product_overview` | CONTENT | 製品全体像・価値提案 | Yes |
| 6 | `architecture` | CONTENT | アーキテクチャ概要図 | Yes |
| 7 | `feature_matrix` | CONTENT | 主要機能一覧 | No |
| 8 | `kpi_highlight` | HIGHLIGHT | 導入効果KPI（3-4指標） | Yes |
| 9 | `case_study` | CONTENT | 導入事例 | No |
| 10 | `competitive_compare` | CONTENT | 競合比較（あれば） | No |
| 11 | `usecase_overview` | CONTENT | ユースケース概要 | No |
| 12 | `roi_impact` | HIGHLIGHT | ROI/コスト効果 | No |
| 13 | `deployment_steps` | CONTENT | 導入ステップ概要 | No |
| 14 | `pricing` | CONTENT | 料金体系概要 | No |
| 15 | `summary` | HIGHLIGHT | まとめ: 3つの差別化ポイント | Yes |
| 16 | `closing` | CLOSING | お問い合わせ・次のステップ | Yes |

#### カスタマイズガイド

- 業界に合わせてスライド #3, #4 を調整する。金融業界なら規制対応、小売業界ならスケーラビリティなど
- 既存顧客向けなら `case_study` を増やし、`competitive_compare` は省略可
- 初回訪問で料金は不要な場合が多いため、`pricing` は省略を推奨
- 時間が限られる場合（15分以内）は必須スライドのみに絞り 8-10 枚で構成

---

### 2.2 technical_deep_dive (P2)

- **目的**: 技術検証・PoC 前の詳細説明。エンジニアやアーキテクトが技術的に判断できるレベル
- **対象**: SA/SE、システムアーキテクト
- **ストーリーライン**: セクション区切りによる構造化。技術的根拠をベースにしたボトムアップ型
- **トーン**: 技術的に正確で詳細。データやベンチマークで裏付け

#### スライド構成テンプレート

| # | type | master | 内容 | 必須 |
|--:|------|--------|------|:----:|
| 1 | `title` | COVER | 表紙 | Yes |
| 2 | `agenda` | SECTION | アジェンダ | Yes |
| 3 | `section_divider` | SECTION | セクション1: アーキテクチャ | Yes |
| 4 | `architecture` | CONTENT | システムアーキテクチャ詳細 | Yes |
| 5 | `data_flow` | CONTENT | データフロー図 | Yes |
| 6 | `tech_specs` | CONTENT | 技術仕様 | Yes |
| 7 | `section_divider` | SECTION | セクション2: 機能詳細 | Yes |
| 8 | `feature_detail` | CONTENT | 機能詳細 #1 | Yes |
| 9 | `feature_detail` | CONTENT | 機能詳細 #2 | Yes |
| 10 | `feature_detail` | CONTENT | 機能詳細 #3 | No |
| 11 | `section_divider` | SECTION | セクション3: デプロイメント | Yes |
| 12 | `multi_cloud` | CONTENT | マルチクラウド対応 | No |
| 13 | `deployment_steps` | CONTENT | デプロイメント手順 | Yes |
| 14 | `migration_path` | CONTENT | マイグレーション | No |
| 15 | `section_divider` | SECTION | セクション4: 性能・信頼性 | No |
| 16 | `benchmark` | CONTENT | ベンチマーク結果 | No |
| 17 | `security_compliance` | CONTENT | セキュリティ・コンプライアンス | No |
| 18 | `section_divider` | SECTION | セクション5: エコシステム | No |
| 19 | `ecosystem` | CONTENT | 連携パートナー・インテグレーション | No |
| 20 | `support_sla` | CONTENT | サポート体制 | No |
| 21 | `summary` | HIGHLIGHT | まとめ | Yes |
| 22 | `closing` | CLOSING | Q&A | Yes |
| 23 | `appendix` | BLANK | 付録 | No |

#### カスタマイズガイド

- ScalarDB 向けの場合: `data_flow`、`multi_cloud` を重点的に展開
- ScalarDL 向けの場合: `security_compliance` を必須に昇格し、改ざん検知・Ledger 機能を詳述
- PoC 準備が目的の場合: `deployment_steps` を詳細化し、具体的な検証項目を追加
- セクション 4, 5 は対象の関心に応じて取捨選択する

---

### 2.3 executive_briefing (P3)

- **目的**: CxO/経営層への簡潔な説明。意思決定に必要な情報のみ
- **対象**: CTO, CIO, VP Engineering
- **ストーリーライン**: ピラミッド原則。結論→根拠→データ のトップダウン構成
- **トーン**: ビジネスインパクト重視。技術詳細は省略し、ROI と戦略的価値を強調

#### スライド構成テンプレート

| # | type | master | 内容 | 必須 |
|--:|------|--------|------|:----:|
| 1 | `title` | COVER | 表紙 | Yes |
| 2 | `text_bullets` | CONTENT | エグゼクティブサマリー | Yes |
| 3 | `problem_solution` | SPLIT_SCREEN | ビジネス課題→解決策 | Yes |
| 4 | `product_overview` | CONTENT | 製品概要（ハイレベル） | Yes |
| 5 | `kpi_highlight` | HIGHLIGHT | 導入効果KPI | Yes |
| 6 | `case_study` | CONTENT | 導入事例（同業界） | No |
| 7 | `roi_impact` | HIGHLIGHT | ROI分析 | Yes |
| 8 | `competitive_compare` | CONTENT | 市場ポジション | No |
| 9 | `roadmap` | CONTENT | 導入ロードマップ | No |
| 10 | `summary` | HIGHLIGHT | 推奨事項 | Yes |
| 11 | `closing` | CLOSING | 次のステップ | Yes |

#### カスタマイズガイド

- 8枚以内に収めることを推奨。経営層の集中力は限られる
- `case_study` は同業界の事例があれば強力。なければ省略
- `competitive_compare` はポジショニングが重要な場合のみ。詳細な機能比較は不要
- `roadmap` は中長期的な導入計画を示す場合に追加
- 数字（KPI、ROI）を多用し、定性的な説明は最小限にする

---

### 2.4 use_case_specific (P4)

- **目的**: 特定業界・ユースケースに特化した提案
- **対象**: 業界担当営業、ドメインエキスパート
- **ストーリーライン**: SCR フレームワーク。業界固有の課題から出発し、具体的な解決策と実績を提示
- **トーン**: 業界知識を示しつつ、具体的なソリューション提案。Before/After で効果を可視化

#### スライド構成テンプレート

| # | type | master | 内容 | 必須 |
|--:|------|--------|------|:----:|
| 1 | `title` | COVER | 表紙: 業界名+ユースケース名 | Yes |
| 2 | `agenda` | SECTION | アジェンダ | No |
| 3 | `section_divider` | SECTION | セクション1: 業界課題 | Yes |
| 4 | `usecase_overview` | CONTENT | 業界概要・主要課題 | Yes |
| 5 | `text_bullets` | CONTENT | 具体的な技術課題 | Yes |
| 6 | `section_divider` | SECTION | セクション2: 解決策 | Yes |
| 7 | `problem_solution` | SPLIT_SCREEN | 課題→解決策の対比 | Yes |
| 8 | `product_overview` | CONTENT | 製品のユースケース適合性 | Yes |
| 9 | `architecture` | CONTENT | ユースケース固有アーキテクチャ | No |
| 10 | `before_after` | SPLIT_SCREEN | 導入前後の比較 | Yes |
| 11 | `section_divider` | SECTION | セクション3: 実績 | No |
| 12 | `case_study` | CONTENT | 同業界導入事例 | No |
| 13 | `kpi_highlight` | HIGHLIGHT | 導入効果 | Yes |
| 14 | `roi_impact` | HIGHLIGHT | ROI分析 | No |
| 15 | `section_divider` | SECTION | セクション4: 導入 | No |
| 16 | `deployment_steps` | CONTENT | 導入ステップ | No |
| 17 | `summary` | HIGHLIGHT | まとめ | Yes |
| 18 | `closing` | CLOSING | 次のステップ | Yes |

#### カスタマイズガイド

- 業界別の課題パターン:
  - **金融**: トランザクション整合性、規制対応、マルチリージョン
  - **小売/EC**: スケーラビリティ、在庫一貫性、ピーク対応
  - **ゲーム**: 低レイテンシ、グローバル分散、ユーザーデータ整合性
  - **物流**: サプライチェーントレーサビリティ、改ざん防止、リアルタイム追跡
  - **医療/ヘルスケア**: データ改ざん検知、コンプライアンス、監査証跡
- `before_after` は効果の可視化に最も有効。数値を入れて定量的に示す
- 同業界の `case_study` がない場合は類似業界の事例で代替可

---

### 2.5 partner_enablement (P5)

- **目的**: パートナー（SIer、クラウドベンダー）への製品理解促進・販売支援
- **対象**: パートナー SE、営業担当者
- **ストーリーライン**: 製品理解→販売ツール→サポート体制 の段階的構成
- **トーン**: パートナーが顧客に再説明できるレベルの情報提供。販売メリットを強調

#### スライド構成テンプレート

| # | type | master | 内容 | 必須 |
|--:|------|--------|------|:----:|
| 1 | `title` | COVER | 表紙 | Yes |
| 2 | `agenda` | SECTION | アジェンダ | Yes |
| 3 | `section_divider` | SECTION | セクション1: 製品理解 | Yes |
| 4 | `product_overview` | CONTENT | 製品概要・ポジショニング | Yes |
| 5 | `architecture` | CONTENT | アーキテクチャ | Yes |
| 6 | `feature_matrix` | CONTENT | 機能マトリクス | Yes |
| 7 | `competitive_compare` | CONTENT | 競合との差別化 | Yes |
| 8 | `section_divider` | SECTION | セクション2: ユースケース | Yes |
| 9 | `usecase_overview` | CONTENT | 主要ユースケース一覧 | Yes |
| 10 | `case_study` | CONTENT | 導入事例 #1 | No |
| 11 | `case_study` | CONTENT | 導入事例 #2 | No |
| 12 | `section_divider` | SECTION | セクション3: 販売支援 | Yes |
| 13 | `pricing` | CONTENT | 料金体系 | Yes |
| 14 | `ecosystem` | CONTENT | パートナーエコシステム | No |
| 15 | `support_sla` | CONTENT | サポート・SLA | Yes |
| 16 | `deployment_steps` | CONTENT | 導入プロセス | No |
| 17 | `icon_grid` | CONTENT | パートナーリソース一覧 | No |
| 18 | `summary` | HIGHLIGHT | パートナーメリットまとめ | Yes |
| 19 | `closing` | CLOSING | パートナー窓口 | Yes |

#### カスタマイズガイド

- パートナータイプ別の調整:
  - **SIer**: `deployment_steps` を必須に昇格。導入支援の具体的手順を示す
  - **クラウドベンダー**: `multi_cloud` を追加し、クラウド連携の具体例を強調
  - **ISV**: `ecosystem` を詳細化し、API 連携のユースケースを追加
- `case_study` はパートナー経由の導入事例があれば最も効果的
- `pricing` はパートナー価格体系を反映する場合、別途情報が必要
- `icon_grid` でパートナーポータル、技術ドキュメント、トレーニング資材などのリソースを一覧化

---

## 3. パターンカスタマイズルール

デッキパターンを運用する際のルール。パターンはテンプレートであり、ユーザー要件に応じた柔軟な変更を許容する。

### 3.1 必須スライドの維持

- `必須=Yes` のスライドは原則として削除しない
- `title`（表紙）と `closing`（締め）は**絶対必須**。すべてのパターンで省略不可
- 必須スライドの内容は変更可能だが、スライドタイプの変更は非推奨

### 3.2 スライド追加

- 任意の位置にスライドを追加可能
- 追加時は `section_divider` → コンテンツ群 の構成を推奨
- 同一タイプの繰り返し（例: `feature_detail` x 3）は問題ない
- 追加により枚数目安を超える場合はセクション 3.6 の枚数上限ルールに従う

### 3.3 スライド削除

- `必須=No` のスライドはユーザー指示で削除可能
- ユーザーの明示的な指示がない場合でも、コンテンツが不足するスライドは省略してよい
- 削除によりセクション内のスライドがゼロになる場合、対応する `section_divider` も削除する

### 3.4 順序変更

- セクション単位での並べ替えを推奨
- セクション内の順序も変更可能
- ただし、以下の順序制約を維持する:
  - `title` は常に先頭
  - `closing` は常に末尾
  - `summary` は `closing` の直前
  - `section_divider` はそのセクション内スライドの直前

### 3.5 テーマ変更

- 推奨テーマ以外も適用可能
- テーマ変更時にマスターの見た目は変わるが、スライドタイプ→マスターの対応は不変
- 利用可能テーマ: `scalar`, `aixdevops`, `corporate`

### 3.6 枚数上限

- 目安を大幅に超える場合（目安 + 5枚以上）は以下の対策を取る:
  - `section_divider` で構造化し、論理的なセクション分割を明確にする
  - 詳細な技術情報やデータは `appendix`（付録）に移動する
  - `appendix` の前に `section_divider`（セクション: 付録）を配置
- 絶対上限: 30枚を超えないことを推奨（付録を除く）

---

## 4. ストーリーライン設計原則

プレゼンテーションの論理的構成を支える原則。マッキンゼー流のストーリーライン設計に基づく。

### 4.1 ピラミッド原則

- 結論を先に提示する（トップダウン）
- 3つの論拠で支持する
- 各論拠をデータで裏付ける

```
        [結論]
       /  |  \
   [論拠1] [論拠2] [論拠3]
    |       |       |
  [データ] [データ] [データ]
```

`executive_briefing` (P3) で特に重要。`summary` スライドの `keyPoints` を 3 つに絞り、各コンテンツスライドが 1 つの論拠を裏付ける構成にする。

### 4.2 SCR フレームワーク

- **Situation（状況）**: 現在の業界・企業の状況を共有する
- **Complication（課題）**: その状況から生じる課題・問題点を提示する
- **Resolution（解決）**: Scalar 製品による解決策を示す

```
[Situation]     → text_bullets / usecase_overview
    ↓
[Complication]  → problem_solution (左パネル)
    ↓
[Resolution]    → problem_solution (右パネル) / product_overview
```

`initial_sales` (P1) および `use_case_specific` (P4) で特に有効。スライド #3-5 の構成が SCR に対応する。

### 4.3 アクションタイトルチェーン

- 全スライドのアクションタイトル（CONTENT マスターのタイトル）を順に読むと、一貫したストーリーになること
- 各タイトルは結論文であり、ラベルではないこと
- 「So What?」テストに合格すること: 各タイトルが「だから何？」の問いに答えていること

#### チェーン例（initial_sales）

```
1. (COVER)    — ScalarDB: 金融業界のデータ一貫性を実現
2. (SECTION)  — アジェンダ
3. (CONTENT)  — 金融機関は 3 つの深刻なデータ課題に直面している
4. (SPLIT)    — 従来のアプローチでは一貫性とスケーラビリティを両立できない
5. (CONTENT)  — ScalarDB はアプリケーション透過的にACID保証を提供する
6. (CONTENT)  — ミドルウェア方式で既存DBを変更せずに導入できる
7. (CONTENT)  — 5つの主要機能が競合製品にない差別化を実現
8. (HIGHLIGHT) — 導入企業は平均 40% のコスト削減を達成
9. (CONTENT)  — A銀行は ScalarDB で決済基盤を刷新した
10. ...
```

上記のようにタイトルだけ読んでストーリーが成立するか確認する。

### 4.4 1スライド=1メッセージ原則

- 各スライドは 1 つの主張のみを含む
- サポートデータ・ビジュアルはその主張を裏付けるものに限定する
- 「このスライドで伝えたいことは何か？」を一文で説明できなければ分割を検討する

---

## 5. パターンとスライドタイプの対応マトリクス

36 種類のスライドタイプが各パターンでどのように使用されるかの対応表。

- ●: 使用（パターン構成テンプレートに含まれる）
- ○: オプション（コンテキストに応じて追加可能）
- —: 不使用（パターンの目的に合致しない）

### basic (6)

| タイプ | P1 | P2 | P3 | P4 | P5 |
|--------|:--:|:--:|:--:|:--:|:--:|
| `title` | ● | ● | ● | ● | ● |
| `agenda` | ● | ● | — | ● | ● |
| `section_divider` | — | ● | — | ● | ● |
| `summary` | ● | ● | ● | ● | ● |
| `closing` | ● | ● | ● | ● | ● |
| `appendix` | — | ● | — | — | — |

### content (9)

| タイプ | P1 | P2 | P3 | P4 | P5 |
|--------|:--:|:--:|:--:|:--:|:--:|
| `text_bullets` | ● | ○ | ● | ● | ○ |
| `columns` | ○ | ○ | ○ | ○ | ○ |
| `image_text` | ○ | ○ | ○ | ○ | ○ |
| `chart` | ○ | ○ | ○ | ○ | ○ |
| `table` | ○ | ○ | ○ | ○ | ○ |
| `kpi_highlight` | ● | ○ | ● | ● | ○ |
| `process_flow` | ○ | ○ | ○ | ○ | ○ |
| `quote` | ○ | ○ | ○ | ○ | ○ |
| `icon_grid` | ○ | ○ | — | ○ | ● |

### product (7)

| タイプ | P1 | P2 | P3 | P4 | P5 |
|--------|:--:|:--:|:--:|:--:|:--:|
| `product_overview` | ● | ○ | ● | ● | ● |
| `architecture` | ● | ● | — | ● | ● |
| `feature_matrix` | ● | ○ | — | ○ | ● |
| `feature_detail` | ○ | ● | — | ○ | ○ |
| `tech_specs` | — | ● | — | — | ○ |
| `competitive_compare` | ● | ○ | ● | ○ | ● |
| `roadmap` | ○ | ○ | ● | — | ○ |

### usecase (6)

| タイプ | P1 | P2 | P3 | P4 | P5 |
|--------|:--:|:--:|:--:|:--:|:--:|
| `usecase_overview` | ● | ○ | — | ● | ● |
| `problem_solution` | ● | ○ | ● | ● | ○ |
| `case_study` | ● | ○ | ● | ● | ● |
| `before_after` | ○ | — | — | ● | — |
| `roi_impact` | ● | ○ | ● | ● | ○ |
| `deployment_steps` | ● | ● | — | ● | ● |

### enterprise (4)

| タイプ | P1 | P2 | P3 | P4 | P5 |
|--------|:--:|:--:|:--:|:--:|:--:|
| `security_compliance` | ○ | ● | — | ○ | ○ |
| `ecosystem` | ○ | ● | — | — | ● |
| `support_sla` | ○ | ● | — | — | ● |
| `pricing` | ● | ○ | — | — | ● |

### db-middleware (4)

| タイプ | P1 | P2 | P3 | P4 | P5 |
|--------|:--:|:--:|:--:|:--:|:--:|
| `data_flow` | ○ | ● | — | ○ | ○ |
| `multi_cloud` | ○ | ● | — | ○ | ○ |
| `benchmark` | ○ | ● | — | ○ | — |
| `migration_path` | — | ● | — | — | — |

### 凡例

| 記号 | 意味 | 説明 |
|:----:|------|------|
| ● | 使用 | パターン構成テンプレートに含まれる。必須または推奨 |
| ○ | オプション | コンテキストに応じて追加可能。テンプレートに含まれないが適合する |
| — | 不使用 | パターンの目的・対象に合致しないため、原則使用しない |

---

## 6. デッキ生成時のメタデータ

### 6.1 生成スクリプトでのパターン指定

デッキパターンは生成スクリプトの冒頭で定数として定義する。

```python
# ============================
# デッキパターン設定
# ============================
DECK_PATTERN = "initial_sales"
# このパターンの推奨テーマ: scalar
# 目安枚数: 15-20
# 対象: 営業担当者、IT部門マネージャー
# ストーリーライン: SCR フレームワーク

THEME = "scalar"
PRODUCT = "ScalarDB"
LANGUAGE = "ja"
COPYRIGHT = "(C) 2026 Scalar, Inc."
```

### 6.2 slide_content.json でのパターン参照

```json
{
  "metadata": {
    "deckPattern": "initial_sales",
    "theme": "scalar",
    "product": "ScalarDB",
    "language": "ja",
    "copyright": "(C) 2026 Scalar, Inc."
  },
  "slides": [
    {
      "index": 0,
      "type": "title",
      "master": "COVER",
      "content": {
        "title": "ScalarDB",
        "subtitle": "金融業界のデータ一貫性を実現するデータベースミドルウェア",
        "presenter": "Scalar, Inc.",
        "date": "2026-02-22"
      },
      "speakerNotes": "本日は ScalarDB の概要と金融業界での活用方法をご紹介します。"
    }
  ]
}
```

### 6.3 パターン選択フロー

Claude がユーザー入力からデッキパターンを自動判定する際のフロー。

```
1. ユーザーが明示的にパターン名を指定
   → そのパターンを使用

2. ユーザーが対象オーディエンスを記述
   a. 「経営層」「CxO」「役員」→ executive_briefing (P3)
   b. 「エンジニア」「アーキテクト」「SA」→ technical_deep_dive (P2)
   c. 「パートナー」「SIer」「リセラー」→ partner_enablement (P5)
   d. 「営業」「初回」「提案」→ initial_sales (P1)

3. ユーザーが業界・ユースケースを具体的に記述
   → use_case_specific (P4)

4. 判定不能
   → initial_sales (P1) をデフォルトとして提案し、ユーザーに確認
```

### 6.4 必須スライドの検証

パターンに基づいて生成されたスライドリストが、必須スライドをすべて含んでいるか検証する。

```python
# 検証ロジック（擬似コード）
REQUIRED_SLIDES = {
    "initial_sales": [
        "title", "text_bullets", "problem_solution", "product_overview",
        "architecture", "kpi_highlight", "summary", "closing"
    ],
    "technical_deep_dive": [
        "title", "agenda", "section_divider", "architecture", "data_flow",
        "tech_specs", "feature_detail", "deployment_steps", "summary", "closing"
    ],
    "executive_briefing": [
        "title", "text_bullets", "problem_solution", "product_overview",
        "kpi_highlight", "roi_impact", "summary", "closing"
    ],
    "use_case_specific": [
        "title", "section_divider", "usecase_overview", "text_bullets",
        "problem_solution", "product_overview", "before_after",
        "kpi_highlight", "summary", "closing"
    ],
    "partner_enablement": [
        "title", "agenda", "section_divider", "product_overview",
        "architecture", "feature_matrix", "competitive_compare",
        "usecase_overview", "pricing", "support_sla", "summary", "closing"
    ]
}

def validate_deck(pattern, slides):
    """生成されたスライドが必須タイプをすべて含んでいるか検証する。"""
    required = REQUIRED_SLIDES[pattern]
    actual_types = [s["type"] for s in slides]

    missing = []
    for req in required:
        if req not in actual_types:
            missing.append(req)

    if missing:
        raise ValueError(
            f"パターン '{pattern}' の必須スライドが不足: {missing}"
        )
    return True
```

### 6.5 枚数チェック

```python
SLIDE_COUNT_GUIDE = {
    "initial_sales":       {"min": 15, "max": 20, "hard_max": 30},
    "technical_deep_dive": {"min": 20, "max": 25, "hard_max": 35},
    "executive_briefing":  {"min": 8,  "max": 12, "hard_max": 15},
    "use_case_specific":   {"min": 15, "max": 20, "hard_max": 30},
    "partner_enablement":  {"min": 15, "max": 20, "hard_max": 30},
}

def check_slide_count(pattern, count):
    """スライド枚数が目安範囲内か確認する。"""
    guide = SLIDE_COUNT_GUIDE[pattern]
    if count > guide["hard_max"]:
        return f"警告: {count}枚は上限({guide['hard_max']}枚)を超過。付録への移動を検討してください。"
    elif count > guide["max"]:
        return f"情報: {count}枚は目安({guide['min']}-{guide['max']}枚)を超過。section_divider で構造化を推奨。"
    elif count < guide["min"]:
        return f"情報: {count}枚は目安({guide['min']}-{guide['max']}枚)を下回り。必須スライドの確認を推奨。"
    return None
```
