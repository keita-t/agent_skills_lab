from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Literal

from ecosystem_lib import (
    EcosystemManifest,
    find_repo_root,
    load_ecosystem_manifest_map,
    manifest_owned_relative_paths,
    resolve_manifest_dependency_closure,
    resolve_manifest_dependency_closure_from_map,
)


@dataclass(frozen=True)
class DeliveryChange:
    action: Literal["copy", "remove"]
    relative_destination: str
    destination: str
    source: str | None = None


@dataclass(frozen=True)
class CommandResult:
    command: tuple[str, ...]
    cwd: str
    stdout: str
    stderr: str


@dataclass(frozen=True)
class DeliveryExecutionResult:
    action: Literal["install", "remove"]
    ecosystem_slug: str
    resolved_ecosystems: list[str]
    target_repo: str
    base_branch: str
    branch_name: str
    working_directory: str
    clone_path: str
    file_actions: list[str]
    pr_title: str
    pr_body: str
    pr_url: str | None
    committed: bool


@dataclass(frozen=True)
class DeliveryConflict:
    action: Literal["copy", "remove"]
    relative_destination: str
    destination: str


class DeliveryConflictError(RuntimeError):
    def __init__(self, conflicts: list[DeliveryConflict]) -> None:
        self.conflicts = conflicts
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        lines = ["Delivery safety check failed for manifest-owned paths:"]
        for conflict in self.conflicts:
            verb = "overwrite" if conflict.action == "copy" else "remove"
            lines.append(f"- {conflict.relative_destination} ({verb})")
        return "\n".join(lines)


class ShellCommandRunner:
    def run(self, command: list[str], cwd: Path) -> CommandResult:
        result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        if result.returncode != 0:
            output = "\n".join(part for part in [stdout, stderr] if part)
            raise RuntimeError(
                f"Command failed ({result.returncode}): {' '.join(command)}\n{output}".rstrip()
            )
        return CommandResult(
            command=tuple(command),
            cwd=str(cwd),
            stdout=stdout,
            stderr=stderr,
        )


def _resolve_source_root(source_root: Path | None) -> Path:
    return source_root or find_repo_root(Path(__file__).resolve())


def _parse_target_repo(target_repo: str) -> tuple[str, str]:
    owner, separator, repo = target_repo.strip().partition("/")
    if not separator or not owner or not repo or "/" in repo:
        raise ValueError(
            "target repository must use owner/repo form for delivery workflows"
        )
    return owner, repo


def prepare_branch_name(
    ecosystem_slug: str,
    action: Literal["install", "remove"],
    branch_name: str | None = None,
) -> str:
    if branch_name:
        return branch_name
    return f"ecosystem-{ecosystem_slug}-{action}"


def generate_pr_title(
    ecosystem_slug: str,
    action: Literal["install", "remove"],
) -> str:
    verb = "Install" if action == "install" else "Remove"
    return f"{verb} {ecosystem_slug} ecosystem"


def generate_pr_body(
    ecosystem_slug: str,
    action: Literal["install", "remove"],
    resolved_ecosystems: list[str],
    file_actions: list[str],
) -> str:
    lines = [
        f"## Ecosystem {action}",
        "",
        f"- Requested ecosystem: `{ecosystem_slug}`",
        f"- Resolved ecosystems: `{', '.join(resolved_ecosystems)}`",
        f"- Action: `{action}`",
        "",
        "## Manifest-owned file changes",
    ]
    lines.extend(f"- `{entry}`" for entry in file_actions)
    return "\n".join(lines)


def _resolve_install_manifests(
    source_root: Path,
    ecosystem_slug: str,
) -> list[EcosystemManifest]:
    return resolve_manifest_dependency_closure(source_root, ecosystem_slug)


