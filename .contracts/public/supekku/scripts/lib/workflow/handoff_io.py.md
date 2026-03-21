# supekku.scripts.lib.workflow.handoff_io

Read and write workflow handoff.current.yaml with schema validation.

All mutations to handoff.current.yaml go through ``write_handoff``,
which validates output against the schema before writing.  Writes are
atomic (write-to-temp + rename) per DR-102 §5.

Design authority: DR-102 §3.2, §5.

## Constants

- `DEFAULT_STATE_DIR`
- `HANDOFF_FILENAME`

## Functions

- `build_handoff() -> dict[Tuple[str, Any]]`: Build a handoff payload dict.

Returns a dict ready for ``write_handoff``.
- `handoff_path(delta_dir, state_dir) -> Path`: Return the path to workflow/handoff.current.yaml.
- `read_handoff(delta_dir, state_dir) -> dict[Tuple[str, Any]]`: Read and validate handoff.current.yaml.

Raises:
  HandoffNotFoundError: If the file does not exist.
  HandoffValidationError: If content fails schema validation.
- `write_handoff(delta_dir, data, state_dir) -> Path`: Validate and atomically write handoff.current.yaml.

Returns:
  Path to the written file.

Raises:
  HandoffValidationError: If data fails schema validation.

## Classes

### HandoffNotFoundError

Raised when handoff.current.yaml does not exist.

**Inherits from:** Exception

### HandoffValidationError

Raised when handoff data fails schema validation.

**Inherits from:** Exception
