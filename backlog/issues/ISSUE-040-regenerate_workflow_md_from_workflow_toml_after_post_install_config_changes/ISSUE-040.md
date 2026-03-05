---
id: ISSUE-040
name: Regenerate workflow.md from workflow.toml after post-install config changes
created: '2026-03-05'
updated: '2026-03-05'
status: open
kind: issue
categories: []
severity: p3
impact: user
---

# Regenerate workflow.md from workflow.toml after post-install config changes

## Problem

`workflow.md` is generated from `workflow.toml` during installation, but there
is no way to regenerate it after post-install config changes. If a user edits
`workflow.toml` (e.g. changes ceremony mode), `workflow.md` goes stale.

## Context

Discovered during DL-047.007 (spec corpus reconciliation). The installer
correctly generates `workflow.md` from `workflow.toml`, but the generation is
a one-shot operation with no re-run affordance.

## Suggested fix

A command like `spec-driver install --regenerate` or `spec-driver configure
--apply` that re-renders template-driven agent docs from current config.

