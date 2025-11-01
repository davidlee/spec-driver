# supekku.scripts.lib.blocks.revision

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
- `extract_revision_blocks(markdown) -> list[RevisionChangeBlock]`: Extract revision change blocks from markdown content.

Args:
  markdown: Markdown content to parse.
  source: Optional source file path for error reporting.

Returns:
  List of parsed RevisionChangeBlock objects.
- `load_revision_blocks(path) -> list[RevisionChangeBlock]`: Load and extract revision change blocks from a file.

Args:
  path: Path to markdown file.

Returns:
  List of parsed RevisionChangeBlock objects.

## Classes

### RevisionBlockValidator

Runtime validator mirroring REVISION_BLOCK_JSON_SCHEMA.

#### Methods

- `validate(self, data) -> list[ValidationMessage]`: Validate revision block data against schema.

Args:
  data: Parsed revision block data.

Returns:
  List of validation messages (empty if valid).
- `_check_root(self, data, messages) -> None`
- `_require_key(self, data, key, messages) -> None`
- `_validate_metadata(self, metadata, messages) -> None`
- `_validate_requirement(self, requirement, messages) -> None`
- `_validate_spec(self, spec, messages) -> None`

### RevisionChangeBlock

Represents a parsed revision change block from markdown.

#### Methods

- `formatted_yaml(self, data) -> str`: Format data as canonical YAML.

Args:
  data: Optional data to format. If None, parses from yaml_content.

Returns:
  Formatted YAML string with trailing newline.
- `parse(self) -> dict[Tuple[str, Any]]`: Parse YAML content from revision block.

Returns:
  Parsed YAML data as dictionary.

Raises:
  ValueError: If YAML is invalid or doesn't parse to a mapping.
- `replace_content(self, original, new_yaml) -> str`: Replace block content in original string.

Args:
  original: Original file content.
  new_yaml: New YAML content to insert.

Returns:
  Updated content with replacement applied.

### ValidationMessage

A validation message with path context for error reporting.

#### Methods

- `render_path(self) -> str`: Render validation path as human-readable string.

Returns:
  Formatted path string (e.g., "specs.primary[0]").
