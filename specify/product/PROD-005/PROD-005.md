---
id: PROD-005
slug: python-package-level-specs
name: Python Package-Level Specs
created: '2025-11-02'
updated: '2025-11-02'
status: draft
kind: prod
aliases: []
relations:
  - type: extends
    target: PROD-001
    nature: Applies spec creation workflow pattern to Python package-level granularity
guiding_principles:
  - Follow proven Go package-level pattern from vice
  - Deterministic ordering for stable git diffs
  - Zero maintenance burden for auto-generated contracts
  - Leaf-package default with future opt-in rollup
assumptions:
  - Python packages use __init__.py to define package boundaries
  - Users prefer predictable automation over subjective cohesion decisions
  - Contract generation already handles deterministic file ordering (sorted())
  - Migration is one-time manual cleanup (no tooling needed)
---

# PROD-005 – Python Package-Level Specs

```yaml supekku:spec.relationships@v1
schema: supekku.spec.relationships
version: 1
spec: PROD-005
requirements:
  primary:
    - PROD-005.FR-001
    - PROD-005.FR-002
    - PROD-005.FR-003
    - PROD-005.FR-004
    - PROD-005.NF-001
    - PROD-005.NF-002
  collaborators: []
interactions:
  - with: PROD-001
    nature: Extends spec creation workflow to support Python package-level granularity
```

```yaml supekku:spec.capabilities@v1
schema: supekku.spec.capabilities
version: 1
spec: PROD-005
capabilities:
  - id: predictable-spec-mapping
    name: Predictable Spec Mapping
    responsibilities:
      - Establish clear 1:1 mapping between Python packages and tech specs
      - Ensure deterministic file ordering within package specs
      - Maintain stable git diffs for contract generation
    requirements:
      - PROD-005.FR-001
      - PROD-005.FR-002
      - PROD-005.NF-001
    summary: >-
      Provides predictable, automatable mapping from Python package structure
      to tech specs, following the proven Go pattern from vice. Each leaf package
      (directory with __init__.py) maps to exactly one tech spec, with deterministic
      file ordering ensuring stable contract generation and meaningful git diffs.
    success_criteria:
      - Package → spec mapping is unambiguous and discoverable
      - Contract generation produces identical output for same package state
      - Developers can locate relevant spec without guesswork
  - id: workflow-integration
    name: Workflow Integration
    responsibilities:
      - Support package-level specs in sync operations
      - Enable relationship discovery at package granularity
      - Maintain registry integrity with package-level entities
    requirements:
      - PROD-005.FR-003
      - PROD-005.FR-004
    summary: >-
      Integrates package-level spec granularity into existing spec-driver
      workflows (sync, validation, relationship tracking). Ensures tooling
      recognizes and correctly handles Python packages as the fundamental
      unit for tech specs rather than individual files.
    success_criteria:
      - sync operations correctly index package-level specs
      - --for-path queries resolve to package specs
      - Relationship tracking works at package granularity
  - id: future-extensibility
    name: Future Extensibility
    responsibilities:
      - Design supports future opt-in rollup mechanism
      - Avoid precluding JS/TS evaluation later
      - Maintain compatibility with Go pattern
    requirements:
      - PROD-005.NF-002
    summary: >-
      Establishes Python package-level pattern in a way that doesn't preclude
      future enhancements (rollup mechanism, JS/TS evaluation) while maintaining
      consistency with the proven Go approach in vice.
    success_criteria:
      - Design accommodates future rollup without breaking changes
      - Pattern remains consistent across languages where applicable
      - No technical debt introduced by premature optimization
```

```yaml supekku:verification.coverage@v1
schema: supekku.verification.coverage
version: 1
subject: PROD-005
entries:
  - artefact: VT-001
    kind: VT
    requirement: PROD-005.FR-001
    status: planned
    notes: Verify leaf package identification from Python directory structure
  - artefact: VT-002
    kind: VT
    requirement: PROD-005.FR-002
    status: planned
    notes: Test deterministic file ordering within packages across platforms
  - artefact: VT-003
    kind: VT
    requirement: PROD-005.FR-003
    status: planned
    notes: Validate sync operation handles package-level specs correctly
  - artefact: VT-004
    kind: VT
    requirement: PROD-005.FR-004
    status: planned
    notes: Test --for-path resolution to package specs
  - artefact: VA-001
    kind: VA
    requirement: PROD-005.NF-001
    status: planned
    notes: Analyze git diff stability across contract regeneration cycles
  - artefact: VA-002
    kind: VA
    requirement: PROD-005.NF-002
    status: planned
    notes: Review design for rollup mechanism compatibility
```

