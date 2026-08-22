---
name: hearing-sheet
description: >-
  Keep the hearing sheet as data and move it between Markdown, Excel and Google
  Spreadsheet in both directions — hand one to a customer or partner to fill in,
  read the answers back, and report what is still unconfirmed. Product-neutral;
  product-fit judgements live in templates/sales/products/.
  Use for: ヒアリングシートを作って, ヒアリング項目を Excel で,
  スプレッドシートで顧客に渡したい, 記入してもらったシートを取り込んで,
  何が聞けていないか.
  Not: slides that do the asking (hearing-slides); minutes and email into the
  record (scalar-deal-intake).
---

*[English](SKILL.md)*

# ヒアリングシートの入出力

先に [`references/hearing-kit.ja.md`](../../references/hearing-kit.ja.md) を読む。
正本・マージ規則・顧客配布版のフィルタ・コマンド一覧はそちらにあり、
**このスキルでは繰り返さない**。ここが持つのは手順と判断だけである。

作業ディレクトリは slide-forge ルート。コマンドは `.venv/bin/python` で実行する。

## 境界

| 依頼 | 行き先 |
|---|---|
| md / xlsx / Google Spreadsheet でのヒアリングシート（両方向） | このスキル |
| 何が未確認か、誰なら答えられるか | このスキル（`gaps`） |
| 空いている項目を聞くためのスライド | `hearing-slides` |
| 議事録・メール・CRM エクスポート → 記録 | `scalar-deal-intake` |
| 製品が当たるか、どのエディションか | `templates/sales/products/<製品>.ja.md`（人が判定し、結論だけがここに入る） |
| ゲート・BANT の判定 | `references/scalar/sales-playbook.ja.md` |
| 見積・BOM の明細表 | `spreadsheets` |
| 提案書 | `scalar-proposal-slides` |

## 手順 1: 記録を探す・起こす

```bash
ls accounts/<AE 名>/<顧客名>/stages/hearing.json
```

無ければ空の様式から起こす。製品が決まっているなら補遺も入れる。

```bash
.venv/bin/python scripts/hearing/hearing_sheet.py init \
    templates/sales/hearing-sheet.ja.md \
    --out accounts/<AE 名>/<顧客名>/stages/hearing.json --product scalar
```

**同じ商談に 2 つ目の記録を作らない。** 1 商談 = 1 `hearing.json` = 1 リンク。

このスキルより前に手で書いた Markdown のシートがあるなら、空の様式ではなく
**そのファイルから `init` する**。回答がそのまま移り、そのときに ID が振られる。

## 手順 2: 誰が書くかで形式を決める

推測できないことだけを 1 回でまとめて聞く（`references/interactive-intake.ja.md`
§0・§5）。

| # | header | 質問 | 選択肢 |
|---|---|---|---|
| 1 | 記入する人 | このシートに書き込むのは誰ですか | こちら（議事録から）/ 顧客 / パートナー / イベントの参加者 |
| 2 | 形式 | どの形式にしますか | Google Spreadsheet（共有して読み戻す）/ Excel（送って返してもらう）/ Markdown（社内のみ） |
| 3 | 配布先 | 社外に出しますか | 社内用 / 顧客に渡す（内部の列と節を落とす） |

依頼に書いてあることは聞かずに決める。**顧客が書き込むシートは Google
Spreadsheet か Excel であって、Markdown ではない。**

```bash
.venv/bin/python scripts/hearing/hearing_sheet.py render <json> --format gsheet \
    --audience customer --folder <Drive フォルダ URL>
```

顧客に渡すシートは `01_顧客提示` に置く。社内用は顧客フォルダに入れない
（`sales-playbook.ja.md` §8）。

**渡す前に、プレイブック §3 の検査を目視で行う。**
`--audience customer` は列と節を落とすだけで、**設問の言い回しが引用されて
困るものかどうかまでは判定できない。**

## 手順 3: 返ってきたものを読む

```bash
cp <json> <json>.baseline-YYYYMMDD          # レンダーする前に baseline を残す
.venv/bin/python scripts/hearing/hearing_sheet.py read <形式|URL> \
    --into <json> --baseline <json>.baseline-YYYYMMDD --dry-run
```

まず `--dry-run` で変更一覧を読む。納得してから書き込む。

- **競合が出たらマージは止まる。** メッセージを消すために `--take` を使わない。
  両方の値を見て、どちらが事実かを判断し、**その理由を報告に書く**。
- 記録に無い ID は、行が足されたか ID 列が書き換えられたということ。
  勝手に設問を作らず、確認する。
- 回答は顧客が書いたまま入る。**顧客の言葉を「回答」に残す。** こちらの読みは
  ステージ記録側に書き、このセルに混ぜない。
- 回答が入っただけで確度は上がらない。`確認済` にできるのは、顧客がそう言った
  か文書にある場合だけ。こちらが読み取ったなら `推定` である。

## 手順 4: 空いているものを報告する

```bash
.venv/bin/python scripts/hearing/hearing_sheet.py gaps <json> [--section 4]
```

日本語で次を返す。

1. 何が変わったか、どこから来たか
2. まだ `未確認` のもの（節ごと、誰なら答えられるかつき）
3. `推定` で入ったもの — これが `hypothesis-check` で確認する対象
4. 競合。**両方の値を出し、解決を捏造しない**
5. その空きが下流の何を止めているか。§4.2 と §5 は
   `scalar-proposal-slides` の構成図と BOM の前提であり、
   どの節が提案書のどこになるかは `hearing-sheet.ja.md` §14.3 にある

そのうえで、対面で聞く価値のある項目について `hearing-slides` を提案する。

## ファイル

| パス | 役割 |
|---|---|
| `scripts/hearing/hearing_sheet.py` | init / render / read / gaps / validate |
| `scripts/hearing/model.py` | 文書の形、Markdown のパーサとレンダラ |
| `templates/sales/hearing-sheet.ja.md` | 空の様式（製品非依存） |
| `templates/sales/products/` | 製品適合の補遺 |
| `references/hearing-kit.ja.md` | 共通規約（正本・マージ・顧客配布版・置き場） |
