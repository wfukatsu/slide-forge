*[English](report-templates.md)*

# 価格戦略レポートの雛形

価格戦略の詳細レポートを、依頼の種類別（A 新製品、B 既存価格の見直し、C 価格構造、D 競合対応、E 値引き・ポリシー、F 組織診断）に構成した雛形である。該当する雛形を 1 つ選び、全節を埋める。見出しは日英併記なので、出力言語の側を使う（ほかの言語は訳す）。

共通の規則:

- 1 節は結論。価格（または行動）、対象、戦略、それを正当化する **1 つの数字**（損益分岐販売変化率、差別化価値の比率、価格／価値の比率など）を書く。
- 前提は表にし、各行に確認済み／要確認、出典、感度（高・中・低）を付ける。
- データがない節も削らず、何が欠けていて、分かると何が変わるかを書く。
- スクリプト（`eve_calc.py`、`breakeven.py`、`structure_compare.py`）の表は Markdown のまま載せ、読み方を 1〜3 文添える。入力 JSON は付録に付ける。

---

## A. 新製品の価格設定 / New-product pricing

```
# {製品} 価格決定レポート / {Product} pricing recommendation
## 1. 推奨事項 / Recommendation                         ← セグメント別の価格、メトリクス、戦略、根拠の数字
## 2. 入力情報と前提 / Inputs and assumptions
## 3. セグメント別の経済的価値 / Economic value by segment      ← eve_calc.py
## 4. セグメント、オファー構成、価格メトリクス、フェンス / Segments, offer, metric, fences
## 5. 価格レンジと戦略 / Price range and strategy               ← 天井・床、スキミング／浸透／中立
## 6. 候補価格の損益分岐分析 / Breakeven analysis of candidate prices ← breakeven.py
## 7. 発売とライフサイクルの計画 / Launch and lifecycle plan
## 8. 価値の伝達と値引きポリシー / Value communication and discount policy
## 9. 測定計画 / Measurement plan
## 10. リスク、倫理・法務チェック / Risks, ethics and legal checks
## 11. 次のステップと未確定事項 / Next steps and open questions
## 付録: スクリプト入力 / Appendix: script inputs
```

1 節の表: `| セグメント | 価格メトリクス | 推奨価格 | レンジ（床〜天井） | 戦略 | 根拠 |`

## B. 既存価格の見直し（値上げ・値下げ） / Repricing an existing offer

```
# {製品} 価格改定レポート / {Product} price change recommendation
## 1. 推奨事項 / Recommendation                         ← 改定するか、幅、時期、対象
## 2. 入力情報と前提 / Inputs and assumptions             ← 現行価格、増分コスト、数量、トレンド（ベースライン）
## 3. 現行価格と価値の位置 / Where today's price sits against value ← EVE、または価格／価値の比率
## 4. 候補価格の損益分岐分析 / Breakeven analysis of candidate prices ← breakeven.py、損益分岐曲線の読み方
## 5. 顧客と競合の反応の見通し / Expected customer and competitor response ← 価格感応度の要因、競合の反応
## 6. 伝え方と移行計画 / Communication and transition plan   ← 値上げの理由、事前告知、既存顧客の扱い
## 7. 測定計画 / Measurement plan
## 8. リスク、倫理・法務チェック / Risks, ethics and legal checks
## 9. 次のステップと未確定事項 / Next steps and open questions
## 付録: スクリプト入力 / Appendix: script inputs
```

## C. 価格構造の再設計 / Price structure redesign

