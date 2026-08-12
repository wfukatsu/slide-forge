---
name: scalar-account-planning-session
description: >-
  Build the Account Planning Session (APS / アカウントプランニングセッション)
  decks for a customer a Scalar Account Executive already keeps a ledger for:
  a full Plan Document for the account team and a nine-page executive review
  deck, from one aps.json. Works out who to meet next per legal entity from
  published officer lists and org charts, ties the proposals to the customer's
  own mid-term management plan, and gives a chapter to each deal. Use for an
  APS / アカウントプランニングセッション / 年次のアカウント棚卸し / 役員レビュー
  資料, or when asked to map a customer group's organisation, officers or key
  people. The per-visit ledger and the activity-plan deck stay in
  `scalar-account-plan`; one visit's materials go to `scalar-ae-materials`.
---

*[English](SKILL.md)*

# Scalar Account Planning Session

APS は**年次・半期のアカウント棚卸し**。訪問のたびに更新する活動計画
（`scalar-account-plan`）とは寿命も入力も違うので混ぜない。

| | 活動計画デッキ | APS デッキ（このスキル） |
|---|---|---|
| 目的 | 今どこにいて次に何をするか | 年次・半期の棚卸しと役員レビュー |
| 更新 | 訪問のたび | APS のたび |
| 入力 | `account.json`（台帳） | `aps.json`（台帳 + 顧客の公開情報） |
| スキル | `scalar-account-plan` | このスキル |

**前提として台帳が要る。** 台帳の作り方・検証・未確認をアクションに変える手順は
[`scalar-account-plan`](../scalar-account-plan/SKILL.ja.md) §1–4 にある。
**このスキルでそれらを再定義しない。**

作業ディレクトリは slide-forge ルート。コマンドは `.venv/bin/python` で実行する。

判断の出典は [references/scalar/sales-playbook.md](../../references/scalar/sales-playbook.ja.md)。
ページ定義と各ページの判断基準は
[references/account-planning-session.md](../../references/account-planning-session.ja.md)。
**どちらもこのスキルで再定義しない。**

> [references/account-planning-template-plan.md](../../references/account-planning-template-plan.ja.md)
> は**まだ実装されていない計画書**。`slide-templates/account-planning` パックは
> 存在せず、現物は `LAYOUT` + `aps.json` の形で動いている。マスター非依存の
> 設計契約（§2）と列幅の下限だけが現行仕様で、テンプレート一覧は将来案。

## Boundaries

| 依頼 | 行き先 |
|---|---|
| APS の資料を作る / 更新する | このスキル |
| 台帳を作る・追記する・状況を答える | `scalar-account-plan` |
| 訪問 1 回分の資料 / WPS / Deal Desk | `scalar-ae-materials` |
| 関与者マップ・ディスカバリーマップそのものの作図 | `b2b-account-maps` |
| 顧客向けの正式提案書 | `scalar-proposal-slides` |
| 生成したデッキの目視検査 | `slide-qa` |

## これは内部資料である

APS は名前のある個人について判断を記録する（影響力、賛否、未接触、経歴、
個人的な関係）。**顧客にもパートナーにも渡さない。** Drive 上でも
`00_活動計画` と `90_社内` は共有しない。

## 成果物と置き場

| 成果物 | 中身 | 読み手 |
|---|---|---|
| Plan Document | 全ページ。分析・商談ごとの章・実行計画 | アカウントチーム |
| APS レビュー資料 | 本編 9 ページ + Appendix | 役員レビュー（30 分） |

```
accounts/<AE>/<顧客>/
  account.json   訪問ごとの事実（scalar-account-plan が管理）
  aps.json       APS デッキの内容（見出し・図の中身・商談・役員名簿・中扉の考慮点）
                 ★ いずれも gitignore 済み。コミットしない
```

**スクリプトには顧客名も実名も書かない。** `build_account_planning.py` が持つのは
図の種類・座標・書式（`LAYOUT`）だけで、文字列はすべて `aps.json` から読む。

## Workflow

### 1. aps.json の欄を埋める

