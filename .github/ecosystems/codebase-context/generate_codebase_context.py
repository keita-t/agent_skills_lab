#!/usr/bin/env python3
"""Generate a CODEBASE_CONTEXT.md snapshot for large-context models."""

from __future__ import annotations

import argparse
import fnmatch
import os
from pathlib import Path
from pathlib import PurePosixPath
import subprocess
import sys

DEFAULT_OUTPUT_NAME = "CODEBASE_CONTEXT.md"
DEFAULT_INDEX_DEPTH = 4
EXCLUDED_DIR_NAMES = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    "out",
    "target",
    "coverage",
    "htmlcov",
    ".pytest_cache",
    ".mypy_cache",
    ".tox",
    ".nox",
}
HIGH_SIGNAL_AUXILIARY_ROOTS = {".github", "docs"}
HIGH_SIGNAL_AUXILIARY_NAMES = {
    ".dockerignore",
    ".editorconfig",
    ".env.example",
    ".gitattributes",
    ".gitignore",
    ".npmrc",
    "CLAUDE.md",
    "Dockerfile",
    "LICENSE",
    "LICENSE.md",
    "Makefile",
    "README.md",
    "compose.yaml",
    "compose.yml",
    "package-lock.json",
    "package.json",
    "pnpm-lock.yaml",
    "poetry.lock",
    "pyproject.toml",
    "requirements-dev.txt",
    "requirements.txt",
    "uv.lock",
    "yarn.lock",
}
AUXILIARY_SUFFIXES = {
    ".cfg",
    ".conf",
    ".csv",
    ".ini",
    ".json",
    ".lock",
    ".md",
    ".properties",
    ".rst",
    ".toml",
    ".tsv",
    ".txt",
    ".yaml",
    ".yml",
}
LANGUAGE_BY_NAME = {
    "Dockerfile": "dockerfile",
    "Makefile": "makefile",
}
LANGUAGE_BY_SUFFIX = {
    ".bash": "bash",
    ".c": "c",
    ".cc": "cpp",
    ".cpp": "cpp",
    ".css": "css",
    ".go": "go",
    ".h": "c",
    ".hpp": "cpp",
    ".html": "html",
    ".ini": "ini",
    ".java": "java",
    ".js": "javascript",
    ".json": "json",
    ".jsx": "jsx",
    ".kt": "kotlin",
    ".kts": "kotlin",
    ".lua": "lua",
    ".md": "markdown",
    ".php": "php",
    ".pl": "perl",
    ".ps1": "powershell",
    ".py": "python",
    ".rb": "ruby",
    ".rs": "rust",
    ".scala": "scala",
    ".sh": "bash",
    ".sql": "sql",
    ".swift": "swift",
    ".toml": "toml",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".txt": "text",
    ".xml": "xml",
    ".yaml": "yaml",
    ".yml": "yaml",
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a single markdown snapshot of a repository.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        help="Repository root to export. Defaults to the current repository.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output markdown path. Defaults to CODEBASE_CONTEXT.md at the repository root.",
    )
    parser.add_argument(
        "--include",
        action="append",
        default=[],
        metavar="GLOB",
        help="Include only paths matching this glob. Repeat as needed.",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="GLOB",
        help="Exclude paths matching this glob after inclusion rules are applied.",
    )
    parser.add_argument(
        "--auxiliary-policy",
        choices=("auto", "all", "none"),
        default="auto",
        help="How to handle supporting files when --include is not supplied.",
    )
    parser.add_argument(
        "--source-only",
        action="store_true",
        help="Shortcut for --auxiliary-policy none.",
    )
    parser.add_argument(
        "--index-depth",
        type=int,
        default=DEFAULT_INDEX_DEPTH,
        help="Maximum directory depth shown in the index tree.",
    )
    return parser.parse_args(argv)


def discover_repo_root(start: Path) -> Path:
    resolved_start = start.resolve()
    for candidate in [resolved_start, *resolved_start.parents]:
        if (candidate / ".git").exists() or (candidate / ".github").is_dir():
            return candidate
    raise RuntimeError("Could not locate the repository root. Pass --repo-root.")


def resolve_output_path(repo_root: Path, output_arg: Path | None) -> Path:
    if output_arg is None:
        return (repo_root / DEFAULT_OUTPUT_NAME).resolve()
    if output_arg.is_absolute():
        return output_arg.resolve()
    return (repo_root / output_arg).resolve()


def relative_posix_path(path: Path, repo_root: Path) -> str:
    return path.relative_to(repo_root).as_posix()


def should_skip_path(path: Path, repo_root: Path, output_path: Path) -> bool:
    resolved_path = path.resolve()
    if resolved_path == output_path:
        return True
    try:
        relative_path = resolved_path.relative_to(repo_root)
    except ValueError:
        return True
    if any(part in EXCLUDED_DIR_NAMES for part in relative_path.parts[:-1]):
        return True
    return not resolved_path.is_file()


