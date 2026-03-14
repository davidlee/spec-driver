---
id: IP-096-P03
name: Normalisation + closure
kind: phase
status: in-progress
delta: DE-096
plan: IP-096
created: "2026-03-14"
updated: "2026-03-14"
---

# Phase 3 – Normalisation + Closure

## Entrance Criteria

- [x] Phase 1 complete (writer)
- [x] Phase 2 complete (CLI)

## Tasks

### 1. Normalisation script

- [x] Script walks all `.spec-driver/**/*.md` files with frontmatter
- [x] For each: `load_markdown_file` → `dump_markdown_file` (body preserved, frontmatter canonicalised)
- [x] Skip files without valid frontmatter (graceful error handling)
- [x] Atomic commits for normalisation

### 2. Verification

- [x] Round-trip idempotency: running the script twice produces no diff
- [x] 4044 tests pass after normalisation
- [x] Spot-check files for sensible output
- [x] Prettier convergence: `normalise → prettier --check` = all files match

### 3. Backlog item

- [ ] Create backlog item for client repo migration strategy (progressive reformatting on first edit, potential `spec-driver format` command)

### 4. Closure

- [ ] Update IP-096 progress tracking
- [ ] Audit (AUD) and close delta

## Exit Criteria

- [x] All `.spec-driver` frontmatter is canonical
- [ ] Backlog item exists for client migration
- [ ] Delta closed
