# supekku.scripts.lib.workflow.review_io_test

Tests for review I/O (DR-102 §3.3/§3.4/§5, DR-109 §3.3/§3.5).

Covers: v2 accumulative rounds (VT-109-004), v1 rejection (VA-109-001),
judgment_status in review-index, and finding status re-derivation.

## Functions

- `_minimal_findings_v2() -> dict`: Return minimal valid v2 review-findings dict.
- `_minimal_index() -> dict`: Return minimal valid review-index dict.
- `_v1_findings() -> dict`: Return a v1 review-findings dict (pre-accumulative).

## Classes

### AppendRoundTest

**Inherits from:** unittest.TestCase

#### Methods

- `test_append_multiple_rounds(self) -> None`
- `test_append_preserves_prior_rounds(self) -> None`
- `test_append_writes_validly(self) -> None`

### BuildFindingsV2Test

**Inherits from:** unittest.TestCase

#### Methods

- `test_build_omits_empty_session(self) -> None`
- `test_build_validates_on_write(self) -> None`
- `test_build_with_findings(self) -> None`
- `test_build_with_session(self) -> None`
- `test_minimal_build(self) -> None`

### BuildReviewIndexTest

**Inherits from:** unittest.TestCase

#### Methods

- `test_build_omits_empty_optionals(self) -> None`
- `test_build_validates_on_write(self) -> None`
- `test_build_with_judgment_status(self) -> None`
- `test_build_with_optionals(self) -> None`
- `test_build_without_judgment_status(self) -> None`
- `test_minimal_build(self) -> None`

### BuildRoundEntryTest

**Inherits from:** unittest.TestCase

#### Methods

- `test_minimal_round(self) -> None`
- `test_round_with_findings(self) -> None`

### FindFindingTest

**Inherits from:** unittest.TestCase

#### Methods

- `test_finds_across_rounds(self) -> None`
- `test_finds_in_blocking(self) -> None`
- `test_finds_in_non_blocking(self) -> None`
- `test_not_found_returns_none(self) -> None`

### FindingsVersionTest

**Inherits from:** unittest.TestCase

#### Methods

- `test_v1_error_includes_path(self) -> None`
- `test_v1_raises_findings_version_error(self) -> None`: v1 files are rejected with clear error directing to teardown.

### NextRoundNumberTest

**Inherits from:** unittest.TestCase

#### Methods

- `test_increments_from_existing_v2(self) -> None`
- `test_increments_from_round_3(self) -> None`
- `test_no_findings_returns_1(self) -> None`

### PathTest

**Inherits from:** unittest.TestCase

#### Methods

- `test_bootstrap_path_default(self) -> None`
- `test_findings_path_default(self) -> None`
- `test_index_path_default(self) -> None`

### ReadFindingsV2Test

**Inherits from:** unittest.TestCase

#### Methods

- `test_read_missing_raises(self) -> None`
- `test_read_valid_v2(self) -> None`

### ReadReviewIndexTest

**Inherits from:** unittest.TestCase

#### Methods

- `test_read_missing_raises(self) -> None`
- `test_read_valid(self) -> None`

### StatusRederivationTest

Status is re-derived from disposition on read.

**Inherits from:** unittest.TestCase

#### Methods

- `test_defer_rederives_to_open(self) -> None`
- `test_fix_rederives_to_resolved(self) -> None`
- `test_no_disposition_stays_open(self) -> None`

### UpdateFindingDispositionTest

**Inherits from:** unittest.TestCase

#### Methods

- `test_not_found_returns_false(self) -> None`
- `test_updates_across_rounds(self) -> None`
- `test_updates_in_originating_round(self) -> None`

### WriteFindingsV2Test

**Inherits from:** unittest.TestCase

#### Methods

- `test_atomic_no_temp_files(self) -> None`
- `test_write_rejects_invalid(self) -> None`
- `test_write_valid_v2(self) -> None`

### WriteReviewIndexTest

**Inherits from:** unittest.TestCase

#### Methods

- `test_atomic_no_temp_files(self) -> None`
- `test_write_rejects_invalid(self) -> None`
- `test_write_valid(self) -> None`
