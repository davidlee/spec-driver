---
id: PROD-014
slug: contract_mirror_tree_index
name: Contract Mirror Tree Index
created: '2026-02-20'
updated: '2026-02-20'
status: draft
kind: prod
scope: Provide a mirror-of-source view for generated contracts to improve discovery, search, and navigation.
value_proposition: Make it trivial for humans/agents to go source-path ↔ contract-artefact and ripgrep contracts using a source-mirroring tree.
aliases: []
relations: []
guiding_principles: []
assumptions: []
---

# PROD-014 – Contract Mirror Tree Index

```yaml supekku:spec.relationships@v1
schema: supekku.spec.relationships
version: 1
spec: PROD-014
requirements:
  primary:
    - PROD-014.FR-001
    - PROD-014.FR-002
    - PROD-014.FR-003
    - PROD-014.FR-004
    - PROD-014.FR-005
    - PROD-014.FR-006
    - PROD-014.FR-007
    - PROD-014.NF-001
    - PROD-014.NF-002
  collaborators: []
interactions:
  - spec: PROD-012
    type: extends
    description: Adds a mirror-of-source view for contracts to improve ergonomic discovery and search.
```

```yaml supekku:spec.capabilities@v1
schema: supekku.spec.capabilities
version: 1
spec: PROD-014
capabilities:
  - id: mirror-of-source-contracts
    name: Mirror-of-Source Contracts Index
    responsibilities:
      - Provide `.contracts/` as a canonical, repo-root entrypoint for generated contracts
      - Mirror repo-relative source paths so navigation matches developer mental models
      - Provide stable views across languages (public/internal/all/tests)
    requirements:
      - PROD-014.FR-001
      - PROD-014.FR-002
      - PROD-014.FR-003
      - PROD-014.FR-006
      - PROD-014.NF-001
      - PROD-014.NF-002
    summary: |
      Provides a deterministic filesystem index at repo root (`.contracts/`) that mirrors the
      source tree and links each source unit to its generated contract markdown artefacts.
    success_criteria:
      - Given a repo-relative source path, the corresponding `.contracts/<view>/...` entry can be opened immediately.
      - `rg` across `.contracts/**` behaves like searching the source tree, but on contract markdown.

  - id: idiom-aliases
    name: Idiom Alias Paths
    responsibilities:
      - Provide idiomatic aliases without sacrificing cross-language consistency
      - Keep aliases trivial (symlinks) and deterministic
    requirements:
      - PROD-014.FR-004
    summary: |
      Adds alias paths (e.g. `.contracts/api`) to reduce cognitive friction between language
      idioms and cross-language tooling conventions.
    success_criteria:
      - Users can choose idiom (`api/`) or canonical (`public/`) without changing the mirror content.
```

```yaml supekku:verification.coverage@v1
schema: supekku.verification.coverage
version: 1
subject: PROD-014
entries:
  - artefact: VT-CONTRACT-MIRROR-001
    kind: VT
    requirement: PROD-014.FR-001
    status: verified
    notes: "Integration tests: .contracts/ creation, variant view dirs, alias symlinks (mirror_test.py)"

  - artefact: VT-CONTRACT-MIRROR-001
    kind: VT
    requirement: PROD-014.FR-004
    status: verified
    notes: "test_rebuild_creates_aliases, test_alias_not_created_for_empty_view"

  - artefact: VT-CONTRACT-MIRROR-002
    kind: VT
    requirement: PROD-014.FR-002
    status: verified
    notes: "Integration tests: Python, Zig, Go, TS mirror symlinks resolve to correct contract artefacts"

  - artefact: VT-CONTRACT-MIRROR-002
    kind: VT
    requirement: PROD-014.FR-003
    status: verified
    notes: "Unit tests: per-language path mapping (python module, zig file, go package, ts file, zig root __root__)"

  - artefact: VT-CONTRACT-MIRROR-003
    kind: VT
    requirement: PROD-014.FR-005
    status: verified
    notes: "test_write_confinement, test_rebuild_cleans_stale, test_rebuild_removes_all_stale_views, test_rebuild_is_idempotent"

  - artefact: VT-CONTRACT-MIRROR-002
    kind: VT
    requirement: PROD-014.FR-006
    status: verified
    notes: "Builder reads only registry JSON + contract directories; no toolchain invocation. Verified by test design."

  - artefact: VT-CONTRACT-MIRROR-002
    kind: VT
    requirement: PROD-014.FR-007
    status: verified
    notes: "test_missing_variant (Zig/TS), test_conflict_resolution (deterministic SPEC ID precedence + warning)"
```

## 1. Intent & Summary
- **Problem / Purpose**: The current contract storage and symlink views make it harder than it should be to locate the right contract artefact from a source path (and vice versa), and to search contracts using a source-mirroring structure.
- **Value Signals**:
  - Humans/agents can go from a source path → contract path with zero “index knowledge”.
  - Humans/agents can `rg` contracts in a tree that mirrors the source tree.
  - The entire tree can be `.gitignore`d as generated output (diff churn isolation).
- **Guiding Principles**:
  - Mirror-of-source beats “taxonomy indices” for day-to-day discovery.
  - Deterministic + rebuildable: safe to delete and recreate at any time.
  - Language idioms first (aliases), cross-language consistency second (canonical views).
- **Change History**: Initial spec; motivated by contract discovery ergonomics and legacy codebase adoption.

## 2. Stakeholders & Journeys
- **Personas / Actors**:
  - **Developer**: wants fast, predictable navigation from code to contracts and back.
  - **Agent**: wants a deterministic corpus to search and cite to avoid hallucination.
- **Primary Journeys / Flows**:
  - **Source → Contract**: Developer has `path/to/file.ext` and wants the generated contract(s) quickly.
  - **Contract → Source**: Agent is reading a contract and wants to open the corresponding source file path.
  - **Search**: Developer runs `rg` on `.contracts/**` to discover APIs without caring where contracts are stored by spec.
- **Edge Cases & Non-goals**:
  - Do not relocate existing contract artefacts in v1.
  - Do not remove existing `specify/tech/by-*` indices in v1.
  - Do not attempt to represent “aspirational/manual contracts” in `.contracts/` (treat as generated/overwriteable).

## 3. Responsibilities & Requirements

### Capability Overview

Expand each capability from the `supekku:spec.capabilities@v1` YAML block above, describing concrete behaviors and linking to specific functional/non-functional requirements.

### Functional Requirements

- **FR-001**: System MUST generate a repo-root `.contracts/` directory as a deterministic, rebuildable index of generated contracts.
  *Verification*: VT-CONTRACT-MIRROR-001

- **FR-002**: System MUST mirror repo-relative source paths inside `.contracts/<view>/...` and use symlinks to point at the underlying contract markdown artefacts under `specify/tech/SPEC-*/contracts/`.
  *Verification*: VT-CONTRACT-MIRROR-002

- **FR-003**: For each supported language, the index builder MUST map registered source units to mirror paths using language-appropriate rules:
  - **Zig (file-based)**:
    - `<identifier>.zig` maps to `.contracts/public/<identifier>.zig.md` (interfaces) and `.contracts/internal/<identifier>.zig.md` (internals).
    - If the Zig source unit identifier is `"."` (repo root Zig package), it MUST map to `.contracts/public/__root__/interfaces.md` and `.contracts/internal/__root__/internals.md`.
  - **Go (package-based)**: `<identifier>/` maps to `.contracts/public/<identifier>/interfaces.md` and `.contracts/internal/<identifier>/internals.md`.
  - **TypeScript/JavaScript (file-based)**: `<identifier>.{ts,tsx,js,jsx}` maps to `.contracts/public/<identifier>.<ext>.md` (api) and `.contracts/internal/<identifier>.<ext>.md` (internal, if generated).
  - **Python (module-based contracts)**: Each module contract MUST map to `.contracts/<view>/<module_path>.py.md` where `<module_path>` is derived from the contract’s module identifier (e.g. `supekku.scripts.lib.backlog.priority` → `supekku/scripts/lib/backlog/priority.py`).
  *Verification*: VT-CONTRACT-MIRROR-002

- **FR-004**: System MUST create idiom alias paths as symlinks:
  - `.contracts/api` MUST be a symlink to `.contracts/public`
  - `.contracts/implementation` MUST be a symlink to `.contracts/all`
  *Verification*: VT-CONTRACT-MIRROR-001

- **FR-005**: Rebuilding the mirror MUST remove stale entries and MUST only write within `.contracts/` (no changes elsewhere in the repo).
  *Verification*: VT-CONTRACT-MIRROR-003

- **FR-006**: Mirror generation MUST be driven by existing registry + existing contract outputs, without requiring code parsing or toolchain execution (beyond reading contract markdown for mapping when required).
  *Verification*: VT-CONTRACT-MIRROR-002

- **FR-007**: Mirror generation MUST handle missing/absent variants gracefully:
  - If a contract artefact is missing, the mirror entry for that variant MUST be skipped (with a warning/report), not treated as a hard failure.
  - If a language suppresses a variant by design (e.g. identical TS api/internal collapsing), the mirror MUST reflect only what exists.
  - If two artefacts would map to the same mirror destination path, the mirror generation MUST warn but MUST still produce a mirror link by applying a deterministic precedence rule. Conflict detection SHOULD also be surfaced by registry validation/spec creation workflows.
  *Verification*: VT-CONTRACT-MIRROR-002
### Non-Functional Requirements

- **NF-001**: Mirror rebuild MUST be fast enough for interactive use (target: <2s for ~10k contract artefacts on a typical dev machine; linear in number of artefacts).
- **NF-002**: `.contracts/` MUST be safe to `.gitignore` entirely without breaking core spec-driver operations (it is a derived index/view).

### Success Metrics / Signals

- **Adoption**: Contract discovery tasks (“find the contract for this source path”) are consistently solved via `.contracts/**` rather than memorizing `SPEC-*/contracts/*` or `by-*` index layouts.

## 4. Solution Outline
- **User Experience / Outcomes**:
  - The path under `.contracts/**` is a mirror of the source tree, enabling muscle-memory navigation.
  - Alias directories (`api`, `implementation`) reduce friction for language-idiomatic workflows.
- **Data & Contracts**:
  - Inputs:
    - `specify/tech/registry_v2.json` mappings of `(language, identifier) -> SPEC-XXX`
    - Each spec bundle’s `specify/tech/SPEC-XXX/contracts/` directory
  - Output:
    - `.contracts/<view>/...` mirror tree containing symlinks to the underlying contract markdown artefacts
    - `.contracts/api` and `.contracts/implementation` alias symlinks

## 5. Behaviour & Scenarios
- **Scenario A — Source → Contract (Zig)**:
  - **Given** a registered Zig source file `src/domain/combat/agent.zig`
  - **When** a user opens `.contracts/public/src/domain/combat/agent.zig.md`
  - **Then** it resolves to the generated public contract artefact for that source unit (FR-002, FR-003)

- **Scenario B — Source → Contract (Go)**:
  - **Given** a registered Go package `internal/foo/bar`
  - **When** a user opens `.contracts/public/internal/foo/bar/interfaces.md`
  - **Then** it resolves to the package’s public interfaces contract (FR-003)

- **Scenario C — Search**:
  - **Given** a user runs `rg "Registry" .contracts/public/`
  - **Then** results appear under paths that mirror the source tree for quick navigation (FR-001, FR-002)

- **Error Handling / Guards**:
  - Missing contract output: skip link and warn (FR-007).
  - Conflicting mirror destinations (two contracts mapping to the same mirror path): warn, then choose deterministically (FR-007).
    - Precedence rule (v1): pick the artefact whose `SPEC-###` id is lexicographically smallest (e.g. `SPEC-004` wins over `SPEC-113`) to ensure stable rebuilds.
    - The warning SHOULD include all conflicting `SPEC-###` ids and contract target paths to make cleanup actionable.

## 6. Quality & Verification
- **Testing Strategy**:
  - Unit tests for path mapping rules per language (FR-003).
  - Integration-style tests that build a temp tech dir with minimal spec bundles and assert `.contracts/**` links exist (FR-001/FR-002/FR-005).
- **Verification Coverage**: Keep `supekku:verification.coverage@v1` entries aligned with FR ownership.
- **Acceptance Gates**:
  - `.contracts/` generated successfully on `sync` and usable for `rg`/filesystem navigation.
  - Rebuild is deterministic and safe to ignore in git (NF-002).

## 7. Backlog Hooks & Dependencies
- **Related Specs / PROD**: Extends PROD-012’s contract discovery goals by adding mirror-of-source navigation.
- **Open Decisions / Questions**:
  - Future v2: migrate underlying contract artefacts to `.contracts/` (real files) while keeping mirror paths stable; decide separation between aspirational/manual contracts vs audit/research artefacts.

## Appendices (Optional)
- Glossary, detailed research, extended API examples, migration history, etc.
