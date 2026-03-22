# supekku.scripts.lib.memory.registry

MemoryRegistry — discovery, parsing, and querying of memory artifacts.

## Classes

### MemoryRegistry

Registry for discovering and querying memory artifact files.

Follows the same collect/find/iter/filter pattern as DecisionRegistry.
Memory files are expected to be named mem.\*.md in the memory directory.
Frontmatter `id` is the primary key; filename stem is fallback.

#### Methods

- `collect(self) -> dict[Tuple[str, MemoryRecord]]`: Discover and parse all mem.\*.md files into MemoryRecords.

Returns:
Dictionary mapping memory ID to MemoryRecord.

- `collect_bodies(self) -> dict[Tuple[str, str]]`: Collect body text for all memory records.

Reads each memory file, strips frontmatter, and returns the body.
Useful for graph operations (backlinks, link expansion).

Returns:
Dictionary mapping memory ID to body text.

- `filter(self) -> list[MemoryRecord]`: Filter memory records by multiple criteria (AND logic).

Args:
memory_type: Filter by memory_type field.
status: Filter by status field.
tag: Filter by tag membership.

Returns:
List of matching MemoryRecords.

- `find(self, memory_id) -> <BinOp>`: Find a specific memory record by ID.

Args:
memory_id: The memory ID (e.g. 'mem.pattern.cli.skinny').

Returns:
MemoryRecord or None if not found.

- `iter(self) -> Iterator[MemoryRecord]`: Iterate over memory records, optionally filtered by status.

Args:
status: If provided, yield only records with this status.

Yields:
MemoryRecord instances.
