# Account Planning Session スライド作成手順

Account Planning Session（以下 APS）用のデッキを、事前準備 → ワークショップ →
サマリー化 → 生成の順に組み立てるための手順書。

## 0. この文書の出典と扱い

- 元資料: `FY17_AP_Template_Training_Public.pptx`（Oracle Key Account PMO、
  2016-06-29、106 ページ）。
- 元資料から取ったもの: **成果物の 2 分類、3 フェーズの流れ、22 種類のページ
  定義、ワークショップの進め方、各ページの情報源と考慮点**。
- Scalar 向けに読み替えたもの: 製品名・組織名・レビュー体制・金額単位。
  読み替え表は §12。
- 関連ドキュメント: `skills/scalar-account-plan/SKILL.md`（顧客ごとの活動計画
  台帳）、`references/scalar/sales-playbook.md`（ステージとゲート定義）、
  `references/account-planning-template-plan.md`（ページテンプレートの実装計画）。

元資料は「テンプレートの書式に厳密に従う必要はなく、参考にするためのサンプル
としての使い方でも OK」と明記している。この手順書も同じ立場を取る。**埋める
ことが目的ではなく、埋まらない欄が「まだ聞けていないこと」を示すことが目的。**

## 1. 最初に決めること: どちらの成果物を作るのか

元資料は Account Plan を 2 つの別物として分けている。この区別を最初に確定しない
と、ページ数も密度も決まらない。

| | **Plan Document**（アカウントチーム用） | **Session 資料**（レビュー用） |
|---|---|---|
| 目的 | 上流エンゲージメントのための戦略計画 | 30 分レビューでの意思決定 |
| 読み手 | アカウントチーム、Sales VP、Executive Sponsor | レビュー実施者（役員） |
| ページ数 | 制約なし。過去資産があると 100 ページ超もある | **1 桁ページ + Appendix** |
| 更新 | 合宿・APS で大改訂、以降は随時マイナー更新 | APS のたびに作成・改訂 |
| 密度 | 読み物として成立させる | 1 ページ 1 メッセージ |

本手順書は **両方を 1 本のパイプラインで作る**。Phase A〜C で Plan Document を
組み立て、そこから Session 資料を抜き出す（§7）。

## 2. 全体の流れ

```
  [事前準備]                    [ワークショップ]           [ワークショップ後]
       │                              │                          │
┌──────▼───────────────┐  ┌───────────▼──────────┐  ┌────────────▼──────────┐
│ Phase A               │  │ Phase B              │  │ Phase C               │
│ 顧客のビジネス状況と  │─▶│ 共通の価値に基づく    │─▶│ 優先順位／数値目標／  │
│ 自社ポジションの理解  │  │ イニシアチブの連携    │  │ 実行アプローチの確認  │
└───────────────────────┘  └──────────────────────┘  └───────────────────────┘
 Corporate Overview          Strategy Map (Step 2)      Prioritization
 SWOT Analysis               Blueprint Map              3 Year Execution Plan
 Strategy Map (Step 1)       Blueprint Summary          Action Plan
 Historical Spend                                       Exec Engagement Plan
 Heatmap                                                Event Plan
 TAM & SOW Analysis                                     Flight Plan
 Influence Map                                          3 Year Projections
 Account Health
 Vision/Strategy for Growth
       │                              │                          │
       └──────────────────────────────┴──────────────────────────┘
                                      │
                        ┌─────────────▼──────────────┐
                        │ Executive Summary          │
                        │ 3 Year Strategy Summary    │
                        │ Management Asks            │
                        │ Challenges & Risk          │
                        └────────────────────────────┘
```

作成主体が Phase ごとに違う。ここを取り違えるとワークショップが資料作成会に
なる。

| Phase | 誰が作るか | いつ |
|---|---|---|
| A | AE / SC が事前に用意 | D-14 〜 D-3 |
| B | アカウントチーム全員でワークショップ形式 | 当日 午前〜午後 |
| C | ワークショップの結論を AE が整形 | 当日午後 〜 D+3 |
| Exec Summary | AE（レビュー前日までに） | D+3 〜 D+7 |

## 3. Step 1 — 準備（D-14 〜 D-7）

### 3.1 対象と体制を確定する

