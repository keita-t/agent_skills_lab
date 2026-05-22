#!/usr/bin/env python3
"""Validate ecosystem registry, manifests, and ecosystem membership metadata."""

from __future__ import annotations

import argparse
from pathlib import Path

from ecosystem_lib import find_repo_root, load_ecosystem_manifests
from ecosystem_registry_validation_service import ValidateRegistryInput, validate_registry


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".", help="Repository root to validate.")
    args = parser.parse_args()

    result = validate_registry(ValidateRegistryInput(repo_root=args.repo_root))

    if not result.passed:
        print("ECOSYSTEM REGISTRY VALIDATION FAILED")
        for index, error in enumerate(result.errors, start=1):
            print(f"{index}. {error.message}")
        return 1

    print("ECOSYSTEM REGISTRY VALIDATION PASSED")
    repo_root = find_repo_root(Path(args.repo_root).resolve())
    manifests_by_slug = {manifest.slug: manifest for manifest in load_ecosystem_manifests(repo_root)}
    print(f"Repository root: {repo_root}")
    print(f"Ecosystems: {', '.join(sorted(manifests_by_slug)) or '(none)'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())