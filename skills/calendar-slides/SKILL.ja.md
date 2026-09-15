---
name: calendar-slides
description: >-
  Turn dated tasks and events into calendar slides — month grid (Monday or
  Sunday start), day-by-day gantt, or a day-by-day task list — with Japanese
  holidays, multi-day spans and automatic page splits; also maintains the
  slide-templates/calendar pack.
  Use for: カレンダーでスケジュールを見せたい, 月間予定表, 日単位のガント, 日次タスク一覧,
  calendar slide, monthly calendar, daily gantt.
  Not: month-level plans (planning/gantt-schedule); milestone-only timelines
  (planning/milestone-timeline).
---
*[English](SKILL.md)*

# カレンダースライド

日付のついたタスクや予定から、カレンダーそのものを軸にしたスライドを作る。
日付の計算（曜日の位置、4〜6 行の週、祝日、週をまたぐ帯、営業日数、ページ分割）は
`scripts/calendars.py` と `scripts/calendar_pages.py` が担う。**カレンダーの座標を手で計算しない。**

コマンドはすべて slide-forge のルートで `.venv/bin/python` を使って実行する。
デッキの流れ（承認 → 検証 → 生成 → QA → 納品）は `references/workflow-contract.md` に従う。

## 担当範囲

| 依頼 | 行き先 |
|---|---|
| 日付のある予定・タスクを、月間カレンダー・日単位ガント・日次タスクリストで見せる | このスキル |
| 月・四半期単位の計画（列ラベルだけの線表） | `planning/gantt-schedule`（`google-slides(-template)` 経由） |
| 等間隔の節目・経緯 | `planning/milestone-timeline`、`planning/chronology` |
| 依存関係で組むロードマップ | `nexus/roadmap` |
| カレンダーのページを一部に含むデッキ全体 | 生成スキル（`google-slides` / `google-slides-template`）。カレンダーのページはこのスキルの手順で作る |
| カレンダーのテンプレートやプリミティブの追加・変更 | このスキルの「カレンダーパックの保守」 |

## テンプレート

| id | 見せ方 | 1 枚の容量 | `calendar_pages.py` の分割単位 |
|---|---|---|---|
| `month-calendar` | 1 週 1 行。1 日の予定はマスに、複数日は帯で | 1 日約 2 件、超えたら「+N件」 | 1 か月 1 枚 |
| `daily-gantt` | 1 列 1 日（60 日まで）か 1 列 1 ISO 週（26 週まで） | 12 行 | グループの切れ目 |
| `daily-agenda` | 1 行 1 タスク、日付が下方向に並ぶ | 11 行（連続する休日は 1 行） | 月曜〜日曜の週 |

選び方は [form-selection.md](references/form-selection.md)、容量と閾値の根拠は
[capacity.md](references/capacity.md)、プリミティブの引数は `references/calendars.ja.md` にある。

## 手順

### 1. ヒアリング

足りないものだけを 1 回でまとめて聞く。

- 伝えたい結論（タイトル。全角 36 字以内・1 行）
- 期間（開始・終了、または対象の月）
- データ: 貼り付けた表、CSV、Google スプレッドシート、既存の資料。
  Google カレンダーからの自動取り込みはまだない。書き出すか貼り付けてもらう
- 週始まり（既定 `mon`。壁掛けカレンダーの見た目が期待される場合は `sun`）
- 祝日以外の会社休業日（年末年始、夏季休業など）
- いつ時点の情報か（`today` の強調と `source` の行に使う）
- デッキの位置づけ（単独ページか、大きなデッキの一部か）、マスター、QA の有無（既定は実行）

### 2. 正規化

`out/<deck>/calendar-data.json` を `calendar_pages.py` の入力形式（docstring 参照）で書く。

- 日付は `YYYY-MM-DD`（`YYYY/M/D` も可）。**年のない日付は推測せず、必ず確認する。**
  「来週水曜」のような相対表現もユーザーと確定させる。
- `month-calendar` の予定: `[開始, 終了, 件名, 分類, 時刻]`。1 日の予定は終了を空にする。
  分類は `primary / success / danger / info / warning / muted` か空。
- `daily-gantt` の行: `["group", 名前, "", "", "", 0]`、
  `["task", 名前, 担当, 開始, 終了, 進捗 0〜1]`、`["milestone", 名前, 担当, 日付, "", 0]`。
