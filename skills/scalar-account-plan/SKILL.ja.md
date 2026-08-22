---
name: scalar-account-plan
description: >-
  Maintain a per-customer sales ledger (account.json) for a Scalar Account
  Executive — what is confirmed, who decides, what is unknown, what to do next —
  rendered as a Google Slides activity plan whose URL never changes.
  Use for: 活動計画, アカウントプラン, 商談の記録, ステージ・フォーキャスト・BANT の
  レビュー, 次に確認すべきこと, アカウントの Drive 準備.
  Not: the annual Account Planning Session decks
  (scalar-account-planning-session); one visit's materials
  (scalar-ae-materials); the customer proposal (scalar-proposal-slides); the maps
  (b2b-account-maps).
---

*[English](SKILL.md)*

# Scalar Account Plan

顧客 1 社につき台帳 1 つ。**台帳が正本**で、デッキはその表示にすぎない。
訪問のたびに台帳へ追記し、同じ URL のデッキを最新化する。

台帳から出るデッキは 2 系統。寿命も入力も違うので混ぜない。**このスキルは左**。

| | 活動計画デッキ（§5） | APS デッキ |
|---|---|---|
| 目的 | 今どこにいて次に何をするか | 年次・半期の棚卸しと役員レビュー |
| 更新 | 訪問のたび | APS のたび |
| 入力 | `account.json`（台帳） | `aps.json`（台帳 + 顧客の公開情報） |
| スキル | **このスキル** | `scalar-account-planning-session` |

作業ディレクトリは slide-forge ルート。コマンドは `.venv/bin/python` で実行する。

判断の出典は [references/scalar/sales-playbook.md](../../references/scalar/sales-playbook.ja.md)。
ステージ、ゲート ID、資料 5 種、BANT、10 問チェックポイントはすべてそこにある。
**このスキルでそれらを再定義しない。**

## Boundaries

| 依頼 | 行き先 |
|---|---|
| 活動計画を作る / 追記する / 状況を答える | このスキル（§5） |
| Account Planning Session の資料を作る | `scalar-account-planning-session` |
| 訪問 1 回分の資料一式を作る | `scalar-ae-materials` |
| 関与者マップ・ディスカバリーマップそのものの作図 | `b2b-account-maps` |
| 議事録・メールをステージ別の記録に整理する | `scalar-deal-intake` |
| 顧客向けの正式提案書 | `scalar-proposal-slides` |
| 見積もり明細 | `spreadsheets` |
| 生成したデッキの目視検査 | `slide-qa` |

## これは内部資料である

活動計画は名前のある個人について判断を記録する（影響力、賛否、未接触）。
**顧客にもパートナーにも渡さない。** Drive 上でも `00_活動計画` と `90_社内` は
共有しない。顧客に見せるものは `01_顧客提示` / `02_顧客提案` に置いたものだけ。

## 置き場

```
config/sales.json                       Drive ルートと既定 AE 名（gitignore 済み）
accounts/<AE 名>/<顧客名>/account.json   ★ 正本（gitignore 済み。コミットしない）
accounts/<AE 名>/<顧客名>/aps.json       APS デッキの内容（別スキルが使う。同上）

Drive: <ルート>/<AE 名>/<顧客名>/
  00_活動計画/  活動計画デッキ（URL 不変）・account.json のコピー・action-plan.md
  01_顧客提示/  顧客提示用
  02_顧客提案/  顧客提案用
  90_社内/      社内説明用
```

## Workflow

### 1. 台帳を用意する

既にあれば読む。無ければ作る。

```bash
.venv/bin/python scripts/scalar/account_ledger.py init --ae "<AE 名>" --customer "<顧客名>" \
    --opportunity "<商談名>"
```

Drive の階層は初回だけルートを聞いて作る（以降は `config/sales.json` の設定を使う）。
**ルートが未設定のときは必ずユーザーに確認する。勝手にマイドライブ直下に作らない。**

```bash
.venv/bin/python scripts/scalar/account_workspace.py ensure \
    --ledger accounts/<AE>/<顧客>/account.json [--root "<Drive フォルダ URL>"]
```

### 2. 手元の材料から埋める（聞く前に読む）

議事録・面談メモ・メール・CRM のエクスポートを先に読む。そのうえで、**足りない
ものだけを 1 回でまとめて聞く**（`references/interactive-intake.md` §0・§5）。

台帳に書くときは、`facts[].kind` で必ず区別する:

