#!/usr/bin/env python3
"""Generate a CODEBASE_CONTEXT.md snapshot for large-context models."""

from __future__ import annotations

import argparse
import ast
import fnmatch
import math
import os
from pathlib import Path
from pathlib import PurePosixPath
import re
import subprocess
import sys

DEFAULT_OUTPUT_NAME = "CODEBASE_CONTEXT.md"
DEFAULT_INDEX_DEPTH = 4
TOKEN_CHAR_RATIO = 4
DEFAULT_SMART_BUDGET = "medium"
SMART_BUDGET_TOKENS = {
    "low": 50_000,
    "medium": 150_000,
    "high": 500_000,
}
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
_OUTPUT_TEMPLATES: dict[str, dict[str, str]] = {
    "ja": {
        "instruction_header": "【指示】",
        "instruction_body": "これから提示するソースコード全体の依存関係を解析し、ユーザーのプロンプトで提示された内容の解決を行ってください。",
        "index_header": "【インデックス】",
        "codebase_header": "【コードベース】",
        "reminder_header": "【念押しの指示】",
        "reminder_body": "以上がコードベースです。上記【指示】に従って、まずは全体の方針から提示してください。",
    },
    "en": {
        "instruction_header": "[Instructions]",
        "instruction_body": "Analyse the full dependency graph of the codebase shown below and resolve the task described in the user prompt.",
        "index_header": "[Index]",
        "codebase_header": "[Codebase]",
        "reminder_header": "[Reminder]",
        "reminder_body": "The full codebase is above. Following the [Instructions], start by describing your overall approach before diving into changes.",
    },
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
    parser.add_argument(
        "--output-lang",
        choices=tuple(_OUTPUT_TEMPLATES),
        default="ja",
        help="Language of the output headers and instructions (default: ja).",
    )
    parser.add_argument(
        "--mode",
        choices=("simple", "smart"),
        help="Export mode. Defaults to simple unless --budget or --task is supplied.",
    )
    parser.add_argument(
        "--budget",
        choices=tuple(SMART_BUDGET_TOKENS),
        help="Smart mode token budget preset: low, medium, or high.",
    )
    parser.add_argument(
        "--task",
        help="Optional task description used by smart mode to prioritize files.",
    )
    return parser.parse_args(argv)


def resolve_export_mode(args: argparse.Namespace) -> tuple[str, str | None]:
    mode = args.mode
    smart_hint = args.budget is not None or args.task is not None
    if mode is None:
        mode = "smart" if smart_hint else "simple"
    if mode == "simple" and smart_hint:
        raise RuntimeError("--budget and --task are only supported with --mode smart")
    budget = args.budget
    if mode == "smart" and budget is None:
        budget = DEFAULT_SMART_BUDGET
    return mode, budget


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


def is_zero_trust_sensitive_file(relative_path: PurePosixPath) -> bool:
    name = relative_path.name
    return name == ".env" or (name.startswith(".env.") and name != ".env.example")


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
    if is_zero_trust_sensitive_file(PurePosixPath(relative_path.as_posix())):
        return True
    return not resolved_path.is_file()


def should_skip_path_for_scope(
    path: Path,
    repo_root: Path,
    output_path: Path,
    include_patterns: list[str],
    exclude_patterns: list[str],
) -> bool:
    if should_skip_path(path, repo_root, output_path):
        return True
    relative_path = relative_posix_path(path.resolve(), repo_root)
    if exclude_patterns and matches_any_pattern(relative_path, exclude_patterns):
        return True
    if not include_patterns:
        return False
    return not matches_any_pattern(relative_path, include_patterns)


def list_repo_files(
    repo_root: Path,
    output_path: Path,
    include_patterns: list[str],
    exclude_patterns: list[str],
) -> list[Path]:
    git_files = list_git_files(repo_root, output_path, include_patterns, exclude_patterns)
    if git_files is not None:
        return git_files
    return list_fallback_files(repo_root, output_path, include_patterns, exclude_patterns)


def list_git_files(
    repo_root: Path,
    output_path: Path,
    include_patterns: list[str],
    exclude_patterns: list[str],
) -> list[Path] | None:
    files: list[Path] = []
    seen: set[Path] = set()
    try:
        commands = [
            [
                "git",
                "-C",
                str(repo_root),
                "ls-files",
                "--cached",
                "-z",
            ]
        ]
        # Only scan untracked files when the caller explicitly narrowed the scope
        # with --include. In that case the user is targeting specific paths and
        # should see newly-created files that match before they are committed.
        # Without --include the export covers the full repository; adding untracked
        # files there would introduce workspace noise (build artifacts, temp files)
        # that git intentionally omits from its committed file set.
        if include_patterns:
            commands.append(
                [
                    "git",
                    "-C",
                    str(repo_root),
                    "ls-files",
                    "--others",
                    "--exclude-standard",
                    "-z",
                ]
            )
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
                if should_skip_path_for_scope(
                    candidate,
                    repo_root,
                    output_path,
                    include_patterns,
                    exclude_patterns,
                ):
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
    exclude_patterns: list[str],
) -> list[Path]:
    files: list[Path] = []
    for current_root, dir_names, file_names in os.walk(repo_root, topdown=True):
        current_root_path = Path(current_root).resolve()
        if include_patterns:
            dir_names[:] = sorted(
                dir_name
                for dir_name in dir_names
                if should_descend_into_directory(
                    relative_posix_path(current_root_path / dir_name, repo_root),
                    include_patterns,
                )
            )
        else:
            dir_names[:] = sorted(
                dir_name for dir_name in dir_names if dir_name not in EXCLUDED_DIR_NAMES
            )
        for file_name in sorted(file_names):
            candidate = (Path(current_root) / file_name).resolve()
            if should_skip_path_for_scope(
                candidate,
                repo_root,
                output_path,
                include_patterns,
                exclude_patterns,
            ):
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


