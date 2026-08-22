---
name: hearing-slides
description: >-
  Slides whose job is to collect information rather than deliver it: the agenda
  of what you need to hear, our understanding put up to be corrected, a fill-in
  sheet to write on during the meeting, an event poll, and the page that says
  where to send the answers (with a QR). Driven by the gaps in a hearing sheet;
  never invents an answer to fill a page.
  Use for: 聞くためのスライド, ヒアリング用の資料, 足りない情報を集めるスライド,
  イベントで情報を集めたい, 記入してもらう資料.
  Not: internal "who do we ask next" pages (scalar-ae-materials /
  b2b-account-maps); the proposal itself (scalar-proposal-slides).
---

*[English](SKILL.md)*

# ヒアリング用スライド — 集めるためのページ

先に [`references/hearing-kit.ja.md`](../../references/hearing-kit.ja.md)（正本・
顧客配布版のフィルタ・回答の置き場）と
`references/scalar/workflow-contract.md`（生成・QA・納品の共通規則）を読む。
**このスキルでは繰り返さない。**

作業ディレクトリは slide-forge ルート。コマンドは `.venv/bin/python` で実行する。

## このページ群が他と違うところ

提案書のページは**主張する**。**ここのページは穴を空けて、顧客に埋めてもらう。**
その穴は実在する — `hearing.json` で `未確認` または `推定` のまま残っている項目
から来ている。

- **ページを完成させるために、穴を推測で埋めない。** 材料が足りないページは
  ビルダーが作成を拒否する（終了コード 2）。それはエラーではなく**答え**である。
- すべて顧客提示物なので、顧客フィルタを通った内容だけから作る。内部の節と
  出典・確度の列はスライドに出ない。
- **返すものを書く。** 集めるだけで何も返さないと、次から埋めてもらえなくなる。

## 境界

| 依頼 | 行き先 |
|---|---|
| 顧客・聴衆に情報を求めるスライド | このスキル |
| シートそのものと、回答の読み戻し | `hearing-sheet` |
| 社内向けの「誰にいつ聞くか」（`discovery-gaps`） | `scalar-ae-materials` / `b2b-account-maps` |
| 対話を始めるための課題仮説（`challenge-hypothesis`） | `scalar-ae-materials` |
| 提案書・PoC 計画・見積 | `scalar-proposal-slides` / `spreadsheets` |
| イベントのセグメントとナーチャリング設計 | `scalar-nurture-intake` |

`discovery-gaps` とこのスキルの `hearing-agenda` は似て非なるものである。
`discovery-gaps` は**社内向け**で、空きを確認相手と期限に割り当てる。
`hearing-agenda` は**顧客に見せて**直接聞く。**互いのフォルダに置かない。**

## ページ

| テンプレート | 使う場面 | 生成元 |
|---|---|---|
| `hearing-agenda` | 打ち合わせの冒頭。何をうかがいたいか、なぜか | `未確認` の設問（「聞く」に印のあるものが先） |
| `hypothesis-check` | 途中。こちらの理解を出して訂正してもらう | 確度が `推定` の設問 |
| `fill-in-sheet` | その場で記入（印刷・画面共有） | 選んだ節の `未確認` |
| `event-poll` | 登壇・セミナー。どれに当てはまるか | セグメントの「抱える状況」（`templates/nurture/segment-sheet.ja.md` §1） |
| `collect-cta` | 締め。回答先と、返ってくるもの | `meta.renders.gsheet` または `--where` |
| `collect-qr` | イベントの締め。同じものを QR で | 上記 ＋ `scripts/hearing/qr.py` |

## 手順 1: 実際に何が空いているかを見る

```bash
.venv/bin/python scripts/hearing/hearing_sheet.py gaps <hearing.json> [--section 4]
```

上の一覧からではなく、**そこにある空きから**ページを選ぶ。

- `推定` が無い → **`hypothesis-check` は作らない。** 訂正してもらう理解がまだ
  無い。ページを埋めるために理解を捏造することこそ、このスキルが防ぐ対象である。
- `未確認` が 3 件未満 → シートはほぼ埋まっている。聞くためのデッキ 1 本は過剰。
  そう言って、合う 1 枚だけを出す。
- 複数の節が空いている → `--section` で分ける。インフラの質問と予算の質問を
  1 枚に混ぜない。

## 手順 2: データを作り、ページにする

```bash
.venv/bin/python scripts/hearing/hearing_slots.py <hearing.json> hearing-agenda \
    --out out/<顧客名>/agenda.json --section 4
.venv/bin/python scripts/render_slide_template.py --template hearing-agenda \
    --data out/<顧客名>/agenda.json --out out/<顧客名>/agenda.slide.json
```

生成される文言は**出発点であって成果物ではない**。組み立てる前に `title` と
`lead` を顧客の状況と語彙に書き換える。**紋切り型の資料には紋切り型の回答しか
返ってこない。**

QR ページを作るなら、先に画像を作って**飛び先を確認する**。

```bash
.venv/bin/python scripts/hearing/qr.py "<回答先の URL>" --out out/<顧客名>/qr.png
```

`qrcode` が入っていない場合はプレースホルダを書き出して終了コード 2 を返す。
**プレースホルダを顧客の前に出さない。** `qrcode[pil]` を入れるか、URL を文字で
持つ `collect-cta` を使う。

## 手順 3: 組み立て・検証・生成

```bash
.venv/bin/python scripts/assemble_spec.py out/<顧客名>/*.slide.json \
    --out out/<顧客名>/deck.json --title "<資料名>"
.venv/bin/python scripts/build_deck.py --template templates/scalar-2026.json \
    --spec out/<顧客名>/deck.json --dry-run --strict
```

検査が出たら**データを直す**（文言を短くする、行を減らす）。テンプレートを
直さない。そのうえで `01_顧客提示` に生成する（顧客に聞くページは顧客提示物
である）。QA と後片付けは共通の契約に従う。

## 手順 4: ループを閉じる

**読み戻されない収集ページは飾りである。** 報告に次を書く。

1. 作ったページと、材料不足で作らなかったページ
2. 各ページが何を求めているか、シートのどの ID を埋めるためか
3. **回答をどう戻すか** — `hearing-sheet` の `read`。シートを出す前に baseline
   を取っておくこと
4. このデッキの後にまだ残る空きと、誰なら答えられるか

イベントの回答は**型と件数に集約してから** `accounts/_nurture/` に入れる。
企業が特定できるものはセグメントではなく商談である
（`references/hearing-kit.ja.md` §4）。

## ファイル

| パス | 役割 |
|---|---|
| `slide-templates/hearing/` | 6 種のページテンプレートと例 |
| `scripts/hearing/hearing_slots.py` | hearing.json → slot データ（薄いページは作らない） |
| `scripts/hearing/qr.py` | 回答先の QR（`qrcode` は任意） |
| `references/hearing-kit.ja.md` | `hearing-sheet` との共通規約 |