## 1. Intent & Summary

- **Problem / Purpose**: File-level tech spec granularity (101 specs for ~108 Python files) creates unsustainable maintenance burden and cognitive fragmentation. Developers working on features spanning multiple files must navigate dozens of file-level specs, and refactoring code incurs spec update tax. The current approach prioritizes automated mapping over practical developer value and doesn't align with how engineers think about code organization.

- **Value Signals**: Package-level granularity reduces from 101 placeholder specs to ~25-30 meaningful specs, improving:
  - **Discoverability**: Find relevant spec without navigating file maze
  - **Cohesion**: Complete design for logically related functionality in one place
  - **Refactoring resilience**: Internal package changes don't break spec links
  - **Maintenance sustainability**: Spec count matches architectural components, not file count
  - **Alignment with thought process**: Engineers reason about packages/modules, not files

- **Guiding Principles**:
  - **Follow proven patterns**: Apply Go package-level approach from vice
  - **Deterministic by default**: Sorted file lists ensure stable git diffs
  - **Automate ruthlessly**: Contract generation handles all file rollup mechanics
  - **Defer complexity**: No rollup mechanism until 2-3 real user requests demonstrate need
  - **Language-appropriate**: Python leaf packages, JS/TS evaluated separately later
  - **Zero migration burden**: Manual cleanup acceptable for single-user project

- **Assumptions**:
  - Python packages defined by `__init__.py` presence (standard convention)
  - Leaf packages are the natural granularity (no parent/child rollup needed initially)
  - Existing `sorted()` in contract generation provides deterministic ordering
  - User (solo developer) comfortable with manual one-time migration
  - Future users will request rollup mechanism if they need non-leaf granularity

- **Change History**:
  - 2025-11-02: Initial spec establishing Python package-level granularity pattern

## 2. Stakeholders & Journeys

### Personas / Actors

1. **Solo Developer (Current User)**
   - **Context**: Maintaining spec-driver, extracted from vice (Go project with proven package-level specs)
   - **Goals**: Sustainable spec maintenance, clear architectural documentation
   - **Pains**: 101 file-level placeholder specs provide noise not signal; file-level coupling resists refactoring
   - **Expectations**: Apply Go pattern to Python; manual migration acceptable

2. **Future spec-driver Adopter**
   - **Context**: Considering spec-driver for their Python project
   - **Goals**: Understand how many specs they'll need; align specs with their mental model
   - **Pains**: Concerned about spec maintenance burden at scale
   - **Expectations**: Predictable mapping (package → spec); tooling handles mechanics

3. **Multi-Language Team**
   - **Context**: Using spec-driver across Go, Python, and potentially JS/TS codebases
   - **Goals**: Consistent patterns across languages where possible
   - **Pains**: Inconsistent granularity makes cross-language work confusing
   - **Expectations**: Python follows Go pattern; JS/TS evaluated independently

### Primary Journeys / Flows

**Journey 1: Developer Creates Package-Level Spec**

Given a developer implements new Python package `supekku/scripts/lib/export/`
1. Developer runs `spec-driver create spec "Export Module" --kind tech`
2. Tooling detects this is Python code (language conventions)
3. Spec generated references package path: `supekku/scripts/lib/export/`
4. Contracts auto-generated with deterministic file ordering (all `.py` files in package sorted alphabetically)
5. Developer fills spec with package-level design (what export module does, not file-by-file details)

Then spec represents cohesive package functionality
And contract lists all symbols from all files in predictable order

**Journey 2: Developer Queries Spec for File**

Given developer working on `supekku/scripts/lib/formatters/change_formatters.py`
1. Developer runs `spec-driver list specs --for-path supekku/scripts/lib/formatters/change_formatters.py`
2. Tooling resolves file to package `supekku/scripts/lib/formatters/`
3. Returns package-level spec: `SPEC-045: Output Formatters`
4. Developer reads spec to understand formatter architecture and patterns

