# Slide template design rules

## Contents

- Page skeletons
- Portable coordinates
- Density and text
- Sources and inference
- Visual QA

## Page skeletons

Use the six skeletons defined in `references/slide-patterns.md`:

- A: full-width exhibit
- B: left exhibit plus right insight
- C: two exhibits
- D: two horizontal levels
- E: full-width exhibit plus bottom insight
- F: text/table only

Default to B for read-alone analysis and A for presentation slides. One slide
must make one claim.

## Portable coordinates

Portable templates use a 10 × 5.625 inch page and `BLANK` layout:

- `governing_message`: x 0.5, y 0.42, w 9.0
- main figure top: about y 1.05
- source line: x 0.5, y no lower than 4.9, w 9.0
- keep substantive figures above the footer safe area

Use Canvas palette values through existing primitives. Do not hard-code a
brand color in a portable template.

## Density and text

- Title: conclusion, not a topic label; no more than two lines.
- Body: 12pt or larger where practical. This applies to the presentation
  density; a `print` density variant (read-alone handout) may go down to
  9–10pt body / 7.5pt source line.
- Tables: roughly ten rows maximum; split rather than shrink.
- When a template declares `$density` variants (see template-schema.md), size
  the two densities from this baseline: **print** ≈ 9–10pt table text, up to
  7–8 rows under a lead-in, longer slot caps; **presentation** ≈ 11–12pt,
   4–5 rows, roughly 60% of the print character caps. Keep the figure skeleton
  identical — only sizes, row heights, caps, and coordinates may differ.
- Table column alignment is semantic — set `aligns` explicitly instead of
  trusting the primitive default (first col START, rest CENTER): short uniform
  values (年, 年月, ID) → CENTER, numbers → END, sentences → START.
- Text next to a marker (●, ◆, bar end) needs visible breathing room; center
  the label vertically in its box (`valign: MIDDLE`) rather than letting it
  hug the marker.
- Use declared slot limits to prevent category and label overload.
- Validate representative Japanese and English strings when the template is
  intended for both languages. ASCII-heavy bold labels ("Go/No-Go") are wider
  than the width estimator assumes — they are the first thing to test in
  thumbnails, because the offline audit shares the estimator with the renderer
  and cannot see the wrap.

## Sources and inference

Numeric templates require a source line. Include period, unit, sample size, and
definition when they change interpretation.

Never present attribution as incrementality, correlation as causation, or a
forecast as an observed result. Encode the warning in `guardrails` and include
an on-slide note when the risk is material.

## Visual QA

Offline validation proves geometry, not communication. In the catalog preview,
check awkward wrapping, hierarchy, contrast, semantic arrow attachment, source
legibility, and master/footer collisions. Run the squint test: the main claim
must be the first thing seen.
