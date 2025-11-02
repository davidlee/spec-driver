---
id: ADR-002
title: 'ADR-002: Do not store backlinks in frontmatter'
status: accepted
created: '2025-11-02'
updated: '2025-11-02'
reviewed: '2025-11-02'
owners: []
supersedes: []
superseded_by: []
policies: []
specs:
  - PROD-003
requirements: []
deltas: []
revisions: []
audits: []
related_decisions:
  - ADR-001
related_policies: []
tags:
  - architecture
  - data-model
  - governance
summary: Backlinks between artifacts must be computed at runtime from forward references, not stored in frontmatter, to prevent data consistency issues and maintain single source of truth.
---

# ADR-002: Do not store backlinks in frontmatter

## Context

spec-driver uses YAML frontmatter to store metadata about artifacts (specs, ADRs, policies, standards, deltas, etc.). These artifacts reference each other via forward links like `specs: [SPEC-001]`, `policies: [POL-001]`, `related_decisions: [ADR-001]`.

**The Problem**: We need to support bidirectional navigation. When viewing SPEC-001, users want to see which ADRs reference it. When viewing POL-001, users want to see which specs implement it.

**Two Approaches Considered**:

1. **Store backlinks in frontmatter**: Add a `backlinks` field to frontmatter containing reverse references
   - Example: SPEC-001 frontmatter includes `backlinks: {decisions: [ADR-023, ADR-035]}`
   - Currently implemented in DecisionRecord (ADR) entities

2. **Compute backlinks at runtime**: Derive backlinks from forward references during registry sync
   - Forward links stored in frontmatter (single source of truth)
   - Backlinks computed by scanning all artifacts and inverting relationships
   - Backlinks maintained in memory or cached registry, not in source files

**Why This Matters Now**:

- Implementing policies and standards (PROD-003) following the ADR pattern
- Frontmatter metadata migration (Phase 6) defining canonical schemas
- Need to establish correct pattern before it spreads to new entity types

## Decision

**We will NOT store backlinks in frontmatter.** Backlinks must be computed at runtime from forward references.

**Rationale**:

1. **Single Source of Truth**: Forward links are the canonical data. Backlinks are derived data that can always be recomputed. Storing both violates DRY and creates dual-source-of-truth problems.

2. **Data Consistency**: When an artifact is modified or deleted, all backlink references must be updated. This is error-prone:
   - Delete ADR-023 → must find and update SPEC-001's backlinks
   - Add `specs: [SPEC-099]` to ADR-035 → must update SPEC-099's backlinks
   - Rename ADR-023 to ADR-024 → must update all backlink references
   - Tools and manual edits can easily create inconsistencies

3. **Coupling and Complexity**: Storing backlinks couples artifact writes:
   - Creating an ADR requires modifying the ADR file AND updating referenced spec files
   - Git commits become multi-file changes for simple reference additions
   - Merge conflicts multiply (both the ADR and all referenced specs change)
   - Violates encapsulation (artifact A's metadata stored in artifact B's file)

4. **Registry Pattern Already Exists**: The sync/registry system already scans and indexes artifacts:
   - `DecisionRegistry.collect()` parses all ADR frontmatter
   - `SpecRegistry.all_specs()` indexes all specs
   - Computing backlinks is a natural extension of existing indexing
   - Minimal performance impact (already reading all files)

5. **Correctness by Construction**: Computed backlinks are always correct:
   - Inconsistency is impossible (derived from forward links)
   - No manual maintenance required
   - Registry sync guarantees consistency
   - Source files remain simple and focused

**Implementation**:

- Forward references stored in frontmatter: `specs: [...]`, `policies: [...]`, `related_decisions: [...]`
- Registry classes compute backlinks during `collect()` phase
- Backlinks stored in registry YAML or in-memory for display
- CLI show commands display backlinks from registry, not frontmatter
- Frontmatter schemas (Phase 6D) do NOT include `backlinks` field

**Migration Path for Existing Code**:

