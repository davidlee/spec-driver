---
id: PROD-012
slug: code-contract-documentation
name: Code Contract Documentation
created: '2025-11-10'
updated: '2025-11-10'
status: draft
kind: prod
aliases: [docgen, sync]
relations: []
guiding_principles:
  - Support both agent and human developer ergonomics as equal citizens
  - Support both legacy and greenfield development
  - Make it easy to identify code changes not covered by specs
  - Support incremental convergence toward accuracy, completeness & currency
  - Be unsurprising
  - Format as compact and minimal as possible without compromising legibility
  - Use existing tools where suitable, otherwise build using AST
  - Make it easy to traverse between code & generated docs
  - Aim for consistency between languages except where it harms utility
  - Don't require configuration to obtain useful results
assumptions:
  - Teams value evergreen, verifiable technical documentation
  - Code documentation must stay synchronized with implementation
  - Agents and humans have different but equally valid documentation needs
  - Deterministic output enables reliable change detection
---

# PROD-012 – code-contract-documentation

```yaml supekku:spec.relationships@v1
schema: supekku.spec.relationships
version: 1
spec: PROD-012
requirements:
  primary:
    - PROD-012.FR-001
    - PROD-012.FR-002
    - PROD-012.FR-003
    - PROD-012.FR-004
    - PROD-012.FR-005
    - PROD-012.FR-006
    - PROD-012.FR-007
    - PROD-012.FR-008
    - PROD-012.FR-009
    - PROD-012.FR-010
    - PROD-012.FR-011
    - PROD-012.FR-012
    - PROD-012.FR-013
    - PROD-012.FR-014
    - PROD-012.FR-015
    - PROD-012.FR-016
    - PROD-012.FR-017
    - PROD-012.FR-018
    - PROD-012.NF-001
    - PROD-012.NF-002
    - PROD-012.NF-003
    - PROD-012.NF-004
    - PROD-012.NF-005
  collaborators: []
interactions: []
```

```yaml supekku:spec.capabilities@v1
schema: supekku.spec.capabilities
version: 1
spec: PROD-012
capabilities:
  - id: deterministic-contract-generation
    name: Deterministic Contract Generation
    responsibilities:
      - Generate API documentation from source code using AST parsing
      - Support Go, Python, and TypeScript languages
      - Preserve comments, type information, and function signatures
      - Produce identical output for identical input (idempotent)
    requirements: [PROD-012.FR-001, PROD-012.FR-002, PROD-012.FR-003, PROD-012.FR-004, PROD-012.NF-001, PROD-012.NF-002]
    summary: >-
      System extracts public and private API contracts from code in multiple languages,
      generating deterministic markdown documentation that preserves all type information,
      comments, and signatures without requiring special annotations.
    success_criteria:
      - Identical code produces byte-identical contract documentation
      - All public interfaces captured with complete type signatures
      - Function reordering does not change output
      - Comments preserved at package, function, and inline levels

  - id: spec-synchronization
    name: Spec-Code Synchronization
    responsibilities:
      - Auto-generate tech spec stubs for uncovered code
      - Store contracts within tech spec bundles
      - Detect and report code changes not covered by specs
      - Support --check mode and --prune operations
      - Track git SHA of last sync to enable drift detection
      - Support recording git SHA when spec reviewed and verified accurate
    requirements: [PROD-012.FR-005, PROD-012.FR-006, PROD-012.FR-007, PROD-012.FR-008, PROD-012.FR-013, PROD-012.FR-014]
    summary: >-
      System maintains bidirectional links between code and specifications by
      auto-stubbing specs for uncovered code and organizing contracts within
      tech spec bundles, making coverage gaps immediately visible. Git SHA
      tracking enables precise detection of code drift: last_sync shows when
      contracts were generated, last_review shows when spec was verified accurate,
      enabling diff between them to show exactly what needs to be accounted for.
    success_criteria:
      - All code mapped to exactly one tech spec
      - Stub specs created only for code lacking coverage
      - Manual specs never deleted by --prune
      - Coverage gaps reported accurately in --check mode
      - Git SHA recorded in spec frontmatter on every sync (last_sync)
      - Review workflow updates last_review SHA with validation

  - id: multi-view-navigation
    name: Multi-View Navigation & Organization
    responsibilities:
      - Organize contracts by language, package, and spec
      - Provide symlink trees for multiple access patterns
      - Enable filtering by visibility (public/private/test)
      - Support CLI tooling ergonomics (ripgrep, fzf, etc)
      - Ensure 1:1 mapping between code and specs (exactly one spec per code unit)
      - Provide bidirectional navigation tooling (code↔spec lookup)
      - Enable easy directory navigation between code and specs
    requirements: [PROD-012.FR-009, PROD-012.FR-010, PROD-012.FR-015, PROD-012.FR-016, PROD-012.FR-017, PROD-012.FR-018, PROD-012.NF-003]
    summary: >-
      System provides multiple organizational views of contracts through symlink
      trees and filtering, optimized for both human browsing and CLI tool usage.
      Clean 1:1 code-to-spec mapping ensures every piece of code has exactly one
      home, while bidirectional navigation tooling and intuitive symlink structures
      make it effortless to move between code and documentation.
    success_criteria:
      - Contracts accessible by-spec, by-language, and by-package
      - Public/private/test contracts separable
      - ripgrep/fzf/bfs operations complete in <2s for typical repos
      - Symlink structures intuitive for first-time users
      - Every code file maps to exactly one spec (no ambiguity)
      - Bidirectional navigation commands fast and reliable (<100ms)
      - Directory switching between code and specs feels natural

  - id: incremental-adoption
    name: Incremental Adoption Support
    responsibilities:
      - Work with legacy codebases without special annotations
      - Support both greenfield and existing projects
      - Require no configuration for useful results
      - Enable gradual spec coverage improvement
    requirements: [PROD-012.FR-011, PROD-012.FR-012, PROD-012.NF-004, PROD-012.NF-005]
    summary: >-
      System works immediately with existing code in any state of documentation,
      requiring zero configuration or code changes, allowing teams to incrementally
      improve spec coverage without blocking current development.
    success_criteria:
      - Generates useful contracts from undocumented legacy code
      - Works without JSDoc, docstrings, or special comments
      - Zero-config operation produces meaningful output
      - Coverage can improve incrementally without full commitment
```

