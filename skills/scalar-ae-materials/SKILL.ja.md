---
name: scalar-ae-materials
description: >-
  Build the materials a Scalar Account Executive needs for one customer visit,
  chosen by deal phase and audience: the customer-facing one-pager that opens a
  conversation, the internal visit plan, the WPS win plan that asks for
  proposal investment, and the Deal Desk / 稟議 packet that asks for internal
  approval. Use when asked to prepare for a customer meeting or 訪問; to make
  材料 for a phase-0..6 conversation; to write a 訪問計画, WPS or Deal Desk
  資料; to get internal resources or approval for a deal; or to produce
  顧客提示用 / 社内説明用 資料. Files land under 「AE 名 / 顧客名」 in Drive and
  every run updates the account ledger. Route the standing activity plan to
  `scalar-account-plan`, the formal proposal to `scalar-proposal-slides`, and
  the stakeholder maps to `b2b-account-maps`.
---

*[English](SKILL.md)*

# Scalar AE Materials

**同じ商談情報を、一つの資料で全員に見せてはならない。** このスキルの仕事は、
フェーズ（0〜6）× 相手（顧客 / 社内）× 目的から資料種別を選び、その種別の
必須要件を満たしたものだけを作ることにある。

作業ディレクトリは slide-forge ルート。コマンドは `.venv/bin/python` で実行する。

判断の出典は [references/scalar/sales-playbook.md](../../references/scalar/sales-playbook.ja.md)
（フェーズと移行条件は §2、資料 5 種は §3、品質基準は §4、会議体は §6）。

## Boundaries

| 依頼 | 行き先 |
|---|---|
| 訪問 1 回分の資料一式 | このスキル |
| 社内の承認・リソース獲得（WPS / Deal Desk / 稟議） | このスキル |
| 顧客ごとの活動計画（常設・追記型） | `scalar-account-plan` |
| 年次の Account Planning Session（組織図・商談棚卸しのデッキ） | `scalar-account-planning-session` |
| 正式提案書・見積 | `scalar-proposal-slides` + `spreadsheets` |
| 関与者マップ・ディスカバリーマップ | `b2b-account-maps` |
| 議事録・メールをステージ別の記録に整理する | `scalar-deal-intake` |
| Scalar の会社・製品紹介（顧客固有でない） | `scalar-product-slides` |
| 生成したデッキの目視検査 | `slide-qa` |

## Step 1: フェーズと相手を確定する

**台帳を先に読む。** `accounts/<AE 名>/<顧客名>/account.json` があれば、フェーズ・
関与者・未確認事項はそこにある。無ければ `scalar-account-plan` の手順 1〜2 で作る。

```bash
.venv/bin/python scripts/scalar/account_ledger.py validate <account.json>
.venv/bin/python scripts/scalar/account_ledger.py gaps <account.json>
```

台帳から取れない前提だけを、`AskUserQuestion` で 1 回にまとめて聞く
（`references/interactive-intake.md` §0・§5 の作法に従う）:

1. 誰に会うか（役職・部門・初対面か）
2. この訪問で顧客から得たい一言は何か
3. 社内で得たいもの（提案投資の承認 / 価格承認 / SA の稼働）があるか
4. 生成後にビジュアル QA を行うか（既定・推奨は実行する）

## Step 2: 資料種別を選ぶ（ルーティング）

| 相手 / 目的 | フェーズ | 作るもの | 置き場 | 担当 |
|---|---|---|---|---|
| 社内 / 訪問前の準備 | 全 | `visit-plan` | `90_社内` | このスキル |
| 顧客 / 対話を始める | 0〜2 | `challenge-hypothesis` ＋ 事例 | `01_顧客提示` | このスキル |
| 顧客 / 課題を構造化する | 2 | 課題構造図・As-Is 概要・検討論点 | `01_顧客提示` | このスキル |
| 社内 / 提案投資の判断（WPS） | 2 終了時 | `win-plan` ＋ 3 マップ | `90_社内` | このスキル ＋ `b2b-account-maps` |
| 顧客 / 実現性を見せる | 3 | デモ資料・To-Be・アーキテクチャ概要 | `01_顧客提示` | `scalar-proposal-slides` |
| 顧客 / PoC を合意する | 3 | PoC 提案書・実施計画 | `02_顧客提案` | `scalar-proposal-slides` |
| 社内 / 価格・契約リスクの承認 | 3〜5 | Deal Desk 資料・稟議 | `90_社内` | このスキル |
| 顧客 / 選定と予算化 | 4 | 正式提案書・見積・ROI（ライセンスのページは `license-pattern-compare` + `license-estimate`） | `02_顧客提案` | `scalar-proposal-slides` + `spreadsheets` |
| 顧客 / 契約手続 | 5 | チェックリスト・SOW・注文書 | `02_顧客提案` | `google-slides-template` |
| 社内 / 更新・拡張の計画 | 6 | ヘルスレビュー・更新計画 | `90_社内` | `scalar-account-plan` |

パートナー提示用・パートナー提案用（プレイブック §3 の残り 2 種）は**専用
テンプレート未実装**。依頼されたら `google-slides-template` で作り、必須項目は
プレイブック §3 と原典 §7.5 から拾う。

判断がつかないときだけ `AskUserQuestion` で 1 回確認する。フェーズが台帳にあり、
相手が指定されているなら聞かずに決める。

## Step 3: 顧客提示用に内部情報を混ぜていないか検査する（省略禁止）

顧客に渡す資料（`01_顧客提示` / `02_顧客提案`）を生成する**前に**、
仕様の本文を読んで次を確認する:

