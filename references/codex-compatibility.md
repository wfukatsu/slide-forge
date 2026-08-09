# Codex compatibility

slide-forge uses one engine and one set of skills for Codex and Claude Code.
The Python scripts, JSON schemas, templates, and validation commands are
host-independent. Only skill discovery, interactive questions, visual file
inspection, and optional work delegation differ between hosts.

## Installation in a repository clone

The repository exposes its skills through `.agents/skills/`:

```text
.agents/skills/forge/SKILL.md
.agents/skills/google-slides -> ../../skills/google-slides
...
```

Start Codex in the repository root. It should discover `AGENTS.md` and the
skills below `.agents/skills/`. The symlinks deliberately point at the shared
`skills/` directories so Claude and Codex cannot drift onto different copies.

The Claude marketplace manifest at `.claude-plugin/marketplace.json` remains
the Claude Code distribution mechanism. Codex does not need that manifest and
does not install `commands/forge.md` as a Claude-style namespaced command.
Invoke the `forge` skill by name instead.

## Runtime setup

Codex uses the same repository-local entry point as every other host:

```bash
.venv/bin/python scripts/list_templates.py
```

The real virtual environment may live anywhere; `.venv` may be a symlink.
References to `~/.claude/venvs/gslides` in legacy setup examples describe the
existing shared environment, not a Codex requirement.

OAuth resolution is host-independent:

1. `$GSLIDES_CONFIG_DIR`
2. `config/` in the repository root
3. the legacy Claude skill configuration path

Google API writes may require user approval or an OAuth browser flow depending
on the Codex sandbox. Offline `--dry-run` validation does not require network
access and must run first.

## Interactive questions

When a skill says `AskUserQuestion` or `ask_question`, use the interaction
mechanism available in the current Codex session. If no structured question
tool is available, print numbered options in chat and wait for the answer.
Outline approval remains a hard gate even though the UI differs.

## Visual QA

When a skill says to open an image with `Read`, use Codex's image-viewing
capability. Text-file reads are not a substitute. Inspect every requested page
at sufficient resolution, report defects by slide number, fix the source spec,
regenerate, and clean up the thumbnails.

## Parallel and sequential execution

`references/parallel-generation.md` describes a performance optimization, not
a correctness requirement. If Codex is allowed to delegate, it may use that
workflow. If delegation is unavailable or prohibited, create the same numbered
page fragments sequentially in the main agent, validate each fragment, then
assemble and validate the complete deck. QA page ranges can likewise be
inspected sequentially. This preserves output and validation behavior at the
cost of additional wall-clock time and main-context usage.

## Compatibility checklist

- Codex discovers all eleven skills under `.agents/skills/`.
- `.venv/bin/python -m pip check` succeeds.
- `scripts/` compiles without syntax errors.
- A representative deck spec passes `build_deck.py --dry-run --strict`.
- `examples/estimate-sample.json` passes `build_sheet.py --dry-run`.
- Google OAuth and optional draw.io/Gemini prerequisites are checked only for
  workflows that use them.
