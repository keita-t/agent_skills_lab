from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

import pytest


@pytest.fixture
def codebase_context_generator(repo_root: Path, load_module_from_path):
    module_path = (
        repo_root
        / ".ai_ecosystems"
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


def git_add_all(path: Path) -> None:
    git_path = shutil.which("git")
    if git_path is None:
        pytest.skip("git is required for this test")
    subprocess.run([git_path, "-C", str(path), "add", "-A"], check=True, capture_output=True)


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
    assert output.index("【コードベース】") < output.index("【念押しの指示】")
    assert "【念押しの指示（最後に小さく）】" not in output
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
    assert "### docs/README.md\n```markdown\n# Guide\n```" in output
    assert "### src/a.py\n```python\nprint('a')\n```" in output


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
    git_add_all(repo_root)

    output_path = repo_root / "default.md"
    codebase_context_generator.main(
        ["--repo-root", str(repo_root), "--output", str(output_path)]
    )

    output = output_path.read_text(encoding="utf-8")

    assert "### src/app.py" in output
    assert "### ignored.txt" not in output


def test_generator_default_git_export_excludes_nonignored_untracked_files(
    tmp_path: Path,
    codebase_context_generator,
) -> None:
    repo_root = tmp_path / "git-repo-tracked-only-default"
    repo_root.mkdir()
    init_git_repo(repo_root)
    (repo_root / ".github").mkdir()
    write_text(repo_root / "README.md", "# Tracked\n")
    write_text(repo_root / "src" / "app.py", "print('untracked')\n")
    git_add_all(repo_root)
    subprocess.run(
        [shutil.which("git"), "-C", str(repo_root), "reset", "-q", "src/app.py"],
        check=True,
        capture_output=True,
    )

    output_path = repo_root / "default.md"
    codebase_context_generator.main(
        ["--repo-root", str(repo_root), "--output", str(output_path)]
    )

    output = output_path.read_text(encoding="utf-8")

    assert "### README.md\n" in output
    assert "### src/app.py\n" not in output


def test_generator_skips_sensitive_env_files_by_default(
    tmp_path: Path,
    codebase_context_generator,
) -> None:
    repo_root = tmp_path / "plain-repo-sensitive-env"
    repo_root.mkdir()
    (repo_root / ".github").mkdir()
    write_text(repo_root / "src" / "app.py", "print('ok')\n")
    write_text(repo_root / ".env", "SECRET=value\n")
    write_text(repo_root / ".env.local", "LOCAL_SECRET=value\n")
    write_text(repo_root / ".env.example", "EXAMPLE=value\n")

    output_path = repo_root / "snapshot.md"
    codebase_context_generator.main(
        ["--repo-root", str(repo_root), "--output", str(output_path)]
    )

    output = output_path.read_text(encoding="utf-8")

    assert "### src/app.py" in output
    assert "### .env.example\n" in output
    assert "### .env\n" not in output
    assert "### .env.local\n" not in output


def test_generator_explicit_include_does_not_override_zero_trust_sensitive_env_policy(
    tmp_path: Path,
    codebase_context_generator,
) -> None:
    repo_root = tmp_path / "plain-repo-sensitive-env-include"
    repo_root.mkdir()
    (repo_root / ".github").mkdir()
    write_text(repo_root / "src" / "app.py", "print('ok')\n")
    write_text(repo_root / ".env.local", "LOCAL_SECRET=value\n")

    output_path = repo_root / "env-only.md"
    with pytest.raises(RuntimeError, match="No repository files matched the selected export scope"):
        codebase_context_generator.main(
            [
                "--repo-root",
                str(repo_root),
                "--include",
                ".env.local",
                "--output",
                str(output_path),
            ]
        )


def test_generator_wildcard_include_keeps_zero_trust_sensitive_env_files_excluded(
    tmp_path: Path,
    codebase_context_generator,
) -> None:
    repo_root = tmp_path / "plain-repo-sensitive-env-wildcard"
    repo_root.mkdir()
    (repo_root / ".github").mkdir()
    write_text(repo_root / "src" / "app.py", "print('ok')\n")
    write_text(repo_root / ".env.local", "LOCAL_SECRET=value\n")
    write_text(repo_root / ".env.example", "EXAMPLE=value\n")

    output_path = repo_root / "wildcard.md"
    codebase_context_generator.main(
        [
            "--repo-root",
            str(repo_root),
            "--include",
            "*",
            "--output",
            str(output_path),
        ]
    )

    output = output_path.read_text(encoding="utf-8")

    assert "### .env.local\n" not in output
    assert "### .env.example\n" in output
    assert "### src/app.py\n" in output


def test_generator_explicit_include_does_not_override_default_exclusions(
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

    with pytest.raises(RuntimeError, match="No repository files matched the selected export scope"):
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


def test_generator_explicit_include_keeps_nonignored_untracked_files_in_git_repo(
    tmp_path: Path,
    codebase_context_generator,
) -> None:
    repo_root = tmp_path / "git-repo-include-nonignored"
    repo_root.mkdir()
    init_git_repo(repo_root)
    (repo_root / ".github").mkdir()
    write_text(repo_root / "src" / "app.py", "print('keep me')\n")
    write_text(repo_root / "README.md", "# Doc\n")

    output_path = repo_root / "explicit-nonignored.md"
    codebase_context_generator.main(
        [
            "--repo-root",
            str(repo_root),
            "--include",
            "src/**",
            "--output",
            str(output_path),
        ]
    )

    output = output_path.read_text(encoding="utf-8")

    assert "### src/app.py" in output
    assert "### README.md" not in output


def test_list_repo_files_applies_include_scope_before_reading_text_files(
    tmp_path: Path,
    codebase_context_generator,
) -> None:
    repo_root = tmp_path / "git-repo-list-scope"
    repo_root.mkdir()
    init_git_repo(repo_root)
    (repo_root / ".github").mkdir()
    write_text(repo_root / "src" / "app.py", "print('keep me')\n")
    write_text(repo_root / "README.md", "# Skip me\n")

    output_path = repo_root / "scoped.md"
    paths = codebase_context_generator.list_repo_files(repo_root, output_path, ["src/**"], [])

    assert [codebase_context_generator.relative_posix_path(path, repo_root) for path in paths] == [
        "src/app.py"
    ]


def test_list_repo_files_keeps_ignored_files_excluded_even_with_include(
    tmp_path: Path,
    codebase_context_generator,
) -> None:
    repo_root = tmp_path / "git-repo-ignored-scope"
    repo_root.mkdir()
    init_git_repo(repo_root)
    (repo_root / ".github").mkdir()
    write_text(repo_root / ".gitignore", "docs/private.md\n")
    write_text(repo_root / "docs" / "public.md", "# Keep me\n")
    write_text(repo_root / "docs" / "private.md", "# Ignore me\n")

    output_path = repo_root / "docs-only.md"
    paths = codebase_context_generator.list_repo_files(repo_root, output_path, ["docs/**"], [])

    assert [codebase_context_generator.relative_posix_path(path, repo_root) for path in paths] == [
        "docs/public.md"
    ]


def test_include_scope_keeps_excluded_directories_filtered_in_git_mode(
    tmp_path: Path,
    codebase_context_generator,
) -> None:
    repo_root = tmp_path / "git-repo-excluded-dir-scope"
    repo_root.mkdir()
    init_git_repo(repo_root)
    (repo_root / ".github").mkdir()
    write_text(repo_root / ".gitignore", "build/\n")
    write_text(repo_root / "src" / "app.py", "print('keep me')\n")
    write_text(repo_root / "build" / "secret.py", "print('skip me')\n")

    output_path = repo_root / "python-only.md"
    paths = codebase_context_generator.list_repo_files(repo_root, output_path, ["*.py"], [])

    assert [codebase_context_generator.relative_posix_path(path, repo_root) for path in paths] == [
        "src/app.py"
    ]


def test_fallback_include_prunes_excluded_directories(
    tmp_path: Path,
    codebase_context_generator,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo_root = tmp_path / "fallback-repo"
    repo_root.mkdir()
    (repo_root / ".github").mkdir()
    write_text(repo_root / "src" / "app.py", "print('keep me')\n")
    write_text(repo_root / ".git" / "HEAD", "ref: refs/heads/main\n")
    write_text(repo_root / "build" / "secret.txt", "keep explicit\n")

    monkeypatch.setattr(codebase_context_generator, "list_git_files", lambda *_args, **_kwargs: None)

    src_output = repo_root / "src-only.md"
    codebase_context_generator.main(
        [
            "--repo-root",
            str(repo_root),
            "--include",
            "src/**",
            "--output",
            str(src_output),
        ]
    )
    src_text = src_output.read_text(encoding="utf-8")

    assert "### src/app.py" in src_text
    assert ".git/HEAD" not in src_text

    explicit_output = repo_root / "build-only.md"
    with pytest.raises(RuntimeError, match="No repository files matched the selected export scope"):
        codebase_context_generator.main(
            [
                "--repo-root",
                str(repo_root),
                "--include",
                "build/**",
                "--output",
                str(explicit_output),
            ]
        )


def test_list_repo_files_applies_exclude_scope_before_reading_text_files(
    tmp_path: Path,
    codebase_context_generator,
) -> None:
    repo_root = tmp_path / "plain-repo-exclude-scope"
    repo_root.mkdir()
    (repo_root / ".github").mkdir()
    write_text(repo_root / "src" / "app.py", "print('keep me')\n")
    write_text(repo_root / "README.md", "# Skip me\n")

    output_path = repo_root / "excluded.md"
    paths = codebase_context_generator.list_repo_files(repo_root, output_path, [], ["README.md"])

    assert [codebase_context_generator.relative_posix_path(path, repo_root) for path in paths] == [
        "src/app.py"
    ]


def test_fallback_include_prunes_unrelated_directories(
    tmp_path: Path,
    codebase_context_generator,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo_root = tmp_path / "fallback-pattern-pruning"
    repo_root.mkdir()
    (repo_root / ".github").mkdir()
    write_text(repo_root / "docs" / "project-charter.md", "# Charter\n")
    write_text(repo_root / "unrelated" / "nested" / "note.md", "# Skip\n")

    visited_roots: list[Path] = []
    real_walk = codebase_context_generator.os.walk

    def recording_walk(*args, **kwargs):
        for current_root, dir_names, file_names in real_walk(*args, **kwargs):
            visited_roots.append(Path(current_root).resolve())
            yield current_root, dir_names, file_names

    monkeypatch.setattr(codebase_context_generator, "list_git_files", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(codebase_context_generator.os, "walk", recording_walk)

    output_path = repo_root / "docs-only.md"
    codebase_context_generator.main(
        [
            "--repo-root",
            str(repo_root),
            "--include",
            "docs/project-charter.md",
            "--output",
            str(output_path),
        ]
    )

    assert repo_root.resolve() in visited_roots
    assert (repo_root / "docs").resolve() in visited_roots
    assert (repo_root / "unrelated").resolve() not in visited_roots


def test_should_descend_into_directory_keeps_excluded_dirs_filtered(
    codebase_context_generator,
) -> None:
    assert codebase_context_generator.should_descend_into_directory("src", ["src/**"])
    assert not codebase_context_generator.should_descend_into_directory(
        "src", ["docs/project-charter.md"]
    )
    assert codebase_context_generator.should_descend_into_directory(
        "docs", ["docs/project-charter.md"]
    )
    assert not codebase_context_generator.should_descend_into_directory(".git", ["src/**"])
    assert not codebase_context_generator.should_descend_into_directory("build", ["build/**"])


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


def test_generator_budget_hint_defaults_to_smart_mode(
    tmp_path: Path,
    codebase_context_generator,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo_root = tmp_path / "plain-repo-smart-budget-hint"
    repo_root.mkdir()
    (repo_root / ".github").mkdir()
    write_text(repo_root / "src" / "app.py", "def main():\n    return 'ok'\n")

    monkeypatch.setitem(codebase_context_generator.SMART_BUDGET_TOKENS, "low", 400)

    output_path = repo_root / "smart.md"
    codebase_context_generator.main(
        [
            "--repo-root",
            str(repo_root),
            "--budget",
            "low",
            "--output",
            str(output_path),
        ]
    )

    output = output_path.read_text(encoding="utf-8")

    assert "### src/app.py" in output
    assert "Smart mode stub: signatures only." not in output


def test_generator_rejects_smart_only_options_in_simple_mode(
    tmp_path: Path,
    codebase_context_generator,
) -> None:
    repo_root = tmp_path / "plain-repo-simple-budget"
    repo_root.mkdir()
    (repo_root / ".github").mkdir()
    write_text(repo_root / "src" / "app.py", "print('ok')\n")

    with pytest.raises(RuntimeError, match="--budget and --task are only supported"):
        codebase_context_generator.main(
            [
                "--repo-root",
                str(repo_root),
                "--mode",
                "simple",
                "--budget",
                "low",
            ]
        )


def test_generator_smart_mode_prefers_task_related_full_files_and_stubs_others(
    tmp_path: Path,
    codebase_context_generator,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo_root = tmp_path / "plain-repo-smart-task"
    repo_root.mkdir()
    (repo_root / ".github").mkdir()
    write_text(
        repo_root / "src" / "cache.py",
        "class CacheStore:\n"
        "    def get(self, key):\n"
        "        return f'cache:{key}'\n",
    )
    write_text(
        repo_root / "src" / "helper.py",
        "def helper():\n"
        "    return 'helper'\n\n"
        f"DETAILS = '{'x' * 2_000}'\n",
    )

    monkeypatch.setitem(codebase_context_generator.SMART_BUDGET_TOKENS, "low", 260)

    output_path = repo_root / "smart-task.md"
    codebase_context_generator.main(
        [
            "--repo-root",
            str(repo_root),
            "--mode",
            "smart",
            "--budget",
            "low",
            "--task",
            "add cache behavior",
            "--output",
            str(output_path),
        ]
    )

    output = output_path.read_text(encoding="utf-8")

    assert "### src/cache.py" in output
    assert "return f'cache:{key}'" in output
    assert "### src/helper.py" in output
    assert "Smart mode stub: signatures only." in output
    assert "DETAILS =" not in output


def test_generator_smart_mode_keeps_sensitive_env_files_excluded(
    tmp_path: Path,
    codebase_context_generator,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo_root = tmp_path / "plain-repo-smart-sensitive-env"
    repo_root.mkdir()
    (repo_root / ".github").mkdir()
    write_text(repo_root / "src" / "app.py", "print('ok')\n")
    write_text(repo_root / ".env", "SECRET=value\n")
    write_text(repo_root / ".env.local", "LOCAL_SECRET=value\n")

    monkeypatch.setitem(codebase_context_generator.SMART_BUDGET_TOKENS, "low", 400)

    output_path = repo_root / "smart-sensitive.md"
    codebase_context_generator.main(
        [
            "--repo-root",
            str(repo_root),
            "--mode",
            "smart",
            "--budget",
            "low",
            "--output",
            str(output_path),
        ]
    )

    output = output_path.read_text(encoding="utf-8")

    assert "### src/app.py" in output
    assert "### .env\n" not in output
    assert "### .env.local\n" not in output


def test_generator_smart_mode_errors_when_include_stubs_exceed_budget(
    tmp_path: Path,
    codebase_context_generator,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo_root = tmp_path / "plain-repo-smart-include-budget"
    repo_root.mkdir()
    (repo_root / ".github").mkdir()
    write_text(repo_root / "src" / "app.py", "def main():\n    return 'ok'\n")

    monkeypatch.setitem(codebase_context_generator.SMART_BUDGET_TOKENS, "low", 1)

    with pytest.raises(RuntimeError, match="explicitly selected files as stubs"):
        codebase_context_generator.main(
            [
                "--repo-root",
                str(repo_root),
                "--mode",
                "smart",
                "--budget",
                "low",
                "--include",
                "src/**",
            ]
        )


def test_generator_smart_mode_explicit_include_rejects_full_candidate_over_budget(
    tmp_path: Path,
    codebase_context_generator,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo_root = tmp_path / "plain-repo-smart-include-exact-full-budget"
    repo_root.mkdir()
    (repo_root / ".github").mkdir()
    relative_path = "src/app.py"
    content = "def main():\n" + ("    x = 1\n" * 20)
    write_text(repo_root / relative_path, content)

    stub_section = codebase_context_generator.render_file_section(
        relative_path,
        codebase_context_generator.render_stub_content(relative_path, content),
    )
    full_section = codebase_context_generator.render_file_section(
        relative_path,
        content,
    )
    stub_tokens = codebase_context_generator.estimate_smart_markdown_tokens(
        {relative_path: stub_section},
        "ja",
        codebase_context_generator.DEFAULT_INDEX_DEPTH,
    )
    full_tokens = codebase_context_generator.estimate_smart_markdown_tokens(
        {relative_path: full_section},
        "ja",
        codebase_context_generator.DEFAULT_INDEX_DEPTH,
    )
    budget_tokens = full_tokens - 1

    assert stub_tokens <= budget_tokens < full_tokens

    monkeypatch.setitem(
        codebase_context_generator.SMART_BUDGET_TOKENS,
        "low",
        budget_tokens,
    )

    output_path = repo_root / "smart-include.md"
    codebase_context_generator.main(
        [
            "--repo-root",
            str(repo_root),
            "--mode",
            "smart",
            "--budget",
            "low",
            "--include",
            "src/**",
            "--output",
            str(output_path),
        ]
    )

    output = output_path.read_text(encoding="utf-8")

    assert "# Smart mode stub: signatures only." in output
    assert "    x = 1" not in output


def test_generator_smart_mode_explicit_include_uses_exact_shared_index_budget(
    tmp_path: Path,
    codebase_context_generator,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo_root = tmp_path / "plain-repo-smart-include-shared-index-budget"
    repo_root.mkdir()
    (repo_root / ".github").mkdir()
    relative_paths = [
        f"src/shared/file_{index:03}.py"
        for index in range(80)
    ]
    content_by_path = {
        relative_path: (
            "def main():\n"
            + "".join(f"    value_{line} = {line}\n" for line in range(8))
            + "    return value_7\n"
        )
        for relative_path in relative_paths
    }
    for relative_path, content in content_by_path.items():
        write_text(repo_root / relative_path, content)

    full_representations = {
        relative_path: codebase_context_generator.render_file_section(
            relative_path,
            content,
        )
        for relative_path, content in content_by_path.items()
    }
    budget_tokens = codebase_context_generator.estimate_smart_markdown_tokens(
        full_representations,
        "ja",
        codebase_context_generator.DEFAULT_INDEX_DEPTH,
    )

    monkeypatch.setitem(
        codebase_context_generator.SMART_BUDGET_TOKENS,
        "low",
        budget_tokens,
    )

    output_path = repo_root / "smart-include.md"
    codebase_context_generator.main(
        [
            "--repo-root",
            str(repo_root),
            "--mode",
            "smart",
            "--budget",
            "low",
            "--include",
            "src/shared/**",
            "--output",
            str(output_path),
        ]
    )

    output = output_path.read_text(encoding="utf-8")

    assert "# Smart mode stub: signatures only." not in output
    assert output.count("    value_7 = 7") == len(relative_paths)
