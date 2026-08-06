#!/usr/bin/env python3
"""AWS / Google Cloud / Azure の公式アーキテクチャアイコンを取り込む。

`download-cloud-icons.sh` の後継。違いは 3 つ。

1. **配布 URL をベンダーのページから解決する。** 版が上がっても追随できる
   （旧スクリプトは URL 直書きで、AWS は 1 版、Azure は 3 版遅れていた）。
2. **SVG を正本として置く。** 使うときに必要な解像度へ焼く（`cloud_icons.py`）。
   旧スクリプトは Azure を 64px の PNG に焼いて捨てていたため、スライドに
   貼ると粗かった。
3. **マニフェスト `cloud-icons.json` を作る。** 名前で引けるようになる。
   旧構成は 1,500 ファイルを `ls` で漁るしかなく、Azure は
   `02390-icon-service-azure-sql.png` のような名前で引けなかった。

    python scripts/fetch_cloud_icons.py                 # 3 ベンダーとも取り込む
    python scripts/fetch_cloud_icons.py --vendor azure  # 1 つだけ更新する
    python scripts/fetch_cloud_icons.py --dry-run       # 取得せず URL だけ確かめる

Places icons under the repo's `assets/cloud-icons/` (single shared destination).

ライセンス上の注意（`references/cloud-icons.md` に詳述）:
アイコンは各ベンダーの資産で、アーキテクチャ図・研修資料・ドキュメントでの
利用のみが許諾されている。**色の変更・回転・反転・縦横比の変更は禁止**。
そのため本スクリプトは素材に一切手を加えず、そのまま置く。
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import shutil
import sys
import tempfile
import urllib.request
import zipfile
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(SCRIPT_DIR)

sys.path.insert(0, SCRIPT_DIR)
from _i18n import t, register  # noqa: E402

register({
    "  warn: could not find the URL on the {vendor} page; using the known URL":
        "  warn: {vendor} のページから URL を拾えず、既知の URL を使います",
    "Could not find the {vendor} download URL on the page: {page}\n"
    "  The page layout may have changed; fix the pattern in SOURCES":
        "{vendor} の配布 URL をページから拾えませんでした: {page}\n"
        "  ページの作りが変わった可能性があります。SOURCES の pattern を直してください",
    "  skip: parent of {dest} does not exist; not copying":
        "  skip: {dest} の親が無いので複製しません",
    "  copied: {dest}": "  複製: {dest}",
    "[{root}] not fetched yet (run this script with no arguments to fetch)":
        "[{root}] 未取り込み（このスクリプトを引数なしで実行すると入ります）",
    "not fetched: {root}": "未取り込み: {root}",
    "files listed but missing on disk: {files}": "実体が無い: {files}",
    "files not in the manifest: {files}": "マニフェストに無いファイル: {files}",
    "icon sets differ between skills ({count} differences)":
        "スキル間でアイコン集合が違う（差 {count} 件）",
    "\nProblems:": "\n問題:",
    "\nConsistency check: no problems": "\n整合チェック: 問題なし",
    "Fetch the official cloud vendor icons": "クラウドベンダーの公式アイコンを取り込む",
    "Target vendor (default: all)": "対象ベンダー（既定は全部）",
    "Destination (default: the built-in destinations)": "配置先（既定は 2 スキル）",
    "Resolve URLs only, do not download": "URL の解決だけ行う",
    "Only check that fetched assets and the manifest are consistent":
        "取り込み済みの素材とマニフェストの整合だけ調べる",
    "Directory holding pre-downloaded ZIPs (skips re-downloading)":
        "ダウンロード済み ZIP を置いたディレクトリ（再取得しない）",
    "  -> {count} icons": "  → {count} 件",
    "  warn: ALIAS_HINTS entry '{key}' not found in the assets"
    " (the service name may have changed)":
        "  warn: ALIAS_HINTS の '{key}' が素材に見つかりません"
        "（サービス名が変わった可能性）",
    "\nPlaced {count} icons in total ({png} with a PNG fallback)":
        "\n合計 {count} 個のアイコンを配置しました（PNG 併置 {png} 件）",
    "Destination: {dest}": "配置先: {dest}",
    "  {vendor}: {count} categories": "  {vendor}: {count} カテゴリ",
})

# Single destination: the repo's shared asset tree (gitignored, restored on demand)
DESTS = [
    os.path.join(REPO_DIR, "assets", "cloud-icons"),
]

UA = {"User-Agent": "Mozilla/5.0 (compatible; gslides-skill/1.0)"}

# 配布ページと、そこから ZIP の URL を拾う正規表現。ページが変わったらここだけ直す
SOURCES = {
    "aws": {
        "page": "https://aws.amazon.com/architecture/icons/",
        "pattern": r"https://[^\"']*Icon-package[^\"']*\.zip",
        "fallback": None,
        "terms": "https://aws.amazon.com/trademark-guidelines/",
    },
    "azure": {
        "page": "https://learn.microsoft.com/en-us/azure/architecture/icons/",
        "pattern": r"https://[^\"')]*Azure_Public_Service_Icons[^\"')]*\.zip",
        "fallback": None,
        "terms": "https://learn.microsoft.com/en-us/azure/architecture/icons/",
    },
    # GCP はページが JS 描画で URL を拾えないため、公開されている 3 本を直接使う。
    # core（現行デザイン・19 種）> category（53 種）> legacy（216 種・2021 年）の
    # 優先順で重ねる
    "gcp": {
        "page": "https://cloud.google.com/icons",
        "urls": [
            ("legacy", "https://services.google.com/fh/files/misc/google-cloud-legacy-icons.zip"),
            ("category", "https://services.google.com/fh/files/misc/category-icons.zip"),
            ("core", "https://services.google.com/fh/files/misc/core-products-icons.zip"),
        ],
        "terms": "https://cloud.google.com/icons",
    },
}

# GCP legacy はカテゴリを持たないため、サービス名から推定する
GCP_CATEGORY_RULES = [
    ("compute", ("compute_engine", "bare_metal", "gpu", "tpu", "vmware", "gce", "os_")),
    ("containers", ("kubernetes", "gke", "container", "anthos", "cloud_run", "artifact_registry", "kuberun")),
    ("serverless", ("cloud_functions", "app_engine", "eventarc", "workflows", "endpoints", "api_gateway", "scheduler", "tasks")),
    ("databases", ("sql", "spanner", "bigtable", "firestore", "datastore", "memorystore", "database", "alloydb")),
    ("storage", ("storage", "persistent_disk", "filestore", "local_ssd", "transfer")),
    ("networking", ("cdn", "dns", "interconnect", "load_balancing", "nat", "network", "router", "routes", "vpn", "armor", "traffic_director", "private_", "firewall", "connectivity")),
    ("security", ("security", "key_", "kms", "binary_authorization", "certificate", "ekm", "hsm", "ids", "beyondcorp", "identity", "phishing", "web_risk", "access_", "data_loss", "secret_manager", "assured", "risk_")),
    ("ai_ml", ("ai_", "automl", "vision", "natural_language", "translation", "inference", "dialogflow", "document_ai", "speech", "text_", "vertex", "video_intelligence", "recommendations", "retail", "genomics", "healthcare_nlp", "agent")),
    ("data_analytics", ("bigquery", "dataflow", "dataproc", "dataplex", "dataprep", "pubsub", "data_catalog", "data_fusion", "datalab", "datastream", "datashare", "composer", "looker", "analytics", "stream_suite")),
    ("developer_tools", ("cloud_build", "cloud_code", "cloud_deploy", "cloud_shell", "test_lab", "debugger", "source_", "tools_", "deployment_manager", "developer")),
    ("management", ("logging", "monitoring", "cloud_ops", "error_reporting", "profiler", "trace", "stackdriver", "audit", "policy", "asset", "quotas", "billing", "administration", "permissions", "project", "support", "configuration")),
    ("integration", ("apigee", "api", "connectors")),
]

# 正式名称からは引けない通称。ここに書いたものが別名として引けるようになる
# （例: 「Amazon Simple Storage Service」を s3 で引く）
ALIAS_HINTS = {
    "aws:simple-storage-service": ["s3", "Amazon S3"],
    "aws:simple-storage-service-glacier": ["glacier", "s3 glacier"],
    "aws:simple-queue-service": ["sqs", "Amazon SQS"],
    "aws:simple-notification-service": ["sns", "Amazon SNS"],
    "aws:simple-email-service": ["ses", "Amazon SES"],
    "aws:identity-and-access-management": ["iam"],
    "aws:key-management-service": ["kms"],
    "aws:elastic-load-balancing": ["elb", "alb", "nlb", "ロードバランサ"],
    "aws:elastic-container-service": ["ecs"],
    "aws:elastic-kubernetes-service": ["eks"],
    "aws:efs": ["elastic file system"],
    "aws:elastic-block-store": ["ebs"],
    "aws:rds": ["relational database service"],
    "aws:route-53": ["route53", "dns"],
    "aws:api-gateway": ["apigw"],
    "aws:step-functions": ["sfn"],
    "aws:virtual-private-cloud": ["vpc"],
    "azure:kubernetes-services": ["aks"],
    "azure:container-registries": ["acr"],
    "azure:cosmos-db": ["cosmosdb", "cosmos"],
    "azure:virtual-machine": ["vm"],
    "azure:virtual-networks": ["vnet"],
    "azure:storage-accounts": ["blob", "blob storage"],
    "azure:key-vaults": ["key vault"],
    "azure:sql-database": ["azure sql"],
    "gcp:gke": ["google kubernetes engine", "kubernetes"],
    "gcp:cloud-storage": ["gcs"],
    "gcp:bigquery": ["bq"],
    "gcp:cloud-load-balancing": ["ロードバランサ"],
    "gcp:key-management-service": ["kms"],
}

# core パッケージと legacy パッケージで名前が違うため、同じ製品なのに 2 件に
# なってしまうもの。左を消して右へ別名として吸収する
GCP_SUPERSEDED = {
    "gcp:google-kubernetes-engine": "gcp:gke",
}

# 表示名を作るときに大文字のままにしたい語
ACRONYMS = {
    "ai", "api", "aws", "bi", "cdn", "cpu", "db", "dns", "dr", "ec2", "ecs", "efs",
    "eks", "gke", "gpu", "hpc", "iam", "id", "ids", "iot", "ip", "kms", "ml", "nat",
    "os", "ram", "rds", "sdk", "sql", "ssd", "ssl", "tpu", "ui", "vm", "vpc", "vpn",
    "waf", "cdc", "hsm", "cli", "gcp",
}


def fetch(url: str, timeout: int = 300) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def resolve_zip_url(vendor: str) -> str:
    """ベンダーのページから最新 ZIP の URL を拾う。"""
    src = SOURCES[vendor]
    html = fetch(src["page"], timeout=60).decode("utf-8", "replace")
    hits = re.findall(src["pattern"], html)
    if not hits:
        if src.get("fallback"):
            print(t("  warn: could not find the URL on the {vendor} page; "
                    "using the known URL", vendor=vendor), file=sys.stderr)
            return src["fallback"]
        raise RuntimeError(
            t("Could not find the {vendor} download URL on the page: {page}\n"
              "  The page layout may have changed; fix the pattern in SOURCES",
              vendor=vendor, page=src["page"]))
    # 同じ URL が複数回出ることがあるので最初の 1 本
    return sorted(set(hits))[0]


# ---------- 名前の正規化 ----------

def slugify(name: str) -> str:
    s = re.sub(r"[_\s]+", "-", name.strip())
    s = re.sub(r"[^A-Za-z0-9\-]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-").lower()
    return s


def _tail_acronyms(name: str) -> list[str]:
    """「Virtual private cloud VPC」のように末尾に付く略称を別名として拾う。"""
    return [w for w in name.split() if 2 <= len(w) <= 5 and w.isupper()]


def titleize(slug: str) -> str:
    words = [w for w in re.split(r"[-_\s]+", slug) if w]
    return " ".join(w.upper() if w.lower() in ACRONYMS else w.capitalize() for w in words)


class Index:
    """マニフェストを組み立てる。slug の衝突をここで解く。"""

    def __init__(self):
        self.icons: dict[str, dict] = {}

    def add(self, vendor, slug, *, name, category, kind, src_path, aliases=(),
            prefer=False):
        key = f"{vendor}:{slug}"
        if key in self.icons and not prefer:
            # 同名が来たら別名として吸収する（例: Resource アイコンとサービスアイコン）
            existing = self.icons[key]
            for a in (name, *aliases):
                if a and a not in existing["aliases"]:
                    existing["aliases"].append(a)
            return None
        self.icons[key] = {
            "vendor": vendor, "slug": slug, "name": name, "category": category,
            "kind": kind, "file": f"{vendor}/{category}/{slug}.svg",
            "aliases": [a for a in dict.fromkeys(aliases) if a and a != name],
            "_src": src_path,
        }
        return key


# ---------- ベンダーごとの取り込み ----------

def collect_aws(root: str, idx: Index) -> None:
    """Architecture-Service-Icons / Resource-Icons / Architecture-Group-Icons / Category-Icons。

    サービスアイコンは 16/32/48/64 の 4 サイズが SVG で入っているが、中身は
    ベクタなので **64 のものだけ**を正本として採る。
    """
    def walk(pattern):
        for dirpath, _dirs, files in os.walk(root):
            for f in files:
                if f.startswith("._") or not f.endswith(".svg"):
                    continue
                p = os.path.join(dirpath, f)
                if pattern in p:
                    yield p

    # サービス: .../Arch_<Category>/64/Arch_<Name>_64.svg
    for p in walk("Architecture-Service-Icons"):
        parts = p.split(os.sep)
        if parts[-2] != "64":
            continue
        category = slugify(parts[-3].replace("Arch_", "")).replace("-", "_")
        name = re.sub(r"^Arch_|_64\.svg$", "", parts[-1]).replace("-", " ").replace("_", " ")
        base = re.sub(r"^(Amazon|AWS)\s+", "", name)
        idx.add("aws", slugify(base), name=name.strip(), category=category,
                kind="service", src_path=p, aliases=[name, slugify(name)])

    # リソース: .../Res_<Category>/Res_<Name>_48.svg
    for p in walk("Resource-Icons"):
        parts = p.split(os.sep)
        category = slugify(parts[-2].replace("Res_", "")).replace("-", "_")
        name = re.sub(r"^Res_|_(48|32|16|64)\.svg$", "", parts[-1]).replace("-", " ").replace("_", " ")
        base = re.sub(r"^(Amazon|AWS)\s+", "", name)
        slug = slugify(base)
        if f"aws:{slug}" in idx.icons:
            slug = "res-" + slug
        idx.add("aws", slug, name=name.strip(), category=category, kind="resource",
                src_path=p, aliases=[name])

    # グループ（VPC・サブネット・リージョン等の枠）: <Name>_32.svg / <Name>_32_Dark.svg
    for p in walk("Architecture-Group-Icons"):
        stem = os.path.basename(p)[:-4]
        dark = stem.endswith("_Dark")
        name = re.sub(r"_(16|32|48|64)(_Dark)?$", "", stem).replace("-", " ")
        slug = slugify(name) + ("-dark" if dark else "")
        if f"aws:{slug}" in idx.icons:
            slug = "group-" + slug
        idx.add("aws", slug, name=name.strip() + ("（濃色背景用）" if dark else ""),
                category="groups", kind="group", src_path=p,
                aliases=[name, "group " + name, *_tail_acronyms(name)])

    # カテゴリ: Arch-Category_<Name>_32.svg（32 のディレクトリだけ採る）
    for p in walk("Category-Icons"):
        if "_32" not in os.path.basename(os.path.dirname(p)):
            continue
        name = re.sub(r"^Arch-Category_|_(16|32|48|64)\.svg$", "", os.path.basename(p))
        name = name.replace("-", " ")
        slug = "category-" + slugify(name)
        idx.add("aws", slug, name=name.strip() + "（カテゴリ）", category="categories",
                kind="category", src_path=p, aliases=[name])


def collect_azure(root: str, idx: Index) -> None:
    """Azure_Public_Service_Icons/Icons/<category>/<NNNNN>-icon-service-<Name>.svg"""
    for dirpath, _dirs, files in os.walk(root):
        for f in files:
            if f.startswith("._") or not f.endswith(".svg"):
                continue
            category = slugify(os.path.basename(dirpath)).replace("-", "_")
            stem = f[:-4]
            # 先頭の連番と icon-service / icon の接頭辞を落とす
            name = re.sub(r"^\d+-icon-(service-)?", "", stem).replace("-", " ")
            base = re.sub(r"^Azure\s+", "", name, flags=re.I)
            slug = slugify(base)
            if f"azure:{slug}" in idx.icons:
                slug = slugify(name)
            idx.add("azure", slug, name=name.strip(), category=category,
                    kind="service", src_path=os.path.join(dirpath, f),
                    aliases=[name, "Azure " + base.strip(), stem])


def collect_gcp(root: str, idx: Index, flavor: str) -> None:
    """legacy: <service>/<service>.svg / core・category: <Name>/SVG/<file>.svg"""
    if flavor == "legacy":
        for entry in sorted(os.listdir(root)):
            d = os.path.join(root, entry)
            if not os.path.isdir(d) or entry.startswith("__"):
                continue
            svg = os.path.join(d, f"{entry}.svg")
            if not os.path.exists(svg):
                cands = [f for f in os.listdir(d) if f.endswith(".svg")]
                if not cands:
                    continue
                svg = os.path.join(d, cands[0])
            slug = slugify(entry)
            idx.add("gcp", slug, name=titleize(entry), category=gcp_category(entry),
                    kind="service", src_path=svg, aliases=[entry])
        return

    # core / category は「Unique Icons/<製品名>/SVG/<file>.svg」の形
    for dirpath, _dirs, files in os.walk(root):
        if os.path.basename(dirpath) != "SVG":
            continue
        product = os.path.basename(os.path.dirname(dirpath))
        svgs = [f for f in files if f.endswith(".svg") and not f.startswith("._")]
        if not svgs:
            continue
        # "-color" 付き（フルカラー版）を優先する
        svgs.sort(key=lambda f: (0 if "color" in f.lower() else 1, len(f)))
        name = product.replace("_", " ").strip()
        slug = slugify(name)
        if flavor == "category":
            slug = "category-" + slug
            kind, category = "category", "categories"
            name = name + "（カテゴリ）"
        else:
            kind, category = "service", gcp_category(slug.replace("-", "_"))
        # core は現行デザインなので legacy を上書きする
        idx.add("gcp", slug, name=name, category=category, kind=kind,
                src_path=os.path.join(dirpath, svgs[0]),
                aliases=[product], prefer=(flavor == "core"))


def gcp_category(service: str) -> str:
    s = service.lower()
    for cat, keys in GCP_CATEGORY_RULES:
        if any(k in s for k in keys):
            return cat
    return "other"


# ---------- 書き出し ----------

def render_check(svg_path: str) -> bool:
    """cairosvg で焼けるか確かめる。焼けないものは PNG を併置する。"""
    try:
        import cairosvg
    except Exception:
        return True  # 判定できないときは素通りさせる
    try:
        cairosvg.svg2png(url=svg_path, write_to=io.BytesIO(), output_width=64,
                         output_height=64)
        return True
    except Exception:
        return False


def write_assets(idx: Index, dests: list[str], sources: dict,
                 vendors: list[str]) -> dict:
    stats = {"icons": 0, "png_fallback": 0}
    primary = dests[0]

    # 今回取り込むベンダーの配下は作り直す（旧版の残骸を残さない）。
    # 触らないベンダーは既存のマニフェストから引き継ぐ
    kept, kept_sources = {}, {}
    old_path = os.path.join(primary, "cloud-icons.json")
    if os.path.exists(old_path):
        with open(old_path, encoding="utf-8") as f:
            old = json.load(f)
        kept = {k: v for k, v in old.get("icons", {}).items()
                if v.get("vendor") not in vendors}
        kept_sources = {k: v for k, v in old.get("sources", {}).items()
                        if k.split(":")[0] not in vendors}
    for v in vendors:
        shutil.rmtree(os.path.join(primary, v), ignore_errors=True)

    for key, meta in sorted(idx.icons.items()):
        dst = os.path.join(primary, meta["file"])
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(meta["_src"], dst)
        if not render_check(dst):
            # ベンダー同梱の PNG があれば拾う（無ければ諦めて svg のまま）
            png_src = meta["_src"][:-4] + ".png"
            alt = os.path.join(os.path.dirname(os.path.dirname(meta["_src"])), "PNG")
            if not os.path.exists(png_src) and os.path.isdir(alt):
                cands = [f for f in os.listdir(alt) if f.endswith(".png")]
                png_src = os.path.join(alt, cands[0]) if cands else png_src
            if os.path.exists(png_src):
                shutil.copyfile(png_src, dst[:-4] + ".png")
                meta["raster"] = meta["file"][:-4] + ".png"
                stats["png_fallback"] += 1
        stats["icons"] += 1

    icons = dict(kept)
    icons.update({k: {kk: vv for kk, vv in m.items() if not kk.startswith("_")}
                  for k, m in idx.icons.items()})
    manifest = {
        "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sources": {**kept_sources, **sources},
        "terms": {v: SOURCES[v]["terms"] for v in SOURCES},
        "note": ("Vendor assets. Use only in architecture diagrams, training "
                 "material, and documentation. Recoloring, rotating, flipping, "
                 "and changing the aspect ratio are prohibited."),
        "icons": dict(sorted(icons.items())),
    }
    with open(os.path.join(primary, "cloud-icons.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        f.write("\n")

    # 2 つめ以降のスキルへ複製する
    for d in dests[1:]:
        if not os.path.isdir(os.path.dirname(d)):
            print(t("  skip: parent of {dest} does not exist; not copying", dest=d),
                  file=sys.stderr)
            continue
        if os.path.isdir(d):
            shutil.rmtree(d)
        shutil.copytree(primary, d)
        print(t("  copied: {dest}", dest=d))
    return stats


# ---------- メイン ----------

def verify(dests: list[str]) -> int:
    """配置済みの素材とマニフェストが食い違っていないか調べる。"""
    problems = []
    sets = []
    for root in dests:
        mf = os.path.join(root, "cloud-icons.json")
        if not os.path.exists(mf):
            print(t("[{root}] not fetched yet (run this script with no arguments "
                    "to fetch)", root=root))
            problems.append(t("not fetched: {root}", root=root))
            continue
        with open(mf, encoding="utf-8") as f:
            icons = json.load(f)["icons"]
        listed = {m["file"] for m in icons.values()}
        listed |= {m["raster"] for m in icons.values() if m.get("raster")}
        on_disk = set()
        for dp, _dn, fn in os.walk(root):
            for f in fn:
                if f.endswith((".svg", ".png")):
                    on_disk.add(os.path.relpath(os.path.join(dp, f), root))
        missing = sorted(listed - on_disk)
        orphan = sorted(on_disk - listed)
        print(f"[{os.path.basename(os.path.dirname(root)) or root}] "
              f"icons={len(icons)} files={len(on_disk)} "
              f"missing={len(missing)} orphan={len(orphan)}")
        if missing:
            problems.append(t("files listed but missing on disk: {files}",
                              files=missing[:5]))
        if orphan:
            problems.append(t("files not in the manifest: {files}", files=orphan[:5]))
        sets.append(set(icons))
    if len(sets) > 1 and sets[0] != sets[1]:
        problems.append(t("icon sets differ between skills ({count} differences)",
                          count=len(sets[0] ^ sets[1])))
    if problems:
        print(t("\nProblems:"))
        for p in problems:
            print("  -", p)
        return 1
    print(t("\nConsistency check: no problems"))
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=t("Fetch the official cloud vendor icons"))
    p.add_argument("--vendor", action="append", choices=sorted(SOURCES),
                   help=t("Target vendor (default: all)"))
    p.add_argument("--dest", action="append",
                   help=t("Destination (default: the built-in destinations)"))
    p.add_argument("--dry-run", action="store_true",
                   help=t("Resolve URLs only, do not download"))
    p.add_argument("--verify", action="store_true",
                   help=t("Only check that fetched assets and the manifest are consistent"))
    p.add_argument("--zip-dir",
                   help=t("Directory holding pre-downloaded ZIPs (skips re-downloading)"))
    args = p.parse_args()

    vendors = args.vendor or sorted(SOURCES)
    dests = args.dest or DESTS
    if args.verify:
        return verify(dests)
    tmp = tempfile.mkdtemp(prefix="cloud-icons-")
    idx = Index()
    sources: dict[str, dict] = {}

    try:
        for vendor in vendors:
            print(f"[{vendor}]")
            if vendor == "gcp":
                packs = SOURCES["gcp"]["urls"]
            else:
                packs = [("main", resolve_zip_url(vendor))]
            for flavor, url in packs:
                print(f"  {flavor}: {url}")
                if args.dry_run:
                    continue
                cached = (os.path.join(args.zip_dir, f"{vendor}-{flavor}.zip")
                          if args.zip_dir else None)
                if cached and os.path.exists(cached):
                    blob = open(cached, "rb").read()
                else:
                    blob = fetch(url)
                    if cached:
                        os.makedirs(args.zip_dir, exist_ok=True)
                        open(cached, "wb").write(blob)
                root = os.path.join(tmp, f"{vendor}-{flavor}")
                with zipfile.ZipFile(io.BytesIO(blob)) as z:
                    z.extractall(root)
                sources[f"{vendor}:{flavor}"] = {
                    "url": url, "bytes": len(blob),
                    "package": os.path.basename(url),
                }
                if vendor == "aws":
                    collect_aws(root, idx)
                elif vendor == "azure":
                    collect_azure(root, idx)
                else:
                    collect_gcp(root, idx, flavor)
            n = sum(1 for k in idx.icons if k.startswith(vendor + ":"))
            print(t("  -> {count} icons", count=n))

        if args.dry_run:
            return 0

        for old, new in GCP_SUPERSEDED.items():
            if old in idx.icons and new in idx.icons:
                dropped = idx.icons.pop(old)
                for a in (dropped["name"], dropped["slug"], *dropped["aliases"]):
                    if a not in idx.icons[new]["aliases"]:
                        idx.icons[new]["aliases"].append(a)

        for key, extra in ALIAS_HINTS.items():
            if key in idx.icons:
                for a in extra:
                    if a not in idx.icons[key]["aliases"]:
                        idx.icons[key]["aliases"].append(a)
            elif key.split(":")[0] in vendors:
                print(t("  warn: ALIAS_HINTS entry '{key}' not found in the assets"
                        " (the service name may have changed)", key=key),
                      file=sys.stderr)

        stats = write_assets(idx, dests, sources, vendors)
        print(t("\nPlaced {count} icons in total ({png} with a PNG fallback)",
                count=stats["icons"], png=stats["png_fallback"]))
        print(t("Destination: {dest}", dest=dests[0]))
        for vendor in vendors:
            cats = sorted({m["category"] for k, m in idx.icons.items()
                           if k.startswith(vendor + ":")})
            print(t("  {vendor}: {count} categories", vendor=vendor, count=len(cats)))
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
