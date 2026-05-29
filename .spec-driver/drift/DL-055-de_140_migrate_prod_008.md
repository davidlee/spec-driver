---
id: DL-055
name: DE-140 requirements migration PROD-008
created: '2026-05-28'
updated: '2026-05-30'
status: closed
kind: drift_ledger
delta_ref: DE-140
---

# DL-055 — DE-140 requirements migration PROD-008

Drift entries from requirements migration of PROD-008.

> **Disposition (DE-136 Phase 4 close, VA-DE136-CLOSE-001):** closed as tolerated drift per IP-136 §4. `requirement_unparseable` entries are false positives (coverage/relationship reference lines, not requirement definitions) → **dismissed**. `*_placeholder` entries are real but minor backfill debt → **deferred**. Durable residue tracked in **ISSUE-064**. Entry `detail` fields re-quoted to valid YAML (emitter bug fixed in DE-136 P4).

## Entries

### DL-055.001: requirement_unparseable — PROD-008

```yaml
target: PROD-008
drift_kind: requirement_unparseable
detail: "unparseable requirement-like line: - PROD-008.FR-001"
disposition: dismissed
owner: unassigned
status: dismissed
```

### DL-055.002: requirement_unparseable — PROD-008

```yaml
target: PROD-008
drift_kind: requirement_unparseable
detail: "unparseable requirement-like line: - PROD-008.FR-002"
disposition: dismissed
owner: unassigned
status: dismissed
```

### DL-055.003: requirement_unparseable — PROD-008

```yaml
target: PROD-008
drift_kind: requirement_unparseable
detail: "unparseable requirement-like line: - PROD-008.FR-003"
disposition: dismissed
owner: unassigned
status: dismissed
```

### DL-055.004: requirement_unparseable — PROD-008

```yaml
target: PROD-008
drift_kind: requirement_unparseable
detail: "unparseable requirement-like line: - SPEC-036.FR-004"
disposition: dismissed
owner: unassigned
status: dismissed
```

### DL-055.005: requirement_unparseable — PROD-008

```yaml
target: PROD-008
drift_kind: requirement_unparseable
detail: "unparseable requirement-like line: - PROD-008.FR-001"
disposition: dismissed
owner: unassigned
status: dismissed
```

### DL-055.006: requirement_unparseable — PROD-008

```yaml
target: PROD-008
drift_kind: requirement_unparseable
detail: "unparseable requirement-like line: - PROD-008.FR-002"
disposition: dismissed
owner: unassigned
status: dismissed
```

### DL-055.007: requirement_unparseable — PROD-008

```yaml
target: PROD-008
drift_kind: requirement_unparseable
detail: "unparseable requirement-like line: - PROD-008.FR-003"
disposition: dismissed
owner: unassigned
status: dismissed
```

### DL-055.008: requirement_unparseable — PROD-008

```yaml
target: PROD-008
drift_kind: requirement_unparseable
detail: "unparseable requirement-like line: requirement: PROD-008.FR-001"
disposition: dismissed
owner: unassigned
status: dismissed
```

### DL-055.009: requirement_unparseable — PROD-008

```yaml
target: PROD-008
drift_kind: requirement_unparseable
detail: "unparseable requirement-like line: requirement: PROD-008.FR-002"
disposition: dismissed
owner: unassigned
status: dismissed
```

### DL-055.010: requirement_unparseable — PROD-008

```yaml
target: PROD-008
drift_kind: requirement_unparseable
detail: "unparseable requirement-like line: requirement: PROD-008.FR-003"
disposition: dismissed
owner: unassigned
status: dismissed
```

### DL-055.011: description_placeholder — PROD-008

```yaml
target: PROD-008
drift_kind: description_placeholder
detail: "FR-001: description is empty placeholder"
disposition: deferred
owner: unassigned
status: deferred
```

### DL-055.012: acceptance_placeholder — PROD-008

```yaml
target: PROD-008
drift_kind: acceptance_placeholder
detail: "FR-001: acceptance_criteria is empty placeholder"
disposition: deferred
owner: unassigned
status: deferred
```

### DL-055.013: description_placeholder — PROD-008

```yaml
target: PROD-008
drift_kind: description_placeholder
detail: "FR-002: description is empty placeholder"
disposition: deferred
owner: unassigned
status: deferred
```

### DL-055.014: acceptance_placeholder — PROD-008

```yaml
target: PROD-008
drift_kind: acceptance_placeholder
detail: "FR-002: acceptance_criteria is empty placeholder"
disposition: deferred
owner: unassigned
status: deferred
```

### DL-055.015: description_placeholder — PROD-008

```yaml
target: PROD-008
drift_kind: description_placeholder
detail: "FR-003: description is empty placeholder"
disposition: deferred
owner: unassigned
status: deferred
```

### DL-055.016: acceptance_placeholder — PROD-008

```yaml
target: PROD-008
drift_kind: acceptance_placeholder
detail: "FR-003: acceptance_criteria is empty placeholder"
disposition: deferred
owner: unassigned
status: deferred
```

### DL-055.017: description_placeholder — PROD-008

```yaml
target: PROD-008
drift_kind: description_placeholder
detail: "NF-001: description is empty placeholder"
disposition: deferred
owner: unassigned
status: deferred
```

### DL-055.018: acceptance_placeholder — PROD-008

```yaml
target: PROD-008
drift_kind: acceptance_placeholder
detail: "NF-001: acceptance_criteria is empty placeholder"
disposition: deferred
owner: unassigned
status: deferred
```

### DL-055.019: description_placeholder — PROD-008

```yaml
target: PROD-008
drift_kind: description_placeholder
detail: "NF-002: description is empty placeholder"
disposition: deferred
owner: unassigned
status: deferred
```

### DL-055.020: acceptance_placeholder — PROD-008

```yaml
target: PROD-008
drift_kind: acceptance_placeholder
detail: "NF-002: acceptance_criteria is empty placeholder"
disposition: deferred
owner: unassigned
status: deferred
```
