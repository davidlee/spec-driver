---
id: ISSUE-018
name: Add tags support for inline requirements
created: '2025-11-04'
updated: '2025-11-04'
status: open
kind: issue
categories:
  - feature_gap
severity: p3
impact: user
---

# Add tags support for inline requirements

## Problem

Requirements extracted from specs have a `tags` field in the requirements registry, but there's currently no mechanism to populate it. The extraction code in `RequirementsRegistry._records_from_content()` uses pure regex matching on markdown list items and doesn't parse any YAML blocks or extract tag metadata.

Current state:
- Requirements registry schema includes `tags: []` field
- All requirements have empty tags arrays
- No way to categorize/tag requirements for filtering or discovery
- Frontmatter schema supports tags for standalone requirement files, but inline requirements can't specify them

## Current Behavior

The `_records_from_content()` method in `supekku/scripts/lib/requirements/registry.py`:
- Uses regex pattern `_REQUIREMENT_LINE` to match lines like `- **FR-001**(category): Title`
- Extracts: label (FR-001), category, and title
- Does NOT parse YAML blocks (e.g., `supekku:spec.relationships@v1` or similar)
- Does NOT extract tags from any source
- Always initializes `tags=[]` in the requirements registry

## Expected Behavior

Requirements should support tags for:
- Cross-cutting concerns (security, performance, accessibility)
- Technical domains (api, database, ui)
- Priority/importance markers
- Discovery and filtering in CLI commands

## Proposed Solution

Options to consider:

1. **YAML block approach**: Define a `supekku:requirements.metadata@v1` block in specs where tags can be specified per requirement
2. **Inline syntax**: Extend the regex pattern to support tag syntax like `- **FR-001**(category)[tag1,tag2]: Title`
3. **Frontmatter inheritance**: Allow spec-level tags to cascade to all requirements in that spec
4. **Dedicated requirements section**: Add optional YAML metadata blocks in Section 6 alongside inline definitions

## Impact

Without tags support:
- Limited requirement discovery and filtering capabilities
- Can't easily identify cross-cutting concerns
- Reduced value of the tags field in the registry schema
- Inconsistency between standalone requirement files (which support tags) and inline requirements (which don't)

## Related

- Requirements registry: `supekku/scripts/lib/requirements/registry.py`
- Extraction regex: `_REQUIREMENT_LINE` pattern (line ~51)
- Extraction method: `RequirementsRegistry._records_from_content()` (line ~970)
- Registry schema includes tags field but never populated
- Frontmatter schema (`supekku/about/frontmatter-schema.md`) documents tags for requirements

