from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    token: str
    client_id: str
    user_id: int

    class Config:
        env_file = Path(__file__).resolve().parents[2] / ".env"

settings = Settings()  # type: ignore
