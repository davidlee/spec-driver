---
id: IP-137-P05
slug: "137-cross_cutting_metadata_schema_infrastructure_validation_templates_cli_migrate_orchestrator_de_136_child-phase-05"
name: IP-137 Phase 05 - Skill gates + acceptance + closure
created: "2026-05-19"
updated: "2026-05-19"
status: completed
kind: phase
plan: IP-137
delta: DE-137
---

# IP-137-P05 — Skill gates + acceptance + closure

## 1. Objective

Land the skill-layer validation gates that depend on the
`validate file` / `validate workspace` surfaces shipped by P03, then
close DE-137:

- Insert verbatim `validate file` / `validate workspace` gate text
  (bracketed by `<!-- validate-gate:<skill> begin -->` /
  `<!-- validate-gate:<skill> end -->` anchor markers per DR-137 §5.5
  + F-23) into 5 skill source files under `supekku/skills/<skill>/SKILL.md`:
  `execute-phase`, `close-change`, `audit-change`, `notes`,
  `update-delta-docs`.
- Ship VT-CC-027 regression test asserting anchor pair + expected
  `spec-driver validate ...` command string per skill.
- Run full acceptance: `just check`, `uv run lint-imports`
  (both contracts `KEPT`), `uv run spec-driver validate workspace`
  on this repo.
- Reconcile PROD-004 coverage blocks: FR-001 / FR-002 / FR-003 /
  FR-006 entries flipped to `status: verified` with VT-CC-NNN
  citations from IP-137 `verification.coverage`.
- Run `uv run spec-driver complete delta DE-137` without `--force`.

No new framework surface; this is a paperwork + skill-text + gate
phase. Per-artefact migrations stay deferred to DE-138..142.

## 2. Links & References

- **Delta**: DE-137
- **Design Revision Sections**:
  - DR-137 §5.5 (Deliverable 6 — Skill tuning):
    - Verbatim insertion table (skill → insertion target → text)
    - Anchor markers F-23 (`<!-- validate-gate:<skill> begin/end -->`)
    - VT-CC-027 marker-presence regression specification
  - DR-137 §11 — VT-CC-027 row.
  - DR-137 §10 — DR-136 §5.5 reconciliation (skills sourced from
    `supekku/skills/<skill>/SKILL.md`; no templating layer; direct
    edits commit + ship via sync).
- **Specs / PRODs**: PROD-004 (FR-001, FR-002, FR-003, FR-006).
- **Support Docs**:
  - `supekku/skills/execute-phase/SKILL.md`
  - `supekku/skills/close-change/SKILL.md`
  - `supekku/skills/audit-change/SKILL.md`
  - `supekku/skills/notes/SKILL.md`
  - `supekku/skills/update-delta-docs/SKILL.md`
  - `IP-137.md` `verification.coverage@v1` block (authoritative
    VT→requirement map; mirror flips in PROD-004 coverage blocks).
  - `.spec-driver/product/PROD-004/PROD-004.md` (coverage block
    targets — confirm exact path/IDs at task 5.5).
  - DE-137/notes.md hand-off section "Hand-off note for IP-137-P05".

## 3. Entrance Criteria

- [x] IP-137-P04 complete and committed (commit `5a008f21`
  `docs(DE-137): IP-137-P04 wrap-up`).
- [x] `validate file` and `validate workspace` surfaces shipped end
  to end (P03; confirmed in P04 hand-off note).
- [x] `admin migrate` orchestrator live with empty inventory
  (P04 task 4.14).
- [ ] Local toolchain green at start: `just check` clean on the
  post-P04 commit; `uv run lint-imports` reports both
  `Architectural Layers` and `Migrations isolation` KEPT.
- [ ] `workflow.toml` install-version warning (`workflow.toml has
  0.9.2, running 0.9.7`) triaged: either run `spec-driver install`
  to refresh, or note as out-of-scope drift and link a follow-up.
  STOP if the running CLI behaviour diverges from the documented
  surface this phase exercises (e.g. `validate file`/`validate
  workspace` flag drift).

