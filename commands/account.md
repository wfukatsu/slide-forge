---
description: >-
  顧客ごとの活動計画を作る・追記する・照会する: 台帳の用意 → 材料の取り込み →
  検証 → 未確認をアクションに変換 → 活動計画デッキを同じ URL で更新 →
  次に確認すべきことの報告
argument-hint: "<顧客名> [new | update | show] [議事録やメモのパス]"
---

# /account — 顧客の活動計画

`$ARGUMENTS` を出発点に、`scalar-account-plan` スキルの流れを**途中で止めずに**
実行する。作業ディレクトリは slide-forge ルート。

このコマンドは**社内資料**を扱う。台帳と活動計画デッキは顧客に渡さない。

## Step 0: モードを決める

引数から判断する。判断がつかないときだけ `AskUserQuestion` で 1 回確認する。

| 引数 | やること |
|---|---|
| `new` / 台帳が無い | 台帳を作り、Drive 階層を用意し、初回のデッキを生成する |
| `update`（既定）/ 議事録が付いている | 台帳に追記し、同じ URL のデッキを差し替える |
| `show` | 台帳を読んで状況を答える。**書き込みも生成もしない** |

AE 名は `config/sales.json` の `defaultAe`、無ければユーザーに確認する。

## Step 1: 台帳を読む・作る

```bash
ls accounts/*/<顧客名>/account.json
```

無ければ `scalar-account-plan` の手順 1 で作り、Drive 階層を用意する。
**Drive ルートが未設定なら必ずユーザーに確認する**（勝手にマイドライブ直下に作らない）。

`show` のときはここで読み、Step 6 の形式で答えて終わる。

## Step 2: 材料を取り込む（聞く前に読む）

引数で渡された議事録・メモ・メールを先に読む。読んだうえで、足りないものだけを
`AskUserQuestion` で **1 回にまとめて**聞く。

台帳に書くときは `facts[].kind` を必ず付ける — `said`（顧客が言った）/
`observed`（文書で確認した）/ `assumed`（こちらの推測）。**`assumed` は
`confirmed` にできない。**

## Step 3: 検証する（省略禁止）

```bash
.venv/bin/python scripts/scalar/account_ledger.py validate accounts/<AE>/<顧客名>/account.json
```

矛盾が出たら**台帳を直す**。検証を緩めない。

## Step 4: 未確認をアクションに変える

```bash
.venv/bin/python scripts/scalar/account_ledger.py gaps accounts/<AE>/<顧客名>/account.json
```

出た項目の**期限だけ**をユーザーに確認する（期限は AE の約束であって、こちらが
決めるものではない）。答えを埋めない。

## Step 5: デッキを作る / 差し替える

```bash
# 検証（API を呼ばない）
.venv/bin/python scripts/scalar/build_account_plan.py <account.json> --dry-run --strict
```

- **初回**: `--folder <00_活動計画 の ID>` を付けて生成する
- **2 回目以降**: 先に `scripts/snapshot_version.py "<デッキ URL>"` で版を確保してから
  `--carry-over` 付きで実行する。デッキ URL は変わらない

```bash
.venv/bin/python scripts/scalar/build_account_plan.py <account.json> --carry-over
```

続けて `slide-qa` スキルで目視検査し、`scripts/cleanup_qa.py` で後片付けする。
台帳と `action-plan.md` を `00_活動計画` にアップロードする。

## Step 6: 報告

1. **次に確認すべきこと**（誰に・いつまでに・何が取れたら完了か）— これが主役
2. ステージ・フォーキャストと、その根拠。前回から変わった点
3. 活動計画デッキの URL と Drive フォルダの URL
4. 材料不足で落としたページと、足りない情報
5. 仕上げの確認: 確定する / 期限を直す / ページ構成を変える / 訪問資料も作る
   （`/visit`）
