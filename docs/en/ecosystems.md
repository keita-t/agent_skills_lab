# Current Ecosystems

This document summarizes the ecosystems currently managed in this repository.
The implementation-facing inventory is anchored by
[.ai_ecosystems/README.md](../../.ai_ecosystems/README.md), and each
ecosystem definition is anchored by its manifest under `.ai_ecosystems/`.
The shared files directly under `.ai_ecosystems/` are support
infrastructure, not separate ecosystems by themselves.

## Related Documents

- [docs/README.md](../README.md): documentation map and reading order.
- [docs/ja/ecosystems.ja.md](../ja/ecosystems.ja.md): Japanese counterpart.

## Snapshot

- Active ecosystem count: 3
- Current ecosystem slugs: `ecosystem-audit`, `codebase-context`, `repository-docs`
- Current root responsibilities: shared ecosystem auditing and work-quality
  feedback, repository codebase export for large-context models, plus
  repository documentation governance, docs refactoring, bootstrap, and TODO
  progress tracking.
- Manifest direction: ownership and dependency contract first.

## Installed Runtime Contract

- Installed runtime is optional across ecosystems.
- Runtime-free ecosystems omit runtime metadata and ship no installed runtime.
- Runtime-enabled ecosystems may declare `runtime-mode`,
  `runtime-entrypoint`, and `runtime-requires` in manifest frontmatter.
- Ecosystems may also declare `shared-ownership-files` to mark specific
  manifest-owned paths as explicitly shareable across installed ecosystems.
- Runtime assets remain part of `ecosystem-files`; runtime metadata describes
  how the installed payload executes on target hosts.
- Delivery copies a duplicate manifest-owned path only when every owning
  ecosystem declares that exact path in `shared-ownership-files`; the remove
  flow keeps it until the last installed owner is removed.
- The only supported installed runtime mode today is `container`, which uses a
  manifest-owned launcher and disposable Docker execution.
- Runtime-enabled launchers may also reuse the shared
  `.ai_ecosystems/runtime_container_lib.sh` helper for bind-mount probing
  and `docker cp` fallback transport when the host Docker daemon cannot see the
  current workspace path directly.

## AI Tool Host Delivery

- Manifest `agents` and `skills` are logical member names backed by canonical
  source files under `.ai_ecosystems/<slug>/agents/` and
  `.ai_ecosystems/<slug>/skills/`.
- Delivery host adapters copy those canonical files into selected AI tool
  native paths: GitHub Copilot uses `.github/agents/` and `.github/skills/`,
  Claude Code uses `.claude/agents/` and `.claude/skills/`, Codex uses
  `.agents/skills/`, and Cursor uses `.cursor/skills/`.
- If no host is specified, delivery detects target repository markers and
  installs into every detected host. If no marker exists, it falls back to
  GitHub Copilot.
- Delivery does not modify target repository root/global instructions such as
  `AGENTS.md`, `CLAUDE.md`, or `.github/copilot-instructions.md`.

## Current Inventory

| Slug | Status | Purpose | Root agent | Skills | Notes |
|---|---|---|---|---|---|
| `ecosystem-audit` | `active` | Provide a shared audit platform for ecosystem manifests, installed ecosystem payloads, and rubric-first work-quality feedback. | `ecosystem-audit.agent.md` | None | Installable into other repositories and extended through manifest-declared `audit-files`. |
| `codebase-context` | `active` | Export a repository into one markdown context file for large-context models. | `codebase-context.agent.md` | `codebase-context-export` | Installable into other repositories. `simple` mode exports the full filtered source code plus useful supporting files by default, while `smart` mode uses token-budgeted task-aware selection. Explicit user pickup rules can narrow or override scope. Uses the shared installed runtime contract in `container` mode. |
| `repository-docs` | `active` | Repository documentation governance, docs refactoring, bootstrap, and TODO progress tracking. | `governance-repository-context-manager.agent.md` | `docs-bootstrap`, `docs-sync`, `docs-refactor`, `todo-maintenance` | Self-hosted in this repository and installable into other repositories. Depends on `ecosystem-audit`, ships a docs-specific audit pack, and declares no installed runtime. |

## Ecosystem Details

