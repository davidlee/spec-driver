"""Dual-validation tests for delta relationships metadata.

Tests that the new metadata-driven validator and the wrapper helper
produce results compatible with the legacy DeltaRelationshipsValidator
behaviour. P03 C3 retires the legacy class; the parallel assertions
remain here while DE-118 is open and are trimmed when the harness
retires.
"""

from __future__ import annotations

import unittest

from supekku.scripts.lib.blocks.metadata import (
  MetadataValidator,
  metadata_to_json_schema,
)

from .delta import (
  DeltaRelationshipsBlock,
  extract_delta_context_inputs,
  render_delta_context_inputs_block,
)
from .delta_metadata import (
  DELTA_CONTEXT_INPUTS_METADATA,
  DELTA_RELATIONSHIPS_METADATA,
  DELTA_RISK_REGISTER_METADATA,
  validate_delta_context_inputs,
  validate_delta_relationships,
)


class DualValidationTest(unittest.TestCase):
  """Test that wrapper + metadata validator capture legacy behaviour."""

  def _validate_both(
    self, data: dict, *, delta_id: str | None = None
  ) -> tuple[list[str], list[str]]:
    """Run wrapper and metadata validator; return (wrapper, metadata)."""
    block = DeltaRelationshipsBlock(raw_yaml="", data=data)
    wrapper_errors = validate_delta_relationships(block, delta_id=delta_id)

    new_validator = MetadataValidator(DELTA_RELATIONSHIPS_METADATA)
    new_errors = [str(err) for err in new_validator.validate(data)]

    return wrapper_errors, new_errors

  def test_valid_minimal_block(self):
    """Both validators accept valid minimal block."""
    data = {
      "schema": "supekku.delta.relationships",
      "version": 1,
      "delta": "DE-001",
    }

    wrapper_errors, new_errors = self._validate_both(data)
    assert wrapper_errors == []
    assert new_errors == []

  def test_valid_complete_block(self):
    """Both validators accept block with all optional fields."""
    data = {
      "schema": "supekku.delta.relationships",
      "version": 1,
      "delta": "DE-002",
      "revision_links": {
        "introduces": ["RE-001", "RE-002"],
        "supersedes": ["RE-000"],
      },
      "specs": {
        "primary": ["SPEC-100"],
        "collaborators": ["SPEC-200", "SPEC-300"],
      },
      "requirements": {
        "implements": ["SPEC-100.FR-001"],
        "updates": ["SPEC-100.FR-002"],
        "verifies": ["SPEC-100.NFR-PERF"],
      },
      "phases": [
        {"id": "IP-001.PHASE-01"},
        {"id": "IP-001.PHASE-02"},
      ],
    }

    wrapper_errors, new_errors = self._validate_both(data)
    assert wrapper_errors == []
    assert new_errors == []

  def test_missing_schema_field(self):
    """Both validators reject missing schema field."""
    data = {
      "version": 1,
      "delta": "DE-001",
    }

    wrapper_errors, new_errors = self._validate_both(data)
    assert any("schema" in err.lower() for err in wrapper_errors)
    assert any("schema" in err.lower() for err in new_errors)

  def test_wrong_schema_value(self):
    """Both validators reject wrong schema value."""
    data = {
      "schema": "wrong.schema",
      "version": 1,
      "delta": "DE-001",
    }

    wrapper_errors, new_errors = self._validate_both(data)
    assert any("schema" in err.lower() for err in wrapper_errors)
    assert any("schema" in err.lower() for err in new_errors)

  def test_wrong_version(self):
    """Both validators reject wrong version."""
    data = {
      "schema": "supekku.delta.relationships",
      "version": 999,
      "delta": "DE-001",
    }

    wrapper_errors, new_errors = self._validate_both(data)
    assert any("version" in err.lower() for err in wrapper_errors)
    assert any("version" in err.lower() for err in new_errors)

  def test_missing_delta(self):
    """Both validators reject missing delta."""
    data = {
      "schema": "supekku.delta.relationships",
      "version": 1,
    }

    wrapper_errors, new_errors = self._validate_both(data)
    assert any("delta" in err.lower() for err in wrapper_errors)
    assert any("delta" in err.lower() for err in new_errors)

  def test_delta_id_mismatch(self):
    """Wrapper detects delta ID mismatch when expected ID provided."""
    data = {
      "schema": "supekku.delta.relationships",
      "version": 1,
      "delta": "DE-999",
    }

    wrapper_errors, new_errors = self._validate_both(data, delta_id="DE-001")
    assert any(
      "de-999" in err.lower() and "de-001" in err.lower() for err in wrapper_errors
    )
    # Metadata validator alone does not enforce caller ID equality.
    assert new_errors == []

  def test_specs_not_object(self):
    """Both validators reject non-object specs."""
    data = {
      "schema": "supekku.delta.relationships",
      "version": 1,
      "delta": "DE-001",
      "specs": "not-object",
    }

    wrapper_errors, new_errors = self._validate_both(data)
    assert any("specs" in err.lower() for err in wrapper_errors)
    assert any("specs" in err.lower() or "object" in err.lower() for err in new_errors)

  def test_requirements_not_object(self):
    """Both validators reject non-object requirements."""
    data = {
      "schema": "supekku.delta.relationships",
      "version": 1,
      "delta": "DE-001",
      "requirements": "not-object",
    }

    wrapper_errors, new_errors = self._validate_both(data)
    assert any("requirements" in err.lower() for err in wrapper_errors)
    assert any(
      "requirements" in err.lower() or "object" in err.lower() for err in new_errors
    )

  def test_specs_primary_not_array(self):
    """Both validators reject non-array specs.primary."""
    data = {
      "schema": "supekku.delta.relationships",
      "version": 1,
      "delta": "DE-001",
      "specs": {
        "primary": "not-array",
      },
    }

    wrapper_errors, new_errors = self._validate_both(data)
    assert any("primary" in err.lower() for err in wrapper_errors)
    assert any("primary" in err.lower() for err in new_errors)

  def test_specs_primary_non_string_items(self):
    """Both validators reject non-string items in specs.primary."""
    data = {
      "schema": "supekku.delta.relationships",
      "version": 1,
      "delta": "DE-001",
      "specs": {
        "primary": ["SPEC-100", 123, "SPEC-200"],
      },
    }

    wrapper_errors, new_errors = self._validate_both(data)
    assert any("string" in err.lower() for err in wrapper_errors)
    assert any("string" in err.lower() for err in new_errors)

  def test_requirements_implements_not_array(self):
    """Both validators reject non-array requirements.implements."""
    data = {
      "schema": "supekku.delta.relationships",
      "version": 1,
      "delta": "DE-001",
      "requirements": {
        "implements": "not-array",
      },
    }

    wrapper_errors, new_errors = self._validate_both(data)
    assert any("implements" in err.lower() for err in wrapper_errors)
    assert any("implements" in err.lower() for err in new_errors)

  def test_phases_not_array(self):
    """Both validators reject non-array phases."""
    data = {
      "schema": "supekku.delta.relationships",
      "version": 1,
      "delta": "DE-001",
      "phases": "not-array",
    }

    wrapper_errors, new_errors = self._validate_both(data)
    assert any("phases" in err.lower() for err in wrapper_errors)
    assert any("phases" in err.lower() or "array" in err.lower() for err in new_errors)

  def test_phases_entry_not_object(self):
    """Both validators reject non-object phase entries."""
    data = {
      "schema": "supekku.delta.relationships",
      "version": 1,
      "delta": "DE-001",
      "phases": ["not-object"],
    }

    wrapper_errors, new_errors = self._validate_both(data)
    assert any("object" in err.lower() for err in wrapper_errors)
    assert any("object" in err.lower() for err in new_errors)

  def test_phases_entry_missing_id(self):
    """Both validators reject phase entry missing id."""
    data = {
      "schema": "supekku.delta.relationships",
      "version": 1,
      "delta": "DE-001",
      "phases": [
        {"name": "Phase 1"},
      ],
    }

    wrapper_errors, new_errors = self._validate_both(data)
    assert any("id" in err.lower() for err in wrapper_errors)
    assert any("id" in err.lower() for err in new_errors)

  def test_all_specs_sections(self):
    """Both validators accept all specs sections."""
    for section in ["primary", "collaborators"]:
      data = {
        "schema": "supekku.delta.relationships",
        "version": 1,
        "delta": "DE-001",
        "specs": {
          section: ["SPEC-100"],
        },
      }

      wrapper_errors, new_errors = self._validate_both(data)
      assert wrapper_errors == [], f"Wrapper rejected valid specs.{section}"
      assert new_errors == [], f"Metadata validator rejected valid specs.{section}"

  def test_all_requirements_sections(self):
    """Both validators accept all requirements sections."""
    for section in ["implements", "updates", "verifies"]:
      data = {
        "schema": "supekku.delta.relationships",
        "version": 1,
        "delta": "DE-001",
        "requirements": {
          section: ["SPEC-100.FR-001"],
        },
      }

      wrapper_errors, new_errors = self._validate_both(data)
      assert wrapper_errors == [], f"Wrapper rejected valid requirements.{section}"
      assert new_errors == [], f"Metadata rejected valid requirements.{section}"

  def test_all_revision_links_sections(self):
    """Both validators accept all revision_links sections."""
    for section in ["introduces", "supersedes"]:
      data = {
        "schema": "supekku.delta.relationships",
        "version": 1,
        "delta": "DE-001",
        "revision_links": {
          section: ["RE-001"],
        },
      }

      wrapper_errors, new_errors = self._validate_both(data)
      assert wrapper_errors == [], f"Wrapper rejected valid revision_links.{section}"
      assert new_errors == [], f"Metadata rejected valid revision_links.{section}"


