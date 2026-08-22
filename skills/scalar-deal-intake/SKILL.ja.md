---
name: scalar-deal-intake
description: >-
  Turn raw deal material — meeting minutes, email threads, Slack, CRM exports,
  customer documents — into per-stage records and a hearing sheet, using the
  stage input/output map derived from the Scalar sales sheet. Use when asked to
  「議事録を整理して」「メールから商談情報をまとめて」「ヒアリングシートを埋めて」
  「ステージごとに整理して」, to work out what is still unconfirmed in a deal, or
  to check whether a stage may advance. Extracts facts with a source and a
  confidence level, never invents an answer, and turns every gap into a question
  with an owner and a due date. The Markdown records feed `scalar-account-plan`
  (the account.json ledger and the activity-plan deck); one visit's materials go
  to `scalar-ae-materials`, the maps to `b2b-account-maps`, and the customer
  proposal to `scalar-proposal-slides`.
---

*[English](SKILL.md)*

# Scalar Deal Intake

生の材料を入れて、ステージ別の記録を出す。**このスキルはスライドを作らない。**
`accounts/<AE 名>/<顧客名>/stages/` 配下の Markdown を作り、デッキ生成側の
スキルがそれを読む。

作業ディレクトリは slide-forge ルート。

判断の出典。**このスキルでこれらを再定義しない。**

| 観点 | 出典 |
|---|---|
| フェーズ・ゲート ID・移行条件・BANT の判定基準・資料 5 種 | [`references/scalar/sales-playbook.ja.md`](../../references/scalar/sales-playbook.ja.md) |
| ステージごとの相手・渡すコンテンツ・持ち帰るアウトプット | [`references/scalar/stage-io-map.ja.md`](../../references/scalar/stage-io-map.ja.md) |
| 安全・Drive・承認・QA の共通規則 | [`references/scalar/workflow-contract.md`](../../references/scalar/workflow-contract.md) |

## Boundaries

| 依頼 | 行き先 |
|---|---|
| 議事録・メールをステージ記録に整理する／ヒアリングシートを埋める | このスキル |
| 何が未確認で、誰に聞けばよいかを出す | このスキル |
| 台帳（`account.json`）への反映と活動計画デッキ | `scalar-account-plan` |
| 訪問 1 回分の資料・WPS・Deal Desk・稟議 | `scalar-ae-materials` |
| ディスカバリー / システム / インフルーエンスマップの作図 | `b2b-account-maps` |
| 正式提案書・見積 | `scalar-proposal-slides` / `spreadsheets` |
| 年次の Account Planning Session | `scalar-account-planning-session` |
| 商談化する前のリード育成（ナーチャリング 0〜4） | `scalar-nurture-intake` |

## この記録は社内文書

実在の個人名、その人のスタンス、その人についての判断が入る。
**顧客にもパートナーにも渡さない。** 置き場の `accounts/` は `.gitignore` 済み。
**記入済みのファイルをコミットしない。**

## 手順

### 1. 渡された材料を先に全部読む

議事録・メール・Slack ログ・CRM エクスポート・顧客資料を、質問する前に読む。
ローカルパス、貼り付けテキスト、Drive URL（Google Drive ツールで読む）、
Gmail スレッドのいずれも受け取る。材料が薄いときは、**薄いと言う**。
足りない分を推測で埋めない。

読んだものは記録の「反映済みの入力」欄に必ず書く（ファイル名または件名、日付、発言者）。
**出典の無い事実は入れない。**

### 2. アカウントとステージを特定する

```bash
ls accounts/<AE 名>/<顧客名>/
```

`account.json` があれば、AE・顧客・ステージ・既知の関与者はそこから取る。

```bash
.venv/bin/python scripts/scalar/account_ledger.py gaps accounts/<AE 名>/<顧客名>/account.json
```

