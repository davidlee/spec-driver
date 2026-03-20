
Below is a spec-driver-specific additive schema set in YAML/TOML terms.

Design goals:

* **no breaking changes** to existing DE/IP/phase schemas
* prefer **new sibling artefacts** under a dedicated workflow directory
* only add **small optional fenced YAML blocks** to existing markdown where there is clear value
* keep event-driving state in **separate `.yaml` files** for easy file watching
* separate **handover resilience** from **review bootstrap amortization**

This fits the existing pattern where DE/IP already carry frontmatter plus fenced YAML schema blocks, phase progress is tracked in markdown, `notes.md` is the human-facing handover surface, and the current continuation skill updates notes and emits the next-agent prompt. ([GitHub][1])

## Proposed directory additions

Add a sibling workflow directory inside each delta bundle:

```text
.spec-driver/deltas/DE-090-.../
  DE-090.md
  IP-090.md
  notes.md
  phases/
    ...
  workflow/
    state.yaml
    handoff.current.yaml
    review-index.yaml
    review-findings.yaml
    sessions.yaml
    review-bootstrap.md
```

This is additive: DE/IP/notes/phases remain authoritative for human workflow, while `workflow/*.yaml` becomes the machine-facing control plane. That separation matches your current setup where DE/IP are structured markdown artefacts, `notes.md` is a running narrative, and continuation currently writes onboarding material there. ([GitHub][1])

---

## 1. Global policy file

Use `.spec-driver/workflow.toml` for configuration.

### `.spec-driver/workflow.toml`

```toml
version = 1

[workflow]
state_dir = "workflow"
handoff_boundary = "phase"
render_continuation_prompt = true
update_notes_new_agent_instructions = true
default_next_role = "implementer"

[watch]
enabled = true
paths = [
  ".spec-driver/deltas/**/workflow/*.yaml",
  ".spec-driver/deltas/**/notes.md",
  ".spec-driver/deltas/**/phases/*.md",
]

[review]
persistent_session = true
bootstrap_cache = true
teardown_on = ["approved", "abandoned"]
recreate_on = ["major_scope_change", "cache_stale", "session_unrecoverable"]

[review.bootstrap]
include_delta = true
include_plan = true
include_active_phase = true
include_notes = true
include_findings = true
include_changed_files = true
max_historical_rounds = 2
```

### Semantics

* pure policy/config, not per-artifact state
* safe to load once at CLI start
* can later grow per-user/per-agent sections without changing artefact schemas

---

## 2. Workflow state schema

This is the minimal machine-readable current truth for an artefact.

### File

`workflow/state.yaml`

### Schema id

`supekku:workflow.state@v1`

### Purpose

* current orchestration status
* current role
* current phase
* pointers to latest related files
* event-friendly summary for dashboards/watchers

### Proposed schema

```yaml
schema: supekku.workflow.state
version: 1

artifact:
  id: DE-090
  kind: delta
  path: .spec-driver/deltas/DE-090-cli_relational_navigation_filters_show_output_and_cross_entity_queries
  notes_path: .spec-driver/deltas/DE-090-cli_relational_navigation_filters_show_output_and_cross_entity_queries/notes.md

plan:
  id: IP-090
  path: .spec-driver/deltas/DE-090-cli_relational_navigation_filters_show_output_and_cross_entity_queries/IP-090.md

phase:
  id: IP-090.PHASE-05
  path: .spec-driver/deltas/DE-090-cli_relational_navigation_filters_show_output_and_cross_entity_queries/phases/phase-05.md
  status: complete

workflow:
  status: awaiting_review
  active_role: implementer
  next_role: reviewer
  handoff_boundary: phase

pointers:
  current_handoff: workflow/handoff.current.yaml
  review_index: workflow/review-index.yaml
  review_findings: workflow/review-findings.yaml
  sessions: workflow/sessions.yaml
  review_bootstrap: workflow/review-bootstrap.md

timestamps:
  created: 2026-03-21T10:00:00Z
  updated: 2026-03-21T10:30:00Z
```

### Required fields

* `schema`
* `version`
* `artifact.id`
* `artifact.kind`
* `workflow.status`
* `workflow.active_role`
* `phase.id`

### Allowed enums

