from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
import subprocess

from ecosystem_lib import EcosystemManifest, copy_path, find_repo_root, load_ecosystem_manifest
from mcp_models import (
    ApplyInstallInput,
    ApplyInstallResult,
    PreviewInstallInput,
    PreviewInstallResult,
    ValidatorResult,
)
from ecosystem_core_update_service import UpdateCoreFilesInput, apply_core_file_updates
from ecosystem_registry_validation_service import ValidateRegistryInput, validate_registry

SHARED_TARGET_FILES = [
    ".github/ecosystems/ecosystem_lib.py",
    ".github/ecosystems/ecosystem_catalog_service.py",
    ".github/ecosystems/ecosystem_core_update_service.py",
    ".github/ecosystems/mcp_models.py",
    ".github/ecosystems/mcp_settings.py",
    ".github/ecosystems/mcp_server.py",
    ".github/ecosystems/mcp_tool_registry.py",
    ".github/ecosystems/MCP_TOOLS.json",
    ".github/ecosystems/ecosystem_registry_validation_service.py",
    ".github/ecosystems/ecosystem_install_service.py",
    ".github/ecosystems/update_ecosystem_core_files.py",
    ".github/ecosystems/update_ecosystem_core_files.sh",
    ".github/ecosystems/validate_ecosystem_registry.py",
    ".github/ecosystems/validate_ecosystem_registry.sh",
]


@dataclass(frozen=True)
class InstallPlan:
    source_root: Path
    target_root: Path
    manifest: EcosystemManifest
    merge_strategy: str
    run_core_update: bool
    run_validation: bool
    actions: list[str]
    post_install_validators: list[str]
    preview_token: str


def ensure_install_safe(source_root: Path, target_root: Path) -> None:
    if not target_root.exists() or not target_root.is_dir():
        raise FileNotFoundError(f"Target repository path does not exist: {target_root}")
    if target_root == source_root:
        raise ValueError(
            "Target repository path matches the source lab repository. "
            "Use a controlled self-host bootstrap for docs instead of the generic installer."
        )


def _run_command(command: list[str], cwd: Path) -> tuple[int, str]:
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    output = "\n".join(part for part in [result.stdout.strip(), result.stderr.strip()] if part).strip()
    return result.returncode, output


def _resolve_manifest(source_root: Path, ecosystem_slug: str) -> EcosystemManifest:
    manifest_path = source_root / ".github" / "ecosystems" / ecosystem_slug / "ECOSYSTEM.md"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Ecosystem manifest not found: {manifest_path}")
    return load_ecosystem_manifest(manifest_path)


def _collect_install_actions(
    source_root: Path,
    target_root: Path,
    manifest: EcosystemManifest,
    merge_strategy: str,
    dry_run: bool,
) -> list[str]:
    actions: list[str] = []

    for rel_path in SHARED_TARGET_FILES:
        actions.extend(
            copy_path(
                source_root / rel_path,
                target_root / rel_path,
                merge_strategy,
                dry_run=dry_run,
            )
        )

    for agent in manifest.agents:
        actions.extend(
            copy_path(
                source_root / ".github" / "agents" / agent,
                target_root / ".github" / "agents" / agent,
                merge_strategy,
                dry_run=dry_run,
            )
        )

    for skill in manifest.skills:
        actions.extend(
            copy_path(
                source_root / ".github" / "skills" / skill,
                target_root / ".github" / "skills" / skill,
                merge_strategy,
                dry_run=dry_run,
            )
        )

    for rel_path in manifest.ecosystem_files:
        actions.extend(
            copy_path(
                source_root / rel_path,
                target_root / rel_path,
                merge_strategy,
                dry_run=dry_run,
            )
        )

    actions.extend(
        copy_path(
            manifest.manifest_path,
            target_root / ".github" / "ecosystems" / manifest.slug / "ECOSYSTEM.md",
            merge_strategy,
            dry_run=dry_run,
        )
    )

    return actions


