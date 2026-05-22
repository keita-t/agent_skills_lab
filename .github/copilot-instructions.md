When working with ecosystems, repository documentation, or progress tracking in
this workspace:

- Read `.github/ECOSYSTEM_REGISTRY.md` and `.github/ecosystems/README.md`
  before changing ecosystem-managed agents, skills, manifests, or routing
  files.
- Prefer `Repository Context Manager` for orchestrating the
  `repository-governance` ecosystem.
- Prefer `repository-governance-bootstrap` for initial setup, repair, or
  validator installation.
- Prefer `repository-doc-governance` for canonical docs updates after code or
  workflow changes.
- Prefer `todo-progress-governance` for TODO, backlog, or design-review
  maintenance.
- Use `bash .github/ecosystems/install_ecosystem.sh` to import a selected
  ecosystem into another project.
- Use `bash .github/ecosystems/update_ecosystem_core_files.sh --target-repo .`
  to regenerate `.github` core management files from installed ecosystem
  manifests.
- Run `bash .github/ecosystems/validate_ecosystem_registry.sh --repo-root .`
  after changing ecosystem manifests or ecosystem-aware core files.
- If `docs/README.md` and `docs/DOCUMENTATION_UPDATE_RULES.md` exist, read them
  before rewriting prose.
- Keep repository entry points such as `README.md`, `CLAUDE.md`, and
  `docs/README.md` aligned in the same change when document structure changes.
- Never structurally reorganize `docs/TODO.md` or the repository's canonical
  progress file without explicit in-session user instruction.