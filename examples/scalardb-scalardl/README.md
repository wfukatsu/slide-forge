*[日本語](README.ja.md)*

# Example: ScalarDB / ScalarDL Product Feature Walkthrough

A 55-slide deck (46 of which are diagrams). A reference example of a structure that covers the features documented in the public docs, one feature per page.

```bash
# Coordinate inspection (does not call the API)
../../.venv/bin/python ../../scripts/validate_layout.py deck.py

# List the composition
../../.venv/bin/python ../../scripts/render_deck.py deck.py --dry-run

# Generate
../../.venv/bin/python ../../scripts/render_deck.py deck.py

# Generating with your own company master
SLIDE_FORGE_TEMPLATE=../../templates/my-brand.json \
    ../../.venv/bin/python ../../scripts/render_deck.py deck.py
```

## Composition

| Section | Slides | Content |
|---|---|---|
| 1. Overview | 3 | Problem statement, 3-layer architecture, edition feature matrix |
| 2. Core | 12 | Transaction protocol, isolation levels, recovery, optimization, data model, API |
| 3. Cluster | 14 | Clustering, various interfaces, authentication/authorization, encryption, replication, AI integration |
| 4. Analytics | 4 | Architecture, data catalog, query execution, authorization |
| 5. Operations | 5 | Data migration, backup, monitoring, K8s deployment, performance evaluation |
| 6. ScalarDL | 6 | Tamper detection, hash chain, signatures, mutual verification, HashStore, TableStore |
| 7. Summary | 2 | How to choose between them, how to proceed |

## Highlights

As a reference for how to write deck modules, the following slides are worth reviewing.

| Function | Diagram pattern |
|---|---|
| `s_problem` | Before/After two-panel comparison (two `zone`s + a bold center arrow + circle/cross marks) |
| `s_arch3` | Hand-drawn layered diagram (varying shade per layer) |
| `s_editions` | Color-coding ●/○/− using `grid`'s `cell_colors` |
| `s_cc_phases` | Swimlanes, with cross-lane arrows connected via real coordinates |
| `s_recovery` | Conditional branching (`DIAMOND` + Yes/No + two outcomes) |
| `s_optim` | Before/After bands + `Canvas.cards` + visualization of counts |
| `s_adapters` | A configuration diagram radiating from a core to 3 groups |
| `s_exceptions` | Branching into 3 categories (each category assigned a color) |
| `s_oidc` | Sequence (lanes + numbered arrows) + a 4-stage verification flow |
| `s_replication` | 3-site configuration diagram (`db` cylinders + inter-site data flow) |
| `s_vector` | Highlighting only part of a pipeline as your own company's domain |
| `s_backup` | Timeline (markers + duration bands + recovery points) |
| `s_catalog` | Hierarchical tree (indentation + elbow connectors) |
| `s_asset` | Hash chain (cross marks at the tampered location) |
| `s_next` | Two columns of steps + an elbow connection through the gap between columns |

## Notes

- **No performance numbers are included.** Since the public documentation has no measured
  values, the benchmark pages are structured to illustrate "the variables you should change
  when measuring," encouraging readers to measure in their own environment.
  Do not chart numbers that lack a source.
- The content is based on the public documentation as of ScalarDB 3.18 / ScalarDL 3.13.
  Feature availability (GA / Private Preview) and editions change with each release,
  so if you reuse this content, verify it against the target version.
- The cover slide is composed of only TITLE and SUBTITLE. Cover layouts with a BODY
  placeholder are limited, so this approach is used for portability.