## 4. Exit Criteria / Done When

- [ ] Five `supekku/skills/<skill>/SKILL.md` files carry the verbatim
  `validate ...` text from DR-137 §5.5, bracketed by the
  `<!-- validate-gate:<skill> begin -->` / `<!-- validate-gate:<skill> end -->`
  anchor pair at the insertion target specified in §5.5:
  - `execute-phase` — after "Verify acceptance" / before "Mark phase
    complete": `Run \`spec-driver validate file <phase-sheet.md>\`
    before transitioning the phase to \`completed\`. Validation
    failures must be resolved or filed as drift before close.`
  - `close-change` — before `complete delta` step: `Run
    \`spec-driver validate workspace\` over the workspace and
    \`spec-driver sync\` to refresh contracts/indices. Both must
    succeed (or have explicit drift entries) before close.`
  - `audit-change` — after populating findings disposition: `Run
    \`spec-driver validate file <audit.md>\` to confirm
    finding/disposition matrix integrity before submission.`
  - `notes` — after persisting note write: `Run \`spec-driver
    validate file <touched-artefact>\` if the note's edit modified
    frontmatter or block content.`
  - `update-delta-docs` — after reconciliation step: `Run
    \`spec-driver validate file\` against each updated artefact
    (delta, DR, IP, phase) to confirm metadata consistency.`
- [ ] Installed skill copies under `.spec-driver/skills/<skill>/SKILL.md`
  (and any `.claude/skills/` / `.agents/skills/` symlinks) reflect
  the new gate text. If sync flow surfaces drift, run
  `spec-driver sync` (per DR-137 §10) and commit.
- [ ] VT-CC-027 regression test ships at
  `tests/supekku/skills/validate_gate_test.py` (or sibling
  location matching project test layout); for each of the five
  skill IDs the test:
  1. opens `supekku/skills/<skill>/SKILL.md`,
  2. asserts the marker pair `<!-- validate-gate:<skill> begin -->`
     ... `<!-- validate-gate:<skill> end -->` is present (regex,
     `re.DOTALL`),
  3. asserts the bracketed content contains the expected
     `spec-driver validate ...` command string for that skill.
- [ ] VT-CC-027 marked `verified` in IP-137 `verification.coverage`.
- [ ] `just check` clean (test + ruff + format + pylint ratchet).
- [ ] `uv run lint-imports` clean (both `Architectural Layers` and
  `Migrations isolation` KEPT).
- [ ] `uv run spec-driver validate workspace` exits clean against
  this repo (warnings tolerated only with explicit drift entries
  per the close-change contract).
- [ ] PROD-004 coverage blocks reconciled: FR-001, FR-002, FR-003,
  FR-006 each carry coverage rows for the relevant DE-137 VTs at
  `status: verified` (with notes citing the VT-CC IDs from IP-137).
- [ ] DE-137 `applies_to` specs (PROD-004 / SPEC-114 / SPEC-116 /
  SPEC-125) carry no `status: planned` rows owned by DE-137 (audit
  at delta close, per DR-137 §3 close-out commitment).
- [ ] `uv run spec-driver complete delta DE-137` succeeds without
  `--force`.
- [ ] Final phase wrap-up commit lands (`docs(DE-137): IP-137-P05
  wrap-up`); DE-137 status flips to `completed` via the CLI.

## 5. Verification

- **Unit tests** (new):
  - `tests/supekku/skills/validate_gate_test.py` — VT-CC-027.
    Parametrise over five `(skill_id, expected_command_substring)`
    pairs. For each: open the source SKILL.md, search for the
    anchor pair via regex, capture the bracketed body, assert the
    expected substring is inside. Fail-fast on missing markers or
    missing command string; clear diff-style message naming the
    skill on failure.
- **Integration / acceptance smoke**:
  - `just check` — phase gate.
  - `uv run lint-imports` — both contracts `KEPT`.
  - `uv run spec-driver validate workspace` against this repo —
    captures the post-DE-137 validation surface for the close-out
    record.
  - `uv run spec-driver sync` (if drift surfaces between source and
    installed skill copies during task 5.2).
  - `uv run spec-driver complete delta DE-137` — closure ceremony.
