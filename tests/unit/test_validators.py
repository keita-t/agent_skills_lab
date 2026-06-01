from __future__ import annotations

import os
from pathlib import Path

from ecosystem_lib import load_ecosystem_manifest, manifest_owned_relative_paths


def test_legacy_validator_files_are_removed(repo_root: Path) -> None:
    retired_paths = [
        repo_root / ".github" / "ecosystems" / "validate_ecosystem_registry.py",
        repo_root / ".github" / "ecosystems" / "validate_ecosystem_registry.sh",
        repo_root / ".github" / "ecosystems" / "ecosystem_registry_validation_service.py",
        repo_root
        / ".github"
        / "ecosystems"
        / "repository-governance"
        / "validate_repository_governance.py",
        repo_root
        / ".github"
        / "ecosystems"
        / "repository-governance"
        / "validate_repository_governance.sh",
    ]

    for path in retired_paths:
        assert not path.exists()


def test_ecosystem_audit_manifest_ships_template_and_smoke_assets(repo_root: Path) -> None:
    manifest_path = (
        repo_root
        / ".github"
        / "ecosystems"
        / "ecosystem-audit"
        / "ECOSYSTEM.md"
    )

    manifest = load_ecosystem_manifest(manifest_path)
    relative_paths = manifest_owned_relative_paths(manifest)

    assert ".github/ecosystems/ecosystem-audit/assets/templates" in manifest.ecosystem_files
    assert ".github/ecosystems/ecosystem-audit/assets/smoke-scenarios" in manifest.ecosystem_files
    assert ".github/ecosystems/ecosystem-audit/audit/core-rules.md" in relative_paths
    assert ".github/ecosystems/ecosystem-audit/audit/report-contract.md" in relative_paths
    assert ".github/ecosystems/ecosystem-audit/audit/work-quality-rubric.md" in relative_paths
    assert ".github/ecosystems/ecosystem-audit/assets/templates" in relative_paths
    assert ".github/ecosystems/ecosystem-audit/assets/smoke-scenarios" in relative_paths


def test_shared_work_quality_rubric_defines_qualitative_scale(repo_root: Path) -> None:
    rubric_path = (
        repo_root
        / ".github"
        / "ecosystems"
        / "ecosystem-audit"
        / "audit"
        / "work-quality-rubric.md"
    )
    text = rubric_path.read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "Strong" in text
    assert "Acceptable" in text
    assert "Needs Work" in text
    assert "Not Assessed" in text
    assert "artifact-observed" in text
    assert "runtime-observed" in text
    assert "definition-inferred" in text
    assert "Do not collapse the rubric into a single aggregate score" in normalized


def test_audit_pack_template_explains_manifest_owned_extension_contract(
    repo_root: Path,
) -> None:
    template_path = (
        repo_root
        / ".github"
        / "ecosystems"
        / "ecosystem-audit"
        / "assets"
        / "templates"
        / "audit-pack-template.md"
    )
    text = template_path.read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "audit-files" in text
    assert ".github/ecosystems/<slug>/audit/" in text
    assert "manifest-owned payload" in normalized
    assert "shared `ecosystem-audit` platform" in text
    assert "runtime output" in normalized
    assert "Artifact Quality Rubric" in text
    assert "Behavior Quality Rubric" in text
    assert "numeric scores" in text


def test_new_ecosystem_smoke_scenario_covers_source_and_target_audit(
    repo_root: Path,
) -> None:
    scenario_path = (
        repo_root
        / ".github"
        / "ecosystems"
        / "ecosystem-audit"
        / "assets"
        / "smoke-scenarios"
        / "new-ecosystem-audit-smoke-scenario.md"
    )
    text = scenario_path.read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "Source Repository Smoke" in text
    assert "Installed Target Repository Smoke" in text
    assert "broken `root-agent`" in text
    assert "Ecosystem Audit Agent" in text
    assert "Shared core rules report source-repository structural defects" in normalized
    assert "ecosystem-specific audit pack reports at least one installed-target defect" in normalized
    assert "definition-inferred" in text
    assert "rubric summary" in normalized
    assert "upstream improvement feedback" in normalized


