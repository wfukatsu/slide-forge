#!/usr/bin/env python3
"""レイアウトパターンのギャラリー。slide-forge が持つ図のパターンを一覧する。

    ../../.venv/bin/python ../../scripts/validate_layout.py deck.py
    ../../.venv/bin/python ../../scripts/render_deck.py deck.py

各パターンは戻り値として描画領域の下端 y を返す。次のブロックはその値を起点に
置くこと。この規約を守ればブロック同士が重ならない。
"""
from __future__ import annotations

import json
import os
import sys

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(_ROOT, "scripts"))

from deckkit import *  # noqa: E402,F403

TITLE = "slide-forge レイアウトパターン集"

TEMPLATE = json.load(open(
    os.environ.get("SLIDE_FORGE_TEMPLATE",
                   os.path.join(_ROOT, "templates", "blank-16x9.json")),
    encoding="utf-8"))


plain(layout="COVER",
      title="slide-forge レイアウトパターン集",
      subtitle="デッキで生成できるすべてのパターン・部品・図形と、コネクタの引き方",
      notes="各パターンの呼び出し例はスピーカーノートと references/diagram-cookbook.md にあります。")


# =====================================================================
plain(layout="SECTION", title="1. 構成・流れ",
      body="対比、レーン、時系列、工程")


@slide("対比パネル：現状と解決後を同じ構造で並べる",
       note="compare_panels(d, x, y, w, h, left, right)。左右で同じ位置に同じ種類の要素を置くと差分だけが目に入ります。")
def s_compare(d):
    b = compare_panels(d, X0, DY0, W, 2.90,
                       {"title": "現状：個別に実装", "tone": "bad",
                        "head": "アプリが各 DB を直接叩く",
                        "items": ["整合性を自作する", "分析は ETL 経由で鮮度が落ちる",
                                  "DB 変更＝アプリ改修"],
                        "note": "作り込みが増え続ける"},
                       {"title": "導入後：横断で1回", "tone": "good",
                        "head": "ミドルウェアが間に入る",
                        "items": ["横断 ACID を後付けする", "現行データを直接分析",
                                  "アプリ非改修で差し替え"],
                        "note": "既存資産を置き換えない"})
    banner(d, b + 0.14, "compare_panels(d, x, y, w, h, left, right) — dict で見出し・強調行・項目・注記を渡す",
           tone="info", size=8.5)
    foot(d, ["・Before / After、A / B、推奨と非推奨。対比は最も伝わる図"])


@slide("スイムレーン：レーンをまたぐ矢印を実座標で結ぶ",
       note="swimlane(d, x, y, w, lanes, steps)。レーンをまたぐ矢印を水平に引くと経路が嘘になるため、始点と終点をそのまま繋いでいます。")
def s_swimlane(d):
    b = swimlane(d, X0, DY0, W,
                 [("レコード\n（各 DB）", lighten(d.P.primary, 0.50)),
                  ("台帳\n（Coordinator）", d.P.primary)],
                 [("1. 準備", "PREPARED で書き込み", 0, "info"),
                  ("2. 検証", "競合を検出", 0, "warn"),
                  ("3. 確定", "COMMITTED を書く", 1, "good"),
                  ("4. 反映", "後処理（非同期可）", 0, "info")])
    banner(d, b + 0.16, "swimlane(d, x, y, w, lanes, steps) — steps の第3要素がレーン index",
           tone="info", size=8.5)
    foot(d, ["・誰が何をするかを示す図。手で座標を組むと矢印の経路を間違えやすい"])


@slide("タイムライン：期間の帯と復旧ポイントを1本の軸に",
       note="timeline(d, x, y, w, marks, bands=...)。補足はマーカーのラベルに持たせます。別ラベル＋縦矢印にすると他の説明文と重なります。")
def s_timeline(d):
    b = timeline(d, X0, DY0 + 0.10, W,
                 [(0.06, "通常運転", "muted"),
                  (0.28, "停止開始\nドレイン", "warn"),
                  (0.53, "★ 復旧ポイント\n期間の中間時刻", "bad"),
                  (0.80, "再開\n通常運転へ", "primary")],
                 bands=[(0.28, 0.80, "この期間に取得", "good")],
                 h=1.70)
    b = legend(d, X0, b + 0.20, W,
               [("muted", "通常"), ("warn", "遷移"), ("bad", "重要点"), ("good", "作業可能期間")])
    banner(d, b + 0.20, "timeline(d, x, y, w, marks, bands=…) ＋ legend(d, x, y, w, items)",
           tone="info", size=8.5)
    foot(d, ["・位置は 0.0〜1.0 の比率で指定する。実時間の縮尺を持たせたい場合は呼び出し側で換算する"])


