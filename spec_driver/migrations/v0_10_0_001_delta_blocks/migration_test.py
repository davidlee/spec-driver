"""VTs for the v0_10_0_001_delta_blocks migration step.

Covers:

- ``VT-DE138-MIG-001`` — ``apply()`` over fixture deltas + idempotence.
- ``VT-DE138-MIG-002`` — ``preview()`` writes nothing and surfaces drift.
- ``VT-DE138-MIG-003`` — FM↔block specs/requirements reconciliation drift.
- ``VT-DE138-RELSYNTH-001`` — relationships-block synthesis from FM applies_to
  when the block is absent.
- ``VT-DE138-BODY-001`` — body §7 deletion + renumber + ``## Outcome`` insertion
  across single-line / folded / literal scalar shapes.

Byte-equality between the migration-local emitters and the supekku-side render
helpers (DEC-138-12) lives in a supekku-side test that imports both surfaces,
because this module's import budget is bounded by the ``Migrations isolation``
contract.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from spec_driver.migrations.v0_10_0_001_delta_blocks import DeltaBlocksStep, step
from spec_driver.migrations.v0_10_0_001_delta_blocks.migration import (
  DRIFT_BODY_RENUMBER,
  DRIFT_BODY_RISK_NARRATIVE,
  DRIFT_CTX_UNMAPPED_TYPE,
  DRIFT_FM_BLOCK_DISAGREEMENT,
  DRIFT_FM_REQS_UNMATCHED,
  DRIFT_FM_SPECS_UNMATCHED,
  DRIFT_OUTCOME_CONFLICT,
  DRIFT_RELATIONSHIPS_SYNTH,
  DRIFT_RISK_MISSING_IMPACT,
  DRIFT_RISK_MISSING_LIKELIHOOD,
  _transform,
)

# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------


def _write_delta(tmp_path: Path, name: str, contents: str) -> Path:
  path = tmp_path / name
  path.write_text(contents, encoding="utf-8")
  return path


def _drift_kinds(drift: list) -> set[str]:
  return {entry.kind for entry in drift}


# ---------------------------------------------------------------------------
# applies_to() head-of-file regex (VT-DE138-MIG-001 prelude)
# ---------------------------------------------------------------------------


def test_applies_to_matches_each_cut_key(tmp_path: Path) -> None:
  for key in (
    "applies_to",
    "context_inputs",
    "risk_register",
    "outcome_summary",
    "lifecycle",
    "aliases",
    "auditers",
    "source",
  ):
    p = _write_delta(
      tmp_path,
      f"DE-test-{key}.md",
      f"---\nid: DE-100\nkind: delta\n{key}: foo\n---\nbody\n",
    )
    assert DeltaBlocksStep().applies_to(p), key


def test_applies_to_skips_clean_target_shape(tmp_path: Path) -> None:
  text = (
    "---\nid: DE-100\nkind: delta\nstatus: draft\n"
    "audit_gate: auto\nowners: []\n---\n# body\n"
  )
  path = _write_delta(tmp_path, "DE-100.md", text)
  assert DeltaBlocksStep().applies_to(path) is False


def test_applies_to_ignores_owners_and_summary_residue(tmp_path: Path) -> None:
  # owners + summary are kept per DR-136 §4; they must NOT trigger sweep.
  text = "---\nid: DE-100\nkind: delta\nowners: []\nsummary: foo\n---\n# body\n"
  path = _write_delta(tmp_path, "DE-100.md", text)
  assert DeltaBlocksStep().applies_to(path) is False


# ---------------------------------------------------------------------------
# Fixture 1 — clean target shape (idempotence)
# ---------------------------------------------------------------------------


_CLEAN_TARGET = """\
---
id: DE-100
kind: delta
status: draft
audit_gate: auto
owners: []
---

# DE-100

```yaml supekku:delta.relationships@v1
schema: supekku.delta.relationships
version: 1
delta: DE-100
revision_links:
  introduces: []
  supersedes: []
specs:
  primary: []
  collaborators: []
requirements:
  implements: []
  updates: []
  verifies: []
phases: []
```

```yaml supekku:delta.context_inputs@v1
schema: supekku.delta.context_inputs
version: 1
entries: []
```

