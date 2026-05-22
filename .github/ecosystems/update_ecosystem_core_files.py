#!/usr/bin/env python3
"""Generate or update ecosystem-managed core files in a target repository."""

from __future__ import annotations

import argparse
from pathlib import Path

from ecosystem_lib import (
    find_repo_root,
    invert_agent_skill_relations,
    load_agent_metadata,
    load_ecosystem_manifests,
    load_skill_metadata,
    write_managed_markdown,
)


def _agent_link(name: str) -> str:
    return f"[{name}](agents/{name})"


def _skill_link(slug: str) -> str:
    return f"[{slug}](skills/{slug}/SKILL.md)"


def _ecosystem_link(slug: str) -> str:
    return f"[{slug}](ecosystems/{slug}/ECOSYSTEM.md)"


def render_registry(manifests) -> str:
    lines = [
        "# Ecosystem Registry",
        "",
        "This document is the canonical inventory of ecosystems installed in this repository.",
        "",
        "## Navigation",
        "- Ecosystems classification: [ecosystems/README.md](ecosystems/README.md)",
        "- Agents-skills routing map: [AGENT_SKILL_ROUTING.md](AGENT_SKILL_ROUTING.md)",
        "- Agents classification: [agents/README.md](agents/README.md)",
        "- Skills classification: [skills/README.md](skills/README.md)",
        "",
        "## Ecosystem Inventory",
        "",
        "| Ecosystem | Root Agent | Skills | Status | Notes |",
        "|---|---|---|---|---|",
    ]
    for manifest in manifests:
        skills = ", ".join(_skill_link(skill) for skill in manifest.skills)
        lines.append(
            f"| {_ecosystem_link(manifest.slug)} | {_agent_link(manifest.root_agent)} | {skills} | {manifest.status} | {manifest.description} |"
        )

    lines.extend(
        [
            "",
            "## Maintenance Rules",
            "- Installed ecosystems are declared by manifests under `.github/ecosystems/<slug>/ECOSYSTEM.md`.",
            "- Regenerate this managed block with `bash .github/ecosystems/update_ecosystem_core_files.sh --target-repo .`.",
            "- Validate ecosystem metadata with `bash .github/ecosystems/validate_ecosystem_registry.sh --repo-root .`.",
        ]
    )
    return "\n".join(lines)


def render_ecosystems_readme(manifests) -> str:
    lines = [
        "# Ecosystems Classification",
        "",
        "This folder contains installed ecosystem manifests and shared automation for `.github` core file generation.",
        "",
        "## Navigation",
        "- Ecosystem registry: [../ECOSYSTEM_REGISTRY.md](../ECOSYSTEM_REGISTRY.md)",
        "- Agents-skills routing map: [../AGENT_SKILL_ROUTING.md](../AGENT_SKILL_ROUTING.md)",
        "- Agents classification: [../agents/README.md](../agents/README.md)",
        "- Skills classification: [../skills/README.md](../skills/README.md)",
        "",
        "## Shared Scripts",
        "- [update_ecosystem_core_files.sh](update_ecosystem_core_files.sh): Regenerate `.github` core management files from installed ecosystem manifests.",
        "- [validate_ecosystem_registry.sh](validate_ecosystem_registry.sh): Validate the registry, manifests, routing links, and ecosystem membership metadata.",
        "",
        "## Installed Ecosystems",
    ]
    for manifest in manifests:
        lines.append(
            f"- [{manifest.slug}/ECOSYSTEM.md]({manifest.slug}/ECOSYSTEM.md): {manifest.description}"
        )
    lines.extend(
        [
            "",
            "## Maintenance Rules",
            "- Keep one ecosystem manifest per subdirectory under `.github/ecosystems/`.",
            "- Treat Markdown manifests as the source of truth for installed ecosystem membership.",
        ]
    )
    return "\n".join(lines)