* `artifact.kind`: `delta | plan | revision | audit | task | other`
* `phase.status`: `not_started | in_progress | blocked | complete | skipped`
* `workflow.status`: `planned | implementing | awaiting_review | reviewing | changes_requested | approved | blocked | archived`
* `workflow.active_role`: `architect | implementer | reviewer | operator | other`

### Notes

This does not replace DE/IP status. It is orchestration state only. Existing DE/IP status fields stay untouched. That keeps the existing artefacts stable while giving the CLI a single file to read. DE/IP already carry their own IDs, status, linked specs, phases, and verification coverage, so this file should remain intentionally small. ([GitHub][1])

---

## 3. Current handoff schema

This is the durable phase-boundary transition payload.

### File

`workflow/handoff.current.yaml`

### Schema id

`supekku:workflow.handoff@v1`

### Purpose

* resilient next-step state
* deterministic input to continuation prompt rendering
* trigger file for orchestration

### Proposed schema

```yaml
schema: supekku.workflow.handoff
version: 1

artifact:
  id: DE-090
  kind: delta

transition:
  from_role: implementer
  to_role: reviewer
  boundary: phase
  status: awaiting_review

phase:
  id: IP-090.PHASE-05
  status: complete

required_reading:
  - .spec-driver/deltas/DE-090-cli_relational_navigation_filters_show_output_and_cross_entity_queries/DE-090.md
  - .spec-driver/deltas/DE-090-cli_relational_navigation_filters_show_output_and_cross_entity_queries/IP-090.md
  - .spec-driver/deltas/DE-090-cli_relational_navigation_filters_show_output_and_cross_entity_queries/phases/phase-05.md
  - .spec-driver/deltas/DE-090-cli_relational_navigation_filters_show_output_and_cross_entity_queries/notes.md

related_documents: []

key_files:
  - supekku/cli/common.py
  - supekku/core/relation_types.py

verification:
  commands:
    - uv run pytest
    - ruff check .
  summary: 3955 tests passing; ruff clean except pre-existing UP042
  status: pass

git:
  head: e31eca9
  branch: null
  worktree:
    has_uncommitted_changes: true
    has_staged_changes: false

open_items:
  - id: OI-001
    kind: next_step
    summary: Implement Phase 06 neighbourhood view
    blocking: false

design_tensions: []
unresolved_assumptions: []
decisions_to_preserve: []

next_activity:
  kind: review
  summary: Resume persistent reviewer and assess Phase 05 output

timestamps:
  emitted_at: 2026-03-21T10:30:00Z
```

### Required fields

* `schema`
* `version`
* `artifact.id`
* `transition.from_role`
* `transition.to_role`
* `phase.id`
* `required_reading`
* `next_activity.kind`

### Allowed enums

* `transition.boundary`: `phase | task | manual`
* `transition.status`: `awaiting_review | changes_requested | ready_for_implementation | approved | blocked`
* `verification.status`: `pass | fail | partial | not_run | unknown`
* `next_activity.kind`: `implementation | review | architecture | verification | operator_attention`

### Notes

This is the structured equivalent of what the continuation skill already asks the agent to write: required reading, related docs, key files, decisions, loose ends, commit-state guidance, and the next logical activity. The schema simply moves that into a stable file without removing the human-readable notes surface. ([GitHub][2])

---

## 4. Review index schema

This is the reviewer bootstrap cache: what the reviewer has already learned and should not have to rediscover.

### File

`workflow/review-index.yaml`

### Schema id

`supekku:workflow.review-index@v1`

### Purpose

* amortize review bootstrap cost
* preserve domain map and invariants
* survive session death
* support recreation of reviewer from cache

### Proposed schema

```yaml
schema: supekku.workflow.review-index
version: 1

artifact:
  id: DE-090
  kind: delta

review:
  session_scope: artifact
  bootstrap_status: warm
  last_bootstrapped_at: 2026-03-21T10:25:00Z
  source_handoff: workflow/handoff.current.yaml

domain_map:
  - area: cli
    purpose: command routing and filter orchestration
    files:
      - supekku/cli/common.py
      - supekku/cli/show.py

  - area: relation_collection
    purpose: collecting references and reverse-reference targets
    files:
      - supekku/core/relation_types.py

invariants:
  - id: INV-001
    summary: JSON list/show output should stay contract-consistent for backlog items
  - id: INV-002
    summary: Reverse lookup features must preserve existing skinny-CLI patterns

risk_areas:
  - id: RA-001
    summary: Reverse lookup logic may miss domain-field references
    files:
      - supekku/core/relation_types.py

review_focus:
  - output contract stability
  - correctness of reverse-reference partitioning
  - alias/conflict handling

known_decisions:
  - id: KD-001
    summary: reviewer should treat requirements as using uid not id where relevant

staleness:
  cache_key:
    phase_id: IP-090.PHASE-05
    head: e31eca9
  invalidation_triggers:
    - major_scope_change
    - dependency_surface_expanded
    - artifact_rebased
```

