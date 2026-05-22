from __future__ import annotations

import json


def test_workspace_mcp_config_points_to_local_stdio_server(repo_root) -> None:
    config_path = repo_root / ".vscode" / "mcp.json"

    config = json.loads(config_path.read_text(encoding="utf-8"))

    server = config["servers"]["ecosystemTools"]
    assert server["type"] == "stdio"
    assert server["command"] == "${workspaceFolder}/.venv/bin/python"
    assert server["args"] == ["${workspaceFolder}/.github/ecosystems/mcp_server.py"]
    assert server["env"]["MCP_REPO_ROOT"] == "${workspaceFolder}"