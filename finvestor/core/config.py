from typing import Literal, Optional

from pydantic import AnyHttpUrl, AnyUrl, BaseSettings, validator


class FinvestorConfig(BaseSettings):
    # DATABASE SETTINGS
    FINVESTOR_DATABASE_URI: Optional[AnyUrl]

    ###############################################
    #     EXTARNAL DATA PROVIDERS SETTINGS        #
    ###############################################

    DATA_PROVIDER: Literal["alpaca", "yfinance"] = "yfinance"

    # YAHOO FINANCE BASE URL TO GET PRICE DATA
    YF_BASE_URL: AnyHttpUrl = AnyHttpUrl(
        url="https://query2.finance.yahoo.com",
        scheme="https",
        host="query2.finance.yahoo.com",
    )
    # YAHOO FINANCE SCRAPE URL TO GET TICKER INFO AND FUNDAMENTALS
    YF_SCRAPE_URL: AnyHttpUrl = AnyHttpUrl(
        url="https://finance.yahoo.com/quote",
        scheme="https",
        host="finance.yahoo.com/quote",
    )
    # BUSINESS INSIDER URL TO SCRAP ISIN OF TICKERS
    ISIN_SCRAPE_URL: AnyHttpUrl = AnyHttpUrl(
        url="https://markets.businessinsider.com/ajax/SearchController_Suggest",
        scheme="https",
        host="markets.businessinsider.com",
        path="/ajax/SearchController_Suggest",
    )

    # ALPACA settings to connect to their api
    APCA_API_BASE_URL: AnyHttpUrl = AnyHttpUrl(
        url="https://paper-api.alpaca.markets",
        scheme="https",
        host="paper-api.alpaca.markets",
    )
    APCA_API_DATA_URL: AnyHttpUrl = AnyHttpUrl(
        url="https://data.alpaca.markets",
        scheme="https",
        host="data.alpaca.markets",
    )
    APCA_API_KEY_ID: Optional[str]
    APCA_API_SECRET_KEY: Optional[str]

    @validator("DATA_PROVIDER")
    def api_ids_must_be_provided(cls, data_provider, values):
        if data_provider == "alpaca" and (
            not values.get("APCA_API_KEY_ID") or not values.get("APCA_API_SECRET_KEY")
        ):
            raise ValueError(
                "To use alpaca data provider, you must set up the env vars: "
                "'APCA_API_KEY_ID' and 'APCA_API_SECRET_KEY'"
            )
        return data_provider

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


config = FinvestorConfig()
