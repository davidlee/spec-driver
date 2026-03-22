"""Tests for requirement parsing and extraction."""

from __future__ import annotations

import logging
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
from supekku.scripts.lib.requirements.parser import (
  _REQUIREMENT_HEADING,
  _is_requirement_like_line,
  _records_from_content,
)
from supekku.scripts.lib.requirements.registry import (
  RequirementRecord,
  RequirementsRegistry,
)


class TestRequirementHeadingRegex(unittest.TestCase):
  """VT-REGEX-076-001: _REQUIREMENT_HEADING regex matches dotted backlog format."""

  def test_matches_fr_dotted(self) -> None:
    m = _REQUIREMENT_HEADING.match("### FR-016.001: User can filter by source")
    assert m is not None
    assert m.group(1).upper() == "FR"
    assert m.group(2) == "016"
    assert m.group(3) == "001"
    assert m.group(4).strip() == "User can filter by source"

  def test_matches_nf_dotted(self) -> None:
    m = _REQUIREMENT_HEADING.match("### NF-013.001: Performance under load")
    assert m is not None
    assert m.group(1).upper() == "NF"
    assert m.group(2) == "013"
    assert m.group(3) == "001"

  def test_rejects_non_dotted(self) -> None:
    assert _REQUIREMENT_HEADING.match("### FR-001: Title") is None

  def test_rejects_bullet_format(self) -> None:
    assert _REQUIREMENT_HEADING.match("- **FR-016.001**: Title") is None

  def test_matches_h2(self) -> None:
    m = _REQUIREMENT_HEADING.match("## FR-016.002: Another requirement")
    assert m is not None

  def test_matches_dash_separator(self) -> None:
    m = _REQUIREMENT_HEADING.match("### FR-016.001 - Dash separated title")
    assert m is not None
    assert m.group(4).strip() == "Dash separated title"


class TestInlineRequirementTags(unittest.TestCase):
  """VT-081-003: Inline tag extraction from [tag1, tag2] syntax."""

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

  def test_tags_extracted_from_inline_syntax(self) -> None:
    """Tags in [brackets] after category are parsed."""
    root = self._make_repo()
    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)

    body = textwrap.dedent("""\
      ## Requirements
      - **FR-001**(api)[security, auth]: Validate tokens
      - **FR-002**[performance]: Fast response
      - **NF-001**(infra)[reliability, ha]: High availability
      - **FR-003**: No tags here
    """)
    specs_root = self._write_spec(root, "SPEC-850", body)

    registry.sync_from_specs(spec_dirs=[specs_root])

    fr001 = registry.records["SPEC-850.FR-001"]
    assert fr001.tags == ["auth", "security"]
    assert fr001.category == "api"

    fr002 = registry.records["SPEC-850.FR-002"]
    assert fr002.tags == ["performance"]
    assert fr002.category is None

    nf001 = registry.records["SPEC-850.NF-001"]
    assert nf001.tags == ["ha", "reliability"]
    assert nf001.category == "infra"

    fr003 = registry.records["SPEC-850.FR-003"]
    assert fr003.tags == []

  def test_tags_populated_in_registry_after_save_load(self) -> None:
    """Tags survive save/load round-trip."""
    root = self._make_repo()
    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)

    body = textwrap.dedent("""\
      ## Requirements
      - **FR-001**[alpha, beta]: Tagged requirement
    """)
    specs_root = self._write_spec(root, "SPEC-860", body)

    registry.sync_from_specs(spec_dirs=[specs_root])
    registry.save()

    # Reload
    registry2 = RequirementsRegistry(registry_path)
    fr001 = registry2.records["SPEC-860.FR-001"]
    assert fr001.tags == ["alpha", "beta"]

  def test_filter_by_tag(self) -> None:
    """filter(tag=...) returns only tagged requirements."""
    root = self._make_repo()
    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)

    body = textwrap.dedent("""\
      ## Requirements
      - **FR-001**[security]: Secure endpoint
      - **FR-002**[performance]: Fast endpoint
      - **FR-003**[security, performance]: Both
    """)
    specs_root = self._write_spec(root, "SPEC-870", body)

    registry.sync_from_specs(spec_dirs=[specs_root])

    security = registry.filter(tag="security")
    assert {r.uid for r in security} == {
      "SPEC-870.FR-001",
      "SPEC-870.FR-003",
    }

    perf = registry.filter(tag="performance")
    assert {r.uid for r in perf} == {
      "SPEC-870.FR-002",
      "SPEC-870.FR-003",
    }

    none = registry.filter(tag="nonexistent")
    assert none == []

  def test_tags_merged_on_multi_spec_sync(self) -> None:
    """Tags from multiple specs are unioned during merge."""
    record1 = RequirementRecord(
      uid="SPEC-001.FR-001",
      label="FR-001",
      title="Shared requirement",
      tags=["alpha", "beta"],
    )
    record2 = RequirementRecord(
      uid="SPEC-001.FR-001",
      label="FR-001",
      title="Shared requirement",
      tags=["beta", "gamma"],
    )
    merged = record1.merge(record2)
    assert merged.tags == ["alpha", "beta", "gamma"]