def pattern_could_match_under_directory(directory_parts: list[str], pattern: str) -> bool:
    pattern_parts = pattern.split("/")
    for index, directory_part in enumerate(directory_parts):
        if index >= len(pattern_parts):
            return False
        pattern_part = pattern_parts[index]
        if pattern_part == "**":
            return True
        if not fnmatch.fnmatchcase(directory_part, pattern_part):
            return False
    return True


def should_descend_into_directory(relative_path: str, patterns: list[str]) -> bool:
    normalized_path = relative_path.strip("/")
    if not normalized_path:
        return True

    basename = normalized_path.rsplit("/", 1)[-1]
    if basename in EXCLUDED_DIR_NAMES:
        return False
    if not patterns:
        return True

    directory_parts = normalized_path.split("/")
    for pattern in patterns:
        normalized_pattern = pattern.replace("\\", "/")
        if normalized_pattern.startswith("./"):
            normalized_pattern = normalized_pattern[2:]
        if normalized_pattern.endswith("/"):
            normalized_pattern = f"{normalized_pattern}**"
        else:
            normalized_pattern = normalized_pattern.rstrip("/")
        if not normalized_pattern:
            return True
        if "/" not in normalized_pattern:
            return True
        if pattern_could_match_under_directory(directory_parts, normalized_pattern):
            return True
    return False


def select_paths(
    text_files: dict[str, str],
    has_include_scope: bool,
    auxiliary_policy: str,
) -> list[str]:
    # list_repo_files already applied include/exclude pattern filtering.
    # This function is responsible solely for auxiliary-file policy: when the
    # caller did not supply --include, decide which supporting files to keep.
    all_paths = sorted(text_files)
    if has_include_scope:
        # Explicit scope provided — all candidates are already include-filtered
        # upstream, so return them as-is regardless of auxiliary status.
        return all_paths
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


def render_file_section(relative_path: str, content: str) -> str:
    fence = code_fence(content)
    language = infer_language(relative_path)
    info_string = language if language else "text"
    return "\n".join(
        [
            f"### {relative_path}",
            f"{fence}{info_string}",
            content.rstrip("\n"),
            fence,
        ]
    )


