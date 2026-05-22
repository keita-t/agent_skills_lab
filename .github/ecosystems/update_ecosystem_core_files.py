#!/usr/bin/env python3
"""Generate or update ecosystem-managed core files in a target repository."""

from __future__ import annotations

import argparse
from pathlib import Path

from ecosystem_core_update_service import UpdateCoreFilesInput, apply_core_file_updates


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-repo", default=".", help="Target repository root.")
    parser.add_argument("--dry-run", action="store_true", help="Print targets without writing files.")
    args = parser.parse_args()

    try:
        result = apply_core_file_updates(
            UpdateCoreFilesInput(target_repo=args.target_repo, dry_run=args.dry_run)
        )
    except ValueError as exc:
        print(str(exc))
        return 1

    status = "would update" if args.dry_run else "updated"
    for rel_path in result.updated_files:
        print(f"{status} {Path(result.target_repo) / rel_path}")
    for warning in result.warnings:
        print(warning)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())