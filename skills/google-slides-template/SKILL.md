---
name: google-slides-template
description: >-
  Generate or update Google Slides from a registered master/template with
  interactive intake, strict offline validation, Drive source collection, and
  optional visual QA. Use when a template URL or registered template exists.
---

*[日本語](SKILL.ja.md)*

# Google Slides from a template

Claude Code is the primary host for this shared skill. Codex and Antigravity
run the same procedure through their host adapters. Work from the slide-forge
repository root with `.venv/bin/python`.

Read this file completely. Then follow `references/workflow-contract.md`.
Load detailed references only when activated by the routing table below.

## Scope

Use this skill to:

- generate a new deck from a registered template;
- inspect and register a supplied, unregistered master before generation;
- update a user-owned templated deck in place when its URL must remain stable.

Use `google-slides` for a deck without a corporate master, `template-forge` to
create a new master design, and `image-slots` when the only task is filling
empty image frames in an existing deck.

## Non-negotiable rules

- Before editing a user-owned deck in place, run
  `.venv/bin/python scripts/snapshot_version.py <URL>` and report the revision.
- Ask only for missing branch decisions; never ask again for supplied or
  delegated (`your call`) decisions.
- Get explicit approval for page count, layout, and every action title before
  authoring, unless that exact outline was already approved.
- Run strict offline validation before every API write.
- Template decorations, logos, and footers are inherited. Do not redraw them.
- Fix the source spec and regenerate. Do not patch around a source defect only
  in the generated artifact.
- API success is not visual QA. When QA is selected, follow `slide-qa`.
- Keep credentials, tokens, generated fragments, and QA images out of Git.

## Reference routing

Read only the selected row's file or relevant section. Search long references
for the named topic before opening a large range.

| Need | Load |
|---|---|
| Intake questions or final adjustment choices | Applicable sections of `references/interactive-intake.md` |
| Spec fields, placeholders, body roles, image slots | `references/template-schema.md` |
| Canvas, flows, connectors | Relevant section of `references/diagrams.md` |
| Dense architecture diagram | `drawio-diagrams` skill; then its routed `drawio.md` section |
| Chart/table | Matching component in `references/charts.md` |
| Business framework | Matching component in `references/patterns.md` |
| Page skeleton/density | Matching skeleton in `references/slide-patterns.md` |
| Image generation/placement | Matching sections in `references/images.md` |
| Scalar or cloud icons | `icons.md` or matching section of `cloud-icons.md` |
| Code sample | `references/code-blocks.md` |
| Outline model | One matching outline in `references/deck-outlines.md` |
| API failure or measured constraint | Search `references/api-notes.md`; use `google-slides-api.md` only if unresolved |
| Large/complex deck | Applicable sections of `references/parallel-generation.md` |
| Visual QA | `slide-qa/SKILL.md` and Gate 2 of `references/validation.md` |

Do not preload catalogs, all Composer guides, all figure-family manuals, or
the complete Google Slides API manual.

## Phase 0: Check the environment

Confirm the repository-local entry point works without exposing secrets:

```bash
.venv/bin/python scripts/list_templates.py
```

Credentials are resolved by `GSLIDES_CONFIG_DIR`, repository `config/`, then
the legacy Claude skill location. Only investigate authentication when a live
operation needs it.

## Phase 1: Settle premises and approve the outline

Determine the template, audience/purpose, page count, outline, density, Drive
folder, QA choice, and relevant delivery formats. Batch only missing decisions
into one or two question rounds. QA defaults to run.

Purpose selects density for `$density` templates:

- proposal, internal review, or handout: `print`;
- projected talk: `presentation`.

List registered templates when needed:

```bash
.venv/bin/python scripts/list_templates.py --json
```

Present the proposed page count, layout for every page, and every action title.
Stop for approval. After approval, continue through delivery without another
routine gate.

## Phase 2: Register only when necessary

Skip this phase for an already registered template. For a new URL, inspect and
emit a template definition:

```bash
.venv/bin/python scripts/inspect_template.py <URL> \
  --emit templates/<id>.json --name <id> --thumbnails out/<deck>/layouts
```

Inspect the actual layout thumbnails. Verify title/body roles, decorations,
image slots, and safe areas. Keep any template-provided roles that inspection
verified; do not guess role mappings from names alone.

## Phase 3: Author and validate

Write one spec against the selected `templates/<id>.json`. Use an action title
for every content page. Choose only the figure family needed for each message,
then load its routed reference.

Validate before any API call:

```bash
.venv/bin/python scripts/build_deck.py \
  --template templates/<id>.json --spec out/<deck>/deck.json \
  --dry-run --strict
```

Resolve every error. Review warnings and record any intentionally accepted
warning. Ordinary decks up to 17 pages stay in one agent. Consider fan-out at
18–20 pages, or earlier only for independent groups of complex figures. When
splitting, follow `parallel-generation.md`: 2–3 related pages per worker, at
most two named reference sections, self-validation, and findings/path-only
returns.

## Phase 4: Generate and collect sources

Create the Drive folder first, generate once, and upload editable sources:

```bash
.venv/bin/python scripts/drive_folder.py create "<Deck title>"
.venv/bin/python scripts/build_deck.py \
  --template templates/<id>.json --spec out/<deck>/deck.json \
  --title "<Deck title>" --folder "<folder URL or ID>"
.venv/bin/python scripts/drive_folder.py upload \
  "<folder URL or ID>" out/<deck>/deck.json out/<deck>/figures/*
```

If generation fails, remove the partial deck made by this run before retrying.
For an approved in-place update, use the builder's supported `--into` path only
after the snapshot rule has passed.

## Phase 5: Verify and deliver

When QA was selected, invoke `slide-qa`. Its first pass inspects every page.
After a fix, reinspect only the changed page plus adjacent pages unless a
shared layout, master, theme, footer, or page-number change expands the impact
scope. Clean local QA files at the end.

Run `pptx-export` or `spreadsheets` only against the final verified deck. Make
spreadsheet totals agree with slide summaries.

Report:

1. presentation and Drive-folder URLs;
2. spec/source locations and optional deliverables;
3. offline validation result;
4. QA scope, defects fixed, remaining limitations, and cleanup—or that QA was
   explicitly skipped;
5. final adjustment choices from the relevant intake section.

## Minimal command index

| Task | Command/owner |
|---|---|
| List templates | `scripts/list_templates.py` |
| Inspect/register template | `scripts/inspect_template.py` |
| Validate/generate spec | `scripts/build_deck.py` |
| Snapshot existing deck | `scripts/snapshot_version.py` |
| Create/upload Drive folder | `scripts/drive_folder.py` |
| Assemble fragments | `scripts/assemble_spec.py` |
| Visual QA | `slide-qa` skill |
| Export PowerPoint | `pptx-export` skill |
| Build estimate/BOM | `spreadsheets` skill |
