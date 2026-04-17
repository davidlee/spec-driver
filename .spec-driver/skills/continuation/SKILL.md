---
name: continuation
description: Write a prompt to help the next agent continue effectively.
---

Ensure /notes on the task card are up to date.

If there is already a 'New Agent Instructions' section, read and update it.
otherwise, create one, including:

- task card code
- required reading
- related documents
- key files
- relevant memories
- relevant doctrines
- any important user instructions or decisions
- any incomplete work or loose ends
- pending commit-state guidance, especially whether `.spec-driver` changes
  should be committed now to keep the worktree clean, and whether they should go
  out with code or separately per repo doctrine
- other advice or knowledge applicable to the next task(s)
- file paths for any files / documents referenced.

Then, print the path to the task card.

If the task card is a delta, use its `notes.md` file for onboarding, and
reference both it and the parent delta.

## Structured Handoff (workflow orchestration)

If the task card is a delta with an active workflow state
(`workflow/state.yaml` exists in the delta bundle), you **must** invoke the
CLI to create a structured handoff:

```
uv run spec-driver create handoff <DELTA-ID> --to <role>
```

Where `<role>` is the appropriate next role (e.g. `reviewer`, `implementer`,
`architect`).

If you are completing a phase, use `phase complete` instead — it marks the
phase done and emits a handoff automatically:

```
uv run spec-driver phase complete <DELTA-ID>
```

Pass `--to reviewer` if the next step is review.

**Do not silently fall back to prose-only handoff** if the CLI command fails.
The failure must be surfaced and resolved. The structured handoff ensures
deterministic state transitions and machine-readable handoff payloads.

When `workflow/state.yaml` does not exist (no orchestration active), continue
with the prose-only handoff as before.

## Next Agent Instructions

Then identify the next logical activity, and print instructions for the next agent.

Usually this means a simple instruction to invoke `/using-spec-driver` or one
of its target skills, with the appropriate artefact.

If the next step is implementation-adjacent or depends on `/preflight`, make
the handover explicitly preserve unresolved assumptions, questions, and design
tensions. Do not hand off with a vague "ready to proceed" if the bundle still
contains ambiguities the next agent should assess before coding.