```yaml supekku:verification.coverage@v1
schema: supekku.verification.coverage
version: 1
subject: PROD-012
entries:
  - artefact: VT-001
    kind: VT
    requirement: PROD-012.FR-001
    status: planned
    notes: Multi-language contract generation test suite
  - artefact: VT-002
    kind: VT
    requirement: PROD-012.NF-001
    status: planned
    notes: Deterministic output verification tests
  - artefact: VA-001
    kind: VA
    requirement: PROD-012.NF-003
    status: planned
    notes: CLI tool performance benchmarks
```

## 1. Intent & Summary

- **Problem / Purpose**: Technical specifications become stale the moment they're written, creating a persistent tension between documentation currency and development velocity. Teams face a choice: invest heavily in manual synchronization (slowing development), accept documentation drift (losing spec value), or skip documentation entirely (losing architectural context for both humans and AI agents). This creates blind spots during code review, onboarding friction, and wasted agent research cycles.

- **Value Signals**:
  - **Research Efficiency**: Reduce agent/human code investigation time by 60%+ through high-level contract access
  - **Spec Currency**: Eliminate manual sync burden; contracts stay current automatically
  - **Coverage Visibility**: Surface coverage gaps immediately via `sync --check` in CI
  - **Agent Effectiveness**: Provide verifiable API contracts immune to hallucination
  - **Incremental ROI**: Teams see value from day one without requiring full adoption commitment

- **Guiding Principles**:
  - Agent and human ergonomics are equal priorities, not competing concerns
  - Legacy codebases are first-class citizens; no annotations/conventions required
  - Determinism enables reliable change detection and diff-based workflows
  - Compactness without sacrificing legibility maximizes research efficiency
  - CLI tool compatibility (ripgrep, fzf, bfs) is a hard requirement, not a nice-to-have
  - Zero-config operation; configuration enables optimization, not basic function
  - Incremental convergence beats big-bang adoption; support gradual improvement

- **Change History**: Initial specification from scratch/docgen.md consolidation.

## 2. Stakeholders & Journeys

### Personas / Actors

**AI Code Agent**
- **Goals**: Rapidly understand API contracts, verify interface compatibility, avoid hallucinating signatures
- **Pains**: Reading full source files wastes tokens; comments/docs often outdated; type info scattered
- **Expectations**: Deterministic, verifiable contracts; fast ripgrep lookups; type signatures always accurate

**Human Developer (New to Codebase)**
- **Goals**: Understand architecture quickly; identify which modules to read; verify interface assumptions
- **Pains**: Reading implementation when only interface matters; docs out of sync; unclear what's public vs internal
- **Expectations**: High-level overview before diving deep; clear visibility markers; fast navigation

**Tech Lead / Architect**
- **Goals**: Maintain spec coverage; catch architecture drift; ensure docs stay current in CI
- **Pains**: Manual doc updates block PRs; coverage gaps invisible until too late; spec rot inevitable
- **Expectations**: Zero-maintenance sync; coverage reports in CI; non-intrusive on dev workflow

**Library Consumer**
- **Goals**: Understand public API contracts; see type signatures and constraints; avoid private internals
- **Pains**: Public vs private unclear; types missing or incomplete; interface stability unknown
- **Expectations**: Clear public API docs; complete type information; stable contracts across versions

