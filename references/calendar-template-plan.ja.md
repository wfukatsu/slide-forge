*[English](calendar-template-plan.md)*

# カレンダー表現テンプレート・スキル作成計画

日付を軸にしたスライド表現（月カレンダー、日単位ガント、縦型日次リストなど）を
`slide-templates/calendar/` パックと専用スキル `calendar-slides` として追加するための
調査結果と実装計画。

## 1. 目的とスコープ

**目的**: 「日付の入った予定・タスクの一覧」を渡すだけで、曜日・週始まり・祝日・
複数日にまたがる予定・スライド分割を正しく扱ったカレンダー系スライドを生成できるようにする。

**スコープに含む**:

- 日付計算エンジンと描画プリミティブ（新規 `scripts/calendars.py`）
- `calendar` パックのテンプレート（§4、段階導入）
- 生成スキル `skills/calendar-slides/`（入力の正規化 → 表現の選択 → 分割 → 生成）
- 日本の祝日データの同梱と更新手順

**スコープに含まない**:

- 月単位の線表 → 既存 `planning/gantt-schedule` を使う（重複させない）
- 等間隔の節目 → `planning/milestone-timeline`、経緯 → `planning/chronology`
- 依存関係つき工程図 → `nexus/roadmap`
- 日付を持たない Now / Next / Later → カレンダーではないので対象外（必要なら planning パックに別途）

## 2. 現状把握

| 項目 | 現状 | カレンダー化への影響 |
|---|---|---|
| `gantt` プリミティブ（`patterns.py`） | 列は任意ラベル、行は列単位の小数、8 行まで | 日付を知らない。休日・今日線・曜日ヘッダーなし。`build_scalar_proposal.py` 等が使っているので**改変せず別プリミティブにする** |
| `$slot` 展開 | 値の置換のみ。式・文字列補間なし | 曜日オフセット、週行数（4〜6）、祝日判定、複数日バーのレーン割り当ては**すべてプリミティブ側で計算**する |
| テンプレートの単位 | 1 テンプレート = 1 スライド | 期間が 1 枚に収まらない場合の分割は、テンプレートの外（スキルのページング処理）で行う |
| 祝日データ | なし（`requirements.txt` にも祝日ライブラリなし） | 同梱データで対応（§3.4） |
| 監査 | `build_deck.py --dry-run --strict` で重なり・はみ出しを検査 | 全テンプレートで監査指摘ゼロを合格条件にする |

## 3. 調査結果（カレンダー表現の類型）

### 3.1 共通の慣習

- **週始まり**: 日本の業務資料では月曜始まりが実務的（ISO 8601 と一致、土日が右端に並ぶ）。
  壁掛けカレンダーの見た目にするなら日曜始まり。Outlook の既定は日曜、Google カレンダーは
  土・日・月から選べる。地域ごとの既定は CLDR weekData に定義されている。
  → `weekStart: "mon" | "sun"`、既定は `mon`。
- **ISO 週番号**: 月曜始まりで、その年最初の木曜を含む週が W1。1/1 が前年の W52/53 に
  属することがあるため、表示は `2026-W38` のように年とセットにする。
- **年度**: 国の会計年度は 4/1〜3/31。企業ごとに異なるため `fiscalStartMonth`（既定 4）で指定し、
  四半期表記は「FY2026 Q1（4〜6月）」のように実際の月を併記する。
- **色（日本）**: 平日は黒、土曜は青、日曜・祝日は赤。色を付けるのは**日付の数字だけ**にし、
  休日のセル背景は薄い面にする。英語・海外向けでは土日とも同じグレー。六曜は扱わない。
  和暦はヘッダーへの任意の併記にとどめる。
- **可読性の下限**: カレンダーは構造上、投影用の 18pt を守れない。**配布資料として読む前提で
  最小 9pt・推奨 10〜12pt**（`design-rules.md` の print 密度に相当）。投影用は粒度を粗くした
  別の表現（週→月など）に切り替える。
- **はみ出し時の優先順位**: ① 文字数上限で省略 → ② 「+N 件」に畳み、詳細は一覧ページへ回す
  → ③ 粒度を上げる（日→週→月） → ④ 期間で複数スライドに分割し「(1/3)」を付ける。

