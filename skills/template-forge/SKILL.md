---
name: template-forge
description: >-
  Create and register a brand-new Google Slides master from a design spec — brand
  colors, fonts, logo, footer — without touching the Slides UI, registered as
  templates/<id>.json and ready for google-slides-template to generate against.
  Design input comes from interactive brand tokens, extraction from existing
  material (site / logo / deck), or a bundled preset.
  Use for: 新しいテンプレートを作って, ブランドに合わせたマスターを作成,
  会社カラーのテンプレート, create a new master.
  Not: hand-tuning an existing master's design (Slides UI); PPTX/.potx templates
  (document-skills:pptx); generating decks from a template
  (google-slides-template).
---

*[日本語](SKILL.ja.md)*

# Template Forge — Create a New Slide Template (Master)

## Important

- **The Slides API cannot create or rename masters/layouts**
  (`references/api-notes.md` §1). This skill therefore *derives*: it copies a
  base and restyles the base's existing layout pages. Unused base layouts
  remain in the file — unregistered and harmless. Role names live only in
  `templates/<id>.json`'s alias table.
- **The base's colorScheme is immutable** — every color is written as
  explicit RGB. The Slides UI color picker will still show the base's theme
  palette; that is expected (same as `templates/corporate.json`).
- **Run every command from the slide-forge root as cwd** — `${CLAUDE_PLUGIN_ROOT}`
  when running from an installed plugin, `/path/to/slide-forge` on a
  local clone. Auth and the venv are shared at the repo root (`config/`, `.venv`).
- **Never hand the template over without visual verification.** Role
  assignment is deterministic, but band/placeholder overlap, font rendering,
  and contrast are judged only by eye: always run the layout catalog + the
  `slide-qa` skill (Phase 5) before reporting done.
- **Fixes happen in the design spec.** On any defect, edit the spec and
  rebuild with `--replace` (deletes the superseded master from Drive after a
  successful rebuild). Never patch the generated master in the Slides UI —
  that forks it from the spec.
- **Fonts must exist in the Slides font menu** (Google Fonts). Unknown names
  fall back silently. Known-safe: Noto Sans JP, Noto Serif JP, M PLUS 1p,
  Zen Maru Gothic, BIZ UDPGothic (Japanese); Montserrat, Roboto, Open Sans,
  Lato, Source Sans Pro (Latin). Anything else: verify in the catalog deck.

## Quick Reference

| Task | Command |
|------|---------|
| Validate the design spec (offline, free) | `.venv/bin/python scripts/build_template.py --spec design.json --dry-run` |
| Build + auto-register | `.venv/bin/python scripts/build_template.py --spec design.json [--folder <URL/ID>]` |
| Rebuild after spec fixes (URL of json stays, old master deleted) | add `--replace` |
| Derive from a registered template instead of blank | `--base <template-id>` (or `"base"` in the spec) |
| Layout catalog for visual check | `.venv/bin/python scripts/layout_sample.py --template templates/<id>.json` |
| Presets (complete specs minus name/logo/footer) | `templates/presets/{navy-consulting,tech-dark,warm-minimal}.json` |

## Design-spec format

```jsonc
{
  "name": "acme-2026",                    // [a-z0-9-], becomes templates/<name>.json
  "displayName": "ACME Master Template",
  "base": "blank",                        // "blank" (Google default) | template id | Slides URL/ID
  "brand": {
    "colors": {                           // all #RRGGBB, all 9 required
      "primary": "#0B3D91", "primaryDark": "#062A66", "accent": "#F59E0B",
      "background": "#FFFFFF", "backgroundAlt": "#F5F7FA",
      "textTitle": "#0B1F3A", "textBody": "#1F2937",
      "textMuted": "#666666", "textOnDark": "#FFFFFF"
    },
    "fonts": { "heading": "Montserrat", "body": "Noto Sans JP" },
    "logo": { "source": "assets/acme.png", "onDark": "assets/acme-white.png" },  // optional
    "footer": { "text": "© 2026 ACME Inc.", "fontSize": 7 }                      // optional
  },
  "style": {
    "coverStyle": "band-bottom",          // band-bottom | band-left | minimal
    "sectionStyle": "dark",               // dark (primary bg) | rule (light bg + accent rule)
    "pageNumbers": true
  },
  "derive": {                             // only when base is a registered template
    "colorMap": { "#1E3A5F": "primary" }, // base's explicit RGB -> semantic token
    "deleteObjects": ["<objectId>"]       // brand elements to remove from the base
  }
}
```

