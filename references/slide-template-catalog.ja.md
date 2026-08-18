*[English](slide-template-catalog.md)*

# スライドテンプレート カタログ（全 55 種）

`slide-templates/` に登録されたテンプレートを実際に 1 枚ずつ生成して
書き出した画像カタログ。**どのテンプレートで 1 枚を作るかを見て選ぶ**ためのもの。
スキーマの書き方は [template-schema.md](template-schema.ja.md)、
汎用ページパターン（骨格・図表の組み方）は
[slide-pattern-catalog.md](slide-pattern-catalog.ja.md) にある。

各テンプレートの **figures** 行は、そのページが使っている描画部品の `type` 名。
テンプレートは `render_slide_template.py` かデッキ仕様の `$template` で使う。

```bash
# このカタログを作り直す（テンプレートを追加したときも同じ手順）
for pack in marketing-analysis b2b-sales scalar-ae planning analysis \
            read-alone business-plan; do
  .venv/bin/python scripts/build_slide_template_catalog.py \
      --pack $pack --out out/template-catalog/$pack.json
done
# 7 つの spec の slides を 1 つに結合して build_deck.py で生成し、
# fetch_thumbnails.py の PNG を references/images/slide-templates/<id>.png に配置
.venv/bin/python scripts/build_template_catalog_doc.py
```

