---
name: capturing-memory
description: |
  Invoke this skill whenever any of the following occurs during work: (1) you discover or confirm a durable fact, constraint, invariant, or “how we do X here” pattern; (2) you create a new workflow/checklist that will be reused; (3) you resolve a recurring confusion (“where is the source of truth?”); (4) you make a decision that is not an ADR/SPEC but would prevent rework; (5) you detect a sharp edge, footgun, or non-obvious dependency that future agents will hit.
  Do NOT rely on conversational context to persist. When the information would save ≥10 minutes for a future agent, write a memory record immediately.
---

Phase and delta wrap-up are mandatory prompts for this skill. Before treating a
phase, task, or delta as wrapped, scan the current notes, phase sheet, audit
findings, and any fresh gotchas for durable guidance worth preserving.

Procedure:

1. Mine recent work for candidates first:
   - Review `notes.md`, the active phase sheet, audit notes, and any current
     scratch findings.
   - Promote only durable guidance: repeatable workflows, sharp edges,
     invariants, or subsystem facts that future agents would otherwise rediscover.

2. Choose the correct memory_type (use the narrowest type that fits):
   - fact: atomic, checkable truth (defaults, limits, invariants)
   - pattern: repeatable recipe / command sequence / workflow
   - system: high-level subsystem map + pointers (NOT a spec)
   - concept: stable mental model, terminology, or taxonomy
   - signpost: “start here” navigation pointer set
   - thread: short-lived, context-dependent working set (expires quickly)
     Use `spec-driver create memory NAME --type TYPE` and include `--summary` and `--tag` early.

3. Create the record:
   - Command: `spec-driver create memory "..." --type <concept|fact|pattern|signpost|system|thread> [--summary "..."] [--tag ...]`
   - Default to lean frontmatter. Keep only fields that improve retrieval/ranking/review now; avoid metadata that can be inferred or generated later.
   - Practical baseline:
     - Keep: `id`, `name`, `kind`, `status`, `memory_type`, `updated` (and usually `tags`, `summary`).
     - Add when useful: `scope`, `priority`, `verified`, `review_by`, `provenance.sources`.
     - Usually omit: `audience: [human, agent]` (default), `created` (low value vs `updated`/`verified`), and `visibility` unless you are intentionally wiring pre-read/write hook surfacing.
   - If the content is risky or easy to drift, add/ensure frontmatter: `provenance.sources` (code/doc/adr/spec/commit refs), `verified` (today), and `review_by` (short horizon for volatile items).
   - **Confidence calibration** — set `confidence` in frontmatter (required; default `medium`):
     - `low`: "I'm inferring or generalizing — this should be validated"
     - `medium`: "I derived this from reasonable context — probably right"
     - `high`: "I verified this against code, specs, or direct observation"
     - Default to `medium`. Require explicit justification for `high`.
     - Remember: creating a memory is authoring, not verification. Do not claim
       `high` confidence unless you truly verified the content against the source
       material during this session.

4. Scope it so it will be findable:
   - Add `scope.paths` for exact file(s) when the memory applies to specific files (strongest match).
   - Add `scope.globs` for subsystem-level relevance (e.g., `src/auth/**`).
   - Add `scope.commands` if it is tied to a command flow (token-prefix semantics).
   - Add tags in `tags` for stable categorization; do not overload tags as scope.

5. Keep the body short and executable:
   - Put the “do X” steps in bullets with exact command snippets.
   - Use `[[artifact-id]]` in prose to reference related artifacts (e.g., `[[ADR-012]]`, `[[mem.pattern.cli.skinny]]`). These are cheaper than manual `relations` entries. Reserve `relations` for lifecycle semantics (supersedes, depends_on).
   - Treat `links.out` as derived metadata: do not hand-author it; generate only when a consumer needs resolved links.
   - For system/concept/signpost, prefer pointers to authoritative artifacts over restating them.
   - If the item would become an ADR/SPEC/other artifact, STOP and link to the proper artifact instead; memory should remain a pointer/recipe layer.

6. Immediately sanity-check surfaceability:
   - Run `spec-driver list memories --type <type> --path ... --command ... --match-tag ...` to confirm it appears under the intended context.
   - Prefer checking against the same concrete file paths you expect future
     agents to query before touching that subsystem; `scope.globs` should
     surface through those `--path` queries.

7. Resolve inline links (if body contains `[[...]]`):
   - `spec-driver admin resolve links` — populates `links.out` from body tokens.
   - Prefer running this on-demand (or in bulk maintenance passes) rather than committing large generated link blocks by default.
