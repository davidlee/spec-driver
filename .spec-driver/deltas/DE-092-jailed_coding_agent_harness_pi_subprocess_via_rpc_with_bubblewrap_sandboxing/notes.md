# Notes for DE-092

## Adversarial Review Findings (2026-03-14)

### 1. No protocol versioning — HIGH
The RPC protocol has no version negotiation, no handshake, no ready signal.
The Python client must handle unknown event types from future pi versions.
**Resolution**: Two-phase detection.
  (a) Pre-flight: `pi --version` with semver parse, reject < 0.57.1
  (b) Startup canary: send `get_state` with 5s timeout after spawn, confirms RPC readiness
  (c) Forward compat: unknown event types silently dropped (dispatch on `type`, ignore unknown)
**Status**: resolved — update DR

### 2. stderr unhandled — HIGH
RPC mode uses stdout only. Node.js, extensions, and bwrap can all write to
stderr. Unread stderr pipe → deadlock. Inherited stderr → TUI corruption.
**Resolution**: Async stderr reader → log file + one-shot TUI notification.
  (a) stderr=PIPE, dedicated asyncio task reads lines continuously
  (b) All lines appended to `.spec-driver/agent-stderr.log`
  (c) First stderr line per session triggers TUI notification ("⚠ Agent stderr — see agent-stderr.log")
  (d) Subsequent lines logged silently to avoid noise
**Status**: resolved — update DR

### 3. Subprocess lifecycle gaps — MEDIUM
No startup failure detection, crash recovery, signal forwarding strategy,
or orphan process handling (especially unsandboxed macOS).
**Resolution**:
  (a) Startup failure: proc.poll() during get_state canary wait; if exited, surface exit code + stderr
  (b) Crash recovery: EOF on stdout → show error + last stderr lines, no auto-restart, offer --continue
  (c) Graceful shutdown: abort (2s) → shutdown (3s) → SIGTERM (2s) → SIGKILL. Close stdin after shutdown.
  (d) Signal forwarding: Ctrl+C → send RPC abort (not signal). SIGTERM → graceful shutdown sequence.
      bwrap --new-session means signals can't reach jail anyway.
  (e) Orphan handling: bwrap --die-with-parent for sandboxed. atexit + proc.kill() for unsandboxed.
      Linux: pdeathsig via preexec_fn as belt-and-suspenders.
**Status**: resolved — update DR

### 4. Extension circular dependency — MEDIUM
Jailed pi calls spec-driver CLI inside jail while host spec-driver manages
the session. Concurrent writes possible. TS extension needs pi types
available inside jail. Consider --append-system-prompt + tools-dir instead.
**Resolution**: Eliminate the TS extension; do everything host-side or via pi CLI flags.
  (a) Context injection: static via --append-system-prompt at launch. Host-side Python
      generates context string from active delta/phase/governance before spawning pi.
      Sufficient because agent sessions are scoped to a single delta/phase; user starts
      new session on context change.
  (b) spec-driver tool: register via project-local .pi/tools/ directory (not an extension).
      This is a shell wrapper — no TS types needed.
  (c) Artifact observation: host-side Python. RPC event stream already contains
      tool_execution_end with tool name + args. Reuse existing classify_path() and
      event-emitting code (artifact_event.py pattern) directly in the RPC client.
      No in-jail hook needed.
  (d) Session tracking: host Python process owns the session — pass session ID directly
      to event system. Same pattern as SPEC_DRIVER_SESSION env var but without the
      env indirection.
  (e) Future dynamic injection: if mid-session context refresh proves necessary, revisit
      the TS extension then. For now, static + tool access covers the need.
**Status**: resolved — update DR

### 5. bwrap security gaps — MEDIUM
`--ro-bind /usr /usr` exposes all host binaries. No seccomp. PATH forwarded.
User namespaces disabled by default on Debian/Ubuntu < 24.04. This is
damage-limitation, not a security boundary.
**Resolution**: Documentation fix, not code fix. Accept and be honest.
  (a) DR must state threat model: sandbox prevents accidental filesystem damage,
      not determined exfiltration. Never overstate the security posture.
  (b) Nix path (closure-only mounts) is the hardened option; bwrap is pragmatic fallback.
  (c) Security model can evolve later (seccomp, tighter mounts, network policy) based on
      security appetite and task. Profiles already allow per-use-case tuning.
  (d) Note user namespace availability as known limitation with distro-specific docs.
**Status**: resolved — update DR

### 6. TUI LOC estimate unrealistic — MEDIUM
~500 LOC is too low. Streaming markdown, tool call rendering, extension UI
proxy, input editor, status bar, abort handling → 1000-1500 LOC minimum.
**Resolution**: Correct estimate, phasing already handles it.
  Phase 1 (plain text streaming, tool call names, basic input): ~500-700 LOC
  Phase 2 (markdown, collapsible results, status bar): +500-800 LOC
  Total: ~1000-1500 LOC. No extension UI proxy needed (finding #4 eliminated TS extension).
  Update DR component estimate from ~500 to ~1000-1500 across phases.
**Status**: resolved — update DR

### 7. Profile passthrough unspecified for non-Nix — LOW
sandbox.py described as single-profile but Phase 3 adds --profile flag.
Need to decide: profiles in sandbox.py from start, or defer and document.
**Resolution**: Defer. sandbox.py ships with specDev-equivalent only.
  --profile flag only effective with Nix-managed jails. Documented limitation.
  Adding profiles to sandbox.py is ~20 lines if demand appears.
**Status**: resolved — update DR

### 8–10: deferred
Remaining findings (session portability, API key exposure, health check)
deferred along with the delta. See "Delta Parked" note below.

---

## Delta Parked (2026-03-14)

Adversarial review complete. Design is sound but premature. The value
proposition needs real-world friction to justify the build cost.

**Immediate next steps (no harness needed):**
1. Explore pi extensions, prompts, hooks, context management
2. Get agent workflow on par with Claude Code (artifact events, boot context)
3. Explore intelligent compaction — possible spec-driver tie-ins
4. Feel out gaps that motivate the harness as necessary

**Concrete deliverables that DON'T need the harness:**
- Shell wrapper for context injection (~3 lines)
- Pi extension for artifact observation (~80 LOC TS, mirrors artifact_event.py)
- Profile-aware jailed-pi usage via existing flake infrastructure

**Reactivation trigger:** repeated manual friction that the harness would
automate — specifically delta-scoped session management, or multi-agent
orchestration needs.

The DR and adversarial findings are preserved for when that happens.
