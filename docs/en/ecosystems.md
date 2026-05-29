# Current Ecosystems

This document summarizes the ecosystems currently managed in this repository.
The implementation-facing inventory is anchored by
[.github/ecosystems/README.md](../../.github/ecosystems/README.md), and each
ecosystem definition is anchored by its manifest under `.github/ecosystems/`.
The shared files directly under `.github/ecosystems/` are support
infrastructure, not separate ecosystems by themselves.

## Related Documents

- [docs/README.md](../README.md): documentation map and reading order.
- [docs/ja/ecosystems.ja.md](../ja/ecosystems.ja.md): Japanese counterpart.

## Snapshot

- Active ecosystem count: 3
- Current ecosystem slugs: `ecosystem-audit`, `codebase-context`, `repository-governance`
- Current root responsibilities: shared ecosystem auditing and work-quality
  feedback, repository codebase export for large-context models, plus
  repository documentation governance, bootstrap, and TODO progress tracking.
- Manifest direction: ownership and dependency contract first.

## Current Inventory

| Slug | Status | Purpose | Root agent | Skills | Notes |
|---|---|---|---|---|---|
| `ecosystem-audit` | `active` | Provide a shared audit platform for ecosystem manifests, installed ecosystem payloads, and rubric-first work-quality feedback. | `ecosystem-audit.agent.md` | None | Installable into other repositories and extended through manifest-declared `audit-files`. |
| `codebase-context` | `active` | Export a repository into one markdown context file for large-context models. | `codebase-context.agent.md` | `codebase-context-export` | Installable into other repositories. The default export includes the full filtered source code plus useful supporting files, while explicit user pickup rules can narrow or override that scope. |
| `repository-governance` | `active` | Repository documentation governance, bootstrap, and TODO progress tracking. | `governance-repository-context-manager.agent.md` | `repository-governance-bootstrap`, `repository-doc-governance`, `todo-progress-governance` | Self-hosted in this repository and installable into other repositories. Depends on `ecosystem-audit` and ships a governance-specific audit pack. |

## Ecosystem Details

### `ecosystem-audit`

Canonical manifest:
[.github/ecosystems/ecosystem-audit/ECOSYSTEM.md](../../.github/ecosystems/ecosystem-audit/ECOSYSTEM.md)

| Area | Current implementation |
|---|---|
| Root agent | [.github/agents/ecosystem-audit.agent.md](../../.github/agents/ecosystem-audit.agent.md) |
| Skills | None |
| Ownership contract | Agent, listed ecosystem-owned files, listed audit files, and the manifest itself |
| Ecosystem-owned files | Starter assets under `.github/ecosystems/ecosystem-audit/assets/` |
| Audit files | Shared core rules, report contract, and work-quality rubric under `.github/ecosystems/ecosystem-audit/audit/` |
| Extension model | Other ecosystems declare additional `audit-files` in their own manifests so ecosystem-specific checks stay owned by the ecosystem they describe |
| Starter assets | Ships an audit-pack template and a manual smoke scenario for newly added ecosystems |
| Output model | Rubric-first reports that summarize quality by dimension before evidence-backed findings |

#### Example Audit Report

The following condensed example shows the intended default shape for a
rubric-first audit report.

```md
1. Scope summary
  - Installed target repository audit for `repository-governance`
  - Shared core rules, shared work-quality rubric, and the governance audit
    pack were applied

2. Rubric summary
  | Dimension | Rating | Evidence basis | Confidence | Short rationale |
  |---|---|---|---|---|
  | clarity | Acceptable | artifact-observed | high | Installed docs route readers to canonical entrypoints, but the bootstrap path still requires some cross-file scanning. |
  | constraint-adherence | Strong | artifact-observed | high | Installed guidance stays inside the manifest-owned payload and avoids source-only helpers. |
  | recovery-behavior | Needs Work | definition-inferred | medium | The docs describe steady-state flow well, but missing-context recovery is still thin without runtime examples. |

3. Findings
  - warning
    - Dimension: recovery-behavior
    - Rule source: `.github/ecosystems/repository-governance/audit/repository-governance-audit.md`
    - Evidence basis: definition-inferred
    - Confidence: medium
    - Impact: Maintainers may know the happy path but still hesitate when the installed docs set is incomplete.
    - Path: `docs/README.md`
    - Message: Recovery guidance explains where to start, but not how to recover when the target repository is missing one canonical doc.
    - Improvement feedback: upstream-ecosystem-feedback - add one short missing-doc recovery branch to installed guidance.

4. Files and manifests inspected
  - `.github/ecosystems/repository-governance/ECOSYSTEM.md`
  - `docs/README.md`
  - `.github/agents/governance-repository-context-manager.agent.md`

5. Suggested follow-up
  - Add one explicit recovery step for incomplete installed docs sets.
  - Re-audit after the upstream guidance change lands.
```

