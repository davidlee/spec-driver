# Core Loop Skill Outline (Early Iteration Workshop)

This is a v0 outline for skills that cover the loop:

`revision -> DR -> delta -> IP -> phase(s) -> audit -> spec/closure`

## Design Goal

- Keep skills small and composable.
- Keep static skill instructions provider-neutral.
- Put project-specific paths/toggles in generated `.spec-driver/agents/*.md`.

## Proposed Skill Set (v0)

| Skill Name                                  | Invoked When                                                            | Expected Outcomes                                                                            |
| ------------------------------------------- | ----------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| `boot` (existing)                           | Agent startup / first contact with repo                                 | Agent has loaded generated execution/workflow/policy/glossary context and repo doctrine.     |
| `preflight` (existing)                      | Before any new loop step or artifact mutation                           | Task intent is clear, owning record identified, and scope of investigation bounded.          |
| `shape-revision` (new)                      | Work starts from requirement/spec movement (Town Planner path)          | Revision draft is created/updated with moved requirements and explicit rationale.            |
| `draft-design-revision` (new)               | Delta scope exists and design implications are non-trivial              | DR captures current vs target behavior, code impact areas, and verification alignment.       |
| `scope-delta` (new)                         | Need to formalize intended code/spec alignment work                     | Delta has clear applies-to requirements/specs, risks, and closure intent.                    |
| `plan-phases` (new)                         | Delta/DR ready for execution planning                                   | IP defines phase objectives, entry/exit criteria, and success criteria tied to verification. |
| `execute-phase` (new, can wrap `implement`) | Active phase sheet exists and entry criteria are met                    | Code/tests/notes updated for phase objective; blockers surfaced via `consult`.               |
| `audit-change` (new)                        | Implementation complete or retroactive conformance check needed         | Audit/evidence produced against PROD/SPEC/contracts truth; findings linked to next actions.  |
| `close-change` (new)                        | All phase/audit gates satisfied and delta ready to close                | Owning records updated (delta/spec coverage/registry fields), `complete delta` succeeds.     |
| `notes` (existing)                          | After each meaningful unit of phase or task work                        | Card/record has concise implementation notes, verification status, and follow-ups.           |
| `consult` (existing)                        | Unexpected complexity, ambiguity, policy risk, or plan conflict appears | Work pauses; tradeoffs and options are surfaced to user before proceeding.                   |
| `continuation` (existing)                   | Context limit approaching or handoff required                           | Next agent receives concrete reading list, state, loose ends, and next command/skill.        |

## Suggested Invocation Contract (Minimal)

Each skill should define:

1. Inputs:
   - required artifact IDs/paths
   - required prerequisite skills or checks
2. Mutations:
   - exact files/sections it may update
3. Exit checks:
   - objective done criteria
   - required verification command(s)
4. Handoff:
   - next skill suggestions by outcome branch

## Mapping To Current Surfaces

- Existing in repo: `boot`, `preflight`, `implement`, `notes`, `consult`, `continuation`
- Command-aligned candidates:
  - `plan-phases` aligns with `/supekku.plan` and `/supekku.phase`
  - `execute-phase` aligns with `/supekku.task`
  - `close-change` aligns with `/supekku.phase-complete` and `/supekku.delta-complete`
- Audit/revision skills are explicit gaps worth adding early if Town Planner flow is desired.

## Early Iteration Recommendation

Start with this minimum path:

`boot -> preflight -> scope-delta -> draft-design-revision -> plan-phases -> execute-phase -> audit-change -> close-change`

Use `consult` as mandatory interrupt on uncertainty, and `notes`/`continuation` as always-on support skills.
