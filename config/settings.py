from pathlib import Path
from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
ASSETS_DIR = PROJECT_ROOT / "assets"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    openai_api_key: str = Field(...)
    openai_model: str = Field(default="gpt-4o-mini")
    
    typecast_api_key: str = Field(default="")
    typecast_voice_id: str = Field(default="")
    
    pexels_api_key: str = Field(default="")
    
    youtube_client_secret_file: str = Field(default="config/client_secret.json")
    youtube_token_file: str = Field(default="config/youtube_token.json")
    
    discord_webhook_url: str = Field(default="")
    
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(default="INFO")
    output_dir: str = Field(default="output")
    temp_dir: str = Field(default="output/temp")
    
    tts_provider: Literal["typecast", "edge"] = Field(default="typecast")
    
    daily_shorts_count: int = Field(default=3)
    upload_privacy: Literal["public", "unlisted", "private"] = Field(default="private")
    
    @property
    def output_path(self) -> Path:
        path = PROJECT_ROOT / self.output_dir
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def temp_path(self) -> Path:
        path = PROJECT_ROOT / self.temp_dir
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def videos_path(self) -> Path:
        path = self.output_path / "videos"
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def logs_path(self) -> Path:
        path = PROJECT_ROOT / "logs"
        path.mkdir(parents=True, exist_ok=True)
        return path


def get_settings() -> Settings:
    return Settings()


_settings: Settings | None = None


def settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = get_settings()
    return _settings
