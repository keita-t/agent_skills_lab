# MCP Tools 仕様

この文書は、このリポジトリで実装されている MCP tool 契約と、現在公開している
tool registry を要約したものです。
正本は引き続き `.github/ecosystems/` 配下の JSON registry、manifest の MCP 関連
frontmatter、そして同ディレクトリの loader / server 実装です。

## 関連文書

- [docs/README.md](../README.md): ドキュメント案内と読書順。
- [docs/en/mcp-tools.md](../en/mcp-tools.md): 英語版の対応文書。
- [docs/ja/ecosystems.ja.md](./ecosystems.ja.md): 現在の ecosystem inventory。

## 正本ソース

- [.github/ecosystems/MCP_TOOLS.json](../../.github/ecosystems/MCP_TOOLS.json):
  共通 `ecosystem` namespace の registry。
- [.github/ecosystems/repository-governance/MCP_TOOLS.json](../../.github/ecosystems/repository-governance/MCP_TOOLS.json):
  ecosystem 固有の `repository_governance` namespace registry。
- [.github/ecosystems/mcp_models.py](../../.github/ecosystems/mcp_models.py):
  registry object の Pydantic model と検証ルール。
- [.github/ecosystems/mcp_tool_registry.py](../../.github/ecosystems/mcp_tool_registry.py):
  registry 読み込み、model 解決、fallback 検証の実装。
- [.github/ecosystems/mcp_server.py](../../.github/ecosystems/mcp_server.py):
  実行時の tool 登録と FastMCP への公開挙動。

## 命名と公開モデル

1. `.github/ecosystems/MCP_TOOLS.json` は `ecosystem` namespace の共通 tool を
   定義します。
2. 各 ecosystem は `mcp-enabled`、`mcp-tool-registry`、`mcp-tool-names` などの
   manifest field によって MCP 参加を宣言できます。
3. registry 内の tool は内部的には `<namespace>.<name>` 形式の qualified name
   で扱われます。
4. FastMCP では `.` を `_` に置換した名前で公開するため、
   `ecosystem.list_available` は `ecosystem_list_available` になります。
5. `enabled_by_default` が false の tool は、`include_disabled=True` を使わない
   限り標準の server 登録対象に入りません。

## Registry Schema

### Registry Object

| Field | 意味 |
|---|---|
| `version` | registry format の version。現在の repository では `"1"`。 |
| `namespace` | qualified tool name を作る prefix。 |
| `tools` | その namespace に属する tool 定義一覧。 |

### Tool Object

| Field | 意味 |
|---|---|
| `name` | registry namespace 内で一意な tool 名。 |
| `title` | MCP client に見せる人間向け title。 |
| `description` | registry と server metadata に使う安定した説明文。 |
| `handler` | `module.function` 形式の Python callable path。 |
| `kind` | `read` または `mutate`。 |
| `risk_level` | `low`、`medium`、`high` の risk 宣言。 |
| `confirmation_mode` | `none`、`preview_token`、`explicit_confirmation` の確認契約。 |
| `input_model` | repository 内 model registry で解決する request model 名。 |
| `result_model` | 同じ model registry で解決する response model 名。 |
| `tags` | discovery と分類のための tag。 |
| `enabled_by_default` | server が標準で登録するかどうか。 |
| `dry_run_supported` | 副作用なしの計画モードを持つかどうか。 |
| `validators_after` | mutate 後に呼ぶべき validator 名。 |
| `requires_repo_root` | source repository root を要求するかどうか。 |
| `requires_target_repo` | target repository path を要求するかどうか。 |
| `requires_ecosystem_slug` | ecosystem slug を要求するかどうか。 |
| `supports_preview_token` | preview token を使う確認フローに参加するかどうか。 |

## 実装済みの検証ルール

- tool 名は 1 つの registry 内で一意でなければなりません。
- `input_model` と `result_model` は
  [.github/ecosystems/mcp_models.py](../../.github/ecosystems/mcp_models.py)
  の model registry に存在する必要があります。
- `read` tool は confirmation を要求できず、preview token も持てません。
- `preview_token` confirmation を使う場合は
  `supports_preview_token=true` が必要です。
- `explicit_confirmation` は `mutate` tool にしか使えません。
- `requires_target_repo=true` は `mutate` tool にしか使えません。
- Pydantic model が使えない環境でも、
  [.github/ecosystems/mcp_tool_registry.py](../../.github/ecosystems/mcp_tool_registry.py)
  の fallback 実装で同等の契約検証を行います。

## 現在の Tool Inventory

### 共通 `ecosystem` Namespace

| Qualified name | FastMCP name | Kind | Confirmation | 主な役割 |
|---|---|---|---|---|
| `ecosystem.list_available` | `ecosystem_list_available` | `read` | `none` | 利用可能な ecosystem manifest と MCP 公開メタデータを一覧する。 |
| `ecosystem.get_manifest` | `ecosystem_get_manifest` | `read` | `none` | 1 つの ecosystem manifest 要約を返す。 |
| `ecosystem.preview_install` | `ecosystem_preview_install` | `mutate` | `none` | dry-run の install plan と preview token を作る。 |
| `ecosystem.apply_install` | `ecosystem_apply_install` | `mutate` | `preview_token` | preview ベースの確認後に ecosystem install を実行する。 |
| `ecosystem.update_core_files` | `ecosystem_update_core_files` | `mutate` | `none` | ecosystem 管理下の `.github` core files を再生成する。 |
| `ecosystem.validate_registry` | `ecosystem_validate_registry` | `read` | `none` | manifest、registry link、managed core file navigation を検証する。 |

### Ecosystem 固有 `repository_governance` Namespace

| Qualified name | FastMCP name | Kind | Confirmation | 主な役割 |
|---|---|---|---|---|
| `repository_governance.validate_repository` | `repository_governance_validate_repository` | `read` | `none` | repository-governance docs、link、TODO 構造を検証する。 |
| `repository_governance.validate_agent_skill_docs` | `repository_governance_validate_agent_skill_docs` | `read` | `none` | agent / skill / routing docs の整合性を検証する。 |