| kind | 意味 | `confirmed` に昇格できるか |
|---|---|---|
| `said` | 顧客がそう言った（誰が・いつ） | できる |
| `observed` | 文書・組織図・送った見積で確認した | できる |
| `assumed` | こちらの推測 | **できない** |

ステータス規則は
[b2b-account-maps の discovery-map.md](../b2b-account-maps/references/discovery-map.md)
に従う。二重定義しない。

**やってはいけないこと**:

- 会っていない人を「中立」として影響力マップの真ん中に置く（未接触は `gaps` に入れる）
- 推測で `confirmed` にする（`evidence` が空の `confirmed` は検証で落ちる）
- 顧客が言っていない数字を書く

### 3. 検証する

```bash
.venv/bin/python scripts/scalar/account_ledger.py validate accounts/<AE>/<顧客>/account.json
```

矛盾はここで止まる — 証拠のない `confirmed`、証拠のない `met` ゲート、期限や
完了条件のないアクション、BANT が揃っていないのに `Commit` のフォーキャスト。
**台帳を直す。検証を緩めない。**

### 4. 未確認をアクションに変える（このスキルの中心）

```bash
.venv/bin/python scripts/scalar/account_ledger.py gaps accounts/<AE>/<顧客>/account.json
```

プレイブック §7 の 10 問のうち答えられないものが、確認相手と完了条件つきで出る。
**答えを埋めない。** 未確認は未確認のまま残し、`--carry-over` で `actions` に
取り込み、**期限だけをユーザーに決めてもらう**（期限は AE の約束であって、
こちらが決めるものではない）。

`--carry-over` は次の 2 コマンドのフラグ（どちらも台帳を書き換えてから出力する）:

```bash
# アクションプランの Markdown を出すついでに取り込む
.venv/bin/python scripts/scalar/account_ledger.py actions <account.json> --carry-over

# デッキ生成（§5）のついでに取り込む
.venv/bin/python scripts/scalar/build_account_plan.py <account.json> --carry-over
```

前回の未完了アクションはそのまま繰り越される。期限切れは検証で警告が出る。

### 5. 活動計画デッキを作る / 更新する

```bash
# 検証（API を呼ばない）
.venv/bin/python scripts/scalar/build_account_plan.py <account.json> --dry-run --strict

# 初回 — 00_活動計画 フォルダに新規作成
.venv/bin/python scripts/scalar/build_account_plan.py <account.json> --folder <00_活動計画 の ID>

# 2 回目以降 — 同じ URL の中身を差し替える（台帳の meta.decks.activityPlan を自動で使う）
.venv/bin/python scripts/scalar/build_account_plan.py <account.json>
```

既定の 9 ページ（表紙を除く）は、読む順序に意味がある:

`account-snapshot`（今どこにいるか）→ `phase-gate`（何が未達か）→
`bant-risk`（どこが危ないか）→ `discovery-map`（何が分かっていないか）→
`pain-chain`（なぜ効くのか）→ `influence-map` / `buying-committee`（誰を動かすか）→
`activity-timeline`（どこまで会えたか）→ `action-plan`（次に何をするか）

**材料が足りないページは自動で落ちる。** 落ちたページは報告に出る。空欄を埋めた
薄いページを作らない — 何が無いかは `action-plan` に出るのが正しい。

`--pages` で `visit-plan` / `win-plan` / `discovery-gaps` を足せる。ただしこの 3 枚は
訪問 1 回・WPS 1 回のための資料で寿命が違うので、常設の活動計画には入れない。

#### 2 回目以降は破壊的である

`--into` は既存デッキの**全ページを消してから**積み直す。実行前に版を確保する:

```bash
.venv/bin/python scripts/snapshot_version.py "<デッキ URL>"
```

`build_account_plan.py` は編集前リビジョン ID を表示する。差し戻しは Slides UI の
「ファイル → 版の履歴」から。

`--into` が拒否するもの（いずれも意図した動作）:

| 差し替え先 | 結果 |
|---|---|
| **テンプレートの原本**（`templates/*.json` の `presentationId`） | 拒否。原本を壊すと、そのテンプレートで作った全デッキの元が失われる |
| 別のマスターから作られたデッキ | 拒否（レイアウトが見つからない） |
| `predefinedLayout` で作る種類のテンプレート（`blank-16x9` 等） | 拒否（実レイアウトが要る） |