def render_codebase_section(selected_paths: list[str], text_files: dict[str, str]) -> str:
    sections: list[str] = []
    for relative_path in selected_paths:
        sections.append(render_file_section(relative_path, text_files[relative_path]))
    return "\n\n".join(sections)


def build_markdown(index_text: str, codebase_text: str, lang: str = "ja") -> str:
    t = _OUTPUT_TEMPLATES[lang]
    parts = [
        t["instruction_header"],
        t["instruction_body"],
        "",
        t["index_header"],
        "```text",
        index_text,
        "```",
        "",
        t["codebase_header"],
        codebase_text,
        "",
        "<small>",
        "",
        t["reminder_header"],
        t["reminder_body"],
        "",
        "</small>",
        "",
    ]
    return "\n".join(parts)


def estimate_tokens(text: str) -> int:
    return max(1, math.ceil(len(text) / TOKEN_CHAR_RATIO))


def estimate_section_separator_tokens(section_count: int) -> int:
    if section_count <= 1:
        return 0
    return (section_count - 1) * estimate_tokens("\n\n")


def estimate_index_path_tokens(relative_path: str, index_depth: int) -> int:
    parts = relative_path.split("/")
    visible_parts = parts[:index_depth]
    if len(parts) > index_depth:
        visible_parts.append("...")
    # Add a small connector/indent allowance per rendered tree line. Directory
    # lines are shared in the real index, so summing each path is conservative.
    estimated_characters = sum(len(part) + 8 for part in visible_parts)
    return estimate_tokens("x" * estimated_characters)


def tokenize_task(task: str | None) -> set[str]:
    if not task:
        return set()
    return {
        token
        for token in re.findall(r"[A-Za-z0-9_]{3,}", task.lower())
        if not token.isdigit()
    }


def git_status_paths(repo_root: Path) -> set[str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), "status", "--short"],
            capture_output=True,
            check=False,
            text=True,
        )
    except FileNotFoundError:
        return set()
    if result.returncode != 0:
        return set()

    paths: set[str] = set()
    for line in result.stdout.splitlines():
        if len(line) < 4:
            continue
        path_text = line[3:]
        if " -> " in path_text:
            path_text = path_text.rsplit(" -> ", 1)[-1]
        paths.add(path_text)
    return paths


def is_source_file(relative_path: str) -> bool:
    suffix = PurePosixPath(relative_path).suffix.lower()
    return suffix in LANGUAGE_BY_SUFFIX and suffix not in AUXILIARY_SUFFIXES


def score_smart_relevance(
    relative_path: str,
    content: str,
    task_tokens: set[str],
    changed_paths: set[str],
    explicit_include: bool,
) -> int:
    score = 0
    path_lower = relative_path.lower()
    name_lower = PurePosixPath(relative_path).name.lower()
    content_sample = content[:4_000].lower()

    if explicit_include:
        score += 80
    if relative_path in changed_paths:
        score += 60
    if is_source_file(relative_path):
        score += 10
    elif is_useful_auxiliary_file(PurePosixPath(relative_path)):
        score += 4

    for token in task_tokens:
        if token in path_lower:
            score += 30
        if token in name_lower:
            score += 20
        if token in content_sample:
            score += 8

    return score


def source_segment_line(source: str, node: ast.AST) -> str | None:
    segment = ast.get_source_segment(source, node)
    if segment is None:
        return None
    first_line = segment.strip().splitlines()[0].rstrip()
    return first_line


def render_python_stub(relative_path: str, content: str) -> str:
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return render_generic_stub(relative_path, content)

    lines = ["# Smart mode stub: signatures only."]
    imports: list[str] = []
    declarations: list[str] = []

    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            line = source_segment_line(content, node)
            if line:
                imports.append(line)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            line = source_segment_line(content, node)
            if line:
                declarations.append(line)
        elif isinstance(node, ast.ClassDef):
            line = source_segment_line(content, node)
            if line:
                declarations.append(line)
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    child_line = source_segment_line(content, child)
                    if child_line:
                        declarations.append(f"    {child_line}")

    lines.extend(imports[:40])
    if imports and declarations:
        lines.append("")
    lines.extend(declarations[:160])
    if len(imports) > 40 or len(declarations) > 160:
        lines.append("# ...")
    if len(lines) == 1:
        lines.extend(content.strip().splitlines()[:80])
    return "\n".join(lines).rstrip() + "\n"


