from __future__ import annotations

from pathlib import Path
import re
import shutil
import subprocess

import pytest

from ecosystem_delivery_service import apply_delivery_changes, build_install_changeset


MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def init_git_repo(path: Path) -> None:
    git_path = shutil.which("git")
    if git_path is None:
        pytest.skip("git is required for this test")
    subprocess.run([git_path, "init", "-q", str(path)], check=True, capture_output=True)


def install_repository_governance(target_root: Path) -> None:
    apply_delivery_changes(
        build_install_changeset(
            target_root=target_root,
            ecosystem_slug="repository-governance",
        )
    )


def apply_bilingual_template_pack(target_root: Path) -> None:
    template_root = (
        target_root
        / ".ai_ecosystems"
        / "repository-governance"
        / "assets"
        / "templates"
        / "bilingual"
    )
    assert template_root.is_dir()

    shutil.copy2(template_root / "README.md", target_root / "README.md")
    shutil.copy2(template_root / "CLAUDE.md", target_root / "CLAUDE.md")
    shutil.copytree(template_root / "docs", target_root / "docs", dirs_exist_ok=True)


def assert_relative_markdown_links_resolve(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    for target in MARKDOWN_LINK_RE.findall(text):
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        target_path = target.split("#", 1)[0]
        if not target_path:
            continue
        resolved = (path.parent / target_path).resolve()
        assert resolved.exists(), f"Broken markdown link in {path}: {target}"


@pytest.mark.integration
def test_installed_repository_governance_bilingual_template_pack_bootstraps_target_repo(
    tmp_path: Path,
) -> None:
    target_root = tmp_path / "target-repo"
    target_root.mkdir()
    init_git_repo(target_root)

    install_repository_governance(target_root)
    apply_bilingual_template_pack(target_root)

    required_paths = [
        target_root / "README.md",
        target_root / "CLAUDE.md",
        target_root / "docs" / "README.md",
        target_root / "docs" / "DOCUMENTATION_UPDATE_RULES.md",
        target_root / "docs" / "TODO.md",
        target_root / "docs" / "en" / "project-charter.md",
        target_root / "docs" / "en" / "ubiquitous-language.md",
        target_root / "docs" / "ja" / "project-charter.ja.md",
        target_root / "docs" / "ja" / "ubiquitous-language.ja.md",
    ]

    for path in required_paths:
        assert path.is_file()

    readme_text = (target_root / "README.md").read_text(encoding="utf-8")
    claude_text = (target_root / "CLAUDE.md").read_text(encoding="utf-8")
    bootstrap_skill = (
        target_root
        / ".github"
        / "skills"
        / "repository-governance-bootstrap"
        / "SKILL.md"
    ).read_text(encoding="utf-8")

    assert "docs/README.md" in readme_text
    assert "docs/DOCUMENTATION_UPDATE_RULES.md" in claude_text
    assert "Ecosystem Audit Agent" in bootstrap_skill
    assert "assets/templates/bilingual/README.md" in bootstrap_skill

    for path in required_paths[:5]:
        assert_relative_markdown_links_resolve(path)
