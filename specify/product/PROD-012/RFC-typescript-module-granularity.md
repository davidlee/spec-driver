# RFC: TypeScript Module Granularity for Contract Generation

**Status**: Draft
**Created**: 2025-11-11
**Updated**: 2025-11-19
**Related**: PROD-012 (Code Contract Documentation), FR-015 (1:1 code-to-spec mapping)

## Executive Summary

TypeScript contract generation currently produces excessive granularity (100+ specs for medium projects) because of a 1:1 file-to-spec mapping. This RFC proposes shifting the fundamental unit of discovery from **Files** to **Scopes**, anchored strictly by `package.json`.

To support this, the underlying architecture must shift from **Iteration** (looping over files) to **Aggregation** (resolving a scope, identifying all contained files, and generating a single combined contract). This necessitates significant changes to the `typescript.py` adapter and the `ts-doc-extract` tool to ensure performance and deterministic boundary resolution.

## Problem Statement

### 1. Excessive Granularity
Current adapter treats every "significant" file as a module.
**Result**: Medium NextJS project (~1134 files) → **119 specs**. This violates FR-015 (cohesive specs) and makes the registry unnavigable.

### 2. Lack of Standard Boundaries
Unlike Python (`__init__.py`) or Go (`go.mod`), TypeScript/JavaScript has no language-enforced module boundary below the `package.json` level. Heuristics like `index.ts` or directory names (`src/`, `app/`) are brittle and fail in too many valid project structures.

### 3. The 1:1 Mapping Trap
The current architecture assumes 1 Source File = 1 Markdown Output.
To group files (e.g., "All components in `src/components`"), we must break this assumption. The system must be able to read N files and produce 1 cohesive Spec.

## Core Design: Scope-Based Aggregation

### 1. The Anchor: `package.json`
The only deterministic, universal boundary in the ecosystem is `package.json`.
- **Discovery**: The adapter shall *only* look for `package.json` files to identify potential Spec roots.
- **Rejection of Heuristics**: We will not use `index.ts`, `src/`, or file counts for the fundamental discovery logic.

### 2. The Unit: Scope (Package + Subtree)
A Spec is defined by a **Scope**, not a file path.
```yaml
# SPEC-001.md
sources:
  - language: typescript
    package: packages/ui-library  # The anchor
    subtree: src/components       # The refinement (optional)
```

### 3. Scope Resolution: "The Hole in the Donut"
To ensure **Exclusivity** (every file belongs to exactly one spec), Scopes must be subtractive.
If a Parent Spec covers `src/` and a Child Spec covers `src/components/`, the Parent's **Effective Scope** is:
`Files(src/) - Files(src/components/)`

**Logic:**
1. Identify all Specs anchored to a specific `package.json`.
2. Sort by subtree length (longest/deepest first).
3. For a given Spec, its file list is:
   `Glob(subtree/**/*) MINUS Union(All Child Spec Subtrees)`

### 4. Architecture Shift: Bulk Extraction
**Current State**: Python loops over files, calling `npx ts-doc-extract <file>` for each.
**Problem**: In a "Package Scope" scenario with 500 files, this spawns 500 Node.js processes.
`500 * (200ms startup + 500ms parse)` = ~6 minutes per sync. **Unacceptable.**

**Required State**: Bulk Extraction.
1. Python calculates the **Effective Scope** (Root path + List of Exclude paths).
2. Python calls `ts-doc-extract` **ONCE** for the Scope.
   `npx ts-doc-extract <package_root> --include "src/**/*" --exclude "src/components/**/*"`
3. `ts-doc-extract` parses the project once and returns a single JSON containing aggregated AST data for all requested files.

## Implementation Requirements

### 1. Update `ts-doc-extract` (Node.js)
Must be upgraded to support **Directory Mode**:
- Input: Directory path instead of single file.
- Input: `--exclude` patterns (to support Scope Subtraction).
- Behavior:
  - Load `tsconfig.json` once.
  - Iterate relevant files internally in JS.
  - Return aggregated AST (e.g., `Map<FilePath, AST>`).

