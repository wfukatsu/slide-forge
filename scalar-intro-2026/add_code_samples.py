#!/usr/bin/env python3
"""「Scalar 製品機能のご紹介」既存デッキにコードサンプルスライドを挿入する。

対象: https://docs.google.com/presentation/d/1NnfZLDVYKFYKNceToJNGSg8Wpnod1Ume7fEgSVJWUKk/
コードが中心の 9 機能（ScalarDB 5 + ScalarDL 4）について、機能スライドの直後に
「コード + 解説 + ポイント」のスライドを差し込む。コードは公式ドキュメント
（2026-08-02 取得）の記載に合わせている。

既存デッキへの挿入なので、新規生成（build_scalar_features.py）と違い
- objectId の衝突を避ける（deck._next_id / Canvas._seq をずらす）
- 挿入位置より後ろの既存ページ番号を振り直す
点に注意。
"""
from __future__ import annotations

import os
import sys
from importlib.machinery import SourceFileLoader

SKILL_DIR = os.path.expanduser("~/.claude/skills/google-slides-template")
sys.path.insert(0, os.path.join(SKILL_DIR, "scripts"))

bd = SourceFileLoader("bd", os.path.join(SKILL_DIR, "scripts", "build-deck.py")).load_module()
from diagrams import Canvas, lighten  # noqa: E402
import _auth  # noqa: E402

TEMPLATE = os.path.join(SKILL_DIR, "templates", "scalar-2026.json")
PRES_ID = "1NnfZLDVYKFYKNceToJNGSg8Wpnod1Ume7fEgSVJWUKk"

DB_DOCS = "https://scalardb.scalar-labs.com/docs/latest/"
DL_DOCS = "https://scalardl.scalar-labs.com/docs/latest/"

# 図版・ページ番号のレイアウト定数
CX, CY, CW = 0.5, 0.98, 6.1          # コード欄（左）
RX, RW = 6.75, 2.75                  # 解説欄（右）
CH = 3.30                            # 本文エリアの高さ
BY, BH = 4.40, 0.62                  # ポイント帯
CODE_SIZE, CODE_LS = 7.5, 104        # コード文字サイズ・行送り(%)
# Slides 上の実効行高は fontSize * lineSpacing の約 1.45 倍
# （Noto Sans JP へのフォールバックを含む audit_text_fit と同じ係数）
LINE_FACTOR = 1.45

# 既存デッキのページ番号ボックス: 1 始まりのスライド位置 p → objectId
# （2..30 が pagenum_067..095 と連番になっているのを実測済み）
PAGENUM_OID = {p: f"pagenum_{p + 65:03d}" for p in range(2, 31)}
PAGENUM_GEO = dict(x=9.333, y=5.378, w=0.5, h=0.219)  # 右端 9.833 を保って幅 0.5in

# 「本資料の見方」(slide_005) の本文プレースホルダ
GUIDE_BODY_OID = "default_proposal_body_007"
GUIDE_LINES = [
    "各機能を 1 スライドずつ「図解 / 機能概要 / ユースケース / 特長」で整理",
    "対象: ScalarDB 15 機能、ScalarDL 9 機能（各セクション冒頭に機能マップ）",
    "コードが中心の 9 機能は、機能スライドの直後にコードサンプルを併載",
    "情報源: developers.scalar-labs.com の公式ドキュメント（2026年8月1日 調査）",
    "バージョン表記（3.15+ など）は機能が導入されたバージョン、右上はエディション",
    "※ プレビュー提供中の機能はその旨を明記",
]


# ---------------------------------------------------------------- コードスライド定義

