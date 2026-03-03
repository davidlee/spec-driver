# Notes for DE-037

## VA-037-001 — Memory Corpus Classification Report

**Date**: 2026-03-04
**Phase**: Phase 0 (Classification & Sifting)
**Classifier**: ID namespace (`mem.*.spec-driver.*` / `mem.*.project.*`)

### spec-driver bucket (22 files — platform-owned, replaced on update)

| # | ID | Type |
|---|---|---|
| 1 | mem.concept.spec-driver.audit | concept |
| 2 | mem.concept.spec-driver.backlog | concept |
| 3 | mem.concept.spec-driver.ceremony.pioneer | concept |
| 4 | mem.concept.spec-driver.ceremony.settler | concept |
| 5 | mem.concept.spec-driver.ceremony.town-planner | concept |
| 6 | mem.concept.spec-driver.contract | concept |
| 7 | mem.concept.spec-driver.delta | concept |
| 8 | mem.concept.spec-driver.design-revision | concept |
| 9 | mem.concept.spec-driver.philosophy | concept |
| 10 | mem.concept.spec-driver.plan | concept |
| 11 | mem.concept.spec-driver.posture | concept |
| 12 | mem.concept.spec-driver.relations | concept |
| 13 | mem.concept.spec-driver.revision | concept |
| 14 | mem.concept.spec-driver.spec | concept |
| 15 | mem.concept.spec-driver.truth-model | concept |
| 16 | mem.concept.spec-driver.verification | concept |
| 17 | mem.fact.spec-driver.coverage-gate | fact |
| 18 | mem.fact.spec-driver.status-enums | fact |
| 19 | mem.pattern.spec-driver.core-loop | pattern |
| 20 | mem.pattern.spec-driver.delta-completion | pattern |
| 21 | mem.pattern.spec-driver.frontmatter-compaction | pattern |
| 22 | mem.signpost.spec-driver.ceremony | signpost |

### seed bucket (2 files — project-owned starters, install-if-missing)

| # | ID | Type | References |
|---|---|---|---|
| 1 | mem.pattern.project.workflow | pattern | [[mem.pattern.spec-driver.core-loop]] |
| 2 | mem.pattern.project.completion | pattern | [[mem.pattern.spec-driver.delta-completion]] |

### unmanaged (3 files — local, never touched by installer)

| # | ID | Type | Rationale |
|---|---|---|---|
| 1 | mem.concept.spec.assembly-only-taxonomy | concept | project-local taxonomy note |
| 2 | mem.pattern.cli.skinny | pattern | project-local coding pattern |
| 3 | mem.pattern.formatters.soc | pattern | project-local coding pattern |

### Actions taken

- Removed stale `seed` tag from 19 spec-driver memory files (tag retired as bucket classifier per DE-037 §9)
- Authored 2 new seed stubs
- Configured `pyproject.toml` `[tool.hatch.build.targets.wheel.force-include]` to bundle `memory/` as `supekku/memory/` in wheel builds

### Totals

| Bucket | Count | Installer behavior |
|---|---|---|
| spec-driver | 22 | Replace/refresh from package source |
| seed | 2 | Install if missing; never overwrite |
| unmanaged | 3 | Ignored by installer |
| **Total** | **27** | |

