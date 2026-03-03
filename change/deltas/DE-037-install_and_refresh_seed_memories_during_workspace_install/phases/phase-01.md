---
id: IP-037.PHASE-01
slug: 037-install_and_refresh_seed_memories_during_workspace_install-phase-01
name: IP-037 Phase 01
created: '2026-03-04'
updated: '2026-03-04'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-037.PHASE-01
plan: IP-037
delta: DE-037
objective: >-
  Classify existing memory corpus into spec-driver/unmanaged buckets,
  author 2 seed project stubs, retire the `seed` tag as bucket classifier,
  and configure wheel build to bundle memories.
entrance_criteria:
  - Bucket model and classifier agreed (DE-037 §9)
  - Replace semantics agreed (seed never overwrite; spec-driver refresh)
exit_criteria:
  - Corpus classified: every memory file in memory/ assigned to spec-driver, seed, or unmanaged bucket
  - 2 seed stubs authored (mem.pattern.project.workflow, mem.pattern.project.completion)
  - Stale `seed` tags removed from memory frontmatter
  - pyproject.toml force-include configured for wheel builds
  - Classification report (VA-037-001) recorded in notes.md
verification:
  tests: []
  evidence:
    - VA-037-001 classification report in notes.md
tasks:
  - id: '1.1'
    description: Author mem.pattern.project.workflow seed stub
  - id: '1.2'
    description: Author mem.pattern.project.completion seed stub
  - id: '1.3'
    description: Remove stale seed tags from memory frontmatter
  - id: '1.4'
    description: Add hatch force-include for memory in pyproject.toml
  - id: '1.5'
    description: Produce VA-037-001 classification report
risks:
  - description: Seed stubs reference platform memories that may evolve
    mitigation: Stubs use wikilinks; content changes in platform memories are transparent
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-037.PHASE-01
```

# Phase 0 — Classification & Sifting

## 1. Objective
Classify existing memory corpus into two managed buckets (spec-driver, seed) plus unmanaged, author seed project stubs, retire the `seed` tag, and configure wheel packaging.

## 2. Links & References
- **Delta**: DE-037 (§9 Classification Decision)
- **Design Revision**: DR-037
- **IP**: IP-037

## 3. Entrance Criteria
- [x] Bucket model and classifier agreed (DE-037 §9 — namespace-based)
- [x] Replace semantics agreed (seed: never overwrite; spec-driver: refresh)

## 4. Exit Criteria / Done When
- [x] Every memory file classified into spec-driver / seed / unmanaged
- [x] 2 seed stubs authored
- [x] Stale `seed` tags removed from frontmatter
- [x] pyproject.toml force-include configured
- [x] VA-037-001 classification report in notes.md

## 5. Verification
- VA-037-001: classification report documenting all 27 memory files (22 spec-driver + 3 unmanaged + 2 new seed)

## 6. Assumptions & STOP Conditions
- Assumptions: namespace classifier is sufficient; no manifest file needed in Phase 0
- STOP when: any memory file cannot be unambiguously classified by namespace

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 1.1 | Author mem.pattern.project.workflow seed stub | [P] | Thin stub referencing core-loop |
| [x] | 1.2 | Author mem.pattern.project.completion seed stub | [P] | Thin stub referencing delta-completion |
| [x] | 1.3 | Remove stale `seed` tags from memory frontmatter | [P] | Removed from 19 files |
| [x] | 1.4 | Add hatch force-include for memory in pyproject.toml | [P] | `"memory" = "supekku/memory"` |
| [x] | 1.5 | Produce VA-037-001 classification report | | 22 spec-driver / 2 seed / 3 unmanaged |

## 8. Risks & Mitigations
| Risk | Mitigation | Status |
| --- | --- | --- |
| Seed stubs reference platform memories that may evolve | Stubs use wikilinks; platform content changes are transparent | open |

## 9. Decisions & Outcomes
- `2026-03-04` - Bucket classifier: ID namespace (`mem.*.spec-driver.*` / `mem.*.project.*`), not tags (DE-037 §9)
- `2026-03-04` - 3 non-spec-driver memories (`assembly-only-taxonomy`, `cli.skinny`, `formatters.soc`) are local/unmanaged
- `2026-03-04` - Package source: dual discovery + hatch force-include; no parallel copies
- `2026-03-04` - Managed prune: yes with notice; no backup; emit "left seed untouched" notices

## 10. Findings / Research Notes
- Current corpus: 25 files in `memory/`, 22 match `mem.*.spec-driver.*`, 3 do not

## 11. Wrap-up Checklist
- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Spec/Delta/Plan updated with lessons
- [ ] Hand-off notes to next phase (if any)
