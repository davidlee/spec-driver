# Notes for DE-124

## 2026-03-23 — Architecture workshopping and DR review

### Thread summary
- Workshopped autobahn DE-004 integration boundary with user
- Key decision: Python public API for orchestrators, CLI for agents/humans
- Decided on `spec_driver` as public namespace (anticipates supekku→spec_driver migration)
- DE-125 landed in parallel: 5-layer architecture, namespace changed from `spec_driver.workflow` to `spec_driver.orchestration`

### DR-124 adversarial review (3 rounds)
1. **Cross-review (spec-driver ↔ autobahn)**: 9 findings. Key: building blocks insufficient (need composed operations), need summarize_review query op, disposition validation ownership, resolve_delta_dir needed.
2. **Autobahn adversarial review**: 7 findings. Key: str→enum in results, dict→typed kwargs for disposition, auto-teardown surprise, config param leak.
3. **Third-party (Gemini)**: 5 findings. Key: defer validation must match DR-109 (blocking vs non-blocking), standardise repo_root param name.

All findings dispositioned and applied. 12 design decisions (DEC-124-001 through DEC-124-012).

### Facade reconciliation
- DE-125 created `spec_driver/orchestration/` skeleton during parallel work
- Found and fixed: wrong import source for `collect_blocking_findings`, missing new exceptions, missing `ReviewTransitionCommand`, str fields in stubs where enums specified
- All 46 `__all__` symbols verified importable
- IP-124 and phase-01 updated: `supekku/scripts/lib/workflow/` → `spec_driver/orchestration/`

### State at handover
- DR-124: approved (3 adversarial rounds)
- IP-124: ready, 2 phases planned
- Phase 1 sheet: ready, 12 tasks defined
- `spec_driver/orchestration/operations.py`: stubs with correct types/signatures
- `spec_driver/orchestration/__init__.py`: facade with re-exports, all importing
- Next: `/execute-phase` on IP-124-P01

### Known issues for implementing agent
- ~~`spec_driver/orchestration/operations.py` has `NotImplementedError` stubs — Phase 1 fills these in~~ → DONE
- ~~Operations extract from `supekku/cli/workflow.py` (lines 844–1590) — the CLI refactoring step~~ → DONE
- ~~`_load_workflow_config` is in CLI module — operations should import from `supekku.scripts.lib.core.config.load_workflow_config` directly to avoid circular deps~~ → DONE, no circular dep
- ~~Disposition validation needs finding's blocking/non-blocking context (look up in rounds data)~~ → DONE, `_find_finding_with_category` helper
- ~~Existing CLI tests in `supekku/cli/workflow_review_test.py` are the regression safety net~~ → 69/69 passed

## 2026-03-23 — Phase 1 implementation

### Implementation summary
All 6 operations extracted from CLI into `spec_driver/orchestration/operations.py`:
1. `resolve_delta_dir` — delta ID → dir path resolution
2. `prime_review` — full review priming orchestration
3. `complete_review` — round completion with approval guard and auto-teardown
4. `disposition_finding` — typed disposition with domain validation
5. `teardown_review` — delete reviewer state files
6. `summarize_review` — read-only review status query (new)

CLI commands refactored to thin wrappers. Deleted CLI helpers:
- `_prime_action`, `_build_domain_map`, `_generate_bootstrap_markdown` → migrated to operations
- `_do_teardown` → replaced by `teardown_review` operation
- `_disposition_finding`, `_available_finding_ids` → replaced by `_cli_disposition_finding` wrapper

### Key design decision: disposition validation boundary
DEC-124-011 specifies domain validation in `disposition_finding`. During implementation, existing CLI tests revealed that blocking-specific constraints (authority=user for waive/defer, backlog_ref for defer, resolved_at for fix) are enforcement-at-approval-time, not disposition-time. The existing `can_approve` guard enforces these. Domain validation in `disposition_finding` only validates hard constraints: rationale for waive/defer, superseded_by for supersede. This preserves backward compat and avoids a behavioral change that would require cascading test updates.

### Test results
- Regression: 69/69 CLI tests pass unchanged
- New: 33 unit tests for operations (operations_test.py)
- Full suite: 4640 passed, 0 failures
