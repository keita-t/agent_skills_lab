# Documentation Update Rules

## Purpose

This file is the canonical policy source for documentation updates in this
repository. Read it before creating, rewriting, splitting, merging, or deleting
stable files under `docs/`.

Related canonical docs:
[docs/README.md](./README.md)
[docs/project-charter.md](./project-charter.md)
[docs/ubiquitous-language.md](./ubiquitous-language.md)
[docs/TODO.md](./TODO.md)

The project charter is not a generic rules catalog. By default it stays
minimal and records only repository-specific scope and explicit maintainer
decisions. Shared vocabulary belongs in the ubiquitous-language doc.

## Canonical Document Set

| Path | Role | Notes |
|---|---|---|
| docs/README.md | Documentation map | Entry point for readers and agents. |
| docs/TODO.md | Operational backlog | Routine maintenance is allowed; structural reorganization requires an explicit in-session human instruction. |
| docs/DOCUMENTATION_UPDATE_RULES.md | Documentation governance | Canonical policy source for docs updates. |
| docs/project-charter.md | Project charter | Repository-specific context and explicit maintainer decisions. It may intentionally remain minimal. |
| docs/ubiquitous-language.md | Ubiquitous language | Shared project vocabulary that agents may maintain for context alignment without adding policy. |

If the repository needs additional permanent docs, extend `docs/README.md` and
describe each new file's responsibility in the same change.

## Update Triggers

- Project-specific scope or explicit maintainer decisions changed and a
  maintainer explicitly instructed charter edits: update the charter in the
  same change.
- Shared project vocabulary or context-alignment terminology changed:
  update the ubiquitous-language doc in the same change. Update the charter
  only if a maintainer explicitly instructs editing it.
- Public contract changed: update the affected reference or overview docs in
  the same change.
- Implementation behavior or developer workflow changed: update the docs that
  explain that behavior in the same change.
- Documentation structure changed: update `docs/README.md`, `README.md`,
  `CLAUDE.md`, and any `docs/TODO.md` references in the same change.
- Before any docs-only rewrite, read the charter when repository-specific
  context matters and read the ubiquitous-language doc when terminology or
  context alignment matters. If the charter is minimal, rely on this file,
  the ubiquitous-language doc, and the implementation-facing docs first.

## Placement And Rewrite Rules

- Keep the split explicit between overview-style docs and implementation-style
  docs.
- Use crosswalk-first planning before large rewrites. Decide where each current
  section moves before editing prose.
- Do not leave stale summary sections behind after content has moved.
- Keep claims anchored to implemented behavior, not future intent.
- Keep ubiquitous-language docs descriptive. They may help align terminology,
  but they must not become a backdoor policy surface.
- `docs/TODO.md` may receive routine maintenance as normal work. Structural
  reorganization is allowed only on an explicit in-session human instruction.

## Quality Bar

Every moved or rewritten section should fit one clear granularity level.

| Label | Expected scale | Use |
|---|---|---|
| Snapshot | 3-5 sentences | Quick orientation and caveats. |
| Overview | 1-2 paragraphs | Responsibilities and current design intent. |
| Table | 1 main table | Stable inventories and maps. |
| Flow | 5-8 ordered steps | Ordered behavior and lifecycle flows. |
| Checklist | 5-8 items | Update rules, extension steps, validation gates. |
| Reference | Complete structured coverage | Detailed stable contracts. |

## Mermaid Policy

Use Mermaid only when it materially improves comprehension over text or tables.
Keep the set of diagram families intentionally small and document approved
families before adding new ones.

## Validation Checklist

1. `docs/README.md` still routes readers to the canonical docs.
2. `README.md` and `CLAUDE.md` still link to `docs/README.md` and this file.
3. `docs/ubiquitous-language.md` stays aligned with the current terminology contract.
4. `docs/TODO.md` edits are either routine maintenance or explicitly approved
   structural reorganization.
5. Rewritten sections match one clear granularity label.
6. Relative links remain valid after file moves or renames.

## Skill Compatibility Contract

- Trigger phrases: `rewrite docs`, `refine docs`, `sync docs with code`,
  `update documentation after implementation`, `update docs map`.
- Required inputs: changed files, affected contracts or workflows, current docs
  map, and language mode.
- Expected outputs: updated docs, updated navigation links, deleted superseded
  sections when needed, and a short validation summary.
- Forbidden shortcuts: leaving stale sections in place, changing only entry
  points without changing canonical docs, and autonomously restructuring
  `docs/TODO.md` without explicit in-session human instruction.