"""Workspace management for organizing specs, changes, and requirements."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .changes.registry import ChangeRegistry
from .core.paths import get_registry_dir
from .core.repo import find_repo_root
from .decisions.registry import DecisionRegistry
from .requirements.registry import RequirementsRegistry
from .specs.registry import SpecRegistry

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
    """Create workspace from current working directory.

    Returns:
      Workspace instance rooted at repository root.
    """
    return cls(root=find_repo_root())

  # Spec access -------------------------------------------------
  @property
  def specs(self) -> SpecRegistry:
    """Get or create spec registry.

    Returns:
      SpecRegistry instance for this workspace.
    """
    if self._specs is None:
      self._specs = SpecRegistry(self.root)
    return self._specs

  def reload_specs(self) -> None:
    """Reload spec registry from disk."""
    if self._specs is not None:
      self._specs.reload()

  # Requirements ------------------------------------------------
  @property
  def requirements(self) -> RequirementsRegistry:
    """Get or create requirements registry.

    Returns:
      RequirementsRegistry instance for this workspace.
    """
    if self._requirements is None:
      self._requirements = RequirementsRegistry(
        get_registry_dir(self.root) / "requirements.yaml",
      )
    return self._requirements

  def sync_requirements(self) -> None:
    """Synchronize requirements registry from specs and changes."""
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
    """Get or create decision registry.

    Returns:
      DecisionRegistry instance for this workspace.
    """
    if self._decisions is None:
      self._decisions = DecisionRegistry(root=self.root)
    return self._decisions

  def sync_decisions(self) -> None:
    """Synchronize decision registry with symlinks."""
    registry = self.decisions
    registry.sync_with_symlinks()

  # Change registries ------------------------------------------
  @property
  def delta_registry(self) -> ChangeRegistry:
    """Get or create delta change registry.

    Returns:
      ChangeRegistry instance for deltas.
    """
    if self._delta_registry is None:
      self._delta_registry = ChangeRegistry(root=self.root, kind="delta")
    return self._delta_registry

  @property
  def revision_registry(self) -> ChangeRegistry:
    """Get or create revision change registry.

    Returns:
      ChangeRegistry instance for revisions.
    """
    if self._revision_registry is None:
      self._revision_registry = ChangeRegistry(root=self.root, kind="revision")
    return self._revision_registry

  @property
  def audit_registry(self) -> ChangeRegistry:
    """Get or create audit change registry.

    Returns:
      ChangeRegistry instance for audits.
    """
    if self._audit_registry is None:
      self._audit_registry = ChangeRegistry(root=self.root, kind="audit")
    return self._audit_registry

  def sync_change_registries(self, *, kinds: list[str] | None = None) -> None:
    """Synchronize change registries of specified kinds.

    Args:
      kinds: List of registry kinds to sync. Defaults to all kinds.

    Raises:
      ValueError: If an unsupported registry kind is specified.
    """
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
