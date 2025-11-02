---
id: SPEC-112
slug: supekku-scripts-cli
name: supekku/scripts/cli Specification
created: '2025-11-02'
updated: '2025-11-02'
status: stub
kind: spec
responsibilities: []
aliases: []
packages:
- supekku/scripts/cli
sources:
- language: python
  identifier: supekku/scripts/cli
  module: supekku.scripts.cli
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

# SPEC-112 – supekku/scripts/cli Specification

```yaml supekku:spec.relationships@v1
schema: supekku.spec.relationships
version: 1
spec: SPEC-112
requirements:
  primary:
    - SPEC-112.FR-001
    - SPEC-112.FR-002
    - SPEC-112.FR-003
    - SPEC-112.FR-004
    - SPEC-112.FR-005
    - SPEC-112.FR-006
    - SPEC-112.FR-007
    - SPEC-112.NF-001
    - SPEC-112.NF-002
  collaborators: []
interactions:
  - spec: SPEC-113
    type: uses
    description: Uses library API from supekku.scripts.lib.docs.python for AST parsing and doc generation
```

```yaml supekku:spec.capabilities@v1
schema: supekku.spec.capabilities
version: 1
spec: SPEC-112
capabilities:
  - id: ast-doc-cli-interface
    name: AST Documentation CLI Interface
    responsibilities:
      - Provides command-line interface for generating Python documentation from AST
      - Supports multiple documentation variants (public, all, tests)
      - Accepts user arguments and validates input paths
    requirements:
      - SPEC-112.FR-001
      - SPEC-112.FR-002
      - SPEC-112.FR-003
    summary: |
      Exposes a user-facing command-line interface for AST-based documentation generation.
      Handles argument parsing, input validation, and user interaction patterns.
    success_criteria:
      - CLI accepts standard arguments (path, type, output-dir, check mode)
      - Invalid inputs result in clear error messages with exit code 1
      - Help text and usage information available via --help

  - id: check-mode-validation
    name: Check Mode Validation
    responsibilities:
      - Verifies generated documentation matches existing files without writing
      - Compares content hashes to detect drift
      - Reports mismatches with appropriate exit codes
    requirements:
      - SPEC-112.FR-004
      - SPEC-112.NF-001
    summary: |
      Implements check mode validation to ensure documentation stays synchronized with code.
      Uses content hashing for deterministic comparison without side effects.
    success_criteria:
      - Check mode exits 0 when all docs match
      - Check mode exits 1 when any doc is missing or changed
      - No files written in check mode

  - id: result-formatting
    name: Result Formatting and Reporting
    responsibilities:
      - Formats generation results for user-friendly display
      - Provides status symbols and summary statistics
      - Handles verbose and quiet output modes
    requirements:
      - SPEC-112.FR-005
      - SPEC-112.FR-006
    summary: |
      Presents documentation generation results in a clear, scannable format.
      Supports different verbosity levels and includes summary statistics.
    success_criteria:
      - Status displayed with clear symbols (+ created, ~ changed, = unchanged, ✗ error)
      - Summary shows counts by status type
      - Verbose mode includes content hashes

  - id: backward-compatibility
    name: Backward Compatibility Layer
    responsibilities:
      - Maintains compatibility with original CLI interface
      - Delegates to refactored library API
      - Preserves expected behavior for existing scripts/tools
    requirements:
      - SPEC-112.FR-007
      - SPEC-112.NF-002
    summary: |
      Ensures existing tools and scripts continue to work after library refactoring.
      Acts as adapter between legacy CLI interface and modern library API.
    success_criteria:
      - All original CLI arguments still accepted
      - Output format unchanged from user perspective
      - Exit codes match original behavior
```

