---
id: SPEC-124
slug: supekku-scripts-lib-sync-adapters
name: supekku/scripts/lib/sync/adapters Specification
created: '2025-11-02'
updated: '2025-11-02'
status: draft
kind: spec
responsibilities:
- Language-specific source code discovery
- AST-based documentation generation
- Multi-language adapter abstraction
- Source validation and git tracking
aliases: []
packages:
- supekku/scripts/lib/sync/adapters
sources:
- language: python
  identifier: supekku/scripts/lib/sync/adapters
  module: supekku.scripts.lib.sync.adapters
  variants:
  - name: api
    path: contracts/api.md
  - name: implementation
    path: contracts/implementation.md
  - name: tests
    path: contracts/tests.md
owners: []
auditers: []
relations: []
---

# SPEC-124 – supekku/scripts/lib/sync/adapters Specification

```yaml supekku:spec.relationships@v1
schema: supekku.spec.relationships
version: 1
spec: SPEC-124
requirements:
  primary:
    - SPEC-124.FR-001
    - SPEC-124.FR-002
    - SPEC-124.FR-003
    - SPEC-124.FR-004
    - SPEC-124.FR-005
    - SPEC-124.FR-006
    - SPEC-124.FR-007
    - SPEC-124.FR-008
    - SPEC-124.FR-009
    - SPEC-124.NF-001
    - SPEC-124.NF-002
    - SPEC-124.NF-003
  collaborators: []
interactions:
  - spec: SPEC-123
    type: uses
    description: Uses package_utils for discovering leaf Python packages
  - spec: SPEC-116
    type: uses
    description: Uses core utilities for Go toolchain detection and subprocess execution
```

```yaml supekku:spec.capabilities@v1
schema: supekku.spec.capabilities
version: 1
spec: SPEC-124
capabilities:
  - id: language-adapter-abstraction
    name: Language Adapter Abstraction
    responsibilities:
      - Define abstract interface for language-specific documentation generation
      - Enforce consistent discovery, description, and generation workflows
      - Support identifier validation and source existence checking
    requirements:
      - SPEC-124.FR-001
      - SPEC-124.FR-002
      - SPEC-124.NF-001
    summary: |
      Provides abstract base class (LanguageAdapter) defining the contract for language-specific
      adapters. Ensures consistent interface across Python, Go, TypeScript/JavaScript adapters
      while allowing language-specific implementation details.
    success_criteria:
      - All language adapters implement the same abstract interface
      - Adapters can be used interchangeably by sync engine
      - Source validation is consistent across languages

  - id: python-ast-documentation
    name: Python AST Documentation
    responsibilities:
      - Discover Python modules for documentation
      - Generate AST-based documentation variants (public, all, tests)
      - Validate Python source files and git tracking
    requirements:
      - SPEC-124.FR-003
      - SPEC-124.FR-004
      - SPEC-124.NF-002
    summary: |
      Python adapter using AST analysis to generate deterministic, token-efficient documentation
      from Python source files. Discovers modules, extracts structure, and generates contract
      markdown files for spec synchronization.
    success_criteria:
      - Python modules successfully discovered from repository
      - Documentation preserves docstring fidelity
      - Generated contracts match AST structure

  - id: go-gomarkdoc-integration
    name: Go gomarkdoc Integration
    responsibilities:
      - Discover Go packages using `go list`
      - Generate documentation using gomarkdoc toolchain
      - Validate Go toolchain and gomarkdoc availability
    requirements:
      - SPEC-124.FR-005
      - SPEC-124.FR-006
      - SPEC-124.NF-002
    summary: |
      Go adapter wrapping existing gomarkdoc workflow. Provides consistent interface while
      maintaining backward compatibility with TechSpecSyncEngine. Handles Go-specific package
      discovery and documentation generation.
    success_criteria:
      - Go packages discovered via `go list`
      - gomarkdoc successfully generates documentation
      - Graceful error handling when Go toolchain unavailable

  - id: typescript-ast-extraction
    name: TypeScript AST Extraction
    responsibilities:
      - Discover TypeScript/JavaScript modules and logical units
      - Extract AST using ts-morph via Node.js subprocess
      - Generate token-efficient documentation from AST JSON
      - Support multiple package managers (npm, pnpm, bun)
    requirements:
      - SPEC-124.FR-007
      - SPEC-124.FR-008
      - SPEC-124.FR-009
      - SPEC-124.NF-002
      - SPEC-124.NF-003
    summary: |
      TypeScript/JavaScript adapter using ts-morph for AST-based extraction. Mirrors Python
      adapter architecture with logical module discovery (not just packages). Supports .ts,
      .tsx, .js, .jsx files across npm/pnpm/bun ecosystems.
    success_criteria:
      - Logical modules discovered (directories with index files, standalone files)
      - AST successfully extracted via ts-doc-extract subprocess
      - Documentation generated from AST JSON
      - Multiple package managers supported
```

