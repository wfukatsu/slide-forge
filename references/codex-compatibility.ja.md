*[English — normative](codex-compatibility.md)*

# Codex 互換性

slide-forge の主ホストであり配布経路でもあるのは Claude Code である。Codex は薄い
互換レイヤーを通じて、同じエンジンと共有スキルを使う。Python スクリプト、JSON
スキーマ、テンプレート、検証コマンドはホスト非依存である。ホスト間で異なるのは、
スキルの発見、対話的な質問、画像の目視、任意の作業委譲だけである。

**この日本語版は理解のための訳であり、正本は英語版
[`codex-compatibility.md`](codex-compatibility.md) である。**

## リポジトリのクローンへの導入

リポジトリは `.agents/skills/` を通じてスキルを公開している。

```text
.agents/skills/forge/SKILL.md
.agents/skills/google-slides -> ../../skills/google-slides
...
```

リポジトリのルートで Codex を起動する。`AGENTS.md` と `.agents/skills/` 配下の
スキルが発見されるはずである。シンボリックリンクは意図的に共有の `skills/`
ディレクトリを指しており、Claude と Codex が別々の複製へ分岐しないようにしている。

`.claude-plugin/marketplace.json` の Claude マーケットプレイスマニフェストと、共有の
`commands/` / `skills/` が主たる配布を定義する。Codex はこのマニフェストを必要とせず、
薄い `.agents/skills/forge` を入口として呼び出す。どちらの経路も
`references/workflow-contract.md` に従う。

### 対応している入口

| ホスト | スキルの発見 | エンドツーエンドの呼び出し | プロジェクト指示 |
|---|---|---|---|
| Codex | `.agents/skills/` | `forge` スキル | `AGENTS.md` |
| Claude Code プラグイン | `.claude-plugin/marketplace.json` | `/slide-forge:forge` | スキルの内容 |
| Claude Code ローカルクローン | `~/.claude/skills/` からのシンボリックリンク | コマンドとして導入時は `/forge` | スキルの内容 |

## 実行環境のセットアップ

Codex も他のホストと同じ、リポジトリローカルの入口を使う。

```bash
.venv/bin/python scripts/list_templates.py
```

実体の仮想環境はどこにあってもよく、`.venv` はシンボリックリンクでよい。旧来の
セットアップ例に出てくる `~/.claude/venvs/gslides` は既存の共有環境を説明している
だけで、Codex の要件ではない。

OAuth の解決順序はホスト非依存である。

1. `$GSLIDES_CONFIG_DIR`
2. リポジトリルートの `config/`
3. 旧来の Claude スキル設定パス

Google API への書き込みは、Codex のサンドボックス次第で利用者の承認や OAuth の
ブラウザフローを要することがある。オフラインの `--dry-run` 検証はネットワークを
必要とせず、必ず先に実行する。

## 対話的な質問

スキルが `AskUserQuestion` や `ask_question` と書いている箇所では、その Codex
セッションで使える対話手段を用いる。構造化された質問ツールが無ければ、番号付きの
選択肢をチャットに出して回答を待つ。UI が違っても、アウトライン承認が強いゲートで
あることは変わらない。

## 視覚 QA

スキルが `Read` で画像を開けと書いている箇所では、Codex の画像表示機能を使う。
テキストファイルとして読むことは代替にならない。指定された全ページを十分な解像度で
検査し、欠陥をスライド番号付きで報告し、ソース仕様を直して再生成し、サムネイルを
後片付けする。

## 並列実行と逐次実行

`references/parallel-generation.md` が説明しているのは性能の最適化であって、正しさの
要件ではない。Codex に委譲が許されていれば、そのワークフローを使ってよい。委譲が
使えない、または禁止されている場合は、同じ番号付きのページ断片を主エージェント内で
逐次作り、断片ごとに検証し、結合して完全なデッキを検証する。QA のページ範囲も同様に
逐次検査してよい。出力と検証の挙動は保たれ、増えるのは所要時間と主コンテキストの
消費だけである。

## 互換性チェックリスト

- Codex が `.agents/skills/` 配下の共有スキルを発見できる。
- 選択した生成スキルを最後まで読み込み、無関係なスキルや参照を先読みしない。
- `scripts/validate_agent_contracts.py` が、Claude Code / Codex / Antigravity の各
  アダプタ、置換の安全性、参照の読み込み、QA の範囲について通る。
- `.venv/bin/python -m pip check` が通る。
- `scripts/` が構文エラーなくコンパイルできる。
- 代表的なデッキ仕様が `build_deck.py --dry-run --strict` を通る。
- `examples/estimate-sample.json` が `build_sheet.py --dry-run` を通る。
- Google OAuth と、任意の draw.io / Gemini の前提条件は、それを使うワークフローに
  ついてだけ確認する。

ホスト非依存のチェックはリポジトリルートから実行する。

```bash
.venv/bin/python -m pip check
.venv/bin/python -m compileall -q scripts
.venv/bin/python scripts/validate_agent_contracts.py
.venv/bin/python scripts/build_deck.py \
  --template templates/corporate.json \
  --spec examples/charts-demo.json --dry-run --strict
.venv/bin/python scripts/build_sheet.py examples/estimate-sample.json --dry-run
```

これらのチェックはデッキもスプレッドシートも作らない。実際の Google API による確認を
意図的に分けているのは、OAuth のブラウザフローが開いたり Drive にファイルを書いたり
する可能性があるためである。

## 関連

- [デッキ生成のワークフロー契約](workflow-contract.ja.md)
- [ページ単位の分担生成](parallel-generation.ja.md)
