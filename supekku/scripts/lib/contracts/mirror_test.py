"""Tests for contract mirror tree builder."""

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from supekku.scripts.lib.core.paths import SPEC_DRIVER_DIR, TECH_SPECS_SUBDIR

from .mirror import (
  ContractMirrorTreeBuilder,
  extract_python_variant,
  go_mirror_entries,
  python_mirror_entries,
  python_module_to_path,
  python_staging_dir,
  read_python_module_name,
  resolve_go_variant_outputs,
  resolve_ts_variant_outputs,
  resolve_zig_variant_outputs,
  ts_mirror_entries,
  zig_mirror_entries,
)

# --- Unit tests: pure mapping functions ---


class TestPythonModuleToPath(unittest.TestCase):
  """Test dotted module name to file path conversion."""

  def test_simple_module(self) -> None:
    """Test two-segment dotted name."""
    assert python_module_to_path("foo.bar") == "foo/bar.py"

  def test_deep_module(self) -> None:
    """Test deeply nested module path."""
    result = python_module_to_path("supekku.scripts.lib.specs.index")
    assert result == "supekku/scripts/lib/specs/index.py"

  def test_single_segment(self) -> None:
    """Test single-segment module name."""
    assert python_module_to_path("module") == "module.py"


class TestExtractPythonVariant(unittest.TestCase):
  """Test variant extraction from Python contract filenames."""

  def test_public_variant(self) -> None:
    """Test extracting 'public' variant."""
    assert extract_python_variant("foo-bar-public.md") == "public"

  def test_all_variant(self) -> None:
    """Test extracting 'all' variant."""
    assert extract_python_variant("foo-bar-all.md") == "all"

  def test_tests_variant(self) -> None:
    """Test extracting 'tests' variant from test module."""
    assert extract_python_variant("foo_test-tests.md") == "tests"

  def test_unknown_variant(self) -> None:
    """Test unknown variant returns None."""
    assert extract_python_variant("foo-bar-unknown.md") is None

  def test_no_hyphen(self) -> None:
    """Test filename without hyphen returns None."""
    assert extract_python_variant("interfaces.md") is None

  def test_empty_stem(self) -> None:
    """Test bare .md returns None."""
    assert extract_python_variant(".md") is None

  def test_realistic_filename(self) -> None:
    """Test real-world contract filename."""
    result = extract_python_variant(
      "supekku-scripts-lib-specs-index-public.md",
    )
    assert result == "public"

  def test_test_module_filename(self) -> None:
    """Test real-world test module contract filename."""
    result = extract_python_variant(
      "supekku-scripts-lib-specs-creation_test-tests.md",
    )
    assert result == "tests"


class TestReadPythonModuleName(unittest.TestCase):
  """Test reading module name from contract header."""

  def setUp(self) -> None:
    """Set up temp directory."""
    self.temp_dir = TemporaryDirectory()  # pylint: disable=consider-using-with
    self.dir = Path(self.temp_dir.name)

  def tearDown(self) -> None:
    """Clean up temp directory."""
    self.temp_dir.cleanup()

  def test_reads_module_name(self) -> None:
    """Test reading simple dotted module name from header."""
    p = self.dir / "test.md"
    p.write_text("# foo.bar.baz\n\nContent")
    assert read_python_module_name(p) == "foo.bar.baz"

  def test_reads_with_description(self) -> None:
    """Test reading header followed by description text."""
    p = self.dir / "test.md"
    p.write_text("# supekku.scripts.lib.specs.index\n\nSpec index management.")
    assert read_python_module_name(p) == "supekku.scripts.lib.specs.index"

  def test_returns_none_for_no_header(self) -> None:
    """Test file without markdown header returns None."""
    p = self.dir / "test.md"
    p.write_text("No header here\n\nContent")
    assert read_python_module_name(p) is None

  def test_returns_none_for_missing_file(self) -> None:
    """Test nonexistent file returns None."""
    assert read_python_module_name(Path("/nonexistent/file.md")) is None

  def test_returns_none_for_empty_file(self) -> None:
    """Test empty file returns None."""
    p = self.dir / "empty.md"
    p.write_text("")
    assert read_python_module_name(p) is None