@slide("パイプライン：全体の流れのうち担当範囲だけを強調",
       note="pipeline(d, x, y, w, steps, highlight=(開始, 終了), highlight_note=…)。自社が担う範囲を示すのに使います。")
def s_pipeline(d):
    b = pipeline(d, X0, DY0 + 0.20, W,
                 ["社内文書", "ベクトル化", "ストアに保存", "類似検索", "LLM が回答"],
                 highlight=(1, 3), highlight_note="この範囲を担う", h=0.90)
    b = stats(d, X0, b + 0.40, W,
              [("5", "工程数", "muted"), ("3", "担当範囲", "primary"),
               ("2", "接続先の選択肢", "info")], h=0.90)
    banner(d, b + 0.20, "pipeline(…, highlight=(1, 3)) ／ stats(d, x, y, w, items)",
           tone="info", size=8.5)
    foot(d, ["・stats は出典のある数値にだけ使う。推測値を大きく見せてはいけない"])


# =====================================================================
plain(layout="SECTION", title="2. 分析・位置づけ",
      body="優先度、競合比較、計画")


@slide("2×2 マトリクス：優先度や打ち手を4象限に分ける",
       note="quadrant(d, x, y, w, h, quads, x_label=…, y_label=…)。quads は左上・右上・左下・右下の順です。")
def s_quadrant(d):
    b = quadrant(d, X0, DY0, 5.40, 2.90,
             [("すぐ着手", ["横断トランザクション", "認証・認可"], "good"),
              ("計画して着手", ["分析基盤の統合"], "info"),
              ("様子見", ["ベクトル検索"], "muted"),
              ("見送り", ["未 GA 機能への依存"], "bad")],
             x_label="実装コスト", y_label="効果",
             x_axis=("小", "大"))
    zone(d, X0 + 5.70, DY0, W - 5.70, 2.90, "使いどころ")
    d.label(X0 + 5.86, DY0 + 0.40, W - 6.02, 2.34,
            "・機能の優先度づけ\n・投資判断の整理\n・「やらないこと」を明示する\n\n"
            "軸のラベルは必ず入れる。\n軸が無い 2×2 は\n読み手が解釈できない。",
            size=9, align="START", valign="TOP", color=d.P.text, line_spacing=140)
    banner(d, b + 0.16, "quadrant(d, x, y, w, h, quads, x_label=…, y_label=…)",
           tone="info", size=8.5)
    foot(d, ["・象限ごとに tone を変えると、どこが推奨かが一目で分かる"])


@slide("ポジショニングマップ：2軸上に項目を配置する",
       note="matrix_map(d, x, y, w, h, items)。items は (名前, x0〜1, y0〜1, tone)。y は上が 1.0 です。")
def s_matrix_map(d):
    b = matrix_map(d, X0, DY0, 5.60, 2.90,
               [("自社製品", 0.78, 0.82, "primary"),
                ("競合 A", 0.30, 0.66, "muted"),
                ("競合 B", 0.62, 0.35, "muted"),
                ("自作", 0.16, 0.22, "bad")],
               x_label="機能の広さ", y_label="運用の容易さ")
    zone(d, X0 + 5.90, DY0, W - 5.90, 2.90, "注意")
    d.label(X0 + 6.06, DY0 + 0.40, W - 6.22, 2.34,
            "位置は主観になりやすい。\n\n"
            "・軸の定義を明記する\n・評価根拠を注記に残す\n"
            "・出典があるなら示す\n\n"
            "根拠を示せないなら\nこの図は使わない。",
            size=9, align="START", valign="TOP", color=d.P.text, line_spacing=140)
    banner(d, b + 0.16, "matrix_map(d, x, y, w, h, items, x_label=…, y_label=…)",
           tone="warn", size=8.5)
    foot(d, ["・散布の位置は主張そのもの。裏付けのない配置は避ける"])


@slide("ロードマップ：フェーズ × レーンで計画を示す",
       note="roadmap(d, x, y, w, phases, lanes)。lanes の各バーは (開始列index, 列数, ラベル, tone) です。")
def s_roadmap(d):
    b = roadmap(d, X0, DY0, W,
                ["Q1", "Q2", "Q3", "Q4"],
                [("基盤", [(0, 2, "PoC・性能検証", "info"),
                          (2, 2, "本番構築", "primary")]),
                 ("アプリ", [(1, 2, "データモデル設計", "info"),
                            (3, 1, "移行", "good")]),
                 ("運用", [(2, 2, "監視・バックアップ整備", "muted")]),
                 ("セキュリティ", [(1, 1, "方式決定", "warn"),
                                (2, 2, "認証認可の実装", "info")])])
    b = legend(d, X0, b + 0.18, W,
               [("info", "設計・検証"), ("primary", "構築"), ("good", "移行"),
                ("warn", "意思決定"), ("muted", "整備")])
    banner(d, b + 0.16, "roadmap(d, x, y, w, phases, lanes)",
           tone="info", size=8.5)
    foot(d, ["・列は等幅。実際の期間が不均等なら、列見出しに期間を書いて補う"])