- **Tooling / commands**:
  - `rg '<!-- validate-gate:' supekku/skills/` — sanity grep that
    five marker pairs landed (10 lines total: begin + end per skill).
  - `rg 'spec-driver validate' supekku/skills/<skill>/SKILL.md`
    per file — confirm the inserted text reads cleanly in context.
- **Evidence to capture** (in `notes.md`):
  - VT-CC-027 pass output.
  - `just check` summary (test count + ruff/pylint scores).
  - `lint-imports` output.
  - `validate workspace` output (or summary of remaining drift if
    any survives with explicit close-change entries).
  - PROD-004 coverage-block diff before/after.
  - `spec-driver complete delta DE-137` CLI output.

## 6. Assumptions & STOP Conditions

- **Assumptions**:
  - Skills are sourced from `supekku/skills/<skill>/SKILL.md` (per
    DR-137 §10 reconciliation of DR-136 §5.5). Edits to the
    `.spec-driver/skills/` installed copies happen via `sync` (or
    via reinstall), not by hand.
  - The exact insertion targets named in DR-137 §5.5 (e.g.
    "After 'Verify acceptance' / before 'Mark phase complete'") map
    onto identifiable headings or marker lines in the current
    SKILL.md files. If a target heading has drifted, task 5.1
    confirms the closest equivalent and surfaces the drift in
    `notes.md` rather than improvising.
  - VT-CC-027 only asserts presence of the anchor markers + the
    expected command substring inside; full-text equality with
    DR-137 §5.5 is NOT asserted, so prose adjustments around the
    gate (e.g. inline links) survive future skill refactors.
  - PROD-004 carries `supekku:verification.coverage@v1` blocks
    under each FR (consistent with the existing block convention).
    If structure differs, task 5.5 follows the PROD-004 file's
    existing pattern.
  - `spec-driver complete delta` runs coverage-completion checks
    against the DE-137 `applies_to` spec set; reconciliation in
    task 5.5 is what satisfies those checks.
- **STOP** when:
  - DR-137 §5.5 insertion target is genuinely ambiguous in the
    current SKILL.md (e.g. heading renamed and no obvious
    equivalent) — `/consult` rather than guess the location; the
    anchor marker discipline depends on a stable insertion site.
  - The installed `.spec-driver/skills/<skill>/SKILL.md` copy
    diverges from the source by more than the new gate insertion
    (i.e. the sync flow is stale and a manual reconcile would
    overwrite real edits) — STOP and surface the divergence; do
    NOT clobber with `sync` until investigated.
  - `spec-driver complete delta DE-137` rejects without `--force`
    on a coverage gap that is NOT one of the DE-137 VT-CC entries
    — investigate the missing requirement; do NOT use `--force` as
    a shortcut.
  - `validate workspace` surfaces errors against in-repo artefacts
    introduced by DE-137 itself (i.e. our own work fails the gate
    we just built) — STOP and fix at the source artefact.
  - `lint-imports` regresses on `Architectural Layers` or
    `Migrations isolation` — this phase should not touch import
    surface; a regression means something landed unintentionally.

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID  | Description | Parallel? | Notes |
| ------ | --- | --- | --- | --- |
| [x] | 5.1 | Pre-flight: locate insertion targets in 5 SKILL.md files; confirm installed-copy parity baseline | [ ] | notes.md 2026-05-19 task 5.1 entry |
| [x] | 5.2 | Insert verbatim gate text + anchor markers into 5 `supekku/skills/<skill>/SKILL.md` files | [P] | commit e6b0bde2 |
| [x] | 5.3 | Sync installed copies via `sync_skills(repo_root)`; parity verified | [ ] | bundled with 5.2 commit |
| [x] | 5.4 | Ship VT-CC-027 (`supekku/scripts/lib/skills/validate_gate_test.py`) | [P] | 5/5 cases passing; commit e6b0bde2 |
| [x] | 5.5 | Reconcile PROD-004 coverage blocks (FR-001/-002/-003/-006 → `verified` for DE-137 VTs); remove stale VT-001/-002/-003 stubs | [P] | commit 4906c163 + c85a16aa |
| [x] | 5.6 | Flip VT-CC-027 to `verified` in IP-137 `verification.coverage` after 5.4 passes | [ ] | commit 4906c163 |
| [x] | 5.7 | Acceptance gate: pytest + ruff + lint-imports + validate workspace | [ ] | All green; notes.md task 5.7 evidence |
| [x] | 5.8 | Audit (AUD-026) + ISSUE-056 + close: `complete delta DE-137 --skip-sync` (no `--force`) | [ ] | RE-041 completion revision created; DE-137 status: completed |
| [x] | 5.9 | Phase + delta wrap-up: notes.md evidence; IP-137 §9 progress boxes; final commit | [ ] | this commit |

