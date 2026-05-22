#!/usr/bin/env python3
"""Install a selected ecosystem from this lab repository into a target project."""

from __future__ import annotations

import argparse

from ecosystem_install_service import build_install_plan, execute_install
from mcp_models import ApplyInstallInput, PreviewInstallInput


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

    preview_request = PreviewInstallInput(
        target_repo=args.target_repo,
        ecosystem_slug=args.ecosystem,
        merge_strategy=args.merge_strategy,
        run_core_update=not args.skip_core_update,
        run_validation=not args.skip_validation,
    )

    try:
        preview = build_install_plan(preview_request)
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc))
        return 1

    print(f"Planned install actions for ecosystem: {args.ecosystem}")
    for action in preview.actions:
        print(f"- {action}")

    if args.dry_run:
        return 0

    apply_request = ApplyInstallInput(
        target_repo=args.target_repo,
        ecosystem_slug=args.ecosystem,
        merge_strategy=args.merge_strategy,
        run_core_update=not args.skip_core_update,
        run_validation=not args.skip_validation,
        confirmation_token=preview.preview_token or "",
    )

    try:
        result = execute_install(apply_request)
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        print(str(exc))
        return 1

    for validator_result in result.validator_results:
        status = "PASSED" if validator_result.passed else "FAILED"
        print(f"Validator {validator_result.name}: {status}")
        for error in validator_result.errors:
            print(f"- {error}")

    print("Ecosystem installation completed.")
    print(f"Installed ecosystem: {result.installed_ecosystem}")
    print(f"Target repository: {result.target_repo}")
    if any(not validator_result.passed for validator_result in result.validator_results):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())