# =====================================================================
plain(layout="SECTION", title="3. 階層・循環",
      body="ツリー、ピラミッド、ファネル、サイクル")


@slide("階層ツリー：親子関係をかぎ線で示す",
       note="tree(d, x, y, w, nodes)。nodes は (深さ, 名前, 説明)。深さは 0 始まりです。")
def s_tree(d):
    b = tree(d, X0, DY0, 5.60,
             [(0, "カタログ", "全データソースを束ねる最上位"),
              (1, "データソース", "個々の DB。接続情報を持つ"),
              (2, "名前空間", "schema / keyspace に対応"),
              (3, "テーブル", "カラム定義と型情報"),
              (1, "データソース", "複数登録できる"),
              (2, "名前空間", "")],
             row_h=0.42, gap=0.08)
    zone(d, X0 + 5.90, DY0, W - 5.90, 2.62, "使いどころ")
    d.label(X0 + 6.06, DY0 + 0.40, W - 6.22, 2.06,
            "・データモデルの階層\n・組織・権限の構造\n・設定ファイルの構造\n\n"
            "深さは 4 段まで。\nそれ以上は別スライドに分ける。",
            size=9, align="START", valign="TOP", color=d.P.text, line_spacing=140)
    banner(d, max(b, DY0 + 2.62) + 0.16, "tree(d, x, y, w, nodes) — nodes は (深さ, 名前, 説明)",
           tone="info", size=8.5)
    foot(d, ["・かぎ線は「1つ浅い直近のノード」から引かれる。兄弟が増えても正しく繋がる"])


@slide("ピラミッドとファネル：積み上げと絞り込み",
       note="pyramid は上ほど狭い（土台→応用）、funnel は上ほど広い（母数→成約）。方向が逆なので使い分けます。")
def s_pyramid_funnel(d):
    d.label(X0, DY0, 4.20, 0.24, "pyramid：土台から応用へ（成熟度）", size=9,
            bold=True, align="START", valign="TOP", color=d.P.primaryDark)
    pyramid(d, X0, DY0 + 0.30, 4.20, 2.50,
            [("最適化", "自動化と改善が回る", "primary"),
             ("標準化", "手順が定義されている", "accent"),
             ("可視化", "現状が計測できる", "info"),
             ("基盤", "動く環境がある", "muted")])
    d.label(X0 + 4.80, DY0, 4.20, 0.24, "funnel：母数から結果へ（絞り込み）", size=9,
            bold=True, align="START", valign="TOP", color=d.P.primaryDark)
    funnel(d, X0 + 4.80, DY0 + 0.30, 4.20, 2.50,
           [("候補", "全対象", "info"),
            ("評価", "条件で絞る", "accent"),
            ("検証", "PoC を実施", "primary"),
            ("採用", "本番導入", "good")])
    banner(d, DY0 + 2.96, "pyramid(d, x, y, w, h, levels) ／ funnel(d, x, y, w, h, stages)",
           tone="info", size=8.5)
    foot(d, ["・どちらも段は 5 つまで。説明は横に余白があれば横に、無ければ段の中に入る"])


@slide("サイクル：循環するプロセスを閉じた輪で示す",
       note="cycle(d, x, y, w, h, steps)。半径は箱が矩形からはみ出さないよう自動で決まります。矢印はステップ間の中間角に接線方向で置かれます。")
def s_cycle(d):
    b = cycle(d, X0, DY0, 5.20, 2.80,
              ["① 構成を決める", "② 設定を変える", "③ 測定する", "④ 比較して判断"])
    zone(d, X0 + 5.50, DY0, W - 5.50, 2.80, "使いどころ")
    d.label(X0 + 5.66, DY0 + 0.40, W - 5.82, 2.30,
            "・PDCA、改善ループ\n・繰り返す検証手順\n・運用サイクル\n\n"
            "ステップは 4〜6 個。\n少なすぎると輪に見えず、\n多すぎると文字が入らない。",
            size=9, align="START", valign="TOP", color=d.P.text, line_spacing=130)
    banner(d, max(b, DY0 + 2.80) + 0.16, "cycle(d, x, y, w, h, steps) — 矩形に内接させる（半径は自動）",
           tone="info", size=8.5)
    foot(d, ["・直線的な工程は pipeline / steps_v、閉じた繰り返しは cycle と使い分ける"])


# =====================================================================
plain(layout="SECTION", title="4. 説明・状態",
      body="分岐、注釈、状態リスト")