GENERIC_DECLARATION_PATTERN = re.compile(
    r"^\s*(?:"
    r"(?:export\s+)?(?:abstract\s+)?(?:class|interface|type|enum|function|const|let|var)\b|"
    r"(?:public|private|protected|internal|static|final|open|data|sealed|fun)\b|"
    r"(?:def|class)\b|"
    r"(?:package|import|from|use|mod)\b"
    r")"
)


def render_generic_stub(relative_path: str, content: str) -> str:
    lines = ["// Smart mode stub: signatures only."]
    matched_lines = [
        line.rstrip()
        for line in content.splitlines()
        if GENERIC_DECLARATION_PATTERN.match(line)
    ]
    if matched_lines:
        lines.extend(matched_lines[:220])
        if len(matched_lines) > 220:
            lines.append("// ...")
    else:
        lines.append("// No lightweight signatures detected; showing leading excerpt.")
        lines.extend(content.strip().splitlines()[:80])
    return "\n".join(lines).rstrip() + "\n"


def render_stub_content(relative_path: str, content: str) -> str:
    if PurePosixPath(relative_path).suffix.lower() == ".py":
        return render_python_stub(relative_path, content)
    return render_generic_stub(relative_path, content)


def minimum_smart_markdown_tokens(
    selected_paths: list[str],
    stub_sections: dict[str, str],
    output_lang: str,
    index_depth: int,
) -> int:
    index_text = build_index(selected_paths, index_depth)
    codebase_text = "\n\n".join(stub_sections[path] for path in selected_paths)
    return estimate_tokens(build_markdown(index_text, codebase_text, lang=output_lang))


def base_empty_smart_markdown_tokens(output_lang: str) -> int:
    return estimate_tokens(build_markdown(".", "", lang=output_lang))


def estimate_additive_smart_markdown_tokens(
    selected_paths: list[str],
    section_tokens: dict[str, int],
    index_path_tokens: dict[str, int],
    output_lang: str,
) -> int:
    return (
        base_empty_smart_markdown_tokens(output_lang)
        + sum(index_path_tokens[path] for path in selected_paths)
        + estimate_section_separator_tokens(len(selected_paths))
        + sum(section_tokens[path] for path in selected_paths)
    )


