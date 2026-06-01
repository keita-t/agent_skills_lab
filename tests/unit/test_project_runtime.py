from __future__ import annotations

import os
import shutil
import subprocess
import tomllib
from pathlib import Path


def test_pyproject_declares_python_3_11_plus(repo_root: Path) -> None:
    pyproject_path = repo_root / "pyproject.toml"
    pyproject = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))

    assert pyproject["project"]["requires-python"] == ">=3.11"


def test_codebase_context_runtime_wrapper_requires_docker(
    repo_root: Path,
    tmp_path: Path,
) -> None:
    bash_path = shutil.which("bash")
    assert bash_path is not None

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()

    script_path = (
        repo_root
        / ".github"
        / "ecosystems"
        / "codebase-context"
        / "generate_codebase_context.sh"
    )

    result = subprocess.run(
        [bash_path, str(script_path)],
        env={"PATH": str(fake_bin)},
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "docker is required for codebase-context runtime" in result.stderr


def test_codebase_context_runtime_wrapper_builds_and_runs_docker_image(
    repo_root: Path,
    tmp_path: Path,
) -> None:
    bash_path = shutil.which("bash")
    assert bash_path is not None

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    docker_log = tmp_path / "docker.log"
    fake_docker = fake_bin / "docker"
    fake_docker.write_text(
        f"#!{bash_path}\n"
        f"printf '%s\\n' \"$*\" >> \"{docker_log}\"\n"
        "exit 0\n",
        encoding="utf-8",
    )
    fake_docker.chmod(0o755)

    script_path = (
        repo_root
        / ".github"
        / "ecosystems"
        / "codebase-context"
        / "generate_codebase_context.sh"
    )

    result = subprocess.run(
        [
            bash_path,
            str(script_path),
            "--repo-root",
            ".",
            "--output",
            "runtime.md",
        ],
        cwd=repo_root,
        env={"PATH": f"{fake_bin}:{os.environ.get('PATH', '')}"},
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr

    log_lines = docker_log.read_text(encoding="utf-8").splitlines()

    assert len(log_lines) == 3
    assert "build --tag agent-skills-lab/codebase-context-runtime:local --file" in log_lines[0]
    assert str(repo_root / ".github" / "ecosystems" / "codebase-context" / "Dockerfile") in log_lines[0]
    assert "run --rm --entrypoint sh" in log_lines[1]
    assert f"--volume {repo_root}:{repo_root}" in log_lines[1]
    assert "agent-skills-lab/codebase-context-runtime:local" in log_lines[1]
    assert "run --rm" in log_lines[2]
    assert f"--volume {repo_root}:{repo_root}" in log_lines[2]
    assert f"--workdir {repo_root}" in log_lines[2]
    assert "agent-skills-lab/codebase-context-runtime:local" in log_lines[2]
    assert f"--repo-root {repo_root} --output runtime.md" in log_lines[2]


def test_codebase_context_runtime_wrapper_falls_back_to_docker_cp_when_bind_mount_probe_fails(
    repo_root: Path,
    tmp_path: Path,
) -> None:
    bash_path = shutil.which("bash")
    assert bash_path is not None

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    docker_log = tmp_path / "docker.log"
    fake_docker = fake_bin / "docker"
    fake_docker.write_text(
        f"#!{bash_path}\n"
        f"printf '%s\\n' \"$*\" >> \"{docker_log}\"\n"
        "if [[ \"$1\" == 'run' && \"$*\" == *'--entrypoint sh'* ]]; then\n"
        "  exit 1\n"
        "fi\n"
        "if [[ \"$1\" == 'create' ]]; then\n"
        "  printf 'fallback-container\\n'\n"
        "fi\n"
        "exit 0\n",
        encoding="utf-8",
    )
    fake_docker.chmod(0o755)

    script_path = (
        repo_root
        / ".github"
        / "ecosystems"
        / "codebase-context"
        / "generate_codebase_context.sh"
    )

    result = subprocess.run(
        [
            bash_path,
            str(script_path),
            "--repo-root",
            str(repo_root),
            "--output",
            "runtime.md",
        ],
        cwd=repo_root,
        env={"PATH": f"{fake_bin}:{os.environ.get('PATH', '')}"},
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr

    log_lines = docker_log.read_text(encoding="utf-8").splitlines()

    assert len(log_lines) == 7
    assert "build --tag agent-skills-lab/codebase-context-runtime:local --file" in log_lines[0]
    assert "run --rm --entrypoint sh" in log_lines[1]
    assert f"create --workdir /tmp/runtime-container-repo agent-skills-lab/codebase-context-runtime:local --repo-root /tmp/runtime-container-repo --output /tmp/runtime-container-repo/runtime.md" in log_lines[2]
    assert f"cp {repo_root}/. fallback-container:/tmp/runtime-container-repo" in log_lines[3]
    assert "start -a fallback-container" in log_lines[4]
    assert f"cp fallback-container:/tmp/runtime-container-repo/runtime.md {repo_root}/runtime.md" in log_lines[5]
    assert "rm -f fallback-container" in log_lines[6]


def test_codebase_context_runtime_wrapper_maps_subdirectory_workdir_for_copy_fallback(
    repo_root: Path,
    tmp_path: Path,
) -> None:
    bash_path = shutil.which("bash")
    assert bash_path is not None

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    docker_log = tmp_path / "docker.log"
    fake_docker = fake_bin / "docker"
    fake_docker.write_text(
        f"#!{bash_path}\n"
        f"printf '%s\\n' \"$*\" >> \"{docker_log}\"\n"
        "if [[ \"$1\" == 'run' && \"$*\" == *'--entrypoint sh'* ]]; then\n"
        "  exit 1\n"
        "fi\n"
        "if [[ \"$1\" == 'create' ]]; then\n"
        "  printf 'fallback-container\\n'\n"
        "fi\n"
        "exit 0\n",
        encoding="utf-8",
    )
    fake_docker.chmod(0o755)

    script_path = (
        repo_root
        / ".github"
        / "ecosystems"
        / "codebase-context"
        / "generate_codebase_context.sh"
    )
    nested_cwd = repo_root / "tests"

    result = subprocess.run(
        [
            bash_path,
            str(script_path),
            "--repo-root",
            str(repo_root),
            "--output",
            "runtime.md",
        ],
        cwd=nested_cwd,
        env={"PATH": f"{fake_bin}:{os.environ.get('PATH', '')}"},
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr

    log_lines = docker_log.read_text(encoding="utf-8").splitlines()

    assert len(log_lines) == 7
    assert "create --workdir /tmp/runtime-container-repo/tests agent-skills-lab/codebase-context-runtime:local" in log_lines[2]