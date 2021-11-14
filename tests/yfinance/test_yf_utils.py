from finvestor.yfinance.utils import parse_quote_summary


def test_parse_quote_summary(yf_scrape_response, quote_summary_snapshot):
    parsed = parse_quote_summary(yf_scrape_response)
    assert parsed == quote_summary_snapshot
