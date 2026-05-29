"""Tests for v0_10_0_005_revision_metadata migration step.

Covers VT-142-MIGRATE-001 through -004.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from .migration import (
  _CUT_KEYS,
  _MARKER,
  RevisionMetadataStep,
  _transform,
)


def _write(tmp_path: Path, name: str, contents: str) -> Path:
  path = tmp_path / name
  path.write_text(contents, encoding="utf-8")
  return path


def _parse_fm(text: str) -> dict:
  lines = text.split("\n")
  assert lines[0] == "---"
  end = lines.index("---", 1)
  return yaml.safe_load("\n".join(lines[1:end]))


def _parse_block(text: str) -> dict:
  pattern = re.compile(
    r"```(?:yaml|yml)\s+" + re.escape(_MARKER) + r"\n(.*?)```",
    re.DOTALL,
  )
  match = pattern.search(text)
  assert match is not None, "no revision.change block found"
  return yaml.safe_load(match.group(1))


# FM-only record carrying every cut key + requirements (RE-034 shape).
FM_ONLY_WITH_REQS = """\
---
id: RE-099
slug: sample
name: Spec Revision - sample
created: "2026-01-01"
updated: "2026-01-01"
status: draft
kind: revision
aliases: []
auditers: []
source: complete-delta
lifecycle:
  status: active
relations:
  - type: documents
    target: DE-099
tags: []
source_specs: [ADR-007]
destination_specs: [PROD-012]
requirements: [PROD-012.FR-006, PROD-012.NF-001]
---

# RE-099

Body text.
"""

# FM-only record, destination spec but no requirements (RE-015 shape).
FM_ONLY_NO_REQS = """\
---
id: RE-098
slug: inplace
name: Spec Revision - inplace
created: "2026-01-01"
updated: "2026-01-01"
status: draft
kind: revision
aliases: []
source_specs: [PROD-014]
destination_specs: [PROD-014]
---

# RE-098

Body.
"""


# ---------------------------------------------------------------------------
# Module export
# ---------------------------------------------------------------------------


def test_module_exports_step_instance() -> None:
  from spec_driver.migrations.v0_10_0_005_revision_metadata import step  # noqa: PLC0415

  assert isinstance(step, RevisionMetadataStep)
  assert step.applies_to_kind == "revision"


# ---------------------------------------------------------------------------
# VT-142-MIGRATE-001: universal + hand-rolled FM key cuts
# ---------------------------------------------------------------------------


class TestFmKeyCuts:
  """VT-142-MIGRATE-001"""

  def test_all_cut_keys_removed(self) -> None:
    result = _transform(FM_ONLY_WITH_REQS)
    fm = _parse_fm(result.text)
    for key in _CUT_KEYS:
      assert key not in fm, f"{key} not cut"

  def test_non_cut_keys_preserved(self) -> None:
    result = _transform(FM_ONLY_WITH_REQS)
    fm = _parse_fm(result.text)
    assert fm["id"] == "RE-099"
    assert fm["name"] == "Spec Revision - sample"
    assert fm["status"] == "draft"
    assert fm["kind"] == "revision"
    assert fm["created"] == "2026-01-01"
    assert fm["relations"] == [{"type": "documents", "target": "DE-099"}]
    assert fm["tags"] == []


# ---------------------------------------------------------------------------
# VT-142-MIGRATE-002: FM-only synthesis (modify, no move/lifecycle/origin/drift)
# ---------------------------------------------------------------------------


class TestSynthesis:
  """VT-142-MIGRATE-002 (DEC-142-09/12)"""

  def test_block_synthesised(self) -> None:
    result = _transform(FM_ONLY_WITH_REQS)
    assert result.changed
    assert _MARKER in result.text

  def test_metadata_revision_matches_id(self) -> None:
    block = _parse_block(_transform(FM_ONLY_WITH_REQS).text)
    assert block["metadata"]["revision"] == "RE-099"

  def test_specs_from_destination_only(self) -> None:
    """DEC-142-12: specs[] from destination_specs; ADR source dropped."""
    block = _parse_block(_transform(FM_ONLY_WITH_REQS).text)
    assert block["specs"] == [{"spec_id": "PROD-012", "action": "updated"}]

  def test_requirements_modify_action(self) -> None:
    block = _parse_block(_transform(FM_ONLY_WITH_REQS).text)
    reqs = block["requirements"]
    assert len(reqs) == 2
    assert all(r["action"] == "modify" for r in reqs)

  def test_requirement_kind_from_token(self) -> None:
    block = _parse_block(_transform(FM_ONLY_WITH_REQS).text)
    by_id = {r["requirement_id"]: r for r in block["requirements"]}
    assert by_id["PROD-012.FR-006"]["kind"] == "functional"
    assert by_id["PROD-012.NF-001"]["kind"] == "non-functional"

  def test_requirement_destination_is_container(self) -> None:
    block = _parse_block(_transform(FM_ONLY_WITH_REQS).text)
    for r in block["requirements"]:
      assert r["destination"] == {"spec": "PROD-012"}

  def test_no_lifecycle_or_origin(self) -> None:
    block = _parse_block(_transform(FM_ONLY_WITH_REQS).text)
    for r in block["requirements"]:
      assert "lifecycle" not in r
      assert "origin" not in r

  def test_no_drift(self) -> None:
    assert _transform(FM_ONLY_WITH_REQS).drift == []

  def test_synthesis_without_requirements(self) -> None:
    result = _transform(FM_ONLY_NO_REQS)
    block = _parse_block(result.text)
    assert block["specs"] == [{"spec_id": "PROD-014", "action": "updated"}]
    assert block["requirements"] == []


# ---------------------------------------------------------------------------
# VT-142-MIGRATE-003: existing block wins, FM keys cut, no synthesis
# ---------------------------------------------------------------------------


class TestBlockWins:
  """VT-142-MIGRATE-003"""

  def _with_block(self) -> str:
    return (
      FM_ONLY_WITH_REQS.rstrip()
      + f"""

