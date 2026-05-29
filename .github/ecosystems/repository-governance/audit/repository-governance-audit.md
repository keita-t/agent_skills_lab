# Repository Governance Audit Pack

Apply these checks only when the `repository-governance` ecosystem is present in
the source repository or installed target repository.

## Structural Checks

1. Required governance entry points must exist for the repository mode in use.
   In single-language mode this includes `docs/README.md`,
   `docs/DOCUMENTATION_UPDATE_RULES.md`, `docs/TODO.md`,
   `docs/project-charter.md`, and `docs/ubiquitous-language.md`.
   In bilingual mode this includes `docs/README.md`,
   `docs/DOCUMENTATION_UPDATE_RULES.md`, `docs/TODO.md`,
   `docs/en/project-charter.md`, `docs/en/ubiquitous-language.md`,
   `docs/ja/project-charter.ja.md`, and `docs/ja/ubiquitous-language.ja.md`.
2. `README.md` and `CLAUDE.md` must route readers to `docs/README.md` and the
   documentation update rules.
3. The English and Japanese ecosystem inventory docs should stay aligned with
   the installed ecosystems and current manifest-owned payload contracts.
4. Relative Markdown links inside the repository-governance docs pack should
   resolve successfully inside the current repository.
5. `docs/TODO.md` should preserve the routine-maintenance versus explicit-human-
   approval distinction for structural reorganization.

## Template Pack Checks

1. The shipped template packs under
   `.github/ecosystems/repository-governance/assets/templates/` should still
   contain their own documentation map and update rules.
2. Installed guidance should refer users to the shared audit agent for
   on-demand validation instead of requiring Python validator execution in the
   target repository.

## Artifact Quality Rubric

- `clarity`
   - Strong: navigation, update rules, and installed guidance are easy to scan
      and lead operators to the right next action without guesswork.
   - Needs Work: readers must infer routing or validation behavior from scattered
      prose.
- `completeness`
   - Strong: required docs, template packs, and installed guidance cover both
      steady-state use and typical maintenance tasks.
   - Needs Work: core repository-governance workflows are left implicit or only
      partially described.
- `constraint-adherence`
   - Strong: docs preserve manifest-owned boundaries, bilingual alignment, and
      TODO governance constraints.
   - Needs Work: guidance blurs structural versus routine change boundaries or
      drifts across language counterparts.
- `operator-ergonomics`
   - Strong: installed maintainers can understand how to bootstrap, audit, and
      repair governance docs with minimal friction.
   - Needs Work: operator guidance is technically correct but impractical to use
      in a target repository.
- `maintainability`
   - Strong: repository-facing docs and installed guidance avoid unnecessary
      duplication and keep ownership clear between manifests, templates, and docs.
   - Needs Work: the same policy or routing guidance must be synchronized in too
      many places.

## Behavior Quality Rubric

- `correctness`
   - Evaluate whether governance agents and skills route users to the correct
      workflows for docs sync, bootstrap, TODO governance, and audit.
- `clarity`
   - Evaluate whether prompts and guidance set clear expectations for what the
      governance workflows will change and what they will leave untouched.
- `recovery-behavior`
   - Evaluate whether the ecosystem explains how to recover from missing docs,
      misalignment, or incomplete repository context without guessing.
- `definition-inferred` evidence note
   - When no runtime logs exist, treat these behavior-quality checks as design
      quality review of prompts, skills, manifests, and installed guidance.

## Evidence Sources

- Repository-facing docs under `docs/`, `README.md`, and `CLAUDE.md`
- Installed template packs under
   `.github/ecosystems/repository-governance/assets/templates/`
- Governance agent and skill definitions that route work inside the ecosystem

## Upstream Improvement Feedback

1. Prefer upstream feedback when installed guidance is technically correct but
    unclear, duplicated, or operationally awkward.
2. When bilingual docs drift in quality rather than pure structure, suggest an
    upstream documentation rewrite instead of treating it only as a local fix.
