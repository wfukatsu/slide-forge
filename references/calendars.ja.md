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

## 複数スライドへの分割

`scripts/calendar_pages.py data.json --out pages.json` は、1 つのデータセットを
テンプレートのスライドに分ける。月ごと、月曜〜日曜の週ごと（日次リスト）、
グループの切れ目での行のまとまりごと（ガント）に分割する。入力形式は docstring を参照。
