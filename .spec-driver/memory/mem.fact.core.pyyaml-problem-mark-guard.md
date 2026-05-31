---
id: mem.fact.core.pyyaml-problem-mark-guard
name: PyYAML problem_mark may be absent on YAMLError
kind: memory
status: active
memory_type: fact
created: '2026-06-01'
updated: '2026-06-01'
verified: '2026-06-01'
confidence: medium
tags: []
summary: yaml.YAMLError subclasses may not always have problem_mark attribute. Use
  getattr(exc, 'problem_mark', None) and guard. Mark line/column are 0-based; surface
  as 1-based for UX (mark.line + 1).
---

# PyYAML problem_mark may be absent on YAMLError

## Summary

## Context
