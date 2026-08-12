---
name: drawio-diagrams
description: >-
  Create dense, complex diagrams — cloud architecture (AWS/GCP/Azure), data
  flow, and network diagrams — as draw.io (.drawio) files, export them to PNG
  headlessly, QA them visually, and insert the PNG into Google Slides decks
  built with the slide-forge skills. The editable .drawio source is archived in
  the deck's Drive folder so the user can keep editing it in draw.io.
  Triggers: "draw.io で図を作って", "drawio", "クラウド構成図", "データフロー図",
  "ネットワーク構成図", "緻密な構成図", "cloud architecture diagram",
  "data flow diagram", or when a diagram is too dense for native Slides shapes.
---
*[English](SKILL.md)*

# Google Slides のための draw.io 図

## 重要

- **スコープ**: `diagrams.py` のネイティブシェイプでは密度が足りない図 —
  2 階層以上ネストしたコンテナ（VPC/サブネット）、10 ノード以上、15 エッジ以上、
  あるいはグループ枠つきの公式スタイルのクラウドベンダーアイコンが欲しい場合。
  単純な概念図・フロー図なら `google-slides` スキルの `diagrams.py` に留まる。
  振り分け表は `references/drawio.md` の冒頭にある。
- **作業ディレクトリ**: slide-forge のルート — インストール済みプラグインから実行する場合は `${CLAUDE_PLUGIN_ROOT}`、ローカルクローンなら `/path/to/slide-forge`（本文中のリテラルパスはローカルクローンを前提とする）。
- **drawio デスクトップ CLI が必要**（`brew install --cask drawio`;
  PATH 上の `drawio` またはアプリバンドル）。macOS でのヘッドレス動作を検証済み。
- **書き出した PNG のビジュアル QA は必須。** シェイプ名の誤り
  （`resIcon` / `prIcon` / azure2 の SVG パス）はエラーにならず、
  ただの色つき四角として描画される — 名前は決して推測せず、必ず調べる
  （`references/drawio.md` § シェイプ名の調べ方）。
- **納品物は 3 点**: PNG を挿入したスライド、書き出した PNG、編集可能な
  `.drawio` ソース。`.drawio` と PNG はデッキの Drive フォルダにアップロードし
  （`scripts/drive_folder.py upload`）、ユーザーが後から図を編集できるようにする
  — PNG だけでは行き止まりになる。
- **ユーザーが既に持っている既存デッキ**に挿入するときは、先に
  `scripts/snapshot_version.py <URL>` を実行する（他の slide-forge スキルと
  共通の「編集前にバージョンを記録する」ルール）。

## クイックリファレンス

| タスク | 場所 |
|------|-------|
| 作図ガイド + 検証済みスタイルレシピ（AWS/GCP/Azure、グループ、エッジ） | `references/drawio.md` |
| .drawio を PNG へ書き出す | `.venv/bin/python scripts/drawio_export.py <in.drawio> [--out out/diagrams/x.png] [--scale 2]` |
| シェイプ名を調べる（決して推測しない） | `grep -ao 'mxgraph\.aws4\.[a-z0-9_]*' /Applications/draw.io.app/Contents/Resources/app.asar \| sort -u` |
| デッキ仕様へ PNG を挿入する | `{ "type": "image", "x": …, "y": …, "w": …, "h": …, "source": "out/diagrams/x.png", "fit": "contain" }` |
| ソースをデッキの Drive フォルダへアーカイブする | `.venv/bin/python scripts/drive_folder.py upload <FOLDER> x.drawio out/diagrams/x.png` |
| 既存デッキ編集前のバージョンスナップショット | `.venv/bin/python scripts/snapshot_version.py <URL>` |

## Phase 0: 環境チェック

```bash
which drawio || ls /Applications/draw.io.app/Contents/MacOS/draw.io
```

どちらも存在しなければ、ユーザーに `brew install --cask drawio` の実行を依頼する。
Python 側は他のスキルと同じく、slide-forge 共有の venv（`.venv`）を使う。

## Phase 1: .drawio を書く

`references/drawio.md` に従い、mxGraph XML を直接書く:

- 必須の `id="0"` / `id="1"` ルートセルを持つファイル骨格
- 座標は px。コンテナの子は親相対座標を使う
- ベンダーアイコン: AWS は `resourceIcon` + `resIcon`、GCP は `hexIcon` + `prIcon`、
  Azure は `image=img/lib/azure2/…` — 検証済みレシピをコピーし、
  使ったことのない名前は必ず調べる
- エッジは常に `source`/`target` で接続し（自由座標は使わない）、
  ラベルは `edgeLabel` の子頂点で付ける
- 描画範囲はスライド上の挿入領域のアスペクト比に合わせる（全面図なら
  16:9〜2:1）。PNG 書き出しはコンテンツでクロップされるため、ページサイズは無関係

ファイルはデッキ仕様の隣に保存する（例: `<deck-dir>/figures/arch.drawio`）。

## Phase 2: PNG へ書き出す

```bash
.venv/bin/python scripts/drawio_export.py <deck-dir>/figures/arch.drawio \
    --out out/diagrams/arch.png --scale 2
```

全面図では `--scale 2` が最低ライン（8in で挿入するなら幅 1600px 以上を目標）。
背景に色が敷かれたデッキには `--transparent`、複数ページのファイルには
`--page N` を使う。

## Phase 3: ビジュアル QA（必須）

Read ツールで PNG を開き、`references/drawio.md` 末尾のチェックリストを回す:
ただの四角になったアイコン（シェイプ名の誤り）、ラベルの重なり、無関係な
シェイプを横切るエッジ、コンテナからはみ出す子、挿入サイズでの可読性。
問題がなくなるまで XML を修正して再書き出しする。

## Phase 4: デッキへ挿入する

- **仕様パス**（`build_deck.py`）: ローカル PNG を指す `image` パートを追加する。
  `fit: "contain"` を使い、ボックスは PNG のアスペクト比に合わせてサイズを決める。
- **コードファーストパス**（`deckkit`）: `image(x, y, w, h, "out/diagrams/arch.png")`。
- **既存デッキ**: まずバージョンをスナップショットし（`snapshot_version.py`）、
  API で挿入して、必要ならページ番号を振り直す
  （挿入パターンは `references/code-blocks.md` にある）。

ジェネレータは PNG を一時的に Drive へアップロードし、後で削除する —
スライドは画像のコピーを自分で保持する。

## Phase 5: ソースをデッキの Drive フォルダへアーカイブする

すべてのデッキは専用の Drive フォルダを持つ（生成スキル側の Drive フォルダ
ルールを参照）。図のソースもそこへ置く:

```bash
.venv/bin/python scripts/drive_folder.py upload <FOLDER_URL_OR_ID> \
    <deck-dir>/figures/arch.drawio out/diagrams/arch.png
```

デッキ URL と併せてフォルダ URL も報告し、`.drawio` は app.diagrams.net または
draw.io デスクトップアプリで開いて後から編集できることを添える。