def should_skip_path_for_scope(
    path: Path,
    repo_root: Path,
    output_path: Path,
    include_patterns: list[str],
) -> bool:
    if not should_skip_path(path, repo_root, output_path):
        return False
    if not include_patterns:
        return True

    resolved_path = path.resolve()
    if resolved_path == output_path:
        return True
    try:
        relative_path = relative_posix_path(resolved_path, repo_root)
    except ValueError:
        return True
    if any(part in EXCLUDED_DIR_NAMES for part in resolved_path.relative_to(repo_root).parts[:-1]):
        return not matches_any_pattern(relative_path, include_patterns)
    return not resolved_path.is_file()


def list_repo_files(repo_root: Path, output_path: Path, include_patterns: list[str]) -> list[Path]:
    git_files = list_git_files(repo_root, output_path, include_patterns)
    if git_files is not None:
        return git_files
    return list_fallback_files(repo_root, output_path, include_patterns)


def list_git_files(
    repo_root: Path,
    output_path: Path,
    include_patterns: list[str],
) -> list[Path] | None:
    commands = [
        [
            "git",
            "-C",
            str(repo_root),
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
            "-z",
        ]
    ]
    if include_patterns:
        commands.append(
            [
                "git",
                "-C",
                str(repo_root),
                "ls-files",
                "--others",
                "--ignored",
                "--exclude-standard",
                "-z",
            ]
        )

    files: list[Path] = []
    seen: set[Path] = set()
    try:
        for command in commands:
            result = subprocess.run(
                command,
                capture_output=True,
                check=False,
            )
            if result.returncode != 0:
                return None
            for raw_path in result.stdout.split(b"\0"):
                if not raw_path:
                    continue
                candidate = (repo_root / raw_path.decode("utf-8")).resolve()
                if should_skip_path_for_scope(candidate, repo_root, output_path, include_patterns):
                    continue
                if candidate in seen:
                    continue
                seen.add(candidate)
                files.append(candidate)
    except FileNotFoundError:
        return None

    return sorted(files, key=lambda path: relative_posix_path(path, repo_root))


def list_fallback_files(
    repo_root: Path,
    output_path: Path,
    include_patterns: list[str],
) -> list[Path]:
    files: list[Path] = []
    for current_root, dir_names, file_names in os.walk(repo_root, topdown=True):
        if include_patterns:
            dir_names[:] = sorted(dir_names)
        else:
            dir_names[:] = sorted(
                dir_name for dir_name in dir_names if dir_name not in EXCLUDED_DIR_NAMES
            )
        for file_name in sorted(file_names):
            candidate = (Path(current_root) / file_name).resolve()
            if should_skip_path_for_scope(candidate, repo_root, output_path, include_patterns):
                continue
            files.append(candidate)
    return files


