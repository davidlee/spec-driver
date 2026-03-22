"""Integration tests for TypeScript adapter dependency handling (VT-019-003).

Tests sync-level behavior when ts-doc-extract is missing,
verifying graceful degradation through the full generate() path.
"""

import shutil
import unittest
from pathlib import Path
from unittest.mock import patch

from supekku.scripts.lib.sync.models import SourceUnit

from .typescript import TypeScriptAdapter


class TestTypescriptSyncWithMissingDependency(unittest.TestCase):
  """VT-019-003: Integration test for sync with missing ts-doc-extract."""

  def setUp(self) -> None:
    self.test_repo = Path("/tmp/test-ts-dep-integration")
    self.test_repo.mkdir(parents=True, exist_ok=True)

    # Create a minimal TS project
    (self.test_repo / "package.json").write_text(
      '{"name": "test-project", "version": "1.0.0"}'
    )
    src = self.test_repo / "src"
    src.mkdir(exist_ok=True)
    (src / "index.ts").write_text("export function hello(): string { return 'hi'; }")

    self.adapter = TypeScriptAdapter(self.test_repo)

  def tearDown(self) -> None:
    if self.test_repo.exists():
      shutil.rmtree(self.test_repo)

  def test_generate_returns_empty_when_ts_doc_extract_missing(self) -> None:
    """Sync skips TS units gracefully when ts-doc-extract is not installed."""
    unit = SourceUnit(
      language="typescript", identifier="src/index.ts", root=self.test_repo
    )
    output_dir = Path("/tmp/test-ts-dep-contracts")
    variant_outputs = {
      "api": output_dir / "public" / "src" / "index.ts.md",
      "internal": output_dir / "internal" / "src" / "index.ts.md",
    }

    try:
      with (
        patch.object(TypeScriptAdapter, "is_node_available", return_value=True),
        patch(
          "supekku.scripts.lib.sync.adapters.typescript.is_npm_package_available",
          return_value=False,
        ),
        patch("supekku.scripts.lib.sync.adapters.typescript.Console"),
      ):
        result = self.adapter.generate(unit, variant_outputs=variant_outputs)

      assert result == [], "Expected empty list when ts-doc-extract is missing"
      # No contract files should have been created
      assert not (output_dir / "public").exists()
      assert not (output_dir / "internal").exists()
    finally:
      if output_dir.exists():
        shutil.rmtree(output_dir)

  def test_warning_includes_install_instructions(self) -> None:
    """Warning message includes actionable install instructions."""
    unit = SourceUnit(
      language="typescript", identifier="src/index.ts", root=self.test_repo
    )
    variant_outputs = {
      "api": Path("/tmp/unused/api.md"),
      "internal": Path("/tmp/unused/internal.md"),
    }

    with (
      patch.object(TypeScriptAdapter, "is_node_available", return_value=True),
      patch(
        "supekku.scripts.lib.sync.adapters.typescript.is_npm_package_available",
        return_value=False,
      ),
      patch("supekku.scripts.lib.sync.adapters.typescript.Console") as mock_console,
    ):
      self.adapter.generate(unit, variant_outputs=variant_outputs)

      mock_console.return_value.print.assert_called_once()
      message = mock_console.return_value.print.call_args[0][0]
      assert "ts-doc-extract not found" in message
      assert "install" in message.lower()

  def test_subsequent_units_skip_without_recheck(self) -> None:
    """Availability check is cached — second unit skips without re-checking."""
    unit1 = SourceUnit(
      language="typescript", identifier="src/index.ts", root=self.test_repo
    )
    unit2 = SourceUnit(
      language="typescript", identifier="src/index.ts", root=self.test_repo
    )
    variant_outputs = {
      "api": Path("/tmp/unused/api.md"),
      "internal": Path("/tmp/unused/internal.md"),
    }

    with (
      patch.object(TypeScriptAdapter, "is_node_available", return_value=True),
      patch(
        "supekku.scripts.lib.sync.adapters.typescript.is_npm_package_available",
        return_value=False,
      ) as mock_check,
      patch("supekku.scripts.lib.sync.adapters.typescript.Console"),
    ):
      self.adapter.generate(unit1, variant_outputs=variant_outputs)
      self.adapter.generate(unit2, variant_outputs=variant_outputs)

      # Only called once due to caching
      mock_check.assert_called_once()