def render_agents_readme(manifests, agents) -> str:
    lines = [
        "# Agents Classification",
        "",
        "This file tracks installed custom agents grouped by ecosystem while keeping all `.agent.md` definitions at the top level for VS Code discovery.",
        "",
        "## Navigation",
        "- Ecosystem registry: [../ECOSYSTEM_REGISTRY.md](../ECOSYSTEM_REGISTRY.md)",
        "- Ecosystems classification: [../ecosystems/README.md](../ecosystems/README.md)",
        "- Skills classification: [../skills/README.md](../skills/README.md)",
        "- Agents-skills routing map: [../AGENT_SKILL_ROUTING.md](../AGENT_SKILL_ROUTING.md)",
        "",
        "## Installed Agents By Ecosystem",
        "",
    ]
    for manifest in manifests:
        lines.append(f"### {manifest.name}")
        for agent in manifest.agents:
            description = agents.get(agent, {}).get("description", "")
            lines.append(f"- [{agent}]({agent}): {description}")
        lines.append("")
    lines.extend(
        [
            "## Maintenance Rules",
            "- Keep every agent frontmatter `ecosystem` field aligned with an installed ecosystem manifest.",
            "- Update `.github/AGENT_SKILL_ROUTING.md` and `.github/ECOSYSTEM_REGISTRY.md` in the same change when the installed agent set changes.",
            "- Run `bash .github/ecosystems/validate_ecosystem_registry.sh --repo-root .` after changing ecosystem-managed agent metadata.",
        ]
    )
    return "\n".join(lines)


def render_skills_readme(manifests, skills) -> str:
    lines = [
        "# Skills Classification",
        "",
        "This file tracks installed reusable skills grouped by ecosystem while keeping every skill directory directly under `.github/skills/`.",
        "",
        "## Navigation",
        "- Ecosystem registry: [../ECOSYSTEM_REGISTRY.md](../ECOSYSTEM_REGISTRY.md)",
        "- Ecosystems classification: [../ecosystems/README.md](../ecosystems/README.md)",
        "- Agents classification: [../agents/README.md](../agents/README.md)",
        "- Agents-skills routing map: [../AGENT_SKILL_ROUTING.md](../AGENT_SKILL_ROUTING.md)",
        "",
        "## Installed Skills By Ecosystem",
        "",
    ]
    for manifest in manifests:
        lines.append(f"### {manifest.name}")
        for skill in manifest.skills:
            description = skills.get(skill, {}).get("description", "")
            lines.append(f"- [{skill}]({skill}/SKILL.md): {description}")
        lines.append("")
    lines.extend(
        [
            "## Maintenance Rules",
            "- Keep every skill frontmatter `ecosystem` field aligned with an installed ecosystem manifest.",
            "- Update `.github/AGENT_SKILL_ROUTING.md` and `.github/ECOSYSTEM_REGISTRY.md` in the same change when the installed skill set changes.",
            "- Run `bash .github/ecosystems/validate_ecosystem_registry.sh --repo-root .` after changing ecosystem-managed skill metadata.",
        ]
    )
    return "\n".join(lines)


