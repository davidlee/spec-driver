---
id: POL-003
title: "POL-003: explicit module boundaries and coupling constraints"
status: required
created: "2026-03-23"
updated: "2026-03-23"
owners: []
supersedes: []
superseded_by: []
standards: []
specs: []
requirements: []
deltas: [DE-125]
related_policies: [POL-001]
related_standards: []
tags: [architecture, module-boundaries, coupling]
summary: Define strict architectural layering and one-way dependency rules to prevent structural decay and god-file entanglement.
---

# POL-003: explicit module boundaries and coupling constraints

## Statement

The `spec-driver` codebase must adhere to a strict, one-way layered architecture. A module in a given layer may only import from its own layer or from layers strictly beneath it in the hierarchy. **Upward dependencies (importing from a higher layer) are strictly forbidden.**

### The 5 Architectural Layers (Bottom to Top)

1.  **Core / Infrastructure (`spec_driver.core`)**
    *   **Responsibility**: Foundational file system operations, base YAML/markdown parsing, Git helpers, and cross-cutting utilities.
    *   **Constraint**: Knows nothing of the domain (specs, deltas, workflows). May only import the Python standard library and approved third-party dependencies.

2.  **Models (`spec_driver.models`)**
    *   **Responsibility**: Pure typed data structures (Pydantic models) and schema validation for artifacts.
    *   **Constraint**: Must be "dumb" data containers. May import from `core`. Must **never** import registries, I/O functions, or orchestration logic.

3.  **Domain / Registry (`spec_driver.domain`)**
    *   **Responsibility**: Entity registries, cross-artifact graph navigation, relation resolution, and in-memory artifact state management.
    *   **Constraint**: May import from `models` and `core`. Must **never** import workflow orchestration or presentation logic.

4.  **Orchestration (`spec_driver.orchestration`)**
    *   **Responsibility**: High-level operations, state machines, transition logic, sync coordination, and multi-artifact validation passes.
    *   **Constraint**: Represents the "Public API" boundary. May import from all layers below. Must **not** import from the presentation layer.

5.  **Presentation (`spec_driver.presentation.cli`, `spec_driver.presentation.tui`)**
    *   **Responsibility**: Argument parsing, formatting, terminal interaction, and user interface.
    *   **Constraint**: Must follow the "Skinny CLI" pattern. May import from any layer below. Must **never** contain domain logic or state transitions.

## Rationale

Without explicit boundaries, internal dependencies become cyclic and untraceable, leading to "god-files" (like the `supekku/scripts/lib/__init__.py`) where importing a single utility recursively loads the entire application. Strict layering ensures the system remains modular, testable, and capable of exposing a clean programmatic API (DE-124).

## Scope

Applies to all production Python code in the `spec-driver` repository, including unit tests.

*   **Unit Tests:** Must reside within the `spec_driver/` package alongside the code they test (e.g., `spec_driver/core/file_ops_test.py`) and are strictly bound by the identical layer constraints as their targets. For instance, a domain test may not import orchestration modules to set up its fixtures.
*   **Integration Tests:** Must be located in a top-level `tests/integration/` directory outside the `spec_driver/` package. Because they sit outside the enforced package, they act as top-level consumers and are exempt from internal layer constraints.

Existing legacy code in `supekku/` must be migrated to the `spec_driver/` package structure and aligned with these layers via DE-125.

## Verification

- **Automated Enforcement**: CI must run `import-linter` to verify the layer contract. Any commit introducing an upward dependency (e.g., a domain model importing a registry) must fail the build.
- **Code Review**: Reviewers must reject any new code that violates layer boundaries, even if the linter hasn't yet been configured for that specific path.
- **Architectural Audits**: Periodic audits of the dependency graph will identify and remediate "leakage" where abstractions are bypassed.

## References

- DR-125: Enforce explicit module boundaries and coupling constraints
- ADR-011: (Planned) Transition to layered package structure
- DE-114: God-file structural splits
- DE-124: Public Python API facade
