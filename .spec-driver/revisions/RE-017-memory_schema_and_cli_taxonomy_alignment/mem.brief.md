Just Markdown Agent Memory Spec (JAMMS) v0.1

A provider-agnostic, model-agnostic memory system using Markdown files with a single unified metadata schema. Records are human-readable, linkable, and maintainable with explicit staleness controls. No vector search is assumed; selection is deterministic via metadata, scope matching, and optional hooks.

⸻

1. Concepts

1.1 Memory record

A memory record is a Markdown file containing:
	•	A YAML frontmatter block (or alternatively a fenced YAML block) conforming to the unified schema.
	•	A body intended for short, high-signal content and links to canonical artifacts (ADRs/specs/design docs/code).

1.2 Canonical artifacts

Memory does not replace:
	•	ADRs, specs, design docs, SOPs, runbooks, README/CLAUDE.md files.
Memory may reference these artifacts and express requirements to read them.

1.3 Record types (enumeration)

type is a categorization label used for filtering and defaults. Types are not separate schemas.

Recommended types:
	•	system: subsystem map / navigation pointers.
	•	fact: atomic durable fact.
	•	pattern: approved design/implementation pattern (not SOP).
	•	thread: in-flight work context / handover.
	•	concept: 1–2 paragraphs clarifying a term/principle and relationships.
	•	signpost: guidance/requirements/todos tied to scope (pre-read, “do this first”, “refactor next time”, etc).

Notes:
	•	signpost intentionally subsumes “hazard”, “footgun”, “lesson”, “FYI”, “guidance”, “pre-read”, and “opportunistic refactor”. Severity levels differentiate urgency/risk.

⸻

2. Storage layout

2.1 Default layout

memory/
  system/
  fact/
  pattern/
  thread/
  concept/
  signpost/
  _review.md        (optional generated)
  _index.md         (optional landing)

2.2 Record file naming

File path is not authoritative; id is authoritative.
Recommended: memory/<type>/<slug>.md

⸻

3. Unified metadata schema

3.1 Encoding

Preferred: YAML frontmatter.

Alternative: fenced code block ```yaml mem ... ``` (for repos where frontmatter is reserved). Tools MUST support at least one; MAY support both.

3.2 Required fields (all records)

id: mem.<type>.<name>         # stable unique identifier
type: system|fact|pattern|thread|concept|signpost
title: "Human readable title"
status: active|draft|deprecated|superseded|obsolete
time:
  created: YYYY-MM-DD
  updated: YYYY-MM-DD
  verified: YYYY-MM-DD|null
  review_by: YYYY-MM-DD|null
provenance:
  sources: []                 # may be empty only for draft/thread
owner:
  contact: "@handle"|null
confidence: low|medium|high|null

3.3 Optional fields (unified across all types)

summary: "One-line summary for hook output"
tags: [tag, ...]
scope:
  repo: <string>|null
  branch: <string>|null
  sha: <hex>|null
  globs: ["path/**", ...]     # filesystem-oriented matching
  paths: ["exact/path", ...]  # exact path matches (stronger than globs)
  commands: ["pnpm test auth", "make lint", ...]  # command-oriented matching
  languages: ["ts", "py", ...]
  platforms: ["linux", "mac", ...]
relations:
  requires_reading: ["docs/adr/011-foo.md", "memory/system/auth.md", ...]
  related_ids: ["mem.system.auth", "mem.concept.least-privilege", ...]
  supersedes: ["mem.signpost.old-x"]
  superseded_by: ["mem.signpost.new-x"]
policy:
  audience: ["human", "agent"]        # default both
  visibility: ["pre", "on_demand"]    # hook vs manual
  pin_to_sha: false                  # if true, treat as as-of scope.sha
priority:
  severity: none|low|medium|high|critical
  weight: 0                          # integer tie-breaker
checks:
  smoke: ["./scripts/check.sh --dry-run", ...]
  assertions: ["file:src/x.ts contains '...'", ...] # optional; tool-defined

