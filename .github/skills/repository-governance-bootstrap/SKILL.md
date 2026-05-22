---
name: repository-governance-bootstrap
description: 'Bootstrap or repair repository documentation governance, documentation maps, TODO progress governance, and validation entry points. Use for initial setup, policy installation, or reusable repository context scaffolding.'
ecosystem: repository-governance
argument-hint: 'Describe the target repository, current docs state, and whether you want single-language or bilingual governance.'
---

# Repository Governance Bootstrap

## When To Use
- Initialize a repository with reusable documentation-governance scaffolding.
- Repair missing governance files, missing routing docs, or missing validators.
- Introduce a TODO/progress-management model that distinguishes routine updates
  from structural reorganization.

## Role
You are the setup and repair skill for repository context governance.
Your goal is to install a reusable structure that humans and AI agents can both
use to understand and maintain the repository.

## Required Inputs
- Current repository entry points such as `README.md`, `CLAUDE.md`, or `docs/`.
- Desired language mode: single-language or bilingual.
- Whether existing docs should be preserved, merged, or replaced.
- Whether progress tracking should live in `docs/TODO.md` or another canonical
  path.

## Procedure
1. Inspect the repository entry points and current documentation structure.
2. Decide whether to merge with existing docs or install the package structure
   as a new canonical set.
3. Add or repair the shared governance artifacts, including document maps,
   routing docs, template-based canonical files, and validators.
4. Ensure repository-level entry points link to the canonical docs map and the
   documentation update rules.
5. Choose a pack from [single-language templates](../../ecosystems/repository-governance/assets/templates/single-language/README.md)
   or [bilingual templates](../../ecosystems/repository-governance/assets/templates/bilingual/README.md)
   and adapt it to the target repository. Keep project-charter files minimal
   unless explicit charter content was supplied by the user or maintainers.
6. When importing this ecosystem into another repository, use
   [../../ecosystems/install_ecosystem.sh](../../ecosystems/install_ecosystem.sh)
   from the source lab repository so the agent, skills, manifest, and shared
   core updater are installed together.
7. After ecosystem import, regenerate target `.github` core files with
   [../../ecosystems/update_ecosystem_core_files.sh](../../ecosystems/update_ecosystem_core_files.sh).
8. Validate ecosystem metadata with
   [../../ecosystems/validate_ecosystem_registry.sh](../../ecosystems/validate_ecosystem_registry.sh)
   when the ecosystem registry or manifests change.
9. Run [validate_agent_skill_docs.sh](../../ecosystems/repository-governance/validate_agent_skill_docs.sh)
   after changing agents, skills, or routing docs.
10. Run [validate_repository_governance.sh](../../ecosystems/repository-governance/validate_repository_governance.sh)
   against the target repository or template pack.

## Rules
1. Do not overwrite repository-specific documentation wholesale without a
   clear migration plan.
2. Preserve project-specific contracts and terminology when adapting the
   generic governance structure.
3. If the repository already has a stable TODO or backlog file, merge rules
   into it instead of creating a conflicting second canonical progress file.
4. Keep the bootstrap output minimal and editable by future maintainers.
5. Do not invent project charter policy. If no explicit charter content is
   supplied, keep project-charter files limited to repository purpose, known
   terminology, and explicit human-approved decisions.

## Outputs
- Installed or repaired governance files
- Any required entry-point link updates
- Validation status for the package structure and the target repository