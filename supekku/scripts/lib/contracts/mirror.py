"""Contract mirror tree builder.

Builds a .contracts/ symlink tree at the repo root that mirrors source paths
to generated contract artefacts, enabling intuitive navigation and search.
"""

from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass
from pathlib import Path

__all__ = ["ContractMirrorTreeBuilder", "MirrorEntry"]

# Python contract variants map 1:1 to canonical view names
PYTHON_KNOWN_VARIANTS = frozenset({"public", "all", "tests"})

# Go/Zig contract filename -> canonical view
GO_ZIG_CONTRACT_MAP: dict[str, str] = {
  "interfaces.md": "public",
  "internals.md": "internal",
}

# TypeScript contract filename -> canonical view
TS_CONTRACT_MAP: dict[str, str] = {
  "api.md": "public",
  "internal.md": "internal",
}

# Alias symlinks at .contracts/ level
VIEW_ALIASES: dict[str, str] = {
  "api": "public",
  "implementation": "all",
}


@dataclass
class MirrorEntry:  # pylint: disable=too-few-public-methods
  """A single mirror symlink mapping."""

  view: str  # canonical view: public, internal, all, tests
  mirror_path: str  # path under .contracts/<view>/
  contract_path: Path  # absolute path to contract artefact
  spec_id: str  # for conflict resolution


# --- Pure mapping functions ---


def python_module_to_path(dotted_name: str) -> str:
  """Convert dotted module name to file path: 'foo.bar' -> 'foo/bar.py'."""
  return dotted_name.replace(".", "/") + ".py"


def extract_python_variant(filename: str) -> str | None:
  """Extract variant from Python contract filename suffix.

  Returns None if the suffix isn't a known variant.
  """
  stem = filename.removesuffix(".md")
  if not stem:
    return None
  parts = stem.rsplit("-", 1)
  if len(parts) == 2 and parts[1] in PYTHON_KNOWN_VARIANTS:
    return parts[1]
  return None


def read_python_module_name(contract_path: Path) -> str | None:
  """Read the dotted module name from a Python contract's first header."""
  try:
    with open(contract_path, encoding="utf-8") as f:
      first_line = f.readline().strip()
    if first_line.startswith("# "):
      return first_line[2:].strip()
  except (OSError, UnicodeDecodeError):
    pass
  return None


def python_mirror_entries(
  spec_id: str, contracts_dir: Path,
) -> tuple[list[MirrorEntry], list[str]]:
  """Produce mirror entries for all Python contracts in a SPEC bundle."""
  entries: list[MirrorEntry] = []
  warnings: list[str] = []

  if not contracts_dir.is_dir():
    return entries, warnings

  for contract_file in sorted(contracts_dir.iterdir()):
    if not contract_file.name.endswith(".md"):
      continue

    variant = extract_python_variant(contract_file.name)
    if variant is None:
      continue

    module_name = read_python_module_name(contract_file)
    if module_name is None:
      warnings.append(f"Could not read module name from {contract_file}")
      continue

    entries.append(MirrorEntry(
      view=variant,
      mirror_path=f"{python_module_to_path(module_name)}.md",
      contract_path=contract_file,
      spec_id=spec_id,
    ))

  return entries, warnings


def zig_mirror_entries(
  spec_id: str, contracts_dir: Path, identifier: str,
) -> tuple[list[MirrorEntry], list[str]]:
  """Produce mirror entries for Zig contracts."""
  entries: list[MirrorEntry] = []
  warnings: list[str] = []

  for contract_name, view in GO_ZIG_CONTRACT_MAP.items():
    contract_path = contracts_dir / contract_name
    if not contract_path.exists():
      continue

    if identifier == ".":
      mirror_path = f"__root__/{contract_name}"
    else:
      mirror_path = f"{identifier}.md"

    entries.append(MirrorEntry(
      view=view,
      mirror_path=mirror_path,
      contract_path=contract_path,
      spec_id=spec_id,
    ))

  return entries, warnings


def go_mirror_entries(
  spec_id: str, contracts_dir: Path, identifier: str,
) -> tuple[list[MirrorEntry], list[str]]:
  """Produce mirror entries for Go contracts."""
  entries: list[MirrorEntry] = []
  warnings: list[str] = []

  for contract_name, view in GO_ZIG_CONTRACT_MAP.items():
    contract_path = contracts_dir / contract_name
    if not contract_path.exists():
      continue

    entries.append(MirrorEntry(
      view=view,
      mirror_path=f"{identifier}/{contract_name}",
      contract_path=contract_path,
      spec_id=spec_id,
    ))

  return entries, warnings


