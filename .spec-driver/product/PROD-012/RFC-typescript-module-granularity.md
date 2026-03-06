# RFC: TypeScript Module Granularity for Contract Generation

**Status**: Draft
**Created**: 2025-11-11
**Related**: PROD-012 (Code Contract Documentation), FR-015 (1:1 code-to-spec mapping)

## Executive Summary

TypeScript contract generation currently produces excessive granularity (100+ specs for medium projects) because it lacks the natural package boundaries that Python (`__init__.py`) and Go (`go.mod`) provide. This RFC proposes using `package.json` as the primary boundary with optional manual refinement via a `split` command, ensuring exhaustive and exclusive file coverage while allowing incremental granularity improvements.

## Problem Statement

### Current Behavior

TypeScript adapter (`typescript.py:221-252`) treats every "significant" standalone file as a module:

```python
for file in src_dir.glob("**/*.ts"):
  is_significant = (
    depth <= 1 or
    any(part in important_dirs for part in rel_path.parts)
  )
  if is_significant:
    modules.append(file)  # One spec per file
```

**Result**: Medium NextJS project (~1134 files) → **119 specs**
- Most contracts <100 lines (only ~3 have >100 lines)
- Navigation difficult: deep symlink trees mirroring individual files
- Violates FR-015: specs not cohesive or right-sized

### Why Python/Go Don't Have This Problem

**Python:**
```
supekku/
  scripts/
    lib/
      formatters/
        __init__.py          ← Package marker
        change_formatters.py
        spec_formatters.py
```
- `__init__.py` defines package boundaries (language requirement)
- Leaf package detection: packages with no child packages
- Natural, deterministic, hierarchical structure

**Go:**
```
pkg/
  registry/
    go.mod               ← Module marker
    registry.go
    types.go
```
- `go.mod` defines module boundaries (language requirement)
- One module per directory (implicit from language design)
- Clear architectural boundaries

**TypeScript:**
```
src/
  services/
    authService.ts       ← No package marker
    cartService.ts       ← No package marker
    userService.ts       ← No package marker
```
- **No language-level package system**
- `index.ts` is convention, not requirement
- Arbitrary filesystem organization

## Design Criteria

Any solution must satisfy:

1. **Deterministic**: Same inputs → same outputs
2. **Stable**: Small code changes don't cause massive spec reorganization
3. **Exhaustive**: Every file covered by exactly one spec
4. **Exclusive**: No file in multiple specs
5. **Cohesive**: Specs have right-sized, logical scope

## Evaluated Strategies

### Strategy 1: Leaf Module Detection (index.ts)

**Rule**: Find directories with `index.ts` that have no child directories with `index.ts`

```python
def is_leaf_module(path: Path) -> bool:
  has_index = any((path / f"index.{ext}").exists()
                  for ext in ["ts", "tsx", "js", "jsx"])
  if not has_index:
    return False

  for child in path.iterdir():
    if child.is_dir() and has_child_index(child):
      return False  # Not a leaf

  return True
```

**Evaluation**:
- ✅ Deterministic: Based on filesystem
- ✅ Stable: Only changes when index files added/removed
- ✅ Respects developer intent where used
- ❌ **Not universal**: Many codebases don't use `index.ts`
- ❌ **Breaks exhaustive**: What about `src/services/` with no index?
- ❌ **Only works for libraries**: Doesn't work for apps, services, models

**Test case**: NextJS project with 1134 files → **6 specs** (only components have index files)
- `src/services/` (12 files): No spec ❌
- `src/models/` (20 files): No spec ❌
- `src/app/` (50+ routes): No spec ❌

**Verdict**: Fails exhaustive criterion. Only viable for codebases that universally use `index.ts` (uncommon).

---

### Strategy 2: Top-Level src/ Subdirectories

**Rule**: One spec per top-level subdirectory under `src/`

