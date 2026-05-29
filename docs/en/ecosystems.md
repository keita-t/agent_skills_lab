# Current Ecosystems

This document summarizes the ecosystems currently managed in this repository.
The implementation-facing inventory is anchored by
[.github/ecosystems/README.md](../../.github/ecosystems/README.md), and each
ecosystem definition is anchored by its manifest under `.github/ecosystems/`.
The shared Python and shell files directly under `.github/ecosystems/` are
support infrastructure, not separate ecosystems by themselves.

## Related Documents

- [docs/README.md](../README.md): documentation map and reading order.
- [docs/ja/ecosystems.ja.md](../ja/ecosystems.ja.md): Japanese counterpart.

## Snapshot

- Active ecosystem count: 2
- Current ecosystem slugs: `codebase-context`, `repository-governance`
- Current root responsibilities: repository codebase export for large-context
  models, plus repository documentation governance, bootstrap, and TODO
  progress tracking.
- Manifest direction: ownership and dependency contract first.

## Current Inventory

| Slug | Status | Purpose | Root agent | Skills | Notes |
|---|---|---|---|---|---|
| `codebase-context` | `active` | Export a repository into one markdown context file for large-context models. | `codebase-context.agent.md` | `codebase-context-export` | Installable into other repositories. The default export includes the full filtered source code plus useful supporting files, while explicit user pickup rules can narrow or override that scope. |
| `repository-governance` | `active` | Repository documentation governance, bootstrap, and TODO progress tracking. | `governance-repository-context-manager.agent.md` | `repository-governance-bootstrap`, `repository-doc-governance`, `todo-progress-governance` | Self-hosted in this repository and installable into other repositories. Manifest-owned payload now excludes legacy MCP metadata. |

## Ecosystem Details

### `codebase-context`

Canonical manifest:
[.github/ecosystems/codebase-context/ECOSYSTEM.md](../../.github/ecosystems/codebase-context/ECOSYSTEM.md)

| Area | Current implementation |
|---|---|
| Root agent | [.github/agents/codebase-context.agent.md](../../.github/agents/codebase-context.agent.md) |
| Skills | [.github/skills/codebase-context-export/SKILL.md](../../.github/skills/codebase-context-export/SKILL.md) |
| Ownership contract | Agent, skill, listed ecosystem-owned files, and the manifest itself |
| Ecosystem-owned files | The generator and shell wrapper under `.github/ecosystems/codebase-context/` |
| Default export behavior | Generates `CODEBASE_CONTEXT.md` at the repository root, exporting the full filtered source code plus useful supporting files in one markdown snapshot |
| User override rule | Explicit user pickup rules such as include, exclude, or source-only constraints override the default broad export policy |
| Runtime output | The generated markdown snapshot is runtime output and is not part of the manifest-owned install payload |

### `repository-governance`

Canonical manifest:
[.github/ecosystems/repository-governance/ECOSYSTEM.md](../../.github/ecosystems/repository-governance/ECOSYSTEM.md)

| Area | Current implementation |
|---|---|
| Root agent | [.github/agents/governance-repository-context-manager.agent.md](../../.github/agents/governance-repository-context-manager.agent.md) |
| Specialized agents | [.github/agents/governance-ecosystem-manifest.agent.md](../../.github/agents/governance-ecosystem-manifest.agent.md), [.github/agents/governance-ecosystem-delivery.agent.md](../../.github/agents/governance-ecosystem-delivery.agent.md) |
| Skills | [.github/skills/repository-governance-bootstrap/SKILL.md](../../.github/skills/repository-governance-bootstrap/SKILL.md), [.github/skills/repository-doc-governance/SKILL.md](../../.github/skills/repository-doc-governance/SKILL.md), [.github/skills/todo-progress-governance/SKILL.md](../../.github/skills/todo-progress-governance/SKILL.md) |
| Ownership contract | Agents, skills, listed ecosystem-owned files, and the manifest itself |
| Ecosystem-owned files | Template assets and repository-governance validators under `.github/ecosystems/repository-governance/` |
| Install portability rule | Repository-local links inside installable markdown must resolve within the manifest-owned payload so installed artifacts stay self-contained in target repositories. |
| Delivery helper | [.github/ecosystems/deliver_ecosystem.py](../../.github/ecosystems/deliver_ecosystem.py) drives PR-oriented install and remove workflows against target repositories |

## Shared Ecosystem Infrastructure

These files support the ecosystem system as a whole and are not separate
ecosystem entries.

| Path | Role |
|---|---|
| [.github/ecosystems/deliver_ecosystem.py](../../.github/ecosystems/deliver_ecosystem.py) | Execute manifest-owned install or remove workflows against a target `owner/repo` and prepare a PR-based delivery flow. |
| [.github/ecosystems/validate_ecosystem_registry.sh](../../.github/ecosystems/validate_ecosystem_registry.sh) | Validate manifests, frontmatter alignment, and structural ecosystem membership. |