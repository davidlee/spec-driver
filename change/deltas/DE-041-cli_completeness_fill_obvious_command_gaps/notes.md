# Notes for DE-041

## Bug fix: _update_plan_overview_phases regex escape (2026-03-04)

`_update_plan_overview_phases` in `creation.py:592` passed the replacement string
directly to `re.sub`, which interprets backslash sequences (`\u`, `\n`, etc.).
Plan files with user-edited content (URLs, unicode) triggered `bad escape \u`.

**Fix**: `pattern.sub(lambda _: new_block, content, count=1)` — lambda avoids
regex interpretation of the replacement string.

**Test**: `test_create_phase_plan_with_backslash_sequences` in `creation_test.py`.