```yaml supekku:verification.coverage@v1
schema: supekku.verification.coverage
version: 1
subject: SPEC-112
entries:
  - artefact: VT-001
    kind: VT
    requirement: SPEC-112.FR-001
    status: planned
    notes: Test argument parser accepts valid path arguments

  - artefact: VT-002
    kind: VT
    requirement: SPEC-112.FR-002
    status: planned
    notes: Test variant type selection (public, all, tests)

  - artefact: VT-003
    kind: VT
    requirement: SPEC-112.FR-003
    status: planned
    notes: Test invalid path handling and error exit codes

  - artefact: VT-004
    kind: VT
    requirement: SPEC-112.FR-004
    status: planned
    notes: Test check mode comparison logic and exit codes

  - artefact: VT-005
    kind: VT
    requirement: SPEC-112.FR-005
    status: planned
    notes: Test status symbol selection and formatting

  - artefact: VT-006
    kind: VT
    requirement: SPEC-112.FR-006
    status: planned
    notes: Test summary statistics calculation and display

  - artefact: VT-007
    kind: VT
    requirement: SPEC-112.FR-007
    status: planned
    notes: Test backward compatibility with original CLI interface

  - artefact: VA-001
    kind: VA
    requirement: SPEC-112.NF-001
    status: planned
    notes: Performance benchmark for typical documentation generation workload

  - artefact: VH-001
    kind: VH
    requirement: SPEC-112.NF-002
    status: planned
    notes: Manual verification that existing scripts work without modification
```

## 1. Intent & Summary

- **Scope / Boundaries**:
  - IN: Command-line interfaces for AST documentation generation (`ast_doc_generator.py`, `deterministic_ast_doc_generator.py`)
  - IN: Argument parsing, input validation, result formatting
  - IN: Check mode validation and backward compatibility
  - OUT: AST parsing logic (delegated to `supekku.scripts.lib.docs.python`)
  - OUT: Documentation generation algorithms (delegated to library)
  - OUT: File I/O and caching implementation (delegated to library)

- **Value Signals**:
  - Provides user-friendly CLI for documentation generation workflow
  - Enables CI/CD integration via check mode (exit codes)
  - Maintains backward compatibility reducing migration friction
  - Clear status reporting improves developer experience

- **Guiding Principles**:
  - Thin CLI wrapper - delegate complex logic to library API
  - Preserve backward compatibility for existing tools
  - Clear, actionable error messages
  - Deterministic behavior for CI/CD reliability

- **Change History**:
  - Introduced as part of AST documentation generation system
  - Refactored to use modular library API while maintaining CLI compatibility

## 2. Stakeholders & Journeys

- **Systems / Integrations**:
  - **Library API** (`supekku.scripts.lib.docs.python`): Core AST parsing and doc generation
  - **File System**: Reads Python source files, writes/checks documentation files
  - **CI/CD Systems**: Invoked via automation scripts with check mode
  - **Developer Workstations**: Interactive CLI usage during development

- **Primary Journeys / Flows**:

  **Developer generates docs locally**:
  - Given a Python package directory
  - When developer runs `ast_doc_generator.py <path> --type public`
  - Then docs are generated to default output directory
  - And status summary shows created/changed/unchanged counts

  **CI pipeline validates docs are up-to-date**:
  - Given a CI/CD pipeline with documentation checks
  - When pipeline runs `deterministic_ast_doc_generator.py <path> --check`
  - Then check mode verifies docs match code without writing
  - And pipeline fails (exit 1) if docs are stale

  **Developer previews what would change**:
  - Given existing documentation
  - When developer runs with `--check --verbose`
  - Then tool shows which files would change with hashes
  - And no files are modified

- **Edge Cases & Non-goals**:
  - Does NOT handle non-Python languages
  - Does NOT implement custom documentation formatters
  - Does NOT provide interactive editing or preview modes
  - Error handling: Invalid paths exit with code 1, permission errors exit with code 1

## 3. Responsibilities & Requirements

### Capability Overview

The CLI package provides four main capabilities:

1. **AST Documentation CLI Interface**: Exposes user-friendly command-line tools for documentation generation with standard Unix conventions
2. **Check Mode Validation**: Implements dry-run verification for CI/CD integration
3. **Result Formatting**: Presents generation results in clear, scannable format with status symbols and statistics
4. **Backward Compatibility**: Maintains compatibility with original CLI interface while using refactored library underneath

