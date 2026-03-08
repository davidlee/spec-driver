---
name: maintaining-memory
description: |
  Invoke this skill whenever you observe memory drift or when your actions would invalidate existing memories. Mandatory triggers: (1) you change a workflow/command, move files, rename modules, or change invariants; (2) you discover a memory is wrong, missing provenance, or stale; (3) you see a memory record guiding behaviour that is no longer true; (4) you find duplicates or near-duplicates; (5) you are about to add a new memory that overlaps an existing one.
  Core rule: if you change reality, you must change memory in the same change-set (or immediately after) so future agents do not inherit incorrect guidance.
---

  Procedure:
  1) Locate impacted memories by scope and tags:
     - Use `spec-driver list memories -p <changed path>... -c "<affected command>" --match-tag <domain tag>...`
     - Use `--regexp` to catch naming/summary matches for renamed concepts.

  2) Validate correctness quickly:
     - Open each candidate via `spec-driver show memory MEM-ID` and compare its assertions to current code/docs/ADRs/SPECs referenced in `provenance.sources`. If no provenance exists, add it or downgrade confidence.

  3) Apply minimal corrective edits:
     - Prefer changing the memory to point to the new authority rather than restating details.
     - Update `updated` and (when you have verified against reality) set `verified` to today; set/adjust `review_by` based on volatility (short for pattern/thread, longer for system/concept).
     - Keep `created` stable unless you are correcting bad history; freshness should be carried by `updated`/`verified`.
     - Prune default/low-value metadata while editing:
       - remove `audience` when it is just `[human, agent]`
       - remove `visibility` unless the memory is intentionally used for pre-read/write hook surfacing with concrete scope
       - remove generated `links` blocks unless an active consumer requires committed resolved links
     - If you edited the body and it contains `[[...]]` references, run `spec-driver admin resolve links` to update `links.out`. Stale links are cleared automatically.

  4) Handle lifecycle states aggressively:
     - If a record is wrong and replaced, mark the old one `superseded` and create/update the successor; link via `relations` (type + target + annotation) or `superseded_by`/`supersedes` if you use that convention.
     - If a record is no longer relevant but still historically useful, prefer `archived` over leaving it `active`.
     - If it is actively harmful, move to `obsolete` (or `deprecated`) promptly; do not leave “known wrong” records active.

  5) Re-scope if selection misses:
     - If a correct memory does not surface under relevant `--path/--command`, add `scope.paths/globs/commands` so retrieval is automatic for future agents. Records without scope are excluded from scope-filtered results.
     - If you add `visibility: [pre]`, ensure it is paired with meaningful `scope.*`; avoid global pre-hook noise.
     - If retrieval is noisy (broad conceptual memories outrank actionable records), tighten scope on the actionable records first:
       - add `scope.commands` for exact command prefixes (for example `uv run spec-driver complete delta`)
       - add `scope.paths` for source-of-truth files tied to the operation
       - avoid adding broad global globs that make every memory match every query

  6) De-duplicate:
     - If two memories cover the same operational guidance, keep one canonical record and convert the other into a short signpost pointing at it (or supersede it). This prevents diverging “truths”.

  7) Validate ranking quality explicitly:
     - Capture a before/after query for the target context (same `--path/--command/--match-tag` and `--limit`).
     - Confirm the top results now include the intended operational memory/memories.
     - If broad concept/signpost records still dominate, either tighten scope on operational records further or reduce over-broad scope on the dominating records.

  Completion criterion:
  - After edits, run the same `list memories` query that originally surfaced the issue and confirm the corrected record ranks above stale/noisy results for that context (severity/weight/specificity/recency + scope).
---
