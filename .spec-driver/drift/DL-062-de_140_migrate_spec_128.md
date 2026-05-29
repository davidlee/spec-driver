---
id: DL-062
name: DE-140 requirements migration SPEC-128
created: '2026-05-28'
updated: '2026-05-30'
status: closed
kind: drift_ledger
delta_ref: DE-140
---

# DL-062 — DE-140 requirements migration SPEC-128

Drift entries from requirements migration of SPEC-128.

> **Disposition (DE-136 Phase 4 close, VA-DE136-CLOSE-001):** closed as tolerated drift per IP-136 §4. `requirement_unparseable` entries are false positives (coverage/relationship reference lines, not requirement definitions) → **dismissed**. `*_placeholder` entries are real but minor backfill debt → **deferred**. Durable residue tracked in **ISSUE-064**. Entry `detail` fields re-quoted to valid YAML (emitter bug fixed in DE-136 P4).

## Entries

### DL-062.001: requirement_unparseable — SPEC-128

```yaml
target: SPEC-128
drift_kind: requirement_unparseable
detail: "unparseable requirement-like line: requirement: SPEC-128.FR-001"
disposition: dismissed
owner: unassigned
status: dismissed
```

### DL-062.002: description_placeholder — SPEC-128

```yaml
target: SPEC-128
drift_kind: description_placeholder
detail: "FR-001: description is empty placeholder"
disposition: deferred
owner: unassigned
status: deferred
```

### DL-062.003: acceptance_placeholder — SPEC-128

```yaml
target: SPEC-128
drift_kind: acceptance_placeholder
detail: "FR-001: acceptance_criteria is empty placeholder"
disposition: deferred
owner: unassigned
status: deferred
```

### DL-062.004: description_placeholder — SPEC-128

```yaml
target: SPEC-128
drift_kind: description_placeholder
detail: "FR-002: description is empty placeholder"
disposition: deferred
owner: unassigned
status: deferred
```

### DL-062.005: acceptance_placeholder — SPEC-128

```yaml
target: SPEC-128
drift_kind: acceptance_placeholder
detail: "FR-002: acceptance_criteria is empty placeholder"
disposition: deferred
owner: unassigned
status: deferred
```

### DL-062.006: description_placeholder — SPEC-128

```yaml
target: SPEC-128
drift_kind: description_placeholder
detail: "FR-003: description is empty placeholder"
disposition: deferred
owner: unassigned
status: deferred
```

### DL-062.007: acceptance_placeholder — SPEC-128

```yaml
target: SPEC-128
drift_kind: acceptance_placeholder
detail: "FR-003: acceptance_criteria is empty placeholder"
disposition: deferred
owner: unassigned
status: deferred
```

### DL-062.008: description_placeholder — SPEC-128

```yaml
target: SPEC-128
drift_kind: description_placeholder
detail: "NF-001: description is empty placeholder"
disposition: deferred
owner: unassigned
status: deferred
```

### DL-062.009: acceptance_placeholder — SPEC-128

```yaml
target: SPEC-128
drift_kind: acceptance_placeholder
detail: "NF-001: acceptance_criteria is empty placeholder"
disposition: deferred
owner: unassigned
status: deferred
```

### DL-062.010: description_placeholder — SPEC-128

```yaml
target: SPEC-128
drift_kind: description_placeholder
detail: "NF-002: description is empty placeholder"
disposition: deferred
owner: unassigned
status: deferred
```

### DL-062.011: acceptance_placeholder — SPEC-128

```yaml
target: SPEC-128
drift_kind: acceptance_placeholder
detail: "NF-002: acceptance_criteria is empty placeholder"
disposition: deferred
owner: unassigned
status: deferred
```

### DL-062.012: description_placeholder — SPEC-128

```yaml
target: SPEC-128
drift_kind: description_placeholder
detail: "NF-003: description is empty placeholder"
disposition: deferred
owner: unassigned
status: deferred
```

### DL-062.013: acceptance_placeholder — SPEC-128

```yaml
target: SPEC-128
drift_kind: acceptance_placeholder
detail: "NF-003: acceptance_criteria is empty placeholder"
disposition: deferred
owner: unassigned
status: deferred
```
