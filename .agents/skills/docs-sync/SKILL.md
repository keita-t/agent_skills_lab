---
name: docs-sync
description: 'Sync repository docs with implementation changes, update docs maps, and keep repository entry points aligned.'
ecosystem: repository-docs
argument-hint: 'Describe the changed code, affected contracts or workflows, and the document set that must stay aligned.'
---

# Docs Sync

## When To Use
- Update canonical docs after implementation changes.
- Rewrite or refine repository documentation while keeping navigation aligned.
- Sync root entry points such as `README.md`, `CLAUDE.md`, and `docs/README.md`
  after document structure changes.
- Use `docs-refactor` instead when the main request is a
  docs-only refactor of stale claims, implementation-log prose, mechanical
  wording, or diagram quality.

## Role
You are the sync skill for repository documentation.
Your purpose is to keep docs structurally clear, directly traceable to
implemented behavior, and easy for humans and AI agents to follow.

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
8. After the repository docs pack or bootstrap output has been applied to the
   target repository, ask the Ecosystem Audit Agent to audit the repository
   using the shared core rules and the shipped repository-docs audit
   pack. State whether the repository should be checked in bilingual or
   single-language mode. Before bootstrap, or when reviewing a shipped template
   pack or another checkout, inspect the matching template path under
   `.ai_ecosystems/repository-docs/assets/templates/<mode>` together
   with the repository-docs audit file.

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
   those edits to `todo-maintenance`.
8. Edit project-charter files only when a maintainer explicitly instructs
   editing the charter.
9. Route shared vocabulary and context-alignment updates into the
   ubiquitous-language docs, and keep those docs descriptive rather than
   policy-setting.

## Outputs
- Updated canonical documentation files
- Updated navigation links and entry points when required
- A short validation summary covering changed docs and link integrity
