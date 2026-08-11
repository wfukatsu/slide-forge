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
  from a companion aps.json, including who to meet next, worked out per legal
  entity from published officer lists and org charts. Produces the action plan
  (slides + Markdown) that turns
  unanswered questions into dated commitments. Route one visit's materials to
  `scalar-ae-materials`, the customer proposal to `scalar-proposal-slides`, and
  the stakeholder/discovery maps themselves to `b2b-account-maps`.
---

# Scalar Account Plan

顧客 1 社につき台帳 1 つ。**台帳が正本**で、デッキはその表示にすぎない。
訪問のたびに台帳へ追記し、同じ URL のデッキを最新化する。

顧客ごとに作るデッキは 2 系統。寿命も入力も違うので混ぜない。

| | 活動計画デッキ（§5） | APS デッキ（§6） |
|---|---|---|
| 目的 | 今どこにいて次に何をするか | 年次・半期の棚卸しと役員レビュー |
| 更新 | 訪問のたび | APS のたび |
| 入力 | `account.json`（台帳） | `aps.json`（台帳 + 顧客の公開情報） |

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
accounts/<AE 名>/<顧客名>/aps.json       APS デッキの内容（同上）

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

**入力は台帳ではなく `accounts/<AE>/<顧客>/aps.json`。** 台帳（`account.json`）は
訪問ごとの事実を貯める場所で、APS は顧客の公開情報も混ぜて 1 年分を組み立てる
ので、入力を分けてある。`aps.json` も `accounts/` 配下なので Git 管理外。

```
accounts/<AE>/<顧客>/
  account.json   訪問ごとの事実（§1-4。活動計画デッキの入力）
  aps.json       APS デッキの内容（見出し・図の中身・商談・役員名簿・中扉の考慮点）
```

**スクリプトには顧客名も実名も書かない。** `build_account_planning.py` が持つのは
図の種類・座標・書式（`LAYOUT`）だけで、文字列はすべて `aps.json` から読む。

