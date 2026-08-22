*[日本語](enterprise.ja.md)*
# Composing Enterprise-Buyer Pages

The pages that answer the questions a purchase runs into once the technology
has been accepted: is it safe, does it fit what we already run, who answers
when it breaks, and what does it cost. Each entry says what the page has to
establish and what to build it from today.

## Security and compliance

Which certifications the product holds and which controls it provides — stated
so a security reviewer can check them, not so a sponsor can feel reassured.

**Build it with**: the `table` figure (control, how it is met, evidence), or
`claim-evidence-table` when each claim needs its source next to it. `icon_grid`
with `lock` / `shield` / `key` works as a summary page, never as the answer.

Name the certification, its scope, and its date. "Enterprise-grade security" is
not a claim anyone can verify, and a reviewer will read its presence as an
absence of the specific ones.

## Ecosystem and integrations

What the product already works with, so a reader can locate it inside the
stack they already run.

**Build it with**: `hub` for one centre and its integrations, `icon_grid` or
`cloud_icon_grid` for a named-technology grid ([cloud-icons.md](../cloud-icons.md)),
`layers` when the point is where the product sits in a stack.

Separate what is supported from what is possible. A logo grid that mixes the
two is the reason integration questions come back later.

## Support and SLA

What is committed, at which tier, and what happens when it is missed.

**Build it with**: `comparison` for tier against tier, or the `table` figure
when there are many rows. `dense-comparison-table` when the criteria run long.

Response time and resolution time are different commitments; a page that gives
one and lets the reader assume the other is the source of the argument later.

## Pricing

What it costs, on what basis it is counted, and what is excluded.

**Build it with**: `license-estimate` for a worked estimate,
`license-pattern-compare` for licence patterns side by side, `cost-structure`
for the investment breakdown, `scenario-comparison` for pessimistic / standard
/ optimistic.

Two things belong on the page and are routinely left off: the unit the price is
counted in, and what is *not* included. Both are what the reader will ask
first.

**List prices come from an internal source and are a reference estimate, not a
quote.** Anything binding goes through the quoting process, and this repository
is public — no non-public pricing goes into a committed file.
