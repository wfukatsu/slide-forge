---
description: slide-forge の共通デッキ生成ワークフローを最後まで実行する
argument-hint: "[テーマ / テンプレートURL / 素材パス / 顧客名など]"
---

*[English](forge.md)*

# /forge — デッキ生成パイプライン

Claude Code をこのコマンドの主ホストとする。`$ARGUMENTS` を起点に、
`${CLAUDE_PLUGIN_ROOT}/references/workflow-contract.md` の共通契約を実行する。

## 生成スキルを1つ選ぶ

| 依頼 | スキル |
|---|---|
| Scalar の会社・製品・機能紹介 | `scalar-product-slides` |
| 顧客課題起点の Scalar 提案書 | `scalar-proposal-slides` |
| 再利用可能な1枚テンプレート | `slide-template-creator` |
| 素材からの現状分析・課題特定（SWOT、PEST、5 フォース、なぜなぜ、ロジックツリー、ギャップ分析など） | `current-state-analysis` |
| 分析フレームワークのテンプレート自体の追加・変更 | `analysis-template-creator` |
| B2B 関与者／ディスカバリーマップ | `b2b-account-maps` |
| 顧客から情報を集めるためのスライド（ヒアリング議題、記入シート、イベントアンケート） | `hearing-slides` |
| nexus-architect のレポート・UI モックの説明 | `nexus-report-slides` |
| 登録テンプレート／マスターを使用 | `google-slides-template` |
| コーポレートマスターなし | `google-slides` |

選択したスキルだけを最後まで読み、共通契約に従う。未選択の生成スキルは読み込まない。
質問は未指定の分岐だけに限定し、QA（既定は実行）、必要な納品形式、密度
（提案・配布は `print`、登壇は `presentation`）を確定する。先に
`scripts/settings.py --show` を読む — 画像生成と成果物の出力先は設定済みの
ことがある。変更を頼まれたら `settings` スキルに回す。

枚数、レイアウト、全アクションタイトルの承認は必須。承認後はオフライン検証、生成、
選択したQA、任意成果物、後片付け、報告まで通常の確認を挟まず進める。
