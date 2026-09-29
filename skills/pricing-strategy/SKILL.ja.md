---
name: pricing-strategy
description: >-
  Value-based pricing (Nagle & Müller). Use for what to charge for a new
  product/tier, raising or cutting a price, price structure (metric, tiers,
  per-seat vs usage, fences), whether a discount pays, responding to a
  competitor's price cut, discount policy, or pricing organization. Runs
  bundled calculators (economic value, breakeven, structure comparison).
  Triggers: 値付け, 価格戦略, 値上げ, 値下げ, 値引き, 料金体系, 課金単位,
  競合の値下げ, プライシング, how much to charge, pricing model.
---

# 価格戦略（価値ベースの戦略的プライシング）

*[English — normative skill](SKILL.md)*

価格の相談を、根拠の数字が付いた推奨に変える。方法は Nagle & Müller [1] の価値カスケード（価値の創造 → 価値の伝達 → 価格構造 → 価格ポリシー → 価格水準 → 価格競争）に従う。価格水準は 6 段のうち 5 段目であり、最初に決めるものではない。

作業ディレクトリは slide-forge のルートで、コマンドは `.venv/bin/python`。参照資料はこのスキルの `references/` にあり、英語版（`x.md`）と日本語版（`x.ja.md`）は同じ内容なので、出力言語に近い方を 1 つだけ読む。トークンを節約するため次を守る。

- reference は、その手順に入り、判断に必要なときだけ読む。**簡潔モードでは reference を原則読まない**。この SKILL.md とスクリプトの出力で答え、判断に迷う点があるときだけ該当ファイルを読む。
- スクリプトはソースを読まずに実行する。入力形式が分からないときだけ、冒頭の docstring を `head -60` で読む。
- `references/glossary.ja.md`（60KB）は全体を読まない。用語は `grep -i "<語>" skills/pricing-strategy/references/glossary.ja.md` で該当行だけ引く。訳語は `references/i18n.json` で足りる。

## 出力言語

ユーザーの指定、なければ依頼文の言語で書く。確認の質問も同じ言語でする。方法の用語は `references/i18n.json`（英→日）で毎回同じ訳にそろえる。英語で出すときは、その英語側を使う。

## 1. 依頼の種類

依頼の言葉ではなく、論点がどの層にあるかで分ける。「値下げすべきか」の答えが構造の変更になることもある。分からなければ `references/value-cascade.ja.md` の「症状から層を診断する」表を使う。

| 種類 | 典型的な依頼 | 主な reference | スクリプト |
|---|---|---|---|
| **A. 新製品の価格** | 新製品、新プラン、アドオン、API の価格 | economic-value, price-structure, price-level, financial-analysis | eve_calc, breakeven |
| **B. 既存価格の見直し** | 値上げ、値下げ、価格は妥当か | price-level, financial-analysis, pricing-policy | breakeven |
| **C. 価格構造の再設計** | 課金単位、段、従量か定額か、大口と小口の価格差、共食い | price-structure, economic-value, financial-analysis | structure_compare, breakeven |
| **D. 競合への対応** | 競合の値下げ、安い新規参入、価格戦争 | price-competition, financial-analysis | breakeven `--reactive` |
| **E. 値引き・ポリシー** | 値引き要求、値引きの常態化、交渉ルール、販促 | pricing-policy, value-communication | breakeven |
| **F. 組織の診断** | 誰が価格を決めるか、承認の仕組み、営業の報酬 | pricing-capability | なし |

複数にまたがるときは最も上流の層を主にする。価値が言語化されていなければ、どの種類でも手順 1 から始める。

## 2. 深さ

- **簡潔モード**（既定）: 「ざっくり」「quick」と言われた、1 つの問いに答えれば足りる（価格 X で数量はどれだけ要るか、この値引きは割に合うか、2 案のどちらか）。スクリプトは必ず実行する。下の「簡潔モードの形式」で書き、省いた手順と、詳細分析に進むべき条件を 1 行添える。
- **詳細モード**: 実際の発売・改定の意思決定、経営層向け資料、複数セグメント、「提案書」「レポート」と言われたとき。`references/report-templates.ja.md` の該当する雛形の全節を書く。

