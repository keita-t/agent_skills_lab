# Agents Classification

This folder organizes custom agent definitions while keeping all definition
files at the top level for VS Code discovery compatibility.

## Navigation
- Ecosystem registry: [../ECOSYSTEM_REGISTRY.md](../ECOSYSTEM_REGISTRY.md)
- Ecosystems classification: [../ecosystems/README.md](../ecosystems/README.md)
- Skills classification: [../skills/README.md](../skills/README.md)
- Agents-skills routing map (canonical): [../AGENT_SKILL_ROUTING.md](../AGENT_SKILL_ROUTING.md)

## Ecosystem Membership

### Repository Governance
- [governance-repository-context-manager.agent.md](governance-repository-context-manager.agent.md)

## Classification Rules For New Agents

### 1) File Placement
- Always place new `.agent.md` files directly under `.github/agents/`.
- Do not create subdirectories for agent definitions.

### 2) Naming Prefix (Required)
- Base rule: `<category>-<purpose>.agent.md`
- Current Governance category: `governance-<purpose>.agent.md`
- If a new category is created, use its slug as prefix.

### 3) Category Decision Criteria
- Governance: Primary purpose is repository documentation governance,
  progress-governance orchestration, validation routing, or approval-gated
  maintenance of repository context artifacts.
- Governance keywords: `governance`, `documentation`, `docs`, `progress`,
  `todo`, `backlog`, `charter`, `routing`, `validation`.

### 4) Required Maintenance When Adding An Agent
- Add the new file to the proper section in this README.
- Ensure frontmatter `name`, `description`, and `ecosystem` include the
  discovery and ownership metadata needed for routing.
- Keep one clear responsibility per agent.
- Update [../ECOSYSTEM_REGISTRY.md](../ECOSYSTEM_REGISTRY.md), the owning
  manifest under [../ecosystems/README.md](../ecosystems/README.md), and
  [../AGENT_SKILL_ROUTING.md](../AGENT_SKILL_ROUTING.md) in the same change.
- Run the local consistency check:
  `bash .github/ecosystems/repository-governance/validate_agent_skill_docs.sh`
  and `bash .github/ecosystems/validate_ecosystem_registry.sh`

### 5) Self-Extending Classification
- Create a new category only when Governance no longer fits the primary
  responsibility.
- Use a stable lowercase kebab-case slug for the category name.
- Add a new top-level section in this README and extend sections `2` and `3`
  in the same change.

### 6) Self-Extending Cross-Link Rules (Agents <-> Skills)
- For each agent addition, rename, or removal, update the Agent -> Skills row
  in [../AGENT_SKILL_ROUTING.md](../AGENT_SKILL_ROUTING.md).
- Keep the agent listed in its owning ecosystem manifest and ecosystem registry.
- If no related skill exists, keep an explicit `none` row with relation type
  `agent-only`.
- If an agent wraps a single canonical skill policy, use relation type
  `wrapper-of`.
- If an agent coordinates multiple skills, use relation type `uses`.