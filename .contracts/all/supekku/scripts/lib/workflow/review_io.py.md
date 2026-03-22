# supekku.scripts.lib.workflow.review_io

Read and write review-index.yaml and review-findings.yaml.

All mutations go through `write_review_index` / `write_findings`,
which validate output against schemas before writing. Writes are
atomic (write-to-temp + rename) per DR-102 §5.

Design authority: DR-102 §3.3, §3.4, §5, §8.

## Constants

- `BOOTSTRAP_FILENAME`
- `DEFAULT_STATE_DIR`
- `FINDINGS_FILENAME`
- `INDEX_FILENAME`
- `_FINDINGS_VALIDATOR`
- `_INDEX_VALIDATOR` - ---------------------------------------------------------------------------

## Functions

- `_atomic_write(path, content) -> Path`: Write content atomically via temp-file + rename.
- `_now_iso() -> str`: Current UTC timestamp in ISO 8601 format.
- `bootstrap_path(delta_dir, state_dir) -> Path`: Return the path to workflow/review-bootstrap.md.
- `build_findings() -> dict[Tuple[str, Any]]`: Build a review-findings payload dict.

Returns a dict ready for `write_findings`.

- `build_review_index() -> dict[Tuple[str, Any]]`: Build a review-index payload dict.

Returns a dict ready for `write_review_index`.

- `findings_path(delta_dir, state_dir) -> Path`: Return the path to workflow/review-findings.yaml.
- `index_path(delta_dir, state_dir) -> Path`: Return the path to workflow/review-index.yaml.
- `next_round_number(delta_dir, state_dir) -> int`: Return the next round number for review findings.

If no findings exist, returns 1. Otherwise, returns current round + 1.

- `read_findings(delta_dir, state_dir) -> dict[Tuple[str, Any]]`: Read and validate review-findings.yaml.

Raises:
FindingsNotFoundError: If the file does not exist.
FindingsValidationError: If content fails schema validation.

- `read_review_index(delta_dir, state_dir) -> dict[Tuple[str, Any]]`: Read and validate review-index.yaml.

Raises:
ReviewIndexNotFoundError: If the file does not exist.
ReviewIndexValidationError: If content fails schema validation.

- `write_findings(delta_dir, data, state_dir) -> Path`: Validate and atomically write review-findings.yaml.

Raises:
FindingsValidationError: If data fails schema validation.

- `write_review_index(delta_dir, data, state_dir) -> Path`: Validate and atomically write review-index.yaml.

Raises:
ReviewIndexValidationError: If data fails schema validation.

## Classes

### FindingsNotFoundError

Raised when review-findings.yaml does not exist.

**Inherits from:** Exception

### FindingsValidationError

Raised when review-findings data fails schema validation.

**Inherits from:** Exception

#### Methods

- `__init__(self, errors) -> None`

### ReviewIndexNotFoundError

Raised when review-index.yaml does not exist.

**Inherits from:** Exception

### ReviewIndexValidationError

Raised when review-index data fails schema validation.

**Inherits from:** Exception

#### Methods

- `__init__(self, errors) -> None`