# block = (見出し or None, コード文字列)
SAMPLES = [
    dict(
        after=5, accent="primary",
        title="コードで見る ACID トランザクション — begin / put / commit だけ",
        edition="全エディション（Community 〜）",
        blocks=[("Java — CRUD インターフェース", """\
TransactionFactory factory =
    TransactionFactory.create("database.properties");
DistributedTransactionManager manager =
    factory.getTransactionManager();
DistributedTransaction tx = manager.begin();      // 開始
try {
  Optional<Result> item = tx.get(Get.newBuilder() // 読み取り
      .namespace("order").table("items")
      .partitionKey(Key.ofInt("item_id", 1))
      .build());
  tx.put(Put.newBuilder()                         // 書き込み
      .namespace("order").table("orders")
      .partitionKey(Key.ofInt("order_id", 10))
      .textValue("status", "PAID").build());
  tx.commit();                                    // 確定
} catch (TransactionException e) {
  tx.rollback();                                  // 取り消し
}""", "java")],
        points=["begin() → CRUD → commit() の 3 段構え",
                "Get / Put はビルダーで型安全に組み立てる",
                "失敗時は rollback() — 障害からの復旧は ScalarDB が担う",
                "接続先が MySQL でも DynamoDB でも、このコードは同じ"],
        point="アプリは ScalarDB API だけを知ればよい — 下位 DB ごとの実装差はコードに現れない",
        notes=f"出典: {DB_DOCS}api-guide/ の Get/Put ビルダー例を注文ドメインに置き換え。"),

    dict(
        after=7, accent="primary",
        title="コードで見るマイクロサービストランザクション — join で参加",
        edition="全エディション",
        blocks=[("Java — 2 フェーズコミットインターフェース", """\
// サービス A（Coordinator）— 開始して ID を発行
TwoPhaseCommitTransaction txA = managerA.begin();
String txId = txA.getId();   // ← サービス B へ連携

// サービス B（Participant）— 同じ TX に参加
TwoPhaseCommitTransaction txB = managerB.join(txId);

// 各サービスで CRUD を実行した後、全員で確定
txA.prepare();  txB.prepare();   // ① 準備
txA.validate(); txB.validate();  // ② 検証
txA.commit();   txB.commit();    // ③ 確定""", "java")],
        points=["トランザクション ID の受け渡しだけでサービスが参加できる",
                "prepare → validate → commit を全参加者で実行",
                "失敗したら rollback() で全体を取り消し",
                "Saga / TCC の補償ロジックを自作しない"],
        point="サービスをまたいでも「単一 DB のトランザクション」と同じ感覚で書ける",
        notes=f"出典: {DB_DOCS}two-phase-commit-transactions/ validate は分離レベル設定により必要。"),

    dict(
        after=9, accent="primary",
        title="コードで見る SQL インターフェース — JDBC URL を替えるだけ",
        edition="Enterprise Premium",
        blocks=[("Java — JDBC", """\
// JDBC URL に ScalarDB の設定ファイルを指すだけ
String url = "jdbc:scalardb:scalardb-sql.properties";

try (Connection con = DriverManager.getConnection(url);
     Statement stmt = con.createStatement()) {
  con.setAutoCommit(false);

  ResultSet rs = stmt.executeQuery(
      "SELECT o.order_id, i.name"
      + " FROM order.orders o"
      + " JOIN order.items i ON o.item_id = i.item_id");

  stmt.executeUpdate(
      "UPDATE order.orders SET status = 'SHIPPED'"
      + " WHERE order_id = 10");

  con.commit();  // JOIN 先が別 DB でも ACID で確定
}""", "java")],
        points=["ドライバと URL 以外は普通の JDBC コード",
                "JOIN 相手が別種の DB でも同じ SQL",
                "Spring Data JDBC / Java SQL API も選べる",
                "標準 SQL の大規模なサブセットをサポート"],
        point="SQL 資産と開発者のスキルをそのままに、異種 DB 横断トランザクションへ",
        notes=f"出典: {DB_DOCS}scalardb-sql/jdbc-guide/ URL 形式は jdbc:scalardb:<設定ファイル>。"),

    dict(
        after=10, accent="primary",
        title="コードで見る GraphQL — 自動生成 API と @transaction",
        edition="Enterprise Premium",
        blocks=[
            ("1 リクエスト = 1 トランザクション（自動コミット）", """\
mutation PutUser1 {
  account_put(put: {key: {id: "user1"},
                    values: {balance: 1000}})
}""", "graphql"),
            ("複数リクエストを 1 つのトランザクションに", """\
# ① 開始 — 応答に TX ID が返る
query Start @transaction {
  account_get(get: {key: {id: "user1"}}) {
    account { balance } } }
# ② id を指定して同じ TX で更新
mutation Transfer @transaction(id: "c88da8…") {
  account_put(put: {key: {id: "user1"},
                    values: {balance: 750}}) }
# ③ commit: true で確定
query End @transaction(id: "c88da8…", commit: true) {
  account_get(get: {key: {id: "user2"}}) { … } }""", "graphql"),
        ],
        points=["get / put / delete などをテーブルごとに自動生成",
                "ディレクティブなしでも 1 リクエスト = 1 TX",
                "@transaction(id: …) で複数リクエストを束ねる",
                "放置した TX は既定 1 分でタイムアウト"],
        point="スキーマ定義も API 実装も書かない — テーブルを作れば API ができている",
        notes="出典: docs-scalardb getting-started-with-scalardb-cluster-graphql.mdx（account テーブル例）。"),

    dict(
        after=19, accent="primary",
        title="コードで見るインポート — JSON と --import だけで完了",
        edition="Core ツール（Schema Loader）",
        blocks=[
            ("import-schema.json — 取り込む既存テーブルを列挙", """\
{
  "legacy.orders":    { "transaction": true },
  "legacy.customers": {
    "transaction": true,
    "override-columns-type": { "created_at": "TIMESTAMP" }
  },
  "legacy.audit_log": { "transaction": false }
}""", "json"),
            ("実行 — データ移行なし・数秒で完了", """\
$ java -jar scalardb-schema-loader-3.18.0.jar \\
    --config database.properties \\
    -f import-schema.json --import""", "bash"),
        ],
        points=["transaction: true でメタデータ列を自動追加",
                "override-columns-type で型マッピングを調整",
                "処理時間は DB サイズに比例しない（数秒）",
                "主キー必須、decimal / enum 等の型は対象外"],
        point="既存 DB を止めずに、宣言 1 枚で異種 DB 横断トランザクションの対象にできる",
        notes=f"出典: {DB_DOCS}schema-loader-import/"),

    dict(
        after=25, accent="success",
        title="コードで見る Contract — 台帳ロジックは invoke 1 メソッド",
        edition="Community / Enterprise",
        blocks=[("Java — JacksonBasedContract（公式ドキュメントの StateUpdater）", """\
public class StateUpdater extends JacksonBasedContract {
  @Override
  public JsonNode invoke(Ledger<JsonNode> ledger,
      JsonNode argument, JsonNode properties) {
    String assetId = argument.get("asset_id").asText();
    int state = argument.get("state").asInt();

    Optional<Asset<JsonNode>> asset = ledger.get(assetId);
    if (!asset.isPresent()
        || asset.get().data().get("state").asInt() != state) {
      ledger.put(assetId, getObjectMapper()
          .createObjectNode().put("state", state));
    }
    return null;
  }
}""", "java")],
        points=["JacksonBasedContract を継承し invoke を実装",
                "台帳操作は ledger.get / put / scan の 3 つだけ",
                "登録・実行は所有者の秘密鍵で署名される",
                "決定性が必須 — 乱数・現在時刻は使わない"],
        point="台帳アプリのビジネスロジックはこの分量から書き始められる",
        notes=f"出典: {DL_DOCS}how-to-write-contract（StateUpdater。引数検証の throw は紙面の都合で省略）。"),

    dict(
        after=26, accent="success",
        title="コードで見る Function — 業務データも同じトランザクションで",
        edition="Community / Enterprise",
        blocks=[("Java — JacksonBasedFunction", """\
public class Payment extends JacksonBasedFunction {
  @Override
  public JsonNode invoke(
      Database<Get, Scan, Put, Delete, Result> db,
      JsonNode functionArg, JsonNode contractArg,
      JsonNode properties) {
    String account = functionArg.get("account").asText();
    long amount = functionArg.get("amount").asLong();

    // 残高（可変の業務データ）を ScalarDB API で更新
    db.put(Put.newBuilder()
        .namespace("bank").table("account")
        .partitionKey(Key.ofText("id", account))
        .bigIntValue("balance", balance + amount)
        .build());
    return null;
  }
}""", "java")],
        points=["Function 内は ScalarDB の Get / Put / Delete",
                "呼び出し元 Contract と 1 つの ACID TX で実行",
                "台帳 = Contract、更新できるデータ = Function と分担",
                "引数も Contract とは別に渡せる（functionArgument）"],
        point="証跡（台帳）と残高（業務データ）がズレない — 決済系の定石構成",
        notes=f"出典: {DL_DOCS}how-to-write-function（Payment 例を要約。残高読み出しは省略）。"),

    dict(
        after=27, accent="success",
        title="コードで見る TableStore — SQL 文だけで台帳テーブル",
        edition="Community / Enterprise / 3.12+",
        blocks=[("CLI — scalardl-tablestore execute-statement", """\
# テーブル作成 — コントラクト開発は不要
$ scalardl-tablestore execute-statement \\
    --properties client.properties --statement \\
    "CREATE TABLE employee (id STRING PRIMARY KEY,
                            department STRING)"

# 挿入・照会も SQL ライク（JOIN も可）
--statement "INSERT INTO employee VALUES
    {'id': '1001', 'name': 'Alice',
     'department': 'sales'}"
--statement "SELECT * FROM employee
    JOIN department
      ON employee.department = department.id"

# 監査は 1 文 — 全変更履歴を返す
--statement "SELECT history() FROM employee
    WHERE id = '1001'\"""", "bash")],
        points=["bootstrap で事前定義コントラクトを自動登録",
                "CREATE / INSERT / SELECT / UPDATE / JOIN に対応",
                "セカンダリインデックスも作れる",
                "history() が改ざん検知付きの全履歴を返す"],
        point="「SQL が書ければ台帳が作れる」— 台帳導入の開発コストを桁で下げる",
        notes=f"出典: {DL_DOCS}getting-started-tablestore"),

    dict(
        after=28, accent="success",
        title="コードで見る HashStore — コマンドだけで証拠保全",
        edition="Community / Enterprise / 3.12+",
        blocks=[("CLI — scalardl-hashstore", """\
# ① ファイルのハッシュを台帳へ（実データは預けない）
$ scalardl-hashstore put-object \\
    --properties client.properties \\
    --object-id contract-2026.pdf \\
    --hash 5c7440fb2273a247…151dab0 \\
    --metadata '{"note": "締結版"}'

# ② 手元のファイルと台帳の記録を突き合わせ
$ scalardl-hashstore compare-object-versions \\
    --object-id contract-2026.pdf \\
    --versions '[{"version_id": "v2",
                  "hash_value": "5c7440…"}]'

# ③ 監査対象のセット（コレクション）も管理
$ scalardl-hashstore create-collection \\
    --collection-id audit-2026 \\
    --object-ids contract-2026.pdf""", "bash")],
        points=["コードは 1 行も書かない（ノーコード）",
                "ハッシュのみ格納 — 大容量ファイルでも軽い",
                "コレクションで「監査対象の集合」ごと改変を検知",
                "validate-ledger で台帳自体の検証も可能"],
        point="put-object と compare だけで、監査に耐える証拠保全が始められる",
        notes=f"出典: {DL_DOCS}getting-started-hashstore"),
]


