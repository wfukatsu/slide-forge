---
name: scalar-proposal-slides
description: >-
  Builds customer-specific Scalar solution-proposal decks in Google Slides —
  starting from the customer's challenges (hearing notes, meeting minutes) and
  mapping them to ScalarDB / ScalarDL, following the problem-solving proposal
  structure (exec summary → challenge agreement → solution → effects → PoC plan
  → costs → risks → next steps). A Scalar-specific workflow layered on top of
  google-slides-template (scalar-2026 template) alongside scalar-product-slides.
  Triggers: "提案書を作って", "提案スライド", "顧客課題", "ソリューション提案",
  "〈顧客名〉向けの提案資料", "scalar-proposal-slides", "ScalarDB/ScalarDL の提案資料".
  Out of scope: product/company introduction decks with no specific customer
  (use scalar-product-slides), non-Scalar proposals (google-slides-template),
  and from-scratch PPTX authoring (document-skills:pptx; exporting the
  generated proposal to .pptx is pptx-export).
---

*[日本語](SKILL.ja.md)*

# Scalar Solution Proposal Slides

Use `references/scalar/workflow-contract.md` for shared sales-material rules
and `references/scalar/research-policy.md` for freshness/research. This skill
owns only proposal-specific decisions and generation.

Working directory: the slide-forge root — `${CLAUDE_PLUGIN_ROOT}` when running
from an installed plugin, `/path/to/slide-forge` on a local clone
(literal `cd` paths below assume the local clone).

## Important

- **Prerequisite skill**: `google-slides-template` (same repo) — auth, the
  shared venv, the `scalar-2026` template, drawing API, and QA tooling. This
  skill owns only what is proposal-specific: the hearing checklist, the
  challenge→product mapping, and the proposal deck structure.
- **The customer's challenges drive everything.** A proposal without agreed
  challenges is a product intro — route it to `scalar-product-slides`. Collect
  hearing material (minutes, notes, RFP) before designing slides; what is not
  known must surface as "to confirm today" on the deck, never as a guess.
