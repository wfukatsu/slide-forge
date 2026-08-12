*[日本語](cloud-icons.ja.md)*
# Cloud Icons (AWS / Google Cloud / Azure)

Use the **1,757** official icons from the 3 vendors, kept in `assets/cloud-icons/`.
SVG is the source of truth; it's rasterized to the resolution needed at use time.

## First-time setup (one time only)

**Icons are not bundled in the repo.** Each vendor's assets are not licensed for
redistribution, so **each user pulls them into their own environment**.

```bash
# slide-forge のリポジトリルートへ移動
.venv/bin/python scripts/fetch_cloud_icons.py
```

1–2 minutes, about 8.6MB. Use `--verify` to check whether they've been fetched.
Using `cloud_icon` without fetching first stops with an error that walks you through this step.

**Do not commit the fetched assets** (already in `.gitignore`).

```
assets/cloud-icons/
  cloud-icons.json          マニフェスト（名前・別名・カテゴリ・種別・出典）
  aws/<category>/<slug>.svg     860 種
  gcp/<category>/<slug>.svg     251 種
  azure/<category>/<slug>.svg   646 種
cache/cloud-icons/          焼いた PNG（<vendor>-<slug>-<px>.png）
scripts/cloud_icons.py      検索 CLI と Canvas 用ミックスイン
```

Fetching and updating assets is handled by the google-slides skill's
`scripts/fetch_cloud_icons.py`, which does it **for both skills at once**
(to keep version management in one place).

## License (read this first)

All 3 vendors permit use only for "**architecture diagrams, training materials,
and documentation**." Rules to follow across all of them:

- **Don't change the color. Don't rotate it. Don't flip it. Don't change the aspect ratio.**
- **Place the product name next to the icon** (Azure explicitly recommends this; other
  vendors follow the same practice)
- Don't use another vendor's icon to represent your own product or service

`cloud_icon()` is **fixed to a square, with a label on by default**, and simply has
no arguments for color or rotation. The API shape itself prevents violations, so
don't work around it by calling `image()` yourself and processing the icon.

| Vendor | Terms |
|---|---|
| AWS | https://aws.amazon.com/trademark-guidelines/ |
| Azure | https://learn.microsoft.com/en-us/azure/architecture/icons/ |
| Google Cloud | https://cloud.google.com/icons |

## Choosing among the icon libraries

| | `illustrations.icon()` | `icons.asset_icon()` | This library |
|---|---|---|---|
| Subject | Generic concepts (server, key, cloud) | Scalar business vocabulary | **Real cloud services** |
| Network access | Not needed | Needed | Needed |
| Color | Theme color | Tinted to theme color | Vendor-specified color (**cannot be changed**) |

If a diagram needs to say "Amazon RDS," use this library; for a generic "database,"
use `illustrations.icon("database")`. Both can be mixed on the same slide.

## Finding a name

```bash
.venv/bin/python scripts/cloud_icons.py --search s3                 # 別名でも引ける
.venv/bin/python scripts/cloud_icons.py --search kubernetes         # 3 ベンダー横断
.venv/bin/python scripts/cloud_icons.py --list --vendor aws --category groups
.venv/bin/python scripts/cloud_icons.py --categories --vendor azure # カテゴリと件数
.venv/bin/python scripts/cloud_icons.py --sources                   # 取り込んだ版
```

Names can be specified as follows. **Ambiguous or misspelled names fail with an
error that suggests candidates**, so you catch it before generation.

| Form | Example |
|---|---|
| `<vendor>:<slug>` (unambiguous) | `aws:ec2` `gcp:bigquery` `azure:cosmos-db` |
| slug alone | `ec2` (fails if it matches multiple vendors) |
| Common name / alias | `s3` `eks` `aks` `gke` `vnet` `cosmos` |
| Display name | `Amazon Simple Storage Service` `Cloud SQL` |

There are 4 `kind` values, filterable with `--kind`.

| kind | Contents | Use |
|---|---|---|
| `service` | The service itself (e.g. Amazon EC2) | Normal choice |
| `resource` | Fine-grained parts within a service (e.g. EC2 instance types) | Detailed diagrams |
| `group` | Enclosures (AWS Cloud / Region / VPC / subnet) | Zone headings |
| `category` | Representative icon for a category | Section dividers, classification diagrams |

## Usage

Exposed as methods on `Canvas`. Coordinates are in inches, and **the return value is
the bottom y including the label** (the same convention as `illustrations` / `icons`).

| Method | What it does |
|---|---|
| `cloud_icon(name, x, y, size, label=…)` | Place a single icon |
| `cloud_icon_row(x, y, w, items)` | A horizontal row |
| `cloud_icon_flow(x, y, w, items)` | Connected with arrows |
| `cloud_icon_grid(x, y, w, items, cols=4)` | A grid |
| `cloud_zone(x, y, w, h, vendor=…, title=…)` | A dashed enclosure with a heading |

`items` is a name, or `(name, label)`. Omitting the label inserts the **official
service name**.

