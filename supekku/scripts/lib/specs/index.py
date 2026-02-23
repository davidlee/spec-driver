"""Specification index management for creating symlink-based indices."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class SpecIndexEntry:
  """Data class representing a specification index entry."""

  spec_id: str
  slug: str
  packages: list[str]
  spec_path: Path
  tests_path: Path | None = None


class SpecIndexBuilder:
  """Builds and manages specification indices using symlinks."""

  def __init__(self, base_dir: Path) -> None:
    self.base_dir = base_dir
    self.slug_dir = base_dir / "by-slug"
    self.package_dir = base_dir / "by-package"
    self.language_dir = base_dir / "by-language"
    self.category_dir = base_dir / "by-category"
    self.c4_level_dir = base_dir / "by-c4-level"

  def rebuild(self) -> None:
    """Rebuild the specification index by creating symlinks."""
    if self.slug_dir.exists():
      for entry in self.slug_dir.iterdir():
        if entry.is_symlink() or entry.is_file():
          entry.unlink()
    else:
      self.slug_dir.mkdir()

    if self.package_dir.exists():
      for entry in self.package_dir.rglob("*"):
        if entry.is_symlink() or entry.is_file():
          entry.unlink()
      for entry in sorted(
        {p.parent for p in self.package_dir.glob("**/*") if p.is_dir()},
        reverse=True,
      ):
        if entry != self.package_dir and not any(entry.iterdir()):
          entry.rmdir()
    else:
      self.package_dir.mkdir()

    # Clean up by-language directory
    if self.language_dir.exists():
      for entry in self.language_dir.rglob("*"):
        if entry.is_symlink() or entry.is_file():
          entry.unlink()
      for entry in sorted(
        {p.parent for p in self.language_dir.glob("**/*") if p.is_dir()},
        reverse=True,
      ):
        if entry != self.language_dir and not any(entry.iterdir()):
          entry.rmdir()
    else:
      self.language_dir.mkdir()

    # Clean up taxonomy view directories
    self._clean_flat_view_dir(self.category_dir)
    self._clean_flat_view_dir(self.c4_level_dir)

    for entry in sorted(self.base_dir.glob("SPEC-*/")):
      spec_file = entry / f"{entry.name}.md"
      if not spec_file.exists():
        continue
      frontmatter = self._read_frontmatter(spec_file)
      slug = frontmatter.get("slug")
      if slug:
        target = self.slug_dir / slug
        if target.exists() or target.is_symlink():
          target.unlink()
        target.symlink_to(Path("..") / entry.name)

      packages = frontmatter.get("packages") or []
      for package in packages:
        pkg_path = self.package_dir / Path(package) / "spec"
        pkg_path.parent.mkdir(parents=True, exist_ok=True)
        if pkg_path.exists() or pkg_path.is_symlink():
          pkg_path.unlink()
        depth = len(Path(package).parts) + 1  # +1 for 'spec'
        rel = Path("..")
        for _ in range(depth - 1):
          rel /= ".."
        rel /= entry.name
        pkg_path.symlink_to(rel)

      # Create by-language symlinks for sources
      sources = frontmatter.get("sources") or []
      for source in sources:
        language = source.get("language")
        identifier = source.get("identifier")

        if language and identifier:
          # Create language-specific symlink path
          lang_path = self.language_dir / language / identifier / "spec"
          lang_path.parent.mkdir(parents=True, exist_ok=True)

          if lang_path.exists() or lang_path.is_symlink():
            lang_path.unlink()

          # Calculate relative path depth
          # by-language/go/cmd/spec -> ../../../SPEC-003
          # From spec location, need to go up:
          # spec(1) + identifier_parts + language(1) = 3 levels up
          depth = 1 + len(Path(identifier).parts) + 1  # spec + identifier + language
          rel = Path("..")
          for _ in range(depth - 1):
            rel /= ".."
          rel /= entry.name
          lang_path.symlink_to(rel)

      # Create taxonomy view symlinks
      # by-category/{unit,assembly,unknown}/SPEC-XXX → ../../SPEC-XXX
      cat = frontmatter.get("category") or "unknown"
      self._create_flat_view_link(self.category_dir, cat, entry.name)

      # by-c4-level/{code,component,...,unknown}/SPEC-XXX → ../../SPEC-XXX
      level = frontmatter.get("c4_level") or "unknown"
      self._create_flat_view_link(self.c4_level_dir, level, entry.name)

    # Create convenience alias directory symlinks
    self._ensure_alias(self.base_dir / "assemblies", Path("by-category/assembly"))
    self._ensure_alias(self.base_dir / "units", Path("by-category/unit"))
    self._ensure_alias(self.base_dir / "c4", Path("by-c4-level"))

  @staticmethod
  def _ensure_alias(link: Path, target: Path) -> None:
    """Create or replace a directory alias symlink."""
    if link.is_symlink() or link.exists():
      link.unlink()
    link.symlink_to(target)

  @staticmethod
  def _clean_flat_view_dir(view_dir: Path) -> None:
    """Remove all symlinks and empty subdirectories in a flat view."""
    if view_dir.exists():
      for entry in view_dir.rglob("*"):
        if entry.is_symlink() or entry.is_file():
          entry.unlink()
      for entry in sorted(
        (p for p in view_dir.iterdir() if p.is_dir()),
        reverse=True,
      ):
        if not any(entry.iterdir()):
          entry.rmdir()
    else:
      view_dir.mkdir()

  @staticmethod
  def _create_flat_view_link(
    view_dir: Path,
    bucket: str,
    spec_name: str,
  ) -> None:
    """Create a symlink: view_dir/bucket/spec_name → ../../spec_name."""
    bucket_dir = view_dir / bucket
    bucket_dir.mkdir(parents=True, exist_ok=True)
    link = bucket_dir / spec_name
    if link.exists() or link.is_symlink():
      link.unlink()
    link.symlink_to(Path("..") / ".." / spec_name)

  def _read_frontmatter(self, path: Path) -> dict:
    """Extract YAML frontmatter from a markdown file."""
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---"):
      return {}
    parts = content.split("---", 2)
    if len(parts) < 3:
      return {}
    try:
      return yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError as e:
      # Warn about malformed YAML and return empty dict
      print(f"Warning: Malformed YAML frontmatter in {path}: {e}")
      return {}


__all__ = ["SpecIndexBuilder", "SpecIndexEntry"]
