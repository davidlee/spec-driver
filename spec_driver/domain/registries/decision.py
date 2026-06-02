"""Decision (ADR) registry — collapsed onto FrontmatterFileRegistry base.

Canonical home in spec_driver.domain.registries.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

from spec_driver.core.dates import parse_date
from spec_driver.core.paths import get_decisions_dir
from spec_driver.domain.records.decision import DecisionRecord
from spec_driver.domain.registries.frontmatter import FrontmatterFileRegistry

if TYPE_CHECKING:
  pass


class DecisionRegistry(FrontmatterFileRegistry[DecisionRecord]):
  """Registry for managing Architecture Decision Records."""

  _prefix: ClassVar[str] = "ADR"
  _yaml_root_key: ClassVar[str] = "decisions"
  backlink_inputs: ClassVar[list[tuple[str, str]]] = []  # ADR has no backlink sources

  # ── Abstract hooks ──────────────────────────────────────────────────────

  def _artifact_dir(self, root: Path) -> Path:
    return get_decisions_dir(root)

  def _build_record(
    self,
    fm: dict[str, Any],
    content: str,  # noqa: ARG002 (content already consumed for title in base)
    *,
    record_id: str,
    title: str,
    status: str,
    path: Path,
  ) -> DecisionRecord:
    return DecisionRecord(
      id=record_id,
      title=title,
      status=status,
      created=parse_date(fm.get("created")),
      decided=parse_date(fm.get("decided")),
      updated=parse_date(fm.get("updated")),
      reviewed=parse_date(fm.get("reviewed")),
      authors=fm.get("authors", []),
      owners=fm.get("owners", []),
      supersedes=fm.get("supersedes", []),
      superseded_by=fm.get("superseded_by", []),
      policies=fm.get("policies", []),
      standards=fm.get("standards", []),
      specs=fm.get("specs", []),
      requirements=fm.get("requirements", []),
      deltas=fm.get("deltas", []),
      revisions=fm.get("revisions", []),
      audits=fm.get("audits", []),
      related_decisions=fm.get("related_decisions", []),
      related_policies=fm.get("related_policies", []),
      tags=fm.get("tags", []),
      summary=fm.get("summary", ""),
      path=str(path),
    )

  # ── Status resolution (AR-1: short-circuit, no super()) ─────────────────

  def _resolve_status(self, fm: dict[str, Any], path: Path) -> str:
    """Resolve ADR status. Short-circuits per AR-1: checks fm first, then symlink dirs.

    Does NOT call super()._resolve_status() — the base default ('draft') would
    mask symlink-dir inference.
    """
    status = (fm.get("status") or "").lower()
    if status:
      return status
    return self._infer_from_dirs(path) or "draft"

  def _infer_from_dirs(self, path: Path) -> str:
    """Infer ADR status from symlink directory membership."""
    from supekku.scripts.lib.decisions.lifecycle import (  # noqa: PLC0415
      ADR_STATUSES,
    )

    for status_dir_name in ADR_STATUSES:
      if (self.directory / status_dir_name / path.name).exists():
        return status_dir_name
    return ""

  # ── Filter (per-registry kw-only fields) ────────────────────────────────

  def filter(
    self,
    *,
    tag: str | None = None,
    spec: str | None = None,
    delta: str | None = None,
    requirement: str | None = None,
    policy: str | None = None,
    standard: str | None = None,
  ) -> list[DecisionRecord]:
    """Filter decisions by various criteria."""
    return self._filter(
      common={"tag": tag, "spec": spec, "delta": delta, "requirement": requirement},
      extra={"policies": policy, "standards": standard},
    )

  # ── Symlink management (ADR-specific — no base equivalent) ──────────────

  def sync_with_symlinks(self) -> None:
    """Sync registry and rebuild status symlinks in one operation."""
    self.collect()  # ensure data loaded
    self.write()
    self.rebuild_status_symlinks()

  def rebuild_status_symlinks(self) -> None:
    """Rebuild all status-based symlink directories."""
    decisions = self.collect()
    decisions_dir = get_decisions_dir(self.root)

    self._cleanup_all_status_directories(decisions_dir)

    status_groups: dict[str, list[DecisionRecord]] = {}
    for decision in decisions.values():
      status_groups.setdefault(decision.status, []).append(decision)

    for status, status_decisions in status_groups.items():
      status_dir = decisions_dir / status
      self._rebuild_status_directory(status_dir, status_decisions)

  def _cleanup_all_status_directories(self, decisions_dir: Path) -> None:
    """Remove all symlinks from existing status directories."""
    from supekku.scripts.lib.decisions.lifecycle import (  # noqa: PLC0415
      ADR_STATUSES,
    )

    for status in ADR_STATUSES:
      status_dir = decisions_dir / status
      if status_dir.exists() and status_dir.is_dir():
        for item in status_dir.iterdir():
          if item.is_symlink():
            item.unlink()

  def _rebuild_status_directory(
    self,
    status_dir: Path,
    decisions: list[DecisionRecord],
  ) -> None:
    """Rebuild a single status directory with symlinks."""
    status_dir.mkdir(exist_ok=True)
    for decision in decisions:
      source_file = Path(decision.path)
      if source_file.exists():
        link_name = status_dir / source_file.name
        relative_target = Path("..") / source_file.name
        link_name.symlink_to(relative_target)


__all__ = ["DecisionRegistry"]
