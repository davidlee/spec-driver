# Notes for DE-040

## Implementation (2026-03-04)

### Done (T1–T6)

- Moved `boot.md` → `supekku/templates/agents/boot.md`; updated `_render_boot_md` path to `"agents/boot.md"`
- Created `supekku/templates/hooks/` with empty `doctrine.md` and `README.md`
- Added `_install_hooks()` in `install.py` — create-if-missing semantics, never overwrites existing files
- Called from `initialize_workspace` after template copy; added `.spec-driver/hooks` to directory list
- Updated 4 skill sources (boot, doctrine, scope-delta, shape-revision) to reference `.spec-driver/hooks/doctrine.md`
- Moved project's `.spec-driver/doctrine.md` → `.spec-driver/hooks/doctrine.md` (content preserved)
- Ran `spec-driver install --yes` to sync skills to `.claude/skills/` and `.agents/skills/`
- 6 new tests: hooks install, create-if-missing, no-overwrite, dry-run, idempotency, boot template resolution

### Verification

- `just lint`: clean
- `just test`: 2292 passed, 3 skipped
- `pylint install.py`: 9.88/10 (no new issues)
- `pylint install_test.py`: pre-existing C0302/C0116 only, no regression from changes

### Surprises / Adaptations

- None. `Path.glob("*.md")` confirmed top-level only — O5 was already satisfied.

### Rough edges / Follow-up

- `install_test.py` exceeds pylint's 1000-line limit (C0302) — pre-existing; consider splitting if more tests added
- VH-1 (manual verification: `spec-driver install --yes` in clean dir) still outstanding for user

### Status

- Uncommitted work