Standard 6 roles are always produced: COVER / SECTION / CONTENT /
TITLE_ONLY / BLANK / CLOSING (on a blank base, CLOSING restyles the
MAIN_POINT layout).

## Workflow

### Phase 1: Intake (AskUserQuestion, interactive-intake.md manners)

Batch into one round; skip anything already specified:

| # | header | question | options |
|---|---|---|---|
| 1 | Design input | What should the design be based on? | Specify interactively (ask for colors/fonts) / Extract from existing material (site URL, logo, existing deck) / Preset (present 3 options with a one-line palette description each) |
| 2 | Base | Which master should this be based on? | blank — Google's default (recommended, default) / derive from a registered template via `list_templates.py` |
| 3 | Logo | Is there a logo image? | Yes (get the path; also get a version for dark backgrounds if one exists) / No (text only) |
| 4 | Footer | What should the footer say? | Include a © notice (get the text) / Omit it |

Template name (`[a-z0-9-]`) is derived from the brand/company name; confirm
it in the outline, not as a separate question.

### Phase 2: Author the design spec

- **Interactive**: put the answers into the schema above. Check contrast as
  you go: textBody on background and textOnDark on primary must be ≥ 4.5:1
  (`colors.py` has helpers; eyeball via the catalog otherwise).
- **Extraction is agent judgment, not code**: for a site URL, WebFetch it and
  read the brand colors from CSS variables / the logo; for a logo file, Read
  the image and pick the dominant color (primary) plus a supporting accent;
  for an existing deck, run `inspect_template.py <URL>` and lift its color
  report. Merge onto the closest preset skeleton.
- **Preset**: copy `templates/presets/<preset>.json`, fill `name` /
  `displayName` / `logo` / `footer.text`.
- Present the palette (hex + role), fonts, and style choices in one summary
  block and get approval before building.

### Phase 3: Offline validation

```bash
.venv/bin/python scripts/build_template.py --spec out/<name>-design.json --dry-run
```

Fix any errors (missing colors, bad hex, missing logo file, unknown enums).

### Phase 4: Build and register

```bash
.venv/bin/python scripts/drive_folder.py create "<displayName>"   # Drive folder rule
.venv/bin/python scripts/build_template.py --spec out/<name>-design.json --folder <FOLDER_ID>
```

This creates the styled master, registers `templates/<name>.json` with
deterministic roles + provenance (`derivedFrom`, dated notes), injects
page-number geometry, and prints the next steps. Upload the design spec to
the same folder (`drive_folder.py upload <FOLDER> out/<name>-design.json`).

### Phase 5: Catalog and visual QA (not optional)

```bash
.venv/bin/python scripts/layout_sample.py --template templates/<name>.json --folder <FOLDER_ID>
```

Then run the **slide-qa** skill on the catalog deck. Template-specific
checklist on top of the standard one:

- [ ] Bands/bars do not overlap any placeholder text
- [ ] Cover: title/subtitle legible, logo not stretched (aspect preserved)
- [ ] Section: title contrast on its background ≥ 4.5:1; accent rule sits under the title
- [ ] Content: body text is the body font (a silent font fallback means the name was wrong)
- [ ] Footer + page number both visible, not doubled, not clipped
- [ ] Closing: text and onDark logo legible on the dark background

### Phase 6: Fix loop

Edit the design spec → `--dry-run` → rebuild with `--replace` (the old
master is deleted from Drive after success; `templates/<name>.json` is
overwritten in place) → re-run Phase 5 on the affected layouts. Delete
superseded catalog decks from Drive.

### Phase 7: Report and hand off

Report: master URL, catalog deck URL, Drive folder URL, `templates/<name>.json`
path, and the palette summary. State that decks are generated with the
**google-slides-template** skill: the new id now appears in
`list_templates.py` and works with `build_deck.py --template templates/<name>.json`.
Run `cleanup_qa.py` for local thumbnails. If the logo could not be inserted
(org sharing policy), say so and point at the Slides UI for manual placement.

## Limitations (state them when relevant)

- Layout set is fixed to the base's — no adding, deleting, or renaming
  layouts. Need more layout variety? Derive from a richer registered
  template instead of blank.
- The theme color picker in the Slides UI keeps the base's palette
  (colorScheme is API-immutable); all styling is explicit RGB.
- SLIDE_NUMBER placeholders cannot be created — page numbers are drawn by
  `build_deck.py` at generation time using the geometry this skill injects.
- Logo insertion needs the image to be anonymously fetchable for a moment
  (AssetStore uploads/shares/cleans up); org policies may block it — the
  build then warns and continues without the logo.
