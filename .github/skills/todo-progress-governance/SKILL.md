---
name: todo-progress-governance
description: 'Update TODO and progress-tracking documents under strict routine-versus-structural rules. Use for backlog maintenance, design-review follow-up, status append, and resolved-trace updates.'
ecosystem: repository-governance
argument-hint: 'Describe the TODO or backlog change, whether it is routine maintenance, and any related implementation or PR references.'
---

# TODO Progress Governance

## When To Use
- Remove completed backlog items from a canonical TODO file.
- Append status or tracking references to design-review concerns.
- Move fully resolved concerns into a short resolved record.
- Decide whether a requested TODO edit is routine maintenance or structural
  reorganization.

## Role
You are the canonical policy skill for progress-governance documents.
Your purpose is to keep backlog and design-review tracking files concise,
traceable, and protected from unauthorized structural rewrites.

## Required Inputs
- The current canonical TODO or backlog file.
- The section-level update rules written inside that file.
- Related implementation changes, issue links, or PR references.
- Whether the requested edit changes content only or restructures the file.

## Procedure
1. Read the TODO file's self-described update rules before planning edits.
2. Classify the request as routine maintenance or structural reorganization.
3. For routine maintenance, apply the smallest change that preserves the file's
   existing structure.
4. Preserve original design-review wording and append progress below it instead
   of rewriting the review text.
5. When a concern is fully resolved, move it to a short resolved record if the
   file's own rules say to do so.
6. If the request is structural reorganization, stop and request explicit
   in-session approval before editing.
7. Re-run repository governance validation when TODO links or canonical entry
   points change.

## Rules
1. Never autonomously re-section, merge, split, or wholesale-rewrite the TODO
   file.
2. Keep completed-item removal and status append operations rule-compliant and
   local.
3. Update related references when file names or linked docs change.
4. If the repository has both implementation docs and progress docs, keep the
   TODO focused on follow-up work rather than detailed technical reference.

## Outputs
- Updated TODO or backlog file when the request is routine and allowed
- An approval request when the change is structural and therefore guarded
- A short summary of what changed and what remains tracked