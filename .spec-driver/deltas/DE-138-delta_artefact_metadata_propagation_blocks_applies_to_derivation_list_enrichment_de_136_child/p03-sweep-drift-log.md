# IP-138-P03 sweep drift log + VA-DE138-DRIFT-001 dispositions

**Sweep step**: `v0_10_0_001_delta_blocks`
**Pre-sweep tag**: `de-138-pre-sweep` @ `46976634c9df07f731d5dcc46b165e785f7a0eba`
**Sweep commit**: `2afc0833` (data mutation only)
**Orchestrator run log** (gitignored, observability only):
`.spec-driver/run/migrations/20260520T022940Z-v0_10_0_001_delta_blocks.md`
**Inventory recovery**: orchestrator run log captures touched/skipped paths
only; drift kind detail was recovered by replaying `_transform()` against
the pre-sweep tree (`git show de-138-pre-sweep:<path>`). The committed
inventory below is therefore the authoritative durable record.

## 1. Sweep result summary

| Metric | Value |
| --- | --- |
| Candidate deltas (kind=delta in .spec-driver/deltas/) | 141 |
| Files touched | 141 |
| Files skipped (already migrated / out of scope) | 0 |
| Drift kinds observed | 5 |
| Total drift entries | 263 |

## 2. Drift kind inventory

| Kind | Count | Disposition (VA-DE138-DRIFT-001) | Rationale |
| --- | --- | --- | --- |
| `body_renumber` | 118 | `auto_resolved` | Structural top-level §§8-9 → §§7-8 renumbering; the sweep itself is the resolution (DR-138 §9.2 + F-138-D). No further action; no cross-reference rewriting expected because deltas reference each other by ID, not by section anchor. |
| `body_risk_narrative` | 137 | `dl_filed` | Full §7 prose captured per entry; reconciliation patch lives in P03.6 reconciliation commit (VA-DE138-RISK-RECON-001); per-entry outcomes recorded inline in that VA's commit. Net durable filing = the reconciliation commit + this drift log. |
| `context_input_unmapped_type` | 3 | `accepted_noise` | All 3 entries are DE-006 plain-string `context_inputs[]` promoted to tolerated_alias `unknown` (DR-138 §5.1). Acceptable post-sweep; P04 strict-flip exposes them under `--no-tolerated-aliases` for operator re-classification (DEC-138-14 wiring). No data loss, no immediate operator action. |
| `fm_requirements_unmatched` | 2 | `dl_filed` | DE-020 (ISSUE-025) + DE-106 (5× PROD-006 requirements). Filed as DL-048.002 + DL-048.003 with per-entry recommendations. The migration step preserved block as canonical (DEC-138-11); FM signal recorded in DL-048 for follow-up block amendment. |
| `fm_specs_unmatched` | 3 | `dl_filed` | DE-016 (PROD-011) + DE-020 (PROD-010, SPEC-110, SPEC-113) + DE-106 (PROD-006, PROD-011). Filed as DL-048.001 / .002 / .003. |

All 5 drift kinds disposed. VA-DE138-DRIFT-001 done criterion satisfied
(DR-138 §10.2).

## 3. Full inventory — body_renumber (118)

All 118 entries are top-level heading renumbers following `## 7. Risks &
Mitigations` deletion per DR-138 §9.2. Shape: `shifted top-level headings:
N->M, ...`. Files (canonical paths):

```
DE-002 DE-003 DE-004 DE-005 DE-006 DE-007 DE-008 DE-009 DE-010 DE-011
DE-012 DE-013 DE-014 DE-015 DE-016 DE-017 DE-018 DE-019 DE-020 DE-021
DE-022 DE-023 DE-024 DE-025 DE-026 DE-027 DE-028 DE-029 DE-030 DE-031
DE-032 DE-033 DE-034 DE-035 DE-036 DE-037 DE-038 DE-039 DE-040 DE-041
DE-042 DE-043 DE-044 DE-045 DE-046 DE-047 DE-048 DE-049 DE-050 DE-051
DE-052 DE-053 DE-054 DE-055 DE-056 DE-057 DE-058 DE-059 DE-060 DE-061
DE-062 DE-063 DE-064 DE-065 DE-066 DE-067 DE-068 DE-069 DE-070 DE-071
DE-072 DE-073 DE-074 DE-075 DE-076 DE-077 DE-078 DE-079 DE-080 DE-081
DE-082 DE-083 DE-084 DE-085 DE-086 DE-087 DE-088 DE-089 DE-090 DE-091
DE-092 DE-093 DE-094 DE-095 DE-096 DE-097 DE-098 DE-099 DE-100 DE-101
DE-102 DE-103 DE-104 DE-105 DE-106 DE-108 DE-109 DE-110 DE-111 DE-112
DE-113 DE-114 DE-115 DE-116 DE-117 DE-118 DE-119
```

