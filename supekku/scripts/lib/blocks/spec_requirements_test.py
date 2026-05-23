"""Tests for spec requirements block extraction, rendering, and validation.

Covers VT-140-001 through VT-140-008, VT-140-027, VT-140-028.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from supekku.scripts.lib.blocks.metadata import metadata_to_json_schema
from supekku.scripts.lib.blocks.schema_registry import (
  get_block_schema,
  list_block_types,
)

from .spec_requirements import (
  REQUIREMENTS_MARKER,
  SpecRequirementsBlock,
  extract_spec_requirements,
  load_spec_requirements,
  render_spec_requirements_block,
)
from .spec_requirements_metadata import (
  SPEC_REQUIREMENTS_METADATA,
  SPEC_REQUIREMENTS_VALIDATOR,
  validate_spec_requirements,
)

if TYPE_CHECKING:
  from pathlib import Path

SAMPLE_VALID_YAML = """\
schema: supekku.spec.requirements
version: 1
spec: PROD-004
requirements:
  - id: FR-001
    title: Metadata-driven validation
    lifecycle: active
    kind: functional
    category: core
    description: |
      The system must validate frontmatter.
    acceptance_criteria:
      - All registered kinds validate via metadata
    tags: [validation, metadata]
  - id: NF-001
    title: Validation performance
    lifecycle: pending
    kind: non-functional
    description: |
      Validation must complete within 500ms.
    acceptance_criteria:
      - p99 latency under 500ms
    tags: [performance]
