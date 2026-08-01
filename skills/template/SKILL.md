---
name: template
description: 既存の Google Slides マスター（テンプレート）を解析して template.json に登録し、slide-forge から使えるようにする。レイアウトの ID・プレースホルダ構成・座標・配色を実測して書き出し、セマンティックロール（COVER/SECTION/CONTENT など）を割り当てる。トリガー: 「このマスターを登録して」「テンプレートを解析」「自社ブランドのレイアウトを使いたい」「inspect_template」。対象外: テンプレートそのもののデザイン作成、PPTX テンプレート。
---

# テンプレートの解析と登録

マスターを登録すると、装飾・ロゴ・フッターがレイアウトから自動継承されるようになる。
自分で描く必要がなくなり（描くと二重になる）、ブランドの一貫性も保てる。

## 手順

### 1. 解析する

```bash
# 人間可読なレポートを表示（まず中身を見る）
python <plugin>/scripts/inspect_template.py <マスターの URL または ID>

# template.json を書き出す
python <plugin>/scripts/inspect_template.py <URL> \
    --emit <plugin>/templates/my-brand.json --name my-brand

# レイアウトのサムネイルも取得する
python <plugin>/scripts/inspect_template.py <URL> --thumbnails out/thumbs
```

マスターは**閲覧できれば十分**（複製して使うため編集権限は不要）。

### 2. ロールを確認する（ここが人間の仕事）

`roles` は表示名とプレースホルダ構成からの**推測**なので、必ず目で確認して直す。
サムネイルを並べて、どのレイアウトがどの役割かを判断する。

| ロール | 役割 | 必要なプレースホルダ |
|---|---|---|
| `COVER` | 表紙 | TITLE（＋ SUBTITLE） |
| `SECTION` | 章の中扉 | TITLE（＋ BODY） |
| `CONTENT` | 本文（テキスト主体） | TITLE ＋ BODY |
| `TITLE_ONLY` | タイトルのみ。**図解ページで使う** | TITLE |
| `BLANK` | 白紙。全面図に使う | なし |
| `CLOSING` | 裏表紙 | なし |

ロールは単なる別名テーブルなので、系統別に増やしてよい
（例: `CONTENT_PRESENTATION`, `TITLE_ONLY_PROPOSAL`）。
ロールを介さず `"layout": "DEFAULT_PROPOSAL"` とレイアウトキーを直接指定してもよいが、
ロールを使うとテンプレートを差し替えても同じデッキモジュールが使い回せる。

**図解デッキでは `TITLE_ONLY` が主役になる。** BODY プレースホルダがあると図と場所を
争うので、タイトルだけのレイアウトを選ぶ。無い場合は `BLANK` を使い、タイトルも自分で描く。

### 3. 安全域を確認する

`template.json` の実測値から、図を描いてよい範囲を決める。

1. `pageSize` … 16:9（10 × 5.625in）以外なら `configure_layout()` で上書きが必要
2. `elements.title` の `y + h` … 図の上端（`DY0`）はこれより下
3. `masterDecorations` … ロゴやフッターの `y`。図の下端（`DY1`）はこれより上
4. `textStyles.title.fontSize` … タイトルが 1 行に収まる文字数の根拠

例（`title` が y=0.126 h=0.351、装飾が y=5.197 から）:

```python
configure_layout(diagram_top=0.84, diagram_bottom=4.30,
                 note_y=4.38, edition_y=4.86)
```

決めたら `validate` スキルで検査が通ることを確認する。

### 4. 使う

```python
TEMPLATE = json.load(open("<plugin>/templates/my-brand.json", encoding="utf-8"))
```

または環境変数で差し替える。

```bash
SLIDE_FORGE_TEMPLATE=<plugin>/templates/my-brand.json \
    python <plugin>/scripts/render_deck.py mydeck.py
```

## 注意

- **テンプレートを更新したら再解析する。** `layoutId` と `existingSlideIds` は実測値なので、
  マスター側でレイアウトを増減すると合わなくなる。
- `SLIDE_NUMBER` プレースホルダは API で生成できない（指定してもエラーにならず無視される）。
  ページ番号は `add_page_numbers()` がテキストボックスで描く。
- 全面サイズの `decorations` があるレイアウトは、マスターのフッターを覆っている可能性がある。
- マスターに機微な情報やブランド資産が含まれる場合、`template.json` には
  プレゼンテーション ID が入る。公開リポジトリに置く前に扱いを判断すること。

`template.json` のスキーマは `references/template-schema.md` を読む。
