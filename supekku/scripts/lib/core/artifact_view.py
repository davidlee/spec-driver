"""Artifact projection layer.

Normalises all registries to a common ArtifactEntry view model.
No TUI imports — pure data in, pure data out. Reusable by any consumer
that needs a uniform artifact view (TUI, CLI search, export).

Design decisions: DEC-053-04, DEC-053-06, DEC-053-07, DEC-053-08, DEC-053-11.
"""

from __future__ import annotations

import contextlib
import io
import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ArtifactGroup(Enum):
  """Semantic grouping for artifact types (DEC-053-11)."""

  GOVERNANCE = "governance"
  CHANGE = "change"
  DOMAIN = "domain"
  OPERATIONAL = "operational"


@dataclass(frozen=True)
class ArtifactTypeMeta:
  """Display and classification metadata for an artifact type (DEC-053-11)."""

  singular: str
  plural: str
  group: ArtifactGroup


class ArtifactType(Enum):
  """Artifact type identifiers, ordered by display group."""

  # Governance
  ADR = "adr"
  POLICY = "policy"
  STANDARD = "standard"
  # Change
  DELTA = "delta"
  REVISION = "revision"
  AUDIT = "audit"
  # Domain
  SPEC = "spec"
  REQUIREMENT = "requirement"
  # Operational
  MEMORY = "memory"
  CARD = "card"
  BACKLOG = "backlog"

  @property
  def meta(self) -> ArtifactTypeMeta:
    """Return display/classification metadata for this type."""
    return ARTIFACT_TYPE_META[self]

  @property
  def singular(self) -> str:
    """Human-readable singular name (e.g. 'ADR', 'Policy')."""
    return self.meta.singular

  @property
  def plural(self) -> str:
    """Human-readable plural name (e.g. 'ADRs', 'Policies')."""
    return self.meta.plural

  @property
  def group(self) -> ArtifactGroup:
    """Semantic group this type belongs to."""
    return self.meta.group


_GOV = ArtifactGroup.GOVERNANCE
_CHG = ArtifactGroup.CHANGE
_DOM = ArtifactGroup.DOMAIN
_OPS = ArtifactGroup.OPERATIONAL

ARTIFACT_TYPE_META: dict[ArtifactType, ArtifactTypeMeta] = {
  ArtifactType.ADR: ArtifactTypeMeta("ADR", "ADRs", _GOV),
  ArtifactType.POLICY: ArtifactTypeMeta("Policy", "Policies", _GOV),
  ArtifactType.STANDARD: ArtifactTypeMeta("Standard", "Standards", _GOV),
  ArtifactType.DELTA: ArtifactTypeMeta("Delta", "Deltas", _CHG),
  ArtifactType.REVISION: ArtifactTypeMeta("Revision", "Revisions", _CHG),
  ArtifactType.AUDIT: ArtifactTypeMeta("Audit", "Audits", _CHG),
  ArtifactType.SPEC: ArtifactTypeMeta("Spec", "Specs", _DOM),
  ArtifactType.REQUIREMENT: ArtifactTypeMeta(
    "Requirement",
    "Requirements",
    _DOM,
  ),
  ArtifactType.MEMORY: ArtifactTypeMeta("Memory", "Memories", _OPS),
  ArtifactType.CARD: ArtifactTypeMeta("Card", "Cards", _OPS),
  ArtifactType.BACKLOG: ArtifactTypeMeta(
    "Backlog Item",
    "Backlog Items",
    _OPS,
  ),
}


# Maps ArtifactType to the attribute name used for title on the record model.
# Most use 'name', some use 'title'.
_TITLE_ATTR: dict[ArtifactType, str] = {
  ArtifactType.ADR: "title",
  ArtifactType.POLICY: "title",
  ArtifactType.STANDARD: "title",
  ArtifactType.DELTA: "name",
  ArtifactType.REVISION: "name",
  ArtifactType.AUDIT: "name",
  ArtifactType.SPEC: "name",
  ArtifactType.REQUIREMENT: "title",
  ArtifactType.MEMORY: "name",
  ArtifactType.CARD: "title",
  ArtifactType.BACKLOG: "title",
}

# Maps ArtifactType to the attribute name used for ID on the record model.
_ID_ATTR: dict[ArtifactType, str] = {
  ArtifactType.REQUIREMENT: "uid",
}

# Maps ArtifactType to the attribute name used for status.
# Card uses 'lane' instead of 'status'.
_STATUS_ATTR: dict[ArtifactType, str] = {
  ArtifactType.CARD: "lane",
}


@dataclass(frozen=True)
class ArtifactEntry:
  """Normalised view model for any artifact."""

  id: str
  title: str
  status: str
  path: Path
  artifact_type: ArtifactType
  error: str | None = None


