# Account Planning ページテンプレート作成計画

`references/account-planning-session.md` の 34 ページを slide-forge で再現する
ための、ページテンプレート（`slide-templates/`）の設計・実装計画。

## 1. 目的とスコープ

**目的**: Account Planning Session の各ページを、顧客データを差し込むだけで
生成できる再利用可能なテンプレートとして登録する。さらに、**適用するスライド
マスターのデザインが変わってもテンプレート側を書き換えずに追従させる。**

**スコープに含む**: `slide-templates/account-planning/` パックの新規テンプレート
28 件（§4）、既存テンプレートの再利用判定、マスター追従の設計契約、検証手順。

> 実装の先行例: ある企業グループ向けの Account Planning デッキは
> `scripts/scalar/build_account_planning.py` が台帳から直接組んでいる。
> テンプレート化はまだだが、**各ページの座標・列幅・スロット構成は実生成と
> ビジュアル QA を通した実測値**なので、テンプレートを起こすときはそこから
> 写す。ゼロから座標を決め直さない。

**スコープに含まない**: スライドマスター（`templates/`）の作成 → `template-forge`。
デッキ生成そのもの → `google-slides-template`。台帳の設計 → `scalar-account-plan`。

## 2. マスターのデザインに追従させる設計

ここが本計画の中心。追従には性質の違う 3 つの層があり、それぞれ実現方法が違う。

### 2.1 現行機構でどこまで自動追従するか

slide-forge の分業は既にこうなっている:

```
 template.json          assemble_spec.py        build_deck.py --template <master>
 （ページの構造）    →   （デッキ仕様）      →   （マスターを適用して生成）
  layout: BLANK                                   colorScheme → colors.Palette
  figures: [...]                                  レイアウト・ロゴ・フッター
  色は意味で指定                                   フォント
```

`scripts/colors.py` の `Palette` は、**適用されたマスターの colorScheme から**
図解用の色を組み立てる:

| トークン | 由来 |
|---|---|
| `primary` | `accent5` |
| `success` / `danger` / `info` / `warning` | `accent1` / `accent2` / `accent3` / `accent4` |
| `text` / `muted` | `dark1` / `dark2` |
| `page` / `surfaceAlt` | `light1` / `light2` |
| `surface` / `border` | `primary` からの派生（明度演算） |
| `series(n)` | 上記からの固定順の系列色 |

**つまり L1（色・フォント）は、テンプレートが意味トークンだけを使っていれば
自動で追従する。** マスターを差し替える操作は `build_deck.py --template` の
引数を変えるだけで、テンプレートには一切触らない。

```bash
# 同じ spec を別マスターで生成する
.venv/bin/python scripts/build_deck.py --template templates/scalar-2026.json --spec out/ap/spec.json --dry-run --strict
.venv/bin/python scripts/build_deck.py --template templates/corporate.json    --spec out/ap/spec.json --dry-run --strict
.venv/bin/python scripts/build_deck.py --template templates/aixdevops.json    --spec out/ap/spec.json --dry-run --strict
```

### 2.2 追従の 3 層

| 層 | 何が変わるか | 実現方法 | 状態 |
|---|---|---|---|
| **L1 色・書体** | ブランド色、文字色、系列色、フォント | `Palette` の意味トークン経由で自動 | **実装済み** |
| **L2 レイアウト選択** | 表紙・中扉など、マスター固有レイアウトに載せる | `slide.layout` で選択。`compatibleLayouts` は**宣言のみで検証されない**（`scripts/` のどこからも参照されていない） | 部分的 |
| **L3 座標・密度** | ヘッダ／フッタ装飾の厚みが違うマスターで図の上下端を変える | `masterProfiles`（下記の提案） | **未実装 / 本計画で追加** |

### 2.3 L1・L2 で守る規約（全テンプレート必須）

- `slide.layout` は原則 `BLANK`。マスター固有レイアウトを使うのは、そのページ
  がマスターの装飾（表紙・中扉）に依存する場合だけ。その場合は
  `compatibleLayouts` に対応マスターのレイアウト名を列挙する。ただしこのキーは
  現状**人間向けの宣言でしかなく、ツールは検証しない**。実際の互換性は §2.5 の
  マスター横断検証で担保する。
