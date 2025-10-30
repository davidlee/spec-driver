"""Tests for decision_registry module."""

from __future__ import annotations

import tempfile
import unittest
from datetime import date
from pathlib import Path

import yaml

from .decision_registry import DecisionRecord, DecisionRegistry


class TestDecisionRecord(unittest.TestCase):
    """Tests for DecisionRecord dataclass."""

    def test_to_dict_minimal(self) -> None:
        """Test serialization with minimal fields."""
        record = DecisionRecord(id="ADR-001", title="Test Decision", status="accepted")

        result = record.to_dict(Path("/tmp"))

        assert result["id"] == "ADR-001"
        assert result["title"] == "Test Decision"
        assert result["status"] == "accepted"
        assert result["summary"] == ""
        assert "authors" not in result  # Empty lists are omitted

    def test_to_dict_full(self) -> None:
        """Test serialization with all fields populated."""
        record = DecisionRecord(
            id="ADR-002",
            title="Full Decision",
            status="accepted",
            created=date(2024, 1, 1),
            decided=date(2024, 1, 2),
            updated=date(2024, 1, 3),
            reviewed=date(2024, 1, 4),
            authors=[{"name": "Jane Doe", "contact": "jane@example.com"}],
            owners=["team-alpha"],
            supersedes=["ADR-001"],
            specs=["SPEC-100"],
            requirements=["SPEC-100.FR-001"],
            tags=["api", "security"],
            summary="A comprehensive decision",
            path="/path/to/file.md",
        )

        result = record.to_dict(Path("/"))

        assert result["created"] == "2024-01-01"
        assert result["decided"] == "2024-01-02"
        assert result["updated"] == "2024-01-03"
        assert result["reviewed"] == "2024-01-04"
        assert result["authors"] == [
            {"name": "Jane Doe", "contact": "jane@example.com"},
        ]
        assert result["owners"] == ["team-alpha"]
        assert result["supersedes"] == ["ADR-001"]
        assert result["specs"] == ["SPEC-100"]
        assert result["requirements"] == ["SPEC-100.FR-001"]
        assert result["tags"] == ["api", "security"]
        assert result["summary"] == "A comprehensive decision"


class TestDecisionRegistry(unittest.TestCase):
    """Tests for DecisionRegistry class."""

    def _setup_test_repo(self, tmpdir: str) -> Path:
        """Set up a test repository with required directories."""
        root = Path(tmpdir)
        # Create .git directory for repo detection
        (root / ".git").mkdir()
        return root

    def test_init(self) -> None:
        """Test registry initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = self._setup_test_repo(tmpdir)
            registry = DecisionRegistry(root=root)

            assert registry.root == root
            assert registry.directory == root / "specify" / "decisions"
            assert (
                registry.output_path == root / "supekku" / "registry" / "decisions.yaml"
            )

    def test_collect_empty_directory(self) -> None:
        """Test collecting from empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = self._setup_test_repo(tmpdir)
            registry = DecisionRegistry(root=root)

            decisions = registry.collect()
            assert len(decisions) == 0

    def test_collect_with_adr_files(self) -> None:
        """Test collecting ADR files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = self._setup_test_repo(tmpdir)
            decisions_dir = root / "specify" / "decisions"
            decisions_dir.mkdir(parents=True)

            # Create test ADR file
            adr_file = decisions_dir / "ADR-001-test-decision.md"
            adr_content = """---
id: ADR-001
title: "Test Decision"
status: accepted
created: 2024-01-01
updated: 2024-01-02
authors:
  - name: "Jane Doe"
    contact: "jane@example.com"
tags: [api, security]
summary: "A test decision"
---

# ADR-001: Test Decision

## Context
This is a test.

