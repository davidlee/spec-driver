"""Artifact resolution, output, and multi-match finding for CLI commands."""

from __future__ import annotations

import fnmatch
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import typer

# Re-export ContentType here since emit_artifact uses it
from supekku.cli.common import EXIT_FAILURE, EXIT_SUCCESS, ContentType
from supekku.cli.ids import (
  PREFIX_TO_TYPE,
  _normalize_plan_id,
  _parse_prefix,
  normalize_id,
)
from supekku.scripts.lib.core.paths import get_deltas_dir

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

  def __init__(self, artifact_type: str, artifact_id: str, paths: list[Path]) -> None:
    self.artifact_type = artifact_type
    self.artifact_id = artifact_id
    self.paths = paths
    path_list = "\n  ".join(str(p) for p in paths)
    super().__init__(
      f"Ambiguous {artifact_type} ID {artifact_id}, matches:\n  {path_list}"
    )


# --- Artifact resolution ---

# Lazy imports for registries to avoid circular imports and keep CLI startup fast.
# Each _resolve_* function imports its registry at call time.


def _resolve_spec(root: Path, raw_id: str) -> ArtifactRef:
  from supekku.scripts.lib.specs.registry import SpecRegistry  # noqa: PLC0415

  registry = SpecRegistry(root)
  spec = registry.find(raw_id)
  if not spec:
    raise ArtifactNotFoundError("spec", raw_id)
  return ArtifactRef(id=raw_id, path=spec.path, record=spec)


def _resolve_change(root: Path, raw_id: str, kind: str) -> ArtifactRef:
  from supekku.scripts.lib.changes.registry import ChangeRegistry  # noqa: PLC0415

  normalized = normalize_id(kind, raw_id)
  registry = ChangeRegistry(root=root, kind=kind)
  artifact = registry.find(normalized)
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
  from supekku.scripts.lib.requirements.registry import (  # noqa: PLC0415
    RequirementsRegistry,
  )

  # DEC-041-05: normalize colon-separated to dot-separated
  normalized = raw_id.replace(":", ".")
  registry = RequirementsRegistry(root=root)
  record = registry.find(normalized)
  if not record:
    raise ArtifactNotFoundError("requirement", normalized)
  req_path = Path(record.path) if record.path else root
  return ArtifactRef(id=normalized, path=req_path, record=record)


def _resolve_drift_ledger(root: Path, raw_id: str) -> ArtifactRef:
  from supekku.scripts.lib.drift.registry import DriftLedgerRegistry  # noqa: PLC0415

  normalized = raw_id.upper()
  registry = DriftLedgerRegistry(root=root)
  ledger = registry.find(normalized)
  if not ledger:
    raise ArtifactNotFoundError("drift_ledger", normalized)
  return ArtifactRef(id=normalized, path=ledger.path, record=ledger)


def _resolve_card(root: Path, raw_id: str) -> ArtifactRef:
  from supekku.scripts.lib.cards import CardRegistry  # noqa: PLC0415

  registry = CardRegistry(root=root)
  card = registry.find(raw_id)
  if not card:
    raise ArtifactNotFoundError("card", raw_id)
  return ArtifactRef(id=raw_id, path=card.path, record=card)


def _resolve_memory(root: Path, raw_id: str) -> ArtifactRef:
  from supekku.scripts.lib.memory.registry import MemoryRegistry  # noqa: PLC0415

  registry = MemoryRegistry(root=root)
  record = registry.find(raw_id)
  if not record:
    raise ArtifactNotFoundError("memory", raw_id)
  return ArtifactRef(id=raw_id, path=Path(record.path), record=record)


def _resolve_plan(root: Path, raw_id: str) -> ArtifactRef:
  from supekku.scripts.lib.core.spec_utils import load_markdown_file  # noqa: PLC0415

  normalized = _normalize_plan_id(raw_id)
  deltas_dir = get_deltas_dir(root)
  if not deltas_dir.exists():
    raise ArtifactNotFoundError("plan", normalized)
  for delta_dir in deltas_dir.iterdir():
    if not delta_dir.is_dir():
      continue
    plan_file = delta_dir / f"{normalized}.md"
    if plan_file.exists():
      frontmatter, _ = load_markdown_file(plan_file)
      return ArtifactRef(id=normalized, path=plan_file, record=frontmatter)
  raise ArtifactNotFoundError("plan", normalized)


