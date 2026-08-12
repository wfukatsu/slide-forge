*[日本語](slide-patterns.ja.md)*

# Slide Patterns (Skeleton × Content)

The templates for **how to compose a page.** The `PageMixin` components
(`scripts/pages.py`) mixed into `diagrams.Canvas`, and a catalog of page
compositions built with them.

Where `illustrations` / `patterns` / `charts` handle "the figure itself,"
this document handles **the page's skeleton** (title band, intro line,
implication, source line, exhibit frame) plus the **analysis diagrams** used
alongside it (trees, waterfalls, rating matrices) and the **deck-design
tools** (summary, storyline, ghost deck).

> **To see, in images, the pages you can build, see
> [slide-pattern-catalog.md](slide-pattern-catalog.md).**
> 42 patterns across 8 categories, each with one real rendered image and
> commentary. This document is the **rules** for how to compose a page;
> that one is the **catalog of actual examples**.

These are also usable by the same `type` names from a deck spec's (JSON)
`figures`. There are two example decks, for different purposes.

| File | Pages | What the deck is for |
|---|---|---|
| `examples/slide-pattern-index.json` | 59 | **Browse and pick which page to build.** A live index, one page per pattern (image version: [slide-pattern-catalog.md](slide-pattern-catalog.md)) |
| `examples/read-alone-guide.json` | 30 | **Learn the conventions of a handout deck.** Component roles, good/bad examples, a collection of anti-patterns |

When starting a new deck, it's fastest to generate `slide-pattern-index.json`
first, have the user point at which pages to build, and write the spec using
the chosen patterns.

## Page Pattern = Skeleton × Content

A page is the product of two choices. **There are only 6 skeletons.**

| Skeleton | Composition | When to use it |
|---|---|---|
| A: One full-width figure | Title + intro + figure (full width) + source | A table or large tree — anything that becomes unreadable when shrunk |
| B: Figure left + implication right | Figure on the left 2/3, `so_what` on the right 1/3 | **Most common. This is the default** |
| C: Two figures side by side | Two figures placed next to each other | Pairing two facts. If it takes two claims, split into two pages instead |
| D: Two rows, top and bottom | A flow (`flow`/`gantt`) on top, detail below | Overlaying a wide figure with a breakdown |
| E: Full-width figure + implication band below | Figure full width, `so_what` laid below it | Figures that need the full width, like `matrix` / `posmap` |
| F: Text only | Table or bullet list only | Content that needs precision — premises, definitions, conditions |

The content (what goes inside the figure frame) spans 7 families and 35
types; Chapters 2–8 of `slide-pattern-index.json` are the complete set of
real examples. The families are: composition / quantitative / comparison
& evaluation / structure & logic / planning & organization / qualitative &
technical / closing & appendix.

## Standard Coordinates by Skeleton (10 × 5.625in — use as-is)

**Don't re-derive coordinates every time.** The values below are measured
values visually confirmed in `slide-pattern-index.json`; use them as-is and
the audit passes. Only adjust the figure's height to fit its content.

`TITLE_ONLY`-family layouts (the title goes in the placeholder):

| Element | x | y | w | h |
|---|---|---|---|---|
| `lead_in` | 0.5 | 0.95 | 9.0 | auto |
| Figure (full width, skeleton A/F) | 0.5 | 1.5 | 9.0 | up to 3.0 |
| Figure (left, skeleton B) | 0.5 | 1.5 | 5.9 | up to 2.9 |
| `so_what` (right, skeleton B) | 6.6 | 1.5 | 2.9 | same as figure |
| Figure × 2 (left/right, skeleton C) | 0.5 / 5.6 | 1.5 | 4.4 / 3.9 | up to 2.8 |
| Top row (skeleton D) | 0.5 | 1.5 | 9.0 | 0.75–1.7 |
| Bottom row (skeleton D) | 0.5 | top row's bottom edge + 0.3 | 9.0 | remainder |
| Figure (centered, skeleton E) | 1.8 | 1.5 | 6.4 | up to 2.3 |
| `so_what` (bottom band, skeleton E) | 0.5 | 3.9 | 9.0 | 0.9 |
| `source_note` | 0.5 | 4.8 | 9.0 | auto |

`BLANK` layout (draws its own title with `governing_message`) — everything shifts down 0.5in:

| Element | x | y | w |
|---|---|---|---|
| `governing_message` | 0.5 | 0.45 | 9.0 |
| `lead_in` | 0.5 | 1.02 | 9.0 |
| Figure | 0.5 | 1.55–1.6 | same as the table above |
| `source_note` | 0.5 | 4.85 | 9.0 |

Minimums to respect:

