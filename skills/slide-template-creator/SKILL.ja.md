# スライドテンプレートの作成

*[English — normative skill](SKILL.md)*

この日本語文書は運用概要であり、実行時の正本は `SKILL.md` と
`references/workflow-contract.md` である。差異があれば英語版が優先する。

再利用可能な「1 枚のページ仕様」を 1 つずつ作る。Google Slides のマスターは
`templates/` に、内容レベルのテンプレートは `slide-templates/` に置く。

コマンドはすべて slide-forge のルートから `.venv/bin/python` で実行する。

## 境界

| 依頼 | 行き先 |
|---|---|
| 再利用可能な 1 枚もののパターンを作る・直す | このスキル |
| 分析フレームワークのテンプレート（PEST、ロジックツリー、パレートなど） | `analysis-template-creator` |
| ブランドカラー・フォント・ロゴ・マスター・レイアウトを作る | `template-forge` |
| デッキ全体を生成する | `google-slides` / `google-slides-template` |
| 生成済みスライドを目視で確認する | `slide-qa` |

スライドテンプレートは `template.json` と `example.json` の組で、
`slide-templates/manifest.json` に登録する。展開すると通常の slide-forge の
スライド 1 枚になるので、`scripts/assemble_spec.py` と組み合わせられる。

## 手順

### 1. インテイク

足りない情報だけを 1 度にまとめて聞く: そのスライドが伝えるべき問い、代表的な
入力データと想定される変化、投影用か読み物用かの密度、マスター間で可搬にするか
特定マスター専用にするか、元スライドやスクリーンショットの有無。

利用者所有の既存デッキを渡された場合は、実編集の前にスナップショットを取る。
デッキは調べるだけにして、テンプレートはローカルで組み直すほうがよい。稼働中の
デッキをテンプレートの登録先として使わない。

### 2. 足す前に探す

```bash
.venv/bin/python scripts/list_slide_templates.py
.venv/bin/python scripts/list_slide_templates.py --tag <term>
```

同じ問いに同じ視覚文法で答えている既存テンプレートがあれば、再利用するか拡張する。
必要なスロットや構造が実質的に異なるときだけ新しい ID を作る。

描画部品の選定は `references/primitive-selection.md`、ページ構造・密度・出典・
マスター可搬性は `references/design-rules.md` を読む。

### 3. 骨子を承認してもらう

編集前に、ID と表示名、答える問いと推論レベル、ページの骨格と意味のあるスロット、
再利用・新規のプリミティブ、プレビュー用のサンプル内容、解釈のガードレールを提示し、
承認を得る。**利用者が既に承認していない限り、このゲートを飛ばさない。**

### 4. テンプレートを書く

```text
slide-templates/<パック>/<id>/template.json
slide-templates/<パック>/<id>/example.json
```

を作り、`slide-templates/manifest.json` に登録する。スキーマの全体は
`references/template-schema.md` に従う。

`scripts/patterns.py` / `pages.py` / `charts.py` / `illustrations.py` の既存
プリミティブを優先する。新しいプリミティブを足すのは、同じ低レベル描画が繰り返され、
ドメイン入力に関数レベルの検証が要り、かつ 1 つのテンプレートから独立して名前を
付けて再利用できる場合に限る。

可搬なテンプレートは `BLANK` と `governing_message`、Canvas プリミティブ経由の
意味づけされたパレットトークン、10 × 5.625 インチの安全域を使う。マスターの
オブジェクト ID を参照したり、ブランドの RGB を直書きしたりしない。

### 5. オフラインで検証する

```bash
.venv/bin/python scripts/validate_slide_templates.py --id <id>
.venv/bin/python scripts/render_slide_template.py \
  --template <id> --data slide-templates/<パック>/<id>/example.json \
  --out out/<id>.json
```

検証器はレジストリ・スキーマ・入力の整合を見てから作例を描画し、
`build_deck.py --dry-run --strict` を走らせる。**監査の指摘はすべて潰す。**

### 6. 視覚 QA

カタログデッキの生成はオフライン検証の後に行う。全ページに `slide-qa` をかけ、
新しいスロット形状は代表入力と境界サイズの両方で試す。直すのはテンプレート・作例・
共有プリミティブであって、生成されたデッキではない。報告前に QA サムネイルを消す。

### 7. 報告

テンプレート ID・パック・パス、答える問いとスロット名、可搬かマスター専用か、
オフライン検証の結果、生成を許可された場合はカタログ URL と視覚 QA の結果、
新しいプリミティブや互換性の制約があればそれを報告する。

## 安全性と品質の規則

- テンプレートを埋めるために本番データを捏造しない。`example.json` は出典または
  注記で、自身がサンプルであることを明示する。
- 数値の主張には `source` スロットを必須にする。
- 記述・診断・予測・因果・戦略の主張を混ぜない。手法固有の注意は `guardrails` に書く。
- 宣言されていない入力スロットと、解決できないスロット参照は拒否する。
- 生成物と QA ファイルは gitignore された `out/` 配下に置く。
- 安定しているテンプレートの後方互換を保つ（`references/registration-and-compatibility.md`）。