def render_routing(manifests, agents, skills) -> str:
    lines = [
        "# Agents-Skills Routing",
        "",
        "This document is the canonical routing map for relationships among installed ecosystems, agents, and skills.",
        "",
        "## Navigation",
        "- Ecosystem registry: [ECOSYSTEM_REGISTRY.md](ECOSYSTEM_REGISTRY.md)",
        "- Ecosystems classification: [ecosystems/README.md](ecosystems/README.md)",
        "- Agents classification: [agents/README.md](agents/README.md)",
        "- Skills classification: [skills/README.md](skills/README.md)",
        "",
        "## Relation Types",
        "- `uses`: Agent calls or follows one or more skills as part of execution.",
        "- `references`: Agent or skill references another artifact for policy alignment.",
        "- `agent-only`: Workflow is intentionally managed as an agent without a skill counterpart.",
        "- `skill-only`: Capability is intentionally managed as a skill without an agent counterpart.",
        "",
        "## Ecosystem -> Members Map",
        "",
        "| Ecosystem | Root Agent | Agents | Skills | Dependencies |",
        "|---|---|---|---|---|",
    ]
    for manifest in manifests:
        agents_links = ", ".join(_agent_link(agent) for agent in manifest.agents)
        skills_links = ", ".join(_skill_link(skill) for skill in manifest.skills)
        dependencies = ", ".join(_ecosystem_link(dep) for dep in manifest.dependencies) or "none"
        lines.append(
            f"| {_ecosystem_link(manifest.slug)} | {_agent_link(manifest.root_agent)} | {agents_links} | {skills_links} | {dependencies} |"
        )

    lines.extend(["", "## Agent -> Skills Map", "", "| Agent | Related Skills | Relation Type | Notes |", "|---|---|---|---|"])
    for manifest in manifests:
        for agent, related_skills in sorted(manifest.agent_skill_relations.items()):
            skill_links = ", ".join(_skill_link(skill) for skill in related_skills)
            note = agents.get(agent, {}).get("description", manifest.description)
            lines.append(
                f"| {_agent_link(agent)} | {skill_links} | uses | Member of {_ecosystem_link(manifest.slug)}. {note} |"
            )

    lines.extend(["", "## Skill -> Agents Map", "", "| Skill | Related Agents | Relation Type | Notes |", "|---|---|---|---|"])
    for manifest in manifests:
        inverse = invert_agent_skill_relations(manifest.agent_skill_relations)
        for skill, related_agents in sorted(inverse.items()):
            agent_links = ", ".join(_agent_link(agent) for agent in related_agents)
            note = skills.get(skill, {}).get("description", manifest.description)
            lines.append(
                f"| {_skill_link(skill)} | {agent_links} | uses | Member of {_ecosystem_link(manifest.slug)}. {note} |"
            )

    lines.extend(
        [
            "",
            "## Self-Extending Maintenance Rules",
            "- Keep `.github/ECOSYSTEM_REGISTRY.md`, `.github/ecosystems/README.md`, and this file aligned in the same change when ecosystem membership changes.",
            "- Regenerate this managed block with `bash .github/ecosystems/update_ecosystem_core_files.sh --target-repo .`.",
            "- Validate ecosystem metadata with `bash .github/ecosystems/validate_ecosystem_registry.sh --repo-root .`.",
        ]
    )
    return "\n".join(lines)


def render_copilot_instructions(manifests, agents, skills) -> str:
    lines = [
        "When working with installed agent ecosystems in this workspace:",
        "",
        "- Read `.github/ECOSYSTEM_REGISTRY.md` and `.github/ecosystems/README.md` before changing ecosystem-managed agents, skills, or routing files.",
    ]
    for manifest in manifests:
        root_agent_name = agents.get(manifest.root_agent, {}).get("name", manifest.root_agent)
        lines.append(
            f"- Prefer `{root_agent_name}` for `{manifest.slug}` orchestration tasks that span multiple installed skills."
        )
        for skill in manifest.skills:
            description = skills.get(skill, {}).get("description", manifest.description)
            lines.append(
                f"- Prefer `{skill}` for `{manifest.slug}` tasks: {description}"
            )
    lines.extend(
        [
            "- Regenerate ecosystem-managed core files with `bash .github/ecosystems/update_ecosystem_core_files.sh --target-repo .`.",
            "- Validate ecosystem metadata with `bash .github/ecosystems/validate_ecosystem_registry.sh --repo-root .`.",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-repo", default=".", help="Target repository root.")
    parser.add_argument("--dry-run", action="store_true", help="Print targets without writing files.")
    args = parser.parse_args()

    repo_root = find_repo_root(Path(args.target_repo).resolve())
    manifests = load_ecosystem_manifests(repo_root)
    if not manifests:
        print("No installed ecosystem manifests were found under .github/ecosystems/")
        return 1

    agents = load_agent_metadata(repo_root)
    skills = load_skill_metadata(repo_root)

    generators = {
        ".github/ECOSYSTEM_REGISTRY.md": render_registry(manifests),
        ".github/ecosystems/README.md": render_ecosystems_readme(manifests),
        ".github/agents/README.md": render_agents_readme(manifests, agents),
        ".github/skills/README.md": render_skills_readme(manifests, skills),
        ".github/AGENT_SKILL_ROUTING.md": render_routing(manifests, agents, skills),
        ".github/copilot-instructions.md": render_copilot_instructions(manifests, agents, skills),
    }

    managed_files = sorted(
        {rel_path for manifest in manifests for rel_path in manifest.managed_core_files}
    )

    for rel_path in managed_files:
        if rel_path not in generators:
            print(f"Skipping unmanaged core file with no generator: {rel_path}")
            continue
        destination = repo_root / rel_path
        write_managed_markdown(destination, generators[rel_path], dry_run=args.dry_run)
        status = "would update" if args.dry_run else "updated"
        print(f"{status} {destination}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())