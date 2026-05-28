from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from ecosystem_lib import (
    find_repo_root,
    load_agent_metadata,
    load_ecosystem_manifests,
    load_skill_metadata,
)

try:
    from mcp_models import ValidateRegistryInput, ValidationIssue, ValidationResult
except ModuleNotFoundError:
    @dataclass(frozen=True)
    class ValidateRegistryInput:
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


def detect_cycle(graph: dict[str, list[str]]) -> list[str] | None:
    visited: set[str] = set()
    visiting: set[str] = set()
    stack: list[str] = []

    def walk(node: str) -> list[str] | None:
        visited.add(node)
        visiting.add(node)
        stack.append(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                cycle = walk(neighbor)
                if cycle:
                    return cycle
            elif neighbor in visiting:
                start_index = stack.index(neighbor)
                return stack[start_index:] + [neighbor]
        visiting.remove(node)
        stack.pop()
        return None

    for node in sorted(graph):
        if node not in visited:
            cycle = walk(node)
            if cycle:
                return cycle
    return None


def validate_registry(request: ValidateRegistryInput) -> ValidationResult:
    repo_root = find_repo_root(Path(request.repo_root).resolve())
    manifests = load_ecosystem_manifests(repo_root)
    agents = load_agent_metadata(repo_root)
    skills = load_skill_metadata(repo_root)
    errors: list[str] = []

    if not manifests:
        errors.append("No ecosystem manifests found under .github/ecosystems")

    manifests_by_slug = {manifest.slug: manifest for manifest in manifests}
    for manifest in manifests:
        if manifest.slug != manifest.manifest_path.parent.name:
            errors.append(
                f"Manifest slug does not match directory name: {manifest.manifest_path}"
            )

        if manifest.root_agent not in manifest.agents:
            errors.append(
                f"Ecosystem {manifest.slug} root agent is not listed in agents: {manifest.root_agent}"
            )

        for rel_path in manifest.ecosystem_files:
            if not (repo_root / rel_path).exists():
                errors.append(
                    f"Ecosystem {manifest.slug} references missing ecosystem file: {rel_path}"
                )

        for agent in manifest.agents:
            if agent not in agents:
                errors.append(f"Manifest {manifest.slug} references missing agent: {agent}")
                continue
            if agents[agent].get("ecosystem") != manifest.slug:
                errors.append(
                    f"Agent {agent} has ecosystem {agents[agent].get('ecosystem')} but manifest expects {manifest.slug}"
                )

        for skill in manifest.skills:
            if skill not in skills:
                errors.append(f"Manifest {manifest.slug} references missing skill: {skill}")
                continue
            if skills[skill].get("ecosystem") != manifest.slug:
                errors.append(
                    f"Skill {skill} has ecosystem {skills[skill].get('ecosystem')} but manifest expects {manifest.slug}"
                )

        for dependency in manifest.dependencies:
            if dependency not in manifests_by_slug:
                errors.append(
                    f"Ecosystem {manifest.slug} references unknown dependency: {dependency}"
                )

    for agent_name, metadata in sorted(agents.items()):
        ecosystem = metadata.get("ecosystem")
        if not ecosystem:
            errors.append(f"Agent is missing ecosystem frontmatter: {agent_name}")
            continue
        if ecosystem not in manifests_by_slug:
            errors.append(f"Agent {agent_name} references unknown ecosystem: {ecosystem}")
            continue
        if agent_name not in manifests_by_slug[str(ecosystem)].agents:
            errors.append(
                f"Agent {agent_name} is not listed in manifest {ecosystem}"
            )

    for skill_name, metadata in sorted(skills.items()):
        ecosystem = metadata.get("ecosystem")
        if not ecosystem:
            errors.append(f"Skill is missing ecosystem frontmatter: {skill_name}")
            continue
        if ecosystem not in manifests_by_slug:
            errors.append(f"Skill {skill_name} references unknown ecosystem: {ecosystem}")
            continue
        if skill_name not in manifests_by_slug[str(ecosystem)].skills:
            errors.append(
                f"Skill {skill_name} is not listed in manifest {ecosystem}"
            )

    dependency_graph = {
        manifest.slug: [dependency for dependency in manifest.dependencies]
        for manifest in manifests
    }
    cycle = detect_cycle(dependency_graph)
    if cycle:
        errors.append("Circular ecosystem dependency detected: " + " -> ".join(cycle))

    return ValidationResult(
        passed=not errors,
        errors=[ValidationIssue(message=error) for error in errors],
    )