Then developer finds relevant design doc in one query
And spec describes complete formatter package, not isolated file

**Journey 3: Developer Refactors Within Package**

Given developer splits `formatters/decision_formatters.py` into `formatters/decision/base.py` and `formatters/decision/table.py`
1. Code refactoring creates new subpackage structure
2. Developer runs `spec-driver sync`
3. Tooling updates contracts (new files added to sorted list)
4. Spec content unchanged (package-level design remains valid)
5. Git diff shows only contract additions (new files), not spec rewrites

Then refactoring has zero spec maintenance cost
And design documentation remains accurate

### Edge Cases & Non-goals

**Edge Cases**:
- **Deep nesting**: Packages like `supekku/scripts/lib/core/frontmatter_metadata/` → treat as leaf package initially
- **Single-file packages**: Package with one `.py` file still gets package-level spec (consistency over optimization)
- **Test-only packages**: Packages containing only `*_test.py` files still generate spec (documents test infrastructure)

**Non-goals**:
- **Parent/child rollup mechanism**: Deferred until 2+ real users request it
- **File-level specs**: Explicitly rejected; contracts provide file-level detail
- **Migration tooling**: One-time manual cleanup sufficient for current user
- **JS/TS granularity decision**: Separate evaluation needed for those ecosystems
- **Automatic granularity detection**: Deterministic leaf-package rule, no heuristics

## 3. Responsibilities & Requirements

### Capability Overview

**Predictable Spec Mapping** ensures every Python leaf package maps to exactly one tech spec with deterministic file ordering. This eliminates ambiguity ("which spec covers this code?") and provides stable contract generation for meaningful git diffs. Following the proven Go pattern from vice, developers get predictable automation without subjective cohesion decisions.

**Workflow Integration** ensures existing spec-driver tooling (sync, validation, relationship tracking) correctly handles package-level granularity. Queries like `--for-path` resolve files to their containing package's spec, and the registry indexes packages as the fundamental unit for tech specs.

**Future Extensibility** preserves design space for future enhancements (opt-in rollup, JS/TS patterns) without requiring breaking changes. The pattern remains consistent with Go while acknowledging Python and JS/TS may have language-specific needs.

### Functional Requirements

- **FR-001**: Leaf Python Package Identification
  Python tech specs MUST map to leaf packages (directories containing `__init__.py` with no child packages containing `__init__.py`), establishing one spec per leaf package as the default granularity.
  *Verification*: VT-001 - Test package detection across various directory structures

- **FR-002**: Deterministic File Ordering Within Packages
  Contract generation MUST process Python files within a package in deterministic sorted order (already implemented via `sorted(path.rglob("*.py"))`) to ensure identical output for identical package state across platforms and runs.
  *Verification*: VT-002 - Verify contract generation produces identical output across multiple runs

- **FR-003**: Sync Operation Package Support
  The `spec-driver sync` command MUST correctly index and validate package-level tech specs, recognizing Python packages (not individual files) as the fundamental unit for relationship tracking and registry operations.
  *Verification*: VT-003 - Test sync with package-level specs across various package structures

- **FR-004**: File-to-Package Resolution
  Query operations (e.g., `spec-driver list specs --for-path <file>`) MUST resolve individual Python files to their containing package's spec, enabling developers to discover relevant specs from any file within the package.
  *Verification*: VT-004 - Test --for-path with files at various depths in package hierarchy

### Non-Functional Requirements

- **NF-001**: Git Diff Stability
  Contract regeneration MUST produce stable, meaningful git diffs with changes reflecting only actual code modifications (new files, removed files, symbol changes), not spurious reordering or formatting variations.
  *Measurement*: VA-001 - Analyze contract diffs across 10+ regeneration cycles for spurious changes

- **NF-002**: Design Extensibility
  The package-level pattern MUST NOT preclude future addition of opt-in rollup mechanisms (parent package specs covering child packages) without breaking changes to existing specs or tooling.
  *Measurement*: VA-002 - Design review confirms rollup mechanism can be added via configuration without migration

