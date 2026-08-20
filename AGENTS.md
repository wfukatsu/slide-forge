*[日本語](AGENTS.ja.md)*

# slide-forge agent instructions

Claude Code is the primary host and distribution path. Codex uses the same
shared Python engine and the same `skills/` through `.agents/skills/` links.
`commands/`, shared `skills/`, and `references/workflow-contract.md` own
behavior; keep this file as a thin Codex compatibility layer.

## Runtime

- Run Python commands from the repository root with `.venv/bin/python`.
- Keep OAuth credentials, tokens, generated files, and caches out of Git.
- Use `GSLIDES_LANG=ja` only when Japanese CLI output is useful; it does not
  affect generated content.
- Before changing an existing user-owned deck, follow the relevant skill's
  snapshot/version rule.

## Skill routing

Use the matching skill and read its complete `SKILL.md` before acting:

| Request | Skill |
|---|---|
| End-to-end deck workflow | `forge` |
| Registered template/master | `google-slides-template` |
| Deck without a corporate master | `google-slides` |
| Create/register a template | `template-forge` |
| Create/register a reusable single-slide content template | `slide-template-creator` |
| Current-state analysis / problem identification from supplied material | `current-state-analysis` |
| Create/change an analysis-framework slide template | `analysis-template-creator` |
| B2B stakeholder map / discovery mapping | `b2b-account-maps` |
| Per-customer activity plan / deal ledger (AE's action plan) | `scalar-account-plan` |
| Account Planning Session (annual/semi-annual stocktake and executive review) | `scalar-account-planning-session` |
| Materials for a single visit / internal approval materials (WPS, Deal Desk) | `scalar-ae-materials` |
| Scalar product/company deck | `scalar-product-slides` |
| Scalar customer proposal | `scalar-proposal-slides` |
| Dense draw.io diagram | `drawio-diagrams` |
| Fill existing image frames | `image-slots` |
| Thumbnail visual QA | `slide-qa` |
| Export Google Slides to PPTX | `pptx-export` |
| Estimate/BOM spreadsheet | `spreadsheets` |
| Change the image-generation or output-destination switches | `settings` |

After selecting a skill, do not preload the other skills or every reference it
mentions. Follow the progressive-loading table in
`references/workflow-contract.md`.

## Host-tool compatibility

Some shared skill documents retain Claude Code terminology. In Codex, apply
these mappings:

- `Read` for text: use `rg`, `sed`, or another read-only shell command.
- `Read` for PNG/JPEG: use the local image-viewing tool and inspect the actual
  pixels; filenames and API success are not visual QA.
- `Write` / `Edit`: use `apply_patch` for repository files.
- `Bash`: use the shell execution tool with the repository root as `cwd`.
- `Grep` / `Glob`: use `rg` / `rg --files` first.
- `WebFetch` / `WebSearch`: use the available web tool. Prefer official,
  primary sources for product facts and technical documentation.
- `AskUserQuestion` / `ask_question`: ask in chat. Present mutually exclusive
  choices as a numbered list and wait for the user's number; accept
  comma-separated numbers for multi-select. Do not silently choose when the
  skill requires an approval gate.
- `Task` / `Subagent` / `Parallel`: use parallel agents only when the current
  host and session instructions explicitly permit them. Otherwise follow the
  sequential fallback in `references/parallel-generation.md`.
- `${CLAUDE_PLUGIN_ROOT}`: resolve to this repository root. Never depend on the
  variable being set under Codex.

Detailed Codex setup and known differences are in
`references/codex-compatibility.md`.

## Safety and validation

- Run the documented offline `--dry-run`/layout validation before API writes.
- Never expose the contents of `config/credentials.json`, `config/token.json`,
  or API-key files.
- `accounts/` holds per-customer sales ledgers — named individuals and
  judgements about them. It is ignored by Git; never commit it, never paste it
  into a customer-facing artifact, and never share the `00_活動計画` /
  `90_社内` Drive folders with a customer or partner.
- Keep generated page fragments and QA thumbnails under ignored `out/` paths.
- A successful API response is not visual QA. When QA is selected, inspect the
  thumbnails and run `scripts/cleanup_qa.py` before reporting completion.
