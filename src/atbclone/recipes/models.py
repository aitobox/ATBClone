from typing import Literal
from pydantic import BaseModel, Field


class ProxyConfig(BaseModel):
    enabled: bool = False
    type: Literal["http", "socks5"] = "http"
    host: str = "127.0.0.1"
    port: int = 1080
    username: str = ""
    password: str = ""
    no_proxy: str = "localhost,127.0.0.1,*.local"

    @property
    def url(self) -> str:
        auth = f"{self.username}:{self.password}@" if self.username else ""
        return f"{self.type}://{auth}{self.host}:{self.port}"


class Recipe(BaseModel):
    bundle_id: str
    app_name: str
    strategy: Literal["hard_clone", "soft_clone"]
    strip_sandbox: bool = False
    proxy: ProxyConfig = Field(default_factory=ProxyConfig)
    environment_injection: dict[str, str] = Field(default_factory=dict)
    symlink_whitelist: list[str] = Field(default_factory=list)
    launch_args: list[str] = Field(default_factory=list)


def supports_data_dir(recipe: Recipe) -> bool:
    """Return True if the recipe uses {{ATB_DATA_DIR}} in launch args or environment injection."""
    has_in_args = any("{{ATB_DATA_DIR}}" in arg for arg in recipe.launch_args)
    has_in_env = any("{{ATB_DATA_DIR}}" in val for val in recipe.environment_injection.values())
    return has_in_args or has_in_env


