from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # The use of pydantic library validates the fields before they're used
    APP_NAME: str
    APP_VERSION: str

    FILE_ALLOWED_TYPES: list
    FILE_MAX_SIZE: int
    FILE_DEFAULT_CHUNK_SIZE: int

    MONGO_URL: str
    MONGODB_DATABASE: str

    GENERATION_BACKENED: str
    EMBEDDING_BACKEND: str

    OPENAI_API_KEY: str
    OPENAI_API_URL: str
    COHERE_API_KEY: str

    GENERATION_MODEL_ID: str
    EMBEDDING_MODEL_ID: str
    EMBEDDING_MODEL_SIZE: int

    INPUT_DEFAULT_MAX_CHARACTERS: int
    GENERATION_DEFAULT_MAX_TOKENS: int
    GENERATION_DEFAULT_TEMPERATURE: float

    class Config:
        env_file = ".env"

# This function returns the configuration settings of the project
def get_settings():
    return Settings()
