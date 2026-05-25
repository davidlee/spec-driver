"""Spec requirements block validation in WorkspaceValidator (DE-140)."""

from __future__ import annotations

import os
from typing import Any

from supekku.scripts.lib.blocks.spec_requirements import (
  REQUIREMENTS_MARKER,
  REQUIREMENTS_SCHEMA,
  REQUIREMENTS_VERSION,
  render_spec_requirements_block,
)
from supekku.scripts.lib.core.paths import (
  PRODUCT_SPECS_SUBDIR,
  SPEC_DRIVER_DIR,
  TECH_SPECS_SUBDIR,
)
from supekku.scripts.lib.core.spec_utils import dump_markdown_file_update
from supekku.scripts.lib.test_base import RepoTestCase
from supekku.scripts.lib.validation.validator import (
  check_requirements_migration_complete,
  validate_workspace,
)
from supekku.scripts.lib.workspace import Workspace


class SpecRequirementsValidationTest(RepoTestCase):
  """VT-140-015, VT-140-016, VT-140-022: spec requirements block validation."""

  def _create_repo(self):
    root = super()._make_repo()
    os.chdir(root)
    return root

  def _write_spec_with_requirements_block(
    self,
    root,
    spec_id: str,
    block_content: str,
    *,
    kind: str = "spec",
  ) -> None:
    if kind == "prod":
      spec_dir = root / SPEC_DRIVER_DIR / PRODUCT_SPECS_SUBDIR / f"{spec_id}-sample"
    else:
      spec_dir = root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR / f"{spec_id}-sample"
    spec_dir.mkdir(parents=True, exist_ok=True)
    spec_path = spec_dir / f"{spec_id}.md"
    frontmatter: dict[str, Any] = {
      "id": spec_id,
      "slug": "sample",
      "name": f"Sample {spec_id}",
      "created": "2024-06-01",
      "updated": "2024-06-01",
      "status": "draft",
      "kind": kind,
    }
    if kind == "spec":
      frontmatter["category"] = "assembly"
      frontmatter["c4_level"] = "component"
    body = f"# {spec_id}\n\n{block_content}\n"
    dump_markdown_file_update(spec_path, frontmatter, body)

  def _render_valid_block(self, spec_id: str) -> str:
    return render_spec_requirements_block(
      spec_id,
      requirements=[
        {
          "id": "FR-001",
          "title": "Test requirement",
          "lifecycle": "pending",
          "kind": "functional",
          "description": "A test requirement.",
          "acceptance_criteria": ["Passes tests"],
          "tags": [],
        },
      ],
    )

  # -- VT-140-015: WorkspaceValidator — requirements block validated --

  def test_valid_requirements_block_no_issues(self) -> None:
    """Valid requirements block produces no validation issues."""
    root = self._create_repo()
    block = self._render_valid_block("SPEC-800")
    self._write_spec_with_requirements_block(root, "SPEC-800", block)
    ws = Workspace(root)
    issues = validate_workspace(ws)
    req_issues = [
      i for i in issues
      if i.artifact == "SPEC-800" and "spec.requirements" in i.message
    ]
    assert len(req_issues) == 0

  def test_malformed_yaml_block_errors(self) -> None:
    """Malformed YAML in requirements block produces an error."""
    root = self._create_repo()
    block = (
      f"```yaml {REQUIREMENTS_MARKER}\n"
      "schema: [\n"
      "  broken yaml\n"
      "```"
    )
    self._write_spec_with_requirements_block(root, "SPEC-801", block)
    ws = Workspace(root)
    issues = validate_workspace(ws)
    errors = [
      i for i in issues
      if i.artifact == "SPEC-801"
      and i.level == "error"
      and "extraction failed" in i.message
    ]
    assert len(errors) == 1

  def test_missing_required_field_errors(self) -> None:
    """Block missing required field produces schema validation error."""
    root = self._create_repo()
    block = (
      f"```yaml {REQUIREMENTS_MARKER}\n"
      f"schema: {REQUIREMENTS_SCHEMA}\n"
      f"version: {REQUIREMENTS_VERSION}\n"
      "requirements: []\n"
      "```"
    )
    self._write_spec_with_requirements_block(root, "SPEC-802", block)
    ws = Workspace(root)
    issues = validate_workspace(ws)
    errors = [
      i for i in issues
      if i.artifact == "SPEC-802" and i.level == "error"
    ]
    assert len(errors) >= 1
    assert any(
      "spec" in e.message.lower() and "required" in e.message.lower()
      for e in errors
    )

  def test_no_block_no_issues(self) -> None:
    """Spec without requirements block produces no issues (pre-flip)."""
    root = self._create_repo()
    self._write_spec_with_requirements_block(root, "SPEC-803", "No block here.")
    ws = Workspace(root)
    issues = validate_workspace(ws)
    req_issues = [
      i for i in issues
      if i.artifact == "SPEC-803" and "spec.requirements" in i.message
    ]
    assert len(req_issues) == 0

  # -- VT-140-016: WorkspaceValidator — spec field cross-validated --

  def test_spec_field_mismatch_errors(self) -> None:
    """spec field not matching artifact ID produces an error."""
    root = self._create_repo()
    block = render_spec_requirements_block(
      "SPEC-999",
      requirements=[
        {
          "id": "FR-001",
          "title": "Test",
          "lifecycle": "pending",
          "kind": "functional",
          "description": "Desc.",
          "acceptance_criteria": ["AC"],
        },
      ],
    )
    self._write_spec_with_requirements_block(root, "SPEC-804", block)
    ws = Workspace(root)
    issues = validate_workspace(ws)
    errors = [
      i for i in issues
      if i.artifact == "SPEC-804"
      and i.level == "error"
      and "SPEC-999" in i.message
      and "SPEC-804" in i.message
    ]
    assert len(errors) >= 1

  def test_spec_field_match_no_cross_validation_error(self) -> None:
    """spec field matching artifact ID produces no cross-validation error."""
    root = self._create_repo()
    block = self._render_valid_block("SPEC-805")
    self._write_spec_with_requirements_block(root, "SPEC-805", block)
    ws = Workspace(root)
    issues = validate_workspace(ws)
    mismatch_errors = [
      i for i in issues
      if i.artifact == "SPEC-805"
      and i.level == "error"
      and "does not match" in i.message
    ]
    assert len(mismatch_errors) == 0

  def test_prod_spec_cross_validated(self) -> None:
    """PROD spec requirements block also cross-validates spec field."""
    root = self._create_repo()
    block = self._render_valid_block("PROD-800")
    self._write_spec_with_requirements_block(root, "PROD-800", block, kind="prod")
    ws = Workspace(root)
    issues = validate_workspace(ws)
    req_issues = [
      i for i in issues
      if i.artifact == "PROD-800" and "spec.requirements" in i.message
    ]
    assert len(req_issues) == 0

  # -- VT-140-022: Trimmed-empty/blank-item rejection --

  def test_strict_rejects_trimmed_empty_description(self) -> None:
    """Strict mode rejects trimmed-empty description field."""
    root = self._create_repo()
    block = (
      f"```yaml {REQUIREMENTS_MARKER}\n"
      f"schema: {REQUIREMENTS_SCHEMA}\n"
      f"version: {REQUIREMENTS_VERSION}\n"
      "spec: SPEC-806\n"
      "requirements:\n"
      "  - id: FR-001\n"
      "    title: Test\n"
      "    lifecycle: pending\n"
      "    kind: functional\n"
      '    description: ""\n'
      "    acceptance_criteria:\n"
      "      - Valid criterion\n"
      "```"
    )
    self._write_spec_with_requirements_block(root, "SPEC-806", block)
    ws = Workspace(root)

    # Non-strict: permitted
    issues = validate_workspace(ws, strict=False)
    empty_desc_errors = [
      i for i in issues
      if i.artifact == "SPEC-806"
      and i.level == "error"
      and "description" in i.message.lower()
      and ("empty" in i.message.lower() or "trimmed" in i.message.lower())
    ]
    assert len(empty_desc_errors) == 0

    # Strict: rejected
    issues = validate_workspace(ws, strict=True)
    empty_desc_errors = [
      i for i in issues
      if i.artifact == "SPEC-806"
      and i.level == "error"
      and "description" in i.message.lower()
      and ("empty" in i.message.lower() or "trimmed" in i.message.lower())
    ]
    assert len(empty_desc_errors) >= 1

  def test_strict_rejects_blank_acceptance_criteria_items(self) -> None:
    """Strict mode rejects blank items in acceptance_criteria."""
    root = self._create_repo()
    block = (
      f"```yaml {REQUIREMENTS_MARKER}\n"
      f"schema: {REQUIREMENTS_SCHEMA}\n"
      f"version: {REQUIREMENTS_VERSION}\n"
      "spec: SPEC-807\n"
      "requirements:\n"
      "  - id: FR-001\n"
      "    title: Test\n"
      "    lifecycle: pending\n"
      "    kind: functional\n"
      "    description: Valid description.\n"
      "    acceptance_criteria:\n"
      '      - ""\n'
      "      - Valid criterion\n"
      "```"
    )
    self._write_spec_with_requirements_block(root, "SPEC-807", block)
    ws = Workspace(root)

    # Non-strict: permitted
    issues = validate_workspace(ws, strict=False)
    blank_ac_errors = [
      i for i in issues
      if i.artifact == "SPEC-807"
      and i.level == "error"
      and "acceptance_criteria" in i.message
      and "blank" in i.message.lower()
    ]
    assert len(blank_ac_errors) == 0

    # Strict: rejected
    issues = validate_workspace(ws, strict=True)
    blank_ac_errors = [
      i for i in issues
      if i.artifact == "SPEC-807"
      and i.level == "error"
      and "acceptance_criteria" in i.message
      and "blank" in i.message.lower()
    ]
    assert len(blank_ac_errors) >= 1

  def test_strict_rejects_empty_acceptance_criteria_list(self) -> None:
    """Strict mode rejects empty acceptance_criteria list."""
    root = self._create_repo()
    block = (
      f"```yaml {REQUIREMENTS_MARKER}\n"
      f"schema: {REQUIREMENTS_SCHEMA}\n"
      f"version: {REQUIREMENTS_VERSION}\n"
      "spec: SPEC-808\n"
      "requirements:\n"
      "  - id: FR-001\n"
      "    title: Test\n"
      "    lifecycle: pending\n"
      "    kind: functional\n"
      "    description: Valid description.\n"
      "    acceptance_criteria: []\n"
      "```"
    )
    self._write_spec_with_requirements_block(root, "SPEC-808", block)
    ws = Workspace(root)

    # Non-strict: permitted
    issues = validate_workspace(ws, strict=False)
    empty_ac_errors = [
      i for i in issues
      if i.artifact == "SPEC-808"
      and i.level == "error"
      and "acceptance_criteria" in i.message
      and "empty" in i.message.lower()
    ]
    assert len(empty_ac_errors) == 0

    # Strict: rejected
    issues = validate_workspace(ws, strict=True)
    empty_ac_errors = [
      i for i in issues
      if i.artifact == "SPEC-808"
      and i.level == "error"
      and "acceptance_criteria" in i.message
      and "empty" in i.message.lower()
    ]
    assert len(empty_ac_errors) >= 1

  def test_non_strict_permits_empty_fields(self) -> None:
    """Non-strict mode permits empty description and acceptance_criteria."""
    root = self._create_repo()
    block = (
      f"```yaml {REQUIREMENTS_MARKER}\n"
      f"schema: {REQUIREMENTS_SCHEMA}\n"
      f"version: {REQUIREMENTS_VERSION}\n"
      "spec: SPEC-809\n"
      "requirements:\n"
      "  - id: FR-001\n"
      "    title: Test\n"
      "    lifecycle: pending\n"
      "    kind: functional\n"
      '    description: ""\n'
      "    acceptance_criteria: []\n"
      "```"
    )
    self._write_spec_with_requirements_block(root, "SPEC-809", block)
    ws = Workspace(root)
    issues = validate_workspace(ws, strict=False)
    req_errors = [
      i for i in issues
      if i.artifact == "SPEC-809" and i.level == "error"
    ]
    assert len(req_errors) == 0


