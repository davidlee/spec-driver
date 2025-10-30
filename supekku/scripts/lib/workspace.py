"""Workspace management for organizing specs, changes, and requirements."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .backlog import find_repo_root
from .change_registry import ChangeRegistry
from .decision_registry import DecisionRegistry
from .paths import get_registry_dir
from .requirements import RequirementsRegistry
from .spec_registry import SpecRegistry

if TYPE_CHECKING:
  from pathlib import Path


@dataclass
class Workspace:
  """Unified facade over project registries."""

  root: Path
  _specs: SpecRegistry | None = None
  _requirements: RequirementsRegistry | None = None
  _decisions: DecisionRegistry | None = None
  _delta_registry: ChangeRegistry | None = None
  _revision_registry: ChangeRegistry | None = None
  _audit_registry: ChangeRegistry | None = None

  @classmethod
  def from_cwd(cls) -> Workspace:
    return cls(root=find_repo_root())

  # Spec access -------------------------------------------------
  @property
  def specs(self) -> SpecRegistry:
    if self._specs is None:
      self._specs = SpecRegistry(self.root)
    return self._specs

  def reload_specs(self) -> None:
    if self._specs is not None:
      self._specs.reload()

  # Requirements ------------------------------------------------
  @property
  def requirements(self) -> RequirementsRegistry:
    if self._requirements is None:
      self._requirements = RequirementsRegistry(
        get_registry_dir(self.root) / "requirements.yaml",
      )
    return self._requirements

  def sync_requirements(self) -> None:
    registry = self.requirements
    registry.sync_from_specs(
      [self.root / "specify" / "tech", self.root / "specify" / "product"],
      spec_registry=self.specs,
      delta_dirs=[self.root / "change" / "deltas"],
      revision_dirs=[self.root / "change" / "revisions"],
      audit_dirs=[self.root / "change" / "audits"],
    )
    registry.save()

  # Decisions --------------------------------------------------
  @property
  def decisions(self) -> DecisionRegistry:
    if self._decisions is None:
      self._decisions = DecisionRegistry(root=self.root)
    return self._decisions

  def sync_decisions(self) -> None:
    registry = self.decisions
    registry.sync_with_symlinks()

  # Change registries ------------------------------------------
  @property
  def delta_registry(self) -> ChangeRegistry:
    if self._delta_registry is None:
      self._delta_registry = ChangeRegistry(root=self.root, kind="delta")
    return self._delta_registry

  @property
  def revision_registry(self) -> ChangeRegistry:
    if self._revision_registry is None:
      self._revision_registry = ChangeRegistry(root=self.root, kind="revision")
    return self._revision_registry

  @property
  def audit_registry(self) -> ChangeRegistry:
    if self._audit_registry is None:
      self._audit_registry = ChangeRegistry(root=self.root, kind="audit")
    return self._audit_registry

  def sync_change_registries(self, *, kinds: list[str] | None = None) -> None:
    kinds = kinds or ["delta", "revision", "audit"]
    for kind in kinds:
      if kind == "delta":
        self.delta_registry.sync()
      elif kind == "revision":
        self.revision_registry.sync()
      elif kind == "audit":
        self.audit_registry.sync()
      else:
        msg = f"Unsupported change registry kind: {kind}"
        raise ValueError(msg)


__all__ = ["Workspace"]
