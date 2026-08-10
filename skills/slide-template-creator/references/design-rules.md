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
- Body: 12pt or larger where practical.
- Tables: roughly ten rows maximum; split rather than shrink.
- Use declared slot limits to prevent category and label overload.
- Validate representative Japanese and English strings when the template is
  intended for both languages.

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