無ければ、AE 名と顧客名だけを聞く。ステージは材料と `stage-io-map.ja.md` §1 を
突き合わせて推定し、**推定であることを明示する。**

1 回の打ち合わせが複数ステージにまたがるのは普通。**その事実が属するのは、
打ち合わせのステージではなく、そのアウトプットを持つステージ**である。
ステージ 2 の訪問で聞いた制約条件は、アウトプットの置き場がステージ 3 なら
ステージ 3 の制約条件表に入れる。

### 3. 記録ファイルを用意する

`templates/sales/` から必要なものだけコピーする。**`deal-log.md` は商談ごとに必ず 1 つ**、
ステージによらず用意する。

```bash
mkdir -p accounts/<AE 名>/<顧客名>/stages
cp templates/sales/deal-log.ja.md      accounts/<AE 名>/<顧客名>/stages/deal-log.md
cp templates/sales/hearing-sheet.ja.md accounts/<AE 名>/<顧客名>/stages/hearing-sheet.md
cp templates/sales/stage-2-discovery.ja.md accounts/<AE 名>/<顧客名>/stages/stage-2-discovery.md
# 検討中の製品の補遺
cp templates/sales/products/scalar.ja.md accounts/<AE 名>/<顧客名>/stages/product-fit-scalar.md
```

ヒアリングシートは**製品に依存しない**。顧客の事実を聞くだけで、製品適合の判定
（課題カテゴリ、提案不可の制約、サイジング、エディション）は
`templates/sales/products/` の製品補遺が持つ（規則: `templates/sales/products/README.md`）。
シート §4.2 / §5 の回答を補遺の B / C / D に当てて判定し、結論をシート §1 に書き戻す。

様式は 2 種類ある。混ぜない。

| | ステージ記録（`stage-*.md`） | 商談ログ（`deal-log.md`） |
|---|---|---|
| 持つもの | 今どうなっているか | いつ何が起きたか |
| 更新 | 該当ステージの内容が変わったとき | 取り込みのたびに §1 へ 1 行追記 |
| 正本 | ゲート判定・要件・制約・合意事項 | 金額・クローズ予定日・フォーキャスト・リスク・失注理由 |

数字や確度が食い違ったら **`deal-log.md` を採る**。

既にある場合は**編集前にスナップショットを取り**（`cp x.md x.md.bak-YYYYMMDD`）、
上書きではなく追記する。出典のある既存行をこのスキルが消すことはしない。
誤りだった事実は取り消し線＋訂正内容＋出典で残し、経緯を読めるようにする。

### 4. 事実を表に落とす

**1 行 = 1 事実。** すべての行に出典と確度を付ける。

| 確度 | 意味 |
|---|---|
| `確認済` | 顧客が言った、または顧客からの文書にある |
| `推定` | こちらの推測。根拠を併記する |
| `未確認` | まだ聞けていない |

プレイブック §4 に基づく規則:

- 顧客の発言は「顧客の発言」欄にそのまま置く。こちらの読みは別欄に、こちらの
  ものとして書く。
- **`推定` を `確認済` に格上げしない。** 表を埋めるために空欄を埋めない。
  確認相手と期限の付いた空欄のほうが役に立つ。
- 社内での協議の結果と、顧客が合意したことは別の行。「社内でスコープを合意した」は
  「顧客がスコープに合意した」ではない。
- 金額・ROI・規模の数値には、算出根拠と前提条件を付ける。
- 指標は**現状値と目標値が揃って初めて指標**。「コスト削減」だけなら `未確認` に置く。

台帳（`account.json`）と語彙を揃える。変換表は `hearing-sheet.ja.md` §14.2 にある。

| 用途 | 語彙 |
|---|---|
| ゲート判定 | `met` / `partial` / `unmet` |
| MEDDPICC の充足（ステージ 2 §10） | `confirmed` / `wip` / `missing` |
| BANT | `ok` / `risk` / `unknown` |
| 事実の種別 | `said` / `observed` / `assumed` |
| フォーキャスト | `Pipeline` / `Best` / `Commit` / `Closed` |

