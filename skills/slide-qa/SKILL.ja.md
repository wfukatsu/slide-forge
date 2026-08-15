---
name: slide-qa
description: >-
  Visual QA of a generated Google Slides deck from thumbnails: fetch every page
  as PNG, inspect with a defect checklist (overflow, overlaps, wrong
  connectors, weak contrast), drive the fix-and-regenerate loop, and clean up
  the local QA files when done. Extracted from the slide-forge generation
  skills (google-slides-template / google-slides / scalar-*) so QA can be
  chosen at generation time — those skills invoke this one when the user opts
  in (the default), and it also runs standalone on any deck URL.
  Triggers: "スライドを検証して", "デッキを QA して", "サムネイルで確認して",
  "生成したスライドをチェック", "slide-qa", "visual QA", "verify the deck",
  "check the generated slides".
  Out of scope: pre-generation offline checks (--dry-run / validate_layout.py
  stay in the generation skills), content fact-checking, and PPTX files
  (exporting a verified deck to .pptx is the pptx-export skill).
---

*[English](SKILL.md)*

# 生成済みスライドのビジュアル QA（サムネイルベース）

`references/workflow-contract.md` のQA範囲に従う。初回は必ず全ページを目視し、
修正後だけ影響範囲に限定して再検査する。

## 重要事項

- **スコープ**: 生成後の視覚的検証のみ。オフラインの座標ゲート
  （Gate 1: `build_deck.py --dry-run` / `validate_layout.py`）は生成スキル側に
  属し、生成の**前**に実行される。本スキルは Gate 2 である
  （2 ゲート構成の理由の全体は `references/validation.md` にある）。
- **すべてのコマンドは slide-forge ルートを cwd として実行する** —
  インストール済みプラグインから実行する場合は `${CLAUDE_PLUGIN_ROOT}`、
  ローカルクローンでは `/path/to/slide-forge`。認証と venv はリポジトリルートで
  共有される（`config/`、`.venv`）。
- **QA を実行するかどうかは生成時に確定する。** 生成スキルはインテイクで確認する
  （既定は**実行** — 推奨すること。API 応答が正常でも、テキストのはみ出しや
  矢印の誤接続は分からない）。ユーザーが QA をスキップした場合、生成スキルは
  報告にその旨を明記し、フォローアップとして本スキルを提案する。
- **修正は成果物ではなくソースに対して行う。** 欠陥を見つけたら、元スキルの
  フローで仕様 / デッキモジュールを修正して再生成する。生成済みデッキを
  その場でパッチしてはならない。
- **終了時は必ずクリーンアップする。** サムネイルはこの検証のためだけに存在し、
  いつでも再取得できる。報告の前に `scripts/cleanup_qa.py` で削除する —
  QA を途中で中断した場合も同様。修正ループ中に作られた旧版デッキも
  Drive から削除する。

## クイックリファレンス

| タスク | コマンド |
|------|---------|
| サムネイル取得 | `.venv/bin/python scripts/fetch_thumbnails.py <URL or ID> --out out/qa --size LARGE` |
| ページの限定（分割 QA） | `--pages 3,8,12,20` / `--pages 9-16` |
| ローカル QA ファイルの削除（最後に必ず） | `.venv/bin/python scripts/cleanup_qa.py`（`--dry-run` でプレビュー） |
| チェックリスト全体・修正ループ・報告ルール | `references/validation.md`（Gate 2） |
| 画像が文脈を圧迫するときの QA 分割 | `references/parallel-generation.md` §6 |
| 旧版デッキの Drive からの削除 | `drive.files().delete(fileId=…)`（またはゴミ箱へ移動） |

---

## Phase 1: サムネイル取得

```bash
.venv/bin/python scripts/fetch_thumbnails.py "<deck URL>" --out out/qa --size LARGE
```

- 判定は `--size LARGE` で行う。SMALL はスクイントテスト専用。
- **画像が主コンテキストを圧迫する場合は、QA を 6〜8 枚のレンジに分割する。** ホストと
  セッションがサブエージェントを許可している場合はレンジを委譲し、
  **所見のみをテキストで返させる**。それ以外の場合は
  `references/parallel-generation.md` の Codex フォールバックに従い、同じ
  レンジを順番に検査する。
- 1 セッションで複数のデッキを QA する場合は `--out out/<deck>/qa` で分離する —
  `cleanup_qa.py` はどちらの慣例も掃除する。

## Phase 2: 検査

