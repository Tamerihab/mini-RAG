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

    MONGODB_URI: str
    MONGODB_DATABASE: str
        
    GENERATION_BACKEND:str
    EMBEDDING_BACKEND:str

    OPENAI_API_KEY: str= None
    OPENAI_API_URL: str= None
    COHERE_API_KEY: str= None
    DEEPSEEK_API_KEY: str= None
    DEEPSEEK_API_URL: str= None


    GENERATION_MODEL_ID: str= None 
    EMBEDDING_MODEL_ID: str= None
    EMBEDDING_MODEL_SIZE: int= None

    INPUT_DEFAULT_MAX_CHARACTERS: int= None
    GENERATION_DEFAULT_MAX_TOKENS: int= None
    GENERATION_DEFAULT_TEMPERATURE: float= None

    VECTOR_DB_BACKEND: str= None
    VECTOR_DB_PATH: str= None
    VECTOR_DB_DISTANCE_METRIC: str= None

    DEFAULT_LANGUAGE: str= None
    PRIMARY_LANGUAGE: str= None


def get_settings() -> Settings:
    return Settings()