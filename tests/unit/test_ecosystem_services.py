from __future__ import annotations

import asyncio

from ecosystem_catalog_service import get_ecosystem_manifest, list_available_ecosystems
from ecosystem_install_service import build_install_plan
from mcp_models import GetManifestInput, ListAvailableEcosystemsInput, PreviewInstallInput
from mcp_server import build_mcp_server, invoke_tool, load_registered_tools


def test_list_available_ecosystems_returns_repository_governance(repo_root) -> None:
    result = list_available_ecosystems(ListAvailableEcosystemsInput(repo_root=str(repo_root)))

    assert [ecosystem.slug for ecosystem in result.ecosystems] == ["repository-governance"]


def test_get_ecosystem_manifest_returns_mcp_tool_names(repo_root) -> None:
    result = get_ecosystem_manifest(
        GetManifestInput(repo_root=str(repo_root), ecosystem_slug="repository-governance")
    )

    assert result.manifest.mcp_tool_names == [
        "repository_governance.validate_repository",
        "repository_governance.validate_agent_skill_docs",
    ]


def test_build_install_plan_returns_confirmation_token(blank_repo) -> None:
    result = build_install_plan(
        PreviewInstallInput(
            target_repo=str(blank_repo),
            ecosystem_slug="repository-governance",
            merge_strategy="merge",
        )
    )

    assert result.preview_token
    assert result.requires_confirmation is True
    assert result.actions


def test_mcp_server_registers_and_invokes_v1_tools(repo_root) -> None:
    tools = load_registered_tools(repo_root)

    assert sorted(tools) == [
        "ecosystem.apply_install",
        "ecosystem.get_manifest",
        "ecosystem.list_available",
        "ecosystem.preview_install",
        "ecosystem.update_core_files",
        "ecosystem.validate_registry",
        "repository_governance.validate_agent_skill_docs",
        "repository_governance.validate_repository",
    ]

    result = invoke_tool(
        "ecosystem.list_available",
        {"repo_root": str(repo_root)},
        repo_root=repo_root,
    )

    assert [ecosystem.slug for ecosystem in result.ecosystems] == ["repository-governance"]


def test_fastmcp_server_lists_registered_v1_tools(repo_root) -> None:
    server = build_mcp_server(repo_root=repo_root)

    tool_names = sorted(tool.name for tool in asyncio.run(server.list_tools()))
    assert tool_names == [
        "ecosystem_apply_install",
        "ecosystem_get_manifest",
        "ecosystem_list_available",
        "ecosystem_preview_install",
        "ecosystem_update_core_files",
        "ecosystem_validate_registry",
        "repository_governance_validate_agent_skill_docs",
        "repository_governance_validate_repository",
    ]