### Primary Journeys / Flows

**Journey 1: Agent API Discovery**
```
GIVEN agent needs to find all Registry implementations
WHEN searches contracts: `rg 'Registry' specify/**/contracts/**public.md -ln`
THEN receives list of relevant contract files in <200ms
AND can read high-level signatures without loading full source
AND type information is complete and accurate
```

**Journey 2: Initial Codebase Adoption**
```
GIVEN legacy Python/TS/Go repository with no existing documentation
WHEN developer runs `spec-driver sync` first time
THEN system generates contracts for all code without errors
AND creates stub specs for uncovered packages
AND organizes contracts under specify/tech/*/contracts/
AND provides by-language, by-package symlink views
AND developer can immediately ripgrep/browse contracts
```

**Journey 3: Incremental Spec Coverage**
```
GIVEN team wants to gradually improve spec coverage
WHEN runs `spec-driver sync --check` in CI
THEN receives report of code not covered by manual specs
AND team creates proper specs incrementally for priority areas
AND `sync --prune` removes stubs only when manual specs exist
AND coverage improves without blocking current development
```

**Journey 4: Detecting Stale Specs**
```
GIVEN developer modifies public API in module Foo
WHEN CI runs `spec-driver sync --check`
THEN detects contracts changed for SPEC-042
AND flags spec as potentially stale
AND developer updates SPEC-042 narrative alongside code
AND contracts regenerate deterministically
```

### Edge Cases & Non-goals

**Deliberately Excluded:**
- **Full narrative documentation generation**: Contracts capture signatures/types only, not "why" or design rationale
- **Annotation-based docs**: Must work without JSDoc, docstrings, or special comments (though we preserve them)
- **Submodule support**: Deferred; single-repo focus initially
- **Custom output formats**: Markdown only; parseable by standard tools
- **Configuration-required operation**: Advanced filtering OK, but basic function must work zero-config
- **Diff/changelog generation**: Tools should detect changes, but narrative diffs out of scope

**Guard Rails:**
- **Monorepo complexity**: TypeScript workspaces supported but may require manual scope hints
- **Dynamic language limitations**: Python type hints optional; contracts show what's extractable from AST
- **Circular references**: Handle gracefully; no infinite recursion in type resolution
- **Binary/generated files**: Skip with clear warnings; don't attempt to parse

## 3. Responsibilities & Requirements

### Capability Overview

See `supekku:spec.capabilities@v1` block above for detailed capability definitions. The four core capabilities work together:

1. **Deterministic Contract Generation** extracts API contracts from code
2. **Spec-Code Synchronization** maintains bidirectional links and coverage visibility
3. **Multi-View Navigation** enables efficient discovery and comparison
4. **Incremental Adoption** supports gradual improvement without blocking current work

### Functional Requirements

- **FR-001**: System MUST generate API contract documentation from Go, Python, and TypeScript source code using AST parsing
  *Verification*: VT-001 - Multi-language contract generation test suite

- **FR-002**: System MUST preserve all comments (package-level, function-level, inline) in generated contracts
  *Verification*: VT-001 - Comment preservation tests

- **FR-003**: System MUST extract and represent complete type information including function signatures, interfaces, type parameters, and optionality markers
  *Verification*: VT-001 - Type information completeness tests

- **FR-004**: System MUST distinguish and separately document public vs private vs test interfaces
  *Verification*: VT-001 - Visibility filtering tests

- **FR-005**: System MUST auto-generate stub tech specs for code not covered by existing specs when running `sync` command
  *Verification*: VT-003 - Stub generation tests

- **FR-006**: System MUST store generated contracts in `specify/tech/SPEC-nnn/contracts/` directory within the corresponding tech spec bundle
  *Verification*: VT-003 - Contract organization tests

- **FR-007**: System MUST provide `--check` mode that reports code requiring spec coverage without modifying files
  *Verification*: VT-004 - Check mode validation tests

- **FR-008**: System MUST provide `--prune` flag that removes stub specs only when manual specs exist covering same code
  *Verification*: VT-004 - Prune operation safety tests

- **FR-009**: System MUST create symlink trees organizing contracts by-language and by-package under `specify/tech/by-**/` directories
  *Verification*: VT-005 - Symlink structure tests

- **FR-010**: System MUST support filtering contract output by visibility level (public/private/test)
  *Verification*: VT-005 - Visibility filter tests

- **FR-011**: System MUST generate useful contracts from code without JSDoc, docstrings, type hints, or special annotations
  *Verification*: VT-006 - Legacy code parsing tests

- **FR-012**: System MUST operate with zero configuration to produce meaningful contracts
  *Verification*: VT-006 - Zero-config operation tests

- **FR-013**: System MUST record git SHA of last sync operation in tech spec frontmatter (`git_shas.last_sync`) to enable drift detection
  *Verification*: VT-007 - Git SHA tracking tests
  *Related*: ISSUE-020

- **FR-014**: System MUST support recording git SHA when spec is reviewed and verified as accurate (`git_shas.last_review`), enabling calculation of what code changes need to be accounted for
  *Verification*: VT-007 - Git SHA tracking tests
  *Related*: ISSUE-020
  *Note*: This is the primary mechanism for knowing "what's drifted since spec was last accurate"

- **FR-015**: System MUST map code to specs such that each piece of code belongs to exactly one spec, with spec scope being cohesive and right-sized for the language
  *Verification*: VT-008 - Scope mapping tests
  *Note*: Ensures 1:1 mapping prevents ambiguity and coverage gaps

- **FR-016**: Symlink tree structures (`by-language/` and `by-package/`) MUST be intuitive, easy to navigate, and follow unsurprising conventions matching developer mental models
  *Verification*: VH-002 - Navigation usability testing

- **FR-017**: System MUST provide tooling to find corresponding spec from code file and vice-versa (bidirectional navigation)
  *Verification*: VT-009 - Bidirectional navigation tests
  *Example*: `spec-driver find-spec src/auth/login.ts` → `SPEC-042`; `spec-driver find-code SPEC-042` → list of source files

- **FR-018**: System MUST provide tooling to navigate between code directories and spec directories
  *Verification*: VT-009 - Navigation tooling tests
  *Example*: `spec-driver cd-spec` from code directory; `spec-driver cd-code SPEC-042` from anywhere

### Non-Functional Requirements

- **NF-001**: Generated contracts MUST be deterministic: identical source code MUST produce byte-identical contract output
  *Measurement*: VT-002 - Deterministic output verification tests (hash comparison across runs)

- **NF-002**: Contract generation MUST be idempotent: running `sync` multiple times on unchanged code MUST produce no file modifications
  *Measurement*: VT-002 - Idempotency verification tests (mtime/checksum stability)

- **NF-003**: Contract search via ripgrep MUST complete in <2 seconds for typical repositories (up to 100K LOC, 1000 files)
  *Measurement*: VA-001 - CLI tool performance benchmarks

- **NF-004**: System MUST support legacy codebases without requiring code changes, annotations, or special formatting
  *Measurement*: VT-006 - Legacy compatibility test suite

- **NF-005**: Contract format MUST be compact and legible: maximize information density while maintaining human readability
  *Measurement*: VH-001 - Human readability review across sample contracts
### Success Metrics / Signals

- **Adoption**: 70% of developers using contracts for API research within 30 days of deployment
  *Measure*: Contract file access logs, ripgrep usage telemetry

- **Efficiency**: 60% reduction in mean time for agents/humans to answer "what's the signature of X?" questions
  *Measure*: Pre/post timing studies on common research tasks

- **Coverage**: 90% of production code mapped to tech specs within 90 days
  *Measure*: `sync --check` coverage reports tracked over time

- **Quality**: <1% contract generation failures on supported languages
  *Measure*: Error rate from sync operations across diverse repos

- **Currency**: Zero manual sync effort; 100% of contract updates automated
  *Measure*: Time spent on documentation sync drops to zero

## 4. Solution Outline

### User Experience / Outcomes

**Command-Line Interface:**
```bash
# Primary operation: generate/update all contracts
spec-driver sync