### 3.2 類型ごとの要件と 16:9（10 × 5.625in）での容量

描画領域は、`governing_message` の下 y ≈ 1.05in から出典行の上 y ≈ 4.75in までの
**約 9.0 × 3.7in** として逆算した。

| # | 表現 | 典型用途 | 必要データ | 1 枚の容量（9pt 前後） | 分割単位 |
|---|---|---|---|---|---|
| A | **月カレンダー**（1 週 1 行、7 列 × 4〜6 行） | 月間イベント、研修・展示会、締切告知 | date, title, endDate, category | 1 セル ≈ 1.29 × 0.58in。日付＋予定 2 件＋「+N」、1 件あたり全角 8 文字 | 1 月 = 1 枚 |
| B | **日単位ガント**（1 列 1 日） | PoC・移行・導入の日次計画 | task, group, start, end, milestone, owner, progress | ラベル列 1.6in、トラック 7.4in ÷ 31 日 ≈ 0.24in/日。約 10 行。32〜45 日は日付ラベルを月曜だけに、60 日を超えたら週列にする | 月 or 行グループ |
| C | **縦型日次リスト**（1 行 1 日、下方向） | 直近 2 週間のアクション、納期一覧、切替作業の日次計画 | date, task, owner, due/time, status | 行高 0.32in で約 11 行。同じ日の予定は日付セルを縦に結合 | 週 or 11 行 |
| D | 週タイムテーブル（曜日列 × 時間行） | 研修週、ブース当番、イベント週 | day, start, end, title, room | 9〜18 時の 1 時間刻みで 10 行。30 分の予定まで判読可能。平日だけなら 5 列 | 週 |
| E | 四半期・年間ミニカレンダー（3 / 12 か月） | 年間行事、決算・監査の年間予定、年度計画 | date/range, category | 12 か月は 1 セル ≈ 0.3in・日付 7〜8pt で**配布専用**。セル内に文字は入れず、色と凡例で示す | 四半期 / 年度 |
| F | スプリントカレンダー | スクラムのイベント計画（主流は 2 週スプリント） | sprintNo, start, lengthDays, goal, events | A か B の上にスプリント帯を重ねる。祝日で減った稼働日数を表示 | 月 |
| G | カウントダウン（残り N 日） | リリース・契約更新・移行期限 | deadline, today | 大きな数字＋今日から期限までを塗った月帯。営業日数を併記 | 1 枚 |
| H | ヒートマップカレンダー（草グラフ型） | 稼働率、障害件数、問い合わせ量 | date, value | 53 列 × 7 行 ≈ 370 図形。5 段階の単色グラデーション＋凡例。数値なので出典必須 | 年 |
| I | シフト表・当番表（人 × 日） | 保守当番、オンコール、展示会要員 | person, date, code | 31 列 × 最大 12 人。セルには 1 文字コード＋色。凡例と日別合計行が必須 | チーム |

参考: Google カレンダーの月表示（表示しきれない予定は「他 N 件」に畳む）、MS Project の
非稼働時間の網掛け、Asana・Jira のタイムライン（週・月・四半期のズーム、依存線）、
SlideModel / Slidesgo のカレンダー・ガントテンプレート、Observable Plot / Cal-HeatMap の
calendar heatmap、Scrum.org（スプリントの長さ）。

### 3.3 描画の細則（採用する慣例）

- **複数日にまたがる予定（A）**: セル上部にレーンを確保して帯で描く。週をまたぐ場合は週ごとに分割し、
  続きの側の端は角を丸めない。タイトルは各週の最初の区間に再掲する。帯がレーンを先に取り、
  残りの行数を単日の予定に割り当てる（Google カレンダーと同じ方式）。
- **前後月の日付（A）**: 薄いグレーで表示するか、非表示にする（`showAdjacent`）。
- **ガント（B）**: 休日・非稼働日は縦の網掛けをバーの背面に描く。今日は赤の縦線に「今日」ラベル。
  マイルストーンはひし形。進捗はバー内部を濃い色で塗り分ける。グループは見出し行で区切る。
  依存線は第 1 段階では描かない（既存 `gantt` と同じ判断。必要なら `nexus/roadmap`）。
