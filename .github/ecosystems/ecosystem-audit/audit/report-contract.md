# Ecosystem Audit Report Contract

When reporting audit results, use a stable finding structure.

## Rubric Summary

Start with a rubric-first summary before detailed findings.

Each rubric row should include:

- Dimension
- Rating
- Evidence basis
- Confidence
- Short rationale

Recommended default ratings are `Strong`, `Acceptable`, `Needs Work`, and
`Not Assessed`.

## Finding Shape

- Severity: `error`, `warning`, or `note`
- Scope: source repository, installed target repository, or specific ecosystem
- Rule source: shared core rules or the path to the ecosystem-specific audit
  file that introduced the check
- Dimension: optional quality dimension such as `correctness` or `clarity`
- Evidence basis: `artifact-observed`, `runtime-observed`, or
  `definition-inferred`
- Confidence: `high`, `medium`, or `low`
- Impact: short statement of why the finding matters to the current repository
  or ecosystem user
- Path: affected file or manifest when one is known
- Message: concise explanation of the mismatch
- Improvement feedback: optional remediation guidance labeled as either
  `local-fix` or `upstream-ecosystem-feedback`

## Expected Sections

1. Scope summary
2. Rubric summary
3. Findings ordered by severity
4. Files and manifests inspected
5. Suggested follow-up, including upstream ecosystem feedback when relevant

## Reporting Rules

- Prefer rubric-first, evidence-backed reports over freeform-only narratives.
- Do not require a single aggregate quality score in this slice.
- When runtime evidence is unavailable, behavior-quality findings must be
  labeled `definition-inferred` instead of being presented as observed runtime
  facts.