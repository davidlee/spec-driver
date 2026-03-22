# supekku.scripts.lib.memory.models

MemoryRecord model for memory artifacts.

## Classes

### MemoryRecord

A memory artifact record parsed from frontmatter.

Required fields: id, name, status, memory_type, path.
All other fields are optional with safe defaults.

**Inherits from:** BaseModel

#### Methods

- `to_dict(self, root) -> dict[Tuple[str, Any]]`: Convert to dictionary for YAML serialization.

Args:
  root: Repository root for relativizing file paths.

Returns:
  Dictionary with non-empty fields only.
- @classmethod @field_validator(created, updated, verified, review_by, mode=before) `_coerce_date(cls, v) -> <BinOp>`: Coerce date-like values permissively. Returns None on bad input.
