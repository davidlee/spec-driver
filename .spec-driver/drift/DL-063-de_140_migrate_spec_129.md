---
id: DL-063
name: DE-140 requirements migration SPEC-129
created: '2026-05-28'
updated: '2026-05-30'
status: closed
kind: drift_ledger
delta_ref: DE-140
---

# DL-063 — DE-140 requirements migration SPEC-129

Drift entries from requirements migration of SPEC-129.

> **Disposition (DE-136 Phase 4 close, VA-DE136-CLOSE-001):** closed as tolerated drift per IP-136 §4. `requirement_unparseable` entries are false positives (coverage/relationship reference lines, not requirement definitions) → **dismissed**. `*_placeholder` entries are real but minor backfill debt → **deferred**. Durable residue tracked in **ISSUE-064**. Entry `detail` fields re-quoted to valid YAML (emitter bug fixed in DE-136 P4).

## Entries

### DL-063.001: requirement_unparseable — SPEC-129

```yaml
target: SPEC-129
drift_kind: requirement_unparseable
detail: "unparseable requirement-like line: requirement: SPEC-129.FR-001"
disposition: dismissed
owner: unassigned
status: dismissed
```

### DL-063.002: description_placeholder — SPEC-129

```yaml
target: SPEC-129
drift_kind: description_placeholder
detail: "FR-001: description is empty placeholder"
disposition: deferred
owner: unassigned
status: deferred
```

### DL-063.003: acceptance_placeholder — SPEC-129

```yaml
target: SPEC-129
drift_kind: acceptance_placeholder
detail: "FR-001: acceptance_criteria is empty placeholder"
disposition: deferred
owner: unassigned
status: deferred
```

### DL-063.004: description_placeholder — SPEC-129

```yaml
target: SPEC-129
drift_kind: description_placeholder
detail: "FR-002: description is empty placeholder"
disposition: deferred
owner: unassigned
status: deferred
```

### DL-063.005: acceptance_placeholder — SPEC-129

```yaml
target: SPEC-129
drift_kind: acceptance_placeholder
detail: "FR-002: acceptance_criteria is empty placeholder"
disposition: deferred
owner: unassigned
status: deferred
```

### DL-063.006: description_placeholder — SPEC-129

```yaml
target: SPEC-129
drift_kind: description_placeholder
detail: "FR-003: description is empty placeholder"
disposition: deferred
owner: unassigned
status: deferred
```

### DL-063.007: acceptance_placeholder — SPEC-129

```yaml
target: SPEC-129
drift_kind: acceptance_placeholder
detail: "FR-003: acceptance_criteria is empty placeholder"
disposition: deferred
owner: unassigned
status: deferred
```

### DL-063.008: description_placeholder — SPEC-129

```yaml
target: SPEC-129
drift_kind: description_placeholder
detail: "NF-001: description is empty placeholder"
disposition: deferred
owner: unassigned
status: deferred
```

### DL-063.009: acceptance_placeholder — SPEC-129

```yaml
target: SPEC-129
drift_kind: acceptance_placeholder
detail: "NF-001: acceptance_criteria is empty placeholder"
disposition: deferred
owner: unassigned
status: deferred
```

### DL-063.010: description_placeholder — SPEC-129

```yaml
target: SPEC-129
drift_kind: description_placeholder
detail: "NF-002: description is empty placeholder"
disposition: deferred
owner: unassigned
status: deferred
```

### DL-063.011: acceptance_placeholder — SPEC-129

```yaml
target: SPEC-129
drift_kind: acceptance_placeholder
detail: "NF-002: acceptance_criteria is empty placeholder"
disposition: deferred
owner: unassigned
status: deferred
```

### DL-063.012: description_placeholder — SPEC-129

```yaml
target: SPEC-129
drift_kind: description_placeholder
detail: "NF-003: description is empty placeholder"
disposition: deferred
owner: unassigned
status: deferred
```

### DL-063.013: acceptance_placeholder — SPEC-129

```yaml
target: SPEC-129
drift_kind: acceptance_placeholder
detail: "NF-003: acceptance_criteria is empty placeholder"
disposition: deferred
owner: unassigned
status: deferred
```
