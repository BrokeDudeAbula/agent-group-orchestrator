# Agent Group Orchestrator

Reusable Codex plugin for project-local multi-agent orchestration.

This plugin turns the original LAPE `agent_group` workflow into a generic package:

- `skills/` contains the Codex-facing workflows.
- `references/` contains reusable policies and contracts loaded on demand.
- `assets/templates/instance/` contains a starter `.codex/agent_group` instance.
- `scripts/` contains deterministic initialization, validation, and compaction helpers.
- `examples/` keeps the original LAPE/Qwen35 and demo instances as regression material.

The plugin should not keep live project state at its root. Project-specific state belongs in a target repository instance, usually `.codex/agent_group/`.