def ts_mirror_entries(
  spec_id: str, contracts_dir: Path, identifier: str,
) -> tuple[list[MirrorEntry], list[str]]:
  """Produce mirror entries for TypeScript contracts."""
  entries: list[MirrorEntry] = []
  warnings: list[str] = []

  for contract_name, view in TS_CONTRACT_MAP.items():
    contract_path = contracts_dir / contract_name
    if not contract_path.exists():
      continue

    entries.append(MirrorEntry(
      view=view,
      mirror_path=f"{identifier}.md",
      contract_path=contract_path,
      spec_id=spec_id,
    ))

  return entries, warnings


class ContractMirrorTreeBuilder:  # pylint: disable=too-few-public-methods
  """Builds a .contracts/ symlink tree mirroring source paths to contracts."""

  def __init__(self, repo_root: Path, tech_dir: Path | None = None) -> None:
    self.repo_root = repo_root
    self.tech_dir = tech_dir or repo_root / "specify" / "tech"
    self.mirror_dir = repo_root / ".contracts"
    self.registry_path = self.tech_dir / "registry_v2.json"

  def rebuild(self) -> list[str]:
    """Rebuild the .contracts/ symlink tree. Returns warnings."""
    warnings: list[str] = []

    # Clean and recreate
    if self.mirror_dir.exists():
      shutil.rmtree(self.mirror_dir)
    self.mirror_dir.mkdir()

    # Load registry
    registry = self._load_registry()
    if registry is None:
      warnings.append(f"Registry not found: {self.registry_path}")
      return warnings

    # Collect all mirror entries
    entries = self._collect_entries(registry, warnings)

    # Resolve conflicts
    resolved = self._resolve_conflicts(entries, warnings)

    # Create symlinks
    self._create_symlinks(resolved)

    # Create aliases
    self._create_aliases()

    return warnings

  def _load_registry(self) -> dict | None:
    """Load registry_v2.json."""
    if not self.registry_path.exists():
      return None
    try:
      with open(self.registry_path, encoding="utf-8") as f:
        return json.load(f)
    except (json.JSONDecodeError, OSError):
      return None

  def _collect_entries(
    self, registry: dict, warnings: list[str],
  ) -> list[MirrorEntry]:
    """Collect mirror entries from all registered source units."""
    entries: list[MirrorEntry] = []
    languages = registry.get("languages", {})

    for language, identifiers in languages.items():
      seen_specs: set[str] = set()

      for identifier, spec_id in identifiers.items():
        contracts_dir = self.tech_dir / spec_id / "contracts"

        if language == "python":
          # Python scans full contracts dir; deduplicate by spec
          if spec_id in seen_specs:
            continue
          seen_specs.add(spec_id)
          new_entries, new_warnings = python_mirror_entries(
            spec_id, contracts_dir,
          )
        elif language == "zig":
          new_entries, new_warnings = zig_mirror_entries(
            spec_id, contracts_dir, identifier,
          )
        elif language == "go":
          new_entries, new_warnings = go_mirror_entries(
            spec_id, contracts_dir, identifier,
          )
        elif language in ("typescript", "javascript"):
          new_entries, new_warnings = ts_mirror_entries(
            spec_id, contracts_dir, identifier,
          )
        else:
          continue

        entries.extend(new_entries)
        warnings.extend(new_warnings)

    return entries

  def _resolve_conflicts(
    self, entries: list[MirrorEntry], warnings: list[str],
  ) -> list[MirrorEntry]:
    """Resolve conflicting mirror destinations. Lowest SPEC ID wins."""
    groups: dict[tuple[str, str], list[MirrorEntry]] = {}
    for entry in entries:
      key = (entry.view, entry.mirror_path)
      groups.setdefault(key, []).append(entry)

    resolved: list[MirrorEntry] = []
    for group in groups.values():
      if len(group) > 1:
        group.sort(key=lambda e: e.spec_id)
        winner = group[0]
        losers = [e.spec_id for e in group[1:] if e.spec_id != winner.spec_id]
        if losers:
          warnings.append(
            f"Conflict at .contracts/{winner.view}/{winner.mirror_path}"
            f" — {winner.spec_id} wins over {', '.join(losers)}"
          )
        resolved.append(winner)
      else:
        resolved.append(group[0])

    return resolved

  def _create_symlinks(self, entries: list[MirrorEntry]) -> None:
    """Create symlinks for all resolved mirror entries."""
    for entry in entries:
      link_path = self.mirror_dir / entry.view / entry.mirror_path
      link_path.parent.mkdir(parents=True, exist_ok=True)

      # Compute relative symlink target
      target = Path(os.path.relpath(entry.contract_path, link_path.parent))

      if link_path.exists() or link_path.is_symlink():
        link_path.unlink()
      link_path.symlink_to(target)

  def _create_aliases(self) -> None:
    """Create alias symlinks (e.g. api -> public)."""
    for alias, target in VIEW_ALIASES.items():
      alias_path = self.mirror_dir / alias
      target_dir = self.mirror_dir / target
      if target_dir.exists():
        if alias_path.exists() or alias_path.is_symlink():
          alias_path.unlink()
        alias_path.symlink_to(target)
