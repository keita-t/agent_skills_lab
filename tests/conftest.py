from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
ECOSYSTEMS_DIR = REPO_ROOT / ".ai_ecosystems"
REPOSITORY_DOCS_DIR = ECOSYSTEMS_DIR / "repository-docs"

for path in (ECOSYSTEMS_DIR, REPOSITORY_DOCS_DIR):
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
    from ecosystem_delivery_service import apply_delivery_changes, build_install_changeset

    apply_delivery_changes(
        build_install_changeset(
            target_root=repo,
            ecosystem_slug="repository-docs",
            source_root=repo_root,
        )
    )
    apply_delivery_changes(
        build_install_changeset(
            target_root=repo,
            ecosystem_slug="codebase-context",
            source_root=repo_root,
        )
    )
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
