# supekku.scripts.lib.revision_blocks

Utilities for extracting and validating structured revision blocks.

## Constants

- `REVISION_BLOCK_MARKER`
- `REVISION_BLOCK_SCHEMA_ID`
- `REVISION_BLOCK_VERSION`

## Functions

- `extract_revision_blocks(markdown) -> list[RevisionChangeBlock]`
- `load_revision_blocks(path) -> list[RevisionChangeBlock]`

## Classes

### RevisionBlockValidator

Runtime validator mirroring REVISION_BLOCK_JSON_SCHEMA.

#### Methods

- `validate(self, data) -> list[ValidationMessage]`

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
