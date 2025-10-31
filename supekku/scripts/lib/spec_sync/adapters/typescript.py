"""TypeScript language adapter for specification synchronization."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from shutil import which
from typing import TYPE_CHECKING, ClassVar

from supekku.scripts.lib.spec_sync.models import (
  DocVariant,
  SourceDescriptor,
  SourceUnit,
)

from .base import LanguageAdapter

if TYPE_CHECKING:
  from collections.abc import Sequence


class NodeRuntimeNotAvailableError(RuntimeError):
  """Raised when Node runtime is required but not available."""


class TypeDocGenerationError(RuntimeError):
  """Raised when TypeDoc generation fails."""


class TypeScriptAdapter(LanguageAdapter):
  """Language adapter for TypeScript packages using TypeDoc.

  Uses TypeDoc via npx for zero-install documentation generation.
  Supports both Node.js and Bun runtimes.
  """

  language: ClassVar[str] = "typescript"

  @staticmethod
  def is_node_available() -> bool:
    """Check if Node.js runtime is available in PATH."""
    return which("node") is not None

  @staticmethod
  def is_npm_available() -> bool:
    """Check if npm is available (provides npx)."""
    return which("npm") is not None

  @staticmethod
  def is_bun_available() -> bool:
    """Check if Bun runtime is available in PATH."""
    return which("bun") is not None

  @staticmethod
  def is_pnpm_available() -> bool:
    """Check if pnpm is available in PATH."""
    return which("pnpm") is not None

  def _detect_package_manager(self, repo_root: Path) -> str | None:
    """Detect which package manager the project uses.

    Args:
        repo_root: Root directory of the repository

    Returns:
        Package manager name ('pnpm', 'yarn', 'npm', 'bun') or None

    """
    # Check for lockfiles in order of preference
    if (repo_root / "pnpm-lock.yaml").exists():
      return "pnpm"
    if (repo_root / "bun.lockb").exists():
      return "bun"
    if (repo_root / "yarn.lock").exists():
      return "yarn"
    if (repo_root / "package-lock.json").exists():
      return "npm"

    return None

  def _get_runtime_command(self, pkg_dir: Path | None = None) -> list[str]:
    """Determine which JS runtime to use for package execution.

    Priority:
    1. Detected package manager (pnpm/bun/yarn/npm)
    2. Bun (if available, faster)
    3. Node + npx (standard)

    Args:
        pkg_dir: Optional package directory to detect package manager from

    Returns:
        Command prefix for executing npm packages

    Raises:
        NodeRuntimeNotAvailableError: If no JS runtime is available

    """
    # Try to detect package manager from lockfile if pkg_dir provided
    if pkg_dir:
      detected_pm = self._detect_package_manager(pkg_dir)

      # Use detected package manager if available
      if detected_pm == "pnpm" and self.is_pnpm_available():
        return ["pnpm", "dlx"]
      if detected_pm == "bun" and self.is_bun_available():
        return ["bunx", "--bun"]
      if detected_pm == "yarn" and which("yarn"):
        return ["yarn", "dlx"]
      if detected_pm == "npm" and self.is_npm_available():
        return ["npx", "--yes"]

    # Fallback to runtime availability
    if self.is_bun_available():
      return ["bunx", "--bun"]
    if self.is_node_available() and self.is_npm_available():
      return ["npx", "--yes"]

    raise NodeRuntimeNotAvailableError(
      "No JavaScript runtime found. Please install Node.js from "
      "https://nodejs.org/ or Bun from https://bun.sh/"
    )

  def discover_targets(
    self,
    repo_root: Path,
    requested: Sequence[str] | None = None,
  ) -> list[SourceUnit]:
    """Discover TypeScript packages for documentation.

    Args:
        repo_root: Root directory of the repository
        requested: Optional list of specific package paths to process

    Returns:
        List of SourceUnit objects for TypeScript packages

    Raises:
        NodeRuntimeNotAvailableError: If no JS runtime is available

    """
    # Check runtime availability
    if not (self.is_node_available() or self.is_bun_available()):
      raise NodeRuntimeNotAvailableError(
        "No JavaScript runtime found. Please install Node.js from "
        "https://nodejs.org/ or Bun from https://bun.sh/"
      )

    if requested:
      # Process specific requested targets
      return self._discover_requested_targets(repo_root, requested)

    # Auto-discover TypeScript packages
    return self._auto_discover_packages(repo_root)

  def _discover_requested_targets(
    self,
    repo_root: Path,
    requested: Sequence[str],
  ) -> list[SourceUnit]:
    """Process specific requested targets.

    Args:
        repo_root: Root directory of the repository
        requested: List of requested identifiers

    Returns:
        List of SourceUnit objects for requested targets

    """
    source_units = []

    for identifier in requested:
      if not self.supports_identifier(identifier):
        continue

      # Resolve identifier to package directory
      pkg_dir = repo_root / identifier
      if not pkg_dir.exists():
        # Try as direct path
        pkg_dir = Path(identifier)
        if not pkg_dir.exists():
          continue

      # Verify it's a TypeScript package
      if self._is_typescript_package(pkg_dir):
        try:
          relative_path = pkg_dir.relative_to(repo_root)
          unit_id = str(relative_path) if str(relative_path) != "." else "root"

          source_units.append(
            SourceUnit(
              language=self.language,
              identifier=unit_id,
              root=repo_root,
            ),
          )
        except ValueError:
          # Path not relative to repo_root
          continue

    return source_units

  def _auto_discover_packages(self, repo_root: Path) -> list[SourceUnit]:
    """Auto-discover TypeScript packages in repository.

    Strategy:
    1. Find all package.json files
    2. Check if they have TypeScript (tsconfig.json or .ts files)
    3. Create SourceUnit for each TS package

    Args:
        repo_root: Root directory of the repository

    Returns:
        List of SourceUnit objects for discovered packages

    """
    source_units = []

    exclude_dirs = {
      "node_modules",
      ".git",
      "dist",
      "build",
      "coverage",
      ".next",
      ".nuxt",
      "out",
      ".cache",
      "target",
      "tmp",
      "temp",
      "__pycache__",
      ".pytest_cache",
      ".venv",
      "venv",
      ".uv-cache",
    }

    # Find all package.json files
    for pkg_json in repo_root.rglob("package.json"):
      # Skip excluded directories
      if any(excluded in pkg_json.parts for excluded in exclude_dirs):
        continue

      # Skip if not git-tracked
      if self._should_skip_path(pkg_json):
        continue

      pkg_dir = pkg_json.parent

      # Check if this is a TypeScript package
      if self._is_typescript_package(pkg_dir):
        try:
          relative_path = pkg_dir.relative_to(repo_root)
          identifier = str(relative_path) if str(relative_path) != "." else "root"

          source_units.append(
            SourceUnit(
              language=self.language,
              identifier=identifier,
              root=repo_root,
            ),
          )
        except ValueError:
          continue

    return source_units

  def _is_typescript_package(self, pkg_dir: Path) -> bool:
    """Check if directory is a TypeScript package.

    Args:
        pkg_dir: Directory to check

    Returns:
        True if directory contains TypeScript configuration or files

    """
    # Check for tsconfig.json
    if (pkg_dir / "tsconfig.json").exists():
      return True

    # Check for TypeScript files
    ts_extensions = ["*.ts", "*.tsx", "*.mts", "*.cts"]
    for ext in ts_extensions:
      if list(pkg_dir.glob(ext)) or list(pkg_dir.glob(f"src/{ext}")):
        return True

    return False

  def _find_entry_point(self, pkg_dir: Path) -> Path | None:
    """Find the best entry point for TypeDoc.

    Args:
        pkg_dir: Package directory

    Returns:
        Path to entry point file, or None if not found

    """
    # Common entry point files in priority order
    entry_candidates = [
      "src/index.ts",
      "src/index.tsx",
      "index.ts",
      "index.tsx",
      "src/main.ts",
      "src/main.tsx",
      "main.ts",
      "main.tsx",
    ]

    for candidate in entry_candidates:
      entry_path = pkg_dir / candidate
      if entry_path.exists():
        return entry_path

    # Check package.json for entry points
    package_json = pkg_dir / "package.json"
    if package_json.exists():
      try:
        pkg_data = json.loads(package_json.read_text(encoding="utf-8"))

        # Check common entry point fields
        for field in ["source", "main", "module", "types"]:
          if field in pkg_data:
            entry = pkg_data[field]
            if isinstance(entry, str) and entry.endswith((".ts", ".tsx")):
              entry_path = pkg_dir / entry
              if entry_path.exists():
                return entry_path

      except (json.JSONDecodeError, OSError):
        pass

    return None

  def describe(self, unit: SourceUnit) -> SourceDescriptor:
    """Describe how a TypeScript package should be processed.

    Args:
        unit: TypeScript package source unit

    Returns:
        SourceDescriptor with TypeScript-specific metadata

    """
    self._validate_unit_language(unit)

    # Generate slug parts from identifier
    # Convert path separators and special chars to slug-friendly format
    slug_parts = (
      unit.identifier.replace("@", "").replace("/", "-").replace("\\", "-").split("-")
    )
    slug_parts = [part for part in slug_parts if part]

    # Define variants
    variants = [
      DocVariant(
        name="public",
        path=Path("contracts/public.md"),
        hash="",
        status="unchanged",
      ),
      DocVariant(
        name="internal",
        path=Path("contracts/internal.md"),
        hash="",
        status="unchanged",
      ),
    ]

    # Frontmatter
    default_frontmatter = {
      "sources": [
        {
          "language": "typescript",
          "identifier": unit.identifier,
          "variants": [
            {
              "name": variant.name,
              "path": str(variant.path),
            }
            for variant in variants
          ],
        },
      ],
    }

    return SourceDescriptor(
      slug_parts=slug_parts,
      default_frontmatter=default_frontmatter,
      variants=variants,
    )

  def generate(
    self,
    unit: SourceUnit,
    *,
    spec_dir: Path,
    check: bool = False,
  ) -> list[DocVariant]:
    """Generate documentation for TypeScript package using TypeDoc.

    Args:
        unit: TypeScript package source unit
        spec_dir: Specification directory to write documentation to
        check: If True, only check if docs would change

    Returns:
        List of DocVariant objects with generation results

    Raises:
        NodeRuntimeNotAvailableError: If no JS runtime is available
        TypeDocGenerationError: If TypeDoc generation fails

    """
    self._validate_unit_language(unit)

    # Check runtime availability
    if not (self.is_node_available() or self.is_bun_available()):
      raise NodeRuntimeNotAvailableError(
        "No JavaScript runtime found. Please install Node.js from "
        "https://nodejs.org/ or Bun from https://bun.sh/"
      )

    # Resolve package directory
    if unit.identifier == "root":
      pkg_dir = self.repo_root
    else:
      pkg_dir = self.repo_root / unit.identifier

    if not pkg_dir.exists():
      msg = f"Package directory not found: {pkg_dir}"
      raise ValueError(msg)

    contracts_dir = spec_dir / "contracts"
    variants = []

    # Generate public API docs
    variants.append(
      self._generate_variant(
        pkg_dir=pkg_dir,
        output_dir=contracts_dir,
        variant_name="public",
        include_private=False,
        check=check,
        spec_dir=spec_dir,
      ),
    )

    # Generate internal docs (with private members)
    variants.append(
      self._generate_variant(
        pkg_dir=pkg_dir,
        output_dir=contracts_dir,
        variant_name="internal",
        include_private=True,
        check=check,
        spec_dir=spec_dir,
      ),
    )

    return variants

  def _generate_variant(
    self,
    pkg_dir: Path,
    output_dir: Path,
    variant_name: str,
    include_private: bool,
    check: bool,
    spec_dir: Path,
  ) -> DocVariant:
    """Generate a single documentation variant using TypeDoc.

    Args:
        pkg_dir: Package directory
        output_dir: Output directory for documentation
        variant_name: Name of the variant (public/internal)
        include_private: Whether to include private members
        check: If True, only check if docs would change
        spec_dir: Specification directory (for relative paths)

    Returns:
        DocVariant with generation results

    Raises:
        TypeDocGenerationError: If generation fails

    """
    output_file = output_dir / f"{variant_name}.md"
    temp_dir = output_dir / f".typedoc-{variant_name}"

    # Try to use local TypeDoc installation from workspace
    # This is important for monorepos with workspace-specific tsconfig
    local_typedoc = None

    # Check for local typedoc in node_modules
    # Walk up from pkg_dir to find node_modules with typedoc
    check_dir = pkg_dir
    for _ in range(5):  # Check up to 5 levels up
      node_modules = check_dir / "node_modules"
      if (node_modules / ".bin" / "typedoc").exists():
        local_typedoc = node_modules / ".bin" / "typedoc"
        break
      if (node_modules / "typedoc").exists():
        # Found typedoc package, can use npx from this directory
        local_typedoc = "typedoc"
        break
      parent = check_dir.parent
      if parent == check_dir:  # Reached filesystem root
        break
      check_dir = parent

    # Construct TypeDoc command
    if local_typedoc and local_typedoc != "typedoc":
      # Use local binary directly
      cmd = [str(local_typedoc)]
    elif local_typedoc == "typedoc":
      # Use package manager to run local typedoc
      pm = self._detect_package_manager(pkg_dir)
      if pm == "pnpm":
        cmd = ["pnpm", "exec", "typedoc"]
      elif pm == "yarn":
        cmd = ["yarn", "typedoc"]
      elif pm == "bun":
        cmd = ["bun", "run", "typedoc"]
      else:
        cmd = ["npx", "typedoc"]
    else:
      # Fall back to npx with temporary install
      runtime_cmd = (
        ["npx", "--yes"] if self.is_npm_available() else ["bunx", "--bun"]
      )
      cmd = [
        *runtime_cmd,
        "-p",
        "typedoc",
        "-p",
        "typedoc-plugin-markdown",
        "typedoc",
      ]

    # Add plugin option (local installs should have plugin in node_modules)
    cmd.extend([
      "--plugin",
      "typedoc-plugin-markdown",
      "--out",
      str(temp_dir),
      "--exclude",
      "**/node_modules/**",
      "--exclude",
      "**/*.test.ts",
      "--exclude",
      "**/*.spec.ts",
      "--exclude",
      "**/*.test.tsx",
      "--exclude",
      "**/*.spec.tsx",
      "--exclude",
      "**/dist/**",
      "--exclude",
      "**/.next/**",
      "--exclude",
      "**/build/**",
    ])

    if include_private:
      cmd.extend(
        [
          "--excludePrivate",
          "false",
          "--excludeProtected",
          "false",
          "--excludeInternal",
          "false",
        ],
      )

    # Determine entry point for TypeDoc
    # Try to find a reasonable entry point instead of just src/
    entry_point = self._find_entry_point(pkg_dir)
    if entry_point:
      cmd.append(str(entry_point))
    else:
      # Fallback to src directory or package directory
      src_dir = pkg_dir / "src" if (pkg_dir / "src").exists() else pkg_dir
      cmd.append(str(src_dir))

    try:
      # Check if output already exists for comparison
      old_hash = None
      if output_file.exists():
        old_content = output_file.read_text(encoding="utf-8")
        old_hash = hashlib.sha256(old_content.encode("utf-8")).hexdigest()

      if check and not output_file.exists():
        # In check mode, if file doesn't exist, it would be created
        return DocVariant(
          name=variant_name,
          path=output_file.relative_to(spec_dir),
          hash="",
          status="created",
        )

      # Execute TypeDoc
      result = subprocess.run(
        cmd,
        cwd=pkg_dir,
        check=True,
        capture_output=True,
        text=True,
        timeout=120,
      )

      # Check if temp directory was created
      if not temp_dir.exists():
        raise TypeDocGenerationError(
          f"TypeDoc did not generate output directory: {temp_dir}. "
          f"stdout: {result.stdout}, stderr: {result.stderr}"
        )

      # Combine TypeDoc output into single markdown
      combined_md = self._combine_typedoc_output(temp_dir, variant_name)

      # Check if we got any content
      if not combined_md or len(combined_md.strip()) < 50:
        raise TypeDocGenerationError(
          f"TypeDoc generated empty or minimal output. "
          f"Directory: {temp_dir}, Content length: {len(combined_md)}"
        )

      # Calculate hash
      content_hash = hashlib.sha256(combined_md.encode("utf-8")).hexdigest()

      if check:
        # Check mode - compare hashes
        status = "unchanged" if content_hash == old_hash else "changed"
      else:
        # Generate mode - write file
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file.write_text(combined_md, encoding="utf-8")

        # Determine status
        if old_hash is None:
          status = "created"
        elif content_hash != old_hash:
          status = "changed"
        else:
          status = "unchanged"

      # Clean up temp directory
      if temp_dir.exists():
        shutil.rmtree(temp_dir)

      return DocVariant(
        name=variant_name,
        path=output_file.relative_to(spec_dir),
        hash=content_hash if not check else "",
        status=status,
      )

    except subprocess.CalledProcessError as e:
      raise TypeDocGenerationError(
        f"TypeDoc generation failed for {pkg_dir}: {e.stderr}"
      ) from e
    except subprocess.TimeoutExpired as e:
      raise TypeDocGenerationError(
        f"TypeDoc generation timed out for {pkg_dir}"
      ) from e

  def _combine_typedoc_output(self, typedoc_out_dir: Path, variant_name: str) -> str:
    """Combine TypeDoc's multi-file output into single markdown.

    TypeDoc generates multiple markdown files. We combine them into
    a single document similar to gomarkdoc output.

    Args:
        typedoc_out_dir: TypeDoc output directory
        variant_name: Variant name for header

    Returns:
        Combined markdown content

    """
    combined = []

    # Add header
    combined.append("<!-- Code generated by TypeDoc. DO NOT EDIT -->\n\n")

    # Read main README if exists
    readme = typedoc_out_dir / "README.md"
    if readme.exists():
      content = readme.read_text(encoding="utf-8")
      # Strip title if it's just "README"
      if content.startswith("# README\n"):
        content = content[len("# README\n") :]
      combined.append(content)
      combined.append("\n")

    # Collect all other markdown files (sorted for consistency)
    md_files = sorted(typedoc_out_dir.rglob("*.md"))
    md_files = [f for f in md_files if f.name != "README.md"]

    for md_file in md_files:
      # Add content
      content = md_file.read_text(encoding="utf-8")
      combined.append(content)
      combined.append("\n")

    return "".join(combined)

  def supports_identifier(self, identifier: str) -> bool:
    """Check if identifier looks like a TypeScript package/module.

    Args:
        identifier: Source identifier to check

    Returns:
        True if identifier appears to be TypeScript-related

    """
    if not identifier:
      return False

    # TypeScript file extensions
    if identifier.endswith((".ts", ".tsx", ".mts", ".cts")):
      return True

    # Exclude obvious non-TypeScript patterns
    exclude_patterns = [
      ".py",
      ".pyc",
      ".go",
      ".java",
      ".rb",
      ".php",
      "__pycache__",
      ".pytest_cache",
    ]

    if any(pattern in identifier for pattern in exclude_patterns):
      return False

    # TypeScript-specific indicators
    ts_indicators = [
      "src/",
      "lib/",
      "packages/",
      "apps/",
      "components/",
      "services/",
      "utils/",
      "helpers/",
      "hooks/",
      "@types/",
      "node_modules/@",
    ]

    if any(indicator in identifier for indicator in ts_indicators):
      return True

    # Scoped package pattern (@scope/name)
    return identifier.startswith("@") and "/" in identifier


__all__ = ["TypeScriptAdapter"]
