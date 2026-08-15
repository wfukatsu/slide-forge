---
status: complete
priority: p1
issue_id: "001"
tags: [agents, skills, token-cost, claude-code, codex, antigravity]
dependencies: []
---

# Reduce agent and skill token cost

## Problem Statement

The deck workflow repeatedly loads large and overlapping instructions. Claude Code is the primary host, while Codex and Antigravity must continue to use the same engine and shared skills without maintaining divergent workflow logic.

## Findings

- `skills/google-slides-template/SKILL.md` is 625 lines and about 42 KB.
- `forge`, leaf generation skills, and `slide-qa` repeat intake, validation, QA, and reporting rules.
- Mandatory fan-out above 12 slides increases total tokens by making workers reread references.
- Full-deck thumbnail reinspection makes QA cost scale with both page count and repair iterations.
- Host-specific files repeat shared behavior that should be owned by Claude-first shared skills and contracts.

## Proposed Solutions

### Option 1: Incremental trimming

Remove obvious duplicate tables while keeping the current structure.

**Pros:** Low migration risk.

**Cons:** Leaves unclear ownership and most repeated context intact.

**Effort:** Medium

**Risk:** Low

### Option 2: Shared contracts with thin host adapters

Make the Claude-distributed shared skills authoritative, extract compact workflow/reference routing contracts, and reduce Codex/Antigravity instructions to compatibility adapters.

**Pros:** Largest durable reduction; prevents host drift.

**Cons:** Requires coordinated documentation updates.

**Effort:** High

**Risk:** Medium

## Recommended Action

Implement Option 2. Keep safety, approval, snapshot, offline validation, and visual-QA gates unchanged. Use progressive disclosure for detailed references and complexity-based fan-out.

## Technical Details

**Affected files:**

- `commands/forge.md`, `commands/forge.ja.md`
- `.agents/skills/forge/SKILL.md`
- `skills/google-slides-template/SKILL.md`
- `skills/google-slides/SKILL.md`
- `skills/slide-qa/SKILL.md`
- `references/parallel-generation.md`
- Host compatibility instructions and shared workflow references

## Acceptance Criteria

- [x] Claude Code is documented as the primary distribution and behavior owner.
- [x] Codex and Antigravity use thin adapters over shared skills.
- [x] `google-slides-template/SKILL.md` is under 15 KB or 200 lines.
- [x] Forge no longer duplicates leaf-skill implementation details.
- [x] Fan-out is based on complexity and normally starts at 18–20 pages.
- [x] Reference reading is routed to named sections/files only when needed.
- [x] QA performs full initial inspection and impact-scoped reinspection after fixes.
- [x] English/Japanese and host compatibility references remain coherent.
- [x] Documentation and offline validation pass.

## Work Log

### 2026-08-15 - Implementation started

**By:** Codex

**Actions:**

- Reviewed host entry points, skill sizes, reference chains, and existing dirty worktree.
- Selected Claude-first shared skills with thin Codex/Antigravity adapters.

**Learnings:**

- The shared `skills/` tree is already the Claude plugin distribution source and the best authority.
- The existing parallel-generation guide explicitly acknowledges that delegation increases total token usage.

### 2026-08-15 - Implementation completed

**By:** Codex

**Actions:**

- Added shared deck, Scalar workflow, and Scalar research contracts.
- Reduced `google-slides-template/SKILL.md` from 625 lines / 42 KB to 188 lines / 7.6 KB.
- Reduced Claude and Codex forge entry points to routing and state-transition instructions.
- Made Claude Code primary and Codex/Antigravity thin adapters over shared skills.
- Changed authoring fan-out to a complexity-based 18–20-page guideline.
- Required full initial QA and impact-scoped repair QA.
- Ran scoped `git diff --check`, Python compileall, strict deck dry-run, and spreadsheet dry-run successfully.

**Learnings:**

- A compact shared contract preserves safety gates while removing repeated workflow prose.
- Image QA benefits from delegation only when context pressure exceeds coordination overhead.