class WrapperTest(unittest.TestCase):
  """Tests for the validate_delta_relationships wrapper helper."""

  def _block(self, data: dict) -> DeltaRelationshipsBlock:
    return DeltaRelationshipsBlock(raw_yaml="", data=data)

  def test_delta_id_match_accepts(self):
    """Wrapper accepts block whose delta value matches the expected id."""
    block = self._block(
      {
        "schema": "supekku.delta.relationships",
        "version": 1,
        "delta": "DE-001",
      }
    )
    assert validate_delta_relationships(block, delta_id="DE-001") == []

  def test_delta_id_none_skips_id_check(self):
    """When delta_id is None the wrapper does not enforce ID equality."""
    block = self._block(
      {
        "schema": "supekku.delta.relationships",
        "version": 1,
        "delta": "DE-999",
      }
    )
    assert validate_delta_relationships(block, delta_id=None) == []

  def test_delta_id_empty_skips_id_check(self):
    """Empty-string delta_id matches the legacy `elif delta_id` truthy gate."""
    block = self._block(
      {
        "schema": "supekku.delta.relationships",
        "version": 1,
        "delta": "DE-999",
      }
    )
    assert validate_delta_relationships(block, delta_id="") == []

  def test_strict_unknown_keys_rejected(self):
    """Wrapper enforces strict_unknown_keys via MetadataValidator."""
    block = self._block(
      {
        "schema": "supekku.delta.relationships",
        "version": 1,
        "delta": "DE-001",
        "unexpected_key": "value",
      }
    )
    errors = validate_delta_relationships(block, delta_id="DE-001")
    assert any("unexpected_key" in err for err in errors)

  def test_combined_metadata_and_id_errors(self):
    """Wrapper returns metadata errors AND id-mismatch when both apply."""
    block = self._block(
      {
        "schema": "wrong.schema",
        "version": 1,
        "delta": "DE-999",
      }
    )
    errors = validate_delta_relationships(block, delta_id="DE-001")
    assert any("schema" in err.lower() for err in errors)
    assert any("de-999" in err.lower() and "de-001" in err.lower() for err in errors)


