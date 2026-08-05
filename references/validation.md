# Validation Gates: Offline Coordinate Checks and Thumbnail QA

Discovering breakage after generation is the most expensive outcome. Two gates
catch defects at two different costs:

1. **Offline coordinate check** — free, instant, no API calls. Catches
   everything that coordinates alone can prove: overflow, overlap, text that
   cannot fit, detached connectors, unresolvable layouts.
2. **Thumbnail QA** — one API round trip per fetch, plus your eyes. Catches
   everything coordinates cannot prove: awkward wrapping, arrows crossing
   other shapes, connectors attached to the *wrong* shape, weak contrast,
   whether the figure actually communicates.

Run the offline check **every time before generating**. Thumbnail QA is owned
by the **`slide-qa` skill** and is **chosen at generation time** (intake asks;
default and recommended: run). When it runs it covers Gate 2 end to end —
fetch, inspection, the fix loop, and deleting the local QA files
(`scripts/cleanup_qa.py`). When the user skips it, the deck ships unverified
and the report must say so. Neither gate replaces the other.

All commands run from the repository root (`/Users/wfukatsu/work/slide-forge`).

---

## Gate 1: Offline Coordinate Check

Which command depends on how the deck is written:

| Deck form | Command |
|---|---|
| Template-driven JSON spec (this skill) | `.venv/bin/python scripts/build_deck.py --template templates/<id>.json --spec deck.json --dry-run [--strict]` |
| Code-first deck module written with `deckkit` (`google-slides` skill) | `.venv/bin/python scripts/validate_layout.py path/to/mydeck.py` |

Both expand every figure to coordinates without touching the API and run the
same audit family (`audit_bounds` / `audit_connectors` / `audit_overlaps` /
`audit_text_fit`). `--dry-run` additionally verifies layout resolution and
placeholder consistency against `template.json`. With `--strict`, a single
audit warning exits non-zero — use it as a CI-style gate.

### validate_layout.py

```bash
.venv/bin/python scripts/validate_layout.py path/to/mydeck.py
.venv/bin/python scripts/validate_layout.py mydeck.py --template templates/my-brand.json
.venv/bin/python scripts/validate_layout.py mydeck.py --quiet    # silent when clean
```

Exit code is 1 when problems are found, so it drops into CI directly.

### What it detects

| Check | Why it fails | Fix |
|---|---|---|
| Figure overflows the bottom | Collides with the master's logo, copyright line, or takeaway row | Tighten block heights and gaps. `DY1` is the figure's lower bound |
| Figure overflows left/right | Falls outside the slide and disappears | Keep within `X0`–`XE` |
| Title wraps to 2 lines | Title crosses `DY0` and collides with the figure | Shorten to ≤ 30.5 full-width characters |
| Exception while drawing | Coordinate arithmetic error, wrong component arguments | Fix per the traceback |
| Layout cannot be resolved | Misspelled role name, template lacks the role | Check `roles` / `layouts` in the template |
| Placeholder missing | The layout has no TITLE/SUBTITLE/BODY | Use another role, or a layout that supports `drawText` |
| Connector not touching a shape | Both endpoints ≥ 0.22 in from every shape | Use `d.connect(a, b)` / `d.link(a, b)` with explicit shapes |
| Connector buried inside a shape | Endpoint ≥ 0.06 in inside a shape's interior | Same as above; if the line is intentional, mark it `free=True` |
| Text hidden behind a later shape | A banner or zone was drawn over an earlier block | Stack using each pattern's return value (bottom y) |
| Text colliding with text | Unfilled labels overlap within their actual text extents | Separate positions, shorten wording |
| Too much text for the box | Required line count exceeds the box height | Make the box taller, cut text |

### What it cannot detect (thumbnail QA required)

These are invisible to coordinates. Always look at the images (Gate 2).

- Awkward line wrapping (text fits the box, but a single particle drops to its own line)
- Whether a connector attaches to the **semantically correct** shape (presence of a connection is provable; meaning is not)
- Whether an arrow crosses over other shapes (route quality is not judged)
- Whether an arrow's direction and route match the intended meaning
- Whether color contrast is sufficient
- Whether the figure actually communicates what it is supposed to

### Layout contract (assumptions behind the checks)

The safe area is defined by `deckkit` constants. Defaults are measured values
for a 16:9 (10 × 5.625 in) template.

- `DY0 = 0.84` — top edge where figures may start (below a one-line title)
- `DY1 = 4.30` — bottom edge where figures must end
- `NY = 4.38` / `EY = 4.86` — takeaway and note rows (used by `foot()`; excluded from checks)
- `TITLE_EM_MAX = 30.5` — title width that fits one line, in full-width character units

For templates with a different page size, override on the deck side:

```python
configure_layout(page_w=13.333, page_h=7.5, margin=0.6,
                 diagram_top=1.0, diagram_bottom=5.9,
                 note_y=6.0, edition_y=6.5)
```