- 対象アカウントと対象範囲（グループ全体か、特定の事業会社／事業部か）。
- 参加者: AE、SC、必要に応じてパートナー担当、経営層（オープニングのみ）。
- 日程: 元資料の標準は **9:00–15:00 の 1 日**（§5.1）。半日に圧縮する場合は
  Phase B のブレストを 90 分確保し、Phase C を後日に回す。
- ゴールの明示: このセッションで何を決めて終わるのか（例: Blueprint テーマの
  優先順位と、次の 90 日のアクション）。

### 3.2 既存資産を棚卸しする

新規作成の前に、既に社内にあるものを探す。元資料も「通常は過去の APS・WPS・
合宿等の資料の中にあるのでそれをベースにする」としている。

- 過去の Account Plan / WPS / 提案書 / 合宿資料
- `accounts/<顧客>/account.json`（活動台帳）と生成済み Markdown
- 直近の議事録・訪問記録・メールスレッド

### 3.3 情報源をそろえる

| 情報源 | 主に効くページ |
|---|---|
| 有価証券報告書、決算説明資料、アニュアルレポート | Corporate Overview, SWOT |
| 中期経営計画 | Strategy Map (Step 1), Corporate Overview |
| 顧客 Web サイト、プレスリリース | Corporate Overview, Strategy Map |
| 新聞・雑誌記事、アナリストコメント | SWOT, Strategy Map |
| 社内の製品担当・SC への照会 | Heatmap, TAM & SOW |
| 訪問記録・議事録・名刺 | Influence Map, Account Health |
| 過去の受注実績 | Historical Spend |

### 3.4 事前配布（D-3）

- Phase A の資料一式を参加者に配布する。
- 当日の進め方、アジェンダ、役割分担を先に決めて共有する。
- 参加者側の宿題: 配布資料を読む／同業種の国内外事例を調べる／これまでの顧客
  訪問の相手と議事録を確認する。

## 4. Step 2 — Phase A: 事前資料を作る

各ページの目的・情報源・つまずきどころ。テンプレート ID は
`references/account-planning-template-plan.md` で定義するもの。

### 4.1 Corporate Overview

対象企業の主要事業、売上・利益の推移、社員数などのプロファイルに加えて、
**経営レベルの課題・今後の戦略・経営層の発言**を記述する。ここで整理した経営
ビジョン／目標／戦略／課題／イニシアチブが Strategy Map の入力になる。

- 判断基準: プロファイル欄が埋まっただけの状態は未完成。経営層の発言が
  1 つも引けていないなら情報収集が足りていない。

### 4.2 SWOT Analysis

内部要因（強み・弱み）と外部要因（機会・脅威）に分けて経営環境を整理する。

- 内部要因の例: 製品力・技術力・開発力、ブランド・顧客基盤・地域展開、経営効率
  （コスト、SCM、スピード）、組織・人材・営業力。
- 外部要因の例: 景気・為替・規制動向、競合と代替手段、市場ニーズの変化、
  技術革新によるビジネスモデルの変化。
- 判断基準: 自社にとっての機会を「顧客にとっての機会」の欄に書かない。

### 4.3 Strategy Map (Step 1 — 顧客分析まで)

顧客の Goal（経営層の要求）／ Strategy（役員の要求）／ Tactic（管理層の要求）
を階層で示し、必要に応じて最上位に経営ビジョン、その下に Objective 層を足す。
重要アカウントでは **イニシアチブまでブレークダウンする**。

- 各項目に「誰の要求か」（Board / CEO / COO / CFO / CIO …）を添える。
- 想定ベース・仮説ベースの項目を含めてよい。ただし §11 のとおり確度を分ける。
- 海外拠点のイニシアチブも対象に含める。
- イニシアチブは、部門最適の改善ではなく Transformation / Innovation を狙う
  大きなものが望ましい。

### 4.4 Historical Spend

過去 3 年の実績を製品別に示す。サブスクリプション／年額課金の数字は一括の
売上と足し合わせず、別に集計する。

### 4.5 Heatmap

レイヤ別・システム別の導入状況（フットプリント）、近い将来の計画、3 年間で
狙う領域をまとめる。現状 → 3 年後ポテンシャルを矢印で対比させ、各行に
**どのイニシアチブに紐づくか**と競合状況を書く。

- 3 値評価: 全社標準 / 足がかりあり・伸長中 / ほぼ未進出。
- 最新状況は社内の製品担当・SC に照会して反映する。

### 4.6 TAM & SOW Analysis

