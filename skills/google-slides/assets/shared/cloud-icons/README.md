# クラウドアイコン（このディレクトリは空です）

AWS / Google Cloud / Azure の公式アイコンは**各社の資産で、再配布が許されていない**
ため、このリポジトリには含めていません。**利用者が自分の環境に取り込みます。**

## 取り込み

```bash
cd ~/.claude/skills/google-slides
~/.claude/venvs/gslides/bin/python scripts/fetch-cloud-icons.py
```

3 ベンダーの配布ページから最新の ZIP を取得し、SVG を正本としてここへ展開し、
`cloud-icons.json`（名前・別名・カテゴリの索引）を作ります。1〜2 分、約 8.6MB。
`google-slides-template` スキルにも同時に配置されます。

```bash
python scripts/fetch-cloud-icons.py --dry-run   # 取得せず URL の解決だけ試す
python scripts/fetch-cloud-icons.py --vendor azure   # 1 ベンダーだけ更新
python scripts/fetch-cloud-icons.py --verify    # 取り込み済みか・欠けが無いか確認
```

取り込むと、この下は次の形になります。

```
cloud-icons.json          索引（名前・別名・カテゴリ・種別・出典の版）
aws/<category>/<slug>.svg
gcp/<category>/<slug>.svg
azure/<category>/<slug>.svg
```

## 利用条件（取り込む前に）

3 ベンダーとも「**アーキテクチャ図・研修資料・ドキュメントでの利用**」のみを
許諾しています。**色の変更・回転・反転・変形は禁止**で、アイコンの近くに製品名を
置くことが求められます。取り込んだ素材の再配布（このリポジトリへのコミットを含む）は
しないでください。

| ベンダー | 条件 |
|---|---|
| AWS | https://aws.amazon.com/trademark-guidelines/ |
| Microsoft Azure | https://learn.microsoft.com/en-us/azure/architecture/icons/ |
| Google Cloud | https://cloud.google.com/icons |

使い方は `references/cloud-icons.md` を参照してください。
