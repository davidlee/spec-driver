"""Tests for contract mirror tree builder."""

import json
import shutil
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from .mirror import (
  ContractMirrorTreeBuilder,
  extract_python_variant,
  go_mirror_entries,
  python_mirror_entries,
  python_module_to_path,
  read_python_module_name,
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
      "SPEC-007", self.contracts_dir, "src/combat/agent.zig",
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
      "SPEC-007", self.contracts_dir, "src/foo.zig",
    )
    assert len(entries) == 1
    assert entries[0].view == "public"

  def test_no_contracts(self) -> None:
    """Test empty contracts directory returns empty."""
    entries, warnings = zig_mirror_entries(
      "SPEC-007", self.contracts_dir, "src/foo.zig",
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
      "SPEC-003", self.contracts_dir, "internal/foo/bar",
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
      "SPEC-050", self.contracts_dir, "src/api.ts",
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
      "SPEC-050", self.contracts_dir, "src/api.ts",
    )
    assert len(entries) == 1
    assert entries[0].view == "public"


# --- Integration tests: ContractMirrorTreeBuilder ---


class TestContractMirrorTreeBuilder(unittest.TestCase):
  """Test ContractMirrorTreeBuilder end-to-end."""

  def setUp(self) -> None:
    """Set up temp repo with tech directory."""
    self.temp_dir = TemporaryDirectory()  # pylint: disable=consider-using-with
    self.repo_root = Path(self.temp_dir.name)
    self.tech_dir = self.repo_root / "specify" / "tech"
    self.tech_dir.mkdir(parents=True)
    self.builder = ContractMirrorTreeBuilder(self.repo_root, self.tech_dir)

  def tearDown(self) -> None:
    """Clean up temp directory."""
    self.temp_dir.cleanup()

  def _create_registry(self, languages: dict) -> None:
    registry = {"version": 2, "languages": languages, "metadata": {}}
    self.builder.registry_path.write_text(
      json.dumps(registry), encoding="utf-8",
    )

  def _create_python_contract(
    self, spec_id: str, filename: str, module_name: str,
  ) -> None:
    contracts_dir = self.tech_dir / spec_id / "contracts"
    contracts_dir.mkdir(parents=True, exist_ok=True)
    (contracts_dir / filename).write_text(f"# {module_name}\n\nContract.")

  def _create_contract_file(
    self, spec_id: str, filename: str, content: str = "Contract.",
  ) -> None:
    contracts_dir = self.tech_dir / spec_id / "contracts"
    contracts_dir.mkdir(parents=True, exist_ok=True)
    (contracts_dir / filename).write_text(content)

  def test_rebuild_creates_mirror_dir(self) -> None:
    """Test rebuild creates .contracts/ directory."""
    self._create_registry({})
    self.builder.rebuild()
    assert self.builder.mirror_dir.exists()

  def test_rebuild_python_contracts(self) -> None:
    """Test Python contracts produce correct mirror symlinks."""
    self._create_registry({
      "python": {"supekku/scripts/lib/foo": "SPEC-100"},
    })
    self._create_python_contract(
      "SPEC-100", "supekku-scripts-lib-foo-bar-public.md",
      "supekku.scripts.lib.foo.bar",
    )

    warnings = self.builder.rebuild()

    link = (
      self.builder.mirror_dir
      / "public" / "supekku/scripts/lib/foo/bar.py.md"
    )
    assert link.exists()
    assert link.is_symlink()
    expected = (
      self.tech_dir / "SPEC-100" / "contracts"
      / "supekku-scripts-lib-foo-bar-public.md"
    )
    assert link.resolve() == expected.resolve()
    assert not warnings

  def test_rebuild_python_multiple_modules(self) -> None:
    """Test multiple Python modules in same SPEC."""
    self._create_registry({
      "python": {"supekku/scripts/lib/foo": "SPEC-100"},
    })
    self._create_python_contract(
      "SPEC-100", "foo-bar-public.md", "supekku.scripts.lib.foo.bar",
    )
    self._create_python_contract(
      "SPEC-100", "foo-baz-all.md", "supekku.scripts.lib.foo.baz",
    )

    self.builder.rebuild()

    pub_link = (
      self.builder.mirror_dir
      / "public" / "supekku/scripts/lib/foo/bar.py.md"
    )
    all_link = (
      self.builder.mirror_dir
      / "all" / "supekku/scripts/lib/foo/baz.py.md"
    )
    assert pub_link.exists()
    assert all_link.exists()

  def test_rebuild_zig_contracts(self) -> None:
    """Test Zig contracts produce correct mirror symlinks."""
    self._create_registry({
      "zig": {"src/combat/agent.zig": "SPEC-007"},
    })
    self._create_contract_file("SPEC-007", "interfaces.md")

    warnings = self.builder.rebuild()

    link = (
      self.builder.mirror_dir / "public" / "src/combat/agent.zig.md"
    )
    assert link.exists()
    assert link.is_symlink()
    assert not warnings

  def test_rebuild_zig_root_package(self) -> None:
    """Test Zig root package maps to __root__/ directory."""
    self._create_registry({"zig": {".": "SPEC-001"}})
    self._create_contract_file("SPEC-001", "interfaces.md")

    self.builder.rebuild()

    link = self.builder.mirror_dir / "public" / "__root__" / "interfaces.md"
    assert link.exists()
    assert link.is_symlink()

  def test_rebuild_go_contracts(self) -> None:
    """Test Go contracts produce correct package-based mirror paths."""
    self._create_registry({
      "go": {"internal/foo/bar": "SPEC-003"},
    })
    self._create_contract_file("SPEC-003", "interfaces.md")
    self._create_contract_file("SPEC-003", "internals.md")

    self.builder.rebuild()

    pub_link = (
      self.builder.mirror_dir
      / "public" / "internal/foo/bar/interfaces.md"
    )
    int_link = (
      self.builder.mirror_dir
      / "internal" / "internal/foo/bar/internals.md"
    )
    assert pub_link.exists()
    assert int_link.exists()

  def test_rebuild_ts_contracts(self) -> None:
    """Test TypeScript contracts produce correct mirror symlinks."""
    self._create_registry({
      "typescript": {"src/api.ts": "SPEC-050"},
    })
    self._create_contract_file("SPEC-050", "api.md")

    self.builder.rebuild()

    link = self.builder.mirror_dir / "public" / "src/api.ts.md"
    assert link.exists()

  def test_rebuild_creates_aliases(self) -> None:
    """Test alias symlinks are created for existing views."""
    self._create_registry({
      "python": {"supekku/scripts/lib/foo": "SPEC-100"},
    })
    self._create_python_contract(
      "SPEC-100", "foo-public.md", "supekku.scripts.lib.foo",
    )

    self.builder.rebuild()

    api_alias = self.builder.mirror_dir / "api"
    assert api_alias.is_symlink()
    assert api_alias.readlink() == Path("public")

  def test_alias_not_created_for_empty_view(self) -> None:
    """Test aliases are not created when target view is empty."""
    self._create_registry({})
    self.builder.rebuild()

    impl_alias = self.builder.mirror_dir / "implementation"
    assert not impl_alias.exists()

  def test_rebuild_cleans_stale(self) -> None:
    """Test rebuild removes stale entries from previous build."""
    self._create_registry({"zig": {"src/old.zig": "SPEC-001"}})
    self._create_contract_file("SPEC-001", "interfaces.md")
    self.builder.rebuild()

    old_link = self.builder.mirror_dir / "public" / "src/old.zig.md"
    assert old_link.exists()

    shutil.rmtree(self.tech_dir / "SPEC-001" / "contracts")
    self._create_registry({"zig": {"src/new.zig": "SPEC-002"}})
    self._create_contract_file("SPEC-002", "interfaces.md")
    self.builder.rebuild()

    assert not old_link.exists()
    new_link = self.builder.mirror_dir / "public" / "src/new.zig.md"
    assert new_link.exists()

  def test_rebuild_is_idempotent(self) -> None:
    """Test consecutive rebuilds produce identical results."""
    self._create_registry({"zig": {"src/foo.zig": "SPEC-001"}})
    self._create_contract_file("SPEC-001", "interfaces.md")

    self.builder.rebuild()
    self.builder.rebuild()

    link = self.builder.mirror_dir / "public" / "src/foo.zig.md"
    assert link.exists()
    assert link.is_symlink()

  def test_conflict_resolution(self) -> None:
    """Test conflicting mirror paths resolved by lowest SPEC ID."""
    self._create_registry({
      "python": {
        "supekku/a": "SPEC-004",
        "supekku/b": "SPEC-113",
      },
    })
    self._create_python_contract(
      "SPEC-004", "shared-module-public.md", "shared.module",
    )
    self._create_python_contract(
      "SPEC-113", "shared-module-public.md", "shared.module",
    )

    warnings = self.builder.rebuild()

    link = self.builder.mirror_dir / "public" / "shared/module.py.md"
    assert link.exists()
    expected = (
      self.tech_dir / "SPEC-004" / "contracts" / "shared-module-public.md"
    )
    assert link.resolve() == expected.resolve()
    assert any(
      "Conflict" in w and "SPEC-004 wins" in w
      for w in warnings
    )

  def test_missing_registry(self) -> None:
    """Test rebuild with missing registry produces warning."""
    warnings = self.builder.rebuild()
    assert any("Registry not found" in w for w in warnings)

  def test_symlinks_use_relative_paths(self) -> None:
    """Test symlink targets are relative, not absolute."""
    self._create_registry({"zig": {"src/foo.zig": "SPEC-007"}})
    self._create_contract_file("SPEC-007", "interfaces.md")

    self.builder.rebuild()

    link = self.builder.mirror_dir / "public" / "src/foo.zig.md"
    target = link.readlink()
    assert not target.is_absolute()

  def test_python_deduplicates_same_spec(self) -> None:
    """Two identifiers mapping to the same SPEC don't produce duplicates."""
    self._create_registry({
      "python": {
        "supekku/scripts/lib/foo": "SPEC-100",
        "supekku/scripts/lib/bar": "SPEC-100",
      },
    })
    self._create_python_contract(
      "SPEC-100", "mod-public.md", "some.module",
    )

    warnings = self.builder.rebuild()

    link = self.builder.mirror_dir / "public" / "some/module.py.md"
    assert link.exists()
    assert not any("Conflict" in w for w in warnings)

  def test_write_confinement(self) -> None:
    """Test rebuild writes only within .contracts/ (VT-CONTRACT-MIRROR-003)."""
    self._create_registry({
      "python": {"supekku/scripts/lib/foo": "SPEC-100"},
    })
    self._create_python_contract(
      "SPEC-100", "foo-public.md", "supekku.scripts.lib.foo",
    )

    # Snapshot all files/dirs outside .contracts/ before rebuild
    before = set()
    for p in self.repo_root.rglob("*"):
      rel = p.relative_to(self.repo_root)
      if not str(rel).startswith(".contracts"):
        before.add((str(rel), p.stat().st_mtime_ns))

    self.builder.rebuild()

    # Verify nothing outside .contracts/ was modified or created
    after = set()
    for p in self.repo_root.rglob("*"):
      rel = p.relative_to(self.repo_root)
      if not str(rel).startswith(".contracts"):
        after.add((str(rel), p.stat().st_mtime_ns))

    assert before == after, (
      f"Files outside .contracts/ changed: {before.symmetric_difference(after)}"
    )

  def test_rebuild_removes_all_stale_views(self) -> None:
    """Test rebuild removes entire stale view directories."""
    # Build with contracts producing an "all" view
    self._create_registry({
      "python": {"supekku/scripts/lib/foo": "SPEC-100"},
    })
    self._create_python_contract(
      "SPEC-100", "foo-all.md", "supekku.scripts.lib.foo",
    )
    self.builder.rebuild()

    all_dir = self.builder.mirror_dir / "all"
    impl_alias = self.builder.mirror_dir / "implementation"
    assert all_dir.exists()
    assert impl_alias.is_symlink()

    # Rebuild with no contracts at all
    shutil.rmtree(self.tech_dir / "SPEC-100" / "contracts")
    self._create_registry({})
    self.builder.rebuild()

    assert not all_dir.exists()
    assert not impl_alias.exists()


if __name__ == "__main__":
  unittest.main()
