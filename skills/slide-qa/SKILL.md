---
name: slide-qa
description: >-
  Visual QA of a generated Google Slides deck from thumbnails: fetch every page
  as PNG, inspect with a defect checklist (overflow, overlaps, wrong
  connectors, weak contrast), drive the fix-and-regenerate loop, and clean up
  the local QA files when done. Extracted from the slide-forge generation
  skills (google-slides-template / google-slides / scalar-*) so QA can be
  chosen at generation time — those skills invoke this one when the user opts
  in (the default), and it also runs standalone on any deck URL.
  Triggers: "スライドを検証して", "デッキを QA して", "サムネイルで確認して",
  "生成したスライドをチェック", "slide-qa", "visual QA", "verify the deck",
  "check the generated slides".
  Out of scope: pre-generation offline checks (--dry-run / validate_layout.py
  stay in the generation skills), content fact-checking, and PPTX files
  (exporting a verified deck to .pptx is the pptx-export skill).
---

# Visual QA for Generated Slides (thumbnail-based)

## Important

- **Scope**: post-generation visual verification only. The offline coordinate
  gate (Gate 1: `build_deck.py --dry-run` / `validate_layout.py`) belongs to
  the generation skills and runs **before** generation; this skill is Gate 2
  (`references/validation.md` has the full two-gate rationale).
- **Run every command from the slide-forge root as cwd** — `${CLAUDE_PLUGIN_ROOT}`
  when running from an installed plugin, `/path/to/slide-forge` on a
  local clone. Auth and the venv are shared at the repo root (`config/`, `.venv`).
- **Whether to run QA is settled at generation time.** The generation skills ask
  during intake (default: **run** — recommend it; a clean API response cannot
  show overflowing text or a misattached arrow). When the user skipped QA, the
  generation skill says so in its report and offers this skill as a follow-up.
- **Fixes happen in the source, not the artifact.** On any defect, fix the spec
  / deck module in the originating skill's flow and regenerate. Never patch a
  generated deck in place.
- **Always clean up when done.** The thumbnails exist only for this
  verification and are re-fetchable at any time. Delete them with
  `scripts/cleanup_qa.py` before reporting — even when QA is aborted midway.
  Superseded decks created during the fix loop are deleted from Drive too.

## Quick Reference

| Task | Command |
|------|---------|
| Fetch thumbnails | `.venv/bin/python scripts/fetch_thumbnails.py <URL or ID> --out out/qa --size LARGE` |
| Restrict pages (split QA) | `--pages 3,8,12,20` / `--pages 9-16` |
| Delete local QA files (always, at the end) | `.venv/bin/python scripts/cleanup_qa.py` (`--dry-run` to preview) |
| Full checklist, fix loop, reporting rules | `references/validation.md` (Gate 2) |
| Splitting QA across sub-agents (>15 slides) | `references/parallel-generation.md` §6 |
| Delete a superseded deck from Drive | `drive.files().delete(fileId=…)` (or move to trash) |

---

## Phase 1: Fetch thumbnails

```bash
.venv/bin/python scripts/fetch_thumbnails.py "<deck URL>" --out out/qa --size LARGE
```

- Judge with `--size LARGE`. SMALL is only for the squint test.
- **If the deck exceeds 15 slides, split the QA into 6–8-slide ranges.** When
  the host and session permit sub-agents, delegate those ranges and have them
  **return only findings as text**. Otherwise inspect the same ranges
  sequentially using the Codex fallback in `references/parallel-generation.md`.
- When several decks are QA'd in one session, keep them apart with
  `--out out/<deck>/qa` — `cleanup_qa.py` sweeps both conventions.

## Phase 2: Inspect

Open the PNGs with the Read tool. Seeing every page is the ideal; with many
slides, prioritize:

1. **The page with the most elements** (overlaps show up there first)
2. **The page with the most complex figure** (swimlanes, branching flows, multi-panel)
3. **Pages with tables** (rows grow and overflow downward)
4. **The first page of each section** (how the structure reads)
5. Cover, section dividers, closing (master decorations vs. your own drawing)

Minimum checklist (the full table with fixes is in `references/validation.md`):

- [ ] No text overflows or is truncated in any placeholder or box
- [ ] No text overlaps the template's decorations (bands, shapes, logos)
- [ ] Page numbers appear, not clipped even at 2 digits
- [ ] Logos and footers are not drawn twice
- [ ] The intended layouts were used (no Proposal/Presentation family mix-up)
- [ ] No single trailing character wraps to its own line ("〜へ", "〜出")
- [ ] Arrows do not cross unrelated shapes and each attaches to the
      *semantically* correct shape — coordinate audits cannot judge meaning
- [ ] Labels do not overlap arrows or rules; body-text contrast ≥ 4.5:1
- [ ] Labels next to markers (●, ◆, bar ends) have visible breathing room —
      cramped vertical spacing is invisible to the coordinate audits
- [ ] Table column alignment matches the content: short uniform values (年,
      年月, ID) centered, numbers right, sentences left
- [ ] **Squint test**: the first thing that draws the eye is the page's main
      message; otherwise the emphasis (fill, bold, color) is wrong

## Phase 3: The fix loop

```
identify defects → fix the spec / deck module (originating skill)
  → offline check (free) → regenerate → re-fetch only the affected pages → confirm
```

- For decks generated as **new presentations**, regeneration creates a new
  presentation and URL. **Delete the superseded version from Drive first** —
  the user holds exactly one URL, the latest.
- **Exception — in-place (`--into`) decks.** Decks whose contract is a stable
  URL — the `scalar-account-plan` activity plan, the two
  `scalar-account-planning-session` decks, and Spreadsheets updated via the
  `spreadsheets` skill — are fixed by regenerating **into the same deck**
  (`build_deck.py --into` / the builder's in-place update), after
  `scripts/snapshot_version.py` records the pre-edit revision.
  **Never delete a deck whose URL has been shared** — the URL *is* the
  deliverable, and deleting it breaks every link the user has handed out.
- Never patch the artifact; fix the source and rebuild (faster, reproducible).
- Delete intermediate decks created during verification from Drive as well
  (this too applies only to new-presentation decks, never to `--into` targets).

## Phase 4: Clean up and report

**This phase is not optional.** Before presenting results:

```bash
.venv/bin/python scripts/cleanup_qa.py            # removes out/qa, out/qa-*, out/*/qa
.venv/bin/python scripts/cleanup_qa.py --dry-run  # preview first if unsure
```

The script only touches directories under `out/` (all gitignored, all
re-fetchable), so it is safe to run unconditionally. Pass explicit paths for a
non-standard `--out` location.

Then report, following `references/validation.md`:

- For anything fixed: **what was wrong and how it was fixed** ("fixed" alone
  cannot be verified). For anything not fixed: say so explicitly.
- State that QA passed, which pages were inspected (all, or the ranges), and
  that local QA files were cleaned up.
- Hand back to the generation skill's post-generation confirmation
  (`references/interactive-intake.md` §4) when invoked from one.