```yaml supekku:delta.risk_register@v1
schema: supekku.delta.risk_register
version: 1
risks: []
```
"""


def test_apply_idempotent_on_clean_target(tmp_path: Path) -> None:
  path = _write_delta(tmp_path, "DE-100.md", _CLEAN_TARGET)
  result = DeltaBlocksStep().apply(path)
  assert result.touched == []
  assert path.read_text(encoding="utf-8") == _CLEAN_TARGET


# ---------------------------------------------------------------------------
# Fixture 4 — FM applies_to + relationships block absent (RELSYNTH-001)
# ---------------------------------------------------------------------------


_FIXTURE_NO_REL_BLOCK = """\
---
id: DE-201
kind: delta
status: draft
applies_to:
  specs:
    - PROD-099
  requirements:
    - PROD-099.FR-001
audit_gate: auto
---

# DE-201

Body text.
"""


def test_relsynth_synthesises_relationships_block(tmp_path: Path) -> None:
  path = _write_delta(tmp_path, "DE-201.md", _FIXTURE_NO_REL_BLOCK)
  step.apply(path)
  text = path.read_text(encoding="utf-8")
  assert "supekku:delta.relationships@v1" in text
  assert "PROD-099" in text
  assert "PROD-099.FR-001" in text
  # Cut keys removed from FM.
  assert "applies_to:" not in text.split("---", 2)[1]


def test_relsynth_emits_drift_entry(tmp_path: Path) -> None:
  result = _transform(_FIXTURE_NO_REL_BLOCK)
  assert DRIFT_RELATIONSHIPS_SYNTH in _drift_kinds(result.drift)


def test_relsynth_skips_when_fm_applies_to_empty(tmp_path: Path) -> None:
  text = "---\nid: DE-202\nkind: delta\napplies_to: {}\n---\n# body\n"
  result = _transform(text)
  # No synthesis drift; cut still occurs.
  assert DRIFT_RELATIONSHIPS_SYNTH not in _drift_kinds(result.drift)


# ---------------------------------------------------------------------------
# Fixture 2 — FM applies_to + block agree (silent cut, no drift)
# ---------------------------------------------------------------------------


_FIXTURE_FM_BLOCK_AGREE = """\
---
id: DE-203
kind: delta
status: draft
applies_to:
  specs:
    - PROD-099
  requirements:
    - PROD-099.FR-001
---

# DE-203

```yaml supekku:delta.relationships@v1
schema: supekku.delta.relationships
version: 1
delta: DE-203
revision_links:
  introduces: []
  supersedes: []
specs:
  primary:
    - PROD-099
  collaborators: []
requirements:
  implements:
    - PROD-099.FR-001
  updates: []
  verifies: []
phases: []
```
"""


def test_fm_block_agreement_no_reconcile_drift(tmp_path: Path) -> None:
  result = _transform(_FIXTURE_FM_BLOCK_AGREE)
  kinds = _drift_kinds(result.drift)
  assert DRIFT_FM_SPECS_UNMATCHED not in kinds
  assert DRIFT_FM_REQS_UNMATCHED not in kinds


# ---------------------------------------------------------------------------
# Fixture 3 — FM applies_to disagrees with block (MIG-003)
# ---------------------------------------------------------------------------


_FIXTURE_FM_BLOCK_DISAGREE = """\
---
id: DE-204
kind: delta
status: draft
applies_to:
  specs:
    - PROD-MISSING
  requirements:
    - PROD-099.FR-NOTREAL
---

# DE-204

```yaml supekku:delta.relationships@v1
schema: supekku.delta.relationships
version: 1
delta: DE-204
revision_links:
  introduces: []
  supersedes: []
specs:
  primary:
    - PROD-099
  collaborators:
    - PROD-OTHER
requirements:
  implements:
    - PROD-099.FR-001
  updates: []
  verifies: []
phases: []
```
"""


def test_fm_block_disagreement_emits_unmatched_drift(tmp_path: Path) -> None:
  result = _transform(_FIXTURE_FM_BLOCK_DISAGREE)
  kinds = _drift_kinds(result.drift)
  assert DRIFT_FM_SPECS_UNMATCHED in kinds
  assert DRIFT_FM_REQS_UNMATCHED in kinds


def test_collaborators_union_avoids_false_unmatched(tmp_path: Path) -> None:
  text = """\
---
id: DE-205
kind: delta
applies_to:
  specs:
    - PROD-OTHER
---