```yaml supekku:verification.coverage@v1
schema: supekku.verification.coverage
version: 1
subject: SPEC-124
entries:
  - artefact: VT-001
    kind: VT
    requirement: SPEC-124.FR-001
    status: implemented
    notes: LanguageAdapter abstract interface tests (base_test.py)

  - artefact: VT-002
    kind: VT
    requirement: SPEC-124.FR-002
    status: implemented
    notes: Source validation and git tracking tests (base_test.py)

  - artefact: VT-003
    kind: VT
    requirement: SPEC-124.FR-003
    status: implemented
    notes: Python adapter discovery and generation tests (python_test.py)

  - artefact: VT-004
    kind: VT
    requirement: SPEC-124.FR-004
    status: implemented
    notes: Python docstring preservation tests (python_test.py)

  - artefact: VT-005
    kind: VT
    requirement: SPEC-124.FR-005
    status: implemented
    notes: Go adapter discovery tests (go_test.py)

  - artefact: VT-006
    kind: VT
    requirement: SPEC-124.FR-006
    status: implemented
    notes: Go toolchain validation tests (go_test.py)

  - artefact: VT-007
    kind: VT
    requirement: SPEC-124.FR-007
    status: implemented
    notes: TypeScript adapter discovery tests (typescript_test.py)

  - artefact: VT-008
    kind: VT
    requirement: SPEC-124.FR-008
    status: implemented
    notes: TypeScript AST extraction tests (typescript_test.py)

  - artefact: VT-009
    kind: VT
    requirement: SPEC-124.FR-009
    status: implemented
    notes: Node.js runtime validation tests (typescript_test.py)

  - artefact: VT-010
    kind: VT
    requirement: SPEC-124.NF-001
    status: implemented
    notes: Deterministic output tests across all adapters

  - artefact: VT-011
    kind: VT
    requirement: SPEC-124.NF-002
    status: implemented
    notes: Error handling tests for missing toolchains

  - artefact: VT-012
    kind: VT
    requirement: SPEC-124.NF-003
    status: implemented
    notes: Package manager detection tests (typescript_test.py)
```

## 1. Intent & Summary

- **Scope / Boundaries**:
  - IN: Language-specific adapters for Python, Go, TypeScript/JavaScript
  - IN: AST-based documentation generation for static analysis
  - IN: Source discovery, validation, git tracking
  - IN: Multi-variant documentation (public, all, tests)
  - OUT: Runtime code execution or dynamic analysis
  - OUT: Languages beyond Python, Go, TypeScript/JavaScript
  - OUT: Bidirectional synchronization (write-back to code)

- **Value Signals**:
  - Enables spec backfill workflow (reduces completion time from 2hrs → 10min)
  - 100% coverage of multi-language codebases after sync
  - Zero manual contract writing for supported languages
  - Deterministic, token-efficient documentation generation

- **Guiding Principles**:
  - Static analysis only (no code execution)
  - Preserve docstring/comment fidelity
  - AST-based extraction for reliability
  - Language-agnostic abstraction with language-specific implementations
  - Fail gracefully when toolchains unavailable
  - Support check mode for validation without writes

- **Change History**: Introduced in DE-005 (spec backfill implementation)

## 2. Stakeholders & Journeys