- **ブランド RGB のハードコード禁止。** `#0B5FFF` のような直値を
  `template.json` に書かない。Canvas プリミティブに意味トークンを渡す。
- **マスターのオブジェクト ID を参照しない。** `g1b3a74d17bb_0_0` のような ID を
  テンプレートに書かない。
- ページサイズは 10 × 5.625 in（16:9）を前提にする。
- 安全域は `references/layout-contract.md` の実測値に従う:

  ```
  X0 = 0.5   W = 9.0   XE = 9.5
  タイトル       y 0.42 〜 0.48（1 行厳守）
  図の描画領域   y 0.84 〜 4.30（DY0 / DY1）
  要点行         y 4.38（NY）
  出典・補足行   y 4.86（EY）
  y 5.197 以降   マスターのロゴ・フッター領域。触らない
  ```

- タイトルは全角換算 30.5 文字以内（`deckkit.em()` で測れる）。2 行になると
  `DY0` を越えて図と重なる — 最も多い崩れ方。
- 日本語と英語の両方で代表文字列を検証する。日本語の方が全角幅で先に溢れる。
- **表の列幅は 0.45in（32pt）以上。** Slides API は 32pt 未満の列を
  `updateTableColumnProperties` で拒否する。`--dry-run` では検出できず、実生成
  で初めて 400 が返る。番号列のような細い列を作るときに踏む。

`slide_templates.py` の検証にこの下限が入るまでは、テンプレート側で
`colWidths` の合計と幅から実寸を出して自分で検査すること
（`scripts/scalar/build_account_planning.py` の `table()` が実装例）。

### 2.4 L3 の提案: `masterProfiles`

同じ 10 × 5.625 in でも、マスターによって上部の装飾帯やフッターの厚みが違う。
現行スキーマは 1 テンプレート = 1 ジオメトリなので、装飾が厚いマスターでは図が
食い込む。これを吸収するために、**後方互換の追加キー**を提案する。

```jsonc
{
  "id": "blueprint-map",
  "slide": {                       // 既定ジオメトリ（従来どおり。必須）
    "layout": "BLANK",
    "figures": [ /* ... */ ]
  },
  "masterProfiles": {              // 任意。マスター名 → 差分パッチ
    "corporate": {
      "figures": {
        "1": { "y": 1.75 },        // インデックス指定で該当 figure のキーだけ上書き
        "3": { "y": 4.70 }
      }
    }
  }
}
```

必要な変更:

| ファイル | 変更内容 |
|---|---|
| `scripts/slide_templates.py` | `render_template(template, data, master=None)` に引数追加。`masterProfiles[master]` を `slide` に深いマージしてからスロット解決する。`master` 未指定なら現行と完全に同じ挙動 |
| `scripts/render_slide_template.py` | `--master <name>` を追加（省略時は既定ジオメトリ） |
| `scripts/validate_slide_templates.py` | 宣言された全プロファイルについてレンダリング → `build_deck.py --dry-run --strict` を実施。未登録マスター名、既定に存在しない figure インデックスへの参照はエラー |
| `references/template-schema.md` | `masterProfiles` の節を追加 |

設計上の制約:

- `masterProfiles` は **ジオメトリと密度パラメータ（`x` / `y` / `w` / `h` /
  `size` / `rowH` / `colWidths`）に限定する。** figure の追加・削除・型変更は
  認めない。認めるとテンプレートが分岐して保守できなくなる。
- 色は書けない（L1 で自動追従するため、書く必要がない）。
- プロファイルを持たないマスターでは既定ジオメトリが使われる。

**代替案（L3 を実装しない場合）**: 全テンプレートを最も装飾の厚いマスターの
安全域に合わせて作る。実装コストはゼロだが、装飾の薄いマスターで余白が過剰に
なる。28 テンプレートすべてに効くので、F2 で実装する価値がある（§6）。

### 2.5 マスター横断の検証を CI 的に回す

`validate_slide_templates.py` は `--deck-template` で**検証に使うマスターを
差し替えられる**（既定は `templates/blank-16x9.json`）。マスター追従の回帰は
この 1 本で回せる。