- `so_what`'s `h` must be **0.9 or more** (the body area is `h - 0.54`; at 0.72 not even one line fits)
- `source_note` must have `y ≤ 4.95` (up to 5.05 if `rule: false`)
- A table needs roughly row count × 0.34in (at size 9) + header. **About 10 rows is the ceiling for one page.** Shrinking `row_h` doesn't help; the bottom edge is capped not by the page edge but by the **footer band at y=5.20in**
- `vbars`'s `h` must be 0.94 or more (0.54 is used up by the value labels and category labels)

## What Changes by Use Case Is Density, Not the Skeleton

**The 6 skeletons are the same across every deck.** What changes is how much
content goes on one page.

| | Stage presentation / study session | Handout / submission / internal approval (read-alone) |
|---|---|---|
| Reader | The speaker fills in the gaps | The reader has to finish reading alone |
| Components used | `governing_message` and `source_note` | Everything (intro line, implication, figure numbers too) |
| Skeleton bias | A and F (a single figure, or text only) | B is most common. C, D, and E are used too |
| Content per page | One message, up to 3 bullet lines | Conclusion, evidence, and source all close on one page |
| Layout family | `*_PRESENTATION` | `*_PROPOSAL` |

**Don't try to serve both purposes with one deck.** Doing so produces the
worst of both — too much text for the stage, not enough information for a
handout. Build two decks if you need both.

The handout-side conventions (density, how to use implications, anti-patterns) are collected in `examples/read-alone-guide.json`.

## Design Rationale (2026-08 research)

