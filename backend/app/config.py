from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # LLM
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    google_api_key: str = ""
    default_llm_provider: str = "anthropic"
    default_llm_model: str = "claude-3-5-sonnet-latest"

    # Search
    search_provider: str = "tavily"
    tavily_api_key: str = ""
    exa_api_key: str = ""
    serpapi_api_key: str = ""

    # GitHub
    github_token: str = ""
    github_repo_owner: str = ""
    github_repo_name: str = "trend2poc-knowledge-base"
    github_default_branch: str = "main"

    # Supabase
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""

    # API
    api_secret_key: str = "change-me-in-production"
    api_port: int = 8000
    backend_cors_origins: str = "http://localhost:3000"

    # Pipeline
    min_eval_score: float = 7.0
    target_eval_score: float = 8.0
    auto_push_to_github: bool = False
    max_topics_per_run: int = 5
    max_sources_per_topic: int = 12
    source_confidence_threshold: float = 0.70

    # Redis
    redis_url: str = ""                  # e.g. redis://localhost:6379/0
    redis_state_ttl_seconds: int = 86400  # 24 hours — how long active run state stays in Redis

    # Facebook
    facebook_page_access_token: str = ""
    facebook_page_id: str = ""
    facebook_auto_post: bool = False

    # Cost
    enable_cost_tracking: bool = True
    max_run_cost_usd: float = 3.00

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.backend_cors_origins.split(",")]


settings = Settings()