### `codebase-context`

Canonical manifest:
[.github/ecosystems/codebase-context/ECOSYSTEM.md](../../.github/ecosystems/codebase-context/ECOSYSTEM.md)

| Area | Current implementation |
|---|---|
| Root agent | [.github/agents/codebase-context.agent.md](../../.github/agents/codebase-context.agent.md) |
| Skills | [.github/skills/codebase-context-export/SKILL.md](../../.github/skills/codebase-context-export/SKILL.md) |
| Ownership contract | Agent, skill, listed ecosystem-owned files, listed audit files, and the manifest itself |
| Dependencies | `ecosystem-audit` |
| Ecosystem-owned files | The generator and shell wrapper under `.github/ecosystems/codebase-context/` |
| Audit files | `.github/ecosystems/codebase-context/audit/codebase-context-audit.md` |
| Quality focus | Export usefulness, signal-to-noise balance, pickup-rule obedience, and operator experience |
| Default export behavior | Generates `CODEBASE_CONTEXT.md` at the repository root, exporting the full filtered source code plus useful supporting files in one markdown snapshot |
| User override rule | Explicit user pickup rules such as include, exclude, or source-only constraints override the default broad export policy |
| Runtime output | The generated markdown snapshot is runtime output and is not part of the manifest-owned install payload |
| Installed-target smoke | [tests/sandbox/run_codebase_context_container_smoke.sh](../../tests/sandbox/run_codebase_context_container_smoke.sh) runs the installed-target smoke tests inside the repo-contained Docker sandbox built from the shared [tests/sandbox/base/Dockerfile](../../tests/sandbox/base/Dockerfile). |

### `repository-governance`

Canonical manifest:
[.github/ecosystems/repository-governance/ECOSYSTEM.md](../../.github/ecosystems/repository-governance/ECOSYSTEM.md)

| Area | Current implementation |
|---|---|
| Root agent | [.github/agents/governance-repository-context-manager.agent.md](../../.github/agents/governance-repository-context-manager.agent.md) |
| Specialized agents | [.github/agents/governance-ecosystem-manifest.agent.md](../../.github/agents/governance-ecosystem-manifest.agent.md), [.github/agents/governance-ecosystem-delivery.agent.md](../../.github/agents/governance-ecosystem-delivery.agent.md) |
| Skills | [.github/skills/repository-governance-bootstrap/SKILL.md](../../.github/skills/repository-governance-bootstrap/SKILL.md), [.github/skills/repository-doc-governance/SKILL.md](../../.github/skills/repository-doc-governance/SKILL.md), [.github/skills/todo-progress-governance/SKILL.md](../../.github/skills/todo-progress-governance/SKILL.md) |
| Ownership contract | Agents, skills, listed ecosystem-owned files, listed audit files, and the manifest itself |
| Dependencies | `ecosystem-audit` |
| Ecosystem-owned files | Template assets under `.github/ecosystems/repository-governance/` |
| Audit files | `.github/ecosystems/repository-governance/audit/repository-governance-audit.md` |
| Install portability rule | Repository-local links inside installable markdown must resolve within the manifest-owned payload so installed artifacts stay self-contained in target repositories. |
| Quality focus | Document clarity, navigability, bilingual alignment quality, and operator usability |
| Audit flow | The shared `ecosystem-audit` platform applies shared core rules, the shared work-quality rubric, and this ecosystem's audit pack on demand |
| Installed-target smoke | [tests/sandbox/run_repository_governance_container_smoke.sh](../../tests/sandbox/run_repository_governance_container_smoke.sh) installs the ecosystem into a temporary repository, applies the shipped bilingual template pack, and runs the smoke inside the repo-contained Docker sandbox built from the shared [tests/sandbox/base/Dockerfile](../../tests/sandbox/base/Dockerfile). |

## CI

[.github/workflows/ci.yml](../../.github/workflows/ci.yml) is the canonical
GitHub Actions entrypoint for repository validation. It runs the full
`python -m pytest -q` suite on the host runner and then executes both sandbox
container smoke runners.

## Shared Ecosystem Infrastructure

These files support the ecosystem system as a whole and are not separate
ecosystem entries.

| Path | Role |
|---|---|
| [.github/ecosystems/deliver_ecosystem.py](../../.github/ecosystems/deliver_ecosystem.py) | Execute manifest-owned install or remove workflows against a target `owner/repo`, including declared dependencies, and prepare a PR-based delivery flow. |