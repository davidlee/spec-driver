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

## Functions

- `append_round(existing) -> dict[Tuple[str, Any]]`: Append a new round to existing v2 findings (accumulative).

Returns the mutated findings dict. Does NOT write to disk —
caller must use `write_findings()` after.

- `bootstrap_path(delta_dir, state_dir) -> Path`: Return the path to workflow/review-bootstrap.md.
- `build_findings() -> dict[Tuple[str, Any]]`: Build a v2 review-findings payload with a single round.

For the first round of a new review. Use `append_round()` to add
subsequent rounds to an existing findings file.

- `build_review_index() -> dict[Tuple[str, Any]]`: Build a review-index payload dict.

Returns a dict ready for `write_review_index`.

- `build_round_entry() -> dict[Tuple[str, Any]]`: Build a single round entry for the rounds array (DR-109 §3.5).
- `find_finding(data, finding_id) -> <BinOp>`: Locate a finding by ID across all rounds. Returns None if not found.
- `findings_path(delta_dir, state_dir) -> Path`: Return the path to workflow/review-findings.yaml.
- `index_path(delta_dir, state_dir) -> Path`: Return the path to workflow/review-index.yaml.
- `next_round_number(delta_dir, state_dir) -> int`: Return the next round number for review findings.

If no findings exist, returns 1. Otherwise, returns current_round + 1.
Raises FindingsVersionError on v1 files.

- `read_findings(delta_dir, state_dir) -> dict[Tuple[str, Any]]`: Read and validate review-findings.yaml (v2 only).

Raises:
FindingsNotFoundError: If the file does not exist.
FindingsVersionError: If the file is v1 (pre-accumulative).
FindingsValidationError: If content fails schema validation.

- `read_review_index(delta_dir, state_dir) -> dict[Tuple[str, Any]]`: Read and validate review-index.yaml.

Raises:
ReviewIndexNotFoundError: If the file does not exist.
ReviewIndexValidationError: If content fails schema validation.

- `update_finding_disposition(data, finding_id, disposition) -> bool`: Update a finding's disposition in-place within its originating round.

Searches all rounds for the finding by ID, updates disposition and
re-derives status. Returns True if found, False if not.

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

### FindingsVersionError

Raised when review-findings.yaml is v1 (pre-accumulative).

Recovery: `review teardown` + `review prime` to start fresh with v2.

**Inherits from:** Exception

### ReviewIndexNotFoundError

Raised when review-index.yaml does not exist.

**Inherits from:** Exception

### ReviewIndexValidationError

Raised when review-index data fails schema validation.

**Inherits from:** Exception
