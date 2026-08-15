---
title: "feat: Add targeted slide updates"
type: feat
status: completed
date: 2026-08-15
origin: docs/brainstorms/2026-08-15-targeted-slide-update-brainstorm.md
---

# feat: Add targeted slide updates

## Overview

`build_deck.py` に既存デッキの指定ページだけを再生成するモードを追加する。
デッキURLと対象外ページはそのまま維持し、現在の破壊的な `--into`（全ページ置換）とは
明確に分離する。Claude Codeを正本とし、CodexとAntigravityも同じCLI・共有スキルを使う。

## Problem Statement

現在の `TemplateDeck.open()` は既存ページをすべて `deleteObject` に積み、完全なSpecから
全ページを再生成する。一枚の修正でも全ページのID、コメント、編集履歴上の差分が変わり、
APIリクエスト、画像生成、QA、トークン消費もデッキ全体に比例する。

## Proposed Solution

完全なデッキSpecと `--update-slides 3,7` のような1始まりページ番号を受け取る。
API書込み直前に既存ページ一覧を取得して、各番号を旧 `objectId` と挿入位置へ固定する。
選択したSpecだけを同じ位置に新規生成し、旧ページだけをID指定で削除する。

MVPではページの中身を要素単位で編集せず、ページ単位で置換する。これにより現行の
placeholder、figure、画像、notes生成を再利用し、レイアウト変更にも対応する
（see brainstorm: `docs/brainstorms/2026-08-15-targeted-slide-update-brainstorm.md`）。

## CLI Contract

```bash
# オフライン検証。APIへ接続しない
.venv/bin/python scripts/build_deck.py \
  --template templates/<id>.json \
  --spec out/<deck>/deck.json \
  --into <deck-url> --update-slides 3,7 \
  --dry-run --strict

# snapshot後の実更新
.venv/bin/python scripts/build_deck.py \
  --template templates/<id>.json \
  --spec out/<deck>/deck.json \
  --into <deck-url> --update-slides 3,7
```

- `--into` 単独: 従来どおり全ページ置換。
- `--into` + `--update-slides`: 指定ページだけを置換。
- `--update-slides` 単独、範囲外、重複、0、負数、空指定は書込み前に拒否。
- `--keep-existing` との併用は拒否。
- `--title` と `--folder` は部分更新では無視せず、誤解を避けるため併用を拒否する。
- dry-runは完全Specを検証したうえで、更新対象と想定リクエスト範囲を表示する。

## Technical Approach

### 1. Selection model

`scripts/build_deck.py` にページ指定の純粋関数を追加する。

- `parse_slide_selection("3,7") -> [2, 6]`
- `select_spec_slides(spec, indices)` は元インデックスを保持した選択を返す。
- live実行では `presentations.get(fields="slides.objectId")` の結果とSpecのページ数が
  一致することを既定で要求する。不一致なら別ページを誤更新する可能性があるため停止する。
- ページ番号は取得直後に `{spec_index, insertion_index, old_slide_id}` へ解決し、以後は
  旧ページIDで削除する。順次削除によるindexずれを起こさない。

### 2. Partial-update deck lifecycle

`TemplateDeck.open_partial()`（名称は実装時に最終決定）を追加する。

1. master自身でないことを確認する。
2. 対象Specが使うlayoutだけ `_require_layouts()` で検証する。
3. 現在のページIDを一度取得し、ページ数と対象範囲を検証する。
4. pre-edit revisionを表示する。
5. 対象ごとに `add_slide(..., index=original_index)` を実行する。
6. 各新ページの生成リクエスト後に、対応する旧ページの `deleteObject` を積む。
7. request数が5MB/10,000件を超えない限り1回の `batchUpdate` でcommitする。

Google Slidesの `batchUpdate` は一つのリクエスト集合として検証されるため、通常サイズの
ページなら作成と削除を同一commitに入れる。複数chunkになるほど大きい対象は原子性を
保証できないため、部分更新では事前にサイズ超過を検出して拒否する。

### 3. Build only selected source pages

