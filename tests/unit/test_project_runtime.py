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


def test_validator_shell_wrappers_require_python_3_11_or_newer(
    repo_root: Path,
    tmp_path: Path,
) -> None:
    bash_path = shutil.which("bash")
    assert bash_path is not None

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()

    for interpreter_name in ("python3", "python"):
        fake_interpreter = fake_bin / interpreter_name
        fake_interpreter.write_text("#!/usr/bin/env bash\nexit 1\n", encoding="utf-8")
        fake_interpreter.chmod(0o755)

    scripts = [
        repo_root
        / ".github"
        / "ecosystems"
        / "codebase-context"
        / "generate_codebase_context.sh",
    ]

    for script_path in scripts:
        result = subprocess.run(
            [bash_path, str(script_path)],
            env={"PATH": f"{fake_bin}:{os.environ.get('PATH', '')}"},
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert "python 3.11 or newer interpreter not found" in result.stderr