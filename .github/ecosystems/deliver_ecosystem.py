#!/usr/bin/env python3
"""Execute manifest-owned ecosystem delivery workflows against a target repository."""

from __future__ import annotations

import argparse
from pathlib import Path

from ecosystem_delivery_service import DeliveryConflictError, execute_delivery_plan


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["install", "remove"], help="Delivery action.")
    parser.add_argument("--target-repo", required=True, help="Target repository in owner/repo form.")
    parser.add_argument("--ecosystem", required=True, help="Ecosystem slug to deliver.")
    parser.add_argument("--base-branch", help="Optional base branch override.")
    parser.add_argument("--branch-name", help="Optional branch name override.")
    parser.add_argument("--working-directory", help="Optional working directory for cloning.")
    parser.add_argument("--source-root", help="Optional source repository root override.")
    parser.add_argument("--dry-run", action="store_true", help="Plan the workflow without mutating the target clone.")
    args = parser.parse_args()

    try:
        result = execute_delivery_plan(
            action=args.action,
            target_repo=args.target_repo,
            ecosystem_slug=args.ecosystem,
            source_root=Path(args.source_root).resolve() if args.source_root else None,
            working_directory=Path(args.working_directory).resolve() if args.working_directory else None,
            base_branch=args.base_branch,
            branch_name=args.branch_name,
            dry_run=args.dry_run,
        )
    except DeliveryConflictError as exc:
        print("Delivery safety check failed.")
        for conflict in exc.conflicts:
            verb = "overwrite" if conflict.action == "copy" else "remove"
            print(f"- {conflict.relative_destination} ({verb})")
        return 1
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        print(str(exc))
        return 1

    print(f"Action: {result.action}")
    print(f"Ecosystem: {result.ecosystem_slug}")
    print(f"Target repository: {result.target_repo}")
    print(f"Base branch: {result.base_branch}")
    print(f"Branch name: {result.branch_name}")
    print(f"Working directory: {result.working_directory}")
    print(f"Clone path: {result.clone_path}")
    for entry in result.file_actions:
        print(f"- {entry}")
    if result.pr_url:
        print(f"Pull request: {result.pr_url}")
    elif args.dry_run:
        print("Dry run completed without creating a pull request.")
    else:
        print("No pull request was created because no file changes were detected.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