```python
def find_modules(package_root: Path) -> list[Path]:
  src_dir = package_root / "src"
  return [d for d in src_dir.iterdir() if d.is_dir()]
```

**Result**:
- `src/services/` → 1 spec
- `src/models/` → 1 spec
- `src/app/` → 1 spec
- `src/components/` → 1 spec

**Evaluation**:
- ✅ Deterministic: Based on filesystem
- ✅ Stable: Only changes with architectural refactoring
- ✅ Exhaustive: Everything under src/ covered
- ✅ Exclusive: Each file in exactly one top-level dir
- ⚠️ Cohesive: Assumes reasonable src/ organization
- ❌ **Doesn't scale**: Large projects have 100+ files per top-level dir
- ❌ **Breaks on monorepos**: Ignores package boundaries entirely

**Monorepo example**:
```
packages/
  ui-library/src/components/  (100+ files) → 1 spec ❌
  api-client/src/endpoints/   (200+ files) → 1 spec ❌
  admin-app/src/features/     (300+ files) → 1 spec ❌
```

**Verdict**: Too coarse for large projects. Violates scaling requirement.

---

### Strategy 3: package.json Boundaries

**Rule**: One spec per `package.json` file

```python
def find_modules(repo_root: Path) -> list[Path]:
  modules = []
  for package_json in repo_root.rglob("package.json"):
    if "node_modules" not in package_json.parts:
      modules.append(package_json.parent)
  return modules
```

**Monorepo result**:
- `packages/ui-library/` → 1 spec (100+ files)
- `packages/api-client/` → 1 spec (200+ files)
- `packages/admin-app/` → 1 spec (300+ files)

**Single-package result**:
- `/` → 1 spec (entire project, 1000+ files)

**Evaluation**:
- ✅ Deterministic: Based on package.json presence
- ✅ Stable: Package structure rarely changes
- ✅ Exhaustive: All files within package covered
- ✅ Exclusive: package.json boundaries don't overlap
- ✅ Works for monorepos (pnpm workspaces, etc.)
- ❌ **Too coarse for large single-package projects**
- ❌ **No refinement path** without breaking exhaustive/exclusive

**Verdict**: Right level for monorepos, too coarse for large single-package projects. Needs refinement mechanism.

---

### Strategy 4: Explicit Scope Metadata

**Rule**: Specs declare scope via glob patterns in frontmatter

```yaml
# SPEC-042.md
sources:
  - language: typescript
    scope:
      - src/services/auth/**/*.ts
      - src/services/session/**/*.ts
```

**Evaluation**:
- ✅ Deterministic: Explicit is deterministic
- ✅ Flexible: Can represent any grouping
- ✅ Stable: Metadata changes are deliberate
- ❌ **Breaks exhaustive**: No automatic gap detection
- ❌ **Breaks exclusive**: Overlapping globs require validation
- ❌ **No obvious initial state**: How to bootstrap?
- ❌ **Encourages bad patterns**: Arbitrary cross-cutting scopes

**Problems**:

1. **Completeness**: How to ensure all files covered?
   - Enumerate all TS files
   - Check against all spec scopes
   - Report gaps
   - Then what? Auto-create catch-all? User creates manually?

2. **Exclusivity**: How to prevent overlaps?
   - Build file sets for each spec at validation time
   - Check for intersections
   - Error on conflict
   - Ongoing maintenance burden

3. **Bootstrap**: What's the initial state?
   - Can't auto-create stubs (violates exhaustive)
   - Require manual spec creation upfront (poor UX)

**Verdict**: Trades automatic boundary detection for two worse problems (ensuring partition validity). Not viable without tooling.

---

## Proposed Solution: package.json + Manual Split

### Design

**Primary boundary**: `package.json` files
**Refinement**: Optional `split` command maintains partition validity

#### Initial State

```bash
spec-driver sync --stub
```

Creates one spec per `package.json`:
- Monorepo: One spec per workspace package
- Single-package: One spec for entire project