def test_report_contract_supports_rubric_first_quality_output(repo_root: Path) -> None:
    contract_path = (
        repo_root
        / ".github"
        / "ecosystems"
        / "ecosystem-audit"
        / "audit"
        / "report-contract.md"
    )
    text = contract_path.read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "Rubric Summary" in text
    assert "Evidence basis" in text
    assert "Confidence" in text
    assert "Improvement feedback" in text
    assert "local-fix" in text
    assert "upstream-ecosystem-feedback" in text
    assert "Do not require a single aggregate quality score" in normalized


def test_repository_docs_no_longer_reference_retired_validators(repo_root: Path) -> None:
    paths = [
        repo_root / "README.md",
        repo_root / ".github" / "ecosystems" / "README.md",
        repo_root / "docs" / "en" / "ecosystems.md",
        repo_root / "docs" / "ja" / "ecosystems.ja.md",
    ]

    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert "validate_ecosystem_registry.sh" not in text
        assert "validate_repository_governance.sh" not in text
def test_ecosystem_docs_include_rubric_first_audit_report_example(repo_root: Path) -> None:
    docs_en_text = (repo_root / "docs" / "en" / "ecosystems.md").read_text(encoding="utf-8")
    docs_ja_text = (repo_root / "docs" / "ja" / "ecosystems.ja.md").read_text(encoding="utf-8")

    assert "Example Audit Report" in docs_en_text
    assert "Rubric summary" in docs_en_text
    assert "upstream-ecosystem-feedback" in docs_en_text
    assert "artifact-observed" in docs_en_text
    assert "definition-inferred" in docs_en_text
    assert "監査レポート例" in docs_ja_text
    assert "Rubric summary" in docs_ja_text
    assert "upstream-ecosystem-feedback" in docs_ja_text
    assert "artifact-observed" in docs_ja_text
    assert "definition-inferred" in docs_ja_text


def test_ecosystem_audit_packs_define_quality_rubrics(repo_root: Path) -> None:
    paths = [
        repo_root
        / ".github"
        / "ecosystems"
        / "repository-governance"
        / "audit"
        / "repository-governance-audit.md",
        repo_root
        / ".github"
        / "ecosystems"
        / "codebase-context"
        / "audit"
        / "codebase-context-audit.md",
    ]
    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert "Artifact Quality Rubric" in text
        assert "Behavior Quality Rubric" in text
        assert "Evidence Sources" in text
        assert "Upstream Improvement Feedback" in text


def test_repository_governance_audit_pack_covers_single_language_ubiquitous_language_doc(
    repo_root: Path,
) -> None:
    audit_path = (
        repo_root
        / ".github"
        / "ecosystems"
        / "repository-governance"
        / "audit"
        / "repository-governance-audit.md"
    )
    text = audit_path.read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "docs/ubiquitous-language.md" in text
    assert "In single-language mode this includes" in normalized


def test_ubiquitous_language_tracks_quality_audit_terms(repo_root: Path) -> None:
    en_text = (repo_root / "docs" / "en" / "ubiquitous-language.md").read_text(encoding="utf-8")
    ja_text = (repo_root / "docs" / "ja" / "ubiquitous-language.ja.md").read_text(encoding="utf-8")

    assert "work-quality audit" in en_text
    assert "installed runtime contract" in en_text
    assert "runtime launcher" in en_text
    assert "runtime container" in en_text
    assert "rubric summary" in en_text
    assert "evidence basis" in en_text
    assert "upstream improvement feedback" in en_text
    assert "work-quality audit" in ja_text
    assert "installed runtime contract" in ja_text
    assert "runtime launcher" in ja_text
    assert "runtime container" in ja_text
    assert "rubric summary" in ja_text
    assert "evidence basis" in ja_text
    assert "upstream improvement feedback" in ja_text


