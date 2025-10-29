# Agent Playbook: Complete Initial Spec (Claude Sonnet)

## Purpose
You are filling out a brand-new SPEC (tech or product) using the templates under `supekku/templates/`. Your job is to extract the current behaviour from the codebase and produce a plausible, traceable description that humans and other agents can refine.

## Inputs
- Spec directory scaffolded via `supekku/scripts/create-new-spec.py Name Here`.
- Newly created spec file, e.g. `doc/specify/tech/SPEC-XYZ-*/SPEC-XYZ.md` (and `SPEC-XYZ.tests.md` when present).
- Reference corpus under `doc/reference/`, existing PROD/SPEC docs, ADRs, policies, backlog notes.
- Source code (Go) and tests (`internal/`, `cmd/`, `test/`, etc.).

## Preparation Checklist
- [ ] Locate the spec directory (`doc/specify/tech/SPEC-XYZ-name-here`) and open the main spec file alongside the testing companion (if present).
- [ ] Skim related reference docs (`doc/reference`, linked ADRs/policies) to understand context.
- [ ] Identify primary packages/modules by searching for the spec’s responsibility keywords (use `rg` / `fd`).
- [ ] Note any existing issues/deltas/problems touching this area (`backlog/`).
- [ ] Note any existing decision records relevant to this area (`decisions/approved`).

## Procedure
1. **Anchor the Intent (Section 1)**
   - Summarise current behaviour in plain English.
   - Link to any authoritative references (design docs, research, ADRs, policies).
   - Record latest relevant delta/audit if known; otherwise leave TODO.

2. **Map Context (Section 2)**
   - Enumerate external systems, packages, or services invoked.
   - Add ADRs/policies/standards using frontmatter-friendly IDs.
   - List collaborating SPECs/PRODs and explain the relationship.

3. **Responsibilities (Section 3)**
   - Extract responsibilities from code: handlers, services, domain aggregates.
   - Describe each responsibility with success criteria and tie to FR/NF IDs (create placeholder IDs if missing).

4. **Architecture Overview (Section 4)**
   - Outline key components: structs, interfaces, processes. Mention critical methods.
   - Summarise data models: Go structs, protobufs, SQL schemas (include inline snippets if clearer).
   - Document integration contracts (request/response schema, invariants). Reference actual code locations.

5. **Behaviour (Section 5)**
   - Describe primary flows (e.g. request lifecycle, background jobs). Use sequence bullet lists referencing components.
   - Capture edge cases, guards, retries. Include pseudo/code snippets when helpful.
   - Define state transitions if stateful (tables/diagrams ok).

6. **Quality & Ops (Section 6)**
   - Fill FR/NF entries with measurable statements. Pull existing constants/metrics when possible.
   - Note observability and security constraints (logs, metrics, auth).

7. **Testing Strategy (Section 7)**
   - Inventory existing tests by suite: unit/component (`internal/...`), integration/tech (`test/...`).
   - Describe current testing conventions, helpers, mocks, fixtures.
   - Identify coverage gaps; queue them as issues/problems.
   - If detail exceeds the inline section, expand `SPEC-XYZ.tests.md` using the testing template.

8. **Verification (Section 8)**
   - Map requirements to existing tests (`VT`, `VA`, `VH`) or note missing coverage.
   - Record latest audit if any; otherwise mark “not yet audited”.

9. **Backlog Hooks (Section 9)**
   - Link to relevant issues/problems/deltas; create new ones if gaps found (coordinate with humans if creation requires approval).
   - Capture pending decisions/hypotheses with owners and due dates.

10. **Risks & Assumptions (Section 10)**
    - Document active risks (link to `backlog/risks/...` risk entries or create TODOs).
    - Log assumptions surfaced during analysis; note consequences if invalid.

11. **Implementation Notes (Section 11)**
    - Provide agent-friendly reminders: commands to run tests, setup steps, pitfalls (e.g. feature flags, migrations).

12. **Appendices / References**
    - Add diagrams (D2/Mermaid), expanded API examples, or migration details if they aid comprehension.

## Quality Gate
Before finishing:
- [ ] Spec and optional testing guide have no `PLACEHOLDER` markers.
- [ ] Every section either filled or marked `[NOT APPLICABLE - TO REMOVE]`.
- [ ] Frontmatter tags, relations, and IDs align with document body.
- [ ] Backlog/testing gaps captured as issues/problems or clear TODOs.
- [ ] Language is concise, actionable, and references code paths (file:line where useful).

## Tooling Tips
- Use `rg` / `fd` / `go list ./...` to explore code quickly.
- Generate diagrams with D2 (save to `SPEC-XYZ` directory).
- Reference templates in `supekku/templates/` for structure cues.
- Consult `supekku/about/frontmatter-schema.md` for frontmatter rules.

## Handover
- Commit spec changes or stage for review per project norms (no branch automation here).
- Notify maintainers if new issues/problems were created or need manual confirmation.
- If significant uncertainty remains, flag sections with `[NEEDS CLARIFICATION: ...]` and document next steps.
