from pydantic import AnyHttpUrl

from finvestor.core import BaseConfig


class YFConfig(BaseConfig, env_prefix="YAHOO_FINANCE_"):
    BASE_URL: AnyHttpUrl = AnyHttpUrl.build(
        scheme="https",
        host="query2.finance.yahoo.com",
    )

    # YAHOO FINANCE SCRAPE URL TO GET TICKER INFO AND FUNDAMENTALS
    SCRAPE_URL: AnyHttpUrl = AnyHttpUrl.build(
        scheme="https",
        host="finance.yahoo.com/quote",
    )
    # BUSINESS INSIDER URL TO SCRAP ISIN OF TICKERS
    ISIN_SCRAPE_URL: AnyHttpUrl = AnyHttpUrl.build(
        scheme="https",
        host="markets.businessinsider.com",
        path="/ajax/SearchController_Suggest",
    )


config = YFConfig()