顧客の TAM（自社が取り得る市場規模）と SOW（財布内シェア）のベースラインと
目標をグラフで示す。顧客の IT 予算の開示を受けるなど実 TAM が分かった場合は
その数字で置き換えてよい。ベースラインは 3 年計画の直前 3 年平均、目標は計画
3 年間の平均。

### 4.7 Influence Map

対象イニシアチブの意思決定に関与する Executive を中心に、LOB と IT 部門の
ステークホルダーをマップ化する。

- IT 部門だけでなく事業側を必ず含める。
- 意思決定上の権限・経路・役割、および Inner Circle を明示する。
- 重要アカウントでは海外のステークホルダーも記載する。
- 既存の `b2b-sales/influence-map` / `influence-map-org` をそのまま使える。

### 4.8 Account Health

アカウントの健全性を 4 側面 × 5 指標で評価し、総合スコアを四半期トレンドで
示す。

| 側面 | 指標 |
|---|---|
| Account Team Effectiveness | アカウント戦略 / リード / Exec Sponsor / サポート責任者 / アドバイザー |
| Relationship Quality | Executive Engagement / 顧客満足 / 関係の広さ / パートナー / 顧客プログラム参加 |
| Product Adoption | フットプリント / アーキテクチャ / ロードマップ / ライセンス消化 / Blueprint 数 |
| Revenue Performance | SOW / ライセンス実績 / サービス実績 / パイプライン / 売上 |

- 各指標は 3 段階（要改善 / 標準 / 優良）で、判定基準を別ページに置く。
- 判断基準: 全部が「標準」で並ぶ評価は評価をしていない。

### 4.9 Vision/Strategy for Growth

このアカウントに対する 3 年間の成長ビジョンと戦略を簡潔に示す。顧客の経営上の
優先事項の分析と自社ポジションを踏まえ、関係をどう高めるか、入り込むべき事業
領域、拡張を狙う製品スタックを示す。競合から既存導入を守るアプローチが必要な
場合はそこにも触れる。

元資料の 4 領域構成:

1. 顧客の変革的な事業目標へのアライン（主要イニシアチブの成熟度と経過期間）
2. 自社の GTM 重点領域のポジショニング（狙うべき追加領域）
3. フットプリント拡張（別の事業部門 / 業務プロセス / スタック階層へ）
4. Executive Engagement のポイント（実施済みの役員間会談、次回予定）

## 5. Step 3 — Phase B: ワークショップ

### 5.1 アジェンダ（元資料の例、1 日開催）

| 時刻 | 時間 | 内容 |
|---|---|---|
| 9:00–9:10 | 10 分 | オープニング（役員挨拶、目的とアウトプットの確認） |
| 9:10–9:20 | 10 分 | アカウント責任者からのメッセージ |
| 9:20–10:20 | 60 分 | アカウント状況の確認と現状 Plan の発表 |
| 10:20–10:30 | 10 分 | 休憩 |
| 10:30–12:00 | 90 分 | 顧客の課題・戦略構想・CSF に基づくソリューションとポテンシャルのマッピング（Blueprint テーマ案の洗い出し）。製品領域別のチームに分かれる |
| 12:00–13:00 | 60 分 | 昼食 |
| 13:00–14:00 | 60 分 | ポテンシャルの見極めとテーマ案の優先順位付け |
| 14:00–14:45 | 45 分 | 実行計画の作成 |
| 14:45–15:00 | 15 分 | クロージング |

### 5.2 進め方

- 10:30 の枠は付箋（Post-it）を使ったブレスト形式で行う。清書は後工程。
- 各製品担当は、単体および他製品との組み合わせで提供できる価値を洗い出す。
  価値の型: 競合にはできない価値／実現コストの削減／TCO の削減／実現期間の
  短縮／実現リスクの回避。
- 複数製品領域にまたがり、価値を大きく訴求できるソリューションを優先する。

### 5.3 アウトプット 1: Strategy Map (Step 2 — Blueprint テーマのマッピング)

Phase A で作った Strategy Map の上に、上流アプローチで提案可能と考えられる
テーマをマップする。**Account Planning で最も重要なプロセス。** 顧客の
Innovation / Transformation イニシアチブのうち、自社スタックが価値を出せる
領域を洗い出す。

分析用の Strategy Map をそのまま報告資料に載せると読めないことが多い。報告用
には「顧客イニシアチブ × 提案テーマ × 提供価値 × 製品」を並べた別フォーマット
（Customer Initiative Alignment）に整形し直す。