### Functional Requirements

- **SPEC-112.FR-001**: CLI MUST accept a path argument (file or directory) and validate it exists before processing
  *Example*: `ast_doc_generator.py /path/to/package` validates path exists
  *Verification*: VT-001 - Path validation test

- **SPEC-112.FR-002**: CLI MUST support `--type` argument with choices: `public` (default), `all`, `tests` to control documentation variants
  *Example*: `--type all` generates documentation including private symbols
  *Verification*: VT-002 - Variant selection test

- **SPEC-112.FR-003**: CLI MUST exit with code 1 for invalid inputs (missing path, permission errors, invalid arguments) and print clear error messages
  *Example*: Non-existent path prints "Error: <path> does not exist" and exits 1
  *Verification*: VT-003 - Error handling test

- **SPEC-112.FR-004**: CLI MUST support `--check` mode that verifies documentation matches code without writing files, exiting 0 if unchanged or 1 if changes detected
  *Example*: `--check` compares content hashes and exits 1 if any doc is stale
  *Verification*: VT-004 - Check mode comparison test

- **SPEC-112.FR-005**: CLI MUST format results with status symbols: `+` (created), `~` (changed), `=` (unchanged), `✗` (error), with `✓`/`✗` in check mode
  *Example*: Output shows `+ contracts/module.md: created`
  *Verification*: VT-005 - Status symbol formatting test

- **SPEC-112.FR-006**: CLI MUST print summary statistics showing counts by status (created, changed, unchanged, errors) after processing multiple files
  *Example*: "Summary: 3 created, 1 changed, 5 unchanged (9 files total)"
  *Verification*: VT-006 - Summary statistics test

- **SPEC-112.FR-007**: CLI MUST maintain backward compatibility with original interface including all argument names, default values, and exit codes
  *Example*: Existing scripts using old CLI continue to work without modification
  *Verification*: VT-007 - Backward compatibility integration test

### Non-Functional Requirements

- **SPEC-112.NF-001**: CLI MUST complete documentation generation for typical package (≤100 files) in ≤5 seconds (wall time) on modern hardware
  *Example*: Generate docs for `supekku/scripts/lib` package in <5s
  *Measurement*: VA-001 - Performance benchmark with time measurement

- **SPEC-112.NF-002**: CLI MUST preserve all original argument names, defaults, and behaviors to ensure zero-modification migration for existing scripts
  *Example*: Scripts using `--output-dir`, `--cache-dir`, `--no-cache` work unchanged
  *Measurement*: VH-001 - Manual verification with existing automation scripts

### Operational Targets

- **Performance**: ≤5 seconds for typical package documentation generation
- **Reliability**: 100% deterministic output (same input → same output hash)
- **Maintainability**: Thin wrapper pattern keeps CLI files ≤250 lines

## 4. Solution Outline

### Architecture / Components

```
┌─────────────────────────────────────────┐
│  supekku/scripts/cli                    │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────────────────────────┐  │
│  │ ast_doc_generator.py             │  │
│  │ - create_parser()                │  │
│  │ - format_status_output()         │  │
│  │ - main()                         │  │
│  └────────────┬─────────────────────┘  │
│               │                         │
│  ┌────────────▼─────────────────────┐  │
│  │ deterministic_ast_doc_generator  │  │
│  │ - check_mode_comparison()        │  │
│  │ - write_mode_comparison()        │  │
│  │ - format_results()               │  │
│  │ - get_status_symbol()            │  │
│  │ - print_summary()                │  │
│  │ - main()                         │  │
│  └────────────┬─────────────────────┘  │
│               │                         │
└───────────────┼─────────────────────────┘
                │
                │ delegates to
                ▼
┌─────────────────────────────────────────┐
│  supekku.scripts.lib.docs.python        │
│  - generate_docs()                      │
│  - VariantSpec / VariantCoordinator     │
│  - ParseCache                           │
│  - calculate_content_hash()             │
└─────────────────────────────────────────┘
```

**Key Components**:

