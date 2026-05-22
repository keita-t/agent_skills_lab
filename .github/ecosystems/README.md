# Ecosystems Classification

This folder contains the canonical manifests and shared automation for
ecosystems managed in this repository.

## Navigation
- Ecosystem registry: [../ECOSYSTEM_REGISTRY.md](../ECOSYSTEM_REGISTRY.md)
- Agents-skills routing map: [../AGENT_SKILL_ROUTING.md](../AGENT_SKILL_ROUTING.md)
- Agents classification: [../agents/README.md](../agents/README.md)
- Skills classification: [../skills/README.md](../skills/README.md)

## Shared Scripts
- [install_ecosystem.sh](install_ecosystem.sh): Import a selected ecosystem into
  another project.
- [update_ecosystem_core_files.sh](update_ecosystem_core_files.sh): Regenerate
  `.github` core management files from installed ecosystem manifests.
- [validate_ecosystem_registry.sh](validate_ecosystem_registry.sh): Validate the
  registry, manifests, routing links, and ecosystem membership metadata.

## Ecosystem Manifests
- [repository-governance/ECOSYSTEM.md](repository-governance/ECOSYSTEM.md):
  Repository documentation governance, bootstrap, and TODO progress tracking.

## Maintenance Rules
- Keep one ecosystem per subdirectory under `.github/ecosystems/`.
- Keep human-readable policy in Markdown manifests and machine-readable fields
  in manifest frontmatter.
- Treat `.github/ECOSYSTEM_REGISTRY.md` as the inventory of record and these
  manifests as the detailed source of truth.