```yaml {_MARKER}
schema: supekku.revision.change
version: 1
metadata:
  revision: RE-099
specs:
  - spec_id: PROD-012
    action: updated
requirements:
  - requirement_id: PROD-012.FR-006
    kind: functional
    action: modify
    destination:
      spec: PROD-012
    summary: Pre-existing block entry
```
"""
    )

  def test_block_preserved_not_duplicated(self) -> None:
    result = _transform(self._with_block())
    assert result.changed  # FM keys still cut
    assert result.text.count(_MARKER) == 1

  def test_existing_block_untouched(self) -> None:
    result = _transform(self._with_block())
    block = _parse_block(result.text)
    # The pre-existing summary survives — no re-synthesis.
    assert block["requirements"][0]["summary"] == "Pre-existing block entry"
    assert len(block["requirements"]) == 1

  def test_fm_keys_cut(self) -> None:
    fm = _parse_fm(_transform(self._with_block()).text)
    for key in _CUT_KEYS:
      assert key not in fm

  def test_no_drift(self) -> None:
    assert _transform(self._with_block()).drift == []


# ---------------------------------------------------------------------------
# VT-142-MIGRATE-004: idempotence
# ---------------------------------------------------------------------------


class TestIdempotence:
  """VT-142-MIGRATE-004"""

  def test_second_transform_is_noop(self) -> None:
    first = _transform(FM_ONLY_WITH_REQS)
    assert first.changed
    second = _transform(first.text)
    assert not second.changed
    assert second.text == first.text

  def test_no_reqs_idempotent(self) -> None:
    first = _transform(FM_ONLY_NO_REQS)
    second = _transform(first.text)
    assert not second.changed
    assert second.text == first.text


# ---------------------------------------------------------------------------
# Step apply/preview
# ---------------------------------------------------------------------------


class TestStepApplyPreview:
  def test_apply_writes(self, tmp_path: Path) -> None:
    path = _write(tmp_path, "RE-099.md", FM_ONLY_WITH_REQS)
    result = RevisionMetadataStep().apply(path)
    assert result.touched == [path]
    text = path.read_text(encoding="utf-8")
    assert _MARKER in text
    assert result.drift_entries == []

  def test_preview_no_write(self, tmp_path: Path) -> None:
    path = _write(tmp_path, "RE-099.md", FM_ONLY_WITH_REQS)
    preview = RevisionMetadataStep().preview(path)
    assert preview.touched == [path]
    assert path.read_text(encoding="utf-8") == FM_ONLY_WITH_REQS

  def test_apply_idempotent(self, tmp_path: Path) -> None:
    path = _write(tmp_path, "RE-099.md", FM_ONLY_WITH_REQS)
    step = RevisionMetadataStep()
    step.apply(path)
    after_first = path.read_text(encoding="utf-8")
    result = step.apply(path)
    assert result.skipped == [path]
    assert path.read_text(encoding="utf-8") == after_first

  def test_applies_to_no_cut_keys(self, tmp_path: Path) -> None:
    clean = """\
---
id: RE-097
status: draft
kind: revision
---

# RE-097
"""
    path = _write(tmp_path, "RE-097.md", clean)
    assert not RevisionMetadataStep().applies_to(path)


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
  def test_no_frontmatter(self) -> None:
    result = _transform("# Heading\n\nText.\n")
    assert not result.changed

  def test_empty_scope_keys_no_synthesis(self) -> None:
    """aliases-only record (no dest/requirements): cut alias, no block."""
    text = """\
---
id: RE-096
status: draft
kind: revision
aliases: []
---

# RE-096
"""
    result = _transform(text)
    assert result.changed
    assert _MARKER not in result.text
    fm = _parse_fm(result.text)
    assert "aliases" not in fm