class MetadataOnlyTest(unittest.TestCase):
  """Test metadata-specific features not in old validator."""

  def test_json_schema_generation(self):
    """Metadata can generate JSON Schema for delta relationships."""
    schema = metadata_to_json_schema(DELTA_RELATIONSHIPS_METADATA)

    # Verify schema structure
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["type"] == "object"
    assert "supekku-delta-relationships" in schema["$id"]

    # Verify required fields
    assert set(schema["required"]) == {"schema", "version", "delta"}

    # Verify properties
    assert schema["properties"]["schema"]["const"] == "supekku.delta.relationships"
    assert schema["properties"]["version"]["const"] == 1
    assert schema["properties"]["delta"]["type"] == "string"

    # Verify optional nested objects
    assert schema["properties"]["specs"]["type"] == "object"
    assert schema["properties"]["requirements"]["type"] == "object"
    assert schema["properties"]["revision_links"]["type"] == "object"

    # Verify phases array
    assert schema["properties"]["phases"]["type"] == "array"
    assert schema["properties"]["phases"]["items"]["type"] == "object"
    assert schema["properties"]["phases"]["items"]["required"] == ["id"]

  def test_examples_included(self):
    """Metadata includes examples."""
    assert len(DELTA_RELATIONSHIPS_METADATA.examples) > 0
    example = DELTA_RELATIONSHIPS_METADATA.examples[0]
    assert example["schema"] == "supekku.delta.relationships"
    assert example["version"] == 1
    assert "delta" in example