### 5.4 アウトプット 2: Blueprint Map

マッピングしたテーマを 1 行 1 テーマの表に一覧化する。列は元資料に準拠:

| Blueprint 名 | 顧客課題 | ソリューション案 | 製品 | なぜ自社か（顧客価値・優位性） | 時期 | 金額 |

- 顧客のビジネス課題に対して、自社の価値が解決策として位置づくように書く。
- 「製品名だけ」の行は課題が特定できていないサイン。

### 5.5 アウトプット 3: Blueprint Summary

重要テーマについて 1 テーマ 1 ページで詳細化する。欄は元資料に準拠:
顧客の変革課題／ソリューション概要／製品・重点施策／自社の差別化要因／
ベネフィットとドライバー／関与する社内ロール／パートナー／参照事例／
開始日・クローズ予定日／事業側スポンサー／IT スポンサー／対象事業部／
現行パイプライン金額／3 年ポテンシャル／案件 ID／競合／関連コミュニティ。

- ここでいう Close は**案件の受注ではなく Blueprint（提案テーマ）の合意**を
  指す。混同しない。
- テーマが仮説ベース → 顧客提示 → 共同検討とステージが進むにつれて記述の精度
  を上げる。

## 6. Step 4 — Phase C: 優先順位と実行計画

### 6.1 Prioritization

各イニシアチブを「顧客にとっての価値」と「自社のポジション」で評価し、
マッピングして優先順位を付ける。

- 顧客価値の軸: 戦略適合、経済的ベネフィット、無形のベネフィット。
- 自社ポジションの軸: フットプリントのポテンシャル、顧客との関係、パートナー
  の支援。
- 表側には、イニシアチブごとに 目的・期待価値／意思決定ステージ／キーパーソン
  （スポンサー・影響者・決裁者）／自社のアライン状況と実績／3 年ポテンシャル／
  顧客側の優先度 を並べる。
- 2 軸マップとスコア表は**両方**あると議論が速い（片方だけだと「なぜその位置
  なのか」が説明できない）。

### 6.2 3 Year Execution Plan

テーマ／プロジェクトごとに 3 年間の実行計画を主要マイルストーンで図示する。
マイルストーンの型: イベント、役員招聘、インサイト提供、共同検討、ロードマップ
策定、案件クローズ。重要テーマは 1 ページ 1 テーマで詳細化してよい。

### 6.3 Action Plan

テーマ／プロジェクトごとに、推進のための具体的なアクションを時系列で書く。
列は 割当日 / アクション / 担当 / 期日 / 成果。

**S.M.A.R.T. を満たすこと**: Specific（具体的）、Measurable（定量化できる）、
Attainable（努力で達成できる）、Realistic（達成が合理的）、Time-bound（期限が
ある）。

- 既存の `scalar-ae/action-plan` をそのまま使える。
- 「◯◯を検討する」は成果ではない。誰の何がどう変わるかを書く。

### 6.4 Executive Engagement Plan

顧客役員とのエンゲージメント計画を一覧化する。列は
レベル / 顧客側役員 / 自社側役員 / 頻度・実施日 / 現状とゴール。

- 定例は頻度、単発は予定時期を明示する。
- アカウントに 1 つ作れば足りる（テーマ別に作らなくてよい）。大型案件のみ
  個別に切り出す。

### 6.5 Event Plan

イベント（自社カンファレンス、顧客向けプライベートイベント、役員招聘など）を、
どの役員・キーパーソンに対して、どんな成果を得る場として使うかをまとめる。
列は イベント / 時期 / 対象顧客 / 自社側の登壇者・キーパーソン / 得たい成果。

### 6.6 Flight Plan

3 年間の活動を 1 枚で可視化する。Blueprint Map の各テーマをバブルで表し、
バブル内にテーマ名と金額を書く。横軸にクローズ時期、縦軸に金額、色で
ステータス（テーマ承認済み／案件化済み／新規発生）を示す。

### 6.7 3 Year Financial Potential / Projections

テーマ由来と通常商流由来の売上ポテンシャルを 3 年分設定する。サブスクリプション
の年額換算値は一括売上と足し合わせず、別に合計を示す。

## 7. Step 5 — Executive Summary 化（Session 資料）

Phase A〜C の成果から、30 分レビュー用に **1 桁ページ + Appendix** に落とす。

推奨構成（9 ページ）:

