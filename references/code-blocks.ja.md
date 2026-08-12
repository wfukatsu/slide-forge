*[English](code-blocks.md)*
# コードブロック（シンタックスハイライト付きコードサンプル）

`Canvas.code_block()` で、等幅フォント + 濃色パネル + シンタックスハイライトの
コードサンプルを描く。ハイライトは Slides API の `updateTextStyle`
（`FIXED_RANGE`）による範囲着色で、生成後もユーザーがテキストとして編集できる。

```python
d.code_block(0.5, 1.0, 6.1, 2.9, code, lang="java")
```

JSON 仕様（`figures`）からも使える:

```json
{ "type": "code_block", "x": 0.5, "y": 1.0, "w": 6.1, "h": 2.9,
  "code": "DistributedTransaction tx = manager.begin();\ntx.commit();",
  "lang": "java" }
```

## 引数

| 引数 | 既定 | 意味 |
|---|---|---|
| `code` | 必須 | コード文字列。BMP 外の文字（絵文字等）は入れない（範囲指定が UTF-16 単位のため） |
| `lang` | `"java"` | `java` / `graphql` / `json` / `bash`。未知の言語は単色で描く |
| `size` / `line_spacing` | 7.5 / 104 | 文字サイズ(pt)・行送り(%) |
| `bg` / `fg` | `#1F2933` / `#E8ECF1` | パネルと基本文字の色 |
| `font` | `"Roboto Mono"` | 等幅フォント |

## 守ること

- **角は直角（RECTANGLE）。角丸にしない。** ユーザー指摘で確定した規約
  （アクセントバー付きカードの直角規約と同じ）。`code_block` は実装で直角を強制する
- **高さは実効行高で見積もる。** Slides 上の 1 行は
  `fontSize × lineSpacing × 約 1.45`（Noto Sans JP フォールバック分）。
  目安: `h = 行数 × size × (ls/100) × 1.45 / 72 + 0.14in`。
  過小だと文字が枠から上下にあふれる（valign=MIDDLE なので両側に出る）
- 1 行は 60 桁程度まで。日本語コメントは短く（等幅でも日本語は約 2 桁分）
- コードは一次資料（公式ドキュメント・リポジトリ）から取り、要約・省略した場合は
  スピーカーノートに出典と省略内容を書く

## 配色（VS Code Dark+ 風・濃色背景でコントラスト比 4.5:1 以上）

| トークン | 色 | 例 |
|---|---|---|
| comment | `#7DBA7D` 緑 | `// 開始` `# ① 開始` |
| string | `#E2A37E` 橙 | `"PAID"` `'sales'` |
| keyword | `#6FB6EA` 青 | `public` `query` `SELECT` `true` |
| type | `#56C9B4` 青緑 | `DistributedTransaction`（大文字始まり） |
| func | `#DCDCAA` 黄 | `begin()` `newBuilder()`、bash は `$ ` 直後のコマンド名 |
| anno | `#D19FD3` 紫 | `@Override` `@transaction` |
| prop | `#9CDCFE` 水色 | GraphQL/JSON のプロパティ名、bash の `--flag` |
| number | `#B5CEA8` 淡緑 | `1000` |

## 言語ごとの癖

- **java**: 大文字始まりの識別子は型として青緑。SQL を含む文字列は IDE と同様に
  文字列色（橙）で塗り潰される
- **bash**: **二重引用符の中身は素通し**にして、`CREATE` / `SELECT` などの
  SQL キーワードを拾う（ScalarDL TableStore の `--statement "CREATE …"` のための設計）。
  文字列として塗るのは単一引用符のみ
- **graphql / json**: `key:` のようなプロパティ名は水色。JSON はキーと値を塗り分ける

## 言語の追加

`diagrams.py` の `Canvas._CODE_RULES` に `(トークン名, 正規表現)` のリストを足す。
**上にある規則が優先**なので、コメント・文字列を必ず先頭に置く（後続の規則が
文字列の中身を誤って塗るのを防ぐ）。トークン名は `_CODE_STYLES` のキーに合わせる。

## レイアウトの定石（コードサンプルスライド）

「左 = コード / 右 = 解説 / 下 = ポイント帯」の 3 分割が収まりが良い。
実例: `~/Documents/Slides/scalar-intro-2026/add_code_samples.py`
（既存デッキへの挿入・ページ番号の振り直しまで含む）。

既存デッキへ挿入する場合は、編集前に必ず
`scripts/snapshot_version.py <URL>` で版を確保し（リビジョン ID の記録と
PPTX バックアップ）、リビジョン ID をユーザーに報告してから実行する。

```python
d.label(CX, y, CW, 0.2, "Java — CRUD インターフェース", size=8.5,
        bold=True, color=accent)                     # ブロック見出し
d.code_block(CX, y + 0.24, 6.1, h, code, lang="java")
# 右: 解説カード（surface 塗り + 上端 0.06in のアクセントバー。直角）
# 下: ポイント帯（lighten(accent, 0.9) 塗り。1 行の結論）
```
