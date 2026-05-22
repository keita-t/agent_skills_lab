from __future__ import annotations

from pathlib import Path

from ecosystem_lib import find_repo_root, load_ecosystem_manifest, load_ecosystem_manifests
from mcp_models import (
    GetManifestInput,
    GetManifestResult,
    ListAvailableEcosystemsInput,
    ListAvailableEcosystemsResult,
    ManifestSummary,
)


def _to_manifest_summary(manifest) -> ManifestSummary:
    return ManifestSummary(
        slug=manifest.slug,
        name=manifest.name,
        description=manifest.description,
        status=manifest.status,
        root_agent=manifest.root_agent,
        skills=manifest.skills,
        dependencies=manifest.dependencies,
        ecosystem_files=manifest.ecosystem_files,
        managed_core_files=manifest.managed_core_files,
        mcp_tool_names=manifest.mcp_tool_names,
    )


def list_available_ecosystems(
    request: ListAvailableEcosystemsInput,
) -> ListAvailableEcosystemsResult:
    repo_root = find_repo_root(Path(request.repo_root).resolve())
    manifests = load_ecosystem_manifests(repo_root)
    return ListAvailableEcosystemsResult(
        ecosystems=[_to_manifest_summary(manifest) for manifest in manifests]
    )


def get_ecosystem_manifest(request: GetManifestInput) -> GetManifestResult:
    repo_root = find_repo_root(Path(request.repo_root).resolve())
    manifest_path = repo_root / ".github" / "ecosystems" / request.ecosystem_slug / "ECOSYSTEM.md"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Ecosystem manifest not found: {manifest_path}")
    manifest = load_ecosystem_manifest(manifest_path)
    return GetManifestResult(manifest=_to_manifest_summary(manifest))