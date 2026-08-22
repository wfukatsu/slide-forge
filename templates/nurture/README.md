# `templates/nurture/` — ナーチャリング設計の Markdown 様式

**スライドテンプレートではない。** `templates/*.json` は Google Slides の
テンプレートパックだが、このディレクトリにあるのはナーチャリング（商談化前の
リード育成）を設計・管理するための Markdown の記入様式である。

| ファイル | 用途 |
|---|---|
| `segment-sheet.ja.md` | セグメント定義。誰に当てるかの「型」。顧客名は書かない |
| `nurture-track.ja.md` | 1 セグメント × 5 ステージの設計。ストーリー、コンテンツ、パワースクリプト、指標、商談への引き渡し |
| `content-inventory.ja.md` | コンテンツ台帳。Contents ID の採番、ステージ別の充足状況、鮮度管理 |

## 出典

- 整理したもの: [`references/scalar/nurture-map.ja.md`](../../references/scalar/nurture-map.ja.md)
  （Google Sheet「ナーチャリング・プラン・シート」）
- 引き渡し先の商談ステージ: [`references/scalar/stage-io-map.ja.md`](../../references/scalar/stage-io-map.ja.md)
- ゲート ID と判定基準: [`references/scalar/sales-playbook.ja.md`](../../references/scalar/sales-playbook.ja.md)

## ステージ番号に注意

**ナーチャリングは 0〜4、商談は 0〜6。別物である。**

| ナーチャリング | 引き渡し先の商談ステージ |
|---|---|
| 0. Education / 1. Need | （まだ商談ではない） |
| 2. Research | 商談 1. Assessment & Qualification |
| 3. Evaluation | 商談 2. Discovery 〜 3. Solution Development |
| 4. Selection | 商談 4. Solution Presentation |

文書内では必ず「ナーチャリング 2」「商談 2」と書き分ける。

## `templates/sales/` との違い

| | `templates/nurture/` | `templates/sales/` |
|---|---|---|
| 対象 | セグメント（型） | 顧客 1 社（実在） |
| 個人名 | **書かない** | 書く（社内専用） |
| 単位 | Segment No. ごとに 1 トラック | 顧客ごとに 1 セット |
| 置き場 | `accounts/_nurture/` | `accounts/<AE 名>/<顧客名>/stages/` |

どちらも `accounts/` 配下（`.gitignore` 済み）に置き、**記入済みのファイルを
コミットしない**。

## 使い方

`scalar-nurture-intake` スキルが、ウェビナー参加ログ・問い合わせメール・
コミュニティの質問などを読んでこれらを埋める。手で使う場合は次の場所へコピーする。

```
accounts/_nurture/
  segments/<Segment No.>.md   セグメント定義
  tracks/<Segment No.>.md     ナーチャリング・トラック
  content-inventory.md        コンテンツ台帳（1 つだけ）
```

日本語のみで用意している（`work/CLAUDE.md` の「ユーザー向け成果物は日本語」に従う）。
