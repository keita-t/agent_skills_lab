from __future__ import annotations

from pathlib import Path

from ecosystem_delivery_service import execute_delivery_plan


class WorkflowCommandRunner:
    def __init__(self) -> None:
        self.commands: list[tuple[tuple[str, ...], Path]] = []
        self.status_outputs = ["?? install\n", " D remove\n"]

    def run(self, command: list[str], cwd: Path):
        self.commands.append((tuple(command), cwd))
        if command[:3] == ["gh", "repo", "clone"]:
            destination = Path(command[4])
            destination.mkdir(parents=True, exist_ok=True)
            (destination / ".git").mkdir(exist_ok=True)
            return type("Result", (), {"stdout": "", "stderr": ""})()
        if command[:3] == ["gh", "repo", "view"]:
            return type("Result", (), {"stdout": "main\n", "stderr": ""})()
        if command[:3] == ["git", "status", "--short"]:
            return type("Result", (), {"stdout": self.status_outputs.pop(0), "stderr": ""})()
        if command[:3] == ["gh", "pr", "create"]:
            branch_name = command[command.index("--head") + 1]
            return type("Result", (), {"stdout": f"https://example.com/{branch_name}\n", "stderr": ""})()
        return type("Result", (), {"stdout": "", "stderr": ""})()


def test_execute_delivery_plan_round_trips_manifest_owned_payload(tmp_path: Path) -> None:
    runner = WorkflowCommandRunner()

    install_result = execute_delivery_plan(
        action="install",
        target_repo="octo/example-repo",
        ecosystem_slug="repository-governance",
        working_directory=tmp_path,
        runner=runner,
    )

    clone_path = Path(install_result.clone_path)
    preserved_file = clone_path / "README.md"
    preserved_file.write_text("keep me\n", encoding="utf-8")

    assert install_result.pr_url == "https://example.com/ecosystem-repository-governance-install"
    assert (clone_path / ".github" / "agents" / "governance-ecosystem-manifest.agent.md").is_file()
    assert (clone_path / ".github" / "agents" / "governance-ecosystem-delivery.agent.md").is_file()
    assert not (clone_path / ".github" / "ecosystems" / "mcp_server.py").exists()
    assert not (clone_path / ".github" / "ecosystems" / "deliver_ecosystem.py").exists()

    remove_result = execute_delivery_plan(
        action="remove",
        target_repo="octo/example-repo",
        ecosystem_slug="repository-governance",
        working_directory=tmp_path,
        runner=runner,
    )

    assert remove_result.pr_url == "https://example.com/ecosystem-repository-governance-remove"
    assert not (clone_path / ".github" / "ecosystems" / "repository-governance").exists()
    assert not (clone_path / ".github" / "agents" / "governance-ecosystem-manifest.agent.md").exists()
    assert preserved_file.read_text(encoding="utf-8") == "keep me\n"