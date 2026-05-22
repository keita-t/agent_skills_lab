---
slug: repository-governance
name: Repository Governance
description: Repository documentation governance, bootstrap, and TODO progress-tracking ecosystem.
status: active
root-agent: governance-repository-context-manager.agent.md
agents: [governance-repository-context-manager.agent.md]
skills: [repository-governance-bootstrap, repository-doc-governance, todo-progress-governance]
dependencies: []
ecosystem-files: [.github/ecosystems/repository-governance/assets/templates, .github/ecosystems/repository-governance/MCP_TOOLS.json, .github/ecosystems/repository-governance/validate_agent_skill_docs.py, .github/ecosystems/repository-governance/validate_agent_skill_docs.sh, .github/ecosystems/repository-governance/validate_repository_governance.py, .github/ecosystems/repository-governance/validate_repository_governance.sh]
managed-core-files: [.github/ECOSYSTEM_REGISTRY.md, .github/ecosystems/README.md, .github/AGENT_SKILL_ROUTING.md, .github/agents/README.md, .github/skills/README.md, .github/copilot-instructions.md]
agent-skill-relations: [governance-repository-context-manager.agent.md=>repository-governance-bootstrap|repository-doc-governance|todo-progress-governance]
post-install-validator: .github/ecosystems/repository-governance/validate_agent_skill_docs.sh
mcp-enabled: true
mcp-tool-registry: .github/ecosystems/repository-governance/MCP_TOOLS.json
mcp-tool-names: [repository_governance.validate_repository, repository_governance.validate_agent_skill_docs]
mcp-tool-groups: [validator, documentation-governance]
---

# Repository Governance Ecosystem

This ecosystem packages a thin orchestration agent and three canonical skills
for repository documentation governance.

## Members
- Root agent:
  [governance-repository-context-manager.agent.md](../../agents/governance-repository-context-manager.agent.md)
- Skills:
  [repository-governance-bootstrap](../../skills/repository-governance-bootstrap/SKILL.md)
  [repository-doc-governance](../../skills/repository-doc-governance/SKILL.md)
  [todo-progress-governance](../../skills/todo-progress-governance/SKILL.md)

## Install Payload
- Copy the listed agent file from `.github/agents/`.
- Copy the listed skill directories from `.github/skills/`.
- Copy the ecosystem-owned files listed in frontmatter from
  `.github/ecosystems/repository-governance/`.
- Copy this manifest into the target project's `.github/ecosystems/` tree.
- Regenerate target `.github` core files with
  [update_ecosystem_core_files.sh](../update_ecosystem_core_files.sh).

## Notes
- Template packs and repository-governance-specific validators are owned by this
  ecosystem directory so install payload and validation dependencies stay
  explicit in the manifest.
- This manifest is the detailed source of truth for installer, updater, and
  ecosystem validation logic.