class DeltaContextInputsTest(unittest.TestCase):
  """VT-DE138-CTX-001 + CTX-002 — delta.context_inputs@v1 schema."""

  def _validator(self) -> MetadataValidator:
    return MetadataValidator(DELTA_CONTEXT_INPUTS_METADATA)

  def _validate(
    self,
    data: dict,
    *,
    strict: bool = True,
    accept_tolerated: bool = True,
  ) -> list[str]:
    errs = self._validator().validate(
      data, strict=strict, accept_tolerated=accept_tolerated
    )
    return [str(err) for err in errs]

  def test_accepts_empty_entries(self):
    """Empty entries[] passes strict (canonical empty-block form)."""
    data = {
      "schema": "supekku.delta.context_inputs",
      "version": 1,
      "entries": [],
    }
    assert self._validate(data) == []

  def test_accepts_canonical_populated(self):
    """Multiple canonical entries pass strict."""
    data = {
      "schema": "supekku.delta.context_inputs",
      "version": 1,
      "entries": [
        {"type": "delta", "id": "DE-136", "summary": "Umbrella program"},
        {"type": "adr", "id": "ADR-010"},
      ],
    }
    assert self._validate(data) == []

  def test_rejects_truly_unrecognised_type_strict(self):
    """A type not in enum/aliases/tolerated rejects under strict (F-138-32)."""
    data = {
      "schema": "supekku.delta.context_inputs",
      "version": 1,
      "entries": [{"type": "gibberish_kind", "id": "X-1"}],
    }
    errs = self._validate(data, strict=True)
    assert any("gibberish_kind" in e or "allowed values" in e for e in errs)

  def test_applies_permanent_aliases(self):
    """Permanent alias values normalise (reference→document, etc.)."""
    data = {
      "schema": "supekku.delta.context_inputs",
      "version": 1,
      "entries": [
        {"type": "reference", "id": "EXT-1"},
        {"type": "brief", "id": "BRIEF-1"},
        {"type": "investigation", "id": "RC-1"},
      ],
    }
    errs = self._validate(data, strict=True)
    for err in errs:
      assert "alias" in err, f"non-alias error surfaced: {err}"

  def test_field_alias_ref_to_id(self):
    """field_aliases on entry: ref → id."""
    data = {
      "schema": "supekku.delta.context_inputs",
      "version": 1,
      "entries": [{"type": "delta", "ref": "DE-001"}],
    }
    errs = self._validate(data, strict=False)
    assert errs == []

  def test_field_alias_note_to_summary(self):
    """field_aliases on entry: note → summary."""
    data = {
      "schema": "supekku.delta.context_inputs",
      "version": 1,
      "entries": [{"type": "delta", "id": "DE-001", "note": "alt summary"}],
    }
    errs = self._validate(data, strict=False)
    assert errs == []

  def test_field_alias_annotation_to_summary(self):
    """field_aliases on entry: annotation → summary."""
    data = {
      "schema": "supekku.delta.context_inputs",
      "version": 1,
      "entries": [{"type": "delta", "id": "DE-001", "annotation": "note"}],
    }
    errs = self._validate(data, strict=False)
    assert errs == []

  # CTX-002 — F-138-31, F-138-32

  def test_literal_unknown_accepted_under_default_strict(self):
    """Tolerated alias 'unknown' accepted under default strict (warning only)."""
    data = {
      "schema": "supekku.delta.context_inputs",
      "version": 1,
      "entries": [{"type": "unknown", "id": "X-1"}],
    }
    errs = self._validate(data, strict=True, accept_tolerated=True)
    # Tolerated-alias entry under default strict surfaces only as warning,
    # not as a hard "must be one of allowed values" error.
    error_only = [e for e in errs if "tolerated alias" not in e and "alias" not in e]
    assert error_only == [], f"hard errors surfaced: {error_only}"

  def test_literal_unknown_rejected_under_no_tolerated(self):
    """Tolerated alias 'unknown' rejected under --no-tolerated-aliases."""
    data = {
      "schema": "supekku.delta.context_inputs",
      "version": 1,
      "entries": [{"type": "unknown", "id": "X-1"}],
    }
    errs = self._validate(data, strict=True, accept_tolerated=False)
    assert any("tolerated alias" in e.lower() for e in errs)

  def test_truly_unrecognised_rejected_under_no_tolerated(self):
    """Truly unrecognised type also rejects under --no-tolerated-aliases."""
    data = {
      "schema": "supekku.delta.context_inputs",
      "version": 1,
      "entries": [{"type": "novel_kind", "id": "X-1"}],
    }
    errs = self._validate(data, strict=True, accept_tolerated=False)
    assert any("novel_kind" in e or "allowed values" in e for e in errs)

  def test_render_plain_string_input_omits_summary_key(self):
    """Render omits summary when absent (never emit `summary: null`; F-138-31)."""
    rendered = render_delta_context_inputs_block(
      entries=[{"type": "document", "id": "PLAIN-1"}]
    )
    assert "summary" not in rendered
    block = extract_delta_context_inputs(rendered)
    assert block is not None
    assert "summary" not in block.data["entries"][0]

  def test_render_omits_none_summary(self):
    """Even if caller passes summary=None, key is omitted (F-138-31)."""
    rendered = render_delta_context_inputs_block(
      entries=[{"type": "document", "id": "PLAIN-1", "summary": None}]
    )
    assert "summary" not in rendered
    block = extract_delta_context_inputs(rendered)
    assert "summary" not in block.data["entries"][0]

  def test_missing_required_type_rejected(self):
    """Missing required `type` rejects under strict."""
    data = {
      "schema": "supekku.delta.context_inputs",
      "version": 1,
      "entries": [{"id": "X-1"}],
    }
    errs = self._validate(data, strict=True)
    assert any("type" in e.lower() and "required" in e.lower() for e in errs)

  def test_missing_required_id_rejected(self):
    """Missing required `id` rejects under strict."""
    data = {
      "schema": "supekku.delta.context_inputs",
      "version": 1,
      "entries": [{"type": "delta"}],
    }
    errs = self._validate(data, strict=True)
    assert any("id" in e.lower() and "required" in e.lower() for e in errs)