def _resolve_backlog(root: Path, raw_id: str, kind: str) -> ArtifactRef:
  from supekku.scripts.lib.backlog.registry import BacklogRegistry  # noqa: PLC0415

  normalized = normalize_id(kind, raw_id) if kind else raw_id
  registry = BacklogRegistry(root=root)
  item = registry.find(normalized)
  error_label = kind or "backlog item"
  if item is None:
    raise ArtifactNotFoundError(error_label, normalized)
  if kind and item.kind != kind:
    raise ArtifactNotFoundError(error_label, normalized)
  return ArtifactRef(id=item.id, path=item.path, record=item)


def load_all_artifacts(root: Path, artifact_type: str) -> list[Any]:
  """Load all artifacts of a given type for cross-registry queries.

  Used by ``--referenced-by`` / ``--not-referenced-by`` CLI flags to load
  referrer registries.  Uses lazy imports matching existing common.py patterns.

  Args:
    root: Repository root path.
    artifact_type: Artifact type key (e.g. 'audit', 'delta', 'spec').

  Returns:
    List of artifact records from the resolved registry.

  Raises:
    typer.BadParameter: If artifact_type is unknown.
  """
  if artifact_type in ("delta", "revision", "audit"):
    from supekku.scripts.lib.changes.registry import ChangeRegistry  # noqa: PLC0415

    return list(ChangeRegistry(root=root, kind=artifact_type).iter())
  if artifact_type == "spec":
    from supekku.scripts.lib.specs.registry import SpecRegistry  # noqa: PLC0415

    return list(SpecRegistry(root=root).all_specs())
  if artifact_type in ("issue", "problem", "improvement", "risk"):
    from supekku.scripts.lib.backlog.registry import BacklogRegistry  # noqa: PLC0415

    return [i for i in BacklogRegistry(root=root).iter() if i.kind == artifact_type]
  if artifact_type == "backlog":
    from supekku.scripts.lib.backlog.registry import BacklogRegistry  # noqa: PLC0415

    return list(BacklogRegistry(root=root).iter())
  if artifact_type == "adr":
    from supekku.scripts.lib.decisions.registry import (  # noqa: PLC0415
      DecisionRegistry,
    )

    return list(DecisionRegistry(root=root).iter())
  if artifact_type == "policy":
    from supekku.scripts.lib.policies.registry import PolicyRegistry  # noqa: PLC0415

    return list(PolicyRegistry(root=root).iter())
  if artifact_type == "standard":
    from supekku.scripts.lib.standards.registry import (  # noqa: PLC0415
      StandardRegistry,
    )

    return list(StandardRegistry(root=root).iter())
  if artifact_type == "requirement":
    from supekku.scripts.lib.requirements.registry import (  # noqa: PLC0415
      RequirementsRegistry,
    )

    return list(RequirementsRegistry(root=root).iter())
  msg = (
    f"Unknown artifact type for --referenced-by/--not-referenced-by: {artifact_type}"
  )
  raise typer.BadParameter(msg)


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
  "drift_ledger": _resolve_drift_ledger,
  "plan": _resolve_plan,
  "issue": lambda root, raw_id: _resolve_backlog(root, raw_id, "issue"),
  "problem": lambda root, raw_id: _resolve_backlog(root, raw_id, "problem"),
  "improvement": lambda root, raw_id: _resolve_backlog(root, raw_id, "improvement"),
  "risk": lambda root, raw_id: _resolve_backlog(root, raw_id, "risk"),
  "backlog": lambda root, raw_id: _resolve_backlog(root, raw_id, ""),
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


# --- ID inference ---