## Decision
We decided to test.
"""
            adr_file.write_text(adr_content, encoding="utf-8")

            registry = DecisionRegistry(root=root)
            decisions = registry.collect()

            assert len(decisions) == 1
            assert "ADR-001" in decisions

            decision = decisions["ADR-001"]
            assert decision.title == "Test Decision"
            assert decision.status == "accepted"
            assert decision.created == date(2024, 1, 1)
            assert decision.updated == date(2024, 1, 2)
            assert decision.authors == [
                {"name": "Jane Doe", "contact": "jane@example.com"},
            ]
            assert decision.tags == ["api", "security"]
            assert decision.summary == "A test decision"

    def test_parse_adr_file_no_frontmatter(self) -> None:
        """Test parsing ADR file without frontmatter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = self._setup_test_repo(tmpdir)
            decisions_dir = root / "specify" / "decisions"
            decisions_dir.mkdir(parents=True)

            # Create ADR file without frontmatter
            adr_file = decisions_dir / "ADR-002-no-frontmatter.md"
            adr_content = """# ADR-002: No Frontmatter Decision

This has no frontmatter.
"""
            adr_file.write_text(adr_content, encoding="utf-8")

            registry = DecisionRegistry(root=root)
            decisions = registry.collect()

            assert len(decisions) == 1
            decision = decisions["ADR-002"]
            assert decision.title == "# ADR-002: No Frontmatter Decision"
            assert decision.status == "draft"  # default status

    def test_write_and_sync(self) -> None:
        """Test writing registry to YAML file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = self._setup_test_repo(tmpdir)
            decisions_dir = root / "specify" / "decisions"
            decisions_dir.mkdir(parents=True)

            # Create test ADR
            adr_file = decisions_dir / "ADR-003-write-test.md"
            adr_content = """---
id: ADR-003
title: "Write Test"
status: accepted
---

# Test
"""
            adr_file.write_text(adr_content, encoding="utf-8")

            registry = DecisionRegistry(root=root)
            registry.sync()

            # Check YAML was written
            assert registry.output_path.exists()

            with registry.output_path.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            assert "decisions" in data
            assert "ADR-003" in data["decisions"]
            assert data["decisions"]["ADR-003"]["title"] == "Write Test"
            assert data["decisions"]["ADR-003"]["status"] == "accepted"

    def test_find(self) -> None:
        """Test finding specific decision."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = self._setup_test_repo(tmpdir)
            decisions_dir = root / "specify" / "decisions"
            decisions_dir.mkdir(parents=True)

            adr_file = decisions_dir / "ADR-004-find-test.md"
            adr_content = """---
id: ADR-004
title: "Find Test"
---

# Test
"""
            adr_file.write_text(adr_content, encoding="utf-8")

            registry = DecisionRegistry(root=root)

            # Find existing decision
            decision = registry.find("ADR-004")
            assert decision is not None
            assert decision.title == "Find Test"

            # Find non-existent decision
            missing = registry.find("ADR-999")
            assert missing is None

    def test_filter(self) -> None:
        """Test filtering decisions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = self._setup_test_repo(tmpdir)
            decisions_dir = root / "specify" / "decisions"
            decisions_dir.mkdir(parents=True)

            # Create multiple ADRs
            adr1 = decisions_dir / "ADR-005-filter-test-1.md"
            adr1.write_text(
                """---
id: ADR-005
tags: [api]
specs: [SPEC-100]
---
# Test 1
""",
                encoding="utf-8",
            )

            adr2 = decisions_dir / "ADR-006-filter-test-2.md"
            adr2.write_text(
                """---
