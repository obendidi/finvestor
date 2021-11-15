from pydantic import AnyHttpUrl, BaseSettings

YF_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"  # noqa
}


class YFSettings(BaseSettings):
    YAHOO_FINANCE_BASE_URL: AnyHttpUrl = AnyHttpUrl(
        url="https://query2.finance.yahoo.com",
        scheme="https",
        host="query2.finance.yahoo.com",
    )

    YAHOO_FINANCE_SCRAPE_URL: AnyHttpUrl = AnyHttpUrl(
        url="https://finance.yahoo.com/quote",
        scheme="https",
        host="finance.yahoo.com/quote",
    )
    ISIN_SCRAPE_URL: AnyHttpUrl = AnyHttpUrl(
        url="https://markets.businessinsider.com/ajax/SearchController_Suggest",
        scheme="https",
        host="markets.businessinsider.com",
        path="/ajax/SearchController_Suggest",
    )
    ISIN_SCRAPE_MAX_RESULTS: int = 25
    ISIN_SCRAPE_TIMEOUT: int = 5

    class Config:
        case_sensitive = True