- **状態（C）**: ピル型の色チップに、色だけに頼らないよう文字も併記する。土日祝の行は背景を薄く塗る。

### 3.4 祝日データ

- **一次情報**: 内閣府「国民の祝日」CSV（`https://www8.cao.go.jp/chosei/shukujitsu/syukujitsu.csv`、
  1955 年以降、Shift_JIS、CC BY）。振替休日・国民の休日を含む公表値。
- **方針**: UTF-8 に変換したスナップショットを `assets/holidays/jp.csv` として同梱し、出典（CC BY）を
  併記する。更新は `scripts/update_holidays.py` で行う。**新しい Python 依存は増やさない**。
  生成時はネットワークを使わない（`--dry-run` を壊さない）。
- **収録範囲外の年**: 推定で埋めずに警告を出し、`extraHolidays` による明示指定を促す。
- **会社独自の休日**（年末年始・夏季休暇・創立記念日）: `extraHolidays: [["2026-12-29", "年末休業"], …]`
  で追加する。`workdays`（既定は月〜金）で、非稼働の曜日も変えられるようにする。

## 4. 作るもの

### 4.1 日付エンジン＋プリミティブ（`scripts/calendars.py` の `CalendarMixin`）

以下は計画時点の名前で、実装で変わったものがある（`month_matrix` →
`month_weeks`、`iso_week` → `iso_week_label`、`load_holidays` → `holidays_for`、
`paginate` は `calendar_pages.py` 側に移った）。実装後の名前は英語版 §4.1 と
コードを参照のこと。

描画を伴わない純粋関数（ユニットテストの対象）:

| 関数 | 役割 |
|---|---|
| `month_matrix(year, month, week_start)` | 週 × 曜日の日付行列（4〜6 行）と、前後月の判定 |
| `iso_week(date)` / `fiscal_quarter(date, start_month)` | 週番号・年度四半期のラベル |
| `load_holidays(years, extra)` / `is_offday(date, workdays, holidays)` | 休日の判定と、休日名の取得 |
| `business_days(start, end)` | 営業日数（F・G 用） |
| `pack_lanes(spans, week_rows)` | 複数日バーを週ごとに分割し、レーンを割り当てる |
| `choose_scale(start, end)` | 期間の長さから day / week / month の粒度を選ぶ（§3.2 B の閾値） |
| `paginate(items, unit)` | 月・週・行数単位でページに分割する |

JSON から呼べるプリミティブ（`build_deck.py::FIGURES` に登録）:

| figure | 表現 | 主な引数 |
|---|---|---|
| `month_calendar` | A（F の帯重ねを含む） | `month`（"2026-09"）, `events`, `weekStart`, `weekNumbers`, `showAdjacent`, `extraHolidays`, `maxPerCell` |
| `day_gantt` | B | `start`, `end`, `tasks`, `today`, `scale`（auto/day/week）, `groups` |
| `day_agenda` | C | `start`, `end`, `items`, `columns`, `showEmptyDays` |
| `week_timetable` | D | `week`（週の開始日）, `events`, `hours`, `days` |
| `mini_calendars` | E / G | `months`, `marks`, `cols` |
| `calendar_heatmap` | H | `year`, `values`, `buckets` |
| `shift_roster` | I | `start`, `end`, `people`, `codes` |

全プリミティブの共通ルール:

- 日付は ISO 文字列（`YYYY-MM-DD`）のみ受け付ける。
- 範囲外の日付、`end < start`、容量超過は `ValueError`（i18n の `register()` を通す）。
- 色は Palette のトークンから取る。休日色は新トークンを増やさず、`accent` / `muted` の既存トークンに割り当てる。
- 戻り値は、描画した領域の下端の y 座標（既存の慣習どおり）。

### 4.2 テンプレート（`slide-templates/calendar/`）

