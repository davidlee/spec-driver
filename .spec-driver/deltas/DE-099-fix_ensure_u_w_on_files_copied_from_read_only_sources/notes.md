# DE-099 Implementation Notes

## 2026-03-16 — implementation (retroactive delta)

Bug reported: `PermissionError: [Errno 13]` on `.claude/settings.json` after
install from Nix devshell. Root cause: `shutil.copy` preserves source `0444`
permissions from read-only package stores.

### Changes

1. **`file_ops.py`**: Added `_ensure_writable()` helper, `copy_with_write_permission()`,
   and `copytree_with_write_permission()`. The copy helper chmod's the dest
   _before_ copy (handles re-install over broken state) and _after_ copy
   (handles read-only source).

2. **`install.py`**: All 8 `shutil.copy` sites → `copy_with_write_permission`.
   Removed now-unused `shutil` import.

3. **`sync.py`**: `shutil.copytree` → `copytree_with_write_permission` for
   skill directory installs.

4. **Tests**: 4 new tests covering read-only source, read-only dest overwrite,
   read-only tree, and integration with Claude config install. 183 total pass.

### Verification

- `uv run pytest supekku/scripts/lib/file_ops_test.py supekku/scripts/lib/install_test.py supekku/scripts/lib/skills/sync_test.py` — 183 passed
- `uv run ruff check` — clean
- `uv run pylint` — 9.85/10, no new issues
