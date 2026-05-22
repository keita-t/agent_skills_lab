from __future__ import annotations

from pathlib import Path
import shutil

import validate_ecosystem_registry as ecosystem_registry_validator
import validate_repository_governance as repository_governance_validator


def test_ecosystem_registry_validator_passes_on_current_repository(
    repo_root: Path,
    invoke_main,
    capsys,
) -> None:
    exit_code = invoke_main(
        ecosystem_registry_validator,
        "--repo-root",
        str(repo_root),
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "ECOSYSTEM REGISTRY VALIDATION PASSED" in captured.out


def test_ecosystem_registry_validator_reports_missing_ecosystem_file(
    isolated_repo: Path,
    invoke_main,
    capsys,
) -> None:
    missing_file = (
        isolated_repo
        / ".github"
        / "ecosystems"
        / "repository-governance"
        / "validate_agent_skill_docs.sh"
    )
    missing_file.unlink()

    exit_code = invoke_main(
        ecosystem_registry_validator,
        "--repo-root",
        str(isolated_repo),
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "references missing ecosystem file" in captured.out


def test_repository_governance_validator_passes_for_bilingual_templates(
    repo_root: Path,
    invoke_main,
    capsys,
) -> None:
    template_root = (
        repo_root
        / ".github"
        / "ecosystems"
        / "repository-governance"
        / "assets"
        / "templates"
        / "bilingual"
    )

    exit_code = invoke_main(
        repository_governance_validator,
        "--repo-root",
        str(template_root),
        "--mode",
        "bilingual",
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "REPOSITORY GOVERNANCE VALIDATION PASSED" in captured.out


def test_project_charter_templates_default_to_minimal_content(repo_root: Path) -> None:
    charter_paths = [
        repo_root / "docs" / "en" / "project-charter.md",
        repo_root
        / ".github"
        / "ecosystems"
        / "repository-governance"
        / "assets"
        / "templates"
        / "bilingual"
        / "docs"
        / "en"
        / "project-charter.md",
        repo_root
        / ".github"
        / "ecosystems"
        / "repository-governance"
        / "assets"
        / "templates"
        / "single-language"
        / "docs"
        / "project-charter.md",
    ]

    for charter_path in charter_paths:
        text = charter_path.read_text(encoding="utf-8")
        assert "intentionally minimal" in text
        assert "generic engineering rules" in text
        assert "shared rule set" not in text
        assert "project-wide engineering rules" not in text

    rules_paths = [
        repo_root / "docs" / "DOCUMENTATION_UPDATE_RULES.md",
        repo_root
        / ".github"
        / "ecosystems"
        / "repository-governance"
        / "assets"
        / "templates"
        / "bilingual"
        / "docs"
        / "DOCUMENTATION_UPDATE_RULES.md",
        repo_root
        / ".github"
        / "ecosystems"
        / "repository-governance"
        / "assets"
        / "templates"
        / "single-language"
        / "docs"
        / "DOCUMENTATION_UPDATE_RULES.md",
    ]

    for rules_path in rules_paths:
        text = rules_path.read_text(encoding="utf-8")
        normalized_text = " ".join(text.split())
        assert (
            "repository-specific scope, terminology, and explicit maintainer decisions"
            in normalized_text
        )
        assert "higher-level engineering policy" not in text
        assert "Project-wide engineering rules." not in text


def test_agent_skill_docs_validator_reports_missing_skill_entry(
    isolated_repo: Path,
    load_module_from_path,
    capsys,
) -> None:
    skills_readme = isolated_repo / ".github" / "skills" / "README.md"
    text = skills_readme.read_text(encoding="utf-8")
    skills_readme.write_text(
        text.replace(
            "- [todo-progress-governance](todo-progress-governance/SKILL.md): Maintains\n  backlog and design-review tracking files under explicit routine-vs-structural\n  editing rules.\n",
            "",
        ),
        encoding="utf-8",
    )

    validator_module = load_module_from_path(
        "temp_validate_agent_skill_docs",
        isolated_repo
        / ".github"
        / "ecosystems"
        / "repository-governance"
        / "validate_agent_skill_docs.py",
    )

    exit_code = validator_module.main()

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "skills/README.md is missing skill entries" in captured.out


def test_repository_governance_validator_rejects_extra_root_reference_doc_in_bilingual_mode(
    repo_root: Path,
    tmp_path: Path,
    invoke_main,
    capsys,
) -> None:
    template_root = (
        repo_root
        / ".github"
        / "ecosystems"
        / "repository-governance"
        / "assets"
        / "templates"
        / "bilingual"
    )
    working_copy = tmp_path / "bilingual-template"
    shutil.copytree(template_root, working_copy)

    (working_copy / "docs" / "extra-reference.md").write_text(
        "# Extra Reference\n",
        encoding="utf-8",
    )

    exit_code = invoke_main(
        repository_governance_validator,
        "--repo-root",
        str(working_copy),
        "--mode",
        "bilingual",
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "root-level docs file is not allowed in bilingual mode" in captured.out


def test_repository_governance_validator_rejects_unpaired_language_specific_doc(
    repo_root: Path,
    tmp_path: Path,
    invoke_main,
    capsys,
) -> None:
    template_root = (
        repo_root
        / ".github"
        / "ecosystems"
        / "repository-governance"
        / "assets"
        / "templates"
        / "bilingual"
    )
    working_copy = tmp_path / "bilingual-template"
    shutil.copytree(template_root, working_copy)

    (working_copy / "docs" / "en" / "mcp-tools.md").write_text(
        "# MCP Tools\n",
        encoding="utf-8",
    )

    exit_code = invoke_main(
        repository_governance_validator,
        "--repo-root",
        str(working_copy),
        "--mode",
        "bilingual",
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "missing Japanese counterpart" in captured.out