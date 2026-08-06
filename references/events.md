# イベント案内図（events.py）

`diagrams.Canvas` に混ざっている `EventMixin` の使い方。セミナー・勉強会・
カンファレンスの案内デッキで定番の部品を型にしたもので、**オンライン開催・
会場（オフライン）開催・ハイブリッド開催**の 3 形式に対応する。すべて図形だけで
描くのでキーもネットワークも不要、色はテンプレートの配色に従う。座標はインチ、
戻り値は描画領域の下端 y。

デッキ仕様（JSON）の `figures` からも同名の type で使える。実例は
`examples/event-announcement.json`（オンライン / オフライン / ハイブリッド /
プログラムの 4 枚デモ）。

**中身は必ずユーザーの素材から取る。** 日付・会場・URL・登壇者名を勝手に
埋めない。未確定の URL は「申込後にご案内」のような文言にする。

## どれを使うか

| 見せたいもの | 使うもの | 補足 |
|---|---|---|
| 開催形式のラベル | `event_mode_badge` | `event_overview` の `mode` でも自動で付く |
| 日時・会場・参加費・定員 | `event_overview` | ピクトグラム付きの項目リスト |
| プログラム（時刻 × 内容） | `event_timetable` | 1 枚 8 行まで目安 |
| 登壇者の顔ぶれ | `event_speakers` | 1 行 5 人まで。超えたら 2 段 |
| 参加方法（会場 / 配信） | `event_access` | `mode="hybrid"` で 2 パネル並列 |

イベント案内でよく使うピクトグラム: `calendar`（日時）, `pin`（会場）,
`browser`（配信）, `coin`（参加費）, `people`（定員）, `mail`（申込）,
`clock`（受付・締切）。

## event_overview — 開催概要

```python
d.event_overview(x, y, w, rows,
                 mode=None,      # "online" / "offline" / "hybrid"。渡すと先頭にバッジ
                 size=11, term_w=1.15, icon_size=0.34, row_h=0.5)
```

- `rows` は `[ピクトグラム名, 項目, 値]` の並び。
- 値が折り返して 2 行になるなら `row_h` を広げる（自動では広げない —
  はみ出しは `audit_text_fit` が拾う）。

```json
{ "type": "event_overview", "x": 0.5, "y": 1.15, "w": 4.4, "mode": "online",
  "rows": [
    ["calendar", "日時", "2026年9月18日(金) 15:00–17:00"],
    ["browser",  "配信", "Zoom ウェビナー"],
    ["coin",     "参加費", "無料（事前登録制）"]
  ] }
```

## event_timetable — プログラム

```python
d.event_timetable(x, y, w, rows,
                  size=11, time_w=1.55, row_h=0.42, zebra=True)
```

- `rows` は `[時刻, 内容]` か `[時刻, 内容, 登壇者]`。時刻は
  `"15:00–15:30"` のような文字列をそのまま描く。
- 登壇者列の幅は最長の名前から自動確保。長い内容は内容列で折り返さず
  短く書き直すこと（1 行に収まる長さが読みやすい）。
- 行数が多いときは `row_h` を詰めるより 2 枚に分ける（1 枚 8 行まで目安）。

## event_speakers — 登壇者カード

```python
d.event_speakers(x, y, w, speakers,
                 size=10, icon="person", gap=0.24)
```

- `speakers` は `[氏名, 肩書]` か `[氏名, 肩書, 講演タイトル]`。**1 行 5 人まで**
  （6 人以上は 2 回呼んで 2 段に分ける）。
- 高さは固定（肩書まで 1.28 / 講演タイトル付き 1.62）。次のブロックは
  戻り値の y から置く。
- 氏名・肩書は**実在の登壇者の確定情報だけ**を使う。

## event_access — 参加方法パネル

```python
d.event_access(x, y, w, h, mode="hybrid",
               venue={"name": …, "address": …, "access": …},   # offline / hybrid
               online={"platform": …, "url": …, "note": …},    # online / hybrid
               size=10.5)
```

- `mode="offline"` は会場パネルのみ（`venue` 必須）、`"online"` は配信パネルのみ
  （`online` 必須）、`"hybrid"` は両方を左右に並べる（両方必須）。
- パネルの高さは行数に合わせて手で決める: 見出し 0.62 + 1 行 0.34。
  3 行（name / address / access）なら h ≥ 1.7、hybrid で 2 行ずつなら h ≥ 1.4。
- `venue.access`（最寄駅など）と `online.note`（アーカイブ配信など）は省略可。

```json
{ "type": "event_access", "x": 0.5, "y": 3.75, "w": 9.0, "h": 1.4,
  "mode": "hybrid",
  "venue":  {"name": "○○カンファレンスセンター 3F", "address": "東京都港区○○ 1-2-3"},
  "online": {"platform": "Zoom ウェビナー", "url": "視聴 URL は申込後にご案内"} }
```

## event_mode_badge — 開催形式バッジ

```python
d.event_mode_badge(x, y, mode, label=None, size=10)
```

既定の文言は オンライン開催 / 会場開催 / ハイブリッド開催。`label` で
「オンライン開催（無料）」のように差し替えられる。`event_overview` に
`mode` を渡した場合は内部でこれが呼ばれるので、単独で使うのは
表紙・クロージングにバッジだけ置きたいときくらい。

## レイアウトの定石（TITLE_ONLY 1 枚に収める）

- **概要 + 参加方法**: `event_overview`（左 w 4.4）+ `event_access`（右 w 4.35）。
- **ハイブリッドの概要**: `event_overview` を全幅（w 8.9）で上に、
  `event_access mode="hybrid"`（w 9.0, h 1.4）を下に。
- **プログラム + 登壇者**: `event_timetable`（w 9.0, 5 行）の下に
  `event_speakers`（w 9.0, 3 人）— 4 枚目の実例を参照。
