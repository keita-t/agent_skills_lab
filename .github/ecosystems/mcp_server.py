from __future__ import annotations

from dataclasses import dataclass
import logging
import importlib
from pathlib import Path
import sys
from typing import Callable

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

from ecosystem_lib import find_repo_root, load_ecosystem_manifests
from mcp_models import MODEL_REGISTRY, McpToolDefinition
from mcp_settings import McpServerSettings
from mcp_tool_registry import load_generic_tool_registry, load_manifest_tool_registry

ECOSYSTEMS_DIR = Path(__file__).resolve().parent
for candidate in [ECOSYSTEMS_DIR, *sorted(path for path in ECOSYSTEMS_DIR.iterdir() if path.is_dir())]:
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))


@dataclass(frozen=True)
class RegisteredTool:
    qualified_name: str
    definition: McpToolDefinition
    input_model: type[BaseModel]
    result_model: type[BaseModel]
    handler: Callable[[BaseModel], object]


def _load_handler(handler_path: str) -> Callable[[BaseModel], object]:
    module_name, function_name = handler_path.rsplit(".", 1)
    module = importlib.import_module(module_name)
    return getattr(module, function_name)


def load_registered_tools(
    repo_root: Path | str = ".",
    include_disabled: bool = False,
) -> dict[str, RegisteredTool]:
    resolved_repo_root = find_repo_root(Path(repo_root).resolve())
    registries = [load_generic_tool_registry(resolved_repo_root)]
    registries.extend(
        registry
        for manifest in load_ecosystem_manifests(resolved_repo_root)
        for registry in [load_manifest_tool_registry(resolved_repo_root, manifest)]
        if registry is not None
    )

    registered_tools: dict[str, RegisteredTool] = {}
    for registry in registries:
        for tool in registry.tools:
            if not include_disabled and not tool.enabled_by_default:
                continue
            qualified_name = f"{registry.namespace}.{tool.name}"
            registered_tools[qualified_name] = RegisteredTool(
                qualified_name=qualified_name,
                definition=tool,
                input_model=MODEL_REGISTRY[tool.input_model],
                result_model=MODEL_REGISTRY[tool.result_model],
                handler=_load_handler(tool.handler),
            )

    return registered_tools


def invoke_tool(
    name: str,
    payload: dict[str, object],
    repo_root: Path | str = ".",
    settings: McpServerSettings | None = None,
) -> BaseModel:
    _ = settings or McpServerSettings(repo_root=str(repo_root))
    tools = load_registered_tools(repo_root)
    if name not in tools:
        raise KeyError(f"Unknown tool: {name}")

    tool = tools[name]
    request = tool.input_model.model_validate(payload)
    response = tool.handler(request)
    if isinstance(response, tool.result_model):
        return response
    return tool.result_model.model_validate(response)


def _build_tool_callable(
    tool: RegisteredTool,
    repo_root: Path,
    settings: McpServerSettings,
) -> Callable[..., BaseModel]:
    input_model = tool.input_model
    result_model = tool.result_model

    def _tool(request: input_model) -> result_model:
        response = invoke_tool(
            tool.qualified_name,
            request.model_dump(mode="json"),
            repo_root=repo_root,
            settings=settings,
        )
        if isinstance(response, result_model):
            return response
        return result_model.model_validate(response)

    _tool.__name__ = tool.qualified_name.replace(".", "_")
    _tool.__qualname__ = _tool.__name__
    _tool.__doc__ = tool.definition.description
    _tool.__annotations__ = {"request": input_model, "return": result_model}
    return _tool


def build_mcp_server(
    settings: McpServerSettings | None = None,
    repo_root: Path | None = None,
) -> FastMCP:
    resolved_settings = settings or McpServerSettings()
    resolved_repo_root = find_repo_root(
        repo_root.resolve() if repo_root is not None else Path(resolved_settings.repo_root).resolve()
    )

    logging.basicConfig(
        level=getattr(logging, resolved_settings.log_level.upper(), logging.INFO),
        stream=sys.stderr,
        format="[%(levelname)s] %(message)s",
    )

    server = FastMCP(
        name="ecosystemTools",
        instructions=(
            "Expose ecosystem installation, validation, and repository-governance tooling "
            "for this workspace over stdio."
        ),
        log_level=resolved_settings.log_level.upper(),
    )

    for registered_tool in load_registered_tools(resolved_repo_root).values():
        safe_name = registered_tool.qualified_name.replace(".", "_")
        server.add_tool(
            _build_tool_callable(registered_tool, resolved_repo_root, resolved_settings),
            name=safe_name,
            title=registered_tool.definition.title,
            description=registered_tool.definition.description,
            meta={
                "risk_level": registered_tool.definition.risk_level,
                "confirmation_mode": registered_tool.definition.confirmation_mode,
                "tags": registered_tool.definition.tags,
                "validators_after": registered_tool.definition.validators_after,
                "qualified_name": registered_tool.qualified_name,
            },
            structured_output=True,
        )

    return server


def main() -> None:
    settings = McpServerSettings()
    server = build_mcp_server(settings)
    server.run(transport="stdio")


if __name__ == "__main__":
    main()