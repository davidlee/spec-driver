---
id: ISSUE-022
name: Add spec-driver doctor diagnostic command
created: '2025-11-08'
updated: '2025-11-08'
status: open
kind: issue
categories: [cli, diagnostics, tooling]
severity: p2
impact: user
---

# Add spec-driver doctor diagnostic command

## Problem Statement

Users may encounter issues with spec-driver due to missing dependencies, incorrect configuration, or environmental problems. Currently there's no easy way to diagnose these issues - users must manually check:

- Is `ts-doc-extract` installed (for TypeScript support)?
- Is Node.js available (for TypeScript support)?
- Are git/jujutsu available (for VCS operations)?
- Is workspace structure correct?
- Are registry files valid?
- Are templates installed?

A `doctor` command would provide automated diagnostics and actionable guidance.

## Proposed Solution

Add `spec-driver doctor` command that runs health checks and reports issues with suggestions for fixes.

### Command Signature

```bash
spec-driver doctor [OPTIONS]

Options:
  --json          Output results as JSON
  --fix           Attempt to fix issues automatically (interactive)
  --verbose, -v   Show detailed diagnostic information
  --check TYPE    Run specific check only (e.g., --check dependencies)
  --help          Show this message and exit
```

### Example Output

```bash
$ spec-driver doctor

spec-driver health check
========================

✓ Workspace structure valid
✓ Registry files valid
✓ Git repository detected
✓ Python environment OK

⚠ Optional dependencies:
  ☐ ts-doc-extract not found
    TypeScript/JavaScript sync will not work
    Install with: npm install -g ts-doc-extract

⚠ Templates not installed
  Some create commands may use fallback templates
  Install with: spec-driver install

ℹ Configuration:
  Workspace root: /home/user/project
  Registry version: 1.0
  Specs: 15 product, 42 tech
  Changes: 8 deltas, 3 revisions

Summary: 2 warnings, 0 errors

Exit code: 0
```

### Example with Errors

```bash
$ spec-driver doctor

spec-driver health check
========================

✗ Workspace not initialized
  Run: spec-driver install

✗ Not a git repository
  Initialize with: git init

Summary: 0 warnings, 2 errors

Exit code: 1
```

### JSON Output

```bash
$ spec-driver doctor --json
```

```json
{
  "summary": {
    "errors": 0,
    "warnings": 2,
    "info": 1
  },
  "checks": [
    {
      "category": "workspace",
      "name": "structure",
      "status": "ok",
      "message": "Workspace structure valid"
    },
    {
      "category": "dependencies",
      "name": "ts-doc-extract",
      "status": "warning",
      "message": "ts-doc-extract not found",
      "suggestion": "Install with: npm install -g ts-doc-extract",
      "optional": true
    },
    {
      "category": "vcs",
      "name": "git",
      "status": "ok",
      "message": "Git repository detected"
    }
  ],
  "environment": {
    "workspace_root": "/home/user/project",
    "registry_version": "1.0",
    "python_version": "3.11.5",
    "spec_driver_version": "0.1.0"
  }
}
```

## Diagnostic Checks

### Critical (Errors)

1. **Workspace Structure**
   - Check for `.spec-driver/` directory
   - Check for required directories (`specify/`, `change/`, `backlog/`)
   - Suggestion: Run `spec-driver install`

2. **Registry Files**
   - Check `.spec-driver/registry/*.yaml` files exist
   - Validate YAML syntax
   - Suggestion: Run `spec-driver sync` or recreate with `install`

### Important (Warnings)

3. **Optional Dependencies**
   - Check for `ts-doc-extract` (TypeScript support)
   - Check for Node.js runtime
   - Suggestion: Installation commands for each

4. **Templates**
   - Check if local templates installed in `.spec-driver/templates/`
   - Suggestion: Run `spec-driver install` to install templates

5. **VCS**
   - Check for git or jujutsu
   - Check if in a repository
   - Suggestion: Initialize repository

### Informational

6. **Configuration Summary**
   - Workspace root path
   - Count of specs, changes, backlog items
   - Registry version
   - Python/spec-driver versions

## Implementation Plan

### Phase 1: Core Diagnostics

1. Create `supekku/cli/doctor.py` command module
2. Implement check framework:
   ```python
   @dataclass
   class DiagnosticCheck:
       category: str
       name: str
       status: Literal["ok", "warning", "error"]
       message: str
       suggestion: str | None = None
       optional: bool = False
   ```

3. Implement critical checks (workspace, registry)
4. Implement CLI output formatting (colored, structured)

### Phase 2: Dependency Checks

1. Add `ts-doc-extract` availability check
2. Add Node.js runtime check
3. Add VCS detection (git/jj)
4. Add template installation check

### Phase 3: JSON Output & Fix Mode

1. Implement `--json` output format
2. Implement `--check TYPE` filtering
3. Implement `--fix` interactive mode (prompt to fix issues)
4. Add `--verbose` mode with detailed diagnostics

## Success Criteria

- [ ] `doctor` command runs all checks and reports status
- [ ] Errors exit with code 1, warnings exit with code 0
- [ ] JSON output mode works for automation
- [ ] Detects missing `ts-doc-extract` and shows install instructions
- [ ] Detects invalid workspace and suggests fixes
- [ ] `--fix` mode can install missing dependencies interactively
- [ ] Comprehensive test coverage

## Related Issues

- ISSUE-021: Fix ts-doc-extract dependency handling (this command will diagnose it)

## References

Similar commands for inspiration:
- `brew doctor`
- `flutter doctor`
- `cargo doctor`
- `npm doctor`

## Open Questions

1. Should `--fix` mode be auto-confirm or interactive by default?
2. Should we check for Python version compatibility?
3. Should we validate all YAML frontmatter in specs?
4. Should we check for common misconfigurations (e.g., broken symlinks)?