Elements drawn by `foot()` sit intentionally below `DY1` and are excluded from
the checks (controlled by the `FOOT_MODE` flag). Custom bottom-fixed elements
should ride the same mechanism. Details in `references/layout-contract.md`.

For template-driven JSON specs, remember the additional manual estimate: the
API silently accepts overflowing placeholder text, and `--dry-run`'s
`audit_text_fit` only inspects `figures`. Compute body-text fit with the
formula in the skill's Phase 3 (paragraph spacing included — ignoring it cuts
real capacity to roughly 60% of the estimate).

---

## Gate 2: Thumbnail QA (the `slide-qa` skill)

Coordinate checks catch overflow, overlap, text fit, and connector attachment.
**Defects invisible to coordinates still remain.** When the user chose QA at
generation time (the default), look at the images after generating.

```bash
.venv/bin/python scripts/fetch_thumbnails.py <URL or ID> --out out/qa --size LARGE
.venv/bin/python scripts/fetch_thumbnails.py <URL> --out out/qa --pages 3,8,12,20
```

`--size` accepts SMALL / MEDIUM / LARGE. Judge with LARGE.

If the deck exceeds 15 slides, split the QA across sub-agents (`--pages 9-16`,
6-8 slides each, findings returned as text only) — see
`references/parallel-generation.md`.

### Which pages to open first

Seeing every page is the ideal; with many slides, prioritize:

1. **The page with the most elements** (overlaps show up there first)
2. **The page with the most complex figure** (swimlanes, branching flows, multi-panel)
3. **Pages with tables** (rows grow and overflow downward)
4. **The first page of each section** (how the structure reads)
5. Cover, section dividers, closing (master decorations vs. your own drawing)

### Checklist

| Where to look | Common defect | Fix |
|---|---|---|
| Text inside boxes | A single character wraps to the next line ("〜へ", "〜出") | Shorten the wording. Widen the box |
| Titles | Wraps to 2 lines and covers the figure | Shorten to ≤ 30.5 full-width characters |
| Arrow routes | Connected, but crossing over another shape mid-route | Rearrange the shapes (stack vertically, etc.). The audits cannot catch this |
| Arrow endpoints | Meant A→B but actually attached A→C | The audits only prove *a* connection exists. Verify the meaning by eye |
| Panel widths | Rightmost panel too narrow, text overflows | Redistribute widths. Move content to a full-width card below |
| Labels | Overlapping arrows or rules, unreadable | Push outward (`align` START/END) |
| Colors | Pale text on pale background, weak contrast | Use `readable_on()`. Body text needs ≥ 4.5:1 |
| Footer | Your drawing overlaps the master's logo/copyright | Keep above `DY1` |
| Whitespace | Figure hugs the top, large empty band below | Increase block heights to use the vertical space |
| Placeholders | Text overflowing or truncated; decorations colliding with text | Cut text, adjust `bodyFontSize`/spacing, or pick a layout with more room |
| Page numbers | Missing or clipped at 2 digits | Confirm `add_page_numbers()`; check position |
| Logos/footers | Drawn twice | Template decorations are inherited by the copy — remove your own drawing |
| Layout families | Proposal vs. Presentation mix-up | Fix the `layout` value in the spec |

### Squint test

Look with your eyes narrowed (or at the SMALL thumbnail). **Is the first thing
that catches the eye the page's main message?** If not, the emphasis — fill,
bold, color — is wrong.

---

## The Fix Loop

```
fetch thumbnails → identify defects → fix the spec / deck module
  → offline check (free) → regenerate → re-fetch only the affected pages → confirm
```

- Regeneration always creates a new presentation. **Move the superseded
  version to the Drive trash** (leaving it around makes it unclear which is
  latest). The user should hold exactly one URL — the latest.
- Never patch a generated artifact in place. Fix the spec or module and
  rebuild: faster and reproducible.
- Partial rendering (`render_deck.py --only 3-8`, code-first path) saves quota
  and wait time during iteration, but page numbers shift — do the final
  confirmation on a full run.
- Delete intermediate decks created during verification from Drive
  (`drive.files().delete(fileId=…)`).

## Cleaning Up QA Files (mandatory)

The thumbnails exist only for verification and can be re-fetched at any time.
When QA finishes — pass, fail-and-fixed, or aborted — delete them before
reporting:

```bash
.venv/bin/python scripts/cleanup_qa.py            # removes out/qa, out/qa-*, out/*/qa
.venv/bin/python scripts/cleanup_qa.py --dry-run  # preview the targets
.venv/bin/python scripts/cleanup_qa.py out/mydeck/qa   # a specific directory
```

The script refuses anything outside `out/` (all gitignored), so it is safe to
run unconditionally.

## Reporting Rules

- For anything you fixed, state **what was wrong and how you fixed it**.
  "Fixed" alone cannot be verified.
- For anything you did not fix, say explicitly that it was not fixed.
- For any number or chart shown, cite the source. A number without a source
  does not go on a slide.
- Pass QA yourself before presenting results — do not let the user find
  defects that a visual pass would have caught.
