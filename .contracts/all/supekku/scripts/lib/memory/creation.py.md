# supekku.scripts.lib.memory.creation

Shared logic for creating memory artifacts.

Memory IDs are user-supplied semantic dot-separated identifiers
(e.g., mem.pattern.cli.skinny). See ids.py for validation rules.

## Functions

- `build_memory_frontmatter(memory_id, options) -> dict`: Build frontmatter dictionary for a memory artifact.

Args:
memory_id: Canonical memory ID (e.g., 'mem.pattern.cli.skinny').
options: Creation options.

Returns:
Dictionary containing memory frontmatter.

- `create_memory(registry, options) -> MemoryCreationResult`: Create a new memory artifact with user-supplied semantic ID.

Args:
registry: Memory registry for uniqueness check.
options: Memory creation options (must include memory_id).

Returns:
MemoryCreationResult with ID, path, filename, and any warnings.

Raises:
ValueError: If the memory ID is malformed.
MemoryAlreadyExistsError: If a memory with this ID already exists.

## Classes

### MemoryAlreadyExistsError

Raised when attempting to create a memory that already exists.

**Inherits from:** Exception

### MemoryCreationOptions

Options for creating a new memory artifact.

### MemoryCreationResult

Result of creating a new memory artifact.
