"""Tests for MultiLanguageSpecManager.process_source_unit.

VT-DE029-GATE: contract generation must proceed independently of spec existence.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from supekku.scripts.lib.core.spec_utils import load_markdown_file
from supekku.scripts.lib.sync.models import DocVariant, SourceDescriptor, SourceUnit
from supekku.scripts.sync_specs import MultiLanguageSpecManager


class ProcessSourceUnitContractGateTest(unittest.TestCase):
  """Contract generation must not be gated on spec existence."""

  def setUp(self) -> None:
    self.tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.root = Path(self.tmpdir.name)
    self.tech_dir = self.root / "specify" / "tech"
    self.tech_dir.mkdir(parents=True)
    self.registry_path = self.tech_dir / "registry_v2.json"
    self._write_registry({})
    self.manager = MultiLanguageSpecManager(self.tech_dir, self.registry_path)

  def tearDown(self) -> None:
    self.tmpdir.cleanup()

  def _write_registry(self, languages: dict) -> None:
    self.registry_path.write_text(
      json.dumps({"version": 2, "languages": languages}),
      encoding="utf-8",
    )

  def test_contracts_generated_when_spec_creation_off(self) -> None:
    """VT-DE029-GATE-001: generate_contracts=True, create_specs=False, no spec.

    Contract generation must proceed even when the source unit has no
    registered spec and spec auto-creation is disabled.
    """
    source_unit = SourceUnit(
      language="go",
      identifier="internal/foo",
      root=self.root,
    )

    expected_variant = DocVariant(
      name="public",
      path=self.root / ".contracts" / "public" / "internal" / "foo" / "interfaces.md",
      hash="abc123",
      status="created",
    )

    adapter = MagicMock()
    adapter.generate.return_value = [expected_variant]

    result = self.manager.process_source_unit(
      source_unit,
      adapter,
      generate_contracts=True,
      create_specs=False,
    )

    assert result["processed"] is True
    assert result["skipped"] is False
    assert result["created"] is False
    assert result["spec_id"] is None
    adapter.generate.assert_called_once()
    assert result["doc_variants"] == [expected_variant]

  def test_no_spec_work_when_spec_creation_off(self) -> None:
    """VT-DE029-GATE-002: spec-related side effects must be skipped."""
    source_unit = SourceUnit(
      language="go",
      identifier="internal/bar",
      root=self.root,
    )

    adapter = MagicMock()
    adapter.generate.return_value = []

    result = self.manager.process_source_unit(
      source_unit,
      adapter,
      generate_contracts=True,
      create_specs=False,
    )

    assert result["processed"] is True
    assert result["created"] is False
    # No spec directory should have been created
    spec_dirs = list(self.tech_dir.glob("SPEC-*"))
    assert spec_dirs == []

  def test_check_mode_still_skips_unregistered(self) -> None:
    """VT-DE029-GATE-003: check_mode with no spec still returns early."""
    source_unit = SourceUnit(
      language="go",
      identifier="internal/baz",
      root=self.root,
    )
    adapter = MagicMock()

    result = self.manager.process_source_unit(
      source_unit,
      adapter,
      check_mode=True,
      create_specs=False,
    )

    assert result["skipped"] is True
    assert result["reason"] == "no registered spec for check mode"
    adapter.generate.assert_not_called()

  def test_both_contracts_and_specs_off_skips(self) -> None:
    """VT-DE029-GATE-004: no contracts + no specs → skip, no work."""
    source_unit = SourceUnit(
      language="go",
      identifier="internal/qux",
      root=self.root,
    )
    adapter = MagicMock()

    result = self.manager.process_source_unit(
      source_unit,
      adapter,
      generate_contracts=False,
      create_specs=False,
    )

    assert result["skipped"] is True
    adapter.generate.assert_not_called()


class SyncCreatedSpecTaxonomyTest(unittest.TestCase):
  """VT-030-002: sync-created specs set category: unit, c4_level: code."""

  def setUp(self) -> None:
    self.tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.root = Path(self.tmpdir.name)
    self.tech_dir = self.root / "specify" / "tech"
    self.tech_dir.mkdir(parents=True)
    self.registry_path = self.tech_dir / "registry_v2.json"
    self._write_registry({})
    self.manager = MultiLanguageSpecManager(self.tech_dir, self.registry_path)

  def tearDown(self) -> None:
    self.tmpdir.cleanup()

  def _write_registry(self, languages: dict) -> None:
    self.registry_path.write_text(
      json.dumps({"version": 2, "languages": languages}),
      encoding="utf-8",
    )

  def test_stub_frontmatter_has_unit_taxonomy(self) -> None:
    """Sync-created stub specs must have category: unit and c4_level: code."""
    source_unit = SourceUnit(
      language="go",
      identifier="internal/foo",
      root=self.root,
    )
    descriptor = SourceDescriptor(
      slug_parts=["internal", "foo"],
      default_frontmatter={
        "sources": [
          {
            "language": "go",
            "identifier": "internal/foo",
            "variants": [],
          }
        ],
      },
      variants=[],
    )
    adapter = MagicMock()
    adapter.describe.return_value = descriptor
    adapter.generate.return_value = []

    result = self.manager.process_source_unit(
      source_unit,
      adapter,
      generate_contracts=False,
      create_specs=True,
    )

    assert result["created"] is True
    spec_id = result["spec_id"]
    spec_file = self.tech_dir / spec_id / f"{spec_id}.md"
    assert spec_file.exists()

    frontmatter, _ = load_markdown_file(spec_file)
    assert frontmatter["category"] == "unit"
    assert frontmatter["c4_level"] == "code"


if __name__ == "__main__":
  unittest.main()
