# supekku.delta_plan

Guidance for authoring and updating delta implementation plans (`IP-xxx.md`) and phase sheets when working on Supekku change bundles.

## 1. Locate Inputs
- Delta directory: `change/deltas/DE-XXX/`
- Implementation plan: `IP-XXX.md`
- Current phase sheet: `phases/phase-0N.md`

## 2. Structured Blocks (authoritative)
- Plans include a `supekku:plan.overview@v1` YAML block immediately after the frontmatter.
  - Update `delta`, `specs.primary`, `requirements.targets`, and `phases` entries as the plan evolves.
  - Append new phase entries as you elaborate future phases.
- Plans also carry a `supekku:verification.coverage@v1` block tying requirements to VT/VA/VH artefacts; keep status and evidence current.
- Each phase sheet includes a `supekku:phase.overview@v1` block. Keep `objective`, `entrance_criteria`, `exit_criteria`, and `verification` aligned with the prose sections.
- Edit the YAML directly; avoid hand-editing any markdown tables generated from it (if/when renderers are introduced).

## 3. Updating an Existing Plan
1. Open the plan: `nvim change/deltas/DE-XXX/IP-XXX.md`
2. Review the structured block:
   - Add collaborating specs or dependent requirements.
   - Add new phase summaries when additional phase sheets are created.
3. Flesh out sections 1–10 with narrative context matching the structured data.
4. Cross-check `requirements.targets` against the delta’s relationships block.

## 4. Creating / Updating Phase Sheets
1. Generate a new phase sheet via `just supekku::new-phase` (if available) or copy the template.
2. Immediately set the `supekku:phase.overview@v1` fields:
   - `objective`: what this phase accomplishes.
   - `entrance_criteria` / `exit_criteria`: mirror the plan.
   - `verification.tests` / `verification.evidence`: list concrete checks and artefacts.
3. Populate the task table and detail blocks beneath it. Use `[P]` in the table for parallelisable work.
4. Track STOP conditions and assumptions explicitly—agents halt work when triggered.

## 5. Keep Artefacts in Sync
- When a phase completes, update the plan overview block’s entry for that phase (e.g., append notes in `objective` or mark status in prose).
- If phases are added or renumbered, update:
  - Delta relationships block (`phases` array)
  - Plan overview block (`phases` array)
  - Phase sheet filenames (`phase-0N.md`)
- Log risks, decisions, and follow-up tasks in both the plan and delta notes (`notes.md`).

## 6. Validation Checklist
- `supekku:plan.overview@v1` exists and lists the active phase.
- Current phase sheet’s overview block matches the plan (objectives, entrance/exit, tests).
- Delta relationships block references the plan phases if known.
- Requirements in plan/delta blocks map back to SPEC registry entries (`just supekku::sync-requirements`).

Treat these YAML blocks as the source of truth; prose expands on them for human auditors.
