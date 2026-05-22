#!/usr/bin/env python3
"""Install a selected ecosystem from this lab repository into a target project."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess

from ecosystem_lib import copy_path, find_repo_root, load_ecosystem_manifest

SHARED_TARGET_FILES = [
    ".github/ecosystems/ecosystem_lib.py",
    ".github/ecosystems/update_ecosystem_core_files.py",
    ".github/ecosystems/update_ecosystem_core_files.sh",
    ".github/ecosystems/validate_ecosystem_registry.py",
    ".github/ecosystems/validate_ecosystem_registry.sh",
]


def _run_command(command: list[str], cwd: Path) -> int:
    result = subprocess.run(command, cwd=cwd)
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-repo", required=True, help="Target repository path.")
    parser.add_argument("--ecosystem", required=True, help="Ecosystem slug to install.")
    parser.add_argument(
        "--merge-strategy",
        choices=["merge", "replace", "skip-existing"],
        default="merge",
        help="How to handle existing files in the target repository.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show planned actions without copying files.")
    parser.add_argument("--skip-core-update", action="store_true", help="Skip target core-file regeneration after copying payload files.")
    parser.add_argument("--skip-validation", action="store_true", help="Skip post-install validation commands.")
    args = parser.parse_args()

    source_root = find_repo_root(Path(__file__).resolve())
    manifest_path = source_root / ".github" / "ecosystems" / args.ecosystem / "ECOSYSTEM.md"
    if not manifest_path.is_file():
        print(f"Ecosystem manifest not found: {manifest_path}")
        return 1

    manifest = load_ecosystem_manifest(manifest_path)
    target_root = Path(args.target_repo).resolve()
    if not target_root.exists() or not target_root.is_dir():
        print(f"Target repository path does not exist: {target_root}")
        return 1
    if target_root == source_root:
        print(
            "Target repository path matches the source lab repository. "
            "Use a controlled self-host bootstrap for docs instead of the generic installer."
        )
        return 1

    actions: list[str] = []

    for rel_path in SHARED_TARGET_FILES:
        actions.extend(
            copy_path(
                source_root / rel_path,
                target_root / rel_path,
                args.merge_strategy,
                dry_run=args.dry_run,
            )
        )

    for agent in manifest.agents:
        source = source_root / ".github" / "agents" / agent
        destination = target_root / ".github" / "agents" / agent
        actions.extend(copy_path(source, destination, args.merge_strategy, dry_run=args.dry_run))

    for skill in manifest.skills:
        source = source_root / ".github" / "skills" / skill
        destination = target_root / ".github" / "skills" / skill
        actions.extend(copy_path(source, destination, args.merge_strategy, dry_run=args.dry_run))

    for rel_path in manifest.ecosystem_files:
        actions.extend(
            copy_path(
                source_root / rel_path,
                target_root / rel_path,
                args.merge_strategy,
                dry_run=args.dry_run,
            )
        )

    actions.extend(
        copy_path(
            manifest.manifest_path,
            target_root / ".github" / "ecosystems" / manifest.slug / "ECOSYSTEM.md",
            args.merge_strategy,
            dry_run=args.dry_run,
        )
    )

    print(f"Planned install actions for ecosystem: {manifest.slug}")
    for action in actions:
        print(f"- {action}")

    if args.dry_run:
        return 0

    if not args.skip_core_update:
        updater = target_root / ".github" / "ecosystems" / "update_ecosystem_core_files.sh"
        print("Running target core-file updater...")
        update_code = _run_command(
            ["bash", str(updater), "--target-repo", str(target_root)],
            cwd=target_root,
        )
        if update_code != 0:
            return update_code

    if not args.skip_validation:
        ecosystem_validator = target_root / ".github" / "ecosystems" / "validate_ecosystem_registry.sh"
        print("Running ecosystem registry validation...")
        ecosystem_code = _run_command(
            ["bash", str(ecosystem_validator), "--repo-root", str(target_root)],
            cwd=target_root,
        )
        if ecosystem_code != 0:
            return ecosystem_code

        if manifest.post_install_validator:
            validator = target_root / manifest.post_install_validator
            print(f"Running post-install validator: {validator}")
            validator_code = _run_command(["bash", str(validator)], cwd=target_root)
            if validator_code != 0:
                return validator_code

    print("Ecosystem installation completed.")
    print(f"Installed ecosystem: {manifest.slug}")
    print(f"Target repository: {target_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())