def _resolve_remove_manifests(
    source_root: Path,
    target_root: Path,
    ecosystem_slug: str,
) -> list[EcosystemManifest]:
    requested_manifests = resolve_manifest_dependency_closure(source_root, ecosystem_slug)
    installed_manifests = load_ecosystem_manifest_map(target_root)
    requested_slugs = {manifest.slug for manifest in requested_manifests}
    preserved_dependencies: set[str] = set()
    blocking_dependents: list[str] = []

    for installed_slug in sorted(installed_manifests):
        if installed_slug == ecosystem_slug:
            continue
        if installed_slug in requested_slugs:
            continue
        installed_closure = resolve_manifest_dependency_closure_from_map(
            installed_manifests,
            installed_slug,
        )
        installed_closure_slugs = {manifest.slug for manifest in installed_closure}
        if ecosystem_slug in installed_closure_slugs:
            blocking_dependents.append(installed_slug)
            continue
        preserved_dependencies.update(installed_closure_slugs & requested_slugs)

    if blocking_dependents:
        raise RuntimeError(
            f"Cannot remove ecosystem {ecosystem_slug} because installed ecosystems depend on it: "
            + ", ".join(blocking_dependents)
        )

    return [
        manifest
        for manifest in requested_manifests
        if manifest.slug == ecosystem_slug or manifest.slug not in preserved_dependencies
    ]


def _iter_manifest_owned_paths(
    manifests: list[EcosystemManifest],
    *,
    remove_mode: bool,
) -> list[tuple[EcosystemManifest, str]]:
    entries: list[tuple[EcosystemManifest, str]] = []
    seen_paths: dict[str, str] = {}

    for manifest in manifests:
        if remove_mode:
            relative_paths = sorted(
                manifest_owned_relative_paths(manifest),
                key=lambda value: (value.count("/"), value),
                reverse=True,
            )
        else:
            relative_paths = sorted(manifest_owned_relative_paths(manifest))

        for relative_path in relative_paths:
            owner = seen_paths.get(relative_path)
            if owner is not None and owner != manifest.slug:
                raise RuntimeError(
                    "Manifest-owned path conflict between ecosystems "
                    f"{owner} and {manifest.slug}: {relative_path}"
                )
            seen_paths[relative_path] = manifest.slug
            entries.append((manifest, relative_path))

    return entries


