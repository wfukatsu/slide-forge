# スライドタイプレジストリ

36 種類のスライドタイプの定義。各タイプのコンテンツスキーマ、マスター、テキスト制約、既存パターンとのマッピングを規定する。

コンポーザー（レンダリング仕様）の詳細は `composers/<category>.md` を参照。

---

## 1. タイプ一覧

### basic (6)

| タイプ | マスター | 説明 | コンポーザー |
|--------|---------|------|------------|
| `title` | COVER | プレゼンテーション表紙 | `compose_title` |
| `agenda` | SECTION | 目次・アジェンダ | `compose_agenda` |
| `section_divider` | SECTION | セクション区切り | `compose_section_divider` |
| `summary` | HIGHLIGHT | エグゼクティブサマリー / 結論 | `compose_summary` |
| `closing` | CLOSING | 締め・お問い合わせ | `compose_closing` |
| `appendix` | BLANK | 付録表紙 | `compose_appendix` |

### content (9)

| タイプ | マスター | 説明 | コンポーザー |
|--------|---------|------|------------|
| `text_bullets` | CONTENT | 箇条書きによる要点列挙 | `compose_text_bullets` |
| `columns` | CONTENT | 2-3列の並列レイアウト | `compose_columns` |
| `image_text` | CONTENT | 画像+テキストの分割レイアウト | `compose_image_text` |
| `chart` | CONTENT | Sheets連携チャート | `compose_chart` |
| `table` | CONTENT | テーブル形式のデータ表示 | `compose_table` |
| `kpi_highlight` | HIGHLIGHT | KPI・主要指標の強調表示 | `compose_kpi_highlight` |
| `process_flow` | CONTENT | プロセスフロー・ステップ表示 | `compose_process_flow` |
| `quote` | QUOTE | 引用・顧客の声 | `compose_quote` |
| `icon_grid` | CONTENT | アイコン+テキストのグリッド | `compose_icon_grid` |

### product (7)

| タイプ | マスター | 説明 | コンポーザー |
|--------|---------|------|------------|
| `product_overview` | CONTENT | 製品全体像・価値提案 | `compose_product_overview` |
| `architecture` | CONTENT | システムアーキテクチャ図 | `compose_architecture` |
| `feature_matrix` | CONTENT | 機能比較マトリクス | `compose_feature_matrix` |
| `feature_detail` | CONTENT | 個別機能の詳細説明 | `compose_feature_detail` |
| `tech_specs` | CONTENT | 技術仕様・スペック一覧 | `compose_tech_specs` |
| `competitive_compare` | CONTENT | 競合比較表 | `compose_competitive_compare` |
| `roadmap` | CONTENT | 製品ロードマップ・タイムライン | `compose_roadmap` |

### usecase (6)

| タイプ | マスター | 説明 | コンポーザー |
|--------|---------|------|------------|
| `usecase_overview` | CONTENT | ユースケース全体像 | `compose_usecase_overview` |
| `problem_solution` | SPLIT_SCREEN | 課題→解決策の対比 | `compose_problem_solution` |
| `case_study` | CONTENT | 導入事例・ケーススタディ | `compose_case_study` |
| `before_after` | SPLIT_SCREEN | 導入前後の比較 | `compose_before_after` |
| `roi_impact` | HIGHLIGHT | ROI・導入効果の数値表示 | `compose_roi_impact` |
| `deployment_steps` | CONTENT | 導入ステップ・フェーズ | `compose_deployment_steps` |

### enterprise (4)

| タイプ | マスター | 説明 | コンポーザー |
|--------|---------|------|------------|
| `security_compliance` | CONTENT | セキュリティ・コンプライアンス | `compose_security_compliance` |
| `ecosystem` | CONTENT | エコシステム・連携パートナー | `compose_ecosystem` |
| `support_sla` | CONTENT | サポート体制・SLA | `compose_support_sla` |
| `pricing` | CONTENT | 料金体系 | `compose_pricing` |

### db-middleware (4)

| タイプ | マスター | 説明 | コンポーザー |
|--------|---------|------|------------|
| `data_flow` | CONTENT | データフロー図 | `compose_data_flow` |
| `multi_cloud` | CONTENT | マルチクラウド構成 | `compose_multi_cloud` |
| `benchmark` | CONTENT | ベンチマーク・性能比較 | `compose_benchmark` |
| `migration_path` | CONTENT | マイグレーションパス | `compose_migration_path` |

