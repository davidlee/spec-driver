# supekku.scripts.lib.core.frontmatter_metadata.memory

Memory frontmatter metadata for kind: memory artifacts.

This module defines the metadata schema for memory frontmatter,
extending the base metadata with memory-specific fields for
deterministic retrieval, staleness tracking, and scope matching.

Field mapping from JAMMS v0.1 to spec-driver conventions:
  - JAMMS `type` → `memory_type` (avoids builtin collision)
  - JAMMS `title` → base `name`
  - JAMMS `time.created/updated` → base `created`/`updated`
  - JAMMS `time.verified/review_by` → `verified`/`review_by`
  - JAMMS `owner.contact` → base `owners`
  - JAMMS `policy.audience/visibility` → `audience`/`visibility`
  - JAMMS `relations.requires_reading` → `requires_reading`
  - JAMMS `relations.supersedes/superseded_by` → base `relations` array

## Constants

- `MEMORY_FRONTMATTER_METADATA`
