*[English](calendars.md)*

# カレンダーの図（`calendars.py`）

座標ではなく日付を入力にする描画部品。`diagrams.Canvas` に組み込まれ、仕様の
figure として登録されている。`slide-templates/calendar` パックと `calendar-slides`
スキルが使う。

| 見せたいもの | 使うもの | 補足 |
|---|---|---|
| 1 か月の予定をマスに書く | `month_calendar` | 月曜 / 日曜始まり、複数日の帯 |
| 日（または週）単位の作業と休日の網掛け | `day_gantt` | 日列は 60 日、週列は 26 週まで |
| 日ごとのタスク一覧 | `day_agenda` | 日付セルの結合、休日の畳み込み |
| 1 週間を時間単位で | `week_timetable` | 5 列か 7 列、重なる予定は横に並べる |
| 連続するスプリント | `sprint_calendar` | スプリントごとの稼働日数、イベント日は自動で配置 |
| 年度全体の俯瞰 | `year_calendar` | 12 か月のミニカレンダー、繁忙期・休業・重要日（配布資料の密度） |
| 期限までの残り日数 | `deadline_countdown` | 暦日と営業日、節目 |
| 月単位の計画 | `gantt`（`patterns.ja.md`） | 列ラベルだけで日付を持たない |

共通の約束:

- 日付は `YYYY-MM-DD` の文字列（または `datetime.date`）。`YYYY/M/D` も受け付ける。
  年のない日付は `ValueError` になる。
- 土曜の数字は青、日曜・祝日の数字は赤。マスや列には薄い色を塗る。祝日は
  `assets/holidays/jp.csv`（`scripts/update_holidays.py` で更新）から判定する。
  収録範囲外の年は警告を出し、土日だけを休日として扱う。
- `extra_holidays` で会社の休業日を足す: `[[日付, 名前], ...]` か `[[開始, 終了, 名前], ...]`。
- どの部品も描画領域の下端 y を返す。読めなくなる入力は `ValueError` で止まるので、
  `scripts/calendar_pages.py` で期間を分割する。

## month_calendar — 月間カレンダー

```python
d.month_calendar(x, y, w, h, month, events,
                 week_start="mon",      # "mon" か "sun"
                 week_numbers=None,     # 既定: "mon" なら表示、"sun" なら非表示
                 extra_holidays=None,
                 size=8.5)
```

- `month` は `"2026-09"`。前後の月の日付（灰色）を含めて 4〜6 行の週になる。
- `events` は `[開始, 終了, 件名, 分類, 時刻]`。終了が空（または開始と同じ）なら
  1 日の予定として「10:00 定例」とマスに書く。それ以外は日をまたぐ帯になり、
  週の行ごとに分かれて、続きには「（続き）」が付く。
- `分類`: `primary / success / danger / info / warning / muted` か空。
- 帯が先にレーンを取り、1 日の予定が残りのレーンを使う。入らない分は「+N件」。
  マスの件名は、まず時刻を落とし、それでも長ければ「…」で切る。
- ISO 週番号（「W38」）は、既定では月曜始まりのときだけ出す。

```json
{ "type": "month_calendar", "x": 0.5, "y": 1.05, "w": 9.0, "h": 3.65,
  "month": "2026-09", "weekStart": "mon",
  "events": [["2026-09-14", "2026-09-18", "データ移行検証", "primary", ""],
             ["2026-09-18", "", "判定会議", "danger", "15:00"]],
  "extraHolidays": [] }
```

## day_gantt — 日単位ガント

```python
d.day_gantt(x, y, w, h, start, end, rows,
            today=None,          # "2026-09-15": 日付ラベルを赤くし、点線を引く
            scale="auto",        # "auto" / "day" / "week"
            label_w=1.8,
            extra_holidays=None,
            size=9)
```

- `rows`: `["group", 名前]`、`["task", 名前, 担当, 開始, 終了, 進捗]`、
  `["milestone", 名前, 担当, 日付]`。テンプレートのタプルでは使わない欄を `""` / `0` で埋める。
- `scale="auto"`: 60 日までは 1 列 1 日（31 日までは全日にラベル、それ以上は月曜に
  日付と ISO 週）、26 週までは 1 列 1 ISO 週。それより長い期間はエラーになるので、
  月単位の `gantt` を使う。
