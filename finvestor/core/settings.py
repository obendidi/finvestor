import logging
from datetime import timedelta
from typing import Literal, Optional

from pydantic import AnyHttpUrl, AnyUrl, BaseSettings, validator

logger = logging.getLogger(__name__)


class FinvestorConfig(BaseSettings):
    # DATABASE SETTINGS
    FINVESTOR_DATABASE_URI: Optional[AnyUrl]

    ###############################################
    #     EXTARNAL DATA PROVIDERS SETTINGS        #
    ###############################################

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
    # by defult free tier has 15 minue delay
    APCA_HISTORICAL_DATA_DELAY_SECONDS: timedelta = timedelta(seconds=15 * 60)
    APCA_API_KEY_ID: Optional[str] = None
    APCA_API_SECRET_KEY: Optional[str] = None

    DATA_PROVIDER: Literal[None, "alpaca", "yahoo_finance"] = None

    @validator("DATA_PROVIDER", pre=True)
    def data_provider_setter(cls, data_provider, values):
        key_id = values.get("APCA_API_KEY_ID")
        secret_id = values.get("APCA_API_SECRET_KEY")
        if data_provider is None:
            if key_id is not None and secret_id is not None:
                _provider = "alpaca"
            else:
                _provider = "yahoo_finance"
            logger.debug(f"Using '{_provider}' as market data provider.")
            return _provider

        if data_provider == "alpaca" and (key_id is None or secret_id is None):
            raise ValueError(
                "To use 'alpaca' as market data provider, you need to set up: "
                "'APCA_API_KEY_ID' and 'APCA_API_KEY_ID'"
            )
        return data_provider

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


config = FinvestorConfig()
