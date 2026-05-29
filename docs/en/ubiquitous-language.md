# Ubiquitous Language

This document tracks the shared project vocabulary that maintainers and
agents use to align context while working in agent_skills_lab.
Unlike the project charter, this file may be updated by agents when they are
grounding terms in current repository behavior, active documents, manifests,
or workflows.
Do not use this file to introduce policy, maintainer decisions, or inferred
local rules. If a wording change would change repository scope or policy,
wait for explicit maintainer instruction and update the charter instead.

## Editing Rules

- Agents may add or refine terms when the term is already used in implemented
  behavior, current docs, manifests, agent names, skill names, or active
  workflows in this repository.
- Agents must not use this file to create approval requirements, hidden local
  rules, or speculative taxonomy.
- Keep entries descriptive and current. Remove or rewrite entries when the
  repository stops using the underlying concept.
- When a term implies repository-specific scope or an explicit maintainer
  decision, record that policy in the charter only after explicit maintainer
  instruction.

## Current Vocabulary

| Term | Meaning in this repository |
|---|---|
| agent_skills_lab | A development and experimentation lab for custom agents, skills, and installable ecosystems. |
| ecosystem | A reusable package of manifest-owned agents, skills, and helper files delivered together into a target repository. |
| manifest | The Markdown contract at `.github/ecosystems/<slug>/ECOSYSTEM.md` that defines an ecosystem's ownership, dependencies, and install payload. |
| ownership contract | The set of files that a manifest claims for install and remove operations. |
| source repository | The repository where reusable ecosystem assets are authored and validated before delivery. |
| target repository | A repository that receives an ecosystem's manifest-owned payload through install or remove workflows. |
| repository-governance | The ecosystem that governs repository docs, documentation update rules, validators, templates, and related orchestration guidance. |
| ubiquitous language | This shared vocabulary layer, maintained to improve maintainer-agent context alignment without becoming a policy surface. |

## Related Documents

- [docs/en/project-charter.md](./project-charter.md): repository-specific scope
  and explicit maintainer decisions.
- [docs/DOCUMENTATION_UPDATE_RULES.md](../DOCUMENTATION_UPDATE_RULES.md):
  canonical rules for stable docs updates.
- [docs/ja/ubiquitous-language.ja.md](../ja/ubiquitous-language.ja.md):
  Japanese counterpart.