```bash
# パック全体を、マスターを変えながら検証する
for m in blank-16x9 scalar-2026 corporate aixdevops; do
  echo "== $m"
  .venv/bin/python scripts/validate_slide_templates.py \
    --pack account-planning --deck-template "templates/$m.json" || exit 1
done
```

**dry-run が通ることは「崩れていない」ことの証明ではない。** 実生成 →
サムネイル目視（`slide-qa`）まで通して初めて完了とする。少なくとも
`scalar-2026` と、色調が最も遠いマスター 1 つで目視する。

## 3. 既存資産の再利用判定

新規 ID を作る前に必ず確認する:

```bash
.venv/bin/python scripts/list_slide_templates.py
.venv/bin/python scripts/list_slide_templates.py --tag account
```

| AP ページ | 既存候補 | 判定 |
|---|---|---|
| SWOT Analysis | `marketing-analysis/swot-analysis` | **そのまま再利用** |
| Influence Map | `b2b-sales/influence-map`, `influence-map-org` | **そのまま再利用**。組織階層が取れているなら `-org` |
| Action Plan | `scalar-ae/action-plan` | **そのまま再利用**。列が S.M.A.R.T. と対応するか確認のみ |
| Prioritization（2 軸） | `marketing-analysis/positioning-map` | **要検証**。バブル径＝3 年ポテンシャル金額が表現できれば再利用、できなければ `prioritization-matrix` を新規 |
| Blueprint Summary | `scalar-ae/challenge-hypothesis` | **新規**。課題仮説 1 枚とは項目数が違いすぎる（15 欄 vs 5 欄） |
| Vision/Strategy for Growth | `scalar-ae/win-plan` | **新規**。win-plan は個別案件の勝ち筋、こちらはアカウント 3 年の成長ビジョン |
| Challenges & Risk | `scalar-ae/bant-risk` | **新規**。BANT の 4 軸に限定されない汎用の課題×緩和策。bant-risk は置き換えない |
| 3 Year Execution Plan | `scalar-ae/activity-timeline` | **新規**。activity-timeline は過去の活動履歴、こちらは未来 3 年のマイルストーン |
| Account Health | — | 新規 |
| Strategy Map | `b2b-sales/discovery-map-tree` | **要検証**。階層ツリーのプリミティブが流用できる可能性。テンプレートは新規 |

判定基準: 「同じ問いに、同じ視覚文法で答えるか」。答えが Yes なら再利用、
スロットか視覚構造が実質的に違うときだけ新規 ID を作る。

## 4. 新規テンプレート仕様（28 件）

パック名: `account-planning`。全件 `schemaVersion: 1`、`status: experimental`、
`compatibleLayouts: ["BLANK"]` を既定とする。

全テンプレート共通のスロット:

| スロット | 型 | 必須 | 説明 |
|---|---|---|---|
| `title` | `string` (≤70) | ○ | 結論を書くタイトル。トピック名を置かない |
| `source` | `string` (≤160) | 数値を含む場合 ○ | 出典・期間・単位・為替前提 |

### P0 — Session 資料の 9 枚を成立させる（9 件）

#### 4.1 `corporate-overview` — 企業概要
- 答える問い: この顧客はどんな会社で、経営として何を課題にしているか
- `inferenceLevel`: `descriptive`
- スキル骨格: D（上下 2 段）。上段にプロファイル＋事業概要、下段に経営課題
- スロット: `profile` `tuple[]`（項目名・値、4〜8）／ `description` `string`
  (≤240)／ `challenges` `string[]`（3〜5、各 ≤80）／ `competitors` `string[]`
  （0〜6）／ `exec_quotes` `tuple[]`（発言者・発言、0〜3）
- guardrails: 経営層の発言は出典（決算説明会・記事など）と時期を明示する／
  プロファイル欄だけ埋まった状態は未完成

