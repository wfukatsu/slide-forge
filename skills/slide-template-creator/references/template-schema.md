# Slide template schema

## Contents

- Registry
- Template record
- Slot types
- Slot references
- Density variants
- Example data

## Registry

`slide-templates/manifest.json` is the discovery source of truth.

```json
{
  "schemaVersion": 1,
  "templates": [{
    "id": "cohort-retention",
    "displayName": "コホート継続率",
    "pack": "marketing-analysis",
    "category": "customer",
    "path": "marketing-analysis/cohort-retention/template.json",
    "tags": ["cohort", "retention"],
    "status": "experimental",
    "version": 1
  }]
}
```

IDs, pack names, categories, and tags use lowercase ASCII words separated by
hyphens. Paths are relative to `slide-templates/`.

## Template record

Required keys:

| Key | Meaning |
|---|---|
| `schemaVersion` | currently `1` |
| `id`, `displayName`, `pack`, `category` | must match the manifest |
| `description` | one-sentence purpose |
| `slots` | semantic input contract |
| `slide` | one ordinary slide-forge slide object |

Recommended keys: `answers`, `inferenceLevel`, `compatibleLayouts`, `guardrails`,
and `example`. Templates using `$density` tokens additionally declare
`defaultDensity` and may declare `examples` (see Density variants).

`inferenceLevel` is one of `strategic`, `descriptive`, `diagnostic`,
`predictive`, or `causal`.

## Slot types

Supported types:

- `string`, `number`, `integer`, `boolean`
- `string[]`, `number[]`, `integer[]`
- nested forms such as `string[][]`
- `tuple` with `fields`, for a fixed-length mixed sequence
- `array` for structured tuples consumed by existing Canvas primitives

Constraints: `required`, `default`, `minLength`, `maxLength`, `minItems`,
`maxItems`, `minimum`, `maximum`, `items`, `fields`, `matchLength`.

`minItems` / `maxItems` bound the level they are declared on. The leaf
constraints — `minLength`, `maxLength`, `minimum`, `maximum` — cascade through
every array level down to the scalars, so `string[][]` with `maxLength: 20`
bounds each cell, not each row.

Prefer typed arrays. Use `array` only when a primitive intentionally accepts
mixed tuples such as `[label, x, y]` or `[seriesName, [values...]]`, and give it
an `items` spec so the elements are checked too — a bare `array` validates only
its length, which lets malformed data reach the drawing primitive.

`items` describes one element of an array-typed slot. It overrides the derived
element type but still inherits any leaf constraint it does not set itself, so a
row-length bound and a per-cell `maxLength` can coexist:

```json
{"type": "string[][]", "maxLength": 20,
 "items": {"type": "string[]", "minItems": 5, "maxItems": 5}}
```

## Row length

A table's rows must be as wide as its headers, and a grouped bar's series must
carry one value per category. The drawing primitives raise on a mismatch, but
that happens at deck-build time and only for whatever data was passed — so the
row width is checked at the slot level too, before anything is drawn.

**Derived automatically.** The validator reads the figures in `slide`. When a
`table` takes its `rows` from a slot, every row of that slot must match the
header count — read from a literal `headers` list, or from the referenced slot
when `headers` is itself a slot. Nothing needs to be declared, and editing the
literal `headers` list re-tightens the rule with no other edit:

```
slot rows[0]: has 3 columns but table.headers needs 5
```

Figures whose elements are deliberately variable — `funnel` and
`nested_circles` accept either `(label, value)` or a bare string — are excluded.

**Declared with `matchLength`.** Where the derivation cannot reach, tie one
list's length to another slot's:

```json
{"type": "number[]", "matchLength": "categories"}
```

`experiment-result` uses this for the values nested inside each `series` tuple,
which must stay as long as `categories`.

`tuple` validates a fixed-length sequence position by position:

```json
{"type": "array", "minItems": 2, "maxItems": 8,
 "items": {"type": "tuple", "fields": [
   {"type": "string", "maxLength": 24},
   {"type": "number", "minimum": 0, "maximum": 1},
   {"type": "number", "minimum": 0, "maximum": 1}]}}
```

## Slot references

Reference a slot with an exact object:

```json
{"$slot": "title"}
```

The renderer replaces exact slot objects recursively. It does not evaluate
expressions or interpolate strings. Put formatting in the Canvas primitive or
provide already-formatted display strings as a declared slot.

A `$slot` object must carry no sibling keys; `{"$slot": "title", "x": 1}` is an
error, not a slot reference.

Every declared slot must appear in `slide`, and every referenced slot must be
declared. An optional slot used by `slide` needs a `default`, otherwise nothing
can fill it. Extra input keys and unresolved references are errors.

## Density variants

A template can carry two densities in one file — `print` (dense, read-alone
handout) and `presentation` (sparse, projected) — with the inline token:

```json
{"$density": {"print": 9, "presentation": 11}}
```

The token is legal anywhere a *value* appears: slot constraint values
(`maxItems`, `maxLength`, …) and figure parameter values (`size`, `rowH`,
`h`, …) alike. The renderer resolves every token to the chosen branch before
any validation runs, so the resolved form is an ordinary template.

Rules:

- A token must carry exactly the keys `print` and `presentation`, and the
  `$density` object may have no sibling keys (mirroring `$slot` strictness).
- A branch value may only be a scalar or a flat array of scalars — never a
  `$slot` object, a figure object, or anything with a `type` key. Both
  densities share the identical figure skeleton and slot mapping; only sizes,
  coordinates, caps, and label text differ.
- Any template containing at least one token **must** declare a top-level
  `"defaultDensity": "print" | "presentation"` — the density used when the
  caller does not choose one, and the form the catalog shows. Declaring
  `defaultDensity` without tokens is an error.
- Density selection is a silent no-op on templates without tokens, so a deck
  build can pass the chosen density to every templated slide uniformly.

CLI: `render_slide_template.py --density print|presentation` picks the
variant; `validate_slide_templates.py` renders and audits **both** variants of
every template that declares them.

## Example data

Keep `example.json` beside `template.json`. It must fill every required slot and
remain within declared limits. For numeric examples, make `source` explicitly
say that the values are samples and must be replaced.

When one example cannot satisfy both densities' caps, declare a per-density
map next to `example` (keys must be densities; `example.json` stays the
default-density canonical form):

```json
"example": "example.json",
"examples": {"print": "example.json", "presentation": "example.presentation.json"}
```
