---
name: pptx-export
description: >-
  Export a generated Google Slides deck to PowerPoint (.pptx) via the Drive API,
  preserving it exactly as generated, saved locally and optionally archived in
  the deck's Drive folder. Invoked by the generation skills when the user chooses
  PPTX at intake, and runs standalone on any accessible deck URL.
  Use for: PPTX でも出力して, PowerPoint 形式でほしい, パワポで納品,
  export to PowerPoint.
  Not: authoring or editing PPTX files directly (document-skills:pptx); QA, which
  runs on the Slides deck via slide-qa before export.
---

*[English](SKILL.md)*

# 生成済みデッキの PPTX エクスポート

## 重要事項

- **エクスポートはスナップショットであり、リンクされたコピーではない。**
  エクスポート時点のデッキをそのまま写し取る。必ずビジュアル QA と修正ループが
  **終わった後**にエクスポートし、デッキを再生成したら毎回再エクスポートする。
  その際は古い `.pptx` を先に Drive フォルダから削除する（旧版デッキと同じルール）。
- **修正は仕様に対して行い、.pptx には決して行わない。** 欠陥を見つけたら元の
  生成スキルに戻り、仕様を修正して再生成し、QA を選択していたなら再実行してから、
  改めてエクスポートする。エクスポート済みファイルを編集すると、正本から
  分岐してしまう。
- **すべてのコマンドは slide-forge ルートを cwd として実行する** —
  インストール済みプラグインから実行する場合は `${CLAUDE_PLUGIN_ROOT}`、
  ローカルクローンでは `/path/to/slide-forge`。認証と venv はリポジトリルートで
  共有される（`config/`、`.venv`）。
- **PPTX をエクスポートするかどうかは生成時に確定する。** インテイクの出力形式の
  質問（`references/interactive-intake.md` §2）で決まり、既定は Google Slides
  のみ。既存デッキ URL に対するスタンドアロン実行ではインテイクは不要。
- **`config/settings.json` の `output: local` ならエクスポートは自動。**
  `build_deck.py` / `render_deck.py` が毎回 `localOutputDir` へ書き出すので、
  PPTX の質問はせず、二重にエクスポートもしない — 生成側が出力したパスを
  報告する。スタンドアロン実行や手編集後の取り直しには引き続き本スキルを使う
  （`references/settings.ja.md`）。
- **ゼロからの PPTX 作成は別の仕事である。** ユーザーが（Google Slides を介さず）
  PPTX を直接作成・編集したい場合は、本スキルではなく `document-skills:pptx` に
  引き継ぐ。

## クイックリファレンス

| タスク | コマンド |
|------|---------|
| エクスポート（`localOutputDir`、既定は `out/pptx/<デッキ名>.pptx` に保存） | `.venv/bin/python scripts/export_pptx.py <URL or ID>` |
| 明示したパスへのエクスポート | `--out path/to/deck.pptx` |
| デッキの Drive フォルダにも保管 | `--folder <Drive フォルダ URL/ID>` |

`files.export` の 10MB 制限を超えるデッキは自動的に `exportLinks` に
フォールバックする — フラグは不要。

## ワークフロー

1. **デッキが最終版であることを確認する。** 生成スキルから呼ばれた場合、これは
   生成が成功し、QA を選択していたなら `slide-qa` のループが完了して
   クリーンアップ済みであることを意味する。スタンドアロンでは何も聞かず、
   URL が指す内容をそのままエクスポートする。
2. **エクスポートする。** デッキの Drive フォルダがある場合はそれを渡し、
   `.pptx` を仕様や図のソースの隣に置く（Drive フォルダルール）:

   ```bash
   .venv/bin/python scripts/export_pptx.py "<deck URL>" --folder "<folder URL>"
   ```

3. **報告する。** ローカルパス、ファイルサイズ、（アップロードした場合は）
   Drive フォルダ URL を、生成報告のデッキ URL と併せて伝える。

## 再現性の注意点（該当する場合は報告に明記する）

エクスポートは Google 自身のコンバーターによるため、レイアウトと座標は正確に
引き継がれる — ただしファイルは PowerPoint という別のレンダリングエンジンで
開かれる:

- **フォントは閲覧者のマシンに存在する必要がある。** Google Fonts（Noto Sans JP
  など）でスタイルされたデッキは、ローカルにインストールされていなければ代替
  フォントにフォールバックし、改行位置がずれることがある。デッキのフォントが
  システムフォントでない場合はその旨を伝える。
- **Google 固有の機能は劣化する**: リンクされた Sheets のグラフは静止画像になり、
  スピーカーノートの書式は簡略化されることがあり、アニメーションは引き継がれない
  （slide-forge のデッキはアニメーションを使わないため、問題になることはまずない）。
- エクスポートしたファイルは再検査しない — QA はすでに Slides デッキ上で実施
  済みで、コンバーターは決定的である。ユーザーから PowerPoint での表示問題の
  報告があった場合は、まず上記のフォント代替を疑う。
