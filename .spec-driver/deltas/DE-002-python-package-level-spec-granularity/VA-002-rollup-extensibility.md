# VA-002: Rollup Mechanism Extensibility Design Review

**Verification Artifact**: VA-002
**Requirement**: PROD-005.NF-002 - Design Extensibility
**Phase**: IP-002.PHASE-01
**Date**: 2025-11-02
**Status**: Complete

## Purpose

Verify that the package-level spec pattern does not preclude future addition of an opt-in rollup mechanism (parent packages covering child packages) without breaking changes.

## Background

The default pattern (Phase 01-03) establishes **leaf-package granularity**: one spec per leaf package. However, future users may want a parent package to "roll up" multiple child packages into a single spec.

**Example**:
- Default: `supekku/scripts/lib/formatters/` (leaf package) → `SPEC-045`
- With rollup: `supekku/scripts/lib/` (parent) → `SPEC-050` covers all child packages under `lib/`

## Design Approach

### Option 1: Frontmatter-Based Rollup (Recommended)

Add optional frontmatter field to parent package specs:

```yaml
---
id: SPEC-050
slug: supekku-scripts-lib
name: supekku/scripts/lib Specification
kind: spec
status: draft
rollup:
  enabled: true
  children:
    - supekku/scripts/lib/formatters
    - supekku/scripts/lib/decisions
    - supekku/scripts/lib/specs
sources:
- language: python
  identifier: supekku/scripts/lib  # Parent package
  module: supekku.scripts.lib
  variants:
  - name: api
    path: contracts/api.md
  - name: implementation
    path: contracts/implementation.md
  - name: tests
    path: contracts/tests.md
---
```

**Contract generation logic**:
- If `rollup.enabled == true`, aggregate all files from listed child packages
- Use existing `sorted(path.rglob("*.py"))` across all children
- Deterministic ordering maintained

**Query resolution** (`--for-path`):
- Check if file's package is in any spec's `rollup.children` list
- Return parent spec if found, otherwise return leaf package spec
- Fall back to current behavior if no rollup configured

### Option 2: Configuration File

Alternative: External config file `specify/rollup-config.yaml`:

```yaml
rollups:
  - parent: supekku/scripts/lib
    spec_id: SPEC-050
    children:
      - supekku/scripts/lib/formatters
      - supekku/scripts/lib/decisions
```

**Pros**: Keeps spec frontmatter clean
**Cons**: Adds external configuration complexity

## Compatibility Analysis

### No Breaking Changes Required

1. **Registry (`SpecRegistry`)**:
   - Already has `find_by_package()` method
   - Can be enhanced to check `rollup.children` without breaking existing calls
   - Add `find_spec_for_file()` method that handles rollup logic

2. **Spec Model (`Spec`)**:
   - Already has `packages` property from frontmatter
   - `rollup` field would be optional, default absent
   - Existing specs without `rollup` work unchanged

3. **PythonAdapter**:
   - Currently discovers leaf packages
   - Can be enhanced to respect rollup configuration
   - If rollup present, skip child packages (already covered by parent)

4. **Contract Generation**:
   - Already handles directories via `rglob()`
   - Rollup just expands the set of files to aggregate
   - `sorted()` ordering works regardless of file count

### Migration Impact

**For existing specs** (post-Phase 02):
- No migration needed
- All specs remain valid (rollup is opt-in)
- Users can add rollup incrementally

**For future users**:
- Default behavior: leaf packages (no rollup)
- Opt-in: Add `rollup` frontmatter when needed
- Tool support: `spec-driver create spec --rollup` flag

## Implementation Sketch

### Phase 1: Registry Enhancement

```python
# supekku/scripts/lib/specs/registry.py

def find_spec_for_file(self, file_path: Path) -> Spec | None:
    """Find spec for a file, respecting rollup configuration."""
    # 1. Find file's package
    package = find_package_for_file(file_path)
    if not package:
        return None

    # 2. Check if any spec rolls up this package
    for spec in self._specs.values():
        rollup = spec.frontmatter.data.get('rollup', {})
        if rollup.get('enabled') and package in rollup.get('children', []):
            return spec  # Parent spec covers this package

    # 3. Fall back to leaf package spec
    return self.find_by_package(str(package))
```

### Phase 2: Sync Adapter Update

```python
# supekku/scripts/lib/sync/adapters/python.py

def discover_targets(self, repo_root, requested):
    # ... existing logic ...

    # Filter out packages that are rolled up
    rollup_children = self._get_rolled_up_packages()
    leaf_packages = [p for p in leaf_packages if p not in rollup_children]

    return leaf_packages
```

### Phase 3: Contract Generation

```python
# Contract generation for rollup specs
if spec.rollup.enabled:
    all_files = []
    for child_pkg in spec.rollup.children:
        all_files.extend(sorted(child_pkg.rglob("*.py")))
    # Process all_files for contract generation
```

## Validation

### Compatibility Checklist

- [x] Existing specs work without rollup field (optional field)
- [x] Registry can be enhanced without breaking `find_by_package()`
- [x] PythonAdapter can filter rolled-up packages without API changes
- [x] Contract generation already supports variable file counts
- [x] Deterministic ordering maintained with rollup
- [x] No migration needed for existing specs

### Design Quality

- [x] Opt-in (default behavior unchanged)
- [x] Configuration-driven (no code changes required to use rollup)
- [x] Backward compatible (existing specs don't break)
- [x] Forward compatible (can add features without breaking rollup)
- [x] Consistent with leaf-package pattern (just aggregates leaves)

## Conclusion

**Verdict**: ✅ **Rollup mechanism can be added without breaking changes**

The package-level pattern (Phase 01-03) establishes a solid foundation that naturally extends to rollup:

1. **Frontmatter-based rollup** is the recommended approach
2. **No breaking changes** required to existing specs or tooling
3. **Opt-in behavior** preserves default leaf-package granularity
4. **Implementation straightforward** (estimated 4-6 hours for full rollup support)

**Recommendation**: Defer rollup implementation until 2+ users request it. The design is validated and ready when needed.

---

**Signed off**: Claude (Agent)
**Date**: 2025-11-02
**PROD-005.NF-002**: ✓ Satisfied
