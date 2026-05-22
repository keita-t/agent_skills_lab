# MCP Tools Specification

This document summarizes the MCP tool contract implemented in this repository
and the tool registries that are currently exposed.
The canonical implementation sources remain the JSON registries under
`.github/ecosystems/`, the manifest fields that opt ecosystems into MCP, and
the loader and server code under the same directory.

## Related Documents

- [docs/README.md](../README.md): documentation map and reading order.
- [docs/ja/mcp-tools.ja.md](../ja/mcp-tools.ja.md): Japanese counterpart.
- [docs/en/ecosystems.md](./ecosystems.md): current ecosystem inventory.

## Canonical Sources

- [.github/ecosystems/MCP_TOOLS.json](../../.github/ecosystems/MCP_TOOLS.json):
  shared `ecosystem` namespace registry.
- [.github/ecosystems/repository-governance/MCP_TOOLS.json](../../.github/ecosystems/repository-governance/MCP_TOOLS.json):
  ecosystem-scoped `repository_governance` namespace registry.
- [.github/ecosystems/mcp_models.py](../../.github/ecosystems/mcp_models.py):
  Pydantic models and validation rules for registry objects.
- [.github/ecosystems/mcp_tool_registry.py](../../.github/ecosystems/mcp_tool_registry.py):
  registry loading, model resolution, and fallback validation behavior.
- [.github/ecosystems/mcp_server.py](../../.github/ecosystems/mcp_server.py):
  runtime registration and FastMCP exposure behavior.

## Naming And Exposure Model

1. The shared registry in `.github/ecosystems/MCP_TOOLS.json` defines tools in
   the `ecosystem` namespace.
2. Each ecosystem may opt into MCP through manifest fields such as
   `mcp-enabled`, `mcp-tool-registry`, and `mcp-tool-names`.
3. A registry tool is addressed internally as a qualified name in the form
   `<namespace>.<name>`.
4. The FastMCP server exposes the same tool with dots replaced by underscores,
   so `ecosystem.list_available` becomes `ecosystem_list_available`.
5. Disabled tools stay out of the default server registration unless explicitly
   loaded with `include_disabled=True`.

## Registry Schema

### Registry Object

| Field | Meaning |
|---|---|
| `version` | Registry format version. The current repository uses `"1"`. |
| `namespace` | Prefix used to build qualified tool names. |
| `tools` | List of tool definitions that belong to the namespace. |

### Tool Object

| Field | Meaning |
|---|---|
| `name` | Tool name unique within its registry namespace. |
| `title` | Human-readable title exposed to MCP clients. |
| `description` | Stable behavior summary used in registry and server metadata. |
| `handler` | Python callable path in `module.function` form. |
| `kind` | `read` or `mutate`. |
| `risk_level` | Declared risk level: `low`, `medium`, or `high`. |
| `confirmation_mode` | Confirmation contract: `none`, `preview_token`, or `explicit_confirmation`. |
| `input_model` | Request model name resolved from the in-repository model registry. |
| `result_model` | Response model name resolved from the same model registry. |
| `tags` | Classification tags for discovery and grouping. |
| `enabled_by_default` | Whether the tool is registered by default in the server. |
| `dry_run_supported` | Whether the tool supports a side-effect-free planning mode. |
| `validators_after` | Validators the caller should run after mutation. |
| `requires_repo_root` | Whether the request needs a source repository root. |
| `requires_target_repo` | Whether the request needs a target repository path. |
| `requires_ecosystem_slug` | Whether the request needs an ecosystem slug. |
| `supports_preview_token` | Whether the tool participates in preview-token confirmation flow. |

## Implemented Validation Rules

- Tool names must be unique inside one registry.
- `input_model` and `result_model` must exist in the model registry loaded by
  [.github/ecosystems/mcp_models.py](../../.github/ecosystems/mcp_models.py).
- `read` tools cannot require confirmation and cannot support preview tokens.
- `preview_token` confirmation requires `supports_preview_token=true`.
- `explicit_confirmation` is only valid for `mutate` tools.
- `requires_target_repo=true` is only valid for `mutate` tools.
- The repository keeps a fallback validation path in
  [.github/ecosystems/mcp_tool_registry.py](../../.github/ecosystems/mcp_tool_registry.py)
  so registry loading still works when Pydantic models are unavailable.

## Current Tool Inventory

### Shared `ecosystem` Namespace

| Qualified name | FastMCP name | Kind | Confirmation | Primary role |
|---|---|---|---|---|
| `ecosystem.list_available` | `ecosystem_list_available` | `read` | `none` | List available ecosystem manifests and MCP exposure metadata. |
| `ecosystem.get_manifest` | `ecosystem_get_manifest` | `read` | `none` | Return one ecosystem manifest summary. |
| `ecosystem.preview_install` | `ecosystem_preview_install` | `mutate` | `none` | Build a dry-run install plan and preview token. |
| `ecosystem.apply_install` | `ecosystem_apply_install` | `mutate` | `preview_token` | Execute an ecosystem install after explicit preview-based confirmation. |
| `ecosystem.update_core_files` | `ecosystem_update_core_files` | `mutate` | `none` | Regenerate ecosystem-managed `.github` core files. |
| `ecosystem.validate_registry` | `ecosystem_validate_registry` | `read` | `none` | Validate manifests, registry links, and managed core file navigation. |

### Ecosystem-Scoped `repository_governance` Namespace

| Qualified name | FastMCP name | Kind | Confirmation | Primary role |
|---|---|---|---|---|
| `repository_governance.validate_repository` | `repository_governance_validate_repository` | `read` | `none` | Validate repository-governance docs, links, and TODO structure. |
| `repository_governance.validate_agent_skill_docs` | `repository_governance_validate_agent_skill_docs` | `read` | `none` | Validate agent, skill, and routing document alignment. |