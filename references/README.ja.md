*[English](README.md)*

# references/ — 何が置いてあるか

下記のファイルは、注記のあるものを除き、すべて `<name>.md`（英語）と
`<name>.ja.md`（日本語）の対で存在する。やることに合う節から入ればよく、
このディレクトリを通しで読むようには作られていない。

## まずここから

| ファイル | 何のためのものか |
|---|---|
| [commands.md](commands.ja.md) | 3 つのスラッシュコマンド — `/forge`・`/account`・`/visit`。slide-forge を**使いたい**ならここから（中身を変えるのではなく） |
| [workflow-contract.md](workflow-contract.ja.md) | デッキ生成をエンドツーエンドで動かすための共通契約。どのホストの動き方を変えるときも、まずこれを読む。正本は英語版 |
| [interactive-intake.md](interactive-intake.md) | 仕様を書く前に、テンプレート・目的・構成・分量をユーザーと確定させる手順 |
| [validation.md](validation.md) | 2 つのゲート — オフラインの座標検査と、サムネイル QA。それぞれ何を拾えて何を拾えないか |
| [parallel-generation.md](parallel-generation.md) | 大きなデッキをページ単位に分割して作る（並列／逐次） |
| [codex-compatibility.md](codex-compatibility.ja.md) | Codex ホストでの差異とセットアップ。正本は英語版 |

## デッキを書く

| ファイル | 何のためのものか |
|---|---|
| [deck-outlines.md](deck-outlines.ja.md) | 「どの図を描くか」の前に来る「どの順で話すか」。標準的なデッキ構成 |
| [composers/](composers/) | デッキ種別ごとのページ構成ガイド: [basic](composers/basic.ja.md)、[content](composers/content.ja.md)、[product](composers/product.ja.md)、[usecase](composers/usecase.ja.md)、[db-middleware](composers/db-middleware.ja.md)、[enterprise](composers/enterprise.ja.md) |
| [slide-patterns.md](slide-patterns.ja.md) | 1 ページの組み方 — 骨格 × 中身、`PageMixin` の部品 |
| [template-schema.md](template-schema.ja.md) | `template.json` とデッキ仕様の構造 |
| [settings.md](settings.ja.md) | `config/settings.json` — 画像生成と成果物の出力先 |

## カタログ — 見てから選ぶ

| ファイル | 何のためのものか |
|---|---|
| [slide-pattern-catalog.md](slide-pattern-catalog.ja.md) | 52 のページパターン。各項目にレンダリング画像つき。生成物 |
| [slide-template-catalog.md](slide-template-catalog.ja.md) | 101 の 1 枚ものテンプレート。画像・**入力**表（スロット / 型 / 必須 / 制約）・ガードレールつき。生成物 |

## 図を描く（`scripts/` のエンジン）

| ファイル | 何のためのものか |
|---|---|
| [diagrams.md](diagrams.ja.md) | `Canvas` 本体 — 描画規約と自己検査。下の mixin 群が集まるハブ |
| [diagram-cookbook.md](diagram-cookbook.ja.md) | 実デッキから起こした、そのまま動くレシピ（単位はインチ） |
| [layout-contract.md](layout-contract.ja.md) | **実際の生成結果から実測した**座標と限界値（推定値ではない）。図中心のデッキはここから壊れる |
| [charts.md](charts.ja.md) | 表とグラフ（`charts.py`） |
| [patterns.md](patterns.ja.md) | ビジネスフレームワークの図（`patterns.py`） |
| [calendars.md](calendars.ja.md) | 座標ではなく日付を入力に取る部品（`calendars.py`） |
| [events.md](events.ja.md) | セミナー・カンファレンス告知の部品（`events.py`） |
| [images.md](images.ja.md) | 図解の 5 通りのやり方と、その選び分け |
| [pictogram-catalog.md](pictogram-catalog.ja.md) | 汎用ピクトグラム 32 種と比喩図（`illustrations.py`） |
| [icons.md](icons.ja.md) | Scalar ブランドのピクトグラム 62 種（`icons.py`）と、使い分け |
| [cloud-icons.md](cloud-icons.ja.md) | AWS / Google Cloud / Azure の公式アイコン 1,757 点 |
| [code-blocks.md](code-blocks.ja.md) | シンタックスハイライトつきコードブロック |
| [account-graphs.md](account-graphs.ja.md) | インフルエンスマップ / ディスカバリーマップ |
| [drawio.md](drawio.ja.md) | 密度の高い図を `.drawio` で作り、ヘッドレスで PNG 化する |