### Success Metrics / Signals

- **Spec Count**: Reduction from 101 file-level specs to ~25-30 package-level specs (75% reduction)
- **Discoverability**: Developers can locate relevant spec in one query (100% success rate)
- **Maintenance Burden**: Refactoring within packages requires zero spec content updates
- **Pattern Consistency**: Python pattern matches Go pattern conceptually (leaf-level default)
- **Diff Quality**: Contract regeneration produces zero spurious changes (100% signal)

## 4. Solution Outline

### User Experience / Outcomes

**Desired Behaviors**:

1. **Clear Package Mapping**: Developer sees `supekku/scripts/lib/formatters/` and knows there's a `SPEC-formatters` covering that package
2. **Single Source of Design**: One spec documents complete formatter architecture, not fragmented across 5 file-level specs
3. **Refactoring Freedom**: Splitting `base.py` into `base.py` + `utils.py` updates contracts automatically, spec content unchanged
4. **Query Simplicity**: `--for-path supekku/scripts/lib/formatters/change_formatters.py` returns package spec directly
5. **Stable Diffs**: Git shows meaningful changes (new symbols, removed files), not spurious reordering

**User Expectations**:
- Package boundaries defined by `__init__.py` presence (Python standard)
- Specs cover packages, contracts cover files (separation of concerns)
- Tooling handles all file ordering/aggregation mechanics
- One-time migration acceptable (delete old, generate new)

### Data & Contracts

**Package-Level Spec Structure**:

```yaml
# Frontmatter
id: SPEC-045
slug: supekku-scripts-lib-formatters
name: supekku/scripts/lib/formatters Specification
sources:
- language: python
  identifier: supekku/scripts/lib/formatters
  module: supekku.scripts.lib.formatters
  variants:
  - name: public
    path: contracts/public.md
  - name: all
    path: contracts/all.md
  - name: tests
    path: contracts/tests.md
```

**Contract Generation** (existing mechanism):
- `sorted(path.rglob("*.py"))` ensures deterministic file order
- Filters: exclude `__init__.py`, exclude `*_test.py` (except tests variant)
- Output: All symbols from all package files in predictable sequence

**Registry Indexing**:
- Package path stored as primary identifier: `supekku/scripts/lib/formatters`
- File-to-package resolution via path prefix matching
- Backward index: package → list of files (for contract regeneration triggers)

## 5. Behaviour & Scenarios

### Primary Flows

**Flow 1: Package Detection During Spec Creation**

1. User invokes `spec-driver create spec "Formatters" --kind tech`
2. User prompted for package path or tooling infers from context
3. Tooling validates path contains `__init__.py` (confirms Python package)
4. Tooling detects leaf package (no child `__init__.py` files)
5. Spec generated with package-level frontmatter
6. Contracts auto-generated via existing mechanism (`sorted()` ordering)

**Flow 2: File-to-Package Resolution**

1. User queries `--for-path supekku/scripts/lib/formatters/decision_formatters.py`
2. Tooling traverses up directory tree looking for `__init__.py`
3. Finds package boundary at `supekku/scripts/lib/formatters/`
4. Registry lookup: package → SPEC-045
5. Returns SPEC-045 with file context ("you're in the formatters package")

**Flow 3: Contract Regeneration After Refactoring**

1. Developer splits `change_formatters.py` → `change/base.py` + `change/table.py`
2. Developer runs `spec-driver sync`
3. Sync detects files changed in `supekku/scripts/lib/formatters/`
4. Contract generator re-scans: `sorted(path.rglob("*.py"))`
5. New sorted list includes `change/base.py` and `change/table.py`
6. Contracts updated with new symbols in deterministic order
7. Spec content unchanged (package design still valid)

### Error Handling / Guards

**Guard: Non-Package Path**
- User tries to create spec for path without `__init__.py`
- Error: "Path is not a Python package (missing __init__.py)"
- Suggestion: "Did you mean the parent package at <nearest __init__.py>?"

**Guard: Parent Package Spec**
- User tries to create spec for `supekku/scripts/lib/` when child packages already have specs
- Warning: "Child packages have existing specs. Use --force-parent to create rollup spec."
- (Rollup mechanism deferred, so --force-parent not implemented initially)