### `ecosystem-audit`

Canonical manifest:
[.ai_ecosystems/ecosystem-audit/ECOSYSTEM.md](../../.ai_ecosystems/ecosystem-audit/ECOSYSTEM.md)

| Area | Current implementation |
|---|---|
| Root agent | [.ai_ecosystems/ecosystem-audit/agents/ecosystem-audit.agent.md](../../.ai_ecosystems/ecosystem-audit/agents/ecosystem-audit.agent.md) |
| Skills | None |
| Ownership contract | Agent, listed ecosystem-owned files, listed audit files, and the manifest itself |
| Ecosystem-owned files | Starter assets under `.ai_ecosystems/ecosystem-audit/assets/` |
| Audit files | Shared core rules, report contract, and work-quality rubric under `.ai_ecosystems/ecosystem-audit/audit/` |
| Extension model | Other ecosystems declare additional `audit-files` in their own manifests so ecosystem-specific checks stay owned by the ecosystem they describe |
| Starter assets | Ships an audit-pack template and a manual smoke scenario for newly added ecosystems |
| Output model | Rubric-first reports that summarize quality by dimension before evidence-backed findings |

#### Example Audit Report

The following condensed example shows the intended default shape for a
rubric-first audit report.

```md
1. Scope summary
  - Installed target repository audit for `repository-docs`
  - Shared core rules, shared work-quality rubric, and the repository-docs audit
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
    - Rule source: `.ai_ecosystems/repository-docs/audit/repository-docs-audit.md`
    - Evidence basis: definition-inferred
    - Confidence: medium
    - Impact: Maintainers may know the happy path but still hesitate when the installed docs set is incomplete.
    - Path: `docs/README.md`
    - Message: Recovery guidance explains where to start, but not how to recover when the target repository is missing one canonical doc.
    - Improvement feedback: upstream-ecosystem-feedback - add one short missing-doc recovery branch to installed guidance.

4. Files and manifests inspected
  - `.ai_ecosystems/repository-docs/ECOSYSTEM.md`
  - `docs/README.md`
  - `.ai_ecosystems/repository-docs/agents/governance-repository-context-manager.agent.md`

5. Suggested follow-up
  - Add one explicit recovery step for incomplete installed docs sets.
  - Re-audit after the upstream guidance change lands.
```

### `codebase-context`

Canonical manifest:
[.ai_ecosystems/codebase-context/ECOSYSTEM.md](../../.ai_ecosystems/codebase-context/ECOSYSTEM.md)

| Area | Current implementation |
|---|---|
| Root agent | [.ai_ecosystems/codebase-context/agents/codebase-context.agent.md](../../.ai_ecosystems/codebase-context/agents/codebase-context.agent.md) |
| Skills | [.ai_ecosystems/codebase-context/skills/codebase-context-export/SKILL.md](../../.ai_ecosystems/codebase-context/skills/codebase-context-export/SKILL.md) |
| Ownership contract | Agent, skill, listed ecosystem-owned files, listed audit files, and the manifest itself |
| Dependencies | `ecosystem-audit` |
| Ecosystem-owned files | The shared `.ai_ecosystems/runtime_container_lib.sh` transport helper, plus the runtime Dockerfile, shell launcher, and generator under `.ai_ecosystems/codebase-context/` |
| Audit files | `.ai_ecosystems/codebase-context/audit/codebase-context-audit.md` |
| Installed runtime | Shared installed runtime contract in `container` mode, with `generate_codebase_context.sh` as the runtime launcher, `.ai_ecosystems/runtime_container_lib.sh` as the shared transport helper, and Docker as the only declared host prerequisite |
| Quality focus | Export usefulness, signal-to-noise balance, pickup-rule obedience, and operator experience |
| Default export behavior | Generates `CODEBASE_CONTEXT.md` at the repository root in `simple` mode, exporting the full filtered source code plus useful supporting files in one markdown snapshot |
| Smart export behavior | `smart` mode uses `--budget low|medium|high` and optional `--task` text to produce a token-budgeted, task-aware snapshot with full or stubbed file representations |
| User override rule | Explicit user pickup rules such as include, exclude, or source-only constraints override the default broad export policy |
| Runtime output | The generated markdown snapshot is runtime output and is not part of the manifest-owned install payload |
| Installed-target smoke | [tests/sandbox/run_codebase_context_container_smoke.sh](../../tests/sandbox/run_codebase_context_container_smoke.sh) uses the shared [tests/sandbox/base/Dockerfile](../../tests/sandbox/base/Dockerfile) to prepare a temporary target repository, then invokes the installed runtime launcher directly so the runtime container is the only execution boundary for the export itself. |

