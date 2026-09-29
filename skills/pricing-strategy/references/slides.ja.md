*[English](slides.md)*

# 分析結果のスライド化

価格戦略の分析結果（経済的価値、損益分岐、価格構造の比較、競合対応、値引きポリシー）を、`slide-templates/pricing` パックのページテンプレートでスライドにする手順である。詳細レポートの節（`report-templates.md` の雛形 A〜F）とテンプレートの対応、計算スクリプトからのデータの流し込み方、注意点をまとめている。

## 0. 作る前に確認する

スライドを作り始める前に、**AskUserQuestion で 1 回だけ**次の 4 点を確認する（ユーザーがすでに答えている項目は省く）。答えによって、スクリプトのオプション、使うテンプレート、生成先が変わる。

| 質問（header） | 選択肢（先頭が推奨） | 答えで変わること |
|---|---|---|
| 計算ロジックのスライドを入れるか（計算ロジック） | 付録にまとめる（推奨）／各結果の直後に置く／入れない | `--slides-logic` を付けるか、ページの並び順 |
| 用途（用途） | 配布・読み物（`print`）（推奨）／登壇（`presentation`） | `--density`。登壇用は文言を縮める |
| 出力先（出力先） | Google スライドまで生成（推奨）／スロットデータ（JSON）まで | Google スライドまで生成するか、データを渡して終えるか |
| 分量（分量） | 詳細 10〜12 枚（推奨）／簡潔 5〜6 枚 | 使う結果テンプレートの数 |

Google スライドまで生成する場合は、ユーザーの Google Drive にファイルができることを出力先の選択肢の説明に書く。

## 1. テンプレートの対応

分析結果は `slide-templates/pricing` パックのページテンプレートでスライドにする。1 枚が 1 つの問いに答える。

| テンプレート | 答える問い | 対応する節 | データの出どころ |
|---|---|---|---|
| `economic-value-waterfall` | 価値はいくらで、価格はそのどこにあるか | A3, C3, B3 | `eve_calc.py --slides`（セグメントごとに 1 枚） |
| `breakeven-sales-change` | 価格変更は数量がどれだけ動けば割に合うか | A6, B4 | `breakeven.py --slides` |
| `price-structure-compare` | どの料金体系が規模ごとの価値に連動するか | C5 | `structure_compare.py --slides` |
| `competitor-response` | 競合の値下げに対抗すべきか | D3〜D4 | `breakeven.py --reactive --slides` |
| `give-get-policy` | 何と引き換えなら値引きしてよいか | A8, E4 | 手で書く（スクリプトなし） |
| `calculation-logic` | この数字はどう計算され、どの入力に依存しているか | 付録 | 各スクリプトの `--slides DIR --slides-logic` |

結論のページは既存の `exec-summary-readable` か `conclusion-rationale-implication` を使う。

`--slides-logic` で書き出される計算ロジックのスライド:

| ファイル | 内容 |
|---|---|
| `calculation-logic-economic-value-N.json` | セグメント N の参照価値、各価値ドライバーの算式（入力値を代入したもの）、総経済価値の合計 |
| `calculation-logic-breakeven.json` | 現行価格・増分単位コスト・単位貢献利益と、候補価格ごとの損益分岐販売変化率の計算 |
| `calculation-logic-reactive.json` | 対抗が得になる流出率の計算（`--reactive` のときだけ） |
| `calculation-logic-structure.json` | 各案の基本料・段・値引きの定義、増分原価、顧客分布、価値の置き方 |

## 2. 手順

1. 計算スクリプトに `--slides DIR`（計算ロジックを入れるなら `--slides-logic` も）を付けて実行する。DIR にテンプレートごとのスロットデータ（JSON）ができる。
2. `【要記入】`（英語は `[TODO]`）で始まる値をすべて書き換える。タイトルは結論の 1 文、lead は対象・期間・単位、source は出典と前提。判定や推奨の欄はスクリプトでは決められない。計算ロジックのスライドのタイトルは「何がこの数字を決めているか」を 1 文で書く。
3. 確認した配置に従ってページ番号を振る。付録にまとめるなら結果ページの後ろに、直後に置くなら各結果ページの次の番号にする（例: 040 の結果に 045 のロジック）。
4. リポジトリのルートで描画し、デッキにまとめて検証する。Google スライドまで生成する場合は、`google-slides` スキルの手順（Drive フォルダ作成 → 生成 → 目視確認）に従う。

