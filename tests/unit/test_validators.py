from __future__ import annotations

import importlib.util
from pathlib import Path
import shutil
import sys
import types
import pytest

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
        / "validate_repository_governance.sh"
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


def test_ecosystem_registry_validator_allows_missing_metadata_docs(
    isolated_repo: Path,
    invoke_main,
    capsys,
) -> None:
    removable_paths = [
        isolated_repo / ".github" / "ECOSYSTEM_REGISTRY.md",
        isolated_repo / ".github" / "AGENT_SKILL_ROUTING.md",
        isolated_repo / ".github" / "agents" / "README.md",
        isolated_repo / ".github" / "skills" / "README.md",
        isolated_repo / ".github" / "ecosystems" / "README.md",
    ]
    for path in removable_paths:
        if path.exists():
            path.unlink()

    exit_code = invoke_main(
        ecosystem_registry_validator,
        "--repo-root",
        str(isolated_repo),
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "ECOSYSTEM REGISTRY VALIDATION PASSED" in captured.out


def test_ecosystem_registry_validator_rejects_source_only_link_in_installable_markdown(
    isolated_repo: Path,
    invoke_main,
    capsys,
) -> None:
    skill_path = (
        isolated_repo
        / ".github"
        / "skills"
        / "repository-governance-bootstrap"
        / "SKILL.md"
    )
    skill_path.write_text(
        skill_path.read_text(encoding="utf-8")
        + "\nSource-only link: [deliver](../../ecosystems/deliver_ecosystem.py)\n",
        encoding="utf-8",
    )

    exit_code = invoke_main(
        ecosystem_registry_validator,
        "--repo-root",
        str(isolated_repo),
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "links outside its manifest-owned payload" in captured.out
    assert ".github/ecosystems/deliver_ecosystem.py" in captured.out


def test_ecosystem_registry_validator_applies_portability_rule_to_any_installable_ecosystem(
    isolated_repo: Path,
    invoke_main,
    capsys,
) -> None:
    manifest_dir = isolated_repo / ".github" / "ecosystems" / "demo-installable"
    manifest_dir.mkdir(parents=True)
    (manifest_dir / "ECOSYSTEM.md").write_text(
        """---
slug: demo-installable
name: Demo Installable
description: Synthetic ecosystem for validator regression coverage.
status: active
root-agent: demo-root.agent.md
agents: [demo-root.agent.md]
skills: [demo-skill]
dependencies: []
ecosystem-files: []
---

# Demo Installable
""",
        encoding="utf-8",
    )

    (isolated_repo / ".github" / "agents" / "demo-root.agent.md").write_text(
        """---
name: Demo Root
description: Synthetic root agent.
ecosystem: demo-installable
tools: [read]
---

# Demo Root
""",
        encoding="utf-8",
    )

    skill_dir = isolated_repo / ".github" / "skills" / "demo-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        """---
name: demo-skill
description: Synthetic installable skill.
ecosystem: demo-installable
argument-hint: Demo.
---

# Demo Skill

Source-only link: [deliver](../../ecosystems/deliver_ecosystem.py)
""",
        encoding="utf-8",
    )

    exit_code = invoke_main(
        ecosystem_registry_validator,
        "--repo-root",
        str(isolated_repo),
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert ".github/skills/demo-skill/SKILL.md" in captured.out
    assert "links outside its manifest-owned payload" in captured.out
    assert ".github/ecosystems/deliver_ecosystem.py" in captured.out


def test_ecosystem_registry_validation_service_uses_local_models_even_if_mcp_models_exists(
    repo_root: Path,
    monkeypatch,
) -> None:
    fake_mcp_models = types.ModuleType("mcp_models")
    fake_mcp_models.ValidateRegistryInput = type("ValidateRegistryInput", (), {})
    fake_mcp_models.ValidationIssue = type("ValidationIssue", (), {})
    fake_mcp_models.ValidationResult = type("ValidationResult", (), {})
    monkeypatch.setitem(sys.modules, "mcp_models", fake_mcp_models)

    module_path = (
        repo_root
        / ".github"
        / "ecosystems"
        / "ecosystem_registry_validation_service.py"
    )
    module_name = "ecosystem_registry_validation_service_local_models_test"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, module_name, module)
    spec.loader.exec_module(module)

    assert module.ValidateRegistryInput.__module__ == module.__name__
    assert module.ValidationIssue.__module__ == module.__name__
    assert module.ValidationResult.__module__ == module.__name__


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


def test_repository_governance_validator_normalizes_equivalent_relative_required_links(
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
    working_copy = tmp_path / "bilingual-template-normalized-links"
    shutil.copytree(template_root, working_copy)

    rules_path = working_copy / "docs" / "DOCUMENTATION_UPDATE_RULES.md"
    rules_path.write_text(
        rules_path.read_text(encoding="utf-8").replace("(./README.md)", "(README.md)"),
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
    assert exit_code == 0
    assert "REPOSITORY GOVERNANCE VALIDATION PASSED" in captured.out


def test_repository_governance_validator_reports_invalid_repo_root(
    tmp_path: Path,
    invoke_main,
    capsys,
) -> None:
    missing_root = tmp_path / "missing-repo-root"

    exit_code = invoke_main(
        repository_governance_validator,
        "--repo-root",
        str(missing_root),
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Repository root does not exist or is not a directory" in captured.out


def test_repository_governance_validator_rejects_unknown_mode_as_library_call(
    blank_repo: Path,
) -> None:
    with pytest.raises(ValueError, match="Unsupported repository-governance mode"):
        repository_governance_validator.validate_repository_governance(
            repository_governance_validator.ValidateRepositoryGovernanceInput(
                repo_root=str(blank_repo),
                mode="unexpected-mode",
            )
        )


def test_repository_governance_validator_missing_required_file_includes_layout_hint(
    blank_repo: Path,
    invoke_main,
    capsys,
) -> None:
    exit_code = invoke_main(
        repository_governance_validator,
        "--repo-root",
        str(blank_repo),
        "--mode",
        "bilingual",
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Install the governance doc pack first" in captured.out
    assert ".github/ecosystems/repository-governance/assets/templates/bilingual" in captured.out


def test_repository_governance_validator_uses_local_models_even_if_mcp_models_exists(
    repo_root: Path,
    monkeypatch,
) -> None:
    fake_mcp_models = types.ModuleType("mcp_models")
    fake_mcp_models.ValidateRepositoryGovernanceInput = type(
        "ValidateRepositoryGovernanceInput",
        (),
        {},
    )
    fake_mcp_models.ValidationIssue = type("ValidationIssue", (), {})
    fake_mcp_models.ValidationResult = type("ValidationResult", (), {})
    monkeypatch.setitem(sys.modules, "mcp_models", fake_mcp_models)

    module_path = (
        repo_root
        / ".github"
        / "ecosystems"
        / "repository-governance"
        / "validate_repository_governance.py"
    )
    module_name = "validate_repository_governance_local_models_test"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, module_name, module)
    spec.loader.exec_module(module)

    assert module.ValidateRepositoryGovernanceInput.__module__ == module.__name__
    assert module.ValidationIssue.__module__ == module.__name__
    assert module.ValidationResult.__module__ == module.__name__


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

    (working_copy / "docs" / "en" / "delivery-workflows.md").write_text(
        "# Delivery Workflows\n",
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