def adapt_record(record: Any, artifact_type: ArtifactType) -> ArtifactEntry:
  """Adapt a registry record to an ArtifactEntry.

  Handles attribute name divergences across record models.
  """
  id_attr = _ID_ATTR.get(artifact_type, "id")
  title_attr = _TITLE_ATTR.get(artifact_type, "name")
  status_attr = _STATUS_ATTR.get(artifact_type, "status")

  return ArtifactEntry(
    id=getattr(record, id_attr, ""),
    title=getattr(record, title_attr, ""),
    status=getattr(record, status_attr, ""),
    path=Path(getattr(record, "path", ".")),
    artifact_type=artifact_type,
  )


def _collect_safe(
  collect_fn: Any,
  artifact_type: ArtifactType,
) -> dict[str, ArtifactEntry]:
  """Call a collect function with error isolation.

  Catches exceptions and stderr output. Returns error entries on failure.
  """
  stderr_capture = io.StringIO()
  try:
    with contextlib.redirect_stderr(stderr_capture):
      records = collect_fn()
  except Exception as exc:
    logger.warning("Failed to load %s: %s", artifact_type.value, exc)
    return {
      f"__error_{artifact_type.value}__": ArtifactEntry(
        id="",
        title="",
        status="",
        path=Path(),
        artifact_type=artifact_type,
        error=f"Load failed: {exc}",
      )
    }

  captured = stderr_capture.getvalue()
  if captured:
    logger.debug("stderr from %s collect: %s", artifact_type.value, captured.strip())

  result: dict[str, ArtifactEntry] = {}
  for key, record in records.items():
    try:
      result[key] = adapt_record(record, artifact_type)
    except Exception as exc:
      logger.warning("Failed to adapt %s record %s: %s", artifact_type.value, key, exc)
      result[key] = ArtifactEntry(
        id=str(key),
        title="",
        status="",
        path=Path(),
        artifact_type=artifact_type,
        error=f"Adapt failed: {exc}",
      )
  return result


class ArtifactSnapshot:
  """Cached snapshot of all artifacts across registries.

  Calls collect() once per registry at init. Supports targeted refresh
  for watch-triggered invalidation (DEC-053-07).
  """

  def __init__(self, *, root: Path) -> None:
    self._root = root
    self.entries: dict[ArtifactType, dict[str, ArtifactEntry]] = {}
    self._load_all()

  def _load_all(self) -> None:
    """Load all registries into the snapshot."""
    for art_type in ArtifactType:
      self._load_type(art_type)

  def _load_type(self, art_type: ArtifactType) -> None:
    """Load a single registry type into the snapshot."""
    registry = self._make_registry(art_type)
    if registry is None:
      self.entries[art_type] = {}
      return

    self.entries[art_type] = _collect_safe(registry.collect, art_type)

  def _make_registry(self, art_type: ArtifactType) -> Any | None:
    """Instantiate a registry for the given type. Returns None on failure."""
    try:
      return _REGISTRY_FACTORIES[art_type](self._root)
    except Exception as exc:
      logger.warning("Failed to create %s registry: %s", art_type.value, exc)
      self.entries[art_type] = {
        f"__error_{art_type.value}__": ArtifactEntry(
          id="",
          title="",
          status="",
          path=Path(),
          artifact_type=art_type,
          error=f"Registry init failed: {exc}",
        )
      }
      return None

  def refresh(self, art_type: ArtifactType) -> None:
    """Re-collect a single registry type (watch-triggered invalidation)."""
    self._load_type(art_type)

  def all_entries(
    self,
    *,
    type_filter: ArtifactType | None = None,
    status_filter: str | None = None,
  ) -> list[ArtifactEntry]:
    """Return a flat list of all entries, optionally filtered."""
    result: list[ArtifactEntry] = []
    for art_type, entries in self.entries.items():
      if type_filter is not None and art_type != type_filter:
        continue
      for entry in entries.values():
        if entry.error is not None:
          continue
        if status_filter is not None and entry.status != status_filter:
          continue
        result.append(entry)
    return result

  def find_entry(self, artifact_id: str) -> ArtifactEntry | None:
    """Find an entry by ID across all artifact types.

    O(n) scan — acceptable for user-initiated navigation (DEC-054-06).
    """
    for type_entries in self.entries.values():
      entry = type_entries.get(artifact_id)
      if entry is not None and entry.error is None:
        return entry
    return None

  def counts_by_type(self) -> dict[ArtifactType, int]:
    """Return artifact counts per type (excluding error entries)."""
    return {
      art_type: sum(1 for e in entries.values() if e.error is None)
      for art_type, entries in self.entries.items()
    }


