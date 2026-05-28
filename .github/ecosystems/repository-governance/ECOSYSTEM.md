---
slug: repository-governance
name: Repository Governance
description: Repository documentation governance, bootstrap, and TODO progress-tracking ecosystem.
status: active
root-agent: governance-repository-context-manager.agent.md
agents: [governance-repository-context-manager.agent.md, governance-ecosystem-manifest.agent.md, governance-ecosystem-delivery.agent.md]
skills: [repository-governance-bootstrap, repository-doc-governance, todo-progress-governance]
dependencies: []
ecosystem-files: [.github/ecosystems/repository-governance/assets/templates, .github/ecosystems/repository-governance/validate_repository_governance.py, .github/ecosystems/repository-governance/validate_repository_governance.sh]
---

# Repository Governance Ecosystem

This ecosystem packages a thin orchestration agent and three canonical skills
for repository documentation governance.

## Members
- Root agent:
  [governance-repository-context-manager.agent.md](../../agents/governance-repository-context-manager.agent.md)
- Specialized agents:
  [governance-ecosystem-manifest.agent.md](../../agents/governance-ecosystem-manifest.agent.md)
  [governance-ecosystem-delivery.agent.md](../../agents/governance-ecosystem-delivery.agent.md)
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
- Treat the listed agents, skills, ecosystem-owned files, and this manifest as
  the full install/remove ownership contract.

## Notes
- Template packs and repository-governance-specific validation assets are owned
  by this ecosystem directory so install payload and validation dependencies
  stay explicit in the manifest.
- Legacy shared automation is being phased out and is not part of this
  manifest-owned payload.