| パック | 数 | 何を作るための章か |
|---|---|---|
| [マーケティング分析パック](#marketing-analysis) | 8 種 | 市場・顧客・施策効果を分析するページ群 |
| [B2B セールスパック](#b2b-sales) | 8 種 | 商談のステークホルダー構造とディスカバリー（課題探索）を可視化するページ群 |
| [Scalar AE パック](#scalar-ae) | 10 種 | Scalar のアカウントエグゼクティブが商談レビュー・活動計画で使う定型ページ群 |
| [計画パック](#planning) | 3 種 | 時間軸を持つ計画を示すページ群 |
| [現状分析パック](#analysis) | 10 種 | コンサルティングの現状分析・課題特定フレームワークをページ化した群 |
| [読み物パック](#read-alone) | 8 種 | 1 枚で読み切れる高密度スライド（外資コンサル型の配布資料）のページ群 |
| [事業計画パック](#business-plan) | 8 種 | 事業計画・稟議で承認者が最初に見る「収益・投資・リスク・体制」のページ群 |

<a id="marketing-analysis"></a>

## マーケティング分析パック（`marketing-analysis`）

市場・顧客・施策効果を分析するページ群。戦略（SWOT / 3C / TAM-SAM-SOM / ポジショニング）から顧客理解（RFM / コホート）、行動（ファネル）、効果検証（A/B テスト）までを 1 枚ずつのフォーマットにしている。

### SWOT分析（`swot-analysis`）

![SWOT分析](images/slide-templates/swot-analysis.png)

内部・外部環境を正負の4象限で整理し、優先アクションを示す

**答える問い**: 自社の戦略上の強み・弱み・機会・脅威は何か

**figures**: `governing_message`, `matrix`, `so_what`, `source_note`  
**推論レベル**: 戦略（評価と方向づけ）  
**status**: experimental

使うときの決まり:

- 事実と解釈を区別する
- SWOTの語句だけで因果関係を主張しない

### 3C分析（`three-c-analysis`）

![3C分析](images/slide-templates/three-c-analysis.png)

Customer・Competitor・Companyの重なりから戦略の焦点を示す

**答える問い**: 顧客価値と競争優位が重なる戦略領域はどこか

**figures**: `governing_message`, `venn`, `table`, `source_note`  
**推論レベル**: 戦略（評価と方向づけ）  
**status**: experimental

### TAM / SAM / SOM（`market-sizing`）

![TAM / SAM / SOM](images/slide-templates/market-sizing.png)

市場全体から獲得可能市場までを入れ子で示す

**答える問い**: 市場規模と現実的な獲得可能範囲はどの程度か

**figures**: `governing_message`, `nested_circles`, `so_what`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**status**: experimental

### ポジショニングマップ（`positioning-map`）

![ポジショニングマップ](images/slide-templates/positioning-map.png)

2軸上で自社と競合の位置関係を示す

**答える問い**: 自社は競合と異なる価値を提供できているか

**figures**: `governing_message`, `posmap`, `so_what`, `source_note`  
**推論レベル**: 診断（要因・構造の特定）  
**status**: experimental

### RFMセグメント（`rfm-segments`）

![RFMセグメント](images/slide-templates/rfm-segments.png)

購買の最新性・頻度・金額から顧客群と施策を比較する

**答える問い**: 優良・育成・休眠顧客は誰で、どの施策を行うか

**figures**: `governing_message`, `table`, `so_what`, `source_note`  
**推論レベル**: 診断（要因・構造の特定）  
**status**: experimental

### コホート継続率（`cohort-retention`）

![コホート継続率](images/slide-templates/cohort-retention.png)

獲得時期別の継続率を期間ごとに比較する

**答える問い**: 新しく獲得した顧客の継続率は改善しているか

**figures**: `governing_message`, `table`, `so_what`, `source_note`  
**推論レベル**: 診断（要因・構造の特定）  
**status**: experimental

使うときの決まり:

- 観測期間の異なる右下セルを単純比較しない
- 母数の小さいコホートを注記する

### コンバージョンファネル（`conversion-funnel`）

![コンバージョンファネル](images/slide-templates/conversion-funnel.png)

購買プロセスの段階別件数と最大の離脱点を示す

**答える問い**: どの段階の離脱を優先して改善すべきか

**figures**: `governing_message`, `funnel`, `so_what`, `source_note`  
**推論レベル**: 診断（要因・構造の特定）  
**status**: experimental

### A/Bテスト結果（`experiment-result`）

![A/Bテスト結果](images/slide-templates/experiment-result.png)

対照群と施策群の結果、母数、差、判定を1枚で示す

**答える問い**: 施策によって主要KPIはどの程度変化したか

**figures**: `governing_message`, `vbars_grouped`, `table`, `so_what`, `source_note`  
**推論レベル**: 因果（原因の主張）  
**status**: experimental

使うときの決まり:

- 有意差がない結果を効果ゼロと断定しない
- 事前に定めた主要KPIと分析期間を明記する

<a id="b2b-sales"></a>

## B2B セールスパック（`b2b-sales`）

商談のステークホルダー構造とディスカバリー（課題探索）を可視化するページ群。誰が意思決定に効くのか・何がまだ聞けていないのかを 1 枚で共有する。

### インフルーエンスマップ（`influence-map`）

![インフルーエンスマップ](images/slide-templates/influence-map.png)

購買関与者を影響力と賛否の2軸に配置し、誰を動かせば決まるかを示す

**答える問い**: この商談は誰を動かせば決まるか / 反対側に影響力が偏っていないか

**figures**: `governing_message`, `posmap`, `so_what`, `source_note`  
**推論レベル**: 診断（要因・構造の特定）  
**status**: experimental

使うときの決まり:

- 位置は面談で確かめた発言に基づくこと。営業の期待を賛否として置かない
- 未接触の関与者を「中立」に置かない。分からないことは discovery-gaps 側に出す
- 影響力は役職ではなく、過去の決裁で実際に効いたかで置く
- バブルのラベルは 6 字まで。役職や氏名の詳細は buying-committee 側に置く
- バブルは直径 0.95in。近すぎるとラベルが隠れる（--dry-run の図版監査が "Text is hidden behind a shape drawn later" で止める）。同じ位置に見える関与者はまとめるか buying-committee 側で分ける

### 購買関与者一覧（`buying-committee`）

![購買関与者一覧](images/slide-templates/buying-committee.png)

購買に関わる人物の役割・影響力・スタンス・接触状況を一覧で押さえる

**答える問い**: 購買に誰が関わり、こちらはどこまで会えているか

**figures**: `governing_message`, `table`, `so_what`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**status**: experimental

使うときの決まり:

- 購買役割は肩書ではなく、この案件で果たす機能で書く（決裁・推進・評価・利用・門番・反対）
- 接触状況は面談実績で書く。名刺交換だけを「接触済」としない

### 決裁ライン（`decision-structure`）

![決裁ライン](images/slide-templates/decision-structure.png)

稟議がどの経路をたどり、どこで止まりうるかを木で示す

**答える問い**: 承認はどの順で上がり、どこで止まるか

**figures**: `governing_message`, `orgchart`, `so_what`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**status**: experimental

使うときの決まり:

- 組織図ではなく、この案件の決裁経路を書く。関与しない部署は載せない
- 金額により経路が変わる場合は、想定金額での経路であることを出典行に書く
- 深さ 4 以上・葉 8 超は文字が潰れる。部門ごとに分けること

### ディスカバリーマップ（`discovery-map`）

![ディスカバリーマップ](images/slide-templates/discovery-map.png)

商談で押さえるべき項目を並べ、確認済み・仮説・未確認を色で見分ける

**答える問い**: この商談で何が分かっていて、何がまだ仮説か

**figures**: `governing_message`, `ghost`, `so_what`, `source_note`  
**推論レベル**: 診断（要因・構造の特定）  
**status**: experimental

使うときの決まり:

- 状態は confirmed（顧客の発言・文書で確認）/ wip（一部のみ）/ missing（未確認）の 3 値
- 営業の推測は confirmed にしない。裏取りの出所を言えないものは wip 以下
- 赤（missing）が残ったまま提案書の作成に進まない

### ペインチェーン（`pain-chain`）

![ペインチェーン](images/slide-templates/pain-chain.png)

現場の困りごとが部門と経営の指標にどう連鎖するかを辿る

**答える問い**: 現場の課題は経営のどの数字に効いているか

**figures**: `governing_message`, `lead_in`, `flow`, `table`, `source_note`  
**推論レベル**: 因果（原因の主張）  
**status**: experimental

使うときの決まり:

- 連鎖は因果の主張。各段に裏付けを置けないなら矢印でつながない
- 経営指標への影響は顧客自身の数字で語る。こちらの試算なら試算と明記する
- 相関を因果として提示しない

### 未確認事項と次の一手（`discovery-gaps`）

![未確認事項と次の一手](images/slide-templates/discovery-gaps.png)

空白のまま残っている論点を、誰にいつ確認するかまで落とす

**答える問い**: 次に誰へ何を確認すれば商談が前に進むか

**figures**: `governing_message`, `lead_in`, `table`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**status**: experimental

使うときの決まり:

- 「なぜ重要か」を書けない項目は聞かない。質問の量ではなく順序で決まる
- 確認相手と期限のない行を残さない
- discovery-map の missing / wip と対応させること

### インフルーエンスマップ（組織構造）（`influence-map-org`）

![インフルーエンスマップ（組織構造）](images/slide-templates/influence-map-org.png)

購買関与者を組織のつながりで並べ、役割・影響度・立場・面談状況を示す

**答える問い**: 誰が誰の下にいて、どこに影響力と支持が集まっているか

**figures**: `governing_message`, `influence_graph`, `so_what`, `source_note`  
**推論レベル**: 診断（要因・構造の特定）  
**status**: experimental

使うときの決まり:

- people / links の中身は scripts/account_graph.py が検証する。id の重複・宙に浮いた reportsTo・循環はそちらで止まるので、必ず account_graph.load() を通したデータを渡す
- 9 名を超えるなら account_graph.extract() で間引き、more に「他 N 名は draw.io 版参照」を書く。全員を 1 枚に詰めない
- 未面談の関与者は met: false のまま載せる（破線で描かれる）。会えていないことも情報
- 立場は面談での発言に基づくこと。営業の期待を stance に書かない

### ディスカバリーマップ（階層）（`discovery-map-tree`）

![ディスカバリーマップ（階層）](images/slide-templates/discovery-map-tree.png)

Goal・Strategy・Tactics を支持関係でつなぎ、何が何を支えるかを示す

**答える問い**: 顧客の目標は何に支えられていて、自社はどこに効くのか

**figures**: `governing_message`, `outcome_tree`, `so_what`, `source_note`  
**推論レベル**: 戦略（評価と方向づけ）  
**status**: experimental

使うときの決まり:

- nodes / edges の中身は scripts/account_graph.py が検証する。循環や下向きの辺はそちらで止まるので、必ず account_graph.load() を通したデータを渡す
- 段は tier ではなくグラフの深さで決まる。上位目標を支える下位目標は 1 段下に置かれる
- 9 ノードを超えるなら account_graph.extract() で間引き、more に「他 N 項目は draw.io 版参照」を書く
- 顧客が言っていない目標を Goal に置かない。推測はディスカバリーマップ側の wip として扱う

<a id="scalar-ae"></a>

## Scalar AE パック（`scalar-ae`）

Scalar のアカウントエグゼクティブが商談レビュー・活動計画で使う定型ページ群。account.json（商談台帳）の内容をそのまま流し込める前提で設計されている。唯一の stable パック。

### 商談スナップショット（`account-snapshot`）

![商談スナップショット](images/slide-templates/account-snapshot.png)

この商談が今どのステージにいて、いくらで、いつ決まるかを 1 枚で示す

**答える問い**: この商談は今どこにいて、いくらで、いつ決まるか

**figures**: `governing_message`, `cards`, `table`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**status**: stable

使うときの決まり:

- forecast は Pipeline / Best / Commit / Closed の 4 値。根拠を書けない Commit は Best に落とす
- 金額は算定根拠を言えるものだけ書く。言えなければ「未確定」と書く
- 社内資料。顧客・パートナーには渡さない（個人の影響力・賛否・社内政治を含む）

### ステージ移行条件（`phase-gate`）

![ステージ移行条件](images/slide-templates/phase-gate.png)

現ステージの移行条件を並べ、顧客側の証拠が取れているかで判定する

**答える問い**: 今のステージの完了条件を示す顧客側の証拠は何か

**figures**: `governing_message`, `lead_in`, `table`, `source_note`  
**推論レベル**: 診断（要因・構造の特定）  
**status**: stable

使うときの決まり:

- 状態は met / partial / unmet の 3 値。「説明した」「提案書を出した」は met の根拠にならない
- 証拠は顧客側のもの（発言・文書・稟議記録）に限る。社内の合意は証拠ではない
- 移行条件は references/scalar/sales-playbook.md §2 のゲート ID に対応させる
- 社内資料。顧客・パートナーには渡さない（個人の影響力・賛否・社内政治を含む）

### BANT リスク（`bant-risk`）

![BANT リスク](images/slide-templates/bant-risk.png)

Budget / Authority / Needs / Timeframe のどれが商談を止めるかを見分ける

**答える問い**: この商談のどこにリスクがあり、フォーキャストは妥当か

**figures**: `governing_message`, `cards`, `so_what`, `source_note`  
**推論レベル**: 診断（要因・構造の特定）  
**status**: stable

使うときの決まり:

- 4 項目の順序は Budget → Authority → Needs → Timeframe で固定する
- 各項目の書き出しは ok / risk / unknown のいずれか。判断の根拠を同じセルに書く
- unknown が残る項目は action-plan に確認相手と期限つきで送る
- 社内資料。顧客・パートナーには渡さない（個人の影響力・賛否・社内政治を含む）

### アクションプラン（`action-plan`）

![アクションプラン](images/slide-templates/action-plan.png)

未確認の論点を、誰が・誰に・いつまでに・何が取れたら完了かまで落とす

**答える問い**: この商談を前に進めるために、誰が何をいつまでにやるか

**figures**: `governing_message`, `lead_in`, `table`, `source_note`  
**推論レベル**: 戦略（評価と方向づけ）  
**status**: stable

使うときの決まり:

- 完了条件を書けない行は載せない。「確認する」は完了条件ではない
- 期限のない行を残さない。相手が社内なら会議体名（WPS / Deal Desk）を書く
- discovery-gaps の未確認事項と 1 対 1 で対応させる
- 社内資料。顧客・パートナーには渡さない（個人の影響力・賛否・社内政治を含む）

### 活動履歴（`activity-timeline`）

![活動履歴](images/slide-templates/activity-timeline.png)

これまで誰に会い、何を得たかを時系列で並べる

**答える問い**: この顧客とどこまで会えていて、何が取れたか

**figures**: `governing_message`, `timeline`, `table`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**status**: stable

使うときの決まり:

- 表は直近 4 件まで。それ以前は台帳（account.json）に残し、スライドには出さない
- 「得たこと」には顧客の発言か文書だけを書く。こちらの手応えは書かない
- 会えていない期間の空白も見えるように、日付を省略しない
- 社内資料。顧客・パートナーには渡さない（個人の影響力・賛否・社内政治を含む）

### 訪問計画（`visit-plan`）

![訪問計画](images/slide-templates/visit-plan.png)

訪問 1 回で何を得るか、どう聞くか、どう返すかを決めてから行く

**答える問い**: この訪問で顧客から何を得るか、想定反論にどう返すか

**figures**: `governing_message`, `lead_in`, `storyline`, `so_what`, `cards`, `source_note`  
**推論レベル**: 戦略（評価と方向づけ）  
**status**: stable

使うときの決まり:

- タイトルは「顧客から得たい一言」にする。「〇〇を説明する」は目的ではない
- ask には次に紹介してほしい人物・部門と、その理由を必ず書く
- 問いは答えが Yes/No で終わらないものにする（SPIN の I と N を含める）
- 社内資料。顧客・パートナーには渡さない（個人の影響力・賛否・社内政治を含む）

### 勝ち筋（WPS）（`win-plan`）

![勝ち筋（WPS）](images/slide-templates/win-plan.png)

WPS でステージ移行と提案投資を判断するための、勝ち筋とリスクの 1 枚

**答える問い**: なぜこの商談に勝てるのか、最大のリスクをどう潰すか

**figures**: `governing_message`, `exec_summary`, `table`, `source_note`  
**推論レベル**: 戦略（評価と方向づけ）  
**status**: stable

使うときの決まり:

- resolution には「顧客がなぜ当社を選ぶ理由になるのか」を書く。製品名の列挙にしない
- リスクは自社でコントロールできる次の行動とセットにする。行動が書けないものは Best 以下
- 継続 / 保留 / 撤退の判断依頼を口頭で必ず添える
- 社内資料。顧客・パートナーには渡さない（個人の影響力・賛否・社内政治を含む）

### 課題仮説ワンページャー（`challenge-hypothesis`）

![課題仮説ワンページャー](images/slide-templates/challenge-hypothesis.png)

顧客がまだ言語化していない論点を示し、対話を始めるための 1 枚

**答える問い**: 顧客がまだ気づいていない課題は何か、放置すると何が起きるか

**figures**: `governing_message`, `lead_in`, `cards`, `so_what`, `source_note`  
**推論レベル**: 診断（要因・構造の特定）  
**status**: stable

使うときの決まり:

- **顧客提示用**。個人の影響力・賛否・社内政治・競合の弱点を書かない
- 3 枚のカードは 地ならし → 再構成 → 裏付け（放置コスト）の順に固定する
- 断定しない。仮説は仮説と分かる言い方にし、最後は必ず顧客への問いで終える
- 出典のない数値を載せない。公開事例は出典を明記する

### ライセンス見積もりサマリー（`license-estimate`）

![ライセンス見積もりサマリー](images/slide-templates/license-estimate.png)

Scalar ライセンス見積もりの明細・定価→値引→御提供金額・前提条件を 1 枚に集約した提案書の費用ページ

**答える問い**: この構成でいくらかかり、金額の内訳と前提は何か

**figures**: `governing_message`, `lead_in`, `table`, `metric`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**densities**: print / presentation（既定 print）  
**status**: experimental

使うときの決まり:

- 単価・金額は price-master の見積書から転記する。このスライド上で手計算しない
- 割引率は載せない。見せるのは定価合計・値引額・御提供金額のみ
- 契約期間（月額 / 年額 / 3年）を集計表に必ず載せる。金額だけ書いて期間を省かない
- Pod 数は見積書・構成図と一致させる。契約 Pod ルール（年額契約＝同時稼働の最大 Pod 数）を前提に明記する

### ライセンスパターン比較（`license-pattern-compare`）

![ライセンスパターン比較](images/slide-templates/license-pattern-compare.png)

複数の見積もりパターン（Standard / Premium、構成違いなど）を構成・Pod 数・御提供金額で横並び比較し、推奨案を明示する

**答える問い**: どのライセンスパターンがこの顧客に最適で、金額はいくら違うのか

**figures**: `governing_message`, `lead_in`, `table`, `so_what`, `source_note`  
**推論レベル**: 診断（要因・構造の特定）  
**densities**: print / presentation（既定 print）  
**status**: experimental

使うときの決まり:

- 金額は price-master の見積書（比較サマリ）から転記する。割引率は載せず御提供金額で比較する
- パターン間で行の観点（構成・Pod 数・期間・金額）を揃え、行ごとに読み比べられるようにする
- 推奨は機能要件と金額の両面から書く。安い案を無条件に推さない

<a id="planning"></a>

## 計画パック（`planning`）

時間軸を持つ計画を示すページ群。線表（ガント）・年表・マイルストーンの 3 形式で、粒度と用途が異なる。

### ガントチャート（線表）（`gantt-schedule`）

![ガントチャート（線表）](images/slide-templates/gantt-schedule.png)

期間 × 作業の線表で、並行して走る作業と節目（マイルストーン）を示す

**答える問い**: いつ・何が並行して走り、次の節目はいつか

**figures**: `governing_message`, `gantt`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**status**: experimental

使うときの決まり:

- 開始・終了は列単位の小数（0 が最初の列の左端、列数が右端）。列数を超える値は生成時にエラーになる
- 開始 == 終了 の行はマイルストーン（◆）として描かれる。バーにしたい行は幅を持たせる
- 依存関係の矢印は表現しない。前後関係を細かく見せたい計画は table で書く
- 行は 8 件まで。細かいタスクは束ねて、1 行 1 ワークストリームにする
- 計画値と実績を混ぜない。予定の線表は source に計画時点を明記する

### 年表（`chronology`）

![年表](images/slide-templates/chronology.png)

時期と出来事を縦に並べた年表で、現在に至る経緯を示す

**答える問い**: これまで何が起き、どういう経緯で現在の状態に至ったか

**figures**: `governing_message`, `table`, `so_what`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**status**: experimental

使うときの決まり:

- 出来事の列には事実だけを書く。解釈・評価は「示唆」に分離する
- 時期の粒度を揃える（年なら年、年月なら年月で統一する）
- 行は 9 件まで。それ以前の経緯は束ねるか、載せる期間を絞る
- 空白期間に意味があるなら、行を省略せず「変化なし」と書いて見せる

### マイルストーン年表（`milestone-timeline`）

![マイルストーン年表](images/slide-templates/milestone-timeline.png)

横一本の時間軸に節目を等間隔で並べ、次の引き返し点を示す

**答える問い**: 節目がどう並んでいて、次に動くべき時点はいつか

**figures**: `governing_message`, `timeline`, `so_what`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**status**: experimental

使うときの決まり:

- 節目は 6 件まで。時間軸は等間隔で、期間の長短は表現しない（長短を見せたい計画は gantt-schedule を使う）
- 未来の節目は予定であることを source に明記する
- 時点ラベルは 10 字以内（例: 2026/09）。粒度を揃える

<a id="analysis"></a>

## 現状分析パック（`analysis`）

コンサルティングの現状分析・課題特定フレームワークをページ化した群。構造分解（ロジックツリー / KPI ツリー）、根本原因（なぜなぜ / 特性要因図）、定量絞り込み（パレート図）、ギャップ・業務フロー、外部環境（PEST / 5 フォース）、優先順位づけまでを揃えている。current-state-analysis スキルが使う。

### ロジックツリー（`logic-tree`）

![ロジックツリー](images/slide-templates/logic-tree.png)

論点を MECE に分解し、どこに問題（または打ち手）があるかを構造で示す

**答える問い**: この問題はどんな要素に分解でき、どこが効いているのか

**figures**: `governing_message`, `mece_tree`, `so_what`, `source_note`  
**推論レベル**: 診断（要因・構造の特定）  
**status**: experimental

使うときの決まり:

- tree は [ラベル, [子…]] の入れ子。子は同じ形か文字列。深さ 4 超・列幅不足は描画時にエラーになる
- 葉は 5 個まで（ノード高 0.46in を確保しているため）。それ以上は木を分割して 2 枚にする
- MECE（漏れなく・重複なく）は部品では保証されない。1 階層 1 基準で分解の切り口を揃えること
- Why ツリー（原因の分解）と How ツリー（打ち手の分解）を 1 本の木に混ぜない
- insight には「どの枝が効いているか」と、その判断根拠を書く

### KPIツリー（`kpi-tree`）

![KPIツリー](images/slide-templates/kpi-tree.png)

KGI を構成指標に分解し、目標未達（または達成）がどの指標に起因するかを示す

**答える問い**: 目標と実績の差は、どの構成指標から生まれているのか

**figures**: `governing_message`, `mece_tree`, `so_what`, `source_note`  
**推論レベル**: 診断（要因・構造の特定）  
**status**: experimental

使うときの決まり:

- 根は KGI 1 つ。ノードのラベルは「指標名\n実績値」（目標比を見せるなら「実績 / 目標」）で書く
- 親子は四則演算で説明できる関係だけにする（売上 = 新規 + 既存、新規 = リード × 転換率 …）。説明できない要素は載せない
- 数値はすべて出典必須。期間・集計定義を source に書く
- 葉は 5 個まで（2 行ラベルのノード高 0.46in を確保しているため）。指標が多いときはボトルネックの枝だけ展開し、他は上位で畳む
- insight には「どの指標が差の主因か」を定量で書く（例: 未達 △12% のうち △9% は商談化率）

### なぜなぜ分析（`why-why`）

![なぜなぜ分析](images/slide-templates/why-why.png)

観測された事象から「なぜ」を繰り返して真因まで掘り下げた連鎖を示す

**答える問い**: この事象の真因は何で、どこに手を打つべきか

**figures**: `governing_message`, `flow`, `so_what`, `source_note`  
**推論レベル**: 因果（原因の主張）  
**status**: experimental

使うときの決まり:

- chain[0] は観測された事象、末尾が真因。途中の段を飛ばさず「なぜ」1 回分ずつ掘る
- 「担当者の不注意」「意識が低い」で止めない。仕組み・プロセスの要因まで掘る
- 各段は事実で確認できる記述にする。確認できていない段には（仮説）を付す
- 幅の都合で 6 段まで。途中で原因が複数に分岐するなら fishbone-diagram を使う
- insight には真因に対する打ち手（再発防止策）を書く。対症療法と区別する

### 特性要因図（フィッシュボーン）（`fishbone-diagram`）

![特性要因図（フィッシュボーン）](images/slide-templates/fishbone-diagram.png)

問題事象に対する原因の仮説をカテゴリ別に洗い出し、検証の当たりを付ける

**答える問い**: この問題の原因はどの系統にあり、どこから検証すべきか

**figures**: `governing_message`, `fishbone`, `so_what`, `source_note`  
**推論レベル**: 診断（要因・構造の特定）  
**status**: experimental

使うときの決まり:

- カテゴリは 4M（人・機械・方法・材料）やプロセス名など、1 つの基準で揃える。基準を混ぜない
- 原因は各カテゴリ 4 個まで。溢れたら統合するか補足資料へ回す（網羅の証明図ではない）
- 載るのは「原因の仮説」。真因の特定は why-why かデータ検証で行い、検証済みの原因だけ太字等で区別しない（この図では全て同格）
- problem は測定可能な事象で書く（「品質が悪い」ではなく「月次不良率 3% 超」）
- insight には次に検証する原因と検証方法を書く

### パレート図（`pareto-analysis`）

![パレート図](images/slide-templates/pareto-analysis.png)

要因別の件数・金額と累積構成比を重ね、どの要因から潰すべきかを示す

**答える問い**: 少数の要因が全体の大半を占めているか。どこから手を付けるべきか

**figures**: `governing_message`, `pareto`, `so_what`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**status**: experimental

使うときの決まり:

- 値の大きい順に自動で並ぶ（「その他」だけは常に末尾）。渡す順序に意味は持たせない
- 合計に意味のある量（件数・金額・時間）だけ使う。率や指数を混ぜない
- 集計期間と母数を source に明記する
- 80% の破線は目安。上位に集中していない（累積線が直線に近い）ときは「集中していない」こと自体が発見で、無理に上位対策と結論しない
- 「その他」が最大になるような分類は粒度が粗すぎる。分類を見直してから使う

### ギャップ分析（As-Is / To-Be）（`gap-analysis`）

![ギャップ分析（As-Is / To-Be）](images/slide-templates/gap-analysis.png)

現状（As-Is）とあるべき姿（To-Be）を対で示し、埋めるべき課題を定義する

**答える問い**: 現状とあるべき姿の差はどこにあり、何を課題として設定するか

**figures**: `governing_message`, `before_after`, `cards`, `source_note`  
**推論レベル**: 戦略（評価と方向づけ）  
**status**: experimental

使うときの決まり:

- As-Is は確認された事実、To-Be は合意された目標。未合意の願望を To-Be に置くなら title で仮説と明示する
- asis と tobe は同じ観点を同じ順に並べる（行の対応で差分が読めるように）
- gaps は「差分の説明」ではなく「埋めるべき課題」として書く（何をどうすべき状態にするか）。課題カードがこのスライドの結論を担う
- 打ち手（How）の詳細はこのスライドに書かない。課題の優先順位付けは priority-matrix へ
- To-Be の数値目標には根拠（ベンチマーク・経営目標）を source に書く

### 業務フローとペインポイント（`process-painpoints`）

![業務フローとペインポイント](images/slide-templates/process-painpoints.png)

現状の業務フローを示し、どの工程にどんなペインポイントがあるかを対応づける

**答える問い**: 現状の業務はどう流れていて、どの工程に問題が集中しているのか

**figures**: `governing_message`, `flow`, `table`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**status**: experimental

使うときの決まり:

- steps は現状（As-Is）の流れ。理想の流れや改善後の姿を混ぜない
- pains の各行は [工程, ペインポイント, 影響]。工程名は steps の表記と一致させる
- ペインポイントは観察・ヒアリングで確認された事実だけ。影響は工数・時間・金額など測れる形で書き、出典を source に記す
- 行は 5 件まで。工程が 6 を超える詳細フローは drawio-diagrams で別紙にし、ここは主要工程に束ねる
- 解決策はこのスライドに書かない（課題の構造化は logic-tree、優先順位は priority-matrix へ）

### PEST分析（`pest-analysis`）

![PEST分析](images/slide-templates/pest-analysis.png)

政治・経済・社会・技術のマクロ環境要因を並べ、事業への外部影響を整理する

**答える問い**: 自社の事業環境を動かす外部要因は何か

**figures**: `governing_message`, `comparison`, `so_what`, `source_note`  
**推論レベル**: 戦略（評価と方向づけ）  
**status**: experimental

使うときの決まり:

- 自社の事業に影響しうる外部要因だけを載せる（一般ニュースの羅列にしない）
- 事実（施行済みの規制・公表統計）と見込み（審議中・兆し）を区別し、見込みには時期を付す
- 機会か脅威かの判定はここでしない（判定は SWOT へ渡す。このスライドは環境の記述に徹する）
- 4 象限とも 1 件以上。空の象限は「調べていない」と読まれる
- 各要因の出典を source にまとめて書く（官報・統計・調査レポート名）

### 5フォース分析（`five-forces`）

![5フォース分析](images/slide-templates/five-forces.png)

業界の競争構造を 5 つの力（業界内競争・新規参入・代替品・買い手・売り手）で評価する

**答える問い**: この業界の競争圧力はどこから来ていて、どの程度強いのか

**figures**: `governing_message`, `cards`, `source_note`  
**推論レベル**: 戦略（評価と方向づけ）  
**status**: experimental

使うときの決まり:

- 各力は「強 / 中 / 弱：根拠」の形で書く（評価だけ・根拠だけにしない）。title が結論（どの力が収益性を最も圧迫するか）を担う
- どの業界（市場の範囲）の話かを title か source に明記する。範囲が変わると評価も変わる
- 5 つの力は業界構造の記述。自社固有の強み・弱みは書かない（swot-analysis へ）
- 評価は評価者の判断を含む。評価の根拠資料と評価日を source に書く
- 中央（業界内の競争）は他の 4 つの力の結果でもある。因果の矢印はこの図では主張しない

### 課題優先順位マトリクス（`priority-matrix`）

![課題優先順位マトリクス](images/slide-templates/priority-matrix.png)

課題を効果と実行容易性の 2 軸に置き、どこから着手すべきかを示す

**答える問い**: 洗い出した課題のうち、どれから着手すべきか

**figures**: `governing_message`, `posmap`, `so_what`, `source_note`  
**推論レベル**: 戦略（評価と方向づけ）  
**status**: experimental

使うときの決まり:

- items は [課題名, x, y]。x / y は 0〜1 の相対値（0=左/下、1=右/上）。評価の根拠（効果試算・工数見積）と評価者・評価日を source に書く
- 課題名はバブル（直径 0.8in ≒ 4 字/行）に入る長さで。5 字以上は「権限申請\n自動化」のように改行位置を \n で明示する
- 右上（実行しやすい × 効果大）が最優先。ただし座標は主観評価になりがちなので、位置の議論より「順序」の合意に使う
- バブルが重なると読めない。課題は 8 件まで、近い課題は統合する
- highlight は着手を決めた課題だけに使う（強調が多いと何も強調されない）
- 課題の中身（何を解決するか）はこのスライドでは説明しない。gap-analysis や logic-tree で定義してから持ち込む

<a id="read-alone"></a>

## 読み物パック（`read-alone`）

1 枚で読み切れる高密度スライド（外資コンサル型の配布資料）のページ群。ガバニングメッセージ・リード文・エビデンス・示唆・出典を 1 枚に収める。全テンプレートが `$density` バリアントを持ち、同じファイルから print（配布・印刷）と presentation（登壇）の 2 密度で描画できる。

### 主張とエビデンス表（`claim-evidence-table`）

![主張とエビデンス表](images/slide-templates/claim-evidence-table.png)

主張・裏付けの表・示唆・出典を 1 枚に収め、読むだけで完結させる読み物スライドの標準形

**答える問い**: この主張はどの事実に支えられているか

**figures**: `governing_message`, `lead_in`, `table`, `so_what`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**densities**: print / presentation（既定 print）  
**status**: experimental

使うときの決まり:

- タイトルは「何が言えるか」を 2 行以内で書く。表の説明文にしない
- 示唆は表から読み取れる範囲に限定する。タイトルの復唱も新情報も書かない
- 出典のない数値は載せない。書けない行は削る

### 図表と示唆（`exhibit-analysis`）

![図表と示唆](images/slide-templates/exhibit-analysis.png)

図表番号つきの枠にグラフを収め、右側に読み取れる示唆を添えて本文・付録から参照できる 1 枚にする

**答える問い**: この図表から何が読み取れるか

**figures**: `governing_message`, `lead_in`, `exhibit_frame`, `vbars`, `so_what`, `source_note`  
**推論レベル**: 診断（要因・構造の特定）  
**densities**: print / presentation（既定 print）  
**status**: experimental

使うときの決まり:

- 図表番号は本文・付録からの参照に使う。通し番号の管理は作成者の責任
- 示唆は図から読み取れる範囲に限定する。図にない新情報は書かない
- 棒グラフの基線はゼロ固定。差を大きく見せる軸の誇張はしない

### エグゼクティブサマリー（`exec-summary-readable`）

![エグゼクティブサマリー](images/slide-templates/exec-summary-readable.png)

状況→課題→答えの 3 段と支える論点で、最初の 1 枚だけで意思決定できる状態にする

**答える問い**: この資料は結局何を決めてほしいのか

**figures**: `governing_message`, `exec_summary`, `source_note`  
**推論レベル**: 戦略（評価と方向づけ）  
**densities**: print / presentation（既定 print）  
**status**: experimental

使うときの決まり:

- この 1 枚だけで意思決定できることが条件。本編は答えの裏付けに回す
- 答えの段は結論を数値つきで書く。「検討する」で終わらせない
- 支える論点が 5 つを超えるなら本編の章立てから見直す

### 結論・根拠・So What（`conclusion-rationale-implication`）

![結論・根拠・So What](images/slide-templates/conclusion-rationale-implication.png)

結論を先に置き、根拠カードと次の打ち手（So What）で 1 枚のピラミッドとして読み切らせる

**答える問い**: 結論は何で、なぜそう言え、次に何をするのか

**figures**: `governing_message`, `lead_in`, `cards`, `so_what`, `source_note`  
**推論レベル**: 戦略（評価と方向づけ）  
**densities**: print / presentation（既定 print）  
**status**: experimental

使うときの決まり:

- 結論はタイトルに書く。本文の最後まで読まないと結論が分からない構成にしない
- 根拠は互いに重ならない 3〜4 点に絞る。5 点を超えるなら別スライドに分ける
- So What は次の行動を書く。根拠やタイトルの復唱にしない

### 案の比較評価（`dense-comparison-table`）

![案の比較評価](images/slide-templates/dense-comparison-table.png)

複数案をドット評価のマトリクスで比較し、推奨案とその理由まで 1 枚で示す

**答える問い**: どの案が最も優れ、なぜそれを推すのか

**figures**: `governing_message`, `lead_in`, `rating_matrix`, `so_what`, `source_note`  
**推論レベル**: 診断（要因・構造の特定）  
**densities**: print / presentation（既定 print）  
**status**: experimental

使うときの決まり:

- 評価基準は意思決定に効くものだけに絞る。埋め草の基準を足さない
- 採点の根拠（見積もり・評価会など）を必ず出典に書く
- 推奨は劣る点も認めた上で総合判断として書く。全勝の案に見せかけない

### ストーリーライン（`key-message-storyline`）

![ストーリーライン](images/slide-templates/key-message-storyline.png)

本編のアクションタイトルを順に並べ、タイトルだけで論旨が通ることを 1 枚で示す横の論理

**答える問い**: タイトルだけを読んで話の筋が通っているか

**figures**: `governing_message`, `lead_in`, `storyline`, `source_note`  
**推論レベル**: 戦略（評価と方向づけ）  
**densities**: print / presentation（既定 print）  
**status**: experimental

使うときの決まり:

- 各行は本編スライドのアクションタイトルと一致させる。要約で書き換えない
- ここで論旨が途切れるならスライドを作る前に構成を直す
- 各行は「何が言えるか」の主張形で書く。「〜について」の目次形にしない

### 想定問答（`faq-objection-handling`）

![想定問答](images/slide-templates/faq-objection-handling.png)

承認会議で想定される反論と根拠つきの回答を対で並べ、質疑を先回りして潰す 1 枚

**答える問い**: 想定される反論にどう答えるか

**figures**: `governing_message`, `lead_in`, `table`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**densities**: print / presentation（既定 print）  
**status**: experimental

使うときの決まり:

- 回答には必ず根拠（本編の図表番号・付録・試験結果など）を添える
- 答えられない懸念は残す。ごまかした回答は資料全体の信頼を壊す
- 懸念は実際に出そうなものに絞る。自作自演の弱い反論を並べない

### ワンページブリーフ（`one-page-brief`）

![ワンページブリーフ](images/slide-templates/one-page-brief.png)

図表・比較表・示唆・決定事項・出典を 1 枚に収める、パック中最も高密度な 1 枚もの決裁資料

**答える問い**: この 1 枚だけで決裁者が判断と決定事項を確認できるか

**figures**: `governing_message`, `lead_in`, `exhibit_frame`, `vbars`, `table`, `so_what`, `source_note`  
**推論レベル**: 戦略（評価と方向づけ）  
**densities**: print / presentation（既定 print）  
**status**: experimental

使うときの決まり:

- この 1 枚は決裁の最終確認用。図表と表は本編の要約であり、初出の数字を置かない
- 決定事項は Yes/No を言える形で書き、期限を添える。「検討を継続」を決定事項にしない
- 詰め込むのは情報であって文字ではない。表のセルは体言止めで短く保つ

<a id="business-plan"></a>

## 事業計画パック（`business-plan`）

事業計画・稟議で承認者が最初に見る「収益・投資・リスク・体制」のページ群。収益計画（P/L）、売上ブリッジ、コスト構造、損益分岐点、シナリオ比較、投資回収、リスクと撤退基準、推進体制を 1 枚ずつのフォーマットにしている。全テンプレートが `$density` バリアントを持ち、配布用の事業計画書（print）と役員会での説明（presentation）の 2 密度で描画できる。

### 収益計画（複数年 P/L）（`revenue-plan`）

![収益計画（複数年 P/L）](images/slide-templates/revenue-plan.png)

売上高から営業利益までの損益計画を年度別の表で示し、黒字化の時期と水準を 1 枚で示す

**答える問い**: この事業は何年目にいくらの売上と利益になり、いつ黒字化するのか

**figures**: `governing_message`, `lead_in`, `table`, `source_note`  
**推論レベル**: 予測（将来値の見通し）  
**densities**: print / presentation（既定 print）  
**status**: experimental

使うときの決まり:

- タイトルは全角 30 字前後・1 行に収める。2 行に折り返すと直下のリード文と重なる
- 先頭列は項目名、残り 4 列は期間。3 期の計画なら最終列を「累計」か「CAGR」に充てる（空列を作らない）
- 単位（百万円・千円）と税抜/税込を先頭列ヘッダーか lead に必ず明記する
- 売上高の根拠は sales-buildup、費用の根拠は cost-structure に置く。このスライドは結果だけを載せる
- 利益率などの比率行は算出済みの文字列を渡す。スライド上では計算されない
- 実績ではなく計画値。実績を併記するなら行ラベルに（実績）と明記して区別する
- 前提が変わると全数字が動く。前提の幅は scenario-comparison で別途示す

### 売上ブリッジ（積み上げ分解）（`sales-buildup`）

![売上ブリッジ（積み上げ分解）](images/slide-templates/sales-buildup.png)

起点から計画値までの売上増減をドライバー別に橋渡しし、成長の内訳と依存先を示す

**答える問い**: 計画売上はどのドライバーの積み上げで成り立ち、どこに最も依存しているか

**figures**: `governing_message`, `lead_in`, `waterfall`, `so_what`, `source_note`  
**推論レベル**: 予測（将来値の見通し）  
**densities**: print / presentation（既定 print）  
**status**: experimental

使うときの決まり:

- タイトルは全角 30 字前後・1 行に収める。2 行に折り返すと直下のリード文と重なる
- 各項目の第 3 要素は total（0 からの累計）か delta（前の累計からの増減）。先頭は必ず total（起点）にする
- 最後の total は増減の積み上げ合計と一致しなければ生成時にエラーになる。表計算の値をそのまま転記する
- 途中の累計がマイナスになる橋は描けない。減少が大きい計画は起点を分けるか別スライドにする
- ドライバーは意思決定できる粒度で切る（新規/既存拡大/解約/価格）。「その他」に大きな塊を残さない
- 単位は unit か lead に明記する。ドライバーごとの算定根拠は出典行に書く
- 積み上げの合計は revenue-plan の売上高と一致させる

### 投資・コスト構造（`cost-structure`）

![投資・コスト構造](images/slide-templates/cost-structure.png)

年度別のコスト構成の推移と、初期投資／年間ランニングの費目内訳を並べて必要投資額を示す

**答える問い**: この事業にいくら必要で、費用は何にどの順で使われるのか

**figures**: `governing_message`, `lead_in`, `vbars_stacked`, `table`, `source_note`  
**推論レベル**: 予測（将来値の見通し）  
**densities**: print / presentation（既定 print）  
**status**: experimental

使うときの決まり:

- タイトルは全角 30 字前後・1 行に収める。2 行に折り返すと直下のリード文と重なる
- 費目は 4 つまで。5 つ目以降は「その他」に畳まないと積み上げが読めなくなる
- 積み上げの合計は revenue-plan の売上原価＋販管費と一致させる
- 初期投資（一時費用）と年間ランニング（継続費用）を右表で必ず分ける。合算した総額だけを見せない
- 該当しないセルは空欄にせず「—」を入れる（未記入と区別できるように）
- 人件費は人数×単価の前提を出典に書く。金額だけでは査定できない
- 単位と税抜／税込を lead か unit に明記する
- 期間は 4 期まで。5 期以上は年度をまとめるか、期間を分けて 2 枚にする

### 損益分岐点分析（`break-even`）

![損益分岐点分析](images/slide-templates/break-even.png)

売上高線と総費用線の交点で損益分岐点を示し、計画に対する安全余裕率まで併記する

**答える問い**: どれだけ売れば赤字を脱するのか、計画にどれだけ余裕があるのか

**figures**: `governing_message`, `lead_in`, `linechart`, `metric`, `source_note`  
**推論レベル**: 予測（将来値の見通し）  
**densities**: print / presentation（既定 print）  
**status**: experimental

使うときの決まり:

- タイトルは全角 30 字前後・1 行に収める。2 行に折り返すと直下のリード文と重なる
- 固定費と変動費の区分定義を出典行に必ず書く。区分が変われば分岐点も変わる
- 売上高線と総費用線は同じ横軸（数量または売上規模）・同じ期間で引く
- 単年度の静的分析であり、資金繰りは示さない。回収と資金の話は roi-payback へ
- 変動費率が数量帯で変わる事業では直線近似が崩れる。適用範囲を lead に明記する
- 安全余裕率は（計画売上−損益分岐点売上）÷計画売上。算出済みの文字列を渡す
- 計画点（現在の販売水準）は lead か出典で言葉にする。線の端に値ラベルは付けない（分岐点付近で必ず重なる）

### シナリオ比較（悲観・標準・楽観）（`scenario-comparison`）

![シナリオ比較（悲観・標準・楽観）](images/slide-templates/scenario-comparison.png)

複数シナリオの業績推移と、その差を生む前提条件を対で示し、計画の振れ幅を明らかにする

**答える問い**: 前提がどう振れると業績はどこまで動くのか、最悪ケースは許容できるか

**figures**: `governing_message`, `lead_in`, `linechart`, `table`, `source_note`  
**推論レベル**: 予測（将来値の見通し）  
**densities**: print / presentation（既定 print）  
**status**: experimental

使うときの決まり:

- タイトルは全角 30 字前後・1 行に収める。2 行に折り返すと直下のリード文と重なる
- シナリオは前提の違いだけで区別する。同じ前提から違う結果を出さない
- 表に載せる前提は結果を動かすドライバーだけに絞る。動かない前提は書かない
- 悲観シナリオは「少し悪い」ではなく、意思決定が変わる水準まで振る。楽観は根拠のある上限に留める
- 標準シナリオの数値は revenue-plan と一致させる
- 確率の重みづけはしない。起こりやすさを論じるなら別スライドで根拠とともに示す
- 撤退判断に使う場合は、どのシナリオで何をするかを risk-register の撤退基準と紐づける
- yMax は最大値のすぐ上の丸い数に置く。自動目盛りは最大値の 1.4 倍まで上に取ることがあり、線が下半分に潰れて読めなくなる

### 投資回収（ROI・回収期間）（`roi-payback`）

![投資回収（ROI・回収期間）](images/slide-templates/roi-payback.png)

累計投資と累計リターンの交点で回収時期を示し、回収率・回収期間・NPV を数値で添える

**答える問い**: 投じた資金はいつ回収でき、投資判断として見合うのか

**figures**: `governing_message`, `lead_in`, `metric`, `linechart`, `source_note`  
**推論レベル**: 予測（将来値の見通し）  
**densities**: print / presentation（既定 print）  
**status**: experimental

使うときの決まり:

- タイトルは全角 30 字前後・1 行に収める。2 行に折り返すと直下のリード文と重なる
- 折れ線は累計値どうしを比べる。単年度の値と累計値を同じ図に混ぜない
- 累計はマイナスにならない形（累計投資額と累計リターン）で描き、交点を回収時点として読む
- 割引率と算定期間を npvLabel か出典行に必ず書く。前提のない NPV は比較できない
- 回収期間は「割引前／割引後」のどちらかを明示する。両者は 1 年以上ずれることがある
- 回収率・NPV は算出済みの文字列を渡す。スライド上では計算されない
- 投資額は cost-structure、リターンの元になる売上は revenue-plan と一致させる
- 線の端に値ラベルは付けない。回収時点の交差付近でラベルが重なるため、金額は上部の指標タイルで示す

### リスクと対策・撤退基準（`risk-register`）

![リスクと対策・撤退基準](images/slide-templates/risk-register.png)

主要リスクを影響度・発生度とともに一覧化し、対策と撤退／見直しの発動基準まで対で示す

**答える問い**: 何が計画を壊しうるのか、どう手当てし、どうなったら止めるのか

**figures**: `governing_message`, `lead_in`, `table`, `so_what`, `source_note`  
**推論レベル**: 戦略（評価と方向づけ）  
**densities**: print / presentation（既定 print）  
**status**: experimental

使うときの決まり:

- タイトルは全角 30 字前後・1 行に収める。2 行に折り返すと直下のリード文と重なる
- 1 行 = 1 リスク。影響度と発生度は 大／中／小 など全行で同じ尺度の語を使う
- 撤退・見直し基準は必ず観測可能な数値で書く（「状況を見て」は基準ではない）
- 対策は担当が動かせる具体行動を書く。「注意する」「検討する」は対策にならない
- 対策済みで残存リスクが小さいものは載せない。承認者が判断を変えうるリスクだけに絞る
- 撤退判断の主体とタイミング（誰がいつ）は decisionRule に書く。行ごとの基準と役割分担を混ぜない
- シナリオ分析と併用する場合、悲観シナリオの水準と撤退基準の整合を取る

### 推進体制と役割分担（`execution-structure`）

![推進体制と役割分担](images/slide-templates/execution-structure.png)

事業を実行する体制図と、役割ごとの担当・人数を並べて実行可能性を裏づける

**答える問い**: 誰がこの事業を実行し、どの役割に何人必要なのか

**figures**: `governing_message`, `lead_in`, `orgchart`, `table`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**densities**: print / presentation（既定 print）  
**status**: experimental

使うときの決まり:

- タイトルは全角 30 字前後・1 行に収める。2 行に折り返すと直下のリード文と重なる
- 全社の組織図ではなく、この事業の推進体制を書く。関与しない部署は載せない
- 人数は cost-structure の人件費と一致させる。体制図で増員し、費用計画で増やし忘れない
- 専任と兼務を必ず区別して書く。兼務比率が高い体制は実行可能性の指摘対象になる
- 深さ 4 以上・葉 8 超は文字が潰れる。部門ごとにスライドを分ける
- ノードのラベルは「役割\n人数」の 2 行にすると読みやすい。個人名は社外提出時に伏せる
- 立ち上げ期と拡大期で体制が変わるなら、時期を明記して 2 枚に分ける
