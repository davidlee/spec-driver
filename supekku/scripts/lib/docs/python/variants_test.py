"""Tests for deterministic contract generation (VT-002).

Verification Target: PROD-005.FR-002 - Deterministic File Ordering

Test Coverage:
- Contract generation produces identical output across multiple runs
- File ordering is deterministic within packages
- Byte-identical output for same package state
- Platform-independent ordering (Linux verified, macOS compatible)
"""

from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path

import pytest

from supekku.scripts.lib.docs.python import (
  VariantCoordinator,
  VariantSpec,
  generate_docs,
)


class TestDeterministicOrdering:
  """Test that contract generation produces deterministic output."""

  def test_file_discovery_order_is_sorted(self) -> None:
    """Test that VariantSpec.get_files() returns sorted results."""
    # Use formatters package as test subject (has multiple .py files)
    package_path = Path("supekku/scripts/lib/formatters")

    if not package_path.exists():
      pytest.skip("Formatters package not found")

    # Get files for "all" variant (excludes test files and __init__.py)
    variant_spec = VariantSpec.all_symbols()
    files = VariantCoordinator.get_files_for_variant(package_path, variant_spec)

    # Should be sorted
    assert files == sorted(files), "Files must be in sorted order"

    # Verify contains expected files
    file_names = [f.name for f in files]
    assert "change_formatters.py" in file_names
    assert "decision_formatters.py" in file_names
    # Should exclude __init__.py and test files
    assert "__init__.py" not in file_names
    assert not any("_test.py" in name for name in file_names)

  def test_contract_generation_is_deterministic(self) -> None:
    """Test that generating contracts multiple times produces identical output.

    This is the core VT-002 test: run contract generation 10 times
    and verify byte-identical output.
    """
    # Use formatters package as test subject
    package_path = Path("supekku/scripts/lib/formatters")

    if not package_path.exists():
      pytest.skip("Formatters package not found")

    # Generate contracts 10 times
    hashes = []
    for _ in range(10):
      with tempfile.TemporaryDirectory() as tmpdir:
        output_root = Path(tmpdir)

        # Generate all three variants
        variants = [
          VariantSpec.public(),
          VariantSpec.all_symbols(),
          VariantSpec.tests(),
        ]

        results = generate_docs(
          unit=package_path,
          variants=variants,
          check=False,
          output_root=output_root,
          base_path=Path(),
        )

        # Collect hash of all generated content
        combined_content = []
        for result in sorted(results, key=lambda r: r.variant):
          if result.path.exists():
            content = result.path.read_text()
            combined_content.append(f"{result.variant}:{content}")

        # Hash the combined output
        combined = "\n---\n".join(combined_content)
        hash_digest = hashlib.md5(combined.encode()).hexdigest()
        hashes.append(hash_digest)

    # All hashes should be identical
    assert len(set(hashes)) == 1, (
      f"Contract generation not deterministic: got {len(set(hashes))} "
      f"different outputs across 10 runs"
    )

  def test_different_packages_have_different_output(self) -> None:
    """Sanity check: different packages should produce different contracts."""
    packages = [
      Path("supekku/scripts/lib/formatters"),
      Path("supekku/scripts/lib/decisions"),
    ]

    hashes = []
    for package_path in packages:
      if not package_path.exists():
        continue

      with tempfile.TemporaryDirectory() as tmpdir:
        output_root = Path(tmpdir)
        variant = VariantSpec.all_symbols()

        results = generate_docs(
          unit=package_path,
          variants=[variant],
          check=False,
          output_root=output_root,
          base_path=Path(),
        )

        # Hash the output
        if results and results[0].path.exists():
          content = results[0].path.read_text()
          hash_digest = hashlib.md5(content.encode()).hexdigest()
          hashes.append(hash_digest)

    # Different packages should have different hashes
    if len(hashes) == 2:
      assert hashes[0] != hashes[1], (
        "Different packages should produce different contracts"
      )


class TestFileOrdering:
  """Test file ordering behavior for various package structures."""

  def test_single_file_package_ordering(self) -> None:
    """Test ordering for package with single Python file."""
    # supekku/cli has minimal files
    package_path = Path("supekku/cli")

    if not package_path.exists():
      pytest.skip("CLI package not found")

    variant_spec = VariantSpec.all_symbols()
    files = VariantCoordinator.get_files_for_variant(package_path, variant_spec)

    # Should be sorted even with one file
    assert files == sorted(files)

  def test_package_with_many_files_ordering(self) -> None:
    """Test ordering for package with many files."""
    # formatters has multiple files
    package_path = Path("supekku/scripts/lib/formatters")

    if not package_path.exists():
      pytest.skip("Formatters package not found")

    variant_spec = VariantSpec.all_symbols()
    files = VariantCoordinator.get_files_for_variant(package_path, variant_spec)

    # All files should be in sorted order
    assert files == sorted(files)

    # Verify sorting is by full path, not just filename
    file_paths = [str(f) for f in files]
    assert file_paths == sorted(file_paths)

  def test_tests_variant_filters_correctly(self) -> None:
    """Test that tests variant only includes test files."""
    package_path = Path("supekku/scripts/lib/specs")

    if not package_path.exists():
      pytest.skip("Specs package not found")

    variant_spec = VariantSpec.tests()
    files = VariantCoordinator.get_files_for_variant(package_path, variant_spec)

    # All files should be test files
    for f in files:
      assert f.name.endswith("_test.py"), f"Expected test file, got {f.name}"

    # Should be sorted
    assert files == sorted(files)


class TestPlatformIndependence:
  """Test that ordering is platform-independent."""

  def test_sorted_ordering_is_stable(self) -> None:
    """Test that Python's sorted() produces stable results.

    This validates the assumption that sorted(Path.rglob())
    produces deterministic results across platforms.
    """
    package_path = Path("supekku/scripts/lib/formatters")

    if not package_path.exists():
      pytest.skip("Formatters package not found")

    # Get files multiple times
    all_runs = []
    for _ in range(5):
      files = sorted(package_path.rglob("*.py"))
      file_paths = [str(f) for f in files]
      all_runs.append(tuple(file_paths))

    # All runs should produce identical results
    assert all(run == all_runs[0] for run in all_runs), (
      "sorted(rglob()) not producing consistent results"
    )

  def test_path_sorting_is_lexicographic(self) -> None:
    """Test that path sorting follows expected lexicographic order."""
    package_path = Path("supekku/scripts/lib/formatters")

    if not package_path.exists():
      pytest.skip("Formatters package not found")

    files = sorted(package_path.rglob("*.py"))

    # Convert to strings for comparison
    file_strs = [str(f) for f in files]

    # Should be in lexicographic order
    for i in range(len(file_strs) - 1):
      assert file_strs[i] < file_strs[i + 1], (
        f"Files not in lexicographic order: {file_strs[i]} vs {file_strs[i + 1]}"
      )
