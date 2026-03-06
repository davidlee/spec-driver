---
id: ISSUE-021
name: Fix ts-doc-extract dependency handling
created: '2025-11-08'
updated: '2025-11-08'
status: open
kind: issue
categories: [installation, dependencies, typescript]
severity: p1
impact: user
---

# Fix ts-doc-extract dependency handling

## Problem Statement

spec-driver has a runtime dependency on the npm package [`ts-doc-extract`](https://www.npmjs.com/package/ts-doc-extract) for TypeScript/JavaScript contract generation, but:

1. **Silent Failure**: The `sync` command silently hangs if `ts-doc-extract` is not installed (bad UX)
2. **No Installation Support**: The installer doesn't check for or attempt to install the dependency
3. **Undocumented**: README/installation instructions don't mention this requirement
4. **No Runtime Validation**: Sync command doesn't check for the dependency before attempting to use it

This creates a poor user experience where TypeScript sync appears broken with no actionable error message.

## Current Behavior

**When `ts-doc-extract` is missing:**

```bash
$ spec-driver sync
# Hangs indefinitely with no output when processing TypeScript files
# User must Ctrl+C to exit
# No error message, no guidance
```

**Code location:** `supekku/scripts/lib/sync/adapters/typescript.py:353-416`

The `_extract_ast()` method calls `subprocess.run()` with a 30s timeout but:
- If `ts-doc-extract` is not installed, `npx`/`pnpm dlx`/`bunx` may hang waiting for install confirmation
- Or fail silently without helpful output
- Exception handling doesn't distinguish "command not found" from other errors

## Expected Behavior

### 1. Installer Attempts Installation

```bash
$ spec-driver install

Workspace initialized in /path/to/project

Optional dependencies:
  ☐ ts-doc-extract (TypeScript/JavaScript contract generation)
    Install with: npm install -g ts-doc-extract

Install ts-doc-extract now? [Y/n] y
Installing ts-doc-extract...
✓ ts-doc-extract installed successfully

# Or if user declines:
Install ts-doc-extract now? [Y/n] n
⚠ Skipped. TypeScript sync will not work until installed.
  Install later with: npm install -g ts-doc-extract
```

### 2. README Documents Dependency

```markdown
## Installation

### Optional Dependencies

**TypeScript/JavaScript Support:**

For TypeScript/JavaScript contract generation, install `ts-doc-extract`:

```bash
npm install -g ts-doc-extract
# Or
pnpm add -g ts-doc-extract
# Or
bun add -g ts-doc-extract
```

Without this, `spec-driver sync` will skip TypeScript files.
```

### 3. Sync Command Validates Dependency

```bash
$ spec-driver sync

Error: ts-doc-extract not found

TypeScript/JavaScript contract generation requires ts-doc-extract.

Install it with one of:
  npm install -g ts-doc-extract
  pnpm add -g ts-doc-extract
  bun add -g ts-doc-extract

Then run: spec-driver sync

Exit code: 1
```

**Implementation:** Check in `TypeScriptAdapter.generate()` before calling `_extract_ast()`

```python
def generate(self, unit: SourceUnit, *, spec_dir: Path, check: bool = False):
    # Check ts-doc-extract availability
    if not self._is_ts_doc_extract_available():
        raise TsDocExtractNotFoundError(
            "ts-doc-extract not found. Install with: npm install -g ts-doc-extract"
        )
    # ... rest of implementation
```

### 4. Exit with Non-Zero Status

All error paths must `sys.exit(1)` or raise exceptions that propagate to CLI exit handlers.

## Implementation Plan

### Phase 1: Runtime Validation (Critical)

1. Add `_is_ts_doc_extract_available()` method to `TypeScriptAdapter`
   - Try running `npx ts-doc-extract --version` (or equivalent for pnpm/bun)
   - Return True if succeeds, False otherwise
   - Cache result to avoid repeated checks

2. Update `generate()` to check before processing:
   ```python
   if not self._is_ts_doc_extract_available():
       raise TsDocExtractNotFoundError(
           "ts-doc-extract not found.\n\n"
           "Install with one of:\n"
           "  npm install -g ts-doc-extract\n"
           "  pnpm add -g ts-doc-extract\n"
           "  bun add -g ts-doc-extract"
       )
   ```

3. Handle exception in sync command CLI to exit with code 1

### Phase 2: Installer Support

1. Add npm package detection/installation to `supekku/scripts/install.py`
2. Prompt user to install `ts-doc-extract` during workspace setup
3. Detect package manager (npm/pnpm/bun) and use appropriate install command
4. Warn if declined, show install instructions

### Phase 3: Documentation

1. Update README.md with TypeScript dependency section
2. Add installation instructions for all supported package managers
3. Document fallback behavior (TypeScript files skipped if not installed)

### Phase 4: doctor Command (Separate Issue)

See ISSUE-022 for `spec-driver doctor` diagnostic command.

## Success Criteria

- [ ] `sync` command exits immediately with error message if `ts-doc-extract` missing
- [ ] Error message shows installation instructions for npm/pnpm/bun
- [ ] Exit code is non-zero (1) on ts-doc-extract missing
- [ ] `install` command prompts to install `ts-doc-extract`
- [ ] README documents TypeScript dependency
- [ ] No silent hangs or timeouts

## Related Issues

- ISSUE-022: `spec-driver doctor` command for dependency diagnostics

## Technical Notes

**Current subprocess call:** `supekku/scripts/lib/sync/adapters/typescript.py:396-404`

```python
result = subprocess.run(
    cmd,
    cwd=package_root,
    capture_output=True,
    text=True,
    timeout=30,  # This may not catch install prompts
    check=True,
)
```

**Problem:** If `ts-doc-extract` isn't installed:
- `npx` may prompt "Need to install the following packages: ts-doc-extract"
- This hangs waiting for stdin input that never comes
- Timeout eventually fires but produces confusing error

**Solution:** Check for command availability before subprocess call.
