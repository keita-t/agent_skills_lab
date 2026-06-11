---
slug: ecosystem-audit
name: Ecosystem Audit
description: Shared audit platform for ecosystem manifests, installed ecosystem payloads, and ecosystem work quality.
status: active
root-agent: ecosystem-audit.agent.md
agents: [ecosystem-audit.agent.md]
skills: []
dependencies: []
ecosystem-files: [.ai_ecosystems/ecosystem-audit/assets/templates, .ai_ecosystems/ecosystem-audit/assets/smoke-scenarios]
audit-files: [.ai_ecosystems/ecosystem-audit/audit/core-rules.md, .ai_ecosystems/ecosystem-audit/audit/report-contract.md, .ai_ecosystems/ecosystem-audit/audit/work-quality-rubric.md]
---

# Ecosystem Audit Ecosystem

This ecosystem packages a shared audit agent, core structural audit rules, and
a shared work-quality rubric that can be extended by any other ecosystem
through manifest-declared audit files.

## Members
- Root agent: `ecosystem-audit.agent.md`
- Source canonical agent: `.ai_ecosystems/ecosystem-audit/agents/ecosystem-audit.agent.md`

## Install Payload
- Treat listed agents and skills as logical member names. Delivery host
  adapters copy them from this ecosystem's `agents/` and `skills/` directories
  to the selected AI tool native paths.
- GitHub Copilot agent target: `.github/agents/*.agent.md`.
- Claude Code agent target: `.claude/agents/*.md`.
- Codex and Cursor receive skills only unless a future host adapter explicitly
  adds native agent support.
- Copy the ecosystem-owned files listed in frontmatter from
  `.ai_ecosystems/ecosystem-audit/`.
- Copy the audit files listed in frontmatter from `.ai_ecosystems/ecosystem-audit/`.
- Copy this manifest into the target project's `.ai_ecosystems/` tree.
- Treat the listed agents, ecosystem-owned files, audit files, and this
  manifest as the full install/remove ownership contract.
- Do not write target repository root/global instruction files such as
  `AGENTS.md`, `CLAUDE.md`, or `.github/copilot-instructions.md`.
- Load ecosystem-specific audit extensions only from manifest-declared
  `audit-files` so each ecosystem keeps ownership of its own checks.

## Notes
- This ecosystem provides shared cross-ecosystem audit rules.
- This ecosystem provides a shared work-quality rubric for rubric-first audit
  reports.
- This ecosystem also ships a starter audit-pack template and a manual smoke
  scenario for newly added ecosystems.
- Ecosystem-specific checks stay in the owning ecosystem's own directory and
  are plugged in through manifest frontmatter.
- Audit execution is explicit and on-demand; delivery does not auto-run audits.