@slide("条件分岐：判定と帰結を扇状に広げる",
       note="decision(d, x, y, w, question, branches)。菱形の文字は図形に直接入れず別ラベルを重ねています（端が切れるため）。")
def s_decision(d):
    b = decision(d, X0, DY0 + 0.10, W,
                 "整合性は複数レコードに\nまたがるか？",
                 [("いいえ", "単一レコードの参照が主体\n→ 軽い分離レベルで足りる", "good"),
                  ("条件つき", "一部の処理だけ強い保証が必要\n→ 処理ごとに分ける", "warn"),
                  ("はい", "不変条件が複数にまたがる\n→ 最も強い分離レベル", "bad")])
    banner(d, b + 0.24, "decision(d, x, y, w, question, branches) — 分岐は 2〜3 個",
           tone="info", size=8.5)
    foot(d, ["・分岐ラベル（はい / いいえ）は矢印の経路を避けて箱の上に置かれる"])


@slide("注釈つき図：中央の対象に番号つきで説明を付ける",
       note="callouts(d, x, y, w, h, center, notes)。notes は (テキスト, 'left'|'right') で、付けた順に番号が振られます。")
def s_callouts(d):
    b = callouts(d, X0, DY0, W, 2.90,
                 ("ScalarDB Cluster", "各ノードが全機能を持ち、\n担当ノードへ転送する"),
                 [("クライアントはどのノードに\n接続してもよい", "left"),
                  ("コンシステントハッシングで\n担当を決める", "left"),
                  ("メンバー情報は\nKubernetes API から取得", "right"),
                  ("セッションアフィニティの\n作り込みが不要", "right")])
    banner(d, b + 0.20, "callouts(d, x, y, w, h, center, notes) — 左右に振り分けて番号を自動採番",
           tone="info", size=8.5)
    foot(d, ["・注釈は片側 3 個まで。増やすと 1 件あたりの高さが縮んで読めなくなる"])


@slide("チェックリストと凡例：状態を色と記号で示す",
       note="checklist(d, x, y, w, items) の state は done / todo / warn。legend(d, x, y, w, items) は色の意味を明示します。")
def s_checklist(d):
    d.label(X0, DY0, 4.30, 0.24, "checklist：導入前の確認項目", size=9, bold=True,
            align="START", valign="TOP", color=d.P.primaryDark)
    b1 = checklist(d, X0, DY0 + 0.32, 4.30,
                   [("対象 DB のアダプタを確認した", "done"),
                    ("分離レベルを決めた", "done"),
                    ("ベンチマークで設定差を測った", "warn"),
                    ("バックアップ運用を設計した", "todo"),
                    ("チェックリストでレビューした", "todo")])
    zone(d, X0 + 4.70, DY0, W - 4.70, b1 - DY0, "状態の使い分け")
    d.label(X0 + 4.86, DY0 + 0.40, W - 5.02, b1 - DY0 - 0.55,
            "done … 完了。緑の ✓\n"
            "warn … 着手済みだが未完了。\n　　　注意が必要な項目\n"
            "todo … 未着手。白い □\n\n"
            "状態を色だけで区別せず、\n記号も併用している。",
            size=9, align="START", valign="TOP", color=d.P.text, line_spacing=135)
    b2 = legend(d, X0, b1 + 0.24, W,
                [("good", "完了"), ("warn", "要注意"), ("muted", "未着手")])
    banner(d, b2 + 0.20, "checklist(d, x, y, w, items) ／ legend(d, x, y, w, items)",
           tone="info", size=8.5)
    foot(d, ["・色だけに意味を持たせない。記号を併用するとモノクロ印刷でも読める"])


# =====================================================================
plain(layout="SECTION", title="5. 表・列挙",
      body="対応表、チップ、層、番号つき手順")


@slide("表とチップ：可否の色分けと、順序のない列挙",
       note="grid は cell_colors でセルごとに配色できます。pills は順序が重要でない列挙に使います。")
def s_grid_pills(d):
    def cc(i, j, cell):
        if j == 0:
            return None
        if cell == "●":
            return (lighten(d.P.success, 0.80), darken(d.P.success, 0.45))
        if cell == "○":
            return (lighten(d.P.warning, 0.70), darken(d.P.warning, 0.55))
        return (None, lighten(d.P.muted, 0.45))

    b = grid(d, X0, DY0, W, ["機能", "無償版", "標準版", "上位版", "提供状況"],
             [["横断トランザクション", "●", "●", "●", "GA"],
              ["クラスタリング", "−", "●", "●", "GA"],
              ["SQL インターフェース", "−", "−", "●", "GA"],
              ["レコード単位の認可", "−", "−", "○", "Preview"]],
             col_w=[3.20, 1.30, 1.40, 1.35, 1.75], row_h=0.30, cell_colors=cc)
    b = legend(d, X0, b + 0.12, W,
               [("good", "提供"), ("warn", "プレビュー"), ("muted", "非提供")])
    d.label(X0, b + 0.24, W, 0.24, "pills：順序が重要でない列挙", size=9, bold=True,
            align="START", valign="TOP", color=d.P.primaryDark)
    b = pills(d, X0, b + 0.52, W,
              ["MySQL", "PostgreSQL", "Oracle", "SQL Server", "Db2",
               "Cassandra", "DynamoDB", "Cosmos DB", "S3", "GCS"],
              per_row=5, h=0.26, gap=0.10)
    foot(d, ["・grid の cell_colors(i, j, cell) は (塗り, 文字色) を返す。可否の一覧に効く"])