# Check coverage without modifying files (ideal for CI)
spec-driver sync --check

# Remove stub specs when manual specs exist
spec-driver sync --prune

# View contracts organized by language
ls specify/tech/by-language/python/
ls specify/tech/by-language/typescript/

# View contracts organized by package
ls specify/tech/by-package/supekku/scripts/lib/
```

**Developer Workflow:**
1. Run `sync` on first adoption → contracts generated, stub specs created
2. Browse contracts via filesystem or ripgrep to understand architecture
3. Gradually convert stubs to proper specs for priority modules
4. Run `sync --check` in CI to catch coverage gaps
5. Contracts regenerate automatically on every sync; always current

**Agent Workflow:**
1. Search contracts via ripgrep instead of reading full source
2. Verify signatures/types from deterministic, verifiable contracts
3. Use by-language or by-package views for systematic exploration
4. Fall back to source only when implementation details needed

### Data & Contracts

**Tech Spec Bundle Structure:**
```
specify/tech/SPEC-042-authentication/
├── SPEC-042.md                    # Manual narrative spec
├── SPEC-042.tests.md              # Testing companion
└── contracts/
    ├── auth-service.public.md     # Public API contracts
    ├── auth-service.private.md    # Internal implementation contracts
    └── auth-service.test.md       # Test helper contracts
