"""Tests for RequirementsRegistry public API and query surface."""

from __future__ import annotations

import os
import tempfile
import textwrap
import unittest
from pathlib import Path

from supekku.scripts.lib.core.paths import (
  SPEC_DRIVER_DIR,
  TECH_SPECS_SUBDIR,
  get_registry_dir,
)
from supekku.scripts.lib.core.spec_utils import dump_markdown_file
from supekku.scripts.lib.requirements.lifecycle import (
  STATUS_ACTIVE,
  STATUS_DEPRECATED,
  STATUS_PENDING,
  STATUS_SUPERSEDED,
  TERMINAL_STATUSES,
)
from supekku.scripts.lib.requirements.registry import (
  RequirementRecord,
  RequirementsRegistry,
)
from supekku.scripts.lib.specs.registry import SpecRegistry


class TestRequirementsRegistryReverseQueries(unittest.TestCase):
  """Test reverse relationship query methods for RequirementsRegistry."""

  def setUp(self) -> None:
    self._cwd = Path.cwd()

  def tearDown(self) -> None:
    os.chdir(self._cwd)

  def _make_repo(self) -> Path:
    tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.addCleanup(tmpdir.cleanup)
    root = Path(tmpdir.name)
    (root / ".git").mkdir()
    os.chdir(root)
    return root

  def _write_spec_with_requirements(
    self, root: Path, spec_id: str, requirements: list[str]
  ) -> None:
    """Write a spec file with specific requirements."""
    spec_dir = root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR / f"{spec_id.lower()}-example"
    spec_dir.mkdir(parents=True, exist_ok=True)
    spec_path = spec_dir / f"{spec_id}.md"

    req_lines = "\n".join(f"- {req}" for req in requirements)
    body = f"# {spec_id}\n\n## 6. Quality & Operational Requirements\n\n{req_lines}\n"

    frontmatter = {
      "id": spec_id,
      "slug": spec_id.lower(),
      "name": f"Spec {spec_id}",
      "created": "2024-06-01",
      "updated": "2024-06-01",
      "status": "draft",
      "kind": "spec",
    }
    dump_markdown_file(spec_path, frontmatter, body)

  def _create_registry_with_verification(self, root: Path) -> RequirementsRegistry:
    """Create requirements registry and manually add verification metadata."""
    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)
    spec_registry = SpecRegistry(root)

    spec_dirs = [root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR]
    registry.sync_from_specs(spec_dirs, spec_registry=spec_registry)

    # Manually add verification metadata to requirements
    # This simulates what would happen after coverage blocks are processed
    if "SPEC-001.FR-001" in registry.records:
      registry.records["SPEC-001.FR-001"].verified_by = ["VT-CLI-001"]
      registry.records["SPEC-001.FR-001"].coverage_evidence = ["VT-PROD010-001"]

    if "SPEC-001.FR-002" in registry.records:
      registry.records["SPEC-001.FR-002"].verified_by = ["VA-REVIEW-001"]
      registry.records["SPEC-001.FR-002"].coverage_evidence = []

    if "SPEC-001.NF-020" in registry.records:
      registry.records["SPEC-001.NF-020"].verified_by = []
      registry.records["SPEC-001.NF-020"].coverage_evidence = [
        "VT-CLI-001",
        "VT-CLI-002",
      ]

    return registry

  def test_find_by_verified_by_exact_match(self) -> None:
    """Test finding requirements verified by specific artifact (exact match)."""
    root = self._make_repo()
    self._write_spec_with_requirements(
      root, "SPEC-001", ["FR-001: First requirement", "FR-002: Second requirement"]
    )

    registry = self._create_registry_with_verification(root)

    # Find requirement verified by VT-CLI-001
    requirements = registry.find_by_verified_by("VT-CLI-001")

    assert isinstance(requirements, list)
    assert len(requirements) == 1
    assert requirements[0].uid == "SPEC-001.FR-001"

  def test_find_by_verified_by_searches_both_fields(self) -> None:
    """Test that find_by_verified_by searches both verified_by and coverage_evidence."""
    root = self._make_repo()
    self._write_spec_with_requirements(
      root,
      "SPEC-001",
      ["FR-001: First requirement", "NF-020: Performance requirement"],
    )

    registry = self._create_registry_with_verification(root)

    # VT-CLI-001 appears in verified_by for FR-001 and coverage_evidence for NF-020
    requirements = registry.find_by_verified_by("VT-CLI-001")

    assert isinstance(requirements, list)
    assert len(requirements) == 2
    uids = {r.uid for r in requirements}
    assert "SPEC-001.FR-001" in uids
    assert "SPEC-001.NF-020" in uids

  def test_find_by_verified_by_glob_pattern(self) -> None:
    """Test finding requirements with glob pattern matching."""
    root = self._make_repo()
    self._write_spec_with_requirements(
      root,
      "SPEC-001",
      [
        "FR-001: First requirement",
        "FR-002: Second requirement",
        "NF-020: Performance",
      ],
    )

    registry = self._create_registry_with_verification(root)

    # Find all requirements verified by VT-CLI-* pattern
    requirements = registry.find_by_verified_by("VT-CLI-*")

    assert isinstance(requirements, list)
    assert len(requirements) == 2  # FR-001 and NF-020 have VT-CLI artifacts
    uids = {r.uid for r in requirements}
    assert "SPEC-001.FR-001" in uids
    assert "SPEC-001.NF-020" in uids

  def test_find_by_verified_by_va_pattern(self) -> None:
    """Test finding requirements with VA (agent validation) artifacts."""
    root = self._make_repo()
    self._write_spec_with_requirements(root, "SPEC-001", ["FR-002: Second requirement"])

    registry = self._create_registry_with_verification(root)

    # Find requirements with VA artifacts
    requirements = registry.find_by_verified_by("VA-*")

    assert isinstance(requirements, list)
    assert len(requirements) == 1
    assert requirements[0].uid == "SPEC-001.FR-002"

  def test_find_by_verified_by_vt_prefix_pattern(self) -> None:
    """Test finding requirements with VT-PROD prefix."""
    root = self._make_repo()
    self._write_spec_with_requirements(root, "SPEC-001", ["FR-001: First requirement"])

    registry = self._create_registry_with_verification(root)

    # Find requirements verified by VT-PROD* artifacts
    requirements = registry.find_by_verified_by("VT-PROD*")

    assert isinstance(requirements, list)
    assert len(requirements) == 1
    assert requirements[0].uid == "SPEC-001.FR-001"

  def test_find_by_verified_by_nonexistent_artifact(self) -> None:
    """Test finding requirements for non-existent artifact returns empty list."""
    root = self._make_repo()
    self._write_spec_with_requirements(root, "SPEC-001", ["FR-001: First requirement"])

    registry = self._create_registry_with_verification(root)

    requirements = registry.find_by_verified_by("NONEXISTENT-ARTIFACT")

    assert isinstance(requirements, list)
    assert len(requirements) == 0

  def test_find_by_verified_by_none(self) -> None:
    """Test find_by_verified_by with None returns empty list."""
    root = self._make_repo()
    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)

    requirements = registry.find_by_verified_by(None)

    assert isinstance(requirements, list)
    assert len(requirements) == 0

  def test_find_by_verified_by_empty_string(self) -> None:
    """Test find_by_verified_by with empty string returns empty list."""
    root = self._make_repo()
    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)

    requirements = registry.find_by_verified_by("")

    assert isinstance(requirements, list)
    assert len(requirements) == 0

  def test_find_by_verified_by_returns_requirement_records(self) -> None:
    """Test that find_by_verified_by returns proper RequirementRecord objects."""
    root = self._make_repo()
    self._write_spec_with_requirements(root, "SPEC-001", ["FR-001: First requirement"])

    registry = self._create_registry_with_verification(root)

    requirements = registry.find_by_verified_by("VT-CLI-001")

    assert len(requirements) == 1
    req = requirements[0]

    # Verify it's a RequirementRecord with expected attributes
    assert isinstance(req, RequirementRecord)
    assert hasattr(req, "uid")
    assert hasattr(req, "label")
    assert hasattr(req, "title")
    assert hasattr(req, "verified_by")
    assert hasattr(req, "coverage_evidence")

  def test_find_by_verified_by_case_sensitive(self) -> None:
    """Test that artifact ID matching is case-sensitive."""
    root = self._make_repo()
    self._write_spec_with_requirements(root, "SPEC-001", ["FR-001: First requirement"])

    registry = self._create_registry_with_verification(root)

    # Correct case
    requirements_upper = registry.find_by_verified_by("VT-CLI-001")
    # Wrong case
    requirements_lower = registry.find_by_verified_by("vt-cli-001")

    assert len(requirements_upper) == 1
    assert len(requirements_lower) == 0

  def test_find_by_verified_by_glob_wildcard_positions(self) -> None:
    """Test glob patterns with wildcards in different positions."""
    root = self._make_repo()
    self._write_spec_with_requirements(
      root,
      "SPEC-001",
      ["FR-001: First", "FR-002: Second", "NF-020: Third"],
    )

    registry = self._create_registry_with_verification(root)

    # Test *-001 pattern (wildcard at start)
    requirements = registry.find_by_verified_by("*-001")
    uids = {r.uid for r in requirements}
    assert "SPEC-001.FR-001" in uids  # VT-CLI-001
    assert "SPEC-001.FR-002" in uids  # VA-REVIEW-001

    # Test VT-* pattern (wildcard at end)
    requirements = registry.find_by_verified_by("VT-*")
    uids = {r.uid for r in requirements}
    assert "SPEC-001.FR-001" in uids
    assert "SPEC-001.NF-020" in uids


