from __future__ import annotations

import os
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


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def create_test_ecosystem_source_root(
    tmp_path: Path,
    manifests: list[dict[str, object]],
) -> Path:
    source_root = tmp_path / "source-repo"

    for manifest in manifests:
        slug = str(manifest["slug"])
        agent_name = f"{slug}.agent.md"
        dependencies = [str(item) for item in manifest.get("dependencies", [])]
        ecosystem_files = [str(item) for item in manifest.get("ecosystem_files", [])]
        shared_ownership_files = [
            str(item) for item in manifest.get("shared_ownership_files", [])
        ]

        write_text(
            source_root / ".github" / "agents" / agent_name,
            f"---\nname: {slug}\n---\n\n# {slug}\n",
        )

        for relative_path in ecosystem_files:
            destination = source_root / relative_path
            if not destination.exists():
                write_text(destination, f"{relative_path}\n")

        dependencies_literal = ", ".join(dependencies)
        ecosystem_files_literal = ", ".join(ecosystem_files)
        shared_ownership_literal = ", ".join(shared_ownership_files)
        write_text(
            source_root / ".github" / "ecosystems" / slug / "ECOSYSTEM.md",
            "\n".join(
                [
                    "---",
                    f"slug: {slug}",
                    f"name: {slug.title()}",
                    "description: Test ecosystem.",
                    "status: active",
                    f"root-agent: {agent_name}",
                    f"agents: [{agent_name}]",
                    "skills: []",
                    f"dependencies: [{dependencies_literal}]",
                    f"ecosystem-files: [{ecosystem_files_literal}]",
                    *(
                        [f"shared-ownership-files: [{shared_ownership_literal}]"]
                        if shared_ownership_files
                        else []
                    ),
                    "---",
                    "",
                    f"# {slug.title()}",
                    "",
                ]
            ),
        )

    return source_root


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
    assert ".github/agents/ecosystem-audit.agent.md" in relative_destinations
    assert ".github/skills/repository-governance-bootstrap" in relative_destinations
    assert ".github/ecosystems/ecosystem-audit/ECOSYSTEM.md" in relative_destinations
    assert ".github/ecosystems/ecosystem-audit/audit/core-rules.md" in relative_destinations
    assert ".github/ecosystems/ecosystem-audit/audit/report-contract.md" in relative_destinations
    assert ".github/ecosystems/ecosystem-audit/audit/work-quality-rubric.md" in relative_destinations
    assert ".github/ecosystems/ecosystem-audit/assets/templates" in relative_destinations
    assert ".github/ecosystems/ecosystem-audit/assets/smoke-scenarios" in relative_destinations
    assert ".github/ecosystems/repository-governance/ECOSYSTEM.md" in relative_destinations
    assert ".github/ecosystems/repository-governance/assets/templates" in relative_destinations
    assert ".github/ecosystems/repository-governance/audit/repository-governance-audit.md" in relative_destinations
    assert ".github/ecosystems/ecosystem_lib.py" not in relative_destinations
    assert ".github/ECOSYSTEM_REGISTRY.md" not in relative_destinations


def test_build_install_changeset_uses_manifest_owned_paths_only_for_codebase_context(tmp_path) -> None:
    result = build_install_changeset(
        target_root=tmp_path / "target-repo",
        ecosystem_slug="codebase-context",
    )

    relative_destinations = {change.relative_destination for change in result}

    assert all(change.action == "copy" for change in result)
    assert ".github/agents/ecosystem-audit.agent.md" in relative_destinations
    assert ".github/agents/codebase-context.agent.md" in relative_destinations
    assert ".github/skills/codebase-context-export" in relative_destinations
    assert ".github/ecosystems/ecosystem-audit/ECOSYSTEM.md" in relative_destinations
    assert ".github/ecosystems/ecosystem-audit/audit/core-rules.md" in relative_destinations
    assert ".github/ecosystems/ecosystem-audit/audit/work-quality-rubric.md" in relative_destinations
    assert ".github/ecosystems/ecosystem-audit/assets/templates" in relative_destinations
    assert ".github/ecosystems/codebase-context/ECOSYSTEM.md" in relative_destinations
    assert ".github/ecosystems/codebase-context/audit/codebase-context-audit.md" in relative_destinations
    assert ".github/ecosystems/runtime_container_lib.sh" in relative_destinations
    assert ".github/ecosystems/codebase-context/Dockerfile" in relative_destinations
    assert ".github/ecosystems/codebase-context/generate_codebase_context.py" in relative_destinations
    assert ".github/ecosystems/codebase-context/generate_codebase_context.sh" in relative_destinations
    assert ".github/ecosystems/ecosystem_lib.py" not in relative_destinations


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
    assert ".github/ecosystems/repository-governance/audit/repository-governance-audit.md" in relative_destinations
    assert ".github/agents/governance-repository-context-manager.agent.md" in relative_destinations
    assert ".github/agents/governance-ecosystem-manifest.agent.md" in relative_destinations
    assert ".github/agents/governance-ecosystem-delivery.agent.md" in relative_destinations
    assert ".github/ecosystems/ecosystem-audit/ECOSYSTEM.md" not in relative_destinations
    assert ".github/agents/ecosystem-audit.agent.md" not in relative_destinations
    assert ".github/ecosystems/codebase-context/ECOSYSTEM.md" not in relative_destinations
    assert ".github/ecosystems/ecosystem_lib.py" not in relative_destinations
    assert ".github/AGENT_SKILL_ROUTING.md" not in relative_destinations