## Slides API そのもの

| ファイル | 何のためのものか |
|---|---|
| [api-notes.md](api-notes.ja.md) | **まずこちらを読む。** 手を動かして確かめた制約と落とし穴。多くはどこにも書かれていない |
| [google-slides-api.md](google-slides-api.ja.md) | リクエストの形・単位・上限の生リファレンス。api-notes で答えが出ないときに来る場所 |

## スキル固有のルール

| ファイル | 何のためのものか |
|---|---|
| [hearing-kit.md](hearing-kit.ja.md) | `hearing-sheet` と `hearing-slides` が共有する記録。顧客に見せてよい範囲を決める顧客フィルタもここにある。どちらのスキルも再定義しない |
| [nexus-reports.md](nexus-reports.ja.md) | nexus-architect の各レポートが、どのスライドになるか |
| [account-planning-session.md](account-planning-session.ja.md) | Account Planning Session デッキの作成手順 |

## Scalar 固有（社内）

`scalar/` はエンジンの文書ではなく、顧客・製品固有の営業材料が入っている:
[sales-playbook](scalar/sales-playbook.ja.md)（フェーズ・ゲート・資料タイプ）、
[proposal-map](scalar/proposal-map.ja.md)（課題 → 製品）、
[stage-io-map](scalar/stage-io-map.ja.md)（商談ステージごとの入出力）、
[nurture-map](scalar/nurture-map.ja.md)（商談化前のセグメントとトラック）、
[okf-bundle](scalar/okf-bundle.ja.md)（製品の事実と価格の出どころ）、
[research-2026-08](scalar/research-2026-08.ja.md)、
`scalar/research-policy.md`*（英語のみ）*。
`scalar/workflow-contract.md` は Scalar 側の契約であり、営業資料における
「顧客提示 / 社内」の切り分け規則が置かれている場所でもある*（英語のみ）*。

## 参照資料ではないもの

以下は記録として残しているもので、ある時点で**何を計画したか・何を測ったか**を
述べている。現在の仕様の説明では**ない**:

- [calendar-template-plan.md](calendar-template-plan.ja.md) — カレンダーパックの実装計画
- [account-planning-template-plan.md](account-planning-template-plan.ja.md) — APS ページテンプレートの実装計画
- [`docs/plans/`](../docs/plans/) と [`docs/brainstorms/`](../docs/brainstorms/) — ブレインストームから始まった作業の、同じ種類の記録。`2026-08-15-feat-targeted-slide-update` は `--update-slides` の計画で、完了扱い
- `agent-token-cost-review.ja.md` — 一度きりのトークンコスト監査*（日本語のみ）*

## 書くものではなく、生成されるもの

- `images/` — 2 つのカタログ用のレンダリング画像。素のクローンでも図入りで読めるようコミットしてある
- `i18n/` — **このディレクトリの**生成カタログ 2 種の英語サイドカー文字列

`i18n/` は 2 つあり、役割が違う:

| ディレクトリ | 中身 | 読むもの |
|---|---|---|
| `references/i18n/` | 生成される**カタログ文書**の英語テキスト | `build_pattern_catalog.py`、`build_template_catalog_doc.py` |
| `slide-templates/i18n/` | **スライド自身が刷る語** — 表の見出し、軸の両端、`出典:`、曜日名 | `slide_templates.resolve_label()`（テンプレートの `{"$t": …}`、描画コードの `Canvas._label()` 経由） |

前者を直すと文書が変わり、後者を直すと**生成されるスライドの見た目が変わる**。