| 段階 | id | 表示名 | 答える問い | 主なプリミティブ |
|---|---|---|---|---|
| **P1** | `month-calendar` | 月間カレンダー | この月のどの日に何があり、どこが混んでいるか | `month_calendar` |
| **P1** | `daily-gantt` | 日単位ガント | 指定期間の作業が日単位でどう並行し、休日を挟んでいつ終わるか | `day_gantt` |
| **P1** | `daily-agenda` | 日次タスクリスト | 日ごとに誰が何をいつまでにやるか | `day_agenda` |
| P2 | `weekly-timetable` | 週間タイムテーブル | この週の、何時にどこで何があるか | `week_timetable` |
| P2 | `sprint-calendar` | スプリントカレンダー | 各スプリントの期間・稼働日数・イベント日はいつか | `month_calendar`（帯重ね） |
| P2 | `year-at-a-glance` | 年間カレンダー | 年度の中で、繁忙期と重要日がどこにあるか | `mini_calendars` |
| P2 | `deadline-countdown` | 期限カウントダウン | 期限まで残り何日（何営業日）か | `metric` ＋ `mini_calendars` |
| P3 | `activity-heatmap` | 日次ヒートマップ | どの曜日・時期に量が集中しているか | `calendar_heatmap` |
| P3 | `shift-roster` | 当番表 | 各日に誰が当番で、手薄な日はどこか | `shift_roster` |

- **週始まり**: 月曜・日曜で別テンプレートにはせず、スロット `weekStart`（既定 `"mon"`）で切り替える。
  カタログでは両方の作例を示すため、`example.json`（月曜始まり）と `example.sun.json` を置き、
  カタログ生成で両方を描く（`examples` のキー拡張が必要か、実装時に確認する）。
- **密度**: `defaultDensity: "print"`。presentation 版は、表示件数と文字数の上限を下げたものにする。
- **inferenceLevel**: すべて `descriptive`。H だけは数値を扱うため `source` を必須にする。
- **共通ガードレール**（各テンプレートに具体化して書く）:
  - 予定（計画値）と実績を混ぜない。計画値は `source` に「いつ時点の計画か」を書く。
  - 未確定の日付は「仮」と明記する（`tentative: true` で点線枠にする）。
  - 祝日は同梱データの収録年だけ自動で判定する。会社独自の休日は明示的に渡す。
  - 1 セル・1 行に詰め込まない。上限を超えたら分割か一覧化する（黙って省略しない）。
  - 顧客の実名・個人名を作例に使わない（このリポジトリは public）。

### 4.3 スキル `skills/calendar-slides/`

`analysis-template-creator` と同じく、スキーマ・検証・登録の共通規約は `slide-template-creator` に
委ねる。その上で、次の 2 つの役割を持つ:

1. **生成（主）**: 予定・タスクを受け取り、カレンダー系スライドを作る。
   - **入力**: Markdown・CSV の表、Google スプレッドシート、Google カレンダー
     （MCP で読む場合は、対象カレンダーと期間をユーザーに確認してから読む）。
   - **正規化**: `scripts/calendar_normalize.py` で ISO 日付に揃え、曖昧な日付（「来週水曜」「9/3」の年）は
     推測で埋めずに確認する。
   - **表現の選択**: 問い（何を見せたいか）と期間の長さから A〜I を推薦する（決定表を SKILL.md に置く）。
     ユーザーの承認を得てから次へ進む。
   - **分割**: `scripts/calendar_pages.py` で期間を月・週・行単位のテンプレート入力に分け、
     `assemble_spec.py` に渡せる JSON を出す。
   - **検証と生成**: `build_deck.py --dry-run --strict` → 生成 → 任意で `slide-qa`。
     マスター指定があれば `google-slides-template`、なければ `google-slides` の経路に乗る。
2. **保守（従）**: calendar パックのテンプレートとプリミティブを追加・修正するときの固有ルール
   （境界ケースの一覧、容量表、祝日データの更新手順）。

同梱ファイル: `SKILL.md` / `SKILL.ja.md` / `references/form-selection.md`（表現の決定表）/
`references/capacity.md`（§3.2 の容量表と閾値）/ `agents/openai.yaml`。

## 5. 検証計画

### 5.1 ユニットテスト（`tests/test_calendars.py`、API 不要）

