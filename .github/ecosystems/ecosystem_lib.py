#!/usr/bin/env python3
"""Shared helpers for ecosystem manifests, validation, installation, and updates."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import shutil

MANAGED_BLOCK_START = "<!-- BEGIN ECOSYSTEM MANAGED BLOCK -->"
MANAGED_BLOCK_END = "<!-- END ECOSYSTEM MANAGED BLOCK -->"


def find_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / ".github").is_dir():
            return candidate
    raise RuntimeError("Could not locate repository root from script path")


def _strip_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _parse_list(value: str) -> list[str]:
    inner = value[1:-1].strip()
    if not inner:
        return []
    return [_strip_quotes(item.strip()) for item in inner.split(",") if item.strip()]


def parse_frontmatter(text: str) -> tuple[dict[str, object], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text

    end_index = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end_index = index
            break

    if end_index is None:
        return {}, text

    data: dict[str, object] = {}
    for line in lines[1:end_index]:
        raw = line.strip()
        if not raw or raw.startswith("#") or ":" not in raw:
            continue
        key, value = raw.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            data[key] = _parse_list(value)
        else:
            data[key] = _strip_quotes(value)

    body = "\n".join(lines[end_index + 1 :]).lstrip("\n")
    return data, body


def load_markdown(path: Path) -> tuple[dict[str, object], str]:
    text = path.read_text(encoding="utf-8")
    return parse_frontmatter(text)


@dataclass(frozen=True)
class EcosystemManifest:
    slug: str
    name: str
    description: str
    status: str
    root_agent: str
    agents: list[str]
    skills: list[str]
    dependencies: list[str]
    ecosystem_files: list[str]
    manifest_path: Path
    audit_files: list[str] = field(default_factory=list)


def manifest_owned_relative_paths(manifest: EcosystemManifest) -> list[str]:
    relative_paths = [f".github/agents/{agent}" for agent in manifest.agents]
    relative_paths.extend(f".github/skills/{skill}" for skill in manifest.skills)
    relative_paths.extend(manifest.ecosystem_files)
    relative_paths.extend(manifest.audit_files)
    relative_paths.append(f".github/ecosystems/{manifest.slug}/ECOSYSTEM.md")
    return relative_paths


def load_ecosystem_manifest(path: Path) -> EcosystemManifest:
    metadata, _ = load_markdown(path)
    required_keys = [
        "slug",
        "name",
        "description",
        "status",
        "root-agent",
        "agents",
        "skills",
        "dependencies",
        "ecosystem-files",
    ]
    missing = [key for key in required_keys if key not in metadata]
    if missing:
        raise RuntimeError(f"Manifest is missing required keys {missing}: {path}")

    return EcosystemManifest(
        slug=str(metadata["slug"]),
        name=str(metadata["name"]),
        description=str(metadata["description"]),
        status=str(metadata["status"]),
        root_agent=str(metadata["root-agent"]),
        agents=list(metadata["agents"]),
        skills=list(metadata["skills"]),
        dependencies=list(metadata["dependencies"]),
        ecosystem_files=list(metadata["ecosystem-files"]),
        audit_files=list(metadata.get("audit-files", [])),
        manifest_path=path,
    )


def load_ecosystem_manifests(repo_root: Path) -> list[EcosystemManifest]:
    ecosystems_dir = repo_root / ".github" / "ecosystems"
    if not ecosystems_dir.is_dir():
        return []
    manifests: list[EcosystemManifest] = []
    for path in sorted(ecosystems_dir.glob("*/ECOSYSTEM.md")):
        manifests.append(load_ecosystem_manifest(path))
    return manifests


def load_ecosystem_manifest_map(repo_root: Path) -> dict[str, EcosystemManifest]:
    return {manifest.slug: manifest for manifest in load_ecosystem_manifests(repo_root)}


def resolve_manifest_dependency_closure_from_map(
    manifests_by_slug: dict[str, EcosystemManifest],
    ecosystem_slug: str,
) -> list[EcosystemManifest]:
    if ecosystem_slug not in manifests_by_slug:
        raise FileNotFoundError(f"Ecosystem manifest not found for slug: {ecosystem_slug}")

    ordered_manifests: list[EcosystemManifest] = []
    visited: set[str] = set()
    visiting: list[str] = []

    def walk(slug: str) -> None:
        if slug in visited:
            return
        if slug in visiting:
            cycle_start = visiting.index(slug)
            cycle = visiting[cycle_start:] + [slug]
            raise RuntimeError(
                "Circular ecosystem dependency detected: " + " -> ".join(cycle)
            )

        manifest = manifests_by_slug.get(slug)
        if manifest is None:
            parent = visiting[-1] if visiting else ecosystem_slug
            raise RuntimeError(
                f"Ecosystem {parent} references unknown dependency: {slug}"
            )

        visiting.append(slug)
        for dependency in manifest.dependencies:
            walk(dependency)
        visiting.pop()
        visited.add(slug)
        ordered_manifests.append(manifest)

    walk(ecosystem_slug)
    return ordered_manifests


def resolve_manifest_dependency_closure(
    repo_root: Path,
    ecosystem_slug: str,
) -> list[EcosystemManifest]:
    manifests_by_slug = load_ecosystem_manifest_map(repo_root)
    return resolve_manifest_dependency_closure_from_map(manifests_by_slug, ecosystem_slug)


def load_agent_metadata(repo_root: Path) -> dict[str, dict[str, object]]:
    agents_dir = repo_root / ".github" / "agents"
    metadata: dict[str, dict[str, object]] = {}
    if not agents_dir.is_dir():
        return metadata
    for path in sorted(agents_dir.glob("*.agent.md")):
        frontmatter, _ = load_markdown(path)
        metadata[path.name] = dict(frontmatter)
    return metadata


def load_skill_metadata(repo_root: Path) -> dict[str, dict[str, object]]:
    skills_dir = repo_root / ".github" / "skills"
    metadata: dict[str, dict[str, object]] = {}
    if not skills_dir.is_dir():
        return metadata
    for path in sorted(skills_dir.glob("*/SKILL.md")):
        frontmatter, _ = load_markdown(path)
        metadata[path.parent.name] = dict(frontmatter)
    return metadata


def merge_managed_block(existing_text: str, generated_text: str) -> str:
    block = (
        f"{MANAGED_BLOCK_START}\n{generated_text.rstrip()}\n{MANAGED_BLOCK_END}\n"
    )

    if MANAGED_BLOCK_START in existing_text and MANAGED_BLOCK_END in existing_text:
        start = existing_text.index(MANAGED_BLOCK_START)
        end = existing_text.index(MANAGED_BLOCK_END, start) + len(MANAGED_BLOCK_END)
        prefix = existing_text[:start].rstrip()
        suffix = existing_text[end:].lstrip("\n")
        parts = [part for part in [prefix, block.rstrip(), suffix] if part]
        return "\n\n".join(parts) + "\n"

    if existing_text.strip():
        return existing_text.rstrip() + "\n\n" + block

    return block


def write_managed_markdown(path: Path, generated_text: str, dry_run: bool = False) -> None:
    existing_text = path.read_text(encoding="utf-8") if path.exists() else ""
    merged_text = merge_managed_block(existing_text, generated_text)
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(merged_text, encoding="utf-8")


def copy_path(
    source: Path,
    destination: Path,
    merge_strategy: str,
    dry_run: bool = False,
) -> list[str]:
    if merge_strategy not in {"merge", "replace", "skip-existing"}:
        raise ValueError(f"Unsupported merge strategy: {merge_strategy}")

    actions: list[str] = []

    if destination.exists():
        if merge_strategy == "skip-existing":
            return [f"skip {destination}"]
        if merge_strategy == "replace":
            actions.append(f"replace {destination}")
            if not dry_run:
                if destination.is_dir():
                    shutil.rmtree(destination)
                else:
                    destination.unlink()
        else:
            actions.append(f"merge {destination}")
    else:
        actions.append(f"copy {destination}")

    if dry_run:
        return actions

    destination.parent.mkdir(parents=True, exist_ok=True)

    if source.is_dir():
        if merge_strategy == "merge" and destination.exists():
            shutil.copytree(source, destination, dirs_exist_ok=True, copy_function=shutil.copy2)
        else:
            shutil.copytree(source, destination, copy_function=shutil.copy2)
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    return actions