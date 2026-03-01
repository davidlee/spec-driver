# Execution Environment

Run spec-driver via: `{{ config.tool.exec }}`

Any instruction like `spec-driver $args` means `{{ config.tool.exec }} $args`.
For example: `spec-driver list adrs` → `{{ config.tool.exec }} list adrs`.

Run `{{ config.tool.exec }} --help` for available commands.

Verification: `{{ config.verification.command }}`