3.4 Semantics of key fields
	•	status
	•	active: intended for use.
	•	draft: incomplete; may surface only on explicit request.
	•	deprecated: should not be used; may still exist for history.
	•	superseded: replaced; must include relations.superseded_by.
	•	obsolete: no longer relevant; should not surface.
	•	time.verified
	•	The last date a human (or automated check) confirmed this record against reality.
	•	updated MUST NOT be treated as verification.
	•	time.review_by
	•	The next required review date. Used to drive review queues.
	•	scope
	•	Defines when/where the record applies.
	•	sha pins truth “as of commit” if policy.pin_to_sha: true.
	•	relations.requires_reading
	•	Declares required pre-reading artifacts for a scope, task, or change. Used by hooks.
	•	priority.severity
	•	Used for hook ordering and filtering. For non-signpost types, default is none.

⸻

4. Content guidelines (normative)

4.1 Body constraints

Records SHOULD be brief:
	•	system: pointers + <=10 invariant bullets.
	•	fact: one assertion + provenance.
	•	pattern: when-to-use + when-not-to-use + canonical links.
	•	thread: goal/state/next actions/handover; expected to expire quickly.
	•	concept: 1–2 paragraphs + “see also”.
	•	signpost: actionable guidance; may include “read this first”, “avoid this”, “refactor next time”, “test guidance”.

4.2 Canonical linking rule

If content becomes normative, long, or detailed:
	•	It MUST be moved to an ADR/spec/design doc/SOP.
	•	The memory record MUST become a pointer + summary.

4.3 Anti-drift rule

Any record with assertions beyond pure pointers MUST include:
	•	provenance.sources referencing the authoritative artifact(s), and
	•	a non-null time.review_by unless status=draft or type=thread.

⸻

5. Selection and surfacing (deterministic retrieval)

5.1 Inputs

Tools MAY compute a “context” from:
	•	changed_files: from VCS diff.
	•	target_paths: explicit paths passed to CLI.
	•	command: the command being run.
	•	tags: explicit tags provided by user.
	•	repo/branch/sha: current VCS context.

5.2 Matching

A record matches context if any of the following are true:
	1.	Path match:
	•	any changed_files or target_paths matches scope.paths, or
	•	matches any scope.globs.
	2.	Command match:
	•	command equals or contains any scope.commands entry (tool-defined matching; MUST be documented).
	3.	Tag match:
	•	any requested tag is in tags.

Records with no scope.* MAY match only via tag or explicit id.

5.3 Filtering

Default filters for hook surfacing:
	•	Exclude status in {deprecated, superseded, obsolete}.
	•	Exclude type=thread unless explicitly requested or explicitly scoped to current branch/sha and recently verified (tool-defined).
	•	Exclude draft unless --include-draft.

5.4 Ordering

Order surfaced records by:
	1.	priority.severity (critical > high > medium > low > none)
	2.	priority.weight descending
	3.	scope specificity (paths > globs > commands > tags-only)
	4.	recency of time.verified (more recent first; null last)
	5.	stable tie-breaker: id lexicographic

5.5 Output format (hook)

Hook output SHOULD use summary if present else title.
It MUST include the id (for mem show <id>).

Suggested cap: 5 items by default; configurable.

⸻

6. Review, staleness, and self-maintenance

6.1 Default review cadences (tool defaults; MAY be overridden)

If time.review_by is null on non-draft non-thread records, tools SHOULD assign defaults by type:
	•	signpost: 30–60 days (short; guidance rots)
	•	pattern: 60–90 days
	•	system: 90 days
	•	concept: 180 days
	•	fact: 180 days
	•	thread: 7–14 days (or explicit expiry)

6.2 Review queue generation

A tool SHOULD generate a review list with categories:
	•	Overdue: review_by < today
	•	Unverified: verified is null and status=active
	•	Orphaned provenance: missing/invalid refs in provenance.sources
	•	Broken relations: superseded without back-links; missing referenced ids
	•	Unscoped signposts: type=signpost with no scope and no tags (likely undiscoverable)

6.3 Supersedence protocol

To supersede record A with record B:
	•	Set A: status: superseded, relations.superseded_by: [B.id]
	•	Set B: relations.supersedes: [A.id]
Tools SHOULD provide an atomic operation for this.

6.4 Verification protocol

Verification SHOULD update:
	•	time.verified = today
	•	time.updated = today
