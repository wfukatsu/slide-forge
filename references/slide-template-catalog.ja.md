*[English](slide-template-catalog.md)*

# スライドテンプレート カタログ（全 108 種）

`slide-templates/` に登録されたテンプレートを実際に 1 枚ずつ生成して
書き出した画像カタログ。**どのテンプレートで 1 枚を作るかを見て選ぶ**ためのもの。
スキーマの書き方は [template-schema.md](template-schema.ja.md)、
汎用ページパターン（骨格・図表の組み方）は
[slide-pattern-catalog.md](slide-pattern-catalog.ja.md) にある。

各テンプレートの **figures** 行は、そのページが使っている描画部品の `type` 名。
**入力**表は、そのテンプレートに渡すデータのスロット名・型・必須・制約。

テンプレートを明示的に指定するには、デッキ仕様のスライドに `$template` を書く。
そのテンプレートが 1 枚に展開される。`data` のキーが各テンプレートの**入力**表の
スロット名:

```json
{
  "slides": [
    {
      "$template": "swot-analysis",
      "data": {
        "title": "自社の戦略ポジション",
        "quadrants": ["強み: …", "弱み: …", "機会: …", "脅威: …"],
        "insight": "…",
        "source": "2026 年 3 月 経営会議資料"
      },
      "notes": "スピーカーノート（任意）"
    }
  ]
}
```

`$template` / `data` / `density` / `lang` 以外のキーは展開後のスライドに上書きで
合流するので、`notes` を足したり `layout` を差し替えたりできる。密度はスライドの
`density` → spec の `density` → テンプレート既定の順。展開は検証・生成・`--into`
より前に走るため、`--dry-run --strict` で入力の過不足を生成前に検査できる。

各テンプレートが自分で刷る語（表の見出し、軸の両端など）は `lang` で切り替わり、
`slide-templates/i18n/<lang>.json` から引く。`data` に書いた内容は翻訳されない。
訳の無いキーは既定言語のまま出るので、未翻訳は空欄ではなく目に見える。

1 枚だけ JSON に落とすなら `render_slide_template.py` を使う:

```bash
.venv/bin/python scripts/render_slide_template.py \
    --template swot-analysis --data my-swot.json --out out/swot.json
```

```bash
# このカタログを作り直す（テンプレートを追加したときも同じ手順）
for pack in marketing-analysis b2b-sales scalar-ae planning calendar analysis read-alone business-plan nexus hearing case-studies proposal marketing partner; do
  .venv/bin/python scripts/build_slide_template_catalog.py \
      --pack $pack --out out/template-catalog/$pack.json
done
# 各 spec の slides を 1 つに結合して build_deck.py で生成し、
# fetch_thumbnails.py の PNG を references/images/slide-templates/<id>.png に配置
.venv/bin/python scripts/build_template_catalog_doc.py
```

> `architecture-exhibit` / `ui-mock-flow` / `ui-mock-detail` は、実行結果の
> スクリーンショットを貼るページのため画像が無い。nexus-architect を実際に
> 走らせた出力が要る。

