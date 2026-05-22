from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

ToolKind = Literal["read", "mutate"]
RiskLevel = Literal["low", "medium", "high"]
ConfirmationMode = Literal["none", "preview_token", "explicit_confirmation"]
MergeStrategy = Literal["merge", "replace", "skip-existing"]
GovernanceMode = Literal["single-language", "bilingual"]


class ManifestSummary(BaseModel):
    slug: str
    name: str
    description: str
    status: str
    root_agent: str
    skills: list[str]
    dependencies: list[str] = Field(default_factory=list)
    ecosystem_files: list[str] = Field(default_factory=list)
    managed_core_files: list[str] = Field(default_factory=list)
    mcp_tool_names: list[str] = Field(default_factory=list)


class ListAvailableEcosystemsInput(BaseModel):
    repo_root: str = "."


class ListAvailableEcosystemsResult(BaseModel):
    ecosystems: list[ManifestSummary]


class GetManifestInput(BaseModel):
    ecosystem_slug: str
    repo_root: str = "."


class GetManifestResult(BaseModel):
    manifest: ManifestSummary


class PreviewInstallInput(BaseModel):
    target_repo: str
    ecosystem_slug: str
    merge_strategy: MergeStrategy = "merge"
    run_core_update: bool = True
    run_validation: bool = True


class PreviewInstallResult(BaseModel):
    actions: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    post_install_validators: list[str] = Field(default_factory=list)
    requires_confirmation: bool = True
    preview_token: str | None = None


class ApplyInstallInput(BaseModel):
    target_repo: str
    ecosystem_slug: str
    merge_strategy: MergeStrategy = "merge"
    run_core_update: bool = True
    run_validation: bool = True
    confirmation_token: str


class ValidatorResult(BaseModel):
    name: str
    passed: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class ApplyInstallResult(BaseModel):
    installed_ecosystem: str
    target_repo: str
    actions: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    validator_results: list[ValidatorResult] = Field(default_factory=list)


class UpdateCoreFilesInput(BaseModel):
    target_repo: str = "."
    dry_run: bool = False


class UpdateCoreFilesResult(BaseModel):
    target_repo: str
    dry_run: bool
    updated_files: list[str] = Field(default_factory=list)
    skipped_files: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class ValidateRegistryInput(BaseModel):
    repo_root: str = "."


class ValidateRepositoryGovernanceInput(BaseModel):
    repo_root: str = "."
    mode: GovernanceMode = "single-language"


class ValidateAgentSkillDocsInput(BaseModel):
    repo_root: str = "."


class ValidationIssue(BaseModel):
    message: str
    path: str | None = None


class ValidationResult(BaseModel):
    passed: bool
    errors: list[ValidationIssue] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class McpToolDefinition(BaseModel):
    name: str
    title: str
    description: str
    handler: str
    kind: ToolKind
    risk_level: RiskLevel = "low"
    confirmation_mode: ConfirmationMode = "none"
    input_model: str
    result_model: str
    tags: list[str] = Field(default_factory=list)
    enabled_by_default: bool = True
    dry_run_supported: bool = False
    validators_after: list[str] = Field(default_factory=list)
    requires_repo_root: bool = False
    requires_target_repo: bool = False
    requires_ecosystem_slug: bool = False
    supports_preview_token: bool = False

    @model_validator(mode="after")
    def validate_confirmation_contract(self) -> "McpToolDefinition":
        if self.kind == "read":
            if self.confirmation_mode != "none":
                raise ValueError("read tools cannot require confirmation")
            if self.supports_preview_token:
                raise ValueError("read tools cannot support preview tokens")
        if self.confirmation_mode == "preview_token" and not self.supports_preview_token:
            raise ValueError("preview_token confirmation requires supports_preview_token")
        if self.confirmation_mode == "explicit_confirmation" and self.kind != "mutate":
            raise ValueError("explicit_confirmation is only valid for mutating tools")
        if self.requires_target_repo and self.kind != "mutate":
            raise ValueError("requires_target_repo is only valid for mutating tools")
        return self


class McpToolRegistry(BaseModel):
    version: str
    namespace: str
    tools: list[McpToolDefinition]

    @model_validator(mode="after")
    def validate_unique_names(self) -> "McpToolRegistry":
        names = [tool.name for tool in self.tools]
        if len(names) != len(set(names)):
            raise ValueError("tool names must be unique within a registry")
        return self

    def qualified_tool_names(self) -> list[str]:
        return [f"{self.namespace}.{tool.name}" for tool in self.tools]


MODEL_REGISTRY: dict[str, type[BaseModel]] = {
    model.__name__: model
    for model in [
        ApplyInstallInput,
        ApplyInstallResult,
        GetManifestInput,
        GetManifestResult,
        ListAvailableEcosystemsInput,
        ListAvailableEcosystemsResult,
        PreviewInstallInput,
        PreviewInstallResult,
        UpdateCoreFilesInput,
        UpdateCoreFilesResult,
        ValidateAgentSkillDocsInput,
        ValidateRegistryInput,
        ValidateRepositoryGovernanceInput,
        ValidationResult,
    ]
}