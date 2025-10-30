"""Python documentation generation API.

This package provides a clean API for generating documentation from Python AST,
designed for integration with multi-language specification sync adapters.
"""

import hashlib
from collections.abc import Iterable
from pathlib import Path
from typing import List, Optional

from .analyzer import DeterministicPythonModuleAnalyzer
from .cache import ParseCache
from .generator import generate_deterministic_markdown_spec
from .models import DocResult, VariantSpec
from .path_utils import PathNormalizer
from .variants import VariantCoordinator


def calculate_content_hash(content: str) -> str:
  """Calculate SHA256 hash of content for comparison."""
  return hashlib.sha256(content.encode("utf-8")).hexdigest()


def check_file_status(output_file: Path, new_content: str) -> str:
  """Check if file needs creation/update. Returns status."""
  new_hash = calculate_content_hash(new_content)

  if not output_file.exists():
    return "created"

  with open(output_file, encoding="utf-8") as f:
    existing_content = f.read()

  existing_hash = calculate_content_hash(existing_content)
  return "unchanged" if existing_hash == new_hash else "changed"


def write_file_with_status(output_file: Path, content: str) -> str:
  """Write file and return status."""
  status = check_file_status(output_file, content)

  if status in ("created", "changed"):
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
      f.write(content)

  return status


def generate_docs(
  unit: Path,
  variants: Iterable[VariantSpec],
  *,
  check: bool = False,
  output_root: Path,
  cache_dir: Path | None = None,
  base_path: Path | None = None,
) -> list[DocResult]:
  """Generate documentation for Python code unit.

  Args:
    unit: Path to Python file or package directory
    variants: Iterable of VariantSpec defining documentation variants to generate
    check: If True, only check if docs would change (don't write files)
    output_root: Root directory for generated documentation
    cache_dir: Optional custom cache directory
    base_path: Optional base path for module name resolution

  Returns:
    List of DocResult objects with generation results and metadata

  """
  # Initialize cache
  cache = ParseCache(cache_dir) if cache_dir else ParseCache()
  results = []

  # Determine base path for module resolution
  if base_path is None:
    base_path = unit.parent if unit.is_file() else unit

  # Process each variant
  for variant_spec in variants:
    # Get files to process for this variant
    try:
      files_to_process = VariantCoordinator.get_files_for_variant(
        unit,
        variant_spec,
      )
    except FileNotFoundError as e:
      results.append(
        DocResult(
          variant=variant_spec.variant_type.value,
          path=unit,
          hash="",
          status="error",
          module_identifier="",
          error_message=str(e),
        ),
      )
      continue

    # Sort files for deterministic processing order
    files_to_process.sort(
      key=lambda p: PathNormalizer.normalize_path_for_id(p, base_path),
    )

    # Process each file for this variant
    for file_path in files_to_process:
      try:
        # Analyze file
        analyzer = DeterministicPythonModuleAnalyzer(
          file_path,
          base_path,
          cache,
        )
        analysis = analyzer.analyze()

        if "error" in analysis:
          results.append(
            DocResult(
              variant=variant_spec.variant_type.value,
              path=file_path,
              hash="",
              status="error",
              module_identifier=PathNormalizer.get_module_name(
                file_path,
                base_path,
              ),
              error_message=analysis["error"],
            ),
          )
          continue

        # Filter analysis for variant
        filtered_analysis = VariantCoordinator.filter_analysis_for_variant(
          analysis,
          variant_spec,
        )

        # Generate markdown
        markdown = generate_deterministic_markdown_spec(
          filtered_analysis,
          variant_spec.variant_type.value,
        )

        # Calculate output path
        output_filename = PathNormalizer.get_output_filename(
          file_path,
          variant_spec.variant_type.value,
          base_path,
        )
        output_file = output_root / output_filename

        # Calculate content hash
        content_hash = calculate_content_hash(markdown)

        # Get module identifier
        module_identifier = PathNormalizer.get_module_name(file_path, base_path)

        if check:
          # Check mode: just compare, mark as error if different
          status = check_file_status(output_file, markdown)
          if status in ("created", "changed"):
            status = "error"  # In check mode, differences are errors
        else:
          # Generate mode: write file
          status = write_file_with_status(output_file, markdown)

        results.append(
          DocResult(
            variant=variant_spec.variant_type.value,
            path=output_file,
            hash=content_hash,
            status=status,
            module_identifier=module_identifier,
          ),
        )

      except Exception as e:
        results.append(
          DocResult(
            variant=variant_spec.variant_type.value,
            path=file_path,
            hash="",
            status="error",
            module_identifier=PathNormalizer.get_module_name(
              file_path,
              base_path,
            ),
            error_message=str(e),
          ),
        )

  return results


# Export main API components
__all__ = [
  "DocResult",
  "ParseCache",
  "PathNormalizer",
  "VariantCoordinator",
  "VariantSpec",
  "generate_docs",
]
