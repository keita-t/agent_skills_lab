# 現在の ecosystem 一覧

この文書は、このリポジトリで現在管理している ecosystem を要約した一覧です。
inventory の正本は
[.github/ECOSYSTEM_REGISTRY.md](../../.github/ECOSYSTEM_REGISTRY.md) にあり、
各 ecosystem の定義は `.github/ecosystems/` 配下の manifest に紐づきます。
`.github/ecosystems/` 直下の Python / shell ファイルは共有インフラであり、
それ自体は別 ecosystem ではありません。

## 関連文書

- [docs/README.md](../README.md): ドキュメント案内と読書順。
- [docs/en/ecosystems.md](../en/ecosystems.md): 英語版の対応文書。
- [docs/ja/mcp-tools.ja.md](./mcp-tools.ja.md): MCP tool registry 契約と現在の公開 tool。

## スナップショット

- Active ecosystem 数: 1
- 現在の ecosystem slug: `repository-governance`
- 主責務: repository documentation governance、bootstrap、TODO progress tracking。

## 現在の Inventory

| Slug | Status | Purpose | Root agent | Skills | MCP | Notes |
|---|---|---|---|---|---|---|
| `repository-governance` | `active` | repository documentation governance、bootstrap、TODO progress tracking。 | `governance-repository-context-manager.agent.md` | `repository-governance-bootstrap`、`repository-doc-governance`、`todo-progress-governance` | Enabled | この repository 自身で self-host しつつ、他 repository へ install できる。 |

## Ecosystem Details

### `repository-governance`

正本 manifest:
[.github/ecosystems/repository-governance/ECOSYSTEM.md](../../.github/ecosystems/repository-governance/ECOSYSTEM.md)

| 項目 | 現在の実装 |
|---|---|
| Root agent | [.github/agents/governance-repository-context-manager.agent.md](../../.github/agents/governance-repository-context-manager.agent.md) |
| Skills | [.github/skills/repository-governance-bootstrap/SKILL.md](../../.github/skills/repository-governance-bootstrap/SKILL.md), [.github/skills/repository-doc-governance/SKILL.md](../../.github/skills/repository-doc-governance/SKILL.md), [.github/skills/todo-progress-governance/SKILL.md](../../.github/skills/todo-progress-governance/SKILL.md) |
| Managed core files | `.github/ECOSYSTEM_REGISTRY.md`、`.github/ecosystems/README.md`、`.github/AGENT_SKILL_ROUTING.md`、`.github/agents/README.md`、`.github/skills/README.md`、`.github/copilot-instructions.md` |
| Ecosystem 固有 files | `.github/ecosystems/repository-governance/` 配下の template assets、MCP tool registry、validator 群 |
| Post-install validator | `.github/ecosystems/repository-governance/validate_agent_skill_docs.sh` |
| MCP tools | `repository_governance.validate_repository`、`repository_governance.validate_agent_skill_docs` |

## 共有 Ecosystem Infrastructure

次のファイルは ecosystem 全体を支える共有基盤であり、個別 ecosystem entry では
ありません。

| Path | 役割 |
|---|---|
| [.github/ecosystems/install_ecosystem.sh](../../.github/ecosystems/install_ecosystem.sh) | 選択した ecosystem を別 repository に import する。 |
| [.github/ecosystems/update_ecosystem_core_files.sh](../../.github/ecosystems/update_ecosystem_core_files.sh) | installed manifest から ecosystem 管理下の `.github` core files を再生成する。 |
| [.github/ecosystems/validate_ecosystem_registry.sh](../../.github/ecosystems/validate_ecosystem_registry.sh) | manifest、registry entry、routing link、ecosystem metadata を検証する。 |
| [.github/ecosystems/mcp_server.py](../../.github/ecosystems/mcp_server.py) | 共通 tool と ecosystem 固有 tool を FastMCP 経由で公開する。 |