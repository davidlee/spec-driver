# Notes for DE-078

## Phase 1 — Implementation

- Added `list_audits` to `supekku/cli/list.py` (lines ~1449–1537), cloning `list_revisions` pattern exactly
- Registered `"audits": "audit"` in `_PLURAL_TO_SINGULAR` for automatic singular alias
- 10 tests added across `TestListCommands` (help + alias) and `TestListAudits` (functional) and `TestJSONFlagConsistency` (json flag + parity)
- All 3603 tests pass, ruff clean, no new pylint warnings
- End-to-end verified: `spec-driver list audits` and `spec-driver list audit` both work
