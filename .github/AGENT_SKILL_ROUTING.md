# Agents-Skills Routing

This document is the canonical routing map for relationships among ecosystems,
custom agents, and skills in this repository.

## Navigation
- Ecosystem registry: [ECOSYSTEM_REGISTRY.md](ECOSYSTEM_REGISTRY.md)
- Ecosystems classification: [ecosystems/README.md](ecosystems/README.md)
- Agents classification: [agents/README.md](agents/README.md)
- Skills classification: [skills/README.md](skills/README.md)

## Relation Types
- `wrapper-of`: Agent is a thin wrapper and the skill is the canonical policy
  source.
- `uses`: Agent calls or follows one or more skills as part of execution.
- `references`: Agent or skill references another artifact for policy
  alignment.
- `agent-only`: Workflow is intentionally managed as an agent without a skill
  counterpart.
- `skill-only`: Capability is intentionally managed as a skill without an agent
  counterpart.

## Ecosystem -> Members Map

| Ecosystem | Root Agent | Agents | Skills | Dependencies |
|---|---|---|---|---|
| [repository-governance](ecosystems/repository-governance/ECOSYSTEM.md) | [governance-repository-context-manager.agent.md](agents/governance-repository-context-manager.agent.md) | [governance-repository-context-manager.agent.md](agents/governance-repository-context-manager.agent.md) | [repository-governance-bootstrap](skills/repository-governance-bootstrap/SKILL.md), [repository-doc-governance](skills/repository-doc-governance/SKILL.md), [todo-progress-governance](skills/todo-progress-governance/SKILL.md) | none |

## Agent -> Skills Map

| Agent | Related Skills | Relation Type | Notes |
|---|---|---|---|
| [governance-repository-context-manager.agent.md](agents/governance-repository-context-manager.agent.md) | [repository-governance-bootstrap](skills/repository-governance-bootstrap/SKILL.md), [repository-doc-governance](skills/repository-doc-governance/SKILL.md), [todo-progress-governance](skills/todo-progress-governance/SKILL.md) | uses | Root agent of [repository-governance](ecosystems/repository-governance/ECOSYSTEM.md). Orchestrates bootstrap, docs synchronization, and TODO governance. |

## Skill -> Agents Map

| Skill | Related Agents | Relation Type | Notes |
|---|---|---|---|
| [repository-governance-bootstrap](skills/repository-governance-bootstrap/SKILL.md) | [governance-repository-context-manager.agent.md](agents/governance-repository-context-manager.agent.md) | uses | Owns package and repository bootstrap procedures plus validation entry points. |
| [repository-doc-governance](skills/repository-doc-governance/SKILL.md) | [governance-repository-context-manager.agent.md](agents/governance-repository-context-manager.agent.md) | uses | Canonical documentation-sync workflow. |
| [todo-progress-governance](skills/todo-progress-governance/SKILL.md) | [governance-repository-context-manager.agent.md](agents/governance-repository-context-manager.agent.md) | uses | Canonical backlog and design-review maintenance workflow. |

## Self-Extending Maintenance Rules

### 1) Source Of Truth
- Keep this file as the single canonical map for agent-skill relationships.
- Keep [ECOSYSTEM_REGISTRY.md](ECOSYSTEM_REGISTRY.md) and ecosystem manifests
  aligned with this file.
- Both [agents/README.md](agents/README.md) and [skills/README.md](skills/README.md)
  must link here.

### 2) Update Trigger
- When an ecosystem, agent, or skill is added, renamed, removed, or
  re-categorized, update this file in the same change.
- If an entry has no counterpart, keep an explicit `none` row with relation
  type `agent-only` or `skill-only`.

### 3) Relation Type Extension
- If a new relation pattern appears, add it to the Relation Types section
  before using it in tables.
- Keep relation labels concise and stable.

### 4) Consistency Check
- Every manifest listed in [ECOSYSTEM_REGISTRY.md](ECOSYSTEM_REGISTRY.md) must
  appear in the Ecosystem -> Members Map.
- Every file listed in [agents/README.md](agents/README.md) must appear in the
  Agent -> Skills Map.
- Every skill directory listed in [skills/README.md](skills/README.md) must
  appear in the Skill -> Agents Map.

### 5) Tie-Break For Invocation Choice
- Prefer the agent when workflow orchestration, approval gates, or multi-step
  control is required.
- Prefer a skill when a reusable policy or procedure should be shared across
  multiple workflows.

### 6) Local Validation Workflow
- Run `bash .github/ecosystems/repository-governance/validate_agent_skill_docs.sh`
  when changing agents, skills, or routing entries.
- Run `bash .github/ecosystems/validate_ecosystem_registry.sh` when changing
  ecosystem manifests, registry entries, or ecosystem metadata.
- Failing this check means the change is incomplete and must be fixed before
  merge.