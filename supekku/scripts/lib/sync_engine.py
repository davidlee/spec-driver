"""Synchronization engine for managing spec and change relationships."""

from __future__ import annotations

import json
import subprocess
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from shutil import which
from subprocess import CompletedProcess

from .spec_index import SpecIndexBuilder
from .spec_utils import (
  append_unique,
  dump_markdown_file,
  ensure_list_entry,
  load_markdown_file,
)

LogFn = Callable[[str], None]
RunFn = Callable[[list[str]], CompletedProcess[str]]
DocGeneratorFn = Callable[[Path, str, bool, bool], None]

CONTRACTS_DIRNAME = "contracts"
PUBLIC_DOC = "interfaces.md"
PRIVATE_DOC = "internals.md"
SKIP_KEYWORDS = {"mock", "mocks", "generated"}


def default_log(message: str) -> None:
  """Default logging function that prints to stdout."""


def default_run(cmd: list[str]) -> CompletedProcess[str]:
  """Default command runner using subprocess."""
  return subprocess.run(cmd, check=True, capture_output=True, text=True)


def default_gomarkdoc_available() -> bool:
  """Check if gomarkdoc command is available in PATH."""
  return which("gomarkdoc") is not None


def default_generate_docs(
  spec_dir: Path,
  module_pkg: str,
  include_unexported: bool,
  check: bool,
) -> None:
  """Generate documentation using gomarkdoc."""
  contracts_dir = spec_dir / CONTRACTS_DIRNAME
  output = contracts_dir / (PRIVATE_DOC if include_unexported else PUBLIC_DOC)

  if check:
    # In check mode, only proceed if the output file already exists
    if not output.exists():
      return  # Skip gracefully - nothing to check
  else:
    # In generate mode, ensure contracts directory exists
    contracts_dir.mkdir(parents=True, exist_ok=True)

  cmd = [
    "gomarkdoc",
    "--format",
    "github",
  ]
  if check:
    cmd.append("--check")
  cmd.extend(
    [
      "--output",
      str(output),
    ],
  )
  if include_unexported:
    cmd.append("--include-unexported")
  cmd.append(module_pkg)
  subprocess.run(cmd, check=True)


class GomarkdocNotAvailableError(RuntimeError):
  """Raised when gomarkdoc is required but not available."""


@dataclass
class SyncOptions:
  """Configuration options for specification synchronization."""

  packages: Sequence[str] = field(default_factory=list)
  existing: bool = False
  check: bool = False
  allow_missing_go: bool = False


@dataclass
class SkippedPackage:
  """Information about a package that was skipped during sync."""

  package: str
  reason: str


@dataclass
class SyncResult:
  """Results from a specification synchronization operation."""

  processed_packages: list[str]
  created_specs: dict[str, str]
  skipped_packages: list[SkippedPackage]
  warnings: list[str]