- 休日はバーの背面に網掛けする（週列では、祝日・休業日が 2 日以上ある週）。
- タスクの注記は営業日数（`5営業日`、週列では `6週・26営業日`）と進捗率。
  マイルストーンはひし形で、日付を添える。
- 1 行に 0.24in 必要。`start`〜`end` の外の日付はエラーになる。

```json
{ "type": "day_gantt", "x": 0.5, "y": 1.05, "w": 9.0, "h": 3.65,
  "start": "2026-09-14", "end": "2026-10-14", "today": "2026-09-15",
  "rows": [["group", "準備フェーズ", "", "", "", 0],
           ["task", "環境構築", "基盤", "2026-09-16", "2026-09-25", 0.6],
           ["milestone", "判定会議", "PM", "2026-10-08", "", 0]] }
```

## day_agenda — 日次タスクリスト

```python
d.day_agenda(x, y, w, h, start, end, items,
             today=None,
             extra_holidays=None,
             show_empty_days=False,   # 予定のない平日に「予定なし」の行を出す
             size=9,
             col_widths=None)         # 比率。既定 [1.25, 4.35, 1.1, 1.0, 1.3]
```

- `items` は `[日付, 内容, 担当, 期日, 状態]`。同じ日のタスクは日付セルを縦に結合する。
  期日が空なら「—」と表示する。
- 予定のない休日の連続は 1 行に畳み、休日名を添える
  （「9/19（土） 〜 9/23（水）　土日・祝日（敬老の日・休日・秋分の日）」）。
- `状態`: `完了 / 進行中 / 予定 / 遅延 / 中止`、または `done / doing / todo / late / cancelled`。
  文字入りのチップで示す。
- 行の高さは 0.30in で、0.24in まで縮む。それを超える行数はエラーになる。

```json
{ "type": "day_agenda", "x": 0.5, "y": 1.05, "w": 9.0, "h": 3.65,
  "start": "2026-09-14", "end": "2026-09-25", "today": "2026-09-15",
  "items": [["2026-09-15", "セキュリティ審査の資料提出", "情シス", "12:00", "完了"]] }
```

## week_timetable — 週間タイムテーブル

```python
d.week_timetable(x, y, w, h, week, events,
                 days=5,                 # 5（月〜金）か 7
                 start_hour=9, end_hour=18,
                 breaks=None,            # 既定 [["12:00", "13:00", "昼休憩"]]
                 extra_holidays=None,
                 size=8.5)
```

- `week` はその週の任意の日付。列はその週の月曜から始まる。
- `events` は `[日付, 開始, 終了, 件名, 場所, 分類]`。時刻は `HH:MM`。同じ日に重なる予定は
  横に並べ（`assign_tracks`）、3 件同時に重なるとエラーになる。
- 1 時間に 0.30in 必要。予定の枠は 8pt 1 行が入る高さが必要
  （テンプレートの 3.65in・9〜18 時なら 30 分）。
- 高さ 0.62in 以上の枠は時間帯・件名・場所、それより低い枠は「9:30 件名」、
  横に並んだ狭い枠は件名だけを表示する。
- 休憩は、その時間に予定がない日だけ灰色の帯で出る。予定のない祝日は休日名で塗る。

```json
{ "type": "week_timetable", "x": 0.5, "y": 1.05, "w": 9.0, "h": 3.65,
  "week": "2026-10-05", "days": 5, "startHour": 9, "endHour": 18,
  "events": [["2026-10-05", "09:30", "12:00", "オリエンテーション", "大会議室", "primary"]],
  "breaks": [["12:00", "13:00", "昼休憩"]] }
```

## sprint_calendar — スプリントカレンダー

```python
d.sprint_calendar(x, y, w, h, start, sprints,
                  length_days=14,        # 7 か 14
                  extra_holidays=None,
                  size=8.5)
```

- `start` は月曜にする。`sprints` は `[番号, ゴール, リリースの有無]` で、連続して並ぶ。
  週の行は 8 行まで（2 週スプリントなら 4 本、1 週なら 8 本）。
