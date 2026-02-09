# supekku.cli.view_test

Tests for view command.

## Constants

- `runner`

## Classes

### TestGetPager

Tests for get_pager function.

#### Methods

- `test_falls_back_to_less(self, monkeypatch) -> None`: Falls back to less when $PAGER unset.
- `test_falls_back_to_more(self, monkeypatch) -> None`: Falls back to more when less unavailable.
- `test_returns_none_when_no_pager(self, monkeypatch) -> None`: Returns None when no pager available.
- `test_returns_pager_env_var(self, monkeypatch) -> None`: Returns $PAGER when set.

### TestNoPagerAvailable

Tests for error handling when no pager available.

#### Methods

- `test_error_when_no_pager(self, monkeypatch) -> None`: Shows error when no pager available.

### TestNormalizeId

Tests for normalize_id function.

#### Methods

- `test_all_artifact_types(self) -> None`: All unambiguous artifact types normalize correctly.
- `test_already_prefixed_unchanged(self) -> None`: ID with prefix is returned unchanged (uppercased).
- `test_ambiguous_types_unchanged(self) -> None`: Ambiguous artifact types are not normalized.
- `test_non_numeric_unchanged(self) -> None`: Non-numeric IDs are returned unchanged.
- `test_numeric_only_gets_prefix_and_padding(self) -> None`: Numeric-only ID gets prefix and zero-padding.

### TestViewAdr

Tests for view adr command.

#### Methods

- `test_view_adr_calls_pager(self, tmp_path, monkeypatch) -> None`: View adr opens file in pager.
- `test_view_adr_not_found(self, monkeypatch) -> None`: View adr shows error when not found.

### TestViewAdrShorthand

Tests for view adr with shorthand IDs.

#### Methods

- `test_view_adr_numeric_shorthand(self, tmp_path, monkeypatch) -> None`: View adr accepts numeric shorthand like '001'.

### TestViewDelta

Tests for view delta command.

#### Methods

- `test_view_delta_calls_pager(self, tmp_path, monkeypatch) -> None`: View delta opens file in pager.

### TestViewDeltaShorthand

Tests for view delta with shorthand IDs.

#### Methods

- `test_view_delta_numeric_shorthand(self, tmp_path, monkeypatch) -> None`: View delta accepts numeric shorthand like '23'.

### TestViewSpec

Tests for view spec command.

#### Methods

- `test_view_spec_calls_pager(self, tmp_path, monkeypatch) -> None`: View spec opens file in pager.