### Task Details

- **5.1 Pre-flight: insertion-target reconnaissance**
  - **Design / Approach**: For each of the five skills, open
    `supekku/skills/<skill>/SKILL.md` and locate the insertion
    target named in DR-137 §5.5. Record line range + surrounding
    context in `notes.md`. Confirm the installed copy under
    `.spec-driver/skills/<skill>/SKILL.md` differs from source by
    only the install-time transformations (or not at all). Confirm
    `.claude/skills/<skill>/SKILL.md` / `.agents/skills/<skill>/SKILL.md`
    are symlinks (per DR-137 §10) — if not, surface as drift.
  - **Files / Components**: read-only.
  - **Testing**: n/a.
  - **Observations & AI Notes**: this protects against the "target
    heading has drifted" failure mode in §6. If §5.5 says "after
    Verify acceptance" but the current SKILL.md has "Confirm
    acceptance," capture the rename in notes.md and use the
    closest equivalent; do NOT silently improvise. Workflow.toml
    version warning (0.9.2 vs 0.9.7) gets a one-line triage entry
    here.
  - **Commits / References**: rolled into 5.2 or 5.9.

- **5.2 Insert verbatim gate text + anchor markers**
  - **Design / Approach**: For each of the five skills, edit
    `supekku/skills/<skill>/SKILL.md` to insert at the §5.1
    confirmed target:
    ```
    <!-- validate-gate:<skill> begin -->
    <verbatim text from DR-137 §5.5 for this skill>
    <!-- validate-gate:<skill> end -->
    ```
    Preserve surrounding prose. Markers go on their own lines for
    grep cleanliness. Verbatim text is the exact string from §5.5
    (no rewording, no link-ification of `spec-driver validate ...`
    — the regression test asserts the literal substring).
  - **Files / Components**: five files under `supekku/skills/`.
  - **Testing**: deferred to 5.4 (VT-CC-027); read the edited
    files manually for prose smoothness.
  - **Observations & AI Notes**: anchor name is the skill id
    literally (e.g. `validate-gate:execute-phase`), not a slug. This
    matches DR-137 §5.5 F-23 verbatim. Each insert is small (3-4
    lines including markers) so the diff is reviewable per skill.
  - **Commits / References**: `docs(DE-137): skill validate gates
    (IP-137-P05 task 5.2)` — single bundled commit across all
    five skills (small diff, single concern).

- **5.3 Sync installed copies**
  - **Design / Approach**: Run `uv run spec-driver sync` (or the
    equivalent skill-install command if `sync` does not own that
    surface). Confirm `.spec-driver/skills/<skill>/SKILL.md`
    matches `supekku/skills/<skill>/SKILL.md` (modulo any
    documented install-time transformation). Inspect
    `.claude/skills/<skill>/SKILL.md` and
    `.agents/skills/<skill>/SKILL.md` symlinks resolve to the
    expected target. Commit any reflowed installed copies.
  - **Files / Components**: `.spec-driver/skills/<skill>/SKILL.md`
    (five), symlinks under `.claude/skills/` and `.agents/skills/`.
  - **Testing**: `diff` source vs installed for each of five
    skills; expect either identity or documented install-time
    transformation only.
  - **Observations & AI Notes**: if `sync` does not propagate
    skill edits, file a follow-up (the gates still ship via source
    edits; agents using installed copies need the propagation
    path). Do not work around with manual cp.
  - **Commits / References**: bundles with 5.2 or separate
    `chore(DE-137): sync installed skill copies (IP-137-P05 task
    5.3)`.