def resolve_by_id(raw_id: str, root: Path) -> list[tuple[str, ArtifactRef]]:
  """Resolve artifact type from a bare ID (prefixed or numeric).

  Uses _build_artifact_index() from resolve.py for O(1) lookup across all
  registries (DEC-063-04 / POL-001).

  Args:
    raw_id: User-provided ID (e.g. 'DE-061', '61', 'SPEC-009').
    root: Repository root path.

  Returns:
    List of (artifact_type, ArtifactRef) tuples. Empty if no match.
    Prefixed IDs return 0 or 1 matches; numeric IDs may return multiple.
  """
  from supekku.cli.resolve import build_artifact_index  # noqa: PLC0415

  index = build_artifact_index(root)

  # Prefixed ID: look up directly
  prefix = _parse_prefix(raw_id)
  if prefix and prefix in PREFIX_TO_TYPE:
    canonical = raw_id.upper()
    if canonical in index:
      _rel_path, kind = index[canonical]
      try:
        ref = resolve_artifact(kind, canonical, root)
        return [(kind, ref)]
      except (ArtifactNotFoundError, ValueError):
        return []
    return []

  # Numeric-only: try all prefixed expansions
  if raw_id.isdigit():
    padded = f"{int(raw_id):03d}"
    matches: list[tuple[str, ArtifactRef]] = []
    for pfx, kind in PREFIX_TO_TYPE.items():
      candidate = f"T{raw_id}" if pfx == "T" else f"{pfx}-{padded}"
      if candidate in index:
        try:
          ref = resolve_artifact(kind, candidate, root)
          matches.append((kind, ref))
        except (ArtifactNotFoundError, ValueError):
          continue
    return matches

  # Unknown format
  return []


# --- Artifact output ---


def extract_yaml_frontmatter(path: Path) -> str:
  """Extract raw YAML frontmatter block from a markdown file.

  Returns the YAML content between the opening and closing ``---`` fences,
  without the fences themselves.  Returns an empty string if no frontmatter
  is found.

  """
  text = path.read_text()
  if not text.startswith("---"):
    return ""
  end = text.find("\n---", 3)
  if end == -1:
    return ""
  # Return content between the fences (excluding the fences themselves)
  return text[4:end].strip()


def emit_artifact(
  ref: ArtifactRef,
  *,
  json_output: bool = False,
  path_only: bool = False,
  raw_output: bool = False,
  body_only: bool = False,
  content_type: ContentType | None = None,
  format_fn: Any,
  json_fn: Any,
) -> None:
  """Dispatch artifact output by mode.

  Supports path, raw, body, json, content-type, or formatted output.

  Handles mutual-exclusivity check for --json/--path/--raw/--body-only
  and calls the appropriate output function. When ``content_type`` is
  provided it takes precedence over the boolean flags (with a warning if
  both are given).  Always raises typer.Exit.

  Args:
    ref: Resolved artifact reference.
    json_output: If True, output JSON via json_fn.
    path_only: If True, echo the artifact path.
    raw_output: If True, echo raw file content.
    body_only: If True, echo body text only (no frontmatter).
    content_type: Unified content-type selector (overrides boolean flags).
    format_fn: Callable(record) -> str for default formatted output.
    json_fn: Callable(record) -> str for JSON output. Required.

  Raises:
    typer.Exit: Always — EXIT_SUCCESS on success, EXIT_FAILURE on error.

  """
  bool_flags = sum([json_output, path_only, raw_output, body_only])

  # --content-type overrides boolean flags with a warning
  if content_type is not None and bool_flags:
    typer.echo(
      "Warning: --content-type overrides --json/--path/--raw/--body-only",
      err=True,
    )
    json_output = path_only = raw_output = body_only = False

  if bool_flags > 1:
    typer.echo(
      "Error: --json, --path, --raw, and --body-only are mutually exclusive",
      err=True,
    )
    raise typer.Exit(EXIT_FAILURE)

  if content_type is not None:
    if content_type == ContentType.markdown:
      typer.echo(ref.path.read_text())
    elif content_type == ContentType.frontmatter:
      typer.echo(format_fn(ref.record))
    elif content_type == ContentType.yaml:
      typer.echo(extract_yaml_frontmatter(ref.path))
  elif path_only:
    typer.echo(ref.path)
  elif raw_output:
    typer.echo(ref.path.read_text())
  elif body_only:
    from supekku.scripts.lib.core.spec_utils import (  # noqa: PLC0415
      load_markdown_file,
    )

    _, body = load_markdown_file(ref.path)
    typer.echo(body)
  elif json_output:
    typer.echo(json_fn(ref.record))
  else:
    typer.echo(format_fn(ref.record))
  raise typer.Exit(EXIT_SUCCESS)


