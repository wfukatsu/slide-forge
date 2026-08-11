# スライドマスター（このディレクトリは空です）

`generationMode: copy` のテンプレート（`scalar-2026`, `scalar-2026-boilerplate`,
`corporate`, `aixdevops`）は、生成時に**実在の Google Slides を複製**します。
`templates/<id>.json` はその `presentationId` を記録しているだけなので、
マスターが自分の Drive に無いとこれらのテンプレートは使えません。

マスターの実体（1 つ 6〜8MB）はリポジトリに含めていません。**利用者が自分の
環境に用意します。** 手順は README の「Setup > 3. Slide masters」を参照。

## 置き場所

`.pptx` を入手したら、テンプレート ID と同じ名前でここに置きます。

```
templates/masters/scalar-2026.pptx
templates/masters/corporate.pptx
```

そのうえで Drive へ取り込み、登録を自分のコピーに向け直します。

```bash
.venv/bin/python scripts/import_template_master.py --all
```

取り込むと Slides がレイアウト・マスター・装飾すべてに新しい object ID を振り
直すため、このスクリプトは `inspect_template.py` を再実行して登録を作り直します。
`--reset-roles` を付けないので、人手で検証したロール割り当てはそのまま残ります。

## 書き出し

マスターに編集権限があるなら、ここへ書き出せます。

```bash
.venv/bin/python scripts/export_template_master.py --all
```

Drive は 10MB を超える Docs エディタ形式ファイルのエクスポートを拒否します
（`exportSizeLimitExceeded`）。超えるマスターは Slides の画面から手動で
ダウンロード（ファイル > ダウンロード > Microsoft PowerPoint）してください。

**容量を下げるためにスライドを削らないこと。** Slides はどのスライドからも
使われていないレイアウトを削除するため、レイアウトが失われます（`aixdevops`
では `WHITE` / `SLIDE_SUB_SECTION` / `CLOSE_PAGE` の 3 つが消えることを確認済み）。
`existingSlideIds` のバンドルスライドもテンプレートの提供物の一部です。

## マスターを持っていない場合

`template-forge` スキル（`scripts/build_template.py`）が、ブランド色・フォント・
ロゴ・フッターの設計指定から**新しいマスターを作成**します。Slides API は
マスターを新規作成できないため、既定マスターを複製してレイアウトを restyle し、
`templates/<id>.json` に登録するところまで行います。

マスターを一切使わないなら `templates/blank-16x9.json`（`generationMode: create`）
を選びます。こちらは Drive 上の実体を必要としません。
