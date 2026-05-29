# New Ecosystem Audit Smoke Scenario

Use this scenario after adding a new ecosystem and its first audit pack.

## Source Repository Smoke

1. Add the new ecosystem manifest, root agent, and any owned files.
2. Declare the ecosystem-specific audit file in the manifest `audit-files`
   field.
3. Introduce one deliberate structural defect, such as a broken `root-agent`
   entry, a missing owned file, or a bad dependency slug.
4. Ask the Ecosystem Audit Agent to audit the source repository and confirm the
   shared core rules report the defect.
5. Fix the structural defect and rerun the audit.
6. Introduce one deliberate work-quality weakness in the source definitions,
   such as ambiguous guidance, incomplete coverage notes, or a missing recovery
   path.
7. Ask the Ecosystem Audit Agent to audit again and confirm the quality report
   marks the weakness with a rubric rating and `definition-inferred` evidence
   when no runtime trace exists.

## Installed Target Repository Smoke

1. Install the new ecosystem into a temporary target repository.
2. Introduce one deliberate ecosystem-specific defect covered by the new audit
   pack, such as a broken manifest-owned path, a stale route to a source-only
   helper, or an invalid generated-output expectation.
3. Ask the Ecosystem Audit Agent to audit the installed target repository and
   confirm the ecosystem-specific audit pack reports the defect.
4. Fix the defect and rerun the audit.
5. Introduce one deliberate work-quality defect in an installed artifact, such
   as low-signal output, unclear operator guidance, or a mismatch with user
   constraints.
6. Ask the Ecosystem Audit Agent to audit the installed target repository again
   and confirm the report includes a rubric summary, evidence basis,
   confidence, and upstream improvement feedback.

## Exit Criteria

- Shared core rules report source-repository structural defects.
- The ecosystem-specific audit pack reports at least one installed-target
  defect.
- Work-quality review produces at least one rubric-based quality finding.
- The audit report identifies the relevant manifest or file path for each
  deliberate defect.