class TestFindByVerificationStatus(unittest.TestCase):
  """Test RequirementsRegistry.find_by_verification_status() method."""

  def setUp(self) -> None:
    self._cwd = Path.cwd()

  def tearDown(self) -> None:
    os.chdir(self._cwd)

  def _make_registry_with_entries(self) -> RequirementsRegistry:
    """Create a registry with records having diverse coverage_entries."""
    tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.addCleanup(tmpdir.cleanup)
    root = Path(tmpdir.name)
    (root / ".git").mkdir()
    os.chdir(root)

    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)

    # FR-001: verified
    registry.records["SPEC-001.FR-001"] = RequirementRecord(
      uid="SPEC-001.FR-001",
      label="FR-001",
      title="Verified requirement",
      coverage_entries=[
        {"artefact": "VT-001", "kind": "VT", "status": "verified"},
      ],
    )
    # FR-002: in-progress
    registry.records["SPEC-001.FR-002"] = RequirementRecord(
      uid="SPEC-001.FR-002",
      label="FR-002",
      title="In-progress requirement",
      coverage_entries=[
        {"artefact": "VT-002", "kind": "VT", "status": "in-progress"},
      ],
    )
    # FR-003: planned
    registry.records["SPEC-001.FR-003"] = RequirementRecord(
      uid="SPEC-001.FR-003",
      label="FR-003",
      title="Planned requirement",
      coverage_entries=[
        {"artefact": "VA-001", "kind": "VA", "status": "planned"},
      ],
    )
    # FR-004: mixed (verified + failed)
    registry.records["SPEC-001.FR-004"] = RequirementRecord(
      uid="SPEC-001.FR-004",
      label="FR-004",
      title="Mixed status requirement",
      coverage_entries=[
        {"artefact": "VT-003", "kind": "VT", "status": "verified"},
        {"artefact": "VH-001", "kind": "VH", "status": "failed"},
      ],
    )
    # NF-001: no coverage entries
    registry.records["SPEC-001.NF-001"] = RequirementRecord(
      uid="SPEC-001.NF-001",
      label="NF-001",
      title="No coverage requirement",
      coverage_entries=[],
    )
    return registry

  def test_single_status_verified(self) -> None:
    """Filter by single status 'verified' returns matching requirements."""
    registry = self._make_registry_with_entries()
    results = registry.find_by_verification_status(["verified"])
    uids = {r.uid for r in results}
    assert "SPEC-001.FR-001" in uids  # Has verified entry
    assert "SPEC-001.FR-004" in uids  # Has verified + failed
    assert "SPEC-001.FR-002" not in uids

  def test_single_status_failed(self) -> None:
    """Filter by 'failed' returns requirements with failed entries."""
    registry = self._make_registry_with_entries()
    results = registry.find_by_verification_status(["failed"])
    uids = {r.uid for r in results}
    assert "SPEC-001.FR-004" in uids
    assert len(uids) == 1

  def test_multi_status_or_logic(self) -> None:
    """Multi-value status uses OR logic: match if ANY entry matches ANY status."""
    registry = self._make_registry_with_entries()
    results = registry.find_by_verification_status(["planned", "in-progress"])
    uids = {r.uid for r in results}
    assert "SPEC-001.FR-002" in uids  # in-progress
    assert "SPEC-001.FR-003" in uids  # planned
    assert "SPEC-001.FR-001" not in uids

  def test_empty_list_returns_all(self) -> None:
    """Empty status list returns empty result (no filter match)."""
    registry = self._make_registry_with_entries()
    results = registry.find_by_verification_status([])
    assert results == []

  def test_nonexistent_status(self) -> None:
    """Non-existent status returns empty list."""
    registry = self._make_registry_with_entries()
    results = registry.find_by_verification_status(["nonexistent"])
    assert results == []

  def test_results_sorted_by_uid(self) -> None:
    """Results are sorted by uid."""
    registry = self._make_registry_with_entries()
    results = registry.find_by_verification_status(["verified"])
    uids = [r.uid for r in results]
    assert uids == sorted(uids)

  def test_no_coverage_entries_excluded(self) -> None:
    """Requirements with empty coverage_entries are never matched."""
    registry = self._make_registry_with_entries()
    # NF-001 has no coverage_entries — should never appear
    for status in ["verified", "in-progress", "planned", "failed", "blocked"]:
      results = registry.find_by_verification_status([status])
      uids = {r.uid for r in results}
      assert "SPEC-001.NF-001" not in uids


