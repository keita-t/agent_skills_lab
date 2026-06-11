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
        / ".ai_ecosystems"
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
        / ".ai_ecosystems"
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
    assert str(repo_root / ".ai_ecosystems" / "codebase-context" / "Dockerfile") in log_lines[0]
    assert "run --rm --entrypoint sh" in log_lines[1]
    assert f"--volume {repo_root}:{repo_root}" in log_lines[1]
    assert "agent-skills-lab/codebase-context-runtime:local" in log_lines[1]
    assert "run --rm" in log_lines[2]
    assert f"--volume {repo_root}:{repo_root}" in log_lines[2]
    assert f"--workdir {repo_root}" in log_lines[2]
    assert "agent-skills-lab/codebase-context-runtime:local" in log_lines[2]
    assert f"--repo-root {repo_root} --output runtime.md" in log_lines[2]


def test_codebase_context_runtime_wrapper_forwards_smart_mode_args(
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
        / ".ai_ecosystems"
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
            "--mode",
            "smart",
            "--budget",
            "low",
            "--task",
            "cache behavior",
        ],
        cwd=repo_root,
        env={"PATH": f"{fake_bin}:{os.environ.get('PATH', '')}"},
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr

    log_lines = docker_log.read_text(encoding="utf-8").splitlines()

    assert len(log_lines) == 3
    assert (
        f"--repo-root {repo_root} --output runtime.md --mode smart --budget low --task cache behavior"
        in log_lines[2]
    )


def test_codebase_context_runtime_wrapper_falls_back_to_docker_cp_when_bind_mount_probe_fails(
    isolated_repo: Path,
    tmp_path: Path,
) -> None:
    bash_path = shutil.which("bash")
    assert bash_path is not None
    repo_root = isolated_repo

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
        "if [[ \"$1\" == 'start' ]]; then\n"
        f"  mkdir -p \"{tmp_path}/container-repo\"\n"
        f"  printf generated > \"{tmp_path}/container-repo/runtime.md\"\n"
        "fi\n"
        "if [[ \"$1\" == 'cp' && \"$3\" == '-' ]]; then\n"
        f"  tar -C \"{tmp_path}/container-repo\" -cf - runtime.md\n"
        "fi\n"
        "exit 0\n",
        encoding="utf-8",
    )
    fake_docker.chmod(0o755)

    script_path = (
        repo_root
        / ".ai_ecosystems"
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
    assert (
        "create --workdir /tmp/runtime-container-repo "
        "agent-skills-lab/codebase-context-runtime:local "
        "--repo-root /tmp/runtime-container-repo --output /tmp/runtime-container-repo/runtime.md"
        in log_lines[2]
    )
    assert f"cp {repo_root}/. fallback-container:/tmp/runtime-container-repo" in log_lines[3]
    assert "start -a fallback-container" in log_lines[4]
    assert "cp fallback-container:/tmp/runtime-container-repo/runtime.md -" in log_lines[5]
    assert "rm -f fallback-container" in log_lines[6]
    assert (repo_root / "runtime.md").read_text(encoding="utf-8") == "generated"


def test_codebase_context_runtime_wrapper_maps_subdirectory_workdir_for_copy_fallback(
    isolated_repo: Path,
    tmp_path: Path,
) -> None:
    bash_path = shutil.which("bash")
    assert bash_path is not None
    repo_root = isolated_repo

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
        "if [[ \"$1\" == 'start' ]]; then\n"
        f"  mkdir -p \"{tmp_path}/container-repo\"\n"
        f"  printf generated > \"{tmp_path}/container-repo/runtime.md\"\n"
        "fi\n"
        "if [[ \"$1\" == 'cp' && \"$3\" == '-' ]]; then\n"
        f"  tar -C \"{tmp_path}/container-repo\" -cf - runtime.md\n"
        "fi\n"
        "exit 0\n",
        encoding="utf-8",
    )
    fake_docker.chmod(0o755)

    script_path = (
        repo_root
        / ".ai_ecosystems"
        / "codebase-context"
        / "generate_codebase_context.sh"
    )
    nested_cwd = repo_root / "tests"
    nested_cwd.mkdir()

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


