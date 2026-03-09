---
id: mem.fact.skills.source-location
name: Skill source vs installed location
kind: memory
status: active
memory_type: fact
created: '2026-03-09'
updated: '2026-03-09'
tags:
- skills
- gotcha
summary: Edit skills at supekku/skills/, not .spec-driver/skills/. The installed copies
  are derived and overwritten on sync.
scope:
  globs:
    - supekku/skills/**
    - .spec-driver/skills/**
verified: '2026-03-09'
provenance:
  sources:
    - DE-085
---

# Skill source vs installed location

- **Source**: `supekku/skills/<skill-name>/SKILL.md` — edit here
- **Installed**: `.spec-driver/skills/<skill-name>/SKILL.md` — derived, overwritten on sync
- Editing the installed copy is a silent no-op: changes are lost on next `spec-driver sync`
- Discovered during DE-085 Phase 3
