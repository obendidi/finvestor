from datetime import timedelta

from pydantic import AnyHttpUrl, BaseSettings


class APCASettings(BaseSettings):

    BASE_URL: AnyHttpUrl = AnyHttpUrl.build(
        scheme="https",
        host="paper-api.alpaca.markets",
    )
    DATA_URL: AnyHttpUrl = AnyHttpUrl.build(
        scheme="https",
        host="data.alpaca.markets",
    )
    # by defult free tier has 15 minue delay
    # If provided as an ENV var, it should be seconds
    # ex: export ALPACA_HISTORICAL_DATA_DELAY=900
    HISTORICAL_DATA_DELAY: timedelta = timedelta(0)
    API_KEY_ID: str
    API_SECRET_KEY: str

    class Config:
        env_prefix = "ALPACA_"
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


alpaca_settings = APCASettings()

if __name__ == "__main__":
    print(alpaca_settings)
