from __future__ import annotations

from pathlib import Path

from ecosystem_lib import (
    MANAGED_BLOCK_END,
    MANAGED_BLOCK_START,
    copy_path,
    find_repo_root,
    invert_agent_skill_relations,
    load_ecosystem_manifest,
    merge_managed_block,
    parse_frontmatter,
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
    assert manifest.skills == [
        "repository-governance-bootstrap",
        "repository-doc-governance",
        "todo-progress-governance",
    ]
    assert manifest.mcp_enabled is True
    assert (
        manifest.mcp_tool_registry
        == ".github/ecosystems/repository-governance/MCP_TOOLS.json"
    )
    assert manifest.mcp_tool_names == [
        "repository_governance.validate_repository",
        "repository_governance.validate_agent_skill_docs",
    ]
    assert ".github/ecosystems/repository-governance/assets/templates" in manifest.ecosystem_files
    assert (
        manifest.post_install_validator
        == ".github/ecosystems/repository-governance/validate_agent_skill_docs.sh"
    )


def test_invert_agent_skill_relations_groups_agents_per_skill() -> None:
    inverse = invert_agent_skill_relations(
        {
            "agent-a": ["skill-a", "skill-b"],
            "agent-b": ["skill-b"],
        }
    )

    assert inverse == {
        "skill-a": ["agent-a"],
        "skill-b": ["agent-a", "agent-b"],
    }


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