| パック | 数 | 何を作るための章か |
|---|---|---|
| [マーケティング分析パック](#marketing-analysis) | 8 種 | 市場・顧客・施策効果を分析するページ群 |
| [B2B セールスパック](#b2b-sales) | 8 種 | 商談のステークホルダー構造とディスカバリー（課題探索）を可視化するページ群 |
| [Scalar AE パック](#scalar-ae) | 10 種 | Scalar のアカウントエグゼクティブが商談レビュー・活動計画で使う定型ページ群 |
| [計画パック](#planning) | 3 種 | 時間軸を持つ計画を示すページ群 |
| [カレンダーパック](#calendar) | 9 種 | 日付を軸にした予定・タスクのページ群 |
| [現状分析パック](#analysis) | 10 種 | コンサルティングの現状分析・課題特定フレームワークをページ化した群 |
| [読み物パック](#read-alone) | 8 種 | 1 枚で読み切れる高密度スライド（外資コンサル型の配布資料）のページ群 |
| [事業計画パック](#business-plan) | 8 種 | 事業計画・稟議で承認者が最初に見る「収益・投資・リスク・体制」のページ群 |
| [Nexus レポートパック](#nexus) | 21 種 | nexus-architect の実行結果をスライドにするページ群 |
| [ヒアリングパック](#hearing) | 6 種 | 伝えるためではなく**集めるため**のページ群 |
| [事例パック](#case-studies) | 3 種 | 公表事例を資料に載せるページ群 |
| [提案パック](#proposal) | 6 種 | 問題解決型提案のうち、再利用できるページが無かった節 |
| [マーケティングパック](#marketing) | 6 種 | まだ商談になっていない相手に当てるページ群 |
| [パートナーパック](#partner) | 2 種 | プレイブックが定義しながらテンプレートの無かった 2 種 |

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `quadrants` | `string[]` | ✔ | 4 件、80 字以内 |
| `insight` | `string` | ✔ | 120 字以内 |
| `source` | `string` | ✔ | 160 字以内 |

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `labels` | `string[]` | ✔ | 3 件、40 字以内 |
| `center` | `string` | ✔ | 36 字以内 |
| `details` | `string[][]` | ✔ | 3 件、60 字以内 |
| `source` | `string` | ✔ | 160 字以内 |

### TAM / SAM / SOM（`market-sizing`）

![TAM / SAM / SOM](images/slide-templates/market-sizing.png)

市場全体から獲得可能市場までを入れ子で示す

**答える問い**: 市場規模と現実的な獲得可能範囲はどの程度か

**figures**: `governing_message`, `nested_circles`, `so_what`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `rings` | `string[][]` | ✔ | 3〜4 件、40 字以内 |
| `insight` | `string` | ✔ | 120 字以内 |
| `source` | `string` | ✔ | 160 字以内 |

### ポジショニングマップ（`positioning-map`）

![ポジショニングマップ](images/slide-templates/positioning-map.png)

2軸上で自社と競合の位置関係を示す

**答える問い**: 自社は競合と異なる価値を提供できているか

**figures**: `governing_message`, `posmap`, `so_what`, `source_note`  
**推論レベル**: 診断（要因・構造の特定）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `points` | `array` (string≤24, number≤1, number≤1) | ✔ | 2〜8 件 |
| `xAxis` | `string[]` | ✔ | 2 件、24 字以内 |
| `yAxis` | `string[]` | ✔ | 2 件、24 字以内 |
| `highlight` | `string` | ✔ | 20 字以内 |
| `insight` | `string` | ✔ | 120 字以内 |
| `source` | `string` | ✔ | 160 字以内 |

### RFMセグメント（`rfm-segments`）

![RFMセグメント](images/slide-templates/rfm-segments.png)

購買の最新性・頻度・金額から顧客群と施策を比較する

**答える問い**: 優良・育成・休眠顧客は誰で、どの施策を行うか

**figures**: `governing_message`, `table`, `so_what`, `source_note`  
**推論レベル**: 診断（要因・構造の特定）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `rows` | `string[][]` | ✔ | 3〜7 件、44 字以内 |
| `insight` | `string` | ✔ | 120 字以内 |
| `source` | `string` | ✔ | 160 字以内 |

### コホート継続率（`cohort-retention`）

![コホート継続率](images/slide-templates/cohort-retention.png)

獲得時期別の継続率を期間ごとに比較する

**答える問い**: 新しく獲得した顧客の継続率は改善しているか

**figures**: `governing_message`, `table`, `so_what`, `source_note`  
**推論レベル**: 診断（要因・構造の特定）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `headers` | `string[]` | ✔ | 4〜10 件、16 字以内 |
| `rows` | `string[][]` | ✔ | 3〜10 件、20 字以内 |
| `insight` | `string` | ✔ | 120 字以内 |
| `source` | `string` | ✔ | 160 字以内 |

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `stages` | `string[][]` | ✔ | 3〜6 件、32 字以内 |
| `insight` | `string` | ✔ | 120 字以内 |
| `source` | `string` | ✔ | 160 字以内 |

### A/Bテスト結果（`experiment-result`）

![A/Bテスト結果](images/slide-templates/experiment-result.png)

対照群と施策群の結果、母数、差、判定を1枚で示す

**答える問い**: 施策によって主要KPIはどの程度変化したか

**figures**: `governing_message`, `vbars_grouped`, `table`, `so_what`, `source_note`  
**推論レベル**: 因果（原因の主張）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `categories` | `string[]` | ✔ | 1〜4 件、20 字以内 |
| `series` | `array` (string≤20, number[]) | ✔ | 2 件 |
| `resultRows` | `string[][]` | ✔ | 3〜5 件、48 字以内 |
| `insight` | `string` | ✔ | 120 字以内 |
| `source` | `string` | ✔ | 180 字以内 |

使うときの決まり:

- 有意差がない結果を効果ゼロと断定しない
- 事前に定めた主要KPIと分析期間を明記する

<a id="b2b-sales"></a>

## B2B セールスパック（`b2b-sales`）

商談のステークホルダー構造とディスカバリー（課題探索）を可視化するページ群。誰が意思決定に効くのか・何がまだ聞けていないのかを 1 枚で共有する。

### インフルエンスマップ（`influence-map`）

![インフルエンスマップ](images/slide-templates/influence-map.png)

購買関与者を影響力と賛否の2軸に配置し、誰を動かせば決まるかを示す

**答える問い**: この商談は誰を動かせば決まるか / 反対側に影響力が偏っていないか

**figures**: `governing_message`, `posmap`, `so_what`, `source_note`  
**推論レベル**: 診断（要因・構造の特定）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `stakeholders` | `array` (string≤6, number≤1, number≤1) | ✔ | 3〜9 件 |
| `xAxis` | `string[]` | ✔ | 2 件、24 字以内 |
| `yAxis` | `string[]` | ✔ | 2 件、24 字以内 |
| `champion` | `string` | ✔ | 6 字以内 |
| `insight` | `string` | ✔ | 120 字以内 |
| `source` | `string` | ✔ | 160 字以内 |

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `members` | `string[][]` | ✔ | 3〜7 件、22 字以内 |
| `insight` | `string` | ✔ | 120 字以内 |
| `source` | `string` | ✔ | 160 字以内 |

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `tree` | `tuple` (string≤30, array) | ✔ | — |
| `insight` | `string` | ✔ | 110 字以内 |
| `source` | `string` | ✔ | 160 字以内 |

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `items` | `array` (integer≤99, string≤16, string≤34, string≤9) | ✔ | 4〜8 件 |
| `insight` | `string` | ✔ | 110 字以内 |
| `source` | `string` | ✔ | 160 字以内 |

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `lead` | `string` | ✔ | 100 字以内 |
| `chain` | `string[]` | ✔ | 3〜5 件、18 字以内 |
| `evidence` | `string[][]` | ✔ | 3〜5 件、40 字以内 |
| `source` | `string` | ✔ | 170 字以内 |

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `lead` | `string` | ✔ | 100 字以内 |
| `gaps` | `string[][]` | ✔ | 3〜6 件、40 字以内 |
| `source` | `string` | ✔ | 160 字以内 |

使うときの決まり:

- 「なぜ重要か」を書けない項目は聞かない。質問の量ではなく順序で決まる
- 確認相手と期限のない行を残さない
- discovery-map の missing / wip と対応させること

### インフルエンスマップ（組織構造）（`influence-map-org`）

![インフルエンスマップ（組織構造）](images/slide-templates/influence-map-org.png)

購買関与者を組織のつながりで並べ、役割・影響度・立場・面談状況を示す

**答える問い**: 誰が誰の下にいて、どこに影響力と支持が集まっているか

**figures**: `governing_message`, `influence_graph`, `so_what`, `source_note`  
**推論レベル**: 診断（要因・構造の特定）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `people` | `array` | ✔ | 2〜9 件 |
| `links` | `array` | — | 最大 4 件、既定 `[]` |
| `more` | `string` | — | 60 字以内、既定 `""` |
| `insight` | `string` | ✔ | 58 字以内 |
| `source` | `string` | ✔ | 160 字以内 |

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `nodes` | `array` | ✔ | 2〜9 件 |
| `edges` | `array` | — | 最大 20 件、既定 `[]` |
| `more` | `string` | — | 60 字以内、既定 `""` |
| `insight` | `string` | ✔ | 58 字以内 |
| `source` | `string` | ✔ | 160 字以内 |

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `headline` | `array` (string≤10, string≤24) | ✔ | 4 件 |
| `rows` | `string[][]` | ✔ | 3〜4 件、46 字以内 |
| `source` | `string` | ✔ | 160 字以内 |

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `stage` | `string` | ✔ | 60 字以内 |
| `gates` | `string[][]` | ✔ | 3〜6 件、40 字以内 |
| `source` | `string` | ✔ | 160 字以内 |

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `items` | `array` (string≤16, string≤80) | ✔ | 4 件 |
| `insight` | `string` | ✔ | 110 字以内 |
| `source` | `string` | ✔ | 160 字以内 |

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `lead` | `string` | ✔ | 100 字以内 |
| `actions` | `string[][]` | ✔ | 3〜6 件、36 字以内 |
| `source` | `string` | ✔ | 160 字以内 |

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `milestones` | `array` (string≤10, string≤16) | ✔ | 3〜6 件 |
| `rows` | `string[][]` | ✔ | 2〜4 件、44 字以内 |
| `source` | `string` | ✔ | 160 字以内 |

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `context` | `string` | ✔ | 120 字以内 |
| `questions` | `string[]` | ✔ | 3〜4 件、44 字以内 |
| `ask` | `string` | ✔ | 90 字以内 |
| `objections` | `array` (string≤20, string≤52) | ✔ | 2〜3 件 |
| `source` | `string` | ✔ | 160 字以内 |

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `situation` | `string` | ✔ | 84 字以内 |
| `complication` | `string` | ✔ | 84 字以内 |
| `resolution` | `string` | ✔ | 84 字以内 |
| `risks` | `string[][]` | ✔ | 2〜3 件、46 字以内 |
| `source` | `string` | ✔ | 160 字以内 |

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `lead` | `string` | ✔ | 100 字以内 |
| `steps` | `array` (string≤16, string≤68) | ✔ | 3 件 |
| `question` | `string` | ✔ | 100 字以内 |
| `source` | `string` | ✔ | 160 字以内 |

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `lead` | `string` | ✔ | 100 字以内 |
| `lines` | `string[][]` | ✔ | 2〜(print 7 · presentation 4) 件、(print 20 · presentation 14) 字以内 |
| `offerPrice` | `string` | ✔ | 12 字以内 |
| `offerLabel` | `string` | — | 18 字以内、既定 `"御提供金額（年額・税抜）"` |
| `pricing` | `string[][]` | ✔ | 3〜4 件、12 字以内 |
| `assumptions` | `string[]` | — | 最大 (print 2 · presentation 1) 件、60 字以内、既定 `[]` |
| `source` | `string` | ✔ | 170 字以内 |

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `lead` | `string` | ✔ | 100 字以内 |
| `patternHeaders` | `string[]` | ✔ | 3〜4 件、14 字以内 |
| `rows` | `string[][]` | ✔ | 3〜(print 5 · presentation 4) 件、(print 20 · presentation 14) 字以内 |
| `recommendation` | `string` | ✔ | (print 55 · presentation 30) 字以内 |
| `source` | `string` | ✔ | 170 字以内 |

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `columns` | `string[]` | ✔ | 3〜8 件、8 字以内 |
| `tasks` | `array` (string≤16, number≤8, number≤8, string≤20) | ✔ | 2〜8 件 |
| `source` | `string` | ✔ | 160 字以内 |

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `events` | `string[][]` | ✔ | 4〜9 件、44 字以内 |
| `insight` | `string` | ✔ | 120 字以内 |
| `source` | `string` | ✔ | 160 字以内 |

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `milestones` | `array` (string≤10, string≤16) | ✔ | 3〜6 件 |
| `insight` | `string` | ✔ | 160 字以内 |
| `source` | `string` | ✔ | 160 字以内 |

使うときの決まり:

- 節目は 6 件まで。時間軸は等間隔で、期間の長短は表現しない（長短を見せたい計画は gantt-schedule を使う）
- 未来の節目は予定であることを source に明記する
- 時点ラベルは 10 字以内（例: 2026/09）。粒度を揃える

<a id="calendar"></a>

## カレンダーパック（`calendar`）

日付を軸にした予定・タスクのページ群。月間カレンダー（月曜/日曜始まり）・日単位ガント・日次タスクリスト・週間タイムテーブル・スプリントカレンダー・年間カレンダー・期限カウントダウン・日次ヒートマップ・当番表の 9 形式で、土日祝の色分けと営業日数の計算、期間の自動分割（scripts/calendar_pages.py）を備える。

### 月間カレンダー（`month-calendar`）

![月間カレンダー](images/slide-templates/month-calendar.png)

1 週 1 行の月カレンダーに予定と複数日の期間を書き込み、月内の混み具合と休日を示す

**答える問い**: この月のどの日に何があり、どこが混んでいるか

**figures**: `governing_message`, `month_calendar`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 36 字以内 |
| `month` | `string` | ✔ | 7 字以内、6 字以上 |
| `weekStart` | `string` | — | 3 字以内、3 字以上、既定 `"mon"` |
| `events` | `array` (string≤10, string≤10, string≤20, string≤7, string≤5) | ✔ | 最大 40 件 |
| `extraHolidays` | `array` (string≤10, string≤10) | — | 最大 20 件、既定 `[]` |
| `source` | `string` | ✔ | 160 字以内 |

使うときの決まり:

- タイトル（結論）は 1 行・全角 36 字まで。2 行になるとカレンダーの見出しに重なる
- 予定は [開始日, 終了日, 件名, 分類, 時刻]。日付は YYYY-MM-DD で書き、年のない日付（9/3 など）を推測で補わない
- 終了日が空なら 1 日の予定としてマスに書き、終了日があれば帯で描く。週をまたぐ帯は週ごとに分かれ「（続き）」が付く
- 週始まりは weekStart で切り替える（mon / sun）。月曜始まりは ISO 週番号を左に出し、日曜始まりでは出さない
- 1 マスに入る予定は約 2 件。超えた分は「+N件」に畳まれるので、詳細は daily-agenda のページで補う
- 件名は全角 8 字程度で省略される。時刻は入りきらなければ省かれ、件名が優先される
- 祝日は同梱の内閣府 CSV の収録年だけ自動で判定する。会社独自の休業日は extraHolidays で渡す
- 予定（計画）であることと、いつ時点の予定かを source に書く

### 日単位ガント（`daily-gantt`）

![日単位ガント](images/slide-templates/daily-gantt.png)

日付の列にタスクの帯を置き、休日を挟んだ実際の稼働日数と節目を日単位で示す

**答える問い**: 指定期間の作業が日単位でどう並行し、休日を挟んでいつ終わるか

**figures**: `governing_message`, `day_gantt`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 36 字以内 |
| `start` | `string` | ✔ | 10 字以内、8 字以上 |
| `end` | `string` | ✔ | 10 字以内、8 字以上 |
| `rows` | `array` (string≤9, string≤14, string≤6, string≤10, string≤10, number≤1) | ✔ | 1〜12 件 |
| `today` | `string` | — | 10 字以内、既定 `""` |
| `extraHolidays` | `array` (string≤10, string≤10) | — | 最大 20 件、既定 `[]` |
| `source` | `string` | ✔ | 160 字以内 |

使うときの決まり:

- タイトル（結論）は 1 行・全角 36 字まで。2 行になるとカレンダーの見出しに重なる
- 行は [種類, 名前, 担当, 開始日, 終了日, 進捗]。種類は group（見出し）/ task（期間）/ milestone（節目・◆）。milestone は開始日の列に置き、終了日は空、進捗は 0 にする
- 期間が 31 日までは毎日、60 日までは月曜だけに日付を出し、61 日〜26 週は 1 列 1 週に自動で切り替わる。それより長い計画は planning/gantt-schedule（月単位）を使う
- バーの右には営業日数（土日・祝日・extraHolidays を除く）が出る。期間の根拠がない作業に日付を入れない
- 行は 12 件まで。超える計画は scripts/calendar_pages.py でグループごとにページを分ける
- 依存関係の矢印は描かない。前後関係を見せたい計画は nexus/roadmap を使う
- 計画値と実績を混ぜない。進捗率を入れるときは source に集計時点を書く

### 日次タスクリスト（`daily-agenda`）

![日次タスクリスト](images/slide-templates/daily-agenda.png)

1 行 1 タスクで日付を下方向に並べ、日ごとの担当・期日・状態を一覧で示す

**答える問い**: 日ごとに誰が何をいつまでにやるか

**figures**: `governing_message`, `day_agenda`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 36 字以内 |
| `start` | `string` | ✔ | 10 字以内、8 字以上 |
| `end` | `string` | ✔ | 10 字以内、8 字以上 |
| `items` | `array` (string≤10, string≤24, string≤6, string≤5, string≤9) | ✔ | 1〜11 件 |
| `today` | `string` | — | 10 字以内、既定 `""` |
| `extraHolidays` | `array` (string≤10, string≤10) | — | 最大 20 件、既定 `[]` |
| `source` | `string` | ✔ | 160 字以内 |

使うときの決まり:

- タイトル（結論）は 1 行・全角 36 字まで。2 行になるとカレンダーの見出しに重なる
- 項目は [日付, 内容, 担当, 期日, 状態]。1 行 1 タスクで、同じ日の複数タスクは日付セルが縦に結合される
- 予定のない土日・祝日の連続は 1 行に畳まれ、休日名が添えられる。休日の行も 1 行として数える
- 1 枚は約 11 行まで。超える期間は scripts/calendar_pages.py で週ごとに分割する
- 状態は 完了 / 進行中 / 予定 / 遅延 / 中止（done / doing / todo / late / cancelled も可）。色だけでなく文字でも示される
- 期日の列には時刻か締切を書き、未定は空にする（「—」と表示される）。推測で埋めない
- today を渡すとその日の日付セルが赤で強調される。資料の作成日と揃え、source にも時点を書く

### 週間タイムテーブル（`weekly-timetable`）

![週間タイムテーブル](images/slide-templates/weekly-timetable.png)

曜日の列と時間の行に予定を置き、1 週間のどの時間帯にどこで何があるかを示す

**答える問い**: この週の、何時にどこで何があるか

**figures**: `governing_message`, `week_timetable`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 36 字以内 |
| `week` | `string` | ✔ | 10 字以内、8 字以上 |
| `days` | `integer` | — | 5〜7、既定 `5` |
| `startHour` | `integer` | — | 0〜23、既定 `9` |
| `endHour` | `integer` | — | 1〜24、既定 `18` |
| `events` | `array` (string≤10, string≤5, string≤5, string≤14, string≤10, string≤7) | ✔ | 1〜25 件 |
| `breaks` | `array` (string≤5, string≤5, string≤6) | — | 最大 3 件、既定 `[["12:00", "13:00", "昼休…` |
| `extraHolidays` | `array` (string≤10, string≤10) | — | 最大 7 件、既定 `[]` |
| `source` | `string` | ✔ | 160 字以内 |

使うときの決まり:

- タイトル（結論）は 1 行・全角 36 字まで。2 行になると見出しに重なる
- 予定は [日付, 開始, 終了, 件名, 場所, 分類]。時刻は HH:MM。week にはその週の任意の日付を入れ、月曜始まりの週として描かれる
- 9〜18 時（9 時間）なら 1 時間 ≈ 0.37in。30 分未満の予定は描けないので、時間を丸めずに一覧（daily-agenda）へ回す
- 同じ時間に重なる予定は 2 件まで横に並ぶ。3 件以上重なる週は部屋別・トラック別にページを分ける
- 休憩（breaks、既定は 12:00〜13:00 の昼休憩）は予定のない日だけ灰色の帯で出る。予定のない祝日は休日名で塗られる
- 土日を含める場合は days を 7 にする。列が狭くなり、1 時間の予定は件名だけ、重なる予定の件名は全角 4 字程度で切れる
- 予定であることと、いつ時点の予定かを source に書く

### スプリントカレンダー（`sprint-calendar`）

![スプリントカレンダー](images/slide-templates/sprint-calendar.png)

連続するスプリントを週の行に並べ、祝日で減る稼働日数と計画・レビュー・リリースの日を示す

**答える問い**: 各スプリントの期間・稼働日数・イベント日はいつか

**figures**: `governing_message`, `sprint_calendar`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 36 字以内 |
| `start` | `string` | ✔ | 10 字以内、8 字以上 |
| `lengthDays` | `integer` | — | 7〜14、既定 `14` |
| `sprints` | `array` (string≤6, string≤14, boolean) | ✔ | 1〜8 件 |
| `extraHolidays` | `array` (string≤10, string≤10) | — | 最大 20 件、既定 `[]` |
| `source` | `string` | ✔ | 160 字以内 |

使うときの決まり:

- タイトル（結論）は 1 行・全角 36 字まで。2 行になると見出しに重なる
- スプリントは [番号, ゴール, リリースの有無]。start は最初のスプリントの月曜で、lengthDays（7 か 14）ずつ連続して並ぶ
- 1 枚は 8 週分まで（2 週スプリントなら 4 本、1 週なら 8 本）。それ以上は scripts/calendar_pages.py で分ける
- 稼働日数は平日から祝日と extraHolidays を除いて数える。「休日 -1」は平日に祝日が当たった日数で、ベロシティの見込みを下げる根拠になる
- 計画は最初の稼働日（初日が祝日なら「計画（振替）」）、レビューかリリースは最後の稼働日に自動で置かれる。実際の開催日が違うなら使わない
- ゴールは 1 行・全角 14 字まで。成果として確認できる表現にし、作業名を書かない
- 未来のスプリントは計画であることを source に書く

### 年間カレンダー（`year-at-a-glance`）

![年間カレンダー](images/slide-templates/year-at-a-glance.png)

年度の 12 か月を小さな月カレンダーで並べ、繁忙期・休業・重要日を色と丸で示す

**答える問い**: 年度の中で繁忙期と重要日がどこにあるか

**figures**: `governing_message`, `year_calendar`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 36 字以内 |
| `startMonth` | `string` | ✔ | 7 字以内、6 字以上 |
| `marks` | `array` (string≤10, string≤10, string≤12, string≤4) | ✔ | 1〜20 件 |
| `extraHolidays` | `array` (string≤10, string≤10) | — | 最大 30 件、既定 `[]` |
| `source` | `string` | ✔ | 160 字以内 |

使うときの決まり:

- タイトル（結論）は 1 行・全角 36 字まで。2 行になると月の見出しに重なる
- 印は [開始日, 終了日, ラベル, 種類]。種類は busy（繁忙期・青の面）/ off（休業・赤の面）/ key（重要日・赤丸、終了日は空）
- startMonth に年度の最初の月（例: 2026-04）を入れると 12 か月が並ぶ。範囲外の日付はエラーになる
- 日付は 7pt で、配布資料専用の密度。投影するなら month-calendar を月ごとに使う
- 凡例には種類ごとのラベルが並ぶ。ラベルは短く（全角 6 字程度）、種類ごとに 3 件程度までにする
- 会社休業日の数字も赤くしたい場合は extraHolidays にも入れる。印の off は面を塗るだけ
- 予定であることと、いつ時点の予定かを source に書く

### 期限カウントダウン（`deadline-countdown`）

![期限カウントダウン](images/slide-templates/deadline-countdown.png)

期限までの残り日数を暦日と営業日で示し、今日から期限までをカレンダーに塗る

**答える問い**: 期限まで残り何日（何営業日）で、途中の節目はいつか

**figures**: `governing_message`, `deadline_countdown`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 36 字以内 |
| `label` | `string` | ✔ | 12 字以内、1 字以上 |
| `deadline` | `string` | ✔ | 10 字以内、8 字以上 |
| `today` | `string` | ✔ | 10 字以内、8 字以上 |
| `checkpoints` | `array` (string≤10, string≤12) | — | 最大 3 件、既定 `[]` |
| `extraHolidays` | `array` (string≤10, string≤10) | — | 最大 20 件、既定 `[]` |
| `source` | `string` | ✔ | 160 字以内 |

使うときの決まり:

- タイトル（結論）は 1 行・全角 36 字まで。2 行になると見出しに重なる
- today は資料の基準日で必須。残り日数は today から期限までの暦日、営業日は today から期限前日までの平日から祝日と extraHolidays を除いた日数
- 期限は today の月か翌月にあること。それより先の期限は month-calendar や daily-gantt で見せる
- 節目は [日付, 名前] で 3 件まで。today から期限までの間の日付にする
- label は「本番切替まで」のように、何の期限かが分かる短い言葉にする
- 基準日を過ぎた資料は数字が古くなる。配布時に today を更新し、source にも基準日を書く

### 日次ヒートマップ（`activity-heatmap`）

![日次ヒートマップ](images/slide-templates/activity-heatmap.png)

日ごとの量を週 × 曜日のマスの濃淡で並べ、曜日・時期による偏りと月別の合計を示す

**答える問い**: どの曜日・時期に量が集中しているか

**figures**: `governing_message`, `calendar_heatmap`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 36 字以内 |
| `start` | `string` | ✔ | 10 字以内、8 字以上 |
| `end` | `string` | ✔ | 10 字以内、8 字以上 |
| `values` | `array` (string≤10, number) | ✔ | 7〜371 件 |
| `unit` | `string` | — | 4 字以内、既定 `"件"` |
| `levels` | `integer` | — | 3〜7、既定 `5` |
| `monthly` | `boolean` | — | 既定 `true` |
| `summary` | `boolean` | — | 既定 `true` |
| `extraHolidays` | `array` (string≤10, string≤10) | — | 最大 30 件、既定 `[]` |
| `source` | `string` | ✔ | 160 字以内 |

使うときの決まり:

- タイトル（結論）は 1 行・全角 36 字まで。2 行になると月の見出しに重なる
- 値は [日付, 数値]。期間は 53 週まで。それより長い系列は scripts/calendar_pages.py で 52 週ごとに分ける
- 数値を扱うので source は必須。期間、集計の定義（何を 1 件と数えたか）、単位、データの出どころを書く
- 濃淡はこの期間の値の分位（levels 段階）で決まる相対的な区分で、絶対的な閾値ではない。別の期間の図と色を比べない
- 値のない日は白、0 の日は最も薄い色。欠測と 0 を混ぜない（欠測を 0 で埋めない）
- 祝日・連休に値が低いのは暦の影響で、異常ではない。カードの祝日平均と合わせて読む
- 下のカードは集計値だけを出す。原因や評価はタイトルか本文に分け、相関を因果として書かない

### 当番表（`shift-roster`）

![当番表](images/slide-templates/shift-roster.png)

担当者 × 日のマスに勤務区分を 1 文字と色で置き、日ごとの人数と手薄な日を示す

**答える問い**: 各日に誰が当番で、手薄な日はどこか

**figures**: `governing_message`, `shift_roster`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 36 字以内 |
| `start` | `string` | ✔ | 10 字以内、8 字以上 |
| `end` | `string` | ✔ | 10 字以内、8 字以上 |
| `people` | `array` (string≤6, string≤31) | ✔ | 1〜12 件 |
| `codes` | `array` (string≤1, string≤8, string≤7, boolean) | ✔ | 1〜6 件 |
| `minStaff` | `integer` | — | 0〜12、既定 `0` |
| `extraHolidays` | `array` (string≤10, string≤10) | — | 最大 20 件、既定 `[]` |
| `source` | `string` | ✔ | 160 字以内 |

使うときの決まり:

- タイトル（結論）は 1 行・全角 36 字まで。2 行になると日付の見出しに重なる
- 担当者は [名前, 予定]。予定は期間の 1 日につき 1 文字のコードを並べた文字列（例: 日日夜休…）で、文字数は期間の日数と一致させる
- コードは [文字, 意味, 色, 人数に数えるか]。色は primary / dark / success / danger / info / warning / muted。凡例は自動で付く
- 1 枚は 31 日 × 12 人まで。長い期間やチームは scripts/calendar_pages.py で月ごと・12 人ごとに分ける
- minStaff を入れると、人数に数えるコードの合計がそれを下回る日が赤くなる。必要人数の根拠（SLA・体制表）を source に書く
- 実在の個人名を載せる資料は共有範囲に注意する。社外向けや作例では役割名・仮名にする
- 予定（計画）であることと、いつ時点の当番表かを source に書く。当日の交代は反映されない

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `tree` | `array` | ✔ | 2 件 |
| `insight` | `string` | ✔ | 88 字以内 |
| `source` | `string` | ✔ | 160 字以内 |

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `tree` | `array` | ✔ | 2 件 |
| `insight` | `string` | ✔ | 88 字以内 |
| `source` | `string` | ✔ | 160 字以内 |

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `chain` | `string[]` | ✔ | 3〜6 件、32 字以内 |
| `insight` | `string` | ✔ | 88 字以内 |
| `source` | `string` | ✔ | 160 字以内 |

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `problem` | `string` | ✔ | 20 字以内 |
| `categories` | `array` (string≤8, string[]≤22) | ✔ | 2〜6 件 |
| `insight` | `string` | ✔ | 44 字以内 |
| `source` | `string` | ✔ | 160 字以内 |

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `items` | `array` (string≤10, number) | ✔ | 3〜10 件 |
| `unit` | `string` | — | 6 字以内、既定 `"件"` |
| `insight` | `string` | ✔ | 44 字以内 |
| `source` | `string` | ✔ | 160 字以内 |

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `asis` | `string[]` | ✔ | 2〜4 件、26 字以内 |
| `tobe` | `string[]` | ✔ | 2〜4 件、26 字以内 |
| `gaps` | `array` (string≤14, string≤34) | ✔ | 1〜3 件 |
| `source` | `string` | ✔ | 160 字以内 |

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `steps` | `string[]` | ✔ | 3〜6 件、12 字以内 |
| `pains` | `string[][]` | ✔ | 1〜5 件、30 字以内 |
| `source` | `string` | ✔ | 160 字以内 |

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `political` | `string[]` | ✔ | 1〜4 件、24 字以内 |
| `economic` | `string[]` | ✔ | 1〜4 件、24 字以内 |
| `social` | `string[]` | ✔ | 1〜4 件、24 字以内 |
| `technological` | `string[]` | ✔ | 1〜4 件、24 字以内 |
| `insight` | `string` | ✔ | 44 字以内 |
| `source` | `string` | ✔ | 160 字以内 |

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `rivalry` | `string` | ✔ | 36 字以内 |
| `entrants` | `string` | ✔ | 40 字以内 |
| `substitutes` | `string` | ✔ | 40 字以内 |
| `buyers` | `string` | ✔ | 36 字以内 |
| `suppliers` | `string` | ✔ | 36 字以内 |
| `source` | `string` | ✔ | 160 字以内 |

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `items` | `array` (string≤10, number≤1, number≤1) | ✔ | 2〜8 件 |
| `highlight` | `string[]` | — | 最大 3 件、10 字以内、既定 `[]` |
| `xAxis` | `string[]` | — | 2 件、12 字以内、既定 `["実行が難しい", "実行しやすい"]` |
| `yAxis` | `string[]` | — | 2 件、12 字以内、既定 `["効果小", "効果大"]` |
| `insight` | `string` | ✔ | 44 字以内 |
| `source` | `string` | ✔ | 160 字以内 |

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `lead` | `string` | ✔ | 100 字以内 |
| `headers` | `string[]` | ✔ | 2〜3 件、10 字以内 |
| `rows` | `string[][]` | ✔ | 3〜(print 7 · presentation 4) 件、(print 24 · presentation 16) 字以内 |
| `insight` | `string` | ✔ | (print 90 · presentation 50) 字以内 |
| `insightPoints` | `string[]` | — | 最大 (print 3 · presentation 2) 件、(print 24 · presentation 18) 字以内、既定 `[]` |
| `source` | `string` | ✔ | 170 字以内 |

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `lead` | `string` | ✔ | 100 字以内 |
| `exhibitNumber` | `integer` | — | 1〜99、既定 `1` |
| `exhibitTitle` | `string` | ✔ | 40 字以内 |
| `bars` | `array` (string≤(print 5 · presentation 6), number) | ✔ | 2〜(print 8 · presentation 5) 件 |
| `unit` | `string` | — | 8 字以内、既定 `""` |
| `insight` | `string` | ✔ | (print 90 · presentation 50) 字以内 |
| `insightPoints` | `string[]` | — | 最大 (print 3 · presentation 2) 件、(print 24 · presentation 18) 字以内、既定 `[]` |
| `source` | `string` | ✔ | 170 字以内 |

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `situation` | `string` | ✔ | (print 80 · presentation 48) 字以内 |
| `complication` | `string` | ✔ | (print 80 · presentation 48) 字以内 |
| `resolution` | `string` | ✔ | (print 80 · presentation 48) 字以内 |
| `points` | `string[]` | — | 最大 (print 4 · presentation 3) 件、(print 46 · presentation 28) 字以内、既定 `[]` |
| `source` | `string` | ✔ | 170 字以内 |

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `lead` | `string` | ✔ | 100 字以内 |
| `rationale` | `array` (string≤12, string≤(print 48 · presentation 30)) | ✔ | 3〜(print 4 · presentation 3) 件 |
| `implication` | `string` | ✔ | (print 100 · presentation 60) 字以内 |
| `source` | `string` | ✔ | 170 字以内 |

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `lead` | `string` | ✔ | 100 字以内 |
| `criteria` | `string[]` | ✔ | 3〜(print 5 · presentation 4) 件、8 字以内 |
| `options` | `array` (string≤16, integer[]≤4) | ✔ | 2〜(print 5 · presentation 4) 件 |
| `recommendation` | `string` | ✔ | (print 100 · presentation 60) 字以内 |
| `source` | `string` | ✔ | 170 字以内 |

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `lead` | `string` | ✔ | 100 字以内 |
| `messages` | `string[]` | ✔ | 4〜(print 8 · presentation 5) 件、(print 40 · presentation 26) 字以内 |
| `source` | `string` | ✔ | 170 字以内 |

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `lead` | `string` | ✔ | 100 字以内 |
| `headers` | `string[]` | — | 2 件、12 字以内、既定 `["想定される懸念", "回答（根拠つき）"]` |
| `qa` | `string[][]` | ✔ | 3〜(print 5 · presentation 3) 件、(print 50 · presentation 30) 字以内 |
| `source` | `string` | ✔ | 170 字以内 |

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `lead` | `string` | ✔ | 100 字以内 |
| `exhibitNumber` | `integer` | — | 1〜99、既定 `1` |
| `exhibitTitle` | `string` | ✔ | 30 字以内 |
| `bars` | `array` (string≤(print 5 · presentation 6), number) | ✔ | 2〜(print 6 · presentation 4) 件 |
| `unit` | `string` | — | 8 字以内、既定 `""` |
| `headers` | `string[]` | ✔ | 2〜3 件、8 字以内 |
| `rows` | `string[][]` | ✔ | 3〜(print 5 · presentation 3) 件、(print 16 · presentation 12) 字以内 |
| `implication` | `string` | ✔ | (print 55 · presentation 28) 字以内 |
| `decisions` | `string[][]` | ✔ | 1〜2 件、(print 22 · presentation 16) 字以内 |
| `source` | `string` | ✔ | 170 字以内 |

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `lead` | `string` | ✔ | 100 字以内 |
| `headers` | `string[]` | ✔ | 5 件、8 字以内 |
| `rows` | `string[][]` | ✔ | 3〜(print 7 · presentation 5) 件、(print 9 · presentation 8) 字以内 |
| `source` | `string` | ✔ | 80 字以内 |

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `lead` | `string` | ✔ | 100 字以内 |
| `items` | `array` (string≤8, number, string≤5) | ✔ | 3〜(print 7 · presentation 5) 件 |
| `unit` | `string` | — | 6 字以内、既定 `""` |
| `implication` | `string` | ✔ | (print 100 · presentation 70) 字以内 |
| `source` | `string` | ✔ | 80 字以内 |

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `lead` | `string` | ✔ | 100 字以内 |
| `categories` | `string[]` | ✔ | 2〜4 件、6 字以内 |
| `series` | `array` (string≤5, number[]) | ✔ | 2〜4 件 |
| `breakdown` | `string[][]` | ✔ | 2〜(print 6 · presentation 4) 件、(print 7 · presentation 5) 字以内 |
| `unit` | `string` | — | 6 字以内、既定 `""` |
| `source` | `string` | ✔ | 80 字以内 |

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `lead` | `string` | ✔ | 100 字以内 |
| `labels` | `string[]` | ✔ | 3〜5 件、5 字以内 |
| `series` | `array` (string≤8, number[]) | ✔ | 2〜3 件 |
| `unit` | `string` | — | 6 字以内、既定 `""` |
| `bepValue` | `string` | ✔ | 8 字以内 |
| `bepLabel` | `string` | — | 14 字以内、既定 `"損益分岐点売上高"` |
| `marginValue` | `string` | ✔ | 8 字以内 |
| `marginLabel` | `string` | — | 14 字以内、既定 `"安全余裕率（計画比）"` |
| `source` | `string` | ✔ | 80 字以内 |

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `lead` | `string` | ✔ | 100 字以内 |
| `labels` | `string[]` | ✔ | 3〜6 件、6 字以内 |
| `series` | `array` (string≤8, number[]) | ✔ | 2〜3 件 |
| `unit` | `string` | — | 6 字以内、既定 `""` |
| `assumptions` | `string[][]` | ✔ | 2〜3 件、(print 12 · presentation 9) 字以内 |
| `source` | `string` | ✔ | 80 字以内 |
| `yMax` | `number` | — | 0 以上、既定 `null` |

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `lead` | `string` | ✔ | 100 字以内 |
| `roiValue` | `string` | ✔ | 8 字以内 |
| `roiLabel` | `string` | — | 14 字以内、既定 `"投資回収率（累計）"` |
| `paybackValue` | `string` | ✔ | 8 字以内 |
| `paybackLabel` | `string` | — | 14 字以内、既定 `"投資回収期間"` |
| `npvValue` | `string` | ✔ | 8 字以内 |
| `npvLabel` | `string` | — | 14 字以内、既定 `"NPV（正味現在価値）"` |
| `labels` | `string[]` | ✔ | 3〜6 件、6 字以内 |
| `series` | `array` (string≤8, number[]) | ✔ | 2〜3 件 |
| `unit` | `string` | — | 6 字以内、既定 `""` |
| `source` | `string` | ✔ | 80 字以内 |

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `lead` | `string` | ✔ | 100 字以内 |
| `risks` | `string[][]` | ✔ | 2〜(print 5 · presentation 4) 件、(print 22 · presentation 16) 字以内 |
| `decisionRule` | `string` | ✔ | (print 110 · presentation 70) 字以内 |
| `source` | `string` | ✔ | 80 字以内 |

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

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `lead` | `string` | ✔ | 100 字以内 |
| `tree` | `tuple` (string≤18, array) | ✔ | — |
| `roles` | `string[][]` | ✔ | 2〜(print 6 · presentation 4) 件、(print 15 · presentation 12) 字以内 |
| `notes` | `string[]` | — | 最大 2 件、60 字以内、既定 `[]` |
| `source` | `string` | ✔ | 80 字以内 |

使うときの決まり:

- タイトルは全角 30 字前後・1 行に収める。2 行に折り返すと直下のリード文と重なる
- 全社の組織図ではなく、この事業の推進体制を書く。関与しない部署は載せない
- 人数は cost-structure の人件費と一致させる。体制図で増員し、費用計画で増やし忘れない
- 専任と兼務を必ず区別して書く。兼務比率が高い体制は実行可能性の指摘対象になる
- 深さ 4 以上・葉 8 超は文字が潰れる。部門ごとにスライドを分ける
- ノードのラベルは「役割\n人数」の 2 行にすると読みやすい。個人名は社外提出時に伏せる
- 立ち上げ期と拡大期で体制が変わるなら、時期を明記して 2 枚に分ける

<a id="nexus"></a>

## Nexus レポートパック（`nexus`）

nexus-architect の実行結果をスライドにするページ群。どこまで分析したか・何が見つかったか・何を決めたか・何が未回答かを、拠って立つ根拠つきで示す。

### パイプラインのカバレッジ（`pipeline-coverage`）

![パイプラインのカバレッジ](images/slide-templates/pipeline-coverage.png)

この資料がどこまでの分析に基づくか（完了・実行中・未着手）を最初に示す

**答える問い**: この提案・報告は、どこまで終わった分析に基づいているのか

**figures**: `governing_message`, `lead_in`, `hbars`, `table`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**densities**: print / presentation（既定 print）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | (print 38 · presentation 30) 字以内 |
| `basis` | `string` | ✔ | (print 150 · presentation 110) 字以内 |
| `counts` | `array` (string≤12, number, string≤8) | ✔ | 2〜5 件 |
| `headers` | `string[]` | ✔ | 3 件、14 字以内 |
| `groups` | `string[][]` | ✔ | 2〜(print 7 · presentation 5) 件、(print 22 · presentation 16) 字以内 |
| `source` | `string` | ✔ | 170 字以内 |

使うときの決まり:

- デッキの 2 枚目に必ず置く。未完了のまま説明する資料は、前提を先に開示してからでないと読み手が誤解する
- counts はフェーズ数の実数。レポートの枚数や作業時間に読み替えない
- 未着手フェーズを『対象外』と書き換えない。skipped（意図的に飛ばした）と pending（まだ）は別物
- source には収集時刻（asOf）を必ず入れる。パイプラインは動き続けるので、資料は常にある時点のスナップショット

### フェーズ要約（章扉）（`phase-digest`）

![フェーズ要約（章扉）](images/slide-templates/phase-digest.png)

1 フェーズが何を明らかにしたかを、そのフェーズ自身の要約と出力ファイルで示す

**答える問い**: このフェーズは何を明らかにし、どのレポートに書いたのか

**figures**: `governing_message`, `lead_in`, `so_what`, `table`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**densities**: print / presentation（既定 print）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | (print 38 · presentation 30) 字以内 |
| `phase` | `string` | ✔ | 60 字以内 |
| `finding` | `string` | ✔ | (print 200 · presentation 150) 字以内 |
| `headers` | `string[]` | ✔ | 2 件、16 字以内 |
| `outputs` | `array` (string≤42, string≤(print 46 · presentation 34)) | ✔ | 1〜3 件 |
| `source` | `string` | ✔ | 170 字以内 |

使うときの決まり:

- summary はフェーズが自分で記録した要約（pipeline-progress.json の summary）を土台にする。読み手向けに言い換えるのはよいが、新しい主張を足さない
- outputs は実在するファイルだけ。宣言されているが書かれていないものは open-questions 側に回す
- 章扉なので結論は 1 つ。複数の発見があるなら後続ページに分ける

### 技術スタックの棚卸し（`stack-inventory`）

![技術スタックの棚卸し](images/slide-templates/stack-inventory.png)

現行システムが何でできているかを層で示し、版と制約を併記する

**答える問い**: このシステムは何の上に建っているのか

**figures**: `governing_message`, `lead_in`, `layers`, `table`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**densities**: print / presentation（既定 print）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | (print 38 · presentation 30) 字以内 |
| `lead` | `string` | ✔ | (print 140 · presentation 100) 字以内 |
| `layers` | `array` (string≤22, string≤(print 52 · presentation 40)) | ✔ | 3〜(print 6 · presentation 5) 件 |
| `facts` | `string[][]` | ✔ | 2〜(print 7 · presentation 5) 件、(print 24 · presentation 18) 字以内 |
| `source` | `string` | ✔ | 170 字以内 |

使うときの決まり:

- 層は実際に動いているものだけ。設定ファイルに書いてあるが呼ばれていないものは note で『宣言のみ』と明示する
- 版は必ず書く。サポート期限や既知脆弱性の判断は版がないとできない
- 評価（良い・悪い）はこのページに書かない。課題は issue-register へ

### 課題・負債・指摘の一覧（`issue-register`）

![課題・負債・指摘の一覧](images/slide-templates/issue-register.png)

検出された課題を重大度の分布と個票で示す

**答える問い**: 何が、どれくらいまずい状態で見つかっているのか

**figures**: `governing_message`, `lead_in`, `hbars`, `table`, `source_note`  
**推論レベル**: 診断（要因・構造の特定）  
**densities**: print / presentation（既定 print）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | (print 38 · presentation 30) 字以内 |
| `lead` | `string` | ✔ | (print 140 · presentation 100) 字以内 |
| `counts` | `array` (string≤12, number, string≤8) | ✔ | 2〜4 件 |
| `issues` | `string[][]` | ✔ | 2〜(print 7 · presentation 5) 件、(print 24 · presentation 18) 字以内 |
| `source` | `string` | ✔ | 170 字以内 |

使うときの決まり:

- 重大度はレポートが付けた値をそのまま使う。デッキ側で上げ下げしない
- counts の合計と issues の総数は一致させる（抜粋するなら lead でそう書く）
- 打ち手はこのページに書かない。ここは『何が見つかったか』まで
- 個票には根拠（ファイル名・行・エンドポイント）を必ず残す

### 評価スコア（単一指標）（`score-card`）

![評価スコア（単一指標）](images/slide-templates/score-card.png)

成熟度・準備度などの単一スコアを帯域つきで示し、内訳を並べる

**答える問い**: この評価軸で、いまどの水準にいるのか

**figures**: `governing_message`, `lead_in`, `metric`, `hbars`, `source_note`  
**推論レベル**: 診断（要因・構造の特定）  
**densities**: print / presentation（既定 print）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | (print 38 · presentation 30) 字以内 |
| `score` | `string` | ✔ | 10 字以内 |
| `scoreCaption` | `string` | ✔ | (print 48 · presentation 34) 字以内 |
| `dimensions` | `array` (string≤18, number, string≤10) | ✔ | 2〜(print 5 · presentation 4) 件 |
| `verdict` | `string` | ✔ | (print 150 · presentation 110) 字以内 |
| `source` | `string` | ✔ | 170 字以内 |
| `scale` | `number` | — | 0.1 以上、既定 `5` |

使うときの決まり:

- スコアは必ず帯域（何点なら何を意味するか）と一緒に出す。数字だけでは判断できない
- 内訳の軸名と重みはレポートの定義をそのまま使う。デッキ側で足したり丸めたりしない
- verdict は数字から言えることだけ。改善策は roadmap / decision-record へ
- 棒の長さは scale（既定 5）を満点として描く。別スケールの指標を載せるときは scale を必ず合わせる

### スコアの内訳（対象 × 観点）（`score-breakdown`）

![スコアの内訳（対象 × 観点）](images/slide-templates/score-breakdown.png)

モジュールや観点ごとのスコアを面で比較し、どこが足を引っ張っているかを示す

**答える問い**: 低いのはどの対象の、どの観点なのか

**figures**: `governing_message`, `lead_in`, `rating_matrix`, `so_what`, `source_note`  
**推論レベル**: 診断（要因・構造の特定）  
**densities**: print / presentation（既定 print）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | (print 38 · presentation 30) 字以内 |
| `lead` | `string` | ✔ | (print 140 · presentation 100) 字以内 |
| `columns` | `string[]` | ✔ | 2〜(print 6 · presentation 5) 件、14 字以内 |
| `rows` | `array` (string≤20, integer[]≤5) | ✔ | 2〜(print 5 · presentation 4) 件 |
| `verdict` | `string` | ✔ | (print 100 · presentation 75) 字以内 |
| `source` | `string` | ✔ | 170 字以内 |

使うときの決まり:

- 行と列の順序はレポートに合わせる。スコア順に並べ替えるなら、そう明記する
- 点は 0〜levels の整数。小数のスコアを丸めて載せる場合は source に丸め方を書く
- 空白（未評価）と 0 点を同じに見せない。未評価の行は載せないか、行ラベルに明記する

### コンテキストマップ（`context-map`）

![コンテキストマップ](images/slide-templates/context-map.png)

中心となるコンテキストと周辺の関係を、関係種別つきで示す

**答える問い**: どの境界が中心で、周辺とはどんな関係にあるのか

**figures**: `governing_message`, `lead_in`, `hub`, `table`, `source_note`  
**推論レベル**: 戦略（評価と方向づけ）  
**densities**: print / presentation（既定 print）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | (print 38 · presentation 30) 字以内 |
| `lead` | `string` | ✔ | (print 140 · presentation 100) 字以内 |
| `center` | `string` | ✔ | 22 字以内 |
| `contexts` | `string[]` | ✔ | 3〜6 件、24 字以内 |
| `relations` | `string[][]` | ✔ | 2〜(print 6 · presentation 4) 件、(print 22 · presentation 18) 字以内 |
| `source` | `string` | ✔ | 170 字以内 |

使うときの決まり:

- 関係種別（Shared Kernel / Conformist / Separate Ways など）はレポートの用語をそのまま使う
- As-Is と To-Be を 1 枚に混ぜない。どちらの図かを title で明示する
- 図で表せない多対多の関係は表側に逃がす。線を増やして読めなくしない
- 元の mermaid をそのまま貼りたい場合は architecture-exhibit を使う

### 構成図（画像＋読み取りポイント）（`architecture-exhibit`）

レポートの構造図をそのまま図表として貼り、読み取るべき点を 3 つ添える

**答える問い**: この構成図から何を読み取ればよいのか

**figures**: `governing_message`, `exhibit_frame`, `image`, `so_what`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**densities**: print / presentation（既定 print）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | (print 38 · presentation 30) 字以内 |
| `exhibitNumber` | `string` | ✔ | 6 字以内 |
| `exhibitTitle` | `string` | ✔ | 44 字以内 |
| `image` | `string` | ✔ | 200 字以内 |
| `lead` | `string` | ✔ | (print 90 · presentation 70) 字以内 |
| `readings` | `string[]` | ✔ | 2〜3 件、(print 34 · presentation 26) 字以内 |
| `source` | `string` | ✔ | 170 字以内 |

使うときの決まり:

- 画像は scripts/mermaid_export.py / drawio_export.py / html_shot.py で書き出したものを使い、生成後に Read で目視確認する
- 画像枠は約 2:1。極端に縦長・横長の図は余白だらけになるので、分割するかネイティブ図に描き直す
- スライドサイズで読めない図は貼らない。読めないなら分割するか、ネイティブ図に描き直す
- readings は図に描かれていることだけ。図にない主張を 3 点に混ぜない
- 図表番号は本文から参照できるように連番で管理する

### 決定と根拠（ADR）（`decision-record`）

![決定と根拠（ADR）](images/slide-templates/decision-record.png)

検討した選択肢と採否、そして決定理由を 1 枚に残す

**答える問い**: なぜこの方式を選んだのか、他は何を理由に落としたのか

**figures**: `governing_message`, `lead_in`, `table`, `so_what`, `source_note`  
**推論レベル**: 戦略（評価と方向づけ）  
**densities**: print / presentation（既定 print）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | (print 38 · presentation 30) 字以内 |
| `question` | `string` | ✔ | (print 140 · presentation 100) 字以内 |
| `options` | `string[][]` | ✔ | 2〜4 件、(print 34 · presentation 26) 字以内 |
| `decision` | `string` | ✔ | (print 150 · presentation 110) 字以内 |
| `source` | `string` | ✔ | 170 字以内 |

使うときの決まり:

- 落とした選択肢を必ず 1 つ以上載せる。採用案だけの表は決定記録ではなく宣伝になる
- 採否理由は評価軸（性能・整合性・運用・コスト）に紐づける。好みで書かない
- 決定が未確定なら『未決』と書く。決まったように見せない
- 決定の影響範囲（どのフェーズがこの決定に依存するか）を decision に含める

### 移行・実装ロードマップ（`roadmap`）

![移行・実装ロードマップ](images/slide-templates/roadmap.png)

段取りと期間、依存関係を帯で示す

**答える問い**: 何を、どの順で、どれくらいの期間でやるのか

**figures**: `governing_message`, `lead_in`, `gantt`, `source_note`  
**推論レベル**: 戦略（評価と方向づけ）  
**densities**: print / presentation（既定 print）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | (print 38 · presentation 30) 字以内 |
| `lead` | `string` | ✔ | (print 140 · presentation 100) 字以内 |
| `columns` | `string[]` | ✔ | 3〜(print 8 · presentation 6) 件、10 字以内 |
| `rows` | `array` (string≤(print 24 · presentation 18), number, number, string≤18) | ✔ | 2〜(print 7 · presentation 5) 件 |
| `source` | `string` | ✔ | 170 字以内 |

使うときの決まり:

- 期間の根拠がないなら期間を書かない。相対順序だけの図にする
- 並行して走る帯は、本当に並行できる（依存がない）ものだけにする
- マイルストーン（start == end）は意思決定点に使う。作業には使わない
- 未着手フェーズに依存する工程は、その旨を lead に書く

### ペルソナと体験の詰まり（`persona-journey`）

![ペルソナと体験の詰まり](images/slide-templates/persona-journey.png)

対象ユーザーの体験を時系列で並べ、どこで詰まるかを示す

**答える問い**: 誰が、どの体験の、どこで詰まっているのか

**figures**: `governing_message`, `lead_in`, `journey`, `cards`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**densities**: print / presentation（既定 print）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | (print 38 · presentation 30) 字以内 |
| `persona` | `string` | ✔ | (print 140 · presentation 100) 字以内 |
| `milestones` | `array` (string≤14, string≤(print 34 · presentation 24)) | ✔ | 3〜5 件 |
| `pains` | `array` (string≤18, string≤(print 50 · presentation 38)) | ✔ | 2〜3 件 |
| `source` | `string` | ✔ | 170 字以内 |

使うときの決まり:

- ペルソナの属性は調査で確認できたものだけ。年齢・年収などを埋めるために創作しない
- 痛みは観察された事実（発言・行動・数値）に紐づける。推測なら『仮説』と明記する
- 解決策をこのページに書かない。ここは現状の体験まで

### 画面フロー（UI モック 3 枚）（`ui-mock-flow`）

ドメインストーリーの順に並べた画面モックで、体験の流れを示す

**答える問い**: この業務は、どの画面をどの順に通るのか

**figures**: `governing_message`, `lead_in`, `image`, `cards`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**densities**: print / presentation（既定 print）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | (print 38 · presentation 30) 字以内 |
| `story` | `string` | ✔ | (print 140 · presentation 100) 字以内 |
| `shot1` | `string` | ✔ | 200 字以内 |
| `shot2` | `string` | ✔ | 200 字以内 |
| `shot3` | `string` | ✔ | 200 字以内 |
| `steps` | `array` (string≤16, string≤(print 44 · presentation 34)) | ✔ | 3 件 |
| `source` | `string` | ✔ | 170 字以内 |

使うときの決まり:

- モックはストーリーの順（{STORY}-NN-{slug}.html の NN 順）に並べる。見栄えで順序を変えない
- 画像は scripts/html_shot.py で撮り、Read で目視確認してから貼る（スタイルが当たらなくても撮影は成功する）
- モックは仕様であって実装ではない。『実装済み』と読める書き方をしない
- 3 枚に収まらないフローは、この枚数で切れる単位に分けて複数ページにする

### 画面詳細（UI モック 1 枚）（`ui-mock-detail`）

1 画面のモックを大きく見せ、注目点と仕様を並べる

**答える問い**: この画面で何が決まっているのか

**figures**: `governing_message`, `lead_in`, `image`, `table`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**densities**: print / presentation（既定 print）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | (print 38 · presentation 30) 字以内 |
| `screen` | `string` | ✔ | (print 140 · presentation 100) 字以内 |
| `shot` | `string` | ✔ | 200 字以内 |
| `notes` | `string[][]` | ✔ | 2〜(print 6 · presentation 4) 件、(print 18 · presentation 14) 字以内 |
| `source` | `string` | ✔ | 170 字以内 |

使うときの決まり:

- 注目点は画面上に見えていることだけ。裏の処理仕様はこのページに書かない
- 画像は scripts/html_shot.py で撮り、Read で目視確認してから貼る
- 未確定の要素は表側に『未確定』と書く。モックに描いてあることを確定事項として説明しない

### 未回答の問いと次アクション（`open-questions`）

![未回答の問いと次アクション](images/slide-templates/open-questions.png)

まだ埋まっていない前提・未着手フェーズを、誰がどう埋めるかと一緒に示す

**答える問い**: この資料でまだ答えられていないことは何で、どうすれば埋まるのか

**figures**: `governing_message`, `lead_in`, `table`, `cards`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**densities**: print / presentation（既定 print）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | (print 38 · presentation 30) 字以内 |
| `lead` | `string` | ✔ | (print 140 · presentation 100) 字以内 |
| `headers` | `string[]` | ✔ | 3 件、16 字以内 |
| `questions` | `string[][]` | ✔ | 2〜(print 5 · presentation 4) 件、(print 36 · presentation 28) 字以内 |
| `nextSteps` | `array` (string≤18, string≤(print 50 · presentation 38)) | ✔ | 2〜3 件 |
| `source` | `string` | ✔ | 170 字以内 |

使うときの決まり:

- 推測で埋めた項目をここから消さない。埋めていないから未回答なのであって、書けることがないわけではない
- 各行に『誰が / どのコマンドで』埋まるかを必ず書く。宿題の一覧で終わらせない
- 未着手フェーズ由来の未回答と、レポートが明示した open question を混ぜない（source で区別する）
- 部分実行のデッキでは最終ページに必ず置く

### 境界づけられたコンテキスト（`bounded-context-canvas`）

![境界づけられたコンテキスト](images/slide-templates/bounded-context-canvas.png)

1 つの境界づけられたコンテキストを 9 区画のキャンバスで示し、担う責務と境界の外側を確定させる

**答える問い**: このコンテキストは何を担い、どこまでが境界か

**figures**: `governing_message`, `lead_in`, `cards`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**densities**: print / presentation（既定 print）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | (print 38 · presentation 30) 字以内 |
| `lead` | `string` | ✔ | (print 140 · presentation 100) 字以内 |
| `purpose` | `string` | ✔ | (print 54 · presentation 38) 字以内 |
| `classification` | `string` | ✔ | (print 54 · presentation 38) 字以内 |
| `evolution` | `string` | ✔ | (print 54 · presentation 38) 字以内 |
| `domainRoles` | `string` | ✔ | (print 54 · presentation 38) 字以内 |
| `inbound` | `string` | ✔ | (print 54 · presentation 38) 字以内 |
| `outbound` | `string` | ✔ | (print 54 · presentation 38) 字以内 |
| `language` | `string` | ✔ | (print 54 · presentation 38) 字以内 |
| `decisions` | `string` | ✔ | (print 54 · presentation 38) 字以内 |
| `assumptions` | `string` | ✔ | (print 54 · presentation 38) 字以内 |
| `source` | `string` | ✔ | 170 字以内 |

使うときの決まり:

- Core / Supporting / Generic の区分はレポートの記述をそのまま使う。スライド上で格上げ・格下げしない
- 未確定は『前提と未解決』に残す。空欄にすると確定済みに見える
- 受信・発信には相手のコンテキスト名を必ず書く。パターン名（ACL・OHS）だけでは関係が復元できない
- 1 ページ 1 コンテキスト。複数を並べたくなったら context-map を使う

### 状態×イベント判定マトリクス（`state-machine-matrix`）

![状態×イベント判定マトリクス](images/slide-templates/state-machine-matrix.png)

集約の状態とイベントの全組み合わせについて、受け付けるか拒否するかの判定を 1 枚で示す

**答える問い**: どの状態でどのイベントを受け付け、どれを拒否するのか

**figures**: `governing_message`, `lead_in`, `table`, `cards`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**densities**: print / presentation（既定 print）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | (print 38 · presentation 30) 字以内 |
| `lead` | `string` | ✔ | (print 140 · presentation 100) 字以内 |
| `headers` | `string[]` | ✔ | 3〜6 件、14 字以内 |
| `rows` | `string[][]` | ✔ | 2〜(print 5 · presentation 4) 件、12 字以内 |
| `notes` | `array` (string≤18, string≤(print 50 · presentation 38)) | ✔ | 2 件 |
| `source` | `string` | ✔ | 170 字以内 |

使うときの決まり:

- 判定は allow / reject / ignore / defer の 4 語だけを使い、レポートの語をそのまま持ち込む
- 空セルを作らない。全セルに判定があることがこの表の価値で、空欄は『未検討』と区別できない
- 状態またはイベントが上限を超えるときはページを分け、分けたことを source に書く
- 遷移の効果（Effect）や事後条件はこの表では表せない。必要なら別ページに出す

### 品質ゲート判定（`gate-verdict`）

![品質ゲート判定](images/slide-templates/gate-verdict.png)

レビューの総合判定と観点別の加重スコア、優先度別の残件を 1 枚にまとめる

**答える問い**: 品質ゲートは通ったのか、通っていないなら何が残っているのか

**figures**: `governing_message`, `lead_in`, `metric`, `hbars`, `table`, `so_what`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**densities**: print / presentation（既定 print）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | (print 38 · presentation 30) 字以内 |
| `lead` | `string` | ✔ | (print 140 · presentation 100) 字以内 |
| `verdict` | `string` | ✔ | 22 字以内 |
| `score` | `string` | ✔ | 24 字以内 |
| `perspectives` | `array` (string≤14, number≤5, string≤8) | ✔ | 3〜(print 5 · presentation 4) 件 |
| `headers` | `string[]` | ✔ | 3 件、12 字以内 |
| `priorities` | `string[][]` | ✔ | 2〜4 件、(print 30 · presentation 22) 字以内 |
| `insight` | `string` | ✔ | (print 110 · presentation 80) 字以内 |
| `source` | `string` | ✔ | 170 字以内 |

使うときの決まり:

- CONDITIONAL_PASS を PASS と書かない。条件付き合格は条件が残っている状態
- 加重スコアは review-registry.json の重みで算出された値をそのまま載せる。スライド上で再計算しない
- P0 が 0 件でないうちは『合格』と要約しない
- 観点を上限まで絞ったときは、載せなかった観点を source に明記する

### Example Mapping（規則・例・未決）（`example-map-wall`）

![Example Mapping（規則・例・未決）](images/slide-templates/example-map-wall.png)

1 つの機能について、守るべき規則と確かめる具体例、決まらなかった問いを分けて示す

**答える問い**: この機能はどの規則で動き、どの例で確かめ、何が未決なのか

**figures**: `governing_message`, `lead_in`, `table`, `cards`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**densities**: print / presentation（既定 print）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | (print 38 · presentation 30) 字以内 |
| `lead` | `string` | ✔ | (print 140 · presentation 100) 字以内 |
| `rules` | `string[][]` | ✔ | 2〜(print 4 · presentation 3) 件、(print 30 · presentation 22) 字以内 |
| `examples` | `string[][]` | ✔ | 2〜(print 4 · presentation 3) 件、(print 24 · presentation 18) 字以内 |
| `questions` | `array` (string≤18, string≤(print 46 · presentation 34)) | ✔ | 2 件 |
| `source` | `string` | ✔ | 170 字以内 |

使うときの決まり:

- 規則と例を混ぜない。規則は『常に成り立つこと』、例は『それを確かめる 1 ケース』
- 肯定例だけを載せない。境界の外側を示す否定例が 1 つ以上ないと、規則は確かめられていない
- 未決の問いを落とさない。決まらなかったことを消すと、決まったように見える
- 規則が上限を超える機能は分割の検討対象。載せきれなかった規則の件数を source に書く

### 集約の境界と不変条件（`aggregate-canvas`）

![集約の境界と不変条件](images/slide-templates/aggregate-canvas.png)

1 つの集約が含む構成要素と、守り続ける不変条件を、確かめる例と一緒に示す

**答える問い**: この集約はどこまでを含み、どの不変条件を守るのか

**figures**: `governing_message`, `lead_in`, `table`, `cards`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**densities**: print / presentation（既定 print）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | (print 38 · presentation 30) 字以内 |
| `lead` | `string` | ✔ | (print 140 · presentation 100) 字以内 |
| `members` | `string[][]` | ✔ | 2〜(print 4 · presentation 3) 件、(print 22 · presentation 16) 字以内 |
| `invariants` | `string[][]` | ✔ | 2〜(print 4 · presentation 3) 件、(print 24 · presentation 18) 字以内 |
| `examples` | `array` (string≤18, string≤(print 46 · presentation 34)) | ✔ | 2 件 |
| `source` | `string` | ✔ | 170 字以内 |

使うときの決まり:

- 境界の外にあるものを構成要素に含めない。参照だけなら種別に『参照』と書く
- 不変条件は『常に真であること』だけを書く。手順や業務ルールの説明はここに置かない
- 違反する操作の欄を空にしない。何が破るのか分からない不変条件は検証できない
- 1 ページ 1 集約。集約間の関係は context-map か state-machine-matrix で示す

### 画面×UX 観点ヒートマップ（`ux-heatmap`）

![画面×UX 観点ヒートマップ](images/slide-templates/ux-heatmap.png)

UX 評価の指摘が、どの画面のどの観点に集中しているかを 1 枚で示す

**答える問い**: どの画面のどの観点に指摘が集中しているのか

**figures**: `governing_message`, `lead_in`, `rating_matrix`, `metric`, `so_what`, `source_note`  
**推論レベル**: 診断（要因・構造の特定）  
**densities**: print / presentation（既定 print）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | (print 38 · presentation 30) 字以内 |
| `lead` | `string` | ✔ | (print 140 · presentation 100) 字以内 |
| `axes` | `string[]` | ✔ | 3〜5 件、10 字以内 |
| `screens` | `array` (string≤16, integer[]≤4) | ✔ | 2〜(print 5 · presentation 4) 件 |
| `uxi` | `string` | ✔ | 12 字以内 |
| `band` | `string` | ✔ | 22 字以内 |
| `insight` | `string` | ✔ | (print 110 · presentation 80) 字以内 |
| `source` | `string` | ✔ | 170 字以内 |

使うときの決まり:

- ドットの数は指摘の件数であって重大度ではない。重大度は issue-register で別に示す
- UXI とバンドは ux-evaluation.json の値をそのまま使う。スライド上で再計算しない
- 指摘 0 件の画面を表から落とさない。空白のセルこそが『調べて問題がなかった』の記録
- runtime 計測でない評価では、体感速度に関する観点を載せない

### 環境パリティ（同一と差異）（`env-parity-matrix`）

![環境パリティ（同一と差異）](images/slide-templates/env-parity-matrix.png)

複数環境のうち何を同一に保ち、何を意図的に変えているかを、理由と一緒に示す

**答える問い**: 環境ごとに何が同一で、どこが意図的に違うのか

**figures**: `governing_message`, `lead_in`, `table`, `cards`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**densities**: print / presentation（既定 print）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | (print 38 · presentation 30) 字以内 |
| `lead` | `string` | ✔ | (print 140 · presentation 100) 字以内 |
| `headers` | `string[]` | ✔ | 3〜5 件、12 字以内 |
| `rows` | `string[][]` | ✔ | 2〜(print 4 · presentation 3) 件、(print 22 · presentation 16) 字以内 |
| `identical` | `array` (string≤18, string≤(print 46 · presentation 34)) | ✔ | 2 件 |
| `source` | `string` | ✔ | 170 字以内 |

使うときの決まり:

- 差異には必ず理由を書く。理由のない差異は差異ではなく、まだ直していない不整合
- 『同一に保つもの』を空にしない。何も保証していない環境間の比較は意味を持たない
- 環境が上限を超えるときは列を分け、分けたことを source に書く
- 本番だけ未確認の項目を『同一』側に書かない。未確認は差異側に理由付きで残す

<a id="hearing"></a>

## ヒアリングパック（`hearing`）

伝えるためではなく**集めるため**のページ群。うかがいたいことの議題、こちらの理解を出して訂正してもらうページ、その場で記入してもらう欄、イベント用の選択、回答先の提示までを 1 枚ずつにしている。

### 本日うかがいたいこと（`hearing-agenda`）

![本日うかがいたいこと](images/slide-templates/hearing-agenda.png)

空いている論点を、なぜうかがうのかと一緒に議題として先に出す 1 枚

**答える問い**: この打ち合わせで何を教えてもらう必要があるのか

**figures**: `governing_message`, `lead_in`, `table`, `so_what`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `lead` | `string` | ✔ | 100 字以内 |
| `items` | `string[][]` | ✔ | 3〜5 件、40 字以内 |
| `ask` | `string` | ✔ | 60 字以内 |
| `source` | `string` | ✔ | 160 字以内 |

使うときの決まり:

- **顧客提示用**。個人の影響力・賛否・社内政治・競合の弱点を書かない
- 「なぜうかがうのか」を書けない項目は載せない。質問は量ではなく順序で決まる
- 空欄をこちらの推測で埋めた状態で持ち込まない。空いているから聞く
- 5 項目まで。1 回の打ち合わせで返せる量を超えない

### 理解の確認（違っていたら教えてください）（`hypothesis-check`）

![理解の確認（違っていたら教えてください）](images/slide-templates/hypothesis-check.png)

こちらの理解を仮説として出し、違っている点を顧客に訂正してもらう 1 枚

**答える問い**: 我々の理解のどこが違っているのか

**figures**: `governing_message`, `lead_in`, `cards`, `so_what`, `source_note`  
**推論レベル**: 診断（要因・構造の特定）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `lead` | `string` | ✔ | 100 字以内 |
| `items` | `array` (string≤16, string≤68) | ✔ | 2〜3 件 |
| `ask` | `string` | ✔ | 100 字以内 |
| `source` | `string` | ✔ | 160 字以内 |

使うときの決まり:

- **顧客提示用**。個人の影響力・賛否・社内政治・競合の弱点を書かない
- **断定しない。** 確度が `推定` の行だけをここに出す。`確認済` を並べても確認にならない
- 訂正してもらうのが目的。最後は必ず「違っていたら教えてください」で終える
- 出典のない数値を載せない

### その場でご記入いただく欄（`fill-in-sheet`）

![その場でご記入いただく欄](images/slide-templates/fill-in-sheet.png)

対面・画面共有・印刷で、その場で書き込んでもらうための記入欄

**答える問い**: この場で埋めてもらいたい項目は何か

**figures**: `governing_message`, `lead_in`, `table`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `lead` | `string` | ✔ | 100 字以内 |
| `items` | `string[][]` | ✔ | 3〜6 件、44 字以内 |
| `source` | `string` | ✔ | 160 字以内 |

使うときの決まり:

- **顧客提示用**。内部の判断（確度・出典・製品適合）を載せない
- 記入欄は空のまま出す。**こちらの推測を薄く入れて「確認してください」にしない**
- 6 項目まで。書く時間が取れる量にする
- その場で答えられない項目は、持ち帰り先（誰が答えられるか）を一緒に聞く

### 当てはまるものはありますか（イベント用）（`event-poll`）

![当てはまるものはありますか（イベント用）](images/slide-templates/event-poll.png)

セミナー・登壇で、聴衆にどの状況に当てはまるかを選んでもらう 1 枚

**答える問い**: この聴衆はどの状況にいるのか

**figures**: `governing_message`, `lead_in`, `cards`, `so_what`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `lead` | `string` | ✔ | 100 字以内 |
| `items` | `array` (string≤8, string≤56) | ✔ | 3〜4 件 |
| `ask` | `string` | ✔ | 100 字以内 |
| `source` | `string` | ✔ | 160 字以内 |

使うときの決まり:

- **顧客提示用・不特定多数向け**。特定の企業や個人が分かる書き方をしない
- 選択肢は買い手の状況で書く。**製品名で選ばせない**（それは製品紹介であって収集ではない）
- 選んだ結果は型として集計する。誰が選んだかを資料に残さない
- 回答を求めるなら、その場で何が返るのかも言う（資料を送る、個別に相談に乗る等）

### 回答のお願いと次の一歩（`collect-cta`）

![回答のお願いと次の一歩](images/slide-templates/collect-cta.png)

どこに何を返してもらうか、返すと何が起きるかを示して回答を集める 1 枚

**答える問い**: 回答は誰が、どこに、いつまでに返すのか

**figures**: `governing_message`, `lead_in`, `flow`, `so_what`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `lead` | `string` | ✔ | 100 字以内 |
| `steps` | `array` | ✔ | 2〜4 件 |
| `where` | `string` | ✔ | 120 字以内 |
| `source` | `string` | ✔ | 160 字以内 |

使うときの決まり:

- **顧客提示用**。回答先の URL は、渡してよい相手の範囲を確認してから載せる
- **返したら何が起きるかを書く。** 集めるだけで返さないと、次から埋まらなくなる
- 期限と担当を書く。どちらも無い依頼は動かない

### 回答フォーム（QR）（`collect-qr`）

![回答フォーム（QR）](images/slide-templates/collect-qr.png)

回答先の QR を大きく出す 1 枚。イベントの最後や、対面での持ち帰り依頼に使う

**答える問い**: その場で回答するにはどこへ行けばよいのか

**figures**: `governing_message`, `lead_in`, `image`, `so_what`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `lead` | `string` | ✔ | 100 字以内 |
| `qr` | `string` | ✔ | 400 字以内 |
| `where` | `string` | ✔ | 120 字以内 |
| `source` | `string` | ✔ | 160 字以内 |

使うときの決まり:

- **顧客提示用**。QR の飛び先が誰に見えるのかを、貼る前に確認する
- **URL を文字でも併記する。** QR が読めない席・環境が必ずある
- 共有シートを飛び先にする場合、顧客配布版（内部の列と節を落としたもの）を指すこと

<a id="case-studies"></a>

## 事例パック（`case-studies`）

公表事例を資料に載せるページ群。複数を抜粋で、1 社を詳細で、そして目の前の顧客に当てはまる理由で。公開許諾と日付つきの出典は templates/marketing/case-study.ja.md が管理する。

### 事例（抜粋・3 社）（`case-study-card`）

![事例（抜粋・3 社）](images/slide-templates/case-study-card.png)

公表事例を 3 件、1 行ずつで並べる。関心を引いた後に信頼を補強する 1 枚

**答える問い**: 同じような課題を、他社はどう解決したのか

**figures**: `governing_message`, `lead_in`, `cards`, `so_what`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `lead` | `string` | ✔ | 100 字以内 |
| `cases` | `array` (string≤16, string≤68) | ✔ | 2〜3 件 |
| `sowhat` | `string` | ✔ | 100 字以内 |
| `source` | `string` | ✔ | 200 字以内 |

使うときの決まり:

- **公表されている事例だけを載せる。** 未公表の顧客名・数値を出さない
- 数値は公表資料の値をそのまま使い、**出典（媒体名と日付）を source に必ず書く**
- 事例・数値は 3 ヶ月ルールの対象。**最終確認日を過ぎたものは再確認してから使う**
- 顧客名の掲載は、その顧客と合意した範囲に限る（商談側の事例化の約束は stage-5 §6 / stage-6 §5）
- 3 件まで。**並べるほど印象は薄くなる**。当てる相手に近い順で選ぶ

### 事例（詳細・1 社）（`case-study-detail`）

![事例（詳細・1 社）](images/slide-templates/case-study-detail.png)

1 社を、課題 → 打ち手 → 結果の順で 1 枚に収める。数値は公表値のみ

**答える問い**: その会社は何に困っていて、何をして、どうなったのか

**figures**: `governing_message`, `lead_in`, `before_after`, `so_what`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `lead` | `string` | ✔ | 100 字以内 |
| `before` | `array` | ✔ | 2〜3 件 |
| `after` | `array` | ✔ | 2〜3 件 |
| `result` | `string` | ✔ | 90 字以内 |
| `source` | `string` | ✔ | 200 字以内 |

使うときの決まり:

- **公表されている事例だけを載せる。** 未公表の顧客名・数値を出さない
- 数値は公表資料の値をそのまま使い、**出典（媒体名と日付）を source に必ず書く**
- 事例・数値は 3 ヶ月ルールの対象。**最終確認日を過ぎたものは再確認してから使う**
- 顧客名の掲載は、その顧客と合意した範囲に限る（商談側の事例化の約束は stage-5 §6 / stage-6 §5）
- **導入前と導入後を、同じ観点で並べる。** 観点がずれた before / after は比較にならない
- 代表数値は 1 つに絞る。**複数出すと、どれが効果なのか伝わらない**

### この事例が当てはまる理由（`case-fit`）

![この事例が当てはまる理由](images/slide-templates/case-fit.png)

事例の状況と目の前の顧客の状況を並べ、なぜ参考になるのかを示す

**答える問い**: その事例は、うちの状況にどこまで当てはまるのか

**figures**: `governing_message`, `lead_in`, `table`, `so_what`, `source_note`  
**推論レベル**: 診断（要因・構造の特定）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `lead` | `string` | ✔ | 100 字以内 |
| `rows` | `string[][]` | ✔ | 3〜4 件、38 字以内 |
| `caveat` | `string` | ✔ | 100 字以内 |
| `source` | `string` | ✔ | 200 字以内 |

使うときの決まり:

- **公表されている事例だけを載せる。** 未公表の顧客名・数値を出さない
- 数値は公表資料の値をそのまま使い、**出典（媒体名と日付）を source に必ず書く**
- 事例・数値は 3 ヶ月ルールの対象。**最終確認日を過ぎたものは再確認してから使う**
- 顧客名の掲載は、その顧客と合意した範囲に限る（商談側の事例化の約束は stage-5 §6 / stage-6 §5）
- **当てはまらない点を必ず 1 つ書く**（caveat）。全部当てはまる事例は無く、隠すと PoC で露見する
- 顧客側の欄は、ヒアリングで取れている事実だけを書く。**推測で埋めない**

<a id="proposal"></a>

## 提案パック（`proposal`）

問題解決型提案のうち、再利用できるページが無かった節。見えている問題の下にある構造、課題→解決のマッピング、対象と対象外、業務がどう変わるか、PoC と合否基準、次の一歩。

### 課題 → 解決のマッピング（`challenge-solution-map`）

![課題 → 解決のマッピング](images/slide-templates/challenge-solution-map.png)

合意した課題と、それを解く機能、その結果を 1 対 1 で並べる提案の核

**答える問い**: どの課題が、何によって、どう解決されるのか

**figures**: `governing_message`, `lead_in`, `table`, `so_what`, `source_note`  
**推論レベル**: 因果（原因の主張）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `lead` | `string` | ✔ | 100 字以内 |
| `rows` | `string[][]` | ✔ | 2〜4 件、34 字以内 |
| `scope_out` | `string` | ✔ | 100 字以内 |
| `source` | `string` | ✔ | 200 字以内 |

使うときの決まり:

- **顧客提示用**。個人の影響力・賛否・社内政治・競合の弱点を書かない
- **課題スライドと、順番も文言も一致させる。** 言い換えると「別の話」に見える
- 1 課題 = 1 行。**1 つの機能で 3 つ解けると書かない**（検証時に破綻する）
- 解けない課題は行を作らず、対象外として下段に書く。**無理に当てはめない**
- 結果は業務がどうなるかで書く。機能名の言い換えにしない

### 対象範囲と対象外（`scope-in-out`）

![対象範囲と対象外](images/slide-templates/scope-in-out.png)

本提案に入るものと入らないものを並べ、期待値をそろえる

**答える問い**: どこまでが今回の話で、どこからが別の話なのか

**figures**: `governing_message`, `lead_in`, `before_after`, `so_what`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `lead` | `string` | ✔ | 100 字以内 |
| `inside` | `array` | ✔ | 2〜4 件 |
| `outside` | `array` | ✔ | 2〜4 件 |
| `why` | `string` | ✔ | 100 字以内 |
| `source` | `string` | ✔ | 200 字以内 |

使うときの決まり:

- **顧客提示用**。個人の影響力・賛否・社内政治・競合の弱点を書かない
- **対象外を先に決めてから対象を書く。** 対象外の空いた提案は、後から膨らむ
- 対象外にした理由を書く。**「やらない」だけだと、できないと読まれる**
- 他ベンダー・他プロジェクトが持っている範囲は、対象外に明記する

### PoC の目的と合否基準（`poc-plan`）

![PoC の目的と合否基準](images/slide-templates/poc-plan.png)

何を確かめれば実現可能と判断できるか、その先に何が起きるかまで書く

**答える問い**: PoC で何を確かめ、合格したら次に何が起きるのか

**figures**: `governing_message`, `lead_in`, `table`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `lead` | `string` | ✔ | 100 字以内 |
| `rows` | `string[][]` | ✔ | 5〜7 件、50 字以内 |
| `source` | `string` | ✔ | 200 字以内 |

使うときの決まり:

- **顧客提示用**。個人の影響力・賛否・社内政治・競合の弱点を書かない
- **合否基準は数値か、YES/NO で答えられる形にする。** 「うまくいくこと」は基準ではない
- **「合格したら次に何が起きるか」を必ず書く。** 顧客がそこに答えられない PoC は、まだ設計されていない
- 不合格だった場合にどうなるかも書く。片道の PoC は検証ではない
- 顧客側に必要な体制・工数・データを明示する。**「特別な負担はありません」と言わない**

### 期待効果（業務がどう変わるか）（`outcome-before-after`）

![期待効果（業務がどう変わるか）](images/slide-templates/outcome-before-after.png)

機能ではなく、日々の業務がどう変わるかで効果を語る 1 枚

**答える問い**: 導入すると、現場の仕事は何が変わるのか

**figures**: `governing_message`, `lead_in`, `before_after`, `so_what`, `source_note`  
**推論レベル**: 予測（将来値の見通し）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `lead` | `string` | ✔ | 100 字以内 |
| `before` | `array` | ✔ | 2〜4 件 |
| `after` | `array` | ✔ | 2〜4 件 |
| `quant` | `string` | ✔ | 100 字以内 |
| `source` | `string` | ✔ | 200 字以内 |

使うときの決まり:

- **顧客提示用**。個人の影響力・賛否・社内政治・競合の弱点を書かない
- **機能ではなく業務で書く。** 「ACID になる」ではなく「突合が要らなくなる」
- **算出根拠のある定量値しか書かない。** 無いなら定性で書き、PoC で実測すると明示する
- before と after を同じ観点で並べる。観点がずれた対比は比較にならない
- 公表事例の数値を自社の効果として書かない。事例は事例として別ページに置く

### 本日決めたいことと次の一歩（`next-step-customer`）

![本日決めたいことと次の一歩](images/slide-templates/next-step-customer.png)

この場で決めることと、次回までに双方が持つ宿題を分けて示す

**答える問い**: 今日決めるのは何で、次までに誰が何をするのか

**figures**: `governing_message`, `lead_in`, `flow`, `so_what`, `table`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `lead` | `string` | ✔ | 100 字以内 |
| `steps` | `array` | ✔ | 2〜4 件 |
| `decide` | `string` | ✔ | 100 字以内 |
| `rows` | `string[][]` | ✔ | 2〜3 件、30 字以内 |
| `source` | `string` | ✔ | 200 字以内 |

使うときの決まり:

- **顧客提示用**。個人の影響力・賛否・社内政治・競合の弱点を書かない
- **今日決めることを 1 つに絞る。** 複数あると、どれも決まらない
- 宿題には担当と期日を書く。**どちらも無い宿題は動かない**
- こちら側の宿題を必ず入れる。顧客にだけ宿題を出す資料にしない

### 課題の構造（見えている問題と根本原因）（`iceberg-challenge`）

![課題の構造（見えている問題と根本原因）](images/slide-templates/iceberg-challenge.png)

表面に出ている問題と、その下にある構造を分けて示し、対症療法と差別化する

**答える問い**: いま見えている問題の下に、何があるのか

**figures**: `governing_message`, `lead_in`, `iceberg`, `source_note`  
**推論レベル**: 因果（原因の主張）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `lead` | `string` | ✔ | 100 字以内 |
| `above` | `array` | ✔ | 2 件 |
| `below` | `array` | ✔ | 2〜3 件 |
| `source` | `string` | ✔ | 200 字以内 |

使うときの決まり:

- **顧客提示用**。個人の影響力・賛否・社内政治・競合の弱点を書かない
- 上段は**顧客が実際に口にした問題**、下段はこちらの構造の読み。**混ぜない**
- 上段は**短い名詞句を 2 つ**（各 10 文字まで）。図の水面上は 2 行しか入らない。3 つ以上並べたくなるなら、表面の問題がまだ絞れていない
- 下段は 3 つまで。**根本原因を並べるほど、どれも根本に見えなくなる**
- この読みが違っている可能性を残す。合意を取る前に断定しない

<a id="marketing"></a>

## マーケティングパック（`marketing`）

まだ商談になっていない相手に当てるページ群。イベント・登壇の告知、課題を認識していない人への価値の提示、ユースケース 1 枚、技術資料の要旨。

### イベント・セミナー告知（`event-announce`）

![イベント・セミナー告知](images/slide-templates/event-announce.png)

開催概要（日時・形式・対象・参加費・申込先）を 1 枚にまとめた告知

**答える問い**: いつ・どこで・誰向けに開かれ、どう申し込むのか

**figures**: `governing_message`, `lead_in`, `event_mode_badge`, `event_overview`, `so_what`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `lead` | `string` | ✔ | 100 字以内 |
| `rows` | `string[][]` | ✔ | 3〜4 件、44 字以内 |
| `mode` | `string` | ✔ | 10 字以内 |
| `cta` | `string` | ✔ | 100 字以内 |
| `source` | `string` | ✔ | 200 字以内 |

使うときの決まり:

- **不特定多数向け**。特定の企業・個人が推測できる書き方をしない
- **確定した情報だけを載せる。** 登壇者・会場・日時は、決まるまで書かない
- **対象者を書く。** 「どなたでも」は誰にも刺さらない（ナーチャリングの段が決まらない）
- 参加費・定員・申込期限を省かない。**4 行に収まらないなら、1 行にまとめる**（行を増やすと申込先が入らなくなる）
- mode は online / offline / hybrid のいずれか
- rows の 1 列目はピクトグラム名。使えるのは `scripts/illustrations.py --list` に出るものだけ（日時=calendar、会場=pin、対象=people、費用=coin、期限=clock）

### セッションのプログラム（`session-agenda`）

![セッションのプログラム](images/slide-templates/session-agenda.png)

当日の進行を時刻・内容・話す人で並べる

**答える問い**: 当日は何が、どの順で、誰から話されるのか

**figures**: `governing_message`, `lead_in`, `event_timetable`, `so_what`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `lead` | `string` | ✔ | 100 字以内 |
| `rows` | `string[][]` | ✔ | 3〜6 件、40 字以内 |
| `note` | `string` | ✔ | 100 字以内 |
| `source` | `string` | ✔ | 200 字以内 |

使うときの決まり:

- **不特定多数向け**。特定の企業・個人が推測できる書き方をしない
- **時刻は確定したものだけ。** 未定の枠は「調整中」と書き、空欄にしない
- 6 枠まで。それ以上は 2 枚に分ける（詰めて小さくしない）
- 質疑の時間を必ず入れる。**質疑の無いセッションでは、聞くべきことが集まらない**

### 登壇者紹介（`speaker-intro`）

![登壇者紹介](images/slide-templates/speaker-intro.png)

話す人の立場と、なぜこの話をするのかを示す

**答える問い**: この話は、どういう立場の人から聞くことになるのか

**figures**: `governing_message`, `lead_in`, `event_speakers`, `so_what`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `lead` | `string` | ✔ | 100 字以内 |
| `speakers` | `array` (string≤14, string≤26, string≤30) | ✔ | 1〜4 件 |
| `why` | `string` | ✔ | 100 字以内 |
| `source` | `string` | ✔ | 200 字以内 |

使うときの決まり:

- **不特定多数向け**。特定の企業・個人が推測できる書き方をしない
- **実在する登壇者の、確認済みの情報だけを書く。** 肩書きは本人に確認する
- 経歴を並べない。**なぜこの人がこの話をするのか**が伝わればよい
- 顧客企業の登壇者を載せる場合は、公開許諾の範囲を確認する（事例と同じ扱い）

### 改善効果とメリット（段 0〜1）（`value-message`）

![改善効果とメリット（段 0〜1）](images/slide-templates/value-message.png)

課題を認識していない相手に、構築・刷新時に解くべき論点とその価値を示す

**答える問い**: いま何を直しておくと、後で何が起きずに済むのか

**figures**: `governing_message`, `lead_in`, `cards`, `so_what`, `source_note`  
**推論レベル**: 診断（要因・構造の特定）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `lead` | `string` | ✔ | 100 字以内 |
| `items` | `array` (string≤16, string≤60) | ✔ | 3 件 |
| `ask` | `string` | ✔ | 100 字以内 |
| `source` | `string` | ✔ | 200 字以内 |

使うときの決まり:

- **不特定多数向け**。特定の企業・個人が推測できる書き方をしない
- **段 0〜1 は Why Change? の段。製品説明を厚く盛らない**（`nurture-map.ja.md` §1）
- 3 枚は 状況 → 気づいていない不都合 → 放置した場合、の順に固定する
- **顧客の言葉で書く。** 製品名から始まる文は、この段では読まれない
- 断定しない。最後は読み手への問いで終える

### ユースケース 1 枚（段 1〜2）（`use-case-one-pager`）

![ユースケース 1 枚（段 1〜2）](images/slide-templates/use-case-one-pager.png)

1 つの使い方を、前提・やること・効くところの順で 1 枚に収める

**答える問い**: この製品は、具体的にどういう使い方をするのか

**figures**: `governing_message`, `lead_in`, `table`, `so_what`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `lead` | `string` | ✔ | 100 字以内 |
| `rows` | `string[][]` | ✔ | 3〜5 件、50 字以内 |
| `fit` | `string` | ✔ | 100 字以内 |
| `source` | `string` | ✔ | 200 字以内 |

使うときの決まり:

- **不特定多数向け**。特定の企業・個人が推測できる書き方をしない
- **1 枚 = 1 ユースケース。** 汎用的に書くほど、誰の話でもなくなる
- 前提（この使い方が成り立つ条件）を必ず書く。**条件を書かないユースケースは営業の作り話になる**
- **事例と混ぜない。** ユースケースは使い方、事例は実績。出典の要否が違う
- プレビュー機能を、提供済みの使い方として書かない

### ホワイトペーパーの要旨（段 3）（`whitepaper-abstract`）

![ホワイトペーパーの要旨（段 3）](images/slide-templates/whitepaper-abstract.png)

技術資料の中身を、読む前に判断できる形で示す表紙 1 枚

**答える問い**: この資料には何が書いてあって、読むと何が分かるのか

**figures**: `governing_message`, `lead_in`, `flow`, `so_what`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `lead` | `string` | ✔ | 100 字以内 |
| `toc` | `array` | ✔ | 3〜5 件 |
| `answers_q` | `string` | ✔ | 100 字以内 |
| `who` | `string` | ✔ | 100 字以内 |
| `source` | `string` | ✔ | 200 字以内 |

使うときの決まり:

- **不特定多数向け**。特定の企業・個人が推測できる書き方をしない
- **読むと何が分かるかを書く。** 目次だけの表紙は、読むかどうかの判断材料にならない
- **想定読者を書く。** 段 3 は技術的裏付けの段で、読み手は評価者である
- 検証していない主張を要旨に置かない。仮説は本文で仮説として扱う
- 性能値・価格・エディションは 3 ヶ月ルールの対象。最終確認日を source に書く

<a id="partner"></a>

## パートナーパック（`partner`）

プレイブックが定義しながらテンプレートの無かった 2 種。担ぐとパートナーに何が得られるかと、RACI・商流・見積境界・責任の所在を決める共同提案方針書。

### パートナー向け 価値と協業の形（`partner-value`）

![パートナー向け 価値と協業の形](images/slide-templates/partner-value.png)

パートナーにとって何が得られ、何を担うのかを示す提示用の 1 枚

**答える問い**: この製品を担ぐと、パートナーにとって何が良いのか

**figures**: `governing_message`, `lead_in`, `cards`, `so_what`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `lead` | `string` | ✔ | 100 字以内 |
| `items` | `array` (string≤16, string≤60) | ✔ | 3 件 |
| `ask` | `string` | ✔ | 100 字以内 |
| `source` | `string` | ✔ | 200 字以内 |

使うときの決まり:

- **パートナー提示用**。顧客固有の機密情報は必要最小限にする（プレイブック §3）
- **再利用しやすい標準情報で書く。** 特定商談の事情を混ぜると、他案件で使えなくなる
- パートナー側の利益（案件規模・役務・継続収益）を書く。**自社の都合だけ書かない**
- 競合の弱点を名指ししない。パートナーは競合とも取引している
- 価格は定価（税別）の参考見積として扱い、割引・複数年条件は載せない（AE に回す）

### 共同提案方針書（`joint-proposal-policy`）

![共同提案方針書](images/slide-templates/joint-proposal-policy.png)

共同勝ち筋・RACI・商流・見積境界・知財と守秘・契約責任を 1 枚で合意する

**答える問い**: この案件で、誰が何に責任を持ち、どこで見積を分けるのか

**figures**: `governing_message`, `lead_in`, `table`, `source_note`  
**推論レベル**: 記述（事実の整理）  
**status**: experimental

**入力**

| スロット | 型 | 必須 | 制約 |
|---|---|---|---|
| `title` | `string` | ✔ | 70 字以内 |
| `lead` | `string` | ✔ | 100 字以内 |
| `rows` | `string[][]` | ✔ | 5〜7 件、50 字以内 |
| `source` | `string` | ✔ | 200 字以内 |

使うときの決まり:

- **パートナー提案用**。合意していない項目を、合意済みのように書かない
- **見積境界を必ず書く。** ここが曖昧なまま顧客に出すと、後で必ずもめる
- 知財・守秘と契約責任の所在を省かない（プレイブック §3 の必須要件）
- 未合意の項目は「未合意」と書いた行として残す。**空欄で出さない**
- 顧客名・顧客固有の条件を書く場合、NDA の締結状況を確認してから入れる