class TestFindByVerificationKind(unittest.TestCase):
  """Test RequirementsRegistry.find_by_verification_kind() method."""

  def setUp(self) -> None:
    self._cwd = Path.cwd()

  def tearDown(self) -> None:
    os.chdir(self._cwd)

  def _make_registry_with_entries(self) -> RequirementsRegistry:
    """Create a registry with records having diverse verification kinds."""
    tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.addCleanup(tmpdir.cleanup)
    root = Path(tmpdir.name)
    (root / ".git").mkdir()
    os.chdir(root)

    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)

    # FR-001: VT only
    registry.records["SPEC-001.FR-001"] = RequirementRecord(
      uid="SPEC-001.FR-001",
      label="FR-001",
      title="VT-only requirement",
      coverage_entries=[
        {"artefact": "VT-001", "kind": "VT", "status": "verified"},
      ],
    )
    # FR-002: VA only
    registry.records["SPEC-001.FR-002"] = RequirementRecord(
      uid="SPEC-001.FR-002",
      label="FR-002",
      title="VA-only requirement",
      coverage_entries=[
        {"artefact": "VA-001", "kind": "VA", "status": "verified"},
      ],
    )
    # FR-003: VH only
    registry.records["SPEC-001.FR-003"] = RequirementRecord(
      uid="SPEC-001.FR-003",
      label="FR-003",
      title="VH-only requirement",
      coverage_entries=[
        {"artefact": "VH-001", "kind": "VH", "status": "planned"},
      ],
    )
    # FR-004: mixed VT + VA
    registry.records["SPEC-001.FR-004"] = RequirementRecord(
      uid="SPEC-001.FR-004",
      label="FR-004",
      title="Mixed VT+VA requirement",
      coverage_entries=[
        {"artefact": "VT-002", "kind": "VT", "status": "in-progress"},
        {"artefact": "VA-002", "kind": "VA", "status": "verified"},
      ],
    )
    # NF-001: no coverage entries
    registry.records["SPEC-001.NF-001"] = RequirementRecord(
      uid="SPEC-001.NF-001",
      label="NF-001",
      title="No coverage requirement",
      coverage_entries=[],
    )
    return registry

  def test_single_kind_vt(self) -> None:
    """Filter by VT returns requirements with VT entries."""
    registry = self._make_registry_with_entries()
    results = registry.find_by_verification_kind(["VT"])
    uids = {r.uid for r in results}
    assert "SPEC-001.FR-001" in uids
    assert "SPEC-001.FR-004" in uids
    assert "SPEC-001.FR-002" not in uids  # VA only
    assert "SPEC-001.FR-003" not in uids  # VH only

  def test_single_kind_va(self) -> None:
    """Filter by VA returns requirements with VA entries."""
    registry = self._make_registry_with_entries()
    results = registry.find_by_verification_kind(["VA"])
    uids = {r.uid for r in results}
    assert "SPEC-001.FR-002" in uids
    assert "SPEC-001.FR-004" in uids
    assert "SPEC-001.FR-001" not in uids

  def test_single_kind_vh(self) -> None:
    """Filter by VH returns requirements with VH entries."""
    registry = self._make_registry_with_entries()
    results = registry.find_by_verification_kind(["VH"])
    uids = {r.uid for r in results}
    assert uids == {"SPEC-001.FR-003"}

  def test_multi_kind_or_logic(self) -> None:
    """Multi-value kind uses OR logic."""
    registry = self._make_registry_with_entries()
    results = registry.find_by_verification_kind(["VA", "VH"])
    uids = {r.uid for r in results}
    assert "SPEC-001.FR-002" in uids  # VA
    assert "SPEC-001.FR-003" in uids  # VH
    assert "SPEC-001.FR-004" in uids  # VA+VT (matches VA)
    assert "SPEC-001.FR-001" not in uids  # VT only

  def test_all_kinds(self) -> None:
    """Filtering by all three kinds returns all requirements with coverage."""
    registry = self._make_registry_with_entries()
    results = registry.find_by_verification_kind(["VT", "VA", "VH"])
    uids = {r.uid for r in results}
    assert "SPEC-001.NF-001" not in uids  # No entries
    assert len(uids) == 4

  def test_empty_list_returns_empty(self) -> None:
    """Empty kind list returns empty result."""
    registry = self._make_registry_with_entries()
    results = registry.find_by_verification_kind([])
    assert results == []

  def test_nonexistent_kind(self) -> None:
    """Non-existent kind returns empty list."""
    registry = self._make_registry_with_entries()
    results = registry.find_by_verification_kind(["XX"])
    assert results == []

  def test_results_sorted_by_uid(self) -> None:
    """Results are sorted by uid."""
    registry = self._make_registry_with_entries()
    results = registry.find_by_verification_kind(["VT"])
    uids = [r.uid for r in results]
    assert uids == sorted(uids)

  def test_no_coverage_entries_excluded(self) -> None:
    """Requirements with empty coverage_entries never matched."""
    registry = self._make_registry_with_entries()
    for kind in ["VT", "VA", "VH"]:
      results = registry.find_by_verification_kind([kind])
      uids = {r.uid for r in results}
      assert "SPEC-001.NF-001" not in uids


