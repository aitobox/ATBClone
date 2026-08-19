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

