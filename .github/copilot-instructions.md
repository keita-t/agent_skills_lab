When working with ecosystems, repository documentation, or progress tracking in
this workspace:

- Read `.github/ecosystems/README.md` and the relevant
  `.github/ecosystems/<slug>/ECOSYSTEM.md` manifest before changing
  ecosystem-managed agents, skills, manifests, or support files.
- Prefer `Repository Context Manager` for orchestrating the
  `repository-governance` ecosystem.
- Prefer `Ecosystem Manifest Governor` for ecosystem manifest definition,
  ownership-contract cleanup, and membership validation changes.
- Prefer `Ecosystem Delivery Orchestrator` for ecosystem install or remove
  workflows that target another repository.
- Prefer `repository-governance-bootstrap` for initial setup, repair, or
  audit-guidance installation.
- Prefer `repository-doc-governance` for canonical docs updates after code or
  workflow changes.
- Prefer `todo-progress-governance` for TODO, backlog, or design-review
  maintenance.
- For local smoke checks or automation, use
  `python .github/ecosystems/deliver_ecosystem.py install|remove --target-repo owner/repo --ecosystem <slug>`.
- Ask the `Ecosystem Audit Agent` to audit the current ecosystems after
  changing ecosystem manifests, dependencies, audit files, or ecosystem-aware
  core files.
- If `docs/README.md` and `docs/DOCUMENTATION_UPDATE_RULES.md` exist, read them
  before rewriting prose.
- Keep repository entry points such as `README.md`, `CLAUDE.md`, and
  `docs/README.md` aligned in the same change when document structure changes.
- Never structurally reorganize `docs/TODO.md` or the repository's canonical
  progress file without explicit in-session user instruction.