class TestPythonMirrorEntries(unittest.TestCase):
  """Test Python contract mirror entry production."""

  def setUp(self) -> None:
    """Set up temp contracts directory."""
    self.temp_dir = TemporaryDirectory()  # pylint: disable=consider-using-with
    self.contracts_dir = Path(self.temp_dir.name)

  def tearDown(self) -> None:
    """Clean up temp directory."""
    self.temp_dir.cleanup()

  def _create_contract(self, filename: str, header: str) -> None:
    p = self.contracts_dir / filename
    p.write_text(f"# {header}\n\nContract content.")

  def test_produces_entry(self) -> None:
    """Test single contract produces correct entry."""
    self._create_contract("foo-bar-public.md", "foo.bar")
    entries, warnings = python_mirror_entries("SPEC-001", self.contracts_dir)
    assert len(entries) == 1
    assert entries[0].view == "public"
    assert entries[0].mirror_path == "foo/bar.py.md"
    assert entries[0].spec_id == "SPEC-001"
    assert not warnings

  def test_multiple_variants(self) -> None:
    """Test same module with multiple variants."""
    self._create_contract("foo-bar-public.md", "foo.bar")
    self._create_contract("foo-bar-all.md", "foo.bar")
    entries, _ = python_mirror_entries("SPEC-001", self.contracts_dir)
    assert len(entries) == 2
    views = {e.view for e in entries}
    assert views == {"public", "all"}

  def test_multiple_modules(self) -> None:
    """Test multiple module contracts in same SPEC."""
    self._create_contract("mod-a-public.md", "pkg.mod_a")
    self._create_contract("mod-b-public.md", "pkg.mod_b")
    entries, _ = python_mirror_entries("SPEC-001", self.contracts_dir)
    assert len(entries) == 2
    paths = {e.mirror_path for e in entries}
    assert paths == {"pkg/mod_a.py.md", "pkg/mod_b.py.md"}

  def test_skips_non_variant_files(self) -> None:
    """Test files without known variant suffix are skipped."""
    self._create_contract("interfaces.md", "foo.bar")
    entries, _ = python_mirror_entries("SPEC-001", self.contracts_dir)
    assert len(entries) == 0

  def test_warns_on_unreadable_header(self) -> None:
    """Test warning when contract has no parseable header."""
    p = self.contracts_dir / "bad-public.md"
    p.write_text("No header line")
    entries, warnings = python_mirror_entries("SPEC-001", self.contracts_dir)
    assert len(entries) == 0
    assert len(warnings) == 1

  def test_nonexistent_dir(self) -> None:
    """Test nonexistent contracts directory returns empty."""
    entries, warnings = python_mirror_entries("SPEC-001", Path("/nonexistent"))
    assert not entries
    assert not warnings


class TestZigMirrorEntries(unittest.TestCase):
  """Test Zig contract mirror entry production."""

  def setUp(self) -> None:
    """Set up temp contracts directory."""
    self.temp_dir = TemporaryDirectory()  # pylint: disable=consider-using-with
    self.contracts_dir = Path(self.temp_dir.name)

  def tearDown(self) -> None:
    """Clean up temp directory."""
    self.temp_dir.cleanup()

  def test_file_based_identifier(self) -> None:
    """Test Zig file identifier produces entries for both views."""
    (self.contracts_dir / "interfaces.md").write_text("Public API")
    (self.contracts_dir / "internals.md").write_text("Internals")
    entries, _ = zig_mirror_entries(
      "SPEC-007",
      self.contracts_dir,
      "src/combat/agent.zig",
    )
    assert len(entries) == 2
    public = next(e for e in entries if e.view == "public")
    internal = next(e for e in entries if e.view == "internal")
    assert public.mirror_path == "src/combat/agent.zig.md"
    assert internal.mirror_path == "src/combat/agent.zig.md"

  def test_root_package(self) -> None:
    """Test root package '.' maps to __root__/ directory."""
    (self.contracts_dir / "interfaces.md").write_text("Root API")
    (self.contracts_dir / "internals.md").write_text("Root internals")
    entries, _ = zig_mirror_entries("SPEC-001", self.contracts_dir, ".")
    assert len(entries) == 2
    public = next(e for e in entries if e.view == "public")
    internal = next(e for e in entries if e.view == "internal")
    assert public.mirror_path == "__root__/interfaces.md"
    assert internal.mirror_path == "__root__/internals.md"

  def test_missing_variant(self) -> None:
    """Test only existing contract files produce entries."""
    (self.contracts_dir / "interfaces.md").write_text("Public API")
    entries, _ = zig_mirror_entries(
      "SPEC-007",
      self.contracts_dir,
      "src/foo.zig",
    )
    assert len(entries) == 1
    assert entries[0].view == "public"

  def test_no_contracts(self) -> None:
    """Test empty contracts directory returns empty."""
    entries, warnings = zig_mirror_entries(
      "SPEC-007",
      self.contracts_dir,
      "src/foo.zig",
    )
    assert not entries
    assert not warnings


