from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env")

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24
    DATABASE_URL: str
    API_TITLE: str = "NorkTech Books API"
    API_VERSION: str = "3.0.0"
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str

@lru_cache()
def get_settings():
    return Settings()