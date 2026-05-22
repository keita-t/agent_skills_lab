#!/usr/bin/env python3
"""Validate cross-links among agents, skills, and routing documents."""

from __future__ import annotations

import re
from pathlib import Path
import sys

ECOSYSTEMS_DIR = Path(__file__).resolve().parents[1]
if str(ECOSYSTEMS_DIR) not in sys.path:
    sys.path.insert(0, str(ECOSYSTEMS_DIR))

try:
    from mcp_models import ValidateAgentSkillDocsInput, ValidationIssue, ValidationResult
except ModuleNotFoundError:
    from dataclasses import dataclass, field

    @dataclass(frozen=True)
    class ValidateAgentSkillDocsInput:
        repo_root: str = "."

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


def _normalize_target(target: str) -> str:
    no_fragment = target.split("#", 1)[0]
    no_query = no_fragment.split("?", 1)[0]
    return no_query.strip()


def _extract_link_targets(path: Path) -> tuple[list[str], str]:
    text = path.read_text(encoding="utf-8")
    targets = [_normalize_target(match) for match in LINK_RE.findall(text)]
    return targets, text


def _find_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / ".github" / "agents").is_dir() and (
            candidate / ".github" / "skills"
        ).is_dir():
            return candidate
    raise RuntimeError("Could not locate repository root from script path")


def _actual_agents(agents_dir: Path) -> set[str]:
    return {path.name for path in agents_dir.glob("*.agent.md") if path.is_file()}


def _actual_skills(skills_dir: Path) -> set[str]:
    slugs: set[str] = set()
    for child in skills_dir.iterdir():
        if child.is_dir() and (child / "SKILL.md").is_file():
            slugs.add(child.name)
    return slugs


def _agents_from_readme(readme_path: Path) -> set[str]:
    targets, _ = _extract_link_targets(readme_path)
    return {Path(target).name for target in targets if target.endswith(".agent.md")}


def _skills_from_readme(readme_path: Path) -> set[str]:
    targets, _ = _extract_link_targets(readme_path)
    slugs: set[str] = set()
    for target in targets:
        path = Path(target)
        if path.name == "SKILL.md" and len(path.parts) >= 2:
            slugs.add(path.parts[-2])
    return slugs


def _agents_from_routing(routing_path: Path) -> set[str]:
    targets, _ = _extract_link_targets(routing_path)
    return {Path(target).name for target in targets if target.endswith(".agent.md")}


def _skills_from_routing(routing_path: Path) -> set[str]:
    targets, _ = _extract_link_targets(routing_path)
    slugs: set[str] = set()
    for target in targets:
        path = Path(target)
        if path.name == "SKILL.md" and len(path.parts) >= 2:
            slugs.add(path.parts[-2])
    return slugs


def _required_links_present(text: str, required_targets: list[str]) -> list[str]:
    missing: list[str] = []
    for target in required_targets:
        if f"({target})" not in text:
            missing.append(target)
    return missing


def _format_values(values: set[str]) -> str:
    return ", ".join(sorted(values)) if values else "(none)"


