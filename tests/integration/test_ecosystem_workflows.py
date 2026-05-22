from __future__ import annotations

from pathlib import Path

import install_ecosystem
import update_ecosystem_core_files
import validate_repository_governance as repository_governance_validator


def test_updater_is_idempotent_for_installed_ecosystems(
    isolated_repo: Path,
    invoke_main,
) -> None:
    first_exit = invoke_main(
        update_ecosystem_core_files,
        "--target-repo",
        str(isolated_repo),
    )
    assert first_exit == 0

    routing_path = isolated_repo / ".github" / "AGENT_SKILL_ROUTING.md"
    first_render = routing_path.read_text(encoding="utf-8")

    second_exit = invoke_main(
        update_ecosystem_core_files,
        "--target-repo",
        str(isolated_repo),
    )
    assert second_exit == 0

    second_render = routing_path.read_text(encoding="utf-8")
    assert first_render == second_render
    assert "<!-- BEGIN ECOSYSTEM MANAGED BLOCK -->" in second_render


def test_installer_rejects_same_source_and_target_repo(
    repo_root: Path,
    invoke_main,
    capsys,
) -> None:
    exit_code = invoke_main(
        install_ecosystem,
        "--target-repo",
        str(repo_root),
        "--ecosystem",
        "repository-governance",
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "controlled self-host bootstrap" in captured.out


def test_installer_populates_blank_repository(
    blank_repo: Path,
    invoke_main,
) -> None:
    exit_code = invoke_main(
        install_ecosystem,
        "--target-repo",
        str(blank_repo),
        "--ecosystem",
        "repository-governance",
        "--merge-strategy",
        "merge",
    )

    assert exit_code == 0
    assert (
        blank_repo
        / ".github"
        / "ecosystems"
        / "repository-governance"
        / "ECOSYSTEM.md"
    ).is_file()
    assert (blank_repo / ".github" / "ECOSYSTEM_REGISTRY.md").is_file()
    assert (blank_repo / ".github" / "skills" / "repository-governance-bootstrap").is_dir()


def test_installer_dry_run_leaves_blank_repository_untouched(
    blank_repo: Path,
    invoke_main,
) -> None:
    exit_code = invoke_main(
        install_ecosystem,
        "--target-repo",
        str(blank_repo),
        "--ecosystem",
        "repository-governance",
        "--dry-run",
    )

    assert exit_code == 0
    assert not (blank_repo / ".github").exists()


def test_current_repository_self_host_docs_validate_in_bilingual_mode(
    repo_root: Path,
    invoke_main,
    capsys,
) -> None:
    exit_code = invoke_main(
        repository_governance_validator,
        "--repo-root",
        str(repo_root),
        "--mode",
        "bilingual",
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "REPOSITORY GOVERNANCE VALIDATION PASSED" in captured.out