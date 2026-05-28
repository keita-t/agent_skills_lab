#!/usr/bin/env python3
"""Validate repository-governance core files and their navigation links."""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import re
from pathlib import Path


@dataclass(frozen=True)
class ValidateRepositoryGovernanceInput:
    repo_root: str = "."
    mode: str = "single-language"


@dataclass(frozen=True)
class ValidationIssue:
    message: str
    path: str | None = None


@dataclass(frozen=True)
class ValidationResult:
    passed: bool
    errors: list[ValidationIssue] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
EN_DOC_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*\.md$")
JA_DOC_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*\.ja\.md$")


def _normalize_target(target: str) -> str:
    no_fragment = target.split("#", 1)[0]
    no_query = no_fragment.split("?", 1)[0]
    return no_query.strip()


def _extract_targets(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return [_normalize_target(match) for match in LINK_RE.findall(text)]


def _check_required_paths(repo_root: Path, required_paths: list[str]) -> list[str]:
    errors: list[str] = []
    for rel_path in required_paths:
        if not (repo_root / rel_path).is_file():
            errors.append(f"Missing required file: {rel_path}")
    return errors


def _check_required_links(repo_root: Path, required_links: dict[str, list[str]]) -> list[str]:
    errors: list[str] = []
    for rel_path, expected_targets in required_links.items():
        file_path = repo_root / rel_path
        if not file_path.is_file():
            continue
        targets = set(_extract_targets(file_path))
        for expected in expected_targets:
            if expected not in targets:
                errors.append(f"{rel_path} is missing link target: {expected}")
    return errors


def _check_relative_links_exist(repo_root: Path, markdown_paths: list[str]) -> list[str]:
    errors: list[str] = []
    for rel_path in markdown_paths:
        file_path = repo_root / rel_path
        if not file_path.is_file():
            continue
        for target in _extract_targets(file_path):
            if not target or target.startswith("#"):
                continue
            if "://" in target or target.startswith("mailto:"):
                continue
            resolved = (file_path.parent / target).resolve()
            try:
                resolved.relative_to(repo_root.resolve())
            except ValueError:
                errors.append(f"{rel_path} links outside repository root: {target}")
                continue
            if not resolved.exists():
                errors.append(f"{rel_path} has broken relative link: {target}")
    return errors


def _check_todo_structure(todo_path: Path) -> list[str]:
    if not todo_path.is_file():
        return []

    text = todo_path.read_text(encoding="utf-8")
    required_fragments = [
        "## This Document Structure And Update Rules",
        "## Implementation Backlog",
        "## Unresolved Design Concerns",
        "## Resolved Concerns Record",
        "explicit in-session human instruction",
        "routine maintenance",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in text]
    return [f"docs/TODO.md is missing required text: {fragment}" for fragment in missing]


def _check_bilingual_docs_layout(repo_root: Path) -> list[str]:
    docs_root = repo_root / "docs"
    en_root = docs_root / "en"
    ja_root = docs_root / "ja"
    errors: list[str] = []

    allowed_root_docs = {"README.md", "DOCUMENTATION_UPDATE_RULES.md", "TODO.md"}
    for file_path in sorted(path for path in docs_root.glob("*.md") if path.is_file()):
        if file_path.name not in allowed_root_docs:
            errors.append(
                "docs/"
                f"{file_path.name} root-level docs file is not allowed in bilingual mode; "
                "place repository-facing reference docs under docs/en and docs/ja"
            )

    english_docs = sorted(path for path in en_root.glob("*.md") if path.is_file())
    japanese_docs = sorted(path for path in ja_root.glob("*.md") if path.is_file())

    for file_path in english_docs:
        if not EN_DOC_NAME_RE.match(file_path.name):
            errors.append(
                f"docs/en/{file_path.name} must use a lowercase kebab-case .md file name"
            )
            continue
        if file_path.name == "project-charter.md":
            continue
        counterpart = ja_root / f"{file_path.stem}.ja.md"
        if not counterpart.is_file():
            errors.append(
                f"docs/en/{file_path.name} is missing Japanese counterpart: "
                f"docs/ja/{file_path.stem}.ja.md"
            )

    for file_path in japanese_docs:
        if not JA_DOC_NAME_RE.match(file_path.name):
            errors.append(
                f"docs/ja/{file_path.name} must use a lowercase kebab-case .ja.md file name"
            )
            continue
        if file_path.name == "project-charter.ja.md":
            continue
        stem = file_path.name.removesuffix(".ja.md")
        counterpart = en_root / f"{stem}.md"
        if not counterpart.is_file():
            errors.append(
                f"docs/ja/{file_path.name} is missing English counterpart: "
                f"docs/en/{stem}.md"
            )
    return errors


def _mode_config(mode: str) -> tuple[list[str], dict[str, list[str]], list[str]]:
    if mode == "bilingual":
        required_paths = [
            "README.md",
            "CLAUDE.md",
            "docs/README.md",
            "docs/DOCUMENTATION_UPDATE_RULES.md",
            "docs/en/project-charter.md",
            "docs/ja/project-charter.ja.md",
            "docs/TODO.md",
        ]
        required_links = {
            "README.md": [
                "docs/README.md",
                "docs/DOCUMENTATION_UPDATE_RULES.md",
                "docs/en/project-charter.md",
                "docs/ja/project-charter.ja.md",
                "docs/TODO.md",
            ],
            "CLAUDE.md": [
                "docs/README.md",
                "docs/DOCUMENTATION_UPDATE_RULES.md",
                "docs/en/project-charter.md",
                "docs/ja/project-charter.ja.md",
                "docs/TODO.md",
            ],
            "docs/README.md": [
                "./DOCUMENTATION_UPDATE_RULES.md",
                "./en/project-charter.md",
                "./ja/project-charter.ja.md",
                "./TODO.md",
            ],
            "docs/DOCUMENTATION_UPDATE_RULES.md": [
                "./README.md",
                "./en/project-charter.md",
                "./ja/project-charter.ja.md",
                "./TODO.md",
            ],
            "docs/en/project-charter.md": [
                "../README.md",
                "../DOCUMENTATION_UPDATE_RULES.md",
                "../TODO.md",
                "../ja/project-charter.ja.md",
            ],
            "docs/ja/project-charter.ja.md": [
                "../README.md",
                "../DOCUMENTATION_UPDATE_RULES.md",
                "../TODO.md",
                "../en/project-charter.md",
            ],
            "docs/TODO.md": ["./DOCUMENTATION_UPDATE_RULES.md"],
        }
    else:
        required_paths = [
            "README.md",
            "CLAUDE.md",
            "docs/README.md",
            "docs/DOCUMENTATION_UPDATE_RULES.md",
            "docs/project-charter.md",
            "docs/TODO.md",
        ]
        required_links = {
            "README.md": [
                "docs/README.md",
                "docs/DOCUMENTATION_UPDATE_RULES.md",
                "docs/project-charter.md",
                "docs/TODO.md",
            ],
            "CLAUDE.md": [
                "docs/README.md",
                "docs/DOCUMENTATION_UPDATE_RULES.md",
                "docs/project-charter.md",
                "docs/TODO.md",
            ],
            "docs/README.md": [
                "./project-charter.md",
                "./DOCUMENTATION_UPDATE_RULES.md",
                "./TODO.md",
            ],
            "docs/DOCUMENTATION_UPDATE_RULES.md": [
                "./README.md",
                "./project-charter.md",
                "./TODO.md",
            ],
            "docs/project-charter.md": [
                "./README.md",
                "./DOCUMENTATION_UPDATE_RULES.md",
                "./TODO.md",
            ],
            "docs/TODO.md": ["./DOCUMENTATION_UPDATE_RULES.md"],
        }

    markdown_paths = list(required_links)
    return required_paths, required_links, markdown_paths


def validate_repository_governance(
    request: ValidateRepositoryGovernanceInput,
) -> ValidationResult:
    repo_root = Path(request.repo_root).resolve()
    required_paths, required_links, markdown_paths = _mode_config(request.mode)

    errors: list[str] = []
    errors.extend(_check_required_paths(repo_root, required_paths))
    errors.extend(_check_required_links(repo_root, required_links))
    errors.extend(_check_relative_links_exist(repo_root, markdown_paths))
    errors.extend(_check_todo_structure(repo_root / "docs" / "TODO.md"))
    if request.mode == "bilingual":
        errors.extend(_check_bilingual_docs_layout(repo_root))

    return ValidationResult(
        passed=not errors,
        errors=[ValidationIssue(message=error) for error in errors],
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root to validate.",
    )
    parser.add_argument(
        "--mode",
        choices=["single-language", "bilingual"],
        default="single-language",
        help="Governance pack mode to validate.",
    )
    args = parser.parse_args()

    result = validate_repository_governance(
        ValidateRepositoryGovernanceInput(repo_root=args.repo_root, mode=args.mode)
    )

    if not result.passed:
        print("REPOSITORY GOVERNANCE VALIDATION FAILED")
        for index, error in enumerate(result.errors, start=1):
            print(f"{index}. {error.message}")
        return 1

    print("REPOSITORY GOVERNANCE VALIDATION PASSED")
    print(f"Mode: {args.mode}")
    print(f"Repository root: {Path(args.repo_root).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())