- **5.4 Ship VT-CC-027**
  - **Design / Approach**: NEW
    `tests/supekku/skills/validate_gate_test.py` (or sibling per
    project test layout; align with existing skill tests if any).
    Parametrised pytest:
    ```python
    SKILL_GATES = [
      ("execute-phase",    "spec-driver validate file"),
      ("close-change",     "spec-driver validate workspace"),
      ("audit-change",     "spec-driver validate file"),
      ("notes",            "spec-driver validate file"),
      ("update-delta-docs","spec-driver validate file"),
    ]
    ```
    Per case: read `supekku/skills/<skill>/SKILL.md`, regex-search
    for `<!-- validate-gate:<skill> begin -->(.+?)<!-- validate-gate:<skill> end -->`
    with `re.DOTALL`, assert match exists, assert
    expected_substring in match.group(1). Fail message names the
    skill and the missing element (markers vs command string).
  - **Files / Components**: NEW
    `tests/supekku/skills/__init__.py` (if absent),
    `tests/supekku/skills/validate_gate_test.py`.
  - **Testing**: this IS the test. Run via `uv run pytest
    tests/supekku/skills/validate_gate_test.py -v`.
  - **Observations & AI Notes**: regex assertion is intentionally
    coarse — anchor presence + command substring presence. Future
    prose tweaks inside the gate survive; structural removal does
    not. Aligns with DR-137 §5.5 anchor rationale.
  - **Commits / References**: `test(DE-137): VT-CC-027 skill
    validate-gate regression (IP-137-P05 task 5.4)`.

- **5.5 Reconcile PROD-004 coverage blocks**
  - **Design / Approach**: Open
    `.spec-driver/product/PROD-004/PROD-004.md`; locate the
    `supekku:verification.coverage@v1` blocks under FR-001,
    FR-002, FR-003, FR-006 (confirm exact structure first per §6
    assumption). For each DE-137 VT in IP-137
    `verification.coverage` that targets PROD-004.FR-NNN, add (or
    update) the matching coverage entry with `status: verified`
    and a notes line citing the VT-CC-NNN id + the phase. Mirror
    the IP-137 entries verbatim where possible; expand `notes`
    to identify DE-137 as the owning delta.
    - FR-001 (template + migrate + workflow.toml + lint-imports):
      VT-CC-001/002/003/004/005/006/007/018/019/020/021/022/023/024/028/029/031/033.
    - FR-002 (validator + aliases + strict + workspace --kind):
      VT-CC-008/009/010/011/012/013/014/017/025/030/034.
    - FR-003 (validate file diagnostics + ISSUE-054 + exit-codes):
      VT-CC-016/026/027/032.
    - FR-006 (schema enums CLI): VT-CC-015 + VA-CC-001.
    Cross-check each FR's pre-DE-137 entries — keep, don't
    overwrite.
  - **Files / Components**:
    `.spec-driver/product/PROD-004/PROD-004.md`.
  - **Testing**: post-edit `uv run spec-driver validate file
    .spec-driver/product/PROD-004/PROD-004.md` clean; coverage
    block parseable (use `spec-driver` registry/inspect surface
    if available).
  - **Observations & AI Notes**: this is the substantive paperwork
    that `spec-driver complete delta DE-137` checks. Get the
    structure right before 5.8 runs. If a VT in IP-137 has not
    actually verified its target requirement (i.e. test exists but
    is xfailed), surface — do NOT mark `verified`.
  - **Commits / References**: `docs(DE-137): PROD-004 coverage
    reconciliation (IP-137-P05 task 5.5)`.