**Guard: Duplicate Package Spec**
- Spec already exists for package
- Error: "SPEC-045 already covers supekku/scripts/lib/formatters/"
- Suggestion: "Use `spec-driver show SPEC-045` to view existing spec"

## 6. Quality & Verification

### Testing Strategy

**VT-001: Package Detection** (FR-001)
- Test cases: leaf packages, nested packages, single-file packages, test-only packages
- Verify correct identification of package boundaries via `__init__.py`
- Success: 100% accurate package boundary detection

**VT-002: Deterministic Ordering** (FR-002)
- Run contract generation 10 times on same package state
- Verify byte-identical output across all runs
- Test on Linux and macOS (different filesystem iteration orders)
- Success: Zero variation across runs/platforms

**VT-003: Sync Integration** (FR-003)
- Create package-level specs for 5 diverse packages
- Run `spec-driver sync`
- Verify registry correctly indexes all packages
- Test relationship tracking between package specs
- Success: Sync completes without errors, registry queries work

**VT-004: File-to-Package Resolution** (FR-004)
- Query `--for-path` for files at various depths
- Verify correct package spec returned
- Test edge cases: files in parent dirs, files in child packages
- Success: 100% correct resolution

**VA-001: Git Diff Stability** (NF-001)
- Generate contracts for package
- Make code change (add function)
- Regenerate contracts
- Analyze diff: should show only new function, no reordering
- Success: Zero spurious changes

**VA-002: Rollup Extensibility** (NF-002)
- Design review: propose rollup mechanism design
- Verify: no breaking changes to existing package specs
- Verify: configuration-driven (e.g., frontmatter flag or config file)
- Success: Design validated by maintainer

### Research / Validation

**Hypothesis 1**: Package-level granularity reduces spec count by 70-80%
- Test: Count file-level specs (101), count leaf packages (~25-30)
- Target: 70%+ reduction
- Evidence: Already validated via directory structure analysis

**Hypothesis 2**: Deterministic ordering already implemented
- Test: Review `supekku/scripts/lib/docs/python/variants.py`
- Verify: `sorted()` used in `get_files_for_variant()`
- Evidence: Code review confirms (line 40-50)

### Observability & Analysis

**Package Spec Metrics**:
- Number of package-level specs created
- Average files per package spec
- Package depth distribution (how nested are packages)

**Resolution Metrics**:
- `--for-path` query success rate
- Average resolution time (should be instant)

**Contract Stability**:
- Contract regeneration frequency
- Git diff size (lines changed per regeneration)
- Spurious change rate (should be 0%)

### Security & Compliance

**No Security Concerns**: This is a documentation/tooling granularity decision with no security implications.

**Data Privacy**: Specs and contracts are local files, no external data transmission.

### Acceptance Gates

1. **Package Detection Works**: VT-001 passes with 100% accuracy across diverse package structures
2. **Deterministic Ordering Validated**: VT-002 shows zero variation across 10 runs on 2 platforms
3. **Sync Integration Complete**: VT-003 passes with package-level specs correctly indexed
4. **File Resolution Accurate**: VT-004 shows 100% correct package resolution from file paths
5. **Git Diffs Stable**: VA-001 demonstrates zero spurious changes across regeneration cycles
6. **Rollup Design Sound**: VA-002 confirms future rollup mechanism feasible without breaking changes

## 7. Backlog Hooks & Dependencies

### Related Specs / PROD

**Direct Dependencies**:
- **PROD-001** (Streamline Spec Creation): This spec extends PROD-001's workflow to Python packages; spec creation mechanics remain the same, granularity changes

**Future Candidates**:
- **Opt-in Rollup Mechanism** (deferred): Allow parent package specs to roll up child packages via configuration
- **JS/TS Granularity Evaluation** (deferred): Determine appropriate granularity for JavaScript/TypeScript projects
- **Cross-Language Consistency** (future): Ensure patterns remain coherent across Go/Python/JS ecosystems

### Risks & Mitigations

**RISK-001**: Deep package nesting creates too many specs
- **Likelihood**: Low (Python codebases rarely nest beyond 3-4 levels)
- **Impact**: Medium (spec count higher than desired)
- **Mitigation**: Rollup mechanism addresses this if it occurs; defer until real evidence

