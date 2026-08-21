from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    token: str
    client_id: str
    user_id: int

    model_config = SettingsConfigDict(
      env_file=Path(__file__).resolve().parents[2] / ".env",
      env_file_encoding="utf-8",
      extra="ignore"
    )

settings = Settings()  # type: ignore