class TestRequirementsRegistryStandardSurface(unittest.TestCase):
  """Tests for ADR-009 standard registry surface: find, collect, iter, filter."""

  def setUp(self) -> None:
    self._cwd = Path.cwd()

  def tearDown(self) -> None:
    os.chdir(self._cwd)

  def _make_registry(self) -> tuple[RequirementsRegistry, Path]:
    tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.addCleanup(tmpdir.cleanup)
    root = Path(tmpdir.name)
    (root / ".git").mkdir()
    os.chdir(root)
    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)
    registry.records["SPEC-001.FR-001"] = RequirementRecord(
      uid="SPEC-001.FR-001",
      label="FR-001",
      title="First requirement",
      specs=["SPEC-001"],
      kind="functional",
      status=STATUS_ACTIVE,
      tags=["core"],
    )
    registry.records["SPEC-001.NF-001"] = RequirementRecord(
      uid="SPEC-001.NF-001",
      label="NF-001",
      title="Non-functional requirement",
      specs=["SPEC-001"],
      kind="non-functional",
      status=STATUS_PENDING,
      tags=["performance"],
    )
    registry.records["SPEC-002.FR-001"] = RequirementRecord(
      uid="SPEC-002.FR-001",
      label="FR-001",
      title="Second spec requirement",
      specs=["SPEC-002"],
      kind="functional",
      status=STATUS_ACTIVE,
    )
    return registry, root

  # -- constructor ----------------------------------------------------------

  def test_constructor_with_root_keyword(self) -> None:
    tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.addCleanup(tmpdir.cleanup)
    root = Path(tmpdir.name)
    (root / ".git").mkdir()
    os.chdir(root)
    registry = RequirementsRegistry(root=root)
    assert registry.registry_path == get_registry_dir(root) / "requirements.yaml"

  def test_constructor_positional_still_works(self) -> None:
    tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.addCleanup(tmpdir.cleanup)
    root = Path(tmpdir.name)
    (root / ".git").mkdir()
    os.chdir(root)
    explicit_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(explicit_path)
    assert registry.registry_path == explicit_path

  # -- find() ---------------------------------------------------------------

  def test_find_returns_record(self) -> None:
    registry, _ = self._make_registry()
    record = registry.find("SPEC-001.FR-001")
    assert record is not None
    assert record.uid == "SPEC-001.FR-001"

  def test_find_returns_none_for_missing(self) -> None:
    registry, _ = self._make_registry()
    assert registry.find("SPEC-999.FR-999") is None

  # -- collect() ------------------------------------------------------------

  def test_collect_returns_dict(self) -> None:
    registry, _ = self._make_registry()
    result = registry.collect()
    assert isinstance(result, dict)
    assert len(result) == 3
    assert "SPEC-001.FR-001" in result

  def test_collect_returns_copy(self) -> None:
    registry, _ = self._make_registry()
    a = registry.collect()
    b = registry.collect()
    assert a is not b

  # -- iter() ---------------------------------------------------------------

  def test_iter_yields_all(self) -> None:
    registry, _ = self._make_registry()
    uids = {r.uid for r in registry.iter()}
    assert len(uids) == 3

  def test_iter_filters_by_status(self) -> None:
    registry, _ = self._make_registry()
    uids = {r.uid for r in registry.iter(status=STATUS_ACTIVE)}
    assert uids == {"SPEC-001.FR-001", "SPEC-002.FR-001"}

  # -- filter() -------------------------------------------------------------

  def test_filter_by_status(self) -> None:
    registry, _ = self._make_registry()
    result = registry.filter(status=STATUS_PENDING)
    assert len(result) == 1
    assert result[0].uid == "SPEC-001.NF-001"

  def test_filter_by_spec(self) -> None:
    registry, _ = self._make_registry()
    result = registry.filter(spec="SPEC-002")
    assert len(result) == 1
    assert result[0].uid == "SPEC-002.FR-001"

  def test_filter_by_kind(self) -> None:
    registry, _ = self._make_registry()
    result = registry.filter(kind="non-functional")
    assert len(result) == 1
    assert result[0].uid == "SPEC-001.NF-001"

  def test_filter_by_tag(self) -> None:
    registry, _ = self._make_registry()
    result = registry.filter(tag="core")
    assert len(result) == 1
    assert result[0].uid == "SPEC-001.FR-001"

  def test_filter_and_logic(self) -> None:
    registry, _ = self._make_registry()
    result = registry.filter(status=STATUS_ACTIVE, kind="functional")
    assert len(result) == 2

  def test_filter_no_params_returns_all(self) -> None:
    registry, _ = self._make_registry()
    assert len(registry.filter()) == 3

  def test_filter_no_matches_returns_empty(self) -> None:
    registry, _ = self._make_registry()
    assert registry.filter(tag="nonexistent") == []