#### Metadata Format

```yaml
# SPEC-042.md
sources:
  - language: typescript
    package: packages/api-client  # Required: which package.json
    subtree: src/services         # Optional: subdirectory within package
```

**Rules**:
- `subtree` must be a directory path, not a glob (deterministic)
- Within a package, all subtrees must be non-overlapping (exclusive)
- Within a package, union of subtrees must cover all files (exhaustive)
- If no `subtree`, spec covers entire package (default)

#### Split Command

```bash
# User sees SPEC-042 is too large (entire api-client package)
spec-driver split SPEC-042 src/services/auth --id SPEC-043

# Or auto-assign ID
spec-driver split SPEC-042 src/services/auth
```

**Behavior**:
1. Create SPEC-043 with:
   ```yaml
   sources:
     - language: typescript
       package: packages/api-client
       subtree: src/services/auth
   ```

2. Update SPEC-042 to exclude that subtree:
   ```yaml
   sources:
     - language: typescript
       package: packages/api-client
       subtree: .  # Implicitly excludes src/services/auth
   ```

3. Move contracts from SPEC-042 to SPEC-043
4. Update symlink trees

**Validation** (on sync/validate):
- Within each package, verify subtrees are:
  - Non-overlapping (exclusive)
  - Complete (exhaustive)
- Error if gaps or overlaps detected

### Benefits

1. **Exhaustive/exclusive by construction**: Tooling enforces partition validity
2. **Deterministic initial state**: package.json boundaries are clear
3. **Stable**: Manual splits are deliberate architectural decisions
4. **Scales to monorepos**: Respects workspace structure
5. **Safe refinement path**: Split command maintains invariants
6. **No arbitrary conventions**: No `.pkg` files, no magic depth numbers

### Limitations

1. **Initial granularity coarse**: Single-package projects start with one spec
   - **Mitigation**: Users expected to split immediately for large projects
   - **Alternative**: Could auto-split at depth-1 under src/ if >N files

2. **Manual work required**: Users must explicitly split large specs
   - **Mitigation**: This is intentional - forces deliberate boundaries
   - **Tooling**: Could suggest splits based on size heuristics

3. **Subtree paths must exist**: Can't split nonexistent paths
   - **Mitigation**: Validation error guides users to correct paths

## Alternative Considered: .pkg Convention

**Idea**: Allow `.pkg` marker files to define additional package boundaries

```
src/
  services/
    auth/
      .pkg          ← Treat as package boundary
      authService.ts
```

**Rejected because**:
- Pollutes codebase with spec-driver-specific files
- Instability: Moving `.pkg` files moves code between specs
- Not better than subtree metadata (same information, worse location)

## Open Questions

### Q1: Auto-split heuristics for initial sync?

**Question**: Should `sync --stub` auto-split large packages?

**Options**:
1. **No auto-split**: Always one spec per package.json
   - Pro: Simple, predictable
   - Con: Poor initial UX for large single-package projects

2. **Auto-split by src/ top-level**: If package >N files, split by src/ subdirectories
   - Pro: Better initial granularity
   - Con: Adds complexity, arbitrary threshold

3. **Prompt user**: Ask if they want to split when creating large stub
   - Pro: User control
   - Con: Breaks non-interactive use (CI)

**Recommendation**: Start with option 1 (no auto-split), add option 2 if user feedback demands it.

### Q2: How to handle spec deletion after merge?

**Scenario**: User splits SPEC-042 into SPEC-042 + SPEC-043, later decides to merge back.

**Options**:
1. **Manual**: User deletes SPEC-043, removes subtree from SPEC-042 metadata
   - Pro: Explicit control
   - Con: Contracts orphaned, symlinks broken

2. **Merge command**: `spec-driver merge SPEC-043 --into SPEC-042`
   - Pro: Maintains partition validity
   - Con: More tooling to build

**Recommendation**: Option 1 initially, add merge command if needed.

