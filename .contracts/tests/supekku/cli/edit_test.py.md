# supekku.cli.edit_test

Tests for edit command.

## Constants

- `DELTA_FRONTMATTER` - ── --status flag tests (DE-068, VT-068-02, VT-068-03) ──
- `runner`

## Classes

### TestEditAdr

Tests for edit adr command.

#### Methods

- `test_edit_adr_calls_editor(self, tmp_path, monkeypatch) -> None`: Edit adr opens file in editor.
- `test_edit_adr_not_found(self, monkeypatch) -> None`: Edit adr shows error when not found.

### TestEditAdrShorthand

Tests for edit adr with shorthand IDs.

#### Methods

- `test_edit_adr_numeric_shorthand(self, tmp_path, monkeypatch) -> None`: Edit adr accepts numeric shorthand like '001'.

### TestEditDelta

Tests for edit delta command.

#### Methods

- `test_edit_delta_calls_editor(self, tmp_path, monkeypatch) -> None`: Edit delta opens file in editor.

### TestEditDeltaShorthand

Tests for edit delta with shorthand IDs.

#### Methods

- `test_edit_delta_numeric_shorthand(self, tmp_path, monkeypatch) -> None`: Edit delta accepts numeric shorthand like '23'.

### TestEditDrift

Tests for edit drift subcommand (new in DE-068).

#### Methods

- `test_edit_drift_opens_editor(self, tmp_path) -> None`
- `test_edit_drift_rejects_invalid_status(self, tmp_path) -> None`
- `test_edit_drift_resolver_key(self, tmp_path) -> None`: Drift uses 'drift_ledger' resolver key, not 'drift'.
- `test_edit_drift_status_update(self, tmp_path) -> None`

### TestEditNewSubcommands

Tests for Phase 2 edit subcommands using mocked resolution.

#### Methods

- `test_edit_audit(self, tmp_path) -> None`
- `test_edit_improvement(self, tmp_path) -> None`
- `test_edit_issue(self, tmp_path) -> None`
- `test_edit_plan(self, tmp_path) -> None`
- `test_edit_plan_not_found(self) -> None`

### TestEditRevisionRegression

Regression tests for edit revision — must pass before AND after migration.

#### Methods

- `test_edit_revision_invokes_editor(self) -> None`: edit revision RE-001 opens editor with correct file.
- `test_edit_revision_not_found(self) -> None`: edit revision with nonexistent ID fails gracefully.
- `test_edit_revision_numeric_shorthand(self) -> None`: edit revision 1 resolves to RE-001.

### TestEditSpec

Tests for edit spec command.

#### Methods

- `test_edit_spec_calls_editor(self, tmp_path, monkeypatch) -> None`: Edit spec opens file in editor.

### TestEditStatusFlag

Tests for --status flag on edit subcommands.

#### Methods

- `test_status_accepts_valid_value_for_spec(self, tmp_path) -> None`: --status with a valid spec status succeeds.
- `test_status_rejects_empty_value(self, tmp_path) -> None`: --status with empty string fails.
- `test_status_rejects_invalid_value_for_delta(self, tmp_path) -> None`: --status with invalid value for enum-covered entity type fails.
- `test_status_rejects_invalid_value_for_spec(self, tmp_path) -> None`: --status with invalid spec status fails.
- `test_status_updates_frontmatter_skips_editor(self, tmp_path) -> None`: --status updates file and does not open editor.
- `test_without_status_opens_editor(self, tmp_path, monkeypatch) -> None`: Default behaviour (no --status) still opens editor.

### TestEditStatusResolveArtifact

Tests for --status on resolve_artifact-based subcommands.

#### Methods

- `test_issue_status_rejects_invalid(self, tmp_path) -> None`
- `test_issue_status_update(self, tmp_path) -> None`

### TestGetEditor

Tests for get_editor function.

#### Methods

- `test_falls_back_to_vi(self, monkeypatch) -> None`: Falls back to vi when env vars unset.
- `test_returns_editor_env_var(self, monkeypatch) -> None`: Returns $EDITOR when set.
- `test_returns_none_when_no_editor(self, monkeypatch) -> None`: Returns None when no editor available.
- `test_returns_visual_env_var(self, monkeypatch) -> None`: Returns $VISUAL when $EDITOR unset.

### TestNoEditorAvailable

Tests for error handling when no editor available.

#### Methods

- `test_error_when_no_editor(self, monkeypatch) -> None`: Shows error when no editor available.
