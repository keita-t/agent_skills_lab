# Ecosystem Audit Core Rules

Apply these checks to every ecosystem manifest in the repository or installed
target repository.

## Cross-Ecosystem Rules

1. Required manifest keys must exist: `slug`, `name`, `description`, `status`,
   `root-agent`, `agents`, `skills`, `dependencies`, and `ecosystem-files`.
2. The manifest `slug` must match its parent directory name.
3. The `root-agent` must also appear in `agents`.
4. Every listed agent file must exist and declare matching `ecosystem`
   frontmatter.
5. Every listed skill directory must exist and declare matching `ecosystem`
   frontmatter.
6. Every listed `ecosystem-files` path and every listed `audit-files` path must
   exist inside the repository.
7. The dependency graph must not reference unknown slugs and must not contain
   cycles.
8. Installable markdown inside a manifest-owned payload must keep repository-
   local links inside that same manifest-owned payload so installed artifacts
   remain self-contained.
9. `audit-files` should stay under `.ai_ecosystems/<slug>/audit/` unless the
   manifest clearly owns a different audit path.
10. Installed runtime metadata is optional. When `runtime-mode` is present,
    `runtime-entrypoint` must reference a manifest-owned path,
    `runtime-requires` must describe the supported host prerequisite set, and
    runtime output must stay distinct from install/remove ownership unless the
    manifest explicitly owns that output path.

## Installed Repository Notes

- When auditing an installed target repository, treat the installed manifests as
  the source of truth.
- If a dependency ecosystem is present, apply its shared or ecosystem-specific
  audit files before auditing dependents that rely on it.