### Q3: Subtree format - path or glob?

**Question**: Should subtree be `src/services/auth` (path) or `src/services/auth/**/*.ts` (glob)?

**Trade-offs**:
- **Path**: Simple, deterministic, easier to validate
- **Glob**: Flexible, can express complex scopes, harder to validate

**Recommendation**: Path only (no globs). Simplicity > flexibility for maintaining invariants.

### Q4: Nested subtrees?

**Question**: Can SPEC-043 have `subtree: src/services/auth/oauth`?

**Valid**:
- SPEC-042: `subtree: src/services`
- SPEC-043: `subtree: src/services/auth` (nested under SPEC-042's scope)

**Options**:
1. **Allow**: Subtrees can nest
   - Pro: Maximum flexibility
   - Con: Complex validation (tree structure)

2. **Forbid**: All subtrees must be at same level
   - Pro: Simpler validation (flat partition)
   - Con: Can't incrementally refine

**Recommendation**: Allow nesting. Validation is tree traversal (manageable). Users need incremental refinement.

### Q5: Migration path for existing 119-spec repositories?

**Question**: How to migrate repositories with existing fine-grained specs?

**Options**:
1. **Manual migration**: Users delete stubs, re-run sync --stub, split as needed
2. **Consolidation tool**: `spec-driver consolidate` merges related specs
3. **Leave as-is**: Don't force migration

**Recommendation**: Option 3 (leave as-is) + document migration path. Breaking changes require user opt-in.

## Implementation Plan

### Phase 1: package.json Boundary Detection (Immediate)

**Scope**: Replace current per-file detection with package.json boundaries

**Changes**:
- `typescript.py`: Replace `_find_logical_modules()` to find package.json files
- Update spec frontmatter to include `package` field
- Generate one spec per package.json
- Update tests

**Result**: Reduces 119 specs → ~1-10 specs (depending on monorepo structure)

### Phase 2: Subtree Metadata (Near-term)

**Scope**: Add support for subtree refinement in spec metadata

**Changes**:
- Add `subtree` field to spec frontmatter schema
- Update contract generation to respect subtree scope
- Add validation: check exhaustive + exclusive within package
- Update sync to respect existing subtrees

**Result**: Enables manual splitting without tooling

### Phase 3: Split Command (Future)

**Scope**: Add `spec-driver split` command for safe spec division

**Changes**:
- New CLI command: `spec-driver split SPEC-ID SUBTREE --id NEW-ID`
- Validation: ensure subtree exists, doesn't overlap
- Update both specs' metadata
- Move contracts and update symlinks
- Tests for split operation

**Result**: User-friendly refinement workflow

### Phase 4: Merge Command (Optional)

**Scope**: Add `spec-driver merge` for consolidation

**Changes**:
- New CLI command: `spec-driver merge SPEC-SRC --into SPEC-DEST`
- Validation: ensure both specs in same package
- Merge contracts
- Delete source spec
- Update symlinks

**Result**: Complete lifecycle management

## Success Criteria

### Quantitative

- Medium project (1000 files): 5-30 specs (not 100+)
- Each spec contract >50 lines average (meaningful content)
- Sync performance: <10s for 1000-file project
- Zero coverage gaps (all files in exactly one spec)

### Qualitative

- Symlink navigation intuitive (follows package structure)
- Split workflow feels natural (minimal friction)
- Validation errors clear and actionable
- Works for monorepos and single-package projects

## References

- PROD-012: Code Contract Documentation
- PROD-012.FR-015: Clean 1:1 code-to-spec mapping
- DR-019 Section 11: Future Work on Module Granularity
- `supekku/scripts/lib/specs/package_utils.py`: Python leaf package detection
- `supekku/scripts/lib/sync/adapters/typescript.py`: Current implementation

## Decision Log

**2025-11-11**: RFC created, no decisions yet. Awaiting feedback.
