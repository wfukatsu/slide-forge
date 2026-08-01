# スライド選択ガイド

ユーザーリクエストから適切なデッキパターンとスライドタイプを選定するためのロジックと判断基準。

---

## 1. 選定フロー概要

```
ユーザーリクエスト
    │
    ▼
Step 1: デッキパターン判定
    │  キーワード分析 + コンテキスト推定
    ▼
Step 2: テーマ判定
    │  パターン推奨 + ユーザー指定
    ▼
Step 3: スライド構成決定
    │  パターンテンプレート + カスタマイズ
    ▼
Step 4: コンテンツ生成
    │  各スライドのコンテンツを生成
    ▼
生成スクリプト
```

各ステップの詳細なロジックを以下に記述する。

---

## 2. デッキパターン判定ロジック

5つのデッキパターンから最適なものを選定する。判定は「キーワードマッチング」「コンテキスト分析」「フローチャート判定」の3段階で行う。

### 2.1 キーワードマッチング

ユーザーリクエスト内のキーワード/フレーズを走査し、パターン候補を抽出する。

| キーワード/フレーズ | 判定パターン | 信頼度 |
|---|---|---|
| 「初回訪問」「初回営業」「紹介資料」「製品紹介」 | initial_sales | High |
| 「技術詳細」「アーキテクチャ」「技術検証」「PoC」「ディープダイブ」 | technical_deep_dive | High |
| 「経営層」「CTO」「CIO」「エグゼクティブ」「役員向け」 | executive_briefing | High |
| 「金融」「小売」「製造」「ヘルスケア」+ 「向け」 | use_case_specific | Medium |
| 「ユースケース」「業界特化」「業種別」 | use_case_specific | High |
| 「パートナー」「SIer」「販売支援」「イネーブルメント」 | partner_enablement | High |
| 「営業資料」「プレゼン」（汎用） | initial_sales | Low |
| 「技術資料」（汎用） | technical_deep_dive | Low |
| 「概要説明」「製品概要」 | initial_sales | Medium |
| 「導入提案」「提案書」 | initial_sales | Medium |
| 「設計レビュー」「技術レビュー」 | technical_deep_dive | Medium |
| 「投資判断」「稟議」「承認」 | executive_briefing | Medium |
| 「再販」「OEM」「代理店」 | partner_enablement | Medium |

**複数パターンが候補に挙がった場合の優先順位**:
1. 信頼度 High のパターンを優先
2. 同一信頼度が複数ある場合はコンテキスト分析（2.2）へ進む
3. High が1つだけなら即座に確定

### 2.2 コンテキスト分析

キーワードだけでは判定が曖昧な場合、以下の3軸でコンテキストを分析する。

#### 2.2.1 対象者の分析

| 対象者の手がかり | 推定パターン |
|---|---|
| 技術者/エンジニア/アーキテクト | technical_deep_dive |
| 経営層/意思決定者/CxO/取締役 | executive_briefing |
| 営業/ビジネス担当/顧客先 | initial_sales |
| パートナー/販売代理店/SIer | partner_enablement |
| 業界担当者/業種特化チーム | use_case_specific |

#### 2.2.2 製品指定の分析

| 製品言及パターン | 推定パターン |
|---|---|
| ScalarDB/ScalarDL + 汎用的な説明要求 | initial_sales |
| 特定機能名への言及（ACID, Consensus など） | technical_deep_dive |
| 業界名 + 製品名 | use_case_specific |
| 製品名なし + ROI/ビジネス価値 | executive_briefing |
| 製品の販売方法/差別化ポイント | partner_enablement |

#### 2.2.3 枚数の指示

| 枚数指示 | 推定パターン |
|---|---|
| 「5枚程度」「簡潔に」 | executive_briefing |
| 「10枚以下」 | executive_briefing |
| 「15枚程度」「標準的に」 | initial_sales |
| 「20枚程度」 | initial_sales or use_case_specific |
| 「25枚以上」「網羅的に」 | technical_deep_dive |
| 「30枚以上」 | technical_deep_dive（appendix 含む） |

### 2.3 判定フローチャート

キーワードとコンテキストの両方を加味した最終判定フロー:

