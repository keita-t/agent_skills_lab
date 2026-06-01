# Audit Pack Template

Use this template when a new ecosystem needs its own audit pack on top of the
shared `ecosystem-audit` platform.

## Placement

1. Create the ecosystem-specific audit file under
   `.github/ecosystems/<slug>/audit/`.
2. Add the new file path to the manifest frontmatter field `audit-files`.
3. Keep the audit file inside the manifest-owned payload so delivery can ship
   it together with the ecosystem.

## Suggested Structure

```md
# <Ecosystem Name> Audit Pack

Apply these checks only when the `<slug>` ecosystem is present in the source
repository or installed target repository.

## Structural Checks

1. <First ecosystem-specific invariant>
2. <Second ecosystem-specific invariant>

## Artifact Quality Rubric

- Dimension: <quality dimension>
- Rating guidance: <what counts as Strong / Acceptable / Needs Work>
- Preferred evidence basis: <artifact-observed | runtime-observed>

## Behavior Quality Rubric

- Dimension: <quality dimension>
- Rating guidance: <what counts as Strong / Acceptable / Needs Work>
- Preferred evidence basis: <runtime-observed | definition-inferred>

## Evidence Sources

- <installed files>
- <generated output>
- <runtime examples or logs, when available>

## Upstream Improvement Feedback

1. <feedback that should loop back into the source ecosystem>
```

## Authoring Notes

- Reuse the shared core rules for manifest structure, dependency, and
  portability checks. Put only ecosystem-specific checks in this audit pack.
- Reuse the shared work-quality rubric for the quality dimensions and keep this
  file focused on ecosystem-specific interpretations of those dimensions.
- Prefer checks that can be grounded in implemented behavior, shipped files,
  or documented contracts already owned by the ecosystem.
- When the ecosystem opts into the shared installed runtime contract, audit the
  runtime launcher, declared host prerequisite set, and runtime outputs as a
  behavior contract distinct from the manifest-owned payload.
- When the ecosystem has generated output, distinguish runtime output from the
  manifest-owned payload explicitly.
- If the ecosystem depends on another installable ecosystem, mention only the
  dependency behavior that is specific to this ecosystem rather than repeating
  the shared dependency rules.
- Prefer rubric-first output and avoid mandatory numeric scores unless the
  ecosystem truly needs them later.