```bash
.venv/bin/python scripts/render_slide_template.py --template breakeven-sales-change \
  --data DIR/breakeven-sales-change.json --density print --out pages/090-breakeven.json
.venv/bin/python scripts/render_slide_template.py --template calculation-logic \
  --data DIR/calculation-logic-breakeven.json --density print --out pages/190-logic-breakeven.json
.venv/bin/python scripts/assemble_spec.py --out deck.json --title "価格改定の提案" --density print pages/
.venv/bin/python scripts/build_deck.py --template templates/blank-16x9.json --spec deck.json --dry-run --strict
```

注意:

- 書き出されるデータは配布用の `print` 密度の文字数に合わせている。登壇用の `--density presentation` では上限が短いので、長い文言を縮める。
- 表示名が長いとテンプレートの上限を超える。価値ドライバーと構造案には入力 JSON で `"short"` を付ける（12 字まで）。計算ロジックの欄は 72 字まで。超えるとスクリプトが警告する。
- 計算ロジックの数値には単位が付く。金額には入力 JSON の `currency`、件数には `unit_label`（価格構造）と `volume_unit`（損益分岐）を使う。価値ドライバーの入力の単位は `units` に書く（例: `"units": {"docs": "件", "rate": "円/時", "prob": "（年間発生確率）"}`。括弧で始まる単位は数値の直後に付く）。`units` がない入力は数値だけになるので、書き足すよう促す。
- 計算ロジックのスライドは、結果のスライドと同じ入力から同時に書き出す。結果だけを後から作り直したときは、ロジックも作り直す。
- 各テンプレートの `guardrails` に、その図の誤用パターンを書いてある。描画の前に読む。

## 3. 生成と目視確認

実際に作ってみて崩れやすかった点と、その防ぎ方。

- **自動チェックの指摘は必ず全部読む。** `build_deck.py --dry-run --strict` の出力を `tail` で切らない。「重なり」「はみ出し」「折り返し」の指摘が 1 件でもあれば、直すか、描画して問題ないことを確かめてから生成する。
- **タイトルは全角 30 字前後で 1 行に収める。** 2 行になるとリード文と重なる。
- **増分分解の図の棒ラベルは 6 字程度まで。** 棒が 6〜7 本並ぶと 1 本あたりの幅が狭い。入力 JSON の `short` で短くする。
- **表の欄は 1 行に収め、空欄を作らない。** 折り返しや空欄があると、その行だけ背が高くなって出典行にはみ出す。Slides の表の行は約 0.34 インチより低くならず、自動チェックはこれを見逃すことがあるので、表のページは画像で確認する。
- **表示の丸めを明記する。** 結果のスライドを万円に丸め、計算ロジックは円のまま載せるなら、リード文に単位を書く。提示用に丸めた価格（例: 算出 67 万円 → 提示 70 万円）は出典行に両方を書く。
- **画像で全ページを確認する。** `scripts/fetch_thumbnails.py` で画像にして 1 枚ずつ見る。直したら、変更したページと同じテンプレートを使うページを見直す。
- **作り直したら古い版を片付ける。** URL を共有していない版はゴミ箱に移し、Drive のフォルダにはデッキ 1 つと、作り直しに使う元データ（`deck.json`、入力 JSON、原稿を組むスクリプト）だけを置く。
- **原稿は組み立てスクリプトにまとめる。** `--slides` の出力を読み、`【要記入】` を置き換え、各ページを描画してデッキにまとめるまでを 1 本のスクリプトにしておくと、入力を変えたときに全ページを同じ手順で作り直せる。

## 関連ドキュメント

- [report-templates.ja.md](report-templates.ja.md): 詳細レポートの雛形（表の「対応する節」の番号はこの雛形の節）。
- `scripts/pricing/slide_data.py`: `--slides` と `--slides-logic` の出力形式、プレースホルダーの定義。

## 参考文献

[1] Nagle, T. T., & Müller, G. (2018). *The Strategy and Tactics of Pricing: A Guide to Growing More Profitably* (6th ed.). Routledge.
- 第2章 "Economic Value: The Guiding Force of Pricing Strategy", pp. 26–55.
- 第4章 "Price Structure: Tactics for Pricing Differently Across Customer Segments", pp. 76–105.
- 第5章 "Pricing Policy: Influencing Customer Expectations and Purchase Behaviors", pp. 106–132.
- 第7章 "Price Competition: Managing Conflict Thoughtfully", pp. 152–172.
- 第9章 "Financial Analysis: Analyzing Costs and Profits for Pricing", pp. 207–239.

各テンプレートが示す分析は [1] の方法に従う。テンプレートの構成とこの手順は、このスキルと slide-forge のために作ったものであり、[1] にはない。