@slide("レイヤーと手順：責務の分担と、番号つきの流れ",
       note="layers は上から下へ「利用する側 → される側」。steps_v は番号つきの縦フローです。")
def s_layers_steps(d):
    d.label(X0, DY0, 4.30, 0.24, "layers：責務の階層", size=9, bold=True,
            align="START", valign="TOP", color=d.P.primaryDark)
    b1 = layers(d, X0, DY0 + 0.32, 4.30,
                [("アプリ", "業務アプリケーション", lighten(d.P.primary, 0.30)),
                 ("サーバ", "API・認証認可・暗号化", d.P.primary),
                 ("基盤", "トランザクション管理", d.P.primaryDark)],
                row_h=0.50, gap=0.08, label_w=1.10)
    d.label(X0 + 4.70, DY0, W - 4.70, 0.24, "steps_v：番号つきの手順", size=9,
            bold=True, align="START", valign="TOP", color=d.P.primaryDark)
    b2 = steps_v(d, X0 + 4.70, DY0 + 0.32, W - 4.70,
                 [("動かす", "まず最小構成で実行する"),
                  ("設計する", "アクセスパターンから決める"),
                  ("測る", "設定差を自環境で比較する")],
                 row_h=0.46, gap=0.10)
    b = max(b1, b2)
    d.label(X0, b + 0.20, W, 0.24, "kv_rows：項目と補足の 2 列", size=9, bold=True,
            align="START", valign="TOP", color=d.P.primaryDark)
    b = kv_rows(d, X0, b + 0.48, W, row_h=0.28, gap=0.05, items=
                [("分離レベル", "強さと速さのバランスで選ぶ"),
                 ("最適化", "有効 / 無効で性能が大きく変わる"),
                 ("配置", "管理テーブルをどの DB に置くか")])
    foot(d, ["・表にするほどでもない対応関係は kv_rows が軽い"])


# =====================================================================
plain(layout="SECTION", title="6. 基本部品とプリミティブ",
      body="カード、工程、数値、箱、記号、配色、図形")


@slide("カードと工程：Canvas が持つ並列説明と横フロー",
       note="cards は 3〜4 項目の並列説明。flow は 4 段以内の横フロー。どちらも Canvas のメソッドです。")
def s_cards_flow(d):
    d.label(X0, DY0, W, 0.24, "Canvas.cards：3〜4 項目の並列説明", size=9, bold=True,
            align="START", valign="TOP", color=d.P.primaryDark)
    d.cards(X0, DY0 + 0.30, W, 1.10, [
        ("見出しA", "本文を2行ぶん入れられる。accent で上のバーの色を変える"),
        ("見出しB", "項目数は 3〜4 が適切。5 以上は文字が小さくなる"),
        ("見出しC", "並列で対等な関係を示すのに向く"),
    ], accent=[d.P.primary, d.P.info, d.P.success])

    d.label(X0, DY0 + 1.60, W, 0.24, "Canvas.flow：左→右の工程（4 段以内）", size=9,
            bold=True, align="START", valign="TOP", color=d.P.primaryDark)
    d.flow(X0, DY0 + 1.90, W, 0.76, ["調査", "設計", "実装", "検証"])

    banner(d, DY0 + 2.80, "d.cards(x, y, w, h, items, accent=…) ／ d.flow(x, y, w, h, steps)",
           tone="info", size=8.5)
    foot(d, ["・5 段以上の工程は pipeline（範囲強調つき）か steps_v（縦・説明つき）に切り替える"])


@slide("数値の見せ方：横棒と大きな数字",
       note="hbars と metric は出典のある数値にだけ使います。ここでの値はパターンを示すためのサンプルです。")