def read_text_file(path: Path) -> str | None:
    raw = path.read_bytes()
    if b"\0" in raw:
        return None
    for encoding in ("utf-8", "utf-8-sig"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return None


def is_auxiliary_file(relative_path: PurePosixPath) -> bool:
    name = relative_path.name
    lower_name = name.lower()
    if name in HIGH_SIGNAL_AUXILIARY_NAMES or lower_name in HIGH_SIGNAL_AUXILIARY_NAMES:
        return True
    if lower_name in {"license", "copying", "notice", "changelog.md"}:
        return True
    return relative_path.suffix.lower() in AUXILIARY_SUFFIXES


def is_useful_auxiliary_file(relative_path: PurePosixPath) -> bool:
    if not is_auxiliary_file(relative_path):
        return False
    if relative_path.name in HIGH_SIGNAL_AUXILIARY_NAMES:
        return True
    if relative_path.parts and relative_path.parts[0] in HIGH_SIGNAL_AUXILIARY_ROOTS:
        return True
    return len(relative_path.parts) <= 2


def matches_any_pattern(relative_path: str, patterns: list[str]) -> bool:
    basename = relative_path.rsplit("/", 1)[-1]
    for pattern in patterns:
        normalized = pattern.replace("\\", "/")
        if normalized.startswith("./"):
            normalized = normalized[2:]
        if normalized.endswith("/") and relative_path.startswith(normalized):
            return True
        if fnmatch.fnmatchcase(relative_path, normalized):
            return True
        if "/" not in normalized and fnmatch.fnmatchcase(basename, normalized):
            return True
    return False


def select_paths(
    text_files: dict[str, str],
    include_patterns: list[str],
    exclude_patterns: list[str],
    auxiliary_policy: str,
) -> list[str]:
    all_paths = sorted(text_files)
    if include_patterns:
        selected = [
            relative_path
            for relative_path in all_paths
            if matches_any_pattern(relative_path, include_patterns)
        ]
    else:
        selected = []
        for relative_path in all_paths:
            pure_path = PurePosixPath(relative_path)
            auxiliary = is_auxiliary_file(pure_path)
            if auxiliary_policy == "all":
                selected.append(relative_path)
                continue
            if auxiliary_policy == "none":
                if not auxiliary:
                    selected.append(relative_path)
                continue
            if not auxiliary or is_useful_auxiliary_file(pure_path):
                selected.append(relative_path)

    if exclude_patterns:
        selected = [
            relative_path
            for relative_path in selected
            if not matches_any_pattern(relative_path, exclude_patterns)
        ]

    return sorted(selected)


def add_tree_path(tree: dict[str, dict], relative_path: str, max_depth: int) -> None:
    parts = relative_path.split("/")
    cursor = tree
    for index, part in enumerate(parts):
        is_last = index == len(parts) - 1
        if index >= max_depth:
            cursor.setdefault("...", {})
            return
        key = part if is_last else f"{part}/"
        cursor = cursor.setdefault(key, {})


def sort_tree_entries(item: tuple[str, dict]) -> tuple[int, str]:
    name = item[0]
    return (0 if name.endswith("/") else 1, name)


def render_tree(tree: dict[str, dict], prefix: str = "") -> list[str]:
    lines: list[str] = []
    entries = sorted(tree.items(), key=sort_tree_entries)
    for index, (name, child) in enumerate(entries):
        last = index == len(entries) - 1
        connector = "└── " if last else "├── "
        lines.append(f"{prefix}{connector}{name}")
        if child:
            child_prefix = f"{prefix}{'    ' if last else '│   '}"
            lines.extend(render_tree(child, child_prefix))
    return lines


def build_index(paths: list[str], max_depth: int) -> str:
    tree: dict[str, dict] = {}
    for relative_path in paths:
        add_tree_path(tree, relative_path, max_depth)
    lines = ["."]
    lines.extend(render_tree(tree))
    return "\n".join(lines)


def longest_backtick_run(text: str) -> int:
    longest = 0
    current = 0
    for character in text:
        if character == "`":
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest


def code_fence(text: str) -> str:
    return "`" * max(3, longest_backtick_run(text) + 1)


def infer_language(relative_path: str) -> str:
    path = PurePosixPath(relative_path)
    if path.name in LANGUAGE_BY_NAME:
        return LANGUAGE_BY_NAME[path.name]
    return LANGUAGE_BY_SUFFIX.get(path.suffix.lower(), "")


def render_codebase_section(selected_paths: list[str], text_files: dict[str, str]) -> str:
    sections: list[str] = []
    for relative_path in selected_paths:
        content = text_files[relative_path]
        fence = code_fence(content)
        language = infer_language(relative_path)
        info_string = language if language else "text"
        sections.append(f"### {relative_path}")
        sections.append(f"{fence}{info_string}")
        sections.append(content.rstrip("\n"))
        sections.append(fence)
    return "\n\n".join(sections)


def build_markdown(index_text: str, codebase_text: str) -> str:
    parts = [
        "【指示】",
        "これから提示するソースコード全体の依存関係を解析し、ユーザーのプロンプトで提示された内容の解決を行ってください。",
        "",
        "【インデックス】",
        "```text",
        index_text,
        "```",
        "",
        "【コードベース】",
        codebase_text,
        "",
        "<small>",
        "",
        "【念押しの指示（最後に小さく）】",
        "以上がコードベースです。上記【指示】に従って、まずは全体の方針から提示してください。",
        "",
        "</small>",
        "",
    ]
    return "\n".join(parts)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = discover_repo_root(args.repo_root or Path.cwd())
    output_path = resolve_output_path(repo_root, args.output)
    auxiliary_policy = "none" if args.source_only else args.auxiliary_policy
    if args.index_depth < 1:
        raise RuntimeError("--index-depth must be 1 or greater")

    candidate_paths = list_repo_files(repo_root, output_path, args.include)
    text_files: dict[str, str] = {}
    for path in candidate_paths:
        content = read_text_file(path)
        if content is None:
            continue
        text_files[relative_posix_path(path, repo_root)] = content

    selected_paths = select_paths(
        text_files,
        include_patterns=args.include,
        exclude_patterns=args.exclude,
        auxiliary_policy=auxiliary_policy,
    )
    if not selected_paths:
        raise RuntimeError("No repository files matched the selected export scope")

    index_text = build_index(selected_paths, args.index_depth)
    codebase_text = render_codebase_section(selected_paths, text_files)
    markdown_text = build_markdown(index_text, codebase_text)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown_text, encoding="utf-8")
    print(f"Wrote {len(selected_paths)} files to {output_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1)