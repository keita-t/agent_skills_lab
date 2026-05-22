from __future__ import annotations

from pathlib import Path

import pytest

from ecosystem_lib import load_ecosystem_manifest
from mcp_tool_registry import load_generic_tool_registry, load_manifest_tool_registry


def test_load_generic_tool_registry_reads_v1_ecosystem_tools(repo_root: Path) -> None:
    registry = load_generic_tool_registry(repo_root)

    assert registry.namespace == "ecosystem"
    assert registry.qualified_tool_names() == [
        "ecosystem.list_available",
        "ecosystem.get_manifest",
        "ecosystem.preview_install",
        "ecosystem.apply_install",
        "ecosystem.update_core_files",
        "ecosystem.validate_registry",
    ]


def test_load_manifest_tool_registry_reads_repository_governance_tools(
    repo_root: Path,
) -> None:
    manifest = load_ecosystem_manifest(
        repo_root / ".github" / "ecosystems" / "repository-governance" / "ECOSYSTEM.md"
    )

    registry = load_manifest_tool_registry(repo_root, manifest)

    assert registry is not None
    assert registry.namespace == "repository_governance"
    assert registry.qualified_tool_names() == manifest.mcp_tool_names


def test_load_tool_registry_rejects_unknown_model(tmp_path: Path) -> None:
    registry_path = tmp_path / "registry.json"
    registry_path.write_text(
        """
{
  "version": "1",
  "namespace": "broken",
  "tools": [
    {
      "name": "demo",
      "title": "Demo",
      "description": "Demo tool",
      "handler": "demo.handler",
      "kind": "read",
      "risk_level": "low",
      "confirmation_mode": "none",
      "input_model": "MissingInput",
      "result_model": "ValidationResult"
    }
  ]
}
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="unknown models"):
        from mcp_tool_registry import load_tool_registry

        load_tool_registry(registry_path)