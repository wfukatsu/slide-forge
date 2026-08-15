---
name: forge
description: >-
  Google Slides デッキ生成を、スキル選択から検証・納品まで共通契約に沿って実行する
  軽量なパイプラインルーター。
---

# /forge — デッキ生成パイプライン

Claude Code の `commands/forge.md` と共有スキルを正本とする。Codex ではこのスキルを
薄いエントリーポイントとして使い、`references/workflow-contract.md` の共通工程を
実行する。

## 1. 生成スキルを1つ選ぶ

| 依頼 | スキル |
|---|---|
| Scalar の会社・製品・機能紹介 | `scalar-product-slides` |
| 顧客課題起点の Scalar 提案書 | `scalar-proposal-slides` |
| 再利用可能な1枚テンプレート | `slide-template-creator` |
| B2B 関与者／ディスカバリーマップ | `b2b-account-maps` |
| 登録済みテンプレート／マスターを使用 | `google-slides-template` |
| コーポレートマスターなし | `google-slides` |

選んだスキルの `SKILL.md` だけを最後まで読む。候補スキルを比較目的で全件読み込まない。

## 2. 共通契約を実行する

`references/workflow-contract.md` に従い、次の状態を順番に完了する。

```text
route → intake → approve → author → validate → generate → verify → deliver
```

- 未指定の分岐だけをまとめて質問する。QAは既定で実行。
- 提案書・配布資料は `print`、登壇資料は `presentation` 密度。
- 枚数、レイアウト、全アクションタイトルの承認を省略しない。
- 承認後は通常の確認を挟まず、納品と報告まで進める。
- API書込み前にオフラインの strict 検証を通す。
- QAを選んだ場合は `slide-qa` に委譲し、最後にローカルQAファイルを削除する。
- PPTXや明細表は最終デッキ確定後に対応スキルへ委譲する。

## 3. コンテキストを制御する

共通契約のルーティング表を使い、選択した図表・画像・API課題に必要なreferenceの
該当セクションだけを読む。通常は17枚以下を単一エージェントで作成する。18〜20枚以上、
または独立した複雑図が複数ある場合だけ `parallel-generation.md` を適用する。
