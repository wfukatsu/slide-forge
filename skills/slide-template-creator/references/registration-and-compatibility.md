# Registration and compatibility

## Status

- `experimental`: slot names and composition may change.
- `stable`: preserve input compatibility.
- `deprecated`: retain the entry and point users to a replacement.

For a stable template, removing a slot, changing its type, or changing its
meaning requires a version increment. Adding an optional slot or correcting
visual spacing does not.

## Portable templates

Portable templates:

- use standard roles, preferably `BLANK`;
- draw titles with `governing_message`;
- use Canvas semantic palette tokens;
- avoid master object IDs and explicit brand RGB colors;
- validate against `blank-16x9` and at least one registered master before
  promotion to stable.

## Master-specific templates

Record compatible template IDs and layout roles. Keep these out of generic
catalogs unless the selected master matches. Re-run their catalog QA whenever
the referenced master changes.

## Registry changes

Update `slide-templates/manifest.json` atomically with the template directory.
Run the full validator after every registry change:

```bash
.venv/bin/python scripts/validate_slide_templates.py
```

Do not delete deprecated templates in the same change that introduces the
replacement.
