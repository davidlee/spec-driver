# Notes for DE-042

## Phase 1 — Fix gomarkdoc invocation (surgical fix)

### Diagnosis

Discovered while testing against `../test-driver` (Go project with nix-direnv).

Three bugs in `GoAdapter._generate_variant()`:

1. **Wrong path format**: `generate()` constructed `f"{module}/{unit.identifier}"` (e.g. `im/cmd/im`) — gomarkdoc rejects fully-qualified import paths and expects `./`-prefixed relative paths (`./cmd/im`)
2. **Missing `cwd`**: `subprocess.run()` calls omitted `cwd=repo_root`, so gomarkdoc couldn't resolve packages even with correct paths
3. **Silent error swallowing**: Outer `except CalledProcessError` at line 319 caught failures and returned `status="unchanged"` — directories were created but no files written, with no visible error

### Fix

- `generate()`: use `f"./{unit.identifier}"` directly (identifier is already module-relative)
- `_generate_variant()`: add `cwd=self.repo_root` to both subprocess calls
- Remove outer `except CalledProcessError` — let errors propagate to engine

### Tests

- Updated `test_generate_creates_variants` and `test_generate_check_mode` to assert `./` prefix and `cwd=repo_root`
- Added `test_generate_propagates_gomarkdoc_error` to verify errors are no longer swallowed
- Removed stale `get_go_module_name` mock from generate tests (no longer called in `generate()`)

### Verified

- 118/118 sync tests pass
- Manual: `spec-driver sync --contracts` in `../test-driver` produces Go contract files

## Phase 2 — PATH/env forwarding

Not yet started. Separate concern — adapters should support optional `env` passthrough for cases where spec-driver is invoked from outside the target project's direnv shell.
