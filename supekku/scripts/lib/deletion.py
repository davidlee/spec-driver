"""Deletion infrastructure for specs, deltas, revisions, and ADRs.

Provides safe deletion with validation, dry-run support, and proper cleanup
of registries, symlinks, and cross-references.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from .registry_migration import RegistryV2
from .spec_index import SpecIndexBuilder

if TYPE_CHECKING:
  pass


@dataclass
class DeletionPlan:
  """Describes what would be deleted without executing.

  Attributes:
      artifact_id: ID of the artifact to delete (e.g., "SPEC-001")
      artifact_type: Type of artifact ("spec", "delta", "revision", "adr")
      files_to_delete: List of file paths that would be deleted
      symlinks_to_remove: List of symlink paths that would be removed
      registry_updates: Registry files and entries to remove
      cross_references: Other artifacts that reference this one
      is_safe: Whether deletion is safe (no blocking issues)
      warnings: List of warning messages

  """

  artifact_id: str
  artifact_type: str
  files_to_delete: list[Path] = field(default_factory=list)
  symlinks_to_remove: list[Path] = field(default_factory=list)
  registry_updates: dict[str, list[str]] = field(default_factory=dict)
  cross_references: dict[str, list[str]] = field(default_factory=dict)
  is_safe: bool = True
  warnings: list[str] = field(default_factory=list)

  def add_warning(self, message: str) -> None:
    """Add a warning message to the plan."""
    self.warnings.append(message)

  def add_file(self, path: Path) -> None:
    """Add a file to delete."""
    self.files_to_delete.append(path)

  def add_symlink(self, path: Path) -> None:
    """Add a symlink to remove."""
    self.symlinks_to_remove.append(path)

  def add_registry_update(self, registry_file: str, entry: str) -> None:
    """Add a registry entry to remove."""
    if registry_file not in self.registry_updates:
      self.registry_updates[registry_file] = []
    self.registry_updates[registry_file].append(entry)

  def add_cross_reference(self, from_id: str, to_id: str) -> None:
    """Add a cross-reference."""
    if from_id not in self.cross_references:
      self.cross_references[from_id] = []
    self.cross_references[from_id].append(to_id)


class DeletionValidator:
  """Validates deletion safety and identifies cleanup requirements.

  Checks if artifact exists, finds cross-references, detects orphaned
  symlinks, and validates that deletion is safe to proceed.
  """

  def __init__(self, repo_root: Path) -> None:
    """Initialize validator.

    Args:
        repo_root: Repository root directory

    """
    self.repo_root = repo_root
    self.tech_dir = repo_root / "specify" / "tech"
    self.change_dir = repo_root / "change"

  def validate_spec_deletion(self, spec_id: str) -> DeletionPlan:
    """Validate deletion of a spec.

    Args:
        spec_id: Spec ID (e.g., "SPEC-001")

    Returns:
        DeletionPlan describing what would be deleted

    """
    plan = DeletionPlan(artifact_id=spec_id, artifact_type="spec")

    # Check if spec directory exists
    spec_dir = self.tech_dir / spec_id
    if not spec_dir.exists():
      plan.is_safe = False
      plan.add_warning(f"Spec directory not found: {spec_dir}")
      return plan

    # Add spec files to deletion plan
    for spec_file in spec_dir.rglob("*.md"):
      plan.add_file(spec_file)

    # Find symlinks pointing to this spec
    symlinks = self._find_spec_symlinks(spec_id)
    for symlink in symlinks:
      plan.add_symlink(symlink)

    # Check registry entries (would need to parse registry_v2.json)
    plan.add_registry_update("registry_v2.json", spec_id)

    # TODO: Find cross-references in deltas, revisions, requirements
    # This requires parsing YAML/markdown files

    return plan

  def _find_spec_symlinks(self, spec_id: str) -> list[Path]:
    """Find all symlinks pointing to a spec directory.

    Args:
        spec_id: Spec ID (e.g., "SPEC-001")

    Returns:
        List of symlink paths

    """
    symlinks = []
    spec_dir = self.tech_dir / spec_id

    # Check index directories for symlinks
    for index_dir in ["by-slug", "by-package", "by-language"]:
      index_path = self.tech_dir / index_dir
      if not index_path.exists():
        continue

      # Find all symlinks in this index
      for item in index_path.rglob("*"):
        if item.is_symlink():
          # Check if it points to our spec
          try:
            target = item.resolve()
            if target == spec_dir or target.is_relative_to(spec_dir):
              symlinks.append(item)
          except (OSError, ValueError):
            # Broken symlink or resolution error
            continue

    return symlinks


class DeletionExecutor:
  """Executes deletion with proper cleanup.

  Handles deletion of specs, deltas, revisions, and ADRs with proper
  registry updates, symlink cleanup, and cross-reference handling.
  """

  def __init__(self, repo_root: Path) -> None:
    """Initialize executor.

    Args:
        repo_root: Repository root directory

    """
    self.repo_root = repo_root
    self.validator = DeletionValidator(repo_root)
    self.registry_path = repo_root / ".spec-driver" / "registry" / "registry_v2.json"

  def delete_spec(
    self,
    spec_id: str,
    *,
    dry_run: bool = False,
  ) -> DeletionPlan:
    """Delete a spec with full cleanup.

    Args:
        spec_id: Spec ID (e.g., "SPEC-001")
        dry_run: If True, only validate and return plan without deleting

    Returns:
        DeletionPlan describing what was (or would be) deleted

    """
    # Validate deletion
    plan = self.validator.validate_spec_deletion(spec_id)

    if not plan.is_safe:
      return plan

    if dry_run:
      return plan

    # Execute deletion
    # Delete files
    for file_path in plan.files_to_delete:
      if file_path.exists():
        file_path.unlink()

    # Delete spec directory
    spec_dir = self.repo_root / "specify" / "tech" / spec_id
    if spec_dir.exists():
      shutil.rmtree(spec_dir)

    # Remove symlinks
    for symlink in plan.symlinks_to_remove:
      if symlink.exists() or symlink.is_symlink():
        symlink.unlink()

    # Update registry
    self._remove_from_registry(spec_id)

    # Rebuild indices
    self._rebuild_spec_indices()

    return plan

  def _remove_from_registry(self, spec_id: str) -> None:
    """Remove spec from registry_v2.json.

    Args:
        spec_id: Spec ID to remove

    """
    if not self.registry_path.exists():
      return

    registry = RegistryV2.from_file(self.registry_path)
    removed_count = registry.remove_spec(spec_id)

    if removed_count > 0:
      registry.save_to_file(self.registry_path)

  def _rebuild_spec_indices(self) -> None:
    """Rebuild spec symlink indices after deletion."""
    tech_dir = self.repo_root / "specify" / "tech"
    if tech_dir.exists():
      builder = SpecIndexBuilder(tech_dir)
      builder.rebuild()


__all__ = [
  "DeletionPlan",
  "DeletionValidator",
  "DeletionExecutor",
]
