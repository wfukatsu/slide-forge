# アカウントグラフ（インフルーエンスマップ / ディスカバリーマップ）

## 目次

- どういう図か
- データモデル
- 検証で止まること
- 抽出（スライド用の間引き）
- draw.io 出力
- 使い分け

## どういう図か

B2B の商談で使う 2 つのグラフ。**どちらも 1 つの JSON から、全体は draw.io へ、
主要部分はスライドへ**出力する。同じ元データを使うのは、隣り合う 2 つの図が
食い違うのを防ぐため。

- **インフルーエンス**: 購買関与者を組織構造でつなぎ、役割・影響度・立場・
  面談の有無を注記する
- **ディスカバリー**: Goal / Strategy / Tactics を上向きの支持関係でつなぐ。
  1 つの Tactics が複数の Strategy を支える多親構造を取れる

2 軸に配置する `influence-map`（`slide-templates/b2b-sales/`）とは別物で、
あちらは位置関係、こちらは**構造**を見せる。

## データモデル

```json
{
  "type": "influence",
  "title": "…",
  "people": [
    {"id": "kaneko", "roles": ["F", "C"], "org": "CFO", "name": "金子",
     "influence": "high", "stance": "close", "met": true,
     "reportsTo": "fukatsu", "note": "資金・経費についての相談役"}
  ],
  "links": [{"from": "a", "to": "b", "label": "二人で話し合って決めている"}]
}
```

| 項目 | 値 | 表示 |
|---|---|---|
| `roles` | `F` 購買者 / `T` 技術者 / `U` 利用者 / `C` コーチ / `S` サポート役員 | 上帯に `F/C` と連結 |
| `influence` | `champion` / `high` / `medium` / `low` | 下帯 |
| `stance` | `close` 親密 / `neutral` / `opposed` 反発 | 本文の塗り |
| `met` | `false` で未面談 | カード全体を破線 |
| `reportsTo` | 上司の `id` | 上下の実線 |
| `links` | 対等な関係・補足 | ラベル付きの横線 |

```json
{
  "type": "discovery",
  "nodes": [{"id": "s1", "tier": "strategy", "text": "…", "owner": "COO"}],
  "edges": [{"from": "t1", "to": "s1"}]
}
```

`tier` は `goal` / `strategy` / `tactics`。`edges` は **支える側 → 支えられる側**。

## 検証で止まること

`account_graph.validate()` が以下を弾く。生成前に必ず通る。

- `id` の重複、存在しない `id` への参照（`reportsTo` / `edges` / `links`）
- 列挙値の誤り（役割・影響度・立場・tier）
- **循環**（`a -> b -> a`）
- **下向きの辺**（`goal -> tactics`）。同 tier どうしは可で、下位目標が上位目標を
  支える形は正しい

## 抽出（スライド用の間引き）

`extract()` はスライドに載る分だけ残す。既定の上限は influence 7 / discovery 8。

**上位 N 件を取るだけでは辺が壊れる。** 途中のノードが消えると、その先の辺が
宙に浮く。そこで残したノードの**祖先を必ず引き込む**。結果が上限を超えることは
あるが、読める図であるほうを優先する。

境目で同点なら、その同点グループごと落とす。同じ重みの兄弟のうち 1 人だけ
載せると、選ばれなかった人が存在しないかのように読めるため。

| グラフ | 優先順位 |
|---|---|
| influence | 影響度 → 購買者役割 (`F`) → 面談済み → 部下の数 |
| discovery | tier（goal > strategy > tactics）→ 支えている数 |

落としたノードは標準出力に列挙される。スライドには「他 N 名は draw.io 版参照」
と明記すること。

## draw.io 出力

```bash
.venv/bin/python scripts/build_account_graph.py <graph.json> --out out/x.drawio
.venv/bin/python scripts/build_account_graph.py <graph.json> --out out/key.drawio --extract
.venv/bin/python scripts/drawio_export.py out/x.drawio --out out/x.png --scale 2
```

カードは**グループ + 3 セル**（帯・本文・帯）。draw.io 上でカードごと動かせて、
各部の塗りは保たれる。辺は必ずグループ id を `source` / `target` にする
（[drawio.md](drawio.md) の規律）。

配置は段組み。influence は `reportsTo` の木で、親は子の中央に寄せる。
discovery は **tier ではなくグラフの深さ**で段を決める。tier で機械的に段を
割ると、上位目標を支える下位目標が同じ段に並んで辺が横に走る。tier は
バッジの色だけを決める。

書き出した PNG は必ず Read で目視確認する。

## 使い分け

| 状況 | 出力 |
|---|---|
| 関与者・項目が少ない | スライドに直接描く |
| 多い | draw.io に全体、スライドには抽出版 |
| 顧客に見せる | **どちらも見せない。** 実在の個人への判断を記録した内部資料 |
