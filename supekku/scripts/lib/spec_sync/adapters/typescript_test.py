"""Tests for TypeScript language adapter."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pytest

from supekku.scripts.lib.spec_sync.models import SourceUnit

from .typescript import NodeRuntimeNotAvailableError, TypeScriptAdapter


class TestTypeScriptAdapter(unittest.TestCase):
  """Test TypeScriptAdapter functionality."""

  def setUp(self) -> None:
    """Set up test fixtures."""
    self.repo_root = Path("/test/repo")
    self.adapter = TypeScriptAdapter(self.repo_root)

  def test_language_identifier(self) -> None:
    """Test that TypeScriptAdapter has correct language identifier."""
    assert TypeScriptAdapter.language == "typescript"
    assert self.adapter.language == "typescript"

  def test_supports_identifier_typescript_files(self) -> None:
    """Test supports_identifier returns True for TypeScript files."""
    valid_identifiers = [
      "src/index.ts",
      "lib/utils.tsx",
      "components/Button.tsx",
      "services/api.ts",
      "types/User.ts",
      "test/helpers.mts",
      "dist/output.cts",
    ]

    for identifier in valid_identifiers:
      with self.subTest(identifier=identifier):
        msg = f"Should support TypeScript file: {identifier}"
        assert self.adapter.supports_identifier(identifier), msg

  def test_supports_identifier_typescript_modules(self) -> None:
    """Test supports_identifier returns True for TypeScript-style paths."""
    valid_identifiers = [
      "src/components",
      "lib/services",
      "node_modules/@types/react",
      "@scope/package-name",
      "packages/core",
      "apps/web",
    ]

    for identifier in valid_identifiers:
      with self.subTest(identifier=identifier):
        msg = f"Should support TypeScript module: {identifier}"
        assert self.adapter.supports_identifier(identifier), msg

  def test_supports_identifier_rejects_non_typescript(self) -> None:
    """Test supports_identifier returns False for non-TypeScript identifiers."""
    invalid_identifiers = [
      "",
      "module.py",
      "package.go",
      "__pycache__/module.pyc",
      "internal/application/services",  # Go-style, no TS indicators
      "cmd/vice",
    ]

    for identifier in invalid_identifiers:
      with self.subTest(identifier=identifier):
        msg = f"Should not support identifier: {identifier}"
        assert not self.adapter.supports_identifier(identifier), msg

  def test_supports_identifier_edge_cases(self) -> None:
    """Test edge cases for identifier support."""
    # Should reject Python/Go files even in TypeScript-like directories
    assert not self.adapter.supports_identifier("src/main.go")
    assert not self.adapter.supports_identifier("lib/utils.py")

    # Should accept scoped packages
    assert self.adapter.supports_identifier("@angular/core")
    assert self.adapter.supports_identifier("@types/node")

  def test_is_node_available(self) -> None:
    """Test is_node_available correctly detects Node presence."""
    with patch("supekku.scripts.lib.spec_sync.adapters.typescript.which") as mock_which:
      # Test when Node is available
      mock_which.return_value = "/usr/bin/node"
      assert TypeScriptAdapter.is_node_available()

      # Test when Node is not available
      mock_which.return_value = None
      assert not TypeScriptAdapter.is_node_available()

  def test_is_npm_available(self) -> None:
    """Test is_npm_available correctly detects npm presence."""
    with patch("supekku.scripts.lib.spec_sync.adapters.typescript.which") as mock_which:
      # Test when npm is available
      mock_which.return_value = "/usr/bin/npm"
      assert TypeScriptAdapter.is_npm_available()

      # Test when npm is not available
      mock_which.return_value = None
      assert not TypeScriptAdapter.is_npm_available()

  def test_is_bun_available(self) -> None:
    """Test is_bun_available correctly detects Bun presence."""
    with patch("supekku.scripts.lib.spec_sync.adapters.typescript.which") as mock_which:
      # Test when Bun is available
      mock_which.return_value = "/usr/bin/bun"
      assert TypeScriptAdapter.is_bun_available()

      # Test when Bun is not available
      mock_which.return_value = None
      assert not TypeScriptAdapter.is_bun_available()

  def test_is_pnpm_available(self) -> None:
    """Test is_pnpm_available correctly detects pnpm presence."""
    with patch("supekku.scripts.lib.spec_sync.adapters.typescript.which") as mock_which:
      # Test when pnpm is available
      mock_which.return_value = "/usr/bin/pnpm"
      assert TypeScriptAdapter.is_pnpm_available()

      # Test when pnpm is not available
      mock_which.return_value = None
      assert not TypeScriptAdapter.is_pnpm_available()

  def test_get_runtime_command_prefers_bun(self) -> None:
    """Test _get_runtime_command prefers Bun when available."""
    with patch("supekku.scripts.lib.spec_sync.adapters.typescript.which") as mock_which:

      def which_side_effect(cmd: str) -> str | None:
        if cmd == "bun":
          return "/usr/bin/bun"
        if cmd in ("node", "npm"):
          return f"/usr/bin/{cmd}"
        return None

      mock_which.side_effect = which_side_effect

      cmd = self.adapter._get_runtime_command()
      assert cmd == ["bunx", "--bun"]

  def test_get_runtime_command_falls_back_to_npx(self) -> None:
    """Test _get_runtime_command uses npx when Bun unavailable."""
    with patch("supekku.scripts.lib.spec_sync.adapters.typescript.which") as mock_which:

      def which_side_effect(cmd: str) -> str | None:
        if cmd == "bun":
          return None
        if cmd in ("node", "npm"):
          return f"/usr/bin/{cmd}"
        return None

      mock_which.side_effect = which_side_effect

      cmd = self.adapter._get_runtime_command()
      assert cmd == ["npx", "--yes"]

  def test_get_runtime_command_raises_when_nothing_available(self) -> None:
    """Test _get_runtime_command raises when no runtime available."""
    with patch("supekku.scripts.lib.spec_sync.adapters.typescript.which") as mock_which:
      mock_which.return_value = None

      with pytest.raises(NodeRuntimeNotAvailableError) as context:
        self.adapter._get_runtime_command()

      assert "No JavaScript runtime found" in str(context.value)

  def test_get_runtime_command_prefers_pnpm_when_lockfile_exists(self) -> None:
    """Test _get_runtime_command uses pnpm dlx when pnpm-lock.yaml exists."""
    with patch("supekku.scripts.lib.spec_sync.adapters.typescript.which") as mock_which:
      mock_which.return_value = "/usr/bin/pnpm"

      # Create a temporary directory with pnpm-lock.yaml
      with tempfile.TemporaryDirectory() as tmpdir:
        pkg_dir = Path(tmpdir)
        (pkg_dir / "pnpm-lock.yaml").touch()

        cmd = self.adapter._get_runtime_command(pkg_dir)
        assert cmd == ["pnpm", "dlx"]

  @patch("supekku.scripts.lib.spec_sync.adapters.typescript.which")
  def test_discover_targets_raises_when_no_runtime(self, mock_which) -> None:
    """Test discover_targets raises when no JS runtime available."""
    mock_which.return_value = None

    with pytest.raises(NodeRuntimeNotAvailableError) as context:
      self.adapter.discover_targets(self.repo_root)

    assert "No JavaScript runtime found" in str(context.value)

  @patch("supekku.scripts.lib.spec_sync.adapters.typescript.which")
  def test_generate_raises_when_no_runtime(self, mock_which) -> None:
    """Test generate raises when no JS runtime available."""
    mock_which.return_value = None

    unit = SourceUnit("typescript", "src", self.repo_root)
    spec_dir = Path("/test/spec/SPEC-001")

    with pytest.raises(NodeRuntimeNotAvailableError) as context:
      self.adapter.generate(unit, spec_dir=spec_dir)

    assert "No JavaScript runtime found" in str(context.value)

  def test_describe_typescript_package(self) -> None:
    """Test describe method generates correct metadata for TS packages."""
    unit = SourceUnit("typescript", "packages/core", self.repo_root)
    descriptor = self.adapter.describe(unit)

    # Check slug parts
    assert descriptor.slug_parts == ["packages", "core"]

    # Check frontmatter
    assert "sources" in descriptor.default_frontmatter
    sources = descriptor.default_frontmatter["sources"]
    assert len(sources) == 1
    assert sources[0]["language"] == "typescript"
    assert sources[0]["identifier"] == "packages/core"

    # Check variants
    assert len(descriptor.variants) == 2
    variant_names = [v.name for v in descriptor.variants]
    assert "public" in variant_names
    assert "internal" in variant_names

  def test_describe_rejects_non_typescript_unit(self) -> None:
    """Test describe method rejects non-TypeScript source units."""
    unit = SourceUnit("python", "some/module.py", self.repo_root)

    with pytest.raises(ValueError) as context:
      self.adapter.describe(unit)

    assert "TypeScriptAdapter cannot process python units" in str(context.value)

  def test_generate_rejects_non_typescript_unit(self) -> None:
    """Test generate method rejects non-TypeScript source units."""
    unit = SourceUnit("python", "some/module.py", self.repo_root)
    spec_dir = Path("/test/spec/SPEC-001")

    with pytest.raises(ValueError) as context:
      self.adapter.generate(unit, spec_dir=spec_dir)

    assert "TypeScriptAdapter cannot process python units" in str(context.value)


class TestTypeScriptAdapterIntegration(unittest.TestCase):
  """Integration tests for TypeScript adapter."""

  def test_adapter_can_be_imported_and_instantiated(self) -> None:
    """Test that TypeScript adapter can be imported and instantiated."""
    from supekku.scripts.lib.spec_sync.adapters.typescript import (  # noqa: PLC0415
      TypeScriptAdapter,
    )

    repo_root = Path("/test/repo")
    adapter = TypeScriptAdapter(repo_root)

    assert adapter.language == "typescript"
    assert adapter.repo_root == repo_root

  def test_adapter_available_in_engine_defaults(self) -> None:
    """Test that TypeScript adapter is available in default engine adapters."""
    from supekku.scripts.lib.spec_sync.engine import SpecSyncEngine  # noqa: PLC0415

    engine = SpecSyncEngine(
      repo_root=Path("/test/repo"),
      tech_dir=Path("/test/repo/specify/tech"),
    )

    assert "typescript" in engine.adapters
    assert isinstance(engine.adapters["typescript"], TypeScriptAdapter)

  def test_engine_can_detect_typescript_support(self) -> None:
    """Test that engine can check for TypeScript support."""
    from supekku.scripts.lib.spec_sync.engine import SpecSyncEngine  # noqa: PLC0415

    engine = SpecSyncEngine(
      repo_root=Path("/test/repo"),
      tech_dir=Path("/test/repo/specify/tech"),
    )

    # Should have TypeScript adapter
    assert "typescript" in engine.adapters

    # Should be able to check identifier support
    ts_adapter = engine.adapters["typescript"]
    assert ts_adapter.supports_identifier("src/index.ts")
    assert not ts_adapter.supports_identifier("main.go")


if __name__ == "__main__":
  unittest.main()