class DeltaRiskRegisterTest(unittest.TestCase):
  """VT-DE138-RISK-001 — delta.risk_register@v1 schema."""

  def _validator(self) -> MetadataValidator:
    return MetadataValidator(DELTA_RISK_REGISTER_METADATA)

  def _validate(self, data: dict, *, strict: bool = True) -> list[str]:
    return [str(e) for e in self._validator().validate(data, strict=strict)]

  def test_accepts_empty_risks(self):
    data = {
      "schema": "supekku.delta.risk_register",
      "version": 1,
      "risks": [],
    }
    assert self._validate(data) == []

  def test_accepts_canonical_risk(self):
    data = {
      "schema": "supekku.delta.risk_register",
      "version": 1,
      "risks": [
        {
          "id": "DE-138.RISK-01",
          "title": "Transition fallback",
          "likelihood": "high",
          "impact": "low",
          "exposure": "systemic",
          "mitigation": "Track for removal",
          "status": "open",
        }
      ],
    }
    assert self._validate(data) == []

  def test_rejects_missing_likelihood(self):
    data = {
      "schema": "supekku.delta.risk_register",
      "version": 1,
      "risks": [
        {
          "id": "R1",
          "title": "T",
          "impact": "low",
          "mitigation": "M",
        }
      ],
    }
    errs = self._validate(data, strict=True)
    assert any("likelihood" in e.lower() for e in errs)

  def test_rejects_missing_impact(self):
    data = {
      "schema": "supekku.delta.risk_register",
      "version": 1,
      "risks": [
        {
          "id": "R1",
          "title": "T",
          "likelihood": "low",
          "mitigation": "M",
        }
      ],
    }
    errs = self._validate(data, strict=True)
    assert any("impact" in e.lower() for e in errs)

  def test_field_alias_description_to_title(self):
    """field_aliases on entry: description → title."""
    data = {
      "schema": "supekku.delta.risk_register",
      "version": 1,
      "risks": [
        {
          "id": "R1",
          "description": "Risk text",
          "likelihood": "low",
          "impact": "low",
          "mitigation": "M",
        }
      ],
    }
    errs = self._validate(data, strict=False)
    assert errs == []

  def test_status_optional_default_open(self):
    """Status is optional (default 'open' if absent)."""
    data = {
      "schema": "supekku.delta.risk_register",
      "version": 1,
      "risks": [
        {
          "id": "R1",
          "title": "T",
          "likelihood": "low",
          "impact": "low",
          "mitigation": "M",
        }
      ],
    }
    assert self._validate(data) == []

  def test_rejects_invalid_likelihood_value(self):
    data = {
      "schema": "supekku.delta.risk_register",
      "version": 1,
      "risks": [
        {
          "id": "R1",
          "title": "T",
          "likelihood": "extreme",
          "impact": "low",
          "mitigation": "M",
        }
      ],
    }
    errs = self._validate(data, strict=True)
    assert any("likelihood" in e or "allowed values" in e for e in errs)