曖昧なら簡潔モードで答え、最後に詳細レポートを 1 行で提案する。

## 3. 手順

**0. 答えを変える情報だけを集める。** 欠けていて推奨を左右する項目だけを 1 回にまとめて尋ねる。仮定で進められる項目は「要確認」の印を付けて先に一巡する。必要な情報は、製品と対象セグメント（1〜3）、セグメントごとの次善の競合代替品とそのコスト、代替品に対する便益、増分コスト（埋没費用は使わない）、現行の価格・数量・トレンド、ライフサイクルと競合状況、目的と制約。

**1. 価値を推定する**（economic-value）。セグメントごとに参照価値と価値ドライバーを JSON に書き `eve_calc.py` を実行する。総経済価値は価格の天井であって推奨価格ではない。差別化価値の比率で、価値で売れるか価格で比べられるかを読む。総額しか分からなければ例示の内訳を置き「例示・要確認」と書く。

**2. 構造を決める**（price-structure）。オファー構成、価格メトリクス、価格フェンスを決め、抜け道を点検する。構造案は `structure_compare.py` で顧客規模の分布に当てて比べる。規模別の価格／価値の比率が偏るなら、メトリクスが価値に連動していない。売上中立の基本料は `"base_fee": "neutral"`、現行の規模別値引きは `"discounts": [{"min_size": 9, "pct": 35}]` で表す。下位プランの共食いは `breakeven.py` の cannibalization モードで計算する。

**3. 水準と戦略を決める**（price-level）。天井（総経済価値）と床（正の差別化なら代替品の価格、負なら増分コスト）を置き、スキミング・浸透・中立を条件で選ぶ。浸透価格は「なぜ競合は追随しないか」に答えられなければ採らない。

**4. 損益分岐で比べる**（financial-analysis）。候補価格ごとに `breakeven.py` を実行する。問いは「この価格が代替の価格に勝つには、数量がどれだけ変わる必要があるか」。損益分岐販売変化率 = −ΔP ÷ (CM + ΔP)。ベースラインは今日の数量ではなく、変更しなかった場合の推移。

**5. 競合の反応を見込む**（price-competition）。種類 D ではここが中心。判断の問いに一問ずつ答え、反応的価格変更の損益分岐で締める。対抗が正当化されるのは、対抗しない場合に失う数量が (CM前 − CM後) ÷ CM前 を超えるときだけ（`--reactive`）。失う数量は実際に流出しうる既存顧客で見積もる。複数年契約で固定された量は外し、新規パイプラインの比率を流出率とみなさない。

**6. 伝え方とポリシー**（value-communication, pricing-policy）。最初の交渉の前に値引きポリシーを書く（何と引き換えに何を出すか、営業の裁量、値引きしないもの）。値上げは理由、事前告知、既存顧客の扱いを計画する。

**7. ライフサイクル・測定・法務**（specialized-strategies, measurement, ethics-legal）。詳細モードでだけ読む。法務は確認を促すもので法的助言ではない。米国法中心なので、日本と EU は法務担当への確認を書く。組織上の障害が見えたら pricing-capability を読む。

**8. 書く。** 冒頭は結論（価格または行動、対象、戦略、正当化する 1 つの数字）。前提は表にし、各行に確認済み／要確認と感度を付ける。スクリプトの表は Markdown のまま載せ、詳細モードでは入力 JSON を付録にする。スライドを求められたときだけ `references/slides.ja.md` を読み、作り始める前に AskUserQuestion で計算ロジックのスライドの有無・用途・出力先・分量を 1 回で確認する（`slide-templates/pricing` パックを使う）。

### 簡潔モードの形式