| # | ページ | 出所 |
|---|---|---|
| 1 | 表紙（アカウント名 / 期 / 作成者 / 日付） | — |
| 2 | Three Year Account Strategy Summary | §7.1 |
| 3 | 顧客の経営戦略とイニシアチブ（Strategy Map 報告用） | §5.3 |
| 4 | Initiative Alignment（イニシアチブ × 提案テーマ × 製品） | §5.3 |
| 5 | Blueprint Map（テーマ一覧と金額・時期） | §5.4 |
| 6 | Prioritization（2 軸マップ） | §6.1 |
| 7 | 3 Year Execution Plan / Flight Plan | §6.2 / §6.6 |
| 8 | Action Plan（次の 90 日） | §6.3 |
| 9 | Management Asks | §7.2 |

Appendix に Phase A の分析（Corporate Overview、SWOT、Heatmap、TAM & SOW、
Influence Map、Account Health）と Blueprint Summary を回す。

### 7.1 Three Year Account Strategy Summary

3 年計画全体を 1 枚にまとめる。中央に 3 年戦略のステートメント（1〜2 文）を置き、
左に「現状」、右に「3 年後の目標」を同じ項目立てで並べる。

項目立て: 売上（SOW %、当期実績）／顧客満足（ロイヤルティ指標、総合満足、
推奨意向）／顧客エンゲージメント（役員スポンサーシップ、アクセスできる階層、
共同計画の有無）／フットプリントの強み。上部に主要な変革テーマを並べる。

- **左右で項目が対応していないと比較にならない。** 現状に書いた項目は必ず
  3 年後にも同じ順で書く。

### 7.2 Management Asks

3 年計画を進めるうえで、担当チームだけでは解決が困難で、経営層の支援が必要な
事項を書く。社内・社外の両方を対象にする。

- 誰から、どんな支援が必要か
- なぜ必要か
- それによって期待される具体的な結果・成果

「リソースが欲しい」だけでは Ask にならない。期待成果まで書いて初めて判断できる。

### 7.3 Account Challenges & Risk Mitigation

列は 課題の内容 / 影響 / 緩和策 / 担当。Management Asks と対になる。Ask に
つながらないリスクは、誰がいつまでに何をするのかを緩和策の欄に書く。

## 8. Step 6 — slide-forge での生成

`scripts/scalar/build_account_planning.py` が台帳から 2 本のデッキ仕様を出す。
Plan Document（34 ページ）と APS レビュー用（9 ページ + Appendix）は同じページ
定義を共有するので、**1 つ直せば両方に反映される**。

**入力は `accounts/<AE>/<顧客>/aps.json`。** スクリプトは図の種類・座標・書式
（`LAYOUT`）だけを持ち、文字列はすべて aps.json から読む。顧客名も実名も
スクリプトに書かない。

`aps.json` の構造:

```jsonc
{
  "meta":     { "title": …, "subtitle": …, "planTitle": …, "reviewTitle": … },
  "sections": { "A": {"title":…, "body":…}, "B": …, "C": …, "E": …, "APX": … },
  "deals":    [ { "id":"1", "company":…, "name":…, "challenge":…, "solution":…,
                  "diff":…, "people":…, "jri":…, "deal":…,
                  "amount":…, "period":…, "stage":… } ],
  "pages":    { "<ページ id>": { "title":…, "lead":…, "source":…,
                                 "figures": [ {内容だけ}, … ] } }
}
```

`pages.<id>.figures` は `LAYOUT[<id>]` の図の並びと 1 対 1 で対応する
（`governing_message` / `lead_in` / `source_note` は `title` / `lead` / `source`
から取るので figures には並べない）。数が合わなければ組み立て時にエラーになる。

```bash
# 1. aps.json から 2 本の仕様を組む
.venv/bin/python scripts/scalar/build_account_planning.py \
  --aps "accounts/<AE>/<顧客>/aps.json" \
  --out "out/account-plan/<顧客>/ap"
#    -> plan.json / review.json

# 2. オフライン検証（API を叩く前に必ず通す）
for f in plan review; do
  .venv/bin/python scripts/build_deck.py --template templates/scalar-2026.json \
    --spec "out/account-plan/<顧客>/ap/$f.json" --dry-run --strict || break
done

# 3. 生成（初回）。既存デッキの更新は 4 へ
.venv/bin/python scripts/build_deck.py \
  --template templates/scalar-2026.json --spec "out/account-plan/<顧客>/ap/plan.json" \
  --title "<顧客> Account Planning Session FY26" --folder <Drive フォルダ ID>

# 4. 既存デッキを同じ URL で更新する（スナップショットが先）
.venv/bin/python scripts/snapshot_version.py <デッキ URL>
.venv/bin/python scripts/build_deck.py \
  --template templates/scalar-2026.json --spec "out/account-plan/<顧客>/ap/plan.json" \
  --into <デッキ URL>

# 5. サムネイルでのビジュアル QA → 修正 → 再生成（skills/slide-qa/SKILL.md）
# 6. QA 用ファイルの後始末
.venv/bin/python scripts/cleanup_qa.py
```

