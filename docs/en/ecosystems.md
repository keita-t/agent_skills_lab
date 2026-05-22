# Current Ecosystems

This document summarizes the ecosystems currently managed in this repository.
The canonical inventory of record remains
[.github/ECOSYSTEM_REGISTRY.md](../../.github/ECOSYSTEM_REGISTRY.md), and each
ecosystem definition is anchored by its manifest under `.github/ecosystems/`.
The shared Python and shell files directly under `.github/ecosystems/` are
support infrastructure, not separate ecosystems by themselves.

## Related Documents

- [docs/README.md](../README.md): documentation map and reading order.
- [docs/ja/ecosystems.ja.md](../ja/ecosystems.ja.md): Japanese counterpart.
- [docs/en/mcp-tools.md](./mcp-tools.md): MCP tool registry contract and
  current exposed tools.

## Snapshot

- Active ecosystem count: 1
- Current ecosystem slug: `repository-governance`
- Root responsibility: repository documentation governance, bootstrap, and TODO
  progress tracking.

## Current Inventory

| Slug | Status | Purpose | Root agent | Skills | MCP | Notes |
|---|---|---|---|---|---|---|
| `repository-governance` | `active` | Repository documentation governance, bootstrap, and TODO progress tracking. | `governance-repository-context-manager.agent.md` | `repository-governance-bootstrap`, `repository-doc-governance`, `todo-progress-governance` | Enabled | Self-hosted in this repository and installable into other repositories. |

## Ecosystem Details

### `repository-governance`

Canonical manifest:
[.github/ecosystems/repository-governance/ECOSYSTEM.md](../../.github/ecosystems/repository-governance/ECOSYSTEM.md)

| Area | Current implementation |
|---|---|
| Root agent | [.github/agents/governance-repository-context-manager.agent.md](../../.github/agents/governance-repository-context-manager.agent.md) |
| Skills | [.github/skills/repository-governance-bootstrap/SKILL.md](../../.github/skills/repository-governance-bootstrap/SKILL.md), [.github/skills/repository-doc-governance/SKILL.md](../../.github/skills/repository-doc-governance/SKILL.md), [.github/skills/todo-progress-governance/SKILL.md](../../.github/skills/todo-progress-governance/SKILL.md) |
| Managed core files | `.github/ECOSYSTEM_REGISTRY.md`, `.github/ecosystems/README.md`, `.github/AGENT_SKILL_ROUTING.md`, `.github/agents/README.md`, `.github/skills/README.md`, `.github/copilot-instructions.md` |
| Ecosystem-owned files | Template assets, MCP tool registry, and repository-governance validators under `.github/ecosystems/repository-governance/` |
| Post-install validator | `.github/ecosystems/repository-governance/validate_agent_skill_docs.sh` |
| MCP tools | `repository_governance.validate_repository`, `repository_governance.validate_agent_skill_docs` |

## Shared Ecosystem Infrastructure

These files support the ecosystem system as a whole and are not separate
ecosystem entries.

| Path | Role |
|---|---|
| [.github/ecosystems/install_ecosystem.sh](../../.github/ecosystems/install_ecosystem.sh) | Import a selected ecosystem into another repository. |
| [.github/ecosystems/update_ecosystem_core_files.sh](../../.github/ecosystems/update_ecosystem_core_files.sh) | Regenerate ecosystem-managed `.github` core files from installed manifests. |
| [.github/ecosystems/validate_ecosystem_registry.sh](../../.github/ecosystems/validate_ecosystem_registry.sh) | Validate manifests, registry entries, routing links, and ecosystem metadata. |
| [.github/ecosystems/mcp_server.py](../../.github/ecosystems/mcp_server.py) | Expose shared and ecosystem-scoped tools over FastMCP. |