1. **Argument Parsers** (`create_parser()`): Standard argparse-based CLI argument handling
2. **Main Entry Points** (`main()`): Orchestrate argument parsing → library API call → result formatting
3. **Result Formatters** (`format_status_output()`, `format_results()`): Convert library results to user-friendly output
4. **Comparison Functions** (`check_mode_comparison()`, `write_mode_comparison()`): Backward compatibility helpers for tests
5. **Status Helpers** (`get_status_symbol()`, `print_summary()`): UI/formatting utilities

### Data & Contracts

**Input Arguments** (argparse namespace):
```python
{
  'path': Path,           # Required: file or directory to document
  'type': str,            # Optional: 'public' | 'all' | 'tests'
  'output_dir': Path,     # Optional: default 'supekku/docs/deterministic'
  'check': bool,          # Optional: check mode flag
  'verbose': bool,        # Optional: show hashes in output
  'no_cache': bool,       # Optional: disable parse cache
  'cache_dir': Path,      # Optional: custom cache location
  'cache_stats': bool,    # Optional: show cache statistics
}
```

**Library API Contract** (`generate_docs()`):
```python
generate_docs(
  unit: Path,                # File or directory to process
  variants: list[VariantSpec],  # Documentation variants to generate
  check: bool,               # Check mode flag
  output_root: Path,         # Output directory
  cache_dir: Path | None,    # Cache directory or None
  base_path: Path | None,    # Base path for relative resolution
) -> list[DocResult]
```

**DocResult Model** (from library):
```python
DocResult(
  path: Path,        # Output file path
  status: str,       # 'created' | 'changed' | 'unchanged' | 'error'
  hash: str,         # Content hash for comparison
  error_message: str | None,  # Error details if status='error'
  success: bool,     # Overall success flag
)
```

### Interfaces

**Public CLI Interface** (both scripts):
```bash
# Basic usage
<script> <path> [--type {public|all|tests}] [--output-dir DIR]

# Check mode
<script> <path> --check

# Caching control
<script> <path> --no-cache
<script> <path> --cache-dir <dir> --cache-stats

# Output control
deterministic_ast_doc_generator.py <path> --verbose
```

**Exit Codes**:
- `0`: Success (or check mode with all docs up-to-date)
- `1`: Failure (errors, invalid input, or check mode with stale docs)

## 5. Behaviour & Scenarios

### Primary Flow: Generate Documentation

1. **Given** a Python package path `/home/user/myproject/src`
2. **When** user runs `ast_doc_generator.py /home/user/myproject/src --type public`
3. **Then** the system:
   - Parses arguments and validates path exists
   - Creates VariantSpec for "public" variant
   - Calls `generate_docs()` with appropriate parameters
   - Receives list of DocResult objects
   - Formats results with status symbols
   - Prints summary statistics
   - Exits with code 0 (success) or 1 (errors)

### Primary Flow: Check Mode Validation

1. **Given** existing documentation in `supekku/docs/deterministic/`
2. **When** user runs `deterministic_ast_doc_generator.py src --check`
3. **Then** the system:
   - Parses arguments with check flag enabled
   - Calls `generate_docs()` with `check=True`
   - Receives DocResult objects with status comparisons
   - Formats with check-mode symbols (✓ unchanged, ✗ changed/missing)
   - Prints summary showing N/M files unchanged
   - Exits 0 if all unchanged, 1 if any changed/missing

### Error Handling / Guards

**Invalid Path**:
- Guard: Check `path.exists()` before calling library
- Response: Print "Error: <path> does not exist", exit 1

**Permission Error**:
- Guard: Catch `PermissionError` from library
- Response: Print error message, exit 1

**Invalid Variant Type**:
- Guard: Argument parser choices constraint
- Response: argparse prints usage, exit 2 (argparse convention)

**Library API Error**:
- Guard: Catch generic `Exception` from `generate_docs()`
- Response: Print "Error generating documentation: <message>", exit 1

### State Transitions

CLI scripts are stateless - each invocation is independent:
```
START → Parse Args → Validate Inputs → Call Library → Format Results → EXIT
```