```
# {製品} 価格構造の見直し / {Product} price structure review
## 1. 推奨事項 / Recommendation                         ← 採るべき構造、売上・貢献利益への影響、根拠の数字
## 2. 入力情報と前提 / Inputs and assumptions             ← 顧客規模の分布、価値、増分コスト
## 3. セグメントと価値の生まれ方 / Segments and how value arises ← eve_calc.py
## 4. 現行構造の問題 / What is wrong with today's structure  ← 規模別の価格／価値、値引きの集中箇所、漏れ
## 5. 構造案の比較 / Comparison of structure options        ← structure_compare.py
## 6. 価格メトリクスの評価とフェンス / Metric scoring and fences ← 5 基準の採点表、抜け道の点検
## 7. 移行計画 / Transition plan                          ← 新規と既存、上限、時期
## 8. 測定計画 / Measurement plan
## 9. リスク、倫理・法務チェック / Risks, ethics and legal checks
## 10. 次のステップと未確定事項 / Next steps and open questions
## 付録: スクリプト入力 / Appendix: script inputs
```

値引きの常態化も論点なら、7 節の後に「価値の伝達と値引きポリシー」（E の 4 節の内容）を加え、以降の番号を振り直す。

## D. 競合の値下げへの対応 / Responding to a competitor's price move

```
# {競合} の価格変更への対応方針 / Response to {competitor}'s price move
## 1. 推奨事項 / Recommendation                         ← 無視・選択的対抗・全面対抗・価値の強化のどれか、範囲、期限
## 2. 状況の整理 / Situation                              ← 競合の動き、狙い、影響を受ける顧客と数量
## 3. 対応判断の問い / Response decision questions         ← price-competition.ja.md の判断の流れに一問ずつ答える
## 4. 反応的価格変更の損益分岐 / Breakeven of a reactive price change ← 失う数量 vs 対抗の費用
## 5. 選択肢の比較 / Options compared                      ← 各案の費用、効果、競合の再反応
## 6. 実施と監視 / Execution and monitoring                ← 対象の限定、シグナル、撤退条件
## 7. リスク、倫理・法務チェック / Risks, ethics and legal checks ← 共謀と受け取られる情報交換、略奪的価格
## 8. 次のステップと未確定事項 / Next steps and open questions
```

## E. 値引き・価格ポリシーの設計 / Discount and pricing policy

```
# {事業} 価格ポリシー / {Business} pricing policy
## 1. 推奨事項 / Recommendation
## 2. 現状 / Current state                              ← 価格ウォーターフォール、実売価格（ポケット価格）のばらつき
## 3. 問題の診断 / Diagnosis                             ← 値引きが何と交換されているか、買い手の学習
## 4. ポリシー設計 / Policy design                         ← ギブ・ゲット、承認権限、値引きしないもの、例外の記録
## 5. 値上げ・販促のルール / Rules for increases and promotions
## 6. 導入と定着 / Rollout and adoption                    ← 営業への説明、インセンティブ、移行期間
## 7. 測定計画 / Measurement plan
## 8. リスク、倫理・法務チェック / Risks, ethics and legal checks
## 9. 次のステップと未確定事項 / Next steps and open questions
```

## F. 価格決定の組織・プロセスの診断 / Pricing capability assessment

```
# {組織} 価格決定の能力診断 / {Organization} pricing capability assessment
## 1. 総合評価と優先課題 / Overall assessment and priorities
## 2. 診断の範囲と根拠 / Scope and evidence
## 3. 観点別の診断 / Findings by dimension                  ← 組織・役割、プロセス、データ・ツール、インセンティブ、文化
## 4. 優先課題と打ち手 / Priority gaps and actions
## 5. ロードマップ / Roadmap                              ← 90 日、6 か月、1 年
## 6. 次のステップと未確定事項 / Next steps and open questions
```

## 参考文献

[1] Nagle, T. T., & Müller, G. (2018). *The Strategy and Tactics of Pricing: A Guide to Growing More Profitably* (6th ed.). Routledge.
- 第1章〜第12章（pp. 1–316）。

雛形の節の順序は、[1] の価値カスケードに沿っている（価値の推定 → 構造 → 水準 → ポリシー → 競争）。雛形そのもの（節の分け方、見出し）は、このスキルのために作ったものであり、[1] にはない。