```yaml supekku:delta.relationships@v1
schema: supekku.delta.relationships
version: 1
delta: DE-205
revision_links:
  introduces: []
  supersedes: []
specs:
  primary:
    - PROD-099
  collaborators:
    - PROD-OTHER
requirements:
  implements: []
  updates: []
  verifies: []
phases: []
```
"""
  result = _transform(text)
  assert DRIFT_FM_SPECS_UNMATCHED not in _drift_kinds(result.drift)


# ---------------------------------------------------------------------------
# Fixture 5 — heterogeneous context_inputs (CTX normalisation)
# ---------------------------------------------------------------------------


_FIXTURE_CTX = """\
---
id: DE-206
kind: delta
context_inputs:
  - "plain string entry"
  - type: delta
    ref: DE-100
    note: An annotation
  - type: reference
    id: DOC-1
  - type: somethingweird
    id: X-1
---

# DE-206
"""


def test_context_inputs_normalisation(tmp_path: Path) -> None:
  result = _transform(_FIXTURE_CTX)
  text = result.text
  # Plain string + unknown type both promoted to tolerated 'unknown'.
  assert DRIFT_CTX_UNMAPPED_TYPE in _drift_kinds(result.drift)
  # Block contains canonical type 'delta' and aliased 'document' (reference → document).
  assert "type: delta" in text
  assert "type: document" in text
  # Schema is non-nullable str — `summary: null` must NEVER appear.
  assert "summary: null" not in text
  # ref → id remap landed.
  assert "id: DE-100" in text


def test_context_inputs_summary_omitted_for_plain_string(tmp_path: Path) -> None:
  text = """\
---
id: DE-207
kind: delta
context_inputs:
  - just-a-string
---
# body
"""
  result = _transform(text)
  # Block emitted with id but no `summary:` line for the plain-string entry.
  ctx_block = re.search(
    r"```yaml supekku:delta\.context_inputs@v1\n(.*?)```",
    result.text,
    re.DOTALL,
  )
  assert ctx_block is not None
  block_body = ctx_block.group(1)
  assert "summary:" not in block_body
  assert "id: just-a-string" in block_body


# ---------------------------------------------------------------------------
# Fixture 6 — risk_register normalisation
# ---------------------------------------------------------------------------


_FIXTURE_RISKS = """\
---
id: DE-208
kind: delta
risk_register:
  - id: DE-208.RISK-01
    description: Migration drops body content
    likelihood: high
    impact: medium
  - id: DE-208.RISK-02
    title: No likelihood declared
    impact: low
  - title: No status declared
    likelihood: low
    impact: low
---

# DE-208
"""


def test_risk_register_normalisation(tmp_path: Path) -> None:
  result = _transform(_FIXTURE_RISKS)
  kinds = _drift_kinds(result.drift)
  # description → title alias landed.
  assert "title: Migration drops body content" in result.text
  # Missing likelihood drifted.
  assert DRIFT_RISK_MISSING_LIKELIHOOD in kinds
  # Default status 'open' applied.
  risk_block = re.search(
    r"```yaml supekku:delta\.risk_register@v1\n(.*?)```",
    result.text,
    re.DOTALL,
  )
  assert risk_block is not None
  assert "status: open" in risk_block.group(1)


def test_risk_register_missing_impact_drifts() -> None:
  text = """\
---
id: DE-209
kind: delta
risk_register:
  - id: DE-209.RISK-01
    title: Foo
    likelihood: low
---
# body
"""
  result = _transform(text)
  assert DRIFT_RISK_MISSING_IMPACT in _drift_kinds(result.drift)


# ---------------------------------------------------------------------------
# Fixture 7 — body §7 Risks + outcome_summary scalars + renumber (BODY-001)
# ---------------------------------------------------------------------------


_FIXTURE_BODY_SINGLE_LINE = """\
---
id: DE-210
kind: delta
outcome_summary: A short one-liner outcome.
---

# DE-210

## 1. Summary

Intro.

## 7. Risks & Mitigations

- **Risk**: Something bad

## 8. Follow-ups & Tracking

After.

## 9. Implementation Notes

Notes.
"""


def test_body_reshape_full_pipeline(tmp_path: Path) -> None:
  result = _transform(_FIXTURE_BODY_SINGLE_LINE)
  text = result.text
  # § 7 deleted.
  assert "## 7. Risks" not in text
  # 8 → 7 renumber, 9 → 8 renumber.
  assert "## 7. Follow-ups & Tracking" in text
  assert "## 8. Implementation Notes" in text
  # ## Outcome inserted before ## Implementation Notes.
  outcome_pos = text.find("## Outcome")
  impl_pos = text.find("## 8. Implementation Notes")
  assert 0 <= outcome_pos < impl_pos
  # Drift recorded for both deletion and renumber.
  kinds = _drift_kinds(result.drift)
  assert DRIFT_BODY_RISK_NARRATIVE in kinds
  assert DRIFT_BODY_RENUMBER in kinds


def test_outcome_literal_scalar_preserves_newlines() -> None:
  text = """\
