---
name: settings
description: >-
  Read and change the slide-forge switches in config/settings.json through a
  short multiple-choice dialogue: whether Gemini generates images at all
  (imageGeneration), and whether the deliverable is Google Drive / Google
  Slides or a local folder as PowerPoint (output / localOutputDir). Shows the
  current values, asks with AskUserQuestion, writes via scripts/settings.py,
  then reads the result back.
  Triggers: "設定を変えたい", "設定を確認して", "画像生成をオフにして",
  "Gemini の画像生成を使わない", "出力先をローカルにして", "PowerPoint で出したい",
  "Google Drive に出したい", "slide-forge の設定", "settings", "change settings",
  "turn off AI images", "export locally instead".
  Out of scope: OAuth credentials and API keys (config/credentials.json,
  config/gemini_api_key — never read or write them here), the Drive sales root
  in config/sales.json (scalar-account-plan owns it), per-deck choices such as
  visual QA or template selection (those stay in intake), and exporting an
  existing deck (pptx-export).
---

*[English](SKILL.md)*

# slide-forge の設定

`config/settings.json` にある 2 つのスイッチは全実行に効くので、生成のたびに
ヒアリングするのではなく、ここで一度決める。仕様は `references/settings.ja.md`、
本スキルはその周りの対話を担当する。

| キー | 値 | 効果 |
|---|---|---|
| `imageGeneration` | `true` / `false` | `false` で `aiImage` 図・`scripts/images.py`・`fill_image_slots.py` を拒否する（オフラインで、クォータを使う前に止まる） |
| `output` | `"google"` / `"local"` | `local` は生成のたびにデッキを `localOutputDir` へ `.pptx` として書き出す |
| `localOutputDir` | パス | その `.pptx` の置き場所（既定 `out/pptx`、相対パスはリポジトリルート基準） |

## 重要

- **`config/` の他のファイルには触れない。** `credentials.json`、`token.json`、
  `gemini_api_key` は秘密情報。本スキルが読み書きするのは `settings.json` だけで、
  キーやトークンを出力することはない。
- **変更前に見せ、変更後に読み戻す。** 実行は必ず `--show` で始まり `--show` で
  終わる。何が変わったかをユーザーが目で確認できるようにする。
- **ユーザーが既に言ったことは聞かない。**「画像生成をオフにして」は完結した指示。
  そのまま適用して報告し、もう片方のスイッチは、設定全体を見直したいと言われた
  ときだけ聞く。
- **設定変更が既存デッキを書き換えることはない。** 効くのは次回の生成から。
  作業の途中なら、その旨を一言添える。
- **コマンドは slide-forge ルートを cwd にして実行する** — プラグイン導入時は
  `${CLAUDE_PLUGIN_ROOT}`、ローカルクローンでは `/path/to/slide-forge`。

## クイックリファレンス

| タスク | コマンド |
|------|---------|
| 現在値と、その出どころを表示 | `.venv/bin/python scripts/settings.py --show` |
| 機械可読 | `.venv/bin/python scripts/settings.py --json` |
| 画像生成 OFF / ON | `… scripts/settings.py --image-generation off` / `on` |
| 成果物をローカルの `.pptx` に | `… scripts/settings.py --output local` |
| 成果物を Drive / Slides に | `… scripts/settings.py --output google` |
| ローカルの書き出し先を変える | `… scripts/settings.py --local-dir ~/decks` |

フラグは 1 回の呼び出しにまとめられる。優先順位は弱い順に、既定値 →
`config/settings.json` → `GSLIDES_IMAGE_GENERATION` / `GSLIDES_OUTPUT` /
`GSLIDES_LOCAL_DIR` → `build_deck.py --output`。`--show` が環境変数の上書きを
報告したらそれも伝える（編集しているファイルの値が、その実行で使われる値とは
限らない）。

## 進め方

1. **現在値を表示する。** 質問の `description` にも現在値を織り込み、既知の状態
   に対して選ばせる:

   ```bash
   .venv/bin/python scripts/settings.py --show
   ```

2. **`AskUserQuestion` で聞く** — 1 ラウンドで両方、現在値が分かる形で。
   ユーザーが既に決めているスイッチは質問から外す:

   ```json
   {
     "questions": [
       {
         "header": "画像生成",
         "question": "Gemini による画像生成を使いますか？",
         "multiSelect": false,
         "options": [
           {"label": "使う（現在の設定）", "description": "aiImage 図・images.py・image-slots が使える。課金済みの GEMINI_API_KEY が要る（画像モデルは無料枠クォータが 0）"},
           {"label": "使わない", "description": "AI 画像を一切生成しない。aiImage は検証時に弾かれ、代わりに図形で描く illustrations / patterns を使う。API キーは不要"}
         ]
       },
       {
         "header": "出力先",
         "question": "成果物をどこに出しますか？",
         "multiSelect": false,
         "options": [
           {"label": "Google Drive / Google Slides（現在の設定）", "description": "生成したデッキの URL が成果物。共同編集・コメントができる。PPTX が要るときは pptx-export で個別に書き出す"},
           {"label": "ローカルフォルダ / PowerPoint", "description": "生成のたびに out/pptx へ .pptx を書き出す。デッキ自体は編集可能な原本として Drive に残る（削除はしない）"}
         ]
       }
     ]
   }
   ```

   **現在の設定を先頭に置き「現在の設定」と明記する**（安全な回答が一番上に来る
   ようにする）。「ローカルフォルダ」が選ばれ、置き場所が `out/pptx` でない場合は
   追加の質問でパスを聞く — 自由入力の「その他」がそのままパスになる。

3. **適用する。** 変更はすべて 1 回の呼び出しにまとめる:

   ```bash
   .venv/bin/python scripts/settings.py --image-generation off --output local
   ```

4. **読み戻して報告する** — ファイルパス、確定した値、そして実務上何が変わるか。
   次の 2 点は明示する価値がある:

   - 画像生成 OFF → 以後は `illustrations` / `patterns` / `diagrams` を提案する。
     `aiImage` を含む spec は、書き換えるまでオフライン検証で落ちる。
   - 出力先 local → インテイクから PPTX の質問が消え、生成時にデッキ URL と並んで
     ローカルパスが出る。ビジュアル QA は引き続き Slides デッキに対して走る
     （書き出しはスナップショットなので、QA → 書き出しの順）。

## 他のスキルからここへ来たとき

生成スキルはインテイク（`references/interactive-intake.ja.md`）でこの設定を読み、
設定が答えている質問を落とす。作業の途中で変更を頼まれたら本スキルを実行し、
新しい値のまま中断したワークフローに戻る。デッキを既に生成済みでない限り、
作り直しは不要。