```bash
# 1. aps.json から 2 本の仕様を組む（plan.json / review.json）
.venv/bin/python scripts/scalar/build_account_planning.py \
    --aps "accounts/<AE>/<顧客>/aps.json" --out "out/account-plan/<顧客>/ap"

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

役員名簿と組織図は 2 の中心。取り方は下の「会うべき人を探す」。

#### 企業グループが相手のとき

親会社 1 社ではなくグループ（銀行・証券・カード・IT 子会社）を相手にする場合、
**商談も関与者も会社ごとに分類する。** 会社が違えば意思決定者も予算も別で、
まとめると打ち手が決まらない。

- **商談番号はグループ会社順に振る**（`aps.json` の `deals[]`）。
  同じ会社の商談が隣り合う
- **商談ごとに章を切る**。中扉（会社名／商談名／金額・時期・ステージ）＋
  全体像カード 6 枚。**型を全商談で揃える**と、章をまたいで「どこが埋まって
  いないか」を比べられる
- **システム子会社は別立てで扱う。** 全社に関わるので、会社別の担当本部と
  横断組織（技術統括・AI 推進など）を分けたページを置く。横断組織を押さえて
  いても会社別の実装部隊に入れていなければ案件は動かない

#### 組織図は一次情報から、法人ごとに 1 枚

顧客の IR / 会社情報ページにある組織図（PDF・PNG）を読み、当社の接点を重ねる。
**台帳の肩書きだけで組織図を描き起こさない** — 接点のない部署が図から消えて、
**空白が見えないという一番大事な情報を失う**。

**グループが相手なら、法人ごとに 1 枚ずつ描く。** グループ全体を 1 枚にまとめると
各社の部レベルが潰れて、どの部署に入れていないかが見えない。持株会社の
グループ体制図とは別に、事業会社と IT 子会社の組織図をそれぞれ置く。

- 組織図が PDF や画像でしか出ていないことが多い。読めなければ組織変更の
  ニュースリリースが代わりになる（新設・改称・移管が書かれている）
- **人の出所も拾う。** 異動リリースには出向元が載ることがあり、
  「この会社のシステム部門は誰が押さえているのか」がそこで分かる

#### 会うべき人を探す（APS のもう半分）

アカウントプランは会った人の記録ではない。**次に誰に会うべきかを出す仕組み**
でもある。台帳だけを見ていると、既に会えている人の周りしか出てこない。

**役員名簿は法人単位で取る。** 企業グループは持株会社・事業会社・IT 子会社が
それぞれ別法人として役員を公開している。グループを 1 つの「顧客」として
まとめると、実装を持つ役員がどの法人にいるのか分からなくなる。

情報源（いずれも公開情報）:

| 何を | どこから |
|---|---|
| 役員の氏名と役職 | 各法人の「会社概要」「役員一覧」 |
| 役職の変更・新任 | 「役員異動のお知らせ」のニュースリリース |
| 部署の一覧 | 組織図（前項） |
| 担当領域 | 持株会社の CxO 一覧には担当部署が書かれていることがある |

やること:

1. **法人ごとに役員名簿を取り、当社の接触状況を重ねる。** 接触済み / 未接触が
   法人別に見えると、どの法人で層が薄いかが分かる
2. **兼務を必ず拾う。** 持株会社の CxO が子会社の取締役を兼ねていることがある。
   **それが最短の紹介経路になる**ので、組織図にも書き込む
3. **組織図と役員名簿を突き合わせる。** 組織図は「どの部署があるか」、名簿は
   「誰が役員か」しか教えない。**部署と役員の紐付けは公開情報では埋まらない
   ことが多く、そこがそのまま確認事項になる**（「役員の担当組織を聞く」）
4. **手がかりは接触済みの人を起点にする。** 誰経由で辿るかが書けない
   「会うべき人」はアクションにならない。書けないならまず起点を作る
5. **役職は公開名簿を正とする。** 台帳の肩書きが古ければ台帳を直す

出力は 2 ページ:

| ページ | 図 | 何を示すか |
|---|---|---|
| 法人別の役員層と接触状況 | `comparison` | 法人ごとの役員数・接触済み・未接触の要人 |
| 会うべき人と手がかり | 表（登録簿） | 誰に / なぜ / **誰経由で** / いつまでに |

#### 経歴と関係性

誰に会うかが決まったら、**その人が何を根拠に判断する人なのか**を押さえる。
役職だけでは、こちらの説明がどこで刺さるか決められない。

- **肩書きの変遷を追う。** 決裁者が過去にどのポジションで何を決め、何を公に
  言ったかは、今の反応を予測する一番強い材料になる。役員異動のリリース、
  新聞の人事欄、インタビュー記事から取れる
- **前任・後任、兼務、出向元を拾う。** 「前任者が今どこにいるか」「持株の役員が
  子会社の取締役を兼ねているか」は、そのまま意思決定の経路になる
- **個人的な関係（元上司・友人・派閥）は面談や社内でしか取れない。**
  公開情報と混ぜず、出典行で必ず分ける。**この種の記述が入った時点で、その
  資料は社外に出せない**

出力は 2 ページ:

| ページ | 図 | 何を示すか |
|---|---|---|
| 主要人物の経歴 | `cards` | 1 人 1 枚。肩書きの変遷と、そこから読める判断の癖 |
| 人物の関係性 | `influence_graph` + `links` | レポートラインに、兼務・前任後任・個人的な関係を重ねる |

`links` は**同じ階層の人どうししか結べない**（階層をまたぐと組み立て時に落ちる）。
階層をまたぐ関係は `more` の注記に置く。

#### 表ではなく図で出す

表は「登録簿」（担当と期日があり後から追跡するもの）と「判定基準」だけに残す。
それ以外は図にする。対応表は
[account-planning-session.md §9.4](../../references/account-planning-session.md)。

#### つまずきどころ

- **`--dry-run` を通っても API に弾かれる制約が 1 つある。** Slides API は幅 32pt
  （0.45in）未満の表列を拒否する。商談番号のような細い列で踏む。
  `build_account_planning.py` の `_check_columns()` が組み立て時に検査している
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

APS を作った回は `aps.json` と `plan.json` / `review.json` も同じフォルダへ上げる。

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
- **会った人の記録で終わらせない。** 公開の役員名簿から**会うべき人**を出し、
  接触済みの人を起点にした手がかりを付ける。起点が書けないなら、まず起点を作る
  ことがアクションになる。
- `accounts/` と `config/` はコミットしない（顧客名・個人名・判断が入る）。
  作業ファイルは無視される `out/` 配下に置く。
