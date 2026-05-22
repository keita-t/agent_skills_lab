from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict

from mcp_models import GovernanceMode


class McpServerSettings(BaseSettings):
    repo_root: str = "."
    default_governance_mode: GovernanceMode = "bilingual"
    subprocess_timeout_seconds: int = 120
    allow_shell_post_install_validators: bool = True
    log_level: str = "INFO"
    require_confirmation_for_mutating_tools: bool = True

    model_config = SettingsConfigDict(env_prefix="MCP_", extra="ignore")