def test_build_install_changeset_allows_explicitly_shared_manifest_owned_path(tmp_path) -> None:
    shared_path = ".github/ecosystems/shared/runtime-helper.sh"
    source_root = create_test_ecosystem_source_root(
        tmp_path,
        [
            {
                "slug": "alpha",
                "dependencies": [],
                "ecosystem_files": [
                    shared_path,
                    ".github/ecosystems/alpha/alpha.txt",
                ],
                "shared_ownership_files": [shared_path],
            },
            {
                "slug": "beta",
                "dependencies": ["alpha"],
                "ecosystem_files": [
                    shared_path,
                    ".github/ecosystems/beta/beta.txt",
                ],
                "shared_ownership_files": [shared_path],
            },
        ],
    )

    result = build_install_changeset(
        target_root=tmp_path / "target-repo",
        ecosystem_slug="beta",
        source_root=source_root,
    )

    relative_destinations = [change.relative_destination for change in result]

    assert relative_destinations.count(shared_path) == 1


def test_build_install_changeset_rejects_duplicate_path_without_shared_ownership_metadata(tmp_path) -> None:
    shared_path = ".github/ecosystems/shared/runtime-helper.sh"
    source_root = create_test_ecosystem_source_root(
        tmp_path,
        [
            {
                "slug": "alpha",
                "dependencies": [],
                "ecosystem_files": [shared_path],
            },
            {
                "slug": "beta",
                "dependencies": ["alpha"],
                "ecosystem_files": [shared_path],
            },
        ],
    )

    with pytest.raises(RuntimeError, match="Manifest-owned path conflict"):
        build_install_changeset(
            target_root=tmp_path / "target-repo",
            ecosystem_slug="beta",
            source_root=source_root,
        )


def test_remove_preserves_explicitly_shared_path_until_last_owner_is_removed(
    tmp_path,
) -> None:
    shared_path = ".github/ecosystems/shared/runtime-helper.sh"
    source_root = create_test_ecosystem_source_root(
        tmp_path,
        [
            {
                "slug": "alpha",
                "dependencies": [],
                "ecosystem_files": [
                    shared_path,
                    ".github/ecosystems/alpha/alpha.txt",
                ],
                "shared_ownership_files": [shared_path],
            },
            {
                "slug": "beta",
                "dependencies": [],
                "ecosystem_files": [
                    shared_path,
                    ".github/ecosystems/beta/beta.txt",
                ],
                "shared_ownership_files": [shared_path],
            },
        ],
    )
    target_root = tmp_path / "target-repo"

    apply_delivery_changes(
        build_install_changeset(
            target_root=target_root,
            ecosystem_slug="alpha",
            source_root=source_root,
        )
    )
    apply_delivery_changes(
        build_install_changeset(
            target_root=target_root,
            ecosystem_slug="beta",
            source_root=source_root,
        )
    )

    shared_helper = target_root / ".github" / "ecosystems" / "shared" / "runtime-helper.sh"

    remove_alpha = build_remove_changeset(
        target_root=target_root,
        ecosystem_slug="alpha",
        source_root=source_root,
    )

    assert shared_path not in {
        change.relative_destination for change in remove_alpha
    }

    apply_delivery_changes(remove_alpha)

    assert shared_helper.is_file()
    assert not (target_root / ".github" / "ecosystems" / "alpha").exists()
    assert (target_root / ".github" / "ecosystems" / "beta").exists()

    apply_delivery_changes(
        build_remove_changeset(
            target_root=target_root,
            ecosystem_slug="beta",
            source_root=source_root,
        )
    )

    assert not shared_helper.exists()


