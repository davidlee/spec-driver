"""Common utilities, options, and callbacks for CLI commands.

This module provides reusable CLI option types, shared data types for artifact
resolution, and consistent flag behavior across all CLI commands.

## Standardized Flags

Across all list commands, we use consistent flag patterns:
- `--format`: Output format (table|json|tsv)
- `--truncate`: Enable field truncation in table output (default: off, full content)
- `--filter`: Substring filter (case-insensitive)
- `--regexp`: Regular expression pattern for filtering
- `--case-insensitive`: Make regexp matching case-insensitive
- `--status`: Filter by status (entity-specific values)
- `--root`: Repository root directory
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Any

import typer

# Exit codes
EXIT_SUCCESS = 0
EXIT_FAILURE = 1


# --- Artifact resolution types ---


@dataclass(frozen=True)
class ArtifactRef:
  """Resolved artifact reference returned by resolve_artifact."""

  id: str
  path: Path
  record: Any


class ArtifactNotFoundError(Exception):
  """Raised when an artifact cannot be found by ID."""

  def __init__(self, artifact_type: str, artifact_id: str) -> None:
    self.artifact_type = artifact_type
    self.artifact_id = artifact_id
    super().__init__(f"{artifact_type} not found: {artifact_id}")


class AmbiguousArtifactError(Exception):
  """Raised when multiple artifacts match a single-target lookup."""

  def __init__(
    self, artifact_type: str, artifact_id: str, paths: list[Path]
  ) -> None:
    self.artifact_type = artifact_type
    self.artifact_id = artifact_id
    self.paths = paths
    path_list = "\n  ".join(str(p) for p in paths)
    super().__init__(
      f"Ambiguous {artifact_type} ID {artifact_id}, matches:\n  {path_list}"
    )


def root_option_callback(value: Path | None) -> Path:
  """Callback to process root directory option with auto-detection.

  Args:
      value: The provided root path, or None to auto-detect

  Returns:
      Resolved root path

  """
  if value is None:
    return Path.cwd()
  return value.resolve()


# Common option definitions for reuse
RootOption = Annotated[
  Path | None,
  typer.Option(
    "--root",
    help="Repository root (auto-detected if omitted)",
    callback=root_option_callback,
    exists=True,
    file_okay=False,
    dir_okay=True,
    resolve_path=True,
  ),
]


def version_callback(value: bool) -> None:
  """Print version and exit if --version flag is provided.

  Args:
      value: Whether --version was specified

  """
  if value:
    from importlib.metadata import PackageNotFoundError, version

    try:
      pkg_version = version("spec-driver")
    except PackageNotFoundError:  # pragma: no cover
      pkg_version = "unknown"
    typer.echo(f"spec-driver {pkg_version}")
    raise typer.Exit(EXIT_SUCCESS)


# Version option for main app
VersionOption = Annotated[
  bool | None,
  typer.Option(
    "--version",
    callback=version_callback,
    is_eager=True,
    help="Show version and exit",
  ),
]

# Standardized list command options
FormatOption = Annotated[
  str,
  typer.Option(
    "--format",
    help="Output format: table (rich), json (structured), or tsv (tabs)",
  ),
]

TruncateOption = Annotated[
  bool,
  typer.Option(
    "--truncate",
    help="Truncate long fields to fit terminal width",
  ),
]

RegexpOption = Annotated[
  str | None,
  typer.Option(
    "--regexp",
    "-r",
    help="Regular expression pattern for filtering on title/name/summary",
  ),
]

CaseInsensitiveOption = Annotated[
  bool,
  typer.Option(
    "--case-insensitive",
    "-i",
    help="Make regexp matching case-insensitive",
  ),
]


def matches_regexp(
  pattern: str | None,
  text_fields: list[str],
  case_insensitive: bool = False,
) -> bool:
  """Check if any of the text fields match the given regexp pattern.

  Args:
    pattern: Regular expression pattern (None means no filtering)
    text_fields: List of text fields to search
    case_insensitive: Whether to perform case-insensitive matching

  Returns:
    True if pattern is None (no filter) or if any field matches the pattern

  Raises:
    re.error: If the pattern is invalid

  """
  if pattern is None:
    return True

  flags = re.IGNORECASE if case_insensitive else 0
  compiled_pattern = re.compile(pattern, flags)

  return any(compiled_pattern.search(field) for field in text_fields if field)


# --- Pager and Editor utilities ---


def get_pager() -> str | None:
  """Get pager command from environment or fallback.

  Resolution order: $PAGER -> less -> more

  Returns:
    Pager command string, or None if no pager available.

  """
  import os
  import shutil

  if pager := os.environ.get("PAGER"):
    return pager
  for cmd in ("less", "more"):
    if shutil.which(cmd):
      return cmd
  return None


def get_editor() -> str | None:
  """Get editor command from environment or fallback.

  Resolution order: $EDITOR -> $VISUAL -> vi

  Returns:
    Editor command string, or None if no editor available.

  """
  import os
  import shutil

  for var in ("EDITOR", "VISUAL"):
    if editor := os.environ.get(var):
      return editor
  if shutil.which("vi"):
    return "vi"
  return None


def open_in_pager(path: Path | str) -> None:
  """Open file in pager.

  Args:
    path: Path to file to open

  Raises:
    RuntimeError: If no pager is available

  """
  import subprocess

  pager = get_pager()
  if not pager:
    msg = "No pager found. Set $PAGER or install less."
    raise RuntimeError(msg)
  subprocess.run([pager, str(path)], check=True)


def open_in_editor(path: Path | str) -> None:
  """Open file in editor.

  Args:
    path: Path to file to open

  Raises:
    RuntimeError: If no editor is available

  """
  import subprocess

  editor = get_editor()
  if not editor:
    msg = "No editor found. Set $EDITOR or install vi."
    raise RuntimeError(msg)
  subprocess.run([editor, str(path)], check=True)


# --- ID normalization for shorthand support ---

# Artifact types with unambiguous prefixes (can use numeric shorthand)
ARTIFACT_PREFIXES: dict[str, str] = {
  "adr": "ADR-",
  "delta": "DE-",
  "revision": "RE-",
  "policy": "POL-",
  "standard": "STD-",
}


def normalize_id(artifact_type: str, raw_id: str) -> str:
  """Normalize artifact ID by prepending prefix if raw_id is numeric-only.

  For artifact types with unambiguous prefixes, allows shorthand like '001' or '1'
  to be expanded to 'ADR-001' etc. Numeric IDs are zero-padded to 3 digits.

  Args:
    artifact_type: The artifact type key (e.g., 'adr', 'delta')
    raw_id: The user-provided ID (e.g., '001', 'ADR-001', 'foo')

  Returns:
    Normalized ID with prefix, or original ID if not applicable.

  Examples:
    >>> normalize_id("adr", "1")
    'ADR-001'
    >>> normalize_id("adr", "001")
    'ADR-001'
    >>> normalize_id("adr", "ADR-001")
    'ADR-001'
    >>> normalize_id("spec", "001")
    '001'

  """
  if artifact_type not in ARTIFACT_PREFIXES:
    return raw_id  # No normalization for ambiguous types

  prefix = ARTIFACT_PREFIXES[artifact_type]

  # Already has correct prefix
  if raw_id.upper().startswith(prefix):
    return raw_id.upper()

  # Numeric-only: prepend prefix with zero-padding
  if raw_id.isdigit():
    return f"{prefix}{int(raw_id):03d}"

  # Not numeric, return as-is (might be a slug or other format)
  return raw_id


# --- Artifact resolution ---

# Lazy imports for registries to avoid circular imports and keep CLI startup fast.
# Each _resolve_* function imports its registry at call time.


def _resolve_spec(root: Path, raw_id: str) -> ArtifactRef:
  from supekku.scripts.lib.specs.registry import SpecRegistry  # noqa: PLC0415

  registry = SpecRegistry(root)
  spec = registry.get(raw_id)
  if not spec:
    raise ArtifactNotFoundError("spec", raw_id)
  return ArtifactRef(id=raw_id, path=spec.path, record=spec)


def _resolve_change(root: Path, raw_id: str, kind: str) -> ArtifactRef:
  from supekku.scripts.lib.changes.registry import ChangeRegistry  # noqa: PLC0415

  normalized = normalize_id(kind, raw_id)
  registry = ChangeRegistry(root=root, kind=kind)
  artifacts = registry.collect()
  artifact = artifacts.get(normalized)
  if not artifact:
    raise ArtifactNotFoundError(kind, normalized)
  return ArtifactRef(id=normalized, path=artifact.path, record=artifact)


def _resolve_decision(root: Path, raw_id: str) -> ArtifactRef:
  from supekku.scripts.lib.decisions.registry import DecisionRegistry  # noqa: PLC0415

  normalized = normalize_id("adr", raw_id)
  registry = DecisionRegistry(root=root)
  decision = registry.find(normalized)
  if not decision:
    raise ArtifactNotFoundError("adr", normalized)
  return ArtifactRef(id=normalized, path=Path(decision.path), record=decision)


def _resolve_policy(root: Path, raw_id: str) -> ArtifactRef:
  from supekku.scripts.lib.policies.registry import PolicyRegistry  # noqa: PLC0415

  normalized = normalize_id("policy", raw_id)
  registry = PolicyRegistry(root=root)
  record = registry.find(normalized)
  if not record:
    raise ArtifactNotFoundError("policy", normalized)
  return ArtifactRef(id=normalized, path=Path(record.path), record=record)


def _resolve_standard(root: Path, raw_id: str) -> ArtifactRef:
  from supekku.scripts.lib.standards.registry import StandardRegistry  # noqa: PLC0415

  normalized = normalize_id("standard", raw_id)
  registry = StandardRegistry(root=root)
  record = registry.find(normalized)
  if not record:
    raise ArtifactNotFoundError("standard", normalized)
  return ArtifactRef(id=normalized, path=Path(record.path), record=record)


def _resolve_requirement(root: Path, raw_id: str) -> ArtifactRef:
  from supekku.scripts.lib.core.paths import get_registry_dir  # noqa: PLC0415
  from supekku.scripts.lib.requirements.registry import (  # noqa: PLC0415
    RequirementsRegistry,
  )

  # DEC-041-05: normalize colon-separated to dot-separated
  normalized = raw_id.replace(":", ".")
  registry_path = get_registry_dir(root) / "requirements.yaml"
  registry = RequirementsRegistry(registry_path)
  record = registry.records.get(normalized)
  if not record:
    raise ArtifactNotFoundError("requirement", normalized)
  req_path = Path(record.path) if record.path else root
  return ArtifactRef(id=normalized, path=req_path, record=record)


def _resolve_card(root: Path, raw_id: str) -> ArtifactRef:
  from supekku.scripts.lib.cards import CardRegistry  # noqa: PLC0415

  registry = CardRegistry(root=root)
  try:
    card = registry.resolve_card(raw_id)
  except (FileNotFoundError, ValueError) as exc:
    raise ArtifactNotFoundError("card", raw_id) from exc
  return ArtifactRef(id=raw_id, path=card.path, record=card)


def _resolve_memory(root: Path, raw_id: str) -> ArtifactRef:
  from supekku.scripts.lib.memory.registry import MemoryRegistry  # noqa: PLC0415

  registry = MemoryRegistry(root=root)
  record = registry.find(raw_id)
  if not record:
    raise ArtifactNotFoundError("memory", raw_id)
  return ArtifactRef(id=raw_id, path=Path(record.path), record=record)


# Dispatch table: artifact_type -> resolver(root, raw_id) -> ArtifactRef
_ARTIFACT_RESOLVERS: dict[str, Any] = {
  "spec": _resolve_spec,
  "delta": lambda root, raw_id: _resolve_change(root, raw_id, "delta"),
  "revision": lambda root, raw_id: _resolve_change(root, raw_id, "revision"),
  "audit": lambda root, raw_id: _resolve_change(root, raw_id, "audit"),
  "adr": _resolve_decision,
  "policy": _resolve_policy,
  "standard": _resolve_standard,
  "requirement": _resolve_requirement,
  "card": _resolve_card,
  "memory": _resolve_memory,
}


def resolve_artifact(artifact_type: str, raw_id: str, root: Path) -> ArtifactRef:
  """Resolve an artifact by type and ID, returning an ArtifactRef.

  Uses a dispatch table to delegate to type-specific resolvers. Each
  resolver handles ID normalization, registry lookup, and not-found errors.

  Args:
    artifact_type: Artifact type key (e.g. 'revision', 'spec', 'adr').
    raw_id: User-provided ID (may be shorthand like '1' or full like 'RE-001').
    root: Repository root path.

  Returns:
    ArtifactRef with resolved id, path, and record.

  Raises:
    ArtifactNotFoundError: If the artifact cannot be found.
    ValueError: If artifact_type is not in the dispatch table.

  """
  resolver = _ARTIFACT_RESOLVERS.get(artifact_type)
  if not resolver:
    msg = f"Unknown artifact type: {artifact_type}"
    raise ValueError(msg)
  return resolver(root, raw_id)


# --- Artifact output ---


def emit_artifact(
  ref: ArtifactRef,
  *,
  json_output: bool = False,
  path_only: bool = False,
  raw_output: bool = False,
  format_fn: Any,
  json_fn: Any,
) -> None:
  """Dispatch artifact output by mode: path, raw, json, or formatted.

  Handles mutual-exclusivity check for --json/--path/--raw and calls the
  appropriate output function. Always raises typer.Exit on completion.

  Args:
    ref: Resolved artifact reference.
    json_output: If True, output JSON via json_fn.
    path_only: If True, echo the artifact path.
    raw_output: If True, echo raw file content.
    format_fn: Callable(record) -> str for default formatted output.
    json_fn: Callable(record) -> str for JSON output. Required.

  Raises:
    typer.Exit: Always — EXIT_SUCCESS on success, EXIT_FAILURE on error.

  """
  if sum([json_output, path_only, raw_output]) > 1:
    typer.echo(
      "Error: --json, --path, and --raw are mutually exclusive", err=True
    )
    raise typer.Exit(EXIT_FAILURE)

  if path_only:
    typer.echo(ref.path)
  elif raw_output:
    typer.echo(ref.path.read_text())
  elif json_output:
    typer.echo(json_fn(ref.record))
  else:
    typer.echo(format_fn(ref.record))
  raise typer.Exit(EXIT_SUCCESS)
