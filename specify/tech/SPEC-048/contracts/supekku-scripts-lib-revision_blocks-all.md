# supekku.scripts.lib.revision_blocks

Utilities for extracting and validating structured revision blocks.

## Constants

- `REVISION_BLOCK_MARKER`
- `REVISION_BLOCK_SCHEMA_ID`
- `REVISION_BLOCK_VERSION`
- `_AUDIT_ID`
- `_BACKLOG_ID`
- `_DELTA_ID`
- `_REQUIREMENT_ID`
- `_REVISION_ID`
- `_SPEC_ID`
- `__all__`

## Functions

- `_disallow_extra_keys(mapping, allowed_keys, path, messages) -> None`
- `_is_audit_id(value) -> bool`
- `_is_backlog_id(value) -> bool`
- `_is_delta_id(value) -> bool`
- `_is_requirement_id(value) -> bool`
- `_is_revision_id(value) -> bool`
- `_is_spec_id(value) -> bool`
- `extract_revision_blocks(markdown) -> list[RevisionChangeBlock]`
- `load_revision_blocks(path) -> list[RevisionChangeBlock]`

## Classes

### RevisionBlockValidator

Runtime validator mirroring REVISION_BLOCK_JSON_SCHEMA.

#### Methods

- `validate(self, data) -> list[ValidationMessage]`
- `_check_root(self, data, messages) -> None`
- `_require_key(self, data, key, messages) -> None`
- `_validate_metadata(self, metadata, messages) -> None`
- `_validate_requirement(self, requirement, messages) -> None`
- `_validate_spec(self, spec, messages) -> None`

### RevisionChangeBlock

Represents a parsed revision change block from markdown.

#### Methods

- `formatted_yaml(self, data) -> str`
- `parse(self) -> dict[Tuple[str, Any]]`
- `replace_content(self, original, new_yaml) -> str`

### ValidationMessage

A validation message with path context for error reporting.

#### Methods

- `render_path(self) -> str`
