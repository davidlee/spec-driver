---
id: ISSUE-007
name: CLI commands missing --json output support
created: '2025-11-02'
updated: '2025-11-02'
status: resolved
kind: issue
categories:
  - cli
  - consistency
severity: p2
impact: user
problem_refs:
  - Inconsistent CLI interface
  - Agent tooling integration blocked
related_requirements: []
affected_verifications: []
linked_deltas:
  - DE-006
---

# CLI commands missing --json output support

## Problem

Many CLI commands advertise `--json` output support in slash command documentation and agent guidance, but don't actually implement it. This creates:

1. **Broken agent workflows**: Agents expect `--json` based on documentation
2. **Inconsistent CLI**: Some commands support `--json`, others don't
3. **Integration friction**: External tooling can't reliably parse output

## Evidence

**Commands that fail with `--json`**:
- `spec-driver create issue <title> --json` → Error: No such option: --json
- `spec-driver list specs --json` → Error: No such option: --json

**Commands that work with `--json`**:
- `spec-driver create spec <name> --kind product --json` ✓

## Expected Behavior

All `create` and `list` commands should support `--json` output for:
- Machine-readable results (file paths, IDs, metadata)
- Agent integration and automation
- Consistent CLI interface patterns

## Suggested Fix

1. Audit all CLI commands in `supekku/cli/` for `--json` support
2. Add `--json` flag to commands missing it (create, list, show, etc.)
3. Standardize JSON output format across commands
4. Update help text and documentation to reflect actual support

## Impact

- **Severity**: P2 (blocks agent automation, creates confusion)
- **Users affected**: Agents, automation scripts, external tooling
- **Workaround**: Parse text output (brittle, error-prone)

## Related

- Slash command `/supekku.specify` assumes `--json` works for discovery
- PROD-001 and PROD-002 workflows depend on `--json` for metadata extraction

## Resolution

**Resolved by**: DE-006 (Standardize CLI JSON output support)

**Changes implemented**:
1. Added `--json` flag to all `create` subcommands (issue, problem, improvement, risk)
   - Returns JSON: `{"id": "...", "path": "...", "kind": "...", "status": "..."}`
   - Preserves existing text output as default

2. Added `--json` flag to `list specs` command as shorthand for `--format=json`
   - Note: `list` commands already supported `--format=json`, now also support `--json`

3. Comprehensive test coverage:
   - 3 new JSON output tests in `create_test.py`
   - All 69 CLI tests passing
   - Ruff and Pylint: 100% clean

**Verification**:
```bash
# Create commands with JSON output
uv run spec-driver create issue "Test" --json
uv run spec-driver create problem "Test" --json
uv run spec-driver create risk "Test" --json

# List commands with JSON output
uv run spec-driver list specs --json
```

**Status**: Resolved and verified ✅