No persistent state between invocations. All state management delegated to library (cache, file I/O).

## 6. Quality & Verification

### Testing Strategy

**Unit Tests** (VT-001 through VT-007):
- Test argument parser with valid/invalid inputs
- Test variant type mapping to VariantSpec
- Test error handling paths (missing path, permission errors)
- Test check mode comparison logic
- Test status symbol selection for all status types
- Test summary statistics calculation
- Test backward compatibility helpers

**Integration Tests**:
- End-to-end CLI invocation with real library
- Test full workflow: args → library → formatting → output
- Verify exit codes match expected values

**Performance Tests** (VA-001):
- Benchmark typical package (≤100 files) generation time
- Target: ≤5 seconds wall time
- Environment: Modern hardware (4-core, SSD)

**Manual Tests** (VH-001):
- Run existing automation scripts without modification
- Verify all original arguments still work
- Confirm output format unchanged

### Observability & Analysis

**Output Logging**:
- Status for each file processed
- Summary statistics at completion
- Error messages for failures

**Cache Statistics** (optional):
- Hit/miss counts via `--cache-stats`
- Invalidation tracking
- Hit rate percentage

**Exit Codes**:
- Track success/failure rates in CI/CD metrics
- Alert on unexpected exit code patterns

### Security & Compliance

**Input Validation**:
- Path existence check before processing
- argparse validates argument types and choices
- No shell injection risk (uses library API, not subprocess)

**File System Access**:
- Reads Python source files (read-only)
- Writes documentation files (controlled by `--output-dir`)
- No arbitrary file access beyond specified paths

**No Authentication/Authorization**:
- CLI tools run with invoking user's permissions
- Rely on OS-level file permissions for access control

### Verification Coverage

All requirements mapped to verification artifacts (see `supekku:verification.coverage@v1` YAML block).

**Coverage Summary**:
- 7 functional requirements → 7 unit tests (VT-001 to VT-007)
- 2 non-functional requirements → 1 performance test (VA-001) + 1 manual test (VH-001)

### Acceptance Gates

**For Release**:
- [ ] All unit tests passing (VT-001 to VT-007)
- [ ] Performance benchmark meets ≤5s target (VA-001)
- [ ] Backward compatibility verified with existing scripts (VH-001)
- [ ] Both linters passing (`ruff`, `pylint`)
- [ ] Check mode correctly detects stale documentation

## 7. Backlog Hooks & Dependencies

### Related Specs / PROD

- **SPEC-113** (supekku.scripts.lib.docs.python): Library API providing AST parsing and doc generation logic
  - Dependency: CLI depends on library API contract
  - Interaction: CLI delegates all complex logic to library

[ASSUMPTION: SPEC-113 exists for the library package based on package structure. If spec number differs, update relationship.]

### Risks & Mitigations

**RISK-001: Library API Changes Break CLI**
- Likelihood: Medium
- Impact: High
- Mitigation: Maintain integration tests covering full CLI workflow; version library API

**RISK-002: Backward Compatibility Violations**
- Likelihood: Low
- Impact: High
- Mitigation: Explicit backward compatibility tests; manual verification with existing scripts

**RISK-003: Performance Degradation**
- Likelihood: Low
- Impact: Medium
- Mitigation: Performance benchmarks in test suite; cache optimization in library

### Known Gaps / Debt

None currently identified. CLI package is mature with stable interface.

### Open Decisions / Questions

None. Implementation is complete and stable.

## Appendices (Optional)

### Comparison: ast_doc_generator vs deterministic_ast_doc_generator

Both scripts provide similar functionality with slight implementation differences:

**ast_doc_generator.py**:
- Simpler result handling
- Focused on core workflow
- Minimal output formatting

**deterministic_ast_doc_generator.py**:
- More detailed result formatting
- Verbose mode with hash display
- Backward compatibility helpers for tests
- Cache statistics support

[ASSUMPTION: deterministic_ast_doc_generator.py is the preferred/newer implementation based on more complete feature set. Consider deprecating ast_doc_generator.py if redundant.]
