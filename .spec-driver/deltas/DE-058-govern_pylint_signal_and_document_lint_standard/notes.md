# Notes for DE-058

- 2026-03-07: Created STD-002 as a `default` standard to document lint
  prioritization and explicitly reject "pre-existing debt" as blanket
  justification for adding more warnings.
- 2026-03-07: Confirmed the installed `pylint-per-file-ignores` plugin uses
  recursive glob expansion. Existing `*_test.py` patterns only matched repo-root
  files, so nested test modules were never suppressed.
- 2026-03-07: Updated `pyproject.toml` per-file ignores to use
  `**/*_test.py` and `**/test_*.py` for
  `protected-access,missing-function-docstring`.
- 2026-03-07: Verification:
  - `just lint` passed.
  - `just pylint` exited 0.
  - `missing-function-docstring` dropped to 6 occurrences, all in non-test
    modules (`supekku/tui/app.py`, `supekku/tui/widgets/artifact_list.py`,
    `supekku/tui/widgets/type_selector.py`).