- **Systems / Integrations**:
  - Python AST parser (built-in `ast` module)
  - Go toolchain (`go list`) and gomarkdoc
  - Node.js runtime and ts-morph (via ts-doc-extract npm package)
  - Git for source tracking validation
  - Package managers: npm, pnpm, bun (TypeScript/JavaScript)

- **Primary Journeys / Flows**:

  1. **Discover Sources**:
     - Given: Repository root and optional requested identifiers
     - When: `discover_targets()` is called
     - Then: Adapter returns list of SourceUnit objects representing discoverable modules/packages

  2. **Generate Documentation**:
     - Given: SourceUnit from discovery
     - When: `generate()` is called
     - Then: Adapter produces DocVariant objects with generated markdown content

  3. **Validate Sources**:
     - Given: SourceUnit to validate
     - When: `validate_source_exists()` is called
     - Then: Adapter checks file/directory existence and git tracking status

- **Edge Cases & Non-goals**:
  - NOT supporting languages beyond Python/Go/TypeScript/JavaScript initially
  - NOT executing code for dynamic analysis
  - NOT supporting write-back from specs to source code
  - Graceful degradation when toolchains unavailable (error messages, not crashes)

## 3. Responsibilities & Requirements

### Capability Overview

The sync adapters provide a **pluggable architecture** for generating specifications from source code across multiple programming languages. Each adapter:

1. **Discovers** language-specific source units (packages, modules, files)
2. **Describes** how units should be processed (slug parts, frontmatter, variants)
3. **Generates** documentation variants using language-appropriate tooling
4. **Validates** source existence and git tracking

The base `LanguageAdapter` abstract class ensures consistency while allowing language-specific implementations (Python AST, Go gomarkdoc, TypeScript ts-morph).

### Functional Requirements

- **SPEC-124.FR-001**: LanguageAdapter base class MUST define abstract methods for `discover_targets()`, `describe()`, `generate()`, and `supports_identifier()`
  *Verification*: VT-001 - Base class interface tests

- **SPEC-124.FR-002**: LanguageAdapter MUST provide `validate_source_exists()` to check file/directory existence and git tracking status
  *Verification*: VT-002 - Source validation tests

- **SPEC-124.FR-003**: PythonAdapter MUST discover Python modules using package structure and `__init__.py` detection
  *Verification*: VT-003 - Python discovery tests

- **SPEC-124.FR-004**: PythonAdapter MUST generate AST-based documentation preserving docstring formatting (including indentation)
  *Verification*: VT-004 - Docstring preservation tests

- **SPEC-124.FR-005**: GoAdapter MUST discover Go packages using `go list` command
  *Verification*: VT-005 - Go package discovery tests

- **SPEC-124.FR-006**: GoAdapter MUST validate Go toolchain and gomarkdoc availability before generation
  *Verification*: VT-006 - Toolchain validation tests

- **SPEC-124.FR-007**: TypeScriptAdapter MUST discover logical modules (directories with index.ts/js, standalone files, src/ subdirectories)
  *Verification*: VT-007 - TypeScript discovery tests

- **SPEC-124.FR-008**: TypeScriptAdapter MUST extract AST using ts-morph via ts-doc-extract subprocess
  *Verification*: VT-008 - AST extraction tests

- **SPEC-124.FR-009**: TypeScriptAdapter MUST detect and support npm, pnpm, and bun package managers
  *Verification*: VT-009 - Package manager detection tests

### Non-Functional Requirements

- **SPEC-124.NF-001**: All adapters MUST generate deterministic output (same input → same output)
  *Measurement*: VT-010 - Deterministic output verification tests

- **SPEC-124.NF-002**: Adapters MUST fail gracefully with descriptive errors when required toolchains are unavailable
  *Measurement*: VT-011 - Error handling tests for missing Go/Node.js

- **SPEC-124.NF-003**: TypeScriptAdapter MUST support multiple package managers without requiring explicit configuration
  *Measurement*: VT-012 - Package manager auto-detection tests

### Operational Targets

- **Performance**: Process 100 Python modules in <5 seconds (AST parsing)
- **Reliability**: 100% success rate for valid source files with available toolchains
- **Maintainability**: Adding new language adapter requires only implementing 4 abstract methods