def test_apply_delivery_changes_copies_manifest_owned_paths(tmp_path) -> None:
    target_root = tmp_path / "target-repo"

    actions = apply_delivery_changes(
        build_install_changeset(
            target_root=target_root,
            ecosystem_slug="repository-governance",
        )
    )

    assert actions
    assert (target_root / ".github" / "agents" / "ecosystem-audit.agent.md").is_file()
    assert (target_root / ".github" / "agents" / "governance-ecosystem-manifest.agent.md").is_file()
    assert (target_root / ".github" / "agents" / "governance-ecosystem-delivery.agent.md").is_file()
    assert (target_root / ".github" / "ecosystems" / "ecosystem-audit" / "audit" / "core-rules.md").is_file()
    assert (target_root / ".github" / "ecosystems" / "ecosystem-audit" / "audit" / "work-quality-rubric.md").is_file()
    assert (target_root / ".github" / "ecosystems" / "ecosystem-audit" / "assets" / "templates" / "audit-pack-template.md").is_file()
    assert (target_root / ".github" / "ecosystems" / "repository-governance" / "assets" / "templates").is_dir()
    installed_skill = (
        target_root
        / ".github"
        / "skills"
        / "repository-governance-bootstrap"
        / "SKILL.md"
    ).read_text(encoding="utf-8")
    assert "deliver_ecosystem.py" not in installed_skill
    assert "](../../ecosystems/validate_ecosystem_registry.sh)" not in installed_skill
    assert "validate_repository_governance.sh" not in installed_skill
    assert "Ecosystem Audit Agent" in installed_skill
    assert "../../agents/governance-ecosystem-delivery.agent.md" in installed_skill
    assert not (target_root / ".github" / "ecosystems" / "ecosystem_lib.py").exists()


def test_apply_delivery_changes_installs_actionable_validation_guidance(tmp_path) -> None:
    target_root = tmp_path / "target-repo"

    apply_delivery_changes(
        build_install_changeset(
            target_root=target_root,
            ecosystem_slug="repository-governance",
        )
    )

    manifest_agent = (
        target_root
        / ".github"
        / "agents"
        / "governance-ecosystem-manifest.agent.md"
    ).read_text(encoding="utf-8")
    context_agent = (
        target_root
        / ".github"
        / "agents"
        / "governance-repository-context-manager.agent.md"
    ).read_text(encoding="utf-8")
    bootstrap_skill = (
        target_root
        / ".github"
        / "skills"
        / "repository-governance-bootstrap"
        / "SKILL.md"
    ).read_text(encoding="utf-8")
    docs_skill = (
        target_root
        / ".github"
        / "skills"
        / "repository-doc-governance"
        / "SKILL.md"
    ).read_text(encoding="utf-8")

    manifest_agent_normalized = " ".join(manifest_agent.split())
    context_agent_normalized = " ".join(context_agent.split())
    bootstrap_skill_normalized = " ".join(bootstrap_skill.split())

    assert "Ecosystem Audit Agent" in manifest_agent
    assert "validate_ecosystem_registry.sh --repo-root ." not in manifest_agent
    assert "validate_repository_governance.sh" not in manifest_agent
    assert "Run the package validator" not in context_agent
    assert "Ecosystem Audit Agent" in context_agent
    assert ".github/ecosystems/repository-governance/assets/templates/<mode>" in context_agent
    assert "validate_ecosystem_registry.sh --repo-root ." not in context_agent
    assert "validate_repository_governance.sh" not in context_agent
    assert "Ecosystem Audit Agent" in bootstrap_skill
    assert "validate_ecosystem_registry.sh --repo-root ." not in bootstrap_skill
    assert "validate_repository_governance.sh" not in bootstrap_skill
    assert "canonical `docs/TODO.md` path used by the governance pack" in bootstrap_skill
    assert "bilingual or single-language mode" in bootstrap_skill_normalized
    assert "ecosystem registry validator" not in bootstrap_skill
    assert "another canonical path" not in bootstrap_skill
    assert "bootstrap output has been applied" in docs_skill
    assert "Ecosystem Audit Agent" in docs_skill
    assert ".github/ecosystems/repository-governance/assets/templates/<mode>" in docs_skill
    assert "validate_repository_governance.sh" not in docs_skill


