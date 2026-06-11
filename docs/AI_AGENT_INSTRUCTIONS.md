# AI Agent Instructions

## English

Use this file as shared operational guidance for AI coding and documentation
agents working in this repository. Tool-specific entry points such as
`AGENTS.md`, `CLAUDE.md`, and `.github/copilot-instructions.md` should route
here instead of carrying separate ecosystem rules.

- Read `docs/README.md`, `docs/DOCUMENTATION_UPDATE_RULES.md`, and the relevant
  ecosystem manifest before changing repository docs or ecosystem-managed
  payload.
- Ecosystem source of truth lives under `.ai_ecosystems/`; the old
  GitHub-hosted ecosystem directory has no compatibility wrapper.
- For ecosystem delivery, use `python .ai_ecosystems/deliver_ecosystem.py
  install|remove --target-repo owner/repo --ecosystem <slug>`.
- Delivery selects AI tool hosts with `--agent-host`; if omitted, it detects
  target markers and falls back to `github-copilot` when none are present.
- Delivery must not modify target repository root/global instruction files such
  as `AGENTS.md`, `CLAUDE.md`, or `.github/copilot-instructions.md`.
- Ask the `Ecosystem Audit Agent` to audit the current ecosystems after
  changing ecosystem manifests, dependencies, audit files, runtime payload, or
  ecosystem-aware delivery code.
- Keep repository entry points such as `README.md`, `CLAUDE.md`, and
  `docs/README.md` aligned in the same change when document structure changes.
- Do not structurally reorganize `docs/TODO.md` or the repository's canonical
  progress file without explicit in-session user instruction.

## 日本語

このファイルは、このリポジトリで作業する AI coding / documentation agent
向けの共通運用ガイダンスです。`AGENTS.md`、`CLAUDE.md`、
`.github/copilot-instructions.md` のような tool-specific entry point は、
個別に ecosystem rule を抱えず、この正本へ案内します。

- repository docs や ecosystem-managed payload を変更する前に、
  `docs/README.md`、`docs/DOCUMENTATION_UPDATE_RULES.md`、関連する
  ecosystem manifest を読む。
- ecosystem の正本は `.ai_ecosystems/` にあり、旧 GitHub-hosted ecosystem
  directory の互換 wrapper は存在しない。
- ecosystem delivery では `python .ai_ecosystems/deliver_ecosystem.py
  install|remove --target-repo owner/repo --ecosystem <slug>` を使う。
- delivery の AI tool host は `--agent-host` で選べる。省略時は target
  marker を検出し、何もなければ `github-copilot` に fallback する。
- delivery は target repository の `AGENTS.md`、`CLAUDE.md`、
  `.github/copilot-instructions.md` のような root/global instruction file を
  変更してはならない。
- ecosystem manifest、dependency、audit file、runtime payload、delivery
  code を変更した後は、`Ecosystem Audit Agent` に current ecosystems の監査を
  依頼する。
- 文書構成を変える場合は、`README.md`、`CLAUDE.md`、`docs/README.md` などの
  entry point を同じ変更で揃える。
- 明示的な in-session user instruction なしに、`docs/TODO.md` や repository
  の canonical progress file を構造変更しない。
