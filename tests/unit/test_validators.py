from __future__ import annotations

from pathlib import Path

from ecosystem_lib import load_ecosystem_manifest, manifest_owned_relative_paths


def test_no_legacy_github_ecosystems_references_remain(repo_root: Path) -> None:
    ignored_directories = {".git", ".pytest_cache", ".tmp", "__pycache__"}
    offenders: list[str] = []
    legacy_path = ".github" + "/ecosystems"

    for path in repo_root.rglob("*"):
        if any(part in ignored_directories for part in path.parts):
            continue
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if legacy_path in text:
            offenders.append(str(path.relative_to(repo_root)))

    assert offenders == []


def test_no_non_hidden_ecosystem_directory_references_remain(repo_root: Path) -> None:
    ignored_directories = {".git", ".pytest_cache", ".tmp", "__pycache__"}
    offenders: list[str] = []
    old_directory = "ai" + "_ecosystems"
    hidden_directory = "." + old_directory

    assert not (repo_root / old_directory).exists()

    for path in repo_root.rglob("*"):
        if any(part in ignored_directories for part in path.parts):
            continue
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if old_directory in text.replace(hidden_directory, ""):
            offenders.append(str(path.relative_to(repo_root)))

    assert offenders == []


def test_legacy_validator_files_are_removed(repo_root: Path) -> None:
    assert not (repo_root / ".github" / "ecosystems").exists()
    retired_paths = [
        repo_root / ".ai_ecosystems" / "validate_ecosystem_registry.py",
        repo_root / ".ai_ecosystems" / "validate_ecosystem_registry.sh",
        repo_root / ".ai_ecosystems" / "ecosystem_registry_validation_service.py",
        repo_root
        / ".ai_ecosystems"
        / "repository-docs"
        / "validate_repository_docs.py",
        repo_root
        / ".ai_ecosystems"
        / "repository-docs"
        / "validate_repository_docs.sh",
    ]

    for path in retired_paths:
        assert not path.exists()


def test_ecosystem_audit_manifest_ships_template_and_smoke_assets(repo_root: Path) -> None:
    manifest_path = (
        repo_root
        / ".ai_ecosystems"
        / "ecosystem-audit"
        / "ECOSYSTEM.md"
    )

    manifest = load_ecosystem_manifest(manifest_path)
    relative_paths = manifest_owned_relative_paths(manifest)

    assert ".ai_ecosystems/ecosystem-audit/assets/templates" in manifest.ecosystem_files
    assert ".ai_ecosystems/ecosystem-audit/assets/smoke-scenarios" in manifest.ecosystem_files
    assert ".ai_ecosystems/ecosystem-audit/audit/core-rules.md" in relative_paths
    assert ".ai_ecosystems/ecosystem-audit/audit/report-contract.md" in relative_paths
    assert ".ai_ecosystems/ecosystem-audit/audit/work-quality-rubric.md" in relative_paths
    assert ".ai_ecosystems/ecosystem-audit/assets/templates" in relative_paths
    assert ".ai_ecosystems/ecosystem-audit/assets/smoke-scenarios" in relative_paths


def test_shared_work_quality_rubric_defines_qualitative_scale(repo_root: Path) -> None:
    rubric_path = (
        repo_root
        / ".ai_ecosystems"
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
        / ".ai_ecosystems"
        / "ecosystem-audit"
        / "assets"
        / "templates"
        / "audit-pack-template.md"
    )
    text = template_path.read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "audit-files" in text
    assert ".ai_ecosystems/<slug>/audit/" in text
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
        / ".ai_ecosystems"
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
        / ".ai_ecosystems"
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
        repo_root / ".ai_ecosystems" / "README.md",
        repo_root / "docs" / "en" / "ecosystems.md",
        repo_root / "docs" / "ja" / "ecosystems.ja.md",
    ]

    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert "validate_ecosystem_registry.sh" not in text
        assert "validate_repository_docs.sh" not in text
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
        / ".ai_ecosystems"
        / "repository-docs"
        / "audit"
        / "repository-docs-audit.md",
        repo_root
        / ".ai_ecosystems"
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


def test_repository_docs_audit_pack_covers_single_language_ubiquitous_language_doc(
    repo_root: Path,
) -> None:
    audit_path = (
        repo_root
        / ".ai_ecosystems"
        / "repository-docs"
        / "audit"
        / "repository-docs-audit.md"
    )
    text = audit_path.read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "docs/ubiquitous-language.md" in text
    assert "In single-language mode this includes" in normalized
    assert "codebase-alignment" in text
    assert "refactoring-behavior" in text
    assert "diagram-fit" in text


def test_repository_doc_refactoring_skill_covers_codebase_and_diagram_cleanup(
    repo_root: Path,
) -> None:
    skill_path = (
        repo_root
        / ".ai_ecosystems"
        / "repository-docs"
        / "skills"
        / "docs-refactor"
        / "SKILL.md"
    )
    text = skill_path.read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "codebase" in text
    assert "implementation-log" in text
    assert "mechanical" in text
    assert "Mermaid diagram" in text
    assert "ASCII diagrams" in text
    assert "Build a short crosswalk" in normalized


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
    assert "documentation refactoring" in en_text
    assert "work-quality audit" in ja_text
    assert "installed runtime contract" in ja_text
    assert "runtime launcher" in ja_text
    assert "runtime container" in ja_text
    assert "rubric summary" in ja_text
    assert "evidence basis" in ja_text
    assert "upstream improvement feedback" in ja_text
    assert "documentation refactoring" in ja_text
