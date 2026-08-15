# 登録テンプレートからの Google Slides 生成

*[English — normative skill](SKILL.md)*

この日本語文書は運用概要であり、実行時の正本は `SKILL.md` と
`references/workflow-contract.md` である。Claude Code を主ホストとし、Codex と
Antigravity も同じ `skills/` と Python エンジンを利用する。

## 適用範囲

- 登録済みテンプレートから新しいデッキを作る
- 未登録のマスターを検査・登録してから作る
- 完全なソースSpecがあるslide-forge管理デッキを、全ページ置換の明示承認後に
  URLを維持したまま再構築する

マスターなしは `google-slides`、新規マスター作成は `template-forge`、既存デッキの
空画像枠だけを埋める場合は `image-slots` を使う。

## 必須ルール

- ユーザー所有デッキを直接更新する前に `snapshot_version.py` を実行する。
- `build_deck.py --into` は全ページを置換する。1枚修正・挿入・任意の既存デッキには
  使用しない。完全なSpec、生成済みデッキであることの確認、snapshot成功、全ページ
  置換の明示承認をすべて必須とする。
- 未指定の分岐だけを質問し、既に指定された内容を聞き直さない。
- 作成前に枚数、各ページのレイアウト、全アクションタイトルの承認を得る。
- API書込み前に `--dry-run --strict` を通す。
- マスターのロゴ、フッター、装飾を重ね描きしない。
- 不具合はソースを直して再生成する。
- API成功をVisual QAの代わりにしない。

## 段階的な参照読込

選択した `SKILL.md` は最後まで読むが、referenceを一括で読み込まない。

| 必要な作業 | 読むもの |
|---|---|
| インテイク | `interactive-intake.md` の該当節 |
| Spec／placeholder／画像枠 | `template-schema.md` |
| Canvas／connector | `diagrams.md` の該当節 |
| chart／table | `charts.md` の該当component |
| business framework | `patterns.md` の該当component |
| page skeleton／density | `slide-patterns.md` の該当skeleton |
| 画像 | `images.md` の該当節 |
| API問題 | `api-notes.md` を検索し、未解決時だけ `google-slides-api.md` |
| 大規模・複雑デッキ | `parallel-generation.md` の該当節 |
| Visual QA | `slide-qa/SKILL.md` と `validation.md` のGate 2 |

## 実行フロー

1. `.venv/bin/python scripts/list_templates.py` で環境と候補を確認する。
2. テンプレート、用途、枚数、アウトライン、密度、Drive、QA、納品形式の未指定分だけを確定する。
3. 枚数、レイアウト、全アクションタイトルを提示して承認を得る。
4. 未登録URLのときだけ `inspect_template.py --emit ... --thumbnails ...` を実行し、画像を目視する。
5. Specを作り、次のオフライン検証を通す。

```bash
.venv/bin/python scripts/build_deck.py \
  --template templates/<id>.json --spec out/<deck>/deck.json \
  --dry-run --strict
```

6. Driveフォルダを先に作り、デッキを生成し、Specと図の編集ソースをアップロードする。
7. QAを選択した場合は `slide-qa` を実行し、最後にローカルQAファイルを削除する。
8. 最終版に対してだけPPTXまたは明細Spreadsheetを生成し、URL、検証、QA範囲を報告する。

通常は17枚以下を単一エージェントで作る。18〜20枚以上、または独立した複雑図が
複数ある場合に限りファンアウトを検討する。分割時は1エージェント2〜3枚、参照は
最大2セクションとする。

QA初回は全ページを確認する。修正後は変更ページと前後ページを確認し、共通レイアウト、
マスター、テーマ、フッター、ページ番号を変えた場合だけ影響ページまたは全ページへ広げる。
