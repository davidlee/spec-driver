# supekku.scripts.lib.core.frontmatter_metadata.revision_test

Validation tests for the completed revision frontmatter metadata (DE-142 P02).

DEC-CONSULT-01 (user-approved 2026-05-29): revision FM is the **narrow** DR §5
shape — Base 7 + ``relations`` + ``tags`` + ``ext_id``/``ext_url`` only.
Deliberately tighter than audit/delta (which keep the full BASE spread): the
universal-cut keys (``lifecycle``/``auditers``/``source``/``owners``/``summary``)
and the hand-rolled scope keys (``source_specs``/``destination_specs``/
``requirements``/``aliases``) reject under strict. Verified zero corpus lossage —
no revision in the 42-record corpus carries the omitted keys.

Tests target ``MetadataValidator`` (the single canonical block-validation
surface) directly, not the legacy ``validate_frontmatter`` — the new validator
is authoritative for the DE-142 VTs.

## Constants

- `_BASE`

## Functions

- `_new_errors(data) -> list[str]`: Strict-mode validation error strings from the canonical validator.

## Classes

### RevisionFrontmatterBesideBlockTest

VT-142-DERIVE-002: ``applies_to`` / scope keys beside the change block.

``applies_to`` is *derived* at load (DEC-142-05 / DEC-138-10), never stored.
The narrow class declares no ``applies_to`` field, so it is an unknown key:
rejected under strict (the post-flip gate), tolerated under ``strict=False``
(transition window). No kind-specific check code is added — the generic
declared-fields check covers revision once the field set omits the key
(R-142-04 resolved MINOR).

**Inherits from:** unittest.TestCase

#### Methods

- `test_applies_to_beside_block_strict_error(self) -> None`
- `test_applies_to_beside_block_tolerated_when_not_strict(self) -> None`

### RevisionFrontmatterValidationTest

VT-142-FM-001 / VT-142-FM-002: narrow revision FM class.

**Inherits from:** unittest.TestCase

#### Methods

- `test_cut_keys_rejected_strict(self) -> None` - -- VT-142-FM-002: cut keys rejected under strict --
- `test_ext_id_and_url_valid(self) -> None`
- `test_minimal_valid(self) -> None` - -- VT-142-FM-001: valid (narrow) field set accepted under strict --
- `test_relations_valid(self) -> None`
- `test_tags_valid(self) -> None`
