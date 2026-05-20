# supekku.scripts.lib.skills.validate_gate_test

VT-CC-027: skill-level validate-gate marker regression (DE-137 / DR-137 §5.5).

For each of the five skills that ship a `validate file` / `validate workspace`
gate (per DR-137 §5.5), assert that the source SKILL.md carries the
`<!-- validate-gate:<skill> begin --> ... <!-- validate-gate:<skill> end -->`
anchor pair (F-23) and that the bracketed body contains the expected
`spec-driver validate ...` command substring.

## Functions

- @pytest.mark.parametrize(Tuple[skill_id, expected_substring], SKILL_GATES) `test_skill_validate_gate_present(skill_id, expected_substring) -> None`
