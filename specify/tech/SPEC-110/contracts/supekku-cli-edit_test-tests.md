# supekku.cli.edit_test

Tests for edit command.

## Constants

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

### TestEditSpec

Tests for edit spec command.

#### Methods

- `test_edit_spec_calls_editor(self, tmp_path, monkeypatch) -> None`: Edit spec opens file in editor.

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
