---
name: scalar-nurture-intake
description: >-
  Turn raw pre-deal signals — webinar and seminar attendance, inbound enquiry
  email, download logs, community and Slack questions, event badge notes,
  partner referrals, CRM/MA exports — into segment definitions, five-stage
  nurture tracks and a content ledger, using the nurture map derived from the
  Scalar nurture plan sheet. Use when asked to 「ナーチャリングを設計して」
  「リード育成」「問い合わせからセグメントを起こして」「ウェビナーの参加者を整理して」
  「コンテンツの棚卸し」「MQL / SQO」, to work out which content is missing for a
  segment, or to decide whether a lead is ready to hand to sales. Works on
  segment types, never on named individuals or customers. Once a lead is handed
  over, the per-customer records go to `scalar-deal-intake`, the deck to
  `scalar-product-slides`, and the customer proposal to `scalar-proposal-slides`.
---

*[English](SKILL.md)*

# Scalar Nurture Intake

商談化前のシグナルを入れて、ナーチャリングの設計を出す。成果物は
`accounts/_nurture/` 配下の Markdown。**このスキルはスライドを作らない。**

作業ディレクトリは slide-forge ルート。

判断の出典。**このスキルでこれらを再定義しない。**

| 観点 | 出典 |
|---|---|
| ナーチャリング 5 ステージ、製品・セグメントレイヤー、シートの未完成箇所 | [`references/scalar/nurture-map.ja.md`](../../references/scalar/nurture-map.ja.md) |
| 引き渡し先の商談ステージと `g1.*` ゲート | [`stage-io-map.ja.md`](../../references/scalar/stage-io-map.ja.md) / [`sales-playbook.ja.md`](../../references/scalar/sales-playbook.ja.md) |
| 課題→製品のマッピング | [`proposal-map.ja.md`](../../references/scalar/proposal-map.ja.md) |

## Boundaries

| 依頼 | 行き先 |
|---|---|
| セグメントの定義／ナーチャリング設計／コンテンツの充足確認 | このスキル |
| そのリードを営業に渡してよいかの判断 | このスキル（§6） |
| 商談化した後の、顧客 1 社ごとの記録 | `scalar-deal-intake` |
| 台帳（`account.json`）と活動計画デッキ | `scalar-account-plan` |
| 訪問 1 回分の資料 | `scalar-ae-materials` |
| 会社・製品紹介デッキ（顧客固有でない） | `scalar-product-slides` |
| 顧客別の提案書 | `scalar-proposal-slides` |

## ナーチャリングのファイルは「型」を持つ。人を持たない

セグメントは**パターン**であって、人でも会社でもない。参加者リスト・問い合わせ
メール・CRM エクスポートには個人情報が入るが、ナーチャリングのファイルには入れない。

- `accounts/_nurture/` に、**個人名・会社名・メールアドレス・個人に紐づく役職を書かない。**
- シグナルは型に集約する。「直近四半期に、カラムの多義化に当たった MySQL ユーザーから
  3 件の問い合わせ」と書く。誰が送ったかは書かない。
- **「誰から来たか」が重要なシグナルは、セグメントではなく商談**である。
  `scalar-deal-intake` に回す。

`accounts/` は `.gitignore` 済み。どちらの側も記入済みファイルをコミットしない。

## 手順

### 1. 渡された材料を先に全部読む

参加ログ・問い合わせメール・資料ダウンロードログ・コミュニティのスレッド・展示会の
メモ・パートナー経由の相談・CRM / MA エクスポートを、質問する前に読む。
ローカルパス、貼り付けテキスト、Drive URL、Gmail スレッドのいずれも受け取る。

読んだものは**件数と日付**で記録する（「ウェビナー 2026-07-15、参加 42 名、
うち質問 11 件」）。名簿を写さない。

### 2. セグメントを特定する

```bash
ls accounts/_nurture/segments/
ls accounts/*/            # 進行中の商談。セグメント化の前に必ず見る
```

**先に、そのシグナルが既存商談の関係者から来ていないかを確かめる。**
進行中の商談の担当者に育成コンテンツを当てるのは事故である。

| 照合の結果 | やること |
|---|---|
| 既存商談の顧客から来ている | **セグメントに入れない。** `scalar-deal-intake` に回す。材料はその商談の `deal-log.md` §1 へ |
| 既存商談の顧客だが、別部門・別ユースケース | 商談側の AE に**先に知らせる**。育成に乗せるかは AE が決める |
| 商談が無い | 通常どおりセグメント化に進む |

照合したこと自体は記録してよいが、**照合に使った社名・個人名を
`accounts/_nurture/` に書かない**。書くのは「既存商談と重複 1 件・除外」のような
件数だけである。

各シグナルを、既存のセグメント定義と `nurture-map.ja.md` §5 の一覧に照合する。
結果は 3 つのどれかになる。

| 結果 | やること |
|---|---|
| 既存セグメントに一致 | そのトラックに根拠を追記する |
| 近いが状況が違う | 既存セグメントの**バリエーション**として記録する。まだ分割しない |
| どれにも当たらない | 「候補セグメント」として件数つきで保留する |

**1 件のシグナルからセグメントを作らない。** 問い合わせ 1 件は逸話である。
同じ状況が **3 回以上**現れたとき、または意図的に投資すると決めたときに採番へ昇格させ、
**どちらの理由で昇格させたかを記録する。**

採番するときは既存一覧を必ず確認し、**番号を再利用しない**。元シートには
`AWS #009` の重複がある（`nurture-map.ja.md` §7-2）。同じことを増やさない。

### 3. ナーチャリングの段を判定する

段は**買い手が何を探しているか**で決まる（`nurture-map.ja.md` §1）。
ダウンロード数では決まらない。