### Required fields

* `schema`
* `version`
* `artifact.id`
* `review.bootstrap_status`
* `domain_map`
* `staleness.cache_key`

### Allowed enums

* `review.session_scope`: `artifact | phase | task`
* `review.bootstrap_status`: `cold | warming | warm | stale`

### Notes

This schema addresses the part you flagged explicitly: structured handoff is not enough to make review efficient. The reviewer needs a maintained cache of dependency surface, invariants, and already-learned architecture. This file is that cache. It complements, rather than replaces, the handoff. The need for review-oriented context is consistent with the continuation skill’s instruction to preserve unresolved assumptions, questions, and design tensions for implementation-adjacent next steps. ([GitHub][2])

---

## 5. Review findings schema

This is the stable issue ledger across review rounds.

### File

`workflow/review-findings.yaml`

### Schema id

`supekku:workflow.review-findings@v1`

### Purpose

* track findings across rounds
* avoid re-litigating fixed issues
* let implementer respond against stable IDs
* let reviewer session be resumed or recreated efficiently

### Proposed schema

```yaml
schema: supekku.workflow.review-findings
version: 1

artifact:
  id: DE-090
  kind: delta

review:
  round: 3
  status: changes_requested
  reviewer_role: reviewer

blocking:
  - id: R3-001
    title: Output mode regression for downstream scripts
    summary: New reverse-reference output changes a field relied on by existing JSON consumers
    status: open
    files:
      - supekku/cli/output.py
    related_invariants:
      - INV-001

non_blocking:
  - id: R3-002
    title: Add regression test for audit reverse lookups
    summary: Coverage gap; behavior appears correct
    status: open
    files:
      - tests/cli/show_test.py

resolved:
  - id: R2-001
    title: Requirement identifier mismatch
    status: resolved
    resolution_summary: Switched requirements partition logic to use uid

waived: []

history:
  - round: 1
    summary: Initial review of reverse-reference filtering
  - round: 2
    summary: Follow-up after alias conflict fixes

timestamps:
  updated: 2026-03-21T10:35:00Z
```

### Required fields

* `schema`
* `version`
* `artifact.id`
* `review.round`
* `review.status`

### Allowed enums

* `review.status`: `not_started | in_progress | changes_requested | approved | blocked`
* finding `status`: `open | resolved | waived | superseded`

### Notes

This should be the main structured input for an implementer returning from review, not a replay of prose comments. It mirrors the stable issue-ledger pattern you want for multi-round review. The repo’s current notes already preserve phase findings and “next” guidance in prose; this adds the missing machine-readable layer without changing that habit. ([GitHub][3])

---

## 6. Sessions schema

This is runtime state for tmux/jail orchestration.

### File

`workflow/sessions.yaml`

### Schema id

`supekku:workflow.sessions@v1`

### Purpose

* map roles to live or paused sessions
* support watchdog/reconciliation logic
* keep ephemeral process metadata out of notes

### Proposed schema

```yaml
schema: supekku.workflow.sessions
version: 1

artifact:
  id: DE-090
  kind: delta

sessions:
  implementer:
    session_name: sd-DE-090-impl
    sandbox: pi-mono
    status: paused
    last_seen: 2026-03-21T10:20:00Z

  reviewer:
    session_name: sd-DE-090-review
    sandbox: gemini-review
    status: active
    last_seen: 2026-03-21T10:34:00Z

  architect:
    session_name: null
    sandbox: null
    status: absent
    last_seen: null
```

### Allowed enums

* session `status`: `active | paused | absent | dead | unknown`

### Notes

This is optional but useful if the CLI is driving tmux and bubblewrap directly.

---

## 7. Review bootstrap markdown companion

This is intentionally not YAML-only.

### File

`workflow/review-bootstrap.md`

### Purpose

* human-readable reviewer briefing
* compiled from DE/IP/phase/notes/handoff/review-index/review-findings
* can be fed directly to a recreated reviewer session