class StrictMissingBlockTest(RepoTestCase):
  """VT-140-017: strict mode — missing block → error."""

  def _create_repo(self):
    root = super()._make_repo()
    os.chdir(root)
    return root

  def _write_spec_without_block(
    self,
    root,
    spec_id: str,
    *,
    kind: str = "spec",
  ) -> None:
    if kind == "prod":
      spec_dir = root / SPEC_DRIVER_DIR / PRODUCT_SPECS_SUBDIR / f"{spec_id}-sample"
    else:
      spec_dir = root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR / f"{spec_id}-sample"
    spec_dir.mkdir(parents=True, exist_ok=True)
    spec_path = spec_dir / f"{spec_id}.md"
    frontmatter: dict[str, Any] = {
      "id": spec_id,
      "slug": "sample",
      "name": f"Sample {spec_id}",
      "created": "2024-06-01",
      "updated": "2024-06-01",
      "status": "draft",
      "kind": kind,
    }
    if kind == "spec":
      frontmatter["category"] = "assembly"
      frontmatter["c4_level"] = "component"
    body = f"# {spec_id}\n\nNo requirements block here.\n"
    dump_markdown_file_update(spec_path, frontmatter, body)

  def test_strict_missing_block_errors(self) -> None:
    """Strict mode: spec without requirements block produces error."""
    root = self._create_repo()
    self._write_spec_without_block(root, "SPEC-850")
    ws = Workspace(root)
    issues = validate_workspace(ws, strict=True)
    missing_errors = [
      i for i in issues
      if i.artifact == "SPEC-850"
      and i.level == "error"
      and "missing" in i.message.lower()
    ]
    assert len(missing_errors) >= 1

  def test_non_strict_missing_block_no_error(self) -> None:
    """Non-strict mode: spec without requirements block is tolerated."""
    root = self._create_repo()
    self._write_spec_without_block(root, "SPEC-851")
    ws = Workspace(root)
    issues = validate_workspace(ws, strict=False)
    missing_errors = [
      i for i in issues
      if i.artifact == "SPEC-851"
      and "missing" in i.message.lower()
      and "spec.requirements" in i.message.lower()
    ]
    assert len(missing_errors) == 0

  def test_strict_prod_missing_block_errors(self) -> None:
    """Strict mode: PROD spec without block also errors."""
    root = self._create_repo()
    self._write_spec_without_block(root, "PROD-850", kind="prod")
    ws = Workspace(root)
    issues = validate_workspace(ws, strict=True)
    missing_errors = [
      i for i in issues
      if i.artifact == "PROD-850"
      and i.level == "error"
      and "missing" in i.message.lower()
    ]
    assert len(missing_errors) >= 1