| シグナルから読み取れる状態 | 段 |
|---|---|
| まだ直すべきものがあると思っていない | 0. Education |
| 課題は分かっているが、プロジェクトが無く、絞り込めていない | 1. Need |
| 解決に繋がる製品を探している | 2. Research |
| 候補を比較して絞り込んでいる | 3. Evaluation |
| 導入を意思決定する | 4. Selection |

**「ウェビナーに参加した」は段ではない。** そう判断した買い手の状態と、その根拠に
なったシグナルを書く。

### 4. トラックを埋める

```bash
mkdir -p accounts/_nurture/segments accounts/_nurture/tracks
cp templates/nurture/segment-sheet.ja.md      accounts/_nurture/segments/<Segment No.>.md
cp templates/nurture/nurture-track.ja.md      accounts/_nurture/tracks/<Segment No.>.md
cp templates/nurture/content-inventory.ja.md  accounts/_nurture/content-inventory.md
```

既にあるファイルは**編集前にスナップショット**を取り（`cp x.md x.md.bak-YYYYMMDD`）、
上書きではなく追記する。

材料が実際に効く場所は決まっている。

| 材料 | 効く場所 |
|---|---|
| ウェビナー・コミュニティで出た質問 | §7 パワースクリプトの想定反論と分岐 |
| 問い合わせメールの文面 | §1〜§5 のストーリー（買い手の言葉のまま） |
| 何をどの順にダウンロードしたか | §10 コンテンツの充足状況、および段の判定 |
| 答えられなかった質問 | §11 未確定事項、およびコンテンツの欠落 |
| リードが止まった理由 | §6 Re-Engagement |

ストーリーは買い手の物語として書く。売り手の説明にしない。検証していない主張は
`（仮説）` と明記して残す。元シートがそうしており、真似する価値がある。

### 5. コンテンツ台帳を更新する

`content-inventory.md` §2（ステージ別の充足状況）を埋める。
**`無` が最も多い段が、そのトラックの詰まっている場所**である。欠落を平坦に並べず、
どこが詰まっているかを名指しする。

事例・価格・エディション構成・性能値には **3 ヶ月ルール**を適用する
（`nurture-map.ja.md` の鮮度注意）。切れたものは `要更新` にする。**消さない。**

### 6. 引き渡しか、Re-Engagement かを判定する

シートに MQL / SQO の定義が無いため、商談側のゲートを使う（`nurture-map.ja.md` §2）。

| 判定 | ゲート |
|---|---|
| MQL → SQO を打診してよい | `g1.problem-recognized` |
| 商談 1 を開始してよい | `g1.owner-reached` |
| 商談 2 へ進める | `g1.timeframe-6q` |

判定は `met` / `partial` / `unmet`。**資料のダウンロードやウェビナーの参加は
`met` の根拠にならない。**

**引き渡し先の商談ステージを、ナーチャリングの段から決めない。** 段は買い手の関心の
位置、商談ステージは合意の到達点で、別の物差しである（`nurture-map.ja.md` §2）。
**起票は原則、商談 1 から**。段 4（Selection）から来たリードはとくに、
「商談 4 に居る」のではなく**「商談 1 に居て、顧客の時計だけが商談 4 に進んでいる」**
と読む。`g2.goal-agreed` と `decisionCriteria` を飛ばしたまま提案に進める提案をしない。
discovery を短縮せざるを得ない場合は、落としたものを `deal-log.md` §3 のリスクとして
引き渡す。

引き渡すときに渡すもの: 接触履歴／閲覧したコンテンツ／出てきた質問／未回答の質問。
**個人名を伴う情報は商談側にだけ置く**（`accounts/<AE 名>/<顧客名>/`）。
以降の記録は `scalar-deal-intake` が持つ。

止まっているリードは §6 を埋める。どの段で止まったか、想定される理由、戻す先の段、
当てるコンテンツ、実施間隔。

### 7. 差分を報告する

日本語で次を返す。

1. 作成・更新したファイルと、追記した内容
2. シグナルがどのセグメントに入ったか、候補のまま残ったものはどれか（件数つき）
3. コンテンツが最も薄い段と、次に作るべきもの
4. 営業へ引き渡せるリードと、そのゲート根拠
5. 材料が既存トラックと矛盾している箇所

## やってはいけないこと

- `accounts/_nurture/` に個人名・会社名・連絡先を書かない。それが必要な依頼は
  `scalar-deal-intake` の仕事。
- シグナル 1 件でセグメントを作らない・採番しない。
- 活動量で段を判定しない。
- シートの製品訴求を現行のものとして扱わない。2021 年のもので、ScalarDB Cluster・
  ScalarDB Analytics・異種 RDB 横断が入っていない（`nurture-map.ja.md` §7-8）。
  古い訴求の上に立ったセグメントは、そう言う。
- 指標の目標値を作らない。元シートに指標が無い（`nurture-map.ja.md` §7-10）。
  目標欄は空のままにして、決めるべき事項として報告する。
- **同意記録・配信停止記録を `accounts/_nurture/` に書かない。** 個人に紐づく情報で、
  置き場は MA / CRM 側（`nurture-map.ja.md` §8）。ここに書くのは、到達手段ごとの
  同意の根拠という型の情報だけ（`segment-sheet.ja.md` §4）。
- **配信の適法性について判断を下さない。** 同意・配信停止・表示義務は
  `nurture-map.ja.md` §8 の論点一覧を提示するに留め、**法務の確認が要ると報告する**。
  到達手段の同意根拠が空欄のトラックは、**配信可能として報告しない**。
- ナーチャリングの段番号を商談ステージに写さない（上記 §6）。
