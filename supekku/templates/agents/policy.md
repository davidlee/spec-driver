# Policy & Governance

{% if config.policy.adrs -%}
## Architecture Decisions

ADRs are enabled. Before making architectural choices, check accepted decisions:

```
{{ config.tool.exec }} list adrs -s accepted
```

Read any relevant ADR before proceeding.

{% endif -%}
{% if config.policy.policies -%}
## Policies

Project policies are enabled.

List them now; read any which might apply before any design or implementation.

```
{{ config.tool.exec }} list policies -s required
```

{% endif -%}
{% if config.policy.standards -%}
## Standards

Technical standards are enabled.

List them now; read any which might apply before any design or implementation.

```
{{ config.tool.exec }} list standards -s required
```

{% endif -%}

{% if not config.policy.adrs and not config.policy.policies and not config.policy.standards -%}
No governance primitives are currently enabled.
{% else -%}
## Requirement for Proactive Compliance

Remember these, and read any potentially relevant artefacts before proceeding
now OR in the future.

If your work conflicts with any of them, stop and raise the conflict for
clarification.

{% endif -%}
