# supekku.scripts.lib.backlog.models_test

Tests for backlog models and status vocabulary (VT-057 + VT-075).

## Classes

### BacklogItemExtFieldsTest

VT-067-001: BacklogItem supports ext_id and ext_url fields.

**Inherits from:** unittest.TestCase

#### Methods

- `test_ext_fields_default_to_empty(self) -> None`
- `test_ext_fields_populated(self) -> None`

### IsValidStatusTest

Test is_valid_status() helper.

**Inherits from:** unittest.TestCase

#### Methods

- `test_base_status_valid_for_all_kinds(self) -> None`
- `test_risk_extra_invalid_for_non_risk(self) -> None`
- `test_risk_extra_valid_for_risk(self) -> None`
- `test_terminal_statuses_are_valid(self) -> None`
- `test_unknown_kind_returns_false(self) -> None`
- `test_unknown_status_returns_false(self) -> None`

### UnifiedStatusSetsTest

Test unified backlog status sets (DEC-075-05).

**Inherits from:** unittest.TestCase

#### Methods

- `test_all_valid_statuses(self) -> None`
- `test_backlog_statuses_covers_all_kinds(self) -> None`
- `test_base_statuses(self) -> None`
- `test_default_hidden_statuses(self) -> None`
- `test_non_risk_kinds_share_base(self) -> None`
- `test_risk_extra_statuses(self) -> None`
- `test_risk_kind_has_extensions(self) -> None`
- `test_risk_statuses_is_superset_of_base(self) -> None`
- `test_sets_are_frozen(self) -> None`