```
Q1: 対象者は誰か？
  ├─ 経営層/CxO → executive_briefing
  ├─ パートナー/SIer → partner_enablement
  ├─ エンジニア/アーキテクト → Q2
  └─ 営業/ビジネス/不明 → Q3

Q2: 目的は何か？
  ├─ 技術評価/PoC/設計検討 → technical_deep_dive
  ├─ 製品概要理解/初回説明 → initial_sales
  └─ 業界特化の技術要件 → use_case_specific

Q3: 業界/ユースケースが特定されているか？
  ├─ Yes（具体的な業界名あり） → use_case_specific
  └─ No → Q4

Q4: 目的の詳細は？
  ├─ 投資判断/ROI/ビジネス価値 → executive_briefing
  ├─ 販売支援/パートナー教育 → partner_enablement
  └─ その他/不明 → initial_sales（デフォルト）
```

### 2.4 信頼度が低い場合のフォールバック

信頼度が Low の場合、または複数パターンが競合する場合は、ユーザーに確認する:

```
「デッキパターンを以下から選択してください:
1. 初回営業（initial_sales）— 製品の価値提案と概要
2. 技術詳細（technical_deep_dive）— アーキテクチャと技術仕様
3. 経営層向け（executive_briefing）— 簡潔なROI中心の説明
4. ユースケース特化（use_case_specific）— 業界固有の課題と解決策
5. パートナー向け（partner_enablement）— 販売支援・製品理解」
```

確認時は推定パターンを先頭に提示し、選択の負担を軽減する。

---

## 3. テーマ判定ロジック

### 3.1 パターン推奨テーマ

| パターン | 推奨テーマ | 理由 |
|---------|----------|------|
| initial_sales | scalar | Scalar ブランドで製品訴求を強化 |
| technical_deep_dive | scalar | 技術的信頼感と製品ブランドの一貫性 |
| executive_briefing | corporate | フォーマルかつ洗練された印象 |
| use_case_specific | scalar | 製品ブランド+業界カスタマイズで訴求力強化 |
| partner_enablement | corporate | 中立的・プロフェッショナルな印象 |

### 3.2 テーマ上書きルール

以下の優先順位でテーマを決定する（上位が優先）:

1. **ユーザー明示指定** — ユーザーがテーマを直接指定した場合は最優先
2. **社外向け一般プレゼン** — corporate テーマ推奨
3. **Scalar 製品中心** — scalar テーマ推奨
4. **勉強会・テックイベント・カンファレンス** — aixdevops テーマ推奨
5. **指定なし** — パターン推奨テーマ（3.1 の表）を適用

### 3.3 テーマ選択の補足条件

| 条件 | テーマ判定 |
|------|----------|
| 「Scalar のブランドカラーで」 | scalar |
| 「コーポレートカラーで」「フォーマルに」 | corporate |
| 「イベント登壇用」「LT用」 | aixdevops |
| 「シンプルに」「白基調で」 | corporate |
| 「ブランドガイドラインに沿って」 | scalar |

---

## 4. スライド構成カスタマイズロジック

### 4.1 必須スライドの確保

パターンテンプレートの必須スライドは常に含める。削除不可:

| スライドタイプ | マスター | 適用パターン |
|---|---|---|
| title | COVER | 全パターン共通（先頭） |
| closing | CLOSING | 全パターン共通（末尾） |
| summary | HIGHLIGHT | executive_briefing 以外 |
| agenda | SECTION | 15枚以上の場合推奨 |

### 4.2 コンテンツベースの追加・削除

ユーザーリクエストの内容に応じてオプショナルスライドを追加/削除する。

| ユーザー言及 | 追加するスライドタイプ | カテゴリ |
|---|---|---|
| 「競合との比較」「他社比較」 | competitive_compare | product |
| 「導入事例」「ケーススタディ」 | case_study | usecase |
| 「料金」「コスト」「価格」 | pricing | enterprise |
| 「ROI」「投資対効果」 | roi_impact | usecase |
| 「ベンチマーク」「性能」 | benchmark | product |
| 「セキュリティ」「コンプライアンス」 | security_compliance | enterprise |
| 「マイグレーション」「移行」 | migration_path | product |
| 「マルチクラウド」 | multi_cloud | product |
| 「ロードマップ」「今後の計画」 | roadmap | product |
| 「エコシステム」「連携」 | ecosystem | product |
| 「サポート」「SLA」 | support_sla | enterprise |
| 「データフロー」 | data_flow | db-middleware |
| 「トランザクション」「ACID」 | tech_specs | db-middleware |
| 「デプロイ」「構成」 | deployment_steps | db-middleware |
| 「可用性」「耐障害性」 | architecture | db-middleware |
| 「お客様の声」「推薦」 | quote | basic |
| 「タイムライン」「スケジュール」 | roadmap | product |