```

**Symlink Organization:**
```
specify/tech/by-language/
├── python/
│   └── supekku/scripts/lib/decisions/ -> ../../../../SPEC-*/contracts/*.md
├── typescript/
│   └── src/components/ -> ../../../../SPEC-*/contracts/*.md
└── go/
    └── pkg/registry/ -> ../../../../SPEC-*/contracts/*.md

specify/tech/by-package/
└── supekku/scripts/lib/
    ├── decisions/ -> ../../../../SPEC-*/contracts/*.md
    └── changes/ -> ../../../../SPEC-*/contracts/*.md
```

**Contract Format (Example):**
```markdown
# Package: supekku.scripts.lib.decisions

Source: `supekku/scripts/lib/decisions/registry.py`

## Classes

### DecisionRegistry

Registry for managing ADR lifecycle and metadata.

#### `__init__(self, root: Path) -> None`

Initialize registry with workspace root.

#### `all_decisions(self) -> list[Decision]`

Return all decisions from registry, sorted by ID.

#### `find_by_id(self, decision_id: str) -> Decision | None`

Find decision by ID. Returns None if not found.
```

## 5. Behaviour & Scenarios

### Primary Flows

**Flow 1: Sync Operation (FR-001, FR-002, FR-003, FR-005, FR-006)**
1. User runs `spec-driver sync`
2. System discovers code roots (Go modules, Python packages, TS package.json)
3. For each language, parse AST and extract public/private interfaces
4. Generate contract markdown preserving comments and types
5. Map code to existing tech specs via metadata or create stubs
6. Write contracts to `specify/tech/SPEC-*/contracts/*.md`
7. Generate symlink trees under `by-language/` and `by-package/`
8. Report summary: specs created/updated, contracts generated

**Flow 2: Coverage Check (FR-007)**
1. User runs `spec-driver sync --check` in CI
2. System performs sync analysis without writing files
3. Reports code that would generate stub specs (coverage gaps)
4. Reports contract changes that would occur (potential staleness)
5. Exits with non-zero status if coverage below threshold (configurable)

**Flow 3: Stub Pruning (FR-008)**
1. User runs `spec-driver sync --prune`
2. System identifies stub specs (minimal frontmatter, auto-generated marker)
3. For each stub, checks if manual spec exists covering same scope
4. Removes stub only if manual spec provides coverage
5. Never removes manually-created specs (safety check on metadata)

**Flow 4: Contract Discovery (FR-009, FR-010)**
1. Agent needs to find all Registry implementations
2. Runs `rg 'class.*Registry' specify/**/contracts/**public.md -l`
3. Reviews list of contract files matching pattern
4. Reads relevant contracts to compare signatures
5. Filters to public-only contracts to avoid internal details

**Flow 5: Spec Review and Accuracy Verification (FR-013, FR-014)**
1. Developer needs to update SPEC-042 to account for recent code changes
2. Reads SPEC-042 frontmatter:
   ```yaml
   git_shas:
     last_review: abc123  # When spec was last verified accurate
     last_sync: def456    # When contracts were last generated
   ```
3. Runs `git diff abc123 def456 -- specify/tech/SPEC-042/contracts/` to see what changed since last review
4. Diff shows: `authenticate(user)` became `authenticate(user, options)` and 3 other signature changes
5. Developer updates SPEC-042 narrative to account for all 4 changes
6. Developer marks spec as reviewed: `spec-driver review SPEC-042` (updates `last_review` to current HEAD)
7. Next developer can diff `last_review` to `last_sync` (or HEAD) to see what needs accounting

**Flow 6: Calculating Drift on Stale Spec (FR-014)**
1. Agent opens SPEC-089 and sees:
   ```yaml
   git_shas:
     last_review: old123  # 6 months ago
     last_sync: new789    # Today
   ```
2. Agent runs `git diff old123 new789 -- specify/tech/SPEC-089/contracts/`
3. Diff shows 47 changed lines across 12 files - significant drift
4. Agent reports to user: "SPEC-089 has significant unaccounted drift; last reviewed 6 months ago"
5. User prioritizes SPEC-089 update based on drift magnitude

**Flow 7: Bidirectional Code-Spec Navigation (FR-017, FR-018)**
1. Developer working in `src/auth/providers/oauth.ts`, wants to read spec
2. Runs `spec-driver find-spec src/auth/providers/oauth.ts`
3. Output: `SPEC-042 (Authentication System)`
4. Runs `spec-driver cd-spec` → navigates to `specify/tech/SPEC-042/`
5. Reads SPEC-042.md, sees contracts in `contracts/` subdirectory
6. Runs `spec-driver cd-code SPEC-042` → navigates back to code root for SPEC-042
7. Developer can also use symlinks: `ls specify/tech/by-language/typescript/src/auth/`

**Flow 8: Finding All Code for a Spec (FR-017)**
1. Agent needs to understand what code SPEC-089 covers
2. Runs `spec-driver find-code SPEC-089`
3. Output lists all source files:
   ```
   supekku/scripts/lib/formatters/decision_formatters.py
   supekku/scripts/lib/formatters/change_formatters.py
   supekku/scripts/lib/formatters/spec_formatters.py
   ```
4. Agent can now read source files knowing complete scope
5. Or use contracts: `ls specify/tech/SPEC-089/contracts/` for high-level view

**Flow 9: Symlink Navigation (FR-016)**
1. Developer wants to see all Python formatting code
2. Navigates to `specify/tech/by-language/python/`
3. Sees directory structure mirroring source: `supekku/scripts/lib/formatters/`
4. Each contract symlinks back to canonical location in spec bundle
5. Structure feels natural: same paths as in source code
6. Developer can use standard tools: `bfs`, `tree`, `fzf`

### Error Handling / Guards

**Parse Failures:**
- WHEN AST parsing fails on file X
- THEN log warning with file path and parse error
- AND skip file, continue processing remaining files
- AND include parse failure in summary report

**Circular Type References:**
- WHEN type resolution encounters circular dependency
- THEN detect cycle via visited-node tracking
- AND emit type as string name without full expansion
- AND continue processing without recursion

**Missing Package Metadata:**
- WHEN cannot determine package/module for file
- THEN use file path as fallback scope identifier
- AND create stub spec named after directory
- AND log warning about ambiguous scope

**Manual Spec Conflicts:**
- WHEN multiple manual specs claim same code scope
- THEN halt sync operation with conflict error
- AND report conflicting specs and overlapping scope
- AND require user resolution before proceeding

**Binary/Generated Files:**
- WHEN encounter non-parseable file (binary, minified, etc.)
- THEN detect via file extension or parse failure heuristics
- AND skip with debug-level log (not warning)
- AND exclude from coverage calculations

## 6. Quality & Verification

### Testing Strategy

**Unit Testing (VT-001, VT-002, VT-003):**
- Multi-language parsers tested independently against fixture codebases
- Contract generation tested for Go, Python, TypeScript with known inputs/outputs
- Determinism verified via hash comparison across multiple runs
- Idempotency verified via filesystem state comparison
- Comment preservation tested with annotated fixtures
- Type extraction tested against typed and untyped code

**Integration Testing (VT-004, VT-005):**
- End-to-end `sync` operations on real repository structures
- `--check` mode validation with coverage gap detection
- `--prune` safety tests ensuring manual specs never deleted
- Symlink tree generation and navigation tests
- Visibility filtering tests (public/private/test separation)

**Compatibility Testing (VT-006):**
- Legacy codebase parsing without annotations
- Zero-config operation on diverse repository structures
- TypeScript monorepo support (workspaces, multiple package.json)
- Python package detection across various structures
- Go module discovery and mapping

**Performance Testing (VA-001):**
- Contract generation performance on repos up to 100K LOC
- ripgrep search performance across contract collections
- Symlink creation/update performance
- Memory usage during large repository parsing

### Research / Validation

**Hypothesis H1: Contracts reduce research time**
- **Test**: Time 10 developers on "find signature of X" tasks with/without contracts
- **Success Criteria**: 60%+ time reduction with contracts
- **Status**: Planned

**Hypothesis H2: Agents prefer contracts over source**
- **Test**: Monitor agent tool usage patterns before/after contract availability
- **Success Criteria**: 70%+ shift from Read to contract search
- **Status**: Planned

**Hypothesis H3: Zero-config adoption is viable**
- **Test**: Deploy to 5 legacy repos without configuration
- **Success Criteria**: Meaningful contracts generated for 90%+ of code
- **Status**: Planned

### Observability & Analysis

**Key Metrics:**
- Contract generation success rate (target: >99%)
- Parse failure rate by language
- Sync operation duration (target: <10s for typical repos)
- Contract file size distribution
- Symlink tree size and depth
- Coverage percentage over time

**Telemetry (optional, privacy-respecting):**
- Anonymous usage patterns (which flags most used)
- Parse failure patterns (which constructs cause issues)
- Performance data (repo size vs sync duration)

### Security & Compliance

**Data Handling:**
- Contracts generated from source code already in repository
- No external network access required for generation
- No telemetry without explicit opt-in
- Generated files stored locally only

**Privacy:**
- Contract content derived from code developer already has access to
- No personal information captured in contracts
- Symlinks reference only local filesystem

**Access Control:**
- Contracts inherit access controls from source repository
- No separate authentication/authorization layer needed
- Visibility filtering (public/private) based on language semantics, not security boundaries

### Verification Coverage

See `supekku:verification.coverage@v1` YAML block for detailed mapping of verification artifacts to requirements.

**Coverage Summary:**
- FR-001 through FR-012: Covered by VT-001 through VT-006
- NF-001, NF-002: Covered by VT-002 (determinism/idempotency)
- NF-003: Covered by VA-001 (performance benchmarks)
- NF-004: Covered by VT-006 (legacy compatibility)
- NF-005: Covered by VH-001 (human readability review)

### Acceptance Gates

**Minimum Viable Product (MVP):**
- [ ] FR-001 through FR-012 verified via VT suite
- [ ] NF-001, NF-002 verified (determinism + idempotency)
- [ ] Python and TypeScript support functional (Go deferred to v2)
- [ ] Symlink navigation works on Linux/macOS
- [ ] Documentation includes usage examples and troubleshooting
- [ ] Performance acceptable for repos up to 10K LOC

**Production Readiness:**
- [ ] All MVP criteria met
- [ ] NF-003 verified (performance <2s for typical repos)
- [ ] VT-006 compatibility suite passes on 10+ diverse repos
- [ ] VH-001 readability review complete with positive feedback
- [ ] CI integration tested and documented
- [ ] Known limitations clearly documented

## 7. Backlog Hooks & Dependencies

### Related Specs / PROD

**Future Tech Specs (to be created):**
- **SPEC-TBD: Python AST Parser**: Implementation details for Python contract extraction
- **SPEC-TBD: TypeScript AST Parser**: Implementation details for TS/JS contract extraction
- **SPEC-TBD: Go AST Parser**: Implementation details for Go contract extraction (v2)
- **SPEC-TBD: Spec Registry**: Tech spec discovery, metadata parsing, scope resolution
- **SPEC-TBD: Symlink Tree Generator**: Multi-view organization and navigation

**Collaborates With:**
- Tech spec system (reads metadata to map code to specs)
- Validation framework (can run `sync --check` in validation pipeline)
- CLI framework (provides `sync` subcommand)

### Risks & Mitigations

**R1: TypeScript Module Resolution Complexity**
- **Description**: TS has ~11 package managers, multiple module systems, complex monorepo setups
- **Likelihood**: High | **Impact**: High
- **Mitigation**: Start with simple case (single package.json), add heuristics iteratively; document limitations clearly; allow manual scope hints via config

**R2: Python Type Brittleness**
- **Description**: Optional typing means contracts may show `<BinOp>` or incomplete types
- **Likelihood**: Medium | **Impact**: Medium
- **Mitigation**: Extract what AST provides; document that Python contracts best-effort; recommend type hints for critical APIs

**R3: Determinism Failures from Language Evolution**
- **Description**: New language features may parse differently across parser versions
- **Likelihood**: Low | **Impact**: Medium
- **Mitigation**: Pin parser versions; version contract format; detect and warn on parser changes

**R4: Performance Degradation on Large Repos**
- **Description**: Repos >100K LOC may exceed performance targets
- **Likelihood**: Medium | **Impact**: Medium
- **Mitigation**: Implement incremental parsing (only changed files); add caching layer; profile and optimize hot paths

**R5: Symlink Compatibility (Windows)**
- **Description**: Windows symlink support requires admin privileges or developer mode
- **Likelihood**: Medium | **Impact**: Low
- **Mitigation**: Detect OS; fall back to file copies on Windows; document requirement; consider junction points

**R6: Scope Conflict Ambiguity**
- **Description**: Multiple specs claiming same code scope may not be detectable without clear metadata
- **Likelihood**: Medium | **Impact**: High
- **Mitigation**: Require explicit scope in spec metadata; validate non-overlapping during sync; halt with clear error on conflict

### Known Gaps / Debt

**Current Implementation Status:**
- Python adapter exists, may need refactoring for determinism
- TypeScript adapter exists but has known issues (see DE-019)
- Go adapter not yet implemented
- Symlink trees not yet implemented
- `--check` and `--prune` flags not yet implemented

**Backlog Items (existing):**
- `ISSUE-020`: Add git SHA tracking to artifact frontmatter (FR-013 dependency)

**Backlog Items (to be created):**
- `ISSUE-TBD`: TypeScript dependency handling failures (see DE-019)
- `ISSUE-TBD`: Symlink tree generation missing
- `ISSUE-TBD`: Contract format not yet standardized
- `ISSUE-TBD`: Determinism not verified across parser versions
- `PROB-TBD`: Manual spec scope metadata often missing
- `PROB-TBD`: Coverage gap detection not integrated with CI

### Open Decisions / Questions

**Q1: Contract File Naming Convention**
- **Question**: Should contracts be `<source-file>.public.md` or `<package>.public.md`?
- **Context**: File-based naming creates clutter with 3 variants (public/private/test); package-based more compact
- **Options**: File-based (matches source 1:1), Package-based (groups by module), Hybrid (configurable)
- **Status**: Needs decision based on real-world usage patterns

**Q2: TypeScript Project Root Detection**
- **Question**: How to reliably detect TS project boundaries in monorepos?
- **Context**: Multiple package.json files, workspaces, nested projects
- **Options**: Nearest package.json, workspace root, explicit config, heuristics
- **Status**: Prototype heuristics needed; see DE-019

**Q3: Public vs Private Determination**
- **Question**: How to classify visibility consistently across languages with different conventions?
- **Context**: Python: `_private` convention; TS: no enforced privacy; Go: capitalization
- **Options**: Language-specific rules, explicit annotations, conservative (all public unless proven private)
- **Status**: Start with language-specific rules, iterate based on feedback

**Q4: Contract Format Versioning**
- **Question**: Should contracts include format version metadata to support evolution?
- **Context**: As parsers improve, format may need to change
- **Options**: Version header in each file, global version per sync, no versioning
- **Status**: Recommend version header for forward compatibility

**Q5: Incremental vs Full Regeneration**
- **Question**: Should `sync` regenerate only changed files or always full regeneration?
- **Context**: Incremental faster but risks inconsistency; full regen guarantees consistency
- **Options**: Always full (safe but slow), Incremental with change detection, Hybrid with periodic full regen
- **Status**: Start with full regen; add incremental optimization if performance issues arise

**Q6: Language-Specific Scope Determination**
- **Question**: How should system determine spec scope boundaries for each language given their different module/package concepts?
- **Context**: Need 1:1 code-to-spec mapping (FR-015), but languages differ:
  - Python: packages defined by `__init__.py`, clear hierarchy
  - TypeScript: package.json defines scope, but monorepos have multiple; modules are loose
  - Go: go.mod defines module, internal packages via directory structure
- **Options**:
  1. **Language heuristics**: Python=package, TS=package.json, Go=module (simple but may not fit all repos)
  2. **Explicit metadata**: Specs declare scope via glob patterns in frontmatter (flexible but requires manual setup)
  3. **Hybrid**: Start with heuristics, allow metadata override for edge cases
  4. **Directory-based**: One spec per top-level directory (simple but may not match logical boundaries)
- **Key Constraint**: Must produce cohesive, right-sized scopes that feel natural to developers
- **Status**: Recommend hybrid approach; prototype needed
- **Related**: FR-015, Q2 (TypeScript project root detection)

**Q7: Git SHA Drift Detection Workflow**
- **Question**: How should users interact with git SHA drift detection in practice?
- **Context**: The critical comparison is `last_review` to `last_sync` (or HEAD): this shows exactly what code changes occurred since spec was last verified accurate and need to be accounted for
- **Options**:
  1. Manual workflow: User runs `git diff <last_review> <last_sync> -- specify/tech/SPEC-*/contracts/` to see changes
  2. CLI helper: `spec-driver drift SPEC-042` shows contract changes since last review with summary stats
  3. Review command: `spec-driver review SPEC-042` validates drift is acceptable, updates last_review SHA
  4. Automated staleness detection: CI flags specs where `last_review` significantly lags `last_sync`
  5. Agent integration: Agents automatically check drift before updating specs, report magnitude
- **Key Insight**: `last_review` is the anchor point; `last_sync` just keeps contracts current. The gap between them is what matters.
- **Status**: Needs design; see ISSUE-020 for git SHA tracking foundation
- **Related**: FR-013, FR-014, ISSUE-020

## Appendices

### Glossary

- **Contract**: Auto-generated API documentation extracted from source code
- **Stub Spec**: Minimal tech spec auto-created for uncovered code
- **Manual Spec**: Human-authored tech spec with full narrative and design rationale
- **Scope**: Set of source files/packages covered by a single tech spec
- **Symlink Tree**: Alternative filesystem view organizing contracts by different dimensions
- **Deterministic**: Same input always produces identical output
- **Idempotent**: Running operation multiple times has same effect as running once
- **last_sync SHA**: Git commit when contracts were last generated via `sync` command
- **last_review SHA**: Git commit when spec was last reviewed and verified as accurate (THE critical anchor point)
- **Drift**: Code changes between `last_review` and `last_sync` (or HEAD) that need to be accounted for in spec narrative
- **Unaccounted Drift**: The delta between `last_review` and current state that hasn't been incorporated into spec

### TypeScript Challenges (Detailed)

From docgen.md section 110-120:

**Module System Complexity:**
- ECMAScript modules (`.mjs`) vs CommonJS
- Multiple module resolution strategies (node, bundler, etc.)
- ~11 different package managers (npm, yarn, pnpm, bun, etc.)
- Each with different workspace/monorepo conventions

**Project Root Detection:**
- Single package.json at root (simple case)
- Nested package.json files (monorepo)
- Workspaces defined in various ways (pnpm, yarn, npm)
- Git submodules (explicitly out of scope initially)

**Implications:**
- Cannot assume single project root
- Must handle multiple module resolution strategies
- May require user hints for complex setups
- Start with simple case, expand coverage iteratively
