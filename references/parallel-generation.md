*[日本語](parallel-generation.ja.md)*

# Splitting Generation by Page (Parallel or Sequential)

A procedure for splitting a large deck into per-page fragments for
generation. When the host and session allow it, delegate to sub-agents to
keep the main context and wait time down. When parallel execution isn't
available or is disallowed, the main agent creates the same fragments
sequentially.

## Sequential Fallback for Codex

If Codex's current instructions don't allow using sub-agents, don't delegate
purely for the sake of parallelism. Instead:

1. The main agent finalizes the outline and all action titles first.
2. Create one file per fragment, 2–3 pages each, under `out/<deck>/pages`, numbered.
3. Run the self-check from Step 3 each time a fragment is created.
4. Combine all fragments with `assemble_spec.py` and validate the complete spec with `--dry-run --strict`.
5. Do QA in batches of 6–8 pages at a time, opening images in order and noting only the findings for each range.

The file format, numbering, and validation conditions are identical to the parallel case. Only who does the work and the execution order change.

## When to Use This (Important)

**Splitting the work doesn't reduce total token usage — it reduces the main
agent's context and wait time.** Because each agent has to re-read the design
conventions (`references/*.md`), **the total goes up**. Given that, it's
worth it when:

| Use it | Don't use it |
|---|---|
| 12+ pages | 10 or fewer (the coordination overhead costs more) |
| Many figures (each page needs a different reference) | Every page is just bullet text |
| QA covers 15+ pages (images crowd out context) | Fixing/regenerating a few pages |
| A large-scale replacement of an existing deck | Fixing a single page |

**Splitting QA pays off even with fewer pages.** A single thumbnail image
costs hundreds to a thousand tokens; reading 20 fills the main context with
images. Splitting just this part is always worthwhile.

## Work That Should Not Be Split

- **Deciding the outline and action titles.** Titles need to read together
  and form the throughline (the horizontal logic). Having each page written
  independently always breaks this. **The main agent decides all titles
  first**, and each agent receives already-finalized titles.
- **Deciding the template, layout family, and `defaults`.** These affect
  every page, so decide them in one place.
- **Assembly and generation.** `assemble_spec.py` → `--dry-run --strict` →
  `build_deck.py` is done by the main agent alone (multiple writers break
  reproducibility).
- **Sourcing numbers and facts.** Having each agent look things up produces
  inconsistent sourcing. The main agent finalizes the numbers and passes them
  **verbatim**. Don't let an agent write a number it wasn't given.

## Procedure

### 1. Main agent: decide the skeleton (don't split this)

Finalize the outline (page number, layout, action title, skeleton, content,
and data to use) as text and get the user's approval
(`references/interactive-intake.md`). Don't write JSON at this stage.

### 2. Main agent: set up the working directory

```bash
mkdir -p out/<deck>/pages
```

### 3. Split: 1 agent = 1–3 pages

**Giving one agent a single page makes the coordination overhead too
costly.** Grouping 2–3 pages of the same skeleton/figure family per agent
means the reference material only has to be read once.

Every agent's instructions must include:

1. The absolute output path (`out/<deck>/pages/0120-cost-bars.json`) — use
   **numbering in steps of 10** so pages can be inserted later. Order follows
   filename ascending order
