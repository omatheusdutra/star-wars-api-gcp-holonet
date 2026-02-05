from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    swapi_base_url: str = Field(default="https://swapi.dev/api", alias="SWAPI_BASE_URL")
    cache_ttl_seconds: int = Field(default=180, alias="CACHE_TTL_SECONDS")
    cache_max_entries: int = Field(default=2048, alias="CACHE_MAX_ENTRIES")
    cache_backend: str = Field(default="inmemory", alias="CACHE_BACKEND")
    redis_url: str | None = Field(default=None, alias="REDIS_URL")

    http_timeout_seconds: float = Field(default=6.0, alias="HTTP_TIMEOUT_SECONDS")
    http_retries: int = Field(default=2, alias="HTTP_RETRIES")
    http_backoff_factor: float = Field(default=0.3, alias="HTTP_BACKOFF_FACTOR")

    api_page_size_default: int = Field(default=10, alias="API_PAGE_SIZE_DEFAULT")
    max_page_size: int = Field(default=50, alias="MAX_PAGE_SIZE")
    max_upstream_pages: int = Field(default=6, alias="MAX_UPSTREAM_PAGES")
    max_expand_concurrency: int = Field(default=8, alias="MAX_EXPAND_CONCURRENCY")

    graph_max_nodes: int = Field(default=250, alias="GRAPH_MAX_NODES")
    graph_max_depth: int = Field(default=1, alias="GRAPH_MAX_DEPTH")
    map_max_pages: int = Field(default=4, alias="MAP_MAX_PAGES")

    require_api_key: bool = Field(default=False, alias="REQUIRE_API_KEY")
    api_key: str = Field(default="", alias="API_KEY")

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")


settings = Settings()