- **5.6 Flip VT-CC-027 to verified in IP-137**
  - **Design / Approach**: In
    `.spec-driver/deltas/DE-137-…/IP-137.md`, locate the
    `verification.coverage@v1` block; flip the VT-CC-027 entry's
    `status: planned` → `status: verified`; update notes to cite
    the test path. Confirm 5.4 ran green first.
  - **Files / Components**: `IP-137.md`.
  - **Testing**: `uv run spec-driver validate file
    .spec-driver/deltas/DE-137-…/IP-137.md` clean.
  - **Observations & AI Notes**: do this AFTER 5.4 commits and
    passes locally; pre-flipping is a status lie.
  - **Commits / References**: bundles with 5.4 or 5.9.

- **5.7 Acceptance gate**
  - **Design / Approach**: Run, in order:
    1. `just check` — test + ruff + format + pylint ratchet. New
       skill-gate test must be green. No regression on touched
       files (pylint per CLAUDE.md).
    2. `uv run lint-imports` — both `Architectural Layers` and
       `Migrations isolation` KEPT.
    3. `uv run spec-driver validate workspace` — clean against
       this repo; remaining warnings (if any) get explicit drift
       entries per the close-change contract before 5.8 runs.
    Capture all three outputs in `notes.md` for the audit trail.
  - **Files / Components**: as needed for cleanup.
  - **Testing**: this is the phase gate.
  - **Observations & AI Notes**: this is the first run of
    `validate workspace` exercising the full DE-137 surface as
    designed (per-kind strict map + alias canonicalisation +
    workspace-scope kind filter). Treat any new error class as a
    blocker, not a curiosity.
  - **Commits / References**: cleanups separate from feature
    commits where practical.

- **5.8 Close delta**
  - **Design / Approach**: Run
    `uv run spec-driver complete delta DE-137`. Expected: success
    without `--force`. If it rejects, the failure must point at a
    specific missing coverage entry; address in 5.5 (or in the
    relevant IP-137 row) and rerun. Do NOT pass `--force` — per
    CLAUDE.md it requires documentation + follow-up task, which
    we explicitly want to avoid by getting 5.5 right.
  - **Files / Components**: CLI invocation; potentially
    `.spec-driver/deltas/DE-137-…/DE-137.md` frontmatter
    `status` flipped by the CLI.
  - **Testing**: confirm DE-137 frontmatter `status: completed`
    post-run; confirm DE-137 disappears from
    `spec-driver list deltas -s in-progress`.
  - **Observations & AI Notes**: if `complete delta` performs
    sync/index regen as part of close, capture any drift it
    surfaces in `notes.md`. Sibling deltas DE-138..142 inherit
    the infrastructure from this delta — anything left
    inconsistent here propagates.
  - **Commits / References**: `chore(DE-137): close delta
    (IP-137-P05 task 5.8)` (or rolled into 5.9 wrap-up).

