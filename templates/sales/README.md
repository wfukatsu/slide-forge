# `templates/sales/` — 商談ステージ記録の Markdown 様式

**スライドテンプレートではない。** `templates/*.json` は Google Slides の
テンプレートパックだが、このディレクトリにあるのは商談情報を整理するための
Markdown の記入様式である。レンダリングエンジンは読まない。

| ファイル | 用途 |
|---|---|
| `deal-log.ja.md` | **商談ログ**。面談履歴（時系列）・クローズプラン・リスク一覧・失注記録。金額 / クローズ予定日 / フォーキャストの正本 |
| `hearing-sheet.ja.md` | ヒアリングシート。ステージ横断の質問集と回答欄。**製品に依存しない** |
| `products/` | 製品別ヒアリング補遺。製品適合の判定はこちら（[README](products/README.md)） |
| `stage-0-planning.ja.md` | ステージ 0 Territory / Account Planning（シートに行が無く、プレイブックから起こした） |
| `stage-1-assessment.ja.md` | ステージ 1 Assessment & Qualification |
| `stage-2-discovery.ja.md` | ステージ 2 Discovery |
| `stage-3-solution-development.ja.md` | ステージ 3 Solution Development |
| `stage-4-solution-presentation.ja.md` | ステージ 4 Solution Presentation |
| `stage-5-resolution.ja.md` | ステージ 5 Resolution（シート空欄・プレイブックから起こした） |
| `stage-6-close.ja.md` | ステージ 6 Delivery / Renewal / Expansion（同上） |

商談化する**前**（リード育成）の様式は [`templates/nurture/`](../nurture/README.md) にある。
ナーチャリングのステージは 0〜4、商談のステージは 0〜6 で、**別物**である。

## 出典

- 様式の元になった入出力の整理: [`references/scalar/stage-io-map.ja.md`](../../references/scalar/stage-io-map.ja.md)
  （Google Sheet「ステージごとの商談の進め方」）
- ゲート ID・移行条件・BANT の判定基準: [`references/scalar/sales-playbook.ja.md`](../../references/scalar/sales-playbook.ja.md)

## 使い方

`scalar-deal-intake` スキルが、議事録・メールなどを読んでこれらを埋める。
手で使う場合は次の場所へコピーする。

```
accounts/<AE 名>/<顧客名>/stages/
  deal-log.md          ← 商談ごとに 1 つ。取り込みのたびに面談履歴へ 1 行足す
  hearing-sheet.md
  product-fit-scalar.md   ← templates/sales/products/scalar.ja.md から
  stage-1-assessment.md
  ...
```

## 製品に依存する部分としない部分

ヒアリングシートは**顧客の事実だけ**を聞く。製品名・バージョン・エディション・
価格は持たない。製品ごとの判定（課題カテゴリ、提案不可の制約、動作要件、数量、
エディション）は `products/<製品>.ja.md` が持つ。**製品が増えたら補遺を 1 つ足す。
シート本体は変更しない。** 規則は [`products/README.md`](products/README.md)。

| 入力（シート） | 判定（補遺） |
|---|---|
| §1 解決したいこと | A. 課題カテゴリ |
| §4.2 現行システムの技術ファクト | B. 適用可否 / C. 技術前提 |
| §5 サイジングと環境構成 | D. 構成と数量（BOM の元） |
| §4.1 / §6 / §11 | E. エディション・機能の要否 |

## 2 種類の様式

| | ステージ記録（`stage-*.md`） | 商談ログ（`deal-log.md`） |
|---|---|---|
| 持つもの | 今どうなっているか（スナップショット） | いつ何が起きたか（時系列） |
| 更新 | 該当ステージの内容が変わったとき | 取り込みのたびに追記 |
| 正本になる項目 | ゲート判定、要件、制約、合意事項 | 金額、クローズ予定日、フォーキャスト、リスク、失注理由 |

数字や確度が食い違ったら **`deal-log.md` を採る**。

## 台帳（`account.json`）との対応

様式の欄名は台帳のキーに合わせてある。語彙も揃えてある。

| 種別 | 語彙 |
|---|---|
| ゲート判定 | `met` / `partial` / `unmet` |
| MEDDPICC の充足 | `confirmed` / `wip` / `missing` |
| BANT | `ok` / `risk` / `unknown` |
| 事実の種別 | `said` / `observed` / `assumed` |
| フォーキャスト | `Pipeline` / `Best` / `Commit` / `Closed` |

ヒアリングシートの `確認済` / `推定` / `未確認` からの変換表は
`hearing-sheet.ja.md` §14.2 にある。

`accounts/` は `.gitignore` 済み。**記入済みのファイルをコミットしない。**
実在の個人名と、その人物についての判断が入るため、顧客・パートナーにも渡さない。

日本語のみで用意している。顧客との会話がそのまま入る様式であり、
ユーザー向け成果物は日本語という運用に従う。

## 3 形式で扱う（hearing-sheet スキル）

この Markdown の様式は**空のフォーム**である。商談で使うときは `hearing-sheet`
スキルで `hearing.json` を起こし、Markdown / Excel / Google Spreadsheet を
そのレンダーとして出す。顧客に渡して記入してもらい、返ってきたものを読み戻せる。

```bash
.venv/bin/python scripts/hearing/hearing_sheet.py init \
    templates/sales/hearing-sheet.ja.md --out accounts/<AE 名>/<顧客名>/stages/hearing.json
```

- **ID 列は JSON との突き合わせに使う。** 振り直さない、消さない、手で並べ替えない
- 顧客に渡す版は `--audience customer`（内部の列と節を落とす）
- 規則は [`references/hearing-kit.ja.md`](../../references/hearing-kit.ja.md)
- 空いている項目を聞くためのスライドは `hearing-slides` スキル
