from __future__ import annotations

from pathlib import Path

import deliver_ecosystem
from ecosystem_delivery_service import DeliveryConflict, DeliveryConflictError, DeliveryExecutionResult


def test_deliver_ecosystem_cli_prints_dry_run_summary(
    monkeypatch,
    invoke_main,
    capsys,
    tmp_path: Path,
) -> None:
    def fake_execute_delivery_plan(**kwargs) -> DeliveryExecutionResult:
        assert kwargs["action"] == "install"
        assert kwargs["target_repo"] == "octo/example-repo"
        assert kwargs["ecosystem_slug"] == "repository-governance"
        assert kwargs["agent_hosts"] is None
        return DeliveryExecutionResult(
            action="install",
            ecosystem_slug="repository-governance",
            resolved_ecosystems=["ecosystem-audit", "repository-governance"],
            target_repo="octo/example-repo",
            base_branch="main",
            branch_name="ecosystem-repository-governance-install",
            agent_hosts=["github-copilot"],
            working_directory=str(tmp_path),
            clone_path=str(tmp_path / "example-repo"),
            file_actions=["copy /tmp/example/.github/agents/governance-ecosystem-delivery.agent.md"],
            pr_title="Install repository-governance ecosystem",
            pr_body="body",
            pr_url=None,
            committed=False,
        )

    monkeypatch.setattr(deliver_ecosystem, "execute_delivery_plan", fake_execute_delivery_plan)

    exit_code = invoke_main(
        deliver_ecosystem,
        "install",
        "--target-repo",
        "octo/example-repo",
        "--ecosystem",
        "repository-governance",
        "--dry-run",
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Dry run completed without creating a pull request." in captured.out
    assert "repository-governance" in captured.out
    assert "Agent hosts: github-copilot" in captured.out


def test_deliver_ecosystem_cli_passes_explicit_agent_hosts(
    monkeypatch,
    invoke_main,
    tmp_path: Path,
) -> None:
    def fake_execute_delivery_plan(**kwargs) -> DeliveryExecutionResult:
        assert kwargs["agent_hosts"] == ["claude-code", "codex"]
        return DeliveryExecutionResult(
            action="install",
            ecosystem_slug="repository-governance",
            resolved_ecosystems=["ecosystem-audit", "repository-governance"],
            target_repo="octo/example-repo",
            base_branch="main",
            branch_name="ecosystem-repository-governance-install",
            agent_hosts=["claude-code", "codex"],
            working_directory=str(tmp_path),
            clone_path=str(tmp_path / "example-repo"),
            file_actions=[],
            pr_title="Install repository-governance ecosystem",
            pr_body="body",
            pr_url=None,
            committed=False,
        )

    monkeypatch.setattr(deliver_ecosystem, "execute_delivery_plan", fake_execute_delivery_plan)

    exit_code = invoke_main(
        deliver_ecosystem,
        "install",
        "--target-repo",
        "octo/example-repo",
        "--ecosystem",
        "repository-governance",
        "--agent-host",
        "claude-code",
        "--agent-host",
        "codex",
    )

    assert exit_code == 0


def test_deliver_ecosystem_cli_returns_error_for_invalid_target_repo(
    invoke_main,
    capsys,
) -> None:
    exit_code = invoke_main(
        deliver_ecosystem,
        "install",
        "--target-repo",
        "not-a-repo",
        "--ecosystem",
        "repository-governance",
        "--dry-run",
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "owner/repo" in captured.out


def test_deliver_ecosystem_cli_lists_conflicting_paths(
    monkeypatch,
    invoke_main,
    capsys,
) -> None:
    def fake_execute_delivery_plan(**kwargs):
        raise DeliveryConflictError(
            [
                DeliveryConflict(
                    action="copy",
                    relative_destination=".github/agents/governance-ecosystem-delivery.agent.md",
                    destination="/tmp/example/.github/agents/governance-ecosystem-delivery.agent.md",
                ),
                DeliveryConflict(
                    action="remove",
                    relative_destination=".github/skills/repository-doc-governance",
                    destination="/tmp/example/.github/skills/repository-doc-governance",
                ),
            ]
        )

    monkeypatch.setattr(deliver_ecosystem, "execute_delivery_plan", fake_execute_delivery_plan)

    exit_code = invoke_main(
        deliver_ecosystem,
        "install",
        "--target-repo",
        "octo/example-repo",
        "--ecosystem",
        "repository-governance",
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Delivery safety check failed." in captured.out
    assert ".github/agents/governance-ecosystem-delivery.agent.md (overwrite)" in captured.out
    assert ".github/skills/repository-doc-governance (remove)" in captured.out