- **5.9 Phase + delta wrap-up**
  - **Design / Approach**: Update `notes.md` with:
    - VT-CC-027 pass output.
    - `just check` summary.
    - `lint-imports` output (both contracts KEPT).
    - `validate workspace` output (or remaining-drift summary).
    - PROD-004 coverage-block diff (link to commit hash for 5.5).
    - `complete delta DE-137` CLI output.
    - Hand-off note: DE-137 closed; sibling deltas DE-138..142
      can now consume `validate workspace --kind <kind> --strict`
      + `admin migrate <kind>` against this delta's infrastructure;
      OQ-137-02 (sunset target) and OQ-137-03 (JSON output) statuses
      either resolved here or filed as follow-up.
    Tick IP-137 §9 progress boxes for IP-137-P05, the VT-CC-027
    line, the PROD-004 reconciliation line, and the
    `complete delta DE-137` line. Final commit:
    `docs(DE-137): IP-137-P05 wrap-up`.
  - **Files / Components**: `notes.md`, `IP-137.md`,
    `phases/phase-05.md`.
  - **Testing**: n/a (paperwork).
  - **Observations & AI Notes**: this is the last commit on
    DE-137. Confirm the working tree is clean post-commit and
    DE-137 status is `completed`.
  - **Commits / References**: final phase + delta commit.

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| --- | --- | --- |
| DR-137 §5.5 insertion targets have drifted in current SKILL.md files; verbatim insert lands in the wrong section | Task 5.1 reconnaissance documents target locations BEFORE 5.2 edits; STOP condition triggers `/consult` on ambiguity | open |
| `spec-driver sync` does not propagate skill-source edits to installed copies; agents using installed copies miss the gate | Task 5.3 verifies parity; if propagation gap, file a follow-up (gates still ship via source) — do NOT cp manually | open |
| `complete delta DE-137` rejects on a coverage gap NOT addressed by task 5.5 (e.g. spec FR not pre-existing) | Task 5.5 mirrors IP-137 `verification.coverage` 1:1; if gap is genuine, fix in 5.5 then rerun 5.8; never `--force` | open |
| `validate workspace` surfaces an error in DE-137-owned artefacts (our own dogfood fails) | STOP per §6; fix at source artefact; this is the gate's purpose | open |
| Installed `.spec-driver/skills/` copies were hand-edited and diverge from `supekku/skills/`; `sync` would clobber real edits | Task 5.3 diff first; STOP if drift exceeds expected install-time transformation | open |
| VT-CC-027 regex is too loose (passes on stub or commented-out gate) | Test asserts both anchor marker pair AND command substring inside the bracket; commented-out anchors still match (acceptable: anchors are the contract) | mitigated |
| `workflow.toml has 0.9.2, running 0.9.7` install drift causes a behavioural surprise during acceptance | Task 5.1 triages: either run `spec-driver install` to reconcile, or document scope and STOP if behaviour diverges | open |
| OQ-137-02 (sunset target naming) and OQ-137-03 (JSON output mode) unresolved at close | DR-137 §8 gates allow either resolve-or-file-follow-up at delta close; 5.9 dispositions both | open |

## 9. Decisions & Outcomes

- `2026-05-19` — P05 sheet drafted at IP-137-P04 close. Inherits
  DR-137 v3.1 decisions: DEC-137-07 (skill tuning by direct edit
  + sync flow), DR-137 §5.5 verbatim text + F-23 anchor markers,
  DR-137 §11 VT-CC-027 specification. No new decisions yet; the
  phase rides on DR-137 §5.5 verbatim. Resolution of OQ-137-02
  and OQ-137-03 captured in 5.9 wrap-up.

## 10. Findings / Research Notes

- Task 5.1 insertion-target reconnaissance + installed-copy parity
  audit captured here.
- Workflow.toml install-version triage entry here.
- PROD-004 coverage block structure (pre-edit) captured here for
  task 5.5 design reference.
- `complete delta DE-137` CLI output captured here for audit trail.

## 11. Wrap-up Checklist

- [x] Exit criteria (all bullets in §4) satisfied.
- [x] Verification evidence stored in `notes.md` (VT-CC-027 pass
  output; pytest/ruff/lint-imports/validate workspace summary;
  PROD-004 diff via commits; `complete delta` output).
- [x] IP-137 §9 progress boxes ticked: IP-137-P05; VT-CC-001..034
  + VA-CC-001 (final state); PROD-004 coverage reconciled;
  `complete delta DE-137` succeeded.
- [x] DE-137 frontmatter `status: completed` (set by CLI in 5.8).
- [x] OQ-137-02 dispositioned (tolerated_drift via AUD-026
  FIND-012; DR-137 §10 authoritative record).
- [x] OQ-137-03 dispositioned (aligned via AUD-026 FIND-013;
  deferral conditions held; no CI-consumer demand).
- [x] FIND-010 filed as ISSUE-056 for post-closure attention.
- [x] Hand-off note in `notes.md` summarising what DE-138..142
  inherit from DE-137 infrastructure (per-kind strict map, admin
  migrate orchestrator, validate Typer group + --kind sweep,
  schema enums CLI, skill validate-gates).
