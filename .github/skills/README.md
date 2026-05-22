# Skills Classification

This folder organizes reusable skills. Each skill directory remains directly
under `.github/skills/` to keep path compatibility stable for agent references
and slash-command discovery.

## Navigation
- Ecosystem registry: [../ECOSYSTEM_REGISTRY.md](../ECOSYSTEM_REGISTRY.md)
- Ecosystems classification: [../ecosystems/README.md](../ecosystems/README.md)
- Agents classification: [../agents/README.md](../agents/README.md)
- Agents-skills routing map (canonical): [../AGENT_SKILL_ROUTING.md](../AGENT_SKILL_ROUTING.md)

## Governance Bootstrap
- [repository-governance-bootstrap](repository-governance-bootstrap/SKILL.md):
  Installs or repairs repository context-governance scaffolding, templates, and
  validation entry points.

## Documentation Governance
- [repository-doc-governance](repository-doc-governance/SKILL.md): Keeps
  canonical repository documents aligned with implementation changes and
  navigation rules.

## Progress Governance
- [todo-progress-governance](todo-progress-governance/SKILL.md): Maintains
  backlog and design-review tracking files under explicit routine-vs-structural
  editing rules.

## Classification Rules For New Skills

### 1) File Placement
- Place each skill in its own directory directly under `.github/skills/`.
- Required file path format: `.github/skills/<skill-slug>/SKILL.md`.
- Do not move existing skill directories without updating all references that
  point to those paths.

### 2) Naming Rule
- Use lowercase kebab-case for `<skill-slug>`.
- Prefer names that express one primary responsibility.
- Use repository-facing nouns when the skill manages shared docs, governance,
  or progress artifacts.

### 3) Category Decision Criteria
- Governance Bootstrap: Skills that initialize, repair, or validate the shared
  governance scaffolding of a repository.
- Documentation Governance: Skills that synchronize architecture docs, docs
  maps, charters, and update rules with implementation changes.
- Progress Governance: Skills that maintain TODO, backlog, or review-tracking
  files under explicit update rules.

### 4) Tie-Break Priority (When Ambiguous)
- If the primary output is repository setup or validation scaffolding, choose
  Governance Bootstrap.
- Else if the primary output is canonical documentation synchronization, choose
  Documentation Governance.
- Else if the primary output is backlog or progress tracking maintenance,
  choose Progress Governance.
- Else create a new category by extending this README in the same change.

### 5) Required Maintenance When Adding A Skill
- Add the skill to exactly one category section in this README.
- Keep one clear responsibility per skill directory.
- Ensure `SKILL.md` descriptions include trigger phrases for when the skill
  should be invoked and keep the `ecosystem` field aligned with its owning
  manifest.
- Update [../ECOSYSTEM_REGISTRY.md](../ECOSYSTEM_REGISTRY.md), the owning
  manifest under [../ecosystems/README.md](../ecosystems/README.md), and
  [../AGENT_SKILL_ROUTING.md](../AGENT_SKILL_ROUTING.md) in the same change.
- Run the local consistency check:
  `bash .github/ecosystems/repository-governance/validate_agent_skill_docs.sh`
  and `bash .github/ecosystems/validate_ecosystem_registry.sh`

### 6) Self-Extending Cross-Link Rules (Skills <-> Agents)
- For each skill addition, rename, or removal, update the Skill -> Agents row
  in [../AGENT_SKILL_ROUTING.md](../AGENT_SKILL_ROUTING.md).
- Keep the skill listed in its owning ecosystem manifest and ecosystem registry.
- If no related agent exists, keep an explicit `none` row with relation type
  `skill-only`.
- If a skill is the canonical policy behind a wrapper agent, relation type
  should include `wrapper-of`.
- If a skill is consumed by workflow agents, relation type should include
  `uses`.