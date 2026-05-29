from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

import pytest


@pytest.fixture
def codebase_context_generator(repo_root: Path, load_module_from_path):
    module_path = (
        repo_root
        / ".github"
        / "ecosystems"
        / "codebase-context"
        / "generate_codebase_context.py"
    )
    return load_module_from_path("generate_codebase_context_test", module_path)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def init_git_repo(path: Path) -> None:
    git_path = shutil.which("git")
    if git_path is None:
        pytest.skip("git is required for this test")
    subprocess.run([git_path, "init", "-q", str(path)], check=True, capture_output=True)


def test_generator_renders_required_template_and_excludes_noise(
    tmp_path: Path,
    codebase_context_generator,
) -> None:
    repo_root = tmp_path / "plain-repo"
    repo_root.mkdir()
    (repo_root / ".github").mkdir()
    write_text(repo_root / "src" / "b.py", "print('b')\n")
    write_text(repo_root / "src" / "a.py", "print('a')\n")
    write_text(repo_root / "docs" / "README.md", "# Guide\n")
    write_text(repo_root / "build" / "ignored.txt", "skip me\n")
    write_bytes(repo_root / "assets" / "logo.bin", b"\x89PNG\x00\x01")

    output_path = repo_root / "snapshot.md"

    exit_code = codebase_context_generator.main(
        ["--repo-root", str(repo_root), "--output", str(output_path)]
    )

    output = output_path.read_text(encoding="utf-8")

    assert exit_code == 0
    assert output.index("【指示】") < output.index("【インデックス】")
    assert output.index("【インデックス】") < output.index("【コードベース】")
    assert output.index("【コードベース】") < output.index("【念押しの指示（最後に小さく）】")
    assert "### docs/README.md" in output
    assert "### src/a.py" in output
    assert "### src/b.py" in output
    assert output.index("### docs/README.md") < output.index("### src/a.py")
    assert output.index("### src/a.py") < output.index("### src/b.py")
    assert "build/ignored.txt" not in output
    assert "assets/logo.bin" not in output
    assert "docs/" in output
    assert "src/" in output
    assert "<small>" in output


def test_generator_respects_gitignore_by_default(
    tmp_path: Path,
    codebase_context_generator,
) -> None:
    repo_root = tmp_path / "git-repo-default"
    repo_root.mkdir()
    init_git_repo(repo_root)
    (repo_root / ".github").mkdir()
    write_text(repo_root / ".gitignore", "ignored.txt\n")
    write_text(repo_root / "src" / "app.py", "print('ok')\n")
    write_text(repo_root / "ignored.txt", "ignore me\n")

    output_path = repo_root / "default.md"
    codebase_context_generator.main(
        ["--repo-root", str(repo_root), "--output", str(output_path)]
    )

    output = output_path.read_text(encoding="utf-8")

    assert "### src/app.py" in output
    assert "### ignored.txt" not in output


def test_generator_explicit_include_can_override_default_exclusions(
    tmp_path: Path,
    codebase_context_generator,
) -> None:
    repo_root = tmp_path / "git-repo-explicit"
    repo_root.mkdir()
    init_git_repo(repo_root)
    (repo_root / ".github").mkdir()
    write_text(repo_root / ".gitignore", "build/\n")
    write_text(repo_root / "src" / "app.py", "print('keep default')\n")
    write_text(repo_root / "build" / "secret.txt", "include me only when explicit\n")

    output_path = repo_root / "explicit.md"
    codebase_context_generator.main(
        [
            "--repo-root",
            str(repo_root),
            "--include",
            "build/**",
            "--output",
            str(output_path),
        ]
    )

    output = output_path.read_text(encoding="utf-8")

    assert "### build/secret.txt" in output
    assert "### src/app.py" not in output


def test_generator_source_only_excludes_auxiliary_files(
    tmp_path: Path,
    codebase_context_generator,
) -> None:
    repo_root = tmp_path / "plain-repo-source-only"
    repo_root.mkdir()
    (repo_root / ".github").mkdir()
    write_text(repo_root / "src" / "main.py", "print('source')\n")
    write_text(repo_root / "README.md", "# Supporting doc\n")
    write_text(repo_root / "pyproject.toml", "[project]\nname = 'demo'\n")

    output_path = repo_root / "source-only.md"
    codebase_context_generator.main(
        [
            "--repo-root",
            str(repo_root),
            "--source-only",
            "--output",
            str(output_path),
        ]
    )

    output = output_path.read_text(encoding="utf-8")

    assert "### src/main.py" in output
    assert "### README.md" not in output
    assert "### pyproject.toml" not in output