| ケース | 期待 |
|---|---|
| 2027-02（1 日が月曜・28 日）、月曜始まり | 4 行 |
| 2026-08（1 日が土曜・31 日）、月曜 / 日曜始まり | どちらも 6 行 |
| 2026-09 のシルバーウィーク | 9/21 敬老の日、9/22 国民の休日、9/23 秋分の日を判定 |
| 2026-12-28 〜 2027-01-04 の ISO 週 | 年またぎの W53 / W1 のラベル |
| 月末から翌週にまたがる複数日予定 | 週ごとに 2 区間に分かれ、レーンが衝突しない |
| 31 / 45 / 61 日の期間 | `choose_scale` が day / day（月曜だけラベル）/ week を返す |
| 同梱データの収録範囲外の年 | 警告を出し、推定で埋めない |

### 5.2 テンプレート検証

- `validate_slide_templates.py --pack calendar` で、両密度とも監査指摘ゼロ。
- 境界サイズの入力（1 日 5 件、最長ラベル、6 行の月、31 日の期間、11 行のリスト）を
  `examples/calendar-boundary.json` として持ち、同じく指摘ゼロにする。
- `gantt` を改変しないので、既存パックの回帰は起きない想定。念のため `planning` と `scalar-ae` も再検証する。

### 5.3 ビジュアル QA

- カタログデッキを生成し、`slide-qa` で全ページを確認する。重点は、ASCII の多いラベルの折り返し、
  土曜青・日曜赤のコントラスト、複数日バーの切れ目、「+N 件」の位置。
- ヒートマップ（約 370 図形）は batchUpdate の分割が効くことを確認する。
- 確認後、`cleanup_qa.py` で QA ファイルを消す。

## 6. 登録と周辺の更新

- `slide-templates/manifest.json` への登録、`references/slide-template-catalog(.ja).md` と
  `references/i18n/slide-template-catalog.en.json` の更新（`build_template_catalog_doc.py`）
- `build_deck.py::FIGURES` への登録、`references/calendars(.ja).md`（プリミティブのリファレンス）の新規作成、
  `template-schema` への追記
- ルーティング: `commands/forge(.ja).md`、`AGENTS(.ja).md` のスキル表、
  [references/workflow-contract.md](workflow-contract.ja.md) の段階読込表
- `README(.ja).md` のパック数・テンプレート数・スキル一覧、`.claude-plugin/marketplace.json` の
  説明文（スキル数）とバージョン
- 本計画書の英語版 `calendar-template-plan.md`

## 7. 実装順序

1. `calendars.py` の純粋関数、祝日データ、`tests/test_calendars.py`
2. `month_calendar` / `day_gantt` / `day_agenda` の各プリミティブと FIGURES 登録
3. P1 テンプレート 3 種と作例、境界サイズの入力でオフライン検証
4. `calendar_normalize.py` / `calendar_pages.py` とスキル文書
5. カタログ生成とビジュアル QA（ここで一度レビューを受ける）
6. P2 → P3 を同じ手順で追加
7. 周辺ドキュメントの更新とバージョン更新

## 8. 決定事項（2026-09-15 のサンプルデッキレビューで承認）

| 論点 | 決定 |
|---|---|
| 最初に作る範囲 | P1 の 3 種（`month-calendar` / `daily-gantt` / `daily-agenda`）＋日付エンジン。P2・P3 は P1 のレビュー後 |
| スキル構成 | 生成と保守を 1 スキル `calendar-slides` にまとめる |
| 週始まりの既定 | `mon`。週番号は月曜始まりでだけ出す |
| 1 マスの予定件数 | レーンに入る分（6 行の月で 1 件、5 行で 2 件、4 行で 3 件）＋「+N件」。時刻より件名を優先する |
| ガントの粒度切替 | 31 日まで全日ラベル、60 日まで月曜ラベル、61 日〜26 週は週列 |
| 休日の見せ方 | 日付の数字に色（土曜青・日曜祝日赤）＋薄い面 |
| 祝日データ | 内閣府 CSV を `assets/holidays/jp.csv` に同梱（依存ゼロ・オフライン）。`jpholiday` は採用しない |
| Google カレンダーからの取り込み | P1 では表・CSV・シート入力のみ |
| パック | 新規 `calendar` パック。月単位の `gantt-schedule` は planning に残す |