マスターを差し替える場合は **`--template` を変えるだけ**（`corporate`、
`aixdevops`、`blank-16x9` など）。ページ定義側は変更しない。この成立条件は
`references/account-planning-template-plan.md` §2 に定義する。

> **`--dry-run` が通っても API に弾かれる制約が 1 つある。** Slides API は幅
> 32pt（0.444in）未満の表列を拒否する。`build_account_planning.py` の
> `_check_columns()` が組み立て時に検査している。商談番号のような細い列を足す
> ときは 0.45in 以上を確保すること。

> 既存デッキを更新する場合は、`--into` で既存デッキを指定する前に必ず
> `scripts/snapshot_version.py` でスナップショットを取る。テンプレート原本を
> `--into` の対象にしない。

## 9. ページ一覧（マスター表）

Plan Document の 35 ページ。「レビュー」列の ○ が APS レビュー用 9 ページ、
それ以外は Appendix に回る。「#」は顧客イニシアチブ番号（§9.1）。

**表は「登録簿」と「判定基準」だけに残し、それ以外は図で表す**（§9.4）。
商談ごとの章（§9.2.1）は下表に含まない。

| # | ページ | 形 | Phase | レビュー | 元資料 |
|---|---|---|---|---|---|
| 1 | グループ体制と当社の接点 | orgchart | A | Appendix | S80 |
| 2a | 事業会社の組織と当社の接点（法人ごとに 1 枚） | orgchart | A | Appendix | S84 |
| 2b | システム子会社の組織と当社の接点 | orgchart | A | Appendix | S84 |
| 3 | Financial Trends | metric + hbars | A | Appendix | S81 |
| 4 | SWOT Analysis | matrix | A | Appendix | S13 |
| 5 | Strategy Map (Step 1) | outcome_tree | A | — | S15 |
| 6 | Strategy Map (Step 2) | outcome_tree | A/B | ○ | S38 / S41 |
| 6b | 法人別の役員層と接触状況 | comparison | A | Appendix | S27 |
| 6c | 会うべき人と手がかり | 表 | A | Appendix | S27 |
| 7 | Customer Business Initiatives | cards | A | ○ | S44 |
| 8 | Customer Programs / Projects | gantt | A | Appendix | S45 |
| 9 | Historical Spend | hbars | A | — | S18 |
| 10 | Scalar Footprint | layers + cards | A | Appendix | S84 |
| 11 | Heatmap | layers | A | Appendix | S23 / S26 |
| 12 | TAM & SOW Analysis | nested_circles | A | — | S21 / S22 |
| 13 | Influence Map | influence_graph | A | Appendix | S27 |
| 13b | 主要人物の経歴 | cards | A | Appendix | S27 |
| 13c | 人物の関係性 | influence_graph + links | A | Appendix | S27 |
| 14 | Account Health | rating_matrix | A | Appendix | S29 |
| 15 | Account Health 評価基準 | **表** | A | — | S31 / S32 |
| 16 | Vision / Strategy for Growth | comparison | A | — | S33 |
| 17 | Initiative Alignment | mece_tree | B | — | S43 / S46 |
| 18 | Blueprint Map | **表** | B | ○ | S49 |
| 19 | Blueprint Summary（テーマごと） | cards ×2 段 | B | — | S51 |
| 20 | Objective（テーマごと） | cards + journey | B | Appendix | S60 / S99 |
| 21 | Prioritization（スコア） | **表** | C | — | S55 |
| 22 | Prioritization（2 軸） | posmap | C | ○ | S56 |
| 23 | 3 Year Execution Plan | gantt | C | ○ | S57 |
| 24 | Engagement Timeline（8 週） | gantt | C | — | S59 / S98 |
| 25 | Action Plan | **表** | C | ○ | S61 / S62 |
| 26 | Executive Engagement Plan | orgchart | C | — | S63 |
| 27 | Event Plan | timeline | C | — | S65 |
| 28 | Flight Plan | posmap | C | — | S70 |
| 29 | 3 Year Projections | **表** | C | — | S67 |
| 30 | 3 Year Account Strategy Summary | exec_summary + before_after | Exec | ○ | S73 |
| 31 | Management Asks | **表** | Exec | ○ | S75 |
| 32 | Challenge & Requirement | **表** | Exec | ○ | S77 / S105 |
| 33 | Challenges & Risk Mitigation | **表** | Exec | Appendix | S86 |

