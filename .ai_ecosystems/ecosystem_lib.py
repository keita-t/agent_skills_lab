#!/usr/bin/env python3
"""Shared helpers for ecosystem manifests, validation, installation, and updates."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import shutil

MANAGED_BLOCK_START = "<!-- BEGIN ECOSYSTEM MANAGED BLOCK -->"
MANAGED_BLOCK_END = "<!-- END ECOSYSTEM MANAGED BLOCK -->"
ECOSYSTEMS_DIRNAME = ".ai_ecosystems"
DEFAULT_AGENT_HOST = "github-copilot"


@dataclass(frozen=True)
class AgentHostAdapter:
    name: str
    agent_directory: str | None
    skill_directory: str


AGENT_HOST_ADAPTERS: dict[str, AgentHostAdapter] = {
    "github-copilot": AgentHostAdapter(
        name="github-copilot",
        agent_directory=".github/agents",
        skill_directory=".github/skills",
    ),
    "claude-code": AgentHostAdapter(
        name="claude-code",
        agent_directory=".claude/agents",
        skill_directory=".claude/skills",
    ),
    "codex": AgentHostAdapter(
        name="codex",
        agent_directory=None,
        skill_directory=".agents/skills",
    ),
    "cursor": AgentHostAdapter(
        name="cursor",
        agent_directory=None,
        skill_directory=".cursor/skills",
    ),
}
SUPPORTED_AGENT_HOSTS = tuple(AGENT_HOST_ADAPTERS)


def find_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / ECOSYSTEMS_DIRNAME).is_dir() or (candidate / ".git").is_dir():
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
    shared_ownership_files: list[str] = field(default_factory=list)
    runtime_mode: str | None = None
    runtime_entrypoint: str | None = None
    runtime_requires: list[str] = field(default_factory=list)


def _require_string_list(
    metadata: dict[str, object],
    key: str,
    path: Path,
) -> list[str]:
    value = metadata.get(key)
    if not isinstance(value, list):
        raise RuntimeError(f"Manifest key must be a list: {key}: {path}")
    return [str(item) for item in value]


def _load_runtime_metadata(
    metadata: dict[str, object],
    path: Path,
) -> tuple[str | None, str | None, list[str]]:
    runtime_mode_value = metadata.get("runtime-mode")
    runtime_mode = str(runtime_mode_value) if runtime_mode_value is not None else None

    runtime_entrypoint_value = metadata.get("runtime-entrypoint")
    runtime_entrypoint = (
        str(runtime_entrypoint_value) if runtime_entrypoint_value is not None else None
    )

    runtime_requires_value = metadata.get("runtime-requires", [])
    if not isinstance(runtime_requires_value, list):
        raise RuntimeError(f"Manifest key must be a list: runtime-requires: {path}")
    runtime_requires = [str(item) for item in runtime_requires_value]

    if runtime_mode is None:
        if runtime_entrypoint is not None or runtime_requires:
            raise RuntimeError(
                "Runtime metadata requires runtime-mode when runtime-entrypoint or "
                f"runtime-requires are set: {path}"
            )
        return None, None, []

    if runtime_mode != "container":
        raise RuntimeError(
            f"Unsupported runtime-mode '{runtime_mode}' in manifest: {path}"
        )

    if runtime_entrypoint is None:
        raise RuntimeError(
            f"runtime-entrypoint is required when runtime-mode is set: {path}"
        )

    if not runtime_requires:
        raise RuntimeError(
            f"runtime-requires must list at least one prerequisite when runtime-mode is set: {path}"
        )

    return runtime_mode, runtime_entrypoint, runtime_requires


def ecosystem_manifest_relative_path(manifest: EcosystemManifest) -> str:
    return f"{ECOSYSTEMS_DIRNAME}/{manifest.slug}/ECOSYSTEM.md"


def ecosystem_agent_relative_path(manifest: EcosystemManifest, agent: str) -> str:
    return f"{ECOSYSTEMS_DIRNAME}/{manifest.slug}/agents/{agent}"


def ecosystem_skill_relative_path(manifest: EcosystemManifest, skill: str) -> str:
    return f"{ECOSYSTEMS_DIRNAME}/{manifest.slug}/skills/{skill}"


def manifest_common_relative_paths(manifest: EcosystemManifest) -> list[str]:
    relative_paths = list(manifest.ecosystem_files)
    relative_paths.extend(manifest.audit_files)
    relative_paths.append(ecosystem_manifest_relative_path(manifest))
    return relative_paths


def manifest_owned_relative_paths(manifest: EcosystemManifest) -> list[str]:
    relative_paths = [
        ecosystem_agent_relative_path(manifest, agent) for agent in manifest.agents
    ]
    relative_paths.extend(
        ecosystem_skill_relative_path(manifest, skill) for skill in manifest.skills
    )
    relative_paths.extend(manifest.ecosystem_files)
    relative_paths.extend(manifest.audit_files)
    relative_paths.append(ecosystem_manifest_relative_path(manifest))
    return relative_paths


def detect_agent_hosts(target_root: Path) -> list[str]:
    root = Path(target_root)
    detected: list[str] = []

    if (
        (root / ".github" / "copilot-instructions.md").exists()
        or (root / ".github" / "agents").is_dir()
        or (root / ".github" / "skills").is_dir()
    ):
        detected.append("github-copilot")

    if (root / "CLAUDE.md").exists() or (root / ".claude").exists():
        detected.append("claude-code")

    if (
        (root / "AGENTS.md").exists()
        or (root / ".agents").exists()
        or (root / ".codex").exists()
    ):
        detected.append("codex")

    if (root / ".cursor").exists() or (root / ".cursorrules").exists():
        detected.append("cursor")

    return detected or [DEFAULT_AGENT_HOST]


def resolve_agent_hosts(
    agent_hosts: list[str] | tuple[str, ...] | None,
    target_root: Path,
) -> list[str]:
    if agent_hosts is None:
        return detect_agent_hosts(target_root)

    requested = [host for host in agent_hosts if host]
    if not requested or requested == ["auto"]:
        return detect_agent_hosts(target_root)

    if "auto" in requested:
        raise ValueError("--agent-host auto cannot be combined with explicit hosts")

    if "all" in requested:
        requested = list(SUPPORTED_AGENT_HOSTS)

    unknown_hosts = sorted(set(requested) - set(SUPPORTED_AGENT_HOSTS))
    if unknown_hosts:
        raise ValueError(
            "Unsupported agent host(s): "
            + ", ".join(unknown_hosts)
            + ". Supported hosts: "
            + ", ".join(SUPPORTED_AGENT_HOSTS)
        )

    resolved: list[str] = []
    for host in requested:
        if host not in resolved:
            resolved.append(host)
    return resolved


def host_agent_destination_relative_path(host: str, agent: str) -> str | None:
    adapter = AGENT_HOST_ADAPTERS[host]
    if adapter.agent_directory is None:
        return None
    return f"{adapter.agent_directory}/{agent}"


def host_skill_destination_relative_path(host: str, skill: str) -> str:
    adapter = AGENT_HOST_ADAPTERS[host]
    return f"{adapter.skill_directory}/{skill}"


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

    runtime_mode, runtime_entrypoint, runtime_requires = _load_runtime_metadata(
        metadata,
        path,
    )

    manifest = EcosystemManifest(
        slug=str(metadata["slug"]),
        name=str(metadata["name"]),
        description=str(metadata["description"]),
        status=str(metadata["status"]),
        root_agent=str(metadata["root-agent"]),
        agents=_require_string_list(metadata, "agents", path),
        skills=_require_string_list(metadata, "skills", path),
        dependencies=_require_string_list(metadata, "dependencies", path),
        ecosystem_files=_require_string_list(metadata, "ecosystem-files", path),
        audit_files=_require_string_list(
            {**metadata, "audit-files": metadata.get("audit-files", [])},
            "audit-files",
            path,
        ),
        shared_ownership_files=_require_string_list(
            {**metadata, "shared-ownership-files": metadata.get("shared-ownership-files", [])},
            "shared-ownership-files",
            path,
        ),
        manifest_path=path,
        runtime_mode=runtime_mode,
        runtime_entrypoint=runtime_entrypoint,
        runtime_requires=runtime_requires,
    )

    invalid_shared_ownership_paths = [
        relative_path
        for relative_path in manifest.shared_ownership_files
        if relative_path not in manifest_owned_relative_paths(manifest)
    ]
    if invalid_shared_ownership_paths:
        raise RuntimeError(
            "shared-ownership-files must reference manifest-owned paths: "
            + ", ".join(invalid_shared_ownership_paths)
            + f": {path}"
        )

    if (
        manifest.runtime_entrypoint is not None
        and manifest.runtime_entrypoint not in manifest_owned_relative_paths(manifest)
    ):
        raise RuntimeError(
            "runtime-entrypoint must reference a manifest-owned path: "
            f"{manifest.runtime_entrypoint}: {path}"
        )

    return manifest


def load_ecosystem_manifests(repo_root: Path) -> list[EcosystemManifest]:
    ecosystems_dir = repo_root / ECOSYSTEMS_DIRNAME
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
    metadata: dict[str, dict[str, object]] = {}
    ecosystems_dir = repo_root / ECOSYSTEMS_DIRNAME
    if not ecosystems_dir.is_dir():
        return metadata
    for path in sorted(ecosystems_dir.glob("*/agents/*.md")):
        frontmatter, _ = load_markdown(path)
        metadata[path.name] = dict(frontmatter)
    return metadata


def load_skill_metadata(repo_root: Path) -> dict[str, dict[str, object]]:
    metadata: dict[str, dict[str, object]] = {}
    ecosystems_dir = repo_root / ECOSYSTEMS_DIRNAME
    if not ecosystems_dir.is_dir():
        return metadata
    for path in sorted(ecosystems_dir.glob("*/skills/*/SKILL.md")):
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
