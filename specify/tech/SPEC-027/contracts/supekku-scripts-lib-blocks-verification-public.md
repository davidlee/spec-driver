# supekku.scripts.lib.blocks.verification

Utilities for parsing verification coverage YAML blocks.

## Constants

- `COVERAGE_MARKER`
- `COVERAGE_SCHEMA`
- `COVERAGE_VERSION`
- `VALID_KINDS` - Valid verification artifact kinds
- `VALID_STATUSES` - Valid verification statuses

## Functions

- `extract_coverage_blocks(text) -> list[VerificationCoverageBlock]`: Extract and parse all coverage blocks from markdown content.

Args:
  text: Markdown content containing coverage blocks.

Returns:
  List of parsed VerificationCoverageBlock instances.

Raises:
  ValueError: If YAML is invalid or doesn't parse to a mapping.
- `load_coverage_blocks(path) -> list[VerificationCoverageBlock]`: Load and extract coverage blocks from file.

Args:
  path: Path to markdown file.

Returns:
  List of parsed VerificationCoverageBlock instances.

## Classes

### VerificationCoverageBlock

Parsed YAML block containing verification coverage entries.

### VerificationCoverageValidator

Validator for verification coverage blocks.

#### Methods

- `validate(self, block) -> list[str]`: Validate coverage block against schema.

Args:
  block: Parsed coverage block to validate.
  subject_id: Optional expected subject ID to match against.

Returns:
  List of error messages (empty if valid).