### Recommended structure

```md
# Review Bootstrap for DE-090

## Current Scope
...

## Dependency Surface
...

## Invariants to Protect
...

## Open Findings
...

## Areas Not Yet Reviewed
...

## Current Diff / Commit Context
...
```

This is the projection layer for reviewer efficiency. It should be regenerated from the YAML sources and the current repo state, not edited by hand.

---

## 8. Minimal additive changes to existing markdown artefacts

### `notes.md`

Do not restructure the whole file. Add one optional fenced block under a stable heading.

````md
## New Agent Instructions

```yaml
schema: supekku.workflow.notes-bridge
version: 1
artifact: DE-090
workflow_state: workflow/state.yaml
current_handoff: workflow/handoff.current.yaml
review_index: workflow/review-index.yaml
review_findings: workflow/review-findings.yaml
review_bootstrap: workflow/review-bootstrap.md
````

````

Why this shape:
- preserves the continuation skill’s current contract of maintaining a “New Agent Instructions” section in `notes.md` :contentReference[oaicite:6]{index=6}
- keeps the prose section intact
- gives a deterministic bridge from human notes to machine state
- avoids moving orchestration state into frontmatter or forcing wholesale notes reformatting

### Phase sheets
Add an optional fenced YAML block if desired.

```md
## Workflow

```yaml
schema: supekku.workflow.phase-bridge
version: 1
phase: IP-090.PHASE-05
status: complete
handoff_ready: true
review_required: true
current_handoff: ../workflow/handoff.current.yaml
````

```

This is additive and lets the CLI determine whether a phase close should emit a handoff.

### DE/IP
No schema change required.

DE already includes frontmatter plus a fenced relationships block, and IP already includes overview and verification coverage blocks with phase IDs and VT entries. Those should remain the source of design and planning truth. :contentReference[oaicite:7]{index=7}

---

## 9. Ownership model

To keep edits deterministic:

- `DE-*.md`: design/intent owner
- `IP-*.md`: plan/verification owner
- `phases/*.md`: per-phase execution owner
- `notes.md`: human narrative + onboarding prose
- `workflow/state.yaml`: CLI owns
- `workflow/handoff.current.yaml`: continuation/handoff command owns
- `workflow/review-index.yaml`: review-prime command owns
- `workflow/review-findings.yaml`: reviewer command/session owns
- `workflow/sessions.yaml`: session manager owns
- `workflow/review-bootstrap.md`: generated, not hand-edited

---

## 10. Validation rules

Recommended validation stance:

### Hard validation
Applies to:
- `workflow/*.yaml`
- fenced `notes-bridge` block
- fenced `phase-bridge` block

Rules:
- `schema` and `version` required
- unknown top-level keys allowed by default only if `x-` prefixed
- all path fields must be relative to artefact root or repo root
- IDs must match known artefact ID patterns where applicable

### Soft validation
Applies to:
- prose sections in `notes.md`
- `review-bootstrap.md`

Reason:
Your existing workflow values readable prose; only the machine-facing surfaces need strict schema validation.

---

## 11. Event model

These file changes are useful watch events:

- `workflow/handoff.current.yaml` changed  
  -> resume/create next role session

- `workflow/review-findings.yaml` changed  
  -> implementer has actionable review output

- `workflow/state.yaml` changed  
  -> dashboard/status refresh

- `phases/*.md` phase bridge changed to `handoff_ready: true`  
  -> emit new handoff

This is why file separation is preferable for the control plane.

---

## 12. Compatibility summary

This proposal is additive because it does **not** require:
- changing DE frontmatter
- changing IP overview/verification schemas
- replacing `notes.md`
- replacing the continuation skill’s human-facing behavior

It only asks for:
- a new `workflow/` sibling directory
- one optional YAML bridge block in `notes.md`
- optional YAML bridge blocks in phase sheets
- continuation to write both prose and `handoff.current.yaml`

That keeps the existing workflow artefacts recognizable and stable while giving the CLI the machine-readable control plane it currently lacks.

## Suggested next step

The next practical move is to codify the exact field-level constraints for these four schema IDs:

- `supekku.workflow.state`
- `supekku.workflow.handoff`
- `supekku.workflow.review-index`
- `supekku.workflow.review-findings`

and then update continuation so it writes `workflow/handoff.current.yaml` plus the small `notes.md` bridge block.
```

