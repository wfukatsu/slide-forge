---
title: "feat: Add slide template creator skill"
type: feat
status: active
date: 2026-08-10
supersedes: docs/plans/2026-08-10-feat-marketing-analysis-slide-recipes-plan.md
---

# スライドテンプレート作成スキルの調査・実装計画

## 結論

`slide-template-creator` という新しいスキルを追加する。

このスキルが作るのはGoogle Slidesのマスターやレイアウトではなく、既存マスター上で再利用できる「1枚単位のスライドテンプレート」である。テンプレートは、単なる完成済みJSONではなく、以下を1組として登録する。

1. スライド仕様の雛形
2. 意味付き入力スロット
3. 入力制約と解釈上の注意
4. サンプルデータ
5. 対応レイアウト条件
6. オフライン検証結果
7. 目視確認用プレビュー

マーケティング分析テンプレートは、この汎用スキルを検証する最初のテンプレートパックとして実装する。スキル自体をマーケティング専用にはしない。

## 調査結果

### 1. 現在の `template` はマスター定義を意味する

`templates/*.json` はGoogle Slidesのマスター、layout、placeholder、paletteを登録するためのファイルである。`template-forge` もブランド付きマスターを作るスキルであり、今回の目的とは異なる。

したがって、1枚単位のテンプレートを `templates/` に保存すると用語と責務が衝突する。新しい保存先は `slide-templates/` とする。

### 2. 既存エンジンはスライドテンプレートの描画に十分近い

現在のJSON deck specは、1枚のスライドを次の要素で表現できる。

- `layout`, `title`, `subtitle`, `body`
- `figures[]`
- `scripts/build_deck.py::FIGURES` に登録された表、グラフ、図解、ページ部品
- `scripts/pages.py` のアクションタイトル、導入、示唆、出典

`scripts/assemble_spec.py` はページ単位のJSON断片を結合できるため、「テンプレートを展開した結果」をデッキへ組み込む処理には再利用できる。

不足しているのは、JSON断片へ安全に値を注入する仕組み、テンプレートの登録・検索、テンプレート単体の検証である。

### 3. 既存の検証基盤を流用できる

`build_deck.py --dry-run --strict` は、layout解決、placeholder整合、figure type、座標、重なり、文字溢れ、フッター侵入をオフラインで検証できる。

生成後の目視確認は `slide-qa` が担当している。したがって新スキルは独自のQA処理を複製せず、テンプレートのカタログデッキを生成して `slide-qa` に渡す。

### 4. スキルは共有正本とホスト別公開層を持つ

このリポジトリでは以下の構造になっている。

- `skills/<name>/SKILL.md`: CodexとClaude Codeが共有する正本
- `.agents/skills/<name>`: Codexの発見用リンク
- `.claude-plugin/marketplace.json`: Claude Codeプラグインへの登録
- `AGENTS.md`: リポジトリ内のスキルルーティング
- `.agents/skills/forge/SKILL.md`: エンドツーエンド生成時のルーティング

新スキルはすべての公開層に追加する必要がある。

OpenAI公式資料でも、繰り返し使うワークフローをSkillとして保存する用途が示されている。ローカルの `skill-creator` の指針に従い、`SKILL.md` は短い中核手順に絞り、詳細なスキーマと設計規約は `references/`、決定的な処理は `scripts/` に置く。

## スキルの責務

### 対象

- 新しい1枚単位スライドテンプレートの設計
- 既存スライドまたは画像からのテンプレート化
- 既存の描画primitiveを使ったテンプレート作成
- 必要な場合に限った新primitiveの追加
- 意味付きスロットと入力制約の定義
- テンプレートID、カテゴリ、検索タグの登録
- サンプル展開、dry-run、カタログ生成、目視QA
- 既存テンプレートの更新と回帰確認

### 対象外

- Google Slidesのマスター作成: `template-forge`
- 登録済みマスターからのデッキ生成: `google-slides-template`
- マスターなしのデッキ生成: `google-slides`
- 完成デッキの目視QA: `slide-qa`
- 分析計算、データ収集、事実調査そのもの
- ユーザー所有デッキへの直接書き込み

## 想定する利用例

新スキルのtriggerと受け入れテストには、少なくとも次を使う。

- 「SWOT分析用のスライドテンプレートを追加して」
- 「コホート継続率を見せる1枚の型を作って」
- 「この既存スライドを再利用可能なテンプレートにして」
- 「KPIダッシュボードのテンプレートを3種類作って」
- 「登録済みテンプレートの一覧を見せて」
- 「`cohort-retention` の入力項目を追加して更新して」
- 「マーケティング分析テンプレート一式をカタログ化して」

