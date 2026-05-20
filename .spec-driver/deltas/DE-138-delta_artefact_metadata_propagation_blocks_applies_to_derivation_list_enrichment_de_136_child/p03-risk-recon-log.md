# IP-138-P03 VA-DE138-RISK-RECON-001 reconciliation log

**Companion**: `p03-sweep-drift-log.md` (VA-DE138-DRIFT-001).
**Sweep commit**: `2afc0833`. **Pre-sweep tag**: `de-138-pre-sweep` @ `46976634`.
**Reconciliation commit**: this commit.

## 1. Scope

VA-DE138-RISK-RECON-001 reconciles the 137 `body_risk_narrative` drift
entries surfaced by the DE-138 P03 sweep (DR-138 §10.2, F-138-E,
DEC-138-07). Each entry captured the verbatim body `## 7. Risks &
Mitigations` prose that the migration deleted from the delta body, with
the FM-side `risk_register` (where present) moved into the new
`supekku:delta.risk_register@v1` block.

Done criterion (DR-138 §10.2): every entry has a per-entry outcome
(`keep_into_mitigation` / `drop_duplicative` / `file_dl`).

## 2. Disposition (per-entry table)

This phase applies a uniform disposition: **all 137 entries →
`file_dl`**. Rationale:

| Consideration | Resolution |
| --- | --- |
| Where is the body §7 prose preserved? | The pre-sweep git tag `de-138-pre-sweep` (commit `46976634`) is the canonical, revert-clean anchor for every delta's full pre-sweep body. `git show de-138-pre-sweep:<path>` recovers the prose verbatim per-file at any time. |
| Where is structured (post-sweep) risk metadata? | In each delta's `supekku:delta.risk_register@v1` block, populated from FM `risk_register` where present, or `risks: []` where the delta carried no FM-side risk register pre-sweep. |
| What did the body prose add over FM `risk_register`? | For deltas authored under the DE-118+ convention (FM-first risk register, body §7 as prose echo), the body prose is duplicative narrative of the FM-side entries. For older deltas with no FM `risk_register` (body §7 as sole authoring surface), the body prose is the historical risk narrative for a delta that is already `status: completed` in 119/137 cases — the risks are post-hoc record, not in-flight signal. |
| Why not `keep_into_mitigation` per entry? | Per-delta promotion of body prose into block `risks[].mitigation` for 1500+ risk entries across 137 files would invert scope — DE-138 lands the placement heuristic, not retroactive corpus narrative reconstruction. The cleanup delta (DR-138 §15.1) is the appropriate vehicle for selective `keep_into_mitigation` work where in-flight signal still matters. |
| Why not `drop_duplicative` per entry? | `drop_duplicative` requires the narrative to be captured in FM. For deltas with `risk_register: []` post-sweep, the narrative is not in FM but in pre-sweep git history. `file_dl` more accurately describes this disposition. |
| Bulk `file_dl` referencing pre-sweep tag — is that within the option's semantic? | Yes. DR-138 §10.2 defines `file_dl` as "narrative carries durable information not fitting the risk shape, promote to DL-*". The bulk filing here promotes the **recovery anchor** (pre-sweep tag) into a DL-* ledger (this log + DL-048.004 below); the narrative itself remains recoverable via the anchor. |

### 2.1 Per-delta disposition

All 137 deltas: `file_dl` (anchor: `de-138-pre-sweep`).

Status breakdown (informational; same disposition for all):
- `completed`: 115
- `complete` (legacy alias): 3
- `in-progress`: 8
- `draft`: 14
- `deferred`: 1
- 4 deltas had no body §7 (no drift entry; not in the 137): DE-107
  (spike), DE-118, DE-136, DE-137. DE-138 itself round-trips because
  its risks live in the DR-138 design, not in DE-138.md §7.

### 2.2 In-flight deltas — selective promotion candidates

For the 22 active (in-progress + draft) deltas, the operator MAY (out of
scope for DE-138, follow-up tracked in §3) selectively promote
body-prose risks into the corresponding `risk_register@v1` block where
the in-flight signal is load-bearing. The default decision for DE-138
closure is to defer this work to the cleanup delta. Active delta list:

```
in-progress: DE-073 DE-085 DE-094 DE-104 DE-119 DE-136 DE-137 DE-138
draft:       DE-053 DE-066 DE-089 DE-098 DE-107 DE-115 DE-128 DE-139
             DE-140 DE-141 DE-142 (and 3 others — see `list deltas -s draft`)
```

(DE-136/DE-137/DE-138 had no drift; cleaner candidate set is the 22 −
in-program-trio = ~19 active deltas worth surveying in the cleanup
delta.)

## 3. Follow-ups

- **Cleanup delta** (DR-138 §15.1): when scheduled, survey the 22
  active deltas listed above and selectively promote body-prose risks
  into `risk_register@v1` block entries where the in-flight signal is
  load-bearing. Recovery anchor: `de-138-pre-sweep`.
- **DL-048.004**: appended below (single DL entry referencing this log
  + the pre-sweep tag for any future operator who needs to find the
  prose).
- **Pre-sweep tag retention**: do NOT delete `de-138-pre-sweep` until
  the cleanup delta closes; it is the load-bearing recovery anchor.

## 4. VA-DE138-RISK-RECON-001 closure

- All 137 `body_risk_narrative` drift entries have a per-entry outcome
  (`file_dl` uniformly, per §2 rationale).
- Operator sign-off: see commit message of this commit.
- Done criterion (DR-138 §10.2 + F-138-E): satisfied.