def test_codebase_context_runtime_wrapper_maps_absolute_repo_output_to_fallback_repo(
    isolated_repo: Path,
    tmp_path: Path,
) -> None:
    bash_path = shutil.which("bash")
    assert bash_path is not None
    repo_root = isolated_repo

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    docker_log = tmp_path / "docker.log"
    output_path = repo_root / "reports" / "runtime.md"
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
        "if [[ \"$1\" == 'start' ]]; then\n"
        f"  mkdir -p \"{tmp_path}/container-repo/reports\"\n"
        f"  printf generated > \"{tmp_path}/container-repo/reports/runtime.md\"\n"
        "fi\n"
        "if [[ \"$1\" == 'cp' && \"$3\" == '-' ]]; then\n"
        f"  tar -C \"{tmp_path}/container-repo/reports\" -cf - runtime.md\n"
        "fi\n"
        "exit 0\n",
        encoding="utf-8",
    )
    fake_docker.chmod(0o755)

    script_path = (
        repo_root
        / ".ai_ecosystems"
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
            str(output_path),
        ],
        cwd=repo_root,
        env={"PATH": f"{fake_bin}:{os.environ.get('PATH', '')}"},
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert output_path.read_text(encoding="utf-8") == "generated"

    log_lines = docker_log.read_text(encoding="utf-8").splitlines()

    assert len(log_lines) == 7
    assert (
        "create --workdir /tmp/runtime-container-repo "
        "agent-skills-lab/codebase-context-runtime:local "
        "--repo-root /tmp/runtime-container-repo --output /tmp/runtime-container-repo/reports/runtime.md"
        in log_lines[2]
    )
    assert "cp fallback-container:/tmp/runtime-container-repo/reports/runtime.md -" in log_lines[5]


def test_codebase_context_runtime_wrapper_uses_copy_fallback_for_external_output(
    repo_root: Path,
    tmp_path: Path,
) -> None:
    bash_path = shutil.which("bash")
    assert bash_path is not None

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    docker_log = tmp_path / "docker.log"
    external_output = tmp_path / "external" / "runtime.md"
    fake_docker = fake_bin / "docker"
    fake_docker.write_text(
        f"#!{bash_path}\n"
        f"printf '%s\\n' \"$*\" >> \"{docker_log}\"\n"
        "if [[ \"$1\" == 'run' && \"$*\" == *'--entrypoint sh'* ]]; then\n"
        "  exit 99\n"
        "fi\n"
        "if [[ \"$1\" == 'create' ]]; then\n"
        "  printf 'fallback-container\\n'\n"
        "fi\n"
        "if [[ \"$1\" == 'start' ]]; then\n"
        f"  mkdir -p \"{tmp_path}/container-output{external_output.parent}\"\n"
        f"  printf generated > \"{tmp_path}/container-output{external_output}\"\n"
        "fi\n"
        "if [[ \"$1\" == 'cp' && \"$3\" == '-' ]]; then\n"
        f"  tar -C \"{tmp_path}/container-output{external_output.parent}\" -cf - runtime.md\n"
        "fi\n"
        "exit 0\n",
        encoding="utf-8",
    )
    fake_docker.chmod(0o755)

    script_path = (
        repo_root
        / ".ai_ecosystems"
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
            str(external_output),
        ],
        cwd=repo_root,
        env={"PATH": f"{fake_bin}:{os.environ.get('PATH', '')}"},
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert external_output.read_text(encoding="utf-8") == "generated"

    log_lines = docker_log.read_text(encoding="utf-8").splitlines()

    assert len(log_lines) == 6
    assert "run --rm --entrypoint sh" not in "\n".join(log_lines)
    assert (
        "create --workdir /tmp/runtime-container-repo "
        "agent-skills-lab/codebase-context-runtime:local "
        f"--repo-root /tmp/runtime-container-repo --output /tmp/runtime-container-output{external_output}"
        in log_lines[1]
    )
    assert f"cp fallback-container:/tmp/runtime-container-output{external_output} -" in log_lines[4]
