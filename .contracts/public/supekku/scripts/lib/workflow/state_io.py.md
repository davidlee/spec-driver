# supekku.scripts.lib.workflow.state_io

Read and write workflow state.yaml with schema validation.

All mutations to state.yaml go through `write_state`, which validates
the output against the schema before writing. Writes are atomic
(write-to-temp + rename) per DR-102 §5.

Design authority: DR-102 §3.1, §5.

## Constants

- `DEFAULT_STATE_DIR` - Default workflow subdirectory within a delta bundle

## Functions

- `init_state() -> dict[Tuple[str, Any]]`: Create initial state.yaml data for `planned → implementing`.

Does NOT write the file — call `write_state` after transition.

Returns:
State dict ready for write_state.

- `read_state(delta_dir, state_dir) -> dict[Tuple[str, Any]]`: Read and validate workflow/state.yaml.

Args:
delta_dir: Path to the delta bundle directory.
state_dir: Subdirectory for workflow files.

Returns:
Parsed and validated state dict.

Raises:
StateNotFoundError: If the file does not exist.
StateValidationError: If the content fails schema validation.

- `state_path(delta_dir, state_dir) -> Path`: Return the path to workflow/state.yaml within a delta bundle.
- `update_state_workflow(data) -> dict[Tuple[str, Any]]`: Update workflow fields in a state dict (in-place).

Uses `...` (Ellipsis) as sentinel to distinguish "not provided"
from "set to None". Pass `claimed_by=None` to clear the claim.

Returns the mutated dict for convenience.

- `write_state(delta_dir, data, state_dir) -> Path`: Validate and atomically write workflow/state.yaml.

Args:
delta_dir: Path to the delta bundle directory.
data: State dict to write.
state_dir: Subdirectory for workflow files.

Returns:
Path to the written file.

Raises:
StateValidationError: If the data fails schema validation.

## Classes

### StateNotFoundError

Raised when workflow/state.yaml does not exist.

**Inherits from:** Exception

### StateValidationError

Raised when state.yaml data fails schema validation.

**Inherits from:** Exception
