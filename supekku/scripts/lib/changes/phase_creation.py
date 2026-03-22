"""Phase artifact creation and sequencing logic."""

from __future__ import annotations

import re
import warnings
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import yaml
from jinja2 import Template

from supekku.scripts.lib.blocks.plan import (
  PLAN_MARKER,
  extract_plan_overview,
)
from supekku.scripts.lib.changes._creation_utils import (
  _ensure_directory,
  _get_template_path,
)
from supekku.scripts.lib.changes.lifecycle import STATUS_DRAFT
from supekku.scripts.lib.core.events import record_artifact
from supekku.scripts.lib.core.paths import get_deltas_dir
from supekku.scripts.lib.core.spec_utils import dump_markdown_file
from supekku.scripts.lib.specs.creation import (
  extract_template_body,
  find_repository_root,
)


class PhaseCreationError(Exception):
  """Raised when phase creation fails."""


@dataclass(frozen=True)
class PhaseCreationResult:
  """Result information from creating a phase."""

  phase_id: str
  phase_path: Path
  plan_id: str
  delta_id: str


def _find_plan_file(plan_id: str, repo_root: Path) -> Path | None:
  """Find plan file by ID in delta directories.

  Args:
    plan_id: Plan identifier (e.g., IP-002).
    repo_root: Repository root path.

  Returns:
    Path to plan file, or None if not found.
  """
  deltas_dir = get_deltas_dir(repo_root)
  if not deltas_dir.exists():
    return None

  # Search all delta directories for plan file
  for delta_dir in deltas_dir.iterdir():
    if not delta_dir.is_dir():
      continue
    plan_path = delta_dir / f"{plan_id}.md"
    if plan_path.exists():
      return plan_path

  return None


def _parse_phase_number(filename: str) -> int | None:
  """Extract phase number from filename like 'phase-01.md'.

  Args:
    filename: Phase filename.

  Returns:
    Phase number as int, or None if not a valid phase filename.
  """
  match = re.match(r"phase-(\d{2})\.md$", filename)
  if match:
    return int(match.group(1))
  return None


PHASE_ID_FORMAT_HYPHEN = "hyphen"
PHASE_ID_FORMAT_DOTTED = "dotted"
_PHASE_ID_PATTERN = re.compile(
  r"^(?P<plan>IP-\d{3,})(?:(?:-P)|(?:\.PHASE-))(?P<num>\d{2})$"
)


def _parse_phase_identity(phase_id: str) -> tuple[str, int, str] | None:
  """Parse a phase ID into plan, sequence number, and spelling convention."""

  match = _PHASE_ID_PATTERN.match(str(phase_id).strip())
  if not match:
    return None
  raw = match.group(0)
  return (
    match.group("plan"),
    int(match.group("num")),
    PHASE_ID_FORMAT_DOTTED if ".PHASE-" in raw else PHASE_ID_FORMAT_HYPHEN,
  )


def _phase_sequence_from_id(phase_id: str, *, plan_id: str) -> int | None:
  """Return phase sequence number when the ID belongs to the given plan."""

  parsed = _parse_phase_identity(phase_id)
  if parsed is None:
    return None
  parsed_plan_id, phase_num, _ = parsed
  if parsed_plan_id != plan_id:
    return None
  return phase_num


def _phase_ids_equivalent(left: str, right: str) -> bool:
  """Return True when two phase IDs refer to the same logical phase."""

  left_parsed = _parse_phase_identity(left)
  right_parsed = _parse_phase_identity(right)
  if left_parsed is None or right_parsed is None:
    return left == right
  return left_parsed[:2] == right_parsed[:2]


def _render_phase_id(plan_id: str, phase_num: int, *, spelling: str) -> str:
  """Render a phase ID using the requested spelling convention."""

  if spelling == PHASE_ID_FORMAT_DOTTED:
    return f"{plan_id}.PHASE-{phase_num:02d}"
  return f"{plan_id}-P{phase_num:02d}"


