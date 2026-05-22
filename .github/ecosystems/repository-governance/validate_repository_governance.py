#!/usr/bin/env python3
"""Validate repository-governance core files and their navigation links."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


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

    repo_root = Path(args.repo_root).resolve()
    required_paths, required_links, markdown_paths = _mode_config(args.mode)

    errors: list[str] = []
    errors.extend(_check_required_paths(repo_root, required_paths))
    errors.extend(_check_required_links(repo_root, required_links))
    errors.extend(_check_relative_links_exist(repo_root, markdown_paths))
    errors.extend(_check_todo_structure(repo_root / "docs" / "TODO.md"))

    if errors:
        print("REPOSITORY GOVERNANCE VALIDATION FAILED")
        for index, error in enumerate(errors, start=1):
            print(f"{index}. {error}")
        return 1

    print("REPOSITORY GOVERNANCE VALIDATION PASSED")
    print(f"Mode: {args.mode}")
    print(f"Repository root: {repo_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())