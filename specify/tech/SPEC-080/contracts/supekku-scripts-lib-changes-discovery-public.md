# supekku.scripts.lib.changes.discovery

Utilities for discovering requirement sources in revision files.

## Functions

- `find_requirement_sources(requirement_ids, revision_dirs) -> dict[Tuple[str, RequirementSource]]`: Find source locations for requirements in revision files.

Scans all revision files in the given directories and locates
requirements in their YAML blocks.

Args:
    requirement_ids: List of requirement IDs to search for
    revision_dirs: Directories containing revision bundles

Returns:
    Mapping of requirement_id -> RequirementSource for found requirements.
    Only includes requirements found in revision blocks.

## Classes

### RequirementSource

Location of a requirement in a revision file.
