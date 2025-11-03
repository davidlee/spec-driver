# Glossary

| Term | Definition | Primary Location |
| --- | --- | --- |
| **PROD Spec** | Product-level specification capturing user problems, hypotheses, and measurable outcomes. | `specify/product/PROD-xxx/` |
| **Tech Spec (SPEC)** | Technical specification describing system responsibilities, architecture, behaviour, quality requirements, and testing strategy. | `specify/tech/SPEC-xxx/` |
| **Design Revision (DR)** | Architecture patch detailing current vs target behaviour for a delta, including code hotspots and test impacts. | `change/deltas/DE-xxx/DR-xxx.md` |
| **Delta (DE)** | Declarative change bundle describing scope, inputs, risks, and desired end state that brings code back into alignment with specs. | `change/deltas/DE-xxx/DE-xxx.md` |
| **Implementation Plan (IP)** | Phased execution plan for a delta, with entrance/exit criteria and tasks. | `change/deltas/DE-xxx/IP-xxx.md` (template: `.spec-driver/templates/implementation-plan-template.md`) |
| **Audit (AUD)** | Patch-level review comparing implementation to PROD/SPEC truths, recording findings and patch status. | `change/audits/AUD-xxx.md` + template in `.spec-driver/templates/audit-template.md` |
| **Responsibility** | Discrete capability declared in a SPEC (frontmatter + Section 3) that the system must uphold. | SPEC frontmatter / Section 3 |
| **Functional Requirement (FR)** | Behavioural requirement that must be testable and trace back to product value. | SPEC Section 6 |
| **Non-Functional Requirement (NF)** | Quality requirement (performance, reliability, etc.) tied to measurement. | SPEC Section 6 |
| **Backlog Issue** | Actionable defect or gap tagged by category/severity feeding future deltas. | `backlog/issues/` |
| **Problem Statement** | Crisp articulation of user/system pain with evidence and success criteria. | `backlog/problems/` |
| **Improvement** | Opportunity/idea to enhance the system, usually linked to a problem statement. | `backlog/improvements/` |
| **Testing Companion** | Supplemental document (`SPEC-xxx.tests.md`) capturing deep testing strategy and suite inventory. | Same directory as SPEC |
| **Spec Revision (RE)** | Documented change to one or more specs without immediate code work; tracks moved requirements/responsibilities. | `change/revisions/RE-xxx.md` (template: `.spec-driver/templates/spec-revision-template.md`) |
| **Phase Sheet** | Per-phase runsheet detailing tasks, assumptions, verification; created just-in-time during execution. | `change/deltas/DE-xxx/phases/phase-0N.md` (template: `.spec-driver/templates/phase-sheet-template.md`) |
| **Requirements Registry** | Generated catalogue of every requirement with lifecycle metadata (status, introduced/implemented/verified-by/coverage-evidence). | `.spec-driver/registry/requirements.yaml` |
| **Change Registry** | Generated YAML index of deltas, revisions, and audits capturing frontmatter summaries and paths. | `.spec-driver/registry/{deltas,revisions,audits}.yaml` |
| **Workspace** | High-level facade combining spec, requirements, and change registries plus validation helpers. | `.spec-driver/scripts/lib/workspace.py` |
| **Workspace Validator** | Automated integrity checks across relations, lifecycle links, and registries. | `.spec-driver/scripts/lib/validator.py` / `just validate-workspace` |
| **Architecture Decision Record (ADR)** | Formal document capturing architecture decisions with context, options considered, and rationale. Uses enhanced frontmatter schema. | `specify/decisions/ADR-xxx-slug.md` |
| **Decision Registry** | Generated YAML catalogue of all ADRs with metadata, relationships, and backlinks for automation and validation. | `.spec-driver/registry/decisions.yaml` |
| **ADR Status Directories** | Symlink directories organizing ADRs by status (`accepted/`, `draft/`, `deprecated/`, etc.). Automatically maintained by registry sync. | `specify/decisions/<status>/` |
| **ADR CLI** | Command-line interface for ADR management: creation, listing, filtering, and registry synchronization. | `just .spec-driver::decision-registry {sync,list,show,new}` |
| **Backlog Helper Scripts** | CLI helpers for creating backlog entries: `just create-backlog-issue\|problem\|improvement\|risk`. | `.spec-driver/scripts/backlog/create_entry.py` |
| **VT (Verification Test)** | Automated test artifact providing test coverage for requirements. Typically unit or integration tests that prove functionality. | Implementation plan verification blocks, test files |
| **VH (Verification by Human)** | Manual verification artifact requiring user testing or attestation. Records human judgment, usability testing, or acceptance. | Implementation plan verification blocks, audit records |
| **VA (Verification by Agent)** | Automated agent-generated test report or analysis artifact. AI/tooling validates behavior, performs design review, or analyzes stability. | Implementation plan verification blocks, analysis documents |