## 4. Solution Outline

### Architecture / Components

The adapter architecture follows a **Strategy pattern** with abstract base class:

```
LanguageAdapter (ABC)
├── discover_targets() -> List[SourceUnit]
├── describe(unit) -> SourceDescriptor
├── generate(unit) -> List[DocVariant]
├── supports_identifier(id) -> bool
└── validate_source_exists(unit) -> dict

Concrete Adapters:
├── PythonAdapter
│   ├── Uses ast module for parsing
│   ├── Discovers via package_utils.find_all_leaf_packages()
│   └── Generates: *-public.md, *-all.md, *-tests.md
│
├── GoAdapter
│   ├── Uses `go list` for discovery
│   ├── Wraps existing TechSpecSyncEngine logic
│   └── Generates via gomarkdoc subprocess
│
└── TypeScriptAdapter
    ├── Uses ts-doc-extract (Node.js subprocess)
    ├── Discovers logical modules (not just packages)
    ├── Supports npm/pnpm/bun detection
    └── Generates from AST JSON output
```

### Data Models

**SourceUnit** (from `supekku.scripts.lib.sync.models`):
- `identifier`: Language-specific source identifier (e.g., module path, package name)
- `language`: Language type (python, go, typescript)
- `path`: Filesystem path to source

**SourceDescriptor**:
- `slug_parts`: List of slug components for contract filenames
- `frontmatter`: Default frontmatter metadata
- `variants`: List of documentation variant types to generate

**DocVariant**:
- `name`: Variant name (public, all, tests)
- `path`: Output path for generated contract
- `content`: Generated markdown content
- `changed`: Whether content differs from existing file

### Interfaces

All adapters implement the `LanguageAdapter` interface:

```python
class LanguageAdapter(ABC):
    @abstractmethod
    def discover_targets(self, repo_root: Path, requested: Optional[List[str]]) -> List[SourceUnit]:
        """Discover source units for this language."""

    @abstractmethod
    def describe(self, unit: SourceUnit) -> SourceDescriptor:
        """Describe how a source unit should be processed."""

    @abstractmethod
    def generate(self, unit: SourceUnit) -> List[DocVariant]:
        """Generate documentation variants for a source unit."""

    @abstractmethod
    def supports_identifier(self, identifier: str) -> bool:
        """Check if this adapter can handle the given identifier format."""

    def validate_source_exists(self, unit: SourceUnit) -> dict:
        """Validate that source exists and is git-tracked."""
```

## 5. Behaviour & Scenarios

### Primary Flow: Multi-Language Documentation Generation

1. **Given**: Repository root and language adapter
2. **When**: Sync engine calls `discover_targets(repo_root, requested=None)`
3. **Then**: Adapter:
   - Scans repository for language-specific sources
   - Returns list of SourceUnit objects

4. **When**: For each SourceUnit, engine calls `describe(unit)`
5. **Then**: Adapter returns SourceDescriptor with:
   - Slug parts for filename generation
   - Frontmatter metadata
   - Variant types to generate (public, all, tests)

6. **When**: Engine calls `generate(unit)`
7. **Then**: Adapter:
   - Validates source exists and is git-tracked
   - Extracts AST or runs language-specific tooling
   - Generates markdown content for each variant
   - Returns list of DocVariant objects

### Python Adapter Flow

1. **Discovery**: Uses `find_all_leaf_packages()` to find Python packages with `__init__.py`
2. **Description**: Generates slug from module path (e.g., `supekku.scripts.lib.sync` → `supekku-scripts-lib-sync`)
3. **Generation**:
   - Parses Python AST
   - Extracts functions, classes, methods with docstrings
   - Generates 3 variants: public, all, tests
   - Preserves docstring indentation and formatting

### Go Adapter Flow

1. **Discovery**: Executes `go list ./...` to find Go packages
2. **Description**: Uses package path for slug
3. **Generation**:
   - Validates Go toolchain available
   - Validates gomarkdoc available
   - Executes gomarkdoc subprocess
   - Returns generated documentation

### TypeScript Adapter Flow