class TestIsRequirementLikeLine(unittest.TestCase):
  """Test _is_requirement_like_line heuristic for false-positive suppression.

  The heuristic distinguishes lines that plausibly *define* a requirement
  (and may have a format problem) from lines that merely *reference* one.
  """

  # -- Lines that ARE plausible definition attempts -----------------------

  def test_bold_bullet_definition(self) -> None:
    """Standard bold-bullet definition format is requirement-like."""
    assert _is_requirement_like_line("- **FR-001**: Some title")

  def test_plain_bullet_definition(self) -> None:
    """Bullet with bare ID (no bold) is requirement-like."""
    assert _is_requirement_like_line("- FR-001: Some title")

  def test_qualified_bullet_definition(self) -> None:
    """Qualified ID (SPEC-100.FR-001) in bullet is requirement-like."""
    assert _is_requirement_like_line("- **SPEC-100.FR-001**: Some title")

  def test_heading_definition(self) -> None:
    """Heading with FR/NF ID as subject is requirement-like."""
    assert _is_requirement_like_line("### FR-016.001: Some title")

  def test_nf_definition(self) -> None:
    """Non-functional requirement definition is requirement-like."""
    assert _is_requirement_like_line("- **NF-001**: Performance target")

  def test_badly_formatted_definition(self) -> None:
    """Missing bold markers — still looks like a definition attempt."""
    assert _is_requirement_like_line("- FR-001 Some badly formatted requirement")

  def test_heading_with_nf_subject(self) -> None:
    """Heading where NF-001 is the subject (not a cross-ref)."""
    assert _is_requirement_like_line(
      "# Formal NF-001 benchmark test for materialisation performance",
    )

  # -- Lines that are NOT definitions (cross-references) ------------------

  def test_per_crossref_in_parenthetical(self) -> None:
    """'per PROD-004.FR-007' inside parentheses is a cross-reference."""
    assert not _is_requirement_like_line(
      "- clap command definitions (noun-verb families per PROD-004.FR-007)",
    )

  def test_per_crossref_qualified(self) -> None:
    """'per SPEC-003.FR-006' is a cross-reference."""
    assert not _is_requirement_like_line(
      "- Contractual properties (must match bough per SPEC-003.FR-006)",
    )

  def test_per_crossref_in_heading(self) -> None:
    """Heading ending with 'per NF-001' is a cross-reference."""
    assert not _is_requirement_like_line(
      "# Structured logging implementation per NF-001",
    )

  def test_parenthetical_only_mention(self) -> None:
    """ID only inside parentheses — citation, not definition."""
    assert not _is_requirement_like_line(
      "Some prose mentioning (FR-007) in parens only",
    )

  def test_parenthetical_qualified_mention(self) -> None:
    """Qualified ID only inside parentheses."""
    assert not _is_requirement_like_line(
      "- some responsibility (PROD-004.FR-007)",
    )

  def test_no_requirement_id(self) -> None:
    """Line without any FR/NF ID at all."""
    assert not _is_requirement_like_line("- Just a normal bullet point")

  def test_plain_prose_mention(self) -> None:
    """Prose line with bare ID — ambiguous, retained as requirement-like.

    Without a clear cross-reference signal (per/parenthetical), the
    heuristic conservatively flags this to catch misformatted definitions.
    """
    assert _is_requirement_like_line(
      "This satisfies FR-001 from the product spec.",
    )

  # -- Edge cases ---------------------------------------------------------

  def test_mixed_definition_and_crossref(self) -> None:
    """Line with both a definition-position ID and a parenthetical ref.

    If 'per' appears, the whole line is treated as a cross-reference
    because the heuristic errs on the side of suppressing false positives.
    """
    assert not _is_requirement_like_line(
      "- FR-001: Implements constraint per NF-002",
    )

  def test_multiple_parenthetical_refs(self) -> None:
    """Multiple IDs all inside parentheses — still a citation."""
    assert not _is_requirement_like_line(
      "- Auth module (FR-001) and perf (NF-002) integration",
    )

  def test_case_insensitive(self) -> None:
    """Lowercase fr/nf should still be detected."""
    assert _is_requirement_like_line("- **fr-001**: lowercase definition")

  def test_empty_line(self) -> None:
    """Empty line is not requirement-like."""
    assert not _is_requirement_like_line("")

  def test_whitespace_only(self) -> None:
    """Whitespace-only line is not requirement-like."""
    assert not _is_requirement_like_line("   ")


class TestRecordsFromContentCrossRefSuppression(unittest.TestCase):
  """Integration test: _records_from_content does not warn on cross-references."""

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

  def test_crossref_only_spec_no_warning(self) -> None:
    """Spec with only cross-references should not trigger extraction warning."""
    root = self._make_repo()

    spec_dir = root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR / "spec-010-example"
    spec_dir.mkdir(parents=True, exist_ok=True)
    spec_path = spec_dir / "SPEC-010.md"
    frontmatter = {
      "id": "SPEC-010",
      "slug": "spec-010",
      "name": "Cross-ref only spec",
      "created": "2024-06-01",
      "updated": "2024-06-01",
      "status": "draft",
      "kind": "spec",
    }
    body = (
      "# SPEC-010\n\n"
      "## Responsibilities\n\n"
      "- clap command definitions (noun-verb families per PROD-004.FR-007)\n"
      "- Contractual properties (must match bough per SPEC-003.FR-006)\n"
      "- Some other thing (PROD-004.NF-001)\n"
    )
    dump_markdown_file(spec_path, frontmatter, body)

    with self.assertLogs("supekku", level="WARNING") as cm:
      # Add a dummy log to ensure assertLogs doesn't fail on no logs
      logging.getLogger("supekku").warning("SENTINEL")
      list(
        _records_from_content(
          "SPEC-010",
          dict(frontmatter),
          body,
          spec_path,
          root,
        ),
      )

    # Only the sentinel should be present, not a requirement-like warning
    for msg in cm.output:
      assert "requirement-like" not in msg, (
        f"Unexpected requirement-like warning: {msg}"
      )


if __name__ == "__main__":
  unittest.main()


if __name__ == "__main__":
  unittest.main()
