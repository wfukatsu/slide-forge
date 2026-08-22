# Scalar research policy

Use cached research first. Re-research only facts outside their stated
freshness window, facts directly requested by the user, or claims that affect
the current recommendation.

Product capability, edition, version, release status, and pricing come from the
OKF bundle (`okf-bundle.md`) before any web research — it is version-pinned and
carries the price list, which the public documentation does not. Research the
web only for what the bundle does not hold: company profile, news, published
case studies, customer results.

Before delegation, the main agent divides non-overlapping source scopes:

1. company/news;
2. product documentation/releases;
3. customer cases.

For a small update, use one researcher. Use multiple researchers only when at
least two scopes genuinely need fresh evidence. Give each researcher URLs or a
domain boundary and this return schema, not the full slide-generation skill:

```text
fact | effective/published date | source URL | target slide | unknowns
```

Prefer official Scalar sources and primary documentation. Search for changes
since the prior research date before rereading stable background material.
Mark unknowns explicitly; never infer a product capability, price, customer
result, or release status from adjacent evidence.
