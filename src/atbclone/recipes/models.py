from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

from atbclone.validation import (
    validate_bundle_id,
    validate_env_key,
    validate_host,
    validate_proxy_credential,
    validate_proxy_port,
)


class ProxyConfig(BaseModel):
    # Validate on assignment too: CLI/GUI flows mutate proxy fields after
    # construction, and those values end up inside generated shell scripts.
    model_config = ConfigDict(validate_assignment=True)

    enabled: bool = False
    type: Literal["http", "https", "socks5"] = "http"
    host: str = "127.0.0.1"
    port: int = 1080
    username: str = ""
    password: str = ""
    no_proxy: str = "localhost,127.0.0.1,*.local"

    @field_validator("host")
    @classmethod
    def _check_host(cls, v: str) -> str:
        return validate_host(v)

    @field_validator("port")
    @classmethod
    def _check_port(cls, v: int) -> int:
        return validate_proxy_port(v)

    @field_validator("username", "password", "no_proxy")
    @classmethod
    def _check_credential(cls, v: str, info) -> str:
        return validate_proxy_credential(v, field=info.field_name)

    @property
    def url(self) -> str:
        auth = f"{self.username}:{self.password}@" if self.username else ""
        return f"{self.type}://{auth}{self.host}:{self.port}"


AppType = Literal["cocoa", "chromium", "electron", "firefox", "generic"]
InjectionStrategy = Literal["auto", "dylib", "launcher"]


class Recipe(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    bundle_id: str
    app_name: str
    strategy: Literal["hard_clone", "soft_clone"]

    @field_validator("bundle_id")
    @classmethod
    def _check_bundle_id(cls, v: str) -> str:
        return validate_bundle_id(v)

    @field_validator("environment_injection")
    @classmethod
    def _check_env_keys(cls, v: dict[str, str]) -> dict[str, str]:
        for key in v:
            validate_env_key(key)
        return v

    @field_validator("symlink_whitelist")
    @classmethod
    def _check_symlink_whitelist(cls, v: list[str]) -> list[str]:
        for item in v:
            cleaned = item.strip().strip("/")
            if not cleaned:
                continue
            if any(part == ".." for part in cleaned.split("/")):
                raise ValueError(
                    f"Invalid symlink_whitelist entry: {item!r}. "
                    f"'..' path components are not allowed."
                )
        return v
    strip_sandbox: bool = False
    proxy: ProxyConfig = Field(default_factory=ProxyConfig)
    environment_injection: dict[str, str] = Field(default_factory=dict)
    symlink_whitelist: list[str] = Field(default_factory=list)
    launch_args: list[str] = Field(default_factory=list)
    language: str = "system"
    app_type: AppType | None = None
    patch_framework_singleton: bool = False
    patch_cef: bool = False
    patch_lark_isolation: bool = False
    patch_chatgpt_isolation: bool = False
    strip_url_schemes: bool = False
    injection_strategy: InjectionStrategy = "auto"


def supports_data_dir(recipe: Recipe) -> bool:
    """Return True if the recipe uses {{ATB_DATA_DIR}} in launch args or environment injection."""
    has_in_args = any("{{ATB_DATA_DIR}}" in arg for arg in recipe.launch_args)
    has_in_env = any("{{ATB_DATA_DIR}}" in val for val in recipe.environment_injection.values())
    return has_in_args or has_in_env


