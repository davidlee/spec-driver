"""VT-CC-027: skill-level validate-gate marker regression (DE-137 / DR-137 §5.5).

For each of the five skills that ship a `validate file` / `validate workspace`
gate (per DR-137 §5.5), assert that the source SKILL.md carries the
`<!-- validate-gate:<skill> begin --> ... <!-- validate-gate:<skill> end -->`
anchor pair (F-23) and that the bracketed body contains the expected
`spec-driver validate ...` command substring.
"""

from __future__ import annotations

import re

import pytest

from supekku.scripts.lib.core.paths import get_package_skills_dir

# (skill_id, expected substring inside the validate-gate block)
SKILL_GATES: list[tuple[str, str]] = [
  ("execute-phase", "spec-driver validate file"),
  ("close-change", "spec-driver validate workspace"),
  ("audit-change", "spec-driver validate file"),
  ("notes", "spec-driver validate file"),
  ("update-delta-docs", "spec-driver validate file"),
]


@pytest.mark.parametrize(("skill_id", "expected_substring"), SKILL_GATES)
def test_skill_validate_gate_present(skill_id: str, expected_substring: str) -> None:
  skill_path = get_package_skills_dir() / skill_id / "SKILL.md"
  assert skill_path.is_file(), f"missing source skill file: {skill_path}"

  text = skill_path.read_text(encoding="utf-8")
  pattern = (
    rf"<!--\s*validate-gate:{re.escape(skill_id)}\s+begin\s*-->"
    rf"(?P<body>.*?)"
    rf"<!--\s*validate-gate:{re.escape(skill_id)}\s+end\s*-->"
  )
  match = re.search(pattern, text, re.DOTALL)
  assert match is not None, (
    f"{skill_id}: missing validate-gate anchor pair in {skill_path}"
  )
  body = match.group("body")
  assert expected_substring in body, (
    f"{skill_id}: validate-gate block does not contain expected command "
    f"substring {expected_substring!r}. Block content: {body!r}"
  )
