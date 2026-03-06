---
id: IMPR-007
name: Drift Ledger primitive
created: '2026-03-05'
updated: '2026-03-05'
status: idea
kind: improvement
---

# Drift Ledger primitive

## Summary
Introduce a Drift Ledger (DL) primitive to track divergence between normative
truth (specs/ADRs/policies), observed truth (code/contracts/runtime), and
ambiguous or missing intent. The ledger is the adjudication queue and
resolution record, distinct from audits, revisions, and deltas.

## Why this matters
Current workflows have to improvise reconciliation registers. A first-class DL
would unify contradiction discovery, design adjudication, and resolution
tracking across projects and maturity levels.

## Scope (initial)
- Support contradictions between documents
- Support canon vs implementation drift
- Track ambiguous intent and open questions
- Capture adjudication + resolution links

## Out of Scope (initial)
- Automated adjudication
- Mandatory enforcement in runtime gates

## Decisions

Decisions made during schema review (2026-03-05). Revised same day after
reviewing the parity ledger pattern from deck_of_dwarf.

### D1. Storage model — ledger-as-file

The *ledger* is the artifact, not the individual entry. Each ledger is a
standalone markdown file in `drift/`: `drift/DL-NNN-slug.md`. Entries are
sections within the ledger, not standalone files.

A ledger is scoped to an initiative or piece of work (a delta, a spec
authoring session, an audit). Entries accumulate within it.

**Rationale**: The file-per-entry model (initially proposed) maps poorly to
how drift is actually discovered and reviewed. Drift surfaces in clusters
during focused work. The parity ledger from deck_of_dwarf demonstrates that a
single-file-per-scope model handles scores of entries with low creation
friction, natural batching, and easy scanning. Creating an entry is adding a
section, not creating a directory + file + frontmatter.

### D2. Registry — deferred, design-compatible

A `drift.yaml` registry is the natural fit once the primitive is validated.
Deferred until after DE-047 pilot, but the ledger/entry schema should not
prevent future registry indexing (stable IDs, parseable structure).

### D3. Entry IDs — ledger-local

Entry IDs are scoped to their ledger: `DL-047.001`, `DL-047.002`, etc.
External references use the full form. Cross-ledger references are infrequent
enough that the verbosity is acceptable — follows the same pattern as spec
requirements (e.g. `SPEC-122.FR-003`).

The *ledger* ID (`DL-NNN`) is repo-global auto-incrementing, consistent with
other artifact types.

### D4. Scope field — removed

The original `scope` field was ambiguous (artifact drifting? artifact affected?
resolution scope?). Removed in favour of:
- `sources[]` — where the drift appears (already existed)
- `affected_artifacts[]` — what needs updating when resolved (new)

These two fields are unambiguous and together cover what `scope` was trying to
do.

### D5. Adjudication → assessment

Replaced `adjudication: legit | deferred | heresy | unknown` with
`assessment: confirmed | disputed | not_drift | deferred`.

**Rationale**: "heresy" and "legit" were evocative but unclear. The new values
answer a precise question: "is this actually drift?" `confirmed` = yes, real
divergence. `disputed` = under review. `not_drift` = false positive.
`deferred` = real but not addressing now. `resolution_path` remains separate
(how to fix confirmed drift).

### D6. Claims structure — flexible per entry type

Claims now have `kind` (assertion | observation | gap | question) and an
optional `label` (expected/observed, A/B, or freeform). This supports:
- Contradictions: two `assertion` claims with labels A/B
- Implementation drift: `assertion` (expected) + `observation` (observed)
- Missing decisions: single `gap` claim
- Ambiguous intent: single `question` claim

**Rationale**: The original A/B pattern was contradiction-centric and didn't
fit other entry types.

### D7. Discovery origin — `discovered_by`

Added `discovered_by` with `kind` (audit | survey | agent | human) and `ref`.
Audits become a discovery mechanism that produces DL entries. The relationship
is: audit *discovers* drift → DL entry tracks resolution.

This clarifies the audit/DL boundary: audits are point-in-time assessments, DL
entries are open items requiring resolution.

### D8. Topic — required at triage, recommended at creation

Topic is the primary grouping mechanism for human review. Required to progress
past `open` (i.e. required for triage), but not strictly required at creation
to keep ad-hoc capture lightweight. Schema should accept entries without topic
at `open` status.

### D9. Closure traceability — `affected_artifacts[]`

Added `affected_artifacts[]` to record which specs/docs were updated as a
result of resolution. Closes the traceability loop:
drift found → resolution created (`resolution_ref`) → artifacts updated
(`affected_artifacts`).

Required for transition to `resolved`.

### D10. Evidence as append-only timeline

Entry evidence is an append-only timestamped list, not a single snapshot field.
Captures the progression from discovery through adjudication to resolution.
Format follows the parity ledger convention: `YYYY-MM-DD <what changed>`.

Replaces the single `analysis` string with a structured `evidence` list plus
an optional `analysis` summary.

### D11. Ledger lifecycle — deferred

No formal lifecycle for ledgers themselves. Nothing prevents adding one later;
the ledger frontmatter should include `status` to allow future lifecycle
without schema changes, but transitions are not enforced.

### D12. Dismissed terminal state

Added `dismissed` as a terminal state for entries assessed as `not_drift`.
Distinct from `resolved` (which implies something was fixed).

### D13. Schema permissiveness — progressive strictness

At creation (`open`), only `entry_type` and at least one `claim` are required.
Fields like `topic`, `severity`, `owner`, `sources` are recommended but not
enforced until triage. This keeps ad-hoc capture lightweight while ensuring
entries mature before resolution.

Formal/large-scale processes (like DE-047's survey) will populate all fields
at creation by convention, not by schema enforcement.

### D14. Ledger creation affordance

`spec-driver create drift` creates a ledger. Additionally, a `--create-ledger`
flag on `create delta` and `create spec` scaffolds an associated ledger
alongside the primary artifact, reducing friction for the organic discovery
case.

## Open questions (remaining)

- **Audit template changes**: D7 establishes that audits *discover* DL entries.
  Does this imply changes to the audit template? Or is it sufficient for audits
  to reference DL entries in their findings?
- **Lifecycle enforcement**: When the registry arrives, should `spec-driver`
  enforce entry lifecycle transition rules (required fields per state), or keep
  it advisory?
- **Topic vocabulary**: Current list (lifecycle | taxonomy | contracts |
  governance | workflow | cli | other) is DE-047-informed. Should it be
  extensible per-project, or fixed?
- **Ledger frontmatter schema**: What metadata does the ledger file itself need
  beyond `id`, `name`, `status`, `created`, `delta_ref`? E.g. should it carry
  `applies_to` like a delta?
- **Entry ordering within ledger**: Append-only (discovery order) or grouped by
  topic/severity? The parity ledger uses capability grouping. For a generic DL,
  discovery order with topic headings may be more natural.

## Proposed next step
Draft a DL schema and format and test it on DE-047 (spec corpus reconciliation).
See `drift-ledger-schema-draft.md` in this folder.

## Current Draft Notes
- Progressive strictness (minimal capture → triage → adjudication → resolution)
- Evidence is append-only, timeline style
- CLI MVP: `create drift`, `schema show drift.entry`, `--create-ledger`
- Lifecycle drift should model explicit normative vs observed disagreement:
  spec = normative claim, audit/delta/plan/registry = observed or derived
  context, resolution via ADR/RE/DE rather than timestamp precedence
