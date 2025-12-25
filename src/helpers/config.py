from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    APP_NAME: str 
    APP_VERSION: str
    OPEN_API_KEY: str
    FILE_ALLOWED_EXTENSIONS: list[str]
    FILE_MAX_SIZE_MB: int
    FILE_DEFAULT_CHUNK_SIZE: int


def get_settings() -> Settings:
    return Settings()