def s_numbers(d):
    d.label(X0, DY0, 5.40, 0.24, "Canvas.hbars：横棒で量を比べる", size=9, bold=True,
            align="START", valign="TOP", color=d.P.primaryDark)
    hb = d.hbars(X0, DY0 + 0.32, 5.40, [
        ("項目 A", 1220, "1,220"),
        ("項目 B", 460, "460"),
        ("項目 C", 56, "56"),
    ], row_h=0.42, gap=0.16, label_w=1.5, value_w=1.0)

    d.label(X0 + 5.80, DY0, W - 5.80, 0.24, "Canvas.metric：単独の数値", size=9,
            bold=True, align="START", valign="TOP", color=d.P.primaryDark)
    mt = d.metric(X0 + 5.80, DY0 + 0.32, 1.50, 1.05, "22x", "削減率", color=d.P.success)
    d.metric(X0 + 7.50, DY0 + 0.32, 1.50, 1.05, "3", "対応 DB 種別", color=d.P.primary)

    # 戻り値で積む。手で y を書くと内容が増えたときに重なる（実際に重なった）
    b = stats(d, X0, max(hb, mt) + 0.18, W,
              [("55", "総ページ数", "muted"),
               ("46", "図解ページ", "primary"),
               ("32", "レイアウトパターン", "info")], h=0.74)
    banner(d, b + 0.20,
           "⚠ 上の値はパターンを示すためのサンプル。実データでも出典でもない",
           tone="warn", size=9)
    foot(d, ["・数値の図は主張そのもの。出典を示せない値をグラフや大きな数字にしない"])


@slide("箱と帯：見出し・面・注釈の作り分け",
       note="box は淡い面＋枠、solid は塗りつぶし、band は背景の帯、grouphead は帯状の見出し、caption は小さな説明です。")
def s_boxes(d):
    row = [("d.box()", "角丸・淡い面・枠あり。既定の箱"),
           ("d.solid()", "塗りつぶし・太字。見出し用"),
           ("d.band()", "背景の帯。グループ化に使う"),
           ("grouphead()", "帯状の小見出し")]
    cw = (W - 0.30 * 3) / 4
    for i, (nm, desc) in enumerate(row):
        cx = X0 + i * (cw + 0.30)
        if i == 0:
            d.box(cx, DY0 + 0.30, cw, 0.52, "box")
        elif i == 1:
            d.solid(cx, DY0 + 0.30, cw, 0.52, "solid")
        elif i == 2:
            d.band(cx, DY0 + 0.30, cw, 0.52)
            d.label(cx, DY0 + 0.30, cw, 0.52, "band", size=9, align="CENTER",
                    valign="MIDDLE", color=d.P.text)
        else:
            grouphead(d, cx, DY0 + 0.42, cw, "grouphead")
        d.label(cx, DY0 + 0.92, cw, 0.20, nm, size=8.5, bold=True, align="CENTER",
                valign="TOP", color=d.P.primaryDark)
        d.label(cx, DY0 + 1.14, cw, 0.40, desc, size=7.5, align="CENTER",
                valign="TOP", color=d.P.text, line_spacing=115)

    b = DY0 + 1.64
    zone(d, X0, b, W, 1.24, "zone：要素をまとめる領域（中身は y + 0.34 以降）")
    pill(d, X0 + 0.20, b + 0.44, 1.50, 0.28, "pill")
    d.label(X0 + 1.90, b + 0.44, 3.20, 0.28, "pill()：単独のチップ", size=8.5,
            align="START", valign="MIDDLE", color=d.P.text)
    caption(d, X0 + 0.20, b + 0.84, 5.00, "caption()：図に添える小さな説明。既定は中央寄せ",
            align="START")

    banner(d, b + 1.36, "d.box / d.solid / d.band ／ grouphead / zone / pill / caption",
           tone="info", size=8.5)
    foot(d, ["・面の濃さで階層を作る。淡い面＝説明、塗りつぶし＝見出しや強調"])


@slide("記号とアイコン：可否・データ・太い矢印",
       note="db は円柱アイコンで、ラベルが図形の外に出るぶん下端の計算に含めます。xmark / checkmark は中心座標で置きます。")
