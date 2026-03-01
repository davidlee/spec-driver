# Workflow

Ceremony mode: **{{ config.ceremony }}**

{% if config.cards.enabled -%}
## Cards

Cards root: `{{ config.cards.root }}`
Lanes: {{ config.cards.lanes | join(', ') }}
ID prefix: `{{ config.cards.id_prefix }}`
{% endif -%}

## Documentation

Artefacts: `{{ config.docs.artefacts_root }}`
Plans: `{{ config.docs.plans_root }}`
