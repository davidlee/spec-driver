# Agent Workflow Context Brief (Core Loop)

This brief is for a fresh agent joining work on the core loop:

`revision -> DR -> delta -> IP -> phase(s) -> audit -> spec/closure updates`

## Source Priority (What To Read First)

Use this order for operational truth:

1. `supekku/about/README.md`
   - High-level loop and artifact intent.
2. `supekku/about/processes.md`
   - Command-level operational flow by artifact type.
3. `docs/commands-workflow.md`
   - Ceremony modes, permutations, closure contract, truth model.
4. `docs/delta-completion-workflow.md`
   - Detailed close-out mechanics and checklist.
5. `supekku/about/lifecycle.md`
   - Traceability semantics (`implemented_by`, `verified_by`) and sync behavior.
6. `.spec-driver/workflow.toml`
   - Active project mode/toggles/paths for this repo.
7. `.spec-driver/agents/{exec,workflow,glossary,policy}.md`
   - Generated project-local guidance consumed by `/boot`.

## Current Repo Posture (From workflow.toml)

- Ceremony: `pioneer`
- Cards: enabled (`kanban`, lanes configured)
- Contracts: enabled (`.contracts`)
- Policy toggles: ADRs enabled; policies/standards disabled
- Command prefix: `uv run spec-driver`
- Verification command: `just check`

## Fast Orientation Checklist For New Agents

1. Run `/boot`.
2. Confirm current ceremony and enabled primitives from `.spec-driver/workflow.toml`.
3. Identify the owning record for current work:
   - revision, delta, phase sheet, audit, card, or spec requirement.
4. Follow closure contract from `docs/commands-workflow.md`:
   - update owning records, not floating narrative.
5. For completion work, use `docs/delta-completion-workflow.md` checklist.

## Where Ambiguity Exists Today

- Sequence variance:
  - `README/processes` present `delta -> DR -> IP -> phase`.
  - Some planning discussions also consider `revision -> DR -> delta`.
- Status vocabulary drift across docs:
  - some places use `verified`, others `passed` for verification entries.
- `lifecycle.md` includes historical notes (`FIXME`) and should be treated as guidance plus caveats.

When sources disagree, prefer:
`commands-workflow.md` for workflow behavior, then `processes.md` for command mechanics.

## Diagram Index (Core Loop Slices)

- `workflow-core-loop.dot`
- `workflow-phase-execution-subloop.dot`
- `workflow-audit-feedback-paths.dot`

These are intentionally small, task-focused views and should be edited incrementally as guidance is clarified.
