# agent_skills_lab

## English

This repository is a development and experimentation lab for custom agents,
skills, and installable ecosystems.

It is structured so one repository can both define reusable ecosystems and act
as a self-hosted target of the repository-governance ecosystem.

## Development Runtime

Use Python 3.10 or newer for local virtual environments, source-only helper
scripts, and current test workflows in this repository.

## Sandbox Smoke

Use
[tests/sandbox/run_codebase_context_container_smoke.sh](tests/sandbox/run_codebase_context_container_smoke.sh)
to run the installed-target `codebase-context` smoke tests inside a repo-
contained Docker sandbox, and use
[tests/sandbox/run_repository_governance_container_smoke.sh](tests/sandbox/run_repository_governance_container_smoke.sh)
to run the installed-target `repository-governance` smoke tests against the
shipped bilingual template pack. The container definitions live at
[tests/sandbox/base/Dockerfile](tests/sandbox/base/Dockerfile), which both
smoke runners share as a common sandbox image definition.

GitHub Actions CI is defined at
[.github/workflows/ci.yml](.github/workflows/ci.yml) and runs the full
`python -m pytest -q` suite plus both sandbox smoke runners.

## Practical Workflow

Today this repository operates three active ecosystems:
[`ecosystem-audit`](.github/ecosystems/ecosystem-audit/ECOSYSTEM.md),
[`codebase-context`](.github/ecosystems/codebase-context/ECOSYSTEM.md), and
[`repository-governance`](.github/ecosystems/repository-governance/ECOSYSTEM.md).
In practice, treat each manifest as the implementation-facing contract. The
manifest defines the root agent, any specialized agents, shipped skills,
dependencies, audit files, and the ecosystem-owned files that install/remove
workflows are allowed to touch.

The shared `ecosystem-audit` platform also ships starter assets for future
ecosystems, including an audit-pack template and a manual smoke scenario for
validating a newly added audit extension.
Its recommended audit output is rubric-first: summarize structural conformance
and work quality by dimension, then follow with evidence-backed findings and
upstream ecosystem feedback.

Most repository-facing work starts with
[Repository Context Manager](.github/agents/governance-repository-context-manager.agent.md),
which routes docs, bootstrap, and TODO/progress tasks to the canonical skills.
When the contract itself changes, use
[Ecosystem Manifest Governor](.github/agents/governance-ecosystem-manifest.agent.md)
to update membership, ownership scope, or frontmatter alignment, then ask the
Ecosystem Audit Agent to audit the current ecosystems for structural
conformance and ecosystem work quality.
When you need to apply the manifest-owned payload to another repository, use
[Ecosystem Delivery Orchestrator](.github/agents/governance-ecosystem-delivery.agent.md)
or run
[deliver_ecosystem.py](.github/ecosystems/deliver_ecosystem.py)
with `install` or `remove` so the same manifest drives the PR-based workflow,
including any declared ecosystem dependencies such as the shared audit
platform.

Start with the canonical docs under `docs/` for repository-specific context,
documentation governance, and current follow-up work.

- [docs/README.md](docs/README.md) - Bilingual documentation map
- [docs/en/ecosystems.md](docs/en/ecosystems.md) - Current ecosystem inventory
- [docs/en/project-charter.md](docs/en/project-charter.md) - English charter
- [docs/en/ubiquitous-language.md](docs/en/ubiquitous-language.md) - English ubiquitous language
- [docs/ja/project-charter.ja.md](docs/ja/project-charter.ja.md) - Japanese charter
- [docs/ja/ubiquitous-language.ja.md](docs/ja/ubiquitous-language.ja.md) - Japanese ubiquitous language
- [docs/DOCUMENTATION_UPDATE_RULES.md](docs/DOCUMENTATION_UPDATE_RULES.md) - Documentation governance
- [docs/TODO.md](docs/TODO.md) - Current backlog and design-review notes
- [.github/ecosystems/README.md](.github/ecosystems/README.md) - Implementation-facing ecosystem index
- [.github/ecosystems/repository-governance/ECOSYSTEM.md](.github/ecosystems/repository-governance/ECOSYSTEM.md) - Current repository-governance manifest

## 日本語