```python
d = Canvas(deck, ref["slideId"], template)
d.cloud_zone(0.45, 1.05, 9.1, 2.5, vendor="aws", title="AWS  ap-northeast-1")
d.cloud_zone(0.75, 1.5, 8.5, 1.85, title="VPC  10.0.0.0/16", color="#6B7280")
d.cloud_icon_row(1.0, 1.9, 8.0, [
    ("aws:elastic-load-balancing", "ALB"),
    ("aws:elastic-container-service", "ECS Fargate"),
    ("aws:rds", "RDS"), ("aws:simple-storage-service", "S3"),
], size=0.7)
```

From a deck spec (JSON), use these through the `type` field of `figures`. **Write
zones before their contents** (writing them after causes the rectangle to cover
the contents).

```json
"figures": [
  { "type": "cloud_zone", "x": 0.45, "y": 1.05, "w": 9.1, "h": 2.5,
    "vendor": "aws", "title": "AWS  ap-northeast-1" },
  { "type": "cloud_icon_row", "x": 1.0, "y": 1.9, "w": 8.0, "size": 0.7,
    "items": [["aws:rds", "RDS"], ["aws:simple-storage-service", "S3"]] }
]
```

Working examples:

- `examples/cloud-architecture.json` — zones, multi-cloud, data flow (spec JSON)
- `examples/scalardb-architecture.py` — **architecture diagram with layers joined by
  arrows** (uses `Canvas` directly)
- `examples/scalardl-architecture.py` — architecture diagram mixing 3 icon families
  (official cloud icons + Scalar brand assets + shape-based pictograms)

### Write arrow-connected architecture diagrams in Python

`figures` has no type for drawing lines. Diagrams that **connect layer to layer**,
such as app layer → ScalarDB → database layer, should **use `Canvas` directly**
(`examples/scalardb-architecture.py`). Cloud icons, pictograms, brand logos, and
connectors can all be mixed into one drawing.

```python
d.cloud_zone(0.9, 3.55, 1.95, 1.5, vendor="aws")
d.cloud_icon("aws:dynamodb", 1.62, 3.89, 0.5, label="DynamoDB")
d.arrow(1.87, 3.23, 1.87, 3.51, color=d.P.muted, _anchored=True)
```

### Icons for in-house products / OSS need a different source

Vendor icon sets **only contain that vendor's own services**. For the following,
use a different method.

| What to draw | How |
|---|---|
| ScalarDB / ScalarDL | Paste `assets/scalar/product-logos/*.png` with `image()` |
| Evidence chain, tamper detection, timestamping | `asset_icon("evidence-chain")` etc. (`references/icons.md`) |
| Scalar logo | `assets/scalar/logos/*.png`, or `asset_icon("scalar-logo")` |
| Self-managed PostgreSQL / MySQL / Cassandra | `illustrations.icon("database")` `icon("stack")` (not in vendor sets, for trademark reasons) |
| Managed DB engines | Official icons exist (`aws:aurora-postgresql-instance` / `azure:database-mysql-server` / `azure:managed-instance-apache-cassandra`, etc.) |

`VENDOR_COLOR` / `VENDOR_LABEL` hold each vendor's brand color (AWS #FF9900 /
GCP #4285F4 / Azure #0078D4) and display name. **Use these colors only for
borders and headings** — never apply them to the icons themselves.

### Behavior under `--dry-run`

Like `asset_icon`, this **substitutes a rectangle of the same size** and checks
only the coordinates. Icon-name typos also surface here, so always run this
before generating.

```bash
.venv/bin/python scripts/build_deck.py --template templates/scalar-2026.json \
    --spec deck.json --dry-run
```

## Updating the assets

The fetch script lives in the shared engine, at `scripts/fetch_cloud_icons.py`.

```bash
# slide-forge のリポジトリルートで実行
.venv/bin/python scripts/fetch_cloud_icons.py           # 全ベンダー
.venv/bin/python scripts/fetch_cloud_icons.py --vendor azure
.venv/bin/python scripts/fetch_cloud_icons.py --dry-run # URL 確認のみ
```

- Distribution URLs are **resolved from each vendor's page** (AWS updates quarterly;
  Azure's version bumps, e.g. V21 → V24). If a page's structure changes and
  scraping breaks, the script stops with an error — fix the regex in `SOURCES`.
- During fetch, every SVG is test-rendered; only the ones that fail to render fall
  back to the vendor-bundled PNG alongside it.
- For GCP, layers are stacked in the order core (current design) > category >
  legacy (2021). Many services exist only in legacy, so all three are fetched.

## Constraints

- **Network access is required.** Slides can only ingest images from a URL, so
  uploads go through Drive. Using the same icon multiple times still uploads only
  once (cached per path).
- A name with no matching asset raises `CloudIconError`. **It never silently
  falls back to a text badge** (the old implementation did that, which caused
  "the icon doesn't show up" incidents).
- Azure has a handful of icons that **aren't square**. `render()` fits the long
  edge to the requested pixel size and **always preserves the aspect ratio**
  (specifying both width and height would stretch the icon, violating the
  "don't distort" rule). Placing one in a square frame leaves margin on either
  the top/bottom or the left/right.
