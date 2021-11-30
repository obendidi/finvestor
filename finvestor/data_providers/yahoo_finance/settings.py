from pydantic import AnyHttpUrl, BaseSettings


class YFSettings(BaseSettings):
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

    class Config:
        env_prefix = "YAHOO_FINANCE_"
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


yf_settings = YFSettings()

if __name__ == "__main__":
    print(yf_settings)