def _plan_phase_entries(plan_content: str) -> list[dict[str, object]]:
  """Return normalized phase entries from a plan overview block."""

  block = extract_plan_overview(plan_content)
  if block is None:
    return []
  phases = block.data.get("phases", [])
  if not isinstance(phases, list):
    return []
  return [phase for phase in phases if isinstance(phase, dict)]


def _select_phase_sequence(
  *,
  plan_id: str,
  plan_content: str,
  phases_dir: Path,
) -> tuple[int, str]:
  """Choose the next phase sequence and spelling for create_phase.

  Prefer the first plan-authored phase entry that does not yet have a phase
  file, so `create phase` materializes the intended phase sheet instead of
  inventing a parallel identifier. When every planned phase already has a file,
  allocate the next sequence number after the highest known phase.
  """

  planned_numbers: list[int] = []
  planned_spellings: dict[int, str] = {}
  for phase in _plan_phase_entries(plan_content):
    phase_id = phase.get("id")
    if not isinstance(phase_id, str):
      continue
    parsed = _parse_phase_identity(phase_id)
    if parsed is None or parsed[0] != plan_id:
      continue
    _, phase_num, spelling = parsed
    planned_numbers.append(phase_num)
    planned_spellings.setdefault(phase_num, spelling)

  existing_file_numbers: set[int] = set()
  if phases_dir.exists():
    for entry in phases_dir.iterdir():
      if entry.is_file():
        file_number = _parse_phase_number(entry.name)
        if file_number is not None:
          existing_file_numbers.add(file_number)

  for planned_number in sorted(set(planned_numbers)):
    if planned_number not in existing_file_numbers:
      return planned_number, planned_spellings.get(
        planned_number,
        PHASE_ID_FORMAT_HYPHEN,
      )

  known_numbers = set(planned_numbers) | existing_file_numbers
  next_number = max(known_numbers, default=0) + 1
  fallback_spelling = (
    planned_spellings[min(planned_numbers)]
    if planned_numbers
    else PHASE_ID_FORMAT_HYPHEN
  )
  return next_number, fallback_spelling


def _find_next_phase_number(phases_dir: Path) -> int:
  """Find next phase number by scanning existing phase files.

  Args:
    phases_dir: Directory containing phase files.

  Returns:
    Next phase number (1 if no phases exist).
  """
  if not phases_dir.exists():
    return 1

  max_num = 0
  for entry in phases_dir.iterdir():
    if entry.is_file():
      num = _parse_phase_number(entry.name)
      if num is not None:
        max_num = max(max_num, num)

  return max_num + 1


def _update_plan_overview_phases(
  plan_path: Path,
  phase_id: str,
) -> None:
  """Update plan.overview block to include new phase entry.

  Appends a minimal phase entry to the phases array in the plan.overview block.
  Uses id-only format to minimize user conflict.

  Args:
    plan_path: Path to the plan markdown file.
    phase_id: Phase ID to add (e.g., "IP-002.PHASE-04").

  Raises:
    ValueError: If plan.overview block missing or malformed.
    OSError: If file I/O fails.
  """
  # Read plan file
  content = plan_path.read_text(encoding="utf-8")

  # Extract plan.overview block
  block = extract_plan_overview(content, plan_path)
  if block is None:
    msg = f"No plan.overview block found in {plan_path}"
    raise ValueError(msg)

  # Parse data
  data = block.data

  # Append new phase entry (minimal - just ID)
  phases = data.get("phases", [])
  if not isinstance(phases, list):
    msg = f"plan.overview phases is not a list in {plan_path}"
    raise ValueError(msg)

  # Add phase with minimal metadata (id only) unless an equivalent phase exists.
  phases.append({"id": phase_id})
  for existing_phase in phases[:-1]:
    if not isinstance(existing_phase, dict):
      continue
    existing_phase_id = existing_phase.get("id")
    if isinstance(existing_phase_id, str) and _phase_ids_equivalent(
      existing_phase_id, phase_id
    ):
      return
  data["phases"] = phases

  # Re-serialize YAML block
  yaml_content = yaml.safe_dump(
    data,
    sort_keys=False,
    indent=2,
    default_flow_style=False,
  )

  # Ensure trailing newline
  if not yaml_content.endswith("\n"):
    yaml_content += "\n"

  # Build new block with markers
  new_block = f"```yaml {PLAN_MARKER}\n{yaml_content}```"

  # Replace old block with new block using regex
  pattern = re.compile(
    r"```(?:yaml|yml)\s+" + re.escape(PLAN_MARKER) + r"\n.*?```",
    re.DOTALL,
  )

  # Use lambda to avoid re.sub interpreting backslash sequences in replacement
  new_content = pattern.sub(lambda _: new_block, content, count=1)

  if new_content == content:
    msg = f"Failed to replace plan.overview block in {plan_path}"
    raise ValueError(msg)

  # Write back to file
  plan_path.write_text(new_content, encoding="utf-8")