次の依頼ではtriggerしないようdescriptionに境界を書く。

- 「会社カラーのマスターを作って」
- 「この資料を20枚のデッキにして」
- 「生成済みデッキをQAして」

## 用語とデータモデル

### Slide template

特定の問いまたは伝達目的に対応する、1枚の再利用可能なページ仕様。例えば `swot-analysis`、`cohort-retention`、`before-after-process`。

### Slot

テンプレート利用者が差し替える意味付き入力。座標ではなく、`title`, `strengths`, `period_labels`, `values`, `source` のようなドメイン語で表現する。

### Primitive

`Canvas` 上で表、グラフ、図形を描く低水準部品。テンプレートから直接shapeを大量に並べるのではなく、既存または新しいprimitiveを利用する。

### Template pack

同一分野のテンプレート群。最初のpackは `marketing-analysis` とする。

## 保存形式

```text
slide-templates/
  manifest.json
  marketing-analysis/
    swot-analysis/
      template.json
      example.json
    three-c-analysis/
      template.json
      example.json
    cohort-retention/
      template.json
      example.json
```

1テンプレートを1ディレクトリにする。テンプレートの説明を別READMEにせず、`template.json` のメタデータとスキルのreferenceへ集約する。

### `template.json` 案

```json
{
  "schemaVersion": 1,
  "id": "cohort-retention",
  "displayName": "コホート継続率",
  "pack": "marketing-analysis",
  "category": "customer",
  "description": "獲得時期別の継続率を期間ごとに比較する",
  "answers": ["継続率は改善しているか", "悪化した獲得群はどれか"],
  "tags": ["cohort", "retention", "repeat"],
  "inferenceLevel": "diagnostic",
  "skeleton": "B",
  "compatibleLayouts": ["BLANK", "TITLE_ONLY"],
  "slots": {
    "title": {"type": "string", "required": true, "maxEm": 61},
    "cohortLabels": {"type": "string[]", "required": true, "maxItems": 12},
    "periodLabels": {"type": "string[]", "required": true, "maxItems": 12},
    "values": {"type": "number[][]", "required": true, "minimum": 0, "maximum": 1},
    "sampleSizes": {"type": "integer[]", "required": false},
    "source": {"type": "string", "required": true}
  },
  "guardrails": [
    "観測期間が異なる右下セルを単純比較しない",
    "母数が小さいセルは注記する"
  ],
  "slide": {
    "layout": "BLANK",
    "figures": []
  }
}
```

`slide` は既存deck specの1 slide objectと互換にする。ただし値は独自テンプレート文字列で直接置換せず、slot mappingを経由して展開する。

## 値の展開方式

### 推奨: slot mapping +限定された変換

任意コードやJinja式をtemplateへ埋め込まない。`template.json` が宣言したslotを、次の限定された操作でslide specへマッピングする。

- 値のそのまま代入
- 配列の繰り返し
- 数値の表示形式指定
- 条件付きの要素表示
- 色トークンへのマッピング

実装は `scripts/render_slide_template.py` に閉じ込める。

```bash
.venv/bin/python scripts/render_slide_template.py \
  --template cohort-retention \
  --data input.json \
  --out out/cohort-retention-slide.json
```

出力は既存 `scripts/assemble_spec.py` が読める1枚のJSON fragmentとする。これにより `build_deck.py` のschemaを二重化しない。

### 採用しない方式

- Pythonの `eval`
- template内の任意式
- `str.replace` によるJSONテキスト置換
- template固有のPython生成スクリプト

これらは入力型、エスケープ、検証、保守性の問題が大きい。

## スキル構成

```text
skills/slide-template-creator/
  SKILL.md
  agents/
    openai.yaml
  references/
    template-schema.md
    design-rules.md
    primitive-selection.md
    registration-and-compatibility.md
  scripts/
    # 原則として置かない。共有エンジンのscripts/を呼ぶ。
```

共有リポジトリの機能をskill内へ複製しない。skillの `scripts/` は、プラグイン単体配布上どうしても必要な薄いwrapperが判明した場合だけ追加する。

### SKILL.mdに残す内容

- scopeと他スキルへのrouting
- 作成フロー
- approval gate
- 既存テンプレート検索
- primitive追加判断
- dry-runとQAの必須順序
- 更新時のsource-of-truthルール
- 最終報告項目

