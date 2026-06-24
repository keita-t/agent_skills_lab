---
name: docs-refactor
description: 'Refactor repository documentation so prose, diagrams, and structure objectively reflect the current codebase.'
ecosystem: repository-docs
argument-hint: 'Describe the document set to refactor, relevant code paths, and whether the repository is single-language or bilingual.'
---

# Docs Refactor

## When To Use
- Refactor existing documentation without a separate implementation change.
- Find and fix documentation claims that drift from or contradict the codebase.
- Remove implementation-log, decision-journal, or weakly code-related prose from
  stable docs.
- Rewrite mechanical or awkward wording into clear, human-readable prose.
- Decide whether a section needs a Mermaid diagram, or replace fragile ASCII
  diagrams with Mermaid.

## Role
You are the documentation refactoring skill for repository-facing docs.
Your purpose is to make stable documentation objective, readable, and grounded
in the implemented codebase rather than in authoring history or speculative
design notes.

## Required Inputs
- The target document paths and repository language mode.
- Relevant implementation paths, public contracts, commands, or workflows.
- The current docs map, documentation update rules, and Mermaid policy.
- Any user-specified scope limits for prose, structure, or diagrams.

## Procedure
1. Read the docs map, documentation update rules, and relevant source files
   before rewriting.
2. Build a short crosswalk from each target section to the code, manifest,
   command, workflow, or test evidence that supports it.
3. Mark unsupported, stale, contradictory, speculative, implementation-log, or
   decision-journal prose before editing.
4. Rewrite supported content as an objective snapshot of current behavior. Keep
   design rationale only when it is required to understand the implemented
   contract.
5. Replace mechanical wording with direct natural language while preserving
   precise names, commands, paths, and contracts.
6. Add a Mermaid diagram only when it materially improves comprehension over
   prose or a table. Prefer Mermaid for lifecycle flows, ownership boundaries,
   and dependency relationships; prefer tables for inventories and crosswalks.
7. Replace ASCII diagrams that are likely to wrap, drift, or render
   inconsistently with Mermaid when the diagram remains useful.
8. In bilingual repositories, apply the same structural refactor to both
   language counterparts in the same change.
9. Validate relative links, headings, diagram fences, and document-map alignment
   before finishing.

## Rules
1. Anchor every retained factual claim to current implementation, tests,
   manifests, or stable repository workflows.
2. Do not preserve prose just because it explains past authoring decisions.
   Move unresolved follow-up work to the canonical TODO only when the requested
   change is routine and allowed by that file's rules.
3. Do not expand the project charter unless a maintainer explicitly instructs
   charter edits.
4. Keep rewritten sections at one clear granularity level such as snapshot,
   overview, table, flow, checklist, or reference.
5. Use Mermaid sparingly and keep diagrams small enough to maintain.
6. Do not add diagrams for decoration or duplicate information that a compact
   table already communicates more clearly.
7. When refactoring installable ecosystem payload docs, keep repository-local
   links self-contained inside the manifest-owned payload unless the manifest
   explicitly owns the target path.

## Outputs
- Updated documentation that reflects the current codebase
- A brief list of drift or contradiction fixes made
- Any Mermaid diagram additions or replacements
- Validation status for links, structure, and bilingual alignment
