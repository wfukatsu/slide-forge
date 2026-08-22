---
description: Route and run the shared slide-forge deck workflow end to end.
argument-hint: "[theme / template URL / material path / customer name, etc.]"
---

*[日本語](forge.ja.md)*

# /forge — Deck Generation Pipeline

Claude Code is the primary host for this command. Starting from `$ARGUMENTS`,
run the shared workflow in `references/workflow-contract.md`. Work from
`${CLAUDE_PLUGIN_ROOT}` for the plugin or the repository root for a local clone.

## Choose one generation skill

Pick one based on the arguments and context. Only ask once via
`AskUserQuestion` if it's unclear.

| Type of request | Skill to use |
|---|---|
| Deck introducing Scalar's company / products / features | `scalar-product-slides` |
| Scalar solution proposal starting from a customer problem | `scalar-proposal-slides` |
| Building a reusable, single-slide-unit template | `slide-template-creator` |
| Current-state analysis / problem identification from material (SWOT, PEST, Five Forces, why-why, logic tree, gap analysis, etc.) | `current-state-analysis` |
| Adding or changing an analysis-framework template itself | `analysis-template-creator` |
| B2B deal stakeholder map / discovery organization | `b2b-account-maps` |
| Slides that collect information from the customer (hearing agenda, fill-in sheet, event poll) | `hearing-slides` |
| Explaining a nexus-architect project's reports / UI mocks | `nexus-report-slides` |
| A template/master URL exists, build with a registered template (default) | `google-slides-template` |
| Build from scratch with no corporate master | `google-slides` |

Load the selected skill completely, then follow it and the shared contract.
Do not load unselected generation skills. Ask only for missing branch
decisions, including QA (default: run), relevant delivery formats, and density
(`print` for proposals/handouts, `presentation` for talks). Read
`config/settings.json` first (`scripts/settings.py --show`) — it may already
settle image generation and the deliverable destination; route a request to
change them to the `settings` skill.

The outline approval gate is mandatory. After approval, continue through
validation, generation, selected QA, optional deliverables, cleanup, and report
without another routine confirmation.
