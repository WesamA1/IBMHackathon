from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    database_url: str = "sqlite:///./homebase.db"
    secret_key: str = "dev-secret"
    environment: str = "development"
    cors_origins: str = "http://localhost:5500,http://127.0.0.1:5500,null"

    # ── AI provider for notes → flashcards ────────────────────────────────
    # Provider priority: Ollama (local) → Groq (free cloud) → watsonx (IBM)

    # Ollama — free, fully local, no key needed.
    # Install: https://ollama.com  then  `ollama pull granite3-moe:1b`
    ollama_model: str = "granite3-moe:1b"

    # Groq — free cloud tier, no credit card.
    # Sign up at https://console.groq.com and create a free API key.
    groq_api_key: str = ""
    groq_model:   str = "llama-3.1-8b-instant"

    # IBM watsonx.ai — paid IBM Cloud account required.
    watsonx_api_key:    str = ""
    watsonx_url:        str = "https://us-south.ml.cloud.ibm.com"
    watsonx_project_id: str = ""
    watsonx_model:      str = "ibm/granite-3-8b-instruct"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()
