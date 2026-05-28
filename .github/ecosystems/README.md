# Ecosystems Classification

This folder contains the canonical manifests and thin delivery and validation
helpers for ecosystems managed in this repository.

## Source Of Truth
- Each ecosystem is defined by a manifest at `.github/ecosystems/<slug>/ECOSYSTEM.md`.
- Agent and skill membership is declared in manifest frontmatter and in the
  matching file frontmatter under `.github/agents/` and `.github/skills/`.
- Manifest-owned payload is defined by the listed agents, skills,
  `ecosystem-files`, and the manifest itself.

## Shared Scripts
- [deliver_ecosystem.py](deliver_ecosystem.py): Execute manifest-owned install
  or remove workflows against a target `owner/repo` and prepare a PR-based
  delivery flow.
- [validate_ecosystem_registry.sh](validate_ecosystem_registry.sh): Validate the
  manifests, frontmatter alignment, and structural ecosystem membership.

## Installed Ecosystems
- [repository-governance/ECOSYSTEM.md](repository-governance/ECOSYSTEM.md):
  Repository documentation governance, bootstrap, TODO progress tracking, and
  ecosystem manifest and delivery orchestration.

## Maintenance Rules
- Keep one ecosystem per subdirectory under `.github/ecosystems/`.
- Keep human-readable policy in Markdown manifests and machine-readable fields
  in manifest frontmatter.
- Keep this file as a thin index and use the manifests as the detailed source
  of truth.