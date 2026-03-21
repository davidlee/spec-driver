# supekku.scripts.lib.workflow.review_io_test

Tests for review I/O (DR-102 §3.3, §3.4, §5).

## Functions

- `_minimal_findings() -> dict`: Return minimal valid review-findings dict.
- `_minimal_index() -> dict`: Return minimal valid review-index dict.

## Classes

### BuildFindingsTest

**Inherits from:** unittest.TestCase

#### Methods

- `test_build_omits_empty_optionals(self) -> None`
- `test_build_validates_on_write(self) -> None`
- `test_build_with_findings(self) -> None`
- `test_minimal_build(self) -> None`

### BuildReviewIndexTest

**Inherits from:** unittest.TestCase

#### Methods

- `test_build_omits_empty_optionals(self) -> None`
- `test_build_validates_on_write(self) -> None` - review-index uses last_bootstrapped_at
- `test_build_with_optionals(self) -> None`
- `test_minimal_build(self) -> None`

### NextRoundNumberTest

**Inherits from:** unittest.TestCase

#### Methods

- `test_increments_from_existing(self) -> None`
- `test_increments_from_round_3(self) -> None`
- `test_no_findings_returns_1(self) -> None`

### PathTest

**Inherits from:** unittest.TestCase

#### Methods

- `test_bootstrap_path_default(self) -> None`
- `test_findings_path_default(self) -> None`
- `test_index_path_default(self) -> None`

### ReadFindingsTest

**Inherits from:** unittest.TestCase

#### Methods

- `test_read_missing_raises(self) -> None`
- `test_read_valid(self) -> None`

### ReadReviewIndexTest

**Inherits from:** unittest.TestCase

#### Methods

- `test_read_missing_raises(self) -> None`
- `test_read_valid(self) -> None`

### WriteFindingsTest

**Inherits from:** unittest.TestCase

#### Methods

- `test_atomic_no_temp_files(self) -> None`
- `test_write_rejects_invalid(self) -> None`
- `test_write_valid(self) -> None`

### WriteReviewIndexTest

**Inherits from:** unittest.TestCase

#### Methods

- `test_atomic_no_temp_files(self) -> None`
- `test_write_rejects_invalid(self) -> None`
- `test_write_valid(self) -> None`
