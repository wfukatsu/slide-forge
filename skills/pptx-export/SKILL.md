---
name: pptx-export
description: >-
  Export a generated Google Slides deck to PowerPoint (.pptx) as a delivery
  format: Drive API export preserving the deck exactly as generated, saved
  locally and optionally archived in the deck's Drive folder next to the spec.
  Invoked by the slide-forge generation skills when the user chooses PPTX
  output at intake, and runs standalone on any accessible deck URL.
  Triggers: "PPTX でも出力して", "PowerPoint 形式でほしい", "pptx に変換",
  "パワポで納品", "pptx-export", "export to PowerPoint",
  "download as pptx", "PowerPoint 版もください".
  Out of scope: authoring or editing PPTX files directly
  (document-skills:pptx), QA of the exported file (QA happens on the
  Google Slides deck via slide-qa, before export), and non-Slides sources.
---

*[日本語](SKILL.ja.md)*

# PPTX Export for Generated Decks

## Important

- **The export is a snapshot, not a linked copy.** It captures the deck as it
  is at export time. Always export **after** visual QA and any fix loop are
  finished — and re-export whenever the deck is regenerated, deleting the
  stale `.pptx` from the Drive folder first (same rule as superseded decks).
- **Fixes happen in the spec, never in the .pptx.** On any defect, return to
  the originating generation skill, fix the spec, regenerate, re-run QA if it
  was chosen, then export again. Editing the exported file forks it from the
  source of truth.
- **Run every command from the slide-forge root as cwd** — `${CLAUDE_PLUGIN_ROOT}`
  when running from an installed plugin, `/path/to/slide-forge` on a
  local clone. Auth and the venv are shared at the repo root (`config/`, `.venv`).
- **Whether to export PPTX is settled at generation time** via the output
  format question in intake (`references/interactive-intake.md` §2); the
  default is Google Slides only. Standalone runs on an existing deck URL need
  no intake.
- **From-scratch PPTX authoring is a different job.** When the user wants a
  PPTX built or edited directly (no Google Slides involved), hand off to
  `document-skills:pptx` instead of this skill.

## Quick Reference

| Task | Command |
|------|---------|
| Export (saves to `out/pptx/<deck name>.pptx`) | `.venv/bin/python scripts/export_pptx.py <URL or ID>` |
| Export to an explicit path | `--out path/to/deck.pptx` |
| Also archive in the deck's Drive folder | `--folder <Drive folder URL/ID>` |

Decks over the 10MB `files.export` limit fall back to `exportLinks`
automatically — no flag needed.

## Workflow

1. **Confirm the deck is final.** When invoked from a generation skill,
   this means generation succeeded and — if QA was chosen — the `slide-qa`
   loop is done and clean. Standalone, ask nothing; export what the URL holds.
2. **Export**, passing the deck's Drive folder when one exists so the
   `.pptx` sits next to the spec and figure sources (Drive folder rule):

   ```bash
   .venv/bin/python scripts/export_pptx.py "<deck URL>" --folder "<folder URL>"
   ```

3. **Report** the local path, the file size, and (when uploaded) the Drive
   folder URL, alongside the deck URL in the generation report.

## Fidelity caveats (state them in the report when relevant)

The export is Google's own converter, so layout and geometry carry over
exactly — but the file opens in PowerPoint, a different rendering engine:

- **Fonts must exist on the viewer's machine.** Decks styled with Google
  Fonts (Noto Sans JP, etc.) fall back to a substitute font if not installed
  locally, which can shift line breaks. Mention the deck's font when it is
  not a system font.
- **Google-specific features degrade**: linked Sheets charts become static
  images; speaker-notes formatting may simplify; animations do not transfer
  (slide-forge decks don't use them, so this rarely matters).
- The exported file is not re-inspected — QA already ran on the Slides deck,
  and the converter is deterministic. If the user reports a rendering issue
  in PowerPoint, treat the font substitution above as the first suspect.
