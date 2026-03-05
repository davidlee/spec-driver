# Drift Ledger schema draft (working)

This draft is intentionally product + technical in one place while the concept
is still forming.

## Definition
A Drift Ledger (DL) is a durable, queryable record of divergence between
normative truth (specs/ADRs/policies), observed truth (code/contracts/runtime),
and intent clarity (missing or ambiguous decisions).

## Entry types
- contradiction
- implementation_drift
- stale_claim
- missing_decision
- ambiguous_intent

## Entry lifecycle
- open
- triaged
- adjudicated
- resolved
- deferred
- superseded

## Resolution paths
- ADR
- RE
- DE
- editorial
- no_change

## Minimal entry schema (YAML)
```yaml
id: DL-001
status: open | triaged | adjudicated | resolved | deferred | superseded
severity: blocking | significant | cosmetic
entry_type: contradiction | implementation_drift | stale_claim | missing_decision | ambiguous_intent
topic: lifecycle | taxonomy | contracts | governance | workflow | cli | other

# Where the drift appears
sources:
  - kind: spec | prod | adr | policy | doc | impl | contract | audit | test
    ref: <artifact ID or path>
    note: <optional>

# What is conflicting or unclear (flexible per entry type)
claims:
  - kind: assertion | observation | gap | question
    label: expected | observed | A | B | <freeform>
    text: "..."

# Supporting evidence
analysis: <why this is drift / what the underlying design question is>

# Adjudication and resolution
assessment: confirmed | disputed | not_drift | deferred
resolution_path: ADR | RE | DE | editorial | no_change
resolution_ref: ADR-XXX | RE-XXX | DE-XXX | <path>
affected_artifacts:
  - PROD-009
  - ADR-002
owner: <person or team>
updated: YYYY-MM-DD

# Discovery origin (optional)
discovered_by:
  kind: audit | survey | agent | human
  ref: AUD-XXX | VA-XXX | VH-XXX | <notes>
```

## Optional fields
- tags: [list]
- links: [related DL entries]

## Example entry (markdown wrapper)
```md
### DL-003: Contract role vs spec role

```yaml
id: DL-003
status: open
severity: significant
entry_type: contradiction
topic: contracts
sources:
  - kind: prod
    ref: PROD-008
    note: "contracts are canonical"
  - kind: adr
    ref: ADR-002
    note: "contracts are derived"
claims:
  - kind: assertion
    label: A
    text: "Contracts are canonical"
  - kind: assertion
    label: B
    text: "Contracts are derived views"
analysis: Conflicting statements about contract authority.
assessment: disputed
resolution_path: ADR
owner: david
updated: 2026-03-05
```

```

## Notes
- This can be a standalone artifact type or a structured block embedded in a
  delta (e.g., DE-047 contradiction work).
- The schema intentionally supports both doc-doc contradictions and
  doc-implementation drift.

## Lifecycle Rules (minimum)
- open → triaged (requires: severity, topic, owner)
- triaged → adjudicated (requires: assessment)
- adjudicated → resolved (requires: resolution_path, resolution_ref, affected_artifacts)
- adjudicated → deferred (requires: reason in analysis or notes)
- deferred → open (re-opened with new evidence)
