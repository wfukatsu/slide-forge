---
name: image-slots
description: >-
  Fill the empty image slots of an **existing** Google Slides deck with
  AI-generated pictures: find the frames the template reserves for a picture
  (PICTURE-family placeholders, empty image elements left in a layout, frames
  the deck reuses), generate a picture composed for each frame's shape, and
  place it so it fills the frame. Runs standalone on any accessible deck URL,
  including decks slide-forge did not generate, and works without a registered
  template by analyzing the deck itself.
  Triggers: "表紙に絵を入れて", "章扉の画像枠を埋めて", "空いている画像枠に画像を生成",
  "このデッキに画像を足して", "image-slots", "fill the image placeholders",
  "generate images into the slots".
  Out of scope: decks still being generated from a deck spec (put `aiImage`
  in the spec and let build_deck.py fill the slot — see below), drawing
  diagrams with shapes (google-slides-template's figure families), replacing
  pictures that are already in place, and visual verification (slide-qa).
---
*[English](SKILL.md)*

# 既存デッキの画像スロットを埋める

作業ディレクトリ: slide-forge のルート — インストール済みプラグインから実行する
場合は `${CLAUDE_PLUGIN_ROOT}`、ローカルクローンなら `/path/to/slide-forge`。

## 重要

- **デッキがまだ生成途中なら、仕様パスを優先する。** slide-forge のデッキ仕様から
  生成されるデッキなら、`x`/`y`/`w`/`h` を省略した `aiImage` figure を仕様に足して
  再生成する — `build_deck.py` がスロットへ収める。これで仕様が Source of Truth の
  まま保たれる。これはリポジトリの恒常ルールである（slide-qa の
  「修正は成果物ではなくソースに対して行う」を参照）。**このスキルは背後に仕様が
  ないデッキ**、あるいは既に存在していて URL を保たなければならないデッキに
  画像を足すためのもの。
- **本番のデッキに書き込む。** 先にバージョンスナップショットを取り、
  リビジョン ID を報告する:
  `.venv/bin/python scripts/snapshot_version.py <URL>`
- **必ず `--dry-run` を先に実行**し、どのスライドのどの枠が埋まるか、それぞれが
  使うプロンプトとともにユーザーへ見せてから、生成に進む。
- **既に画像が入っているスロットには決して触れない。** 既存画像の差し替えは
  スコープ外 — それが意図なら、先に手で削除してもらう。
- **`GEMINI_API_KEY` が必須**で、画像モデルの**無料枠クォータはゼロ**。
  キーは課金が有効なプロジェクトのものでなければならない
  （`references/images.md`）。
- **画像生成はツールキット全体で OFF にできる**
  （`config/settings.json` の `imageGeneration: false`）。このスキルを提案する
  前に `.venv/bin/python scripts/settings.py --show` で確認する。OFF のとき
  `fill_image_slots.py` はデッキを読む前に停止するので、ユーザーが ON にするか、
  枠は空のままにする（`references/settings.ja.md`）。
- **完了後はサムネイルで検証する。** API レスポンスが正常でも、被写体が切れた
  画像は検出できない。`slide-qa` スキルへ引き継ぐ。

## クイックリファレンス

| タスク | 使うもの |
|------|-----|
| 埋められる枠を一覧する（画像 API 呼び出しなし、変更なし） | `.venv/bin/python scripts/fill_image_slots.py <URL> --dry-run` |
| 空いている枠をすべて埋める | `.venv/bin/python scripts/fill_image_slots.py <URL>` |
| 1 スライドだけ、被写体を明示する | `… <URL> --slide 3 --prompt "夜間のデータセンター"` |
| 1 スライドに複数の枠があるとき選ぶ | `… --slot 1`（0 始まり、サーベイの列挙順） |
| デッキ自身の使われ方から*推測*しただけの枠も使う | `--include-inferred`（既定はオフ — 後述） |
| イラストのスタイルを変える | `--style isometric`（`flat_vector` / `line_art` / `blueprint` / `paper` / `photo`） |
| 書き込み前のスナップショット | `.venv/bin/python scripts/snapshot_version.py <URL>` |
| スロットとは何か、画像はどう構図されるか | `references/images.md` |

## 枠はどう見つかるか

テンプレート登録（`references/template-schema.md`）と同じ 3 つのソースを使う:

1. スライド上の **PICTURE 系プレースホルダ**（`PICTURE` / `CLIP_ART` /
   `DIAGRAM` / `MEDIA` / `OBJECT` / `SLIDE_IMAGE`）
2. スライド上の**空の画像要素** — 何も描画されないのだから、装飾ではなく
   スロットである
3. どちらもなければ、**レイアウト**の `imageSlots`。大きい枠から順

ソース 1 と 2 は**宣言**である — テンプレートが「ここには画像が入る」と言っている。
`imageSlots` が保持しうる第 3 の種類の枠、すなわち他のスライドが同じ位置に画像を
置いていることから*推測*された枠は、**既定では除外**される: 実際のデッキでは
この推測は通常のコンテンツスライドの本文領域に一致し、それを全部埋めると
デッキが画像で埋め尽くされてしまう。78 スライドのテンプレートで測定したところ、
推測が 39 の枠を提示するのに対し、既定で埋められる枠は 0 だった。本当にそれが
欲しいときだけ、実行ごとに `--include-inferred` でオプトインする。

スライド自身の枠がレイアウトの枠に勝つ。自前のプレースホルダを持つスライドは、
その元になったレイアウトより具体的だからだ。サーベイはレイアウトの枠を大きい順に
列挙する。スライド上で見つかった枠はスライドが保持する順に並ぶので、`--slot` を
選ぶときは順序を仮定せず、`--dry-run` の出力を読む。

**画像は枠に流し込まれるのではなく、枠の上に重ねられる。** 空の PICTURE
プレースホルダは消費されない — 画像は枠の座標に作成され、プレースホルダは
その下に残る。何も描画されないが、エディタ上にはまだ存在している。
仕様パス（`build_deck.py`）も同じ挙動をする。

デッキが登録済みテンプレートから生成されたものなら
`--template templates/<id>.json` を渡す — 検証済みのロールとパレットが使われる。
渡さなければデッキをその場で解析するため、このスキルは**どんな**デッキでも動く。

## 何が描かれるか

プロンプトの既定はスライドの**タイトル** — TITLE プレースホルダ、なければ
最上部のテキスト — であり、「第1章 データ基盤の刷新」と題した章扉なら、それを
主題とした画像を求める。本文テキストは意図的に除外している: スライドの箇条書きは
「① 検証 ② 配布 ③ 反映」のように読め、描画指示としては貧弱だからだ。実行ごとに
`--prompt` で上書きできる。**テキストがまったくない**スライドは推測せず、
メッセージを出してスキップする — そうしたスライドには `--prompt` を渡す。

画像は枠の形に合わせて生成される: モデルが対応する中で最も近いアスペクト比を選び、
さらに fill がどの辺を何パーセント切り落とすかを名指しするプロンプト指示を加えて、
被写体が生き残るようにする。その後 `fit="cover"` で配置され、枠を過不足なく埋める。
詳細は `references/images.md`。

生成は (モデル, スタイル, アスペクト比, プロンプト全文) でキャッシュされるため、
再実行しても再描画・再課金は起きない。`--force` で上書きできる。

## フロー

1. **スナップショット** — `snapshot_version.py <URL>`。報告用にリビジョン ID を控える。
2. **サーベイ** — `fill_image_slots.py <URL> --dry-run`。スライド番号・枠・
   プロンプトをユーザーへ見せる。すべてが「already has a picture」であるか
   枠が存在しないなら、そう伝えて止める — 枠をでっち上げない。
3. **主題の確認。** 自動導出されたプロンプトはスライドのテキスト由来で、
   しばしば直訳的すぎる。主題が画像として不出来に読める場合（長い本文、数字、
   製品名）は、スライドごとに `--prompt` を設定するよう提案する。
4. **埋める** — `--dry-run` なしで実行する。配置ごとに、選ばれたアスペクト比と
   構図ノートが表示される。
5. **QA** — デッキ URL に対して `slide-qa` スキルを起動し、画像の被写体が
   切れていないか、レイアウトのテキストと喧嘩していないかを確認する。
6. **報告** — 埋めたスライド、使ったスタイル、スナップショットのリビジョン ID、
   デッキ URL。

## トラブルシューティング

| 症状 | 原因と対処 |
|---|---|
| `Nothing to fill` | すべての枠に既に画像があるか、レイアウトが枠を確保していない。`inspect_template.py <URL>` で確認し、代わりにデッキ仕様で座標を指定して画像を置く |
| `skipped: no text on this slide to build a prompt from` | タイトルのないスライド — `--prompt` を渡す |
| 画像の被写体が切れている | 枠の比率が、モデルが生成できるどの比率からも遠い。中央寄せの単純な被写体を記述した `--prompt` でそのスライドを再実行するか、`--force` で別の描画を得る |
| `HTTP 429 / limit: 0` | API キーのプロジェクトに画像クォータがない — 課金の有効化が必要 |
| 画像が引き伸ばされて / レターボックスに見える | 要報告: 枠は常に `cover` で埋められるので、これはフィット合わせの処理が失敗したことを意味する（作成された画像のサイズを読めないとき、実行時に警告が出る） |