class TestGoMirrorEntries(unittest.TestCase):
  """Test Go contract mirror entry production."""

  def setUp(self) -> None:
    """Set up temp contracts directory."""
    self.temp_dir = TemporaryDirectory()  # pylint: disable=consider-using-with
    self.contracts_dir = Path(self.temp_dir.name)

  def tearDown(self) -> None:
    """Clean up temp directory."""
    self.temp_dir.cleanup()

  def test_package_based(self) -> None:
    """Test Go package identifier preserves contract filename in path."""
    (self.contracts_dir / "interfaces.md").write_text("Public API")
    (self.contracts_dir / "internals.md").write_text("Internals")
    entries, _ = go_mirror_entries(
      "SPEC-003",
      self.contracts_dir,
      "internal/foo/bar",
    )
    assert len(entries) == 2
    public = next(e for e in entries if e.view == "public")
    internal = next(e for e in entries if e.view == "internal")
    assert public.mirror_path == "internal/foo/bar/interfaces.md"
    assert internal.mirror_path == "internal/foo/bar/internals.md"


class TestTsMirrorEntries(unittest.TestCase):
  """Test TypeScript contract mirror entry production."""

  def setUp(self) -> None:
    """Set up temp contracts directory."""
    self.temp_dir = TemporaryDirectory()  # pylint: disable=consider-using-with
    self.contracts_dir = Path(self.temp_dir.name)

  def tearDown(self) -> None:
    """Clean up temp directory."""
    self.temp_dir.cleanup()

  def test_file_based(self) -> None:
    """Test TS file identifier produces entries for both views."""
    (self.contracts_dir / "api.md").write_text("Public API")
    (self.contracts_dir / "internal.md").write_text("Internal")
    entries, _ = ts_mirror_entries(
      "SPEC-050",
      self.contracts_dir,
      "src/api.ts",
    )
    assert len(entries) == 2
    public = next(e for e in entries if e.view == "public")
    internal = next(e for e in entries if e.view == "internal")
    assert public.mirror_path == "src/api.ts.md"
    assert internal.mirror_path == "src/api.ts.md"

  def test_missing_variant(self) -> None:
    """Test only existing contract files produce entries."""
    (self.contracts_dir / "api.md").write_text("Public API")
    entries, _ = ts_mirror_entries(
      "SPEC-050",
      self.contracts_dir,
      "src/api.ts",
    )
    assert len(entries) == 1
    assert entries[0].view == "public"


# --- Pre-generation path resolver tests ---


class TestResolveGoVariantOutputs(unittest.TestCase):
  """Test Go pre-generation path resolution."""

  def test_standard_package(self) -> None:
    """Test Go package produces dir/filename canonical paths."""
    root = Path("/repo/.contracts")
    result = resolve_go_variant_outputs("internal/foo/bar", root)
    assert result == {
      "public": root / "public" / "internal/foo/bar" / "interfaces.md",
      "internal": root / "internal" / "internal/foo/bar" / "internals.md",
    }

  def test_simple_package(self) -> None:
    """Test single-segment Go package."""
    root = Path("/repo/.contracts")
    result = resolve_go_variant_outputs("pkg", root)
    assert result == {
      "public": root / "public" / "pkg" / "interfaces.md",
      "internal": root / "internal" / "pkg" / "internals.md",
    }


