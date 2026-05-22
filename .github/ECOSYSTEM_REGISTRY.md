# Ecosystem Registry

This document is the canonical registry for ecosystems managed in this
repository.

## Navigation
- Ecosystems classification: [ecosystems/README.md](ecosystems/README.md)
- Agents-skills routing map: [AGENT_SKILL_ROUTING.md](AGENT_SKILL_ROUTING.md)
- Agents classification: [agents/README.md](agents/README.md)
- Skills classification: [skills/README.md](skills/README.md)

## Ecosystem Inventory

| Ecosystem | Root Agent | Skills | Status | Notes |
|---|---|---|---|---|
| [repository-governance](ecosystems/repository-governance/ECOSYSTEM.md) | [governance-repository-context-manager.agent.md](agents/governance-repository-context-manager.agent.md) | [repository-governance-bootstrap](skills/repository-governance-bootstrap/SKILL.md), [repository-doc-governance](skills/repository-doc-governance/SKILL.md), [todo-progress-governance](skills/todo-progress-governance/SKILL.md) | active | Repository documentation governance, bootstrap, and TODO progress tracking. |

## Registry Rules
- Every ecosystem must have one manifest at `.github/ecosystems/<slug>/ECOSYSTEM.md`.
- Every agent and skill that belongs to an ecosystem must declare the
  ecosystem slug in frontmatter.
- When an ecosystem is added, renamed, removed, or re-scoped, update this file,
  the manifest, `.github/AGENT_SKILL_ROUTING.md`, `.github/agents/README.md`,
  and `.github/skills/README.md` in the same change.
- Run `bash .github/ecosystems/validate_ecosystem_registry.sh` after editing
  ecosystem manifests or ecosystem-aware core files.