#### 4.2 `strategy-map` — 顧客の経営戦略マップ
- 答える問い: 顧客の Goal / Strategy / Tactic / Initiative はどう連なっているか
- `inferenceLevel`: `strategic`
- 骨格: A（全幅）。3〜4 層の階層ツリー、各ノードに要求元ロールのラベル
- スロット: `layers` `string[]`（層名、3〜4）／ `nodes` `array`（[層 index,
  ラベル, 要求元ロール, 確度]、6〜24）／ `edges` `array`（[親 index, 子 index]）
- guardrails: 仮説ノードは `確度 = "hypothesis"` にして視覚的に区別する／
  イニシアチブは顧客の公開情報か発言に紐づくもののみ `confirmed`
- 依存: 階層ツリーのプリミティブ（`discovery-map-tree` の流用可否を先に検証）

#### 4.3 `footprint-heatmap` — 導入状況ヒートマップ
- 答える問い: レイヤごとに今どこまで入っていて、3 年後どこまで狙うのか
- `inferenceLevel`: `descriptive`
- 骨格: A。行＝レイヤ、列＝現状 → 3 年後（矢印）、イニシアチブ紐付け、競合メモ
- スロット: `rows` `array`（[レイヤ名, 現状 0-2, 3年後 0-2, イニシアチブ番号列,
  メモ]、4〜10）／ `legend` `string[3]`（既定: 全社標準 / 足がかりあり / 未進出）
- guardrails: 3 値は 全社標準 / 足がかりあり・伸長中 / ほぼ未進出 の 3 段階のみ／
  評価は社内の製品担当・SC への照会で裏を取る

#### 4.4 `initiative-solution-alignment` — イニシアチブ × ソリューション
- 答える問い: 顧客のどのイニシアチブに、自社の何がどう効くのか
- `inferenceLevel`: `strategic`
- 骨格: A。3 段の帯（顧客イニシアチブ → 提供価値 → 主要商談機会）を縦に対応
- スロット: `initiatives` `string[]`（3〜6、各 ≤40）／ `capabilities`
  `string[][]`（イニシアチブごとの提供価値、各 1〜3）／ `opportunities`
  `string[][]`（同、各 0〜3）
- guardrails: 製品名だけの列は不可。顧客課題に対応する価値を書く

#### 4.5 `blueprint-map` — 提案テーマ一覧
- 答える問い: 狙うテーマは何で、いくらで、いつか
- `inferenceLevel`: `strategic`
- 骨格: F（表のみ）
- スロット: `headers` 固定（テーマ名 / 顧客課題 / ソリューション案 / 製品 /
  なぜ自社か / 時期 / 金額）／ `rows` `string[][]`（3〜7 行、7 列、各セル ≤60）
- guardrails: 顧客課題が空の行は載せない／金額は単位と根拠を `source` に書く／
  Close はテーマの合意成立であって受注ではない

#### 4.6 `initiative-prioritization` — 優先順位スコア表
- 答える問い: どのイニシアチブから取りにいくのか、その根拠は何か
- `inferenceLevel`: `strategic`
- 骨格: F
- スロット: `headers` 固定（イニシアチブ / 目的・期待価値 / 意思決定ステージ /
  キーパーソン / 自社のアライン / 3 年ポテンシャル / 顧客側優先度）／ `rows`
  `string[][]`（3〜7 行、7 列）
- guardrails: キーパーソンはスポンサー・影響者・決裁者を役割付きで書く／
  顧客側優先度は顧客の発言に基づく場合のみ「高」を付ける／社内限定

#### 4.7 `execution-roadmap` — 3 年実行計画
- 答える問い: 3 年で、いつ何を起こすのか
- `inferenceLevel`: `predictive`
- 骨格: A。横軸に期（12 四半期または 3 年）、行にテーマ、マイルストーンを配置
- スロット: `periods` `string[]`（4〜12）／ `tracks` `string[]`（2〜6）／
  `milestones` `array`（[track index, period index, ラベル, 種別]）
- 種別: イベント / 役員招聘 / インサイト / 共同検討 / ロードマップ策定 /
  案件クローズ
- guardrails: 予測であって確定ではない旨をスライド上に残す

