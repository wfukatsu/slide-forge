# slide-forge

図解主体の Google Slides デッキを、Python で宣言的に組み立てて生成する Claude Code プラグイン。

箇条書きだけでは伝わらない資料 — 1 機能 1 ページの製品説明、技術解説、アーキテクチャ資料 —
を対象にしている。特徴は **生成前に座標をオフライン検査すること**。図のはみ出し、
文字が図形に隠れる重なり、枠からの文字溢れ、矢印の不接続は、生成してサムネイルを
見るまで気づけないのが普通だが、それを API を呼ぶ前に潰す。

```
調査・構成設計 → デッキモジュールを書く → 座標検査（無料・即時） → 生成 → サムネイル目視
                                              ↑____________修正____________|
```

## インストール

```
/plugin marketplace add <このリポジトリの URL または パス>
/plugin install slide-forge@slide-forge
```

### 前提

1. Python 3.10+

   ```bash
   python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
   ```

2. Google Cloud プロジェクトで **Slides API** と **Drive API** を有効化

3. OAuth 2.0 デスクトップクライアントの `credentials.json` を `~/.config/slide-forge/` に置く
   （初回実行時にブラウザで認証し、`token.json` が自動生成される）

   置き場所は環境変数 `SLIDE_FORGE_CONFIG_DIR` で変更できる。

## スキル

| スキル | 役割 |
|---|---|
| `/slide-forge:build` | デッキの構成設計から生成まで。図の選び方と書き方 |
| `/slide-forge:validate` | 座標のオフライン検査（生成前に必ず通す） |
| `/slide-forge:template` | 自社マスターを解析して `template.json` に登録 |
| `/slide-forge:qa` | サムネイルによる視覚 QA |

## 使い方

デッキは **1 モジュール = 1 デッキ** の Python ファイル。関数がスライド 1 枚に対応する。

```python
import json, os, sys
sys.path.insert(0, "<plugin>/scripts")
from deckkit import *

TITLE = "製品機能解説"
TEMPLATE = json.load(open("<plugin>/templates/blank-16x9.json", encoding="utf-8"))

plain(layout="COVER", title="製品機能解説", subtitle="機能別リファレンス")
plain(layout="SECTION", title="1. 全体像", body="何を解決する製品なのか")

@slide("3 層構成で HTAP を実現する", note="Core は OSS、上位 2 つが商用")
def s_arch(d):
    layers(d, X0, DY0, W, [
        ("アプリ", "業務アプリケーション",   lighten(d.P.primary, 0.3)),
        ("サーバ", "SQL / 認証認可 / 暗号化", d.P.primary),
        ("基盤",   "トランザクション管理",    d.P.primaryDark),
    ])
    banner(d, DY1 - 0.4, "3 者は同じデータモデル上で成立する", tone="good")
    foot(d, ["・持ち帰ってほしい1行"], "提供: Community / Enterprise ｜ 状況: GA")
```

```bash
python <plugin>/scripts/validate_layout.py mydeck.py       # 座標検査（API を呼ばない）
python <plugin>/scripts/render_deck.py     mydeck.py       # 生成
python <plugin>/scripts/fetch_thumbnails.py <URL> --out out/qa --size LARGE
```

`render_deck.py` は生成前に検査を自動実行し、問題があれば生成しない。

## 何を検査するか

| 検査 | 落ちる理由 |
|---|---|
| 図がフッター領域にはみ出す | マスターのロゴ・著作権表示・要点行と重なる |
| 図が左右にはみ出す | スライド外に出て見えなくなる |
| タイトルが 2 行になる | タイトルが図の領域を侵食する |
| 描画で例外 | 座標計算のミス |
| レイアウト / プレースホルダの不整合 | ロール名の誤り、存在しない枠の指定 |
| コネクタが図形に接していない / 埋まっている | 矢印の端点が浮く、枠に食い込む |
| 文字が後から描いた図形に隠れている | バナーやゾーンが直前のブロックに重なる |
| 文字どうしがぶつかっている | ラベルが重なって読めない |
| 枠に対して文字が多すぎる | 枠からはみ出して切れる |

**検査できないこと**（サムネイル目視が必要）: 矢印の向きと経路（他の図形を横切っていないか）、
コントラスト、図が実際に伝えたいことを伝えているか。

## 図のパターン（32 種）

`references/diagram-cookbook.md` の早見表から「何を伝えたいか」で選ぶ。
実際の描画例は `examples/pattern-gallery/` にある。

