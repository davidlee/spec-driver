"""ADR-009 canonical registry read surface + frontmatter-file registry ABC.

RegistryProtocol[T_co]: find / collect / iter  (filter excluded per ER-1).
FrontmatterFileRegistry[T]: template-method ABC for YAML-backed registries.

Imports spec_driver.core.* (canonical helpers) — NOT supekku.* (ER-6).
Imports nothing from domain.relations (DEC-116-2).
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from collections.abc import Iterator
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, Generic, Protocol, TypeVar, runtime_checkable

import yaml

from spec_driver.core.dates import parse_date
from spec_driver.core.paths import get_registry_dir
from spec_driver.core.repo import find_repo_root
from spec_driver.core.spec_utils import extract_h1_title, load_markdown_file

if TYPE_CHECKING:
  from typing import Never

T_co = TypeVar("T_co", covariant=True)
T = TypeVar("T")


# ── ADR-009 Read-Surface Protocol ────────────────────────────────────────────


@runtime_checkable
class RegistryProtocol(Protocol[T_co]):
  """ADR-009 canonical read surface. Covers find/collect/iter only; filter excluded (ER-1).

  Signature locked by P0 spike (DE-116/phase-01.md §9):
    - ``find(self, id, /)`` positional-only absorbs decision_id/policy_id/standard_id divergence.
    - ``iter(self, status=None)`` positional-or-keyword per ADR-009 §1.
  """

  def find(self, id: str, /) -> T_co | None:
    ...

  def collect(self) -> dict[str, T_co]:
    ...

  def iter(self, status: str | None = None) -> Iterator[T_co]:
    ...


# ── Frontmatter-File Registry Base ───────────────────────────────────────────


class FrontmatterFileRegistry(ABC, Generic[T]):
  """Template-method ABC for a registry backed by frontmatter markdown files.

  Subclasses define ``_prefix``, ``_yaml_root_key``, ``_build_record``, and
  ``_artifact_dir``.  Backlink composition is owned by the orchestration layer
  (Workspace); registries are pure (DEC-116-2).
  """

  _prefix: ClassVar[str]
  _yaml_root_key: ClassVar[str]
  backlink_inputs: ClassVar[list[tuple[str, str]]] = []

  def __init__(self, *, root: Path | None = None) -> None:
    self.root = find_repo_root(root)
    self.directory = self._artifact_dir(self.root)
    self.output_path = get_registry_dir(self.root) / f"{self._yaml_root_key}.yaml"

  # ── ADR-009 read surface ────────────────────────────────────────────────

  def collect(self) -> dict[str, T]:
    """Glob ``{_prefix}-*.md`` in the artefact directory, parse each file."""
    records: dict[str, T] = {}
    if not self.directory.exists():
      return records
    pattern = f"{self._prefix}-*.md"
    for file_path in sorted(self.directory.glob(pattern)):
      try:
        record = self._parse_file(file_path)
        if record is not None:
          records[record.id] = record  # type: ignore[attr-defined]
      except (ValueError, KeyError, FileNotFoundError):
        continue
    return records

  def iter(self, status: str | None = None) -> Iterator[T]:
    """Iterate records, optionally filtered by status. Positional-or-keyword (ADR-009 §1)."""
    for record in self.collect().values():
      if status is None or getattr(record, "status", None) == status:
        yield record

  def find(self, id: str, /) -> T | None:
    """Find a specific record by ID. Positional-only."""
    return self.collect().get(id)

  # ── Persistence (pure — no backlinks) ───────────────────────────────────

  def write(
    self,
    path: Path | None = None,
    *,
    records: dict[str, T] | None = None,
  ) -> None:
    """Write registry to YAML (pure dump; no backlink composition).

    Args:
        path: Output path. Defaults to ``self.output_path``.
        records: Pre-collected records. Defaults to ``self.collect()``.
    """
    if path is None:
      path = self.output_path
    if records is None:
      records = self.collect()

    registry_data = {
      self._yaml_root_key: {
        record_id: record.to_dict(self.root)  # type: ignore[attr-defined]
        for record_id, record in sorted(records.items())
      },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(registry_data, sort_keys=False), encoding="utf-8")

  def sync(self) -> None:
    """Sync registry: collect and write (no backlinks — orchestration owns composition)."""
    self.write(records=self.collect())

  # ── Template-method hooks ───────────────────────────────────────────────

  def _parse_file(self, file_path: Path) -> T | None:
    """Parse a frontmatter markdown file into a record.

    Template method: calls ``_resolve_status`` → ``_build_record``.
    Override ``_resolve_status`` for custom status inference (e.g., ADR symlink dirs).
    """
    frontmatter, content = load_markdown_file(file_path)
    if not frontmatter:
      frontmatter = {}

    m = re.match(rf"{self._prefix}-(\d+)", file_path.name)
    if not m:
      return None

    record_id = frontmatter.get("id", f"{self._prefix}-{m.group(1)}")
    title = (
      frontmatter.get("title", "")
      or extract_h1_title(content, f"{self._prefix}-")
      or file_path.stem.replace("-", " ").title()
    )
    status = self._resolve_status(frontmatter, file_path)
    return self._build_record(
      frontmatter,
      content,
      record_id=record_id,
      title=title,
      status=status,
      path=file_path,
    )

  def _resolve_status(self, fm: dict[str, Any], path: Path) -> str:  # noqa: ARG002
    """Resolve status from frontmatter. Base: fm['status'] or 'draft'.

    Subclasses MAY override (e.g., DecisionRegistry infers from symlink dirs).
    AR-1: DecisionRegistry MUST short-circuit — do NOT call super() if your
    override can return early; the base default ('draft') would mask later logic.
    """
    return (fm.get("status") or "").lower() or "draft"

  def _matches_common(
    self,
    record: T,
    *,
    tag: str | None,
    spec: str | None,
    delta: str | None,
    requirement: str | None,
  ) -> bool:
    """Shared filter predicate for the 4 common kw-only filter fields."""
    if tag and tag not in getattr(record, "tags", ()):
      return False
    if spec and spec not in getattr(record, "specs", ()):
      return False
    if delta and delta not in getattr(record, "deltas", ()):
      return False
    if requirement and requirement not in getattr(record, "requirements", ()):
      return False
    return True

  def _filter(
    self,
    *,
    common: dict[str, str | None],
    extra: dict[str, str | None],
  ) -> list[T]:
    """Generic filter: common kw-only fields + per-registry extras.

    ``common`` is passed to ``_matches_common``. ``extra`` is checked as
    ``getattr(record, field_name)`` for each non-None value.
    """
    return [
      r
      for r in self.iter()
      if self._matches_common(r, **common)  # type: ignore[arg-type]
      and all(
        v is None or v in (getattr(r, f, ()) or ())
        for f, v in extra.items()
      )
    ]

  # ── Abstract hooks ──────────────────────────────────────────────────────

  @abstractmethod
  def _artifact_dir(self, root: Path) -> Path:
    """Return the artefact directory for this registry (e.g. get_decisions_dir)."""
    ...

  @abstractmethod
  def _build_record(
    self,
    fm: dict[str, Any],
    content: str,
    *,
    record_id: str,
    title: str,
    status: str,
    path: Path,
  ) -> T | None:
    """Build a typed record from parsed frontmatter and content."""
    ...


__all__ = [
  "FrontmatterFileRegistry",
  "RegistryProtocol",
]
