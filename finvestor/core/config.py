from pydantic import BaseSettings

__all__ = "BaseConfig"


class BaseConfig(BaseSettings):
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"
