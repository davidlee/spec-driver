"""Registry for managing and accessing specification files."""

from __future__ import annotations

import warnings
from typing import TYPE_CHECKING

from supekku.scripts.lib.core.paths import get_product_specs_dir, get_tech_specs_dir
from supekku.scripts.lib.core.repo import find_repo_root
from supekku.scripts.lib.core.spec_utils import load_validated_markdown_file

from .models import Spec

if TYPE_CHECKING:
  from collections.abc import Iterator
  from pathlib import Path


class SpecRegistry:
  """Discovery service for SPEC/PROD artefacts."""

  def __init__(self, root: Path | None = None) -> None:
    self.root = find_repo_root(root)
    self.tech_dir = get_tech_specs_dir(self.root)
    self.product_dir = get_product_specs_dir(self.root)
    self._specs: dict[str, Spec] = {}
    self.reload()

  def reload(self) -> None:
    """Reload all specs from the filesystem."""
    self._specs.clear()
    self._load_directory(
      self.tech_dir,
      expected_prefix="SPEC-",
      expected_kind="spec",
    )
    self._load_directory(
      self.product_dir,
      expected_prefix="PROD-",
      expected_kind="prod",
    )

  def find(self, spec_id: str) -> Spec | None:
    """Find a spec by its ID.

    Returns:
      Spec or None if not found.
    """
    return self._specs.get(spec_id)

  def get(self, spec_id: str) -> Spec | None:
    """Find a spec by ID. Deprecated — use find() instead."""
    warnings.warn(
      "SpecRegistry.get() is deprecated, use find() instead",
      DeprecationWarning,
      stacklevel=2,
    )
    return self.find(spec_id)

  def collect(self) -> dict[str, Spec]:
    """Return all specs as a dictionary keyed by ID.

    Returns:
      Copy of the internal spec dictionary.
    """
    return dict(self._specs)

  def iter(self, *, status: str | None = None) -> Iterator[Spec]:
    """Iterate over specs, optionally filtered by status.

    Args:
      status: If provided, yield only specs with this status.

    Yields:
      Spec instances.
    """
    for spec in self._specs.values():
      if status is None or spec.status == status:
        yield spec

  def filter(
    self,
    *,
    status: str | None = None,
    category: str | None = None,
    kind: str | None = None,
    tag: str | None = None,
  ) -> list[Spec]:
    """Filter specs by multiple criteria (AND logic).

    Args:
      status: Filter by status field.
      category: Filter by category (unit/assembly).
      kind: Filter by kind (spec/prod).
      tag: Filter by tag membership.

    Returns:
      List of matching Specs.
    """
    results = []
    for spec in self.iter(status=status):
      if category and spec.category != category:
        continue
      if kind and spec.kind != kind:
        continue
      if tag and tag not in spec.tags:
        continue
      results.append(spec)
    return results

  def all_specs(self) -> list[Spec]:
    """Return all loaded specs."""
    return list(self._specs.values())

  def find_by_package(self, package: str) -> list[Spec]:
    """Find all specs that reference the given package."""
    return [spec for spec in self._specs.values() if package in spec.packages]

  def find_by_informed_by(self, adr_id: str | None) -> list[Spec]:
    """Find specs informed by a specific ADR.

    Args:
      adr_id: The ADR ID to search for (e.g., "ADR-001").
              Returns empty list if None or empty string.

    Returns:
      List of Spec objects informed by the given ADR.
      Returns empty list if adr_id is None, empty, or no matches found.
    """
    if not adr_id:
      return []

    return [spec for spec in self._specs.values() if adr_id in spec.informed_by]

  # ------------------------------------------------------------------
  def _load_directory(
    self,
    directory: Path,
    *,
    expected_prefix: str,
    expected_kind: str,
  ) -> None:
    if not directory.exists():
      return
    for entry in directory.iterdir():
      if entry.is_dir():
        for candidate in self._iter_prefixed_files(entry, expected_prefix):
          self._register_spec(candidate, expected_kind)
      elif entry.is_file() and entry.name.startswith(expected_prefix):
        self._register_spec(entry, expected_kind)

  def _iter_prefixed_files(self, directory: Path, prefix: str) -> Iterator[Path]:
    """Iterate over files with the given prefix in a directory."""
    yield from directory.glob(f"{prefix}*.md")

  def _register_spec(self, path: Path, expected_kind: str) -> None:
    frontmatter, body = load_validated_markdown_file(path, kind=expected_kind)
    spec_id = frontmatter.id
    if not spec_id:
      return
    self._specs[spec_id] = Spec(
      id=spec_id,
      path=path,
      frontmatter=frontmatter,
      body=body,
    )


__all__ = ["SpecRegistry"]
