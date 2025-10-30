"""Tests for registry migration from v1 to v2 format."""

import unittest

from .registry_migration import (
    LanguageDetector,
    RegistryV2,
)


class TestRegistryV2(unittest.TestCase):
    """Test v2 registry model."""

    def test_create_empty(self) -> None:
        """Test creating empty v2 registry."""
        registry = RegistryV2.create_empty()

        assert registry.version == 2
        assert registry.languages == {}
        assert "created" in registry.metadata

    def test_load_from_dict(self) -> None:
        """Test loading v2 registry from dictionary."""
        data = {
            "version": 2,
            "languages": {
                "go": {"cmd": "SPEC-003"},
                "python": {"module.py": "SPEC-200"},
            },
            "metadata": {"created": "2025-01-15"},
        }

        registry = RegistryV2.from_dict(data)

        assert registry.version == 2
        assert len(registry.languages) == 2
        assert registry.get_spec_id("go", "cmd") == "SPEC-003"
        assert registry.get_spec_id("python", "module.py") == "SPEC-200"

    def test_add_source_unit(self) -> None:
        """Test adding source units to v2 registry."""
        registry = RegistryV2.create_empty()

        registry.add_source_unit("go", "cmd", "SPEC-003")
        registry.add_source_unit("python", "module.py", "SPEC-200")

        assert registry.get_spec_id("go", "cmd") == "SPEC-003"
        assert registry.get_spec_id("python", "module.py") == "SPEC-200"

    def test_get_all_source_units(self) -> None:
        """Test getting all source units across languages."""
        registry = RegistryV2.create_empty()
        registry.add_source_unit("go", "cmd", "SPEC-003")
        registry.add_source_unit("python", "module.py", "SPEC-200")

        all_units = registry.get_all_source_units()

        expected = {("go", "cmd"): "SPEC-003", ("python", "module.py"): "SPEC-200"}
        assert all_units == expected

    def test_backwards_compatibility_lookup(self) -> None:
        """Test backwards compatible lookup (assumes Go for unspecified language)."""
        registry = RegistryV2.create_empty()
        registry.add_source_unit("go", "cmd", "SPEC-003")

        # Should work with just package name (assumes Go)
        assert registry.get_spec_id_compat("cmd") == "SPEC-003"
        assert registry.get_spec_id_compat("nonexistent") is None


class TestLanguageDetector(unittest.TestCase):
    """Test language detection logic."""

    def setUp(self) -> None:
        self.detector = LanguageDetector()

    def test_detect_go_packages(self) -> None:
        """Test detection of Go packages."""
        go_packages = [
            "cmd",
            "internal/application/services/git",
            "tools/eventgen",
            "test/integration/search",
        ]

        for package in go_packages:
            with self.subTest(package=package):
                assert self.detector.detect_language(package) == "go"

    def test_detect_python_modules(self) -> None:
        """Test detection of Python modules."""
        python_modules = [
            "module.py",
            "package/submodule.py",
            "scripts/lib/sync_engine.py",
            "some_script.py",
        ]

        for module in python_modules:
            with self.subTest(module=module):
                assert self.detector.detect_language(module) == "python"

    def test_detect_unknown_language(self) -> None:
        """Test detection of unknown/ambiguous identifiers."""
        unknown_identifiers = ["some_ambiguous_thing", "README.md", "Dockerfile"]

        for identifier in unknown_identifiers:
            with self.subTest(identifier=identifier):
                # Should default to "go" for backwards compatibility
                assert self.detector.detect_language(identifier) == "go"

    def test_detect_uses_adapter_logic(self) -> None:
        """Test that detection uses the same logic as SpecSyncEngine adapters."""
        # Test cases that should match the adapter patterns
        test_cases = [
            # Go packages (from adapter patterns)
            ("cmd", "go"),
            ("internal/application/services/git", "go"),
            ("tools/eventgen", "go"),
            # Python modules (from adapter patterns)
            ("module.py", "python"),
            ("package/submodule.py", "python"),
            ("scripts/lib/sync_engine.py", "python"),
            # Edge cases
            ("ambiguous_package", "go"),  # Should default to Go
        ]

        for identifier, expected_language in test_cases:
            with self.subTest(identifier=identifier):
                detected = self.detector.detect_language(identifier)
                assert detected == expected_language, f"Expected {identifier} to be detected as {expected_language}, got {detected}"


if __name__ == "__main__":
    unittest.main()