`build_from_spec()` に `selected_indices` を渡せるようにし、警告の `slides[n]` は元Specの
indexを維持する。`add_page_numbers()` は全ページへ触れるため部分更新では使わず、
新ページにだけ元のページ番号を描く小さなAPIを追加する。

画像upload、speaker notes、image fixupは選択ページだけを対象にする。post-passが失敗した場合は
本文置換済み・notes/fixup未完了になり得るので、エラーにデッキURL、対象ページ、新ページIDを
含め、snapshotからの復旧手順を表示する。

### 4. Source-of-truth metadata

完全Specを引き続き正本とする。生成後にSpecを書き換えて実体だけpatchする設計にはしない。
将来の並べ替え耐性向上に備え、各slideに任意の安定キー `id` を許可する案を設計に残すが、
MVPのCLI対象指定はページ番号に限定する。安定キー導入時は重複検証とlive deckへのkey保存方法を
別途決める。

## Implementation Phases

### Phase 1: Pure selection and validation

- [x] `scripts/build_deck.py` に `--update-slides` と純粋なparse/validation関数を追加する。
- [x] full replacement、partial replacement、new deckのCLI組合せ表を実装する。
- [x] dry-runに対象ページ一覧、対象外ページ非変更、live-only検査事項を表示する。
- [x] ページ数不一致、範囲外、重複指定をAPI write前に拒否する。

### Phase 2: Scoped request generation

- [x] `TemplateDeck` にpartial-open lifecycleを追加し、既存ページIDを一度だけ取得する。
- [x] `build_from_spec()` を選択index対応にし、figure監査の元indexを維持する。
- [x] `add_slide(index=...)` と旧IDの `deleteObject` を対象ページごとに組み立てる。
- [x] ページ番号を新規ページだけに描くAPIを抽出する。
- [x] 部分更新時は単一batch上限を超えるrequestを送信前に拒否する。

### Phase 3: Safety, QA, and host contracts

- [x] snapshot必須、master拒否、template layout整合を既存契約から再利用する。
- [x] `skills/google-slides-template/SKILL.md` と日本語版に部分更新手順を追加する。
- [x] `references/workflow-contract.md` の「scoped editing workflow」を新CLIへ接続する。
- [x] `references/agent-contract-evals.json` とvalidatorに3ホスト共通の部分更新シナリオを追加する。
- [x] `slide-qa` に更新ページ+隣接ページの具体的コマンド例を追加する。
- [x] README/CLIヘルプへ全置換との違いとスライドID変更の制約を記載する。

## System-Wide Impact

### Interaction graph

`build_deck.py CLI` → selection validation → `TemplateDeck.open_partial()` →
`presentations.get` → selected `add_slide()/draw_figures()` → one `batchUpdate` →
notes/image post-pass → scoped thumbnail QA。

対象外ページにはcreate/update/delete requestを生成しない。Drive title/folderも変更しない。

### Error and failure propagation

- selection/layout/page-countエラー: API write前に終了。
- image uploadエラー: commit前に終了し、一時assetをcleanupする。
- main batch失敗: Slides側の原子的拒否を前提に旧ページを維持し、URLを表示する。
- post-pass失敗: 新ページは存在する可能性があるため、自動再送せずsnapshot復旧を案内する。
- response喪失: 非冪等batchを再送しない既存方針を維持する。

### API surface parity

- 直接対象: `scripts/build_deck.py`、`TemplateDeck`、shared workflow contract。
- 間接対象: Scalar builderがpartial modeを明示的に選べるようにするが、自動移行はしない。
- 対象外: `google-slides` code-first path、`fill_image_slots.py`、template master編集。

## Test Strategy

既存の専用test directoryがないため、APIを呼ばない `unittest` を `tests/` に新設し、fake
Slides/Drive serviceでrequest列を検証する。