---

## 2. コンテンツスキーマ

各タイプの `content` フィールドの構造。`(opt)` はオプション。

### basic

#### title

```json
{
  "title": "string — プレゼンテーションタイトル",
  "subtitle": "string (opt) — サブタイトル",
  "presenter": "string (opt) — 発表者名",
  "date": "string (opt) — 日付",
  "company": "string (opt) — 企業名"
}
```

| フィールド | 日本語上限 | 英語上限 |
|-----------|----------|---------|
| title | 16文字 | 40文字 |
| subtitle | 30文字 | 60文字 |

#### agenda

```json
{
  "title": "string — タイトル（例: 'アジェンダ'）",
  "items": ["string — セクション名"],
  "currentIndex": "number (opt) — 現在のセクション（0始まり、ハイライト表示）"
}
```

| フィールド | 制約 |
|-----------|------|
| items | 最大8項目、各40文字以内 |

#### section_divider

```json
{
  "title": "string — セクションタイトル",
  "subtitle": "string (opt) — 補足テキスト",
  "sectionNumber": "number (opt) — セクション番号"
}
```

| フィールド | 日本語上限 | 英語上限 |
|-----------|----------|---------|
| title | 25文字 | 50文字 |

#### summary

```json
{
  "title": "string — アクションタイトル（結論文）",
  "keyPoints": ["string — 要点"],
  "recommendation": "string (opt) — 推奨事項",
  "nextSteps": ["string (opt) — ネクストステップ"]
}
```

| フィールド | 制約 |
|-----------|------|
| keyPoints | 最大5項目、各40文字以内 |
| nextSteps | 最大3項目 |

#### closing

```json
{
  "message": "string (opt) — クロージングメッセージ",
  "contactInfo": {
    "name": "string (opt)",
    "email": "string (opt)",
    "phone": "string (opt)",
    "url": "string (opt)"
  }
}
```

#### appendix

```json
{
  "title": "string — 付録タイトル（例: 'Appendix'）",
  "subtitle": "string (opt) — 補足テキスト"
}
```

### content

#### text_bullets

```json
{
  "title": "string — アクションタイトル",
  "subtitle": "string (opt)",
  "bullets": ["string — 箇条書き項目"],
  "footnote": "string (opt) — 脚注"
}
```

| フィールド | 制約 |
|-----------|------|
| title | 50文字(ja) / 100文字(en) |
| bullets | 最大6項目、各40文字以内 |

#### columns

```json
{
  "title": "string — アクションタイトル",
  "columns": [
    {
      "heading": "string — カラム見出し",
      "bullets": ["string"],
      "icon": "string (opt) — アイコン文字（1-2文字）"
    }
  ]
}
```

| フィールド | 制約 |
|-----------|------|
| columns | 2-3列 |
| bullets | 各カラム最大4項目 |

#### image_text

```json
{
  "title": "string — アクションタイトル",
  "text": "string — 説明テキスト",
  "bullets": ["string (opt)"],
  "imageAsset": "string — アセットパス（例: 'shared/icons/diagram.png'）",
  "imagePosition": "string (opt) — 'left' | 'right'（デフォルト: 'right'）"
}
```

#### chart

```json
{
  "title": "string — アクションタイトル",
  "chartType": "string — bar | line | pie | doughnut | radar | area",
  "data": {
    "labels": ["string — カテゴリラベル"],
    "series": [
      {
        "name": "string — 系列名",
        "values": ["number"]
      }
    ]
  },
  "options": {
    "showValues": "boolean (opt)",
    "showLegend": "boolean (opt)",
    "unit": "string (opt) — 値の単位",
    "source": "string (opt) — データソース"
  }
}
```

#### table

```json
{
  "title": "string — アクションタイトル",
  "headers": ["string — ヘッダー列名"],
  "rows": [["string — セルデータ"]],
  "footnote": "string (opt) — 脚注"
}
```

| フィールド | 制約 |
|-----------|------|
| headers | 最大6列 |
| rows | 最大8行 |

#### kpi_highlight

