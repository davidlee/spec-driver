# supekku.scripts.lib.memory.ids

Memory ID validation, normalization, and utilities.

Canonical form: mem.<type>.<domain>.<subject>[.<purpose>]

- Charset per segment: [a-z0-9]+(-[a-z0-9]+)\*
- Separator: .
- 2–7 total segments (mem + 1–6 user segments)
- Lowercase enforced on write

Shorthand: omit mem. prefix -> prepend automatically.

## Functions

- `extract_type_from_id(memory_id) -> <BinOp>`: Extract the type segment (second segment) from a canonical memory ID.

Args:
memory_id: A memory ID string.

Returns:
The type segment, or None if not a valid semantic memory ID.

- `filename_from_id(memory_id) -> str`: Derive filename from canonical memory ID.

Args:
memory_id: Canonical memory ID (e.g., 'mem.pattern.cli.skinny').

Returns:
Filename string (e.g., 'mem.pattern.cli.skinny.md').

- `normalize_memory_id(raw) -> str`: Normalize shorthand to canonical form.

Prepends 'mem.' if missing, lowercases, then validates.

Args:
raw: Raw ID or shorthand (e.g., 'pattern.cli.skinny').

Returns:
Canonical memory ID.

Raises:
ValueError: If the resulting ID is malformed.

- `validate_memory_id(raw) -> str`: Validate and return canonical memory ID.

Args:
raw: Raw ID string (must already have mem. prefix).

Returns:
Canonical (lowercased) memory ID.

Raises:
ValueError: If the ID is malformed.