### `repository-docs`

Canonical manifest:
[.ai_ecosystems/repository-docs/ECOSYSTEM.md](../../.ai_ecosystems/repository-docs/ECOSYSTEM.md)

| Area | Current implementation |
|---|---|
| Root agent | [.ai_ecosystems/repository-docs/agents/governance-repository-context-manager.agent.md](../../.ai_ecosystems/repository-docs/agents/governance-repository-context-manager.agent.md) |
| Specialized agents | [.ai_ecosystems/repository-docs/agents/governance-ecosystem-manifest.agent.md](../../.ai_ecosystems/repository-docs/agents/governance-ecosystem-manifest.agent.md), [.ai_ecosystems/repository-docs/agents/governance-ecosystem-delivery.agent.md](../../.ai_ecosystems/repository-docs/agents/governance-ecosystem-delivery.agent.md) |
| Skills | [.ai_ecosystems/repository-docs/skills/docs-bootstrap/SKILL.md](../../.ai_ecosystems/repository-docs/skills/docs-bootstrap/SKILL.md), [.ai_ecosystems/repository-docs/skills/docs-sync/SKILL.md](../../.ai_ecosystems/repository-docs/skills/docs-sync/SKILL.md), [.ai_ecosystems/repository-docs/skills/docs-refactor/SKILL.md](../../.ai_ecosystems/repository-docs/skills/docs-refactor/SKILL.md), [.ai_ecosystems/repository-docs/skills/todo-maintenance/SKILL.md](../../.ai_ecosystems/repository-docs/skills/todo-maintenance/SKILL.md) |
| Ownership contract | Agents, skills, listed ecosystem-owned files, listed audit files, and the manifest itself |
| Dependencies | `ecosystem-audit` |
| Ecosystem-owned files | Template assets under `.ai_ecosystems/repository-docs/` |
| Audit files | `.ai_ecosystems/repository-docs/audit/repository-docs-audit.md` |
| Installed runtime | None declared. This ecosystem ships no installed executable runtime. |
| Install portability rule | Repository-local links inside installable markdown must resolve within the manifest-owned payload so installed artifacts stay self-contained in target repositories. |
| Quality focus | Document clarity, codebase alignment, natural-language readability, diagram fit, bilingual alignment quality, and operator usability |
| Audit flow | The shared `ecosystem-audit` platform applies shared core rules, the shared work-quality rubric, and this ecosystem's audit pack on demand |
| Installed-target smoke | [tests/sandbox/run_repository_docs_container_smoke.sh](../../tests/sandbox/run_repository_docs_container_smoke.sh) installs the ecosystem into a temporary repository, applies the shipped bilingual template pack, and runs the smoke inside the repo-contained Docker sandbox built from the shared [tests/sandbox/base/Dockerfile](../../tests/sandbox/base/Dockerfile). |

## Validation

This repository does not currently install a GitHub Actions workflow. Run
`python -m pytest -q` locally when validation is needed. The sandbox smoke
scripts under `tests/sandbox/` remain available for manual installed-target
checks.

## Shared Ecosystem Infrastructure

These files support the ecosystem system as a whole and are not separate
ecosystem entries.

| Path | Role |
|---|---|
| [.ai_ecosystems/deliver_ecosystem.py](../../.ai_ecosystems/deliver_ecosystem.py) | Execute manifest-owned install or remove workflows against a target `owner/repo`, including declared dependencies, and prepare a PR-based delivery flow. |
| [.ai_ecosystems/runtime_container_lib.sh](../../.ai_ecosystems/runtime_container_lib.sh) | Provide shared shell transport for installed `container` runtimes, including bind-mount probing and `docker cp` fallback execution when the Docker host cannot resolve the current workspace path. |
