"""Python language adapter for specification synchronization."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from supekku.scripts.lib.spec_sync.models import (
  DocVariant,
  SourceDescriptor,
  SourceUnit,
)

from .base import LanguageAdapter

if TYPE_CHECKING:
  from collections.abc import Sequence


class PythonAdapter(LanguageAdapter):
  """Language adapter for Python modules using AST documentation workflow.

  Uses the existing deterministic AST documentation system to generate
  specification variants for Python source files.
  """

  language: ClassVar[str] = "python"

  def discover_targets(
    self,
    repo_root: Path,
    requested: Sequence[str] | None = None,
  ) -> list[SourceUnit]:
    """Discover Python modules for documentation.

    Args:
        repo_root: Root directory of the repository
        requested: Optional list of specific module paths to process

    Returns:
        List of SourceUnit objects for Python modules

    """
    if requested:
      # Process specific requested modules
      source_units = []
      for identifier in requested:
        if self.supports_identifier(identifier):
          # Convert identifier to path
          if identifier.endswith(".py"):
            # File path
            module_path = repo_root / identifier
            normalized_id = identifier
          else:
            # Package or module path - look for __init__.py or .py file
            potential_file = repo_root / f"{identifier}.py"
            potential_package = repo_root / identifier / "__init__.py"

            if potential_file.exists():
              module_path = potential_file
              normalized_id = str(potential_file.relative_to(repo_root))
            elif potential_package.exists():
              module_path = potential_package
              normalized_id = str(
                potential_package.relative_to(repo_root),
              )
            else:
              continue  # Skip if not found

          if module_path.exists():
            source_units.append(
              SourceUnit(
                language=self.language,
                identifier=normalized_id,
                root=repo_root,
              ),
            )
      return source_units

    # Auto-discover Python files
    source_units = []

    # Look for Python files in common locations
    search_patterns = [
      "**/*.py",
    ]

    for pattern in search_patterns:
      for py_file in repo_root.glob(pattern):
        # Skip test files, __pycache__, and other unwanted files
        if self._should_skip_file(py_file):
          continue

        # Convert to relative path for identifier
        identifier = str(py_file.relative_to(repo_root))

        source_units.append(
          SourceUnit(
            language=self.language,
            identifier=identifier,
            root=repo_root,
          ),
        )

    return sorted(source_units, key=lambda u: u.identifier)

  def describe(self, unit: SourceUnit) -> SourceDescriptor:
    """Describe how a Python module should be processed.

    Args:
        unit: Python module source unit

    Returns:
        SourceDescriptor with Python-specific metadata

    """
    self._validate_unit_language(unit)

    # Generate slug parts from module path
    # Convert path like "supekku/scripts/lib/workspace.py" to
    # ["supekku", "scripts", "lib", "workspace"]
    path_parts = Path(unit.identifier).with_suffix("").parts
    slug_parts = list(path_parts)

    # Generate module name for frontmatter (dotted notation)
    if unit.identifier.endswith("__init__.py"):
      # Package: "supekku/scripts/lib/__init__.py" -> "supekku.scripts.lib"
      module_name = ".".join(path_parts[:-1])  # Remove __init__
    else:
      # Module: "supekku/scripts/lib/workspace.py" ->
      # "supekku.scripts.lib.workspace"
      module_name = ".".join(path_parts)

    # Default frontmatter for Python modules
    default_frontmatter = {
      "sources": [
        {
          "language": "python",
          "identifier": unit.identifier,
          "module": module_name,
          "variants": [
            {
              "name": "api",
              "path": "contracts/api.md",
            },
            {
              "name": "implementation",
              "path": "contracts/implementation.md",
            },
            {
              "name": "tests",
              "path": "contracts/tests.md",
            },
          ],
        },
      ],
    }

    # Document variants that will be generated
    variants = [
      DocVariant(
        name="api",
        path=Path("contracts/api.md"),
        hash="",
        status="unchanged",
      ),
      DocVariant(
        name="implementation",
        path=Path("contracts/implementation.md"),
        hash="",
        status="unchanged",
      ),
      DocVariant(
        name="tests",
        path=Path("contracts/tests.md"),
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
    spec_dir: Path,
    check: bool = False,
  ) -> list[DocVariant]:
    """Generate documentation for a Python module using AST analysis.

    Args:
        unit: Python module source unit
        spec_dir: Specification directory to write documentation to
        check: If True, only check if docs would change

    Returns:
        List of DocVariant objects with generation results

    """
    self._validate_unit_language(unit)

    # Import here to avoid circular imports
    from supekku.scripts.lib.docs.python import (  # noqa: PLC0415
      VariantSpec,
      generate_docs,
    )

    # Convert unit to absolute path
    module_path = self.repo_root / unit.identifier

    if not module_path.exists():
      # Return error variant
      return [
        DocVariant(name="error", path=Path(), hash="", status="unchanged"),
      ]

    # Create variant specifications
    variants_to_generate = [
      VariantSpec.public(),  # Maps to "api"
      VariantSpec.all_symbols(),  # Maps to "implementation"
      VariantSpec.tests(),  # Maps to "tests"
    ]

    # Map variant names from AST generator to our naming
    variant_name_mapping = {
      "public": "api",
      "all": "implementation",
      "tests": "tests",
    }

    # Set output directory (within spec directory)
    output_root = spec_dir / "contracts"

    try:
      # Generate documentation using the Python AST system
      results = generate_docs(
        unit=module_path,
        variants=variants_to_generate,
        check=check,
        output_root=output_root,
        base_path=self.repo_root,
      )

      # Convert DocResult objects to DocVariant objects
      doc_variants = []
      for result in results:
        # Map variant name to our naming convention
        mapped_name = variant_name_mapping.get(result.variant, result.variant)

        # Use the actual path from the result, relative to spec_dir
        actual_path = result.path

        doc_variants.append(
          DocVariant(
            name=mapped_name,
            path=actual_path.relative_to(spec_dir),
            hash=result.hash,
            status=result.status,
          ),
        )

      return doc_variants

    except Exception:
      # Handle any errors in documentation generation

      # Return error variants for each expected output
      error_variants = []
      for variant_name in ["api", "implementation", "tests"]:
        error_variants.append(
          DocVariant(
            name=variant_name,
            path=Path(f"contracts/{variant_name}.md"),
            hash="",
            status="unchanged",  # Error status handled at higher level
          ),
        )

      return error_variants

  def supports_identifier(self, identifier: str) -> bool:
    """Check if identifier looks like a Python module or file path.

    Args:
        identifier: Identifier to check

    Returns:
        True if identifier appears to be a Python module path

    """
    if not identifier:
      return False

    # Basic sanity checks
    if " " in identifier or "\n" in identifier or "\t" in identifier:
      return False

    # Python files end with .py
    if identifier.endswith(".py"):
      return True

    # Exclude non-Python file extensions
    non_python_extensions = [".go", ".js", ".ts", ".java", ".cpp", ".c", ".h"]
    if any(identifier.endswith(ext) for ext in non_python_extensions):
      return False

    # Python packages/modules can be dotted paths
    if "." in identifier:
      # Could be a dotted module path like "supekku.scripts.lib"
      return True

    # Directory paths that could contain Python modules
    python_patterns = [
      "supekku/",
      "scripts/",
      "lib/",
      "test/",
      "tests/",
    ]

    if any(identifier.startswith(pattern) for pattern in python_patterns):
      return True

    # Simple paths with reasonable characters (could be Python)
    # But exclude obvious non-Python patterns
    return all(c.isalnum() or c in "/-_." for c in identifier) and not any(
      identifier.startswith(pattern) for pattern in ["cmd/", "internal/"]
    )

  def _should_skip_file(self, file_path: Path) -> bool:
    """Check if a Python file should be skipped during discovery.

    Args:
        file_path: Path to the Python file

    Returns:
        True if the file should be skipped

    """
    # Use base adapter checks (symlinks, gitignored, documentation directories)
    if self._should_skip_path(file_path):
      return True

    # Skip common unwanted files and directories
    skip_patterns = [
      "__pycache__",
      ".git",
      ".pytest_cache",
      "node_modules",
      "venv",
      ".venv",
      ".uv-cache",
      "env",
      ".env",
    ]

    # Check if any part of the path contains skip patterns
    for part in file_path.parts:
      if any(pattern in part for pattern in skip_patterns):
        return True

    # Skip files that start with dots (hidden files)
    if file_path.name.startswith("."):
      return True

    # Skip __init__.py files (package markers, typically empty or re-exports)
    if file_path.name == "__init__.py":
      return True

    # Skip test files (matching Go pattern: mock, generated, test)
    filename = file_path.name
    filename_lower = filename.lower()

    # Test file patterns
    if "_test.py" in filename or filename.startswith("test_"):
      return True

    # Test-related files: fixtures, conftest, etc.
    test_keywords = ["fixture", "conftest"]
    if any(keyword in filename_lower for keyword in test_keywords):
      return True

    # Skip files with mock or generated in name
    if "mock" in filename_lower or "generated" in filename_lower:
      return True

    # Skip files in test/tests directories (check relative to repo_root)
    try:
      rel_path = file_path.relative_to(self.repo_root)
      for part in rel_path.parts:
        if part.lower() in ("test", "tests"):
          return True
    except ValueError:
      # file_path is not relative to repo_root, check absolute path parts
      # but skip root-level directories (like /test/)
      for i, part in enumerate(file_path.parts):
        if i > 0 and part.lower() in ("test", "tests"):  # Skip index 0 (root)
          return True

    return False