```json
{
  "title": "string (opt) — アクションタイトル",
  "kpis": [
    {
      "value": "string — KPI値（例: '99.9%', '3x', '<5ms'）",
      "label": "string — KPI名称",
      "description": "string (opt) — 補足説明",
      "trend": "string (opt) — 'up' | 'down' | 'stable'"
    }
  ]
}
```

| フィールド | 制約 |
|-----------|------|
| kpis | 2-4個 |
| value | 簡潔（数文字） |

#### process_flow

```json
{
  "title": "string — アクションタイトル",
  "steps": [
    {
      "name": "string — ステップ名",
      "description": "string (opt) — 説明",
      "icon": "string (opt) — アイコン文字"
    }
  ]
}
```

| フィールド | 制約 |
|-----------|------|
| steps | 3-5ステップ |

#### quote

```json
{
  "quoteText": "string — 引用テキスト",
  "attribution": "string — 発言者名",
  "role": "string (opt) — 役職",
  "company": "string (opt) — 所属企業",
  "companyLogo": "string (opt) — ロゴアセットパス"
}
```

#### icon_grid

```json
{
  "title": "string — アクションタイトル",
  "items": [
    {
      "icon": "string — アイコン文字（1-2文字）",
      "label": "string — ラベル",
      "description": "string (opt) — 説明"
    }
  ]
}
```

| フィールド | 制約 |
|-----------|------|
| items | 3-6個（2列×1-3行 or 3列×1-2行） |

### product

#### product_overview

```json
{
  "title": "string — アクションタイトル",
  "productName": "string — 製品名",
  "tagline": "string — キャッチコピー",
  "keyFeatures": [
    {
      "icon": "string (opt)",
      "name": "string",
      "description": "string"
    }
  ],
  "productLogo": "string (opt) — 製品ロゴアセットパス"
}
```

| フィールド | 制約 |
|-----------|------|
| keyFeatures | 3-4個 |

#### architecture

```json
{
  "title": "string — アクションタイトル",
  "layers": [
    {
      "name": "string — レイヤー名",
      "components": [
        {
          "name": "string — コンポーネント名",
          "type": "string (opt) — 'scalar' | 'external' | 'client'",
          "icon": "string (opt) — クラウドアイコンパス"
        }
      ]
    }
  ],
  "connections": [
    {
      "from": "string — 接続元コンポーネント名",
      "to": "string — 接続先コンポーネント名",
      "label": "string (opt) — 接続ラベル",
      "style": "string (opt) — 'solid' | 'dashed'"
    }
  ]
}
```

#### feature_matrix

```json
{
  "title": "string — アクションタイトル",
  "features": ["string — 機能名"],
  "products": [
    {
      "name": "string — 製品名",
      "values": ["string — 対応状況: 'yes' | 'no' | 'partial' | テキスト"]
    }
  ]
}
```

#### feature_detail

```json
{
  "title": "string — アクションタイトル",
  "featureName": "string — 機能名",
  "description": "string — 機能説明",
  "benefits": ["string — メリット"],
  "technicalDetail": "string (opt) — 技術詳細",
  "diagram": "string (opt) — 図アセットパス"
}
```

#### tech_specs

```json
{
  "title": "string — アクションタイトル",
  "categories": [
    {
      "name": "string — カテゴリ名",
      "specs": [
        {
          "item": "string — 項目名",
          "value": "string — 値"
        }
      ]
    }
  ]
}
```

#### competitive_compare

```json
{
  "title": "string — アクションタイトル",
  "dimensions": ["string — 比較軸"],
  "competitors": [
    {
      "name": "string — 製品/競合名",
      "isOurs": "boolean (opt) — 自社製品フラグ",
      "values": ["string — 各軸の評価"]
    }
  ]
}
```

#### roadmap

```json
{
  "title": "string — アクションタイトル",
  "milestones": [
    {
      "date": "string — 時期（例: 'Q1 2026'）",
      "title": "string — マイルストーン名",
      "description": "string (opt) — 説明",
      "status": "string (opt) — 'completed' | 'in_progress' | 'planned'"
    }
  ]
}
```

| フィールド | 制約 |
|-----------|------|
| milestones | 4-8個 |

### usecase

#### usecase_overview