PNG を Read ツールで開く。初回QAでは全ページを見る。サンプリングで代用しない。
枚数が多い場合は次の順序を優先する:

1. **要素数が最も多いページ**（重なりはここに最初に現れる）
2. **図が最も複雑なページ**（スイムレーン、分岐フロー、マルチパネル）
3. **表があるページ**（行は増えて下方向にはみ出す）
4. **各セクションの先頭ページ**（構成がどう読めるか）
5. 表紙・セクション区切り・クロージング（マスターの装飾と自前の描画の関係）

最小チェックリスト（修正方法つきの完全な表は `references/validation.md` にある）:

- [ ] どのプレースホルダー・ボックスでもテキストがはみ出したり切れたりしていない
- [ ] テキストがテンプレートの装飾（帯、図形、ロゴ）に重なっていない
- [ ] ページ番号が表示され、2 桁でも切れていない
- [ ] ロゴとフッターが二重に描かれていない
- [ ] 意図したレイアウトが使われている（Proposal / Presentation ファミリーの取り違えがない）
- [ ] 末尾 1 文字だけが単独で折り返された行がない（「〜へ」「〜出」）
- [ ] 矢印が無関係な図形を横切らず、それぞれが*意味的に*正しい図形に接続している —
      座標監査では意味は判定できない
- [ ] ラベルが矢印や罫線に重なっていない。本文テキストのコントラスト比 ≥ 4.5:1
- [ ] マーカー（●、◆、バーの端）に隣接するラベルに目に見える余白がある —
      詰まった垂直間隔は座標監査には見えない
- [ ] 表の列揃えが内容に合っている: 短く均一な値（年、年月、ID）は中央、
      数値は右、文は左
- [ ] **スクイントテスト**: 最初に目を引くものがそのページの主メッセージであること。
      そうでなければ強調（塗り、太字、色）が誤っている

## Phase 3: 修正ループ

```
identify defects → fix the spec / deck module (originating skill)
  → offline check (free) → regenerate → re-fetch only the affected pages → confirm
```

- **新規プレゼンテーションとして生成された**デッキでは、再生成のたびに新しい
  プレゼンテーションと URL が作られる。**先に旧版を Drive から削除する** —
  ユーザーが持つ URL は最新の 1 つだけにする。
- **例外 — インプレース（`--into`）デッキ。** ページ固有の修正は
  `--into <deck> --update-slides <pages>` を使い、変更ページと前後ページだけを取得する。
  URL の不変が契約であるデッキ — `scalar-account-plan` の活動計画、`scalar-account-planning-session` の
  2 つのデッキ、`spreadsheets` スキルで更新するスプレッドシート — は、
  `scripts/snapshot_version.py` で編集前リビジョンを記録した上で、
  **同じデッキへの再生成**（裸の `build_deck.py --into` は承認済み全再構築のみ）
  で修正する。**共有済み URL のデッキは決して削除しない** — URL そのものが
  納品物であり、削除すればユーザーが配ったリンクがすべて壊れる。
- 成果物をパッチせず、ソースを直して再ビルドする（速く、再現可能）。
- ページ固有の修正後はそのページと前後ページを再取得する。共通レイアウト／componentを
  直した場合は利用ページをすべて再取得し、マスター、テーマ、フッター、ページ番号を
  変えた場合は全ページを再取得する。
- 検証中に作られた中間デッキも Drive から削除する
  （これも新規プレゼンテーションのデッキにのみ適用し、`--into` 対象には決して適用しない）。

## Phase 4: クリーンアップと報告

**このフェーズは省略できない。** 結果を提示する前に:

```bash
.venv/bin/python scripts/cleanup_qa.py            # removes out/qa, out/qa-*, out/*/qa
.venv/bin/python scripts/cleanup_qa.py --dry-run  # preview first if unsure
```

このスクリプトが触るのは `out/` 配下のディレクトリのみ（すべて gitignore 済みで
再取得可能）なので、無条件に実行して安全である。標準外の `--out` を使った場合は
明示的にパスを渡す。

その後、`references/validation.md` に従って報告する:

- 修正したものについては、**何が悪くてどう直したか**を述べる（「直した」だけでは
  検証できない）。直していないものについては、その旨を明示する。
- QA が合格したこと、どのページを検査したか（全ページ、またはレンジ）、
  ローカル QA ファイルをクリーンアップしたことを述べる。
- 生成スキルから呼び出された場合は、そのスキルの生成後確認
  （`references/interactive-intake.md` §4）に処理を戻す。
