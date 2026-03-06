---
id: ISSUE-037
name: Show commands not using emit_artifact have duplicated output dispatch
created: '2026-03-05'
updated: '2026-03-05'
status: open
kind: issue
categories: []
severity: p3
impact: user
---

# Show commands not using emit_artifact have duplicated output dispatch

## Summary

7 of 15 show commands bypass the shared `emit_artifact()` helper (`cli/common.py:517`)
and duplicate the `--json`/`--path`/`--raw` mutual-exclusivity check and output dispatch
inline. This means new output modes (like `--body-only` from DE-045) must be wired into
each command individually instead of being available via the shared path.

## Affected commands

Commands **not** using `emit_artifact` (roll their own dispatch):
- `show spec` (line 50)
- `show delta` (line 92)
- `show requirement` (line 158)
- `show adr` (line 209)
- `show policy` (line 252)
- `show standard` (line 295)
- `show card` (line 387)
- `show memory` (line 446) — **being migrated in DE-045**

Commands already using `emit_artifact`:
- `show revision`, `show plan`, `show audit`, `show issue`, `show problem`, `show improvement`, `show risk`

## Evidence

The mutual-exclusivity check `if sum([json_output, path_only, raw_output]) > 1` appears
8 times in `cli/show.py`. `emit_artifact` already handles this check internally.

## Impact

- New output modes require N individual command changes instead of 1 shared change
- Inconsistent error messages possible across commands
- Violates skinny CLI pattern (dispatch logic belongs in shared infrastructure)

## Proposed Fix

Migrate remaining 7 commands (after DE-045 migrates `show memory`) to use
`emit_artifact` with `resolve_artifact` + appropriate `format_fn`/`json_fn` callbacks.

## Related

- DE-045 (migrates `show memory` as part of phase 1)
- ISSUE-035 / ISSUE-036 (output mode consistency)
