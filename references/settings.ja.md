*[English](settings.md)*
# 設定 — `config/settings.json`

これまで生成のたびにヒアリングで決めていた 2 つの判断を、ここで一度だけ決めて
以降のすべての実行に効かせる。

| キー | 値 | 既定 | 何を切り替えるか |
|---|---|---|---|
| `imageGeneration` | `true` / `false`（`"on"` / `"off"` も可） | `true` | Gemini による画像生成をそもそも行うか — `aiImage` 図、`scripts/images.py`、`scripts/fill_image_slots.py` |
| `output` | `"google"` / `"local"` | `"google"` | 成果物の置き場所: Google Drive / Google Slides か、ローカルフォルダへの PowerPoint（`.pptx`）か |
| `localOutputDir` | パス | `"out/pptx"` | `output` が `local` のときの書き出し先。相対パスはリポジトリルート基準 |

`config/` は gitignore 済みなので、このファイルはチェックアウトごとに閉じていて
コミットされない。雛形として `config/settings.example.json` をコミットしてある。
**既定値はこのファイルが無かった頃の挙動そのもの**なので、`settings.json` が
無い状態では何も変わらない。

## 確認と変更

これらを選択式の対話でまとめて扱うのが `settings` スキル
（Claude Code では `/slide-forge:settings`、他ホストでは `settings` スキル）。
現在値の表示 → 質問 → 書き込み → 読み戻しまでを行う。設定する値が既に
決まっているときは、以下のコマンドを直接使う。

```bash
.venv/bin/python scripts/settings.py --show          # 現在値と、その出どころ
.venv/bin/python scripts/settings.py --json          # 機械可読

.venv/bin/python scripts/settings.py --image-generation off
.venv/bin/python scripts/settings.py --output local --local-dir ~/decks
```

優先順位は弱い順に **既定値 → `config/settings.json` → 環境変数 →
コマンドラインフラグ**。

```bash
GSLIDES_IMAGE_GENERATION=off  GSLIDES_OUTPUT=local  GSLIDES_LOCAL_DIR=~/decks
```

`build_deck.py` と `render_deck.py` は、ファイルを触らず 1 回だけ切り替える
`--output google|local` を受ける。画像生成側に実行単位のフラグは無い
（デッキが `aiImage` を宣言するかどうかがすべて）。

Python から:

```python
import settings
settings.image_generation_enabled()      # bool
settings.output_target()                 # "google" | "local"
settings.local_output_dir()              # 絶対パス
```

## `imageGeneration: off` のとき

3 か所で、いずれも**課金も書き込みも発生する前に**止める。

- `images.generate()` が `ImageGenerationError` を投げる。キャッシュ参照より
  前に判定する — この設定は「クォータを使うかどうか」ではなく「AI 画像を
  出すかどうか」のスイッチだから。
- `build_deck.py` が spec 検証の時点で `aiImage` を弾く。デッキを作りかけた
  ところで落ちるのではなく、`--dry-run` がオフラインで報告する。
- `fill_image_slots.py` はデッキを読む前に停止する（埋める枠がすべて AI 生成
  のため）。

図形で描く手段 — `scripts/illustrations.py`、`scripts/patterns.py`、
`scripts/diagrams.py` — はこの設定の影響を受けず、API キーも要らない。OFF の
ときはキーを要求せず、こちらを提案する。

## `output: local` のとき

エンジンはどちらの設定でも Google Slides API で描く。つまり `local` が変える
のは**成果物であって生成方法ではない**。生成が成功したあとにデッキを
`localOutputDir` 配下へ `.pptx` として書き出し、生成された Slides デッキは
編集可能な原本として意図的に残す（こちらからは何も削除しない）。

```
生成（Slides API） → .pptx 書き出し → <localOutputDir>/<デッキ名>.pptx
                                       ＋ デッキは Drive の URL にそのまま残る
```

書き出しの失敗は報告するだけで致命傷にはしない。その時点でデッキは出来て
いるし、`scripts/export_pptx.py` で取り直せる（`--out` 省略時は同じフォルダに
書く）。

ビジュアル QA（`slide-qa`）はサムネイルを Slides API から取るため、引き続き
Slides デッキに対して走る。**QA → 書き出し**の順は崩さないこと（書き出しは
その時点のスナップショットなので、作り直したら取り直す）。

## ヒアリングへの影響

`references/interactive-intake.ja.md` は出力形式と AI 画像を質問する。
**先に設定を読み、設定が答えている質問はしない**こと。

- `output: local` → 「PowerPoint にも書き出しますか？」は聞かない（すでに
  それが成果物）。最終報告ではデッキ URL と一緒にローカルパスを伝える。
- `output: google` → PPTX の質問は従来どおり（PPTX 配布が想定される場合のみ）。
- `imageGeneration: off` → `aiImage` を提案せず、API キーの有無も聞かない。
  図形で描く表現を提案する。