### 4.3 枚数制約によるスライド調整

ユーザーが枚数を指定した場合、以下の方針でスライド構成を調整する。

| 指示された枚数 | 調整方針 |
|---|---|
| 5-8枚 | 必須スライドのみ。section_divider 削除。概要中心 |
| 8-12枚 | executive_briefing パターン推奨。コア情報に絞る |
| 12-15枚 | オプショナルスライド 2-3枚追加 |
| 15-20枚 | 標準パターン通り。バランスの取れた構成 |
| 20-25枚 | オプショナルスライドを積極的に追加 |
| 25枚以上 | section_divider で構造化。appendix を追加 |

### 4.4 セクション分割の基準

25枚以上のデッキでは section_divider を挿入して構造化する:

| セクション | 含まれるスライドタイプ例 |
|---|---|
| イントロダクション | title, agenda, problem_solution |
| 製品概要 | feature_matrix, feature_detail, architecture |
| 技術詳細 | tech_specs, data_flow, benchmark |
| 導入効果 | roi_impact, case_study, kpi_highlight |
| ネクストステップ | roadmap, deployment_steps, closing |

---

## 5. スライドタイプ選定ヒューリスティクス

### 5.1 コンテンツ種類からタイプへのマッピング

コンテンツの性質に基づいて最適なスライドタイプを選定する。

| コンテンツの性質 | 推奨スライドタイプ | 代替タイプ |
|---|---|---|
| 定量データ（数値、KPI） | kpi_highlight | chart |
| 比較データ（2項目対比） | before_after | problem_solution |
| 比較データ（3項目以上） | competitive_compare | table |
| プロセス・手順（3-6ステップ） | process_flow | deployment_steps |
| 機能一覧（概要レベル） | feature_matrix | icon_grid |
| 個別機能の詳細説明 | feature_detail | text_bullets |
| 時系列データ | chart (line) | roadmap |
| 分布データ | chart (pie/doughnut) | kpi_highlight |
| カテゴリ別データ | chart (bar) | table |
| アーキテクチャ図 | architecture | data_flow |
| 引用・推薦文 | quote | --- |
| ROI/効果の数値 | roi_impact | kpi_highlight |
| 箇条書きテキスト | text_bullets | columns |
| 左右並列情報 | columns | --- |
| 画像+説明テキスト | image_text | --- |
| アイコンベースの概念図 | icon_grid | --- |
| 課題と解決策のペア | problem_solution | before_after |
| ステップバイステップの導入手順 | deployment_steps | process_flow |
| セキュリティ要件一覧 | security_compliance | text_bullets |
| 価格体系 | pricing | table |

### 5.2 マスター選定ルール

スライドタイプからマスターは自動決定される（slide-types.md 参照）。基本的に追加の判断は不要。

ただし、以下のケースでは手動でマスターを変更する場合がある:

| 変更ケース | 変更前 | 変更後 | 理由 |
|---|---|---|---|
| summary を通常表示したい | HIGHLIGHT | CONTENT | 白背景で控えめに表示 |
| kpi_highlight を通常表示したい | HIGHLIGHT | CONTENT | 他のスライドと統一感を出す |
| text_bullets を強調したい | CONTENT | HIGHLIGHT | 重要メッセージの視覚的強調 |
| quote を全面表示したい | QUOTE | HIGHLIGHT | インパクトを強める |

### 5.3 スライドタイプの組み合わせパターン

効果的なストーリーテリングのために、以下の組み合わせを推奨する:

| ストーリー展開 | スライドタイプの流れ |
|---|---|
| 課題提起 → 解決策 | problem_solution → feature_detail → kpi_highlight |
| 現状 → 改善後 | before_after → roi_impact → case_study |
| 概要 → 詳細 | feature_matrix → feature_detail → tech_specs |
| 実績紹介 | case_study → quote → kpi_highlight |
| 導入提案 | architecture → deployment_steps → pricing → roadmap |

---

## 6. 判定例

### 例1: 「金融業界向けScalarDB初回営業デッキ」

