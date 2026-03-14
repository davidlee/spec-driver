---
name: retrieving-memory
description: |
  Invoke this skill before making non-trivial assumptions in a large codebase. Mandatory triggers: (1) you are about to modify a subsystem you have not touched in this run; (2) you are about to run, change, or suggest a command pipeline (tests, builds, releases, migrations); (3) you see conflicting cues in code/docs; (4) you are asked “what is the right way here?”; (5) you are debugging a recurring failure mode; (6) you are about to answer with “probably/usually/likely”.
  Default rule: if you cannot cite a source-of-truth file/doc/ADR/SPEC from the repo, you must consult memories first and then proceed.
---

Retrieval procedure (fast → thorough):

1. Contextual list (preferred):
   - Use scope matching to get the most relevant memories:
     `spec-driver list memories -p <path>... -c "<command tokens>" --match-tag <tag>...`
   - Before working on a specific subsystem, build this query from the concrete
     files you expect to read or edit first. Memories with `scope.globs` still
     match those `-p` paths, so you do not need a separate glob flag.
   - For planned code changes, prefer at least one exact file path plus the
     command context you are about to run. Example:
     `spec-driver list memories -p supekku/scripts/lib/skills/sync.py -c "uv run pytest" --match-tag skills`
   - Remember: scope matching is OR across query types, but metadata filters (`--type`, `--status`, `--tag`) are AND pre-filters; avoid over-filtering unless you are certain.

2. Narrow by metadata only after you have a hit list:
   - `--type` to focus (e.g., `--type pattern` for operational commands, `--type system` for subsystem map).
   - `--regexp/-r` to find by title/summary, `-i` for case-insensitive.

3. Inspect candidates:
   - Use `spec-driver show memory MEM-ID` (or numeric shorthand) to read full details; use `--raw` if you need the full markdown body; use `--path` if you need to open the file directly.

4. If you have a partial ID:
   - Use `spec-driver find memory PATTERN` with fnmatch (`*`, `?`) to locate likely candidates.

Decision framework (what to trust):

- Prefer memories with higher `priority.severity`, higher `priority.weight`, higher scope specificity, and more recent `verified/updated` (the list ordering already encodes this).
- If a memory lacks `provenance.sources` for a claim, treat it as advisory only and verify against code/docs before acting.
- If retrieved memories disagree, do not “average”; escalate to maintenance (update/supersede) before proceeding with consequential changes.

Output discipline:

- When responding or planning, cite the relevant memory IDs and their linked sources (paths/ADRs/specs). If you cannot, retrieve again with tighter `--path/--command/--match-tag` until you can.
- When starting work on a new file cluster, do the scoped query before deep
  reading or editing so glob-scoped gotchas surface while the change is still
  cheap.
- **Staleness awareness** — when presenting a retrieved memory, surface its
  verification state qualitatively:
  - No `verified_sha`: "this memory has not been attested against the codebase"
  - High staleness (many commits since attestation): "many commits have affected
    its scope since last attestation — treat with caution"
  - Low staleness (few/no commits since attestation): "recently attested, scope
    is quiet"
  - Do not use numeric thresholds — qualitative language is more robust across
    different repo cadences and avoids magic numbers.

---