### 9.1 商談番号による相互参照

商談に番号を振り、Heatmap・Customer Business Initiatives・Blueprint Map・
Prioritization・Action Plan で**同じ番号を参照**する。番号がないと、各ページが
独立した表になって束として追えなくなる。

**番号はグループ会社順に振る。** 同じ会社の商談が隣り合うので、会社単位の
話をするときにページをまたいで拾い直さなくて済む。

番号・会社・担当組織・金額は `build_account_planning.py` の `DEALS` で
一元管理し、全ページと商談ごとの章がそこから引く。

### 9.2 グループ会社ごとの分類

親会社 1 社ではなく企業グループを相手にする場合、**商談も関与者も会社ごとに
分類する。** 会社が違えば意思決定者も予算も別なので、まとめると打ち手が決まらない。

必要な 3 ページ:

| ページ | 図 | 何を示すか |
|---|---|---|
| グループ会社別の商談ポートフォリオ | `mece_tree` | どの会社に何件・いくらの商談があるか |
| グループ会社別の関与者 | `comparison` | 会社ごとに誰を押さえ、誰が名刺どまりか |
| システム子会社 ↔ 各社の担当マッピング | `comparison` | 横断組織と会社別実装部隊の区別 |

**システム子会社は全社に関係するので、必ず別立てで扱う。** 金融グループの
金融グループの IT 子会社は、会社ごとに担当本部が分かれる一方、技術統括や
AI 推進のような横断組織を持つ。横断組織を押さえていても会社別の実装部隊に
入れていなければ案件は動かない。**この区別が見えるように、公式組織図を
会社別に読み替えたページを置く。**

### 9.2.2 会うべき人を探す

アカウントプランは会った人の記録ではなく、**次に誰に会うべきかを出す仕組み**
でもある。台帳だけを見ていると既に会えている人の周りしか出てこない。

**役員名簿は法人単位で取る。** グループは持株会社・事業会社・IT 子会社が
それぞれ別法人として役員を公開している。まとめてしまうと、実装を持つ役員が
どの法人にいるのか分からなくなる。

0. **法人ごとに組織図を 1 枚ずつ描く。** グループ全体を 1 枚にまとめると
   部レベルが潰れ、どの部署に入れていないかが見えない
1. 法人ごとに公開の役員名簿を取り、当社の接触状況を重ねる
2. **兼務を拾う。** 持株会社の CxO が子会社の取締役を兼ねていることがあり、
   それが最短の紹介経路になる
3. 組織図（どの部署があるか）と役員名簿（誰が役員か）を突き合わせる。
   **部署と役員の紐付けは公開情報では埋まらないことが多く、そこが確認事項**
4. **手がかりは接触済みの人を起点にする。** 誰経由かが書けない「会うべき人」は
   アクションにならない
5. 役職は公開名簿を正とし、台帳の古い肩書きは直す
6. **会う相手が決まったら経歴を押さえる。** 肩書きの変遷は、その人が何を根拠に
   判断するかを示す。前任・後任・兼務・出向元は意思決定の経路そのもの
7. **個人的な関係（元上司・友人・派閥）は公開情報ではない。** 出典行で分け、
   その記述が入った資料は社外に出さない

### 9.2.1 商談ごとの章立て

商談の詳細は、全体の分析に混ぜず**商談ごとに章を切る**。各章は:

1. 中扉（会社名／商談名／金額・時期・ステージ）
2. 商談の全体像（`cards` 6 枚: 顧客の課題 / 当社の解 / 差別化要因 /
   顧客側キーパーソン / **システム子会社の担当組織** / 金額・時期・ステージ）
3. Objective（主要商談のみ。`cards` + `journey`）