class TestTerminalStatusGuard(unittest.TestCase):
  """VT-081-002: Terminal statuses not overwritten by coverage derivation."""

  def _make_repo(self) -> Path:
    root = Path(tempfile.mkdtemp())
    (root / ".git").mkdir()
    return root

  def _write_spec(self, root: Path, spec_id: str, body: str) -> Path:
    spec_dir = root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR / spec_id.lower()
    spec_dir.mkdir(parents=True, exist_ok=True)
    dump_markdown_file(
      spec_dir / f"{spec_id}.md",
      {"id": spec_id, "status": "draft", "kind": "spec"},
      body,
    )
    return root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR

  def test_deprecated_status_constants(self) -> None:
    """deprecated and superseded are valid requirement statuses."""
    assert STATUS_DEPRECATED == "deprecated"
    assert STATUS_SUPERSEDED == "superseded"
    assert STATUS_DEPRECATED in TERMINAL_STATUSES
    assert STATUS_SUPERSEDED in TERMINAL_STATUSES

  def test_deprecated_not_overwritten_by_coverage(self) -> None:
    """A deprecated requirement keeps its status despite verified coverage."""
    root = self._make_repo()
    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)

    body = textwrap.dedent("""\
      ## Requirements
      - **FR-001**: Deprecated requirement

      ```yaml supekku:verification.coverage@v1
      schema: supekku.verification.coverage
      version: 1
      subject: SPEC-830
      entries:
        - artefact: VT-831
          kind: VT
          requirement: SPEC-830.FR-001
          status: verified
      ```
    """)
    specs_root = self._write_spec(root, "SPEC-830", body)

    registry.sync_from_specs(spec_dirs=[specs_root])
    assert registry.records["SPEC-830.FR-001"].status == STATUS_ACTIVE

    # Manually set to deprecated (normative lifecycle claim)
    registry.records["SPEC-830.FR-001"].status = STATUS_DEPRECATED

    # Re-sync — coverage says verified, but deprecated is terminal
    registry.sync_from_specs(spec_dirs=[specs_root])
    assert registry.records["SPEC-830.FR-001"].status == STATUS_DEPRECATED

  def test_superseded_not_overwritten_by_coverage(self) -> None:
    """A superseded requirement keeps its status despite coverage."""
    root = self._make_repo()
    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)

    body = textwrap.dedent("""\
      ## Requirements
      - **FR-001**: Superseded requirement

      ```yaml supekku:verification.coverage@v1
      schema: supekku.verification.coverage
      version: 1
      subject: SPEC-840
      entries:
        - artefact: VT-841
          kind: VT
          requirement: SPEC-840.FR-001
          status: in-progress
      ```
    """)
    specs_root = self._write_spec(root, "SPEC-840", body)

    registry.sync_from_specs(spec_dirs=[specs_root])
    registry.records["SPEC-840.FR-001"].status = STATUS_SUPERSEDED
    registry.sync_from_specs(spec_dirs=[specs_root])
    assert registry.records["SPEC-840.FR-001"].status == STATUS_SUPERSEDED


if __name__ == "__main__":
  unittest.main()
