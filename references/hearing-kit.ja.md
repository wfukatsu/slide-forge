*[English](hearing-kit.md)*

# ヒアリングキット — `hearing-sheet` と `hearing-slides` の共通規約

2 つのスキルが 1 つの記録を共有する。両方が従う規則をここに置く。
**各スキルはここに書いてあることを再定義しない。**

| 観点 | 出典 |
|---|---|
| 正本・3 形式・マージ・顧客配布版のフィルタ | **このドキュメント** |
| そもそも何を聞くか | `templates/sales/hearing-sheet.ja.md`（＋ `templates/sales/products/`） |
| フェーズ・ゲート・BANT の判定基準・資料 5 種 | `references/scalar/sales-playbook.ja.md` |
| 議事録・メールから記録を埋める | `scalar-deal-intake` |
| 製品適合（カテゴリ・提案不可の制約・エディション） | `templates/sales/products/<製品>.ja.md` |

## 1. JSON が正本

置き場は `accounts/<AE 名>/<顧客名>/stages/hearing.json`。
Markdown / Excel / Google Spreadsheet は**そのレンダー**であり、
どれも読み戻せる。設問が安定した ID（`4.2-05`）を持っているからである。

```
templates/sales/hearing-sheet.ja.md ──init──▶ hearing.json ──render──▶ md / xlsx / gsheet
                                                    ▲                        │
                                                    └────────read────────────┘
```

- **ID 列が紐づけそのもの。** 振り直さない、読み戻す形式で手で並べ替えない、
  列を消さない。
- 語彙は既存のまま（`確認済` / `推定` / `未確認`）。台帳の
  `confirmed` / `wip` / `missing` への変換表は `hearing-sheet.ja.md` §14.2。
  **4 つ目の値を作らない。**
- §12（未確認リスト）と §13（顧客に確認を返すこと）は**派生**である。確度から
  自動で決まり、手で同期させない。派生表のフォローアップ欄を編集すると、
  元の設問に書き戻る。

## 2. マージは黙って上書きしない

`read` は取り込む形式と記録を突き合わせ、**同じセルで双方が変わっていたら
競合として報告し、何も書かずに止まる**。

```bash
.venv/bin/python scripts/hearing/hearing_sheet.py read <形式> --into hearing.json \
    --baseline <その形式を書き出したときの JSON>
```

- **baseline を残す。** 無いと、古い形式を取り込んだときに新しい回答が黙って
  戻る。相手の編集とこちらの編集も区別できない。
- 競合の解決は `--take sheet` / `--take json` を明示したときだけ。
- `deal-log.md` §1 の矛盾表と同じ考え方。食い違いは**記録するもの**であって、
  最後に書いた人が勝つものではない。
- **Google Spreadsheet の再レンダーは中身を置き換える。** 相手が記入している
  可能性があるものへ `render` する前に、必ず `read` する。

## 3. 顧客配布版は「フィルタ」であって「レビュー」ではない

`--audience customer` は内部の列（出典・確度）と、見出しが
`customerSafe: false` の節（既定で 関与者と購買プロセス／パートナー／競合／
金額・BANT／対応表）を落とす。

**これは機械的な除去にすぎない。** 渡す前に、プレイブック §3 の検査を目視で行う。

- 個人の影響力・賛否・「未接触」といった判断が入っていないか
- 競合の弱点を名指ししていないか
- 未確認が、確定したことのように書かれていないか
- 出典の無い数値が入っていないか
- 価格・ロードマップが、その相手に開示してよい範囲か

## 4. 回答の置き場

| 何を | どこに |
|---|---|
| 特定の顧客の回答 | `accounts/<AE 名>/<顧客名>/stages/` のみ |
| イベントの回答 | **型と件数に集約してから** `accounts/_nurture/` |
| 同意記録・配信停止記録 | MA / CRM。**このリポジトリに置かない**（`nurture-map.ja.md` §8） |

`accounts/` は `.gitignore` 済み。**記入済みのシートをコミットしない。**
顧客フィルタを通していないものを顧客・パートナーに渡さない。

**個人や企業が特定できるイベント回答は、セグメントではなく商談である。**
`scalar-deal-intake` に回す（`scalar-nurture-intake` §2）。

## 5. コマンド

すべて slide-forge ルートを cwd にして `.venv/bin/python` で実行する。

| やること | コマンド |
|---|---|
| 記録を起こす | `scripts/hearing/hearing_sheet.py init templates/sales/hearing-sheet.ja.md --out <json>` |
| 製品補遺を取り込む | 同じコマンドを `templates/sales/products/scalar.ja.md` に `--section-prefix scalar- --no-derived` で |
| 出力する | `scripts/hearing/hearing_sheet.py render <json> --format md / xlsx / gsheet [--audience customer]` |
| 表計算をオフラインで検証 | 上に `--dry-run`（API を呼ばない） |
| 読み戻す | `scripts/hearing/hearing_sheet.py read <形式> --into <json> --baseline <前回の json>` |
| 何が空いているか | `scripts/hearing/hearing_sheet.py gaps <json> [--section 4]` |
| スライドのデータ | `scripts/hearing/hearing_slots.py <json> <ページ> --out <data.json>` |
| 回答先の QR | `scripts/hearing/qr.py <url> --out out/hearing/qr.png` |

`render --format gsheet` は同じフォルダの同名ファイルを**その場で更新**するので
URL が変わらない。**商談ごとにリンクは 1 本に保つ。**
