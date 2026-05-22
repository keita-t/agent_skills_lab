from __future__ import annotations

import importlib.util
import shutil
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
ECOSYSTEMS_DIR = REPO_ROOT / ".github" / "ecosystems"
REPOSITORY_GOVERNANCE_DIR = ECOSYSTEMS_DIR / "repository-governance"

for path in (ECOSYSTEMS_DIR, REPOSITORY_GOVERNANCE_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


@pytest.fixture
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture
def blank_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "blank-repo"
    repo.mkdir()
    return repo


@pytest.fixture
def isolated_repo(tmp_path: Path, repo_root: Path) -> Path:
    repo = tmp_path / "isolated-repo"
    repo.mkdir()
    shutil.copytree(repo_root / ".github", repo / ".github")
    return repo


@pytest.fixture
def invoke_main(monkeypatch: pytest.MonkeyPatch):
    def _invoke(module, *args: str) -> int:
        monkeypatch.setattr(
            sys,
            "argv",
            [str(getattr(module, "__file__", module.__name__)), *[str(arg) for arg in args]],
        )
        return module.main()

    return _invoke


@pytest.fixture
def load_module_from_path():
    def _load(module_name: str, module_path: Path):
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        assert spec is not None
        assert spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        module_dir = str(module_path.parent)
        if module_dir not in sys.path:
            sys.path.insert(0, module_dir)
        spec.loader.exec_module(module)
        return module

    return _load
