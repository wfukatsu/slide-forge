*[日本語](report-templates.ja.md)*

# Pricing Strategy Report Templates

Templates for a detailed pricing strategy report, organized by request type (A new product, B repricing an existing offer, C price structure, D competitive response, E discounts and policy, F capability assessment). Pick the one matching template and fill every section. Headings are bilingual Japanese/English, so use the side matching the output language (translate for other languages).

Common rules:

- Section 1 is the conclusion. State the price (or action), target, strategy, and the **one number** that justifies it (breakeven sales change, differentiation share, price/value ratio, and so on).
- Put assumptions in a table, with confirmed / to confirm, source, and sensitivity (high, medium, low) on each row.
- Do not drop a section for lack of data. Write what is missing and what would change if it were known.
- Include the tables from the scripts (`eve_calc.py`, `breakeven.py`, `structure_compare.py`) as Markdown, with 1–3 sentences on how to read them. Attach the input JSON as an appendix.

---

## A. 新製品の価格設定 / New-product pricing

```
# {製品} 価格決定レポート / {Product} pricing recommendation
## 1. 推奨事項 / Recommendation                         ← price by segment, metric, strategy, justifying number
## 2. 入力情報と前提 / Inputs and assumptions
## 3. セグメント別の経済的価値 / Economic value by segment      ← eve_calc.py
## 4. セグメント、オファー構成、価格メトリクス、フェンス / Segments, offer, metric, fences
## 5. 価格レンジと戦略 / Price range and strategy               ← ceiling and floor; skimming / penetration / neutral
## 6. 候補価格の損益分岐分析 / Breakeven analysis of candidate prices ← breakeven.py
## 7. 発売とライフサイクルの計画 / Launch and lifecycle plan
## 8. 価値の伝達と値引きポリシー / Value communication and discount policy
## 9. 測定計画 / Measurement plan
## 10. リスク、倫理・法務チェック / Risks, ethics and legal checks
## 11. 次のステップと未確定事項 / Next steps and open questions
## 付録: スクリプト入力 / Appendix: script inputs
```

Section 1 table: `| Segment | Price metric | Recommended price | Range (floor–ceiling) | Strategy | Why |`

## B. 既存価格の見直し（値上げ・値下げ） / Repricing an existing offer

```
# {製品} 価格改定レポート / {Product} price change recommendation
## 1. 推奨事項 / Recommendation                         ← whether to change, by how much, when, for whom
## 2. 入力情報と前提 / Inputs and assumptions             ← current price, incremental cost, volume, trend (baseline)
## 3. 現行価格と価値の位置 / Where today's price sits against value ← EVE, or the price/value ratio
## 4. 候補価格の損益分岐分析 / Breakeven analysis of candidate prices ← breakeven.py; how to read the breakeven sales curve
## 5. 顧客と競合の反応の見通し / Expected customer and competitor response ← drivers of price sensitivity, competitor reaction
## 6. 伝え方と移行計画 / Communication and transition plan   ← rationale for the increase, advance notice, treatment of existing customers
## 7. 測定計画 / Measurement plan
## 8. リスク、倫理・法務チェック / Risks, ethics and legal checks
## 9. 次のステップと未確定事項 / Next steps and open questions
## 付録: スクリプト入力 / Appendix: script inputs
```

## C. 価格構造の再設計 / Price structure redesign

```
# {製品} 価格構造の見直し / {Product} price structure review
## 1. 推奨事項 / Recommendation                         ← structure to adopt, effect on revenue and contribution margin, justifying number
## 2. 入力情報と前提 / Inputs and assumptions             ← distribution of customer sizes, value, incremental cost
## 3. セグメントと価値の生まれ方 / Segments and how value arises ← eve_calc.py
## 4. 現行構造の問題 / What is wrong with today's structure  ← price/value by size, where discounts concentrate, leakage
## 5. 構造案の比較 / Comparison of structure options        ← structure_compare.py
## 6. 価格メトリクスの評価とフェンス / Metric scoring and fences ← scoring table on the 5 criteria, loophole check
## 7. 移行計画 / Transition plan                          ← new vs existing customers, caps, timing
## 8. 測定計画 / Measurement plan
## 9. リスク、倫理・法務チェック / Risks, ethics and legal checks
## 10. 次のステップと未確定事項 / Next steps and open questions
## 付録: スクリプト入力 / Appendix: script inputs
```

If habitual discounting is also an issue, add "Value communication and discount policy" (the content of section 4 of E) after section 7 and renumber the sections that follow.

## D. 競合の値下げへの対応 / Responding to a competitor's price move

```
# {競合} の価格変更への対応方針 / Response to {competitor}'s price move
## 1. 推奨事項 / Recommendation                         ← ignore, selective response, full match, or reinforce value; scope; time limit
## 2. 状況の整理 / Situation                              ← competitor's move, its aim, affected customers and volume
## 3. 対応判断の問い / Response decision questions         ← answer the decision flow in price-competition.md one question at a time
## 4. 反応的価格変更の損益分岐 / Breakeven of a reactive price change ← volume lost vs cost of matching
## 5. 選択肢の比較 / Options compared                      ← cost, effect and competitor counter-reaction of each option
## 6. 実施と監視 / Execution and monitoring                ← limiting the scope, signals, exit conditions
## 7. リスク、倫理・法務チェック / Risks, ethics and legal checks ← information exchange that could be read as collusion, predatory pricing
## 8. 次のステップと未確定事項 / Next steps and open questions
```

## E. 値引き・価格ポリシーの設計 / Discount and pricing policy

```
# {事業} 価格ポリシー / {Business} pricing policy
## 1. 推奨事項 / Recommendation
## 2. 現状 / Current state                              ← price waterfall, dispersion of realized prices (pocket prices)
## 3. 問題の診断 / Diagnosis                             ← what discounts are exchanged for, buyer learning
## 4. ポリシー設計 / Policy design                         ← give–get, approval authority, what is never discounted, logging exceptions
## 5. 値上げ・販促のルール / Rules for increases and promotions
## 6. 導入と定着 / Rollout and adoption                    ← briefing sales, incentives, transition period
## 7. 測定計画 / Measurement plan
## 8. リスク、倫理・法務チェック / Risks, ethics and legal checks
## 9. 次のステップと未確定事項 / Next steps and open questions
```

## F. 価格決定の組織・プロセスの診断 / Pricing capability assessment

```
# {組織} 価格決定の能力診断 / {Organization} pricing capability assessment
## 1. 総合評価と優先課題 / Overall assessment and priorities
## 2. 診断の範囲と根拠 / Scope and evidence
## 3. 観点別の診断 / Findings by dimension                  ← organization and roles, process, data and tools, incentives, culture
## 4. 優先課題と打ち手 / Priority gaps and actions
## 5. ロードマップ / Roadmap                              ← 90 days, 6 months, 1 year
## 6. 次のステップと未確定事項 / Next steps and open questions
```

## References

[1] Nagle, T. T., & Müller, G. (2018). *The Strategy and Tactics of Pricing: A Guide to Growing More Profitably* (6th ed.). Routledge.
- Chapters 1–12 (pp. 1–316).

The order of sections in the templates follows the value cascade of [1] (value estimation → structure → level → policy → competition). The templates themselves (how sections are divided, the headings) were created for this skill and are not in [1].
