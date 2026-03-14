---
id: IP-077.PHASE-03
slug: 077-cli_ux_schema_discoverability_and_flag_parsing-phase-03
name: 'IP-077 Phase 03: Skills and memory coverage'
created: '2026-03-09'
updated: '2026-03-09'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-077.PHASE-03
plan: IP-077
delta: DE-077
objective: >-
  Ensure spec-driver skills and memories reflect the new CLI behaviour —
  schema hints, --from-backlog shape change, and hints.py module
entrance_criteria:
  - Phase 2 complete (all checks green)
exit_criteria:
  - Relevant skills mention schema hint output where useful
  - Memory records current for CLI create command behaviour
  - No stale guidance about --from-backlog as string option
verification:
  tests: []
  evidence:
    - VA-077-skills-current
    - VA-077-memory-coverage
tasks:
  - id: "3.1"
    description: Audit skills that reference create commands or --from-backlog
  - id: "3.2"
    description: Check memory records for CLI create behaviour
  - id: "3.3"
    description: Update or create memories as needed
  - id: "3.4"
    description: Update spec-driver skill tips if schema hints should be mentioned
risks: []
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-077.PHASE-03
```

# Phase 3 — Skills and memory coverage

## 1. Objective

Ensure that agent-facing guidance (skills and memories) reflects the new CLI behaviour introduced in phases 1–2. Prevent future agents from:

- Not knowing about schema hint output after creation
- Using the old `--from-backlog ITEM-ID` string option shape
- Not knowing about `supekku/cli/hints.py` as the home for schema hint logic

## 2. Links & References

- **Delta**: DE-077
- **Phase 1–2**: `phases/phase-01.md`, `phases/phase-02.md`
- **Skill**: `/spec-driver` — references `create` commands
- **Memory candidates**: `mem.signpost.spec-driver.file-map`, CLI-related memories

## 3. Entrance Criteria

- [ ] Phase 2 complete (all checks green)

## 4. Exit Criteria / Done When

- [ ] Skills that reference `create` or `--from-backlog` are current
- [ ] Memory records for CLI create behaviour are current
- [ ] No stale guidance about `--from-backlog` as string option anywhere in memories/skills
- [ ] `hints.py` discoverable via file-map or relevant memory

## 5. Verification

- VA-077-skills-current: grep skills for `--from-backlog`, `create delta`, schema hint references
- VA-077-memory-coverage: `spec-driver list memories -c "create"` and review

## 7. Tasks & Progress

| Status | ID  | Description                                           | Parallel? | Notes         |
| ------ | --- | ----------------------------------------------------- | --------- | ------------- |
| [ ]    | 3.1 | Grep skills for stale `--from-backlog` references     | [P]       |               |
| [ ]    | 3.2 | Search memories for CLI create behaviour              | [P]       |               |
| [ ]    | 3.3 | Update/create memory records as needed                |           | After 3.1–3.2 |
| [ ]    | 3.4 | Update skill tips if schema hints should be mentioned |           | After 3.1–3.2 |

### Task Details

- **3.1 Audit skills**
  - Grep `.claude/skills/` and `.spec-driver/agents/` for `--from-backlog`, `create delta`, `create.*backlog`
  - Fix any stale references

- **3.2 Check memories**
  - `spec-driver list memories -c "create"` and `-c "cli"`
  - Check `mem.signpost.spec-driver.file-map` for `hints.py` coverage
  - Check for any memory mentioning `--from-backlog` old shape

- **3.3 Update/create memories**
  - If `hints.py` not in file-map memory, add it
  - If `--from-backlog` shape change not documented, create or update relevant memory
  - If schema hints post-creation not mentioned, capture as pattern

- **3.4 Update skill tips**
  - `/spec-driver` skill mentions `--from-backlog` in common commands — update if stale
