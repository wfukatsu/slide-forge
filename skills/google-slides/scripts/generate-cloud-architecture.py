#!/usr/bin/env python3
"""クラウド構成図のサンプルデッキを生成する。

`assets/shared/cloud-icons/` の公式アイコンを使って、よくある 4 つの見せ方を
1 枚ずつ作る。SlideBuilder に `CloudIconMixin` を混ぜる書き方の実例。

  # 初回だけ: クラウドアイコンを取り込む（リポジトリには同梱していない）
  ~/.claude/venvs/gslides/bin/python scripts/fetch-cloud-icons.py
  ~/.claude/venvs/gslides/bin/python scripts/generate-cloud-architecture.py

SlideBuilder の本体は `generate-icon-gallery.py` のものを使い回している
（デモ用の最小構成。実務では references/google-slides-api.md の SlideBuilder に
`CloudIconMixin` を混ぜる）。

ライセンス: アイコンは各ベンダーの資産。アーキテクチャ図・研修資料・
ドキュメントでの利用のみが許諾されており、**色の変更・回転・反転は禁止**。
`add_cloud_icon` は既定でアイコンの下に正式名称を出す（各社の推奨）。
"""

import os
import sys
from importlib.machinery import SourceFileLoader

if sys.version_info < (3, 10):
    sys.exit("Error: Python 3.10+ が必要です")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from googleapiclient.discovery import build  # noqa: E402

from cloud_icons import VENDOR_COLOR, VENDOR_LABEL, CloudIconMixin  # noqa: E402

gallery = SourceFileLoader(
    "gallery", os.path.join(SCRIPT_DIR, "generate-icon-gallery.py")).load_module()
C = gallery.C
PAGE_W, PAGE_H = gallery.PAGE_W, gallery.PAGE_H


class ArchBuilder(gallery.SlideBuilder, CloudIconMixin):
    """デモ用 SlideBuilder にクラウドアイコンを足したもの。"""

    def __init__(self, drive_service):
        super().__init__(drive_service)
        self.cloud_label_color = C.muted

    def zone(self, slide_id, x, y, w, h, *, vendor=None, title=None, color=None):
        """ゾーン枠（クラウド / リージョン / VPC）。**中身より先に描く。**"""
        c = color or (VENDOR_COLOR.get(vendor) if vendor else "#9AA5B1")
        oid = self.add_rect(slide_id, x, y, w, h, border_color=self._cloud_rgb(c))
        # **塗りは明示的に消す。** fill を渡さないだけだと Slides の既定色
        # （薄いグレー）が残り、囲いのはずが板になる
        self.requests.append({"updateShapeProperties": {
            "objectId": oid,
            "shapeProperties": {
                "shapeBackgroundFill": {"propertyState": "NOT_RENDERED"},
                "outline": {"dashStyle": "DASH"}},
            "fields": "shapeBackgroundFill,outline.dashStyle"}})
        label = title if title is not None else (VENDOR_LABEL.get(vendor) or "")
        if label:
            self.add_text(slide_id, label, x + 0.12, y + 0.06, min(w - 0.24, 3.2), 0.22,
                          font_size=9, bold=True, color=self._cloud_rgb(c),
                          alignment="START", valign="MIDDLE")
        return oid


def main():
    creds = gallery.get_credentials()
    slides = build("slides", "v1", credentials=creds)
    drive = build("drive", "v3", credentials=creds)

    pres = slides.presentations().create(
        body={"title": "クラウド構成図サンプル"}).execute()
    pid = pres["presentationId"]
    sb = ArchBuilder(drive)

    # 1. 表紙
    sid = sb.add_slide()
    sb.add_rect(sid, 0, 0, PAGE_W, PAGE_H, fill=C.primary)
    sb.add_text(sid, "クラウド構成図", 0.8, 2.1, 8.4, 0.7, font_size=32, bold=True,
                color=C.white)
    sb.add_text(sid, "AWS / Google Cloud / Azure の公式アイコンで描く",
                0.8, 2.95, 8.4, 0.4, font_size=13, color=C.white)

    # 2. ゾーンで囲う
    sid = sb.title_slide("ゾーンで囲って中に並べる")
    sb.zone(sid, 0.45, 1.1, 9.1, 2.5, vendor="aws", title="AWS  ap-northeast-1")
    sb.zone(sid, 0.75, 1.5, 8.5, 1.85, title="VPC  10.0.0.0/16")
    sb.add_cloud_icon_row(sid, 1.0, 1.9, 8.0, [
        ("aws:elastic-load-balancing", "ALB"),
        ("aws:elastic-container-service", "ECS Fargate"),
        ("aws:rds", "RDS"),
        ("aws:simple-storage-service", "S3"),
        ("aws:cloudwatch", "CloudWatch"),
    ], size=0.7, label_size=8.5)

    # 3. マルチクラウド
    sid = sb.title_slide("マルチクラウドを並べる")
    for i, (vendor, items) in enumerate([
        ("aws", [("aws:elastic-kubernetes-service", "EKS"), ("aws:aurora", "Aurora")]),
        ("gcp", [("gcp:gke", "GKE"), ("gcp:cloud-spanner", "Spanner")]),
        ("azure", [("azure:kubernetes-services", "AKS"), ("azure:cosmos-db", "Cosmos DB")]),
    ]):
        x = 0.45 + i * 3.07
        sb.zone(sid, x, 1.15, 2.9, 2.1, vendor=vendor)
        sb.add_cloud_icon_row(sid, x + 0.15, 1.6, 2.6, items, size=0.62, label_size=8)

    # 4. データの流れ
    sid = sb.title_slide("データの流れを見せる")
    sb.add_cloud_icon_flow(sid, 0.5, 1.35, 9.0, [
        ("aws:kinesis-data-streams", "取り込み"), ("aws:lambda", "変換"),
        ("aws:simple-storage-service", "保管"), ("aws:glue", "カタログ"),
        ("aws:athena", "分析"),
    ], size=0.7)
    sb.add_cloud_icon_flow(sid, 0.5, 3.1, 9.0, [
        ("gcp:pubsub", "取り込み"), ("gcp:dataflow", "変換"),
        ("gcp:cloud-storage", "保管"), ("gcp:data-catalog", "カタログ"),
        ("gcp:bigquery", "分析"),
    ], size=0.7)

    # 5. 囲いのアイコン
    sid = sb.title_slide("囲いのアイコン（kind: group）")
    sb.add_cloud_icon_row(sid, 0.5, 1.6, 9.0, [
        ("aws:aws-cloud", "AWS Cloud"), ("aws:region", "リージョン"),
        ("aws:virtual-private-cloud-vpc", "VPC"),
        ("aws:public-subnet", "パブリック\nサブネット"),
        ("aws:private-subnet", "プライベート\nサブネット"),
        ("aws:auto-scaling-group", "Auto Scaling"),
    ], size=0.78, label_size=9)

    first = slides.presentations().get(presentationId=pid).execute()["slides"][0]
    sb.requests.append({"deleteObject": {"objectId": first["objectId"]}})

    for i in range(0, len(sb.requests), 500):
        chunk = sb.requests[i:i + 500]
        slides.presentations().batchUpdate(
            presentationId=pid, body={"requests": chunk}).execute()
        print(f"  batch {i // 500 + 1}: {len(chunk)} requests")

    sb.cleanup_uploaded_assets()
    print(f"Done! {len(sb.slide_ids)} slides created.")
    print(f"Open: https://docs.google.com/presentation/d/{pid}/edit")
    return 0


if __name__ == "__main__":
    sys.exit(main())
