# Notes for DE-038

## 2026-03-03
- Added [IP-038.md](./IP-038.md) with three phases and explicit memory-review + skill-review passes.
- Penciled in concrete review targets:
  - memory set: core-loop, revision, delta-completion, posture, ceremony signpost/settler, plus new coverage-gate + status-enums memories.
  - skill set: workflow-facing skills/templates that can affect sequencing and closure guidance.
- Captured strict-mode policy contract alignment in the plan (hard-fail non-canonical paths, no exception knobs in baseline contract).
- Captured recommended v1 coverage precedence and mixed-status warning posture in verification focus.
- No runtime/code behavior changes made.
- Verification status: `just`, `just test`, `just lint`, and `just pylint` not run in this step (documentation-only edits).

## 2026-03-03 (phase sheet setup)
- Created phase sheet via CLI: `IP-038.PHASE-01` at `phases/phase-01.md`.
- Prefilled Phase 01 (Contract Freeze) checklist, tasks, verification evidence, and wrap-up outcomes.
- Updated `IP-038.md` to point at active phase sheet.
- Surprise encountered: `create phase` appended a duplicate `IP-038.PHASE-01` entry in `supekku:plan.overview` phases list; cleaned manually in `IP-038.md`.
- Verification status: no runtime/test/lint commands run (`just`, `just test`, `just lint`, `just pylint` not run) because this was documentation-only.

## 2026-03-03 (phase 02 scaffold)
- Created phase sheet via CLI: `IP-038.PHASE-02` at `phases/phase-02.md`.
- Prefilled Phase 02 (Memory Review Pass) with execution checklist, task map (`2.1`-`2.4`), verification expectations, and stop conditions.
- Surprise encountered again: `create phase` appended duplicate `IP-038.PHASE-02` in `IP-038` plan overview; cleaned manually and switched active phase reference to `phase-02.md`.
- Verification status: no runtime/test/lint commands run (`just`, `just test`, `just lint`, `just pylint` not run) because this was documentation-only.

## 2026-03-03 (phase 03 scaffold)
- Created phase sheet via CLI: `IP-038.PHASE-03` at `phases/phase-03.md`.
- Prefilled Phase 03 (Skill Review Pass) with execution checklist, task map (`3.1`-`3.4`), verification expectations, and stop conditions.
- Duplicate `IP-038.PHASE-03` was appended by scaffold in `IP-038` plan overview; cleaned manually and active phase reference switched to `phase-03.md`.
- Verification status: no runtime/test/lint commands run (`just`, `just test`, `just lint`, `just pylint` not run) because this was documentation-only.

## 2026-03-03 (phase 02 memory review pass execution)
- Executed Phase 02 tasks `2.1`-`2.4` from `phases/phase-02.md`.
- Updated workflow-critical memories:
  - `mem.pattern.spec-driver.core-loop` (delta-first canonical narrative; revision-first now concession path)
  - `mem.concept.spec-driver.revision` (post-audit/default framing corrected; settler completion nuance added)
  - `mem.pattern.spec-driver.delta-completion` (explicit coverage gate prerequisites and bypass semantics)
  - `mem.concept.spec-driver.posture` (ceremony guidance vs runtime enforcement clarified)
  - `mem.signpost.spec-driver.ceremony` and `mem.concept.spec-driver.ceremony.settler` (advisory ceremony posture + completion gate callouts)
- Added missing fact memories:
  - `mem.fact.spec-driver.coverage-gate`
  - `mem.fact.spec-driver.status-enums`
- Preserved fixed policy decisions:
  - `strict_mode` remains one setting.
  - Baseline strict-mode contract remains hard-fail for non-canonical paths with no exception knobs.
  - v1 coverage precedence and mixed-status warning posture unchanged.
- Verification evidence: code-truth checks performed via `uv run spec-driver show/list memory`, `rg -n`, and `nl -ba` against completion, coverage, lifecycle, registry, and config sources.
- Residual risk: many non-target memories still rank similarly for command/path memory queries because broad historical scope metadata remains; phase 03/maintenance can tighten surfacing later.
- Verification status: no runtime/test/lint commands run (`just`, `just test`, `just lint`, `just pylint` not run) because this was documentation/memory-only.

## 2026-03-03 (retrieval precision pass added)
- Added explicit Phase 04 retrieval-precision pass:
  - updated `IP-038.md` phase overview/progress to include `IP-038.PHASE-04`.
  - added [phases/phase-04.md](./phases/phase-04.md) with baseline-query, scope-tuning, and before/after ranking verification tasks.
- Updated DE/DR contract text to include retrieval-precision outcomes as part of DE-038 scope.
- Updated memory maintenance skill guidance:
  - added explicit noisy-ranking playbook for `scope.commands`/`scope.paths` tuning.
  - added required before/after query validation step for ranking quality.
- Verification status: no runtime/test/lint commands run (`just`, `just test`, `just lint`, `just pylint` not run) because this was documentation/skill-guidance-only.

## New Agent Instructions
- Task card code: DE-038 (`canonical_workflow_alignment`)
- Next activity: execute Phase 2 (Skill Review Pass) via `/implement` using [phase-03.md](./phases/phase-03.md).
- Required reading:
  - [DE-038.md](./DE-038.md)
  - [DR-038.md](./DR-038.md)
  - [workflow-research.md](./workflow-research.md)
  - [IP-038.md](./IP-038.md)
  - [phases/phase-03.md](./phases/phase-03.md)
  - [gaps-to-adoption.md](./gaps-to-adoption.md)
- Key source-of-truth files:
  - `/home/david/dev/spec-driver/supekku/scripts/complete_delta.py`
  - `/home/david/dev/spec-driver/supekku/scripts/lib/changes/coverage_check.py`
  - `/home/david/dev/spec-driver/supekku/scripts/lib/changes/creation.py`
  - `/home/david/dev/spec-driver/supekku/scripts/lib/requirements/lifecycle.py`
  - `/home/david/dev/spec-driver/supekku/scripts/lib/requirements/registry.py`
  - `/home/david/dev/spec-driver/supekku/scripts/lib/specs/registry.py`
  - `/home/david/dev/spec-driver/supekku/scripts/lib/workspace.py`
  - `/home/david/dev/spec-driver/supekku/cli/create.py`
  - `/home/david/dev/spec-driver/supekku/cli/complete.py`
  - `/home/david/dev/spec-driver/supekku/cli/sync.py`
- Memory review outcome:
  - Completed in phase 02; target memories now updated and two fact memories added.
- Fixed policy decisions to preserve:
  - `strict_mode` remains one setting for now (split later only if too restrictive).
  - Baseline strict-mode contract: hard-fail non-canonical paths; no exception knobs in this delta.
  - Recommended v1 coverage precedence: mixed status => `in-progress`; mixed-status validation => warning.
- Incomplete work / loose ends:
  - Execute phase 03 skill-review tasks to align workflow-facing skills with DE-038 contract.
  - Execute phase 04 retrieval-precision tasks after phase 03 to tighten memory scope/ranking behavior.
  - Re-check workflow-facing instructions for any implied ceremony enforcement or revision-first defaults.
  - Keep notes current after each completed unit of work.
- Advice:
  - `uv run spec-driver create phase` currently appends duplicate phase IDs in `IP-038` plan block; clean duplicates if command is used again.
  - Keep edits documentation/skill guidance only; no runtime behavior changes.