台帳だけでは埋まらない欄が出る。**順番を守る。**

1. 台帳（`account.json`）から取れるものを取る
2. 足りないものは**顧客の公開情報**から取る（IR・組織図・中期経営計画・決算短信）。
   取ったら台帳の `facts` に `observed` として書き戻す
3. それでも取れないものは **「未取得」と書く**。推測で埋めない

役員名簿と組織図が 2 の中心（§4・§5）。

### 2. 中期経営計画に紐付ける

中計は**顧客が自分で公開した優先順位**。提案をそこに接続できれば、稟議に書く
言葉が顧客自身の言葉になる。

- **一次資料から原文を取る。** 中計のリリース PDF と IR の該当ページ。要約記事で
  代用しない。スライドには原文の表現をそのまま置く（言い換えると接続が切れる）
- **柱の構造を見る。** IT が事業戦略の下にあるのか、並列の柱として置かれているのかで
  **稟議のルートが変わる**。並列なら事業側の合意を待たずに CIO ラインで立つ
- **紐付けは柱ではなく記述単位で行う。** 投資額のような柱の見出しではなく、
  その下にある「何をどう変えるか」を書いた具体的な一文に当てる
- **紐付かない提案は無理に紐付けない。** 紐付かないこと自体が「顧客の優先順位に
  乗っていない」という情報で、それは提案の作り直しか、時期の判断材料になる

出力は 2 ページ（どちらも `mece_tree`）:

| ページ | 何を示すか |
|---|---|
| 中期経営計画の構造 | 柱の関係。IT がどこに置かれているか |
| 中計と提案の紐付け | 中計の記述（原文）→ 当社の提案。商談番号で本編とつなぐ |

### 3. 企業グループが相手のとき

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

### 4. 組織図は一次情報から、法人ごとに 1 枚

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

### 5. 会うべき人を探す（APS のもう半分）

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
| 部署の一覧 | 組織図（§4） |
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

### 6. 経歴と関係性

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

関与者が 9 人を超えたら全体版を draw.io に出す。手順は
[`scalar-account-plan`](../scalar-account-plan/SKILL.ja.md) §7。
**企業グループなら必ず `--layout grouped`。**

### 7. 表ではなく図で出す

表は「登録簿」（担当と期日があり後から追跡するもの）と「判定基準」だけに残す。
それ以外は図にする。対応表は
[account-planning-session.md §9.4](../../references/account-planning-session.ja.md)。

### 8. 2 本のデッキを生成する

```bash
# 1. aps.json から 2 本の仕様を組む（plan.json / review.json）
.venv/bin/python scripts/scalar/build_account_planning.py \
    --aps "accounts/<AE>/<顧客>/aps.json" --out "out/account-plan/<顧客>/ap"

# 2. オフライン検証。両方通してから API を叩く
for f in plan review; do
  .venv/bin/python scripts/build_deck.py --template templates/scalar-2026.json \
      --spec "out/account-plan/<顧客>/ap/$f.json" --dry-run --strict || break
done

# 3a. 初回。plan / review を別々のデッキとして作る（2 本とも作ること）
.venv/bin/python scripts/build_deck.py --template templates/scalar-2026.json \
    --spec "out/account-plan/<顧客>/ap/plan.json" \
    --title "<顧客> Account Planning Session FY26" --folder <00_活動計画 の ID>
.venv/bin/python scripts/build_deck.py --template templates/scalar-2026.json \
    --spec "out/account-plan/<顧客>/ap/review.json" \
    --title "<顧客> APS レビュー資料 FY26" --folder <00_活動計画 の ID>

# 3b. 2 回目以降（破壊的。スナップショットが先）。2 本とも差し替える
for f in plan review; do
  .venv/bin/python scripts/snapshot_version.py "<$f のデッキ URL>"
  .venv/bin/python scripts/build_deck.py --template templates/scalar-2026.json \
      --spec "out/account-plan/<顧客>/ap/$f.json" --into "<$f のデッキ URL>"
done
```

