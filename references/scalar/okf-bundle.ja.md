*[English](okf-bundle.md)*

# OKF バンドル — Scalar 製品事実・価格の一次参照先

`OKF-ScalarDB-ScalarDL` は、ScalarDB / ScalarDL の公式ドキュメント
（developers.scalar-labs.com）を製品ごと・バージョンごとに
[OKF v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
バンドルとしてまとめたもの。加えて、上流には存在しない `pricing/`（価格・ライセンス）
セクションを持つ。

**Scalar の提案を作るときは、製品の主張・エディション境界・価格を書く前にこのバンドルを読む。**
推測の代わりであり、バンドルが扱う範囲については Web 調査の代わりでもある。

リポジトリ: <https://github.com/wfukatsu/OKF-ScalarDB-ScalarDL>

## どこにあるか

次の順に解決し、最初に見つかったものを使う。

| # | 場所 | 備考 |
|---|---|---|
| 1 | `/Users/wfukatsu/work/OKF-ScalarDB-ScalarDL/okf/` | ローカルクローン（最速。使う前に `git pull`） |
| 2 | `/Users/wfukatsu/work/nexus-architect/knowledge/okf-scalardb-scalardl/okf/` | nexus-architect が pin している submodule |
| 3 | `https://github.com/wfukatsu/OKF-ScalarDB-ScalarDL` | クローンが無い場合に raw を取得 |

slide-forge はバンドルを同梱していない。3 つとも解決できない場合はその旨を述べ、
`research-2026-08.ja.md` にフォールバックする。事実を捏造しない。

## 収録範囲

| 用途 | ファイル |
|---|---|
| バンドルの読み方（鉄則） | `okf/guides/how-ai-agents-use-this-bundle.md` |
| どの製品・エディション・バージョンを引くか | `okf/guides/product-and-version-selection.md` |
| 特定バージョンの製品事実 | `okf/products/<product>/<version>/index.md` → 配下の概念ページ |
| 課金モデル（3 種）の全体像 | `okf/pricing/index.md` |
| ScalarDB EE Standard / Premium の定価 | `okf/pricing/scalardb-pricing.md` |
| ScalarDL Ledger / Auditor の定価 | `okf/pricing/scalardl-pricing.md` |
| ScalarDB Analytics の SDBU 従量課金 | `okf/pricing/scalardb-analytics-pricing.md` |
| 1 Pod = 2vCPU / 4GB と契約期間ごとの Pod 数の数え方 | `okf/pricing/licensing-units.md` |
| エディションに含まれるもの（機能・提供物マトリクス） | `okf/pricing/edition-feature-matrix.md` |
| サンプル見積 5 パターン＋見積チェックリスト | `okf/pricing/sample-quotations.md` |

収録製品: ScalarDB (3.14〜3.19)、ScalarDL (3.10〜3.14)、ScalarDB Saga (3.19・未 GA)、
ScalarDB Community (3.4〜3.13)。

## 引用時のルール

`okf/guides/how-ai-agents-use-this-bundle.md` の鉄則。緩めずにそのまま適用する。

1. **バージョンを跨いで答えない。** `products/<product>/<version>/` を 1 つ選び、
   その配下だけを根拠にする。設定キー・エラーコード・API シグネチャはマイナー
   バージョン間で変わる。スライドにはバージョンを明記する。
2. **エディションを確認する。** 各概念の frontmatter の `editions` を見る。
   Community 前提の案件に Enterprise 限定機能を提案しない。エディションを示さずに
   機能を書かない。
3. **プレビュー状態を明示する。** `feature_status: [Private Preview | Public Preview]`、
   `status: draft` / `prerelease: true`（現時点では ScalarDB Saga 3.19 =
   `3.19.0-alpha.1`）は、触れるスライドで「未 GA」と明記する。
4. **推測しない。** 根拠が無ければ「ドキュメントに記載が無い」と述べ、`resource` の
   URL を示して確認を促す。これは `research-policy.md` と同じ規律で、機能・価格・
   顧客成果・リリース状況を周辺情報から推定してはならない。
5. **`status: deprecated` の概念は既存システム調査専用。** 提案の設計判断の根拠にしない。

## 価格を引くときのルール

`okf/pricing/` はこのバンドルで唯一、上流を持たないセクション。出典は株式会社 Scalar の
社内価格表（ScalarDB / ScalarDL は 2024-07-01 版、ScalarDB Analytics は 2024-09-10 版）。

- 記載はすべて **定価・税抜・JPY**。**参考見積の材料としてのみ**使い、確定金額・提出可能な
  見積として提示しない。社外に出る見積は必ず営業担当のレビューを通す。
- 収録しているのは 3 つだけ — Analytics の SDBU・時間単価、および Pod サブスクリプション
  4 製品の月額・年額定価。**3年契約の定価、先払いクレジット価格、値引き条件、顧客固有の
  契約条件は「非公開」と明記され、意図的に載っていない。** 提案で必要になったら「非公開」
  である旨を述べて営業担当につなぐ。月額・年額から内挿しない。
- **実際の見積書に載る単価は引き続き見積マスター**
  （`scalar-quotation` → `/Users/wfukatsu/work/price-master/data/scalar-pricing.json`）
  が唯一の正。バンドルはそのマスターの裏取りと、マスターが持たない情報
  — エディションの内容、Pod 数の数え方、見積チェックリスト — の供給に使う。
- `pricing/` の価格表は社内出典。そのまま顧客提示資料に貼らない。顧客ごとに算出した
  金額を見積成果物側に載せる。

## 他の参照先との分担

| 事実 | 出典 |
|---|---|
| 製品機能・エディション・設定・バージョン・リリース状況 | **本バンドル** |
| 定価・課金モデル・Pod 数の数え方・エディション内容 | **本バンドル**（`pricing/`） |
| 見積書に載る単価 | `scalar-quotation` の価格マスター |
| 会社情報・ニュース・公開事例・定量成果 | `research-2026-08.ja.md`（バンドルは持たない） |
| 営業フェーズ・ゲート・資料タイプ | `sales-playbook.ja.md` |
