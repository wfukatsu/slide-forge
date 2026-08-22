*[日本語](okf-bundle.ja.md)*

# OKF bundle — the first-line source for Scalar product facts and prices

`OKF-ScalarDB-ScalarDL` is an [OKF v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
bundle of the ScalarDB / ScalarDL official documentation (developers.scalar-labs.com),
split per product and per version, plus a hand-written `pricing/` section that
does **not** exist upstream.

**When building a Scalar proposal, read this bundle before you write a product
claim, an edition boundary, or a price.** It replaces guessing and replaces a
web search for anything it already covers.

Repository: <https://github.com/wfukatsu/OKF-ScalarDB-ScalarDL>

## Where to find it

Resolve in this order and use the first hit:

| # | Location | Note |
|---|---|---|
| 1 | `/Users/wfukatsu/work/OKF-ScalarDB-ScalarDL/okf/` | Local clone (fastest; `git pull` before relying on it) |
| 2 | `/Users/wfukatsu/work/nexus-architect/knowledge/okf-scalardb-scalardl/okf/` | Submodule pinned by nexus-architect |
| 3 | `https://github.com/wfukatsu/OKF-ScalarDB-ScalarDL` | Fetch the raw file when no clone exists |

slide-forge does not vendor the bundle. If none of the three resolve, say so and
fall back to `research-2026-08.md` — do not invent the fact.

## What it covers

| Need | File |
|---|---|
| How to read the bundle (the hard rules) | `okf/guides/how-ai-agents-use-this-bundle.md` |
| Which product / edition / version to cite | `okf/guides/product-and-version-selection.md` |
| Product facts for a given version | `okf/products/<product>/<version>/index.md`, then the concept pages under it |
| Billing models overview (3 models) | `okf/pricing/index.md` |
| ScalarDB EE Standard / Premium list prices | `okf/pricing/scalardb-pricing.md` |
| ScalarDL Ledger / Auditor list prices | `okf/pricing/scalardl-pricing.md` |
| ScalarDB Analytics SDBU metering | `okf/pricing/scalardb-analytics-pricing.md` |
| 1 Pod = 2vCPU / 4GB, and how Pods are counted per contract term | `okf/pricing/licensing-units.md` |
| What each edition includes (feature / component matrix) | `okf/pricing/edition-feature-matrix.md` |
| Five worked sample quotations + a quote checklist | `okf/pricing/sample-quotations.md` |

Products covered: ScalarDB (3.14–3.19), ScalarDL (3.10–3.14), ScalarDB Saga
(3.19, pre-GA), ScalarDB Community (3.4–3.13).

## Rules when citing it

These come from `okf/guides/how-ai-agents-use-this-bundle.md`; reproduce them,
do not soften them.

1. **Do not answer across versions.** Pick one `products/<product>/<version>/`
   and cite only from under it. Config keys, error codes, and API signatures
   change between minor versions. Name the version on the slide.
2. **Check the edition.** Each concept's frontmatter carries `editions`. Never
   propose an Enterprise-only capability to a Community-premised project, and
   never state a capability without its edition.
3. **State preview status.** `feature_status: [Private Preview | Public Preview]`
   and `status: draft` / `prerelease: true` (currently ScalarDB Saga 3.19 =
   `3.19.0-alpha.1`) must be labelled as not GA on any slide that mentions them.
4. **Do not infer.** If the bundle has no basis for a claim, say "not documented"
   and give the `resource` URL for confirmation. This is the same rule as
   `research-policy.md`: never infer a capability, price, customer result, or
   release status from adjacent evidence.
5. **`status: deprecated` concepts are for investigating existing systems only** —
   never a basis for a design decision in a proposal.

## Rules when citing prices

`okf/pricing/` is the one section with no upstream source: it was written from
Scalar's price list (ScalarDB / ScalarDL 2024-07-01, ScalarDB Analytics
2024-09-10). **The bundle repository is public, so everything it carries is
published information and may be cited** — including the list prices. The
boundary is not "internal vs external"; it is what the bundle chose to publish
versus what it deliberately withheld.

- **Published, citable**: the SDBU-hour rate for ScalarDB Analytics, and the
  monthly and annual list prices of the four Pod-subscription products, plus the
  billing models, Pod-counting rules, and edition contents.
- **Withheld, not citable**: 3-year list prices, prepaid credit prices, discount
  rates, and customer-specific terms are all marked 非公開 and are absent on
  purpose. When a proposal needs one, say it is not public and route to the
  account executive — never interpolate it from the monthly/annual figures.
- Every figure is a **list price, tax-excluded, JPY**. Cite it as a list price
  and as **material for a reference estimate** — not as a confirmed or
  submittable amount. Actual terms adjust by volume and contract, so a quote
  that goes to the customer is reviewed by the account executive first.
- **Unit prices for an actual quotation still come from the quotation master**
  (`scalar-quotation` → `/Users/wfukatsu/work/price-master/data/scalar-pricing.json`),
  which is the single source of truth for numbers that land in a 見積書. Use the
  bundle to cross-check that master, and to source what the master does not carry:
  edition contents, Pod-counting rules, and the sample-quotation checklist.

## Division of labour with other references

| Fact | Source |
|---|---|
| Product capability, edition, config, version, release status | **This bundle** |
| List prices, billing models, Pod counting, edition contents | **This bundle** (`pricing/`) |
| Unit prices that appear in a 見積書 | `scalar-quotation` price master |
| Company profile, news, published case studies, quantitative customer results | `research-2026-08.md` (the bundle carries none of these) |
| Sales phases, gates, material types | `sales-playbook.md` |