def execute_delivery_plan(
    action: Literal["install", "remove"],
    target_repo: str,
    ecosystem_slug: str,
    source_root: Path | None = None,
    working_directory: Path | str | None = None,
    base_branch: str | None = None,
    branch_name: str | None = None,
    dry_run: bool = False,
    runner: ShellCommandRunner | None = None,
) -> DeliveryExecutionResult:
    resolved_source_root = _resolve_source_root(source_root)
    _, repo_name = _parse_target_repo(target_repo)
    runner = runner or ShellCommandRunner()
    resolved_working_directory = Path(working_directory).resolve() if working_directory else Path(
        tempfile.mkdtemp(prefix="ecosystem-delivery-")
    )
    resolved_working_directory.mkdir(parents=True, exist_ok=True)
    clone_path = resolved_working_directory / repo_name

    runner.run(["gh", "repo", "clone", target_repo, str(clone_path)], cwd=resolved_working_directory)

    resolved_base_branch = base_branch or runner.run(
        [
            "gh",
            "repo",
            "view",
            target_repo,
            "--json",
            "defaultBranchRef",
            "--jq",
            ".defaultBranchRef.name",
        ],
        cwd=clone_path,
    ).stdout.strip()
    if not resolved_base_branch:
        raise RuntimeError("Could not determine base branch for target repository")

    if dry_run:
        if action == "install":
            resolved_manifests = _resolve_install_manifests(
                resolved_source_root,
                ecosystem_slug,
            )
            changes = build_install_changeset(
                target_root=clone_path,
                ecosystem_slug=ecosystem_slug,
                source_root=resolved_source_root,
                manifests=resolved_manifests,
            )
        else:
            resolved_manifests = _resolve_remove_manifests(
                resolved_source_root,
                clone_path,
                ecosystem_slug,
            )
            changes = build_remove_changeset(
                target_root=clone_path,
                ecosystem_slug=ecosystem_slug,
                source_root=resolved_source_root,
                manifests=resolved_manifests,
            )
        file_actions = apply_delivery_changes(changes, dry_run=True)
        return DeliveryExecutionResult(
            action=action,
            ecosystem_slug=ecosystem_slug,
            resolved_ecosystems=[manifest.slug for manifest in resolved_manifests],
            target_repo=target_repo,
            base_branch=resolved_base_branch,
            branch_name=prepare_branch_name(ecosystem_slug, action, branch_name),
            working_directory=str(resolved_working_directory),
            clone_path=str(clone_path),
            file_actions=file_actions,
            pr_title=generate_pr_title(ecosystem_slug, action),
            pr_body=generate_pr_body(
                ecosystem_slug,
                action,
                [manifest.slug for manifest in resolved_manifests],
                file_actions,
            ),
            pr_url=None,
            committed=False,
        )

    if base_branch and base_branch != resolved_base_branch:
        runner.run(["git", "switch", resolved_base_branch], cwd=clone_path)

    if action == "install":
        resolved_manifests = _resolve_install_manifests(
            resolved_source_root,
            ecosystem_slug,
        )
        changes = build_install_changeset(
            target_root=clone_path,
            ecosystem_slug=ecosystem_slug,
            source_root=resolved_source_root,
            manifests=resolved_manifests,
        )
    else:
        resolved_manifests = _resolve_remove_manifests(
            resolved_source_root,
            clone_path,
            ecosystem_slug,
        )
        changes = build_remove_changeset(
            target_root=clone_path,
            ecosystem_slug=ecosystem_slug,
            source_root=resolved_source_root,
            manifests=resolved_manifests,
        )

    file_actions = apply_delivery_changes(changes)
    pr_title = generate_pr_title(ecosystem_slug, action)
    pr_body = generate_pr_body(
        ecosystem_slug,
        action,
        [manifest.slug for manifest in resolved_manifests],
        file_actions,
    )
    resolved_branch_name = prepare_branch_name(ecosystem_slug, action, branch_name)

    status_result = runner.run(["git", "status", "--short"], cwd=clone_path)
    if not status_result.stdout.strip():
        return DeliveryExecutionResult(
            action=action,
            ecosystem_slug=ecosystem_slug,
            resolved_ecosystems=[manifest.slug for manifest in resolved_manifests],
            target_repo=target_repo,
            base_branch=resolved_base_branch,
            branch_name=resolved_branch_name,
            working_directory=str(resolved_working_directory),
            clone_path=str(clone_path),
            file_actions=file_actions,
            pr_title=pr_title,
            pr_body=pr_body,
            pr_url=None,
            committed=False,
        )

    runner.run(["git", "switch", "-c", resolved_branch_name], cwd=clone_path)
    runner.run(["git", "add", "--all"], cwd=clone_path)
    runner.run(["git", "commit", "-m", pr_title], cwd=clone_path)
    runner.run(["git", "push", "--set-upstream", "origin", resolved_branch_name], cwd=clone_path)
    pr_url = runner.run(
        [
            "gh",
            "pr",
            "create",
            "--base",
            resolved_base_branch,
            "--head",
            resolved_branch_name,
            "--title",
            pr_title,
            "--body",
            pr_body,
        ],
        cwd=clone_path,
    ).stdout.strip() or None

    return DeliveryExecutionResult(
        action=action,
        ecosystem_slug=ecosystem_slug,
        resolved_ecosystems=[manifest.slug for manifest in resolved_manifests],
        target_repo=target_repo,
        base_branch=resolved_base_branch,
        branch_name=resolved_branch_name,
        working_directory=str(resolved_working_directory),
        clone_path=str(clone_path),
        file_actions=file_actions,
        pr_title=pr_title,
        pr_body=pr_body,
        pr_url=pr_url,
        committed=True,
    )


def build_install_changeset(
    target_root: Path | str,
    ecosystem_slug: str,
    source_root: Path | None = None,
    manifests: list[EcosystemManifest] | None = None,
) -> list[DeliveryChange]:
    resolved_source_root = _resolve_source_root(source_root)
    resolved_target_root = Path(target_root).resolve()
    resolved_manifests = manifests or _resolve_install_manifests(
        resolved_source_root,
        ecosystem_slug,
    )

    changes: list[DeliveryChange] = []
    for _, relative_path in _iter_manifest_owned_paths(resolved_manifests, remove_mode=False):
        source_path = resolved_source_root / relative_path
        if not source_path.exists():
            raise FileNotFoundError(f"Manifest-owned source path not found: {source_path}")
        destination = resolved_target_root / relative_path
        changes.append(
            DeliveryChange(
                action="copy",
                relative_destination=relative_path,
                destination=str(destination),
                source=str(source_path),
            )
        )

    return changes