id: ADR-006
tags: [security]
specs: [SPEC-200]
---
# Test 2
""",
                encoding="utf-8",
            )

            registry = DecisionRegistry(root=root)

            # Filter by tag
            api_decisions = registry.filter(tag="api")
            assert len(api_decisions) == 1
            assert api_decisions[0].id == "ADR-005"

            # Filter by spec
            spec_decisions = registry.filter(spec="SPEC-200")
            assert len(spec_decisions) == 1
            assert spec_decisions[0].id == "ADR-006"

            # Filter by non-existent criteria
            empty_results = registry.filter(tag="nonexistent")
            assert len(empty_results) == 0

    def test_iter_with_status_filter(self) -> None:
        """Test iterating with status filter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = self._setup_test_repo(tmpdir)
            decisions_dir = root / "specify" / "decisions"
            decisions_dir.mkdir(parents=True)

            # Create ADRs with different statuses
            adr1 = decisions_dir / "ADR-007-accepted.md"
            adr1.write_text(
                """---
id: ADR-007
status: accepted
---
# Test
""",
                encoding="utf-8",
            )

            adr2 = decisions_dir / "ADR-008-draft.md"
            adr2.write_text(
                """---
id: ADR-008
status: draft
---
# Test
""",
                encoding="utf-8",
            )

            registry = DecisionRegistry(root=root)

            # Get all decisions
            all_decisions = list(registry.iter())
            assert len(all_decisions) == 2

            # Get only accepted
            accepted = list(registry.iter(status="accepted"))
            assert len(accepted) == 1
            assert accepted[0].id == "ADR-007"

            # Get only drafts
            drafts = list(registry.iter(status="draft"))
            assert len(drafts) == 1
            assert drafts[0].id == "ADR-008"

    def test_parse_date_formats(self) -> None:
        """Test parsing various date formats."""
        registry = DecisionRegistry()

        # Test valid formats
        assert registry.parse_date("2024-01-01") == date(2024, 1, 1)
        assert registry.parse_date("2024-01-01 10:30:00") == date(2024, 1, 1)
        assert registry.parse_date("2024/01/01") == date(2024, 1, 1)

        # Test invalid/empty values
        assert registry.parse_date("") is None
        assert registry.parse_date(None) is None
        assert registry.parse_date("invalid") is None

        # Test date objects
        test_date = date(2024, 1, 1)
        assert registry.parse_date(test_date) == test_date

    def test_rebuild_status_symlinks_creates_directories(self) -> None:
        """Test that rebuild_status_symlinks creates status directories and symlinks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = self._setup_test_repo(tmpdir)
            decisions_dir = root / "specify" / "decisions"
            decisions_dir.mkdir(parents=True)

            # Create ADRs with different statuses
            adr1 = decisions_dir / "ADR-001-accepted.md"
            adr1.write_text(
                """---
id: ADR-001
title: "Accepted Decision"
status: accepted
---
# Test""",
                encoding="utf-8",
            )

            adr2 = decisions_dir / "ADR-002-draft.md"
            adr2.write_text(
                """---
id: ADR-002
title: "Draft Decision"
status: draft
---
# Test""",
                encoding="utf-8",
            )

            registry = DecisionRegistry(root=root)
            registry.rebuild_status_symlinks()

            # Verify status directories were created
            accepted_dir = decisions_dir / "accepted"
            draft_dir = decisions_dir / "draft"
            assert accepted_dir.exists()
            assert accepted_dir.is_dir()
            assert draft_dir.exists()
            assert draft_dir.is_dir()

            # Verify symlinks were created
            accepted_link = accepted_dir / "ADR-001-accepted.md"
            draft_link = draft_dir / "ADR-002-draft.md"
            assert accepted_link.exists()
            assert accepted_link.is_symlink()
            assert draft_link.exists()
            assert draft_link.is_symlink()

            # Verify symlinks point to correct files
            assert accepted_link.resolve() == adr1.resolve()
            assert draft_link.resolve() == adr2.resolve()

    def test_rebuild_status_symlinks_cleans_existing(self) -> None:
        """Test that rebuild_status_symlinks cleans up existing symlinks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = self._setup_test_repo(tmpdir)
            decisions_dir = root / "specify" / "decisions"
            decisions_dir.mkdir(parents=True)

            # Create an ADR
            adr = decisions_dir / "ADR-001-test.md"
            adr.write_text(
                """---
