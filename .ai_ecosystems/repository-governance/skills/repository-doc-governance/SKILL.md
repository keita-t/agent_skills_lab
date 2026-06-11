---
name: repository-doc-governance
description: 'Sync repository documentation with implementation, rewrite docs safely, update documentation maps, and keep repository entry points aligned with code changes.'
ecosystem: repository-governance
argument-hint: 'Describe the changed code, affected contracts or workflows, and the document set that must stay aligned.'
---

# Repository Documentation Governance

## When To Use
- Update canonical docs after implementation changes.
- Rewrite or refine repository documentation while keeping navigation aligned.
- Sync root entry points such as `README.md`, `CLAUDE.md`, and `docs/README.md`
  after document structure changes.

## Role
You are the canonical policy skill for repository document management.
Your purpose is to keep repository documentation structurally clear, directly
traceable to implemented behavior, and easy for humans and AI agents to follow.

## Required Inputs
- Changed files and affected implementation areas.
- Affected public contracts, runtime boundaries, or developer workflows.
- The current canonical docs map and update rules.
- The chosen language mode for the repository.

## Procedure
1. Read the repository charter, documentation update rules, and docs map before
   editing prose. Treat the charter as project-specific context, not as a
   place to invent generic rules or terminology catalogs.
2. Determine which canonical documents must change based on the implementation
   delta.
3. Before large rewrites, decide where each affected section will move and only
   then edit the prose.
4. When the repository already has a stable docs grouping such as `docs/en`
   and `docs/ja`, place new repository-facing docs inside that structure and
   reuse neighboring naming conventions. Add a new root-level `docs/` file only
   when no clearer placement guidance exists.
5. Update entry-point links in the same change when document structure or file
   names change.
6. Keep rewritten sections at one clear granularity level such as snapshot,
   overview, table, flow, checklist, or reference.
7. Validate links and structural alignment before finishing.
8. After the governance doc pack or bootstrap output has been applied to the
   target repository, ask the Ecosystem Audit Agent to audit the repository
   using the shared core rules and the shipped repository-governance audit
   pack. State whether the repository should be checked in bilingual or
   single-language mode. Before bootstrap, or when reviewing a shipped template
   pack or another checkout, inspect the matching template path under
   `.ai_ecosystems/repository-governance/assets/templates/<mode>` together
   with the repository-governance audit file.

## Rules
1. Keep overview documents about what the system is and implementation
   documents about how the code is organized and operated.
2. Prefer implemented behavior over future-looking speculation in canonical
   docs.
3. Do not leave stale summary sections behind after content has moved.
4. If the repository already has a clear docs directory structure, preserve it
   for new repository-facing docs and follow neighboring file naming patterns.
5. In bilingual repositories, keep shared navigation and governance files at
   the root of `docs/` and place topical reference docs as paired language
   files under the existing language directories.
6. If the repository uses paired languages, keep the counterparts structurally
   aligned in the same change.
7. Do not autonomously restructure TODO or progress documents here; delegate
   those edits to `todo-progress-governance`.
8. Edit project-charter files only when a maintainer explicitly instructs
   editing the charter.
9. Route shared vocabulary and context-alignment updates into the
   ubiquitous-language docs, and keep those docs descriptive rather than
   policy-setting.

## Outputs
- Updated canonical documentation files
- Updated navigation links and entry points when required
- A short validation summary covering changed docs and link integrity