class OperationalGuardTest(RepoTestCase):
  """VT-140-029: strict flip blocked when unmigrated files remain."""

  def _create_repo(self):
    root = super()._make_repo()
    os.chdir(root)
    return root

  def _write_spec_with_block(self, root, spec_id: str) -> None:
    spec_dir = root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR / f"{spec_id}-sample"
    spec_dir.mkdir(parents=True, exist_ok=True)
    spec_path = spec_dir / f"{spec_id}.md"
    frontmatter: dict[str, Any] = {
      "id": spec_id,
      "slug": "sample",
      "name": f"Sample {spec_id}",
      "created": "2024-06-01",
      "updated": "2024-06-01",
      "status": "draft",
      "kind": "spec",
      "category": "assembly",
      "c4_level": "component",
    }
    block = render_spec_requirements_block(spec_id)
    body = f"# {spec_id}\n\n{block}\n"
    dump_markdown_file_update(spec_path, frontmatter, body)

  def _write_spec_without_block(self, root, spec_id: str) -> None:
    spec_dir = root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR / f"{spec_id}-sample"
    spec_dir.mkdir(parents=True, exist_ok=True)
    spec_path = spec_dir / f"{spec_id}.md"
    frontmatter: dict[str, Any] = {
      "id": spec_id,
      "slug": "sample",
      "name": f"Sample {spec_id}",
      "created": "2024-06-01",
      "updated": "2024-06-01",
      "status": "draft",
      "kind": "spec",
      "category": "assembly",
      "c4_level": "component",
    }
    body = f"# {spec_id}\n\nNo block.\n"
    dump_markdown_file_update(spec_path, frontmatter, body)

  def test_all_migrated_returns_empty(self) -> None:
    """Guard returns empty list when all specs have blocks."""
    root = self._create_repo()
    self._write_spec_with_block(root, "SPEC-900")
    self._write_spec_with_block(root, "SPEC-901")
    ws = Workspace(root)
    unmigrated = check_requirements_migration_complete(ws)
    assert unmigrated == []

  def test_unmigrated_returns_ids(self) -> None:
    """Guard returns IDs of specs without blocks."""
    root = self._create_repo()
    self._write_spec_with_block(root, "SPEC-900")
    self._write_spec_without_block(root, "SPEC-901")
    ws = Workspace(root)
    unmigrated = check_requirements_migration_complete(ws)
    assert "SPEC-901" in unmigrated
    assert "SPEC-900" not in unmigrated

  def test_no_specs_returns_empty(self) -> None:
    """Guard returns empty list when workspace has no specs."""
    root = self._create_repo()
    ws = Workspace(root)
    unmigrated = check_requirements_migration_complete(ws)
    assert unmigrated == []

  def test_malformed_block_counts_as_unmigrated(self) -> None:
    """Spec with malformed requirements block is unmigrated."""
    root = self._create_repo()
    spec_dir = root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR / "SPEC-902-sample"
    spec_dir.mkdir(parents=True, exist_ok=True)
    spec_path = spec_dir / "SPEC-902.md"
    frontmatter: dict[str, Any] = {
      "id": "SPEC-902",
      "slug": "sample",
      "name": "Sample SPEC-902",
      "created": "2024-06-01",
      "updated": "2024-06-01",
      "status": "draft",
      "kind": "spec",
      "category": "assembly",
      "c4_level": "component",
    }
    body = (
      "# SPEC-902\n\n"
      f"```yaml {REQUIREMENTS_MARKER}\n"
      "schema: [\n"
      "  broken yaml\n"
      "```\n"
    )
    dump_markdown_file_update(spec_path, frontmatter, body)
    ws = Workspace(root)
    unmigrated = check_requirements_migration_complete(ws)
    assert "SPEC-902" in unmigrated
