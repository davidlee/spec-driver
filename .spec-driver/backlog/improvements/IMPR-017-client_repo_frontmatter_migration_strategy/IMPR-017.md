---
id: IMPR-017
name: Client repo frontmatter migration strategy
created: "2026-03-14"
updated: "2026-03-14"
status: idea
kind: improvement
tags: [frontmatter, migration, dx]
---

# Client repo frontmatter migration strategy

## Context

DE-096 introduced CompactDumper for canonical, prettier-compatible frontmatter YAML formatting. The spec-driver repo itself is normalised, but client repos using spec-driver still have old-style frontmatter.

## Problem

Client repos will accumulate mixed formatting: old files with block-style lists and single-quoted dates, new/edited files with CompactDumper output. This creates noisy diffs and inconsistency.

## Options

1. **Progressive normalisation on edit** — when `update_frontmatter` touches a file, it already uses CompactDumper. Files converge organically as they're edited. No action needed beyond what DE-096 already delivers.

2. **`spec-driver format` command** — explicit CLI command to normalise all frontmatter in a workspace. Could be run once after upgrading, or wired into CI/pre-commit.

3. **Migration script in install** — `spec-driver install` could optionally normalise existing frontmatter during upgrade.

## Recommendation

Option 1 is the baseline (already implemented). Option 2 would be a nice-to-have for repos wanting a clean one-time migration. Low effort — the normalisation script from DE-096 (`scripts/normalise_frontmatter.py`) is the reference implementation.
