# Deck workflow contract

This is the single shared contract for end-to-end deck generation. Claude Code
is the primary distribution host. Codex and Antigravity use the same `skills/`
and Python engine through thin host adapters.

## Required states

1. **Route** — select exactly one generation skill. Load that skill completely.
2. **Intake** — ask only for missing branch decisions. Use
   `interactive-intake.md` only for the applicable question set. Read
   `config/settings.json` first (`scripts/settings.py --show`) and drop the
   questions it already answers — Gemini image generation on/off, and whether
   the deliverable is Google Slides or a local `.pptx` (`references/settings.md`).
3. **Approve** — show page count, layout, and every action title. Do not write
   the deck before explicit approval unless the user already supplied and
   approved that outline.
4. **Author** — create the spec or deck module. Load only the references needed
   by the chosen components; use the routing table in the generation skill.
5. **Validate** — run offline strict validation before any API write.
6. **Generate** — create the Drive folder first, then generate and upload the
   editable sources. Remove a partial deck after a failed generation.
7. **Verify** — when QA was selected, follow `slide-qa` and clean local QA files.
8. **Deliver** — run optional PPTX or spreadsheet skills only after the deck is
   final. Report URLs, local deliverables, QA scope/results, and cleanup. Under
   `output: local` the generator already exported the `.pptx` on its last run;
   report that path instead of exporting again.

After outline approval, continue through delivery without another approval
gate. A missing credential, external permission, destructive target ambiguity,
or materially changed scope may still require user input.

## Invariants

- Snapshot a user-owned deck before editing it in place.
- Treat full-deck replacement as destructive. `build_deck.py --into` is allowed
  only when a complete source spec exists, the target is confirmed to be a
  generated deck rather than its master, a snapshot succeeded, and the user
  explicitly approved replacing every page. A request to edit, insert, or fix
  one page does not authorize bare `--into`; route local fixes to `--into
  <deck> --update-slides <pages>`. Partial updates still require a complete
  source spec, snapshot, strict validation, template match, and live page-count
  match; they preserve every unselected slide but assign new IDs to replaced slides.
- Never expose credentials, tokens, API keys, or account-ledger internals.
- Never put named-person judgements or internal sales material in a
  customer-facing artifact.
- API success is not visual QA.
- Fix the source and regenerate; do not hide source defects by patching only the
  generated artifact.
- Preserve one final customer-facing URL and remove superseded artifacts made
  during the current run.

## Progressive reference loading

Do not preload every file named by a skill. Read the complete selected
`SKILL.md`, then load only references activated by the task:

| Trigger | Load |
|---|---|
| Missing intake decision | Relevant sections of `interactive-intake.md` |
| Spec schema or placeholders | `template-schema.md` |
| Canvas or connectors | `diagrams.md`; add `diagram-cookbook.md` only for a matching recipe |
| Chart or table | Matching section of `charts.md` |
| Business framework | Matching section of `patterns.md` |
| Page skeleton | Matching section of `slide-patterns.md` |
| Ready-made one-page template (`$template`) | `list_slide_templates.py --tag <term>` to find it, then that template's `template.json` for its slots. Open `slide-template-catalog.md` only to browse the rendered images |
| Seminar / event announcement figure | Matching section of `events.md` |
| Pictogram or icon by name | `illustrations.py --list` (or `--search <term>`) for the valid names; `diagrams.md` for placement |
| Image or image slot | Matching sections of `images.md` |
| Cloud icon | Matching section of `cloud-icons.md` |
| Code block | `code-blocks.md` |
| API error or measured constraint | Search `api-notes.md`; use `google-slides-api.md` only when unresolved |
| Large/complex authoring or QA | Applicable sections of `parallel-generation.md` |
| Visual QA | `slide-qa/SKILL.md` and Gate 2 of `validation.md` |

Search a long reference for the relevant heading first. Do not read a catalog
or API manual in full when one section answers the task.

## Delegation policy

Delegation optimizes elapsed time and main-agent context, not total tokens.
Keep authoring in one agent for ordinary decks up to 17 pages. Consider page
fan-out at 18–20 pages, or earlier only when independent page groups require
different complex figures. Give each worker 2–3 related pages and at most two
named reference sections.

QA may be split into ranges when images would crowd the main context. Workers
return findings only, never image descriptions or generated JSON.

## Visual QA scope

- First QA pass: inspect every page.
- After a local page fix: inspect the changed page and its adjacent pages.
- After a shared layout/component fix: inspect every page using it.
- After a master, theme, footer, or page-number change: inspect every page.
- Run offline audits before opening thumbnails; they reduce avoidable image
  review but never replace the first visual pass.