def test_apply_delivery_changes_installs_codebase_context_payload(tmp_path) -> None:
    target_root = tmp_path / "target-repo"

    actions = apply_delivery_changes(
        build_install_changeset(
            target_root=target_root,
            ecosystem_slug="codebase-context",
        )
    )

    assert actions
    assert (target_root / ".github" / "agents" / "ecosystem-audit.agent.md").is_file()
    assert (target_root / ".github" / "agents" / "codebase-context.agent.md").is_file()
    assert (target_root / ".github" / "skills" / "codebase-context-export" / "SKILL.md").is_file()
    assert (
        target_root
        / ".github"
        / "ecosystems"
        / "ecosystem-audit"
        / "assets"
        / "smoke-scenarios"
        / "new-ecosystem-audit-smoke-scenario.md"
    ).is_file()
    assert (
        target_root
        / ".github"
        / "ecosystems"
        / "runtime_container_lib.sh"
    ).is_file()
    assert (
        target_root
        / ".github"
        / "ecosystems"
        / "codebase-context"
        / "audit"
        / "codebase-context-audit.md"
    ).is_file()
    assert (
        target_root
        / ".github"
        / "ecosystems"
        / "codebase-context"
        / "Dockerfile"
    ).is_file()
    assert (
        target_root
        / ".github"
        / "ecosystems"
        / "codebase-context"
        / "generate_codebase_context.py"
    ).is_file()
    assert (
        target_root
        / ".github"
        / "ecosystems"
        / "codebase-context"
        / "generate_codebase_context.sh"
    ).is_file()

    installed_skill = (
        target_root / ".github" / "skills" / "codebase-context-export" / "SKILL.md"
    ).read_text(encoding="utf-8")
    installed_wrapper = (
        target_root
        / ".github"
        / "ecosystems"
        / "codebase-context"
        / "generate_codebase_context.sh"
    )

    assert "../../ecosystems/codebase-context/generate_codebase_context.sh" in installed_skill
    assert "../../ecosystems/deliver_ecosystem.py" not in installed_skill
    assert os.access(installed_wrapper, os.X_OK)


def test_apply_delivery_changes_removes_codebase_context_manifest_owned_paths(tmp_path) -> None:
    target_root = tmp_path / "target-repo"

    apply_delivery_changes(
        build_install_changeset(
            target_root=target_root,
            ecosystem_slug="codebase-context",
        )
    )

    actions = apply_delivery_changes(
        build_remove_changeset(
            target_root=target_root,
            ecosystem_slug="codebase-context",
        )
    )

    assert actions
    assert not (target_root / ".github" / "agents" / "codebase-context.agent.md").exists()
    assert not (target_root / ".github" / "skills" / "codebase-context-export").exists()
    assert not (target_root / ".github" / "ecosystems" / "codebase-context").exists()
    assert not (target_root / ".github" / "ecosystems" / "runtime_container_lib.sh").exists()
    assert not (target_root / ".github" / "agents" / "ecosystem-audit.agent.md").exists()
    assert not (target_root / ".github" / "ecosystems" / "ecosystem-audit").exists()


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
    assert not (target_root / ".github" / "agents" / "ecosystem-audit.agent.md").exists()
    assert not (target_root / ".github" / "agents" / "governance-ecosystem-manifest.agent.md").exists()
    assert not (target_root / ".github" / "agents" / "governance-ecosystem-delivery.agent.md").exists()
    assert not (target_root / ".github" / "ecosystems" / "ecosystem-audit").exists()
    assert not (target_root / ".github" / "ecosystems" / "repository-governance").exists()
    assert preserved_file.read_text(encoding="utf-8") == "keep me\n"


def test_remove_preserves_shared_dependency_needed_by_other_installed_ecosystem(
    tmp_path,
) -> None:
    target_root = tmp_path / "target-repo"

    apply_delivery_changes(
        build_install_changeset(
            target_root=target_root,
            ecosystem_slug="repository-governance",
        )
    )
    apply_delivery_changes(
        build_install_changeset(
            target_root=target_root,
            ecosystem_slug="codebase-context",
        )
    )

    actions = apply_delivery_changes(
        build_remove_changeset(
            target_root=target_root,
            ecosystem_slug="repository-governance",
        )
    )

    assert actions
    assert not (target_root / ".github" / "ecosystems" / "repository-governance").exists()
    assert (target_root / ".github" / "ecosystems" / "ecosystem-audit").exists()
    assert (target_root / ".github" / "ecosystems" / "codebase-context").exists()


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
        ["ecosystem-audit", "repository-governance"],
        ["copy /tmp/target/.github/agents/governance-ecosystem-delivery.agent.md"],
    )

    assert "Ecosystem install" in body
    assert "repository-governance" in body
    assert "ecosystem-audit, repository-governance" in body
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
    assert result.resolved_ecosystems == ["ecosystem-audit", "repository-governance"]
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
    assert result.resolved_ecosystems == ["ecosystem-audit", "repository-governance"]
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