### referencesへ分離する内容

- 完全なtemplate schema
- slot型一覧
- 6つのページ骨格と標準座標
- primitive選択表
- 分析・比較・プロセス・定量などのカテゴリ別設計規約
- master互換性ルール
- 命名・versioning・deprecationルール

## スキルのワークフロー

### Phase 1: Intake

未指定の項目だけを1回で確認する。

1. 何を伝えるスライドか
2. 代表的な利用依頼と入力データ
3. 登壇用か配布用か
4. 特定マスター専用か、マスター非依存か
5. 既存スライド、画像、参考資料の有無

### Phase 2: 重複調査

- `slide-templates/manifest.json` を検索する。
- 同じ `answers`、tag、構造を持つテンプレートを確認する。
- 既存テンプレートのvariantで足りる場合は新IDを作らない。
- `scripts/patterns.py`, `pages.py`, `charts.py`, `illustrations.py` の既存primitiveを検索する。

### Phase 3: Template outline approval

実装前に以下を提示し、承認を得る。

- template ID
- 答える問い
- スライド骨格
- 意味付きslot一覧
- 使用するprimitive
- サンプルプレビューの内容
- 解釈上のguardrail

これはデッキ生成におけるアウトライン承認と同等の必須ゲートとする。

### Phase 4: Author

- `template.json` と `example.json` を作る。
- 既存primitiveで表現できる場合は共有エンジンを変更しない。
- 新primitiveが必要な場合だけ、責務に応じて `patterns.py`、`charts.py`、または新しいdomain mixinへ追加する。
- `scripts/build_deck.py::FIGURES` とreferenceを同時に更新する。

新primitiveの追加条件:

- 既存primitiveでは20個以上の低水準shape記述が繰り返される。
- 入力配列の整合などを関数レベルで検証する必要がある。
- 複数テンプレートで再利用される。
- 一般化した関数名と入力契約を定義できる。

### Phase 5: Offline validation

```bash
.venv/bin/python scripts/validate_slide_templates.py --id <template-id>
.venv/bin/python scripts/render_slide_template.py \
  --template <template-id> --data <example.json> --out out/<id>.json
.venv/bin/python scripts/assemble_spec.py \
  --title "<displayName> preview" --out out/<id>-deck.json out/<id>.json
.venv/bin/python scripts/build_deck.py \
  --template templates/blank-16x9.json \
  --spec out/<id>-deck.json --dry-run --strict
```

validatorは次を確認する。

- ID、pack、category、tagの形式
- manifestとの整合
- slot型とrequired/defaultの整合
- templateが未宣言slotを参照していないこと
- exampleが全required slotを満たすこと
- 未置換slotが出力へ残らないこと
- 出力slideが既存deck specとして妥当なこと
- 数値を載せるtemplateにsource slotがあること
- compatible layoutの解決

### Phase 6: Catalog and visual QA

- pack単位のカタログdeckをmanifestから生成する。
- 新規・変更テンプレートを、blank masterと代表的な登録masterで生成する。
- `slide-qa` で実ピクセルを確認する。
- 修正は生成済みdeckではなく、template、example、primitiveへ戻す。
- `scripts/cleanup_qa.py` を実行する。

確認項目:

- タイトルと図が同じ結論を示す
- sample値が実データに見えない表示になっている
- slot最大値でも文字が収まる
- template装飾、footer、page numberと衝突しない
- paletteをハードコードせずmasterのPaletteを利用する
- source、単位、期間、母数が読める

### Phase 7: Register and report

- `slide-templates/manifest.json` に登録する。
- pack catalogを更新する。
- manifest全件を回帰検証する。
- template ID、用途、slot、プレビューdeck URL、対応master、QA結果を報告する。

## Manifestとライフサイクル

`slide-templates/manifest.json` はテンプレート検索の正本とする。

```json
{
  "schemaVersion": 1,
  "templates": [
    {
      "id": "cohort-retention",
      "displayName": "コホート継続率",
      "pack": "marketing-analysis",
      "category": "customer",
      "path": "marketing-analysis/cohort-retention/template.json",
      "tags": ["cohort", "retention"],
      "status": "stable",
      "version": 1
    }
  ]
}
```

ライフサイクル:

- `experimental`: slotや見た目が変更されうる
- `stable`: 後方互換を維持する
- `deprecated`: 代替IDを示し、即時削除しない