def s_marks(d):
    zone(d, X0, DY0, 4.30, 2.30, "db()：データの所在")
    db(d, X0 + 0.40, DY0 + 0.50, 1.30, 0.52, "MySQL", sub="orders")
    db(d, X0 + 2.30, DY0 + 0.50, 1.30, 0.52, "Cassandra")
    caption(d, X0 + 0.20, DY0 + 1.50, 3.90,
            "ラベルは図形の外に出る。\nsub 付きなら下に 0.42in はみ出す", align="START", h=0.50)

    rx = X0 + 4.60
    zone(d, rx, DY0, W - 4.60, 2.30, "記号と太い矢印")
    checkmark(d, rx + 0.55, DY0 + 0.62)
    d.label(rx + 0.90, DY0 + 0.50, 1.60, 0.24, "checkmark()", size=8.5,
            align="START", valign="MIDDLE", color=darken(d.P.success, 0.4))
    xmark(d, rx + 2.70, DY0 + 0.62)
    d.label(rx + 3.05, DY0 + 0.50, 1.30, 0.24, "xmark()", size=8.5,
            align="START", valign="MIDDLE", color=darken(d.P.danger, 0.25))
    d.arrow_shape(rx + 0.40, DY0 + 1.10, 1.60, 0.46, text="工程", size=8.5)
    d.label(rx + 2.20, DY0 + 1.10, 2.00, 0.46, "arrow_shape()：\n太い矢印図形", size=8,
            align="START", valign="MIDDLE", color=d.P.text, line_spacing=110)
    caption(d, rx + 0.20, DY0 + 1.76, W - 5.00,
            "記号は中心座標で置く（cx, cy）", align="START")

    banner(d, DY0 + 2.46, "db(d, x, y, w, h, name, sub=…) ／ checkmark / xmark / d.arrow_shape",
           tone="info", size=8.5)
    foot(d, ["・可否は色だけでなく記号でも示す。モノクロ印刷や色覚特性に依存しない"])


@slide("配色：7 つの tone とパレット",
       note="tone_colors は (塗り, 枠, 文字色) を、tone_solid は濃い単色を返します。テンプレートの colors から組み立てるためテーマから外れません。")
def s_tones(d):
    tones = [("primary", "自社製品・主要コンポーネント"),
             ("accent", "副系統・別カテゴリ"),
             ("info", "説明・中立"),
             ("good", "良い状態・After・可"),
             ("warn", "注意・条件つき"),
             ("bad", "問題・Before・不可"),
             ("muted", "補足・対象外")]
    rh = 0.32
    for i, (t, use) in enumerate(tones):
        ry = DY0 + 0.06 + i * (rh + 0.05)
        fill, stroke, col = tone_colors(d, t)
        d.label(X0, ry, 1.00, rh, t, size=9, bold=True, align="START",
                valign="MIDDLE", color=d.P.text)
        d.shape(X0 + 1.05, ry, 1.70, rh, kind="ROUND_RECTANGLE", fill=fill,
                stroke=stroke, text="tone_colors", size=8, color=col)
        d.shape(X0 + 2.85, ry, 1.30, rh, kind="ROUND_RECTANGLE",
                fill=tone_solid(d, t), stroke=None, text="tone_solid", size=8,
                color=readable_on(tone_solid(d, t)))
        d.label(X0 + 4.30, ry, W - 4.30, rh, use, size=8.5, align="START",
                valign="MIDDLE", color=d.P.muted)

    b = DY0 + 0.06 + 7 * (rh + 0.05)
    d.shape(X0, b + 0.08, W, 0.44, kind="ROUND_RECTANGLE", fill="#F4F6F9",
            stroke=lighten(d.P.muted, 0.6))
    d.label(X0 + 0.14, b + 0.14, W - 0.28, 0.36,
            "lighten(色, 0〜1) / darken(色, 0〜1) で明度調整。"
            "readable_on(背景色) が背景に応じた文字色を返す。"
            "1 スライド最大 3 色に抑える。",
            size=8.5, align="START", valign="TOP", color=d.P.text)
    foot(d, ["・色はテンプレートの colors から組み立てられる。テーマを変えても図が破綻しない"])


@slide("図形カタログ：使えるシェイプ 26 種",
       note="Canvas.shape(kind=...) に渡せる主な図形です。TEXT_BOX は枠も塗りも無いテキスト専用なので除いています。")
def s_shapes(d):
    kinds = ["RECTANGLE", "ROUND_RECTANGLE", "ELLIPSE", "DIAMOND", "CAN", "CLOUD",
             "HEXAGON", "PENTAGON", "CHEVRON", "HOME_PLATE", "PARALLELOGRAM",
             "TRAPEZOID", "PLAQUE", "FOLDED_CORNER", "DONUT", "STAR_5", "ARC",
             "RIGHT_ARROW", "LEFT_RIGHT_ARROW", "UP_ARROW", "DOWN_ARROW",
             "BENT_ARROW", "CURVED_RIGHT_ARROW", "NOTCHED_RIGHT_ARROW",
             "FLOW_CHART_MAGNETIC_DISK", "WEDGE_ROUND_RECTANGLE_CALLOUT"]
    def wrap_kind(k, width=15):
        """図形名を読める位置で折り返す。先頭の _ だけで割ると意味が壊れる。"""
        lines, cur = [], ""
        for part in k.split("_"):
            cand = f"{cur}_{part}" if cur else part
            if len(cand) > width and cur:
                lines.append(cur)
                cur = part
            else:
                cur = cand
        lines.append(cur)
        return "\n".join(lines)

    per, sw, sh = 7, 1.18, 0.34
    gap = (W - per * sw) / (per - 1)
    for i, k in enumerate(kinds):
        r, c = divmod(i, per)
        sx = X0 + c * (sw + gap)
        sy = DY0 + 0.02 + r * 0.74
        d.shape(sx, sy, sw, sh, kind=k, fill=lighten(d.P.primary, 0.86),
                stroke=lighten(d.P.primary, 0.55))
        d.label(sx - 0.14, sy + sh + 0.02, sw + 0.28, 0.38, wrap_kind(k),
                size=6, align="CENTER", valign="TOP", color=d.P.muted, line_spacing=100)
    banner(d, DY0 + 3.08, "d.shape(x, y, w, h, kind=\"HEXAGON\", …) — TEXT_BOX は枠も塗りも無い",
           tone="info", size=8.5)
    foot(d, ["・ARC と CURVED_RIGHT_ARROW は塗りが意図どおりに乗らない。"
             "凝った図形ほど中の文字も切れやすいので、文字は別ラベルで重ねる"])


