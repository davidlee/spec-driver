# supekku.scripts.lib.memory.models

MemoryRecord model for memory artifacts.

## Classes

### MemoryRecord

A memory artifact record parsed from frontmatter.

Required fields: id, name, status, memory_type, path.
All other fields are optional with safe defaults.

#### Methods

- @classmethod `from_frontmatter(cls, path, fm) -> MemoryRecord`: Construct a MemoryRecord from parsed frontmatter.

Args:
  path: Filesystem path to the memory file.
  fm: Parsed frontmatter dictionary.

Returns:
  Populated MemoryRecord.
- `to_dict(self, root) -> dict[Tuple[str, Any]]`: Convert to dictionary for YAML serialization.

Args:
  root: Repository root for relativizing file paths.

Returns:
  Dictionary with non-empty fields only.
