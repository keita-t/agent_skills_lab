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
- Whether existing backlog or TODO content should be migrated into the
   canonical `docs/TODO.md` path used by the governance pack.

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
   unless explicit charter content was supplied by the user or maintainers,
   and install or adapt the ubiquitous-language doc as the editable home for
   shared terminology.
6. When importing this ecosystem into another repository, use the
   [Ecosystem Delivery Orchestrator](../../agents/governance-ecosystem-delivery.agent.md)
   or another source-side delivery workflow that copies only the
   manifest-owned payload into the target repository.
7. When the ecosystem registry or manifests change in the upstream source
   ecosystem repository, run that source repository's own ecosystem-registry
   validation workflow before delivery; it is source-only and is not shipped
   into target repositories. Keep installable artifacts free of links to
   source-only shared helpers.
8. Run [validate_repository_governance.sh](../../ecosystems/repository-governance/validate_repository_governance.sh)
   with `--mode bilingual` for bilingual repositories or `--mode single-language`
   otherwise. When validating a template pack or another checkout, pass
   `--repo-root <path>`.

## Rules
1. Do not overwrite repository-specific documentation wholesale without a
   clear migration plan.
2. Preserve project-specific contracts and terminology when adapting the
   generic governance structure.
3. If the repository already has a stable TODO or backlog file, migrate or
   merge its canonical progress-tracking content into `docs/TODO.md`, and keep
   any legacy path as a pointer or auxiliary note rather than as a competing
   canonical tracker.
4. Keep the bootstrap output minimal and editable by future maintainers.
5. Do not invent project charter policy. If no explicit charter content is
   supplied, keep project-charter files limited to repository purpose,
   repository-specific context, and explicit human-approved decisions.
6. Put evolving shared terminology in the ubiquitous-language doc, not in the
   charter, and keep that terminology descriptive rather than policy-setting.

## Outputs
- Installed or repaired governance files
- Any required entry-point link updates
- Validation status for the package structure and the target repository