#### 4.8 `account-strategy-summary` — 3 年アカウント戦略サマリー
- 答える問い: 現状から 3 年後へ、何をどこまで動かすのか
- `inferenceLevel`: `strategic`
- 骨格: D。上段に 3 年戦略ステートメントと主要変革テーマ、下段に現状 / 3 年後の
  対比
- スロット: `strategy_statement` `string` (≤200)／ `themes` `string[]`（2〜5）／
  `dimensions` `string[]`（3〜5、既定: 売上 / 顧客満足 / エンゲージメント /
  フットプリント）／ `current` `string[][]`（`matchLength: dimensions`）／
  `target` `string[][]`（同）
- guardrails: **`current` と `target` は同じ項目立て・同じ順序でなければならない**
  （`matchLength` で強制）

#### 4.9 `management-asks` — 経営への依頼事項
- 答える問い: 経営層に何をしてほしいのか、それで何が動くのか
- `inferenceLevel`: `strategic`
- 骨格: F
- スロット: `headers` 固定（依頼先 / 依頼内容 / なぜ必要か / 期待される成果 /
  期限）／ `rows` `string[][]`（1〜5 行、5 列）
- guardrails: 期待成果が空の行は Ask として成立しない／社内限定

### P1 — Plan Document を埋める（7 件）

#### 4.10 `account-health` — アカウント健全性
- 4 側面 × 5 指標のスコアカード＋四半期トレンド。骨格 B
- スロット: `dimensions` `string[4]`／ `metrics` `string[4][5]`／ `scores`
  `integer[4][5]`（1〜3）／ `trend` `array`（[四半期, 総合スコア]、2〜8）
- guardrails: 全指標が中央値で並ぶ評価は評価をしていない／判定基準は別ページに置く

#### 4.11 `tam-sow-analysis` — TAM と SOW
- カテゴリ別 TAM と SOW のベースライン／目標。骨格 B（左に棒、右に読み筋）
- スロット: `categories` `string[]`（2〜6）／ `tam` `number[]`
  (`matchLength: categories`)／ `sow_baseline` `number[]`／ `sow_target`
  `number[]`／ `annual_revenue` `string`／ `it_spend` `string`
- guardrails: TAM は推計。実 IT 予算の開示があれば置き換え、その旨を `source` に

#### 4.12 `historical-spend` — 過去実績
- 過去 3 年の製品別実績。骨格 B（積み上げ棒＋読み筋）
- スロット: `periods` `string[]`（2〜5）／ `series` `array`（[製品名, 値列]、
  1〜6、値列は `matchLength: periods`）／ `recurring_note` `string`
- guardrails: 年額換算のサブスクリプション額を一括売上と足し合わせない

#### 4.13 `growth-vision` — 成長ビジョン
- 4 領域の記述。骨格 F または C
- スロット: `areas` `tuple[]`（[領域名, 記述]、3〜5、記述 ≤200）
- 既定の領域名: 顧客の変革目標へのアライン / 自社重点領域のポジショニング /
  フットプリント拡張 / Executive Engagement

#### 4.14 `blueprint-summary` — テーマ詳細 1 枚
- 1 テーマの 15 欄。骨格 F（3×5 のセルグリッド）
- スロット: `blueprint_name` `string`／ `cells` `tuple[]`（[欄名, 内容]、
  固定 15 件）
- 欄: 顧客の変革課題 / ソリューション概要 / 製品・重点施策 / 差別化要因 /
  ベネフィット / 関与ロール / 重点施策 / パートナー / 参照事例 / 開始日 /
  クローズ予定 / 事業側スポンサー / IT スポンサー / 対象事業部 / 現行パイプ・
  3 年ポテンシャル・競合
- guardrails: Close はテーマ合意の成立であり受注ではない／ステージが進むほど
  記述の精度を上げる

#### 4.15 `exec-engagement-plan` — 役員エンゲージメント計画
- 骨格 F。列: レベル / 顧客側役員 / 自社側役員 / 頻度・実施日 / 現状とゴール
- `rows` `string[][]`（2〜8 行、5 列）
- guardrails: 実名を含む。社内限定。顧客・パートナーに渡さない

#### 4.16 `event-plan` — イベント計画
- 骨格 F。列: イベント / 時期 / 対象顧客 / 自社側キーパーソン / 得たい成果
- `rows` `string[][]`（2〜8 行、5 列）