**2 本の URL は台帳の `meta.decks.accountPlanningSession` /
`meta.decks.apsReview` に手で書く。** `build_account_planning.py` は台帳を
読み書きしないので、ここは自動化されていない。

**材料が足りないページは自動で落ちない。** 活動計画デッキは材料の無いページを
黙って外すが、APS は `aps.json` に無いページ ID を並びが参照していると
組み立て時にエラーで止まる。

**ページを減らすときは `aps.json` の `meta.skipPages` が第一の手段。**
スクリプトの並び（`PLAN_A` / `REVIEW_*`）を直すのは、全顧客共通で
ページ構成を変えるときだけ。

- ページ ID のリストなら**両方のデッキ**から、`{"plan": [...], "review": [...]}`
  なら**指定したデッキだけ**から外す
- 商談章にも効く（`deal-<商談番号>`）。章の中身が全部 skip されると
  **中扉ごと落ちる**
- 存在しないページ ID や不正なデッキ名は `ValueError` で止まる
  （タイポを黙って無視しない）
- 両方のデッキで skip したページは `pages` からデータを消してもよい
  （残しておけば、外した判断は戻せる）

**顧客ごとの構成判断も `aps.json` の `meta` が持つ**（スクリプトにハードコード
しない）:

| キー | 何を決めるか | 例 |
|---|---|---|
| `meta.dealExtraPages` | 商談章の中扉の後ろに足す付録ページ（商談 ID → ページ ID 列） | `{"1": ["objective-ledger"]}` |
| `meta.reviewDealPages` | 役員レビュー Appendix に載せる商談ページの ID 列 | `["deal-1", "deal-3", "objective-ledger"]` |

ページ ID は役割の総称（`bank-orgchart` / `securities-orgchart` /
`itsub-orgchart` / `itsub-mapping` など）で、顧客名は入らない。

`--into` の禁則（テンプレート原本を差し替え先にしない等）は
[`scalar-account-plan`](../scalar-account-plan/SKILL.ja.md) §5 と同じ。

### 9. 目視検査と報告

`slide-qa` でサムネイルを確認し、終わったら `scripts/cleanup_qa.py`。

```bash
.venv/bin/python scripts/drive_folder.py upload <00_活動計画 の ID> \
    accounts/<AE>/<顧客>/aps.json \
    out/account-plan/<顧客>/ap/plan.json out/account-plan/<顧客>/ap/review.json
```

報告に必ず入れるもの:

1. 2 本のデッキ URL と Drive フォルダの URL
2. **公開情報から補った項目**と、**「未取得」のまま残した項目**
3. **次に会うべき人**（誰に・誰経由で・いつまでに）
4. 台帳と食い違った肩書き・事実があれば、その一覧（台帳を直すかは AE の判断）

## つまずきどころ

- **`--dry-run` を通っても API に弾かれる制約が 1 つある。** Slides API は幅 32pt
  （0.45in）未満の表列を拒否する。商談番号のような細い列で踏む。
  `build_account_planning.py` の `_check_columns()` が組み立て時に検査している
- `batchUpdate` は原子的なので、途中で失敗しても既存デッキは壊れない。
  直して作り直せばよい
- APS で置く期日は**「本 APS での提案」と出典行に明記する**。台帳の `actions` は
  期日未設定のままにしておき、AE が顧客と合意した時点で台帳へ入れる

## Rules

- **答えを埋めない。** 台帳に無い欄は公開情報で埋めるか「未取得」と書く。
  埋まらない欄そのものが、APS で決めるべきことを指している。
- **会った人の記録で終わらせない。** 公開の役員名簿から**会うべき人**を出し、
  接触済みの人を起点にした手がかりを付ける。起点が書けないなら、まず起点を作る
  ことがアクションになる。
- **公開情報と社内由来を出典行で分ける。** 個人的な関係が入った資料は社外に出せない。
- **台帳が正本。** APS で分かった事実は `account.json` にも書き戻す。
- `accounts/` はコミットしない（顧客名・個人名・判断が入る）。
  作業ファイルは無視される `out/` 配下に置く。
