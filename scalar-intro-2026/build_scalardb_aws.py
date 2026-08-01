#!/usr/bin/env python3
"""ScalarDB の AWS(EKS)デプロイ構成図デッキ。

出典(2026-08-01 参照):
- https://scalardb.scalar-labs.com/docs/latest/scalar-kubernetes/ManualDeploymentGuideScalarDBClusterOnEKS/
- https://scalardb.scalar-labs.com/docs/latest/scalar-kubernetes/CreateEKSClusterForScalarDBCluster/
"""
from __future__ import annotations

import argparse
import os
import sys
from importlib.machinery import SourceFileLoader

SKILL_DIR = os.path.expanduser("~/.claude/skills/google-slides-template")
sys.path.insert(0, os.path.join(SKILL_DIR, "scripts"))

bd = SourceFileLoader("bd", os.path.join(SKILL_DIR, "scripts", "build-deck.py")).load_module()
from diagrams import Canvas, lighten  # noqa: E402

TEMPLATE = os.path.join(SKILL_DIR, "templates", "scalar-2026.json")
LOGO_DB = os.path.join(SKILL_DIR, "assets", "brand", "product-logos",
                       "scalardb-logo-horizontal.png")

TITLE = "ScalarDB — AWS デプロイ構成"
SUBTITLE = "Amazon EKS を用いた本番構成とクライアント接続モード"
DATE = "2026年8月"

DOCS = "https://scalardb.scalar-labs.com/docs/latest/scalar-kubernetes/"


def _pill(d, x, y, w, h, text, accent, *, light=0.88, size=8, bold=False):
    return d.shape(x, y, w, h, kind="ROUND_RECTANGLE",
                   fill=lighten(accent, light), stroke=accent, text=text,
                   size=size, bold=bold, color=d.P.text, line_spacing=112)


def _va(d, x1, y1, x2, y2):
    d.arrow(x1, y1, x2, y2, color=d.P.muted, weight=1.0, _anchored=True)


def draw_eks_production(d: Canvas) -> None:
    """本番構成: 3 AZ / 3 ノードの EKS + バックエンド DB。"""
    d.cloud_zone(0.45, 0.85, 9.1, 3.85, vendor="aws",
                 title="AWS リージョン（例: ap-northeast-1）", title_size=8.5)

    # VPC とその中の 3 AZ
    d.cloud_zone(0.7, 1.3, 5.6, 3.2, title="VPC — プライベートサブネット",
                 title_size=8, color=d.P.muted)
    d.cloud_icon("aws:elastic-kubernetes-service", 0.95, 1.62, 0.38, label="")
    d.label(1.45, 1.63, 2.6, 0.36, "Amazon EKS\n（Helm Chart でデプロイ）",
            size=8, align="START", valign="MIDDLE", color=d.P.text,
            line_spacing=115)
    for i, az in enumerate(["AZ-a", "AZ-c", "AZ-d"]):
        zx = 0.9 + i * 1.78
        d.cloud_zone(zx, 2.05, 1.62, 2.25, title=az, title_size=7.5,
                     color=d.P.info)
        _pill(d, zx + 0.12, 2.6, 1.38, 0.56, "EKS ノード\n4vCPU / 8GB〜",
              d.P.muted, size=7)
        _pill(d, zx + 0.12, 3.4, 1.38, 0.56, "ScalarDB\nCluster Pod",
              d.P.primary, size=7.5, bold=True)

    # バックエンド DB
    d.cloud_zone(6.55, 1.3, 2.75, 2.2, title="バックエンドデータベース",
                 title_size=8)
    d.cloud_icon("aws:aurora", 6.95, 1.7, 0.44, label="Aurora / RDS",
                 label_size=7.5, label_w=1.5)
    d.cloud_icon("aws:dynamodb", 8.25, 1.7, 0.44, label="DynamoDB",
                 label_size=7.5, label_w=1.3)
    d.label(6.75, 2.7, 2.4, 0.6,
            "事前に作成し、Cluster から\nプライベート接続", size=7.5,
            align="CENTER", valign="MIDDLE", color=d.P.muted, line_spacing=120)
    for ay in (2.6, 3.3):
        _va(d, 6.34, ay, 6.52, ay)

    # 運用系(踏み台・監視)
    d.cloud_icon("aws:ec2", 6.9, 3.75, 0.4, label="踏み台サーバー",
                 label_size=7.5, label_w=1.5)
    d.cloud_icon("aws:cloudwatch", 8.3, 3.75, 0.4, label="監視",
                 label_size=7.5, label_w=1.1)

    d.label(0.45, 4.78, 9.1, 0.24,
            "最低 3 ノード / 3 Pod を podAntiAffinity で AZ 分散 — 単一 AZ 障害でもサービス継続",
            size=9, align="CENTER", color=d.P.muted)