# ---------------------------------------------------------------- 描画

def block_height(code: str) -> float:
    lines = code.count("\n") + 1
    return lines * CODE_SIZE * (CODE_LS / 100) * LINE_FACTOR / 72 + 0.14


def draw_code_slide(d: Canvas, spec: dict, accent: str) -> None:
    d.label(5.0, 0.60, 4.5, 0.26, spec["edition"], size=9, align="END",
            color=d.P.muted)

    # 左: コードブロック（縦積み・シンタックスハイライト付き）
    y = CY
    for head, code, lang in spec["blocks"]:
        if head:
            d.label(CX, y, CW, 0.2, head, size=8.5, bold=True, color=accent)
            y += 0.24
        h = block_height(code)
        d.code_block(CX, y, CW, h, code, lang=lang, size=CODE_SIZE,
                     line_spacing=CODE_LS)
        y += h + 0.12
    if y - 0.12 > CY + CH + 0.02:
        print(f"  warn: コード欄がはみ出し気味 ({y - 0.12:.2f} > {CY + CH:.2f}) "
              f"— {spec['title'][:16]}", file=sys.stderr)

    # 右: 解説
    d.shape(RX, CY, RW, CH, kind="RECTANGLE", fill=d.P.surface,
            stroke=d.P.border)
    d.shape(RX, CY, RW, 0.06, kind="RECTANGLE", fill=accent, stroke=None)
    d.label(RX + 0.16, CY + 0.13, RW - 0.3, 0.28, "解説", size=10.5,
            bold=True, color=accent)
    d.label(RX + 0.16, CY + 0.48, RW - 0.32, CH - 0.6,
            "\n".join(f"・{p}" for p in spec["points"]), size=9,
            color=d.P.text, line_spacing=132)

    # 下: ポイント帯（機能スライドの「特長」帯と同じ体裁）
    d.shape(0.5, BY, 9.0, BH, kind="RECTANGLE",
            fill=lighten(accent, 0.9), stroke=lighten(accent, 0.5))
    d.label(0.68, BY, 1.5, BH, "ポイント", size=9.5, bold=True,
            align="START", valign="MIDDLE", color=accent)
    d.label(2.3, BY + 0.05, 7.0, BH - 0.1, spec["point"], size=9.5,
            align="START", valign="MIDDLE", color=d.P.text, line_spacing=122)


