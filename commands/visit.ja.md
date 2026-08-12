---
description: >-
  顧客訪問 1 回分の資料を一続きで作る: 台帳読み込み → フェーズと相手の確定 →
  資料種別のルーティング → 内部情報の混入検査 → オフライン検証 → 生成と Drive 配置 →
  ビジュアル QA → 台帳への書き戻しと活動計画の更新 → アクションプランの報告
argument-hint: "<顧客名> [訪問の目的 / 相手 / フェーズ] [議事録やメモのパス]"
---

*[English](visit.md)*

# /visit — 訪問資料パイプライン

`$ARGUMENTS` を出発点に、`scalar-ae-materials` スキルの流れを**途中で止めずに
一続きで**実行する。作業ディレクトリは slide-forge ルート。

判断の出典は `references/scalar/sales-playbook.md`。

## Step 1: 台帳を読む

```bash
ls accounts/*/<顧客名>/account.json
.venv/bin/python scripts/scalar/account_ledger.py validate <account.json>
.venv/bin/python scripts/scalar/account_ledger.py gaps <account.json>
```

台帳が無ければ `/account <顧客名> new` を先に通す（このコマンドの中で実行してよい）。
**台帳にある前提は聞かない。**

## Step 2: 不足だけをまとめて聞く（最大 1 往復）

`AskUserQuestion` で 4 問まで。台帳とユーザーの指定で埋まっている項目は省く。

1. 誰に会うか（役職・部門・初対面か）
2. この訪問で顧客から得たい一言は何か
3. 社内で得たいもの（提案投資の承認 / 価格承認 / SA の稼働）はあるか
4. 生成後にビジュアル QA を行うか（既定・推奨は実行する）

採用した前提を 1 行で明示してから進む。

## Step 3: 資料種別を決めて構成を承認してもらう（ゲート・省略禁止）

`scalar-ae-materials` の Step 2 のルーティング表で、フェーズ × 相手 × 目的から
資料種別を選ぶ。**顧客向けと社内向けは必ず別ファイルにする。**

本文で次を提示して承認を得る:

- 作る資料の一覧（種別・枚数・置き場フォルダ）
- 各スライドのアクションタイトル
- 委譲する先があればその旨（正式提案は `scalar-proposal-slides`、
  3 マップは `b2b-account-maps`）

**承認後は Step 8 の報告まで確認を挟まず通す。**

## Step 4: 内部情報の混入検査（顧客向け資料がある場合・省略禁止）

生成前に仕様の本文を読み、`scalar-ae-materials` の Step 3 のチェックリストを通す
（個人の影響力・賛否・未接触、競合の弱点、未確認事項の断定、出典のない数値、
開示範囲外の価格・ロードマップ）。該当したら `90_社内` の資料へ移す。

## Step 5: 仕様を書いてオフライン検証する

台帳から作れるページは台帳から作る:

```bash
.venv/bin/python scripts/scalar/account_ledger.py slots <account.json> visit-plan \
    --out out/<顧客名>/visit-plan.json
.venv/bin/python scripts/render_slide_template.py --template visit-plan \
    --data out/<顧客名>/visit-plan.json --out out/<顧客名>/visit-plan.slide.json
```

`visit-plan` を作るには、先に台帳の `visits[]` へ `status: "planned"` の訪問
（日付・相手・目的・問い 3〜4・想定反論 2〜3・紹介依頼）を書く。

```bash
.venv/bin/python scripts/assemble_spec.py out/<顧客名>/*.slide.json \
    --out out/<顧客名>/deck.json --title "<資料名>"
.venv/bin/python scripts/build_deck.py --template templates/scalar-2026.json \
    --spec out/<顧客名>/deck.json --dry-run --strict
```

指摘はデータを直して解消する。テンプレートは直さない。

## Step 6: 生成して正しいフォルダへ置く

```bash
.venv/bin/python scripts/scalar/account_workspace.py ensure --ledger <account.json> --json
```

顧客提示用 → `01_顧客提示` / 顧客提案用 → `02_顧客提案` / 社内説明用 → `90_社内`。
仕様 JSON と図のソースも同じフォルダにアップロードする。生成に失敗したら、
作りかけを Drive から削除して作り直す。

## Step 7: ビジュアル QA と台帳への書き戻し

- Step 2 で「実行する」を選んだ場合は `slide-qa` の手順で検査し、
  最後に `.venv/bin/python scripts/cleanup_qa.py` を必ず実行する
- スキップした場合は、報告に QA 未実施であることを明記する

続けて台帳へ書き戻す（**省略禁止**）:

1. `visits[]` に今回を追加（実施後は `status: "done"` と `heard` / `next`）
2. 新しく分かったことを `facts[]` に `kind` つきで追加
3. 満たしたゲートを `gates` に**顧客側の証拠つきで**記録

```bash
.venv/bin/python scripts/scalar/build_account_plan.py <account.json> --carry-over
```

活動計画の 2 回目以降は破壊的なので、先に
`.venv/bin/python scripts/snapshot_version.py "<デッキ URL>"` で版を確保する。

## Step 8: 報告

1. **AE のアクションプラン** — 誰に・何を・いつまでに・何が取れたら完了か
   （`out/account-plan/<顧客名>/action-plan.md`）
2. 作った資料の名前・種別・URL・置いた Drive フォルダ
3. 顧客提示用について、Step 4 の検査を通したことと、社内へ移した項目
4. QA の結果、または QA 未実施の明記。検証ファイルを削除済みであること
5. 社内承認を求める資料がある場合は、**判断を仰ぐ事項**を 1 行で
   （継続 / 保留 / 撤退、値引きの対価、必要な稼働）
6. 仕上げの確認: 確定する / 文言を直す / 資料を足す / 活動計画も見直す（`/account`）