def _extract_phase_metadata_from_plan(
  plan_content: str,
  phase_id: str,
) -> dict[str, str | list[str]]:
  """Extract phase metadata from plan.overview block.

  Args:
    plan_content: Full plan file content.
    phase_id: Phase ID to look for (e.g., "IP-012.PHASE-01").

  Returns:
    Dictionary with optional keys: objective, entrance_criteria, exit_criteria.
    Returns empty dict if plan.overview not found or phase not in phases array.
  """
  # Try to extract plan.overview block
  block = extract_plan_overview(plan_content)
  if not block:
    return {}

  # Look for the phase in the phases array
  phases = block.data.get("phases", [])
  if not isinstance(phases, list):
    return {}

  for phase in phases:
    if not isinstance(phase, dict):
      continue
    candidate_phase_id = phase.get("id")
    if not isinstance(candidate_phase_id, str):
      continue
    if not _phase_ids_equivalent(candidate_phase_id, phase_id):
      continue

    # Found the phase - extract optional metadata
    metadata: dict[str, str | list[str]] = {}
    if "objective" in phase:
      metadata["objective"] = phase["objective"]
    if "entrance_criteria" in phase and isinstance(phase["entrance_criteria"], list):
      metadata["entrance_criteria"] = phase["entrance_criteria"]
    if "exit_criteria" in phase and isinstance(phase["exit_criteria"], list):
      metadata["exit_criteria"] = phase["exit_criteria"]

    return metadata

  # Phase ID not found in phases array
  return {}


