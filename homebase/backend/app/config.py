from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    database_url: str = "sqlite:///./homebase.db"
    secret_key: str = "dev-secret"
    environment: str = "development"
    cors_origins: str = "http://localhost:5500,http://127.0.0.1:5500,null"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()