- **パターン**: initial_sales（「初回営業」→ High）
- **テーマ**: scalar（パターン推奨 + Scalar 製品中心）
- **業界カスタマイズ**: 金融業界の課題（リアルタイム決済、データ整合性）をスライド #3, #4 に反映
- **追加候補**: security_compliance（金融業界ではコンプライアンスが重要）
- **推定枚数**: 15-20枚（標準的な初回営業）
- **言語**: ja（デフォルト）

### 例2: 「CTOに向けたScalarDBの投資対効果の説明」

- **パターン**: executive_briefing（「CTO」→ High）
- **テーマ**: corporate（パターン推奨 + 経営層向け）
- **追加**: roi_impact（「投資対効果」→ 必須追加）
- **枚数**: 8-12枚で簡潔に
- **特記**: 技術詳細は最小限、ビジネスインパクトを中心に構成
- **推奨フロー**: title → problem_solution → roi_impact → kpi_highlight → case_study → closing

### 例3: 「ScalarDBのアーキテクチャと性能について詳しく」

- **パターン**: technical_deep_dive（「アーキテクチャ」「性能」→ High）
- **テーマ**: scalar（パターン推奨）
- **追加**: benchmark（「性能」→ 追加）
- **強化**: architecture, tech_specs に詳細を充実
- **推定枚数**: 20-25枚（技術詳細は情報量が多い）
- **推奨フロー**: title → agenda → architecture → data_flow → tech_specs → benchmark → deployment_steps → closing

### 例4: 「SIerパートナー向けの販売支援資料」

- **パターン**: partner_enablement（「SIer」「パートナー」「販売支援」→ High）
- **テーマ**: corporate（パターン推奨 + 中立的な印象）
- **標準構成をベースに**
- **追加候補**: competitive_compare（パートナーが他社と比較説明する場面を想定）
- **推定枚数**: 15-20枚

### 例5: 「製造業のサプライチェーン管理に特化したデッキ」

- **パターン**: use_case_specific（「製造業」+ 「に特化した」→ High）
- **テーマ**: scalar（パターン推奨）
- **業界**: 製造業のサプライチェーン課題に特化
- **追加候補**: data_flow（サプライチェーンのデータ連携を可視化）
- **推定枚数**: 15-20枚

### 例6: 「プレゼン資料を作って」（曖昧なリクエスト）

- **パターン**: 判定不可（信頼度 Low）
- **対応**: ヒアリングフロー（セクション7）に移行
- **最小質問**: 「誰向けの、何についてのプレゼンですか？」
- **フォールバック**: 回答から判定できない場合は initial_sales をデフォルトとして提案

---

## 7. ヒアリングフロー

パターンが自動判定できない場合、インタラクティブにユーザーへ質問する。

### 7.1 Phase 1 質問項目

以下の情報を収集する。ただし、全項目を一度に質問しない:

1. **デッキの目的**: 「プレゼンテーションの目的を教えてください」
2. **対象者**: 「対象者は誰ですか？（経営層/技術者/営業/パートナー）」
3. **製品**: 「どの製品についてですか？（ScalarDB / ScalarDL / 両方）」
4. **業界**: 「特定の業界向けですか？（金融/小売/製造/ヘルスケア/汎用）」
5. **枚数**: 「目安の枚数はありますか？」
6. **言語**: 「日本語/英語のどちらですか？」

### 7.2 最小限の質問でパターンを決定

通常、1-2 問で判定可能。効率的な質問戦略:

**第1問（統合質問）**:
「誰向けの、何についてのプレゼンですか？」

この1問で以下が判明する可能性が高い:
- 対象者 → パターン候補の絞り込み
- 目的/製品 → パターンの確定
- 業界 → use_case_specific の判定

**第2問（補足、必要な場合のみ）**:
- パターンが絞り込めた場合: 「枚数の目安はありますか？」
- パターンが競合する場合: 「技術的な内容と業務的な内容のどちらを重視しますか？」

### 7.3 ヒアリング結果からの判定マトリクス

| 目的 | 対象者 | 判定パターン |
|------|--------|-------------|
| 製品紹介 | 顧客（初回） | initial_sales |
| 製品紹介 | 顧客（技術検証） | technical_deep_dive |
| 投資判断 | 経営層 | executive_briefing |
| 業界課題解決 | 業界担当者 | use_case_specific |
| 販売支援 | パートナー | partner_enablement |
| 製品紹介 | 社内（不明） | initial_sales（デフォルト） |

---

## 8. 生成スクリプトへの反映

