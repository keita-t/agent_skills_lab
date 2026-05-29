from __future__ import annotations

from pathlib import Path

from ecosystem_lib import (
    MANAGED_BLOCK_END,
    MANAGED_BLOCK_START,
    EcosystemManifest,
    copy_path,
    find_repo_root,
    load_ecosystem_manifest,
    manifest_owned_relative_paths,
    merge_managed_block,
    parse_frontmatter,
    resolve_manifest_dependency_closure,
)


def test_parse_frontmatter_reads_scalar_and_list_values() -> None:
    metadata, body = parse_frontmatter(
        """---
slug: test-ecosystem
skills: [skill-a, skill-b]
description: 'Example ecosystem'
---

Body line
"""
    )

    assert metadata["slug"] == "test-ecosystem"
    assert metadata["skills"] == ["skill-a", "skill-b"]
    assert metadata["description"] == "Example ecosystem"
    assert body == "Body line"


def test_load_ecosystem_manifest_reads_repository_governance_manifest() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    manifest_path = (
        repo_root
        / ".github"
        / "ecosystems"
        / "repository-governance"
        / "ECOSYSTEM.md"
    )

    manifest = load_ecosystem_manifest(manifest_path)

    assert manifest.slug == "repository-governance"
    assert manifest.root_agent == "governance-repository-context-manager.agent.md"
    assert manifest.agents == [
        "governance-repository-context-manager.agent.md",
        "governance-ecosystem-manifest.agent.md",
        "governance-ecosystem-delivery.agent.md",
    ]
    assert manifest.skills == [
        "repository-governance-bootstrap",
        "repository-doc-governance",
        "todo-progress-governance",
    ]
    assert manifest.dependencies == ["ecosystem-audit"]
    assert ".github/ecosystems/repository-governance/assets/templates" in manifest.ecosystem_files
    assert ".github/ecosystems/repository-governance/validate_repository_governance.py" not in manifest.ecosystem_files
    assert manifest.audit_files == [
        ".github/ecosystems/repository-governance/audit/repository-governance-audit.md"
    ]
    assert ".github/ecosystems/repository-governance/MCP_TOOLS.json" not in manifest.ecosystem_files


def test_load_ecosystem_manifest_reads_optional_audit_files(tmp_path: Path) -> None:
    manifest_path = tmp_path / "ECOSYSTEM.md"
    manifest_path.write_text(
        """---
slug: ecosystem-audit
name: Ecosystem Audit
description: Shared ecosystem audit platform.
status: active
root-agent: ecosystem-audit.agent.md
agents: [ecosystem-audit.agent.md]
skills: []
dependencies: []
ecosystem-files: []
audit-files: [.github/ecosystems/ecosystem-audit/audit/core-rules.md]
---

# Ecosystem Audit
""",
        encoding="utf-8",
    )

    manifest = load_ecosystem_manifest(manifest_path)

    assert manifest.audit_files == [
        ".github/ecosystems/ecosystem-audit/audit/core-rules.md"
    ]


def test_manifest_owned_relative_paths_match_repository_governance_contract() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    manifest_path = (
        repo_root
        / ".github"
        / "ecosystems"
        / "repository-governance"
        / "ECOSYSTEM.md"
    )

    manifest = load_ecosystem_manifest(manifest_path)
    relative_paths = manifest_owned_relative_paths(manifest)

    assert ".github/agents/governance-repository-context-manager.agent.md" in relative_paths
    assert ".github/skills/repository-governance-bootstrap" in relative_paths
    assert ".github/ecosystems/repository-governance/audit/repository-governance-audit.md" in relative_paths
    assert ".github/ecosystems/repository-governance/ECOSYSTEM.md" in relative_paths
    assert ".github/ecosystems/deliver_ecosystem.py" not in relative_paths


def test_manifest_owned_relative_paths_include_audit_files() -> None:
    manifest = EcosystemManifest(
        slug="ecosystem-audit",
        name="Ecosystem Audit",
        description="Shared ecosystem audit platform.",
        status="active",
        root_agent="ecosystem-audit.agent.md",
        agents=["ecosystem-audit.agent.md"],
        skills=[],
        dependencies=[],
        ecosystem_files=[],
        manifest_path=Path(".github/ecosystems/ecosystem-audit/ECOSYSTEM.md"),
        audit_files=[".github/ecosystems/ecosystem-audit/audit/core-rules.md"],
    )

    relative_paths = manifest_owned_relative_paths(manifest)

    assert ".github/ecosystems/ecosystem-audit/audit/core-rules.md" in relative_paths


def test_resolve_manifest_dependency_closure_orders_dependencies_first(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"

    def write_manifest(slug: str, dependencies: list[str]) -> None:
        manifest_path = repo_root / ".github" / "ecosystems" / slug / "ECOSYSTEM.md"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        dependency_text = ", ".join(dependencies)
        manifest_path.write_text(
            f"""---
slug: {slug}
name: {slug}
description: Test ecosystem.
status: active
root-agent: {slug}.agent.md
agents: [{slug}.agent.md]
skills: []
dependencies: [{dependency_text}]
ecosystem-files: []
---

# {slug}
""",
            encoding="utf-8",
        )

    write_manifest("ecosystem-audit", [])
    write_manifest("repository-governance", ["ecosystem-audit"])
    write_manifest("product-docs", ["repository-governance"])

    closure = resolve_manifest_dependency_closure(repo_root, "product-docs")

    assert [manifest.slug for manifest in closure] == [
        "ecosystem-audit",
        "repository-governance",
        "product-docs",
    ]


def test_merge_managed_block_replaces_existing_managed_content() -> None:
    existing = "Manual heading\n\n<!-- BEGIN ECOSYSTEM MANAGED BLOCK -->\nold\n<!-- END ECOSYSTEM MANAGED BLOCK -->\n\nManual footer\n"

    merged = merge_managed_block(existing, "new body")

    assert "Manual heading" in merged
    assert "Manual footer" in merged
    assert "new body" in merged
    assert "old" not in merged
    assert merged.count(MANAGED_BLOCK_START) == 1
    assert merged.count(MANAGED_BLOCK_END) == 1


def test_copy_path_respects_skip_existing_strategy(tmp_path: Path) -> None:
    source = tmp_path / "source.txt"
    destination = tmp_path / "destination.txt"
    source.write_text("source", encoding="utf-8")
    destination.write_text("existing", encoding="utf-8")

    actions = copy_path(source, destination, "skip-existing")

    assert actions == [f"skip {destination}"]
    assert destination.read_text(encoding="utf-8") == "existing"


def test_find_repo_root_locates_current_repository() -> None:
    start = Path(__file__).resolve()

    repo_root = find_repo_root(start)

    assert repo_root == Path(__file__).resolve().parents[2]