```json
{
  "title": "string — アクションタイトル",
  "industry": "string — 業界名",
  "challenge": "string — 課題",
  "solution": "string — 解決策",
  "outcomes": ["string — 成果"]
}
```

#### problem_solution

```json
{
  "title": "string — アクションタイトル",
  "problem": {
    "heading": "string — 課題見出し",
    "points": ["string — 課題ポイント"]
  },
  "solution": {
    "heading": "string — 解決策見出し",
    "points": ["string — 解決策ポイント"]
  }
}
```

#### case_study

```json
{
  "title": "string — アクションタイトル",
  "company": "string — 企業名",
  "industry": "string — 業界",
  "challenge": "string — 課題",
  "solution": "string — 採用ソリューション",
  "results": [
    {
      "metric": "string — 指標名",
      "value": "string — 値",
      "description": "string (opt)"
    }
  ],
  "quote": "string (opt) — 顧客の声",
  "companyLogo": "string (opt) — ロゴアセットパス"
}
```

#### before_after

```json
{
  "title": "string — アクションタイトル",
  "before": {
    "heading": "string — Before 見出し",
    "points": ["string — ポイント"]
  },
  "after": {
    "heading": "string — After 見出し",
    "points": ["string — ポイント"]
  }
}
```

#### roi_impact

```json
{
  "title": "string (opt) — アクションタイトル",
  "metrics": [
    {
      "value": "string — 数値（例: '40%', '3x', '$1.2M'）",
      "label": "string — 指標名",
      "description": "string (opt) — 補足"
    }
  ],
  "summary": "string (opt) — ROI サマリー"
}
```

| フィールド | 制約 |
|-----------|------|
| metrics | 2-4個 |

#### deployment_steps

```json
{
  "title": "string — アクションタイトル",
  "phases": [
    {
      "name": "string — フェーズ名",
      "duration": "string — 期間（例: '2週間'）",
      "tasks": ["string — タスク"]
    }
  ]
}
```

| フィールド | 制約 |
|-----------|------|
| phases | 3-5フェーズ |

### enterprise

#### security_compliance

```json
{
  "title": "string — アクションタイトル",
  "certifications": ["string — 認証名（例: 'SOC 2 Type II'）"],
  "securityFeatures": [
    {
      "icon": "string (opt)",
      "name": "string",
      "description": "string"
    }
  ]
}
```

#### ecosystem

```json
{
  "title": "string — アクションタイトル",
  "center": {
    "name": "string — 中心製品名",
    "icon": "string (opt)"
  },
  "partners": [
    {
      "category": "string — カテゴリ（例: 'Cloud', 'Database', 'Monitoring'）",
      "items": [
        {
          "name": "string",
          "icon": "string (opt) — クラウドアイコンパス"
        }
      ]
    }
  ]
}
```

#### support_sla

```json
{
  "title": "string — アクションタイトル",
  "tiers": [
    {
      "name": "string — プラン名",
      "features": ["string — 機能"],
      "sla": "string — SLA（例: '99.99%'）",
      "responseTime": "string — 応答時間",
      "highlighted": "boolean (opt) — 推奨プランフラグ"
    }
  ]
}
```

#### pricing

```json
{
  "title": "string — アクションタイトル",
  "plans": [
    {
      "name": "string — プラン名",
      "price": "string — 価格（例: '$500/月'）",
      "features": ["string — 含まれる機能"],
      "highlighted": "boolean (opt) — 推奨プランフラグ"
    }
  ],
  "footnote": "string (opt) — 注記"
}
```

### db-middleware

#### data_flow

```json
{
  "title": "string — アクションタイトル",
  "nodes": [
    {
      "name": "string",
      "type": "string — 'source' | 'process' | 'store' | 'output'",
      "icon": "string (opt) — クラウドアイコンパス"
    }
  ],
  "flows": [
    {
      "from": "string",
      "to": "string",
      "label": "string (opt)",
      "style": "string (opt) — 'solid' | 'dashed'"
    }
  ]
}
```

#### multi_cloud

```json
{
  "title": "string — アクションタイトル",
  "clouds": [
    {
      "provider": "string — 'aws' | 'gcp' | 'azure' | 'onpremise'",
      "services": [
        {
          "name": "string",
          "icon": "string (opt) — クラウドアイコンパス"
        }
      ]
    }
  ],
  "scalarLayer": {
    "components": ["string — Scalar コンポーネント名"]
  }
}
```