def render_smart_codebase(
    selected_paths: list[str],
    text_files: dict[str, str],
    repo_root: Path,
    task: str | None,
    budget_name: str,
    output_lang: str,
    index_depth: int,
    explicit_include: bool,
) -> tuple[list[str], str]:
    budget_tokens = SMART_BUDGET_TOKENS[budget_name]
    task_tokens = tokenize_task(task)
    changed_paths = git_status_paths(repo_root)

    full_sections = {
        relative_path: render_file_section(relative_path, text_files[relative_path])
        for relative_path in selected_paths
    }
    stub_sections = {
        relative_path: render_file_section(
            relative_path,
            render_stub_content(relative_path, text_files[relative_path]),
        )
        for relative_path in selected_paths
    }
    full_section_tokens = {
        relative_path: estimate_tokens(section)
        for relative_path, section in full_sections.items()
    }
    stub_section_tokens = {
        relative_path: estimate_tokens(section)
        for relative_path, section in stub_sections.items()
    }
    index_path_tokens = {
        relative_path: estimate_index_path_tokens(relative_path, index_depth)
        for relative_path in selected_paths
    }

    required_paths = set(selected_paths) if explicit_include else set()
    scored_paths = sorted(
        selected_paths,
        key=lambda path: (
            -score_smart_relevance(
                path,
                text_files[path],
                task_tokens,
                changed_paths,
                path in required_paths,
            ),
            path,
        ),
    )

    if explicit_include:
        minimum_tokens = minimum_smart_markdown_tokens(
            selected_paths,
            stub_sections,
            output_lang,
            index_depth,
        )
        if minimum_tokens > budget_tokens:
            raise RuntimeError(
                "Smart mode budget is too small to include all explicitly selected files as stubs"
            )

    selected_representations: dict[str, str] = {}
    selected_estimated_tokens = base_empty_smart_markdown_tokens(output_lang)
    selected_section_count = 0

    if explicit_include:
        selected_representations = {
            relative_path: stub_sections[relative_path]
            for relative_path in selected_paths
        }
        selected_estimated_tokens = estimate_additive_smart_markdown_tokens(
            selected_paths,
            stub_section_tokens,
            index_path_tokens,
            output_lang,
        )
        selected_section_count = len(selected_representations)

    for relative_path in scored_paths:
        if relative_path in selected_representations:
            token_delta = (
                full_section_tokens[relative_path] - stub_section_tokens[relative_path]
            )
            if selected_estimated_tokens + token_delta <= budget_tokens:
                selected_representations[relative_path] = full_sections[relative_path]
                selected_estimated_tokens += token_delta
            continue

        separator_tokens = estimate_section_separator_tokens(selected_section_count + 1) - (
            estimate_section_separator_tokens(selected_section_count)
        )
        full_candidate_tokens = (
            selected_estimated_tokens
            + index_path_tokens[relative_path]
            + separator_tokens
            + full_section_tokens[relative_path]
        )
        if full_candidate_tokens <= budget_tokens:
            selected_representations[relative_path] = full_sections[relative_path]
            selected_estimated_tokens = full_candidate_tokens
            selected_section_count += 1
            continue

        stub_candidate_tokens = (
            selected_estimated_tokens
            + index_path_tokens[relative_path]
            + separator_tokens
            + stub_section_tokens[relative_path]
        )
        if stub_candidate_tokens <= budget_tokens:
            selected_representations[relative_path] = stub_sections[relative_path]
            selected_estimated_tokens = stub_candidate_tokens
            selected_section_count += 1
            continue

        if relative_path in required_paths:
            raise RuntimeError(
                "Smart mode budget is too small to include an explicitly selected file as a stub"
            )

    final_paths = sorted(selected_representations)
    if not final_paths:
        raise RuntimeError("No repository files fit within the selected smart mode budget")
    codebase_text = "\n\n".join(selected_representations[path] for path in final_paths)
    return final_paths, codebase_text


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    mode, budget = resolve_export_mode(args)
    repo_root = discover_repo_root(args.repo_root or Path.cwd())
    output_path = resolve_output_path(repo_root, args.output)
    auxiliary_policy = "none" if args.source_only else args.auxiliary_policy
    if args.index_depth < 1:
        raise RuntimeError("--index-depth must be 1 or greater")

    candidate_paths = list_repo_files(repo_root, output_path, args.include, args.exclude)
    text_files: dict[str, str] = {}
    for path in candidate_paths:
        content = read_text_file(path)
        if content is None:
            continue
        text_files[relative_posix_path(path, repo_root)] = content

    selected_paths = select_paths(
        text_files,
        has_include_scope=bool(args.include),
        auxiliary_policy=auxiliary_policy,
    )
    if not selected_paths:
        raise RuntimeError("No repository files matched the selected export scope")

    if mode == "smart":
        assert budget is not None
        selected_paths, codebase_text = render_smart_codebase(
            selected_paths,
            text_files,
            repo_root,
            args.task,
            budget,
            args.output_lang,
            args.index_depth,
            explicit_include=bool(args.include),
        )
    else:
        codebase_text = render_codebase_section(selected_paths, text_files)
    index_text = build_index(selected_paths, args.index_depth)
    markdown_text = build_markdown(index_text, codebase_text, lang=args.output_lang)

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