- DecisionRecord currently has `backlinks: dict[str, list[str]]` field
- This is stored in frontmatter and registry YAML
- **Technical Debt**: Mark for future cleanup
- New entity types (policies, standards) will NOT include backlinks in frontmatter
- Eventually refactor DecisionRecord to compute backlinks

## Consequences

### Positive

- **Data integrity**: Impossible to have inconsistent backlinks (derived from truth)
- **Simpler artifact files**: Frontmatter only contains direct metadata, not derived data
- **Easier editing**: Adding a reference only requires editing one file, not two
- **Cleaner git history**: Single-file commits for reference changes
- **Better encapsulation**: Artifact A doesn't store data "owned by" artifact B
- **Maintainability**: No manual backlink synchronization needed
- **Scalability**: Backlink computation scales with artifact count, already handled by registry
- **Correctness**: Registry sync guarantees backlinks match forward references

### Negative

- **Performance**: Backlinks require registry scan (mitigated: already scanning for other reasons)
- **Latency**: Backlinks not available until registry sync completes (acceptable: sync is fast)
- **Implementation effort**: Requires backlink computation logic in each registry class (small, reusable pattern)
- **Migration**: Existing ADR backlinks need eventual cleanup (technical debt documented)

### Neutral

- **Display layer unchanged**: CLI and tools still show backlinks, just sourced from registry not frontmatter
- **Registry YAML may store backlinks**: For caching purposes, but not in source frontmatter
- **Pattern divergence**: ADRs currently store backlinks, new entities won't (temporary inconsistency during migration)

## Verification

**For new entity types (policies, standards, requirements, etc.)**:

- [ ] Frontmatter schemas do NOT include `backlinks` field
- [ ] Registry classes compute backlinks in `collect()` method
- [ ] Show commands display backlinks from registry
- [ ] Tests verify backlinks computed correctly from forward references
- [ ] No backlinks stored in source markdown frontmatter

**For existing ADRs (migration)**:

- [ ] Document that DecisionRecord backlinks are technical debt
- [ ] Add TODO to remove backlinks from DecisionRecord schema
- [ ] Refactor when resources available (not blocking)
- [ ] Ensure new code doesn't copy this pattern

**Registry sync validation**:

- [ ] Backlinks correctly reflect all forward references
- [ ] Deleting artifact removes all its backlinks
- [ ] Adding reference immediately appears in target's backlinks
- [ ] Registry YAML may cache backlinks but frontmatter must not

**Code review checklist**:

- [ ] No new `backlinks` fields added to frontmatter schemas
- [ ] Backlink computation logic in registry, not frontmatter
- [ ] Forward references remain in frontmatter
- [ ] Tests validate backlink computation, not storage

## References

- **PROD-003**: Policy and Standard Management (specify/product/PROD-003/PROD-003.md)
  - Section 4: Data & Contracts documents PolicyRecord without backlinks field
  - Section 5: Primary Flow 3 shows bidirectional navigation via registry

- **POLICIES_STANDARDS_IMPLEMENTATION_PLAN.md**:
  - Section 1: Domain Models notes "backlinks: dict[str, list[str]]" in example but marked for exclusion
  - Implementation guidance to compute backlinks at runtime

- **FRONTMATTER_MIGRATION_HANDOVER.md**: Addendum section
  - Critical architecture decision documented
  - Schema design explicitly excludes backlinks
  - Implementation pattern for PolicyRegistry/StandardRegistry

- **External Model Analysis**: gemini-2.5-pro conversation (continuation_id: 2eb47381-b03d-49f1-bdf0-b93b961980d9)
  - Recommendation to compute backlinks on demand
  - Anti-pattern analysis of storing derived data
  - Graph-based approach for dependency management

- **Current Implementation** (technical debt):
  - `supekku/scripts/lib/decisions/registry.py`: DecisionRecord.backlinks field (lines 47)
  - `supekku/scripts/lib/decisions/registry.py`: to_dict() includes backlinks (lines 104-105)
  - Should NOT be replicated in new entity types

- **ADR-001**: Use spec-driver to build spec-driver
  - Establishes practice of using spec-driver for governance decisions
  - This ADR follows same pattern for architectural decisions
