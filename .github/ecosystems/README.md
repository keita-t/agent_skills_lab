# Ecosystems Classification

This folder contains the canonical manifests plus thin delivery helpers and
shared audit assets for ecosystems managed in this repository.

## Source Of Truth
- Each ecosystem is defined by a manifest at `.github/ecosystems/<slug>/ECOSYSTEM.md`.
- Agent and skill membership is declared in manifest frontmatter and in the
  matching file frontmatter under `.github/agents/` and `.github/skills/`.
- Manifest-owned payload is defined by the listed agents, skills,
  `ecosystem-files`, `audit-files`, and the manifest itself.

## Installed Runtime Contract
- Installed runtime is optional. Ecosystems that do not execute installed code
  in target repositories omit runtime metadata entirely.
- Runtime-enabled ecosystems may declare `runtime-mode`,
  `runtime-entrypoint`, and `runtime-requires` in manifest frontmatter.
- Ecosystems may also declare `shared-ownership-files` for manifest-owned paths
  that multiple installed ecosystems are allowed to co-own explicitly.
- Runtime assets still belong in `ecosystem-files`; runtime metadata describes
  execution behavior and host prerequisites, not extra ownership.
- Delivery copies a duplicate manifest-owned path only when every owning
  ecosystem declares that exact path in `shared-ownership-files`; removals keep
  the shared path in place until the last installed owner is removed.
- Supported installed runtime mode today is `container`, which standardizes on
  a manifest-owned launcher and disposable Docker execution.
- Runtime-enabled launchers may source the shared
  `.github/ecosystems/runtime_container_lib.sh` helper to reuse the bind-mount
  probe and `docker cp` fallback transport needed for Docker-outside-of-Docker
  environments.
- Runtime-enabled smoke should invoke the declared runtime launcher directly so
  the runtime container remains the only execution boundary.

## Shared Delivery Helper
- [deliver_ecosystem.py](deliver_ecosystem.py): Execute manifest-owned install
  or remove workflows against a target `owner/repo`, resolve manifest
  dependencies, and prepare a PR-based delivery flow.
- [runtime_container_lib.sh](runtime_container_lib.sh): Shared shell helper for
  installed `container` runtimes, including repo-root argument normalization,
  bind-mount probing, and copy-based fallback transport.

## Installed Ecosystems
- [ecosystem-audit/ECOSYSTEM.md](ecosystem-audit/ECOSYSTEM.md):
  Shared audit platform for ecosystem manifests and installed ecosystem
  payloads, plus rubric-first work-quality evaluation extended through
  manifest-declared audit files. Ships starter audit pack templates and smoke
  scenarios for newly added ecosystems.
- [codebase-context/ECOSYSTEM.md](codebase-context/ECOSYSTEM.md):
  Export a repository into a single markdown context file for large-context
  models, with default broad coverage, explicit user pickup rules, a shared
  installed runtime contract in `container` mode, and a manifest-declared
  audit pack that can assess export usefulness and operator experience.
- [repository-governance/ECOSYSTEM.md](repository-governance/ECOSYSTEM.md):
  Repository documentation governance, bootstrap, TODO progress tracking,
  ecosystem manifest and delivery orchestration, and a governance-specific
  audit pack that can assess document and operator quality as well as
  structural conformance.

## Maintenance Rules
- Keep one ecosystem per subdirectory under `.github/ecosystems/`.
- Keep human-readable policy in Markdown manifests and machine-readable fields
  in manifest frontmatter.
- For installable ecosystems, keep repository-local links inside
  manifest-owned Markdown self-contained to the manifest-owned payload unless
  the manifest explicitly lists the target path.
- Keep ecosystem-specific audit rules in the owning ecosystem and expose them
  through `audit-files` instead of centralizing ecosystem-specific policy in
  shared scripts.
- Prefer rubric-first quality feedback over score-only or freeform-only audit
  output.
- Keep this file as a thin index and use the manifests as the detailed source
  of truth.