- [ ] 個人の影響力・賛否・「未接触」などの判断が入っていないか
- [ ] 競合の弱点を名指ししていないか（顧客が競合に伝える前提で読む）
- [ ] 未確認の事項が、確定事項のように書かれていないか
  → 「本日確認したい」に落とす。推測で埋めない
- [ ] 出典のない数値を載せていないか（公開事例は出典を明記する）
- [ ] 価格・ロードマップが、その相手に開示してよい範囲か —
      `license-estimate` / `license-pattern-compare` の金額は生成済み見積書
      （`scalar-quotation`）からの転記であり、エディション内容・Pod 数の数え方・
      課金モデルは OKF バンドル（`references/scalar/okf-bundle.ja.md`）から取る。
      バンドルの定価は社内情報で参考見積の材料に留め、3年契約・先払いクレジット・
      値引き率は「非公開」— 顧客提示ページに載せない

`challenge-hypothesis` のガードレールにも同じことが書いてある。1 つでも該当したら、
その内容は `90_社内` の資料に移す。

## Step 4: 仕様を書いてオフライン検証する

台帳から作れるページは台帳から作る（手で書き写さない）:

```bash
.venv/bin/python scripts/scalar/account_ledger.py slots <account.json> visit-plan \
    --out out/<顧客名>/visit-plan.json
.venv/bin/python scripts/render_slide_template.py --template visit-plan \
    --data out/<顧客名>/visit-plan.json --out out/<顧客名>/visit-plan.slide.json
```

`visit-plan` は台帳の `visits[]` のうち `status: "planned"` のものから作る。
訪問の目的・問い・想定反論を先に台帳へ書けば、資料は台帳から出てくる。

台帳に無いページ（顧客提示用の事例など）は、`slide-templates` のテンプレートか
`references/slide-pattern-catalog.md` の型で書く。組み上げと検証:

```bash
.venv/bin/python scripts/assemble_spec.py out/<顧客名>/*.slide.json \
    --out out/<顧客名>/deck.json --title "<資料名>"
.venv/bin/python scripts/build_deck.py --template templates/scalar-2026.json \
    --spec out/<顧客名>/deck.json --dry-run --strict
```

指摘が出たら**データを直す**（文言を短くする、人を離す）。テンプレートは直さない。

## Step 5: 生成して正しいフォルダへ置く

```bash
.venv/bin/python scripts/scalar/account_workspace.py ensure --ledger <account.json> --json
```

出た ID から、Step 2 の表の置き場に合わせて `--folder` を選ぶ:

| 種別 | フォルダ |
|---|---|
| 顧客提示用 | `01_顧客提示` |
| 顧客提案用 | `02_顧客提案` |
| 社内説明用 | `90_社内` |
| 活動計画 | `00_活動計画` |

```bash
.venv/bin/python scripts/build_deck.py --template templates/scalar-2026.json \
    --spec out/<顧客名>/deck.json --folder <フォルダ ID>
.venv/bin/python scripts/drive_folder.py upload <フォルダ ID> out/<顧客名>/deck.json
```

**間違ったフォルダに置かない。** 社内資料が `01_顧客提示` に入ると、顧客への
共有で個人の判断がそのまま渡る。

## Step 6: 目視検査

Step 1 で「実行する」を選んだ場合は `slide-qa` スキルの手順で行い、終わったら
`.venv/bin/python scripts/cleanup_qa.py` で検証ファイルを消す。
スキップした場合は、QA 未実施であることを報告に明記する。

## Step 7: 台帳へ戻す（省略禁止）

**訪問資料を作って終わりにしない。** 作った資料と、そこで決めたことを台帳に
書き戻し、活動計画を更新する。これが訪問資料と活動計画が乖離しない唯一の仕掛け。

1. `visits[]` に今回の訪問を足す（訪問前は `status: "planned"`、
   実施後に `status: "done"` と `heard` / `next` を書く）
2. 新しく分かったことを `facts[]` に `kind` つきで足す
3. 満たしたゲートを `gates` に**顧客側の証拠つきで**記録する
4. `scalar-account-plan` の手順 4〜5 で未確認をアクションに変え、活動計画を差し替える

```bash
.venv/bin/python scripts/scalar/build_account_plan.py <account.json> --carry-over
```

## Step 8: 報告

1. 作った資料の名前・種別・デッキ URL・置いた Drive フォルダ
2. 顧客提示用については、Step 3 の検査を通したことと、内部情報を移した項目
3. QA の結果（または未実施であること）
4. **AE のアクションプラン** — 誰に・何を・いつまでに・何が取れたら完了か
   （`out/account-plan/<顧客名>/action-plan.md`）
5. 社内承認を求める資料の場合は、**判断を仰ぐ事項**（継続 / 保留 / 撤退、
   値引きの対価、必要な稼働）を 1 行で

## Rules

- **相手を間違えない。** 資料種別は読み手で決まる。迷ったら社内向けに倒す。
- **ステージは活動量ではなく顧客の合意で進む。** 「説明した」「資料を出した」を
  移行の根拠にしない（プレイブック §1 原則 5）。
- **WHAT・WHY を飛ばさない。** 顧客の要件に HOW だけで答える資料を作らない。
- **推測で埋めない。** 未確認は「本日確認したい」として資料に出す。
- **数値には根拠を付ける。** 出典を書けない数字は載せない。
- 古いテンプレートの顧客名・金額・構成・注記を残さない（プレイブック §4）。
- `accounts/` と `config/` はコミットしない。作業ファイルは `out/` 配下。