1. **Discovery**:
   - Finds packages with `package.json` containing TypeScript/JavaScript
   - Within packages, discovers logical modules:
     - Directories with `index.ts` or `index.js`
     - Standalone significant `.ts`/`.js` files
     - Top-level `src/` subdirectories

2. **Description**: Generates slug from module path
3. **Generation**:
   - Validates Node.js runtime available
   - Detects package manager (npm/pnpm/bun)
   - Executes ts-doc-extract subprocess
   - Parses AST JSON output
   - Generates markdown from AST structure

### Error Handling / Guards

- **Missing Toolchain**: Adapters check for required tools (Go, Node.js, gomarkdoc) before generation
  - Raises descriptive errors: `GoToolchainNotAvailableError`, `NodeRuntimeNotAvailableError`
  - Errors caught by sync engine for graceful degradation

- **Invalid Source**: `validate_source_exists()` checks:
  - File/directory exists on disk
  - Source is git-tracked (warns if untracked)
  - Returns status: "valid", "missing", or "untracked"

- **Parse Failures**: Language-specific parse errors (AST, subprocess) are caught and re-raised with context

## 6. Quality & Verification

### Testing Strategy

- **Unit Tests**: Each adapter has comprehensive test suite
  - Base: Abstract interface enforcement, source validation
  - Python: Discovery, AST parsing, docstring preservation
  - Go: Package discovery, toolchain validation, gomarkdoc integration
  - TypeScript: Logical module discovery, AST extraction, package manager detection

- **Integration Tests**: Not yet implemented (would test end-to-end sync workflow)

- **Test Coverage**: >80% coverage across all adapters (based on test file sizes)

### Observability & Analysis

- **Logging**: [ASSUMPTION: Based on sync engine patterns, assuming logging for discovery/generation steps]
- **Metrics**: Not currently instrumented
- **Error Tracking**: Descriptive exceptions with context (toolchain errors, parse failures)

### Security & Compliance

- **Input Validation**: Source paths validated for existence and git tracking
- **Subprocess Execution**:
  - Go: Uses `subprocess.run()` with `go list` and `gomarkdoc`
  - TypeScript: Uses `subprocess.run()` with Node.js ts-doc-extract
  - [ASSUMPTION: No shell=True usage, paths are validated]
- **No Code Execution**: Static analysis only (AST parsing, no `eval()` or `exec()`)

### Verification Coverage

All functional requirements have corresponding unit tests (VT-001 through VT-012). Tests validate:
- Abstract interface enforcement
- Source discovery for each language
- Documentation generation with toolchains
- Graceful error handling for missing dependencies
- Deterministic output

### Acceptance Gates

- All unit tests pass (`just test`)
- Linters pass (ruff, pylint)
- Spec backfill workflow completes in <10 minutes per spec
- Multi-language repositories successfully sync (Python + Go + TypeScript)

## 7. Backlog Hooks & Dependencies

### Related Specs / PROD

- **SPEC-123** (supekku/scripts/lib/specs): Uses `package_utils.find_all_leaf_packages()` for Python discovery
- **SPEC-116** (supekku/scripts/lib/core): Uses `go_utils` for Go toolchain detection
- **sync.models** (not yet spec'd): Defines SourceUnit, SourceDescriptor, DocVariant data models
- **sync.engine** (not yet spec'd): Orchestrates adapter discovery and generation

### Risks & Mitigations

- **Risk**: Toolchain dependencies (Go, Node.js, gomarkdoc) not available
  - **Mitigation**: Graceful errors, check mode validation, installation documentation

- **Risk**: Language-specific edge cases (complex AST patterns)
  - **Mitigation**: Comprehensive test coverage, incremental adapter improvements

- **Risk**: Breaking changes in external tools (gomarkdoc, ts-morph)
  - **Mitigation**: Version pinning in npm package, integration tests

### Known Gaps / Debt

- Integration tests for full sync workflow (discovery → description → generation → write)
- Performance benchmarks for large codebases (>1000 files)
- Support for additional languages (Rust, Java, etc.)
- Documentation of expected AST JSON schema from ts-doc-extract

### Open Decisions / Questions

None currently. All design decisions implemented and tested.
