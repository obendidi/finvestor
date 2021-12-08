from pydantic import BaseSettings

__all__ = "BaseConfig"


class BaseConfig(BaseSettings):
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


# class FinvestorConfig(BaseSettings):

#     MARKET_DATA_PROVIDER: Literal["alpaca", "yahoo_finance"] = "yahoo_finance"

#     # DATABASE SETTINGS
#     DATABASE_URI: Optional[AnyUrl]

#     class Config:
#         env_prefix = "FINVESTOR_"
#         case_sensitive = True
#         env_file = ".env"
#         env_file_encoding = "utf-8"
