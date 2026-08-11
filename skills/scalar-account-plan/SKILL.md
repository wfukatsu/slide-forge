---
name: scalar-account-plan
description: >-
  Maintain a per-customer sales activity plan for a Scalar Account Executive:
  a ledger (account.json) of what is confirmed, who decides, what is still
  unknown, and what to do next — rendered as a Google Slides deck whose URL
  never changes, so the same shared link always shows the current state.
  Use when asked to create or update an account plan, activity plan or
  アカウントプラン / 活動計画; to record what came out of a customer meeting;
  to review a deal's stage, forecast or BANT risk; to work out what an AE must
  confirm next; or to set up the Drive folders for an account. Also builds the
  annual/half-year Account Planning Session (APS / アカウントプランニング
  セッション) decks — a full Plan Document plus a 9-page executive review deck —
  from the same ledger. Produces the action plan (slides + Markdown) that turns
  unanswered questions into dated commitments. Route one visit's materials to
  `scalar-ae-materials`, the customer proposal to `scalar-proposal-slides`, and
  the stakeholder/discovery maps themselves to `b2b-account-maps`.
---

# Scalar Account Plan

顧客 1 社につき台帳 1 つ。**台帳が正本**で、デッキはその表示にすぎない。
訪問のたびに台帳へ追記し、同じ URL のデッキを最新化する。

台帳から出るデッキは 2 系統。寿命が違うので混ぜない。

| | 活動計画デッキ（§5） | APS デッキ（§6） |
|---|---|---|
| 目的 | 今どこにいて次に何をするか | 年次・半期の棚卸しと役員レビュー |
| 更新 | 訪問のたび | APS のたび |
| 範囲 | 台帳の中身だけ | 台帳 + 顧客の公開情報 |

作業ディレクトリは slide-forge ルート。コマンドは `.venv/bin/python` で実行する。

判断の出典は [references/scalar/sales-playbook.md](../../references/scalar/sales-playbook.md)。
ステージ、ゲート ID、資料 5 種、BANT、10 問チェックポイントはすべてそこにある。
**このスキルでそれらを再定義しない。**

## Boundaries

| 依頼 | 行き先 |
|---|---|
| 活動計画を作る / 追記する / 状況を答える | このスキル（§5） |
| Account Planning Session の資料を作る | このスキル（§6） |
| 訪問 1 回分の資料一式を作る | `scalar-ae-materials` |
| 関与者マップ・ディスカバリーマップそのものの作図 | `b2b-account-maps` |
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

### 6. Account Planning Session（APS）のデッキを作る

活動計画デッキ（§5）が「今どこにいて次に何をするか」を訪問のたびに更新するのに
対し、APS デッキは**年次・半期の棚卸し**。同じ台帳から 2 本出る。

| 成果物 | 中身 | 読み手 |
|---|---|---|
| Plan Document | 全ページ。分析・商談ごとの章・実行計画 | アカウントチーム |
| APS レビュー資料 | 本編 9 ページ + Appendix | 役員レビュー（30 分） |

**ページ定義と各ページの判断基準はこのスキルで再定義しない。** 手順は
[references/account-planning-session.md](../../references/account-planning-session.md)、
テンプレート化の計画は
[references/account-planning-template-plan.md](../../references/account-planning-template-plan.md)。

```bash
# 1. 台帳から 2 本の仕様を組む（plan.json / review.json）
.venv/bin/python scripts/scalar/build_account_planning.py \
    --ledger accounts/<AE>/<顧客>/account.json --out "out/account-plan/<顧客>/ap"

# 2. オフライン検証。両方通してから API を叩く
for f in plan review; do
  .venv/bin/python scripts/build_deck.py --template templates/scalar-2026.json \
      --spec "out/account-plan/<顧客>/ap/$f.json" --dry-run --strict || break
done

# 3a. 初回
.venv/bin/python scripts/build_deck.py --template templates/scalar-2026.json \
    --spec "out/account-plan/<顧客>/ap/plan.json" \
    --title "<顧客> Account Planning Session FY26" --folder <00_活動計画 の ID>

# 3b. 2 回目以降（§5 と同じく破壊的。スナップショットが先）
.venv/bin/python scripts/snapshot_version.py "<デッキ URL>"
.venv/bin/python scripts/build_deck.py --template templates/scalar-2026.json \
    --spec "out/account-plan/<顧客>/ap/plan.json" --into "<デッキ URL>"
```