選定結果を Google Slides 生成スクリプトに反映する方法。

### 8.1 選定結果の構造化

```python
# Phase 1 ヒアリング結果
DECK_PATTERN = "initial_sales"
THEME = "scalar"
PRODUCT = "ScalarDB"
INDUSTRY = "金融"
LANGUAGE = "ja"
TARGET_SLIDE_COUNT = 18  # 目標枚数

# パターンテンプレートから必須スライドを展開
# + ユーザーリクエストに基づくカスタマイズ
slides = [
    {"type": "title", "content": {...}},
    {"type": "agenda", "content": {...}},
    {"type": "problem_solution", "content": {...}},
    # ... pattern template + customizations
    {"type": "closing", "content": {...}},
]
```

### 8.2 スライド順序の決定ルール

スライドの並び順は以下の論理構造に従う:

1. **導入部** (1-3枚目): title, agenda
2. **課題提起** (4-6枚目): problem_solution, before_after
3. **解決策** (7-12枚目): feature_matrix, feature_detail, architecture, tech_specs
4. **実証** (13-16枚目): benchmark, case_study, kpi_highlight, roi_impact
5. **提案** (17-19枚目): pricing, deployment_steps, roadmap
6. **締め** (最終): summary, closing

section_divider は各セクションの先頭に挿入する（25枚以上の場合）。

### 8.3 パターン別のスライド構成テンプレート

#### initial_sales（15-20枚）
```
title → agenda → problem_solution → feature_matrix → feature_detail(x2)
→ architecture → competitive_compare → case_study → kpi_highlight
→ roi_impact → deployment_steps → roadmap → summary → closing
```

#### technical_deep_dive（20-25枚）
```
title → agenda → architecture → data_flow → tech_specs(x2-3)
→ benchmark → feature_detail(x3) → deployment_steps → migration_path
→ multi_cloud → ecosystem → security_compliance → summary → closing
```

#### executive_briefing（8-12枚）
```
title → problem_solution → kpi_highlight → roi_impact
→ case_study → competitive_compare → roadmap → closing
```

#### use_case_specific（15-20枚）
```
title → agenda → problem_solution(業界特化) → feature_matrix
→ architecture(業界構成) → case_study(同業界) → data_flow
→ kpi_highlight → roi_impact → deployment_steps → summary → closing
```

#### partner_enablement（15-20枚）
```
title → agenda → problem_solution(市場課題) → feature_matrix
→ competitive_compare → case_study → pricing → support_sla
→ deployment_steps → ecosystem → summary → closing
```

---

## 9. 判定精度の向上指針

### 9.1 曖昧性の解消パターン

以下のケースでは特に注意して判定する:

| 曖昧な表現 | 解釈の候補 | 解消方法 |
|---|---|---|
| 「ScalarDBの資料」 | initial_sales / technical_deep_dive | 対象者を確認 |
| 「詳しい説明」 | technical_deep_dive / initial_sales（詳細版） | 技術詳細か機能詳細かを確認 |
| 「お客様向け」 | initial_sales / executive_briefing / use_case_specific | 役職・業界を確認 |
| 「社内向け」 | 全パターン可能性あり | 目的を確認 |
| 「短くまとめて」 | executive_briefing / initial_sales（短縮版） | 対象者を確認 |

### 9.2 複合リクエストへの対応

ユーザーが複数の要素を含むリクエストをした場合:

- 「金融業界のCTO向けにScalarDBの技術概要」
  → 対象者: CTO（executive_briefing）+ 技術概要（technical_deep_dive）
  → **判定**: executive_briefing（対象者優先）+ 技術スライドを多めに追加

- 「パートナー向けの業界別ユースケース集」
  → 対象者: パートナー + 業界別
  → **判定**: partner_enablement（対象者優先）+ 業界別スライドを追加

原則として**対象者を最優先**し、コンテンツ要素はスライド追加で対応する。

### 9.3 フィードバックループ

生成後にユーザーから修正指示があった場合の対応:

1. 「もっと技術的に」→ technical_deep_dive のスライドタイプを追加
2. 「もっと簡潔に」→ 枚数を削減、executive_briefing 寄りに調整
3. 「業界事例を増やして」→ case_study, use_case_specific のスライドを追加
4. 「経営層にも見せたい」→ roi_impact, kpi_highlight を前方に移動

これらの修正は既存のパターン判定を変更せず、スライド構成の調整で対応する。