このリポジトリは、custom agents、skills、installable ecosystems の開発と実験のためのラボです。

再利用可能な ecosystem の source repository であると同時に、repository-governance ecosystem を self-host する target repository としても成立するよう構成しています。

## 開発用ランタイム

このリポジトリの local virtual environment、validator、ecosystem helper script は
Python 3.10 以上を前提とします。

## Sandbox Smoke

[tests/sandbox/run_codebase_context_container_smoke.sh](tests/sandbox/run_codebase_context_container_smoke.sh)
を使うと、installed-target 向けの `codebase-context` smoke test を、この repo に
同梱した Docker sandbox の中で実行できます。さらに
[tests/sandbox/run_repository_governance_container_smoke.sh](tests/sandbox/run_repository_governance_container_smoke.sh)
を使うと、shipped bilingual template pack を使った `repository-governance`
の installed-target smoke test も同じく repo 内で完結します。container 定義は
[tests/sandbox/base/Dockerfile](tests/sandbox/base/Dockerfile)
に共通化してあり、2 本の runner が同じ sandbox image 定義を共有します。

GitHub Actions CI は
[.github/workflows/ci.yml](.github/workflows/ci.yml)
で定義しており、`python -m pytest -q` の full suite と 2 本の sandbox smoke
runner をまとめて実行します。

## 実務フローの見取り図

現時点でこの repository が運用している active ecosystem は
[`ecosystem-audit`](.github/ecosystems/ecosystem-audit/ECOSYSTEM.md)、
[`codebase-context`](.github/ecosystems/codebase-context/ECOSYSTEM.md)、
[`repository-governance`](.github/ecosystems/repository-governance/ECOSYSTEM.md)
の 3 つです。実務上は、それぞれの manifest を implementation-facing な
contract として扱います。root agent、専用 agent、同梱する skills、
dependency、audit files、さらに install/remove workflow が触れてよい
ecosystem-owned files は、ここを正本として決まります。

repository 側の作業の起点は、通常
[Repository Context Manager](.github/agents/governance-repository-context-manager.agent.md)
です。これは docs、bootstrap、TODO/progress の変更を正規の skill へ振り分けます。
contract 自体を変えるときは
[Ecosystem Manifest Governor](.github/agents/governance-ecosystem-manifest.agent.md)
を使って membership、ownership scope、frontmatter alignment を更新し、その後に
Ecosystem Audit Agent へ現在の ecosystem 監査を依頼します。
manifest-owned payload を他 repository に適用するときは
[Ecosystem Delivery Orchestrator](.github/agents/governance-ecosystem-delivery.agent.md)
または
[deliver_ecosystem.py](.github/ecosystems/deliver_ecosystem.py)
の `install` / `remove` を使い、同じ manifest を PR ベースの delivery workflow の
入力にします。必要な dependency が宣言されていれば、shared audit platform の
ような ecosystem も一緒に解決されます。

リポジトリ固有の前提、文書更新ガバナンス、現在の追跡事項は `docs/` の正本文書から読み始めます。

- [docs/README.md](docs/README.md) - 英日対応のドキュメント案内
- [docs/ja/ecosystems.ja.md](docs/ja/ecosystems.ja.md) - 現在の ecosystem inventory
- [docs/en/project-charter.md](docs/en/project-charter.md) - 英語版憲章
- [docs/en/ubiquitous-language.md](docs/en/ubiquitous-language.md) - 英語版ユビキタス言語
- [docs/ja/project-charter.ja.md](docs/ja/project-charter.ja.md) - 日本語版憲章
- [docs/ja/ubiquitous-language.ja.md](docs/ja/ubiquitous-language.ja.md) - 日本語版ユビキタス言語
- [docs/DOCUMENTATION_UPDATE_RULES.md](docs/DOCUMENTATION_UPDATE_RULES.md) - 文書更新ルール
- [docs/TODO.md](docs/TODO.md) - 現在の TODO とレビュー用メモ
- [.github/ecosystems/README.md](.github/ecosystems/README.md) - implementation-facing ecosystem index
- [.github/ecosystems/repository-governance/ECOSYSTEM.md](.github/ecosystems/repository-governance/ECOSYSTEM.md) - 現在の repository-governance manifest