### 2. Update `typescript.py` (Python)
Must be rewritten to support **Aggregation**:
- **Discovery**: Find `package.json` files.
- **Resolution**:
  - Find all existing Specs referencing this package.
  - Calculate the "Hole in the Donut" (excludes) for each Spec.
- **Generation**:
  - Construct the bulk command for `ts-doc-extract`.
  - Pass the aggregated JSON to the Markdown formatter.
  - Formatter must now render a "Module of Modules" view (grouping exports by their source file or re-export structure).

## Migration & UX Strategy

### Initial Sync (The "Giant Spec" Issue)
Since we reject heuristics for *Discovery*, a `sync --stub` on a fresh repo will produce **One Spec per `package.json`**.
- For single-package repos, this is one giant Spec (1000+ files).
- This is "Correct" but "Unusable".

**Mitigation (Layer 2):**
While the *Core* is deterministic, the *Stub Generator* can use heuristics to suggest splits *during creation*.
- When creating a new Stub for a large package, the CLI can suggest: "This package is huge. Split by `src/` subdirectories?"
- If accepted, it generates multiple Specs with correct `subtree` metadata immediately.
- **Crucially**: This is a one-time generation convenience, not a runtime discovery rule.

### Migration Command
Existing repos with 1:1 file specs need a migration path.
`spec-driver migrate-ts-granularity`:
1. Reads all current file-based specs.
2. Identifies their `package.json` owner.
3. Generates new Scope-based Specs (aggregating the old ones).
4. Archives/Deletes the old file-specs.

## Open Questions

### Q1: Formatting the Aggregated Contract
How do we present the content of 50 files in one generated Markdown contract (e.g., `contracts/api.md`)?
- **Option A**: Flat list of exports (unusable for large sets).
- **Option B**: File-based sections (`## src/utils/date.ts`).
- **Option C**: Heuristic grouping (group by folder).
**Recommendation**: Option B (File-based sections) is the safest default.

## Contract Structure & Artifacts

### 1. File Structure within Contracts
Aggregate contract files (Markdown) will map directory structure to headers to preserve context and navigability.
*   **Ordering**: Strictly alphabetical by file path (deterministic).
*   **Headers**:
    *   Level 1 (`#`): Package Name (e.g., `@org/ui-lib`) or Scope Root.
    *   Level 2 (`##`): Relative File Path (e.g., `src/utils/date.ts`).
    *   Level 3+ (`###`): Symbols (Classes, Functions, Interfaces).

### 2. Variant Strategy
We will maintain specific variants to segment audiences and manage token usage.
*   `contracts/api.md`: Publicly exported symbols (for library consumers).
*   `contracts/internal.md`: Non-exported/Internal symbols (for maintainers).
*   `contracts/tests.md`: Test file signatures (for QA/Verification agents).

### 3. Symlink Strategy
Symlinks will map **Scopes**, not individual files.

*   **`specify/tech/by-slug/`**: Flat list of specs (Standard).
*   **`specify/tech/by-package/`**: Maps to the `package.json` location. Links to the **Root Spec** of that package.
*   **`specify/tech/by-language/typescript/`**: Mirrors the source tree at the **Scope Level**.
    *   If `SPEC-001` covers `src/utils`, a symlink is created at `specify/tech/by-language/typescript/src/utils` pointing to the spec.
    *   Individual files *inside* that scope are NOT symlinked. This creates a clean map of "Which Spec owns this folder?".

## Plan

1.  **Tooling Upgrade**: Modify `ts-doc-extract` to support directory input and excludes.
2.  **Adapter Core**: Rewrite `typescript.py` to use `package.json` discovery and bulk extraction.
3.  **Schema**: Add `package` and `subtree` to Source Descriptor.
4.  **Markdown**: Update formatter to handle multiple files in one output using the `## FilePath` header structure.