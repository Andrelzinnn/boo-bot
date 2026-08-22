from pathlib import Path
from typing import ClassVar

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    token: str = Field(default="")
    client_id: str = Field(default="")
    user_id: int = Field(default=0)
    gif_unpresence_url: str = Field(default="https://klipy.com/gifs/cat-hello-cat-peek")
    violin_gif_url: str = Field(default="https://klipy.com/gifs/cat-instrumental-1")
    yay_gif_url: str = Field(default="https://klipy.com/gifs/cat-chinese-4")
    cooldown_seconds: int = Field(default=10)
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