# --- Artifact finding (multi-match) ---


def _matches_pattern(artifact_id: str, pattern: str) -> bool:
  """Check if artifact ID matches fnmatch pattern (case-insensitive)."""
  return fnmatch.fnmatch(artifact_id, pattern) or fnmatch.fnmatch(
    artifact_id, pattern.upper()
  )


def _find_specs(root: Path, pattern: str) -> Iterator[ArtifactRef]:
  from supekku.scripts.lib.specs.registry import SpecRegistry  # noqa: PLC0415

  registry = SpecRegistry(root)
  for spec in registry.all_specs():
    if _matches_pattern(spec.id, pattern):
      yield ArtifactRef(id=spec.id, path=spec.path, record=spec)


def _find_changes(root: Path, pattern: str, kind: str) -> Iterator[ArtifactRef]:
  from supekku.scripts.lib.changes.registry import ChangeRegistry  # noqa: PLC0415

  normalized = normalize_id(kind, pattern)
  registry = ChangeRegistry(root=root, kind=kind)
  for art_id, art in registry.collect().items():
    if _matches_pattern(art_id, normalized):
      yield ArtifactRef(id=art_id, path=art.path, record=art)


def _find_decisions(root: Path, pattern: str) -> Iterator[ArtifactRef]:
  from supekku.scripts.lib.decisions.registry import (  # noqa: PLC0415
    DecisionRegistry,
  )

  normalized = normalize_id("adr", pattern)
  registry = DecisionRegistry(root=root)
  for art_id, art in registry.collect().items():
    if _matches_pattern(art_id, normalized):
      yield ArtifactRef(id=art_id, path=Path(art.path), record=art)


def _find_policies(root: Path, pattern: str) -> Iterator[ArtifactRef]:
  from supekku.scripts.lib.policies.registry import PolicyRegistry  # noqa: PLC0415

  normalized = normalize_id("policy", pattern)
  registry = PolicyRegistry(root=root)
  for art_id, art in registry.collect().items():
    if _matches_pattern(art_id, normalized):
      yield ArtifactRef(id=art_id, path=Path(art.path), record=art)


def _find_standards(root: Path, pattern: str) -> Iterator[ArtifactRef]:
  from supekku.scripts.lib.standards.registry import (  # noqa: PLC0415
    StandardRegistry,
  )

  normalized = normalize_id("standard", pattern)
  registry = StandardRegistry(root=root)
  for art_id, art in registry.collect().items():
    if _matches_pattern(art_id, normalized):
      yield ArtifactRef(id=art_id, path=Path(art.path), record=art)


def _find_memories(root: Path, pattern: str) -> Iterator[ArtifactRef]:
  from supekku.scripts.lib.memory.registry import MemoryRegistry  # noqa: PLC0415

  normalized = pattern.strip().lower()
  if not normalized.startswith("mem."):
    normalized = f"mem.{normalized}"
  registry = MemoryRegistry(root=root)
  for art_id, art in registry.collect().items():
    if _matches_pattern(art_id, normalized):
      yield ArtifactRef(id=art_id, path=Path(art.path), record=art)


def _find_drift_ledgers(root: Path, pattern: str) -> Iterator[ArtifactRef]:
  from supekku.scripts.lib.drift.registry import (  # noqa: PLC0415
    DriftLedgerRegistry,
  )

  normalized = pattern.upper()
  registry = DriftLedgerRegistry(root=root)
  for ledger in registry.iter():
    if _matches_pattern(ledger.id, normalized):
      yield ArtifactRef(id=ledger.id, path=ledger.path, record=ledger)