章の中身は商談ごとに同じ型にする。型が同じなら、章をまたいで「どこが埋まって
いないか」を比べられる。

### 9.4 表を使ってよい場所

表が続くとページの見た目が同じになり、どこが要点か分からなくなる。表は
次の 2 つに限り、それ以外は図にする。

- **登録簿**: 行ごとに担当と期日があり、後から追跡するもの（Blueprint Map /
  Action Plan / Management Asks / Challenge & Requirement / Risk / Prioritization
  スコア / Projections）
- **判定基準**: 段階の定義そのものが内容であるもの（Account Health 評価基準）

置き換えの目安:

| 表にしがちなもの | 使う図 |
|---|---|
| 階層・所属・レポートライン | `orgchart` |
| 上位目標と下位施策のつながり | `outcome_tree` / `mece_tree` |
| レイヤごとの状態 | `layers` |
| 時期のあるプロジェクト群 | `gantt` / `timeline` |
| 大小の入れ子（市場規模） | `nested_circles` |
| 金額・件数の比較 | `hbars` / `vbars` |
| 数項目の並列説明 | `cards` |
| 年度ごとの到達点 | `journey` |
| 現在と目標の対比 | `before_after` |
| 関与者の立場と影響力 | `influence_graph` / `posmap` |

### 9.5 顧客側の 4 層

イニシアチブとテーマの間に**顧客のプログラム / プロジェクト層**を必ず置く。
ここを飛ばすと、実在するプロジェクト名と提案テーマが対応しなくなる。

```
顧客イニシアチブ（§9.1 の番号）
  └ 顧客プログラム / プロジェクト（実在する名前で書く）
      └ 提案テーマ（Blueprint）
          └ 案件
```

## 10. 更新運用

- Session の直後に、決まったことを `accounts/<顧客>/account.json` に反映する。
  スライドを正とせず、台帳を正とする。
- Action Plan は次の 90 日分を常に埋まった状態に保つ。期日を過ぎた行は、完了・
  未完了・中止のいずれかに決着させてから消す。
- Blueprint のステージが進んだら Blueprint Summary の記述精度を上げる。
- デッキの URL は変えない。同じリンクが常に最新を指す状態を保つ。

## 11. 品質チェックリスト

Session 資料を出す前に。

- [ ] 1 ページ 1 メッセージになっているか。タイトルが結論になっているか。
- [ ] 顧客の発言・文書に基づく事実と、こちらの仮説が見分けられるか。仮説は
      仮説と明示しているか。
- [ ] Strategy Map のイニシアチブは、顧客の公開情報または顧客の発言に紐づくか。
- [ ] Blueprint Map の各行に、顧客課題が特定できているか（製品名だけの行がないか）。
- [ ] Prioritization の位置づけに根拠（スコア表）が対応しているか。
- [ ] Action Plan の各行が S.M.A.R.T. を満たすか。担当と期日が空欄でないか。
- [ ] Management Asks に期待成果が書かれているか。
- [ ] Strategy Summary の「現状」と「3 年後」が同じ項目立てで対応しているか。
- [ ] 金額の単位・期間・為替前提が明示されているか。
- [ ] 社内限定情報（個人の影響力評価、社内政治、賛否）が顧客共有版に混ざって
      いないか。
- [ ] サムネイルでのビジュアル QA を通したか（文字あふれ、重なり、コントラスト）。

## 12. 元資料からの読み替え表

| 元資料（Oracle） | この手順書での扱い |
|---|---|
| KAD（Key Account Director） | アカウント責任者 / AE |
| GCA / EA | SC / ソリューションアーキテクト |
| APS（Account Planning Session） | そのまま。役員レビューを伴う計画セッション |
| APWS（Account Planning Workshop） | §5 のワークショップ |
| Blueprint | 上流提案テーマ。案件の前段にある仮説 |
| Blueprint の Close | テーマの合意成立（受注ではない） |
| Pillar（Tech / Apps など） | 製品領域 |
| Sales Play | 重点施策 |
| CVC（Customer Visit Center） | 本社招聘・役員訪問 |
| OOW / Insight | 自社カンファレンス / インサイト提供活動 |
| ULA / ELA Utilization | ライセンス契約の消化状況 |
| SOW（Share of Wallet） | 顧客 IT 支出内の自社シェア |
| ARR booking | 年額換算の新規契約額 |
| InfoMentis / Oracle Sales Methodology | `references/scalar/sales-playbook.md` |