class DeltaBlockMalformedTest(unittest.TestCase):
  """VT-DE138-MALFORMED-001 — block-extraction edge cases."""

  def test_malformed_yaml_inside_fence_raises(self):
    """Malformed YAML inside the fence → ValueError from extract."""
    text = (
      "```yaml supekku:delta.context_inputs@v1\n"
      "schema: supekku.delta.context_inputs\n"
      "version: 1\n"
      "entries: [unclosed\n"
      "```\n"
    )
    try:
      extract_delta_context_inputs(text)
    except ValueError as exc:
      assert "context_inputs" in str(exc).lower() or "yaml" in str(exc).lower()
    else:
      msg = "expected ValueError for malformed YAML"
      raise AssertionError(msg)

  def test_non_mapping_block_raises(self):
    """Block that parses to a list (not mapping) raises ValueError."""
    text = "```yaml supekku:delta.context_inputs@v1\n- item1\n- item2\n```\n"
    try:
      extract_delta_context_inputs(text)
    except ValueError as exc:
      assert "mapping" in str(exc).lower()
    else:
      msg = "expected ValueError for non-mapping payload"
      raise AssertionError(msg)

  def test_no_block_returns_none(self):
    text = "no block here"
    assert extract_delta_context_inputs(text) is None

  def test_entries_null_fails_strict_validator(self):
    """`entries: null` distinct from `entries: []` — fails strict (not array)."""
    text = (
      "```yaml supekku:delta.context_inputs@v1\n"
      "schema: supekku.delta.context_inputs\n"
      "version: 1\n"
      "entries: null\n"
      "```\n"
    )
    block = extract_delta_context_inputs(text)
    assert block is not None
    errs = validate_delta_context_inputs(block, strict=True)
    assert any("entries" in e.lower() for e in errs)

  def test_entries_empty_list_passes_strict_validator(self):
    """`entries: []` is the canonical empty-block form."""
    text = (
      "```yaml supekku:delta.context_inputs@v1\n"
      "schema: supekku.delta.context_inputs\n"
      "version: 1\n"
      "entries: []\n"
      "```\n"
    )
    block = extract_delta_context_inputs(text)
    errs = validate_delta_context_inputs(block, strict=True)
    assert errs == []

  def test_duplicate_block_first_match_wins_at_extract(self):
    """Two CTX blocks in same text: extract returns first.

    Strict-mode "duplicate block of same schema" detection lives at the
    validate-file/workspace layer (DEC-138-10) and is exercised in P04
    alongside the strict-flip wiring (VT-DE138-FLIP-001 / GATE-001).
    """
    text = (
      "```yaml supekku:delta.context_inputs@v1\n"
      "schema: supekku.delta.context_inputs\n"
      "version: 1\n"
      "entries:\n"
      "- type: delta\n"
      "  id: FIRST\n"
      "```\n\n"
      "```yaml supekku:delta.context_inputs@v1\n"
      "schema: supekku.delta.context_inputs\n"
      "version: 1\n"
      "entries:\n"
      "- type: delta\n"
      "  id: SECOND\n"
      "```\n"
    )
    block = extract_delta_context_inputs(text)
    assert block is not None
    assert block.data["entries"][0]["id"] == "FIRST"


if __name__ == "__main__":
  unittest.main()