def path_to_artifact_type(changed_path: Path, root: Path) -> ArtifactType | None:
  """Map a changed filesystem path to its ArtifactType.

  Uses paths.py subdirectory conventions to determine which registry
  owns the changed file. Returns None if the path doesn't map to a
  known artifact type.
  """
  from supekku.scripts.lib.core.paths import (  # noqa: PLC0415
    AUDITS_SUBDIR,
    BACKLOG_DIR,
    DECISIONS_SUBDIR,
    DELTAS_SUBDIR,
    MEMORY_DIR,
    POLICIES_SUBDIR,
    PRODUCT_SPECS_SUBDIR,
    REVISIONS_SUBDIR,
    STANDARDS_SUBDIR,
    TECH_SPECS_SUBDIR,
    get_spec_driver_root,
  )

  sd_root = get_spec_driver_root(root)
  try:
    rel = changed_path.resolve().relative_to(sd_root.resolve())
  except ValueError:
    # Check if it's a kanban card (lives at repo root, not under .spec-driver)
    try:
      repo_rel = changed_path.resolve().relative_to(root.resolve())
      if repo_rel.parts and repo_rel.parts[0] == "kanban":
        return ArtifactType.CARD
    except ValueError:
      pass
    return None

  if not rel.parts:
    return None

  top = rel.parts[0]
  _subdir_map: dict[str, ArtifactType] = {
    TECH_SPECS_SUBDIR: ArtifactType.SPEC,
    PRODUCT_SPECS_SUBDIR: ArtifactType.SPEC,
    DECISIONS_SUBDIR: ArtifactType.ADR,
    POLICIES_SUBDIR: ArtifactType.POLICY,
    STANDARDS_SUBDIR: ArtifactType.STANDARD,
    DELTAS_SUBDIR: ArtifactType.DELTA,
    REVISIONS_SUBDIR: ArtifactType.REVISION,
    AUDITS_SUBDIR: ArtifactType.AUDIT,
    BACKLOG_DIR: ArtifactType.BACKLOG,
    MEMORY_DIR: ArtifactType.MEMORY,
  }
  return _subdir_map.get(top)


def _make_spec_registry(root: Path) -> Any:
  from supekku.scripts.lib.specs.registry import SpecRegistry  # noqa: PLC0415

  return SpecRegistry(root)


def _make_change_registry(root: Path, kind: str) -> Any:
  from supekku.scripts.lib.changes.registry import ChangeRegistry  # noqa: PLC0415

  return ChangeRegistry(root=root, kind=kind)


def _make_decision_registry(root: Path) -> Any:
  from supekku.scripts.lib.decisions.registry import DecisionRegistry  # noqa: PLC0415

  return DecisionRegistry(root=root)


def _make_requirements_registry(root: Path) -> Any:
  from supekku.scripts.lib.requirements.registry import (  # noqa: PLC0415
    RequirementsRegistry,
  )

  return RequirementsRegistry(root=root)


def _make_memory_registry(root: Path) -> Any:
  from supekku.scripts.lib.memory.registry import MemoryRegistry  # noqa: PLC0415

  return MemoryRegistry(root=root)


def _make_card_registry(root: Path) -> Any:
  from supekku.scripts.lib.cards.registry import CardRegistry  # noqa: PLC0415

  return CardRegistry(root)


def _make_policy_registry(root: Path) -> Any:
  from supekku.scripts.lib.policies.registry import PolicyRegistry  # noqa: PLC0415

  return PolicyRegistry(root=root)


def _make_standard_registry(root: Path) -> Any:
  from supekku.scripts.lib.standards.registry import StandardRegistry  # noqa: PLC0415

  return StandardRegistry(root=root)


def _make_backlog_registry(root: Path) -> Any:
  from supekku.scripts.lib.backlog.registry import BacklogRegistry  # noqa: PLC0415

  return BacklogRegistry(root=root)


_REGISTRY_FACTORIES: dict[ArtifactType, Any] = {
  ArtifactType.ADR: _make_decision_registry,
  ArtifactType.POLICY: _make_policy_registry,
  ArtifactType.STANDARD: _make_standard_registry,
  ArtifactType.DELTA: lambda root: _make_change_registry(root, "delta"),
  ArtifactType.REVISION: lambda root: _make_change_registry(root, "revision"),
  ArtifactType.AUDIT: lambda root: _make_change_registry(root, "audit"),
  ArtifactType.SPEC: _make_spec_registry,
  ArtifactType.REQUIREMENT: _make_requirements_registry,
  ArtifactType.MEMORY: _make_memory_registry,
  ArtifactType.CARD: _make_card_registry,
  ArtifactType.BACKLOG: _make_backlog_registry,
}