def create_phase(
  name: str,
  plan_id: str,
  *,
  repo_root: Path | None = None,
) -> PhaseCreationResult:
  """Create a new phase for an implementation plan.

  Args:
    name: Phase name (e.g., "Phase 01 - Foundation").
    plan_id: Implementation plan ID (e.g., "IP-002").
    repo_root: Optional repository root. Auto-detected if not provided.

  Returns:
    PhaseCreationResult with phase details.

  Raises:
    PhaseCreationError: If plan not found, invalid input, or creation fails.
  """
  if not name or not name.strip():
    msg = "Phase name cannot be empty"
    raise PhaseCreationError(msg)

  if not plan_id or not plan_id.strip():
    msg = "Plan ID cannot be empty"
    raise PhaseCreationError(msg)

  plan_id = plan_id.strip().upper()
  name = name.strip()

  # Find repository root
  repo = find_repository_root(repo_root or Path.cwd())

  # Find plan file
  plan_path = _find_plan_file(plan_id, repo)
  if plan_path is None:
    msg = f"Implementation plan not found: {plan_id}"
    raise PhaseCreationError(msg)

  # Read plan frontmatter to get delta ID
  with plan_path.open(encoding="utf-8") as f:
    content = f.read()

  # Extract frontmatter between --- markers
  if not content.startswith("---\n"):
    msg = f"Plan file {plan_path} has invalid frontmatter"
    raise PhaseCreationError(msg)

  parts = content.split("---\n", 2)
  if len(parts) < 3:  # noqa: PLR2004
    msg = f"Plan file {plan_path} has invalid frontmatter"
    raise PhaseCreationError(msg)

  frontmatter = yaml.safe_load(parts[1])
  delta_id = frontmatter.get("id", "").replace("IP-", "DE-")

  if not delta_id or not delta_id.startswith("DE-"):
    # Try to find delta from plan.overview block
    overview_match = re.search(
      r"```yaml supekku:plan\.overview@v1\n(.*?)\n```", content, re.DOTALL
    )
    if overview_match:
      overview_yaml = yaml.safe_load(overview_match.group(1))
      delta_id = overview_yaml.get("delta", "")

  if not delta_id or not delta_id.startswith("DE-"):
    msg = (
      f"Plan {plan_id} does not specify delta ID in frontmatter or plan.overview block"
    )
    raise PhaseCreationError(msg)

  # Find delta directory
  delta_dir = plan_path.parent
  phases_dir = delta_dir / "phases"
  _ensure_directory(phases_dir)

  # Determine next phase number and spelling convention from plan + filesystem.
  phase_num, phase_id_spelling = _select_phase_sequence(
    plan_id=plan_id,
    plan_content=content,
    phases_dir=phases_dir,
  )

  # Generate phase ID
  phase_id = _render_phase_id(plan_id, phase_num, spelling=phase_id_spelling)
  record_artifact(phase_id)

  # Get current date
  today = date.today().isoformat()

  # Get slug from delta directory name
  slug = delta_dir.name.split("-", 1)[1] if "-" in delta_dir.name else "phase"

  # Extract phase metadata from plan.overview if available
  phase_metadata = _extract_phase_metadata_from_plan(content, phase_id)

  # Load and render phase template (frontmatter carries structured data; no blocks)
  phase_template_path = _get_template_path("phase.md", repo)
  phase_template_body = extract_template_body(phase_template_path)
  phase_template = Template(phase_template_body)
  phase_body = phase_template.render(
    phase_id=phase_id,
    plan_id=plan_id,
    delta_id=delta_id,
  )

  # Create phase file
  phase_path = phases_dir / f"phase-{phase_num:02d}.md"
  phase_frontmatter = {
    "id": phase_id,
    "slug": f"{slug}-phase-{phase_num:02d}",
    "name": f"{plan_id} Phase {phase_num:02d}",
    "created": today,
    "updated": today,
    "status": STATUS_DRAFT,
    "kind": "phase",
    # Canonical phase fields (DR-106 DEC-005)
    "plan": plan_id,
    "delta": delta_id,
  }

  # Populate optional canonical fields from plan entry metadata
  if phase_metadata.get("objective"):
    phase_frontmatter["objective"] = phase_metadata["objective"]
  if phase_metadata.get("entrance_criteria"):
    phase_frontmatter["entrance_criteria"] = phase_metadata["entrance_criteria"]
  if phase_metadata.get("exit_criteria"):
    phase_frontmatter["exit_criteria"] = phase_metadata["exit_criteria"]

  dump_markdown_file(phase_path, phase_frontmatter, phase_body)

  # Update plan.overview block with new phase
  try:
    _update_plan_overview_phases(plan_path, phase_id)
  except (ValueError, OSError) as exc:
    # Phase file created successfully but metadata update failed
    # Log warning but don't fail phase creation
    warnings.warn(
      f"Phase {phase_id} created but plan metadata update failed: {exc}",
      stacklevel=2,
    )

  return PhaseCreationResult(
    phase_id=phase_id,
    phase_path=phase_path,
    plan_id=plan_id,
    delta_id=delta_id,
  )
