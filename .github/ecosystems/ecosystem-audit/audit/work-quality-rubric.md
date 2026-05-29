# Ecosystem Audit Work-Quality Rubric

Apply this shared rubric to every ecosystem after structural conformance checks.

## Recommended Rating Scale

- `Strong`: Evidence indicates the ecosystem performs well for this dimension
  with no meaningful correction needed now.
- `Acceptable`: The ecosystem is serviceable for this dimension, but some
  improvement headroom remains.
- `Needs Work`: The dimension has a meaningful weakness that should feed back
  into ecosystem improvement.
- `Not Assessed`: The current audit did not have enough evidence to evaluate
  the dimension.

Use qualitative ratings by default. Do not collapse the rubric into a single
aggregate score in this slice.

## Evidence Basis

- `artifact-observed`: Based on delivered or installed files, generated output,
  or repository content that the audit can inspect directly.
- `runtime-observed`: Based on actual execution traces, logs, or user-provided
  runtime examples.
- `definition-inferred`: Based on prompts, skills, manifests, guidance, or
  other static definitions when runtime evidence is unavailable.

## Shared Quality Dimensions

1. `correctness`
   - Does the ecosystem appear to perform the right work without violating its
     own contract?
2. `completeness`
   - Does the ecosystem cover the expected work scope, including required
     artifacts, guidance, and recovery paths?
3. `constraint-adherence`
   - Does the ecosystem respect explicit user instructions, manifest-owned
     boundaries, and documented delivery constraints?
4. `clarity`
   - Are the ecosystem's outputs, instructions, and guidance understandable and
     easy to follow?
5. `maintainability`
   - Does the ecosystem stay adaptable, with changes localized to the owning
     contract and without avoidable duplication?
6. `operator-ergonomics`
   - Does the ecosystem provide a practical operator experience for maintainers
     and target-repository users?
7. `recovery-behavior`
   - When information is incomplete or the environment is imperfect, does the
     ecosystem guide the operator toward safe recovery rather than silent
     failure?

## Reporting Rules

- Start quality reporting with a rubric summary table or equivalent compact
  section that lists the evaluated dimensions and their ratings.
- Every rubric row should cite the dominant evidence basis and confidence.
- Follow the rubric summary with detailed findings and upstream improvement
  feedback when a dimension is rated `Needs Work` or when a `Strong` rating
  still depends on narrow evidence.