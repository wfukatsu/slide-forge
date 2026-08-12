# スライドテンプレート カタログ（全 37 種）

`slide-templates/` に登録されたテンプレートを実際に 1 枚ずつ生成して
書き出した画像カタログ。**どのテンプレートで 1 枚を作るかを見て選ぶ**ためのもの。
スキーマの書き方は [template-schema.md](template-schema.md)、
汎用ページパターン（骨格・図表の組み方）は
[slide-pattern-catalog.md](slide-pattern-catalog.md) にある。

各テンプレートの **figures** 行は、そのページが使っている描画部品の `type` 名。
テンプレートは `render_slide_template.py` かデッキ仕様の `$template` で使う。

```bash
# このカタログを作り直す（テンプレートを追加したときも同じ手順）
for pack in marketing-analysis b2b-sales scalar-ae planning analysis; do
  .venv/bin/python scripts/build_slide_template_catalog.py \
      --pack $pack --out out/template-catalog/$pack.json
done
# 5 つの spec の slides を 1 つに結合して build_deck.py で生成し、
# fetch_thumbnails.py の PNG を references/images/slide-templates/<id>.png に配置
.venv/bin/python scripts/build_template_catalog_doc.py
```

| パック | 数 | 何を作るための章か |
|---|---|---|
| [マーケティング分析パック](#marketing-analysis) | 8 種 | 市場・顧客・施策効果を分析するページ群 |
| [B2B セールスパック](#b2b-sales) | 8 種 | 商談のステークホルダー構造とディスカバリー（課題探索）を可視化するページ群 |
| [Scalar AE パック](#scalar-ae) | 8 種 | Scalar のアカウントエグゼクティブが商談レビュー・活動計画で使う定型ページ群 |
| [計画パック](#planning) | 3 種 | 時間軸を持つ計画を示すページ群 |
| [現状分析パック](#analysis) | 10 種 | コンサルティングの現状分析・課題特定フレームワークをページ化した群 |

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