- [x] parser: 単一、複数、空、重複、範囲外、非数値。
- [x] request scope: 5ページ中3ページ更新で、旧3ページIDだけがdelete対象になる。
- [x] order: 新ページは元indexへ挿入され、旧ID削除はindex変動に依存しない。
- [x] preservation: 対象外slide IDがどのrequestにも現れない。
- [x] page count mismatch: commitが一度も呼ばれない。
- [x] master/layout mismatch: writeが一度も呼ばれない。
- [x] atomicity guard: batch上限超過でwrite前に停止する。
- [x] notes/images: post-pass対象が新ページだけになる。
- [x] regression: `--into` 単独の全置換と新規生成のrequest列が変わらない。
- [x] contract eval: Claude/Codex/Antigravityが同じpartial-update commandへrouteする。

統合確認ではsnapshotを作成したテストデッキに対し中央の1ページを更新し、前後ページの
`objectId`、内容、順序が不変であること、対象ページだけIDが変わることをAPIレスポンスで確認する。

## Acceptance Criteria

- [x] 指定ページ以外のslide ID、内容、notes、順序が更新前後で不変。
- [x] デッキURL、Drive folder、タイトルが不変。
- [x] 対象ページは完全Specの同じindexから再生成され、レイアウト変更にも対応する。
- [x] snapshot、strict dry-run、master/layout/page-count検査を通らない限り書き込まない。
- [x] 通常サイズの部分更新はcreate+deleteを一つのbatchUpdateで送る。
- [x] 対象ページと隣接ページだけのQAコマンドが提示される。
- [x] 全置換モードと新規生成に回帰がない。
- [x] スライドID、コメント、旧IDへの内部リンクが維持されない制約をCLIと文書で警告する。
- [x] Claude Code、Codex、Antigravityの契約evalが成功する。

## Implementation Result

- Implemented `--into <deck> --update-slides <pages>` with complete-spec validation.
- Added atomic single-batch enforcement and untouched-slide request-scope tests.
- Added eight offline unit tests plus strict deck, spreadsheet, compile, and contract checks.
- Live mutation was intentionally not run because no user-owned test deck was authorized.

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| ページ番号が古く別ページを更新 | write直前にページ一覧を取得し、Specとのページ数一致を必須化 |
| 対象ページへの内部リンク切れ | MVPの既知制約として警告。リンク検出時は既定で停止する案を実装時に評価 |
| コメント消失 | snapshotと明示警告。ID維持型の要素更新は第2段階へ分離 |
| batch分割で部分状態 | partial modeは単一batch上限超過を拒否 |
| page numberが全体更新を誘発 | 新ページ専用の番号描画へ分離 |
| post-passだけ失敗 | 対象IDを含む復旧情報を出し、自動再送しない |

## Alternatives Considered

1. **同一スライド上の全要素を差分更新**: slide IDを維持できるが、手作業要素と生成要素の
   所有権、layout変更、placeholder、group、notesの扱いが未定義。MVPには採用しない。
2. **一時デッキで対象ページを生成してコピー**: 本番deckへの失敗影響は減るが、Slides APIに
   汎用的なページcopy操作がなく、要素複製とasset管理が複雑になるため不採用。
3. **従来どおり全再生成**: 実装不要だが、対象外ページ保持という要求を満たさない。

## Success Metrics

- 1ページ修正時の生成request数とQA対象ページ数が全体ページ数ではなく対象ページ複雑度に比例。
- 20ページdeckの1ページ更新で、対象外19ページのIDが100%維持される。
- 誤指定・不一致ケースではAPI writeが0回。

## Documentation Plan

- `skills/google-slides-template/SKILL.md` / `.ja.md`
- `references/workflow-contract.md`
- `README.md` / `README.ja.md`
- `scripts/build_deck.py --help`
- `references/agent-contract-evals.json`

## Sources and References

- Origin brainstorm: `docs/brainstorms/2026-08-15-targeted-slide-update-brainstorm.md`
- Full replacement lifecycle: `scripts/build_deck.py` (`TemplateDeck.open`)
- Indexed slide creation: `scripts/build_deck.py` (`TemplateDeck.add_slide`)
- Commit and post-pass behavior: `scripts/build_deck.py` (`TemplateDeck.commit`, `_post_pass`)
- Shared safety contract: `references/workflow-contract.md`
- Template workflow: `skills/google-slides-template/SKILL.md`
- Batch constraints: `references/layout-contract.md`