---
id: DE-211
kind: delta
outcome_summary: |
  Line one.
  Line two.

  Paragraph two.
---

# DE-211
"""
  result = _transform(text)
  out_match = re.search(
    r"## Outcome\s*\n\s*\n(.*?)(?=\n## |\Z)", result.text, re.DOTALL
  )
  assert out_match is not None
  outcome_body = out_match.group(1).strip()
  assert "Line one." in outcome_body
  assert "Line two." in outcome_body
  assert "Paragraph two." in outcome_body


def test_outcome_folded_scalar_collapses_newlines() -> None:
  # Folded scalars collapse newlines to spaces — that's PyYAML's contract, not
  # ours; the test pins the visible behaviour so we notice if PyYAML changes.
  text = """\
---
id: DE-212
kind: delta
outcome_summary: >
  Folded text wraps
  onto one line.
---
# DE-212
"""
  result = _transform(text)
  assert "Folded text wraps onto one line." in result.text


def test_outcome_conflict_kept_existing() -> None:
  text = """\
---
id: DE-213
kind: delta
outcome_summary: From FM only.
---

# DE-213

## Outcome

Existing body outcome.

## Implementation Notes

Notes.
"""
  result = _transform(text)
  # Existing body retained.
  assert "Existing body outcome." in result.text
  # FM-only text NOT inserted as a new section.
  assert result.text.count("## Outcome") == 1
  assert DRIFT_OUTCOME_CONFLICT in _drift_kinds(result.drift)


# ---------------------------------------------------------------------------
# Idempotence
# ---------------------------------------------------------------------------


def test_apply_idempotent_on_second_run(tmp_path: Path) -> None:
  path = _write_delta(tmp_path, "DE-220.md", _FIXTURE_NO_REL_BLOCK)
  first = step.apply(path)
  assert first.touched == [path]
  after_first = path.read_text(encoding="utf-8")
  second = step.apply(path)
  assert second.touched == []
  assert path.read_text(encoding="utf-8") == after_first


# ---------------------------------------------------------------------------
# Partial-shape: block present + FM key also present (block wins)
# ---------------------------------------------------------------------------


def test_block_disagreement_keeps_block() -> None:
  text = """\
---
id: DE-230
kind: delta
context_inputs:
  - type: delta
    id: DE-OLD
---

# DE-230

```yaml supekku:delta.context_inputs@v1
schema: supekku.delta.context_inputs
version: 1
entries:
  - type: delta
    id: DE-NEW
```
"""
  result = _transform(text)
  assert "DE-NEW" in result.text
  assert "DE-OLD" not in result.text.split("---", 2)[1]
  assert DRIFT_FM_BLOCK_DISAGREEMENT in _drift_kinds(result.drift)


# ---------------------------------------------------------------------------
# preview() — no writes (VT-DE138-MIG-002)
# ---------------------------------------------------------------------------


def test_preview_does_not_mutate_file(tmp_path: Path) -> None:
  path = _write_delta(tmp_path, "DE-240.md", _FIXTURE_NO_REL_BLOCK)
  before = path.read_bytes()
  preview = step.preview(path)
  assert path.read_bytes() == before
  assert preview.touched == [path]
  assert any("relationships_block_synthesised_from_fm" in d for d in preview.drift)


def test_preview_clean_file_returns_skipped(tmp_path: Path) -> None:
  path = _write_delta(tmp_path, "DE-241.md", _CLEAN_TARGET)
  preview = step.preview(path)
  assert preview.touched == []
  assert preview.skipped == [path]


# ---------------------------------------------------------------------------
# Step Protocol surface
# ---------------------------------------------------------------------------


def test_step_kind_and_description() -> None:
  assert step.applies_to_kind == "delta"
  assert "ADR-010" in step.description


@pytest.mark.parametrize(
  "fixture",
  [
    _CLEAN_TARGET,
    _FIXTURE_NO_REL_BLOCK,
    _FIXTURE_FM_BLOCK_AGREE,
    _FIXTURE_FM_BLOCK_DISAGREE,
    _FIXTURE_CTX,
    _FIXTURE_RISKS,
    _FIXTURE_BODY_SINGLE_LINE,
  ],
)
def test_transform_is_idempotent(fixture: str) -> None:
  first = _transform(fixture)
  second = _transform(first.text)
  assert second.text == first.text
