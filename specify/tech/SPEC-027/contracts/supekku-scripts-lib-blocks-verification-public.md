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
- `render_verification_coverage_block(subject_id) -> str`: Render a verification coverage YAML block with given values.

This is the canonical source for the block structure. Templates and
creation code should use this instead of hardcoding the structure.

Args:
  subject_id: The subject ID (SPEC, PROD, IP, or AUD).
  entries: List of verification entries. Each entry is a dict with:
    - artefact: str (e.g., "VT-001")
    - kind: str (VT, VA, or VH)
    - requirement: str (e.g., "SPEC-100.FR-001")
    - status: str (planned, in-progress, verified, failed, blocked)
    - phase: str | None (optional, e.g., "IP-001.PHASE-01")
    - notes: str | None (optional)

Returns:
  Formatted YAML code block as string.

Example:
  >>> block = render_verification_coverage_block(
  ...   "SPEC-100",
  ...   entries=[{
  ...     "artefact": "VT-001",
  ...     "kind": "VT",
  ...     "requirement": "SPEC-100.FR-001",
  ...     "status": "planned",
  ...   }]
  ... )

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
