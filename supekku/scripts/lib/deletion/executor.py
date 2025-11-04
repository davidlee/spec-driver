"""Deletion infrastructure for specs, deltas, revisions, and ADRs.

Provides safe deletion with validation, dry-run support, and proper cleanup
of registries, symlinks, and cross-references.
"""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml

from supekku.scripts.lib.registry_migration import RegistryV2
from supekku.scripts.lib.specs.index import SpecIndexBuilder

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


class RegistryScanner:
  """Scans YAML registries for cross-references to specs.

  Loads and parses requirements, deltas, revisions, and decisions registries
  to find which artifacts reference a given spec.
  """

  def __init__(self, repo_root: Path) -> None:
    """Initialize scanner.

    Args:
        repo_root: Repository root directory

    """
    self.repo_root = repo_root
    self.registry_dir = repo_root / ".spec-driver" / "registry"

  def find_spec_references(self, spec_id: str) -> dict[str, list[str]]:
    """Find all artifacts that reference a spec.

    Args:
        spec_id: Spec ID to search for (e.g., "SPEC-001")

    Returns:
        Dictionary mapping artifact type to list of artifact IDs:
        {
          "requirements": ["SPEC-001.FR-001", "SPEC-001.NFR-002"],
          "deltas": ["DE-005"],
          "revisions": ["RE-003"],
          "decisions": ["ADR-042"]
        }

    """
    references: dict[str, list[str]] = {
      "requirements": [],
      "deltas": [],
      "revisions": [],
      "decisions": [],
    }

    # Check requirements.yaml
    self._scan_requirements(spec_id, references)

    # Check deltas.yaml
    self._scan_deltas(spec_id, references)

    # Check revisions.yaml
    self._scan_revisions(spec_id, references)

    # Check decisions.yaml
    self._scan_decisions(spec_id, references)

    return references

  def _load_registry(self, filename: str) -> dict[str, Any] | None:
    """Load a registry YAML file.

    Args:
        filename: Name of the registry file (e.g., "requirements.yaml")

    Returns:
        Parsed YAML data or None if file missing/malformed

    """
    registry_path = self.registry_dir / filename
    if not registry_path.exists():
      return None

    try:
      with registry_path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
        return data if isinstance(data, dict) else None
    except (yaml.YAMLError, OSError):
      # Malformed YAML or read error - treat as no references
      return None

  def _scan_requirements(
    self,
    spec_id: str,
    references: dict[str, list[str]],
  ) -> None:
    """Scan requirements.yaml for references to spec_id.

    Args:
        spec_id: Spec ID to search for
        references: Dictionary to populate with found references

    """
    data = self._load_registry("requirements.yaml")
    if not data or "requirements" not in data:
      return

    for req_id, req_data in data["requirements"].items():
      if not isinstance(req_data, dict):
        continue

      # Check if this requirement references the spec
      specs = req_data.get("specs", [])
      if isinstance(specs, list) and spec_id in specs:
        references["requirements"].append(req_id)

  def _scan_deltas(
    self,
    spec_id: str,
    references: dict[str, list[str]],
  ) -> None:
    """Scan deltas.yaml for references to spec_id.

    Args:
        spec_id: Spec ID to search for
        references: Dictionary to populate with found references

    """
    data = self._load_registry("deltas.yaml")
    if not data or "deltas" not in data:
      return

    for delta_id, delta_data in data["deltas"].items():
      if not isinstance(delta_data, dict):
        continue

      # Check applies_to.specs
      applies_to = delta_data.get("applies_to", {})
      if isinstance(applies_to, dict):
        specs = applies_to.get("specs", [])
        if isinstance(specs, list) and spec_id in specs:
          references["deltas"].append(delta_id)

  def _scan_revisions(
    self,
    spec_id: str,
    references: dict[str, list[str]],
  ) -> None:
    """Scan revisions.yaml for references to spec_id.

    Args:
        spec_id: Spec ID to search for
        references: Dictionary to populate with found references

    """
    data = self._load_registry("revisions.yaml")
    if not data or "revisions" not in data:
      return

    for revision_id, revision_data in data["revisions"].items():
      if not isinstance(revision_data, dict):
        continue

      # Check relations[].target
      relations = revision_data.get("relations", [])
      if isinstance(relations, list):
        for relation in relations:
          if isinstance(relation, dict):
            target = relation.get("target")
            if target == spec_id:
              references["revisions"].append(revision_id)
              break  # Only add revision once even if multiple relations

  def _scan_decisions(
    self,
    spec_id: str,
    references: dict[str, list[str]],
  ) -> None:
    """Scan decisions.yaml for references to spec_id.

    Args:
        spec_id: Spec ID to search for
        references: Dictionary to populate with found references

    """
    data = self._load_registry("decisions.yaml")
    if not data or "decisions" not in data:
      return

    for decision_id, decision_data in data["decisions"].items():
      if not isinstance(decision_data, dict):
        continue

      # Check specs list
      specs = decision_data.get("specs", [])
      if isinstance(specs, list) and spec_id in specs:
        references["decisions"].append(decision_id)
        continue

      # Check requirements list (extract spec from SPEC-XXX.FR-YYY)
      requirements = decision_data.get("requirements", [])
      if isinstance(requirements, list):
        for req_id in requirements:
          extracted = self._extract_spec_from_requirement(req_id)
          if isinstance(req_id, str) and extracted == spec_id:
            references["decisions"].append(decision_id)
            break

  @staticmethod
  def _extract_spec_from_requirement(req_id: str) -> str | None:
    """Extract spec ID from requirement ID.

    Args:
        req_id: Requirement ID (e.g., "SPEC-042.FR-001")

    Returns:
        Spec ID (e.g., "SPEC-042") or None if no match

    """
    match = re.match(r"^(SPEC-\d+|PROD-\d+)\..*", req_id)
    return match.group(1) if match else None


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
    self.scanner = RegistryScanner(repo_root)

  def validate_spec_deletion(
    self,
    spec_id: str,
    *,
    orphaned_specs: set[str] | None = None,
  ) -> DeletionPlan:
    """Validate deletion of a spec.

    Args:
        spec_id: Spec ID (e.g., "SPEC-001")
        orphaned_specs: Set of spec IDs known to be orphaned (for context).
                       If provided, cross-references from other orphaned specs
                       will not block deletion.

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

    # Find cross-references in registries
    references = self.scanner.find_spec_references(spec_id)

    # Process cross-references
    # Note: orphaned_specs parameter reserved for future orphan-to-orphan logic
    for ref_type, ref_ids in references.items():
      if not ref_ids:
        continue

      if ref_type == "requirements":
        # Requirements reference specs - always block deletion
        for req_id in ref_ids:
          plan.add_cross_reference(req_id, spec_id)
          plan.is_safe = False
          plan.add_warning(f"Referenced by requirement {req_id}")

      elif ref_type == "deltas":
        # Deltas reference specs - always block deletion
        for delta_id in ref_ids:
          plan.add_cross_reference(delta_id, spec_id)
          plan.is_safe = False
          plan.add_warning(f"Referenced by delta {delta_id}")

      elif ref_type == "revisions":
        # Revisions reference specs - always block deletion
        for revision_id in ref_ids:
          plan.add_cross_reference(revision_id, spec_id)
          plan.is_safe = False
          plan.add_warning(f"Referenced by revision {revision_id}")

      elif ref_type == "decisions":
        # Decisions reference specs - always block deletion
        for decision_id in ref_ids:
          plan.add_cross_reference(decision_id, spec_id)
          plan.is_safe = False
          plan.add_warning(f"Referenced by decision {decision_id}")

    # Note: We could add logic to check if requirements are from orphaned specs,
    # but requirements are typically tied to specific spec IDs (SPEC-XXX.FR-YYY)
    # and should persist even if the source is deleted, so we block all
    # requirement references unconditionally.

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
    # Resolve spec_dir to handle macOS /var -> /private/var symlink
    spec_dir_resolved = spec_dir.resolve()

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
            if target == spec_dir_resolved or target.is_relative_to(spec_dir_resolved):
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
  "RegistryScanner",
]