### P0b — 元資料との突き合わせで追加（9 件）

初版の 23 ページを `FY17_AP_Template_Training_Public.pptx` と 1 ページずつ
突き合わせて見つかった不足分。先行実装では
`scripts/scalar/build_account_planning.py` に実装済みで、**そのページ定義が
テンプレート化するときの参照ジオメトリになる**。

| ID | 元資料 | 何を足すか |
|---|---|---|
| `customer-initiatives` | S44 | イニシアチブ × **顧客側オーナー** × 目的・アウトカム × **緊迫性を生む要因** |
| `customer-programs` | S45 | イニシアチブとテーマの間の**顧客プログラム / プロジェクト層**。実在する名前で書く |
| `strategy-map-step2` | S38 / S41 | Step 1 と**同じマップの上に**提案テーマを重ねる。`outcome_tree` に 4 段目を足すだけで済む |
| `objective-sheet` | S60 / S99 | テーマごとの Customer Benefit / 当社の貢献 ＋ **年ごとの「結果」**（活動ではない） |
| `challenge-requirement` | S77 / S105 | Challenge / Requirement / Owner / **期日** / Outcome |
| `health-criteria` | S31 / S32 | Account Health の各段階の判定基準。スコアだけでは検証できない |
| `financial-trends` | S81 | 顧客の業績推移と同業比較。`metric` ×3 ＋ `hbars` |
| `engagement-timeline` | S59 / S98 | **週単位 8 週**の線表。半期の `gantt` では次の関門に間に合うか判断できない |
| `scalar-footprint` | S84 | 製品 4 つ（ScalarDB / Saga / Analytics / ScalarDL）を `layers`、ソリューション 4 つ（AI 駆動開発 / RAG / AI 向けデータカタログ / マルチクラウド基盤）を `cards` で並べ、**提示状況**を添える |
| `group-orgchart` | S80 | 顧客グループの公式組織図に当社の接点を重ねる |
| `jri-orgchart` | S84 | IT 子会社の公式組織図。**接点のない部署が見えることが価値** |
| `deal-portfolio` | S45 | グループ会社別の商談ポートフォリオ（`mece_tree`） |
| `company-stakeholders` | S27 | グループ会社別の関与者（`comparison`）。名刺のみは接触に数えない |
| `subsidiary-mapping` | S84 | システム子会社 ↔ グループ各社の担当マッピング（`comparison`）。横断組織と会社別実装部隊を分ける |
| `deal-detail` | S51 / S52 | 商談 1 件の全体像（`cards` 6 枚）。商談ごとの章の本体 |

あわせて既存ページに足した欄:

- **Heatmap**: 紐づくイニシアチブ番号と「競合・前提」列（S26）。ドットだけでは
  評価の根拠が書けないので `rating_matrix` を `table` に置き換えた
- **Executive Engagement Plan**: **当社側の役員カウンターパート**列（S64）。
  空欄なら空欄と書く。Management Asks への起票がそこから出る
- **Action Plan**: 割当日と期日（S62）。テーマ番号で Blueprint に紐づける
- **Management Asks**: 期日
- **TAM & SOW**: 顧客の年間収益と主要競合（S22 / S69）
- **Corporate Overview**: 主要競合（S80 の KEY COMPETITORS）
- **Blueprint Summary**: 1 テーマ 1 ページ。まとめて 1 枚にしない

### P0c — 表から図への置き換え

表が続くとページの見た目が同じになり、要点が沈む。**表は「登録簿」（担当と
期日があり後から追跡するもの）と「判定基準」だけに残す。** 対応表は
`references/account-planning-session.md` §9.3。

先行実装では 20 表 → 8 表に減らし、次の図に置き換えた:
`orgchart` / `outcome_tree` / `mece_tree` / `layers` / `gantt` / `timeline` /
`nested_circles` / `hbars` / `cards` / `journey` / `before_after` /
`influence_graph`。テンプレート化するときも同じ割り当てを使う。