def validate_agent_skill_docs(request: ValidateAgentSkillDocsInput) -> ValidationResult:
    repo_root = _find_repo_root(Path(request.repo_root).resolve())

    agents_dir = repo_root / ".github" / "agents"
    skills_dir = repo_root / ".github" / "skills"

    agents_readme = agents_dir / "README.md"
    skills_readme = skills_dir / "README.md"
    routing_doc = repo_root / ".github" / "AGENT_SKILL_ROUTING.md"

    errors: list[str] = []

    actual_agents = _actual_agents(agents_dir)
    actual_skills = _actual_skills(skills_dir)

    listed_agents = _agents_from_readme(agents_readme)
    listed_skills = _skills_from_readme(skills_readme)

    routed_agents = _agents_from_routing(routing_doc)
    routed_skills = _skills_from_routing(routing_doc)

    missing_in_agents_readme = actual_agents - listed_agents
    stale_in_agents_readme = listed_agents - actual_agents
    if missing_in_agents_readme:
        errors.append(
            "agents/README.md is missing agent entries: "
            + _format_values(missing_in_agents_readme)
        )
    if stale_in_agents_readme:
        errors.append(
            "agents/README.md has stale agent entries: "
            + _format_values(stale_in_agents_readme)
        )

    missing_in_skills_readme = actual_skills - listed_skills
    stale_in_skills_readme = listed_skills - actual_skills
    if missing_in_skills_readme:
        errors.append(
            "skills/README.md is missing skill entries: "
            + _format_values(missing_in_skills_readme)
        )
    if stale_in_skills_readme:
        errors.append(
            "skills/README.md has stale skill entries: "
            + _format_values(stale_in_skills_readme)
        )

    missing_in_routing_agents = actual_agents - routed_agents
    stale_in_routing_agents = routed_agents - actual_agents
    if missing_in_routing_agents:
        errors.append(
            "AGENT_SKILL_ROUTING.md is missing agent rows: "
            + _format_values(missing_in_routing_agents)
        )
    if stale_in_routing_agents:
        errors.append(
            "AGENT_SKILL_ROUTING.md has stale agent rows: "
            + _format_values(stale_in_routing_agents)
        )

    missing_in_routing_skills = actual_skills - routed_skills
    stale_in_routing_skills = routed_skills - actual_skills
    if missing_in_routing_skills:
        errors.append(
            "AGENT_SKILL_ROUTING.md is missing skill rows: "
            + _format_values(missing_in_routing_skills)
        )
    if stale_in_routing_skills:
        errors.append(
            "AGENT_SKILL_ROUTING.md has stale skill rows: "
            + _format_values(stale_in_routing_skills)
        )

    agents_text = agents_readme.read_text(encoding="utf-8")
    skills_text = skills_readme.read_text(encoding="utf-8")
    routing_text = routing_doc.read_text(encoding="utf-8")

    missing_agents_links = _required_links_present(
        agents_text,
        [
            "../skills/README.md",
            "../AGENT_SKILL_ROUTING.md",
            "../ECOSYSTEM_REGISTRY.md",
            "../ecosystems/README.md",
        ],
    )
    if missing_agents_links:
        errors.append(
            "agents/README.md is missing navigation links: "
            + _format_values(set(missing_agents_links))
        )

    missing_skills_links = _required_links_present(
        skills_text,
        [
            "../agents/README.md",
            "../AGENT_SKILL_ROUTING.md",
            "../ECOSYSTEM_REGISTRY.md",
            "../ecosystems/README.md",
        ],
    )
    if missing_skills_links:
        errors.append(
            "skills/README.md is missing navigation links: "
            + _format_values(set(missing_skills_links))
        )

    missing_routing_links = _required_links_present(
        routing_text,
        [
            "agents/README.md",
            "skills/README.md",
            "ECOSYSTEM_REGISTRY.md",
            "ecosystems/README.md",
        ],
    )
    if missing_routing_links:
        errors.append(
            "AGENT_SKILL_ROUTING.md is missing navigation links: "
            + _format_values(set(missing_routing_links))
        )

    return ValidationResult(
        passed=not errors,
        errors=[ValidationIssue(message=error) for error in errors],
    )


def main() -> int:
    result = validate_agent_skill_docs(
        ValidateAgentSkillDocsInput(repo_root=str(_find_repo_root(Path(__file__).resolve())))
    )

    if not result.passed:
        print("AGENT/SKILL DOC VALIDATION FAILED")
        for index, error in enumerate(result.errors, start=1):
            print(f"{index}. {error.message}")
        print("Fix the missing or stale entries in:")
        print("- .github/agents/README.md")
        print("- .github/skills/README.md")
        print("- .github/AGENT_SKILL_ROUTING.md")
        return 1

    print("AGENT/SKILL DOC VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())