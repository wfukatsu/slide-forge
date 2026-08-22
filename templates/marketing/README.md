# `templates/marketing/` — 事例・コンテンツ・イベントの企画様式

**スライドテンプレートではない。** ここにあるのは、資料を作る**前**に決めることを
書き留める Markdown の記入様式である。スライドの型は
[`slide-templates/`](../../slide-templates/) にある。

| ファイル | 用途 |
|---|---|
| `case-study.ja.md` | 事例。**公開許諾・数値の出典・鮮度**を管理する。提案とナーチャリングの両方で使う |
| `content-brief.ja.md` | コンテンツ企画。誰に・どの段で・何を持ち帰ってもらうかを決める |
| `event-plan.ja.md` | イベント / 登壇。当てる段と、**回収する情報**を先に決める |

## `templates/nurture/` との違い

| | `templates/marketing/` | `templates/nurture/` |
|---|---|---|
| 対象 | 1 つの成果物（事例・コンテンツ・イベント） | セグメントとトラックの設計 |
| 問い | これをどう作るか | 誰に、どの順で当てるか |
| 例 | 「常石造船の事例をどう書くか」 | 「AWS #001 の 5 段をどう設計するか」 |

トラック（`templates/nurture/nurture-track.ja.md` §10）が「必要なコンテンツ」を
挙げ、その 1 件ずつをここで企画し、完成したら
`templates/nurture/content-inventory.ja.md` の台帳に登録する、という順になる。

## 対応するスライドテンプレート

| 様式 | スライド |
|---|---|
| `case-study.ja.md` | `case-study-card` / `case-study-detail` / `case-fit`（`case-studies` パック） |
| `content-brief.ja.md` | `value-message` / `use-case-one-pager` / `whitepaper-abstract`（`marketing` パック） |
| `event-plan.ja.md` | `event-announce` / `session-agenda` / `speaker-intro`（`marketing` パック）＋ 回収は `hearing-slides` |

## 置き場と扱い

```
accounts/_marketing/
  cases/<事例 ID>.md
  briefs/<Contents ID>.md
  events/<イベント ID>.md
```

`accounts/` は `.gitignore` 済み。**記入済みのファイルをコミットしない。**

- 事例は**公開許諾が取れるまで顧客提示物に載せない**（`case-study.ja.md` §1）
- 参加者名簿・個人に紐づく回答をここに書かない。**件数と型に集約する**
- 事例・価格・性能値は 3 ヶ月ルールの対象

日本語のみで用意している（`work/CLAUDE.md` の「ユーザー向け成果物は日本語」に従う）。