23 deltas did NOT need renumbering (their pre-sweep §§7-9 already matched
target shape OR they had non-standard body shapes already): DE-107
(spike), DE-120..DE-142 (recent deltas already authored at target shape).

## 4. Full inventory — context_input_unmapped_type (3)

```
DE-006: 'ISSUE-007 documentation and evidence' -> unknown
DE-006: 'Existing --json implementation in create spec command' -> unknown
DE-006: 'Agent workflow requirements from PROD-001 and PROD-002' -> unknown
```

Each was a plain-string `context_inputs[]` entry. Migration normalised to
`{type: unknown, id: <string>}` (DR-138 §5.3). DE-006 is `status:
completed`; re-classification is operator polish, not blocking.

## 5. Full inventory — fm_requirements_unmatched (2)

```
DE-020: FM applies_to.requirements ['ISSUE-025'] not in block.requirements
DE-106: FM applies_to.requirements ['PROD-006.FR-001', 'PROD-006.FR-003',
        'PROD-006.FR-004', 'PROD-006.FR-005', 'PROD-006.NF-002']
        not in block.requirements
```

DE-020 ISSUE-025: ISSUE-* in `applies_to.requirements` is a legacy
authoring convention (pre-ADR-002). Filed as DL-048.002.
DE-106 PROD-006 family: real coverage gap — block was sparse, FM
carried the truth. Filed as DL-048.003.

## 6. Full inventory — fm_specs_unmatched (3)

```
DE-016: FM applies_to.specs ['PROD-011'] not in block.specs.primary ∪ collaborators
DE-020: FM applies_to.specs ['PROD-010', 'SPEC-110', 'SPEC-113'] not in block
DE-106: FM applies_to.specs ['PROD-006', 'PROD-011'] not in block
```

All 3 filed as DL-048.001 / .002 / .003 with per-target recommendations.

## 7. Full inventory — body_risk_narrative (137)

Full §7 prose was captured per delta during the sweep. The narrative text
is not duplicated here (137 entries × ~5–15 risks each = >1500 risk
prose blocks); the canonical recovery anchor is `git show
de-138-pre-sweep:<path>`. The reconciliation commit (P03.6,
VA-DE138-RISK-RECON-001) applies a per-entry outcome
(`keep_into_mitigation` / `drop_duplicative` / `file_dl`) into the
migrated `risk_register@v1` blocks for each delta.

Files affected (137): all 141 swept deltas EXCEPT 4 with no §7 Risks
section pre-sweep:
- DE-107 (spike)
- DE-118 (block already canonical)
- DE-136 / DE-137 / DE-138 (recent program deltas authored at target
  shape; DE-138 itself round-trips because its DR-138 §7 narrative was
  authored into the relationships block from the start)

VA-DE138-RISK-RECON-001 dispositions land in P03.6 commit; this drift
log records that the work is delegated to the companion VA, not deferred
to backlog.

## 8. VA-DE138-DRIFT-001 closure

- All 5 drift kinds have a disposition (§2 table).
- Persistent drift filed in DL-048 (3 entries, status `open`, owner
  unassigned, recommendations recorded).
- This document is the durable record per DR-138 §10.2 done criterion.
- Operator sign-off: see commit message of this commit.

## 9. Follow-ups

- DL-048.001 / .002 / .003 — block amendments for DE-016 / DE-020 /
  DE-106. Reviewed during cleanup delta (DR-138 §15.1) or earlier if
  PROD-006 / PROD-010 / PROD-011 coverage queries surface the gap.
- P04 strict-flip with `--no-tolerated-aliases` will surface DE-006's
  3× tolerated `unknown` entries for re-classification (acceptable to
  defer until that flip).
- Pre-existing run log (`.spec-driver/run/migrations/...`) is
  gitignored and may be pruned per operator policy.