## 9. P1 の実装状況（2026-09-15）

計画からの変更点:

- **タイトルは 1 行・全角 36 字まで。** `governing_message`（17pt・幅 9.0in）は 1 行に全角約 36.8 字で、
  2 行目がカレンダーの見出し（y 1.05）に重なるため、3 テンプレートとも `title` の上限を 36 にした。
- **密度の 2 版（`$density`）は P1 では作らない。** カレンダーは構造上 8.5〜9pt が下限で、
  投影用の粗い版は表現を変える（期間を縮める・一覧化する）ほうが効くため。
- **正規化は `calendar_pages.py` に含めた**（`calendar_normalize.py` は作らない）。日付の正規化と
  年のない日付の拒否は `calendars.parse_date` が担う。
- `calendar_pages.py` はテンプレートを展開済みのスライド（`{"slides": [...]}`）を出力する。
  P1 の時点でデッキ仕様の `$template` 展開が存在しなかったためで、この前提は後に解消された
  （`build_deck.expand_slide_templates`）。カレンダーは日付の正規化とページ分割を先に行う
  必要があるため、出力形式は展開済みのままでよい。
- P1 はコミット `a26a338`（ブランチ `feat/calendar-templates`）。

## 10. P2 の実装状況（2026-09-15）

`weekly-timetable` / `sprint-calendar` / `year-at-a-glance` / `deadline-countdown` と、
プリミティブ `week_timetable` / `sprint_calendar` / `year_calendar` / `deadline_countdown` を追加した。

計画・試作からの変更点:

- **重なる予定の列分けは自動にした**（`assign_tracks`）。試作では手で列を指定していた。
  3 件以上の重なりはエラーにし、部屋やトラックでページを分ける。
- **30 分の予定は、枠を空で描いてラベルを重ねる。** 高さ約 0.18in の枠では
  Slides の上下の余白に文字が収まらず、はみ出したため。
- **スプリントの計画・レビュー・リリースの日は自動で置く**（最初と最後の稼働日）。
  実際の開催日が違う運用ではこのテンプレートを使わない、とガードレールに書いた。
- **期限カウントダウンは、期限が今日の月か翌月にある場合だけ**に絞った。
  それより先の期限は月間カレンダーか日単位ガントで見せる。
- 年間カレンダーは試作どおり 7pt の配布資料専用とし、投影には `planning/gantt-schedule` を案内する。
- P2 はコミット `9333528`。

## 11. P3 の実装状況（2026-09-15）

`activity-heatmap` / `shift-roster` と、プリミティブ `calendar_heatmap` / `shift_roster` を追加し、
計画の 9 形式がそろった。

計画・試作からの変更点:

- **ヒートマップの欠測と 0 を区別する。** 値のない日は枠つきの白、0 は最も薄い色にし、
  欠測があるときだけ凡例に「データなし」を出す。
- **色の区切りは期間内の分位**（既定 5 段階、3〜7 で指定可）。凡例に区切りの値を出し、
  別期間の図と色を比べないことをガードレールに書いた。
- **集計カードはプリミティブが計算する**（曜日別平均、月別合計、祝日平均）。解釈は描かない。
- **マスの大きさは高さにも合わせる。** 短い期間ではマスが大きくなりすぎて高さを超えるため、
  幅と高さの両方から決め、0.1in を下回ったらエラーにする。
- **当番表の予定は 1 日 1 文字の文字列**（例: `日日夜休…`）で渡す。スロットの JSON が短く、
  日数との不一致も検出しやすいため。人数に数えるかどうかはコードごとに指定する。
- `calendar_pages.py` はヒートマップを 52 週ごと、当番表を月ごと・12 人ごとに分ける。

## 関連

- [カレンダーの図（`calendars.py`）](calendars.ja.md)
- [スライドテンプレート カタログ（全 101 種）](slide-template-catalog.ja.md)
- [デッキ生成のワークフロー契約](workflow-contract.ja.md)
