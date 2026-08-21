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

settings = Settings()

VIOLIN_GIF_URL = "https://klipy.com/gifs/cat-instrumental-1"
YAY_CAT_GIF_URL = "https://klipy.com/gifs/cat-chinese-4"
GIF_URL = "https://klipy.com/gifs/cat-hello-cat-peek"