def draw_client_modes(d: Canvas) -> None:
    """クライアント接続の 2 モード。"""
    # direct-kubernetes モード
    d.cloud_zone(0.5, 1.0, 4.4, 3.3, title="direct-kubernetes モード",
                 title_size=8.5, color=d.P.primary)
    d.cloud_zone(0.75, 1.5, 3.9, 2.55, vendor="aws", title="Amazon EKS（同一クラスタ）",
                 title_size=7.5)
    _pill(d, 1.05, 2.1, 1.5, 0.6, "アプリ\nPod", d.P.info, size=8, bold=True)
    _pill(d, 2.85, 2.1, 1.5, 0.6, "ScalarDB\nCluster Pod", d.P.primary,
          size=8, bold=True)
    _va(d, 2.6, 2.4, 2.82, 2.4)
    d.label(0.75, 3.15, 3.9, 0.5,
            "同一 Kubernetes 内で直接通信\n（gRPC / SQL 60053・GraphQL 8080）",
            size=8, align="CENTER", valign="MIDDLE", color=d.P.muted,
            line_spacing=120)

    # indirect モード
    d.cloud_zone(5.1, 1.0, 4.4, 3.3, title="indirect モード", title_size=8.5,
                 color=d.P.success)
    d.icon("server", 5.4, 1.6, 0.4, label="アプリ\n（別環境）", label_size=7.5,
           label_w=1.2)
    d.cloud_icon("aws:elastic-load-balancing-network-load-balancer",
                 6.85, 1.6, 0.44, label="LoadBalancer", label_size=7,
                 label_w=1.3)
    d.cloud_zone(5.35, 2.7, 3.9, 1.35, vendor="aws", title="Amazon EKS",
                 title_size=7.5)
    _pill(d, 5.6, 3.15, 1.5, 0.6, "Scalar\nEnvoy", d.P.success, size=8,
          bold=True)
    _pill(d, 7.45, 3.15, 1.5, 0.6, "ScalarDB\nCluster Pod", d.P.primary,
          size=8, bold=True)
    _va(d, 6.05, 2.05, 6.85, 1.95)
    _va(d, 7.1, 2.3, 6.6, 3.12)
    _va(d, 7.15, 3.45, 7.42, 3.45)
    d.label(5.1, 4.42, 4.4, 0.26,
            "envoy.enabled=true / service.type=LoadBalancer",
            size=7.5, align="CENTER", color=d.P.muted)

    d.label(0.5, 4.78, 9.0, 0.24,
            "アプリの配置場所で選ぶ — 同一クラスタなら直結、外部からは Envoy 経由でロードバランス",
            size=9, align="CENTER", color=d.P.muted)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--folder", default=None)
    args = p.parse_args()

    template = bd.load_template(TEMPLATE)
    deck = bd.TemplateDeck.create(template, title=TITLE, folder=args.folder)
    problems: list[str] = []

    deck.add_slide("COVER", title=TITLE, subtitle=SUBTITLE,
                   body=f"{DATE}\n株式会社Scalar")

    for title, draw, notes in [
        ("本番構成: ScalarDB Cluster を 3 AZ の EKS ノードへ分散配置",
         draw_eks_production,
         f"出典: {DOCS}CreateEKSClusterForScalarDBCluster/ ノード最低3台(4vCPU/8GB、BYOLは2vCPU/4GB可)。"
         "Cluster Autoscaler 使用時は /24 等の十分な CIDR。"),
        ("クライアント接続は 2 モード: 同一クラスタ直結か、Envoy 経由か",
         draw_client_modes,
         f"出典: {DOCS}ManualDeploymentGuideScalarDBClusterOnEKS/ ポート: gRPC/SQL 60053、GraphQL 8080、"
         "メトリクス 9080、Envoy 管理 9001。"),
    ]:
        ref = deck.add_slide("TITLE_ONLY", title=title, notes=notes)
        d = Canvas(deck, ref["slideId"], template)
        draw(d)
        problems += [f"{title[:14]}…: {m}" for m in
                     (d.audit_bounds() + d.audit_connectors()
                      + d.audit_overlaps() + d.audit_text_fit())]

    deck.add_slide(
        "CONTENT", title="構成のポイント — 公式ガイドの要件と推奨",
        body=[
            "ワーカーノードは最低 3 台（4vCPU / 8GB 以上。BYOL は 2vCPU / 4GB 可）、Cluster Pod も 3 つ以上を podAntiAffinity で別ノードに分散",
            "EKS クラスタは VPC のプライベートサブネットに構築。Cluster Autoscaler を使う場合は /24 など十分な CIDR を確保",
            "開放ポートは gRPC / SQL 60053、GraphQL 8080、監視 9080（Envoy 併用時は 60053 / 9001）。セキュリティグループと NACL で未使用接続を制限",
            "HPA（水平 Pod オートスケール）を使う場合は Cluster Autoscaler も併せて構成",
            "バックエンド DB（Aurora / RDS / DynamoDB など）は事前に用意し、運用作業は踏み台サーバー経由で実施",
            "商用ライセンスは AWS Marketplace の従量課金（Pod 単位）または BYOL",
        ], body_font_size=13, body_line_spacing=150,
        notes=f"出典: {DOCS}CreateEKSClusterForScalarDBCluster/ , {DOCS}ManualDeploymentGuideScalarDBClusterOnEKS/（2026-08-01 参照）")

    deck.add_slide("CLOSING")
    deck.add_page_numbers()
    for m in problems:
        print(f"  検査: {m}")
    url = deck.commit()
    print(f"Done! 5 slides. Open: {url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