**RISK-002**: Developers expect file-level detail in specs
- **Likelihood**: Medium (habit from file-level approach)
- **Impact**: Low (contracts provide file-level detail)
- **Mitigation**: Documentation clarifies: specs = package design, contracts = file detail

**RISK-003**: Package refactoring (splitting/merging packages) disrupts specs
- **Likelihood**: Low (package structure relatively stable)
- **Impact**: Medium (spec needs rewrite when package boundaries change)
- **Mitigation**: Acceptable trade-off; package refactoring is deliberate architectural change

**RISK-004**: Rollup mechanism never gets designed
- **Likelihood**: Medium (solo user may not need it)
- **Impact**: Low (leaf-package granularity works well)
- **Mitigation**: Design accommodates future addition (NF-002); no urgency

### Known Gaps / Debt

**Gaps**:
- No rollup mechanism (intentionally deferred)
- No JS/TS granularity decision (different language, separate evaluation)
- No migration tooling (manual cleanup acceptable for current user)
- Package-level spec creation guidance in documentation (needs update)

**Technical Debt**:
- Existing 101 file-level specs need deletion (one-time manual task)
- Registry may have file-level indexing assumptions (audit needed)

### Open Decisions / Questions

**Decision 1**: Should package specs include sub-package relationships explicitly?
- **Context**: If `supekku/scripts/lib/` has spec, should it list child packages?
- **Options**: (A) Yes, explicit list (B) No, inferred from filesystem (C) Optional metadata
- **Leaning**: B (inferred from filesystem) - reduces maintenance burden

**Decision 2**: What happens when __init__.py removed from package?
- **Context**: Package boundary disappears, becomes parent package
- **Options**: (A) Spec becomes orphaned (error) (B) Spec automatically associates with parent (C) User must manually update
- **Leaning**: A (orphaned/error) - deliberate package structure change should be deliberate spec change

**Decision 3**: Should contract variants live in package or spec directory?
- **Context**: Currently contracts in `specify/tech/SPEC-XXX/contracts/`, could be near code
- **Options**: (A) Keep in spec dir (current) (B) Near code (e.g., `supekku/formatters/.spec/contracts/`)
- **Decision**: A (keep current) - separation of code and documentation, already working

## Appendices (Optional)

### Glossary

- **Leaf Package**: Python package (directory with `__init__.py`) containing no child packages with `__init__.py`
- **Package-Level Spec**: Tech spec documenting a Python package's architecture, covering all files within
- **Contract**: Auto-generated API documentation for a package variant (public/all/tests)
- **Rollup**: Future mechanism allowing parent package specs to cover child packages (deferred)

### Migration Path (Reference)

**Current State**: 101 file-level specs (SPEC-001 through SPEC-101, mostly placeholders)

**Target State**: ~25-30 leaf-package specs

**Migration Steps** (manual, one-time):
1. Identify leaf packages in `supekku/` directory tree
2. Delete existing file-level specs: `rm -rf specify/tech/SPEC-0*`
3. Create package-level spec for each leaf package via `spec-driver create spec`
4. Fill specs with package-level design (not file-by-file detail)
5. Run `spec-driver sync` to rebuild registry
6. Validate with `spec-driver validate`

**Time Estimate**: 2-4 hours for cleanup + spec creation

### Design Rationale: Why Not Other Granularities?

**File-level (rejected)**:
- 101 specs for 108 files = unsustainable maintenance
- Cognitive fragmentation (features span multiple files)
- Refactoring tax (file renames/moves break specs)

**Capability/feature-level (considered)**:
- Overlaps with PROD specs (which are capability-focused)
- Harder to automate (subjective boundaries)
- TECH specs should map to code structure, PROD specs to user features

**Component/cohesion-based (considered)**:
- Requires subjective decisions ("is this cohesive enough?")
- Inconsistent across projects/developers
- Automation difficult without heuristics

**Leaf-package level (chosen)**:
- Predictable, automatable (follows filesystem structure)
- Matches Go proven pattern from vice
- Reduces spec count by 75% while maintaining traceability
- Aligns with Python conventions (`__init__.py` = package boundary)