def build_remove_changeset(
    target_root: Path | str,
    ecosystem_slug: str,
    source_root: Path | None = None,
    manifests: list[EcosystemManifest] | None = None,
) -> list[DeliveryChange]:
    resolved_source_root = _resolve_source_root(source_root)
    resolved_target_root = Path(target_root).resolve()
    if not resolved_target_root.exists():
        raise FileNotFoundError(f"Target repository path does not exist: {resolved_target_root}")

    resolved_manifests = manifests or _resolve_remove_manifests(
        resolved_source_root,
        resolved_target_root,
        ecosystem_slug,
    )
    changes: list[DeliveryChange] = []
    for _, relative_path in _iter_manifest_owned_paths(
        list(reversed(resolved_manifests)),
        remove_mode=True,
    ):
        source_path = resolved_source_root / relative_path
        if not source_path.exists():
            raise FileNotFoundError(f"Manifest-owned source path not found: {source_path}")
        destination = resolved_target_root / relative_path
        if not destination.exists():
            continue
        changes.append(
            DeliveryChange(
                action="remove",
                relative_destination=relative_path,
                destination=str(destination),
                source=str(source_path),
            )
        )

    return changes


def apply_delivery_changes(
    changes: list[DeliveryChange],
    dry_run: bool = False,
) -> list[str]:
    _validate_delivery_changes(changes)
    actions: list[str] = []
    prune_boundary = (
        Path(os.path.commonpath([change.destination for change in changes]))
        if changes
        else None
    )

    for change in changes:
        destination = Path(change.destination)
        if change.action == "copy":
            source = Path(change.source)
            if destination.exists() and _paths_match(source, destination):
                continue
            actions.append(f"copy {destination}")
            if dry_run:
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            if source.is_dir():
                shutil.copytree(source, destination)
            else:
                shutil.copy2(source, destination)
            continue

        if change.action != "remove":
            raise ValueError(f"Unsupported delivery action: {change.action}")

        if not destination.exists():
            continue
        actions.append(f"remove {destination}")
        if dry_run:
            continue
        if destination.is_dir():
            shutil.rmtree(destination)
        else:
            destination.unlink()
        _prune_empty_parents(destination.parent, prune_boundary)

    return actions


def _validate_delivery_changes(changes: list[DeliveryChange]) -> None:
    conflicts: list[DeliveryConflict] = []
    for change in changes:
        destination = Path(change.destination)
        if change.source is None:
            raise ValueError(f"delivery change is missing source: {change.relative_destination}")
        source = Path(change.source)
        if not source.exists():
            raise FileNotFoundError(f"Manifest-owned source path not found: {source}")
        if not destination.exists():
            continue
        if change.action == "copy":
            if not _paths_match(source, destination):
                conflicts.append(
                    DeliveryConflict(
                        action="copy",
                        relative_destination=change.relative_destination,
                        destination=change.destination,
                    )
                )
            continue
        if change.action == "remove":
            if not _paths_match(source, destination):
                conflicts.append(
                    DeliveryConflict(
                        action="remove",
                        relative_destination=change.relative_destination,
                        destination=change.destination,
                    )
                )
            continue
        raise ValueError(f"Unsupported delivery action: {change.action}")
    if conflicts:
        raise DeliveryConflictError(conflicts)


def _paths_match(source: Path, destination: Path) -> bool:
    if source.is_dir() != destination.is_dir():
        return False
    if source.is_file() != destination.is_file():
        return False
    if source.is_file():
        return source.read_bytes() == destination.read_bytes()

    source_entries = sorted(path.relative_to(source) for path in source.rglob("*"))
    destination_entries = sorted(path.relative_to(destination) for path in destination.rglob("*"))
    if source_entries != destination_entries:
        return False

    for relative_path in source_entries:
        left = source / relative_path
        right = destination / relative_path
        if left.is_dir() != right.is_dir():
            return False
        if left.is_file() and left.read_bytes() != right.read_bytes():
            return False

    return True


def _prune_empty_parents(path: Path, boundary: Path | None) -> None:
    current = path
    while boundary is not None and current != boundary and current.exists():
        if any(current.iterdir()):
            return
        current.rmdir()
        current = current.parent