Sources: [Deckary: Consulting Slide Standards](https://deckary.com/blog/consulting-slide-standards),
[Slideworks: Action Titles](https://slideworks.io/resources/how-to-write-action-titles-like-mckinsey),
[A1 Slides: McKinsey Presentation Framework](https://a1slides.com/mckinsey-presentation-framework/),
[Analyst Academy: Takeaway Boxes](https://www.theanalystacademy.com/takeaway-boxes-when-to-use/)

- **Action titles: within 15 words (40 full-width characters/line), 2 lines
  max, active voice.** Not "what am I showing" but "what can I claim."
  Reading only the titles in sequence should produce the throughline of the
  whole deck (the horizontal logic).
- **Vertical logic**: the title and the figure are inseparable. Hiding the
  figure and reading only the title, or hiding the title and looking only at
  the figure, must land on the same conclusion either way.
- **Every numeric claim needs a source line.** Even one number of unknown
  origin casts doubt on the whole deck.
- **Implication boxes (kickers) should be ≤ 20% of pages.** Never restate the
  title, never introduce new information absent from the figure.
- **Pyramid principle**: conclusion first (executive summary), evidence
  decomposed MECE.
- **Ghost deck**: validate the throughline before the final polish, using
  just the skeleton (titles, figure placeholders, data status).

## Which One to Use

| What you want to show | Use | Notes |
|---|---|---|
| One page that leads with the conclusion | `exec_summary` | SCR (situation → problem → answer). Opening slide only |
| A chain of titles = the throughline | `storyline` | For validating a design, tables of contents, section dividers |
| A pre-polish skeleton | `ghost` | Carries data status (confirmed/in progress/not yet obtained) |
| Decomposing an issue | `mece_tree` | A horizontal logic tree. Use `orgchart` for an org chart |
| A title built on BLANK | `governing_message` | Prefer the TITLE placeholder if the layout has one |
| An introduction to how to read the figure | `lead_in` | 1–2 lines right below the title |
| A non-obvious implication of the figure | `so_what` | Use on ≤ 20% of pages |
| Source/annotation | `source_note` | Required on every slide with a number |
| A frame with a figure number | `exhibit_frame` | For figures referenced from the body text or an appendix |
| A bridge of increases and decreases | `waterfall` | A mismatched total raises ValueError |
| Comparing options (3 options × criteria) | `rating_matrix` | Dot-based. Holds up in black-and-white printing |

## Standard Form of a Page (Quantitative Slide)

```python
d = Canvas(deck, slide_id, template)
b = d.governing_message(0.5, 0.45, 9.0, "手作業コストは業界中央値の 2.4 倍")
b = d.lead_in(0.5, b + 0.06, 9.0, "同業 12 社の公開データと自社実績の比較。")
inner = d.exhibit_frame(0.5, b + 0.15, 5.9, 2.9, 1, "1 件あたり処理コスト")
d.vbars(inner[0] + 0.2, inner[1] + 0.1, inner[2] - 0.4, inner[3] - 0.2, [...])
d.so_what(6.6, b + 0.15, 2.9, 2.9, "差の大半は受付・照合に由来する")
d.source_note(0.5, 4.85, 9.0, "各社 IR 資料（2025 年度）",
              notes=["※1 間接費は含まない"])
```

Per the stacking convention, each component returns its bottom edge y.
**`exhibit_frame` is the only exception** — it returns the inner area
`(x, y, w, h)` for drawing the content. When used from JSON, that inner area
can't be received, so only the frame is drawn and the content coordinates
have to be hand-aligned (roughly: x+0.2 / header bottom +0.45).

## Notes per Component

### governing_message — action title

- Warns above 40 full-width characters/line × 2 lines. On a layout whose
  template has a TITLE, use that instead — this component is for building
  an entire page from scratch on BLANK.

### lead_in — intro line

- 1–2 lines on "why look at this figure." Unnecessary for stage
  presentations, since it can be said aloud.
- Height is computed automatically from character count (125% leading is baked in).

### so_what — implication box

- `points` can add bulleted supplementary notes. `accent` can change the
  color (e.g. red for a bad example).
- Never write: a restatement of the title / new information absent from the
  figure / multiple claims.

### source_note — source/annotation line

- Raises `ValueError` if `source` is empty. **Enforces, in code, that a
  number without a citable source doesn't go on the slide.**
- `notes` are "※1 …"-style annotations, placed above the source. `prefix`
  can change the label to something like "Basis."

### exhibit_frame — exhibit frame

- The caller manages numbering sequentially (the component itself doesn't assign numbers).
- Unnecessary for material with one figure per page and no cross-references.

### mece_tree — logic tree

- Raises `ValueError` for depth beyond 4, a column narrower than 1.1in, or a
  height too short for its leaves.
- Whether the decomposition is actually MECE (no gaps, no overlaps) is **the
  author's responsibility** — the component only guarantees the shape.

### waterfall — waterfall

- `items` is `(label, value, "total"|"delta")`. The first item must be `total`.
- **Raises `ValueError` if the final total doesn't match the running sum**
  (catches data mix-ups).
- The total/primary bar is blue. `good` decides which direction (increase or
  decrease) is colored green: `good="up"` (default — a revenue/profit
  bridge, where increases are green) or `good="down"` (a cost/lead-time
  reduction bridge, where decreases are green). Coloring purely by sign would
  invert the meaning in a cost context ("reduction = red").
- The baseline is fixed at zero (no negative regions).

### rating_matrix — rating matrix

- Values are integers from 0 to `levels`. Harvey balls (partially filled
  circles) can't be drawn because the Slides API has no pie-wedge shape, so
  **a count of filled dots** is used instead. Distinguishable even in
  black-and-white printing.
- For a 2-option comparison, `before_after` (illustrations) is enough. For 3
  or more options, or a parallel comparison without ranking, use
  `comparison`. Only add an arrow when showing a "transition."

### exec_summary — executive summary

- `points` (the arguments supporting the answer) are capped at 5. If it
  splits into more than that, reconsider the chapter structure.
- The bar for passing is: "reading only this one page is enough to decide."

### storyline — horizontal logic

- `titles` is either a string or `(page number, title)`. `highlight` can mark the current position.
- Serves double duty as a deliverable (table of contents, section divider) and a design tool (validating the throughline).

### ghost — ghost deck

- Status is `confirmed` (green) / `wip` (yellow) / `missing` (red).
- **A checkboard to prevent "not yet obtained" items from surviving into the
  final polish** — it isn't a deliverable itself.

## Anti-Patterns (What Components Stop vs. What a Human Must Catch)

| Failure | How it's caught |
|---|---|
| A number with no source | `source_note` raises `ValueError` for an empty source |
| A waterfall total that doesn't reconcile | `waterfall` raises `ValueError` |
| A shifted baseline on a bar chart | Disallowed in `charts` (`ValueError`) |
| Using dual axes to stage a correlation | `linechart` deliberately doesn't support this |
| A 3-line title | `governing_message` warns |
| Text overflow/overlap | `audit_text_fit` / `audit_overlaps` (`--dry-run --strict`) |
| A title that's only a theme / two claims on one page / overused implications | Not machine-detectable. Check by eye against the anti-pattern chapter in `examples/read-alone-guide.json` |

## Pitfalls

- **The meaning of the `size` key differs by type.** For icon-family and
  `pie` it's inches (a spatial quantity); for `table` and others it's font
  points. Spec validation already accounts for this distinction.
- **An index/listing table caps out around 10 rows.** Slides table rows
  don't shrink, and the bottom edge is capped not by the page edge but by
  the master's logo/footer band. Split by category into multiple pages when
  there are more rows than that (this is why `slide-pattern-index.json`'s
  index spans 5 pages). `--dry-run` stops overlap with the band as an error.
- When using `exhibit_frame` from JSON, the content coordinates are
  hand-placed. If they drift, `--dry-run`'s `audit_overlaps` catches it —
  fix it once you see the warning.
- Harvey balls and angle-specified pie wedges can't be drawn (the same
  constraint that makes `pie` an image).
- Printing assumes one landscape page at a time. The page size can't be
  changed under the copy-based generation method
  (`references/api-notes.md` section 7). If you need a portrait A4 page,
  that's outside this skill's scope.