@slide("コネクタは図形どうしを結ぶ。座標で書かない",
       note="connect() は API のコネクタとして図形に紐づき、図形を動かすと追従します。link() は辺の交点を計算して線を引きます。座標直指定の line()/arrow() は端点がずれても API は何も言いません。")
def s_connectors(d):
    zone(d, X0, DY0, W, 1.86, "3 通りの引き方")
    bw, bh, gap = 1.05, 0.50, 0.38
    row_y = DY0 + 0.52
    cols = [("connect()", "good"), ("link()", "info"), ("line() / arrow()", "bad")]
    cw = (W - 0.28) / 3
    for i, (nm, tone) in enumerate(cols):
        gx = X0 + 0.14 + i * cw
        fill, stroke, col = tone_colors(d, tone)
        a = d.shape(gx, row_y, bw, bh, kind="ROUND_RECTANGLE", fill=fill,
                    stroke=stroke, text="A", size=10, bold=True, color=col)
        b_ = d.shape(gx + bw + gap, row_y + 0.40, bw, bh, kind="ROUND_RECTANGLE",
                     fill=fill, stroke=stroke, text="B", size=10, bold=True, color=col)
        if i == 0:
            d.connect(a, b_, color=tone_solid(d, tone), weight=1.6)
        elif i == 1:
            d.link(a, b_, color=tone_solid(d, tone), weight=1.6)
        else:
            # わざと端点をずらした例。検査で「接していない」と落ちる書き方
            d.arrow(gx + bw + 0.14, row_y + 0.16, gx + bw + 0.28, row_y + 0.44,
                    color=tone_solid(d, tone), weight=1.6, free=True)
        d.label(gx, row_y + 1.06, cw - 0.20, 0.22, nm, size=9, bold=True,
                align="START", valign="TOP", color=col)

    b = kv_rows(d, X0, DY0 + 2.00, W, [
        ("connect(a, b)", "API のコネクタとして図形に紐づく。図形を動かすと線が追従する"),
        ("link(a, b)", "中心を結ぶ線と辺の交点を端点にする。斜めでもぴたりと触れる"),
        ("free=True", "軸・目盛り・引き出し線など、図形に接しないのが正しい線に付ける"),
    ], row_h=0.28, gap=0.05)
    banner(d, b + 0.14, "検査器がコネクタの端点を調べ、浮いている線・埋まっている線を落とす",
           tone="good", size=9)
    foot(d, ["・図形どうしを結ぶときに座標を手で書かない。ずれても API はエラーにしない"])


@slide("すべてのパターンは下端 y を返す",
       note="この規約により、前のブロックがはみ出して次に重なる事故を防げます。検査器も重なりを拾いますが、検出は最後の砦であって設計ではありません。")
def s_contract(d):
    b = pipeline(d, X0, DY0 + 0.10, W,
                 ["b = layers(...)", "b = grid(..., y=b+0.2)", "b = pills(..., y=b+0.2)",
                  "banner(d, b+0.2, ...)"],
                 h=0.80, gap=0.24, size=8)
    zone(d, X0, b + 0.34, W, 1.34, "なぜ戻り値を決めているか")
    d.label(X0 + 0.16, b + 0.68, W - 0.32, 0.92,
            "各パターンが自分の下端を返し、呼び出し側がそれを起点に積むことで、"
            "重なりを構造的に防いでいる。手で y を計算しないこと。\n"
            "検査器は重なりも文字溢れも拾うが、検出は最後の砦であって設計ではない。",
            size=9, align="START", valign="TOP", color=d.P.text, line_spacing=130)
    banner(d, b + 1.84, "b = pattern(...) → 次は b + 余白 から置く", tone="good", size=9.5)
    foot(d, ["・生成後はサムネイル目視を必ず行う。座標検査だけでは重なりも文字の折返しも分からない"])


plain(layout="CLOSING")
