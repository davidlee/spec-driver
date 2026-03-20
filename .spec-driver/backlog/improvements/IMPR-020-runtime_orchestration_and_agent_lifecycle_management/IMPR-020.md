---
id: IMPR-020
name: Runtime orchestration and agent lifecycle management
created: "2026-03-21"
updated: "2026-03-21"
status: idea
kind: improvement
tags:
  - orchestration
  - downstream-of-IMPR-019
---

# Runtime Orchestration and Agent Lifecycle Management

## Relationship

Downstream of IMPR-019 (handover and review orchestration). Consumes the
workflow schemas and CLI command semantics defined there as inputs.

## Objective

Design and implement the runtime layer that manipulates and observes
spec-driver workflow state safely across real agent processes.

IMPR-019 covers layers 1–2 (workflow semantics + file-based control plane).
This improvement covers layers 3–5: orchestration runtime, agent/harness
adapters, and policy.

## Scope

### Layer 3: Orchestration Runtime

- Supervisor model (centralized vs cooperative)
- Process/session lifecycle: spawn, resume, detach, observe, tear down
- Signal handling and shutdown semantics
- IPC/event transport (file-based mailbox, sockets, or hybrid)
- Sandbox abstraction (bubblewrap, macOS sandbox-exec, none)
- Failure domains and recovery
- Logging, telemetry, and reconciliation

### Layer 4: Agent/Harness Adapter

- Concrete support for: Claude Code, pi, Gemini CLI, Codex
- Harness-specific configuration installation (extensions, skills, prompts)
- Continuation and review-prime hooks per harness
- Subagent lifecycle and topology

### Layer 5: Policy

- Model/role assignment (which model is implementer vs reviewer)
- Reviewer persistence policy (artifact-scoped vs phase-scoped)
- Sandbox policy per role
- Install/bootstrap policy
- Subagent permissions
- Escalation and budget rules

## Key Design Questions

- Event-driven vs command-driven orchestration (or hybrid)
- One supervisor owns all child sessions vs loosely reconciled sessions
- IPC mechanism: file-first, socket-first, or multiplexer-first
- How much behaviour belongs in generic orchestration vs per-harness adapters
- How subagents are represented in the state model
- Whether spec-driver should own sandbox lifecycle directly

## Feasibility Risks (require PoC)

1. **Multiplexer abstraction** — spawn/detach/reattach across tmux, zellij, raw terminals
2. **File watching across sandbox boundaries** — inotify/fsevents delivery when writer is inside bwrap/sandbox-exec
3. **Harness installer hooks** — automatic detection and injection of harness-specific config
4. **IPC mailbox reliability** — agent-to-agent file-based communication without deadlocks or race conditions

## Constraints

- Must consume IMPR-019 schemas as stable inputs (not redefine them)
- Must not require changes to DE/IP/phase/notes artifact formats
- Runtime failures must not corrupt the durable control plane
- The orchestration layer must degrade gracefully to manual CLI operation

## Non-Goals

- Redesigning workflow semantics (that's IMPR-019)
- Replacing the file-based control plane with a database or service
- Building a general-purpose agent framework unrelated to spec-driver workflows
