"""Tests for the multi-language SpecSyncEngine."""

import unittest
from pathlib import Path
from unittest.mock import Mock

from .engine import SpecSyncEngine
from .models import DocVariant, SourceDescriptor, SourceUnit


class TestSpecSyncEngine(unittest.TestCase):
    """Test SpecSyncEngine functionality."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.repo_root = Path("/test/repo")
        self.tech_dir = Path("/test/repo/specify/tech")

        # Create mock adapters
        self.mock_go_adapter = Mock()
        self.mock_go_adapter.language = "go"
        self.mock_go_adapter.discover_targets.return_value = []  # Default empty return

        self.mock_python_adapter = Mock()
        self.mock_python_adapter.language = "python"
        self.mock_python_adapter.discover_targets.return_value = []  # Default empty return

        self.adapters = {
            "go": self.mock_go_adapter,
            "python": self.mock_python_adapter,
        }

        self.engine = SpecSyncEngine(
            repo_root=self.repo_root, tech_dir=self.tech_dir, adapters=self.adapters,
        )

    def test_initialization_with_default_adapters(self) -> None:
        """Test engine initialization with default adapters."""
        engine = SpecSyncEngine(repo_root=self.repo_root, tech_dir=self.tech_dir)

        # Should have default Go, Python, and TypeScript adapters
        assert "go" in engine.adapters
        assert "python" in engine.adapters
        assert "typescript" in engine.adapters
        assert len(engine.adapters) == 3

    def test_initialization_with_custom_adapters(self) -> None:
        """Test engine initialization with custom adapters."""
        assert self.engine.repo_root == self.repo_root
        assert self.engine.tech_dir == self.tech_dir
        assert len(self.engine.adapters) == 2
        assert "go" in self.engine.adapters
        assert "python" in self.engine.adapters

    def test_get_supported_languages(self) -> None:
        """Test getting list of supported languages."""
        languages = self.engine.get_supported_languages()
        assert "go" in languages
        assert "python" in languages
        assert len(languages) == 2

    def test_get_adapter(self) -> None:
        """Test getting adapter for specific language."""
        go_adapter = self.engine.get_adapter("go")
        python_adapter = self.engine.get_adapter("python")
        unknown_adapter = self.engine.get_adapter("typescript")

        assert go_adapter == self.mock_go_adapter
        assert python_adapter == self.mock_python_adapter
        assert unknown_adapter is None

    def test_add_adapter(self) -> None:
        """Test adding new adapter."""
        mock_ts_adapter = Mock()
        mock_ts_adapter.language = "typescript"

        self.engine.add_adapter("typescript", mock_ts_adapter)

        assert "typescript" in self.engine.adapters
        assert self.engine.get_adapter("typescript") == mock_ts_adapter

    def test_supports_identifier(self) -> None:
        """Test identifier support detection."""
        # Setup mock responses
        self.mock_go_adapter.supports_identifier.side_effect = lambda x: x.startswith(
            "internal/",
        )
        self.mock_python_adapter.supports_identifier.side_effect = lambda x: x.endswith(
            ".py",
        )

        # Test Go identifier
        go_result = self.engine.supports_identifier("internal/package")
        assert go_result == "go"

        # Test Python identifier
        python_result = self.engine.supports_identifier("module.py")
        assert python_result == "python"

        # Test unsupported identifier
        unknown_result = self.engine.supports_identifier("unknown.xyz")
        assert unknown_result is None

    def test_synchronize_all_languages(self) -> None:
        """Test synchronization across all languages."""
        # Setup mock source units
        go_unit = SourceUnit("go", "internal/test", self.repo_root)
        python_unit = SourceUnit("python", "module.py", self.repo_root)

        # Setup mock adapter responses
        self.mock_go_adapter.discover_targets.return_value = [go_unit]
        self.mock_python_adapter.discover_targets.return_value = [python_unit]

        # Setup mock describe responses
        go_descriptor = SourceDescriptor(
            slug_parts=["internal", "test"], default_frontmatter={}, variants=[],
        )
        python_descriptor = SourceDescriptor(
            slug_parts=["module"], default_frontmatter={}, variants=[],
        )

        self.mock_go_adapter.describe.return_value = go_descriptor
        self.mock_python_adapter.describe.return_value = python_descriptor

        # Setup mock generate responses
        go_variants = [DocVariant("public", Path("test.md"), "hash1", "created")]
        python_variants = [DocVariant("api", Path("test.md"), "hash2", "created")]

        self.mock_go_adapter.generate.return_value = go_variants
        self.mock_python_adapter.generate.return_value = python_variants

        # Run synchronization
        result = self.engine.synchronize()

        # Verify results
        assert len(result.processed_units) == 2
        assert len(result.created_specs) == 2
        assert "go:internal/test" in result.created_specs
        assert "python:module.py" in result.created_specs

        # Verify adapter calls
        self.mock_go_adapter.discover_targets.assert_called_once()
        self.mock_python_adapter.discover_targets.assert_called_once()
        self.mock_go_adapter.describe.assert_called_once_with(go_unit)
        self.mock_python_adapter.describe.assert_called_once_with(python_unit)
        self.mock_go_adapter.generate.assert_called_once_with(go_unit, check=False)
        self.mock_python_adapter.generate.assert_called_once_with(
            python_unit, check=False,
        )

    def test_synchronize_specific_languages(self) -> None:
        """Test synchronization with specific language filter."""
        # Setup mock
        go_unit = SourceUnit("go", "internal/test", self.repo_root)
        self.mock_go_adapter.discover_targets.return_value = [go_unit]
        self.mock_go_adapter.describe.return_value = SourceDescriptor(
            slug_parts=["internal", "test"], default_frontmatter={}, variants=[],
        )
        self.mock_go_adapter.generate.return_value = []

        # Run synchronization for Go only
        self.engine.synchronize(languages=["go"])

        # Verify only Go adapter was called
        self.mock_go_adapter.discover_targets.assert_called_once()
        self.mock_python_adapter.discover_targets.assert_not_called()

    def test_synchronize_with_targets(self) -> None:
        """Test synchronization with specific targets."""
        # Setup mock
        go_unit = SourceUnit("go", "internal/test", self.repo_root)
        self.mock_go_adapter.discover_targets.return_value = [go_unit]
        self.mock_go_adapter.describe.return_value = SourceDescriptor(
            slug_parts=["internal", "test"], default_frontmatter={}, variants=[],
        )
        self.mock_go_adapter.generate.return_value = []

        # Run synchronization with specific targets
        targets = ["go:internal/test"]
        self.engine.synchronize(targets=targets)

        # Verify adapter was called with correct targets
        self.mock_go_adapter.discover_targets.assert_called_once_with(
            self.repo_root, requested=["internal/test"],
        )

    def test_synchronize_with_auto_detected_targets(self) -> None:
        """Test synchronization with auto-detected language targets."""
        # Setup mock for language detection
        self.mock_go_adapter.supports_identifier.return_value = True
        self.mock_python_adapter.supports_identifier.return_value = False

        # Setup mock for processing
        go_unit = SourceUnit("go", "internal/test", self.repo_root)
        self.mock_go_adapter.discover_targets.return_value = [go_unit]
        self.mock_go_adapter.describe.return_value = SourceDescriptor(
            slug_parts=["internal", "test"], default_frontmatter={}, variants=[],
        )
        self.mock_go_adapter.generate.return_value = []

        # Run synchronization with target that Go adapter supports
        targets = ["internal/test"]
        self.engine.synchronize(targets=targets)

        # Verify Go adapter was called with the target
        self.mock_go_adapter.discover_targets.assert_called_once_with(
            self.repo_root, requested=["internal/test"],
        )

    def test_synchronize_check_mode(self) -> None:
        """Test synchronization in check mode."""
        # Setup mock
        go_unit = SourceUnit("go", "internal/test", self.repo_root)
        self.mock_go_adapter.discover_targets.return_value = [go_unit]
        self.mock_go_adapter.describe.return_value = SourceDescriptor(
            slug_parts=["internal", "test"], default_frontmatter={}, variants=[],
        )
        self.mock_go_adapter.generate.return_value = []

        # Run synchronization in check mode
        result = self.engine.synchronize(check=True)

        # Verify check=True was passed to generate
        self.mock_go_adapter.generate.assert_called_once_with(go_unit, check=True)

        # Verify no specs were "created" in check mode
        assert len(result.created_specs) == 0

    def test_synchronize_handles_no_source_units(self) -> None:
        """Test synchronization when no source units are found."""
        # Setup mock to return no units
        self.mock_go_adapter.discover_targets.return_value = []
        self.mock_python_adapter.discover_targets.return_value = []

        # Run synchronization
        result = self.engine.synchronize()

        # Verify warnings are generated
        assert len(result.processed_units) == 0
        assert len(result.warnings) == 2
        assert "No source units found for language: go" in result.warnings
        assert "No source units found for language: python" in result.warnings

    def test_synchronize_handles_adapter_errors(self) -> None:
        """Test synchronization handles adapter errors gracefully."""
        # Setup mock to raise exception
        self.mock_go_adapter.discover_targets.side_effect = Exception(
            "Go adapter error",
        )
        self.mock_python_adapter.discover_targets.return_value = []

        # Run synchronization
        result = self.engine.synchronize()

        # Verify error handling
        assert len(result.processed_units) == 0
        assert len(result.errors) == 1
        assert "Error processing language go: Go adapter error" in result.errors

    def test_synchronize_handles_unit_processing_errors(self) -> None:
        """Test synchronization handles individual unit processing errors."""
        # Setup mock - only test Go to avoid Python warning
        go_unit = SourceUnit("go", "internal/test", self.repo_root)
        self.mock_go_adapter.discover_targets.return_value = [go_unit]
        self.mock_go_adapter.describe.side_effect = Exception("Description error")

        # Run synchronization for Go only
        result = self.engine.synchronize(languages=["go"])

        # Verify error handling
        assert len(result.processed_units) == 0
        assert len(result.errors) == 1
        assert "Error processing internal/test: Description error" in result.errors
        assert "internal/test (error)" in result.skipped_units


if __name__ == "__main__":
    unittest.main()