2. The `layout` and **finalized action titles** (don't make the agent decide them)
3. The skeleton (A–F) and content (component names)
4. The numbers/copy to place, **verbatim**. Pass the source citation string too
5. Which reference(s) to read, **named explicitly, only 1–2** (don't have it read everything)
6. Coordinates must follow the "Standard Coordinates by Skeleton" in `references/slide-patterns.md`
7. The self-check below must be completed

Self-check every agent must run before returning:

```bash
# Run from the slide-forge repository root
.venv/bin/python scripts/assemble_spec.py --out /tmp/chk-$$.json --title chk \
    out/<deck>/pages/0120-cost-bars.json
.venv/bin/python scripts/build_deck.py --template templates/<id>.json \
    --spec /tmp/chk-$$.json --dry-run --strict
```

State in the instructions **that this must pass before returning**. If a
broken fragment is returned to the main agent, every fix floods the main
context with errors.

An agent's return value should be **only the path of the file it wrote plus
a one-line summary**. Don't have it return the JSON contents (doing so
defeats the purpose of saving context).

### 4. Main agent: assemble and validate

```bash
.venv/bin/python scripts/assemble_spec.py \
    --out out/<deck>/deck.json --title "Deck Title" out/<deck>/pages
.venv/bin/python scripts/build_deck.py --template templates/<id>.json \
    --spec out/<deck>/deck.json --dry-run --strict
```

Even if the fragments passed individually, **the whole may still fail**
(duplicate page numbers, gaps in figure numbering, mismatched `defaults`).
Catch and fix these here.

### 5. Generate

```bash
.venv/bin/python scripts/build_deck.py --template templates/<id>.json \
    --spec out/<deck>/deck.json --title "Deck Title"
```

### 6. Split QA too

If the main agent reads every thumbnail, that's the most expensive part.
Split by range.

```bash
.venv/bin/python scripts/fetch_thumbnails.py "<URL>" --out out/<deck>/qa
```

Assign 6–8 pages per agent and **have it return only the findings as text**:

> Open `out/<deck>/qa/slide-17.png` through `slide-24.png` with Read, check
> the following, and list only the slides with problems as one line each,
> "number: symptom." If there are none, respond with just "none." Don't
> write descriptions or impressions of the images.
> - Does text overflow its placeholder/box?
> - Does the text overlap the template's decorations (band, logo, footer)?
> - Is the page number present, and not clipped at 2 digits?
> - Does an arrow cross an unrelated shape?
> - Is the color meaning of the figure reversed (e.g. reduction shown in red, increase in green)?

The main agent only receives the collected findings and **fixes and
regenerates only the affected page's fragment** (it doesn't rewrite the
whole deck).

Once QA is done, delete the fetched thumbnails with
`.venv/bin/python scripts/cleanup_qa.py` (it cleans up `out/qa` / `out/qa-*`
/ `out/*/qa`; the full procedure lives in the `slide-qa` skill).

## Choosing a Model

A page's difficulty is almost entirely determined by whether it requires
reasoning about coordinates.

| Page | model | Rationale |
|---|---|---|
| `COVER` / `SECTION` / `CLOSING` / `CONTENT` (text only) | `haiku` | No figure. Just flows text in |
| Skeleton A/F (one table, bullet list) with data passed verbatim | `haiku` | Standard coordinates apply directly |
| Skeleton B (figure + implication), 1–2 standard charts | `sonnet` | **Most pages fall here.** Coordinates are the standard form; only value formatting needs judgment |
| Skeleton C/D/E (multi-figure layout), nested `exhibit_frame` | `sonnet` | Combines standard coordinates, but height allocation needs judgment |
| Composition diagrams built directly with Canvas, cloud architecture diagrams, 3+ mixed systems | `opus` | Coordinates must be designed from scratch. Passing the audit takes iteration |
| QA (eyeballing thumbnails, listing findings) | `sonnet` | Detecting visual anomalies. `haiku` misses overflow |

- When in doubt, use `sonnet`. Reserve `haiku` for pages you can say with certainty require no reasoning.
- **Reserve `opus` for pages that require designing new coordinates.** Using it on pages where standard coordinates suffice costs more without improving the result.
- Don't use `haiku` for QA. **A missed defect leads to a redo, which ends up costing more.**

## Pitfalls

- **Don't let a fragment write a `title`.** The deck title is supplied from
  one place, `assemble_spec.py --title`. Spec-level keys in a fragment are
  decided by **whichever is read first**, so a later page silently
  overwriting the overall default can't actually happen — but it's still
  safer not to let fragments write it at all.
- **Figure numbers (`exhibit_frame`) are numbered and handed out by the main
  agent.** Letting each agent assign its own creates duplicates.
- **Never give the same output path to two agents.** Whichever writes last silently overwrites the other.
- **Don't issue instructions that let the page count change.** Saying "split
  into 2 pages if needed" causes numbering collisions. Once a split turns out
  to be necessary, the main agent renumbers.
- Fragments live under `out/` (already gitignored). **They are not
  deliverables — don't commit them.**
