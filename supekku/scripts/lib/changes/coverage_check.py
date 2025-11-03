"""Coverage completeness checking for delta completion enforcement."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from supekku.scripts.lib.blocks.verification import load_coverage_blocks

if TYPE_CHECKING:
  from supekku.scripts.lib.workspace import Workspace


@dataclass
class CoverageMissing:
  """Details about missing or incomplete coverage for a requirement."""

  requirement_id: str
  spec_id: str
  spec_path: Path | None
  current_status: str | None  # None if missing entirely
  reason: str  # 'spec_not_found' | 'missing_block' | 'missing_entry' | 'not_verified'


def is_coverage_enforcement_enabled() -> bool:
  """Check if coverage enforcement is enabled via environment variable.

  Returns:
    True if enforcement is enabled (default), False otherwise.
  """
  value = os.getenv("SPEC_DRIVER_ENFORCE_COVERAGE", "true").lower()
  return value in ("true", "1", "yes", "on")


def parse_requirement_spec_id(requirement_id: str) -> str | None:
  """Extract parent spec ID from requirement ID.

  Args:
    requirement_id: Requirement ID (e.g., "PROD-008.FR-001")

  Returns:
    Spec ID (e.g., "PROD-008") or None if invalid format.
  """
  if "." not in requirement_id:
    return None
  return requirement_id.split(".", 1)[0]


def check_requirement_coverage(
  requirement_id: str,
  spec_path: Path,
) -> tuple[bool, str | None, str]:
  """Check if requirement has verified coverage in spec.

  Args:
    requirement_id: Requirement ID to check.
    spec_path: Path to parent spec file.

  Returns:
    Tuple of (is_verified, current_status, reason).
    - is_verified: True if requirement has verified coverage
    - current_status: Status string if entry exists, None otherwise
    - reason: Description of why verification failed
  """
  if not spec_path.exists():
    return False, None, "spec_not_found"

  try:
    blocks = load_coverage_blocks(spec_path)
  except (ValueError, OSError):
    # Coverage parsing failed or no blocks present
    return False, None, "missing_block"

  if not blocks:
    return False, None, "missing_block"

  # Search all coverage blocks for this requirement
  for block in blocks:
    entries = block.data.get("entries", [])
    for entry in entries:
      if entry.get("requirement") == requirement_id:
        status = entry.get("status")
        if status == "verified":
          return True, status, ""
        return False, status, "not_verified"

  # Requirement not found in any coverage block
  return False, None, "missing_entry"


def check_coverage_completeness(
  delta_id: str,
  workspace: Workspace,
) -> tuple[bool, list[CoverageMissing]]:
  """Check if all delta requirements have verified coverage in specs.

  Args:
    delta_id: Delta identifier (e.g., "DE-007").
    workspace: Workspace instance for registry access.

  Returns:
    Tuple of (is_complete, missing_coverage_list).
    - is_complete: True if all requirements have verified coverage
    - missing_coverage_list: Details about incomplete coverage
  """
  # Load delta
  delta_registry = workspace.delta_registry
  delta_artifacts = delta_registry.collect()

  if delta_id not in delta_artifacts:
    # Delta not found - let calling code handle this error
    return False, []

  delta = delta_artifacts[delta_id]

  # Get requirements to check
  requirement_ids = delta.applies_to.get("requirements", [])
  if not requirement_ids:
    # No requirements to check - completion is valid
    return True, []

  # Check each requirement's coverage
  missing: list[CoverageMissing] = []
  spec_registry = workspace.specs

  for req_id in requirement_ids:
    # Parse spec ID from requirement ID
    spec_id = parse_requirement_spec_id(req_id)
    if not spec_id:
      # Invalid requirement ID format
      missing.append(
        CoverageMissing(
          requirement_id=req_id,
          spec_id="UNKNOWN",
          spec_path=None,
          current_status=None,
          reason="invalid_requirement_id",
        ),
      )
      continue

    # Get spec from registry
    spec = spec_registry.get(spec_id)
    if not spec:
      # Spec not found in registry
      missing.append(
        CoverageMissing(
          requirement_id=req_id,
          spec_id=spec_id,
          spec_path=None,
          current_status=None,
          reason="spec_not_found",
        ),
      )
      continue

    # Check coverage in spec
    is_verified, current_status, reason = check_requirement_coverage(
      req_id,
      spec.path,
    )

    if not is_verified:
      missing.append(
        CoverageMissing(
          requirement_id=req_id,
          spec_id=spec_id,
          spec_path=spec.path,
          current_status=current_status,
          reason=reason,
        ),
      )

  return len(missing) == 0, missing


def format_coverage_error(
  delta_id: str,
  missing: list[CoverageMissing],
  root: Path,
) -> str:
  """Format error message for missing coverage.

  Args:
    delta_id: Delta identifier.
    missing: List of missing coverage details.
    root: Repository root for relative path calculation.

  Returns:
    Formatted error message.
  """
  lines = [
    f"ERROR: Cannot complete {delta_id} - coverage verification required",
    "",
    "The following requirements need verified coverage in their specs:",
    "",
  ]

  for item in missing:
    lines.append(f"  {item.requirement_id}")

    if item.spec_path:
      rel_path = item.spec_path.relative_to(root)
      lines.append(f"    Spec: {rel_path}")
    else:
      lines.append(f"    Spec: {item.spec_id} (not found)")

    # Show current status and action
    if item.reason == "spec_not_found":
      lines.append("    Issue: Parent spec file not found")
      lines.append("    Action: Verify spec exists in workspace")
    elif item.reason == "missing_block":
      lines.append("    Issue: Spec has no coverage block")
      lines.append("    Action: Add coverage block to spec (see example below)")
    elif item.reason == "missing_entry":
      lines.append("    Issue: Requirement not found in coverage block")
      lines.append("    Action: Add coverage entry to spec (see example below)")
    elif item.reason == "not_verified":
      lines.append(f"    Current status: {item.current_status}")
      lines.append("    Action: Update coverage status to 'verified'")
    elif item.reason == "invalid_requirement_id":
      lines.append("    Issue: Invalid requirement ID format")
      lines.append("    Action: Fix requirement ID in delta frontmatter")

    lines.append("")

  # Add example coverage block
  if missing:
    example_req = missing[0].requirement_id
    lines.extend(
      [
        "Example coverage entry:",
        "```yaml supekku:verification.coverage@v1",
        "schema: supekku.verification.coverage",
        "version: 1",
        f"subject: {missing[0].spec_id}",
        "entries:",
        "  - artefact: VT-902",
        "    kind: VT",
        f"    requirement: {example_req}",
        "    status: verified  # ← Update this",
        "    notes: Description of verification",
        "```",
        "",
      ],
    )

  lines.extend(
    [
      "Documentation: .spec-driver/RUN.md",
      "",
      "To bypass this check (emergency only):",
      f"  uv run spec-driver complete delta {delta_id} --force",
      "",
    ],
  )

  return "\n".join(lines)


def display_coverage_error(
  delta_id: str,
  missing: list[CoverageMissing],
  root: Path,
) -> None:
  """Display coverage error message to stderr.

  Args:
    delta_id: Delta identifier.
    missing: List of missing coverage details.
    root: Repository root for relative path calculation.
  """
  error_msg = format_coverage_error(delta_id, missing, root)
  print(error_msg, file=sys.stderr)


__all__ = [
  "CoverageMissing",
  "check_coverage_completeness",
  "display_coverage_error",
  "is_coverage_enforcement_enabled",
]
