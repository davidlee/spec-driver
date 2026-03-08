# Project doctrine

This file is intentionally short and is loaded by skills at specific “hook points”
(boot/preflight/new-card/brainstorm/plan/notes/handover) to apply project-specific
conventions without forking vendor-managed skills.

## Preferences for agents

- "Card" means whatever artifact tracks active work in this project — kanban card, delta, revision, etc, depending on ceremony mode & context.
- Commit policy for workflow artefacts:
  - Prefer frequent, small commits of `.spec-driver/**` changes.
  - Bias toward keeping the repo clean over waiting for perfectly related `.spec-driver` batches.
  - When `.spec-driver/**` changes and code/product changes both exist, it is fine to commit them together or separately; prefer whichever comes first while keeping the worktree clean.
  - If this repo wants a more specific commit ritual or message shape, document it here.
  - Use short, conventional commit messages by default. Example: `fix(DE-093): address memory leaks in flux capacitor`.
