# Policy & Governance

{% if config.policy.adrs -%}
## Architecture Decisions

ADRs are enabled. Before making architectural choices, check accepted decisions:

```
uv run spec-driver list adrs -s accepted
```

Read any relevant ADR before proceeding. If your work conflicts with an accepted ADR, stop and raise the conflict for clarification.

See `specify/decisions/` for all ADRs.
{% endif -%}
{% if config.policy.policies -%}
## Policies

Project policies are enabled. See `specify/policies/`.
{% endif -%}
{% if config.policy.standards -%}
## Standards

Technical standards are enabled. See `specify/standards/`.
{% endif -%}
{% if not config.policy.adrs and not config.policy.policies and not config.policy.standards -%}
No governance primitives are currently enabled.
{% endif -%}