| 分類 | パターン |
|---|---|
| 構成・流れ | `compare_panels` `swimlane` `timeline` `pipeline` `steps_v` `layers` |
| 分析・位置づけ | `quadrant` `matrix_map` `roadmap` |
| 階層・循環 | `tree` `pyramid` `funnel` `cycle` |
| 説明・状態 | `decision` `callouts` `checklist` `stats` `legend` |
| 基本 | `zone` `banner` `grid` `pills` `kv_rows` `db` `caption` `grouphead` `pill` `xmark` `checkmark` `foot` |
| Canvas | `cards` `flow` `hbars` `metric` |

**すべてのパターンは戻り値に描画領域の下端 y を返す。** 次のブロックはその値を
起点に置く。検査器は重なりも検出するが、検出は最後の砦であって設計ではない。

**図形どうしを結ぶ矢印は座標で書かない。** `d.connect(a, b)` は API のコネクタとして
図形に紐づき（動かすと追従する）、`d.link(a, b)` は辺の交点を端点にする。
軸や引き出し線など接しないのが正しい線は `d.line(..., free=True)` と明示する。

```python
b = layers(d, X0, DY0, W, [...])
b = grid(d, X0, b + 0.24, W, cols, rows)
banner(d, b + 0.20, "まとめ", tone="good")
```

## テンプレート

| 状況 | 使うもの |
|---|---|
| マスターが無い / まず試す | 同梱の `templates/blank-16x9.json`（新規プレゼンを作る） |
| 自社マスターがある | `/slide-forge:template` で解析・登録 |

マスターを複製する場合、装飾・ロゴ・著作権フッターはレイアウトから自動継承される。
自分で描くと二重になる。

同梱テンプレートは Google 既定レイアウトの `BLANK` の上にタイトル等を座標指定で描く。
既定プレースホルダは幅を変更できず折り返してしまうため（Slides API に要素のサイズを
変更するリクエストが無い）、この方式にしている。

## ドキュメント

| ファイル | 内容 |
|---|---|
| `references/layout-contract.md` | 座標系、安全域、実測値、崩しがちなパターン、API の制約 |
| `references/diagram-cookbook.md` | パターン早見表 32 種、積み方の約束、配色、禁止事項 |
| `references/template-schema.md` | `template.json` のスキーマと拡張フィールド |

## 実例

| ディレクトリ | 内容 |
|---|---|
| `examples/pattern-gallery/` | 全パターンのギャラリー（23 枚）。呼び出し方の見本 |
| `examples/scalardb-scalardl/` | 製品機能カタログ（55 枚、うち図解 46 枚）。1 機能 1 ページの構成の見本 |

```bash
cd examples/pattern-gallery
python ../../scripts/validate_layout.py deck.py
python ../../scripts/render_deck.py deck.py
```

## 構成

```
slide-forge/
├── .claude-plugin/marketplace.json
├── skills/{build,validate,template,qa}/SKILL.md
├── scripts/
│   ├── deckkit.py           # スライド登録・レイアウト定数・複合パーツ
│   ├── diagrams.py          # Canvas / Palette / 色ユーティリティ
│   ├── build_deck.py        # TemplateDeck（複製・新規作成・スライド追加）
│   ├── validate_layout.py   # オフライン座標検査
│   ├── render_deck.py       # 生成（検査を自動実行）
│   ├── inspect_template.py  # マスター解析 → template.json
│   ├── fetch_thumbnails.py  # サムネイル取得（視覚 QA）
│   └── _auth.py             # OAuth・単位変換・ID 抽出
├── references/              # レイアウト契約・図のレシピ・スキーマ
├── templates/blank-16x9.json
└── examples/
    ├── pattern-gallery/      # 全パターンのギャラリー
    └── scalardb-scalardl/    # 製品機能カタログ
```

## 由来とライセンス

`_auth.py` / `diagrams.py` / `build_deck.py` / `inspect_template.py` /
`fetch_thumbnails.py` は、作者のローカル `google-slides-template` スキルから取り込み、
プラグインとして自己完結するよう改変したもの（モジュール名をインポート可能な形に変更、
マスター無しでの新規作成と `drawText` / `applyElementGeometry` に対応、
資格情報の探索パスを一般化）。

本パッケージは **MIT License**（`LICENSE` 参照）。取り込み元のスクリプトについても
作者が権利を保持しているものとして MIT で配布している。

`examples/scalardb-scalardl/` の内容は developers.scalar-labs.com の公開ドキュメントに
基づく解説であり、Scalar 社の公式資料ではない。ScalarDB / ScalarDL は Scalar 社の製品。
