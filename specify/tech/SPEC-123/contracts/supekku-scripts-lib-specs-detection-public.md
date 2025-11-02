# supekku.scripts.lib.specs.detection

Stub spec detection logic.

Detects whether a spec file is a stub (auto-generated) vs manually modified.

## Functions

- `is_stub_spec(spec_path) -> bool`: Detect if spec is a stub based on status and line count.

Uses two-stage detection:
1. Primary: Check if status == "stub" in frontmatter
2. Fallback: Check if line count ≤ 30 (handles human error/typos)

Args:
  spec_path: Path to spec file

Returns:
  True if spec is a stub, False if modified

Raises:
  FileNotFoundError: If spec_path does not exist