- **Never fabricate customer-specific numbers.** Quantified effects need a
  calculation basis from the hearing; otherwise write qualitative effects and
  route quantification to the PoC ("measure it during the PoC and use it as
  material for internal approval"). Public case numbers (ENS approx. 1/5, etc.)
  are usable with sources.
- **Every initial proposal includes an architecture diagram and a BOM.** The
  standard topology is 3 environments — development (local) / test
  (aidd-infra-test) / staging (aidd-infra-staging) — on **AWS by default**
  (rebuild the same role split on GCP/Azure only if the customer specifies).
  After composing the architecture, output the cloud-service list and the
  Scalar product list with quantities (and monthly license cost when
  quantities are not specified) — on the deck AND as a list in the final
  report (proposal-map.md §6).
- **Check the constraints before proposing** —
  `references/scalar/proposal-map.md` §4 (cases where ScalarDB/DL does not
  fit). Do not force a challenge onto a Scalar product; saying so is part of
  proposal quality.
- **Research freshness**: facts come from `references/scalar/research-2026-08.md`
  and `references/scalar/proposal-map.md` (§3/§5 dated 2026-08-05). Both follow
  the **3-month rule** — refresh only affected claims using
  `references/scalar/research-policy.md`; parallel research is not automatic.

## Quick Reference

| Task | Use |
|------|-----|
| Hearing checklist / proposal structure / challenge→product map / constraints / pricing / standard environments + BOM | `references/scalar/proposal-map.md` |
| Proposal deck builder (worked example, 23 slides incl. architecture + BOM) | `scripts/scalar/build_scalar_proposal.py` |
| Environment diagram source (3 environments, AWS) | `examples/scalar-proposal-envs.drawio` → PNG via `scripts/drawio_export.py` |
| Researched company/product facts + pitfalls | `references/scalar/research-2026-08.md` |
| Section ordering rationale (problem-solving outline) | `references/deck-outlines.md` |
| Run | `cd /path/to/slide-forge && .venv/bin/python scripts/scalar/build_scalar_proposal.py [--folder <Drive URL>]` |
| Validate first (no API calls) | same command with `--dry-run` — runs the coordinate and text-fit audits without creating a deck |

## Phase 1: Collect the challenges and settle premises

Follow `references/interactive-intake.md` sections 0/3/4/5. Ask in one batch:

| # | header | Question | Options |
|---|---|---|---|
| 1 | Challenge material | Do you have material on the customer's challenges? | Provide minutes/hearing notes (file/paste) / Explain verbally now / Not yet (start from presenting the hearing checklist) |
| 2 | Challenge category | Which category are the main challenges closest to? | 3 likely categories from proposal-map.md §3's A–H based on the material + Other (multiple selection allowed) |
| 3 | Proposal stage | What stage is this proposal at? | Initial proposal (mainly to agree on challenges) / PoC proposal (through scope and success criteria) / Full-rollout proposal (cost and team at a fixed level of detail) |
| 4 | Decision maker | Who is the main reader? | Executive / decision maker / IT department / Business department / Mixed |

- Material first: if minutes/notes exist, **read them before asking Q2** and
  pre-select the likely categories in the option descriptions.
- If nothing is known yet, present the hearing checklist
  (proposal-map.md §1) as the deliverable instead of forcing a deck.
- Second round if unspecified: output Drive folder, cover date, language, and
  cloud (default AWS — state the adopted default instead of asking when the
  customer's cloud is unknown). The shared contract owns the QA question.
- **Do not ask about** diagram composition, coordinates, colors, or which
  part draws which section — that is fixed by the worked example and
  design conventions.

Then **present the slide outline (page count + each slide's action title,
challenge→product mapping made explicit) and get approval before generating**
(the outline gate of interactive-intake.md §3).

## Phase 2: Map challenges to products

1. Classify each agreed challenge into proposal-map.md §3 categories (A–H);
   pull the product/feature line and the public cases from the same row.
2. Check §4 (unsuitable cases) — direct-write bypass, DB-specific features,
   OLAP-only workloads, "tamper prevention" wording, Community-edition gaps.
   Surface any hit as a risk-slide item or descope it honestly.
3. Verify freshness (3-month rule) of §3/§5 and research-2026-08.md; re-run
   research agents if stale, and check the pitfall list at the end of
   research-2026-08.md before writing slides.

## Phase 2.5: Compose the architecture and BOM

1. Start from the standard 3-environment topology (proposal-map.md §6):
   development (local, Community edition, free) → test aidd-infra-test
   (Cluster, 1 Pod) → staging aidd-infra-staging (Cluster, 3 Pods), AWS by
   default. Adjust environment names, sizes, and the production environment
   to the hearing.
2. Author the diagram from `examples/scalar-proposal-envs.drawio` (edit →
   `scripts/drawio_export.py` → Read the PNG; drawio-diagrams skill rules
   apply: verified shape names only, visual check mandatory).
3. Derive the BOM: per environment, the cloud services and the Scalar
   products with quantities; compute monthly license cost with the §6 formula
   when quantities are not customer-specified. Premium features or ScalarDL
   change the unit prices (§5/§6).
4. **When the customer needs an editable estimate** (itemized quotation) —
   typical for full-rollout proposals, or when the user asks — build it from the BOM with
   the `spreadsheets` skill (Excel / Google Spreadsheet, real formulas for
   quantities × unit prices and tax) into the deck's Drive folder. The cost
   slide keeps the summary; the spreadsheet carries the line items, and the
   two totals must match.

## Phase 3: Build the deck

`scripts/scalar/build_scalar_proposal.py` is a worked example (fictional
manufacturing scenario, 23 slides incl. architecture + BOM) that encodes the
standard structure —
proposal-map.md §2 has the section-by-section rationale. To build a real
proposal, rewrite only the `PROPOSAL` dict at the top of the script
(customer, summary, challenges, mapping, alternatives, effects, cases,
journey, gantt, team, costs, risks, next) with hearing results, keeping:

- Challenge slides ≤ 3 items, same order and wording as the mapping table
- The alternatives table's comparison axes rewritten to the customer's actual
  KBF (what they will evaluate proposals on)
- Cases picked from the mapped categories (§3), with sources in speaker notes
- Cost figures only from §5 with `source_note`; anything else stays
  "quote available on request"
- Dense architecture diagrams (10+ nodes, cloud-specific) → author with the
  `drawio-diagrams` skill and insert as an image instead of the built-in
  solution diagram

Design conventions are shared with scalar-product-slides: action titles,
square corners on accent-bar cards, pictograms from `illustrations`.

## Phase 4: Generate and QA

```bash
cd /path/to/slide-forge
.venv/bin/python scripts/scalar/build_scalar_proposal.py --dry-run   # audits only, no API
.venv/bin/python scripts/scalar/build_scalar_proposal.py [--folder <URL>]
```

1. The script prints "audit:" lines from `audit_*` on every drawn slide.
   **If any audit fires, fix the data/spec and rebuild** (delete the old deck
   from Drive first; rebuilding changes the URL — tell the user).
2. Apply the shared contract's QA and cleanup procedure.
3. Content QA specific to proposals: no customer-specific number without a
   hearing basis, no case/price without a source note, challenge wording
   consistent across slides 3 / 7 (challenge summary and mapping table), scope-out line present.
4. In the final report, alongside the deck/folder URLs, include the BOM
   lists (cloud services per environment; Scalar products with quantity and
   monthly cost) — the builder prints them as `=== Bill of Materials (BOM) ===`.
5. Use the shared contract's final-adjustment step, adding proposal-specific
   choices for swapping cases or adding/removing sections.

## File layout

| Path | Role |
|------|------|
| `scripts/scalar/build_scalar_proposal.py` | Proposal deck builder (worked example; rewrite `PROPOSAL` per customer) |
| `references/scalar/proposal-map.md` | Hearing items, proposal structure + rationale, challenge→product map, constraints, pricing |
| `references/scalar/research-2026-08.md` | Company/product facts, cases, slide pitfalls (shared with scalar-product-slides) |
| `examples/scalar-proposal-envs.drawio` / `.png` | 3-environment architecture diagram source and export (rewrite per customer) |
| `templates/scalar-2026.json` | Scalar 2026 template |
