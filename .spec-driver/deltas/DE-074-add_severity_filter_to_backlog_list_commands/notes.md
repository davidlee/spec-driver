# Notes for DE-074

## Phase 1 — Add --severity filter (in progress, uncommitted)

### Done

- `--severity` param added to `list_backlog()` with filter logic (case-insensitive match)
- `--severity` param + passthrough added to `list_issues` wrapper
- Delta scoped, phase sheet created, DE status set to in-progress

### Remaining

- Add `--severity` param + passthrough to 3 remaining wrappers:
  `list_problems`, `list_improvements`, `list_risks`
- Write tests
- Lint, test, commit

### Design note

- The 4 kind-specific wrappers (`list_issues`, `list_problems`, etc.) duplicate
  ~70 lines of identical parameter declarations each. Adding `--severity` makes
  this worse. A future refactor could extract shared params into an Annotated
  type or decorator, but that's out of scope here.
- Registry already has `filter(severity=...)` but we filter in the CLI layer
  instead (consistent with how status/substring filtering works — the CLI
  iterates `registry.iter()` and applies filters inline).

### Verification

- Not yet run since code was last modified