- 左のパネルに期間、稼働日数と祝日で減った平日の数（「休日 -1」）、ゴールを出す
  （1 週の行では期間を 2 行目にまとめる）。
- 最初の稼働日に「計画」（月曜が休日なら「計画（振替）」）、最後の稼働日に「レビュー」、
  `release` が true なら赤の「リリース」を置く。

```json
{ "type": "sprint_calendar", "x": 0.5, "y": 1.05, "w": 9.0, "h": 3.65,
  "start": "2026-09-28", "lengthDays": 14,
  "sprints": [["12", "検索 API の公開", false], ["13", "権限管理の追加", true]] }
```

## year_calendar — 年間カレンダー

```python
d.year_calendar(x, y, w, h, start_month, marks,
                extra_holidays=None,
                size=7)
```

- `start_month`（年度なら "2026-04"）から 12 か月を 6 か月ずつ 2 段に並べる。
  日付は 7pt なので配布資料向け。
- `marks` は `[開始, 終了, ラベル, 種類]`。`busy` は青、`off` は赤で期間を塗り、
  `key` は開始日を丸で囲む（終了は空）。12 か月の外の日付はエラーになる。
- 凡例には種類ごとのラベルが並ぶ。数字も赤くしたい休業日は `extra_holidays` にも入れる。

```json
{ "type": "year_calendar", "x": 0.5, "y": 1.05, "w": 9.0, "h": 3.65,
  "startMonth": "2026-04",
  "marks": [["2026-04-01", "2026-04-24", "決算", "busy"],
            ["2026-06-25", "", "株主総会", "key"]] }
```

## deadline_countdown — 期限カウントダウン

```python
d.deadline_countdown(x, y, w, h, deadline, today, label,
                     checkpoints=None,   # [日付, 名前] を 3 件まで
                     extra_holidays=None)
```

- 暦日の残り日数（`deadline - today`）を大きく出し、今日から期限前日までの営業日数と、
  「あとN日」つきの節目を並べる。
- 右に今日の月と翌月を並べ、残りの日を塗る。期限はそのどちらかの月にあること
  （それより先なら `month_calendar` / `day_gantt`）。h は 3.3in 以上必要。

```json
{ "type": "deadline_countdown", "x": 0.5, "y": 1.05, "w": 9.0, "h": 3.65,
  "deadline": "2026-10-14", "today": "2026-09-15", "label": "本番切替まで",
  "checkpoints": [["2026-09-18", "判定会議"]] }
```

## 日付エンジン

`calendars.py` の純粋関数。`tests/test_calendars.py` でテストしている。

| 関数 | 戻り値 |
|---|---|
| `parse_date(value)` / `parse_month(value)` | `date` / `(年, 月)` |
| `month_weeks(year, month, week_start)` | 7 日ずつの週の行 |
| `holidays_for(years, extra)` | `{日付: 名前}`（同梱データ + 休業日） |
| `business_days(start, end, holidays)` | 両端を含む営業日数 |
| `iso_week_label(day)` | `"2026-W53"` |
| `fiscal_quarter(day, start_month=4)` | `(年度, 四半期)` |
| `choose_scale(start, end)` | `"day"` / `"week"` |
| `pack_lanes(spans, nlanes)` | レーンの割り当てとあふれ |
| `agenda_entries(start, end, items, holidays)` | 日・休日・予定なしの行 |
| `parse_time(value)` / `format_time(hours)` | `9.5` / `"9:30"` |
| `assign_tracks(intervals)` | 区間ごとの（列, 重なりのまとまりの列数） |
| `sprint_ranges(start, count, length_days)` | 連続するスプリントの期間 |
| `months_from(start_month, count)` | `[(年, 月), ...]` |

## 複数スライドへの分割

`scripts/calendar_pages.py data.json --out pages.json` は、1 つのデータセットを
テンプレートのスライドに分ける。月ごと、月曜〜日曜の週ごと（日次リスト・タイムテーブル）、
グループの切れ目での行のまとまりごと（ガント）、週 8 行ごと（スプリント）に分割する。
年間カレンダーとカウントダウンは 1 枚ずつ。入力形式は docstring を参照。