URL は台帳の `meta.decks.accountPlanningSession` / `meta.decks.apsReview` に記録する。

#### 台帳に無い欄を埋める順番

APS は活動計画より広い範囲を扱うので、台帳だけでは埋まらない欄が出る。
**順番を守る。**

1. 台帳（`account.json`）から取れるものを取る
2. 足りないものは**顧客の公開情報**から取る（IR・組織図・中期経営計画・決算短信）。
   取ったら台帳の `facts` に `observed` として書き戻す
3. それでも取れないものは **「未取得」と書く**。推測で埋めない

#### 企業グループが相手のとき

親会社 1 社ではなくグループ（銀行・証券・カード・IT 子会社）を相手にする場合、
**商談も関与者も会社ごとに分類する。** 会社が違えば意思決定者も予算も別で、
まとめると打ち手が決まらない。

- **商談番号はグループ会社順に振る**（`build_account_planning.py` の `DEALS`）。
  同じ会社の商談が隣り合う
- **商談ごとに章を切る**。中扉（会社名／商談名／金額・時期・ステージ）＋
  全体像カード 6 枚。**型を全商談で揃える**と、章をまたいで「どこが埋まって
  いないか」を比べられる
- **システム子会社は別立てで扱う。** 全社に関わるので、会社別の担当本部と
  横断組織（技術統括・AI 推進など）を分けたページを置く。横断組織を押さえて
  いても会社別の実装部隊に入れていなければ案件は動かない

#### 組織図は一次情報から取る

顧客の IR / 会社情報ページにある組織図（PDF・PNG）を読み、当社の接点を重ねる。
**台帳の肩書きだけで組織図を描き起こさない** — 接点のない部署が図から消えて、
**空白が見えないという一番大事な情報を失う**。

#### 表ではなく図で出す

表は「登録簿」（担当と期日があり後から追跡するもの）と「判定基準」だけに残す。
それ以外は図にする。対応表は
[account-planning-session.md §9.4](../../references/account-planning-session.md)。

#### つまずきどころ

- **`--dry-run` を通っても API に弾かれる制約が 1 つある。** Slides API は幅 32pt
  （0.45in）未満の表列を拒否する。商談番号のような細い列で踏む。
  `build_account_planning.py` の `table()` が組み立て時に検査している
- `batchUpdate` は原子的なので、途中で失敗しても既存デッキは壊れない。
  直して作り直せばよい
- APS で置く期日は**「本 APS での提案」と出典行に明記する**。台帳の `actions` は
  期日未設定のままにしておき、AE が顧客と合意した時点で台帳へ入れる

### 7. 関与者が 9 人を超えたら

スライドに詰めない。`b2b-account-maps` の既定どおり、全体を draw.io に出して
スライドには抽出版を載せ、落ちた人数を必ず書く。

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

APS を作った回は `plan.json` / `review.json` も同じフォルダへ上げる。

報告に必ず入れるもの:

1. デッキの URL と Drive フォルダの URL
2. ステージ・フォーキャストと、その根拠
3. **次に確認すべきことの最短リスト**（誰に・いつまでに・何が取れたら完了か）
4. 材料不足で落としたページがあれば、その名前と足りない情報
5. APS の回は、**公開情報から補った項目**と、**「未取得」のまま残した項目**

URL ではなく 3 が報告の主役。デッキは手段で、AE が次に取る行動が成果物である。

## Rules

- **台帳が正本。デッキを直接編集しない。** 直すことがあれば台帳を直して作り直す。
- **CRM を置き換えない。** ステージ・金額・予定日・Next Action の正本は CRM。
  台帳を更新したら CRM も揃える（プレイブック §8）。
- **証拠か、さもなくば未確認。** `confirmed` と `met` には出所（誰が・いつ）が要る。
- **絶対に答えを埋めない。** 空欄は AE の次の行動であって、埋める穴ではない。
- **古い活動計画は無いより悪い。** 更新できないなら台帳ごと畳む。
- **APS でも答えを埋めない。** 台帳に無い欄は公開情報で埋めるか「未取得」と書く。
  埋まらない欄そのものが、APS で決めるべきことを指している。
- `accounts/` と `config/` はコミットしない（顧客名・個人名・判断が入る）。
  作業ファイルは無視される `out/` 配下に置く。
