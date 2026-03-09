# Notes for DE-084

## Scope correction

Initial analysis incorrectly concluded only 2 commands needed migration (grepped
for `if sum([json_output` but missed the `bool_flags = sum([` variant used by 5
others). Actual count: 7 commands, matching ISSUE-037's original report exactly.

## Implementation

Migrated all 7 show commands (`spec`, `delta`, `requirement`, `adr`, `policy`,
`standard`, `card`) from inline output dispatch to `resolve_artifact` + `emit_artifact`.

Key patterns:
- Most commands: `resolve_artifact(type, id, root)` → `emit_artifact(ref, ...)`
- `show card`: kept manual `CardRegistry.resolve_card(id, anywhere=anywhere)` then
  constructed `ArtifactRef` before passing to `emit_artifact` (for `--anywhere` support)
- `to_dict(root)` closures: `spec`, `adr`, `policy`, `standard` capture `repo_root`
  in the `json_fn` lambda
- `show delta`: uses existing `format_delta_details_json` for `json_fn`
- `show requirement`: `to_dict()` takes no params

## Cleanup

- Removed unused imports: `ContentType`, `extract_yaml_frontmatter`, `normalize_id`,
  `ChangeRegistry`, `DecisionRegistry`, `PolicyRegistry`, `RequirementsRegistry`,
  `SpecRegistry`, `StandardRegistry`
- Eliminated 5 inline `from ... import find_repo_root` re-imports that pylint flagged
  as `reimported` / `redefined-outer-name`
- Added `content_type` param to `show requirement` and `show card` (previously missing)

## Test updates

- Fixed `test_show_delta_not_found`: error message casing changed (`"Delta not found"`
  → `"delta not found"`) because `ArtifactNotFoundError` uses the type key
- Fixed 4 mutual-exclusivity tests: previously used non-existent `DE-001` which worked
  when flag check preceded resolution; now resolution happens first via `resolve_artifact`,
  so tests use real delta IDs

## IMPR-006

Confirmed fully resolved by prior work — all formatters already use `format_list_table`,
cell helpers extracted, `no_truncate` cleaned up. Can be closed separately.