# ---------------------------------------------------------------- 生成

def main() -> int:
    template = bd.load_template(TEMPLATE)
    slides, drive = _auth.services(None)
    deck = bd.TemplateDeck(slides, drive, PRES_ID, template)

    # 既存 objectId（slide_*, pagenum_*, dgs*）との衝突を避ける
    orig_next_id = deck._next_id
    deck._next_id = lambda prefix: orig_next_id(f"cs_{prefix}")
    Canvas._seq = 5000

    problems: list[str] = []
    inserts = sorted(s["after"] for s in SAMPLES)

    def new_pos(old: int) -> int:
        """挿入後の 1 始まり位置。挿入スライド自身は new_pos(after)+1。"""
        return old + sum(1 for t in inserts if t < old)

    # 後ろから挿入すれば、先に積んだ insertionIndex がずれない
    for spec in sorted(SAMPLES, key=lambda s: -s["after"]):
        ref = deck.add_slide("TITLE_ONLY", title=spec["title"],
                             notes=spec.get("notes"), index=spec["after"])
        d = Canvas(deck, ref["slideId"], template)
        accent = getattr(d.P, spec["accent"])
        draw_code_slide(d, spec, accent)

        # 新規スライドのページ番号（既存デッキと同じ体裁で自前描画）
        num = new_pos(spec["after"]) + 1
        d.label(PAGENUM_GEO["x"], PAGENUM_GEO["y"], PAGENUM_GEO["w"],
                PAGENUM_GEO["h"], str(num), size=7, color="#666666",
                align="END", font="Arial")

        problems.extend(f"{spec['title'][:14]}…: {m}" for m in
                        (d.audit_bounds() + d.audit_overlaps()
                         + d.audit_text_fit()))

    # 既存スライドのページ番号を振り直す（番号が変わるものだけ）
    renumbered = 0
    for p, oid in PAGENUM_OID.items():
        n = new_pos(p)
        if n == p:
            continue
        deck.requests += [
            {"deleteText": {"objectId": oid, "textRange": {"type": "ALL"}}},
            {"insertText": {"objectId": oid, "text": str(n)}},
            {"updateTextStyle": {
                "objectId": oid,
                "style": {"fontFamily": "Arial",
                          "fontSize": {"magnitude": 7, "unit": "PT"},
                          "foregroundColor": {"opaqueColor": {
                              "rgbColor": _auth.hex_to_rgb("#666666")}}},
                "textRange": {"type": "ALL"},
                "fields": "fontFamily,fontSize,foregroundColor"}},
            {"updateParagraphStyle": {
                "objectId": oid, "style": {"alignment": "END"},
                "textRange": {"type": "ALL"}, "fields": "alignment"}},
        ]
        renumbered += 1

    # 「本資料の見方」にコードサンプルの一文を追記（全文入れ替え）
    deck.requests += [
        {"deleteText": {"objectId": GUIDE_BODY_OID, "textRange": {"type": "ALL"}}},
        {"insertText": {"objectId": GUIDE_BODY_OID, "text": "\n".join(GUIDE_LINES)}},
        {"updateTextStyle": {
            "objectId": GUIDE_BODY_OID,
            "style": {"fontSize": {"magnitude": 14, "unit": "PT"}},
            "textRange": {"type": "ALL"}, "fields": "fontSize"}},
        {"updateParagraphStyle": {
            "objectId": GUIDE_BODY_OID, "style": {"lineSpacing": 150},
            "textRange": {"type": "ALL"}, "fields": "lineSpacing"}},
    ]

    for m in problems:
        print(f"  検査: {m}")
    url = deck.commit()
    print(f"Done! +{len(SAMPLES)} slides, {renumbered} 枚のページ番号を更新. Open: {url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