class TechSpecSyncEngine:
  """Engine for synchronizing technical specifications with source code."""

  def __init__(
    self,
    *,
    root: Path,
    tech_dir: Path,
    registry_path: Path,
    log: LogFn = default_log,
    run_cmd: RunFn = default_run,
    gomarkdoc_available: Callable[[], bool] = default_gomarkdoc_available,
    generate_docs: DocGeneratorFn = default_generate_docs,
  ) -> None:
    """Initialize the TechSpecSyncEngine with required dependencies."""
    self.root = root
    self.tech_dir = tech_dir
    self.registry_path = registry_path
    self.log = log
    self.run_cmd = run_cmd
    self._gomarkdoc_available = gomarkdoc_available
    self.generate_docs = generate_docs

  # Public API -----------------------------------------------------
  def synchronize(self, options: SyncOptions) -> SyncResult:
    """Synchronize specifications with source code packages."""
    module = self.go_module_name()
    registry = self.load_registry()

    package_targets = self._resolve_package_targets(options, module, registry)
    package_targets = [pkg.strip() for pkg in package_targets if pkg.strip()]
    package_targets = [pkg for pkg in package_targets if not self.should_skip(pkg)]

    existing_ids = self.spec_ids_from_disk()
    next_id_value = self.next_spec_id(existing_ids + list(registry.values()))
    next_num = int(next_id_value.split("-")[1])

    created_specs: dict[str, str] = {}
    processed: list[str] = []
    skipped: list[SkippedPackage] = []
    warnings: list[str] = []

    gomarkdoc_missing = not self._gomarkdoc_available()
    if gomarkdoc_missing and options.check:
      msg = "gomarkdoc required for --check mode"
      raise GomarkdocNotAvailableError(msg)
    if gomarkdoc_missing and not options.check:
      warnings.append("gomarkdoc not found; documentation generation skipped")
      self.log("warning: gomarkdoc not found; documentation generation skipped")

    for module_pkg in package_targets:
      rel_pkg = self.normalize_package(module_pkg, module)
      slug = self.determine_slug(rel_pkg)
      has_go_files = self.package_has_go_files(rel_pkg)
      skip_docs = False
      if not has_go_files:
        if options.allow_missing_go:
          skip_docs = True
          self.log(
            f"No Go files detected for {rel_pkg}; proceeding due to allow-missing-go",
          )
        else:
          reason = "no non-test Go files"
          skipped.append(SkippedPackage(rel_pkg, reason))
          self.log(f"Skipping {rel_pkg} ({reason})")
          continue

      if rel_pkg in registry:
        spec_id = registry[rel_pkg]
        try:
          spec_dir = self.resolve_spec_dir(spec_id)
        except FileNotFoundError:
          spec_dir = self.tech_dir / spec_id
      else:
        if options.check:
          reason = "no registered spec for check mode"
          skipped.append(SkippedPackage(rel_pkg, reason))
          self.log(f"Skipping {rel_pkg} ({reason})")
          continue
        spec_id = f"SPEC-{next_num:03d}"
        next_num += 1
        registry[rel_pkg] = spec_id
        spec_dir = self.tech_dir / spec_id
        created_specs[rel_pkg] = spec_id

      spec_file = self.ensure_spec_stub(
        spec_dir,
        spec_id,
        slug,
        rel_pkg,
        allow_create=not options.check,
      )
      if spec_file is None:
        skipped.append(SkippedPackage(rel_pkg, "missing spec stub"))
        continue

      self.ensure_package_list(spec_file, rel_pkg)

      if options.check:
        self.log(f"Checking docs for {rel_pkg} -> {spec_dir}")
        self.generate_docs(
          spec_dir,
          module_pkg,
          include_unexported=False,
          check=True,
        )
        self.generate_docs(
          spec_dir,
          module_pkg,
          include_unexported=True,
          check=True,
        )
      elif not gomarkdoc_missing and not skip_docs:
        self.log(f"Generating docs for {rel_pkg} -> {spec_dir}")
        self.generate_docs(
          spec_dir,
          module_pkg,
          include_unexported=False,
          check=False,
        )
        self.generate_docs(
          spec_dir,
          module_pkg,
          include_unexported=True,
          check=False,
        )
      elif skip_docs:
        self.log(
          f"Skipping documentation generation for {rel_pkg} (no Go files)",
        )

      processed.append(rel_pkg)

    self.save_registry(registry)

    # Rebuild symlink indices
    index_builder = SpecIndexBuilder(self.tech_dir)
    index_builder.rebuild()

    return SyncResult(
      processed_packages=processed,
      created_specs=created_specs,
      skipped_packages=skipped,
      warnings=warnings,
    )

  # Internal helpers ----------------------------------------------
  def go_module_name(self) -> str:
    """Get the Go module name from go.mod."""
    result = self.run_cmd(["go", "list", "-m"])
    return result.stdout.strip()

  def load_registry(self) -> dict[str, str]:
    """Load the package-to-spec registry from disk (v2 format only)."""
    if not self.registry_path.exists():
      return {}

    data = json.loads(self.registry_path.read_text())

    # Handle v2 format (nested under "languages" -> "go")
    if isinstance(data, dict) and data.get("version") == 2:
      languages = data.get("languages", {})
      return languages.get("go", {})

    # Legacy v1 format no longer supported - should be migrated
    msg = (
      f"Registry at {self.registry_path} is in v1 format. "
      "Please migrate to v2 using: just supekku::migrate-registry"
    )
    raise ValueError(
      msg,
    )

  def save_registry(self, registry: Mapping[str, str]) -> None:
    """Save the package-to-spec registry to disk (v2 format only)."""
    self.registry_path.parent.mkdir(parents=True, exist_ok=True)

    if self.registry_path.exists():
      existing_data = json.loads(self.registry_path.read_text())
      if isinstance(existing_data, dict) and existing_data.get("version") == 2:
        # Update Go packages in v2 registry
        existing_data["languages"] = existing_data.get("languages", {})
        existing_data["languages"]["go"] = dict(sorted(registry.items()))
        serialized = json.dumps(existing_data, indent=2) + "\n"
        self.registry_path.write_text(serialized)
        return

    # No v2 registry exists - create one
    from .registry_migration import RegistryV2  # noqa: PLC0415

    v2_registry = RegistryV2.create_empty()
    v2_registry.add_source_unit("go", "", "")  # Initialize go language
    v2_registry.languages["go"] = dict(sorted(registry.items()))
    v2_registry.save_to_file(self.registry_path)

  def next_spec_id(self, existing: Iterable[str]) -> str:
    """Generate the next available SPEC-### ID."""
    highest = 0
    for spec_id in existing:
      if isinstance(spec_id, str) and spec_id.startswith("SPEC-"):
        try:
          highest = max(highest, int(spec_id.split("-")[1]))
        except (ValueError, IndexError):
          continue
    return f"SPEC-{highest + 1:03d}"

  def spec_ids_from_disk(self) -> list[str]:
    """Get all existing spec IDs from filesystem."""
    ids: list[str] = []
    if not self.tech_dir.exists():
      return ids
    for entry in self.tech_dir.iterdir():
      if entry.is_dir() and entry.name.startswith("SPEC-"):
        parts = entry.name.split("-")
        if len(parts) >= 2:
          ids.append("-".join(parts[:2]))
    return ids

  def ensure_spec_stub(
    self,
    spec_dir: Path,
    spec_id: str,
    slug: str,
    package: str,
    *,
    allow_create: bool,
  ) -> Path | None:
    """Ensure a spec stub file exists, creating if allowed."""
    spec_file = spec_dir / f"{spec_id}.md"
    if spec_file.exists():
      return spec_file
    if not allow_create:
      self.log(f"Missing spec file for {spec_id} ({package}); skipping")
      return None
    spec_dir.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    frontmatter = {
      "id": spec_id,
      "slug": slug,
      "name": f"{package} Specification",
      "created": today,
      "updated": today,
      "status": "draft",
      "kind": "spec",
      "packages": [package],
      "responsibilities": [],
      "aliases": [],
    }
    body = (
      f"# {spec_id} – {package}\n\n"
      "> TODO: Populate responsibilities, behaviour, quality requirements, "
      "and testing strategy.\n"
    )
    dump_markdown_file(spec_file, frontmatter, body)
    return spec_file

  def ensure_package_list(self, spec_path: Path, package: str) -> None:
    """Ensure package is listed in spec frontmatter."""
    frontmatter, body = load_markdown_file(spec_path)
    packages = ensure_list_entry(frontmatter, "packages")
    if append_unique(packages, package):
      dump_markdown_file(spec_path, frontmatter, body)

  def package_has_go_files(self, rel_pkg: str) -> bool:
    """Check if package contains non-test Go files."""
    pkg_path = self.root / rel_pkg
    if not pkg_path.exists():
      return False
    for path in pkg_path.glob("*.go"):
      if path.name.endswith("_test.go"):
        continue
      return True
    return False

  def resolve_spec_dir(self, spec_id: str) -> Path:
    """Resolve the directory path for a given spec ID."""
    # First try canonical format (SPEC-###/)
    canonical_dir = self.tech_dir / spec_id
    if canonical_dir.is_dir():
      return canonical_dir

    # Fall back to old format (SPEC-###-slug/) for backward compatibility
    for entry in self.tech_dir.iterdir():
      if entry.is_dir() and entry.name.startswith(spec_id + "-"):
        return entry
    msg = f"Spec directory for {spec_id} not found"
    raise FileNotFoundError(msg)

  @staticmethod
  def normalize_package(pkg: str, module: str) -> str:
    """Convert absolute package path to relative package path."""
    if pkg.startswith(module + "/"):
      return pkg[len(module) + 1 :]
    return pkg

  @staticmethod
  def should_skip(pkg: str) -> bool:
    """Check if package should be skipped based on patterns."""
    if "/vendor/" in pkg:
      return True
    parts = pkg.split("/")
    for part in parts:
      lower = part.lower()
      if any(keyword in lower for keyword in SKIP_KEYWORDS):
        return True
    return bool(pkg.endswith("_test"))

  @staticmethod
  def determine_slug(package: str) -> str:
    """Generate a filesystem-safe slug from package path."""
    return package.replace("/", "-")

  # Private helper -------------------------------------------------
  def _resolve_package_targets(
    self,
    options: SyncOptions,
    module: str,
    registry: Mapping[str, str],
  ) -> list[str]:
    """Resolve which packages to process based on options."""
    if options.packages:
      targets: list[str] = []
      for item in options.packages:
        if item.startswith(module):
          targets.append(item)
        else:
          rel = item.strip("./")
          targets.append(f"{module}/{rel}")
      return targets
    if options.existing:
      return [f"{module}/{rel}" for rel in registry]
    result = self.run_cmd(["go", "list", "./..."])
    return result.stdout.splitlines()


__all__ = [
  "GomarkdocNotAvailableError",
  "SkippedPackage",
  "SyncOptions",
  "SyncResult",
  "TechSpecSyncEngine",
]
