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

    # Database connection URLs are supplied at runtime via MTG_AI_DATABASE_URL
    # (restricted app role) and MTG_AI_DATA_DATABASE_URL (data writer role),
    # built from .env by docker-compose or set in the environment. They default
    # to empty so that neither a credential nor a password-less connection
    # string is committed to source; the application requires them to be set.
    database_url: str = ""
    data_database_url: str = ""
    sql_echo: bool = False

    # Authentication. PBKDF2-HMAC-SHA256 is FIPS-approved; bcrypt is prohibited.
    # The iteration count is stored inside each hash, so changing it here only
    # affects newly created hashes; existing hashes still verify.
    pbkdf2_iterations: int = 600_000
    session_ttl_seconds: int = 60 * 60 * 24 * 14  # 14 days


# A single, global instance of the settings
settings = Settings()
