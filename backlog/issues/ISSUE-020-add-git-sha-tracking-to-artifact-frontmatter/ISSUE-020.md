---
id: ISSUE-020
name: Add git SHA tracking to artifact frontmatter
created: '2025-11-08'
updated: '2025-11-08'
status: open
kind: issue
categories: [metadata, traceability]
severity: p2
impact: system
---

# Add git SHA tracking to artifact frontmatter

## Problem Statement

Artifacts (specs, deltas, ADRs, etc.) currently track dates for creation, updates, and reviews, but lack git commit SHAs that provide precise traceability to repository history. This creates several issues:

1. **Ambiguous History**: Date-only timestamps don't capture which specific commit introduced changes
2. **Difficult Auditing**: Hard to trace when a spec was last synced with code or reviewed against actual implementation
3. **Lost Context**: Can't easily link artifact state to git history for debugging or understanding evolution
4. **Sync Verification**: No way to verify if a tech spec reflects the codebase state at a specific commit

## Proposed Solution

Extend frontmatter schema to include git SHA tracking for key lifecycle events:

```yaml
---
id: SPEC-110
created: '2025-11-01'
updated: '2025-11-08'
git_shas:
  created: abc123def456  # Commit where artifact was created
  last_material_update: def789abc012  # Last substantive content change (not typos/formatting)
  last_sync: ghi345jkl678  # For tech specs: last code sync
  last_review: mno901pqr234  # Last review confirming accuracy
---
```

### Artifact-Specific Fields

**All artifacts:**
- `git_shas.created` - commit where artifact was first created
- `git_shas.last_material_update` - last substantive content change

**Tech specs only:**
- `git_shas.last_sync` - last sync with codebase (when contracts/code analysis ran)

**All artifacts (optional):**
- `git_shas.last_review` - commit where artifact was reviewed and deemed accurate

## Affected Artifacts

- Product specs (PROD-*)
- Tech specs (SPEC-*)
- ADRs
- Policies
- Standards
- Deltas (DE-*)
- Revisions (RE-*)
- Audits (AUD-*)
- Backlog items (issues, problems, improvements, risks)

## Implementation Considerations

1. **Backward Compatibility**: Make git_shas optional; existing artifacts continue to work
2. **Automation**: CLI commands should auto-populate git_shas when creating/updating artifacts
3. **Validation**: Validate SHA format (7-40 char hex strings)
4. **Tooling**:
   - `create` commands auto-capture `created` SHA
   - `sync` commands auto-capture `last_sync` SHA
   - Manual review workflow updates `last_review` SHA
5. **Display**: Show relevant SHAs in `show` commands with `--verbose` or `--git-info` flag

## Benefits

- **Precise Traceability**: Link artifact state to exact git commits
- **Audit Trail**: Verify when specs were last synced/reviewed against code
- **Historical Analysis**: Understand artifact evolution in context of code changes
- **Sync Verification**: Confirm tech specs reflect current codebase state
- **Review Tracking**: Know when artifacts were last validated as accurate

## Related Work

- FR-015 (PROD-010): Per-file validation could validate SHA format
- Tech spec sync automation could auto-update `last_sync` SHA
- Review workflows could prompt for `last_review` SHA update

## Open Questions

1. Should we backfill SHAs for existing artifacts? (likely no - too much effort for little value)
2. Should `last_material_update` auto-update on every content change, or require manual flag?
3. How to distinguish "material" vs "non-material" updates (formatting, typos)?
4. Should we track multiple SHAs per event type (e.g., sync history array)?

