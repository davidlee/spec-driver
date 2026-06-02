"""Policy registry — collapsed onto FrontmatterFileRegistry base.

Canonical home in spec_driver.domain.registries.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

from spec_driver.core.dates import parse_date
from spec_driver.core.paths import get_policies_dir
from spec_driver.domain.records.policy import PolicyRecord
from spec_driver.domain.registries.frontmatter import FrontmatterFileRegistry

if TYPE_CHECKING:
  pass


class PolicyRegistry(FrontmatterFileRegistry[PolicyRecord]):
  """Registry for managing Policies."""

  _prefix: ClassVar[str] = "POL"
  _yaml_root_key: ClassVar[str] = "policies"
  backlink_inputs: ClassVar[list[tuple[str, str]]] = [
    ("decisions", "policies"),
  ]

  # ── Abstract hooks ──────────────────────────────────────────────────────

  def _artifact_dir(self, root: Path) -> Path:
    return get_policies_dir(root)

  def _build_record(
    self,
    fm: dict[str, Any],
    content: str,  # noqa: ARG002
    *,
    record_id: str,
    title: str,
    status: str,
    path: Path,
  ) -> PolicyRecord:
    return PolicyRecord(
      id=record_id,
      title=title,
      status=status,
      created=parse_date(fm.get("created")),
      updated=parse_date(fm.get("updated")),
      reviewed=parse_date(fm.get("reviewed")),
      owners=fm.get("owners", []),
      supersedes=fm.get("supersedes", []),
      superseded_by=fm.get("superseded_by", []),
      standards=fm.get("standards", []),
      specs=fm.get("specs", []),
      requirements=fm.get("requirements", []),
      deltas=fm.get("deltas", []),
      related_policies=fm.get("related_policies", []),
      related_standards=fm.get("related_standards", []),
      tags=fm.get("tags", []),
      summary=fm.get("summary", ""),
      path=str(path),
      ext_id=str(fm.get("ext_id", "")),
      ext_url=str(fm.get("ext_url", "")),
    )

  # ── Filter (per-registry kw-only fields) ────────────────────────────────

  def filter(
    self,
    *,
    tag: str | None = None,
    spec: str | None = None,
    delta: str | None = None,
    requirement: str | None = None,
    standard: str | None = None,
  ) -> list[PolicyRecord]:
    """Filter policies by various criteria."""
    return self._filter(
      common={"tag": tag, "spec": spec, "delta": delta, "requirement": requirement},
      extra={"standards": standard},
    )


__all__ = ["PolicyRegistry"]
