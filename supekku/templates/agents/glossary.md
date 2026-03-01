# Glossary of Active Primitives

{% if config.cards.enabled -%}
- **Card**: Work item tracked in `{{ config.cards.root }}/`. ID format: `{{ config.cards.id_prefix }}NNN-slug`.
{% endif -%}
{% if config.contracts.enabled -%}
- **Contract**: Auto-generated API doc in `{{ config.contracts.root }}/`.
{% endif -%}
{% if config.policy.adrs -%}
- **ADR**: Architecture Decision Record in `specify/decisions/`.
{% endif -%}
{% if config.policy.policies -%}
- **Policy**: Organisational policy in `specify/policies/`.
{% endif -%}
{% if config.policy.standards -%}
- **Standard**: Technical standard in `specify/standards/`.
{% endif -%}
- **Spec**: Technical specification in `specify/tech/`.
- **Delta**: Change bundle in `change/deltas/`.
