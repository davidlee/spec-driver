# Notes for DE-086

## Phase 01 — Core Primitives (complete)

See `phases/phase-01.md` §9 for details. All 6 tasks done, 3742 tests passing.

## Phase 02 — CLI + Staleness (complete)

### What's done

- **`memory/staleness.py`**: `StalenessInfo` dataclass, `compute_batch_staleness()`, `glob_to_pathspec()`. Single batched `git log` invocation (DEC-086-06). 17 tests.
- **`edit memory --verify`**: Stamps `verified`, `verified_sha`, `updated` via `update_frontmatter_fields`. Mutex with `--status`. Refuses when git unavailable. Extracted `_verify_memory` helper. 5 tests.
- **Staleness formatter**: `format_staleness_table()` in `memory_formatters.py`. Three-tier plain text output. 7 tests.
- **`list memories --stale`**: Wired through `_format_stale_memories` helper in list.py. 2 CLI tests.

### Adaptations

- `_query_git_log` returns `None` (not empty list) on failure, so callers distinguish "git failed" from "0 commits found". Without this, git failure would falsely report `commits_since=0`.
- Staleness formatter uses plain text rather than Rich table — simpler, avoids coupling to Rich for a one-off tiered view. Could be upgraded later if needed.

### Rough edges / follow-ups

- **list.py size**: 2750+ lines. Pre-existing 95 pylint warnings. Needs factoring review — backlog item to be created after Phase 03. Noted in phase sheet.
- Staleness plain-text formatter alignment may break with very long memory IDs (>36 chars). Current corpus max is ~40 chars. Minor.
- `mem.pattern.cli.skinny` was legitimately verified during smoke testing and SHA-stamped.

### Commits

- `4fb1858` — feat(DE-086): Phase 02 code (9 files, 1110 insertions)
- `d279913` — doc(DE-086): Phase 02 sheet, IP progress, verified memory
- Code and `.spec-driver` committed separately per doctrine.

### Verification

- `just` passed after final code change: 3773 passed, 0 failed; ruff clean; pylint 9.72/10 (repo-wide, pre-existing).
- Pylint 10/10 on all new files (`staleness.py`, `edit.py`, `memory_formatters.py`).
- Smoke tested: `list memories --stale` shows real tiered output; `edit memory --verify` stamps SHA correctly; mutex enforced.

### Phase 03 readiness

Phase 03 scope: skill updates (`/retrieving-memory`, `/reviewing-memory`, `/capturing-memory`), backward compat validation, final lint/test sweep. No open design questions.

## Phase 03 — Skills and Cleanup (complete)

### What's done

- **`/capturing-memory`**: Added confidence calibration guidance after step 3 (create the record). Defines low/medium/high with plain-language descriptions. Default medium, explicit justification required for high. Reinforces that creation is authoring, not verification.
- **`/retrieving-memory`**: Added staleness awareness to output discipline section. Qualitative language per DEC-086-08/POL-002 — "not attested", "many commits since attestation", "recently attested, scope is quiet". No numeric thresholds.
- **`/reviewing-memory`**: Replaced step 1 to start with `list memories --stale` as the default review queue. Tier 1 (scoped+attested+high commit count) prioritized. Unscoped flagged separately by age.
- **Backward compat (VA-backward-compat)**: Verified — `list memories` and `show memory` work correctly with existing memories lacking `verified_sha` or `confidence`.
- **IP-086 verification coverage**: All 8 entries updated to `verified`. Fixed duplicate phase entries in plan overview block.
- **Backlog item**: ISSUE-048 created for list.py factoring review.

### Adaptations

- None. DR §5.9 was precise enough that implementation was straightforward.
- Skill sync required `spec-driver install -y` (not `sync --skills` — no such flag). The `install` command runs `sync_skills()` internally.

### Verification

- `just` passed: 3773 passed, 0 failed; ruff clean; pylint 9.72/10 (pre-existing, no regressions from this phase).

### Commits

- Uncommitted. All changes are skill markdown edits (source + installed), IP-086 updates, phase-03 sheet, ISSUE-048, and notes. No code changes in this phase.

### Follow-ups

- Delta is ready for audit/closure. All three phases complete, all verification entries verified.
- ISSUE-048 (list.py factoring) is the only deferred work item.