def test_codebase_context_sandbox_container_assets_are_documented(repo_root: Path) -> None:
    runner_path = repo_root / "tests" / "sandbox" / "run_codebase_context_container_smoke.sh"
    dockerfile_path = repo_root / "tests" / "sandbox" / "base" / "Dockerfile"
    runner_text = runner_path.read_text(encoding="utf-8")
    readme_text = (repo_root / "README.md").read_text(encoding="utf-8")
    platform_text = (repo_root / ".github" / "ecosystems" / "README.md").read_text(encoding="utf-8")
    docs_en_text = (repo_root / "docs" / "en" / "ecosystems.md").read_text(encoding="utf-8")
    docs_ja_text = (repo_root / "docs" / "ja" / "ecosystems.ja.md").read_text(encoding="utf-8")
    ubiq_en_text = (repo_root / "docs" / "en" / "ubiquitous-language.md").read_text(encoding="utf-8")
    ubiq_ja_text = (repo_root / "docs" / "ja" / "ubiquitous-language.ja.md").read_text(encoding="utf-8")

    assert dockerfile_path.is_file()
    assert runner_path.is_file()
    assert os.access(runner_path, os.X_OK)
    assert "docker build" in runner_text
    assert "generate_codebase_context.sh" in runner_text
    assert "tests/sandbox/base/Dockerfile" not in readme_text or "base/Dockerfile" in readme_text
    assert "run_codebase_context_container_smoke.sh" in readme_text
    assert "runtime launcher" in readme_text
    assert "runtime container" in readme_text
    assert "base/Dockerfile" in readme_text
    assert "runtime-mode" in readme_text
    assert "runtime-entrypoint" in platform_text
    assert "shared-ownership-files" in platform_text
    assert "runtime_container_lib.sh" in platform_text
    assert "run_codebase_context_container_smoke.sh" in docs_en_text
    assert "Installed Runtime Contract" in docs_en_text
    assert "shared-ownership-files" in docs_en_text
    assert "runtime launcher" in docs_en_text
    assert "runtime container" in docs_en_text
    assert "runtime_container_lib.sh" in docs_en_text
    assert "base/Dockerfile" in docs_en_text
    assert "run_codebase_context_container_smoke.sh" in docs_ja_text
    assert "Installed Runtime Contract" in docs_ja_text
    assert "shared-ownership-files" in docs_ja_text
    assert "runtime launcher" in docs_ja_text
    assert "runtime container" in docs_ja_text
    assert "runtime_container_lib.sh" in docs_ja_text
    assert "base/Dockerfile" in docs_ja_text
    assert "sandbox smoke" in ubiq_en_text
    assert "sandbox smoke" in ubiq_ja_text


def test_repository_governance_sandbox_assets_and_ci_are_documented(repo_root: Path) -> None:
    runner_path = (
        repo_root / "tests" / "sandbox" / "run_repository_governance_container_smoke.sh"
    )
    dockerfile_path = repo_root / "tests" / "sandbox" / "base" / "Dockerfile"
    workflow_path = repo_root / ".github" / "workflows" / "ci.yml"
    runner_text = runner_path.read_text(encoding="utf-8")
    workflow_text = workflow_path.read_text(encoding="utf-8")
    readme_text = (repo_root / "README.md").read_text(encoding="utf-8")
    docs_en_text = (repo_root / "docs" / "en" / "ecosystems.md").read_text(encoding="utf-8")
    docs_ja_text = (repo_root / "docs" / "ja" / "ecosystems.ja.md").read_text(encoding="utf-8")

    assert dockerfile_path.is_file()
    assert runner_path.is_file()
    assert workflow_path.is_file()
    assert os.access(runner_path, os.X_OK)
    assert "docker build" in runner_text
    assert "test_repository_governance_installed_smoke.py" in runner_text
    assert "python -m pytest -q" in workflow_text
    assert "run_codebase_context_container_smoke.sh" in workflow_text
    assert "run_repository_governance_container_smoke.sh" in workflow_text
    assert "run_repository_governance_container_smoke.sh" in readme_text
    assert "base/Dockerfile" in readme_text
    assert ".github/workflows/ci.yml" in readme_text
    assert "GitHub Actions CI" in readme_text
    assert "run_repository_governance_container_smoke.sh" in docs_en_text
    assert "base/Dockerfile" in docs_en_text
    assert ".github/workflows/ci.yml" in docs_en_text
    assert "run_repository_governance_container_smoke.sh" in docs_ja_text
    assert "base/Dockerfile" in docs_ja_text
    assert ".github/workflows/ci.yml" in docs_ja_text
