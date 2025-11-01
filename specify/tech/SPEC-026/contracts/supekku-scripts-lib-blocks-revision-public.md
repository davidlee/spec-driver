# supekku.scripts.lib.blocks.revision

Utilities for extracting and validating structured revision blocks.

## Constants

- `REVISION_BLOCK_MARKER`
- `REVISION_BLOCK_SCHEMA_ID`
- `REVISION_BLOCK_VERSION`

## Functions

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
- `render_revision_change_block(revision_id) -> str`: Render a revision change YAML block with given values.

This is the canonical source for the block structure. Templates and
creation code should use this instead of hardcoding the structure.

Note: This generates a minimal but valid revision block. For complex revisions,
consider building the dict structure and using yaml.safe_dump directly.

Args:
  revision_id: The revision ID (e.g., "RE-001").
  specs: List of spec change dicts with:
    - spec_id: str
    - action: str ("created", "updated", "retired")
    - summary: str (optional)
    - requirement_flow: dict (optional)
    - section_changes: list (optional)
  requirements: List of requirement change dicts with:
    - requirement_id: str
    - kind: str ("functional", "non-functional")
    - action: str ("introduce", "modify", "move", "retire")
    - summary: str (optional)
    - destination: dict (optional)
    - origin: list (optional)
    - lifecycle: dict (optional)
  prepared_by: Optional preparer identifier.
  generated_at: Optional generation timestamp.

Returns:
  Formatted YAML code block as string.

## Classes

### RevisionBlockValidator

Runtime validator mirroring REVISION_BLOCK_JSON_SCHEMA.

#### Methods

- `validate(self, data) -> list[ValidationMessage]`: Validate revision block data against schema.

Args:
  data: Parsed revision block data.

Returns:
  List of validation messages (empty if valid).

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
