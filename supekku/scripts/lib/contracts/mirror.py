"""Contract mirror tree builder.

Builds a .contracts/ symlink tree at the repo root that mirrors source paths
to generated contract artefacts, enabling intuitive navigation and search.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

__all__ = [
  "ContractMirrorTreeBuilder",
  "MirrorEntry",
  "resolve_go_variant_outputs",
  "resolve_ts_variant_outputs",
  "resolve_zig_variant_outputs",
]

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


# --- Pre-generation path resolvers ---
# Compute per-variant canonical output file paths *before* generation.
# Same mapping logic as the post-hoc mirror entry functions, applied upfront.


def resolve_go_variant_outputs(
  identifier: str,
  contracts_root: Path,
) -> dict[str, Path]:
  """Compute per-variant canonical output paths for Go.

  Go preserves adapter filenames (interfaces.md, internals.md).
  Canonical path: .contracts/<view>/<identifier>/<contract_name>
  """
  return {
    "public": contracts_root / "public" / identifier / "interfaces.md",
    "internal": contracts_root / "internal" / identifier / "internals.md",
  }


def resolve_zig_variant_outputs(
  identifier: str,
  contracts_root: Path,
) -> dict[str, Path]:
  """Compute per-variant canonical output paths for Zig.

  Zig discards adapter filenames; canonical leaf is {identifier}.md.
  Root package '.' maps to __root__/ with original filenames preserved.
  """
  if identifier == ".":
    return {
      "public": contracts_root / "public" / "__root__" / "interfaces.md",
      "internal": contracts_root / "internal" / "__root__" / "internals.md",
    }
  return {
    "public": contracts_root / "public" / f"{identifier}.md",
    "internal": contracts_root / "internal" / f"{identifier}.md",
  }


def resolve_ts_variant_outputs(
  identifier: str,
  contracts_root: Path,
) -> dict[str, Path]:
  """Compute per-variant canonical output paths for TypeScript.

  TS discards adapter filenames; canonical leaf is {identifier}.md.
  Keys use the adapter's own variant names (api, internal).
  """
  return {
    "api": contracts_root / "public" / f"{identifier}.md",
    "internal": contracts_root / "internal" / f"{identifier}.md",
  }


def python_staging_dir(
  identifier: str,
  contracts_root: Path,
) -> Path:
  """Compute the Python staging directory path.

  Staging key: python/<identifier-slug> (not spec-id).
  """
  slug = identifier.replace("/", "-").replace(".", "-")
  return contracts_root / ".staging" / "python" / slug


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
  spec_id: str,
  contracts_dir: Path,
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

    entries.append(
      MirrorEntry(
        view=variant,
        mirror_path=f"{python_module_to_path(module_name)}.md",
        contract_path=contract_file,
        spec_id=spec_id,
      )
    )

  return entries, warnings


def zig_mirror_entries(
  spec_id: str,
  contracts_dir: Path,
  identifier: str,
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

    entries.append(
      MirrorEntry(
        view=view,
        mirror_path=mirror_path,
        contract_path=contract_path,
        spec_id=spec_id,
      )
    )

  return entries, warnings


def go_mirror_entries(
  spec_id: str,
  contracts_dir: Path,
  identifier: str,
) -> tuple[list[MirrorEntry], list[str]]:
  """Produce mirror entries for Go contracts."""
  entries: list[MirrorEntry] = []
  warnings: list[str] = []

  for contract_name, view in GO_ZIG_CONTRACT_MAP.items():
    contract_path = contracts_dir / contract_name
    if not contract_path.exists():
      continue

    entries.append(
      MirrorEntry(
        view=view,
        mirror_path=f"{identifier}/{contract_name}",
        contract_path=contract_path,
        spec_id=spec_id,
      )
    )

  return entries, warnings


def ts_mirror_entries(
  spec_id: str,
  contracts_dir: Path,
  identifier: str,
) -> tuple[list[MirrorEntry], list[str]]:
  """Produce mirror entries for TypeScript contracts."""
  entries: list[MirrorEntry] = []
  warnings: list[str] = []

  for contract_name, view in TS_CONTRACT_MAP.items():
    contract_path = contracts_dir / contract_name
    if not contract_path.exists():
      continue

    entries.append(
      MirrorEntry(
        view=view,
        mirror_path=f"{identifier}.md",
        contract_path=contract_path,
        spec_id=spec_id,
      )
    )

  return entries, warnings


class ContractMirrorTreeBuilder:  # pylint: disable=too-few-public-methods
  """Builds a .contracts/ symlink tree mirroring source paths to contracts."""

  def __init__(self, repo_root: Path, tech_dir: Path | None = None) -> None:
    self.repo_root = repo_root
    self.tech_dir = tech_dir or repo_root / "specify" / "tech"
    self.mirror_dir = repo_root / ".contracts"
    self.registry_path = self.tech_dir / "registry_v2.json"

  def rebuild(self) -> list[str]:
    """Rebuild compat symlinks: SPEC-*/contracts/ → .contracts/.

    Canonical contract files live in .contracts/<view>/<path>.
    For each registered spec, create compat symlinks from
    SPEC-*/contracts/<view>/<path> pointing into .contracts/.
    """
    warnings: list[str] = []

    registry = self._load_registry()
    if registry is None:
      warnings.append(f"Registry not found: {self.registry_path}")
      return warnings

    languages = registry.get("languages", {})
    contracts_root = self.mirror_dir  # .contracts/

    for language, identifiers in languages.items():
      for identifier, entry in identifiers.items():
        spec_id = entry if isinstance(entry, str) else entry.get("spec_id")
        if not spec_id:
          continue

        # Compute expected canonical paths for this source unit
        canonical_paths = self._canonical_paths_for(
          language,
          identifier,
          contracts_root,
        )

        # Create compat symlinks from SPEC-*/contracts/ → .contracts/
        spec_contracts = self.tech_dir / spec_id / "contracts"
        for canonical in canonical_paths:
          if not canonical.exists():
            continue

          # Relative path under .contracts/ (e.g. public/internal/foo/interfaces.md)
          rel = canonical.relative_to(contracts_root)
          link_path = spec_contracts / rel
          link_path.parent.mkdir(parents=True, exist_ok=True)

          target = Path(os.path.relpath(canonical, link_path.parent))
          if link_path.is_symlink() or link_path.exists():
            if link_path.is_symlink():
              link_path.unlink()
            else:
              warnings.append(
                f"Replacing non-symlink {link_path} with compat symlink",
              )
              link_path.unlink()
          link_path.symlink_to(target)

    # Create view aliases inside .contracts/ (api → public, etc.)
    self._create_aliases()

    return warnings

  def _canonical_paths_for(
    self,
    language: str,
    identifier: str,
    contracts_root: Path,
  ) -> list[Path]:
    """Return expected canonical file paths for a source unit."""
    if language == "go":
      outputs = resolve_go_variant_outputs(identifier, contracts_root)
      return list(outputs.values())
    if language == "zig":
      outputs = resolve_zig_variant_outputs(identifier, contracts_root)
      return list(outputs.values())
    if language in ("typescript", "javascript"):
      outputs = resolve_ts_variant_outputs(identifier, contracts_root)
      return list(outputs.values())
    if language == "python":
      # Python files are distributed; scan for matching files
      return self._scan_python_contracts(identifier, contracts_root)
    return []

  @staticmethod
  def _scan_python_contracts(
    identifier: str,
    contracts_root: Path,
  ) -> list[Path]:
    """Find canonical Python contract files by scanning .contracts/ views."""
    results: list[Path] = []
    for view_dir in contracts_root.iterdir():
      if not view_dir.is_dir() or view_dir.is_symlink():
        continue
      # Python contracts mirror the module path
      module_dir = view_dir / identifier
      if module_dir.is_dir():
        results.extend(module_dir.rglob("*.md"))
      # Also check for single-file modules
      module_file = view_dir / f"{identifier}.md"
      if module_file.is_file():
        results.append(module_file)
    return results

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
    self,
    registry: dict,
    warnings: list[str],
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
            spec_id,
            contracts_dir,
          )
        elif language == "zig":
          new_entries, new_warnings = zig_mirror_entries(
            spec_id,
            contracts_dir,
            identifier,
          )
        elif language == "go":
          new_entries, new_warnings = go_mirror_entries(
            spec_id,
            contracts_dir,
            identifier,
          )
        elif language in ("typescript", "javascript"):
          new_entries, new_warnings = ts_mirror_entries(
            spec_id,
            contracts_dir,
            identifier,
          )
        else:
          continue

        entries.extend(new_entries)
        warnings.extend(new_warnings)

    return entries

  def _resolve_conflicts(
    self,
    entries: list[MirrorEntry],
    warnings: list[str],
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
