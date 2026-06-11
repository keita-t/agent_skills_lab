<<<<<<< HEAD
=======
# agent_skills_lab
>>>>>>> 4a78c77 (feat: Add repository governance documentation and skills)

## English

**agent_skills_lab** is a development lab for building and testing *ecosystems* — reusable bundles of AI agents and skills that can be installed into any GitHub repository.

### What is an ecosystem?

An ecosystem packages one or more AI agent definitions, the skills those agents can invoke, and any required helper files, all governed by a single manifest. You author an ecosystem once in this repository, then install it into any target repository with a single command. Because the manifest declares exactly which files the ecosystem owns, install and remove are predictable and reversible.

### Active ecosystems

Three ecosystems are currently developed and hosted here:

| Ecosystem | What it does |
|---|---|
| **`ecosystem-audit`** | Audits other ecosystems for structural correctness and work quality. Acts as a shared platform that the other two ecosystems depend on. |
| **`codebase-context`** | Exports repository context into one Markdown file, with a full simple mode and a token-budgeted smart mode for large-context AI prompts. |
| **`repository-governance`** | Manages a repository's documentation: bootstraps the doc structure, enforces update rules, and tracks TODO progress. |

### This repository is its own guinea pig

agent_skills_lab is both the place where ecosystems are developed and a live target that runs `repository-governance` on itself. The documentation governance you see here is actively maintained by the same ecosystem you can install into your own repositories.

### Installing an ecosystem into another repository

Use the
[Ecosystem Delivery Orchestrator](.ai_ecosystems/repository-governance/agents/governance-ecosystem-delivery.agent.md)
agent to drive the install or remove workflow interactively. It prepares a
PR-based delivery flow and resolves any declared dependencies automatically —
for example, installing `repository-governance` also brings in `ecosystem-audit`.
If you do not specify an AI tool host, delivery detects target repository
markers and installs into every detected host. If no marker exists, it falls
back to GitHub Copilot for compatibility. Delivery does not modify target root
instructions such as `AGENTS.md`, `CLAUDE.md`, or `.github/copilot-instructions.md`.

If you prefer to run the delivery script directly, use
[deliver_ecosystem.py](.ai_ecosystems/deliver_ecosystem.py):

```bash
python .ai_ecosystems/deliver_ecosystem.py install --target-repo owner/repo --ecosystem repository-governance
```

### Ecosystem installation and quality improvement loop

Installing an ecosystem into another repository is proposed as a pull request.
Review that PR actively and feed findings back into this source repository so
the ecosystem keeps improving through the loop. Even features that feel rough at
first should get steadily better as feedback accumulates.

### Development runtime

The repository ships a [dev container](.devcontainer/devcontainer.json) that
provides Python 3.11 and Docker out of the box — open the repository in VS Code
and choose **Reopen in Container** to get a ready-to-use environment.

For a local setup without the dev container, Python 3.11 or newer is required.
Create a virtual environment and install dependencies as usual.

### Operational Precautions

The agents that make up the ecosystem are powered by AI and therefore can make critical mistakes. While the installation and removal workflows are designed to only affect files declared in the manifest, there is a non-zero risk of unexpected file changes due to AI errors. If you install the ecosystem in a critical repository, do so at your own risk and carefully review any changes.

### Where to go next

- [docs/en/ecosystems.md](docs/en/ecosystems.md) — Full ecosystem inventory with implementation details
- [docs/en/project-charter.md](docs/en/project-charter.md) — Repository scope and maintainer decisions
- [docs/en/ubiquitous-language.md](docs/en/ubiquitous-language.md) — Shared vocabulary used throughout this project
- [docs/README.md](docs/README.md) — Bilingual documentation map
- [docs/DOCUMENTATION_UPDATE_RULES.md](docs/DOCUMENTATION_UPDATE_RULES.md) — Documentation update rules
- [docs/AI_AGENT_INSTRUCTIONS.md](docs/AI_AGENT_INSTRUCTIONS.md) — Shared AI agent operating guidance
- [.ai_ecosystems/README.md](.ai_ecosystems/README.md) — Implementation-facing ecosystem index

---

## 日本語

**agent_skills_lab** は *ecosystem* — AI エージェントとスキルを束ねた再利用可能なパッケージ — を開発・テストするためのラボです。作った ecosystem は任意の GitHub リポジトリにインストールできます。

### ecosystem とは？

