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

    class Config:
        env_file = ".env"

# This function returns the configuration settings of the project
def get_settings():
    return Settings()