stable templateのslot削除・型変更はversionを上げる。表示上の微修正やguardrail追加は同一versionでよい。

## マスター互換性

テンプレートを次の2種類へ分ける。

### Portable

- 標準role (`BLANK`, `TITLE_ONLY`, `CONTENT`) のみ使用
- ページサイズ10×5.625インチを基準にする
- 色は `Canvas.Palette` のsemantic tokenを使用
- master固有object IDやRGB値を参照しない

### Master-specific

- 特定template IDとlayout roleを明記
- `compatibleTemplates` を必須にする
- 一般カタログではportableと区別する
- 元master変更時に回帰QA対象へ自動的に含める

初期実装はportable templateだけを対象にする。

## マーケティング分析packでの実証

汎用スキルのMVPを、次の8テンプレートでforward-testする。

1. `swot-analysis`
2. `three-c-analysis`
3. `market-sizing`
4. `positioning-map`
5. `rfm-segments`
6. `cohort-retention`
7. `conversion-funnel`
8. `experiment-result`

この組み合わせにより、次の異なるテンプレート特性を検証できる。

- 定性4象限
- 3要素関係図
- 入れ子構造
- 2軸マップ
- セグメントマトリクス
- ヒートマップ
- 段階変換
- 統計結果比較

## 実装フェーズ

### Phase 1: 契約とCLI

- [ ] `slide-templates/manifest.json` とschema versionを定義する。
- [ ] `scripts/list_slide_templates.py` を追加する。
- [ ] `scripts/render_slide_template.py` を追加する。
- [ ] `scripts/validate_slide_templates.py` を追加する。
- [ ] slot型、限定変換、エラー形式を決める。
- [ ] portable/master-specific互換性を定義する。

### Phase 2: 新スキル

- [ ] skill-creator付属の `init_skill.py` を使い `skills/slide-template-creator/` を初期化する。
- [ ] `SKILL.md`、`agents/openai.yaml`、4つのreferenceを作成する。
- [ ] `quick_validate.py` でskill構造を検証する。
- [ ] `.agents/skills/slide-template-creator` の相対symlinkを追加する。
- [ ] `AGENTS.md` のrouting tableを更新する。
- [ ] `.agents/skills/forge/SKILL.md` と `commands/forge.md` のroutingを更新する。
- [ ] `.claude-plugin/marketplace.json` のskills、説明、件数、versionを更新する。
- [ ] READMEのskill一覧、repository layout、Codex/Claude利用方法を更新する。

### Phase 3: マーケティング分析MVP

- [ ] 既存primitiveで作れる `market-sizing`, `positioning-map`, `conversion-funnel` を先に登録する。
- [ ] それらを使ってslot mappingとcatalog生成を検証する。
- [ ] 不足primitiveを最小単位で実装する。
- [ ] `swot-analysis`, `three-c-analysis`, `rfm-segments`, `cohort-retention`, `experiment-result` を追加する。
- [ ] 各templateにtemplate.json、example.json、guardrailを用意する。

### Phase 4: CatalogとQA

- [ ] `scripts/build_slide_template_catalog.py --pack marketing-analysis` を追加する。
- [ ] blank masterで全8枚をdry-runする。
- [ ] corporateなど代表masterでもdry-runする。
- [ ] preview deckを生成し全ページを目視QAする。
- [ ] slot上限値を使ったstress previewも生成する。
- [ ] QA後にローカルthumbnailを削除する。

### Phase 5: Forward testと改善

skill-creatorの指針に従い、実装後は新しい文脈で次を試す。

- 新しいテンプレートを既存primitiveだけで作れるか
- 既存スライドを抽象化し、意味付きslotへ変換できるか
- 類似テンプレートを重複登録せずvariantとして判断できるか
- データ不足時にサンプル値を実値として残さないか
- master作成依頼を `template-forge` へ正しくroutingできるか

並列agentの利用が許可されるセッションでは、独立したagentに実利用依頼として渡して評価する。許可されない場合は順次、クリーンな一時出力先で実行する。

## 受け入れ基準

### Skill

- [ ] `slide-template-creator` が具体的なtriggerで発見される。
- [ ] master作成、deck生成、QA依頼と誤triggerしない。
- [ ] SKILL.mdが500行未満で、詳細は直接リンクしたreferencesへ分離される。
- [ ] skill validatorが成功する。
- [ ] CodexとClaude Codeの双方から同じSKILL.mdを利用する。

### Template system

