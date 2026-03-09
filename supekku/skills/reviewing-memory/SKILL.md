---
name: reviewing-memory
description: |
  Invoke this skill as a deliberate review pass whenever stability matters: (1) before a release/migration/large refactor; (2) at the start of work in an unfamiliar subsystem; (3) when you see repeated agent confusion; (4) when thread-type working sets accumulate; (5) when you suspect stale guidance is causing defects. This is not ad-hoc maintenance; it is a structured audit to prevent systemic drift.
---

Review procedure:
1) Pull the highest-impact set first:
    - Start with the staleness-ranked view:
      `spec-driver list memories --stale`
    - Prioritize tier 1 (scoped, attested, high commit count) — these are the
      highest-value review targets because they have scope and attestation but
      their scoped files have changed significantly since last verification.
    - Flag unscoped memories separately for manual review based on age.
    - Then run contextual reviews for the active area:
      `spec-driver list memories -p <subsystem paths>... -c "<common commands>" --match-tag <subsystem tags>... --limit N`

2) Explicitly include drafts only when reviewing for promotion:
    - Use `--include-draft` to evaluate whether drafts should become active or be removed/merged.

3) For each surfaced record, apply a strict checklist:
    - Provenance: does it cite authoritative sources (`provenance.sources`)? If not, add sources or reduce confidence.
    - Freshness: is `verified` recent enough for its type? If not, verify against code/docs now or schedule by setting `review_by` soon.
    - Metadata efficiency: remove low-value defaults and generated bloat (`audience: [human, agent]`, unnecessary `created`, bulk `links.out` when not actively consumed).
    - Scope: does it surface under the correct `--path/--command/--match-tag` queries? If not, fix `scope.*`.
    - Visibility discipline: keep `visibility: [pre]` only for memories with strong `scope.*` and clear pre-hook value.
    - Actionability: does it contain executable steps/pointers (especially for pattern/signpost/system)? If not, rewrite to be procedural or convert to a signpost.
    - Duplication/conflict: does it overlap or contradict another memory? If yes, merge/supersede immediately.
    - Links: run `spec-driver admin resolve links --dry-run` to check for broken `[[...]]` references. Missing targets may indicate renamed/deleted artifacts; only persist resolved `links` when needed.

4) Thread hygiene (mandatory):
    - Threads are context-dependent and should not linger. Any thread that is not verified recently (or no longer relevant to current work) must be moved to `archived`, `superseded`, or converted into a durable fact/pattern/system record with proper scope and provenance.

5) Produce an outcome, not notes:
    - Every reviewed item must end in one of: verified (date updated), corrected (content/scope/provenance updated), superseded (replacement created/linked), archived/obsolete (removed from surfacing), or promoted from draft.

Stop conditions:
- Do not expand memories into mini-specs. If review uncovers missing design/decision authority, create or reference ADR/SPEC/design docs and convert the memory into a pointer/signpost to the canonical artifact.

Success metric:
- After review, the top results for common `--path/--command/--match-tag` queries should be accurate, source-backed, and recently verified, so future agents default to correct guidance without extra investigation.
---