"""


def _wrap_block(inner: str) -> str:
  return f"# Test\n\n```yaml {REQUIREMENTS_MARKER}\n{inner}```\n\n## More\n"


# ---------------------------------------------------------------------------
# VT-140-001: Block extraction — valid block parses to SpecRequirementsBlock
# ---------------------------------------------------------------------------


class TestExtraction:
  """VT-140-001, -002a, -002b, -028: block extraction."""

  def test_valid_block_extracts(self) -> None:
    """VT-140-001"""
    content = _wrap_block(SAMPLE_VALID_YAML)
    block = extract_spec_requirements(content)
    assert block is not None
    assert isinstance(block, SpecRequirementsBlock)
    assert block.data["schema"] == "supekku.spec.requirements"
    assert block.data["version"] == 1
    assert block.data["spec"] == "PROD-004"
    assert len(block.data["requirements"]) == 2

  def test_raw_yaml_preserved(self) -> None:
    content = _wrap_block(SAMPLE_VALID_YAML)
    block = extract_spec_requirements(content)
    assert block is not None
    assert block.raw_yaml.startswith("schema:")

  # -----------------------------------------------------------------------
  # VT-140-002a: No block → returns None
  # -----------------------------------------------------------------------

  def test_no_block_returns_none(self) -> None:
    """VT-140-002a"""
    content = "# No blocks here\n\nJust prose.\n"
    assert extract_spec_requirements(content) is None

  # -----------------------------------------------------------------------
  # VT-140-002b: Malformed YAML → raises ValueError
  # -----------------------------------------------------------------------

  def test_malformed_yaml_raises(self) -> None:
    """VT-140-002b"""
    bad = f"```yaml {REQUIREMENTS_MARKER}\ninvalid: yaml: :\n```"
    with pytest.raises(ValueError, match="invalid spec requirements YAML"):
      extract_spec_requirements(bad)

  def test_non_mapping_yaml_raises(self) -> None:
    bad = f"```yaml {REQUIREMENTS_MARKER}\n- list\n- items\n```"
    with pytest.raises(ValueError, match="must parse to mapping"):
      extract_spec_requirements(bad)

  # -----------------------------------------------------------------------
  # VT-140-028: Multiple blocks in one file → hard error
  # -----------------------------------------------------------------------

  def test_multiple_blocks_raises(self) -> None:
    """VT-140-028"""
    block1 = _wrap_block(SAMPLE_VALID_YAML)
    block2 = _wrap_block(SAMPLE_VALID_YAML)
    content = block1 + "\n" + block2
    with pytest.raises(ValueError, match="multiple spec.requirements blocks"):
      extract_spec_requirements(content)


# ---------------------------------------------------------------------------
# Load from file
# ---------------------------------------------------------------------------


class TestLoadFromFile:
  """Load from file path."""

  def test_load_spec_requirements(self, tmp_path: Path) -> None:
    path = tmp_path / "spec.md"
    path.write_text(_wrap_block(SAMPLE_VALID_YAML))
    block = load_spec_requirements(path)
    assert block is not None
    assert block.data["spec"] == "PROD-004"

  def test_load_returns_none_when_no_block(self, tmp_path: Path) -> None:
    path = tmp_path / "spec.md"
    path.write_text("# No blocks\n")
    assert load_spec_requirements(path) is None


# ---------------------------------------------------------------------------
# VT-140-003: Required fields enforced
# ---------------------------------------------------------------------------


def _validate_strict(data: dict) -> list[str]:
  return [str(e) for e in SPEC_REQUIREMENTS_VALIDATOR.validate(data, strict=True)]


class TestRequiredFields:
  """VT-140-003"""

  def test_valid_minimal(self) -> None:
    data = {
      "schema": "supekku.spec.requirements",
      "version": 1,
      "spec": "SPEC-100",
      "requirements": [],
    }
    assert _validate_strict(data) == []

  def test_missing_schema(self) -> None:
    data = {"version": 1, "spec": "SPEC-100", "requirements": []}
    assert any("schema" in e.lower() for e in _validate_strict(data))

  def test_missing_version(self) -> None:
    data = {
      "schema": "supekku.spec.requirements",
      "spec": "SPEC-100",
      "requirements": [],
    }
    assert any("version" in e.lower() for e in _validate_strict(data))

  def test_missing_spec(self) -> None:
    data = {"schema": "supekku.spec.requirements", "version": 1, "requirements": []}
    assert any("spec" in e.lower() for e in _validate_strict(data))

  def test_missing_requirements(self) -> None:
    data = {"schema": "supekku.spec.requirements", "version": 1, "spec": "SPEC-100"}
    assert any("requirements" in e.lower() for e in _validate_strict(data))

  def test_entry_missing_required_fields(self) -> None:
    data = {
      "schema": "supekku.spec.requirements",
      "version": 1,
      "spec": "SPEC-100",
      "requirements": [{"id": "FR-001"}],
    }
    errors = _validate_strict(data)
    assert any("title" in e.lower() for e in errors)
    assert any("lifecycle" in e.lower() for e in errors)
    assert any("kind" in e.lower() for e in errors)
    assert any("description" in e.lower() for e in errors)
    assert any("acceptance_criteria" in e.lower() for e in errors)


# ---------------------------------------------------------------------------
# VT-140-004: Enum constraints (lifecycle, kind)
# ---------------------------------------------------------------------------


class TestEnumConstraints:
  """VT-140-004"""

  def _entry(self, **overrides: str) -> dict:
    return {
      "schema": "supekku.spec.requirements",
      "version": 1,
      "spec": "SPEC-100",
      "requirements": [
        {
          "id": "FR-001",
          "title": "Test",
          "lifecycle": "pending",
          "kind": "functional",
          "description": "Desc",
          "acceptance_criteria": ["AC"],
          **overrides,
        }
      ],
    }

  def test_valid_lifecycle_values(self) -> None:
    valid = [
      "pending", "in-progress", "active",
      "retired", "deprecated", "superseded",
    ]
    for status in valid:
      data = self._entry(lifecycle=status)
      errs = _validate_strict(data)
      assert errs == [], f"Rejected '{status}'"

  def test_invalid_lifecycle(self) -> None:
    data = self._entry(lifecycle="invalid")
    errors = _validate_strict(data)
    assert any(
      "lifecycle" in e.lower() or "allowed" in e.lower()
      for e in errors
    )

  def test_valid_kind_values(self) -> None:
    pairs = [("functional", "FR"), ("non-functional", "NF")]
    for kind, prefix in pairs:
      data = self._entry(kind=kind, id=f"{prefix}-001")
      errs = _validate_strict(data)
      assert errs == [], f"Rejected '{kind}'"

  def test_invalid_kind(self) -> None:
    data = self._entry(kind="invalid")
    errors = _validate_strict(data)
    assert any(
      "kind" in e.lower() or "allowed" in e.lower()
      for e in errors
    )


# ---------------------------------------------------------------------------
# VT-140-005: Tolerated aliases canonicalized with sunset
# ---------------------------------------------------------------------------


class TestToleratedAliases:
  """VT-140-005"""

  def _entry_with_kind(self, kind: str, req_id: str = "FR-001") -> dict:
    return {
      "schema": "supekku.spec.requirements",
      "version": 1,
      "spec": "SPEC-100",
      "requirements": [
        {
          "id": req_id,
          "title": "Test",
          "lifecycle": "pending",
          "kind": kind,
          "description": "Desc",
          "acceptance_criteria": ["AC"],
        }
      ],
    }

  def test_fr_alias_accepted_default(self) -> None:
    data = self._entry_with_kind("FR")
    errors = [
      str(e) for e in SPEC_REQUIREMENTS_VALIDATOR.validate(data, strict=False)
    ]
    assert errors == []

  def test_nf_alias_accepted_default(self) -> None:
    data = self._entry_with_kind("NF", req_id="NF-001")
    errors = [
      str(e) for e in SPEC_REQUIREMENTS_VALIDATOR.validate(data, strict=False)
    ]
    assert errors == []

  def test_nfr_alias_accepted_default(self) -> None:
    data = self._entry_with_kind("NFR", req_id="NF-001")
    errors = [
      str(e) for e in SPEC_REQUIREMENTS_VALIDATOR.validate(data, strict=False)
    ]
    assert errors == []

  def test_alias_emits_warning_in_strict(self) -> None:
    data = self._entry_with_kind("FR")
    errors = SPEC_REQUIREMENTS_VALIDATOR.validate(data, strict=True)
    warnings = [e for e in errors if e.severity == "warning"]
    assert any("tolerated" in str(w).lower() for w in warnings)

  def test_alias_rejected_when_tolerated_disabled(self) -> None:
    data = self._entry_with_kind("FR")
    errors = SPEC_REQUIREMENTS_VALIDATOR.validate(
      data, strict=True, accept_tolerated=False
    )
    hard_errors = [
      e for e in errors if e.severity == "error"
    ]
    assert any(
      "tolerated" in str(e).lower() or "kind" in str(e).lower()
      for e in hard_errors
    )


# ---------------------------------------------------------------------------
# VT-140-006: Cross-field invariant — ID prefix matches kind
# ---------------------------------------------------------------------------


class TestCrossFieldInvariant:
  """VT-140-006"""

  def test_fr_with_functional_valid(self) -> None:
    block = SpecRequirementsBlock(raw_yaml="", data={
      "schema": "supekku.spec.requirements",
      "version": 1,
      "spec": "SPEC-100",
      "requirements": [
        {"id": "FR-001", "title": "T", "lifecycle": "pending",
         "kind": "functional", "description": "D", "acceptance_criteria": ["AC"]},
      ],
    })
    errors = validate_spec_requirements(block, strict=True)
    assert not any("prefix" in e.lower() for e in errors)

  def test_nf_with_non_functional_valid(self) -> None:
    block = SpecRequirementsBlock(raw_yaml="", data={
      "schema": "supekku.spec.requirements",
      "version": 1,
      "spec": "SPEC-100",
      "requirements": [
        {"id": "NF-001", "title": "T", "lifecycle": "pending",
         "kind": "non-functional", "description": "D", "acceptance_criteria": ["AC"]},
      ],
    })
    errors = validate_spec_requirements(block, strict=True)
    assert not any("prefix" in e.lower() for e in errors)

  def test_fr_with_non_functional_invalid(self) -> None:
    block = SpecRequirementsBlock(raw_yaml="", data={
      "schema": "supekku.spec.requirements",
      "version": 1,
      "spec": "SPEC-100",
      "requirements": [
        {"id": "FR-001", "title": "T", "lifecycle": "pending",
         "kind": "non-functional", "description": "D", "acceptance_criteria": ["AC"]},
      ],
    })
    errors = validate_spec_requirements(block, strict=True)
    assert any("prefix" in e.lower() for e in errors)

  def test_nf_with_functional_invalid(self) -> None:
    block = SpecRequirementsBlock(raw_yaml="", data={
      "schema": "supekku.spec.requirements",
      "version": 1,
      "spec": "SPEC-100",
      "requirements": [
        {"id": "NF-001", "title": "T", "lifecycle": "pending",
         "kind": "functional", "description": "D", "acceptance_criteria": ["AC"]},
      ],
    })
    errors = validate_spec_requirements(block, strict=True)
    assert any("prefix" in e.lower() for e in errors)

  def test_tolerated_alias_still_checks_invariant(self) -> None:
    """FR alias with NF-prefixed ID should fail invariant."""
    block = SpecRequirementsBlock(raw_yaml="", data={
      "schema": "supekku.spec.requirements",
      "version": 1,
      "spec": "SPEC-100",
      "requirements": [
        {"id": "NF-001", "title": "T", "lifecycle": "pending",
         "kind": "FR", "description": "D", "acceptance_criteria": ["AC"]},
      ],
    })
    errors = validate_spec_requirements(block)
    assert any("prefix" in e.lower() for e in errors)


# ---------------------------------------------------------------------------
# VT-140-027: Duplicate IDs within block → hard error
# ---------------------------------------------------------------------------


class TestDuplicateIds:
  """VT-140-027"""

  def test_duplicate_ids_error(self) -> None:
    block = SpecRequirementsBlock(raw_yaml="", data={
      "schema": "supekku.spec.requirements",
      "version": 1,
      "spec": "SPEC-100",
      "requirements": [
        {"id": "FR-001", "title": "First", "lifecycle": "pending",
         "kind": "functional", "description": "D", "acceptance_criteria": ["AC"]},
        {"id": "FR-001", "title": "Dupe", "lifecycle": "pending",
         "kind": "functional", "description": "D", "acceptance_criteria": ["AC"]},
      ],
    })
    errors = validate_spec_requirements(block, strict=True)
    assert any("duplicate" in e.lower() for e in errors)

  def test_unique_ids_pass(self) -> None:
    block = SpecRequirementsBlock(raw_yaml="", data={
      "schema": "supekku.spec.requirements",
      "version": 1,
      "spec": "SPEC-100",
      "requirements": [
        {"id": "FR-001", "title": "First", "lifecycle": "pending",
         "kind": "functional", "description": "D", "acceptance_criteria": ["AC"]},
        {"id": "FR-002", "title": "Second", "lifecycle": "pending",
         "kind": "functional", "description": "D", "acceptance_criteria": ["AC"]},
      ],
    })
    errors = validate_spec_requirements(block, strict=True)
    assert not any("duplicate" in e.lower() for e in errors)


# ---------------------------------------------------------------------------
# VT-140-007: Renderer produces valid parseable block YAML
# ---------------------------------------------------------------------------


class TestRenderer:
  """VT-140-007"""

  def test_render_empty_requirements(self) -> None:
    block_str = render_spec_requirements_block("SPEC-100")
    assert f"```yaml {REQUIREMENTS_MARKER}" in block_str
    assert "requirements: []" in block_str
    assert block_str.endswith("```")

  def test_render_with_entries(self) -> None:
    entries = [
      {
        "id": "FR-001",
        "title": "Test req",
        "lifecycle": "active",
        "kind": "functional",
        "category": "core",
        "description": "A description.",
        "acceptance_criteria": ["Criterion one", "Criterion two"],
        "tags": ["tag1", "tag2"],
      },
    ]
    block_str = render_spec_requirements_block("PROD-004", requirements=entries)
    assert "id: FR-001" in block_str
    assert "title: Test req" in block_str
    assert "lifecycle: active" in block_str
    assert "kind: functional" in block_str
    assert "category: core" in block_str
    assert "tags: [tag1, tag2]" in block_str

  def test_round_trip(self) -> None:
    """Rendered block should be extractable."""
    entries = [
      {
        "id": "FR-001",
        "title": "Round trip",
        "lifecycle": "pending",
        "kind": "functional",
        "description": "Test desc",
        "acceptance_criteria": ["AC1"],
        "tags": ["test"],
      },
    ]
    rendered = render_spec_requirements_block("SPEC-100", requirements=entries)
    block = extract_spec_requirements(rendered)
    assert block is not None
    assert block.data["spec"] == "SPEC-100"
    assert len(block.data["requirements"]) == 1
    assert block.data["requirements"][0]["id"] == "FR-001"


# ---------------------------------------------------------------------------
# VT-140-008: Schema registry — registered with marker/version/renderer
# ---------------------------------------------------------------------------


class TestSchemaRegistry:
  """VT-140-008"""

  def test_registered_in_registry(self) -> None:
    schema = get_block_schema("spec.requirements")
    assert schema is not None
    assert schema.marker == REQUIREMENTS_MARKER
    assert schema.version == 1
    assert schema.renderer is render_spec_requirements_block
    assert schema.metadata is SPEC_REQUIREMENTS_METADATA

  def test_appears_in_list(self) -> None:
    assert "spec.requirements" in list_block_types()


# ---------------------------------------------------------------------------
# Spec ID cross-validation
# ---------------------------------------------------------------------------


class TestSpecIdCrossValidation:
  """Spec ID cross-validation in wrapper."""

  def test_matching_spec_id_passes(self) -> None:
    block = SpecRequirementsBlock(raw_yaml="", data={
      "schema": "supekku.spec.requirements",
      "version": 1,
      "spec": "SPEC-100",
      "requirements": [],
    })
    errors = validate_spec_requirements(block, spec_id="SPEC-100")
    assert not any("spec field" in e.lower() for e in errors)

  def test_mismatched_spec_id_errors(self) -> None:
    block = SpecRequirementsBlock(raw_yaml="", data={
      "schema": "supekku.spec.requirements",
      "version": 1,
      "spec": "SPEC-100",
      "requirements": [],
    })
    errors = validate_spec_requirements(block, spec_id="SPEC-999")
    assert any("does not match" in e.lower() for e in errors)


# ---------------------------------------------------------------------------
# JSON Schema generation
# ---------------------------------------------------------------------------


class TestJsonSchema:
  """JSON Schema generation and examples."""

  def test_generates_valid_schema(self) -> None:
    schema = metadata_to_json_schema(SPEC_REQUIREMENTS_METADATA)
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["type"] == "object"
    assert set(schema["required"]) == {"schema", "version", "spec", "requirements"}

  def test_examples_present(self) -> None:
    assert len(SPEC_REQUIREMENTS_METADATA.examples) > 0
    example = SPEC_REQUIREMENTS_METADATA.examples[0]
    assert example["schema"] == "supekku.spec.requirements"
