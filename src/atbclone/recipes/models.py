from typing import Literal
from pydantic import BaseModel, Field


class ProxyConfig(BaseModel):
    enabled: bool = False
    type: Literal["http", "https", "socks5"] = "http"
    host: str = "127.0.0.1"
    port: int = 1080
    username: str = ""
    password: str = ""
    no_proxy: str = "localhost,127.0.0.1,*.local"

    @property
    def url(self) -> str:
        auth = f"{self.username}:{self.password}@" if self.username else ""
        return f"{self.type}://{auth}{self.host}:{self.port}"


AppType = Literal["cocoa", "chromium", "electron", "firefox", "generic"]
InjectionStrategy = Literal["auto", "dylib", "launcher"]


class Recipe(BaseModel):
    bundle_id: str
    app_name: str
    strategy: Literal["hard_clone", "soft_clone"]
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