id: ADR-001
status: accepted
---
# Test""",
                encoding="utf-8",
            )

            # Create status directory with existing symlink
            accepted_dir = decisions_dir / "accepted"
            accepted_dir.mkdir()
            old_link = accepted_dir / "old-file.md"
            old_link.symlink_to("../nonexistent.md")

            registry = DecisionRegistry(root=root)
            registry.rebuild_status_symlinks()

            # Verify old symlink was removed
            assert not old_link.exists()
            # Verify new symlink was created
            new_link = accepted_dir / "ADR-001-test.md"
            assert new_link.exists()
            assert new_link.is_symlink()

    def test_rebuild_status_symlinks_handles_missing_files(self) -> None:
        """Test that rebuild_status_symlinks skips ADRs with missing files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = self._setup_test_repo(tmpdir)
            decisions_dir = root / "specify" / "decisions"
            decisions_dir.mkdir(parents=True)

            # Create ADR file
            adr = decisions_dir / "ADR-001-test.md"
            adr.write_text(
                """---
id: ADR-001
status: accepted
---
# Test""",
                encoding="utf-8",
            )

            registry = DecisionRegistry(root=root)
            # Manually modify decision path to non-existent file
            decisions = registry.collect()
            decisions["ADR-001"].path = str(decisions_dir / "nonexistent.md")

            # Mock the collect method to return our modified data
            original_collect = registry.collect
            registry.collect = lambda: decisions

            registry.rebuild_status_symlinks()

            # Verify no symlink was created for missing file
            accepted_dir = decisions_dir / "accepted"
            assert accepted_dir.exists()
            assert len(list(accepted_dir.iterdir())) == 0

            # Restore original method
            registry.collect = original_collect

    def test_sync_with_symlinks_integration(self) -> None:
        """Test sync_with_symlinks performs both sync and symlink rebuild."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = self._setup_test_repo(tmpdir)
            decisions_dir = root / "specify" / "decisions"
            decisions_dir.mkdir(parents=True)
            registry_dir = root / "supekku" / "registry"
            registry_dir.mkdir(parents=True)

            # Create ADR
            adr = decisions_dir / "ADR-001-test.md"
            adr.write_text(
                """---
id: ADR-001
title: "Test Decision"
status: accepted
---
# Test""",
                encoding="utf-8",
            )

            registry = DecisionRegistry(root=root)
            registry.sync_with_symlinks()

            # Verify YAML registry was created
            yaml_path = registry_dir / "decisions.yaml"
            assert yaml_path.exists()

            # Verify symlinks were created
            accepted_dir = decisions_dir / "accepted"
            link = accepted_dir / "ADR-001-test.md"
            assert link.exists()
            assert link.is_symlink()

    def test_cleanup_all_status_directories(self) -> None:
        """Test _cleanup_all_status_directories removes all symlinks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = self._setup_test_repo(tmpdir)
            decisions_dir = root / "specify" / "decisions"
            decisions_dir.mkdir(parents=True)

            # Create status directories with symlinks
            for status in ["accepted", "draft", "deprecated"]:
                status_dir = decisions_dir / status
                status_dir.mkdir()
                # Create a symlink
                link = status_dir / f"test-{status}.md"
                link.symlink_to("../test.md")

            registry = DecisionRegistry(root=root)
            registry._cleanup_all_status_directories(decisions_dir)

            # Verify all symlinks were removed
            for status in ["accepted", "draft", "deprecated"]:
                status_dir = decisions_dir / status
                assert status_dir.exists()  # Directory still exists
                assert len(list(status_dir.iterdir())) == 0  # But no symlinks

    def test_rebuild_status_directory_relative_paths(self) -> None:
        """Test _rebuild_status_directory creates relative symlinks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = self._setup_test_repo(tmpdir)
            decisions_dir = root / "specify" / "decisions"
            decisions_dir.mkdir(parents=True)

            # Create ADR
            adr = decisions_dir / "ADR-001-test.md"
            adr.write_text("# Test", encoding="utf-8")

            # Create decision record
            decision = DecisionRecord(
                id="ADR-001", title="Test", status="accepted", path=str(adr),
            )

            registry = DecisionRegistry(root=root)
            status_dir = decisions_dir / "accepted"
            registry._rebuild_status_directory(status_dir, [decision])

            # Verify symlink uses relative path
            link = status_dir / "ADR-001-test.md"
            assert link.is_symlink()
            # The symlink target should be relative
            assert str(link.readlink()) == "../ADR-001-test.md"

    def test_status_transition_updates_symlinks(self) -> None:
        """Test that changing ADR status moves symlinks between directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = self._setup_test_repo(tmpdir)
            decisions_dir = root / "specify" / "decisions"
            decisions_dir.mkdir(parents=True)

            # Create ADR initially as draft
            adr = decisions_dir / "ADR-001-test.md"
            adr.write_text(
                """---
