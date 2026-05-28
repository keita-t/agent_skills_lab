# 現在の ecosystem 一覧

この文書は、このリポジトリで現在管理している ecosystem を要約した一覧です。
実装向け inventory は
[.github/ecosystems/README.md](../../.github/ecosystems/README.md) に集約し、
各 ecosystem の定義は `.github/ecosystems/` 配下の manifest に紐づきます。
`.github/ecosystems/` 直下の Python / shell ファイルは共有インフラであり、
それ自体は別 ecosystem ではありません。

## 関連文書

- [docs/README.md](../README.md): ドキュメント案内と読書順。
- [docs/en/ecosystems.md](../en/ecosystems.md): 英語版の対応文書。

## スナップショット

- Active ecosystem 数: 1
- 現在の ecosystem slug: `repository-governance`
- 主責務: repository documentation governance、bootstrap、TODO progress tracking。
- manifest の方向性: ownership と dependency の structural contract を優先する。

## 現在の Inventory

| Slug | Status | Purpose | Root agent | Skills | Notes |
|---|---|---|---|---|---|
| `repository-governance` | `active` | repository documentation governance、bootstrap、TODO progress tracking。 | `governance-repository-context-manager.agent.md` | `repository-governance-bootstrap`、`repository-doc-governance`、`todo-progress-governance` | この repository 自身で self-host しつつ、他 repository へ install できる。manifest-owned payload からは legacy MCP metadata を外した。 |

## Ecosystem Details

### `repository-governance`

正本 manifest:
[.github/ecosystems/repository-governance/ECOSYSTEM.md](../../.github/ecosystems/repository-governance/ECOSYSTEM.md)

| 項目 | 現在の実装 |
|---|---|
| Root agent | [.github/agents/governance-repository-context-manager.agent.md](../../.github/agents/governance-repository-context-manager.agent.md) |
| Specialized agents | [.github/agents/governance-ecosystem-manifest.agent.md](../../.github/agents/governance-ecosystem-manifest.agent.md), [.github/agents/governance-ecosystem-delivery.agent.md](../../.github/agents/governance-ecosystem-delivery.agent.md) |
| Skills | [.github/skills/repository-governance-bootstrap/SKILL.md](../../.github/skills/repository-governance-bootstrap/SKILL.md), [.github/skills/repository-doc-governance/SKILL.md](../../.github/skills/repository-doc-governance/SKILL.md), [.github/skills/todo-progress-governance/SKILL.md](../../.github/skills/todo-progress-governance/SKILL.md) |
| Ownership contract | agents、skills、listed ecosystem-owned files、および manifest 自体 |
| Ecosystem 固有 files | `.github/ecosystems/repository-governance/` 配下の template assets と validator 群 |
| Delivery helper | [.github/ecosystems/deliver_ecosystem.py](../../.github/ecosystems/deliver_ecosystem.py) が target repository 向けの PR ベース install/remove workflow を駆動する |

## 共有 Ecosystem Infrastructure

次のファイルは、ecosystem 全体を支える共有基盤であり、個別 ecosystem entry
ではありません。

| Path | 役割 |
|---|---|
| [.github/ecosystems/deliver_ecosystem.py](../../.github/ecosystems/deliver_ecosystem.py) | manifest-owned install/remove workflow を target `owner/repo` に適用し、PR ベース delivery を準備する。 |
| [.github/ecosystems/validate_ecosystem_registry.sh](../../.github/ecosystems/validate_ecosystem_registry.sh) | manifest、frontmatter 整合性、structural な ecosystem membership を検証する。 |