class TestResolveZigVariantOutputs(unittest.TestCase):
  """Test Zig pre-generation path resolution."""

  def test_file_identifier(self) -> None:
    """Test Zig file produces {identifier}.md leaf."""
    root = Path("/repo/.contracts")
    result = resolve_zig_variant_outputs("src/combat/agent.zig", root)
    assert result == {
      "public": root / "public" / "src/combat/agent.zig.md",
      "internal": root / "internal" / "src/combat/agent.zig.md",
    }

  def test_root_package(self) -> None:
    """Test root '.' maps to __root__/ with original filenames."""
    root = Path("/repo/.contracts")
    result = resolve_zig_variant_outputs(".", root)
    assert result == {
      "public": root / "public" / "__root__" / "interfaces.md",
      "internal": root / "internal" / "__root__" / "internals.md",
    }


class TestResolveTsVariantOutputs(unittest.TestCase):
  """Test TypeScript pre-generation path resolution."""

  def test_file_identifier(self) -> None:
    """Test TS file produces {identifier}.md leaf with adapter variant names."""
    root = Path("/repo/.contracts")
    result = resolve_ts_variant_outputs("src/api.ts", root)
    assert result == {
      "api": root / "public" / "src/api.ts.md",
      "internal": root / "internal" / "src/api.ts.md",
    }


class TestPythonStagingDir(unittest.TestCase):
  """Test Python staging directory computation."""

  def test_package_identifier(self) -> None:
    """Test Python package identifier slugified correctly."""
    root = Path("/repo/.contracts")
    result = python_staging_dir("supekku/scripts/lib/foo", root)
    assert result == root / ".staging" / "python" / "supekku-scripts-lib-foo"

  def test_dotted_identifier(self) -> None:
    """Test dotted module names are slugified."""
    root = Path("/repo/.contracts")
    result = python_staging_dir("supekku.scripts.lib.foo", root)
    assert result == root / ".staging" / "python" / "supekku-scripts-lib-foo"


# --- Integration tests: ContractMirrorTreeBuilder ---


