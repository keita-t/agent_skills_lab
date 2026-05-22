from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

from ecosystem_lib import (
    find_repo_root,
    load_agent_metadata,
    load_ecosystem_manifests,
    load_skill_metadata,
)
from mcp_tool_registry import load_tool_registry

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


LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def extract_targets(path: Path) -> set[str]:
    if not path.is_file():
        return set()
    text = path.read_text(encoding="utf-8")
    targets = set()
    for match in LINK_RE.findall(text):
        targets.add(match.split("#", 1)[0].split("?", 1)[0].strip())
    return targets


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
    registry_path = repo_root / ".github" / "ECOSYSTEM_REGISTRY.md"
    ecosystems_readme = repo_root / ".github" / "ecosystems" / "README.md"
    routing_path = repo_root / ".github" / "AGENT_SKILL_ROUTING.md"
    agents_readme = repo_root / ".github" / "agents" / "README.md"
    skills_readme = repo_root / ".github" / "skills" / "README.md"

    manifests = load_ecosystem_manifests(repo_root)
    agents = load_agent_metadata(repo_root)
    skills = load_skill_metadata(repo_root)
    errors: list[str] = []

    if not registry_path.is_file():
        errors.append("Missing required file: .github/ECOSYSTEM_REGISTRY.md")
    if not ecosystems_readme.is_file():
        errors.append("Missing required file: .github/ecosystems/README.md")

    registry_targets = extract_targets(registry_path)
    ecosystems_targets = extract_targets(ecosystems_readme)
    routing_targets = extract_targets(routing_path)
    agents_targets = extract_targets(agents_readme)
    skills_targets = extract_targets(skills_readme)

    if "ecosystems/README.md" not in registry_targets:
        errors.append(".github/ECOSYSTEM_REGISTRY.md is missing link target: ecosystems/README.md")
    if "../ECOSYSTEM_REGISTRY.md" not in ecosystems_targets:
        errors.append(".github/ecosystems/README.md is missing link target: ../ECOSYSTEM_REGISTRY.md")
    if "ECOSYSTEM_REGISTRY.md" not in routing_targets:
        errors.append(".github/AGENT_SKILL_ROUTING.md is missing link target: ECOSYSTEM_REGISTRY.md")
    if "ecosystems/README.md" not in routing_targets:
        errors.append(".github/AGENT_SKILL_ROUTING.md is missing link target: ecosystems/README.md")
    if "../ECOSYSTEM_REGISTRY.md" not in agents_targets:
        errors.append(".github/agents/README.md is missing link target: ../ECOSYSTEM_REGISTRY.md")
    if "../ecosystems/README.md" not in agents_targets:
        errors.append(".github/agents/README.md is missing link target: ../ecosystems/README.md")
    if "../ECOSYSTEM_REGISTRY.md" not in skills_targets:
        errors.append(".github/skills/README.md is missing link target: ../ECOSYSTEM_REGISTRY.md")
    if "../ecosystems/README.md" not in skills_targets:
        errors.append(".github/skills/README.md is missing link target: ../ecosystems/README.md")

    manifests_by_slug = {manifest.slug: manifest for manifest in manifests}
    for manifest in manifests:
        expected_registry_target = f"ecosystems/{manifest.slug}/ECOSYSTEM.md"
        expected_ecosystems_target = f"{manifest.slug}/ECOSYSTEM.md"
        expected_routing_target = f"ecosystems/{manifest.slug}/ECOSYSTEM.md"

        if manifest.slug != manifest.manifest_path.parent.name:
            errors.append(
                f"Manifest slug does not match directory name: {manifest.manifest_path}"
            )
        if expected_registry_target not in registry_targets:
            errors.append(
                f".github/ECOSYSTEM_REGISTRY.md is missing manifest link: {expected_registry_target}"
            )
        if expected_ecosystems_target not in ecosystems_targets:
            errors.append(
                f".github/ecosystems/README.md is missing manifest link: {expected_ecosystems_target}"
            )
        if expected_routing_target not in routing_targets:
            errors.append(
                f".github/AGENT_SKILL_ROUTING.md is missing manifest link: {expected_routing_target}"
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

        if manifest.post_install_validator and manifest.post_install_validator not in manifest.ecosystem_files:
            errors.append(
                f"Ecosystem {manifest.slug} post-install validator must be listed in ecosystem-files: {manifest.post_install_validator}"
            )

        if manifest.mcp_enabled:
            if not manifest.mcp_tool_registry:
                errors.append(
                    f"Ecosystem {manifest.slug} has mcp-enabled but no mcp-tool-registry"
                )
            else:
                tool_registry_path = repo_root / manifest.mcp_tool_registry
                if not tool_registry_path.is_file():
                    errors.append(
                        f"Ecosystem {manifest.slug} references missing MCP tool registry: {manifest.mcp_tool_registry}"
                    )
                else:
                    try:
                        registry = load_tool_registry(tool_registry_path)
                    except Exception as exc:
                        errors.append(
                            f"Ecosystem {manifest.slug} has invalid MCP tool registry {manifest.mcp_tool_registry}: {exc}"
                        )
                    else:
                        if set(manifest.mcp_tool_names) != set(registry.qualified_tool_names()):
                            errors.append(
                                f"Ecosystem {manifest.slug} mcp-tool-names do not match {manifest.mcp_tool_registry}"
                            )
        elif manifest.mcp_tool_registry or manifest.mcp_tool_names or manifest.mcp_tool_groups:
            errors.append(
                f"Ecosystem {manifest.slug} declares MCP metadata without mcp-enabled: true"
            )

        relation_agents = set(manifest.agent_skill_relations)
        if relation_agents != set(manifest.agents):
            errors.append(
                f"Ecosystem {manifest.slug} relation map does not cover the same agent set as the manifest"
            )

        related_skills = {skill for values in manifest.agent_skill_relations.values() for skill in values}
        if related_skills != set(manifest.skills):
            errors.append(
                f"Ecosystem {manifest.slug} relation map does not cover the same skill set as the manifest"
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