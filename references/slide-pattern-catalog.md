*[日本語](slide-pattern-catalog.ja.md)*
# Slide Pattern Catalog (43 real examples)

An image catalog built by actually rendering `examples/slide-pattern-index.json` and exporting it one slide at a time.
It's meant for **choosing a page by looking at what can be built**; the layout rules themselves live in
[slide-patterns.md](slide-patterns.md), and the details of figure components live in
[patterns.md](patterns.md) / [charts.md](charts.md) / [diagrams.md](diagrams.md).

Each pattern's **figures** line is the exact `type` name you write into `figures` in the deck spec (JSON).

> The images are committed to the repository. When you add or change a pattern,
> rebuild with the commands below and commit the images along with it.

```bash
# Build this catalog (same steps when you add a pattern)
.venv/bin/python scripts/build_deck.py \
    --template templates/scalar-2026.json --spec examples/slide-pattern-index.json
.venv/bin/python scripts/fetch_thumbnails.py <generated URL> --out out/patterns --size MEDIUM
.venv/bin/python scripts/build_pattern_catalog.py --thumbs out/patterns
```

| Category | Count | What this chapter helps you choose |
|---|---|---|
| [1. 6 Skeletons](#1-6-skeletons) | 6 | How to lay out a page |
| [2. Structural pages](#2-structural-pages) | 4 | The deck's framework |
| [3. Quantitative pages (trend, composition, change)](#3-quantitative-pages-trend-composition-change) | 7 | Making a case with numbers |
| [4. Comparison / evaluation pages](#4-comparison--evaluation-pages) | 6 | Putting options side by side for a decision |
| [5. Structure / logic pages](#5-structure--logic-pages) | 7 | Turning relationships into a diagram |
| [6. Planning / organization pages](#6-planning--organization-pages) | 5 | Showing time and people |
| [7. Qualitative / technical pages](#7-qualitative--technical-pages) | 5 | Making a case without numbers |
| [8. Closing / appendix pages](#8-closing--appendix-pages) | 3 | Decisions and what follows |

> Only "System Architecture" draws official cloud vendor icons, so it requires
> running `.venv/bin/python scripts/fetch_cloud_icons.py` beforehand.
> The icons aren't included in the repository because redistribution isn't permitted
> (see [assets/cloud-icons/README.md](../assets/cloud-icons/README.md)).

## 1. 6 Skeletons

The **layout** itself for a page. Before deciding which figure to use, decide which of these 6 skeletons to build with.
The default is Skeleton B (figure left + kicker right). Coordinates you can use as-is are in "Skeleton standard coordinates" in [slide-patterns.md](slide-patterns.md).

### Skeleton A | Full-width single figure

![Skeleton A | Full-width single figure](images/slide-patterns/skeleton-a-full-width.png)

No kicker; the figure uses the full width. Use this for figures with many elements — such as tables or large trees — that become unreadable when shrunk.

**figures**: `governing_message` / `lead_in` / `table` / `source_note`

### Skeleton B | Figure left + kicker right

![Skeleton B | Figure left + kicker right](images/slide-patterns/skeleton-b-figure-left-kicker-right.png)

Places the figure in the left 2/3 and the kicker in the right 1/3. The reader's eye flows figure → kicker, so there's no ambiguity about reading order.

**figures**: `governing_message` / `lead_in` / `vbars` / `so_what` / `source_note`

### Skeleton C | Two figures side by side

![Skeleton C | Two figures side by side](images/slide-patterns/skeleton-c-two-figures.png)

Places two figures side by side that support the same claim. If you have two claims, split them across two slides instead.

**figures**: `governing_message` / `lead_in` / `linechart` / `pie` / `source_note`

### Skeleton D | Two rows, top and bottom

![Skeleton D | Two rows, top and bottom](images/slide-patterns/skeleton-d-two-rows.png)

Puts the overall flow in the top row and its breakdown or supplementary detail in the bottom row. Suits wide figures such as processes or timelines.

**figures**: `governing_message` / `lead_in` / `flow` / `table` / `source_note`

### Skeleton E | Full-width figure + kicker band below

![Skeleton E | Full-width figure + kicker band below](images/slide-patterns/skeleton-e-full-width-kicker-band.png)

For figures that need full width, such as four-quadrant charts or positioning maps. The kicker sits as a band underneath.

**figures**: `governing_message` / `lead_in` / `matrix` / `so_what` / `source_note`

### Skeleton F | Text only

![Skeleton F | Text only](images/slide-patterns/skeleton-f-text-only.png)

For content that needs precision — definitions, premises, conditions — don't force it into a figure. Structure it with a table instead.

**figures**: `governing_message` / `lead_in` / `table` / `source_note`

## 2. Structural pages

Pages that build the deck's overall framework. `storyline` and `ghost` are both deliverables and design tools used to verify the argument before finalizing the deck.

### Executive summary

![Executive summary](images/slide-patterns/exec-summary.png)

Opening slide only. Use SCR (Situation → Complication → Resolution) so a decision can be made from this one slide alone. Keep it to at most 5 points.

Example heading: "Make the decision from this one slide"

**figures**: `exec_summary`

### Agenda

![Agenda](images/slide-patterns/agenda.png)

Shows the chapters and page counts up front so readers can grasp the overall scope. If there are many rows, split them by area.

Example heading: "Show chapters and page counts up front to lower the reader's load"

**figures**: `table` / `source_note`

### Storyline

![Storyline](images/slide-patterns/storyline.png)

Used as chapter dividers so readers can track where they are. During design, also used to verify the argument.

Example heading: "Show whether the argument holds up from the titles alone"

**figures**: `lead_in` / `storyline`

### Ghost deck

![Ghost deck](images/slide-patterns/ghost-deck.png)

Not a deliverable — a design tool. A checklist to catch "not yet obtained" items before they slip into the final deck.

Example heading: "Confirm the outline and data sources before finalizing"

**figures**: `lead_in` / `ghost`

## 3. Quantitative pages (trend, composition, change)

Pages that make a case with numbers. **All of them require a source line** (`source_note` raises `ValueError` on an empty source). The components reject dual axes and truncated baselines.

### Trend

![Trend](images/slide-patterns/trend.png)

The basic form for showing change over time. A single axis only (no dual axes). Attach values only at the endpoint.

Example heading: "Operating margin has fallen for three straight years, below the median"

**figures**: `lead_in` / `linechart` / `so_what` / `source_note`

### Waterfall breakdown

![Waterfall breakdown](images/slide-patterns/waterfall.png)

Breaks down the difference between a starting and ending value into contributing factors. The component halts with an error if the total doesn't match the sum.

Example heading: "Bridge across the gap to show where the difference came from"

**figures**: `lead_in` / `waterfall` / `source_note`

### Composition (pie)

![Composition (pie)](images/slide-patterns/composition-pie.png)

Shows a share of the whole. Up to 6 series. Drawn clockwise in the order passed.

Example heading: "80% of the reduction potential lies in the reception and reconciliation steps"

**figures**: `lead_in` / `pie` / `so_what` / `source_note`

### Stacked trend

![Stacked trend](images/slide-patterns/stacked-trend.png)

Shows the trend of a total and its breakdown at the same time. If comparing the breakdown components against each other is the main point, use grouped vertical bars instead.

Example heading: "The total volume is shrinking while staffing costs edge up slightly"

**figures**: `lead_in` / `vbars_stacked` / `source_note`

### Series comparison

![Series comparison](images/slide-patterns/grouped-comparison.png)

Compares 2–3 series within the same category. If you have more than 4 series, switch to a table.

Example heading: "The proposed composition cuts effort by more than half in every quarter"

**figures**: `lead_in` / `vbars_grouped` / `source_note`

### KPI

![KPI](images/slide-patterns/kpi.png)

One or two headline metrics shown large, with breakdowns as horizontal bars. Cramming in too many numbers means none of them stick.

Example heading: "Narrow down the numbers to take away, and add the breakdown alongside"

**figures**: `lead_in` / `metric` / `hbars` / `source_note`

### Numbered exhibit

![Numbered exhibit](images/slide-patterns/exhibit-numbered.png)

Adding a frame and a number lets you point to it with "see Exhibit 3." Keep it in sync with the exhibit list in the appendix.

Example heading: "A page referenced from the body text and the appendix"

**figures**: `lead_in` / `exhibit_frame` / `vbars` / `so_what` / `source_note`

## 4. Comparison / evaluation pages

Pages that put options side by side for a decision. For 2 options use a side-by-side layout; for 3 or more use `comparison`; for roughly 3 options × roughly 4 criteria use a rating matrix; when precision matters, use a table.

### Two-option comparison

![Two-option comparison](images/slide-patterns/two-option-compare.png)

Puts the current state and the proposal side by side. This is enough for 2 options — no rating matrix needed.

**figures**: `before_after` / `so_what` / `source_note`

### Multi-option comparison

![Multi-option comparison](images/slide-patterns/multi-option-comparison.png)

Only add arrows for "transitions." Adding arrows to a parallel comparison implies a left-to-right progression that doesn't actually exist.

Example heading: "Lay out 3+ options side by side and point to a single recommendation"

**figures**: `lead_in` / `comparison` / `so_what` / `source_note`

### Multiple options × criteria

![Multiple options × criteria](images/slide-patterns/rating-matrix.png)

Roughly 3 options × roughly 4 criteria is the practical limit. 4-dot ratings work best. For 2 options, a side-by-side layout is enough.

Example heading: "Dot ratings stay legible even in black-and-white printing"

**figures**: `lead_in` / `rating_matrix` / `so_what` / `source_note`

### Positioning map

![Positioning map](images/slide-patterns/positioning-map.png)

Shows relative position along two axes. If you want to show "classification" into four quadrants, use `matrix` instead.

Example heading: "Show position relative to competitors on two axes"

**figures**: `posmap` / `so_what`

### Balance

![Balance](images/slide-patterns/balance.png)

Shows the trade-off between two options as weights. Not a quantitative comparison — a figure that shows which way the judgment tips.

**figures**: `balance` / `source_note`

### Spec comparison table

![Spec comparison table](images/slide-patterns/spec-table.png)

Lines up numbers and conditions precisely. Keep content as a table when turning it into a figure would lose precision.

**figures**: `table` / `source_note`

## 5. Structure / logic pages

Pages that turn relationships into a diagram. The claim is about **structure**, not numbers.

### Logic tree

![Logic tree](images/slide-patterns/logic-tree.png)

Breaks a question down with no gaps and no overlaps. A depth greater than 4 is an error. Whether it's truly MECE is the author's responsibility.

**figures**: `mece_tree` / `source_note`

### Hierarchy and narrowing

![Hierarchy and narrowing](images/slide-patterns/pyramid-funnel.png)

Places a metric hierarchy (pyramid) alongside a decreasing count (funnel).

Example heading: "Metric hierarchy and decreasing counts"

**figures**: `pyramid` / `funnel` / `source_note`

### Layers

![Layers](images/slide-patterns/layers.png)

Shows a system's responsibilities as layers. The order of the layers itself is the claim.

**figures**: `layers` / `source_note`

### Process

![Process](images/slide-patterns/process-flow.png)

Shows a process's flow and stages. Use `flow` / `steps` / `icon_flow` depending on the level of granularity.

**figures**: `flow` / `steps` / `icon_flow` / `source_note`

### Hub and spokes

![Hub and spokes](images/slide-patterns/hub-radial.png)

A structure where one foundation supports multiple lines of business. Keep the number of spokes to around 6 or fewer.

**figures**: `hub` / `source_note`

### Four quadrants

![Four quadrants](images/slide-patterns/quadrant-matrix.png)

Positions initiatives on two axes to establish priority. For position relative to competitors, use `posmap` instead.

Example heading: "Position initiatives by impact and cost"

**figures**: `matrix` / `source_note`

### Overlap and depth

![Overlap and depth](images/slide-patterns/venn-iceberg.png)

Combines the overlap of conditions (Venn diagram) with factors that aren't visible on the surface (iceberg).

Example heading: "Overlapping conditions and hidden factors"

**figures**: `venn` / `iceberg` / `source_note`

## 6. Planning / organization pages

Pages that show time and people — when, who, and what scope.

### Schedule

![Schedule](images/slide-patterns/gantt-schedule.png)

Lays out a process along a timeline. Well suited to explaining a "no downtime" plan such as a phased migration.

Example heading: "Two-phase migration without stopping operations"

**figures**: `gantt` / `source_note`

### Roadmap

![Roadmap](images/slide-patterns/roadmap.png)

Shows a phased path forward. `journey` shows the ups and downs of an experience; `timeline` shows a sequence of points in time.

Example heading: "A phased path and a chronological sequence"

**figures**: `journey` / `timeline`

### Org chart

![Org chart](images/slide-patterns/org-chart.png)

Makes owners and roles explicit. Breaking down a question is `mece_tree`'s job; this one handles the organization.

**figures**: `orgchart` / `source_note`

### Market sizing

![Market sizing](images/slide-patterns/market-sizing.png)

Shows the target scope as nested circles (TAM / SAM / SOM). Pass them from the outside in.

**figures**: `nested_circles` / `source_note`

### Lean canvas

![Lean canvas](images/slide-patterns/lean-canvas.png)

Fits the overall picture of a business onto one slide. Don't use it while you still can't fill in every field.

**figures**: `lean_canvas`

## 7. Qualitative / technical pages

Pages that make their case without numbers — quotes, case studies, architecture diagrams, code, and the like.

### Testimonial

![Testimonial](images/slide-patterns/testimonial.png)

Shows pain points that don't show up in the numbers, through a quote. Works well placed right after a quantitative page.

**figures**: `testimonial` / `source_note`

### Case cards

![Case cards](images/slide-patterns/case-cards.png)

Lays out initiatives as cards so readers can grasp the overall picture. Put individual details in the appendix.

Example heading: "Lay out initiatives as cards to convey the overall picture"

**figures**: `asset_icon_cards` / `source_note`

### System architecture

![System architecture](images/slide-patterns/cloud-architecture.png)

Shows the layout using official cloud icons. **Requires fetching vendor icons** (see above).

**figures**: `cloud_zone` / `cloud_icon_row` / `so_what` / `source_note`

### Code sample

![Code sample](images/slide-patterns/code-sample.png)

Trim it down to an amount that's readable on screen. Move long code to the appendix and keep only the key points in the body.

Example heading: "Show the specifics of the implementation"

**figures**: `lead_in` / `code_block` / `cards` / `source_note`

### Pictogram grid

![Pictogram grid](images/slide-patterns/pictogram-grid.png)

Organizes business vocabulary with icons. Can be placed at the opening in place of a glossary.

**figures**: `asset_icon_grid` / `source_note`

## 8. Closing / appendix pages

Pages that handle decisions and what comes after. The principle is to keep the main body thin and the appendix thick.

### Decisions

![Decisions](images/slide-patterns/decisions.png)

Puts what needs a Yes/No answer onto one slide. Defines the exit point of the meeting right here.

**figures**: `table` / `source_note`

### Next steps

![Next steps](images/slide-patterns/next-steps.png)

Who does what by when. Don't write a line that lacks a subject and a deadline.

**figures**: `flow` / `table` / `source_note`

### Appendix

![Appendix](images/slide-patterns/appendix-index.png)

An exhibit index showing where each is referenced from in the body. Keep it in sync with the numbering in `exhibit_frame`.

**figures**: `table` / `source_note`

---

The images are the rendered output of `examples/slide-pattern-index.json` (the `scalar-2026` template, MEDIUM thumbnails).
When adding a pattern, add one page to that spec first, then rebuild with the commands above.