class TestContractMirrorTreeBuilder(unittest.TestCase):
  """Test ContractMirrorTreeBuilder: compat symlinks SPEC-*/contracts/ → .contracts/.

  Canonical contract files live in .contracts/<view>/<path>.
  rebuild() creates compat symlinks from SPEC-*/contracts/ pointing back
  into .contracts/ so that spec-relative tooling still works.
  """

  def setUp(self) -> None:
    """Set up temp repo with tech directory."""
    self.temp_dir = TemporaryDirectory()  # pylint: disable=consider-using-with
    self.repo_root = Path(self.temp_dir.name)
    self.tech_dir = self.repo_root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR
    self.tech_dir.mkdir(parents=True)
    self.contracts_root = self.repo_root / ".contracts"
    self.builder = ContractMirrorTreeBuilder(self.repo_root, self.tech_dir)

  def tearDown(self) -> None:
    """Clean up temp directory."""
    self.temp_dir.cleanup()

  def _create_registry(self, languages: dict) -> None:
    registry = {"version": 2, "languages": languages, "metadata": {}}
    self.builder.registry_path.write_text(
      json.dumps(registry),
      encoding="utf-8",
    )

  def _create_canonical(self, view: str, rel_path: str) -> Path:
    """Create a canonical contract file in .contracts/<view>/<rel_path>."""
    path = self.contracts_root / view / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("Contract.")
    return path

  def _compat_link(self, spec_id: str, view: str, rel_path: str) -> Path:
    """Return expected compat symlink path in SPEC-*/contracts/."""
    return self.tech_dir / spec_id / "contracts" / view / rel_path

  # -- basic wiring --

  def test_missing_registry(self) -> None:
    """Test rebuild with missing registry produces warning."""
    warnings = self.builder.rebuild()
    assert any("Registry not found" in w for w in warnings)

  def test_empty_registry(self) -> None:
    """Test rebuild with empty registry is a no-op."""
    self._create_registry({})
    warnings = self.builder.rebuild()
    assert not warnings

  # -- per-language compat symlinks --

  def test_zig_compat_symlinks(self) -> None:
    """Zig: compat symlinks in SPEC-*/contracts/ → .contracts/."""
    self._create_registry({"zig": {"src/combat/agent.zig": "SPEC-007"}})
    self._create_canonical("public", "src/combat/agent.zig.md")
    self._create_canonical("internal", "src/combat/agent.zig.md")

    warnings = self.builder.rebuild()

    pub = self._compat_link("SPEC-007", "public", "src/combat/agent.zig.md")
    int_ = self._compat_link("SPEC-007", "internal", "src/combat/agent.zig.md")
    assert pub.is_symlink()
    assert int_.is_symlink()
    assert (
      pub.resolve()
      == (self.contracts_root / "public" / "src/combat/agent.zig.md").resolve()
    )
    assert not warnings

  def test_zig_root_package(self) -> None:
    """Zig root package '.' maps to __root__/ directory."""
    self._create_registry({"zig": {".": "SPEC-001"}})
    self._create_canonical("public", "__root__/interfaces.md")

    self.builder.rebuild()

    link = self._compat_link("SPEC-001", "public", "__root__/interfaces.md")
    assert link.is_symlink()

  def test_go_compat_symlinks(self) -> None:
    """Go: compat symlinks mirror package-based paths."""
    self._create_registry({"go": {"internal/foo/bar": "SPEC-003"}})
    self._create_canonical("public", "internal/foo/bar/interfaces.md")
    self._create_canonical("internal", "internal/foo/bar/internals.md")

    self.builder.rebuild()

    pub = self._compat_link("SPEC-003", "public", "internal/foo/bar/interfaces.md")
    int_ = self._compat_link("SPEC-003", "internal", "internal/foo/bar/internals.md")
    assert pub.is_symlink()
    assert int_.is_symlink()

  def test_ts_compat_symlinks(self) -> None:
    """TypeScript: compat symlinks for file-based identifiers."""
    self._create_registry({"typescript": {"src/api.ts": "SPEC-050"}})
    self._create_canonical("public", "src/api.ts.md")

    self.builder.rebuild()

    link = self._compat_link("SPEC-050", "public", "src/api.ts.md")
    assert link.is_symlink()

  def test_python_compat_symlinks(self) -> None:
    """Python: compat symlinks for distributed contract files."""
    self._create_registry(
      {"python": {"supekku/scripts/lib/foo": "SPEC-100"}},
    )
    self._create_canonical(
      "public",
      "supekku/scripts/lib/foo/bar.py.md",
    )

    self.builder.rebuild()

    link = self._compat_link(
      "SPEC-100",
      "public",
      "supekku/scripts/lib/foo/bar.py.md",
    )
    assert link.is_symlink()

  # -- aliases --

  def test_aliases_created_in_contracts_root(self) -> None:
    """View aliases (api → public) created in .contracts/."""
    self._create_registry({"go": {"internal/foo": "SPEC-001"}})
    self._create_canonical("public", "internal/foo/interfaces.md")

    self.builder.rebuild()

    api_alias = self.contracts_root / "api"
    assert api_alias.is_symlink()
    assert api_alias.readlink() == Path("public")

  def test_alias_not_created_for_empty_view(self) -> None:
    """Aliases are not created when target view directory doesn't exist."""
    self._create_registry({})
    self.builder.rebuild()

    impl_alias = self.contracts_root / "implementation"
    assert not impl_alias.exists()

  # -- properties --

  def test_symlinks_use_relative_paths(self) -> None:
    """Compat symlink targets are relative, not absolute."""
    self._create_registry({"zig": {"src/foo.zig": "SPEC-007"}})
    self._create_canonical("public", "src/foo.zig.md")

    self.builder.rebuild()

    link = self._compat_link("SPEC-007", "public", "src/foo.zig.md")
    target = link.readlink()
    assert not target.is_absolute()

  def test_rebuild_is_idempotent(self) -> None:
    """Consecutive rebuilds produce identical results."""
    self._create_registry({"zig": {"src/foo.zig": "SPEC-001"}})
    self._create_canonical("public", "src/foo.zig.md")

    self.builder.rebuild()
    self.builder.rebuild()

    link = self._compat_link("SPEC-001", "public", "src/foo.zig.md")
    assert link.is_symlink()

  def test_canonical_files_not_modified(self) -> None:
    """Rebuild must not modify canonical .contracts/ files."""
    self._create_registry({"go": {"internal/foo": "SPEC-001"}})
    canonical = self._create_canonical("public", "internal/foo/interfaces.md")
    mtime_before = canonical.stat().st_mtime_ns

    self.builder.rebuild()

    assert canonical.stat().st_mtime_ns == mtime_before
    assert not canonical.is_symlink()

  def test_replaces_non_symlink_with_warning(self) -> None:
    """Replacing a real file in SPEC-*/contracts/ emits a warning."""
    self._create_registry({"zig": {"src/foo.zig": "SPEC-001"}})
    self._create_canonical("public", "src/foo.zig.md")

    # Pre-create a real file where the compat symlink should go
    compat = self._compat_link("SPEC-001", "public", "src/foo.zig.md")
    compat.parent.mkdir(parents=True, exist_ok=True)
    compat.write_text("stale real file")

    warnings = self.builder.rebuild()

    assert compat.is_symlink()
    assert any("non-symlink" in w for w in warnings)

  # -- drift warnings (VT-CONTRACTS-DRIFT-001) --

  def test_drift_warning_when_spec_has_contracts_but_no_canonical(self) -> None:
    """VT-CONTRACTS-DRIFT-001: warn on contracts/ with no canonical."""
    self._create_registry({"zig": {"src/foo.zig": "SPEC-001"}})
    # Create non-empty contracts/ in spec dir (pre-existing real files)
    spec_contracts = self.tech_dir / "SPEC-001" / "contracts"
    spec_contracts.mkdir(parents=True)
    (spec_contracts / "interfaces.md").write_text("stale contract")
    # Do NOT create any canonical .contracts/ entries

    warnings = self.builder.rebuild()

    assert any("drift" in w.lower() for w in warnings), (
      f"Expected drift warning, got: {warnings}"
    )

  def test_no_drift_warning_when_canonical_entries_exist(self) -> None:
    """No drift warning when canonical entries exist for the spec's unit."""
    self._create_registry({"zig": {"src/foo.zig": "SPEC-001"}})
    spec_contracts = self.tech_dir / "SPEC-001" / "contracts"
    spec_contracts.mkdir(parents=True)
    (spec_contracts / "interfaces.md").write_text("old contract")
    # Canonical entry exists
    self._create_canonical("public", "src/foo.zig.md")

    warnings = self.builder.rebuild()

    assert not any("drift" in w.lower() for w in warnings), (
      f"Unexpected drift warning: {warnings}"
    )

  def test_no_drift_warning_for_empty_contracts_dir(self) -> None:
    """Empty contracts/ dir does NOT trigger drift warning (no false positives)."""
    self._create_registry({"zig": {"src/foo.zig": "SPEC-001"}})
    spec_contracts = self.tech_dir / "SPEC-001" / "contracts"
    spec_contracts.mkdir(parents=True)
    # Empty — no .md files

    warnings = self.builder.rebuild()

    assert not any("drift" in w.lower() for w in warnings)

  def test_no_drift_warning_when_contracts_dir_missing(self) -> None:
    """No drift warning when SPEC has no contracts/ directory at all."""
    self._create_registry({"zig": {"src/foo.zig": "SPEC-001"}})
    (self.tech_dir / "SPEC-001").mkdir(parents=True)
    # No contracts/ subdir

    warnings = self.builder.rebuild()

    assert not any("drift" in w.lower() for w in warnings)

  def test_drift_warning_python_spec(self) -> None:
    """Drift warning fires for Python specs with contracts but no canonical."""
    self._create_registry({"python": {"supekku/lib/foo": "SPEC-200"}})
    spec_contracts = self.tech_dir / "SPEC-200" / "contracts"
    spec_contracts.mkdir(parents=True)
    (spec_contracts / "foo-public.md").write_text("# supekku.lib.foo\nold")

    warnings = self.builder.rebuild()

    assert any("drift" in w.lower() for w in warnings)


if __name__ == "__main__":
  unittest.main()
