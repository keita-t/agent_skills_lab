from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from ecosystem_lib import EcosystemManifest

try:
    from mcp_models import MODEL_REGISTRY, McpToolRegistry
except ModuleNotFoundError:
    MODEL_REGISTRY = {
        "ApplyInstallInput": object,
        "ApplyInstallResult": object,
        "GetManifestInput": object,
        "GetManifestResult": object,
        "ListAvailableEcosystemsInput": object,
        "ListAvailableEcosystemsResult": object,
        "PreviewInstallInput": object,
        "PreviewInstallResult": object,
        "UpdateCoreFilesInput": object,
        "UpdateCoreFilesResult": object,
        "ValidateAgentSkillDocsInput": object,
        "ValidateRegistryInput": object,
        "ValidateRepositoryGovernanceInput": object,
        "ValidationResult": object,
    }

    @dataclass(frozen=True)
    class _FallbackToolDefinition:
        name: str
        title: str
        description: str
        handler: str
        kind: str
        risk_level: str = "low"
        confirmation_mode: str = "none"
        input_model: str = ""
        result_model: str = ""
        tags: list[str] | None = None
        enabled_by_default: bool = True
        dry_run_supported: bool = False
        validators_after: list[str] | None = None
        requires_repo_root: bool = False
        requires_target_repo: bool = False
        requires_ecosystem_slug: bool = False
        supports_preview_token: bool = False

        def __post_init__(self) -> None:
            if self.kind == "read":
                if self.confirmation_mode != "none":
                    raise ValueError("read tools cannot require confirmation")
                if self.supports_preview_token:
                    raise ValueError("read tools cannot support preview tokens")
            if self.confirmation_mode == "preview_token" and not self.supports_preview_token:
                raise ValueError("preview_token confirmation requires supports_preview_token")
            if self.confirmation_mode == "explicit_confirmation" and self.kind != "mutate":
                raise ValueError("explicit_confirmation is only valid for mutating tools")
            if self.requires_target_repo and self.kind != "mutate":
                raise ValueError("requires_target_repo is only valid for mutating tools")

    @dataclass(frozen=True)
    class McpToolRegistry:
        version: str
        namespace: str
        tools: list[_FallbackToolDefinition]

        @classmethod
        def model_validate(cls, data: dict[str, object]) -> "McpToolRegistry":
            tools = [
                _FallbackToolDefinition(**tool)
                for tool in data.get("tools", [])
            ]
            names = [tool.name for tool in tools]
            if len(names) != len(set(names)):
                raise ValueError("tool names must be unique within a registry")
            return cls(
                version=str(data["version"]),
                namespace=str(data["namespace"]),
                tools=tools,
            )

        def qualified_tool_names(self) -> list[str]:
            return [f"{self.namespace}.{tool.name}" for tool in self.tools]


def load_tool_registry(path: Path) -> McpToolRegistry:
    data = json.loads(path.read_text(encoding="utf-8"))
    registry = McpToolRegistry.model_validate(data)

    missing_models: list[str] = []
    for tool in registry.tools:
        if tool.input_model not in MODEL_REGISTRY:
            missing_models.append(tool.input_model)
        if tool.result_model not in MODEL_REGISTRY:
            missing_models.append(tool.result_model)

    if missing_models:
        missing = ", ".join(sorted(set(missing_models)))
        raise ValueError(f"registry references unknown models: {missing}")

    return registry


def load_generic_tool_registry(repo_root: Path) -> McpToolRegistry:
    return load_tool_registry(repo_root / ".github" / "ecosystems" / "MCP_TOOLS.json")


def load_manifest_tool_registry(
    repo_root: Path,
    manifest: EcosystemManifest,
) -> McpToolRegistry | None:
    if not manifest.mcp_enabled or not manifest.mcp_tool_registry:
        return None
    return load_tool_registry(repo_root / manifest.mcp_tool_registry)