"""Tests for list_changes functionality."""

from __future__ import annotations

from pathlib import Path

import pytest

from supekku.scripts.lib.spec_utils import dump_markdown_file
from supekku.scripts.list_changes import main as list_changes_main


@pytest.fixture
def temp_repo(tmp_path: Path) -> Path:
    root = tmp_path
    (root / ".git").mkdir()
    return root


def _write_change(
    root: Path,
    kind: str,
    artifact_id: str,
    *,
    status: str = "draft",
    applies_to: list[str] | None = None,
    relations: list[tuple[str, str]] | None = None,
    plan_block: str | None = None,
    phases: dict[str, str] | None = None,
) -> Path:
    directory = root / "change" / f"{kind}s" / f"{artifact_id.lower()}-bundle"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{artifact_id}.md"
    frontmatter = {
        "id": artifact_id,
        "slug": artifact_id.lower(),
        "name": artifact_id,
        "created": "2024-01-01",
        "updated": "2024-01-01",
        "status": status,
        "kind": kind,
    }
    if applies_to:
        frontmatter["applies_to"] = {"requirements": applies_to}
    if relations:
        frontmatter["relations"] = [
            {"type": rel_type, "target": target} for rel_type, target in relations
        ]
    dump_markdown_file(path, frontmatter, f"# {artifact_id}\n")

    if plan_block:
        plan_id = artifact_id.replace("DE", "IP")
        plan_path = directory / f"{plan_id}.md"
        dump_markdown_file(
            plan_path,
            {
                "id": plan_id,
                "slug": plan_id.lower(),
                "name": f"Implementation Plan – {artifact_id}",
                "created": "2024-01-01",
                "updated": "2024-01-01",
                "status": "draft",
                "kind": "plan",
            },
            plan_block,
        )

    if phases:
        phases_dir = directory / "phases"
        phases_dir.mkdir(exist_ok=True)
        for filename, body in phases.items():
            phase_id = (
                artifact_id.replace("DE", "IP")
                + "."
                + filename.replace(".md", "").upper()
            ).replace("-", ".")
            dump_markdown_file(
                phases_dir / filename,
                {
                    "id": phase_id,
                    "slug": filename.replace(".md", ""),
                    "name": filename.replace(".md", ""),
                    "created": "2024-01-01",
                    "updated": "2024-01-01",
                    "status": "draft",
                    "kind": "phase",
                },
                body,
            )
    return path


def _run(args: list[str], *, root: Path) -> list[str]:
    import io
    from contextlib import redirect_stdout

    buf = io.StringIO()
    with redirect_stdout(buf):
        list_changes_main(["--root", str(root), *args])
    return [line for line in buf.getvalue().splitlines() if line.strip()]


def test_lists_all_kinds(temp_repo: Path) -> None:
    _write_change(temp_repo, "delta", "DE-010")
    _write_change(temp_repo, "revision", "RE-020")

    lines = _run([], root=temp_repo)
    assert lines == ["DE-010\tdelta\tdraft\tde-010", "RE-020\trevision\tdraft\tre-020"]


def test_filters_by_kind_and_status(temp_repo: Path) -> None:
    _write_change(temp_repo, "delta", "DE-001", status="draft")
    _write_change(temp_repo, "delta", "DE-002", status="pending")

    lines = _run(["--kind", "delta", "--status", "pending"], root=temp_repo)
    assert lines == ["DE-002\tdelta\tpending\tde-002"]


def test_filters_by_applies_and_includes_metadata(temp_repo: Path) -> None:
    _write_change(
        temp_repo,
        "revision",
        "RE-050",
        applies_to=["SPEC-001.FR-001"],
        relations=[("introduces", "SPEC-001.FR-001")],
    )
    lines = _run(
        [
            "--applies-to",
            "SPEC-001.FR-001",
            "--kind",
            "revision",
            "--applies",
            "--relations",
        ],
        root=temp_repo,
    )
    assert lines == [
        "RE-050\trevision\tdraft\tre-050\tSPEC-001.FR-001\tintroduces:SPEC-001.FR-001",
    ]


def test_plan_flag_outputs_plan_summary(temp_repo: Path) -> None:
    from textwrap import dedent

    plan_block = dedent(
        """```yaml supekku:plan.overview@v1
schema: supekku.plan.overview
version: 1
plan: IP-010
delta: DE-010
revision_links:
  aligns_with: []
specs:
  primary:
    - SPEC-100
  collaborators: []
requirements:
  targets:
    - SPEC-100.FR-001
  dependencies: []
phases:
  - id: IP-010.PHASE-01
    name: Phase 01
    objective: >-
      Initial implementation.
    entrance_criteria: []
    exit_criteria: []
```

# IP-010 – Example Plan
""",
    )

    phase_body = dedent(
        """```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-010.PHASE-01
plan: IP-010
delta: DE-010
objective: >-
  Build MVP.
entrance_criteria: []
exit_criteria: []
verification:
  tests: []
  evidence: []
tasks: []
risks: []
```

# Phase 01
""",
    )

    _write_change(
        temp_repo,
        "delta",
        "DE-010",
        plan_block=plan_block,
        phases={"phase-01.md": phase_body},
    )

    lines = _run(["--kind", "delta", "--plan"], root=temp_repo)
    assert lines == [
        "DE-010\tdelta\tdraft\tde-010\tIP-010 [IP-010.PHASE-01:Build MVP.]",
    ]
