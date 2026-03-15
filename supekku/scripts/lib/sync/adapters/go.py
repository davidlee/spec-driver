"""Go language adapter for specification synchronization."""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path
from shutil import which
from typing import TYPE_CHECKING, ClassVar

from supekku.scripts.lib.core.go_utils import (
  get_go_module_name,
  is_go_available,
  normalize_go_package,
  run_go_list,
)
from supekku.scripts.lib.sync.models import (
  DocVariant,
  SourceDescriptor,
  SourceUnit,
)

from .base import LanguageAdapter

if TYPE_CHECKING:
  from collections.abc import Sequence


class GoToolchainNotAvailableError(RuntimeError):
  """Raised when Go toolchain is required but not available."""


class GomarkdocNotAvailableError(RuntimeError):
  """Raised when gomarkdoc is required but not available."""


class GoAdapter(LanguageAdapter):
  """Language adapter for Go packages using existing gomarkdoc workflow.

  Wraps the existing TechSpecSyncEngine logic to provide consistent interface
  with other language adapters while maintaining full backward compatibility.
  """

  language: ClassVar[str] = "go"

  @staticmethod
  def is_gomarkdoc_available() -> bool:
    """Check if gomarkdoc is available in PATH."""
    return which("gomarkdoc") is not None

  def discover_targets(
    self,
    repo_root: Path,
    requested: Sequence[str] | None = None,
  ) -> list[SourceUnit]:
    """Discover Go packages using `go list`.

    Args:
        repo_root: Root directory of the repository
        requested: Optional list of specific package paths to process

    Returns:
        List of SourceUnit objects for Go packages

    Raises:
        GoToolchainNotAvailableError: If Go toolchain is not available

    """
    # Check if Go toolchain is available
    if not is_go_available():
      raise GoToolchainNotAvailableError(
        "Go toolchain not found in PATH. Please install Go from https://go.dev/dl/ "
        "or ensure it is in your PATH."
      )

    module = get_go_module_name(repo_root)

    # Resolve package targets
    if requested:
      targets = []
      for item in requested:
        if item.startswith(module):
          targets.append(item)
        else:
          rel = item.strip("./")
          targets.append(f"{module}/{rel}")
    else:
      targets = run_go_list(repo_root)

    # Filter and normalize packages
    source_units = []
    skip_keywords = {"mock", "mocks", "generated"}

    for module_pkg in targets:
      # Skip vendor, test packages, and packages with skip keywords
      if "/vendor/" in module_pkg or module_pkg.endswith("_test"):
        continue

      parts = module_pkg.split("/")
      if any(keyword in part.lower() for part in parts for keyword in skip_keywords):
        continue

      rel_pkg = normalize_go_package(module_pkg, module)
      pkg_path = repo_root / rel_pkg

      # Only include if package directory exists
      if pkg_path.exists():
        source_units.append(
          SourceUnit(
            language=self.language,
            identifier=rel_pkg,
            root=repo_root,
          ),
        )

    return source_units

  def describe(self, unit: SourceUnit) -> SourceDescriptor:
    """Describe how a Go package should be processed.

    Args:
        unit: Go package source unit

    Returns:
        SourceDescriptor with Go-specific metadata

    """
    self._validate_unit_language(unit)

    # Generate slug parts from package path
    slug_parts = unit.identifier.split("/")

    # Default frontmatter for Go packages
    default_frontmatter = {
      "packages": [unit.identifier],
      "sources": [
        {
          "language": "go",
          "identifier": unit.identifier,
          "variants": [
            {
              "name": "public",
              "path": "contracts/interfaces.md",
            },
            {
              "name": "internal",
              "path": "contracts/internals.md",
            },
          ],
        },
      ],
    }

    # Document variants that will be generated
    variants = [
      DocVariant(
        name="public",
        path=Path("contracts/interfaces.md"),
        hash="",
        status="unchanged",
      ),
      DocVariant(
        name="internal",
        path=Path("contracts/internals.md"),
        hash="",
        status="unchanged",
      ),
    ]

    return SourceDescriptor(
      slug_parts=slug_parts,
      default_frontmatter=default_frontmatter,
      variants=variants,
    )

  def generate(
    self,
    unit: SourceUnit,
    *,
    variant_outputs: dict[str, Path],
    check: bool = False,
  ) -> list[DocVariant]:
    """Generate documentation for a Go package using gomarkdoc.

    Args:
        unit: Go package source unit
        variant_outputs: Per-variant canonical output file paths
        check: If True, only check if docs would change

    Returns:
        List of DocVariant objects with generation results

    Raises:
        GoToolchainNotAvailableError: If Go toolchain is not available
        GomarkdocNotAvailableError: If gomarkdoc is not available

    """
    self._validate_unit_language(unit)

    # Check if Go toolchain is available
    if not is_go_available():
      raise GoToolchainNotAvailableError(
        "Go toolchain not found in PATH. Please install Go from https://go.dev/dl/ "
        "or ensure it is in your PATH."
      )

    # Check if gomarkdoc is available
    if not self.is_gomarkdoc_available():
      raise GomarkdocNotAvailableError(
        "gomarkdoc not found in PATH. Please install it with: "
        "go install github.com/princjef/gomarkdoc/cmd/gomarkdoc@latest"
      )

    # gomarkdoc expects ./-prefixed relative paths, not import paths
    pkg_arg = f"./{unit.identifier}"

    # Output paths from caller-provided variant_outputs
    public_output = variant_outputs["public"]
    internal_output = variant_outputs["internal"]

    variants: list[DocVariant] = []

    # Generate public docs (interfaces)
    variants.append(
      self._generate_variant(
        name="public",
        output_path=public_output,
        module_pkg=pkg_arg,
        check=check,
        extra_flags=[],
      ),
    )

    # Generate internal docs (with unexported symbols)
    variants.append(
      self._generate_variant(
        name="internal",
        output_path=internal_output,
        module_pkg=pkg_arg,
        check=check,
        extra_flags=["--include-unexported"],
      ),
    )

    return variants

  def _generate_variant(
    self,
    *,
    name: str,
    output_path: Path,
    module_pkg: str,
    check: bool,
    extra_flags: list[str],
  ) -> DocVariant:
    """Generate a single documentation variant via gomarkdoc."""
    if check and not output_path.exists():
      return DocVariant(name=name, path=output_path, hash="", status="created")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    content_hash = ""

    if check:
      cmd = [
        "gomarkdoc",
        "--format",
        "github",
        "--check",
        *extra_flags,
        "--output",
        str(output_path),
        module_pkg,
      ]
      try:
        subprocess.run(
          cmd,
          check=True,
          capture_output=True,
          text=True,
          cwd=self.repo_root,
        )
        status = "unchanged"
      except subprocess.CalledProcessError:
        status = "changed"
    else:
      existed_before = output_path.exists()
      old_hash = None
      if existed_before:
        old_hash = hashlib.sha256(
          output_path.read_text(encoding="utf-8").encode("utf-8"),
        ).hexdigest()

      cmd = [
        "gomarkdoc",
        "--format",
        "github",
        *extra_flags,
        "--output",
        str(output_path),
        module_pkg,
      ]
      try:
        subprocess.run(
          cmd,
          check=True,
          capture_output=True,
          text=True,
          cwd=self.repo_root,
        )
      except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "").strip()
        raise RuntimeError(
          f"gomarkdoc failed for {module_pkg} ({name}): {detail}"
        ) from exc

      if output_path.exists():
        content = output_path.read_text(encoding="utf-8")
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        if not existed_before:
          status = "created"
        elif content_hash != old_hash:
          status = "changed"
        else:
          status = "unchanged"
      else:
        status = "created"

    return DocVariant(
      name=name,
      path=output_path,
      hash=content_hash if not check else "",
      status=status,
    )

  def supports_identifier(self, identifier: str) -> bool:
    """Check if identifier looks like a Go package path.

    Args:
        identifier: Identifier to check

    Returns:
        True if identifier appears to be a Go package path

    """
    # Go package paths typically:
    # - Use forward slashes as separators
    # - Don't end with file extensions
    # - May start with domain names or "internal/"
    # - Don't contain spaces or special characters (except /, -, _)

    if not identifier:
      return False

    # Basic sanity checks
    if " " in identifier or "\n" in identifier or "\t" in identifier:
      return False

    # Check for file extensions (Go packages are directories)
    if identifier.endswith((".go", ".py", ".ts", ".js")):
      return False

    # Go packages commonly start with these patterns
    go_patterns = [
      "cmd/",
      "internal/",
      "pkg/",
      "test/",
      "tools/",
    ]

    # Allow common Go patterns or domain-like paths
    if any(identifier.startswith(pattern) for pattern in go_patterns):
      return True

    # Allow simple paths with reasonable characters
    return bool(all(c.isalnum() or c in "/-_." for c in identifier))
