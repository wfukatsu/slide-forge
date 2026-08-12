---
description: >-
  Google Slides デッキ生成を一連の流れで実行する: スキル選択 → インテイク →
  アウトライン承認 → 仕様作成 → オフライン検証 → 生成 → ビジュアル QA（任意・既定は実行）
  → 検証ファイル削除 → 追加納品物（PPTX / 見積もり明細スプレッドシート、任意）→ 報告
argument-hint: "[テーマ / テンプレート URL / 素材パス / 顧客名など]"
---

*[English](forge.md)*

# /forge — デッキ生成パイプライン

`$ARGUMENTS` を出発点に、slide-forge の生成フローを**途中で止めずに一続きで**実行する。
作業ディレクトリは slide-forge ルート（プラグインでは `${CLAUDE_PLUGIN_ROOT}`、
ローカルクローンでは `/path/to/slide-forge`）。

## Step 1: 生成スキルを選ぶ（ルーティング）

引数と文脈から 1 つ選ぶ。判断がつかないときだけ `AskUserQuestion` で 1 回確認する。

| 依頼の形 | 使うスキル |
|---|---|
| Scalar の会社・製品・機能紹介デッキ | `scalar-product-slides` |
| 顧客課題起点の Scalar ソリューション提案書 | `scalar-proposal-slides` |
| 再利用可能な1枚単位のスライドテンプレートを作る | `slide-template-creator` |
| B2B 商談の関与者マップ・ディスカバリー整理 | `b2b-account-maps` |
| テンプレート/マスター URL がある、登録テンプレートで作る（既定） | `google-slides-template` |
| コーポレートマスター無しでゼロから作る | `google-slides` |

以降は選んだスキルの SKILL.md に従う。このコマンドの役割は、次の順序を
飛ばさず・止まらず通すことにある。

## Step 2: 前提のインテイク（1〜2 往復）

`references/interactive-intake.md` に従い、未指定の前提だけをまとめて聞く。
**「検証」の質問（生成後にビジュアル QA を行うか）を必ず含める** — 既定・推奨は
「実行する」。PPTX での納品・配布が想定されるとき（提案書・顧客向け資料）は
「出力形式」の質問（PPTX も書き出すか）を、費用・構成の数字が載るときは
「明細資料」の質問（見積もり明細をスプレッドシートでも出すか）も同じセットに
含める。ユーザーが既に指定済みの項目、「おまかせ」の項目は聞かず、採用した
前提を 1 行で明示する。

## Step 3: アウトライン承認ゲート（省略禁止）

枚数・レイアウト・各スライドのアクションタイトルを本文で提示し、承認を得る。
**承認後は Step 7 の報告まで確認を挟まず通す。**

## Step 4: 仕様作成とオフライン検証

スキルの手順どおり仕様（JSON またはデッキモジュール）を書き、生成前に必ず通す:

```bash
.venv/bin/python scripts/build_deck.py --template templates/<id>.json --spec deck.json --dry-run --strict
# コードファーストの場合: .venv/bin/python scripts/validate_layout.py deck.py
```

12 枚超は `references/parallel-generation.md` のファンアウトを使う。

## Step 5: 生成

Drive フォルダを作成してから生成し、仕様・図のソースをフォルダに集約する
（Drive フォルダルール）。生成失敗時は作りかけを Drive から削除して作り直す。

## Step 6: ビジュアル QA と後片付け（Step 2 の選択で分岐）

- **「実行する」（既定）**: `slide-qa` スキルの手順で実施する —
  サムネイル取得 → チェックリストで目視 → 不具合があれば仕様を直して再生成
  （旧デッキは Drive から削除）→ **最後に必ず検証ファイルを削除する**:

  ```bash
  .venv/bin/python scripts/cleanup_qa.py
  ```

- **「スキップする」**: QA を行わず Step 6.5 へ。報告に **QA 未実施**であることと、
  後から `slide-qa` スキルで検証できることを明記する。

## Step 6.5: 追加の納品物（Step 2 の選択で分岐）

- **「PPTX も書き出す」を選んだ場合**: デッキが確定した後（QA・修正ループの
  完了後）に `pptx-export` スキルで実行する:

  ```bash
  .venv/bin/python scripts/export_pptx.py "<デッキ URL>" --folder "<Drive フォルダ URL>"
  ```

  QA の修正で再生成した場合も、エクスポートは必ず**最終版に対して**行う。

- **「明細資料を出す」を選んだ場合**: `spreadsheets` スキルで見積もり明細を
  生成する（スペック作成 → `--dry-run` → `build_sheet.py --gsheet --folder
  "<Drive フォルダ URL>"`）。明細の合計とスライドの費用数字を一致させ、
  CSV エクスポートで計算結果を確認する。

## Step 7: 報告

1. デッキ URL と Drive フォルダ URL（PPTX はローカルパス、明細スプレッドシートは
   Spreadsheet URL と xlsx パスも）
2. QA の結果（検査したページ範囲、直した内容と直していない内容）または QA 未実施の明記。
   検証ファイルを削除済みであることも添える
3. 仕上げの確認（`references/interactive-intake.md` §4）: 確定する / 文言を直す /
   図の見せ方を変える / 枚数を調整する