### 取り込みのたびに必ず触る 3 箇所

1. `deal-log.md` §1 — 面談 1 回につき 1 行（出席者・決まったこと・双方の宿題・次回・温度感）
2. `deal-log.md` §3 — 新しく分かったリスク。**未確認事項（聞けば分かること）とは別**
3. 該当ステージの記録 — その回で埋まった欄

既存記録と矛盾する材料が出たら、`deal-log.md` §1 の矛盾表に残す。**黙って上書きしない。**

### 5. ゲートは顧客側の証拠で判定する

ステージ記録の末尾にある移行判断表を埋める。ゲートが通るのは
**顧客側の証拠**（誰が・いつ・何と言ったか）がある場合だけ。「説明した」
「提案書を出した」は証拠にならない（プレイブック §1 原則 5）。

シート記載の判断基準とプレイブックのゲートが食い違う箇所は、記録側に
「（シート記載）」と注記してある。**シートの行だけでなく、表のゲートを全部判定する。**

### 6. 未確認をアクションに変える

`未確認` はすべて、記録のアクション表とヒアリングシート §12 に落とす。
何が未確認か、誰なら答えられるか、いつまでに、誰が聞くか。
確認相手は `stage-io-map.ja.md` の**そのアウトプットを持つ行**から選ぶ。
誰が答えを持っているかは表に書いてある。

そのうえで、次回訪問用にヒアリングシートの「聞く」欄へチェックを立てる。

### フォーキャストは根拠で決める

`deal-log.md` のヘッダを更新するとき、次を満たさない `Commit` は `Best` に落とす
（プレイブック §4）。

- §2 クローズプランに、**顧客と合意済み**のタスクが契約日まで並んでいる
- §3 のリスクのうち「影響: 大」がすべて解消しているか、次の行動が顧客と合意できている
- ステージ 4 §12 の契約手続に、要否と所要期間が入っている

### 失注・保留のとき

`deal-log.md` §4 を埋めるまで商談を閉じない。敗因、分かれ目になった評価軸、
どのステージのどの確認漏れが効いたか、再アプローチの条件までを残す。
**「価格が高い」を真因として採らない。**

### 7. 差分を報告する

日本語で次を返す。

1. 作成・更新したファイルと、追記した内容
2. 今回通ったゲートとその証拠、まだ通らないゲート
3. 未確認の上位項目（確認相手と期限つき）
4. 材料と既存記録が矛盾している箇所

そのうえで次の一手を示す。台帳への反映と活動計画の更新は `scalar-account-plan`、
次の訪問資料は `scalar-ae-materials`。

## やってはいけないこと

- 活動量でステージを判定しない。ステージは顧客の合意で進む（プレイブック §1 原則 5）。
- 課題適合性シートの ScalarDB 2 行に当てはまらないことを、ステージ 1 の失格理由に
  しない。あの 2 行は古い（`stage-io-map.ja.md` §8）。
- シートの「6. Close」を商談の終わりと読まない。プレイブックのフェーズ 6 は
  導入・更新・拡張まで含む（`stage-io-map.ja.md` §7）。
- 材料に含まれる価格・競合の弱点・個人についての判断は、この記録の中に留める。
  顧客の目に触れるものへ持ち出さない。
- 競合を他社ベンダーだけで埋めない。**現状維持・内製・既存ベンダーの拡張**の 3 行は
  常に見る（ステージ 2 §8）。
- 「Champion がいる」と書くのは、ステージ 2 §1 の検証 5 項目のうち 3 つ以上が
  未検証でない場合だけ。役職や本人の意欲では判定しない。
- PoC の記録で「合格した場合に顧客が次に行うこと」が空欄なら、その PoC を
  フォーキャストを上げる根拠に使わない。