def _find_cards(root: Path, pattern: str) -> Iterator[ArtifactRef]:
  """Find cards by repo-wide rglob matching {pattern}-*.md."""
  search_pattern = f"{pattern}-*.md"
  for match in sorted(root.rglob(search_pattern)):
    yield ArtifactRef(id=pattern, path=match, record=None)


def _find_requirements(root: Path, pattern: str) -> Iterator[ArtifactRef]:
  from supekku.scripts.lib.requirements.registry import (  # noqa: PLC0415
    RequirementsRegistry,
  )

  # DEC-041-05: normalize colon to dot
  normalized = pattern.replace(":", ".")
  registry = RequirementsRegistry(root=root)
  for uid, record in registry.collect().items():
    if _matches_pattern(uid, normalized):
      req_path = Path(record.path) if record.path else root
      yield ArtifactRef(id=uid, path=req_path, record=record)


def _find_plans(root: Path, pattern: str) -> Iterator[ArtifactRef]:
  from supekku.scripts.lib.core.spec_utils import (  # noqa: PLC0415
    load_markdown_file,
  )

  normalized = _normalize_plan_id(pattern)
  deltas_dir = get_deltas_dir(root)
  if not deltas_dir.exists():
    return
  for delta_dir in sorted(deltas_dir.iterdir()):
    if not delta_dir.is_dir():
      continue
    for plan_file in sorted(delta_dir.glob("IP-*.md")):
      plan_id = plan_file.stem
      if _matches_pattern(plan_id, normalized):
        try:
          frontmatter, _ = load_markdown_file(plan_file)
        except Exception:  # noqa: BLE001
          continue
        yield ArtifactRef(id=plan_id, path=plan_file, record=frontmatter)


def _find_backlog(root: Path, pattern: str, kind: str) -> Iterator[ArtifactRef]:
  from supekku.scripts.lib.backlog.registry import BacklogRegistry  # noqa: PLC0415

  kind_filter = kind if kind != "all" else None
  registry = BacklogRegistry(root=root)
  for item in registry.iter(kind=kind_filter):
    if _matches_pattern(item.id, pattern):
      yield ArtifactRef(id=item.id, path=item.path, record=item)


# Dispatch table for find: artifact_type -> finder(root, pattern) -> Iterator
_ARTIFACT_FINDERS: dict[str, Any] = {
  "spec": _find_specs,
  "delta": lambda root, pat: _find_changes(root, pat, "delta"),
  "revision": lambda root, pat: _find_changes(root, pat, "revision"),
  "audit": lambda root, pat: _find_changes(root, pat, "audit"),
  "adr": _find_decisions,
  "policy": _find_policies,
  "standard": _find_standards,
  "requirement": _find_requirements,
  "card": _find_cards,
  "memory": _find_memories,
  "drift_ledger": _find_drift_ledgers,
  "plan": _find_plans,
  "issue": lambda root, pat: _find_backlog(root, pat, "issue"),
  "problem": lambda root, pat: _find_backlog(root, pat, "problem"),
  "improvement": lambda root, pat: _find_backlog(root, pat, "improvement"),
  "risk": lambda root, pat: _find_backlog(root, pat, "risk"),
}


def find_artifacts(
  artifact_type: str, pattern: str, root: Path
) -> Iterator[ArtifactRef]:
  """Find all artifacts of a type matching a fnmatch pattern.

  Companion to resolve_artifact for the find verb group. Returns an
  iterator of ArtifactRef for all matching artifacts.

  Args:
    artifact_type: Artifact type key (e.g. 'revision', 'spec').
    pattern: fnmatch pattern to match against artifact IDs.
    root: Repository root path.

  Yields:
    ArtifactRef for each matching artifact.

  Raises:
    ValueError: If artifact_type is not in the dispatch table.

  """
  finder = _ARTIFACT_FINDERS.get(artifact_type)
  if not finder:
    msg = f"Unknown artifact type: {artifact_type}"
    raise ValueError(msg)
  yield from finder(root, pattern)
