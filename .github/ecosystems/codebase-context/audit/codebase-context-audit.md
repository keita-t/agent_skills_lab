# Codebase Context Audit Pack

Apply these checks only when the `codebase-context` ecosystem is present in the
source repository or installed target repository.

## Structural Checks

1. The manifest-owned generator entry points
   `.github/ecosystems/codebase-context/generate_codebase_context.py` and
   `.github/ecosystems/codebase-context/generate_codebase_context.sh` must both
   exist.
2. The root agent and export skill should keep routing users to the manifest-
   owned generator entry points instead of source-only shared helpers.
3. `CODEBASE_CONTEXT.md` is runtime output, not part of the manifest-owned
   payload, and should not be treated as install/remove ownership.
4. The ecosystem should remain auditable through the shared `ecosystem-audit`
   platform rather than repository-governance-specific validation guidance.

## Artifact Quality Rubric

- `completeness`
   - Strong: the exported context contains enough source and supporting material
      for the user's stated task without omitting critical files.
   - Needs Work: the export leaves out key repository context or fails to carry
      through the declared pickup rules.
- `clarity`
   - Strong: the generator guidance and resulting context make scope, defaults,
      and overrides easy to understand.
   - Needs Work: the output or guidance is difficult to interpret or forces the
      user to reverse-engineer what was included.
- `constraint-adherence`
   - Strong: include, exclude, and source-only instructions clearly override the
      default broad export behavior.
   - Needs Work: the ecosystem drifts from explicit user constraints or leaves
      override rules ambiguous.
- `operator-ergonomics`
   - Strong: users can find the right entrypoint, understand the output path,
      and rerun the export without friction.
   - Needs Work: the ecosystem technically works but places too much manual
      reasoning burden on the operator.
- `maintainability`
   - Strong: guidance stays anchored to manifest-owned generator entrypoints and
      avoids routing through source-only helpers.
   - Needs Work: export behavior depends on scattered or duplicated guidance.

## Behavior Quality Rubric

- `correctness`
   - Evaluate whether the root agent and export guidance route work to the
      manifest-owned generator entrypoints consistently.
- `completeness`
   - Evaluate whether the ecosystem's design explains both default broad export
      behavior and narrower user-directed pickup rules.
- `recovery-behavior`
   - Evaluate whether the ecosystem handles incomplete user scope by defaulting
      safely to a useful export rather than producing an underspecified artifact.
- `definition-inferred` evidence note
   - When runtime logs are absent, treat behavior-quality findings as design
      review of the agent definition, manifest, and export guidance.

## Evidence Sources

- Generator entrypoints under `.github/ecosystems/codebase-context/`
- The codebase-context agent and export skill definitions
- Generated `CODEBASE_CONTEXT.md` output when a runtime example is available

## Upstream Improvement Feedback

1. Prefer upstream feedback when exported context is valid but too noisy, too
    sparse, or unclear for downstream use.
2. When the operator experience depends on implicit knowledge of pickup rules,
    suggest upstream guidance changes rather than treating the issue as a purely
    local artifact defect.
