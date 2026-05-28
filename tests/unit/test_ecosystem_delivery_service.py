from __future__ import annotations

from pathlib import Path
import pytest

from ecosystem_delivery_service import (
    execute_delivery_plan,
    apply_delivery_changes,
    build_install_changeset,
    build_remove_changeset,
    DeliveryConflictError,
    generate_pr_body,
    prepare_branch_name,
)


class FakeCommandRunner:
    def __init__(self, clone_root: Path, status_output: str = "?? manifest-owned-change\n") -> None:
        self.clone_root = clone_root
        self.status_output = status_output
        self.commands: list[tuple[tuple[str, ...], Path]] = []

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
            return type("Result", (), {"stdout": self.status_output, "stderr": ""})()
        if command[:3] == ["gh", "pr", "create"]:
            return type("Result", (), {"stdout": "https://example.com/pr/123\n", "stderr": ""})()
        return type("Result", (), {"stdout": "", "stderr": ""})()


def test_build_install_changeset_uses_manifest_owned_paths_only(tmp_path) -> None:
    result = build_install_changeset(
        target_root=tmp_path / "target-repo",
        ecosystem_slug="repository-governance",
    )

    relative_destinations = {change.relative_destination for change in result}

    assert all(change.action == "copy" for change in result)
    assert ".github/agents/governance-repository-context-manager.agent.md" in relative_destinations
    assert ".github/agents/governance-ecosystem-manifest.agent.md" in relative_destinations
    assert ".github/agents/governance-ecosystem-delivery.agent.md" in relative_destinations
    assert ".github/skills/repository-governance-bootstrap" in relative_destinations
    assert ".github/ecosystems/repository-governance/ECOSYSTEM.md" in relative_destinations
    assert ".github/ecosystems/repository-governance/assets/templates" in relative_destinations
    assert ".github/ecosystems/ecosystem_lib.py" not in relative_destinations
    assert ".github/ECOSYSTEM_REGISTRY.md" not in relative_destinations


def test_build_remove_changeset_lists_only_existing_manifest_owned_paths(isolated_repo) -> None:
    result = build_remove_changeset(
        target_root=isolated_repo,
        ecosystem_slug="repository-governance",
    )

    relative_destinations = [change.relative_destination for change in result]

    assert result
    assert all(change.action == "remove" for change in result)
    assert ".github/ecosystems/repository-governance/ECOSYSTEM.md" in relative_destinations
    assert ".github/ecosystems/repository-governance/assets/templates" in relative_destinations
    assert ".github/agents/governance-repository-context-manager.agent.md" in relative_destinations
    assert ".github/agents/governance-ecosystem-manifest.agent.md" in relative_destinations
    assert ".github/agents/governance-ecosystem-delivery.agent.md" in relative_destinations
    assert ".github/ecosystems/ecosystem_lib.py" not in relative_destinations
    assert ".github/AGENT_SKILL_ROUTING.md" not in relative_destinations


def test_apply_delivery_changes_copies_manifest_owned_paths(tmp_path) -> None:
    target_root = tmp_path / "target-repo"

    actions = apply_delivery_changes(
        build_install_changeset(
            target_root=target_root,
            ecosystem_slug="repository-governance",
        )
    )

    assert actions
    assert (target_root / ".github" / "agents" / "governance-ecosystem-manifest.agent.md").is_file()
    assert (target_root / ".github" / "agents" / "governance-ecosystem-delivery.agent.md").is_file()
    assert (target_root / ".github" / "ecosystems" / "repository-governance" / "assets" / "templates").is_dir()
    installed_skill = (
        target_root
        / ".github"
        / "skills"
        / "repository-governance-bootstrap"
        / "SKILL.md"
    ).read_text(encoding="utf-8")
    assert "deliver_ecosystem.py" not in installed_skill
    assert "validate_ecosystem_registry.sh" not in installed_skill
    assert "../../agents/governance-ecosystem-delivery.agent.md" in installed_skill
    assert not (target_root / ".github" / "ecosystems" / "ecosystem_lib.py").exists()


def test_apply_delivery_changes_removes_existing_manifest_owned_paths(tmp_path) -> None:
    target_root = tmp_path / "target-repo"
    preserved_file = target_root / "README.md"
    preserved_file.parent.mkdir(parents=True, exist_ok=True)
    preserved_file.write_text("keep me\n", encoding="utf-8")

    apply_delivery_changes(
        build_install_changeset(
            target_root=target_root,
            ecosystem_slug="repository-governance",
        )
    )

    actions = apply_delivery_changes(
        build_remove_changeset(
            target_root=target_root,
            ecosystem_slug="repository-governance",
        )
    )

    assert actions
    assert not (target_root / ".github" / "agents" / "governance-ecosystem-manifest.agent.md").exists()
    assert not (target_root / ".github" / "agents" / "governance-ecosystem-delivery.agent.md").exists()
    assert not (target_root / ".github" / "ecosystems" / "repository-governance").exists()
    assert preserved_file.read_text(encoding="utf-8") == "keep me\n"


def test_apply_delivery_changes_skips_identical_existing_manifest_payload(tmp_path) -> None:
    target_root = tmp_path / "target-repo"

    apply_delivery_changes(
        build_install_changeset(
            target_root=target_root,
            ecosystem_slug="repository-governance",
        )
    )

    actions = apply_delivery_changes(
        build_install_changeset(
            target_root=target_root,
            ecosystem_slug="repository-governance",
        )
    )

    assert actions == []


