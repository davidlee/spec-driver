# Glossary of Primitives & Concepts

## Card

A **card** is the primary record for task execution and implementation notes. Depending on the project's ceremony level and workflow, a card may be:

- A **kanban card** (lightweight task in `kanban/`)
- A **delta** (declarative change bundle in `.spec-driver/deltas/`)
- An **implementation plan** (phased execution plan within a delta)

The term "card" in skills and workflows refers to whichever of these the project uses as its primary unit of work — not exclusively a kanban card.

## Specifications

- **PROD Spec** (`PROD-xxx`): Product-level specification capturing user problems, hypotheses, and outcomes. Location: `.spec-driver/product/PROD-xxx/`.
- **Tech Spec** (`SPEC-xxx`): Technical specification describing responsibilities, architecture, behaviour, and requirements. Location: `.spec-driver/specs/tech/SPEC-xxx/`.
  - `category: unit` — 1:1 with a code unit (file/module/package).
  - `category: assembly` — cross-unit subsystem/integration/functional slice.
  - `c4_level: system|container|component|code|interaction` — C4 architecture level.
- **Testing Companion** (`SPEC-xxx.tests.md`): Supplemental testing strategy and suite inventory.

## Change Artefacts

- **Delta** (`DE-xxx`): Declarative change bundle describing scope, inputs, risks, and desired end state. Location: `.spec-driver/deltas/DE-xxx/`.
- **Design Revision** (`DR-xxx`): Architecture patch detailing current vs target behaviour. Location: `.spec-driver/deltas/DE-xxx/DR-xxx.md`.
- **Implementation Plan** (`IP-xxx`): Phased execution plan with entrance/exit criteria. Location: `.spec-driver/deltas/DE-xxx/IP-xxx.md`.
- **Phase Sheet**: Per-phase runsheet with tasks and verification. Location: `.spec-driver/deltas/DE-xxx/phases/phase-0N.md`.
- **Spec Revision** (`RE-xxx`): Documented spec change without immediate code work. Location: `.spec-driver/revisions/RE-xxx.md`.
- **Audit** (`AUD-xxx`): Patch-level review comparing implementation to specs. Location: `.spec-driver/audits/AUD-xxx.md`.

## Requirements & Verification

- **Functional Requirement** (`FR-xxx`): Behavioural requirement, testable, traced to product value.
- **Non-Functional Requirement** (`NF-xxx`): Quality requirement (performance, reliability, etc.).
- **VT (Verification Test)**: Automated test artifact proving functionality.
- **VA (Verification by Agent)**: Agent-generated test report or analysis.
- **VH (Verification by Human)**: Manual verification requiring user attestation.

## Governance

- **ADR** (`ADR-xxx`): Architecture Decision Record. Location: `.spec-driver/decisions/ADR-xxx-slug.md`.
  - **Contract**: Auto-generated API documentation. Location: `.contracts/`.
  ## Backlog

- **Issue**: Actionable defect or gap. Location: `.spec-driver/backlog/issues/`.
- **Problem Statement**: Articulation of user/system pain. Location: `.spec-driver/backlog/problems/`.
- **Improvement**: Enhancement opportunity. Location: `.spec-driver/backlog/improvements/`.
- **Risk**: Identified risk with likelihood/impact assessment. Location: `.spec-driver/backlog/risks/`.
- **Drift Ledger** (`DL-xxx`): Tracked spec-vs-reality divergence. Location: `.spec-driver/drift/`.
