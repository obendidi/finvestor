from pydantic import AnyHttpUrl, BaseSettings

USER_AGENT_HEADERS = {
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

    class Config:
        case_sensitive = True
