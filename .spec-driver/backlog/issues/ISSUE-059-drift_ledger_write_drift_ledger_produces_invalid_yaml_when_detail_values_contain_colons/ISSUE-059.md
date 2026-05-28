---
id: ISSUE-059
name: Drift ledger write_drift_ledger() produces invalid YAML when detail values contain colons
created: "2026-05-28"
updated: "2026-05-28"
status: open
kind: issue
categories: []
severity: p3
impact: user
---

# Drift ledger write_drift_ledger() produces invalid YAML when detail values contain colons

## Description

`write_drift_ledger()` in `spec_driver/migrations/spec_requirements/migration.py` emits drift entry YAML blocks with unquoted `detail:` values. When the value itself contains a colon (e.g., `detail: NF-001: description is empty placeholder`), the resulting YAML is malformed — the second colon creates an invalid mapping.

## Reproduction

```bash
uv run spec-driver admin migrate-requirements PROD-007
# produces DL-049 with entries like:
#   detail: NF-001: description is empty placeholder
# which fails YAML parsing
```

## Expected

Values containing colons should be quoted:
```yaml
detail: "NF-001: description is empty placeholder"
```

## Observed

`validate workspace` emits warnings:
```
Malformed YAML in entry: mapping values are not allowed here
```

## Affected files

- `spec_driver/migrations/spec_requirements/migration.py` — `write_drift_ledger()`
- `DL-049` (and any future drift ledgers produced by this function)

## Fix

Quote `detail` values in the YAML template string, or use `yaml.dump()` for the entry blocks instead of f-string templating.

## References

- AUD-027 finding F-004
- DE-140 (origin delta)
