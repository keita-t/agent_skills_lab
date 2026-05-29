---
slug: ecosystem-audit
name: Ecosystem Audit
description: Shared audit platform for ecosystem manifests, installed ecosystem payloads, and ecosystem work quality.
status: active
root-agent: ecosystem-audit.agent.md
agents: [ecosystem-audit.agent.md]
skills: []
dependencies: []
ecosystem-files: [.github/ecosystems/ecosystem-audit/assets/templates, .github/ecosystems/ecosystem-audit/assets/smoke-scenarios]
audit-files: [.github/ecosystems/ecosystem-audit/audit/core-rules.md, .github/ecosystems/ecosystem-audit/audit/report-contract.md, .github/ecosystems/ecosystem-audit/audit/work-quality-rubric.md]
---

# Ecosystem Audit Ecosystem

This ecosystem packages a shared audit agent, core structural audit rules, and
a shared work-quality rubric that can be extended by any other ecosystem
through manifest-declared audit files.

## Members
- Root agent:
  [ecosystem-audit.agent.md](../../agents/ecosystem-audit.agent.md)

## Install Payload
- Copy the listed agent file from `.github/agents/`.
- Copy the ecosystem-owned files listed in frontmatter from
  `.github/ecosystems/ecosystem-audit/`.
- Copy the audit files listed in frontmatter from `.github/ecosystems/ecosystem-audit/`.
- Copy this manifest into the target project's `.github/ecosystems/` tree.
- Treat the listed agents, ecosystem-owned files, audit files, and this
  manifest as the full install/remove ownership contract.
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
