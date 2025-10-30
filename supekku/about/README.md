# About: The Supekku Spec-Driven Development Methodology

This directory contains the reference material and meta-guidance for the Supekku development methodology as implemented in this project. Supekku is a rigorous, agent-centric workflow designed to build auditable, maintainable, and robust software by treating specifications as the evergreen source of truth.

This implementation supports multi-language codebases (Go, Python, TypeScript) and is designed with the intention of being extracted into a generic, open-source framework.

## Core Philosophy

Supekku is based on an "inverted model" of spec-driven development. Unlike traditional approaches where specs are disposable artifacts used only for initial implementation, here they are living documents that co-evolve with the codebase.

-   **Specs as Truth**: Technical and Product Specifications (`SPECs` and `PRODs`) are the canonical source of truth for the system's behavior and intent.
-   **Change is Explicit**: All changes to the system are managed through explicit, declarative `Deltas` that describe the required modifications to bring the code back into alignment with the specs.
-   **Specs Evolve via Revisions**: Spec Revisions (`RE-`) document the movement of requirements and responsibilities before code work begins, preserving the documentation lineage.
-   **Continuous Auditing**: The system is designed for continuous verification. `Audits` and automated tooling ensure that the implementation never drifts far from its specification.
-   **Agent-Native**: The process is designed to be automatable and leveraged by AI development agents, with structured, machine-readable artifacts and clear, deterministic workflows.

## Key Artifacts & Concepts

The methodology is built around a set of interconnected markdown artifacts, linked via a rich frontmatter schema and structured YAML blocks that are machine-auditable.

-   **Constitution**: The set of non-negotiable principles and rules that govern all development work. See (`specify/constitution.md`).
-   **Tech Spec (SPEC)**: A detailed, evergreen technical specification for a specific system component (e.g., a Go package). It defines responsibilities, architecture, contracts, and testing strategies.
-   **Product Spec (PROD)**: A product-level specification that captures user problems, business value, hypotheses, and success metrics.
-   **Architecture Decision Record (ADR)**: Formal documents capturing significant architectural decisions with context, options considered, and rationale. ADRs use enhanced frontmatter with relationships and are managed through a comprehensive registry system.
-   **Delta (DE)**: A declarative change bundle. It's the primary mechanism for managing change, scoping the work required to align the codebase with updated specifications.
-   **Design Artefact (DA)**: A companion to a Delta, detailing the specific code-level design changes required (`kind: design_artefact` in frontmatter).
-   **Implementation Plan (IP)**: A phased plan for executing a Delta, defining clear entrance and exit criteria for each stage. Phase sheets embed `supekku:plan`/`supekku:phase` YAML blocks that drive registry updates.
-   **Audit (AUD)**: A formal review that compares the state of the code against its corresponding specs to identify drift and ensure alignment.
-   **Workspace**: An orchestration facade (`supekku/scripts/lib/workspace.py`) that loads registries, validates relations, and powers automation.

See `glossary.md`, `frontmatter-schema.md`, and `directory-structure.md` in this directory for detailed definitions and navigation patterns.

## The Development Workflow

The Supekku workflow follows a structured, iterative loop:

1.  **Capture**: Need for change is captured in a `Problem Statement`, `Issue`, or `PROD` spec.
2.  **Specify**: The desired end-state is defined by creating or updating `SPEC` and `PROD` documents. For non-code changes, a `Spec Revision` is used.
3.  **Scope Change**: A `Delta` is created to declare the intent to modify the system, referencing the relevant specs and requirements.
4.  **Design**: A `Design Revision` is drafted to translate the Delta's intent into a concrete technical design.
5.  **Plan**: An `Implementation Plan` breaks the work into verifiable phases.
6.  **Implement**: An agent (or developer) executes the plan, writing code and tests to match the design revision.
7.  **Verify**: The changes are verified against the spec through testing and a final `Audit`. Automated tooling like `sync_specs.py` helps ensure contracts are aligned across all supported languages.
8.  **Archive**: Once complete, the Delta and its related artifacts are archived, and the evergreen specs now reflect the new state of the system.

See `processes.md` for a more detailed breakdown of the commands and steps for each stage.