**公式組織図は必ず一次情報から取る。** 顧客の IR / 会社情報ページにある
組織図（PDF・PNG）を読み、当社の接点を重ねる。台帳の肩書きだけで組織図を
描き起こすと、接点のない部署が図から消えてしまい、**空白が見えないという
一番大事な情報を失う**。

意図的に採らなかったもの: **Create / Evolve / Protect 分類**（S47）は
フットプリントが全レイヤ 0 のあいだ全部 Create にしかならず縮退する。
**Appendix の空テンプレート集**（S79）は生成スクリプトがあるため不要。

### P2 — あると議論が速い（3 件）

#### 4.17 `flight-plan` — フライトプラン
- 横軸＝クローズ時期、縦軸＝金額、バブル＝テーマ、色＝ステータス。骨格 A
- スロット: `bubbles` `array`（[テーマ名, 期 index, 金額, ステータス]、2〜10）／
  `periods` `string[]`／ `statuses` `string[3]`
- guardrails: 予測。確定案件と区別できる凡例を必ず置く

#### 4.18 `revenue-projection` — 3 年財務見通し
- 骨格 B。年別・カテゴリ別のポテンシャル
- guardrails: 年額換算値は別集計。前提（為替・期・単位）を `source` に明記

#### 4.19 `risk-mitigation` — 課題とリスク緩和
- 骨格 F。列: 課題 / 影響 / 緩和策 / 担当
- `rows` `string[][]`（2〜8 行、4 列）
- guardrails: `scalar-ae/bant-risk` を置き換えない。BANT に収まるリスクは
  そちらを使う

## 5. 新規プリミティブの判定

`scripts/patterns.py` / `pages.py` / `charts.py` / `illustrations.py` に既にある
ものを優先する。**新規プリミティブを足すのは 3 条件をすべて満たすときだけ**:
同じ低レベル描画が複数テンプレートで繰り返される、ドメイン入力に関数レベルの
検証が要る、1 テンプレートと独立に名前を付けて再利用できる。

| 候補 | 使うテンプレート | 判定 |
|---|---|---|
| 階層ツリー（層ラベル付き） | `strategy-map` | `discovery-map-tree` の実装を先に読む。流用可なら新規不要 |
| 3 値ヒートマップ行（現状→将来の矢印付き） | `footprint-heatmap` | **新規候補**。2 テンプレート以上で使う見込みが立ってから追加 |
| 現状 / 目標の対比パネル | `account-strategy-summary`, `growth-vision` | **新規候補**。2 件で使うので条件を満たす |
| バブルチャート（3 変数＋カテゴリ色） | `flight-plan`, （`positioning-map` 拡張） | **要調査**。`positioning-map` の実装で足りる可能性 |
| セルグリッド（欄名＋内容の格子） | `blueprint-summary` | 1 件のみ。`table` で代替できるか先に試す |

## 6. 実装フェーズ

| フェーズ | 内容 | 成果 |
|---|---|---|
| **F0** 調査 | `discovery-map-tree` / `positioning-map` / `action-plan` の実装を読み、流用可否を確定。§3 の「要検証」を解消 | 再利用判定表の確定版 |
| **F1** P0 テンプレート 9 件 | 表・帯・対比パネル系（4.4〜4.6、4.8、4.9）から着手。図解系（4.2、4.3、4.7）は F0 の結論待ち | Session 資料 9 枚が生成できる |
| **F2** L3 `masterProfiles` | §2.4 の 4 ファイル変更。F1 の 9 件を最初のプロファイル対象にする | マスター差分をテンプレートで吸収できる |
| **F3** P1 テンプレート 7 件 | Plan Document 側 | Appendix が埋まる |
| **F4** P2 テンプレート 3 件 | Flight Plan など | 議論用の可視化がそろう |
| **F5** カタログとドキュメント | パックカタログを生成し、`skills/scalar-account-plan/SKILL.md` から参照を張る | 運用に載る |

F1 と F2 は独立。F2 を待たずに F1 を出せる（既定ジオメトリだけで動く）。

## 7. 受け入れ基準

各テンプレートは、以下をすべて満たして初めて `status` を `experimental` から
上げる。

