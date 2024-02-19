from functools import lru_cache

from pydantic.v1 import BaseSettings


class Environment(BaseSettings):
    API_VERSION: str
    APP_NAME: str
    API_PREFIX: str
    INTERVAL_MINUTES: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_config() -> Environment:
    return Environment()
