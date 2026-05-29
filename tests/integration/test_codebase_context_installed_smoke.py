from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess

import pytest

from ecosystem_delivery_service import apply_delivery_changes, build_install_changeset


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def init_git_repo(path: Path) -> None:
    git_path = shutil.which("git")
    if git_path is None:
        pytest.skip("git is required for this test")
    subprocess.run([git_path, "init", "-q", str(path)], check=True, capture_output=True)


def install_codebase_context(target_root: Path) -> None:
    apply_delivery_changes(
        build_install_changeset(
            target_root=target_root,
            ecosystem_slug="codebase-context",
        )
    )


def installed_wrapper_path(target_root: Path) -> Path:
    return (
        target_root
        / ".github"
        / "ecosystems"
        / "codebase-context"
        / "generate_codebase_context.sh"
    )


def run_installed_wrapper(target_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    wrapper = installed_wrapper_path(target_root)
    assert os.access(wrapper, os.X_OK)
    return subprocess.run(
        [str(wrapper), "--repo-root", str(target_root), *args],
        cwd=target_root,
        check=False,
        capture_output=True,
        text=True,
    )


@pytest.mark.integration
def test_installed_codebase_context_wrapper_runs_directly_for_narrow_scope(
    tmp_path: Path,
) -> None:
    target_root = tmp_path / "target-repo"
    target_root.mkdir()
    init_git_repo(target_root)
    write_text(target_root / "src" / "main.py", "print('main')\n")
    write_text(target_root / "src" / "internal" / "skip.py", "print('skip')\n")
    write_text(target_root / "README.md", "# Sandbox\n")

    install_codebase_context(target_root)

    result = run_installed_wrapper(
        target_root,
        "--include",
        "src/**",
        "--exclude",
        "src/internal/**",
        "--output",
        "narrow.md",
    )

    assert result.returncode == 0, result.stderr

    output = (target_root / "narrow.md").read_text(encoding="utf-8")

    assert "### src/main.py" in output
    assert "### src/internal/skip.py" not in output
    assert "### README.md" not in output


@pytest.mark.integration
def test_installed_codebase_context_wrapper_reports_empty_scope_failure(
    tmp_path: Path,
) -> None:
    target_root = tmp_path / "target-repo"
    target_root.mkdir()
    init_git_repo(target_root)
    write_text(target_root / "src" / "main.py", "print('main')\n")

    install_codebase_context(target_root)

    result = run_installed_wrapper(
        target_root,
        "--include",
        "missing/**",
        "--output",
        "empty.md",
    )

    assert result.returncode == 1
    assert "No repository files matched the selected export scope" in result.stderr
    assert not (target_root / "empty.md").exists()