def _build_plan(
    request: PreviewInstallInput,
    source_root: Path | None = None,
) -> InstallPlan:
    resolved_source_root = source_root or find_repo_root(Path(__file__).resolve())
    manifest = _resolve_manifest(resolved_source_root, request.ecosystem_slug)
    target_root = Path(request.target_repo).resolve()
    ensure_install_safe(resolved_source_root, target_root)

    actions = _collect_install_actions(
        resolved_source_root,
        target_root,
        manifest,
        request.merge_strategy,
        dry_run=True,
    )
    token_source = "\n".join(
        [
            request.ecosystem_slug,
            str(target_root),
            request.merge_strategy,
            str(request.run_core_update),
            str(request.run_validation),
            *actions,
        ]
    )
    preview_token = hashlib.sha256(token_source.encode("utf-8")).hexdigest()[:16]
    post_install_validators = [manifest.post_install_validator] if manifest.post_install_validator else []

    return InstallPlan(
        source_root=resolved_source_root,
        target_root=target_root,
        manifest=manifest,
        merge_strategy=request.merge_strategy,
        run_core_update=request.run_core_update,
        run_validation=request.run_validation,
        actions=actions,
        post_install_validators=post_install_validators,
        preview_token=preview_token,
    )


def build_install_plan(
    request: PreviewInstallInput,
    source_root: Path | None = None,
) -> PreviewInstallResult:
    plan = _build_plan(request, source_root=source_root)
    warnings: list[str] = []
    if request.merge_strategy == "replace":
        warnings.append("replace merge strategy may overwrite existing files in the target repository")

    return PreviewInstallResult(
        actions=plan.actions,
        warnings=warnings,
        post_install_validators=plan.post_install_validators,
        requires_confirmation=True,
        preview_token=plan.preview_token,
    )


def execute_install(
    request: ApplyInstallInput,
    source_root: Path | None = None,
) -> ApplyInstallResult:
    preview_request = PreviewInstallInput(
        target_repo=request.target_repo,
        ecosystem_slug=request.ecosystem_slug,
        merge_strategy=request.merge_strategy,
        run_core_update=request.run_core_update,
        run_validation=request.run_validation,
    )
    plan = _build_plan(preview_request, source_root=source_root)
    if request.confirmation_token != plan.preview_token:
        raise ValueError("confirmation token does not match the current install plan")

    executed_actions = _collect_install_actions(
        plan.source_root,
        plan.target_root,
        plan.manifest,
        plan.merge_strategy,
        dry_run=False,
    )
    validator_results: list[ValidatorResult] = []
    warnings: list[str] = []

    if plan.run_core_update:
        apply_core_file_updates(
            UpdateCoreFilesInput(target_repo=str(plan.target_root), dry_run=False)
        )

    if plan.run_validation:
        registry_result = validate_registry(
            ValidateRegistryInput(repo_root=str(plan.target_root))
        )
        validator_results.append(
            ValidatorResult(
                name="ecosystem.validate_registry",
                passed=registry_result.passed,
                errors=[issue.message for issue in registry_result.errors],
                warnings=registry_result.warnings,
            )
        )
        if plan.manifest.post_install_validator:
            validator_path = plan.target_root / plan.manifest.post_install_validator
            exit_code, output = _run_command(["bash", str(validator_path)], cwd=plan.target_root)
            validator_results.append(
                ValidatorResult(
                    name=plan.manifest.post_install_validator,
                    passed=exit_code == 0,
                    errors=[output] if exit_code != 0 and output else [],
                    warnings=[],
                )
            )
            if exit_code != 0 and not output:
                warnings.append(f"post-install validator failed without output: {validator_path}")

    return ApplyInstallResult(
        installed_ecosystem=plan.manifest.slug,
        target_repo=str(plan.target_root),
        actions=executed_actions,
        warnings=warnings,
        validator_results=validator_results,
    )