#### benchmark

```json
{
  "title": "string — アクションタイトル",
  "metrics": [
    {
      "name": "string — 指標名",
      "unit": "string — 単位",
      "results": [
        {
          "product": "string — 製品名",
          "value": "number",
          "isOurs": "boolean (opt)"
        }
      ]
    }
  ],
  "source": "string (opt) — ベンチマークソース"
}
```

#### migration_path

```json
{
  "title": "string — アクションタイトル",
  "from": {
    "name": "string — 移行元",
    "icon": "string (opt)"
  },
  "to": {
    "name": "string — 移行先",
    "icon": "string (opt)"
  },
  "steps": [
    {
      "name": "string — ステップ名",
      "description": "string (opt)",
      "duration": "string (opt)"
    }
  ]
}
```

---

## 3. 既存パターンとのマッピング

スライドタイプと `infographic-patterns.md` のコンポジットパターンの対応。

| スライドタイプ | 主要パターン | 補助パターン |
|-------------|------------|------------|
| title | — (COVER マスター独自) | — |
| agenda | Pattern 7 (Icon+Text Row) | — |
| section_divider | — (SECTION マスター独自) | — |
| summary | Pattern 8 (Stat Card) | Pattern 7 |
| closing | — (CLOSING マスター独自) | — |
| appendix | — (BLANK マスター独自) | — |
| text_bullets | — (テキスト直接配置) | — |
| columns | Pattern 9 (Comparison) | Pattern 7 |
| image_text | — (画像+テキスト分割) | — |
| chart | — (Sheets API 連携) | — |
| table | — (Table API 直接) | — |
| kpi_highlight | Pattern 8 (Stat Card) | — |
| process_flow | Pattern 10 (Flow) | Pattern 2 (Timeline) |
| quote | — (QUOTE マスター独自) | — |
| icon_grid | Pattern 7 (Icon+Text Row) | — |
| product_overview | Pattern 7 + Pattern 8 | — |
| architecture | Pattern 10/11 (Flow/Decision) | — |
| feature_matrix | — (Table 拡張) | — |
| feature_detail | Pattern 7 | — |
| tech_specs | — (Table 拡張) | — |
| competitive_compare | Pattern 9 (Comparison) | — |
| roadmap | Pattern 2 (H-Timeline) | — |
| usecase_overview | Pattern 7 | Pattern 6 (Pyramid) |
| problem_solution | Pattern 9 (Comparison) | — |
| case_study | Pattern 8 + テキスト | — |
| before_after | Pattern 9 (Comparison) | — |
| roi_impact | Pattern 8 (Stat Card) | — |
| deployment_steps | Pattern 2 (Timeline) | Pattern 10 (Flow) |
| security_compliance | Pattern 7 (Icon+Text) | — |
| ecosystem | Pattern 12 (Venn) | — |
| support_sla | Pattern 9 (Comparison) | — |
| pricing | Pattern 9 (Comparison) | — |
| data_flow | Pattern 10/11 (Flow) | — |
| multi_cloud | Pattern 10 + アイコン | — |
| benchmark | Pattern 4 (Bar Chart) | — |
| migration_path | Pattern 10 (Flow) | Pattern 2 (Timeline) |

---

## 4. テキスト制約サマリ

| 要素 | 日本語 | 英語 |
|------|--------|------|
| 表紙タイトル | 16文字 | 40文字 |
| アクションタイトル | 50文字 | 100文字 |
| セクションタイトル | 25文字 | 50文字 |
| 箇条書き1項目 | 40文字 | 80文字 |
| 箇条書き最大数 | 6項目 | 6項目 |
| カラム数 | 2-3列 | 2-3列 |
| テーブル列数 | 最大6列 | 最大6列 |
| テーブル行数 | 最大8行 | 最大8行 |
| KPI 数 | 2-4個 | 2-4個 |
| プロセスステップ | 3-5個 | 3-5個 |
| タイムラインマイルストーン | 4-8個 | 4-8個 |
| スピーカーノート | 200文字 | 400文字 |
