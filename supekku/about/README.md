# About: The Supekku Spec-Driven Development Methodology

This directory contains reference material guidance for spec-driver.

Spec-driver is a rigorous, agent-centric workflow designed to build auditable,
maintainable, and robust software by treating specifications as the evergreen
source of truth.

Many approaches claim to support spec-driven development. Spec-driver can drive
specs from development.

It supports multi-language codebases (Go, Python, TypeScript, Zig) and is an
open-source framework for building evolvable, highly customisable workflows
which can evolve with growing agentic engineering projects.

## Core Philosophy

Supekku is based on an "inverted model" of spec-driven development.

Under naive approaches, specs (and research) are disposable, and begin to rot
as soon as the code changes - often as soon as implementation begins.

They don't have to be disposable.

-   **Specs as Normative Truth**: Technical and Product Specifications (`SPECs`
    and `PRODs`) are the canonical source of truth for the system's behavior
    and intent.
-   **Change is Explicit**: All changes to the system are managed through
    explicit `Deltas` whiwh describe the changes and verification gates.
-   **Specs Evolve via Revisions**: Spec Revisions (`RE-`) document
    requirement/spec updates and lineage, during reconciliation after
    implementation/audit in delta-first flows.
-   **Continuous Auditing**: Spec-driver is designed for continuous
    verification. `Audits` and compact, deterministically generated contracts
    ensure that implementation never drifts far from its specification.
-   **Agent-Native**: Designed to provide fast rails for agents, with
    structured, machine-readable artifacts and configurable workflows.

## Key Artifacts & Concepts

Built around a set of interconnected markdown artifacts, linked by schema-validated YAML.

-   **Policy Layer**: Governance is expressed through ADRs, Policies, and
    Standards.
-   **Tech Spec (SPEC)**: A detailed, evergreen technical specification for a
    given subsystem. Defines responsibilities, architecture, contracts, and
    testing strategies.
-   **Product Spec (PROD)**: A product requirements document which captures
    problems, value drivers, hypotheses, use cases, and success metrics.
-   **Architecture Decision Record (ADR)**: These capture significant
    architectural decisions with context, options considered, and rationale.
-   **Delta (DE)**: A declarative change bundle. The primary mechanism for
    managing change, scoping the work required to align the codebase with
    updated specifications.
-   **Design Revision (DR)**: A companion to a Delta, detailing the specific
    code-level design changes required.
-   **Implementation Plan (IP)**: A phased plan for executing a Delta, defining
    clear entrance and exit criteria for each stage. Phase sheets embed YAML
    which propagate progress through a registry.
-   **Audit (AUD)**: A formal review that compares observed system reality
    against its corresponding specs to identify drift and ensure alignment.
-   **Workspace**: An orchestration facade that loads registries, validates
    relations, and powers automation.

See `glossary.md`, `frontmatter-schema.md`, and `directory-structure.md` in this directory for detailed definitions and navigation patterns.

## The Development Workflow

Work follows a structured, iterative loop:

1.  **Capture**: Need for change is captured in a backlog card or spec.
2.  **Specify**: The desired end-state is defined by creating or updating `SPEC` and `PROD` documents. For non-code changes, a `Spec Revision` is used.
3.  **Scope Change**: A `Delta` is created to declare the intent to modify the system, referencing the relevant specs and requirements.
4.  **Design**: A `Design Revision` is drafted to translate the Delta's intent into a concrete technical design.
5.  **Plan**: An `Implementation Plan` breaks the work into verifiable phases.
6.  **Implement**: An agent (or developer) executes the plan, writing code and tests to match the design revision.
7.  **Verify**: The changes are verified against the spec through testing and a final `Audit`. Automated tooling like `sync_specs.py` helps ensure contracts are aligned across all supported languages.
8.  **Close**: Complete the Delta and reconcile owning records (coverage/lifecycle/relations), then run sync/validate so evergreen specs and registries reflect the current system state.

See `processes.md` for a more detailed breakdown of the commands and steps for each stage.
