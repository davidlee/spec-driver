# Drift Ledger schema draft (working)

Revised 2026-03-05 after parity ledger review. See IMPR-007 decisions D1–D14.

## Definition

A Drift Ledger (DL) is a durable, queryable record of divergence between
normative truth (specs/ADRs/policies), observed truth (code/contracts/runtime),
and intent clarity (missing or ambiguous decisions).

The **ledger** is the artifact (one file per initiative/scope of work).
**Entries** are sections within the ledger.

## Ledger frontmatter (minimal)

```yaml
---
id: DL-047
name: Spec corpus reconciliation
created: '2026-03-05'
updated: '2026-03-05'
status: open
kind: drift_ledger
delta_ref: DE-047
---
```

## Entry types

- `contradiction` — two documents assert incompatible things
- `implementation_drift` — observed code/runtime differs from normative doc
- `stale_claim` — document asserts something no longer true
- `missing_decision` — no document addresses a question that needs answering
- `ambiguous_intent` — a document's meaning is unclear or open to interpretation

## Entry lifecycle

- `open` — captured, not yet reviewed
- `triaged` — severity, topic, owner assigned
- `adjudicated` — assessment made (confirmed / not_drift / deferred)
- `resolved` — fix applied and traced
- `deferred` — real drift, intentionally not addressing now
- `dismissed` — assessed as not_drift; false positive (keep evidence + reason)
- `superseded` — replaced by another entry or made moot

### Lifecycle transitions (minimum required fields)

- `open` → `triaged`: requires severity, topic, owner
- `triaged` → `adjudicated`: requires assessment
- `adjudicated` → `resolved`: requires resolution_path, resolution_ref, affected_artifacts
- `adjudicated` → `deferred`: requires reason in evidence
- `adjudicated` → `dismissed`: requires assessment = not_drift + evidence note
- `deferred` → `open`: re-opened with new evidence

## Entry schema

### Required at creation (open)

- `entry_type`
- At least one `claim`

### Required at triage

- `severity`: blocking | significant | cosmetic
- `topic`: lifecycle | taxonomy | contracts | governance | workflow | cli | other
- `owner`
 - At least one `source` OR evidence note explaining why sources are not yet identified

### Full schema

```yaml
# Identity (ledger-local)
id: DL-047.001

status: open
entry_type: contradiction
severity: significant
topic: contracts
owner: david

# Where the drift appears
sources:
  - kind: spec | prod | adr | policy | doc | impl | contract | audit | test
    ref: <artifact ID or path>
    note: <optional>

# What is conflicting or unclear
claims:
  - kind: assertion | observation | gap | question
    label: <optional: expected | observed | A | B | freeform>
    text: "..."

# Assessment and resolution
assessment: confirmed | disputed | not_drift
resolution_path: ADR | RE | DE | editorial | no_change
resolution_ref: ADR-XXX | RE-XXX | DE-XXX | <path>
affected_artifacts:
  - PROD-009
  - ADR-002

# Discovery origin
discovered_by:
  kind: audit | survey | agent | human
  ref: VA-047-001

# Evidence trail (append-only)
evidence:
  - 2026-03-05 discovered during PROD spec cross-reference survey (VA-047-001)
  - 2026-03-06 triaged as significant; contracts topic
  - 2026-03-07 adjudicated: confirmed — contradicts ADR-002
  - 2026-03-08 resolved via ADR-004; PROD-008 §3 updated
```

### Optional fields

- `tags`: [list]
- `links`: [related entry IDs, e.g. DL-047.003]

## Resolution paths

- `ADR` — architectural decision affecting 3+ specs or redefining a term
- `RE` — spec revision, local to 1-2 specs
- `DE` — requires a delta (implementation change needed)
- `editorial` — wording fix, no design decision
- `no_change` — confirmed drift but accepted as legitimate divergence

## Example ledger file

```markdown
---
id: DL-047
name: Spec corpus reconciliation
created: '2026-03-05'
updated: '2026-03-05'
status: open
kind: drift_ledger
delta_ref: DE-047
---

# DL-047 — Spec corpus reconciliation

Drift ledger for DE-047. Tracks contradictions and ambiguities across the
PROD spec corpus discovered during the cross-reference survey.

## Entries

### DL-047.001: Contract authority — canonical vs derived

- status: triaged
- entry_type: contradiction
- severity: significant
- topic: contracts
- owner: david
- sources:
  - kind: prod
    ref: PROD-012
    note: "§3: contracts are the canonical record of what the code exposes"
  - kind: doc
    ref: CLAUDE.md
    note: "contracts corpus is derived and deterministic"
- claims:
  - kind: assertion
    label: A
    text: "Contracts are canonical"
  - kind: assertion
    label: B
    text: "Contracts are derived and deterministic — always safe to delete and regenerate"
- assessment: disputed
- evidence:
  - 2026-03-05 discovered during PROD spec survey (VA-047-001)

### DL-047.002: Ceremony mode enforcement

- status: open
- entry_type: ambiguous_intent
- topic: governance
- claims:
  - kind: question
    text: "Do ceremony modes constrain what artifacts are required, or only set guidance posture?"
- evidence:
  - 2026-03-05 workflow.md says 'guidance posture, not runtime enforcement' but PROD-016 implies modes gate artifact creation
```

## CLI affordances (MVP)

- `spec-driver create drift <name>` — create a ledger file
- `spec-driver create drift <name> --delta DE-047` — create with delta_ref
- `spec-driver schema show drift.entry` — show entry schema for reference
- `--create-ledger` flag on `create delta` / `create spec` — scaffold alongside

## Notes

- Supports doc-doc contradictions, doc-implementation drift, missing decisions,
  and ambiguous intent via flexible claims structure (D6).
- Evidence is append-only timestamped, following the parity ledger convention
  from deck_of_dwarf (D10).
- Registry (`drift.yaml`) and richer CLI deferred until after DE-047 pilot (D2).
