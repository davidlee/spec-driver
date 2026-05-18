---
id: "{{ audit_id }}"
name: "Audit - {{ name }}"
slug: "{{ slug }}"
kind: audit  # one of: audit | delta | design_revision | issue | memory | phase | plan | policy | problem | prod | requirement | risk | spec | standard | task | verification
status: draft  # one of: completed | deferred | draft | in-progress | pending
created: "{{ today }}"
updated: "{{ today }}"
---

{{ audit_verification_block }}

## Observations

- …

## Evidence

- Code references, logs, test results

## Recommendations

- …
