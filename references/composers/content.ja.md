*[English](content.md)*
# 本文ページの組み立て

汎用の本文ページ — 箇条書き、段組み、画像＋文章、グラフ、表、KPI、工程、
引用、アイコングリッド。各項目に、そのページが何のためにあるか、そして今
何で作るか（プレースホルダのレイアウト / BLANK 上の図 / 登録済みテンプレート）
を書く。

図は本文プレースホルダを持たないページに置く:

```python
ref = deck.add_slide("TITLE_ONLY", title="…")
d = Canvas(deck, ref["slideId"], template)
d.flow(0.5, 1.3, 9.0, 0.8, ["受付", "審査", "記録"])
```

図の系統は [diagrams.md](../diagrams.md)、spec の形は
[template-schema.md](../template-schema.md)、既製の 92 ページは
`list_slide_templates.py` を参照。

## 箇条書き

要点の列挙。既定の本文ページであり、そのページに見せるべき構造ができた時点で
使うのをやめるべきページでもある。

**作り方**: `layout="CONTENT"`、`body` をリストで。`body_font_size=12` と
`body_line_spacing=120` で約 14 行。それを超えるならページを割る。

3〜5 項目。7 項目のページは、まだ分けていない 2 ページである。

## 段組み

2〜3 本の並行する筋 — 選択肢、読み手、フェーズ — を、縦に読ませるのではなく
横に見比べさせる。

**作り方**: `cards` 図（カードごとに見出しと本文）、または内容が素の文字なら
テンプレートの TWO_COLUMN / THREE_COLUMN。明示的な比較なら `comparison` が
各列に同じ行を与える。

## 画像＋文章

片側に絵、反対側に読み。絵が装飾ではなく証拠であるとき（画面、写真）に使う。

**作り方**: 片側に `d.image(...)`、反対側に `d.label(...)`。または
`architecture-exhibit` テンプレート（画像と、そこから読み取る点）。
`fit="contain"` は全体を残し、`"cover"` は切り取って埋める。

## グラフ

形として意味を持つ数値 — 推移、構成比、順位。

**作り方**: チャート図 — `vbars`、`hbars`、`linechart`、`pie`、`waterfall`、
`pareto`。Sheets を経由せずネイティブに描く。[charts.md](../charts.md) 参照。

すべての数値に `source_note` を付ける。出典のないグラフは主張にすぎない。

## 表

形ではなく個々のセルに価値があるデータ。

**作り方**: `table` 図 — `headers`、`rows`、`colWidths`、`size`。列幅は実際の
制約である。監査はセルからはみ出た文字を弾き、しかも幅は全角換算で測るので、
同じ文字数でも英字と日本語では幅が違う。

密な評価表は `dense-comparison-table`、主張と根拠の対応は
`claim-evidence-table`。

## KPI

そのページの主旨になるだけの大きさで示す、1 つないし少数の数値。

**作り方**: `metric` 図（`value`、`caption`）、または評価スコアなら
`score-card` / `score-breakdown`。1 ページ 4 つまで。5 つ目からは、ただの表に
戻る。

## 工程フロー

順序のある 3〜5 段を、つないで見せる。

**作り方**: 素の段なら `flow`、各段に絵にする主体がいるなら `icon_flow`、
前段の上に積み上がるなら `steps`、日付があるなら `gantt-schedule`。

## 引用

顧客自身の言葉。逐語であることと、出所が明示されていることが力の源である。

**作り方**: `testimonial` 図。言い換えて入れないこと。正確に引用し出所を
名指しできないなら、それは引用ではない。

## アイコングリッド

同じ重みの 3〜6 項目を、絵とラベルで並べる。

**作り方**: `icon_grid`（`cols`、`size`）、1 行なら `icon_row`。名前は
`illustrations.py --list`、大きさとキャプションは
[pictogram-catalog.md](../pictogram-catalog.md)。