- `daily-agenda` の項目: `[日付, 内容, 担当, 期日, 状態]`。状態は
  `完了 / 進行中 / 予定 / 遅延 / 中止`（`done / doing / todo / late / cancelled` も可）。
- 計画と実績を混ぜない。進捗を載せるなら `source` に集計時点を書く。

### 3. 分割と承認

```bash
.venv/bin/python scripts/calendar_pages.py out/<deck>/calendar-data.json \
    --out out/<deck>/pages/200-calendar.json
```

ページ数、各ページの期間、タイトルを示す。自動で付く「（1/3）」は仮置きなので、
ページごとの結論を提案して `titles` で渡す。生成の前に承認を得る。

### 4. 検証と生成

必要なら他のページと結合し（`scripts/assemble_spec.py`）、次を実行する。

```bash
.venv/bin/python scripts/build_deck.py --template templates/blank-16x9.json \
    --spec out/<deck>/deck.json --dry-run --strict
.venv/bin/python scripts/drive_folder.py create "<デッキ名>"
.venv/bin/python scripts/build_deck.py --template templates/blank-16x9.json \
    --spec out/<deck>/deck.json --title "<デッキ名>" --folder <FOLDER_ID>
```

カレンダーのページは `BLANK` レイアウトとパレットのトークンだけを使うので、
`blank-16x9.json` の代わりに登録済みのマスターも使える。プリミティブのエラー
（期間外の日付、行数超過、未知の状態など）は dry-run で止まる。直すのはデータで、
テンプレートではない。`calendar-data.json` と仕様ファイルもフォルダにアップロードする。

### 5. ビジュアル QA

`slide-qa` を実行する。カレンダー固有の確認点は次のとおり。

- 「+N件」がどのマスに付いているか
- 週をまたぐ帯が行ごとに分かれ、「（続き）」が付いているか
- 土曜が青、日曜・祝日が赤になっているか
- 休日の網掛けがバーを隠していないか
- 注記が今日の線とぶつかっていないか
- タイトルが 1 行に収まっているか

### 6. 報告

デッキとフォルダの URL、ページと期間、同梱の祝日データの範囲外だった年
（スクリプトが警告を出す）、QA の結果と後片付けを報告する。

## カレンダーパックの保守

スキーマ・検証・登録・互換性は [`slide-template-creator`](../slide-template-creator/SKILL.md) に従う。
加えて次を守る。

1. **入力は日付、座標は出力。** スロットは ISO 文字列を受け取り、カレンダーの計算は
   すべて `calendars.py` の純粋関数に置く（`tests/test_calendars.py` でテストする）。
   描画に使う前に、純粋関数とテストを先に足す。
2. **二重に守る。** スロットの上限で作例の監査をゼロに保ち、読めなくなる入力
   （行が低すぎる、期間が長すぎる、期間外の日付）はプリミティブが `ValueError` で止める。
   `calendar_pages.py` の分割も同じ上限に合わせ、変えるときは両方を変える。
3. **境界入力**（`tests/test_calendars.py` が網羅する）を必ず通す:
   - 4 行の月（2027-02、月曜始まり）、6 行の月（2026-08）、日曜始まり
   - 週と月をまたぐ帯、帯のあるマスでの「+N件」
   - 31 / 60 / 61 日のガント、年末年始の休業を含む 26 週のガント
   - 連続する休日を畳んだ日次リスト
   - 最長のタイトル
4. **祝日。** `assets/holidays/jp.csv` を手で編集しない。`scripts/update_holidays.py` を
   実行する（毎年 2 月に内閣府が翌年の春分・秋分を公表した後に 1 回）。
5. **検証。** `validate_slide_templates.py --pack calendar` と単体テストを実行し、
   共有プリミティブを変えたときは全パックも検証する。そのうえでカタログ
   （`build_slide_template_catalog.py --pack calendar`）を生成して `slide-qa` にかけ、
   `references/images/slide-templates/<id>.png` とカタログ文書を更新する。

計画済みで未実装のもの（`references/calendar-template-plan.ja.md` 参照）:
週間タイムテーブル、スプリントカレンダー、年間カレンダー、期限カウントダウン、
日次ヒートマップ、当番表。

## 安全性

- カレンダーには個人名や私的な予定が含まれやすい。実データは Git 管理外の `out/` に置き、
  作例には架空の役割名を使う。
- 計画を約束として見せない。`source` の行に、いつ時点の予定かを書く。