```
**推奨 / Recommendation** — 価格（または行動）、対象、根拠の数字（2〜3 文）
**数字 / Numbers** — スクリプトの表を判断に効く行だけに絞る
**構造 / Structure** — 段・共食い・フェンス・競合対応の問いが関わる場合だけ（3〜5 項目）
**前提 / Assumptions** — 箇条書き。未確認の項目に印を付ける
**次の一手 / Next step** — 1〜2 項目
```

本文は表を除き約 400 語（日本語は約 800 字）まで。

## reference（`references/`）

| ファイル | 内容 |
|---|---|
| value-cascade | 全体像、どの層の問題かの診断 |
| economic-value | 価値の推定、セグメンテーション、`eve_calc` の入力形式 |
| value-communication | 価値の伝え方、フレーミング |
| price-structure | メトリクス、段、バンドル、フェンス、二部料金 |
| pricing-policy | 値引き、交渉、値上げの伝え方、販促、価格ウォーターフォール |
| price-level | 価格レンジ、戦略の選択、価格感応度の要因 |
| price-competition | 競合の値下げ、価格戦争 |
| measurement | 支払意思額・価格感応度の調査手法 |
| financial-analysis | 増分コスト、損益分岐、共食い、`breakeven` の入力形式 |
| specialized-strategies | ライフサイクル、イノベーション、為替、不況、移転価格 |
| pricing-capability | 価格決定の組織、権限、プロセス、報酬 |
| ethics-legal | 倫理、独占禁止法、価格差別、再販価格 |
| worked-example | 分析の流れの実例（構造変更が答えになった例） |
| glossary | 用語 222 語（grep で引く） |

ネットワーク効果とダイナミックプライシングは [1] の主題ではない。補うときは [1] に基づかない一般的知見と明記する。

## スクリプト

計算スクリプトは `scripts/pricing/` にある（slide-forge のルートからの相対パス）。入力 JSON は `out/pricing/` などの無視されるパスに置く。標準ライブラリのみ（Python 3.8+）。すべて Markdown を出力し、`--json` で JSON、`--lang en|ja` で言語を切り替える。計算は手でせずスクリプトで行う。

```bash
.venv/bin/python scripts/pricing/eve_calc.py --input eve.json --lang ja
.venv/bin/python scripts/pricing/breakeven.py --input prices.json --lang ja
.venv/bin/python scripts/pricing/breakeven.py --price 100 --cost 40 --candidates 90,110,120 --volume 1000
.venv/bin/python scripts/pricing/breakeven.py --price 12 --cost 2 --candidates 8 --reactive
.venv/bin/python scripts/pricing/structure_compare.py --input structures.json --lang ja
# どれも --slides DIR で slide-forge の pricing パック用のスロットデータも書き出す（--slides-logic で計算ロジックのスライドも）
```

## よくある失敗

- **名前を変えたコストプラス**: コストが決めるのは床だけ。手順 1 に戻る。
- **目の前の顧客の支払意思額に合わせる**: 初期の買い手は価値を判断できない。満足した利用者が認める価値で付け、価値を示すことに投資する。
- **全員に同じ価格**: セグメント間で価値が大きく違うなら、妥協価格ではなく構造で解く。
- **構造・ポリシーの問題を水準で解こうとする**: 値引きが特定の規模に集中していれば、先に `structure_compare.py` で規模別の価格／価値を見る。
- **埋没費用を入れる**: 損益分岐に入れるのは増分で回避可能なコストだけ。
- **精度と正確さの混同**: 推測した入力にはレンジと感度を示す。
- **競合の値下げに反射的に追随する**: 損益分岐と反応の広がりを先に確かめ、対抗するなら対象を限定する。
- **最初の交渉の後にポリシーを決める**: 最初の取引が以後の参照点になる。

## 参考文献

[1] Nagle, T. T., & Müller, G. (2018). *The Strategy and Tactics of Pricing: A Guide to Growing More Profitably* (6th ed.). Routledge.
- 第1章〜第12章（pp. 1–316）。各 reference ファイルが扱う章とページは、それぞれの末尾の「参考文献」に記載している。
