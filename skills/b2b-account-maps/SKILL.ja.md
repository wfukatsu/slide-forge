---
name: b2b-account-maps
description: >-
  Build the two maps a B2B deal turns on: an influence map of the buying
  committee (who decides, who blocks, who can be moved) and a discovery map of
  what is confirmed versus still assumed. Renders from the b2b-sales templates.
  Use for: ステークホルダーを整理, 関与者マップ, 意思決定者と承認経路, MEDDPICC,
  ディスカバリー, パイプラインレビュー, 提案前に何が未確認かを洗い出す.
  Not: the proposal deck itself (scalar-proposal-slides / google-slides-template);
  new reusable page templates (slide-template-creator).
---
*[English](SKILL.md)*

# B2B アカウントマップ

マップは 2 つ、目的は 1 つ: この案件が本当にクローズできるのか、次に何を
すべきかを知ること。インフルエンスマップは**誰か**に答え、ディスカバリー
マップは**何がまだ分かっていないか**に答える。

すべてのコマンドは slide-forge リポジトリルートから実行する。
`.venv/bin/python` を使う。

## 境界

| 依頼 | ルート先 |
|---|---|
| 誰が決めるか / 誰が止めるか / 承認経路 | 本スキル |
| 何が確認済みで何が仮定か、次に何を聞くか | 本スキル |
| 顧客に見せる提案デッキそのもの | `scalar-proposal-slides` / `google-slides-template` |
| 再利用できる新しい 1 枚テンプレート | `slide-template-creator` |
| 生成済みデッキの目視チェック | `slide-qa` |

これらのマップは**社内向けの作業成果物**である。顧客側の特定個人に
ついての判断を記録するものなので、顧客に渡してはならず、提案デッキに
貼り付けてもならない。

## 8 枚のページ

すべて `b2b-sales` パック（`slide-templates/b2b-sales/`）にある。

| テンプレート | 答えるもの |
|---|---|
| `influence-map` | 誰を動かせば決まるか（影響力 × 賛否の 2 軸） |
| `buying-committee` | 誰が関与し、どこまで会えているか |
| `decision-structure` | 承認はどの順で上がり、どこで止まるか |
| `discovery-map` | 何が確認済みで、何がまだ仮説か |
| `pain-chain` | 現場の課題は経営のどの数字に効いているか |
| `discovery-gaps` | 次に誰へ何を確認するか |
| `influence-map-org` | 誰が誰の下にいて、影響力と支持がどこに集まるか（組織構造） |
| `discovery-map-tree` | 顧客の目標は何に支えられ、自社はどこに効くか（Goal/Strategy/Tactics） |

```bash
.venv/bin/python scripts/list_slide_templates.py --pack b2b-sales
```

8 枚すべてを 1 つの架空アカウントに適用した実例デッキが
`examples/b2b-account-review.json` — 表紙、エグゼクティブサマリー、2 つの
マップとその補助ページを、実際のレビューが進む順に並べてある:

```bash
.venv/bin/python scripts/build_deck.py \
    --template templates/scalar-2026.json --spec examples/b2b-account-review.json --dry-run --strict
```

依頼に合ったペアを使う。パイプラインレビューなら通常
`discovery-map` + `discovery-gaps`、停滞している案件なら通常
`influence-map` + `decision-structure`。

### 構造で見せる 2 枚と、関与者が多い場合

`influence-map-org` と `discovery-map-tree` は**つながり**を見せる。2 軸の
`influence-map` が「誰の影響力が大きいか」なら、こちらは「誰が誰の下にいるか」。
MEDDPICC の `discovery-map` が「何が確認済みか」なら、こちらは「何が何を支えるか」。

どちらも 1 つの JSON から作る。関与者・項目が 9 を超えたらスライドに詰めず、
**全体を draw.io に出し、スライドには抽出版を載せる**:

```bash
.venv/bin/python scripts/build_account_graph.py <graph.json> --out out/<account>.drawio
.venv/bin/python scripts/drawio_export.py out/<account>.drawio --out out/<account>.png --scale 2
```

抽出は `account_graph.extract()`。落ちた人・項目は標準出力に出るので、その数を
テンプレートの `more` スロットに「他 N 名は draw.io 版参照」として必ず書く。
データモデルと抽出規則は
[references/account-graphs.ja.md](../../references/account-graphs.ja.md)。

## ワークフロー

### 1. インテイク

