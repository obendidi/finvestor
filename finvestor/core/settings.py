from pydantic import BaseSettings, AnyUrl


class FinvestorSettings(BaseSettings):
    DATABASE_URI: AnyUrl

    class Config:
        env_prefix = "FINVESTOR_"
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = FinvestorSettings()
