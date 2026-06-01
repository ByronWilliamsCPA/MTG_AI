"""Configuration settings for MTG AI.

Settings are loaded from environment variables with the prefix 'MTG_AI_'.
Pydantic-settings handles the parsing and validation.
"""

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuration settings for the application, loaded from environment variables.

    Attributes:
        log_level: The logging level for the application.
        json_logs: Flag to enable or disable JSON formatted logs.
        include_timestamp: Flag to include timestamps in logs.
    """

    model_config = SettingsConfigDict(
        env_prefix="mtg_ai_",
        case_sensitive=False,
        extra="ignore",
    )

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    json_logs: bool = False
    include_timestamp: bool = True


# A single, global instance of the settings
settings = Settings()
