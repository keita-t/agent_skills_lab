---
slug: repository-docs
name: Repository Docs
description: Repository documentation governance, refactoring, bootstrap, and TODO progress-tracking ecosystem.
status: active
root-agent: governance-repository-context-manager.agent.md
agents: [governance-repository-context-manager.agent.md, governance-ecosystem-manifest.agent.md, governance-ecosystem-delivery.agent.md]
skills: [docs-bootstrap, docs-sync, docs-refactor, todo-maintenance]
dependencies: [ecosystem-audit]
ecosystem-files: [.ai_ecosystems/repository-docs/assets/templates]
audit-files: [.ai_ecosystems/repository-docs/audit/repository-docs-audit.md]
---

# Repository Docs Ecosystem

This ecosystem packages a thin orchestration agent and four canonical skills
for repository documentation governance and refactoring.

## Members
- Root agent: `governance-repository-context-manager.agent.md`
- Specialized agents:
  `governance-ecosystem-manifest.agent.md`,
  `governance-ecosystem-delivery.agent.md`
- Skills:
  `docs-bootstrap`, `docs-sync`,
  `docs-refactor`, `todo-maintenance`
- Source canonical agents: `.ai_ecosystems/repository-docs/agents/`
- Source canonical skills: `.ai_ecosystems/repository-docs/skills/`

## Install Payload
- Treat listed agents and skills as logical member names. Delivery host
  adapters copy them from this ecosystem's `agents/` and `skills/` directories
  to the selected AI tool native paths.
- GitHub Copilot targets: `.github/agents/*.agent.md` and `.github/skills/*`.
- Claude Code targets: `.claude/agents/*.md` and `.claude/skills/*`.
- Codex target: `.agents/skills/*`.
- Cursor target: `.cursor/skills/*`.
- Copy the ecosystem-owned files listed in frontmatter from
  `.ai_ecosystems/repository-docs/`.
- Copy the audit files listed in frontmatter from
  `.ai_ecosystems/repository-docs/`.
- Copy this manifest into the target project's `.ai_ecosystems/` tree.
- Treat the listed agents, skills, ecosystem-owned files, audit files, and this
  manifest as the full install/remove ownership contract.
- Keep installable markdown artifacts self-contained to that manifest-owned
  payload. Relative repository-local links inside installed agents, skills,
  template docs, and this manifest must resolve to manifest-owned paths.
- Do not write target repository root/global instruction files such as
  `AGENTS.md`, `CLAUDE.md`, or `.github/copilot-instructions.md`.

## Notes
- Template packs and repository-docs-specific validation assets are owned
  by this ecosystem directory so install payload and validation dependencies
  stay explicit in the manifest.
- Repository-docs-specific audits live in manifest-declared audit files and
  are applied through the shared `ecosystem-audit` platform.
- Legacy validator scripts may remain in the source repository during
  migration, but they are not part of the shipped manifest-owned payload.
- Source-only shared helpers under `.ai_ecosystems/` may be mentioned as
  operational context, but installable artifacts must not link to them unless
  the manifest explicitly owns them.