何かを尋ねる前に、ユーザーが既に持っているもの — ヒアリングノート、
議事録、CRM エクスポート — から作業する。そのうえで足りないものだけを
1 ラウンドで聞く:

- どのマップが欲しいか。対象のアカウントとオポチュニティはどれか;
- 既に会えている人物、その役職と実際の発言内容;
- 課題について顧客自身の数字が出ていればその数字;
- 案件の現在のステージと、追いかけている意思決定・期日。

人物・役職・立場をでっち上げない。誰も会っていないステークホルダーは、
ディスカバリーマップ上の `missing` であって、インフルエンスマップ上の
中立の点ではない。

### 2. 聞いたことと推測したことを分ける

資料を一度通読し、すべての記述にラベルを付ける: **顧客が言った**、
**観察した**（文書、組織図、送付済みの見積もり）、**当方の仮定**。
`confirmed` になれるのは最初の 2 つだけ。この作業こそがマップの価値を
生む — ステータスの規則は
[discovery-map.md](references/discovery-map.md) を読むこと。

### 3. 人を配置し、その理由を言えるようにする

インフルエンスマップでは、各人物を 影響力 (縦) × 賛否 (横) に配置し、
両方の座標について根拠を挙げられるようにする。影響力とは過去の意思決定を
実際に動かしたものであって、役職の高さではない。
[influence-map.md](references/influence-map.md) に、バイイングロール、
発言からスタンスを読み取る方法、よくある罠をまとめてある。

### 4. 作成とオフライン検証

アカウントのデータでテンプレートをレンダリングし、生成前に検証する:

```bash
.venv/bin/python scripts/render_slide_template.py \
  --template influence-map --data out/<account>-influence.json --out out/<account>-slide.json
.venv/bin/python scripts/build_deck.py \
  --template templates/scalar-2026.json --spec out/<account>-deck.json --dry-run --strict
```

この監査は、互いのラベルを覆い隠すバブル、ヘッダーと合っていない表の行、
あふれるテキストを検出する。修正はテンプレートではなくデータ側で行う —
通常はラベルを短くするか、同じ位置に重なった 2 人を離せば済む。

### 5. 生成と確認

生成したら、結果に対して `slide-qa` を実行する。インフルエンスマップでは
squint test（目を細めて見るテスト）を確認する: 次に動かすべき人物が最初に
目に入ること。

グラフ系の 2 ページには、オフライン監査では代わりに確認できないチェックが
1 つある。**コネクタを拡大表示し、カードに接していることを確かめる。**
カードは 3 つのセルを縦に積んだもので、全幅なのは中央のセルだけ —
ティアのバッジは右寄せ、影響力とオーナーの帯は左寄せ — なので、カードの
外周を狙った線は帯の横の余白に着地し、ページ上は何もつながっていないように
見えてしまう。図がボディボックスにアタッチしているのはまさにこのためで
あり、カードデザインを変更した場合はそれが保たれているか検証する。
`.drawio` でも同じチェックを行う。エッジはグループの id ではなくボディ
セルの id を取らなければならない
（[references/account-graphs.ja.md](../../references/account-graphs.ja.md)）。

その後、ページ全体を読む: すべてのカードが最上部から到達可能であること、
無関係なカードを横切る矢印がないこと、`extract()` が何かを落とした場合は
省略の注記があること。

### 6. 報告

アカウント、作成したマップ、デッキ URL、そして — 最も重要な —
`discovery-gaps` から取った**次に確認すべき事項の最短リスト**を報告する。

## ルール

- **根拠がなければ載せない。** すべての配置とすべての `confirmed` には
  出典が要る: 誰が、いつ言ったか。`source` スロットが必須なのはまさに
  このためである。
- **不在を中立にすり替えない。** 未接触のステークホルダーはギャップに
  属し、マップの中央には置かない。
- **影響力は実績であって肩書きではない。** 過去の意思決定を動かした証拠に
  基づいて配置する。
- **ペインチェーンは因果の主張である。** 各リンクにはそれぞれの裏付けが
  要る; リンクが測定値ではなく顧客の見立てである場合は、そう明記する。
- **マップは最新に保つ。さもなければ削除する。** 古びたインフルエンス
  マップはないより悪い — 過去の仮定を事実として流通させてしまう。
- 作業ファイルは ignore 済みの `out/` 以下に置き、リポジトリには決して
  置かない。