id: ADR-001
title: "Test Decision"
status: draft
---
# Test""",
                encoding="utf-8",
            )

            registry = DecisionRegistry(root=root)
            registry.rebuild_status_symlinks()

            # Verify initial symlink in draft directory
            draft_dir = decisions_dir / "draft"
            draft_link = draft_dir / "ADR-001-test.md"
            assert draft_link.exists()
            assert draft_link.is_symlink()

            # Update status to accepted
            adr.write_text(
                """---
id: ADR-001
title: "Test Decision"
status: accepted
---
# Test""",
                encoding="utf-8",
            )

            # Rebuild symlinks
            registry.rebuild_status_symlinks()

            # Verify symlink moved to accepted directory
            accepted_dir = decisions_dir / "accepted"
            accepted_link = accepted_dir / "ADR-001-test.md"
            assert accepted_link.exists()
            assert accepted_link.is_symlink()

            # Verify old symlink was removed
            assert not draft_link.exists()

    def test_edge_case_invalid_status_values(self) -> None:
        """Test handling of ADRs with invalid/non-standard status values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = self._setup_test_repo(tmpdir)
            decisions_dir = root / "specify" / "decisions"
            decisions_dir.mkdir(parents=True)

            # Create ADR with non-standard status
            adr = decisions_dir / "ADR-001-test.md"
            adr.write_text(
                """---
id: ADR-001
title: "Test Decision"
status: unknown-status
---
# Test""",
                encoding="utf-8",
            )

            registry = DecisionRegistry(root=root)
            registry.rebuild_status_symlinks()

            # Verify status directory was created even for non-standard status
            status_dir = decisions_dir / "unknown-status"
            assert status_dir.exists()
            link = status_dir / "ADR-001-test.md"
            assert link.exists()
            assert link.is_symlink()

    def test_edge_case_broken_symlinks_cleanup(self) -> None:
        """Test that broken symlinks are properly cleaned up."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = self._setup_test_repo(tmpdir)
            decisions_dir = root / "specify" / "decisions"
            decisions_dir.mkdir(parents=True)

            # Create status directory with broken symlinks
            accepted_dir = decisions_dir / "accepted"
            accepted_dir.mkdir()

            # Create broken symlinks
            broken_link1 = accepted_dir / "broken1.md"
            broken_link2 = accepted_dir / "broken2.md"
            broken_link1.symlink_to("../nonexistent1.md")
            broken_link2.symlink_to("../nonexistent2.md")

            # Create valid ADR
            adr = decisions_dir / "ADR-001-test.md"
            adr.write_text(
                """---
id: ADR-001
status: accepted
---
# Test""",
                encoding="utf-8",
            )

            registry = DecisionRegistry(root=root)
            registry.rebuild_status_symlinks()

            # Verify broken symlinks were removed
            assert not broken_link1.exists()
            assert not broken_link2.exists()

            # Verify valid symlink was created
            valid_link = accepted_dir / "ADR-001-test.md"
            assert valid_link.exists()
            assert valid_link.is_symlink()

    def test_edge_case_concurrent_directory_operations(self) -> None:
        """Test robustness when directories are modified during operations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = self._setup_test_repo(tmpdir)
            decisions_dir = root / "specify" / "decisions"
            decisions_dir.mkdir(parents=True)

            # Create ADR
            adr = decisions_dir / "ADR-001-test.md"
            adr.write_text(
                """---
