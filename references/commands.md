*[日本語](commands.ja.md)*

# Slash commands

Three commands ship with the plugin. They are the entry point most people
actually use: a command routes to a skill, so you do not have to know which of
the 24 skills fits before you start.

| Command | Argument | What it produces |
|---|---|---|
| `/forge` | theme, template URL, material path, customer name … | A deck, end to end |
| `/account` | `<customer name> [new \| update \| show] [notes path]` | A customer's activity plan, at a URL that never changes |
| `/visit` | `<customer name> [purpose / counterpart / phase] [notes path]` | One visit's materials, filed in Drive |

On Claude Code they are `/forge`, `/account`, `/visit` — or
`/slide-forge:forge` when installed from the marketplace. On Codex, invoke the
`forge` skill by name; `/account` and `/visit` are Claude Code commands.
All three follow [workflow-contract.md](workflow-contract.md).

## `/forge` — deck generation

Routes to exactly one generation skill, then runs intake → outline approval →
spec → offline validation → generation → optional visual QA → cleanup →
optional PPTX or spreadsheet → report.

It picks the skill from your arguments, asking once only when the choice is
genuinely unclear. The routing table lives in
[`commands/forge.md`](../commands/forge.md); in summary, a request for a Scalar
product or proposal deck, an analysis framework, calendar slides, a B2B
stakeholder map, information-collecting slides, or a nexus-architect
explanation each has its own skill, and anything else falls to
`google-slides-template` when a master exists or `google-slides` when it does
not.

**The outline approval gate is mandatory.** After you approve the page count,
layouts and action titles, the command runs through to delivery without asking
again.

## `/account` — customer activity plan

Reads the customer's ledger, records what came out of the last meeting, checks
the playbook's ten review questions, turns every unanswered one into an action
with a person to ask and a deadline, and replaces the contents of the same
activity-plan deck so the shared link keeps working.

What the ledger cannot answer becomes the deliverable, rather than being
quietly dropped.

## `/visit` — one visit's materials

Routes deal phase × counterpart × purpose to the right material type, so the
customer-facing one-pager, the internal visit plan, the win plan and the
approval packet never end up in the same file. It checks that no judgement
about a named individual, competitor weakness or unconfirmed figure reaches
anything a customer will read, generates and files each artifact, then writes
the visit back to the ledger and refreshes the activity plan.

## Where the state lives

`/account` and `/visit` keep their source of truth in
`accounts/<AE name>/<customer name>/account.json`, which is gitignored and
never committed. Output is filed under `<Drive root>/<AE name>/<customer
name>/`; the Drive root is asked once and remembered in `config/sales.json`.

## See also

- [Deck workflow contract](workflow-contract.md)
- [Nailing Down a Deck's Design Through Dialogue](interactive-intake.md)
- [Where the Codex host differs](codex-compatibility.md)