**差し替え先の URL は台帳の `meta.decks.activityPlan` から取る。**
手で URL を貼るときは、それが生成物であって原本でないことを必ず確かめる。

### 6. 年次・半期の棚卸し（APS）

年次・半期のアカウント棚卸しと役員レビュー資料は
[`scalar-account-planning-session`](../scalar-account-planning-session/SKILL.ja.md)。
入力は台帳ではなく `accounts/<AE>/<顧客>/aps.json` で、台帳に顧客の公開情報
（中期経営計画・組織図・役員名簿）を足して組み立てる。

**このスキルはそこまでやらない。** 台帳（§1–4）が APS の前提になるので、
先に台帳を最新にしてから APS 側へ渡す。

### 7. 関与者が 9 人を超えたら

スライドに詰めない。`b2b-account-maps` の既定どおり、全体を draw.io に出して
スライドには抽出版を載せ、**落ちた人数と全体版の在り処を必ず書く**（`more` スロット）。

**レイアウトを先に決める。** 既定の木レイアウトは根の数だけ横に伸びる。
企業グループのように根が多いと帯になって読めない（49 名で 18,000 × 709px）。

| グラフの形 | 使うもの |
|---|---|
| 1 社・1 本の指揮系統（根が 1〜2 本） | 既定（`--layout tree`） |
| **企業グループ・根が 3 本以上** | **`--layout grouped`** |

```bash
# 企業グループ。people[].entity ごとの枠に格子で並べ、法人をまたぐ線は枠の外を通す
.venv/bin/python scripts/build_account_graph.py <graph.json> --layout grouped \
    --title "<顧客> インフルーエンスマップ（全体）" \
    --out out/account-plan/<顧客>/influence-map-full.drawio

# 1 社なら既定のままでよい
.venv/bin/python scripts/build_account_graph.py <graph.json> \
    --out out/account-plan/<顧客>/influence-map-full.drawio

# PNG に書き出す（drawio CLI が要る）
drawio -x -f png -s 2 -b 8 \
    -o out/account-plan/<顧客>/influence-map-full.png \
       out/account-plan/<顧客>/influence-map-full.drawio
```

- `entity` は法人名（`entityOrder` で枠の並び順を決める）。組織図と同じ単位にする
- **人のつながり（`links`）は線に番号だけを置き、文言は図の下の一覧に出す。**
  線上にラベルを置くと、長い線ほどカードに重なって読めなくなる
- `.drawio` と PNG は必ずデッキの Drive フォルダに置く。PNG だけでは編集できない

### 8. 目視検査と後片付け

`slide-qa` スキルでサムネイルを確認する。特に見るところ:

- インフルーエンスマップで**次に動かす人**が最初に目に入るか（squint test）
- 表の行が下端のロゴ帯に重なっていないか
- 人物のラベルが互いを隠していないか — 隠れていたら**台帳の座標を直す**
  （テンプレートを直すのではない）

終わったら `.venv/bin/python scripts/cleanup_qa.py`。

### 9. Drive にまとめて報告する

```bash
.venv/bin/python scripts/scalar/account_workspace.py ensure --ledger <account.json>
.venv/bin/python scripts/drive_folder.py upload <00_活動計画 の ID> \
    accounts/<AE>/<顧客>/account.json out/account-plan/<顧客名>/action-plan.md
```

報告に必ず入れるもの:

1. デッキの URL と Drive フォルダの URL
2. ステージ・フォーキャストと、その根拠
3. **次に確認すべきことの最短リスト**（誰に・いつまでに・何が取れたら完了か）
4. 材料不足で落としたページがあれば、その名前と足りない情報

URL ではなく 3 が報告の主役。デッキは手段で、AE が次に取る行動が成果物である。

## Rules

- **台帳が正本。デッキを直接編集しない。** 直すことがあれば台帳を直して作り直す。
- **CRM を置き換えない。** ステージ・金額・予定日・Next Action の正本は CRM。
  台帳を更新したら CRM も揃える（プレイブック §8）。
- **証拠か、さもなくば未確認。** `confirmed` と `met` には出所（誰が・いつ）が要る。
- **絶対に答えを埋めない。** 空欄は AE の次の行動であって、埋める穴ではない。
- **古い活動計画は無いより悪い。** 更新できないなら台帳ごと畳む。
- `accounts/` と `config/` はコミットしない（顧客名・個人名・判断が入る）。
  作業ファイルは無視される `out/` 配下に置く。