def test_apply_delivery_changes_rejects_modified_existing_manifest_payload(tmp_path) -> None:
    target_root = tmp_path / "target-repo"
    conflicting_file = (
        target_root
        / ".github"
        / "agents"
        / "governance-ecosystem-delivery.agent.md"
    )
    conflicting_file.parent.mkdir(parents=True, exist_ok=True)
    conflicting_file.write_text("manually modified\n", encoding="utf-8")

    with pytest.raises(DeliveryConflictError) as exc_info:
        apply_delivery_changes(
            build_install_changeset(
                target_root=target_root,
                ecosystem_slug="repository-governance",
            )
        )

    assert [conflict.relative_destination for conflict in exc_info.value.conflicts] == [
        ".github/agents/governance-ecosystem-delivery.agent.md"
    ]
    assert "overwrite" in str(exc_info.value)


def test_apply_delivery_changes_rejects_removing_modified_manifest_payload(tmp_path) -> None:
    target_root = tmp_path / "target-repo"

    apply_delivery_changes(
        build_install_changeset(
            target_root=target_root,
            ecosystem_slug="repository-governance",
        )
    )
    modified_file = (
        target_root
        / ".github"
        / "agents"
        / "governance-ecosystem-delivery.agent.md"
    )
    modified_file.write_text(modified_file.read_text(encoding="utf-8") + "\nmodified\n", encoding="utf-8")

    with pytest.raises(DeliveryConflictError) as exc_info:
        apply_delivery_changes(
            build_remove_changeset(
                target_root=target_root,
                ecosystem_slug="repository-governance",
            )
        )

    assert [conflict.relative_destination for conflict in exc_info.value.conflicts] == [
        ".github/agents/governance-ecosystem-delivery.agent.md"
    ]
    assert "remove" in str(exc_info.value)


def test_prepare_branch_name_uses_default_pattern() -> None:
    assert prepare_branch_name("repository-governance", "install") == "ecosystem-repository-governance-install"


def test_generate_pr_body_lists_file_actions() -> None:
    body = generate_pr_body(
        "repository-governance",
        "install",
        ["copy /tmp/target/.github/agents/governance-ecosystem-delivery.agent.md"],
    )

    assert "Ecosystem install" in body
    assert "repository-governance" in body
    assert "copy /tmp/target/.github/agents/governance-ecosystem-delivery.agent.md" in body


def test_execute_delivery_plan_runs_clone_branch_commit_push_and_pr(tmp_path) -> None:
    runner = FakeCommandRunner(tmp_path)

    result = execute_delivery_plan(
        action="install",
        target_repo="octo/example-repo",
        ecosystem_slug="repository-governance",
        working_directory=tmp_path,
        runner=runner,
    )

    command_prefixes = [command for command, _ in runner.commands]

    assert result.pr_url == "https://example.com/pr/123"
    assert result.branch_name == "ecosystem-repository-governance-install"
    assert command_prefixes == [
        ("gh", "repo", "clone", "octo/example-repo", str(tmp_path / "example-repo")),
        ("gh", "repo", "view", "octo/example-repo", "--json", "defaultBranchRef", "--jq", ".defaultBranchRef.name"),
        ("git", "status", "--short"),
        ("git", "switch", "-c", "ecosystem-repository-governance-install"),
        ("git", "add", "--all"),
        ("git", "commit", "-m", "Install repository-governance ecosystem"),
        ("git", "push", "--set-upstream", "origin", "ecosystem-repository-governance-install"),
        ("gh", "pr", "create", "--base", "main", "--head", "ecosystem-repository-governance-install", "--title", "Install repository-governance ecosystem", "--body", result.pr_body),
    ]
    assert (tmp_path / "example-repo" / ".github" / "agents" / "governance-ecosystem-delivery.agent.md").is_file()


def test_execute_delivery_plan_dry_run_skips_branch_and_pr(tmp_path) -> None:
    runner = FakeCommandRunner(tmp_path)

    result = execute_delivery_plan(
        action="install",
        target_repo="octo/example-repo",
        ecosystem_slug="repository-governance",
        working_directory=tmp_path,
        runner=runner,
        dry_run=True,
    )

    command_prefixes = [command for command, _ in runner.commands]

    assert result.pr_url is None
    assert result.committed is False
    assert command_prefixes == [
        ("gh", "repo", "clone", "octo/example-repo", str(tmp_path / "example-repo")),
        ("gh", "repo", "view", "octo/example-repo", "--json", "defaultBranchRef", "--jq", ".defaultBranchRef.name"),
    ]


def test_execute_delivery_plan_remove_noop_skips_branch_and_pr(tmp_path) -> None:
    runner = FakeCommandRunner(tmp_path, status_output="")

    result = execute_delivery_plan(
        action="remove",
        target_repo="octo/example-repo",
        ecosystem_slug="repository-governance",
        working_directory=tmp_path,
        runner=runner,
    )

    command_prefixes = [command for command, _ in runner.commands]

    assert result.pr_url is None
    assert result.committed is False
    assert command_prefixes == [
        ("gh", "repo", "clone", "octo/example-repo", str(tmp_path / "example-repo")),
        ("gh", "repo", "view", "octo/example-repo", "--json", "defaultBranchRef", "--jq", ".defaultBranchRef.name"),
        ("git", "status", "--short"),
    ]