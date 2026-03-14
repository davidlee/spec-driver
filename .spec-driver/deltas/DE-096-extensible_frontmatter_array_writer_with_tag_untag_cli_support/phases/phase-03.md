---
id: IP-096-P03
name: Normalisation + closure
kind: phase
status: pending
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

- [ ] Script walks all `.spec-driver/**/*.md` files with frontmatter
- [ ] For each: `load_markdown_file` → `dump_markdown_file` (body preserved, frontmatter canonicalised)
- [ ] Skip files without valid frontmatter (graceful error handling)
- [ ] One atomic commit: `chore(DE-096): normalise all .spec-driver frontmatter via CompactDumper`

### 2. Verification

- [ ] Round-trip idempotency: running the script twice produces no diff
- [ ] `just check` passes after normalisation
- [ ] Spot-check a few files for sensible output

### 3. Backlog item

- [ ] Create backlog item for client repo migration strategy (progressive reformatting on first edit, potential `spec-driver format` command)

### 4. Closure

- [ ] Update IP-096 progress tracking
- [ ] Audit (AUD) and close delta

## Exit Criteria

- [ ] All `.spec-driver` frontmatter is canonical
- [ ] Backlog item exists for client migration
- [ ] Delta closed