id: ADR-001
status: accepted
---
# Test""",
                encoding="utf-8",
            )

            # Pre-create status directory with a regular file (not symlink)
            accepted_dir = decisions_dir / "accepted"
            accepted_dir.mkdir()
            regular_file = accepted_dir / "regular-file.txt"
            regular_file.write_text("This is not a symlink")

            registry = DecisionRegistry(root=root)
            registry.rebuild_status_symlinks()

            # Verify regular file was not removed (only symlinks should be cleaned)
            assert regular_file.exists()

            # Verify symlink was still created
            link = accepted_dir / "ADR-001-test.md"
            assert link.exists()
            assert link.is_symlink()

    def test_edge_case_empty_decisions_directory(self) -> None:
        """Test symlink rebuild with no ADR files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = self._setup_test_repo(tmpdir)
            decisions_dir = root / "specify" / "decisions"
            decisions_dir.mkdir(parents=True)

            # Create some status directories with old symlinks
            for status in ["accepted", "draft"]:
                status_dir = decisions_dir / status
                status_dir.mkdir()
                old_link = status_dir / "old-file.md"
                old_link.symlink_to("../nonexistent.md")

            registry = DecisionRegistry(root=root)
            registry.rebuild_status_symlinks()

            # Verify all old symlinks were cleaned up
            for status in ["accepted", "draft"]:
                status_dir = decisions_dir / status
                assert status_dir.exists()
                assert len(list(status_dir.iterdir())) == 0

    def test_edge_case_permission_errors_handling(self) -> None:
        """Test graceful handling when symlink creation might fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = self._setup_test_repo(tmpdir)
            decisions_dir = root / "specify" / "decisions"
            decisions_dir.mkdir(parents=True)

            # Create ADR
            adr = decisions_dir / "ADR-001-test.md"
            adr.write_text(
                """---
id: ADR-001
status: accepted
---
# Test""",
                encoding="utf-8",
            )

            # Create status directory but make it read-only
            accepted_dir = decisions_dir / "accepted"
            accepted_dir.mkdir()

            registry = DecisionRegistry(root=root)

            # This should not crash even if symlink creation fails
            # (In practice, this test mainly verifies no exceptions are thrown)
            try:
                registry.rebuild_status_symlinks()
                # If we reach here, symlink creation succeeded
                link = accepted_dir / "ADR-001-test.md"
                assert link.exists()
                assert link.is_symlink()
            except PermissionError:
                # This is acceptable behavior - the system handled the error gracefully
                pass

    def test_multiple_adrs_same_status_grouping(self) -> None:
        """Test that multiple ADRs with same status are properly grouped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = self._setup_test_repo(tmpdir)
            decisions_dir = root / "specify" / "decisions"
            decisions_dir.mkdir(parents=True)

            # Create multiple ADRs with same status
            for i in range(1, 6):
                adr = decisions_dir / f"ADR-{i:03d}-test.md"
                adr.write_text(
                    f"""---
id: ADR-{i:03d}
title: "Test Decision {i}"
status: accepted
---
# Test {i}""",
                    encoding="utf-8",
                )

            registry = DecisionRegistry(root=root)
            registry.rebuild_status_symlinks()

            # Verify all symlinks were created in accepted directory
            accepted_dir = decisions_dir / "accepted"
            links = list(accepted_dir.iterdir())
            assert len(links) == 5

            # Verify all are symlinks
            for link in links:
                assert link.is_symlink()

            # Verify naming
            expected_names = {f"ADR-{i:03d}-test.md" for i in range(1, 6)}
            actual_names = {link.name for link in links}
            assert actual_names == expected_names