ecosystem は、AI エージェント定義・エージェントが呼び出せるスキル・必要なヘルパーファイルをひとつのマニフェストで管理する自己完結したパッケージです。このリポジトリで一度作れば、コマンド一発で任意のリポジトリにインストールできます。マニフェストが「この ecosystem が所有するファイル」を宣言するため、インストールも削除も予測可能かつ巻き戻し可能です。

### 現在稼動中の ecosystem

現在、3 つの ecosystem がここで開発・運用されています。

| Ecosystem | 何をするか |
|---|---|
| **`ecosystem-audit`** | 他の ecosystem の構造的な正確性と成果物の品質を監査します。他の 2 つの ecosystem が依存する共有プラットフォームです。 |
| **`codebase-context`** | リポジトリの context をひとつの Markdown ファイルにエクスポートします。full simple mode と token-budgeted smart mode を大規模文脈 AI プロンプト向けに使い分けられます。 |
| **`repository-governance`** | リポジトリのドキュメント管理を担います。ドキュメント構造のブートストラップ、更新ルールの適用、TODO 進捗の追跡を行います。 |

### このリポジトリ自身も実験台

agent_skills_lab は ecosystem を開発する場所であると同時に、`repository-governance` を自分自身に適用している live target でもあります。ここで見えているドキュメント管理の仕組みは、あなたのリポジトリにもインストールできる同じ ecosystem によってアクティブに維持されています。

### 別のリポジトリへのインストール

[Ecosystem Delivery Orchestrator](.ai_ecosystems/repository-governance/agents/governance-ecosystem-delivery.agent.md)
エージェントを使うと、インストール・削除のワークフローを対話形式で進められます。PR ベースのデリバリーフローを準備し、宣言済みの依存関係を自動で解決します（例：`repository-governance` をインストールすると `ecosystem-audit` も一緒に入ります）。
AI ツール host を指定しない場合、delivery は target repository の marker
を検出し、検出されたすべての host に配布します。marker がない場合は
互換性のため GitHub Copilot に fallback します。target repository の
`AGENTS.md`、`CLAUDE.md`、`.github/copilot-instructions.md` のような root
instructions は変更しません。

スクリプトを直接実行する場合は
[deliver_ecosystem.py](.ai_ecosystems/deliver_ecosystem.py) を使います：

```bash
python .ai_ecosystems/deliver_ecosystem.py install --target-repo owner/repo --ecosystem repository-governance
```

### ecosystem のインストールと品質改善ループ

他のリポジトリへの ecosystem のインストールは、PRとして提案されます。PRの内容を積極的にレビューし、指摘を本リポジトリへとフィードバックすることで、ecosystem はその改善ループによって確実に品質向上していきます。はじめは微妙な機能でも、フィードバックを重ねるうちにどんどん良くなっていくはずです。

### 開発環境

リポジトリには Python 3.11 と Docker がすぐ使える [dev container](.devcontainer/devcontainer.json) が同梱されています。VS Code でリポジトリを開き、**Reopen in Container** を選ぶだけで環境が整います。

dev container を使わない場合は Python 3.11 以上が必要です。通常通り仮想環境を作成し、依存関係をインストールしてください。

### 運用上の注意

ecosystem を構成するエージェントは、 AI によって動作しているため、致命的なミスをする可能性があります。インストールや削除のワークフローは、マニフェストで宣言されたファイルにのみ作用するように設計されていますが、AI の判断ミスによって予期せぬファイルが変更されるリスクはゼロではありません。重要なリポジトリに ecosystem をインストールする場合は、自己責任で、変更内容を注意深くレビューしてください。

### 次に読む

- [docs/ja/ecosystems.ja.md](docs/ja/ecosystems.ja.md) — 実装詳細を含む ecosystem inventory
- [docs/ja/project-charter.ja.md](docs/ja/project-charter.ja.md) — リポジトリの目的と maintainer の判断
- [docs/ja/ubiquitous-language.ja.md](docs/ja/ubiquitous-language.ja.md) — このプロジェクト全体で使う共有語彙
- [docs/README.md](docs/README.md) — 英日対応のドキュメント案内
- [docs/DOCUMENTATION_UPDATE_RULES.md](docs/DOCUMENTATION_UPDATE_RULES.md) — docs 更新ルール
- [docs/AI_AGENT_INSTRUCTIONS.md](docs/AI_AGENT_INSTRUCTIONS.md) — AI agent 共通の運用ガイダンス
- [.ai_ecosystems/README.md](.ai_ecosystems/README.md) — 実装向け ecosystem index