- [ ] template IDまたはtagから一覧・検索できる。
- [ ] 意味付きinput JSONから1枚のdeck fragmentを生成できる。
- [ ] 任意コードを実行せず、未宣言slotを拒否する。
- [ ] 出力fragmentを既存 `assemble_spec.py` と `build_deck.py` が処理できる。
- [ ] 全templateを一括検証できる。
- [ ] stable templateの破壊的変更を検出できる。

### Visual quality

- [ ] blank masterと代表masterでMVP 8枚がstrict dry-runを通る。
- [ ] sample入力と最大入力の双方で文字が収まる。
- [ ] preview catalogの全ページが目視QAを通る。
- [ ] 数値templateにsource、単位、期間の表示領域がある。
- [ ] portable templateがhard-coded RGBやmaster object IDを持たない。

## リスクと対策

| リスク | 対策 |
|---|---|
| masterとslide templateの混同 | ディレクトリ、skill名、routing、用語を分離する |
| template言語が複雑化する | 初期版の変換を代入、繰返し、形式指定、条件表示に限定する |
| deck specとの二重schema | 展開結果を既存の1 slide objectに固定する |
| 既存primitiveの無秩序な増加 | primitive追加条件をskillに明記する |
| masterごとの崩れ | portable/master-specificを分け、複数masterで検証する |
| sample値の納品混入 | exampleを別ファイルにし、未置換・sampleフラグを検証する |
| skillのcontext肥大化 | SKILL.mdを手順中心にし、schemaと設計規約をreferencesへ分離する |
| プラグイン登録漏れ | manifest、README、symlinkを受け入れ基準へ含める |

## 代替案

### JSON fragmentをそのままコピーするだけのスキル

実装は小さいが、差し替え対象、型、必須値、上限、sample値を検証できない。最初の試作には使えても、登録テンプレートとして長期運用できないため採用しない。

### テンプレートごとにPython関数を作る

自由度は高いが、検索、メタデータ、入力契約、後方互換性が分散する。描画primitiveだけPythonに置き、ページ構成は宣言的templateにする。

### テンプレートをskillのassetsに閉じ込める

skill単体としては自然だが、`build_deck.py`、catalog、他の生成skillからの利用が難しくなる。このリポジトリでは共有エンジン資産として `slide-templates/` に置く。

### 既存の `template-forge` を拡張する

マスター作成とページ構成作成は、入力、Slides API制約、検証、成果物が異なる。triggerの曖昧さも増すため別skillにする。

## 推奨実装順

1. 既存primitiveだけで作れる3テンプレートを手作業で試作する。
2. 試作からslot schemaとrendererの最小要件を確定する。
3. manifest、renderer、validator、list CLIを実装する。
4. `slide-template-creator` skillを初期化・記述・検証する。
5. 不足primitiveと残り5つのMVP templateを追加する。
6. catalog生成、複数master dry-run、目視QAを行う。
7. Codex/Claude公開層とドキュメントを更新する。
8. 実利用promptでforward-testし、triggerと手順を調整する。

この順序なら、テンプレート言語を先に過剰設計せず、実在する3つのパターンから必要な抽象化を導ける。

## 見積もり

- 試作とschema確定: 1〜2日
- renderer、validator、list CLI: 2〜4日
- skill本体と公開層統合: 1〜2日
- マーケティングMVP 8枚と不足primitive: 3〜5日
- catalog、複数master検証、QA、forward test: 2〜3日

合計は1名で約2週間を目安とする。

## 内部参照

- `skills/template-forge/SKILL.md` — master作成との境界
- `skills/google-slides/SKILL.md` — JSON spec生成と検証フロー
- `skills/slide-qa/SKILL.md` — 目視QAとsource-of-truthルール
- `scripts/build_deck.py:858` — figure registry
- `scripts/assemble_spec.py` — page fragmentの結合
- `scripts/diagrams.py:145` — Canvas mixin構成
- `references/template-schema.md` — 既存deck spec
- `references/slide-patterns.md` — 骨格6種と標準座標
- `references/validation.md` — offline/thumbnailの2段階検証
- `.claude-plugin/marketplace.json` — pluginへのskill登録
- `README.md` — Codex/Claudeのskill公開構成

## 外部参照

- OpenAI Developers, “Save workflows as skills” — 繰り返し使うワークフローをSkillとして保存するユースケース
- ローカル `skill-creator` — SKILL.md、agents/openai.yaml、progressive disclosure、init/validate/forward-testの標準手順