- [ ] `scripts/validate_slide_templates.py --id <id>` が指摘ゼロで通る
- [ ] `example.json` が全必須スロットを埋め、宣言した上限内に収まる
- [ ] `example.json` の `source` に **サンプルデータである旨が明記**されている
- [ ] 数値を含むテンプレートに `source` スロットがある
- [ ] `answers`（答える問い）と `inferenceLevel` が宣言されている
- [ ] `guardrails` に、そのページで最も起きやすい誤読が書かれている
- [ ] スロットの最小・最大で生成しても崩れない（境界値テスト）
- [ ] 日本語・英語の代表文字列の両方で崩れない
- [ ] `scalar-2026` と、色調が最も遠いマスター 1 つの **両方**でサムネイル目視
      を通す（文字あふれ / 重なり / コントラスト / フッター衝突）
- [ ] ブランド RGB 直値とマスターオブジェクト ID を含まない（grep で確認）

## 8. 検証手順

```bash
# 単体
.venv/bin/python scripts/validate_slide_templates.py --id blueprint-map
.venv/bin/python scripts/render_slide_template.py \
  --template blueprint-map \
  --data slide-templates/account-planning/blueprint-map/example.json \
  --out out/blueprint-map.json

# パック一括（マスター横断。§2.5）
for m in blank-16x9 scalar-2026 corporate aixdevops; do
  .venv/bin/python scripts/validate_slide_templates.py \
    --pack account-planning --deck-template "templates/$m.json" || exit 1
done

# カタログ
.venv/bin/python scripts/build_slide_template_catalog.py \
  --pack account-planning --out out/account-planning-catalog.json

# 実生成 → ビジュアル QA → 後始末
.venv/bin/python scripts/build_deck.py \
  --template templates/scalar-2026.json --spec out/account-planning-catalog.json \
  --title "Account Planning テンプレートカタログ"
# skills/slide-qa/SKILL.md に従って目視
.venv/bin/python scripts/cleanup_qa.py
```

崩れを見つけたら **生成物ではなくテンプレート・example・共有プリミティブを
直して再生成する。** 生成されたスライドを手で直さない。

## 9. 安全性

- `account-planning` パックには、`initiative-prioritization`、
  `exec-engagement-plan`、`management-asks`、`account-health`、`risk-mitigation`
  のように **個人の実名と、その人物に対する社内判断**を含むページがある。
  これらの `guardrails` に「社内資料。顧客・パートナーに渡さない」を必ず書く。
- 顧客データは `accounts/` 配下に置く。`accounts/` は Git 管理外。テンプレートの
  `example.json` に実在顧客のデータを入れない。
- `example.json` は必ず架空データとし、`source` でサンプルであることを宣言する。

## 10. 未決事項

| # | 論点 | 決める人 | 期限の目安 |
|---|---|---|---|
| 1 | `masterProfiles`（L3）を実装するか、最厚マスターに合わせる代替案で済ませるか | — | F1 完了時 |
| 2 | `positioning-map` を Prioritization 2 軸に流用できるか（バブル径＝金額） | — | F0 |
| 3 | `discovery-map-tree` の階層プリミティブを `strategy-map` に流用できるか | — | F0 |
| 4 | Session 資料の既定ページ数を 9 で固定するか、アカウント規模で可変にするか | — | F1 |
| 5 | `account-planning` パックを `scalar-ae` に統合するか、独立パックのままにするか | — | F5 |
| 6 | `compatibleLayouts` を validator で強制するか、宣言のままにするか | — | F2 |

## 11. 参照

- `references/account-planning-session.md` — 手順とページ定義
- `skills/slide-template-creator/SKILL.md` — テンプレート作成のワークフロー
- `skills/slide-template-creator/references/template-schema.md` — スキーマ
- `skills/slide-template-creator/references/design-rules.md` — 骨格・密度・出典
- `references/layout-contract.md` — 座標の実測値と安全域
- `references/slide-patterns.md` — 骨格 A〜F の定義
- `scripts/colors.py` — `Palette`（マスター colorScheme → 意味トークン）
- `scripts/scalar/build_account_planning.py` — 実装済みのページ定義（参照ジオメトリ）
