# Primitive selection

## Prefer existing parts

| Need | Primitive |
|---|---|
| Exact comparison | `table` |
| Category magnitude | `vbars` / `hbars` |
| Multiple series | `vbars_grouped` |
| Trend | `linechart` |
| Composition | `pie` / `vbars_stacked` |
| One headline number | `metric` |
| 2×2 classification | `matrix` |
| Competitive position | `posmap` |
| Funnel | `funnel` |
| Market sizing | `nested_circles` |
| Three-way overlap | `venn` |
| Sequence | `flow`, `steps`, `journey`, `timeline` |
| Insight and source | `so_what`, `source_note` |

Search method signatures in `scripts/*.py` and working JSON examples in
`examples/` before designing a new primitive.

## Add a primitive only when

- equivalent low-level shapes recur across templates;
- domain arrays need deterministic validation;
- at least two templates can reuse the function; and
- the function has a stable, independent input contract.

Put general business frameworks in `patterns.py`, charts in `charts.py`, page
scaffolding in `pages.py`, and domain-specific families in a separate mixin.
Register JSON-facing methods in `scripts/build_deck.py::FIGURES` and document
them in the corresponding repository reference.