Optionally:
	•	If policy.pin_to_sha true, set scope.sha to current commit.

⸻

7. Provenance format

7.1 Source entry

Each provenance source is an object:

- kind: adr|spec|design|doc|code|issue|pr|commit|external
  ref: "relative/path/or/url"
  note: "optional human note"

Tools MAY validate ref existence for local paths.

⸻

8. Interop with folder-local CLAUDE.md / README.md
	•	Memory records MAY reference local CLAUDE.md files in provenance.sources or relations.requires_reading.
	•	Tools MAY optionally treat CLAUDE.md as implicit signpost inputs during hooks, but this spec does not require it.
	•	To avoid duplication, recommended practice is:
	•	folder-local CLAUDE.md = immediate, local instructions
	•	memory signpost = cross-cutting, relational, or “requires reading” rules spanning multiple areas

⸻

9. Examples

9.1 Signpost: “read ADR-11 before touching this”

---
id: mem.signpost.adr11-required-for-auth
type: signpost
title: ADR-11 required pre-reading for auth changes
summary: "Pre-read: ADR-11 before modifying auth flow"
status: active
priority: { severity: high, weight: 10 }
scope:
  globs: ["src/auth/**", "packages/auth/**"]
relations:
  requires_reading: ["docs/adr/011-auth-flow.md"]
time: { created: 2026-02-01, updated: 2026-02-01, verified: 2026-02-01, review_by: 2026-04-01 }
provenance:
  sources:
    - { kind: adr, ref: docs/adr/011-auth-flow.md }
owner: { contact: "@platform" }
confidence: high
tags: [auth]
---

When changing auth flow code, read ADR-11 first. It defines invariants and migration constraints.

9.2 Signpost: “write an integration test? read guidance”

---
id: mem.signpost.integration-test-guidance
type: signpost
title: Integration test guidance for auth
summary: "Use the auth integration harness; avoid unit-level mocks"
status: active
priority: { severity: medium, weight: 5 }
scope:
  globs: ["src/auth/**"]
  commands: ["pnpm test auth:integration"]
relations:
  requires_reading: ["docs/testing/auth-integration.md"]
time: { created: 2026-01-10, updated: 2026-02-15, verified: 2026-02-15, review_by: 2026-04-15 }
provenance:
  sources:
    - { kind: doc, ref: docs/testing/auth-integration.md }
owner: { contact: "@devex" }
confidence: medium
tags: [testing, auth]
---

If you add integration tests, use the harness in `docs/testing/auth-integration.md`. Prefer exercising real middleware wiring.

9.3 Signpost: “refactor next time you touch it”

---
id: mem.signpost.refactor-auth-cache-next-touch
type: signpost
title: Refactor auth cache on next non-trivial change
summary: "If you’re changing auth cache logic, refactor module boundaries"
status: active
priority: { severity: low, weight: 1 }
scope:
  paths: ["src/auth/cache.ts"]
time: { created: 2026-02-20, updated: 2026-02-20, verified: 2026-02-20, review_by: 2026-05-20 }
provenance:
  sources:
    - { kind: issue, ref: docs/techdebt/auth-cache.md }
owner: { contact: "@platform" }
confidence: medium
tags: [techdebt, auth]
---

This file mixes cache policy and storage details. If you touch it beyond small edits, split policy from storage and add coverage.


⸻

10. Tooling requirements (for your CLI)

A conforming tool SHOULD provide:
	•	mem list with filters: --type --tag --status --severity --path --cmd
	•	mem show <id>
	•	mem pre (hook mode): computes context and prints top matches
	•	mem status (review queue)
	•	mem lint:
	•	schema validation
	•	link/ref existence (best-effort)
	•	supersede chain integrity
	•	mem supersede <old> <new> (atomic update)
	•	mem verify <id> [--pin-sha]

⸻

11. Non-goals
	•	Semantic search / embeddings / vector indices.
	•	Replacing ADRs/specs/design docs/SOPs.
	•	Automatically generating or rewriting canonical docs from memory.

⸻

If you want a v0.2, the next increment is to standardize checks.assertions (a tiny DSL) so “verified” can be partially automated (e.g., file exists, symbol exists, command succeeds), which materially reduces drift without needing any LLM involvement.
