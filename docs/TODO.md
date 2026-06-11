# TODO

This document aggregates the repository backlog and design-review notes.

## This Document Structure And Update Rules

- **Implementation Backlog**: concrete tasks that are ready to be worked on.
  Remove completed items in normal pull requests.
- **Unresolved Design Concerns**: design-review issues that are not yet broken
  into concrete tasks. Append progress below each item instead of rewriting the
  original concern text.
- **Resolved Concerns Record**: short traces for concerns that are fully
  resolved. Delete items when they no longer help future design decisions.
- Preserve original review wording whenever possible. Add `Status` and `Trace`
  lines below the concern instead of editing the concern body directly.
- routine maintenance is allowed as normal work. This includes removing
  completed backlog items, appending progress, and deleting fully resolved
  concerns.
- Structural reorganization of this file is allowed only on an explicit in-session human instruction. See
  [docs/DOCUMENTATION_UPDATE_RULES.md](./DOCUMENTATION_UPDATE_RULES.md).

## Implementation Backlog

- Add a second ecosystem fixture and multi-ecosystem updater tests.
- Add pytest coverage for shell wrappers as lightweight smoke checks.
- Add a dedicated self-host bootstrap command for this repository's docs.

## Unresolved Design Concerns

### Managed block scope in generated core files

The current updater preserves text outside managed blocks, but the long-term
boundary between handwritten explanatory text and generated sections still needs
clearer authoring guidance.

Status: not started
Trace: docs/DOCUMENTATION_UPDATE_RULES.md

### Template evolution policy for self-hosted docs

This repository now uses repository-governance templates as its own stable
documentation base. The policy for when self-host docs should diverge from the
templates remains intentionally narrow and should be made explicit in follow-up
guidance.

Status: not started
Trace: .ai_ecosystems/repository-governance/assets/templates/bilingual

## Resolved Concerns Record

- Moved repository-governance-owned templates and validators out of the bootstrap
  skill directory and into the ecosystem directory to make install payload
  ownership explicit.